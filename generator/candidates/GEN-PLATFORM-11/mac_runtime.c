/* SPDX-License-Identifier: Apache-2.0 */
#include "unified_runtime.h"
#include "session_clock.h"
#include <inttypes.h>
#include <stdio.h>
#include <IOKit/IOKitLib.h>
#include <mach/mach.h>
#include "mac_capture_pinned.inc"
static int input_id(AudioDeviceID *id) {
    AudioObjectPropertyAddress a={kAudioHardwarePropertyDefaultInputDevice,
        kAudioObjectPropertyScopeGlobal,kAudioObjectPropertyElementMain};
    UInt32 n=sizeof(*id);
    return AudioObjectGetPropertyData(kAudioObjectSystemObject,&a,0,NULL,&n,id)==noErr&&
        n==sizeof(*id)&&*id!=kAudioObjectUnknown;
}
static int input_metadata(unsigned *channels_out,FMRoute *route,double *rate) {
    AudioDeviceID id=0,after=0;FMEndpoint p={0};
    if(!input_id(&id)||!identity(id,&p))return 0;
    AudioObjectPropertyAddress a={kAudioDevicePropertyStreamConfiguration,
        kAudioObjectPropertyScopeInput,kAudioObjectPropertyElementMain};
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
    double nominal=0;
    if(!ok||!sum||!scalar(id,kAudioDevicePropertyNominalSampleRate,&nominal,sizeof(nominal))||
       !isfinite(nominal)||nominal<=0||!input_id(&after)||after!=id)return 0;
    *channels_out=sum;*route=p.route;*rate=nominal;return 1;
}
/* Registry class witness only: no identifiers, radio configuration or transmission.
 * Zero matches does not establish hardware absence. */
static const char *registry_class(const char *name) {
    CFMutableDictionaryRef match=IOServiceMatching(name);
    if(!match)return "QUERY_UNAVAILABLE";
    io_iterator_t iter=IO_OBJECT_NULL;
    if(IOServiceGetMatchingServices(MACH_PORT_NULL,match,&iter)!=KERN_SUCCESS)
        return "QUERY_UNAVAILABLE";
    io_service_t service=IOIteratorNext(iter);
    if(service)IOObjectRelease(service);
    IOObjectRelease(iter);
    return service?"CLASS_OBSERVED":"CLASS_NOT_OBSERVED";
}
static const char *route_name(FMRoute r) {
    switch(r){
        case FM_ROUTE_BUILT_IN:return "BUILT_IN";
        case FM_ROUTE_USB:return "USB";
        case FM_ROUTE_VIRTUAL:return "VIRTUAL";
        case FM_ROUTE_OTHER:return "OTHER";
        default:return "UNKNOWN";
    }
}
int main(void) {
    FMRuntime r;fm_runtime_init(&r);
    FMReadinessProfile a={0},b={0},p={0};
    int one=capture(&a),two=capture(&b);
    unsigned captures=(unsigned)(one+two),steps=0,inputs=0;
    double input_rate=0;FMRoute input_route=FM_ROUTE_UNKNOWN;
    int input_ok=input_metadata(&inputs,&input_route,&input_rate);
    const char *wifi=registry_class("IO80211Interface");
    const char *bluetooth=registry_class("IOBluetoothHCIController");
    const char *status="METADATA_NOT_READY";
    uint64_t token=0,now=0,expected=0,consumed=0,blocks=0;
    int completed=0,stopped=0,stale=0,error=0;
    /* Memory-only numerical vector; no physical output or input stream. */
    FMCommand cmd={FM_ACOUSTIC,1000.0,0.25,1000U};
    if(one&&two&&fm_readiness_assess(&a,&b)==FM_RD_METADATA_ONLY) {
        if(!fm_session_clock_ms(&now))error=1;
        else if(fm_runtime_start(&r,&a,&b,&cmd,now,&token)==FM_U_OK) {
            status="RUNTIME_INCOMPLETE";
            while(r.state==FM_U_RUNNING&&steps<256) {
                int got=capture(&p);captures+=(unsigned)got;++steps;
                if(!fm_session_clock_ms(&now)){error=1;break;}
                FMRuntimeResult s=fm_runtime_step(&r,got?&p:NULL,token,now,FM_U_BUDGET_MAX);
                if(s!=FM_U_OK&&s!=FM_U_TERMINAL){error=1;break;}
            }
            expected=r.expected;consumed=r.consumed;blocks=r.blocks;
            completed=r.state==FM_U_COMPLETE&&expected==consumed&&fm_runtime_clean(&r);
            if(r.state==FM_U_FAULT)error=1;
            if(r.state==FM_U_RUNNING)(void)fm_runtime_stop(&r,token);
            stale=fm_runtime_stop(&r,token)==FM_U_STALE;
            if(completed&&!error) {
                one=capture(&a);two=capture(&b);captures+=(unsigned)(one+two);
                uint64_t next=0;
                if(!fm_session_clock_ms(&now))error=1;
                else if(one&&two&&fm_runtime_start(&r,&a,&b,&cmd,now,&next)==FM_U_OK) {
                    int got=capture(&p);captures+=(unsigned)got;
                    if(!fm_session_clock_ms(&now))error=1;
                    else if(fm_runtime_step(&r,got?&p:NULL,next,now,1)==FM_U_OK&&r.lifecycle.count==1) {
                        stale=stale&&fm_runtime_stop(&r,token)==FM_U_STALE;
                        stopped=fm_runtime_stop(&r,next)==FM_U_TERMINAL&&
                            r.state==FM_U_STOPPED&&fm_runtime_clean(&r);
                    }
                    if(r.state==FM_U_RUNNING)(void)fm_runtime_stop(&r,next);
                    if(r.state==FM_U_FAULT)error=1;
                }
            }
        } else if(r.state==FM_U_FAULT)error=1;
    }
    int clean=fm_runtime_clean(&r),backend=fm_acoustic_native_backend_available();
    if(!clean||backend)error=1;
    if(completed&&stopped&&stale&&!error)status="PASS_MEMORY_ONLY_RUNTIME";
    printf("{\"native_runtime\":\"%s\",\"captures_completed\":%u,\"runtime_steps\":%u,"
        "\"expected_samples\":%" PRIu64 ",\"consumed_samples\":%" PRIu64 ",\"consumed_blocks\":%" PRIu64 ","
        "\"normal_completion\":%s,\"explicit_stop\":%s,\"stale_token_rejected\":%s,\"runtime_clean\":%s,"
        "\"physical_backend_available\":%s,\"integrated_inventory\":{\"output_route\":\"%s\","
        "\"default_input_metadata\":%s,\"input_route\":\"%s\",\"input_channels\":%u,\"input_nominal_rate_hz\":",
        error?"NATIVE_ERROR":status,captures,steps,expected,consumed,blocks,
        completed?"true":"false",stopped?"true":"false",stale?"true":"false",clean?"true":"false",
        backend?"true":"false",two?route_name(b.endpoint.route):"UNKNOWN",
        input_ok?"true":"false",input_ok?route_name(input_route):"UNKNOWN",inputs);
    if(input_ok)printf("%.17g",input_rate);else fputs("null",stdout);
    printf(",\"wifi_registry_class\":\"%s\",\"bluetooth_registry_class\":\"%s\","
        "\"radio_generator_qualified\":false,\"microphone_stream_opened\":false}}\n",wifi,bluetooth);
    return error?2:0;
}
