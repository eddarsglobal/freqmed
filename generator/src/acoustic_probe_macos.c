/* SPDX-License-Identifier: Apache-2.0 */
/* Actual CoreAudio read-only metadata query: no AudioQueue, no device start,
   no microphone, no signal generation, no sensitive device identifier. */
#include "generator.h"
#include <string.h>
#if defined(__APPLE__)
#include <CoreAudio/CoreAudio.h>
#include <math.h>
#include <stdlib.h>
#include <stddef.h>
#include <stdint.h>

int fm_acoustic_readonly_probe(FMOutputCapabilities *out) {
  if (!out) return -1;
  memset(out,0,sizeof(*out));
  const AudioObjectPropertyAddress def = {
    kAudioHardwarePropertyDefaultOutputDevice,
    kAudioObjectPropertyScopeGlobal,
    kAudioObjectPropertyElementMaster
  };
  AudioDeviceID dev = kAudioObjectUnknown;
  UInt32 n=(UInt32)sizeof(dev);
  if (AudioObjectGetPropertyData(kAudioObjectSystemObject,&def,0,NULL,&n,&dev)!=noErr ||
      n!=sizeof(dev) || dev==kAudioObjectUnknown) return -1;

  const AudioObjectPropertyAddress rate_address={
    kAudioDevicePropertyNominalSampleRate,
    kAudioObjectPropertyScopeGlobal,
    kAudioObjectPropertyElementMaster
  };
  Float64 sample_rate=0.0;
  n=(UInt32)sizeof(sample_rate);
  if (AudioObjectGetPropertyData(dev,&rate_address,0,NULL,&n,&sample_rate)!=noErr ||
      n!=sizeof(sample_rate) || !isfinite(sample_rate) || sample_rate<=0.0) return -1;

  const AudioObjectPropertyAddress config_address={
    kAudioDevicePropertyStreamConfiguration,
    kAudioDevicePropertyScopeOutput,
    kAudioObjectPropertyElementMaster
  };
  UInt32 size=0;
  if (AudioObjectGetPropertyDataSize(dev,&config_address,0,NULL,&size)!=noErr ||
      size<offsetof(AudioBufferList,mBuffers) || size>65536U) return -1;
  /* Apple's API uses a variable-size AudioBufferList. Never assume 1 buffer. */
  AudioBufferList *list=(AudioBufferList*)calloc(1U,(size_t)size);
  if (!list) return -1;
  UInt32 received=size;
  OSStatus ret=AudioObjectGetPropertyData(dev,&config_address,0,NULL,&received,list);
  unsigned channels=0;
  if (ret==noErr && received>=offsetof(AudioBufferList,mBuffers) &&
      list->mNumberBuffers<=
        (received - offsetof(AudioBufferList,mBuffers))/sizeof(AudioBuffer)) {
    for (UInt32 i=0;i<list->mNumberBuffers;i++) {
      const UInt32 v=list->mBuffers[i].mNumberChannels;
      if (v==0 || v>256U || channels>256U-v) {channels=0;break;}
      channels+=v;
    }
  }
  free(list);
  if (channels==0) return -1;
  out->output_channels=channels;
  out->nominal_sample_rate_hz=sample_rate;
  out->metadata_observed=1;
  return 0;
}
#else
int fm_acoustic_readonly_probe(FMOutputCapabilities *out) {
  if (out) memset(out,0,sizeof(*out));
  return -1;
}
#endif
