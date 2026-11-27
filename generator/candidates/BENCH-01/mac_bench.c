/* SPDX-License-Identifier: Apache-2.0 */
/* Native read-only audio inventory. No streams, setters or device start. */
#include <CoreAudio/CoreAudio.h>
#include <CoreFoundation/CoreFoundation.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "em_hardware_discovery.h"

static int scalar(AudioObjectID id,AudioObjectPropertySelector sel,void *v,UInt32 size) {
    AudioObjectPropertyAddress a={sel,kAudioObjectPropertyScopeGlobal,kAudioObjectPropertyElementMain};
    UInt32 got=size;
    return AudioObjectGetPropertyData(id,&a,0,NULL,&got,v)==noErr && got==size;
}
static int channels(AudioDeviceID id,AudioObjectPropertyScope scope) {
    AudioObjectPropertyAddress a={kAudioDevicePropertyStreamConfiguration,scope,kAudioObjectPropertyElementMain};
    UInt32 size=0;
    if(AudioObjectGetPropertyDataSize(id,&a,0,NULL,&size)!=noErr ||
       size<offsetof(AudioBufferList,mBuffers) || size>65536U)return -1;
    AudioBufferList *p=calloc(1,size);if(!p)return -1;
    UInt32 got=size;int n=-1;
    if(AudioObjectGetPropertyData(id,&a,0,NULL,&got,p)==noErr &&
       got<=size && got>=offsetof(AudioBufferList,mBuffers) &&
       p->mNumberBuffers<=(got-offsetof(AudioBufferList,mBuffers))/sizeof(AudioBuffer)){
        unsigned total=0;n=0;
        for(UInt32 i=0;i<p->mNumberBuffers;i++){
            if(p->mBuffers[i].mNumberChannels>256U-total){n=-1;break;}
            total+=p->mBuffers[i].mNumberChannels;n=(int)total;
        }
    }
    free(p);return n;
}
static const char *route(AudioDeviceID id) {
    UInt32 t=0;if(!scalar(id,kAudioDevicePropertyTransportType,&t,sizeof(t)))return "UNKNOWN";
    switch(t){case kAudioDeviceTransportTypeBuiltIn:return "BUILT_IN";
        case kAudioDeviceTransportTypeUSB:return "USB";
        case kAudioDeviceTransportTypeVirtual:return "VIRTUAL";
        case kAudioDeviceTransportTypeAggregate:return "AGGREGATE";
        case kAudioDeviceTransportTypeBluetooth:return "BLUETOOTH";
        default:return "OTHER";}
}
static int uid(AudioDeviceID id,char *out,size_t cap){
    CFStringRef v=NULL;
    if(!scalar(id,kAudioDevicePropertyDeviceUID,&v,sizeof(v))||!v)return 0;
    int ok=CFGetTypeID(v)==CFStringGetTypeID()&&
        CFStringGetCString(v,out,(CFIndex)cap,kCFStringEncodingUTF8)&&out[0]!=0;
    CFRelease(v);return ok;
}
int main(void){
    AudioObjectPropertyAddress a={kAudioHardwarePropertyDevices,kAudioObjectPropertyScopeGlobal,kAudioObjectPropertyElementMain};
    UInt32 size=0;
    if(AudioObjectGetPropertyDataSize(kAudioObjectSystemObject,&a,0,NULL,&size)!=noErr||
       size==0||size%sizeof(AudioDeviceID)||size>256U*sizeof(AudioDeviceID))return 2;
    AudioDeviceID ids[256],in=0,out=0;UInt32 got=size;
    if(AudioObjectGetPropertyData(kAudioObjectSystemObject,&a,0,NULL,&got,ids)!=noErr||got!=size)return 2;
    if(!scalar(kAudioObjectSystemObject,kAudioHardwarePropertyDefaultInputDevice,&in,sizeof(in))||
       !scalar(kAudioObjectSystemObject,kAudioHardwarePropertyDefaultOutputDevice,&out,sizeof(out)))return 2;
    for(UInt32 i=0;i<size/sizeof(AudioDeviceID);i++){
        char u[1024];Float64 rate=0;UInt32 clock=0,alive=0;AudioDeviceID id=ids[i];
        int known=uid(id,u,sizeof(u));
        int ic=channels(id,kAudioDevicePropertyScopeInput),oc=channels(id,kAudioDevicePropertyScopeOutput);
        int rk=scalar(id,kAudioDevicePropertyNominalSampleRate,&rate,sizeof(rate))&&isfinite(rate)&&rate>0;
        int ck=scalar(id,kAudioDevicePropertyClockDomain,&clock,sizeof(clock));
        int ak=scalar(id,kAudioDevicePropertyDeviceIsAlive,&alive,sizeof(alive))&&alive<=1U;
        printf("A\t%u\t%s\t%d\t%d\t%d\t%d\t%.9g\t%lld\t%d\t",(unsigned)id,route(id),ic,oc,id==in,id==out,rk?rate:0.0,ck?(long long)clock:-1LL,ak?(int)alive:-1);
        if(known)for(const unsigned char *p=(const unsigned char *)u;*p;p++)printf("%02x",(unsigned)*p);
        else printf("-");
        putchar('\n');
    }
    FMEmReadonlyInventory em;
    if(fm_em_discover_readonly(&em)==0){
        printf("E\t%u\t%u\t%u\t%u\t%d\n",em.usb_devices_reported,em.usb_interfaces_reported,em.serial_callout_nodes_reported,em.usbtmc_interfaces_reported,em.listing_truncated);
        for(uint32_t i=0;i<em.candidates_stored;i++){
            const FMEmUsbInterfaceCandidate *p=&em.candidates[i];
            printf("U\t%u\t%u\t%u\t%d\n",p->vendor_id,p->product_id,p->interface_protocol,p->has_vendor_product);
        }
    }else puts("E\tUNKNOWN");
    return 0;
}
