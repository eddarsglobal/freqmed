/* SPDX-License-Identifier: Apache-2.0 */
#include "acoustic_integrity_r64.h"
#include "acoustic_pcm_r63.h"
#include <math.h>
#include <stddef.h>
#include <string.h>

int fm_r64_verify_digital_pcm(const float *buffer, uint64_t samples,
                             uint32_t channels, float maximum,
                             FMR64DigitalIntegrity *report) {
    if (report) memset(report, 0, sizeof(*report));
    if (!report || !buffer || channels == 0U || channels > FM_R63_MAX_CHANNELS ||
        samples < 2U * (uint64_t)channels ||
        samples > FM_R63_MAX_FRAMES * FM_R63_MAX_CHANNELS ||
        samples % channels != 0U || !isfinite(maximum) || maximum < 0.0f ||
        maximum > (float)FM_R63_MAX_DIGITAL_LEVEL) return 0;
    const uint64_t frames = samples / channels;
    if (frames > FM_R63_MAX_FRAMES) return 0;
    float peak = 0.0f;
    for (uint64_t i = 0U; i < samples; ++i) {
        const float v = buffer[i];
        if (!isfinite(v) || fabsf(v) > maximum) return 0;
        if ((i < channels || i >= samples - channels) && v != 0.0f) return 0;
        const float mag = fabsf(v);
        if (mag > peak) peak = mag;
    }
    report->checked_samples = samples;
    report->channels = channels;
    report->digital_peak_normalized = peak;
    report->zero_edges = 1U;
    return 1;
}
