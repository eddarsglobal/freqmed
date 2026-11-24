#define _POSIX_C_SOURCE 200809L
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

#include "monitor.h"
#include <time.h>
static FMMonitor monitor;
static atomic_uint callback_seen;
typedef struct { AudioObjectID object; AudioObjectPropertyAddress address; int registered; } Watch;
static OSStatus notified(AudioObjectID object,UInt32 count,const AudioObjectPropertyAddress addresses[],void *context) {
    (void)object;(void)count;(void)addresses;
    fm_monitor_mark((FMMonitor *)context);
    atomic_store_explicit(&callback_seen,1U,memory_order_release);
    return noErr;
}
static int remove_all(Watch *w,unsigned n) {
    int ok=1;
    for(unsigned i=n;i>0;i--) {
        Watch *p=&w[i-1];
        if(p->registered) {
            if(AudioObjectRemovePropertyListener(p->object,&p->address,notified,&monitor)!=noErr) ok=0;
            else p->registered=0;
        }
    }
    return ok;
}
int main(void) {
    fm_monitor_init(&monitor);
    atomic_init(&callback_seen,0U);
    AudioDeviceID device=0,check=0;
    if(!default_id(&device)) {
        puts("{\"native_monitor\":\"NO_DEFAULT\",\"listeners_registered\":0,\"listeners_removed\":true}");
        return 0;
    }
    Watch watches[]={
      {kAudioObjectSystemObject,{kAudioHardwarePropertyDevices,kAudioObjectPropertyScopeGlobal,kAudioObjectPropertyElementMain},0},
      {kAudioObjectSystemObject,{kAudioHardwarePropertyDefaultOutputDevice,kAudioObjectPropertyScopeGlobal,kAudioObjectPropertyElementMain},0},
      {device,{kAudioDevicePropertyNominalSampleRate,kAudioObjectPropertyScopeGlobal,kAudioObjectPropertyElementMain},0},
      {device,{kAudioDevicePropertyStreamConfiguration,kAudioDevicePropertyScopeOutput,kAudioObjectPropertyElementMain},0},
      {device,{kAudioDevicePropertyDeviceIsAlive,kAudioObjectPropertyScopeGlobal,kAudioObjectPropertyElementMain},0},
    };
    const unsigned n=sizeof(watches)/sizeof(watches[0]);
    unsigned added=0, polls=0;
    const char *status="LISTENER_REGISTRATION_FAILED";
    int error=0,closed=0,prepared=0;
    uint64_t now=0,token=0;
    FMSnapshot s={0};
    FMBinding b;fm_binding_init(&b);
    for(;added<n;added++) {
        Watch *w=&watches[added];
        if(AudioObjectAddPropertyListener(w->object,&w->address,notified,&monitor)!=noErr) break;
        w->registered=1;
    }
    if(added==n) {
        unsigned index=0;
        if(!capture(&s)||!default_id(&check)||check!=device) status="SNAPSHOT_UNAVAILABLE";
        else if(fm_binding_select(&s,&index)!=FM_B_OK) status="NO_ELIGIBLE_ENDPOINT";
        else {
            /* Software-only session vector; never passed to an output API. */
            FMCommand cmd={FM_ACOUSTIC,1.0,0.5,5000U};
            FMIntegrationRequest req={FM_ACOUSTIC,&cmd,NULL,NULL};
            if(!fm_session_clock_ms(&now)||
               fm_binding_prepare(&b,&s,&req,now,&token)!=FM_B_OK) {
                status="SESSION_PREPARE_FAILED";error=1;
            } else {
                prepared=1;status="NO_CHANGE_OBSERVED";
                for(unsigned i=0;i<20;i++) {
                    struct timespec delay={0,50000000L};
                    if(nanosleep(&delay,NULL)!=0) {status="WAIT_INTERRUPTED";error=1;break;}
                    int captured=capture(&s);
                    if(!fm_session_clock_ms(&now)) {status="CLOCK_FAILED";error=1;break;}
                    FMMonitorResult r=fm_monitor_poll(&monitor,&b,captured?&s:NULL,token,now);
                    ++polls;
                    if(r==FM_M_INVALIDATED) {status="SESSION_INVALIDATED";break;}
                    if(r==FM_M_EXPIRED) {status="SESSION_EXPIRED";break;}
                    if(r!=FM_M_STABLE) {status="SESSION_ERROR";error=1;break;}
                }
            }
        }
    }
    /* Remove exact registrations before exit; static callback storage remains alive. */
    int removed=remove_all(watches,n);
    if(prepared) {
        closed=fm_binding_close(&b,token)==FM_B_OK;
        if(!closed) error=1;
    }
    if(!removed) error=1;
    printf("{\"native_monitor\":\"%s\",\"listeners_registered\":%u,"
           "\"listeners_removed\":%s,\"polls\":%u,\"native_callback_observed\":%s,"
           "\"session_prepared\":%s,\"session_closed\":%s}\n",
           status,added,removed?"true":"false",polls,
           atomic_load_explicit(&callback_seen,memory_order_acquire)?"true":"false",
           prepared?"true":"false",closed?"true":"false");
    return error?2:0;
}
