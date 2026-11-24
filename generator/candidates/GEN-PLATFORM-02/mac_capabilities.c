/* SPDX-License-Identifier: Apache-2.0 */
#include "audio_devices.h"
#include "em_hardware_discovery.h"
#include <CoreAudio/CoreAudio.h>
#include <math.h>
#include <stdio.h>

static const char *transport(AudioDeviceID id) {
    AudioObjectPropertyAddress a={kAudioDevicePropertyTransportType,
        kAudioObjectPropertyScopeGlobal,kAudioObjectPropertyElementMain};
    UInt32 t=0,n=sizeof(t);
    if (AudioObjectGetPropertyData(id,&a,0,NULL,&n,&t)!=noErr || n!=sizeof(t))
        return "UNKNOWN";
    switch(t) {
        case kAudioDeviceTransportTypeBuiltIn: return "BUILT_IN";
        case kAudioDeviceTransportTypeUSB: return "USB";
        case kAudioDeviceTransportTypeBluetooth: return "BLUETOOTH";
        case kAudioDeviceTransportTypeVirtual: return "VIRTUAL";
        case kAudioDeviceTransportTypeAggregate: return "AGGREGATE";
        default: return "OTHER_OS_REPORTED";
    }
}
int main(void) {
    FMNativeAudioSnapshot a={0};
    FMEmReadonlyInventory e={0};
    int ar=fm_list_acoustic_outputs(&a);
    int er=fm_em_discover_readonly(&e);
    if (ar || a.count>FM_AUDIO_MAX_DEVICES) {
        printf("{\"audio_status\":\"UNAVAILABLE\",\"audio_profiles\":null,");
    } else {
        printf("{\"audio_status\":\"%s\",\"audio_profiles\":[",a.truncated?"PARTIAL":"OBSERVED");
        for (unsigned i=0;i<a.count;i++) {
            const FMNativeAudioDevice *d=&a.devices[i];
            if (!isfinite(d->nominal_rate_hz) || d->nominal_rate_hz<=0 ||
                d->output_channels==0 || d->output_channels>256) return 2;
            printf("%s{\"index\":%u,\"channels\":%u,\"sample_rate_hz\":%.17g,"
                   "\"format_source\":\"COREAUDIO_NOMINAL\",\"transport\":\"%s\","
                   "\"default\":%s}",i?",":"",i+1,(unsigned)d->output_channels,
                   d->nominal_rate_hz,transport(d->device_id),d->is_default?"true":"false");
        }
        printf("],");
    }
    if (er || e.candidates_stored>FM_EM_USB_CANDIDATES_CAP) {
        printf("\"em_status\":\"UNAVAILABLE\",\"em_candidates\":null,\"serial_nodes\":null,"
               "\"usbtmc_count\":null}\n");
    } else {
        printf("\"em_status\":\"%s\",\"serial_nodes\":%u,\"usbtmc_count\":%u,"
               "\"em_candidates\":[",e.listing_truncated?"PARTIAL":"OBSERVED",
               (unsigned)e.serial_callout_nodes_reported,(unsigned)e.usbtmc_interfaces_reported);
        for (unsigned i=0;i<e.candidates_stored;i++) {
            const FMEmUsbInterfaceCandidate *c=&e.candidates[i];
            printf("%s{\"index\":%u,\"transport\":\"USBTMC\",\"protocol\":%u,"
                   "\"vendor_id\":",i?",":"",i+1,(unsigned)c->interface_protocol);
            if(c->has_vendor_product) printf("%u,\"product_id\":%u}",
                (unsigned)c->vendor_id,(unsigned)c->product_id);
            else printf("null,\"product_id\":null}");
        }
        printf("]}\n");
    }
    return 0;
}
