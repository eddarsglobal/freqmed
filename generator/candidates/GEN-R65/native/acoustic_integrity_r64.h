/* SPDX-License-Identifier: Apache-2.0 */
#ifndef FREQMED_ACOUSTIC_INTEGRITY_R64_H
#define FREQMED_ACOUSTIC_INTEGRITY_R64_H
#include <stdint.h>
/* Read-only digital engineering check. No OS, no speakers, no measurements. */
typedef struct {
    uint64_t checked_samples;
    uint32_t channels;
    float digital_peak_normalized;
    uint32_t zero_edges;
} FMR64DigitalIntegrity;
/* Return 1 only for bounded finite PCM data with zero start/end frames.
 * This C report is NOT an acoustic safety limit or actual sound measurement.
 * Caller must zeroize the buffer regardless of return value. */
int fm_r64_verify_digital_pcm(const float *buffer, uint64_t samples,
                              uint32_t channels, float max_digital_peak,
                              FMR64DigitalIntegrity *report);
#endif
