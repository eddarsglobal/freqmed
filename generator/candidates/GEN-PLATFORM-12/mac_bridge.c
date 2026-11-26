/* SPDX-License-Identifier: Apache-2.0 */
#include "integrated_bridge.h"
#include "session_clock.h"
#include <inttypes.h>
#include <stdio.h>
#include <SystemConfiguration/SystemConfiguration.h>
#include <IOKit/IOKitLib.h>
#include <mach/mach.h>
#include "mac_capture_pinned.inc"
static FMIntegratedBridge bridge;
static atomic_uint callbacks;
typedef struct {AudioObjectID object;AudioObjectPropertyAddress address;int installed;} Watch;
static Watch watches[8];
static unsigned watch_count;
static int input_id(AudioDeviceID *id) {
    AudioObjectPropertyAddress a={kAudioHardwarePropertyDefaultInputDevice,
        kAudioObjectPropertyScopeGlobal,kAudioObjectPropertyElementMain};
    UInt32 n=sizeof(*id);
    return AudioObjectGetPropertyData(kAudioObjectSystemObject,&a,0,NULL,&n,id)==noErr&&
        n==sizeof(*id)&&*id!=kAudioObjectUnknown;
}
static int input_channels(AudioDeviceID id,unsigned *out) {
    AudioObjectPropertyAddress a={kAudioDevicePropertyStreamConfiguration,
        kAudioDevicePropertyScopeInput,kAudioObjectPropertyElementMain};
    UInt32 size=0;const size_t header=offsetof(AudioBufferList,mBuffers);
    if(AudioObjectGetPropertyDataSize(id,&a,0,NULL,&size)!=noErr||
       size<header||size>65536U)return 0;
    AudioBufferList *list=calloc(1,size);
    if(!list)return 0;
    UInt32 got=size;
    int ok=AudioObjectGetPropertyData(id,&a,0,NULL,&got,list)==noErr&&
        got>=header&&got<=size&&list->mNumberBuffers<=(got-header)/sizeof(AudioBuffer);
    unsigned sum=0;
    if(ok)for(UInt32 i=0;i<list->mNumberBuffers;i++){
        UInt32 v=list->mBuffers[i].mNumberChannels;
        if(v>256U||sum>256U-v){ok=0;break;}sum+=v;
    }
    free(list);
    if(!ok||!sum)return 0;
    *out=sum;return 1;
}
static int pair_capture(AudioDeviceID output,AudioDeviceID input,FMIntegratedPair *p) {
    memset(p,0,sizeof(*p));
    AudioDeviceID o=0,i=0;
    if(!default_id(&o)||o!=output||!input_id(&i)||i!=input||
       !capture(&p->output)||!identity(input,&p->input)||
       !input_channels(input,&p->input.channels)||
       !scalar(input,kAudioDevicePropertyNominalSampleRate,&p->input.rate,sizeof(Float64)))
        return 0;
    UInt32 alive=0;
    if(scalar(input,kAudioDevicePropertyDeviceIsAlive,&alive,sizeof(alive))&&alive<=1) {
        p->input_alive_known=1;p->input_alive=alive;
    }
    p->input.is_default=1;
    return default_id(&o)&&o==output&&input_id(&i)&&i==input;
}
static OSStatus changed(AudioObjectID object,UInt32 n,const AudioObjectPropertyAddress a[],void *context) {
    (void)object;(void)n;(void)a;(void)context;
    /* Any delivered callback is treated conservatively; no origin attribution. */
    atomic_fetch_add_explicit(&callbacks,1U,memory_order_relaxed);
    fm_bridge_notify(&bridge);return noErr;
}
static int add(AudioObjectID obj,AudioObjectPropertySelector sel,AudioObjectPropertyScope scope) {
    for(unsigned i=0;i<watch_count;i++)
        if(watches[i].object==obj&&watches[i].address.mSelector==sel&&
           watches[i].address.mScope==scope)return 1;
    if(watch_count>=8)return 0;
    Watch *w=&watches[watch_count];
    *w=(Watch){obj,{sel,scope,kAudioObjectPropertyElementMain},0};
    if(AudioObjectAddPropertyListener(obj,&w->address,changed,w)!=noErr)return 0;
    w->installed=1;++watch_count;return 1;
}
static int install(AudioDeviceID output,AudioDeviceID input) {
    return add(kAudioObjectSystemObject,kAudioHardwarePropertyDefaultOutputDevice,kAudioObjectPropertyScopeGlobal)&&
        add(kAudioObjectSystemObject,kAudioHardwarePropertyDefaultInputDevice,kAudioObjectPropertyScopeGlobal)&&
        add(output,kAudioDevicePropertyDeviceIsAlive,kAudioObjectPropertyScopeGlobal)&&
        add(output,kAudioDevicePropertyNominalSampleRate,kAudioObjectPropertyScopeGlobal)&&
        add(output,kAudioDevicePropertyStreamConfiguration,kAudioDevicePropertyScopeOutput)&&
        add(input,kAudioDevicePropertyDeviceIsAlive,kAudioObjectPropertyScopeGlobal)&&
        add(input,kAudioDevicePropertyNominalSampleRate,kAudioObjectPropertyScopeGlobal)&&
        add(input,kAudioDevicePropertyStreamConfiguration,kAudioDevicePropertyScopeInput);
}
static int remove_all(void) {
    int ok=1;
    for(unsigned i=watch_count;i>0;i--) {
        Watch *w=&watches[i-1];
        if(w->installed) {
            if(AudioObjectRemovePropertyListener(w->object,&w->address,changed,w)!=noErr)ok=0;
            else w->installed=0;
        }
    }
    return ok;
}
static const char *wifi_type(void) {
    CFArrayRef a=SCNetworkInterfaceCopyAll();
    if(!a)return "QUERY_UNAVAILABLE";
    int found=0;
    CFIndex count=CFArrayGetCount(a);
    for(CFIndex i=0;i<count;i++) {
        SCNetworkInterfaceRef iface=(SCNetworkInterfaceRef)CFArrayGetValueAtIndex(a,i);
        CFStringRef type=SCNetworkInterfaceGetInterfaceType(iface);
        if(type&&CFEqual(type,kSCNetworkInterfaceTypeIEEE80211)){found=1;break;}
    }
    CFRelease(a);
    return found?"IEEE80211_INTERFACE_OBSERVED":"IEEE80211_INTERFACE_NOT_OBSERVED";
}
static const char *bluetooth_class(void) {
    CFMutableDictionaryRef match=IOServiceMatching("IOBluetoothHCIController");
    if(!match)return "QUERY_UNAVAILABLE";
    io_iterator_t iter=IO_OBJECT_NULL;
    if(IOServiceGetMatchingServices(MACH_PORT_NULL,match,&iter)!=KERN_SUCCESS)return "QUERY_UNAVAILABLE";
    io_service_t service=IOIteratorNext(iter);
    if(service)IOObjectRelease(service);
    IOObjectRelease(iter);
    return service?"CLASS_OBSERVED":"CLASS_NOT_OBSERVED";
}
int main(void) {
    fm_bridge_init(&bridge);atomic_init(&callbacks,0U);
    FMIntegratedPair a={0},b={0},p={0};
    AudioDeviceID output=0,input=0;
    const char *wifi=wifi_type(),*bt=bluetooth_class();
    unsigned captures=0,steps=0;
    uint64_t token=0,now=0;
    int installed=0,prepared=0,matched=0,completed=0,error=0;
    const char *status="NO_DEFAULT_PAIR";
    if(default_id(&output)&&input_id(&input)) {
        installed=install(output,input);
        status="LISTENER_REGISTRATION_FAILED";
        if(installed) {
            int one=pair_capture(output,input,&a),two=pair_capture(output,input,&b);
            captures=(unsigned)(one+two);
            matched=one&&two&&fm_pair_assess(&a,&b)==FM_PAIR_METADATA_ONLY;
            status="PAIR_METADATA_NOT_READY";
            if(matched) {
                /* Memory-only test vector, never sent to hardware. */
                FMCommand cmd={FM_ACOUSTIC,1000.0,0.25,1000U};
                if(!fm_session_clock_ms(&now))error=1;
                else {
                    FMRuntimeResult r=fm_bridge_start(&bridge,&a,&b,&cmd,now,&token);
                    if(r==FM_U_OK) {
                        prepared=1;status="RUNTIME_INCOMPLETE";
                        while(bridge.runtime.state==FM_U_RUNNING&&steps<256) {
                            int got=pair_capture(output,input,&p);captures+=(unsigned)got;++steps;
                            if(!fm_session_clock_ms(&now)){error=1;break;}
                            r=fm_bridge_step(&bridge,got?&p:NULL,token,now,FM_U_BUDGET_MAX);
                            if(r!=FM_U_OK&&r!=FM_U_TERMINAL){error=1;break;}
                        }
                        completed=bridge.runtime.state==FM_U_COMPLETE&&
                            bridge.runtime.expected==bridge.runtime.consumed;
                        if(bridge.runtime.state==FM_U_INVALIDATED)status="PAIR_OR_EVENT_INVALIDATED";
                        if(bridge.runtime.state==FM_U_EXPIRED)status="SESSION_EXPIRED";
                        if(bridge.runtime.state==FM_U_FAULT)error=1;
                        if(bridge.runtime.state==FM_U_RUNNING)(void)fm_bridge_stop(&bridge,token);
                    } else if(r==FM_U_REJECTED)status="START_REJECTED";
                    else error=1;
                }
            }
        }
    }
    int removed=remove_all(),clean=fm_runtime_clean(&bridge.runtime);
    unsigned seen=atomic_load_explicit(&callbacks,memory_order_acquire);
    if(!removed||!clean||fm_acoustic_native_backend_available()!=0)error=1;
    if(completed&&removed&&clean&&!seen&&!error)status="PASS_READONLY_INTEGRATED_BRIDGE";
    else if(completed&&seen&&!error)status="COMPLETED_WITH_NATIVE_NOTIFICATION";
    printf("{\"native_bridge\":\"%s\",\"captures_completed\":%u,\"runtime_steps\":%u,"
        "\"pair_metadata_matched\":%s,\"session_prepared\":%s,\"runtime_completed\":%s,"
        "\"expected_samples\":%" PRIu64 ",\"consumed_samples\":%" PRIu64 ","
        "\"runtime_clean\":%s,\"listeners_registered\":%u,\"listeners_removed\":%s,"
        "\"native_callbacks_observed\":%u,\"runtime_invalidated\":%s,"
        "\"wifi_interface\":\"%s\",\"bluetooth_registry_class\":\"%s\","
        "\"microphone_stream_opened\":false,\"physical_backend_available\":false,"
        "\"radio_generator_qualified\":false}\n",
        error?"NATIVE_ERROR":status,captures,steps,matched?"true":"false",
        prepared?"true":"false",completed?"true":"false",bridge.runtime.expected,bridge.runtime.consumed,
        clean?"true":"false",watch_count,removed?"true":"false",seen,
        bridge.runtime.state==FM_U_INVALIDATED?"true":"false",wifi,bt);
    return error?2:0;
}
