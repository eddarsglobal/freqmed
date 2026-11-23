/* SPDX-License-Identifier: Apache-2.0 */
#include "acoustic_sequence_audit_r66.h"
#include "acoustic_pcm_r63.h"
#include <math.h>
#include <stddef.h>
#include <string.h>

static int fail(FMR66Audit *a) {
    if (a) a->state = FM_R66_FAILED;
    return 0;
}

int fm_r66_audit_begin(FMR66Audit *a, uint64_t frames, uint32_t channels) {
    if (!a) return 0;
    memset(a, 0, sizeof(*a));
    if (!frames || frames > FM_R63_MAX_FRAMES ||
        !channels || channels > FM_R63_MAX_CHANNELS) return fail(a);
    a->expected_frames = frames;
    a->channels = channels;
    a->state = FM_R66_ACTIVE;
    return 1;
}

int fm_r66_audit_chunk(FMR66Audit *a, const FMR65ChunkReport *r,
                       const float *pcm, uint64_t capacity) {
    if (!a) return 0;
    if (a->state != FM_R66_ACTIVE || !r || !pcm ||
        a->checked_frames >= a->expected_frames ||
        capacity != FM_R65_CHUNK_FRAMES * (uint64_t)a->channels ||
        a->segments >= (FM_R63_MAX_FRAMES + FM_R65_CHUNK_FRAMES - 1U)/FM_R65_CHUNK_FRAMES)
        return fail(a);
    const uint64_t left = a->expected_frames - a->checked_frames;
    const uint64_t required = left >= FM_R65_CHUNK_FRAMES ? FM_R65_CHUNK_FRAMES : left;
    const uint64_t count = required * (uint64_t)a->channels;
    const uint32_t should_have_edges =
        (a->checked_frames == 0U || a->checked_frames + required == a->expected_frames) ? 1U : 0U;
    if (r->start_frame != a->checked_frames || r->frames != required ||
        r->channels != a->channels || r->samples != count ||
        r->zero_edges_verified != should_have_edges ||
        !isfinite(r->chunk_digital_peak) ||
        r->chunk_digital_peak < 0.0f ||
        r->chunk_digital_peak > FM_R63_MAX_DIGITAL_LEVEL + 1.0e-7f)
        return fail(a);
    float actual_peak = 0.0f;
    for (uint64_t i = 0; i < capacity; ++i) {
        const float v = pcm[i];
        if (!isfinite(v) || fabsf(v) > FM_R63_MAX_DIGITAL_LEVEL + 1.0e-7f)
            return fail(a);
        if (i >= count) {
            if (v != 0.0f) return fail(a);
            continue;
        }
        const uint64_t frame = a->checked_frames + i / a->channels;
        if ((frame == 0U || frame + 1U == a->expected_frames) && v != 0.0f)
            return fail(a);
        if (a->channels == 2U && (i & 1U) && v != pcm[i-1U])
            return fail(a);
        const float mag = fabsf(v);
        if (mag > actual_peak) actual_peak = mag;
    }
    if (fabsf(actual_peak - r->chunk_digital_peak) > 1.0e-7f)
        return fail(a);
    if (actual_peak > a->observed_digital_peak)
        a->observed_digital_peak = actual_peak;
    a->checked_frames += required;
    a->checked_samples += count;
    a->segments++;
    return 1;
}

int fm_r66_audit_finish(FMR66Audit *a) {
    if (!a) return 0;
    if (a->state != FM_R66_ACTIVE ||
        a->checked_frames != a->expected_frames ||
        a->checked_samples != a->expected_frames * (uint64_t)a->channels ||
        a->segments != (a->expected_frames + FM_R65_CHUNK_FRAMES - 1U)/FM_R65_CHUNK_FRAMES ||
        !isfinite(a->observed_digital_peak)) return fail(a);
    a->state = FM_R66_COMPLETE;
    return 1;
}

void fm_r66_audit_clear(FMR66Audit *a) {
    if (!a) return;
    volatile unsigned char *p = (volatile unsigned char *)a;
    for (size_t i=0; i<sizeof(*a); ++i) p[i] = 0U;
}
