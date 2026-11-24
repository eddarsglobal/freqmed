/* SPDX-License-Identifier: Apache-2.0 */
#include "binding.h"
#include "audio_devices.h"
#include "session_clock.h"
#include <CoreAudio/CoreAudio.h>
#include <CoreFoundation/CoreFoundation.h>
#include <stdio.h>
#include <string.h>

static int default_id(AudioDeviceID *id) {
    AudioObjectPropertyAddress a={kAudioHardwarePropertyDefaultOutputDevice,
        kAudioObjectPropertyScopeGlobal,kAudioObjectPropertyElementMain};
    UInt32 n=sizeof(*id);
    return AudioObjectGetPropertyData(kAudioObjectSystemObject,&a,0,NULL,&n,id)==noErr &&
        n==sizeof(*id) && *id!=kAudioObjectUnknown;
}
static int identity(AudioDeviceID id,FMEndpoint *p) {
    AudioObjectPropertyAddress a={kAudioDevicePropertyDeviceUID,
        kAudioObjectPropertyScopeGlobal,kAudioObjectPropertyElementMain};
    CFStringRef uid=NULL; UInt32 n=sizeof(uid);
    if(AudioObjectGetPropertyData(id,&a,0,NULL,&n,&uid)!=noErr ||
       n!=sizeof(uid)||!uid) return 0;
    int ok=CFStringGetCString(uid,p->uid,sizeof(p->uid),kCFStringEncodingUTF8);
    CFRelease(uid);
    if(!ok||!p->uid[0]) return 0;
    a.mSelector=kAudioDevicePropertyTransportType;
    UInt32 t=0; n=sizeof(t);
    if(AudioObjectGetPropertyData(id,&a,0,NULL,&n,&t)!=noErr||n!=sizeof(t))
        p->route=FM_ROUTE_UNKNOWN;
    else if(t==kAudioDeviceTransportTypeBuiltIn) p->route=FM_ROUTE_BUILT_IN;
    else if(t==kAudioDeviceTransportTypeUSB) p->route=FM_ROUTE_USB;
    else if(t==kAudioDeviceTransportTypeVirtual) p->route=FM_ROUTE_VIRTUAL;
    else p->route=FM_ROUTE_OTHER;
    return 1;
}
static int capture(FMSnapshot *s) {
    memset(s,0,sizeof(*s));
    AudioDeviceID before=0,after=0;
    FMNativeAudioSnapshot a={0};
    if(!default_id(&before)||fm_list_acoustic_outputs(&a)!=0||
       a.truncated||a.count>FM_BIND_MAX) return 0;
    unsigned defaults=0;
    for(unsigned i=0;i<a.count;i++) {
        const FMNativeAudioDevice *d=&a.devices[i];
        FMEndpoint *p=&s->endpoints[i];
        if(!identity(d->device_id,p)) return 0;
        p->channels=d->output_channels; p->rate=d->nominal_rate_hz;
        p->is_default=d->device_id==before;
        defaults+=(unsigned)p->is_default;
    }
    if(!default_id(&after)||after!=before||defaults!=1) return 0;
    s->count=a.count; s->usable=1; return 1;
}
int main(void) {
    FMSnapshot first={0},second={0};
    unsigned index=0;
    if(!capture(&first)) {
        puts("{\"native_binding\":\"METADATA_UNAVAILABLE\",\"snapshots\":0}");
        return 0;
    }
    FMBResult result=fm_binding_select(&first,&index);
    if(result!=FM_B_OK) {
        printf("{\"native_binding\":\"%s\",\"snapshots\":1,\"outputs\":%u}\n",
            result==FM_B_NO_CANDIDATE?"NO_CANDIDATE":"INVALID_METADATA",first.count);
        return 0;
    }
    /* Software-only validation vector. No audio stream, no physical command. */
    FMCommand cmd={FM_ACOUSTIC,1.0,0.5,1000U};
    FMIntegrationRequest req={FM_ACOUSTIC,&cmd,NULL,NULL};
    FMBinding b; fm_binding_init(&b);
    uint64_t now=0,token=0;
    if(!fm_session_clock_ms(&now)||
       fm_binding_prepare(&b,&first,&req,now,&token)!=FM_B_OK) return 2;
    int captured=capture(&second);
    if(!fm_session_clock_ms(&now)) { (void)fm_binding_close(&b,token); return 2; }
    FMBResult refresh=fm_binding_refresh(&b,captured?&second:NULL,token,now);
    int expired=b.sessions.acoustic.state==FM_S_EXPIRED;
    if(fm_binding_close(&b,token)!=FM_B_OK) return 2;
    printf("{\"native_binding\":\"%s\",\"snapshots\":%d,\"outputs\":%u,"
           "\"selected_transport\":\"%s\",\"channels\":%u,\"nominal_rate_hz\":%.17g,"
           "\"session_closed\":true,\"session_expired\":%s}\n",
           refresh==FM_B_OK?"STABLE_AT_REFRESH":refresh==FM_B_CHANGED?"CHANGED_OR_UNREADABLE":"SESSION_ERROR",
           captured?2:1,first.count,first.endpoints[index].route==FM_ROUTE_BUILT_IN?"BUILT_IN":"USB",
           first.endpoints[index].channels,first.endpoints[index].rate,expired?"true":"false");
    return refresh==FM_B_SESSION_ERROR?2:0;
}
