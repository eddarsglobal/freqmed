/* SPDX-License-Identifier: Apache-2.0 */
#ifndef FM_ACOUSTIC_PCM_R63_H
#define FM_ACOUSTIC_PCM_R63_H
#include <stdint.h>
#include "acoustic_session_r59.h"
/* Digital samples in ephemeral RAM ONLY. Not CoreAudio, a sound-pressure
 * measurement, calibration, safety gate or authorization of physical output. */
#define FM_R63_MAX_FRAMES 96000ULL
#define FM_R63_MAX_CHANNELS 2U
#define FM_R63_MAX_DIGITAL_LEVEL 0.01
#define FM_R63_MAX_DURATION_MS 1000U
typedef struct {
  uint64_t frames;
  uint64_t samples;
  uint32_t channels;
  float digital_peak_normalized;
} FMR63DigitalReport;
/* Returns 1 if a full verified digital PCM block is written, 0 if refused.
 * The caller must check native OS route, UID, lease and fault immediately
 * before invoking and MUST zeroize/free the buffer after examination.
 * No function in this module uses AudioQueue, speakers or hardware. */
int fm_r63_render_digital_pcm(const FMR59Session *session, float *buffer,
                            uint64_t capacity_samples, FMR63DigitalReport *report);
void fm_r63_zeroize_digital_pcm(float *buffer, uint64_t capacity_samples);
#endif
