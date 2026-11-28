/* SPDX-License-Identifier: Apache-2.0 */
/* Only property notifications and private RAM; no IOProc, start, setter or stream. */
#define _POSIX_C_SOURCE 200809L
#include "digital_signal.h"
#include "session_clock.h"
#include "transport.h"
#include "rt_queue.h"
#include "output_resource.h"
#include "mac_rt_prefix.inc"
#include <stdatomic.h>
typedef struct { AudioObjectID id; AudioObjectPropertyAddress a; } Watch;
static Watch watches[9];
static size_t count;
static atomic_uint changed_flag;
static OSStatus changed(AudioObjectID id,UInt32 n,const AudioObjectPropertyAddress *a,void *context){
    (void)id;(void)n;(void)a;(void)context;
    atomic_store_explicit(&changed_flag,1,memory_order_release);return noErr;
}
static int watch(AudioObjectID id,AudioObjectPropertySelector selector,AudioObjectPropertyScope scope){
    AudioObjectPropertyAddress a={selector,scope,kAudioObjectPropertyElementMain};
    if(count>=sizeof(watches)/sizeof(watches[0]))return 0;
    if(AudioObjectAddPropertyListener(id,&a,changed,NULL)!=noErr)return 0;
    watches[count++]=(Watch){id,a};return 1;
}
static size_t unwatch(void){
    size_t removed=0;
    while(count){Watch w=watches[--count];if(AudioObjectRemovePropertyListener(w.id,&w.a,changed,NULL)==noErr)removed++;}
    return removed;
}
static int one_stream(AudioDeviceID id,AudioStreamID *stream){
    AudioObjectPropertyAddress a={kAudioDevicePropertyStreams,kAudioObjectPropertyScopeOutput,kAudioObjectPropertyElementMain};
    UInt32 size=0;
    if(AudioObjectGetPropertyDataSize(id,&a,0,NULL,&size)!=noErr||size!=sizeof(*stream))return 0;
    return AudioObjectGetPropertyData(id,&a,0,NULL,&size,stream)==noErr&&size==sizeof(*stream)&&*stream!=0;
}
static int format(AudioStreamID stream,AudioObjectPropertySelector selector,uint32_t frames,FMOutputSpec *s){
    AudioStreamBasicDescription d={0};
    if(!scalar(stream,selector,&d,sizeof(d)))return 0;
    *s=(FMOutputSpec){d.mSampleRate,frames,d.mChannelsPerFrame,d.mFormatID,d.mFormatFlags,d.mBitsPerChannel,
        d.mBytesPerFrame,d.mFramesPerPacket,d.mBytesPerPacket};
    return 1;
}
static int same(const FMOutputSpec *a,const FMOutputSpec *b){
    return a->rate==b->rate&&a->frames==b->frames&&a->channels==b->channels&&a->format==b->format&&
        a->flags==b->flags&&a->bits==b->bits&&a->bytes_frame==b->bytes_frame&&
        a->frames_packet==b->frames_packet&&a->bytes_packet==b->bytes_packet;
}
static int snapshot(AudioDeviceID device,AudioStreamID stream,const FMReadinessProfile *p,FMOutputSpec *v,FMOutputSpec *physical){
    AudioDeviceID current=0;AudioStreamID s=0;
    return default_id(&current)&&current==device&&one_stream(device,&s)&&s==stream&&
        format(stream,kAudioStreamPropertyVirtualFormat,p->buffer_frames,v)&&
        format(stream,kAudioStreamPropertyPhysicalFormat,p->buffer_frames,physical)&&
        fm_output_compatible(v)&&fm_output_compatible(physical)&&same(v,physical)&&
        v->rate==p->endpoint.rate&&v->channels==p->endpoint.channels&&
        default_id(&current)&&current==device;
}
int main(void){
    FMDigital d;fm_digital_init(&d);
    FMReadinessProfile a={0},b={0},fresh={0};
    InputMetadata ia={0},ib={0};
    FMOutputSpec initial={0},physical={0},current={0},pcurrent={0};
    AudioDeviceID device=0;AudioStreamID stream=0;
    FMOutputResource *r=NULL;float *dst=NULL;double mono[FM_DIGITAL_BLOCK_MAX];
    size_t values=0,blocks=0,frames=0,registered=0,removed=0;
    uint64_t token=0,now=0;int ok=0,closed=0,guardian=0;
    const char *reason="METADATA_NOT_READY";
    atomic_init(&changed_flag,0);
    if(!default_id(&device)||!one_stream(device,&stream)||!input_capture(&ia)||ia.id==device)goto done;
    reason="SUBSCRIPTION_FAILED";
    if(!watch(kAudioObjectSystemObject,kAudioHardwarePropertyDefaultOutputDevice,kAudioObjectPropertyScopeGlobal)||
       !watch(kAudioObjectSystemObject,kAudioHardwarePropertyDefaultInputDevice,kAudioObjectPropertyScopeGlobal)||
       !watch(device,kAudioDevicePropertyDeviceIsAlive,kAudioObjectPropertyScopeGlobal)||
       !watch(device,kAudioDevicePropertyNominalSampleRate,kAudioObjectPropertyScopeGlobal)||
       !watch(device,kAudioDevicePropertyBufferFrameSize,kAudioObjectPropertyScopeGlobal)||
       !watch(device,kAudioDevicePropertyDeviceIsRunningSomewhere,kAudioObjectPropertyScopeGlobal)||
       !watch(device,kAudioDevicePropertyStreams,kAudioObjectPropertyScopeOutput)||
       !watch(stream,kAudioStreamPropertyVirtualFormat,kAudioObjectPropertyScopeGlobal)||
       !watch(stream,kAudioStreamPropertyPhysicalFormat,kAudioObjectPropertyScopeGlobal))goto done;
    reason="FORMAT_NOT_READY";
    if(!capture(&a)||!capture(&b)||fm_readiness_assess(&a,&b)!=FM_RD_METADATA_ONLY||
       !snapshot(device,stream,&a,&initial,&physical)||!snapshot(device,stream,&b,&current,&pcurrent)||
       !same(&initial,&current)||!same(&physical,&pcurrent))goto done;
    if(atomic_load_explicit(&changed_flag,memory_order_acquire)){reason="PROPERTY_CHANGED";goto done;}
    frames=initial.frames;values=frames*initial.channels;
    r=fm_output_create(&initial);dst=calloc(values,sizeof(float));
    reason="RESOURCE_ALLOCATION_FAILED";
    if(!r||!dst)goto done;
    AudioBufferList list={0};list.mNumberBuffers=1;
    list.mBuffers[0].mNumberChannels=initial.channels;
    list.mBuffers[0].mDataByteSize=(UInt32)(values*sizeof(float));list.mBuffers[0].mData=dst;
    /* Existing numerical command path, private memory only. */
    FMCommand cmd={FM_ACOUSTIC,1000.0,0.25,1000U};
    reason="DIGITAL_PREPARE_FAILED";
    if(!fm_session_clock_ms(&now)||fm_digital_prepare(&d,&a,&b,&cmd,now,&token)!=FM_D_OK)goto done;
    for(unsigned k=0;k<2;k++){
        size_t written=0;
        reason="PROFILE_OR_FORMAT_CHANGED";
        if(atomic_load_explicit(&changed_flag,memory_order_acquire)||!capture(&fresh)||
           fm_readiness_assess(&b,&fresh)!=FM_RD_METADATA_ONLY||
           !snapshot(device,stream,&fresh,&current,&pcurrent)||!same(&initial,&current)||!same(&physical,&pcurrent))goto done;
        reason="DIGITAL_BLOCK_FAILED";
        if(!fm_session_clock_ms(&now)||fm_digital_block(&d,&fresh,token,now,mono,FM_DIGITAL_BLOCK_MAX,frames,&written)!=FM_D_OK||written!=frames)goto done;
        reason="RESOURCE_TRANSFER_FAILED";
        if(!fm_output_submit(r,mono,written)||atomic_load_explicit(&changed_flag,memory_order_acquire)||
           !fm_output_read(r,&current,list.mBuffers[0].mData,values))goto done;
        for(size_t i=0;i<frames;i++)for(size_t j=0;j<initial.channels;j++)
            if(dst[i*initial.channels+j]!=(float)mono[i])goto done;
        blocks++;
    }
    reason="FINAL_PROFILE_CHANGED";
    if(!input_capture(&ib)||!input_equal(&ia,&ib)||!capture(&fresh)||
       fm_readiness_assess(&b,&fresh)!=FM_RD_METADATA_ONLY||
       !snapshot(device,stream,&fresh,&current,&pcurrent)||!same(&initial,&current)||!same(&physical,&pcurrent))goto done;
    ok=1;reason="NONE";
done:
    if(d.assembly.recovery.binding.token&&fm_digital_stop(&d,token)!=FM_D_OK){ok=0;reason="DIGITAL_STOP_FAILED";}
    guardian=d.assembly.state==FM_A_OFF&&!d.assembly.recovery.binding.token&&
        d.assembly.guardian.state==FM_OFF&&!d.assembly.guardian.physical_output_enabled&&fm_acoustic_native_backend_available()==0;
    fm_output_stop(r);closed=fm_output_closed(r);fm_output_destroy(r);free(dst);
    registered=count;removed=unwatch();
    int event=atomic_load_explicit(&changed_flag,memory_order_acquire)!=0;
    if(event){ok=0;reason="PROPERTY_CHANGED";}
    if(registered!=removed){ok=0;reason="SUBSCRIPTION_CLEANUP_FAILED";}
    if(!guardian||!closed){ok=0;if(blocks==2)reason="RESOURCE_CLEANUP_FAILED";}
    printf("{\"status\":\"%s\",\"reason\":\"%s\",\"nominal_rate_hz\":%.17g,\"frames\":%zu,\"channels\":%u,"
        "\"blocks\":%zu,\"numerical_frames\":%zu,\"float_values\":%zu,\"registered\":%zu,\"removed\":%zu,"
        "\"property_change_observed\":%s,\"resources_closed\":%s,\"guardian_off\":%s,"
        "\"destination\":\"PRIVATE_RAM_ONLY\",\"audio_ioproc_registered\":false,\"stream_opened\":false,"
        "\"physical_output\":\"NOT_PERFORMED\",\"authorization\":\"NONE\"}\n",
        ok?"PASS_PRIVATE_OUTPUT_RESOURCE":"BLOCK",reason,initial.rate,frames,(unsigned)initial.channels,
        blocks,blocks*frames,blocks*values,registered,removed,event?"true":"false",closed?"true":"false",guardian?"true":"false");
    return ok?0:75;
}
