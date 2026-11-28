/* SPDX-License-Identifier: Apache-2.0 */
/* Native descriptors only; no device start, registration or setter. */
#include "bench02_prefix.inc"
#include <inttypes.h>
static int descriptor(AudioStreamID id,AudioObjectPropertySelector selector,char side,char kind){
    AudioStreamBasicDescription d={0};
    AudioObjectPropertyAddress a={selector,kAudioObjectPropertyScopeGlobal,kAudioObjectPropertyElementMain};
    UInt32 size=sizeof(d);
    if(AudioObjectGetPropertyData(id,&a,0,NULL,&size,&d)!=noErr||size!=sizeof(d))return 0;
    printf("F\t%c\t%c\t%" PRIu32 "\t%.17g\t%" PRIu32 "\t%" PRIu32 "\t%" PRIu32 "\t%" PRIu32 "\t%" PRIu32 "\t%" PRIu32 "\t%" PRIu32 "\t%d\n",
        side,kind,(uint32_t)id,d.mSampleRate,(uint32_t)d.mFormatID,(uint32_t)d.mFormatFlags,
        (uint32_t)d.mBytesPerPacket,(uint32_t)d.mFramesPerPacket,(uint32_t)d.mBytesPerFrame,
        (uint32_t)d.mChannelsPerFrame,(uint32_t)d.mBitsPerChannel,
        d.mFormatID==kAudioFormatLinearPCM && (d.mFormatFlags & kAudioFormatFlagIsFloat)!=0 &&
        (d.mFormatFlags & (kAudioFormatFlagIsNonInterleaved|kAudioFormatFlagIsBigEndian))==0);
    return 1;
}
static int stream_descriptors(AudioDeviceID id,AudioObjectPropertyScope scope,char side){
    AudioObjectPropertyAddress a={kAudioDevicePropertyStreams,scope,kAudioObjectPropertyElementMain};
    AudioStreamID ids[16]={0};
    UInt32 size=0;
    if(AudioObjectGetPropertyDataSize(id,&a,0,NULL,&size)!=noErr||!size||size>sizeof(ids)||size%sizeof(ids[0]))return 0;
    UInt32 got=size;
    if(AudioObjectGetPropertyData(id,&a,0,NULL,&got,ids)!=noErr||!got||got>size||got%sizeof(ids[0]))return 0;
    for(size_t i=0;i<got/sizeof(ids[0]);i++){
        if(!ids[i]||!descriptor(ids[i],kAudioStreamPropertyVirtualFormat,side,'V')||
           !descriptor(ids[i],kAudioStreamPropertyPhysicalFormat,side,'P'))return 0;
    }
    return 1;
}
int main(void){
    AudioDeviceID in=0,out=0,i=0,o=0;
    if(!defaults(&in,&out)||!in||!out||in==out)return 75;
    if(!endpoint(out,kAudioDevicePropertyScopeOutput,'O')||!endpoint(in,kAudioDevicePropertyScopeInput,'I')||
       !stream_descriptors(out,kAudioDevicePropertyScopeOutput,'O')||
       !stream_descriptors(in,kAudioDevicePropertyScopeInput,'I')||
       !defaults(&i,&o)||i!=in||o!=out)return 75;
    return 0;
}
