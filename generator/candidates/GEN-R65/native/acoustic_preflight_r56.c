/* SPDX-License-Identifier: Apache-2.0 */
/* R56: bind one requested acoustic command to one live CoreAudio route using
 * real OS metadata. No PCM samples, AudioQueue, hardware output, measurement,
 * simulation or physical authorization can occur in this translation unit.
 */
#include "acoustic_preflight_r56.h"
#include "audio_devices.h"
#include <math.h>
#include <stddef.h>
#include <string.h>

static int fm_r56_name_too_long(const char *p) {
    for (size_t i=0;i<FM_AUDIO_LABEL_MAX;i++) if (p[i]=='\0') return 0;
    return 1;
}

/* Result: 1=valid digital plan for OS route, 2=invalid command,
 * 3=route mismatch, 4=OS unavailable, 5=sample-rate constraint,
 * 6=bounded digital frame envelope exceeded, 7=invalid route metadata.
 * Even result 1 is NEVER an authorization to emit. */
int fm_r56_acoustic_preflight(const FMCommand *command, uint32_t device_id,
                             const char *expected_name, uint32_t expected_channels,
                             double expected_os_rate_hz, FMAcousticPreflight *out) {
    if (!out) return -1;
    memset(out,0,sizeof(*out));
    out->result_code=7;
    if (!command || command->channel!=FM_ACOUSTIC ||
        !fm_validate_command(command,NULL,0)) {out->result_code=2;return 0;}
    if (device_id==0U || !expected_name || !expected_name[0] ||
        fm_r56_name_too_long(expected_name) ||
        expected_channels==0U || expected_channels>256U ||
        !isfinite(expected_os_rate_hz) || expected_os_rate_hz<=0.0) return 0;
    FMNativeAudioSnapshot snap;
    if (fm_list_acoustic_outputs(&snap)!=0 || snap.count>FM_AUDIO_MAX_DEVICES) {
        out->result_code=4;return 0;
    }
    if (snap.truncated) {out->result_code=3;return 0;}
    const FMNativeAudioDevice *match=NULL;
    for(uint32_t i=0U;i<snap.count;i++) if(snap.devices[i].device_id==device_id) {
        match=&snap.devices[i];break;
    }
    if(!match || match->output_channels!=expected_channels ||
       strcmp(match->name,expected_name)!=0 ||
       match->nominal_rate_hz!=expected_os_rate_hz) {out->result_code=3;return 0;}
    out->device_id=match->device_id;
    out->channels=match->output_channels;
    out->os_rate_hz=match->nominal_rate_hz;
    out->requested_hz=command->frequency_hz;
    out->duration_ms=command->duration_ms;
    /* Nyquist is a digital encoding constraint, NOT a proof the transducer
     * can emit this frequency, acoustic calibration, or exposure safety. */
    if (!isfinite(match->nominal_rate_hz) || match->nominal_rate_hz<=0.0 ||
        !(command->frequency_hz<match->nominal_rate_hz/2.0)) {
        out->result_code=5;return 0;
    }
    /* Bound prospective memory/scheduling *without allocating a buffer*. */
    const double frames=ceil((match->nominal_rate_hz*(double)command->duration_ms)/1000.0);
    if (!isfinite(frames) || frames<1.0 || frames>4000000.0 ||
        command->duration_ms>30000U) {out->result_code=6;return 0;}
    out->digital_frame_count=(uint64_t)frames;
    out->result_code=1;
    return 0;
}
