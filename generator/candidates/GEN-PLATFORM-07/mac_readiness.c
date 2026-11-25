#define _POSIX_C_SOURCE 200809L
/* SPDX-License-Identifier: Apache-2.0 */
#include "binding.h"
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
#include "readiness.h"
#include <math.h>
#include <stddef.h>
#include <stdlib.h>
static int scalar(AudioDeviceID id,AudioObjectPropertySelector sel,void *p,UInt32 size) {
    AudioObjectPropertyAddress a={sel,kAudioObjectPropertyScopeGlobal,kAudioObjectPropertyElementMain};
    UInt32 got=size;
    return AudioObjectGetPropertyData(id,&a,0,NULL,&got,p)==noErr&&got==size;
}
static int channels(AudioDeviceID id,unsigned *out) {
    AudioObjectPropertyAddress a={kAudioDevicePropertyStreamConfiguration,
        kAudioDevicePropertyScopeOutput,kAudioObjectPropertyElementMain};
    UInt32 size=0;
    const size_t header=offsetof(AudioBufferList,mBuffers);
    if(AudioObjectGetPropertyDataSize(id,&a,0,NULL,&size)!=noErr||
       size<header||size>65536U) return 0;
    AudioBufferList *p=calloc(1,size);
    if(!p) return 0;
    UInt32 got=size;
    int ok=AudioObjectGetPropertyData(id,&a,0,NULL,&got,p)==noErr&&
        got>=header&&got<=size&&p->mNumberBuffers<=(got-header)/sizeof(AudioBuffer);
    unsigned sum=0;
    if(ok) for(UInt32 i=0;i<p->mNumberBuffers;i++) {
        UInt32 v=p->mBuffers[i].mNumberChannels;
        if(v>256U||sum>256U-v){ok=0;break;}
        sum+=v;
    }
    free(p);
    if(!ok||!sum) return 0;
    *out=sum;return 1;
}
static void rate_ranges(AudioDeviceID id,FMReadinessProfile *p) {
    AudioObjectPropertyAddress a={kAudioDevicePropertyAvailableNominalSampleRates,
        kAudioObjectPropertyScopeGlobal,kAudioObjectPropertyElementMain};
    AudioValueRange rows[FM_RATE_CAP]={0};
    UInt32 size=0;
    if(AudioObjectGetPropertyDataSize(id,&a,0,NULL,&size)!=noErr||
       !size||size>sizeof(rows)||size%sizeof(rows[0])) return;
    UInt32 got=size;
    if(AudioObjectGetPropertyData(id,&a,0,NULL,&got,rows)!=noErr||
       !got||got>size||got%sizeof(rows[0])) return;
    p->range_count=got/sizeof(rows[0]);
    for(unsigned i=0;i<p->range_count;i++)
        p->rates[i]=(FMRateRange){rows[i].mMinimum,rows[i].mMaximum};
    p->ranges_known=1;
}
static int capture(FMReadinessProfile *p) {
    memset(p,0,sizeof(*p));
    AudioDeviceID id=0,after=0;
    if(!default_id(&id)||!identity(id,&p->endpoint)||
       !channels(id,&p->endpoint.channels)||
       !scalar(id,kAudioDevicePropertyNominalSampleRate,&p->endpoint.rate,sizeof(Float64)))
        return 0;
    p->endpoint.is_default=1;
    UInt32 v=0;
    if(scalar(id,kAudioDevicePropertyDeviceIsAlive,&v,sizeof(v))&&v<=1) {
        p->alive_known=1;p->alive=v;
    }
    v=0;
    if(scalar(id,kAudioDevicePropertyDeviceIsRunningSomewhere,&v,sizeof(v))&&v<=1) {
        p->running_known=1;p->running=v;
    }
    v=0;
    if(scalar(id,kAudioDevicePropertyBufferFrameSize,&v,sizeof(v))) {
        p->buffer_known=1;p->buffer_frames=v;
    }
    AudioValueRange range={0};
    if(scalar(id,kAudioDevicePropertyBufferFrameSizeRange,&range,sizeof(range))) {
        p->buffer_range_known=1;p->buffer_min=range.mMinimum;p->buffer_max=range.mMaximum;
    }
    rate_ranges(id,p);
    return default_id(&after)&&id==after;
}
static const char *verdict(FMReadinessResult r) {
    switch(r) {
        case FM_RD_METADATA_ONLY:return "PASS_READONLY_METADATA";
        case FM_RD_INCONSISTENT:return "INCONSISTENT_METADATA";
        case FM_RD_CHANGED:return "PROFILE_CHANGED";
        case FM_RD_NOT_CANDIDATE:return "NOT_ELIGIBLE";
        case FM_RD_BUSY:return "OUTPUT_REPORTED_RUNNING";
        default:return "INCOMPLETE_METADATA";
    }
}
static void number(double v) {if(isfinite(v)) printf("%.17g",v);else fputs("null",stdout);}
static const char *tri(unsigned known,unsigned v) {return known?(v?"true":"false"):"null";}
int main(void) {
    FMReadinessProfile a={0},b={0};
    int ca=capture(&a),cb=capture(&b);
    FMReadinessResult r=fm_readiness_assess(ca?&a:NULL,cb?&b:NULL);
    printf("{\"native_readiness\":\"%s\",\"captures_completed\":%d,",verdict(r),ca+cb);
    if(!cb) {
        puts("\"profile\":null,\"physical_ready\":false,\"independent_stop_verified\":false}");
        return 0;
    }
    const char *transport=b.endpoint.route==FM_ROUTE_BUILT_IN?"BUILT_IN":
        b.endpoint.route==FM_ROUTE_USB?"USB":b.endpoint.route==FM_ROUTE_VIRTUAL?"VIRTUAL":
        b.endpoint.route==FM_ROUTE_UNKNOWN?"UNKNOWN":"OTHER";
    printf("\"profile\":{\"transport\":\"%s\",\"channels\":%u,\"nominal_sample_rate_hz\":",
        transport,b.endpoint.channels);
    number(b.endpoint.rate);
    printf(",\"alive\":%s,\"running_somewhere\":%s,\"buffer_frames\":",
        tri(b.alive_known,b.alive),tri(b.running_known,b.running));
    if(b.buffer_known) printf("%u",b.buffer_frames);else fputs("null",stdout);
    fputs(",\"buffer_range_frames\":",stdout);
    if(b.buffer_range_known) {
        putchar('[');number(b.buffer_min);putchar(',');number(b.buffer_max);putchar(']');
    } else fputs("null",stdout);
    fputs(",\"available_nominal_sample_rate_ranges_hz\":",stdout);
    if(b.ranges_known) {
        putchar('[');
        for(unsigned i=0;i<b.range_count;i++) {
            if(i) putchar(',');
            putchar('[');number(b.rates[i].minimum);putchar(',');number(b.rates[i].maximum);putchar(']');
        }
        putchar(']');
    } else fputs("null",stdout);
    puts("},\"physical_ready\":false,\"independent_stop_verified\":false}");
    return 0;
}
