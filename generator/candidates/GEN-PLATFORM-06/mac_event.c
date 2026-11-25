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
#include "event_evidence.h"
#include <time.h>
#include <inttypes.h>
static FMRecovery recovery;
static FMEventLatch latch;
static atomic_uint observing;
typedef struct { AudioObjectID object; AudioObjectPropertyAddress address; unsigned category; int registered; } Watch;
static Watch initial[5],retry[5];
static OSStatus notified(AudioObjectID object,UInt32 count,const AudioObjectPropertyAddress addresses[],void *context) {
    const Watch *w=context;
    unsigned matched=0;
    if(w && object==w->object && addresses && count<=128) {
        for(UInt32 i=0;i<count;i++)
            if(addresses[i].mSelector==w->address.mSelector &&
               addresses[i].mScope==w->address.mScope &&
               addresses[i].mElement==w->address.mElement) matched=w->category;
    }
    if(atomic_load_explicit(&observing,memory_order_acquire) && matched) {
        uint64_t now=0;
        if(fm_session_clock_ms(&now)) {
            (void)fm_event_record(&latch,matched,now);
            return noErr;
        }
    }
    /* Unclassified/early/late events still invalidate conservatively;
       they cannot establish a classified native event receipt. */
    fm_recovery_notify(&recovery);
    return noErr;
}
static unsigned install(Watch w[5],AudioDeviceID device) {
    const Watch defs[]={
      {kAudioObjectSystemObject,{kAudioHardwarePropertyDevices,kAudioObjectPropertyScopeGlobal,kAudioObjectPropertyElementMain},1,0},
      {kAudioObjectSystemObject,{kAudioHardwarePropertyDefaultOutputDevice,kAudioObjectPropertyScopeGlobal,kAudioObjectPropertyElementMain},2,0},
      {device,{kAudioDevicePropertyNominalSampleRate,kAudioObjectPropertyScopeGlobal,kAudioObjectPropertyElementMain},4,0},
      {device,{kAudioDevicePropertyStreamConfiguration,kAudioDevicePropertyScopeOutput,kAudioObjectPropertyElementMain},8,0},
      {device,{kAudioDevicePropertyDeviceIsAlive,kAudioObjectPropertyScopeGlobal,kAudioObjectPropertyElementMain},16,0}
    };
    memcpy(w,defs,sizeof(defs));
    unsigned i=0;
    for(;i<5;i++) {
        if(AudioObjectAddPropertyListener(w[i].object,&w[i].address,notified,&w[i])!=noErr) break;
        w[i].registered=1;
    }
    return i;
}
static int remove_all(Watch w[5]) {
    int ok=1;
    for(unsigned i=5;i>0;i--) {
        Watch *p=&w[i-1];
        if(p->registered) {
            if(AudioObjectRemovePropertyListener(p->object,&p->address,notified,p)!=noErr) ok=0;
            else p->registered=0;
        }
    }
    return ok;
}
static int capture_for(AudioDeviceID expected,FMSnapshot *s) {
    AudioDeviceID before=0,after=0;
    return default_id(&before)&&before==expected&&capture(s)&&
        default_id(&after)&&after==expected;
}
static FMRecoveryResult discover(AudioDeviceID device,FMSnapshot *a,FMSnapshot *b) {
    if(fm_recovery_begin(&recovery)!=FM_R_OK) return FM_R_ERROR;
    int first=capture_for(device,a),second=capture_for(device,b);
    return fm_recovery_finish(&recovery,first?a:NULL,second?b:NULL);
}
int main(void) {
    fm_recovery_init(&recovery);fm_event_init(&latch);atomic_init(&observing,0U);
    FMSnapshot a={0},b={0};
    FMEventEvidence e={0};
    FMEvent ev={0};
    AudioDeviceID device=0;
    uint64_t now=0,token=0;
    unsigned added=0,readded=0,polls=0;
    int error=0,event_consumed=0,other_invalidated=0;
    const char *status="NO_DEFAULT";
    if(default_id(&device)) {
        added=install(initial,device);
        status="LISTENER_REGISTRATION_FAILED";
        if(added==5) {
            status="INITIAL_DISCOVERY_UNAVAILABLE";
            if(discover(device,&a,&b)==FM_R_OK) {
                /* Structural software test only; no output APIs. */
                FMCommand cmd={FM_ACOUSTIC,1.0,0.5,120000U};
                FMIntegrationRequest req={FM_ACOUSTIC,&cmd,NULL,NULL};
                if(!fm_session_clock_ms(&now)) error=1;
                else if(fm_recovery_prepare(&recovery,&b,&req,now,&token)==FM_R_OK) {
                    e.prepared=1;e.prepared_ms=now;
                    if(!fm_event_arm(&latch)) error=1;
                    else {
                        atomic_store_explicit(&observing,1U,memory_order_release);
                        status="NO_CLASSIFIED_EVENT_OBSERVED";
                        fputs("READY_FOR_NATIVE_EVENT: 60-second observation maximum; no audio output.\n",stderr);
                        for(unsigned i=0;i<600;i++) {
                            const struct timespec delay={0,100000000L};
                            if(nanosleep(&delay,NULL)!=0) {error=1;break;}
                            if(!fm_session_clock_ms(&now)) {error=1;break;}
                            ++polls;
                            int captured=capture_for(device,&a);
                            if(fm_event_read(&latch,&ev)) {
                                if(!fm_session_clock_ms(&now)) {error=1;break;}
                                e.category=ev.category;e.event_ms=ev.ms;
                                /* Explicit handoff of the real callback to the single owner.
                                 * Use the prior valid snapshot; invalidation here is event-driven. */
                                fm_recovery_notify(&recovery);
                                FMRecoveryResult q=fm_recovery_poll(&recovery,&b,token,now);
                                e.consumed_ms=now;
                                if(q==FM_R_INVALIDATED) {
                                    event_consumed=1;e.invalidated=1;
                                    e.closed=recovery.binding.token==0 &&
                                        recovery.binding.sessions.acoustic.state==FM_S_EMPTY;
                                    e.stale_rejected=fm_recovery_poll(&recovery,&b,token,now)==FM_R_STALE;
                                    status="EVENT_INVALIDATED";
                                } else {status="EVENT_HANDOFF_FAILED";error=1;}
                                break;
                            }
                            if(!fm_session_clock_ms(&now)) {error=1;break;}
                            /* A late callback may arrive after this check. Do not
                               attribute an unclassified invalidation to that event. */
                            FMRecoveryResult q=fm_recovery_poll(&recovery,captured?&a:NULL,token,now);
                            if(q==FM_R_INVALIDATED) {
                                other_invalidated=1;status="INVALIDATED_WITHOUT_EVENT_HANDOFF";break;
                            }
                            if(q==FM_R_EXPIRED) {status="SESSION_EXPIRED";break;}
                            if(q!=FM_R_OK) {error=1;break;}
                        }
                    }
                } else status="INITIAL_PREPARE_UNAVAILABLE";
            }
        }
    }
    atomic_store_explicit(&observing,0U,memory_order_release);
    if(recovery.binding.token && fm_recovery_close(&recovery,token)!=FM_R_OK) error=1;
    int removed=remove_all(initial);
    if(!removed) error=1;
    if(event_consumed && !error && removed) {
        status="EVENT_INVALIDATED_REDISCOVERY_UNAVAILABLE";
        /* One bounded retry window, only when a valid new default is present.
         * Two coherent snapshots are still required; no new session prepared. */
        for(unsigned i=0;i<30;i++) {
            if(default_id(&device)&&capture_for(device,&a)) {
                unsigned index=0;
                if(fm_binding_select(&a,&index)==FM_B_OK) {
                    readded=install(retry,device);
                    if(readded==5 && discover(device,&a,&b)==FM_R_OK &&
                       !atomic_load_explicit(&recovery.monitor.pending,memory_order_acquire)) {
                        if(fm_session_clock_ms(&now)) {
                            e.rediscovered=1;e.rediscovered_ms=now;
                        } else error=1;
                    }
                    if(!remove_all(retry)) {removed=0;error=1;}
                    break;
                }
            }
            const struct timespec delay={0,500000000L};
            if(nanosleep(&delay,NULL)!=0) {error=1;break;}
        }
    }
    e.new_session=recovery.binding.token!=0;
    e.cleanup=removed && !error;
    int complete=fm_event_evidence_complete(&e);
    if(complete) status="PASS_NATIVE_EVENT_RECOVERY";
    else if(error) status="NATIVE_ERROR";
    printf("{\"native_event_verdict\":\"%s\",\"event_complete\":%s,\"category_mask\":%u,"
        "\"prepared_ms\":%" PRIu64 ",\"event_ms\":%" PRIu64 ",\"consumed_ms\":%" PRIu64 ","
        "\"rediscovered_ms\":%" PRIu64 ",\"listeners_registered_initial\":%u,"
        "\"listeners_registered_recovery\":%u,\"listeners_removed\":%s,\"polls\":%u,"
        "\"event_consumed\":%s,\"other_invalidation\":%s,\"old_session_closed_on_event\":%s,"
        "\"stale_token_rejected\":%s,\"profile_rediscovered\":%s,\"new_session_prepared\":%s}\n",
        status,complete?"true":"false",e.category,e.prepared_ms,e.event_ms,e.consumed_ms,e.rediscovered_ms,
        added,readded,removed?"true":"false",polls,event_consumed?"true":"false",
        other_invalidated?"true":"false",e.closed?"true":"false",e.stale_rejected?"true":"false",
        e.rediscovered?"true":"false",e.new_session?"true":"false");
    return error?2:0;
}
