/* SPDX-License-Identifier: Apache-2.0 */
#ifndef FREQMED_ACOUSTIC_PREFLIGHT_R56_H
#define FREQMED_ACOUSTIC_PREFLIGHT_R56_H
#include "generator.h"
#include <stdint.h>
/* Software-only digital route contract. This does NOT open an audio stream. */
typedef struct {
    int32_t result_code; /* 1=OS route and digital envelope matched, NOT authorized to emit */
    uint32_t device_id;
    uint32_t channels;
    double os_rate_hz;
    double requested_hz;
    uint32_t duration_ms;
    uint64_t digital_frame_count;
} FMAcousticPreflight;
int fm_r56_acoustic_preflight(const FMCommand *command, uint32_t device_id,
                             const char *expected_name, uint32_t expected_channels,
                             double expected_os_rate_hz, FMAcousticPreflight *result);
#endif
