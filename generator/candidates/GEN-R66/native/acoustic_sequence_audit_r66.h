/* SPDX-License-Identifier: Apache-2.0 */
#ifndef FM_ACOUSTIC_SEQUENCE_AUDIT_R66_H
#define FM_ACOUSTIC_SEQUENCE_AUDIT_R66_H
#include "acoustic_segment_r65.h"
#include <stdint.h>

/* Read-only checker, separate from R65 PCM synthesis.
 * Only inspect in-memory digital command samples. Never emit or measure sound.
 */
#define FM_R66_ACTIVE 1U
#define FM_R66_COMPLETE 2U
#define FM_R66_FAILED 3U

typedef struct {
    uint64_t expected_frames;
    uint64_t checked_frames;
    uint64_t checked_samples;
    uint32_t channels;
    uint32_t segments;
    uint32_t state;
    float observed_digital_peak;
} FMR66Audit;

int fm_r66_audit_begin(FMR66Audit *audit, uint64_t frames, uint32_t channels);
/* Capacity must be exactly 256 * channels floats. A full/partial chunk
 * must be contiguous and every unused float must be zero. Returns 1 on PASS.
 * On any fault, audit stays FAILED until explicitly cleared/reinitialized. */
int fm_r66_audit_chunk(FMR66Audit *audit, const FMR65ChunkReport *report,
                       const float *pcm, uint64_t capacity_samples);
int fm_r66_audit_finish(FMR66Audit *audit);
void fm_r66_audit_clear(FMR66Audit *audit);
#endif
