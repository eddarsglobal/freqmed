/* SPDX-License-Identifier: Apache-2.0 */
/* GEN-R57: same-route admission for existing SOURCE-ONLY backend that obtains
 * a fingerprint of macOS's DEFAULT output. This module only reads CoreAudio
 * metadata. No AudioQueue, no PCM, no start/stop calls, no output symbol.
 */
#include "acoustic_backend_route_r57.h"
#include "acoustic_preflight_r56.h"
#include <math.h>
#include <string.h>
#if defined(__APPLE__)
#include <CoreAudio/CoreAudio.h>
static int current_default(uint32_t *out) {
    if (!out) return -1;
    AudioDeviceID dev=kAudioObjectUnknown;
    const AudioObjectPropertyAddress key={kAudioHardwarePropertyDefaultOutputDevice,
        kAudioObjectPropertyScopeGlobal,kAudioObjectPropertyElementMain};
    UInt32 n=(UInt32)sizeof(dev);
    if (AudioObjectGetPropertyData(kAudioObjectSystemObject,&key,0,NULL,&n,&dev)!=noErr ||
        n!=sizeof(dev) || dev==kAudioObjectUnknown) return -1;
    *out=(uint32_t)dev;
    return 0;
}
#endif
int fm_r57_backend_route_check(const FMCommand *command,uint32_t expected_device_id,
    const char *expected_name,uint32_t expected_channels,double expected_rate_hz,
    FMR57BackendRouteCheck *out) {
    if (!out) return -1;
    memset(out,0,sizeof(*out));
    out->result_code=4; /* fail closed when OS metadata cannot be obtained */
    FMAcousticPreflight plan={0};
    if (fm_r56_acoustic_preflight(command,expected_device_id,expected_name,
            expected_channels,expected_rate_hz,&plan)!=0) return -1;
    if (plan.result_code!=1) { out->result_code=plan.result_code; return 0; }
#if defined(__APPLE__)
    uint32_t before=0,after=0;
    if (current_default(&before)!=0) return 0;
    if (before!=expected_device_id) {out->result_code=8;return 0;}
    FMOutputCapabilities caps={0};
    if (fm_acoustic_readonly_probe(&caps)!=0 || caps.metadata_observed!=1 ||
        caps.output_channels!=expected_channels ||
        !isfinite(caps.nominal_sample_rate_hz) ||
        caps.nominal_sample_rate_hz!=expected_rate_hz) {
        out->result_code=9;return 0;
    }
    if (current_default(&after)!=0 || after!=before) {
        out->result_code=9;return 0;
    }
    out->nominal_rate_hz=caps.nominal_sample_rate_hz;
    out->digital_frame_budget=plan.digital_frame_count;
    out->default_route_matches=1;
    out->result_code=1;
#else
    (void)expected_device_id;
#endif
    return 0;
}
