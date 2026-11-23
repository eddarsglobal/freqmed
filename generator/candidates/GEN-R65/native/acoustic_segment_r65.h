/* SPDX-License-Identifier: Apache-2.0 */
#ifndef FM_ACOUSTIC_SEGMENT_R65_H
#define FM_ACOUSTIC_SEGMENT_R65_H
#include "acoustic_session_r59.h"
#include <stdint.h>
/* Real numeric digital command stream; never physical emission/metrology. */
#define FM_R65_CHUNK_FRAMES 256U
#define FM_R65_READY 1U
#define FM_R65_COMPLETE 2U
#define FM_R65_FAILED 3U
typedef struct {
    FMR59Session contract;
    uint64_t next_frame;
    float digital_peak_normalized;
    uint32_t state;
} FMR65Cursor;
typedef struct {
    uint64_t start_frame;
    uint64_t frames;
    uint64_t samples;
    uint32_t channels;
    float chunk_digital_peak;
    uint32_t zero_edges_verified;
} FMR65ChunkReport;
/* Accept only bounded, route-verified digital commands (not an armed route).
 * The caller MUST independently check OS route, real UID, R60 lease, R61
 * fault, and R58 isolated backend before AND after the whole preparation. */
int fm_r65_stream_begin(FMR65Cursor *cursor, const FMR59Session *contract);
/* Exact capacity must equal 256 * channels floats; unused tail is zero.
 * Return 1 for one numeric segment, 0 after last segment, -1 fail-closed. */
int fm_r65_stream_next(FMR65Cursor *cursor, const FMR59Session *current,
                       float *output, uint64_t capacity_samples,
                       FMR65ChunkReport *report);
void fm_r65_stream_clear(FMR65Cursor *cursor);
#endif
