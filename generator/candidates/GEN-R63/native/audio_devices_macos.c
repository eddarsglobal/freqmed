/* SPDX-License-Identifier: Apache-2.0 */
/* FREQMED GEN-R54: LIVE CoreAudio output device metadata, no audio streams.
 * Numeric AudioDeviceID is process-local OS state, not a stable identity.
 * No AudioQueue and no call that starts/stops a physical output appears here.
 */
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "audio_devices.h"

#if defined(__APPLE__)
#include <CoreAudio/CoreAudio.h>
#include <CoreFoundation/CoreFoundation.h>
#include <math.h>
#include <stdlib.h>

static int fm_get_output_channels(AudioDeviceID id, uint32_t *out) {
    AudioObjectPropertyAddress a = {
        kAudioDevicePropertyStreamConfiguration,
        kAudioDevicePropertyScopeOutput,
        kAudioObjectPropertyElementMain
    };
    UInt32 size=0;
    if (AudioObjectGetPropertyDataSize(id,&a,0,NULL,&size)!=noErr ||
        size<offsetof(AudioBufferList,mBuffers) || size>65536U) return -1;
    AudioBufferList *list=(AudioBufferList*)calloc(1U,(size_t)size);
    if (!list) return -1;
    UInt32 got=size;
    OSStatus ret=AudioObjectGetPropertyData(id,&a,0,NULL,&got,list);
    uint32_t channels=0;
    if (ret==noErr && got>=offsetof(AudioBufferList,mBuffers) &&
        list->mNumberBuffers<=(got - offsetof(AudioBufferList,mBuffers))/sizeof(AudioBuffer)) {
        for (UInt32 i=0;i<list->mNumberBuffers;i++) {
            UInt32 n=list->mBuffers[i].mNumberChannels;
            if (n>256U || channels>256U-n) { channels=0; break; }
            channels+=n;
        }
    }
    free(list);
    if (channels==0) return -1;
    *out=channels;
    return 0;
}

static int fm_get_output_rate(AudioDeviceID id, double *out) {
    AudioObjectPropertyAddress a = {
        kAudioDevicePropertyNominalSampleRate,
        kAudioObjectPropertyScopeGlobal,
        kAudioObjectPropertyElementMain
    };
    Float64 rate=0;
    UInt32 size=(UInt32)sizeof(rate);
    if (AudioObjectGetPropertyData(id,&a,0,NULL,&size,&rate)!=noErr ||
        size!=sizeof(rate) || !isfinite(rate) || rate<=0.0) return -1;
    *out=(double)rate;
    return 0;
}

static int fm_get_output_name(AudioDeviceID id, char *out, size_t capacity) {
    AudioObjectPropertyAddress a = {
        kAudioObjectPropertyName,
        kAudioObjectPropertyScopeGlobal,
        kAudioObjectPropertyElementMain
    };
    CFStringRef cf=NULL;
    UInt32 size=(UInt32)sizeof(cf);
    OSStatus ret=AudioObjectGetPropertyData(id,&a,0,NULL,&size,&cf);
    if (ret!=noErr || size!=sizeof(cf) || !cf) return -1;
    Boolean ok=CFStringGetCString(cf,out,(CFIndex)capacity,kCFStringEncodingUTF8);
    CFRelease(cf);
    if (!ok) return -1;
    return 0;
}

int fm_list_acoustic_outputs(FMNativeAudioSnapshot *out) {
    if (!out) return -1;
    memset(out,0,sizeof(*out));
    AudioObjectPropertyAddress adr = {
        kAudioHardwarePropertyDevices,
        kAudioObjectPropertyScopeGlobal,
        kAudioObjectPropertyElementMain
    };
    UInt32 size=0;
    if (AudioObjectGetPropertyDataSize(kAudioObjectSystemObject,&adr,0,NULL,&size)!=noErr ||
        size==0 || size>65536U || size%sizeof(AudioDeviceID)!=0U) return -1;
    AudioDeviceID *ids=(AudioDeviceID*)calloc(1U,(size_t)size);
    if (!ids) return -1;
    UInt32 got=size;
    OSStatus status=AudioObjectGetPropertyData(kAudioObjectSystemObject,&adr,0,NULL,&got,ids);
    if (status!=noErr || got>size || got%sizeof(AudioDeviceID)!=0U) {
        free(ids); return -1;
    }
    AudioDeviceID current=kAudioObjectUnknown;
    AudioObjectPropertyAddress def = {
        kAudioHardwarePropertyDefaultOutputDevice,
        kAudioObjectPropertyScopeGlobal,
        kAudioObjectPropertyElementMain
    };
    UInt32 defsize=(UInt32)sizeof(current);
    if (AudioObjectGetPropertyData(kAudioObjectSystemObject,&def,0,NULL,&defsize,&current)!=noErr ||
        defsize!=sizeof(current)) current=kAudioObjectUnknown;
    for (UInt32 i=0;i<got/sizeof(AudioDeviceID);i++) {
        AudioDeviceID id=ids[i];
        uint32_t channels=0;
        double rate=0;
        if (id==kAudioObjectUnknown || fm_get_output_channels(id,&channels)!=0 ||
            fm_get_output_rate(id,&rate)!=0) continue;
        if (out->count>=FM_AUDIO_MAX_DEVICES) {out->truncated=1;continue;}
        FMNativeAudioDevice *dev=&out->devices[out->count];
        dev->device_id=id;
        dev->output_channels=channels;
        dev->nominal_rate_hz=rate;
        dev->is_default=(id==current)?1:0;
        if (fm_get_output_name(id,dev->name,sizeof(dev->name))!=0)
            (void)strncpy(dev->name,"(name unavailable)",sizeof(dev->name)-1);
        out->count++;
    }
    free(ids);
    return 0;
}
#else
int fm_list_acoustic_outputs(FMNativeAudioSnapshot *out) {
    if (out) memset(out,0,sizeof(*out));
    return -1; /* No invented Linux/macOS devices. */
}
#endif
