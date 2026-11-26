/* SPDX-License-Identifier: Apache-2.0 */
#include "native_format.h"
#include "session_clock.h"
#include <inttypes.h>
#include <stdio.h>
#include "mac_capture_pinned.inc"
#include "mac_pair_pinned.inc"

static int read_format(AudioStreamID id,AudioObjectPropertySelector selector,FMNativeFormat *f) {
    AudioStreamBasicDescription d={0};
    if(!scalar(id,selector,&d,sizeof(d)))return 0;
    *f=(FMNativeFormat){d.mSampleRate,d.mFormatID,d.mFormatFlags,d.mBytesPerPacket,
        d.mFramesPerPacket,d.mBytesPerFrame,d.mChannelsPerFrame,d.mBitsPerChannel,
        d.mFormatID==kAudioFormatLinearPCM};
    return 1;
}
static int streams(AudioDeviceID id,AudioObjectPropertyScope scope,FMStreamSet *out) {
    AudioObjectPropertyAddress a={kAudioDevicePropertyStreams,scope,kAudioObjectPropertyElementMain};
    AudioStreamID ids[FM_STREAM_CAP]={0};
    UInt32 size=0;
    memset(out,0,sizeof(*out));
    if(AudioObjectGetPropertyDataSize(id,&a,0,NULL,&size)!=noErr||
       !size||size>sizeof(ids)||size%sizeof(ids[0]))return 0;
    UInt32 got=size;
    if(AudioObjectGetPropertyData(id,&a,0,NULL,&got,ids)!=noErr||
       !got||got>size||got%sizeof(ids[0]))return 0;
    unsigned count=got/sizeof(ids[0]);
    for(unsigned i=0;i<count;i++) {
        FMStream *s=&out->streams[i];
        s->local_id=ids[i];
        if(!s->local_id||!read_format(ids[i],kAudioStreamPropertyVirtualFormat,&s->logical)||
           !read_format(ids[i],kAudioStreamPropertyPhysicalFormat,&s->physical))return 0;
    }
    out->count=count;return 1;
}
static int profile(AudioDeviceID output,AudioDeviceID input,FMNativeIOProfile *p) {
    memset(p,0,sizeof(*p));
    AudioDeviceID o=0,i=0;
    return pair_capture(output,input,&p->pair)&&
        streams(output,kAudioObjectPropertyScopeOutput,&p->output)&&
        streams(input,kAudioObjectPropertyScopeInput,&p->input)&&
        default_id(&o)&&o==output&&input_id(&i)&&i==input;
}
static void print_format(const FMNativeFormat *f) {
    fputs("{\"rate_hz\":",stdout);
    if(isfinite(f->rate))printf("%.17g",f->rate);else fputs("null",stdout);
    printf(",\"format_id\":%" PRIu32 ",\"flags\":%" PRIu32 ",\"channels\":%" PRIu32
        ",\"bits_per_channel\":%" PRIu32 ",\"bytes_per_frame\":%" PRIu32
        ",\"bytes_per_packet\":%" PRIu32 ",\"frames_per_packet\":%" PRIu32
        ",\"linear_pcm\":%s}",f->format_id,f->flags,f->channels,f->bits,
        f->bytes_frame,f->bytes_packet,f->frames_packet,f->linear_pcm?"true":"false");
}
static void print_streams(const FMStreamSet *s) {
    putchar('[');
    for(unsigned i=0;i<s->count;i++){
        if(i)putchar(',');
        fputs("{\"logical\":",stdout);print_format(&s->streams[i].logical);
        fputs(",\"physical\":",stdout);print_format(&s->streams[i].physical);
        putchar('}');
    }
    putchar(']');
}
int main(void) {
    FMIntegratedBridge bridge;fm_bridge_init(&bridge);
    FMNativeIOProfile a={0},b={0},p={0};
    AudioDeviceID out=0,in=0;
    uint64_t now=0,token=0;
    unsigned captures=0,steps=0;
    int matched=0,prepared=0,completed=0,error=0,changed=0;
    const char *status="NO_DEFAULT_PAIR";
    if(default_id(&out)&&input_id(&in)){
        int first=profile(out,in,&a),second=profile(out,in,&b);
        captures=(unsigned)(first+second);
        matched=first&&second&&fm_native_assess(&a,&b)==FM_N_METADATA_ONLY;
        status="NATIVE_FORMAT_NOT_READY";
        if(matched){
            /* No audio data is sent to or acquired from the device. */
            FMCommand cmd={FM_ACOUSTIC,1000.0,0.25,1000U};
            if(!fm_session_clock_ms(&now))error=1;
            else {
                FMRuntimeResult r=fm_bridge_start(&bridge,&a.pair,&b.pair,&cmd,now,&token);
                if(r==FM_U_OK){
                    prepared=1;status="RUNTIME_INCOMPLETE";
                    while(bridge.runtime.state==FM_U_RUNNING&&steps<256){
                        int got=profile(out,in,&p);captures+=(unsigned)got;++steps;
                        if(!fm_session_clock_ms(&now)){error=1;break;}
                        int stable=got&&fm_native_assess(&b,&p)==FM_N_METADATA_ONLY;
                        if(!stable){changed=1;fm_bridge_notify(&bridge);}
                        r=fm_bridge_step(&bridge,stable?&p.pair:NULL,token,now,FM_U_BUDGET_MAX);
                        if(r!=FM_U_OK&&r!=FM_U_TERMINAL){error=1;break;}
                    }
                    completed=bridge.runtime.state==FM_U_COMPLETE&&
                        bridge.runtime.expected==bridge.runtime.consumed;
                    if(bridge.runtime.state==FM_U_INVALIDATED)status="FORMAT_OR_PAIR_INVALIDATED";
                    if(bridge.runtime.state==FM_U_EXPIRED)status="SESSION_EXPIRED";
                    if(bridge.runtime.state==FM_U_FAULT)error=1;
                    if(bridge.runtime.state==FM_U_RUNNING)(void)fm_bridge_stop(&bridge,token);
                } else if(r!=FM_U_REJECTED)error=1;
            }
        }
    }
    int clean=fm_runtime_clean(&bridge.runtime),backend=fm_acoustic_native_backend_available();
    if(!clean||backend)error=1;
    if(completed&&matched&&clean&&!changed&&!error)status="PASS_READONLY_NATIVE_FORMAT_CONTRACT";
    printf("{\"native_backend_preparation\":\"%s\",\"captures_completed\":%u,"
        "\"runtime_steps\":%u,\"format_metadata_matched\":%s,\"session_prepared\":%s,"
        "\"runtime_completed\":%s,\"runtime_clean\":%s,\"format_or_pair_changed\":%s,"
        "\"expected_samples\":%" PRIu64 ",\"consumed_samples\":%" PRIu64 ","
        "\"output_streams\":",error?"NATIVE_ERROR":status,captures,steps,matched?"true":"false",
        prepared?"true":"false",completed?"true":"false",clean?"true":"false",changed?"true":"false",
        bridge.runtime.expected,bridge.runtime.consumed);
    print_streams(&b.output);fputs(",\"input_streams\":",stdout);print_streams(&b.input);
    puts(",\"microphone_stream_opened\":false,\"output_stream_opened\":false,"
        "\"physical_backend_available\":false,\"physical_calibration_verified\":false}");
    return error?2:0;
}
