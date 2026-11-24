/* SPDX-License-Identifier: Apache-2.0 */
#include "audio_devices.h"
#include "em_hardware_discovery.h"
#include <stdio.h>
int main(void) {
    FMNativeAudioSnapshot a={0};
    FMEmReadonlyInventory e={0};
    int ar=fm_list_acoustic_outputs(&a);
    int er=fm_em_discover_readonly(&e);
    if (ar==0 && a.count<=FM_AUDIO_MAX_DEVICES) {
        unsigned defaults=0;
        for (unsigned i=0;i<a.count;i++) if (a.devices[i].is_default) ++defaults;
        printf("{\"audio_status\":\"OBSERVED\",\"audio_outputs\":%u,"
               "\"audio_default_count\":%u,\"audio_truncated\":%s,",
               (unsigned)a.count,defaults,a.truncated?"true":"false");
    } else {
        printf("{\"audio_status\":\"UNAVAILABLE\",\"audio_outputs\":null,"
               "\"audio_default_count\":null,\"audio_truncated\":null,");
    }
    if (er==0 && e.candidates_stored<=FM_EM_USB_CANDIDATES_CAP) {
        printf("\"usb_status\":\"OBSERVED\",\"usb_devices\":%u,"
               "\"usb_interfaces\":%u,\"serial_nodes\":%u,"
               "\"usbtmc_signatures\":%u,\"em_listing_truncated\":%s}\n",
               (unsigned)e.usb_devices_reported,(unsigned)e.usb_interfaces_reported,
               (unsigned)e.serial_callout_nodes_reported,(unsigned)e.usbtmc_interfaces_reported,
               e.listing_truncated?"true":"false");
    } else {
        printf("\"usb_status\":\"UNAVAILABLE\",\"usb_devices\":null,"
               "\"usb_interfaces\":null,\"serial_nodes\":null,"
               "\"usbtmc_signatures\":null,\"em_listing_truncated\":null}\n");
    }
    return 0;
}
