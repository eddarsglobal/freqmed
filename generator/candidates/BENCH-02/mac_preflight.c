/* SPDX-License-Identifier: Apache-2.0 */
/* Native metadata adapter only; no IOProc, streams, setters, or starts. */
#include "bench01_prefix.inc"

static long long prop(AudioObjectID id, AudioObjectPropertySelector sel,
                      AudioObjectPropertyScope scope) {
    AudioObjectPropertyAddress a={sel,scope,kAudioObjectPropertyElementMain};
    UInt32 v=0, size=sizeof(v);
    if(AudioObjectGetPropertyData(id,&a,0,NULL,&size,&v)!=noErr || size!=sizeof(v))return -1;
    return (long long)v;
}
static int endpoint(AudioDeviceID id, AudioObjectPropertyScope scope, char side) {
    char u[1024]; Float64 rate=0;
    if(!id || !uid(id,u,sizeof(u)))return 0;
    int n=channels(id,scope);
    long long clock=prop(id,kAudioDevicePropertyClockDomain,kAudioObjectPropertyScopeGlobal);
    long long alive=prop(id,kAudioDevicePropertyDeviceIsAlive,kAudioObjectPropertyScopeGlobal);
    long long frames=prop(id,kAudioDevicePropertyBufferFrameSize,kAudioObjectPropertyScopeGlobal);
    long long latency=prop(id,kAudioDevicePropertyLatency,scope);
    long long safety=prop(id,kAudioDevicePropertySafetyOffset,scope);
    long long running=prop(id,kAudioDevicePropertyDeviceIsRunningSomewhere,kAudioObjectPropertyScopeGlobal);
    if(!scalar(id,kAudioDevicePropertyNominalSampleRate,&rate,sizeof(rate))||!isfinite(rate)||rate<=0)return 0;
    printf("%c\t%u\t%s\t%d\t%.17g\t%lld\t%lld\t%lld\t%lld\t%lld\t%lld\t",side,(unsigned)id,route(id),n,rate,clock,alive,frames,latency,safety,running);
    for(const unsigned char *p=(const unsigned char *)u;*p;p++)printf("%02x",(unsigned)*p);
    putchar('\n');return 1;
}
static int defaults(AudioDeviceID *in,AudioDeviceID *out){
    return scalar(kAudioObjectSystemObject,kAudioHardwarePropertyDefaultInputDevice,in,sizeof(*in)) &&
           scalar(kAudioObjectSystemObject,kAudioHardwarePropertyDefaultOutputDevice,out,sizeof(*out));
}
int main(void){
    AudioDeviceID in=0,out=0,again_in=0,again_out=0;
    if(!defaults(&in,&out)||!endpoint(out,kAudioDevicePropertyScopeOutput,'O')||
       !endpoint(in,kAudioDevicePropertyScopeInput,'I')||!defaults(&again_in,&again_out)||
       in!=again_in||out!=again_out)return 2;
    return 0;
}
