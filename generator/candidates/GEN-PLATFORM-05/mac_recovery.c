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

#include "recovery.h"
#include <time.h>
static FMRecovery recovery;
static atomic_uint callback_seen;
typedef struct { AudioObjectID object; AudioObjectPropertyAddress address; int registered; } Watch;
static OSStatus notified(AudioObjectID object,UInt32 count,const AudioObjectPropertyAddress addresses[],void *context) {
    (void)object;(void)count;(void)addresses;
    fm_recovery_notify((FMRecovery *)context);
    atomic_store_explicit(&callback_seen,1U,memory_order_release);
    return noErr;
}
static int remove_all(Watch *w,unsigned n) {
    int ok=1;
    for(unsigned i=n;i>0;i--) {
        Watch *p=&w[i-1];
        if(p->registered) {
            if(AudioObjectRemovePropertyListener(p->object,&p->address,notified,&recovery)!=noErr) ok=0;
            else p->registered=0;
        }
    }
    return ok;
}
static unsigned install(Watch w[5],AudioDeviceID device) {
    const Watch initial[]={
      {kAudioObjectSystemObject,{kAudioHardwarePropertyDevices,kAudioObjectPropertyScopeGlobal,kAudioObjectPropertyElementMain},0},
      {kAudioObjectSystemObject,{kAudioHardwarePropertyDefaultOutputDevice,kAudioObjectPropertyScopeGlobal,kAudioObjectPropertyElementMain},0},
      {device,{kAudioDevicePropertyNominalSampleRate,kAudioObjectPropertyScopeGlobal,kAudioObjectPropertyElementMain},0},
      {device,{kAudioDevicePropertyStreamConfiguration,kAudioDevicePropertyScopeOutput,kAudioObjectPropertyElementMain},0},
      {device,{kAudioDevicePropertyDeviceIsAlive,kAudioObjectPropertyScopeGlobal,kAudioObjectPropertyElementMain},0}
    };
    memcpy(w,initial,sizeof(initial));
    unsigned i=0;
    for(;i<5;i++) {
        if(AudioObjectAddPropertyListener(w[i].object,&w[i].address,notified,&recovery)!=noErr) break;
        w[i].registered=1;
    }
    return i;
}
static int capture_for(AudioDeviceID expected,FMSnapshot *s) {
    AudioDeviceID before=0,after=0;
    return default_id(&before)&&before==expected&&capture(s)&&
        default_id(&after)&&after==expected;
}
static FMRecoveryResult discover(AudioDeviceID device,FMSnapshot *a,FMSnapshot *b) {
    if(fm_recovery_begin(&recovery)!=FM_R_OK) return FM_R_ERROR;
    int first=capture_for(device,a);
    int second=capture_for(device,b);
    return fm_recovery_finish(&recovery,first?a:NULL,second?b:NULL);
}
int main(void) {
    fm_recovery_init(&recovery);atomic_init(&callback_seen,0U);
    Watch w[5]={0};
    FMSnapshot a={0},b={0};
    AudioDeviceID device=0;
    unsigned first_added=0,second_added=0,polls=0;
    int error=0,removed=1,prepared=0,closed=0,invalidated=0,rediscovered=0;
    uint64_t now=0,token=0;
    const char *status="NO_DEFAULT";
    if(default_id(&device)) {
        first_added=install(w,device);
        status="LISTENER_REGISTRATION_FAILED";
        if(first_added==5) {
            status="INITIAL_DISCOVERY_UNAVAILABLE";
            if(discover(device,&a,&b)==FM_R_OK) {
                FMCommand cmd={FM_ACOUSTIC,1.0,0.5,30000U};
                FMIntegrationRequest req={FM_ACOUSTIC,&cmd,NULL,NULL};
                if(!fm_session_clock_ms(&now)) {status="CLOCK_ERROR";error=1;}
                else {
                    FMRecoveryResult p=fm_recovery_prepare(&recovery,&b,&req,now,&token);
                    if(p==FM_R_RETRY) status="INITIAL_PROFILE_CHANGED";
                    else if(p!=FM_R_OK) {status="PREPARE_ERROR";error=1;}
                    else {
                        prepared=1;status="NO_CHANGE_OBSERVED";
                        fputs("Native event observation (100 polls maximum); no device change required.\n",stderr);
                        for(unsigned i=0;i<100;i++) {
                            const struct timespec delay={0,100000000L};
                            if(nanosleep(&delay,NULL)!=0) {status="WAIT_ERROR";error=1;break;}
                            int captured=capture_for(device,&a);
                            if(!fm_session_clock_ms(&now)) {status="CLOCK_ERROR";error=1;break;}
                            FMRecoveryResult q=fm_recovery_poll(&recovery,captured?&a:NULL,token,now);
                            ++polls;
                            if(q==FM_R_INVALIDATED) {invalidated=1;closed=1;status="INVALIDATED";break;}
                            if(q==FM_R_EXPIRED) {closed=1;status="EXPIRED";break;}
                            if(q!=FM_R_OK) {status="POLL_ERROR";error=1;break;}
                        }
                        if(recovery.binding.token) {
                            closed=fm_recovery_close(&recovery,token)==FM_R_OK;
                            if(!closed) error=1;
                        }
                    }
                }
            }
        }
        removed=remove_all(w,5);
        if(!removed) error=1;
        if(invalidated && !error && removed) {
            status="REDISCOVERY_UNAVAILABLE";
            if(default_id(&device)) {
                second_added=install(w,device);
                if(second_added==5) {
                    FMRecoveryResult d=discover(device,&a,&b);
                    if(d==FM_R_OK &&
                       !atomic_load_explicit(&recovery.monitor.pending,memory_order_acquire)) {
                        rediscovered=1;status="PROFILE_REDISCOVERED_NO_SESSION";
                    } else if(d==FM_R_ERROR) error=1;
                }
                removed=remove_all(w,5);
                if(!removed) error=1;
            }
        }
    }
    if(recovery.binding.token) error=1;
    printf("{\"native_recovery\":\"%s\",\"listeners_registered_initial\":%u,"
        "\"listeners_registered_recovery\":%u,\"listeners_removed\":%s,\"polls\":%u,"
        "\"native_callback_observed\":%s,\"session_prepared\":%s,\"old_session_closed\":%s,"
        "\"session_invalidated\":%s,\"profile_rediscovered\":%s,\"new_session_prepared\":false}\n",
        status,first_added,second_added,removed?"true":"false",polls,
        atomic_load_explicit(&callback_seen,memory_order_acquire)?"true":"false",
        prepared?"true":"false",closed?"true":"false",invalidated?"true":"false",
        rediscovered?"true":"false");
    return error?2:0;
}
