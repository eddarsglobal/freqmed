/* SPDX-License-Identifier: Apache-2.0 */
#include "acoustic_segment_r65.h"
#include "acoustic_pcm_r63.h"
#include <math.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

static int valid_contract(const FMR59Session *s) {
    if (!s || s->phase != FM_R59_PHASE_ROUTE_VERIFIED ||
        s->command.channel != 1 || s->device_id == 0U ||
        s->channels < 1U || s->channels > FM_R63_MAX_CHANNELS ||
        !isfinite(s->sample_rate_hz) ||
        s->sample_rate_hz < 8000.0 || s->sample_rate_hz > 96000.0 ||
        !isfinite(s->command.frequency_hz) ||
        !isfinite(s->command.normalized_level) ||
        s->command.frequency_hz <= 0.0 ||
        s->command.frequency_hz > 0.45*s->sample_rate_hz ||
        s->command.frequency_hz > 20000.0 ||
        s->command.normalized_level < 0.0 ||
        s->command.normalized_level > FM_R63_MAX_DIGITAL_LEVEL ||
        s->command.duration_ms == 0U ||
        s->command.duration_ms > FM_R63_MAX_DURATION_MS ||
        !memchr(s->name, 0, FM_R59_DEVICE_NAME_CAP)) return 0;
    const double exact = s->sample_rate_hz * ((double)s->command.duration_ms / 1000.0);
    if (!isfinite(exact) || exact < 1.0) return 0;
    const uint64_t frames = (uint64_t)llround(exact);
    return frames > 0U && frames <= FM_R63_MAX_FRAMES &&
           frames == s->digital_frame_budget;
}
static int same_contract(const FMR59Session *a, const FMR59Session *b) {
    if (!valid_contract(b)) return 0;
    return a->device_id == b->device_id && a->channels == b->channels &&
           a->sample_rate_hz == b->sample_rate_hz &&
           a->digital_frame_budget == b->digital_frame_budget &&
           a->command.channel == b->command.channel &&
           a->command.duration_ms == b->command.duration_ms &&
           a->command.frequency_hz == b->command.frequency_hz &&
           a->command.normalized_level == b->command.normalized_level &&
           strncmp(a->name, b->name, FM_R59_DEVICE_NAME_CAP) == 0;
}
int fm_r65_stream_begin(FMR65Cursor *cursor, const FMR59Session *session) {
    if (!cursor) return 0;
    memset(cursor, 0, sizeof(*cursor));
    if (!valid_contract(session)) return 0;
    cursor->contract = *session;
    cursor->state = FM_R65_READY;
    return 1;
}
int fm_r65_stream_next(FMR65Cursor *cursor, const FMR59Session *current,
                       float *output, uint64_t capacity, FMR65ChunkReport *report) {
    if (report) memset(report, 0, sizeof(*report));
    if (!cursor || !output || !report) return -1;
    if (cursor->state == FM_R65_COMPLETE) return 0;
    if (cursor->state != FM_R65_READY || !same_contract(&cursor->contract,current) ||
        capacity != FM_R65_CHUNK_FRAMES*(uint64_t)cursor->contract.channels ||
        cursor->next_frame >= cursor->contract.digital_frame_budget) {
        cursor->state = FM_R65_FAILED;
        return -1;
    }
    /* Explicit zero-fill including unused final-chunk tail. */
    memset(output, 0, (size_t)capacity*sizeof(float));
    const FMR59Session *s = &cursor->contract;
    const uint64_t total = s->digital_frame_budget;
    const uint64_t start = cursor->next_frame;
    const uint64_t count = total-start < FM_R65_CHUNK_FRAMES ? total-start : FM_R65_CHUNK_FRAMES;
    const double tau = 6.283185307179586476925286766559;
    const double ramp = fmin(0.005*s->sample_rate_hz, (double)total*0.1);
    float peak = 0.0f;
    for (uint64_t local=0; local<count; ++local) {
        const uint64_t index = start+local;
        const double edge = fmin((double)index,(double)(total-1U-index));
        const double scaled = ramp >= 1.0 ? fmin(1.0,edge/ramp) : (edge > 0.0 ? 1.0 : 0.0);
        const double window = sin(0.25*tau*scaled);
        const float value = (float)(s->command.normalized_level *
            sin(tau*s->command.frequency_hz*(double)index/s->sample_rate_hz)*window*window);
        if (!isfinite(value) || fabsf(value) > (float)FM_R63_MAX_DIGITAL_LEVEL + 1.0e-7f ||
            ((index==0U || index+1U==total) && value != 0.0f)) {
            cursor->state = FM_R65_FAILED;
            return -1;
        }
        const float abs_value = fabsf(value);
        if (abs_value > peak) peak = abs_value;
        for (uint32_t channel=0; channel<s->channels; ++channel)
            output[local*s->channels+channel] = value;
    }
    for (uint64_t i=0; i<count*(uint64_t)s->channels; ++i) {
        if (!isfinite(output[i]) || fabsf(output[i]) > FM_R63_MAX_DIGITAL_LEVEL+1.0e-7f) {
            cursor->state = FM_R65_FAILED;
            return -1;
        }
    }
    report->start_frame = start;
    report->frames = count;
    report->samples = count*s->channels;
    report->channels = s->channels;
    report->chunk_digital_peak = peak;
    report->zero_edges_verified = (start == 0U || start+count == total) ? 1U : 0U;
    if (peak > cursor->digital_peak_normalized) cursor->digital_peak_normalized = peak;
    cursor->next_frame += count;
    if (cursor->next_frame == total) cursor->state = FM_R65_COMPLETE;
    return 1;
}
void fm_r65_stream_clear(FMR65Cursor *cursor) {
    if (!cursor) return;
    volatile unsigned char *b = (volatile unsigned char *)cursor;
    for (size_t i=0; i<sizeof(*cursor); ++i) b[i] = 0U;
}
