/* SPDX-License-Identifier: Apache-2.0 */
/* CoreAudio metadata and private AudioBufferList only. No IOProc or stream. */
#define _POSIX_C_SOURCE 200809L
#include "digital_signal.h"
#include "session_clock.h"
#include "transport.h"
#include "mac_capture_pinned.inc"
typedef struct { AudioDeviceID id; FMEndpoint ep; UInt32 frames; } InputMetadata;
static int input_capture(InputMetadata *p){
    AudioObjectPropertyAddress a={kAudioHardwarePropertyDefaultInputDevice,kAudioObjectPropertyScopeGlobal,kAudioObjectPropertyElementMain};
    UInt32 size=sizeof(p->id); AudioDeviceID after=0;
    memset(p,0,sizeof(*p));
    if(AudioObjectGetPropertyData(kAudioObjectSystemObject,&a,0,NULL,&size,&p->id)!=noErr||size!=sizeof(p->id)||!p->id)return 0;
    if(!identity(p->id,&p->ep)||(p->ep.route!=FM_ROUTE_BUILT_IN&&p->ep.route!=FM_ROUTE_USB))return 0;
    UInt32 alive=0,running=1;
    if(!scalar(p->id,kAudioDevicePropertyDeviceIsAlive,&alive,sizeof(alive))||alive!=1||
       !scalar(p->id,kAudioDevicePropertyDeviceIsRunningSomewhere,&running,sizeof(running))||running!=0||
       !scalar(p->id,kAudioDevicePropertyNominalSampleRate,&p->ep.rate,sizeof(Float64))||
       !isfinite(p->ep.rate)||p->ep.rate<=0||
       !scalar(p->id,kAudioDevicePropertyBufferFrameSize,&p->frames,sizeof(p->frames))||
       !p->frames||p->frames>16384)return 0;
    AudioObjectPropertyAddress cfg={kAudioDevicePropertyStreamConfiguration,kAudioDevicePropertyScopeInput,kAudioObjectPropertyElementMain};
    size=0;
    const size_t header=offsetof(AudioBufferList,mBuffers);
    if(AudioObjectGetPropertyDataSize(p->id,&cfg,0,NULL,&size)!=noErr||size<header||size>65536)return 0;
    AudioBufferList *list=calloc(1,size);if(!list)return 0;
    UInt32 got=size;
    int ok=AudioObjectGetPropertyData(p->id,&cfg,0,NULL,&got,list)==noErr&&got>=header&&got<=size&&
        list->mNumberBuffers<=(got-header)/sizeof(AudioBuffer);
    unsigned sum=0;
    if(ok)for(UInt32 k=0;k<list->mNumberBuffers;k++){
        UInt32 n=list->mBuffers[k].mNumberChannels;
        if(n>64U-sum){ok=0;break;}sum+=n;
    }
    free(list);p->ep.channels=sum;
    size=sizeof(after);
    return ok&&sum&&AudioObjectGetPropertyData(kAudioObjectSystemObject,&a,0,NULL,&size,&after)==noErr&&size==sizeof(after)&&after==p->id;
}
static int input_equal(const InputMetadata *a,const InputMetadata *b){
    return a->id==b->id&&a->frames==b->frames&&a->ep.channels==b->ep.channels&&
        a->ep.rate==b->ep.rate&&a->ep.route==b->ep.route&&!strcmp(a->ep.uid,b->ep.uid);
}
/* Contract for an interleaved float32 consumer backed exclusively by private RAM.
 * The list is constructed by this executable, not delivered by CoreAudio. */
static int consume_private(FMTransport *t,AudioBufferList *list,size_t frames,size_t channels,size_t *written){
    if(!list||list->mNumberBuffers!=1||list->mBuffers[0].mNumberChannels!=channels||
       !list->mBuffers[0].mData||list->mBuffers[0].mDataByteSize!=frames*channels*sizeof(float))return 0;
    return fm_transport_take(t,list->mBuffers[0].mData,frames*channels,written);
}
int main(void){
    FMDigital d;fm_digital_init(&d);
    FMReadinessProfile a={0},b={0},fresh={0};
    InputMetadata ia={0},ib={0};
    FMTransport *t=NULL;float *out=NULL;double mono[FM_DIGITAL_BLOCK_MAX];
    uint64_t token=0,now=0;size_t frames=0,channels_out=0,total=0,blocks=0;
    int ok=0,nonzero=0,closed=0;const char *reason="NATIVE_METADATA_NOT_READY";
    if(!input_capture(&ia)||!capture(&a)||!capture(&b)||fm_readiness_assess(&a,&b)!=FM_RD_METADATA_ONLY)goto done;
    frames=b.buffer_frames;channels_out=b.endpoint.channels;
    if(!frames||frames>FM_DIGITAL_BLOCK_MAX||!channels_out||channels_out>64) {reason="UNSUPPORTED_DIMENSIONS";goto done;}
    t=fm_transport_create(ia.frames,ia.ep.channels,(uint32_t)frames,(uint32_t)channels_out);
    out=calloc(frames*channels_out,sizeof(float));
    if(!t||!out){reason="ALLOCATION_FAILED";goto done;}
    AudioBufferList list={0};
    list.mNumberBuffers=1;list.mBuffers[0].mNumberChannels=(UInt32)channels_out;
    list.mBuffers[0].mDataByteSize=(UInt32)(frames*channels_out*sizeof(float));list.mBuffers[0].mData=out;
    /* Numerical software qualification vector, never routed to hardware. */
    FMCommand cmd={FM_ACOUSTIC,1000.0,0.25,1000U};
    reason="DIGITAL_PREPARE_FAILED";
    if(!fm_session_clock_ms(&now)||fm_digital_prepare(&d,&a,&b,&cmd,now,&token)!=FM_D_OK)goto done;
    for(unsigned k=0;k<2;k++){
        size_t written=0,taken=0;
        reason="DIGITAL_BLOCK_FAILED";
        if(!capture(&fresh)||!fm_session_clock_ms(&now)||
           fm_digital_block(&d,&fresh,token,now,mono,FM_DIGITAL_BLOCK_MAX,frames,&written)!=FM_D_OK||written!=frames)goto done;
        reason="TRANSPORT_FAILED";
        if(!fm_transport_push(t,mono,written)||!consume_private(t,&list,frames,channels_out,&taken)||taken!=written)goto done;
        for(size_t i=0;i<frames;i++){
            if(!isfinite(mono[i])||fabs(mono[i])>0.25)goto done;
            if(mono[i]!=0)nonzero=1;
            for(size_t c=0;c<channels_out;c++)if(out[i*channels_out+c]!=(float)mono[i])goto done;
        }
        total+=taken;blocks++;
    }
    reason="INPUT_METADATA_CHANGED";
    if(!input_capture(&ib)||!input_equal(&ia,&ib)||!nonzero)goto done;
    ok=1;reason="NONE";
done:
    if(d.assembly.recovery.binding.token&&fm_digital_stop(&d,token)!=FM_D_OK)ok=0;
    closed=d.assembly.state==FM_A_OFF&&!d.assembly.recovery.binding.token&&
        d.assembly.guardian.state==FM_OFF&&!d.assembly.guardian.physical_output_enabled;
    fm_transport_stop(t);fm_transport_destroy(t);free(out);
    if(!closed||fm_acoustic_native_backend_available()!=0){ok=0;reason="GUARDIAN_NOT_OFF";}
    printf("{\"status\":\"%s\",\"reason\":\"%s\",\"nominal_rate_hz\":%.17g,\"input_frames\":%u,\"input_channels\":%u,"
        "\"output_frames\":%zu,\"output_channels\":%zu,\"blocks\":%zu,\"numerical_frames\":%zu,"
        "\"guardian_off\":%s,\"destination\":\"PRIVATE_RAM_ONLY\",\"audio_ioproc_registered\":false,"
        "\"stream_opened\":false,\"physical_output\":\"NOT_PERFORMED\",\"physical_measurement\":\"NOT_PERFORMED\","
        "\"authorization\":\"NONE\",\"certification\":\"NOT_ISSUED\"}\n",
        ok?"PASS_MEMORY_ONLY_NATIVE_PROFILE":"BLOCK",reason,b.endpoint.rate,(unsigned)ia.frames,ia.ep.channels,
        frames,channels_out,blocks,total,closed?"true":"false");
    return ok?0:75;
}
