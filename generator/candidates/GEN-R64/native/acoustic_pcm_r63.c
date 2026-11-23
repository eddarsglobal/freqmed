/* SPDX-License-Identifier: Apache-2.0 */
#include "acoustic_pcm_r63.h"
#include <math.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>
/* Render a real DIGITAL command stream for future hardware integration.
 * It is neither a scientific simulation nor an acoustic measurement.
 * It NEVER opens any CoreAudio playback device or produces physical sound. */
int fm_r63_render_digital_pcm(const FMR59Session *s, float *buffer,
                            uint64_t capacity, FMR63DigitalReport *out) {
  if (out) memset(out, 0, sizeof(*out));
  if (!s || !buffer || !out || s->phase != FM_R59_PHASE_ROUTE_VERIFIED) return 0;
  const FMCommand *cmd = &s->command;
  if (cmd->channel != 1 || !isfinite(cmd->frequency_hz) ||
      !isfinite(cmd->normalized_level) || !isfinite(s->sample_rate_hz)) return 0;
  if (s->channels < 1U || s->channels > FM_R63_MAX_CHANNELS ||
      s->sample_rate_hz < 8000.0 || s->sample_rate_hz > 96000.0 ||
      cmd->duration_ms < 1U || cmd->duration_ms > FM_R63_MAX_DURATION_MS ||
      cmd->normalized_level < 0.0 || cmd->normalized_level > FM_R63_MAX_DIGITAL_LEVEL ||
      cmd->frequency_hz <= 0.0 ||
      cmd->frequency_hz > 0.45 * s->sample_rate_hz ||
      cmd->frequency_hz > 20000.0) return 0;
  const double exact_frames = s->sample_rate_hz * ((double)cmd->duration_ms / 1000.0);
  if (!isfinite(exact_frames) || exact_frames < 1.0) return 0;
  const uint64_t frames = (uint64_t)llround(exact_frames);
  if (frames < 1U || frames > FM_R63_MAX_FRAMES ||
      frames != s->digital_frame_budget ||
      frames > UINT64_MAX / s->channels) return 0;
  const uint64_t sample_count = frames * s->channels;
  if (capacity != sample_count) return 0;
  const double tau = 6.283185307179586476925286766559;
  const double ramp_frames = fmin(0.005*s->sample_rate_hz, (double)frames*0.1);
  float peak = 0.0f;
  for (uint64_t i=0; i<frames; ++i) {
    const double edge = fmin((double)i, (double)(frames-1U-i));
    const double scaled = ramp_frames >= 1.0 ? fmin(1.0, edge/ramp_frames) : 1.0;
    const double window = sin(0.25*tau*scaled); /* starts/ends at exactly zero */
    const float value = (float)(cmd->normalized_level *
      sin(tau*cmd->frequency_hz*(double)i/s->sample_rate_hz) * window*window);
    if (!isfinite(value) || fabsf(value) > (float)FM_R63_MAX_DIGITAL_LEVEL + 1.0e-7f) return 0;
    const float magnitude = fabsf(value);
    if (magnitude > peak) peak = magnitude;
    for (uint32_t ch=0; ch<s->channels; ++ch) buffer[i*s->channels+ch]=value;
  }
  out->frames=frames; out->samples=sample_count;
  out->channels=s->channels; out->digital_peak_normalized=peak;
  return 1;
}
void fm_r63_zeroize_digital_pcm(float *buffer, uint64_t count) {
  if (!buffer || count > FM_R63_MAX_FRAMES*FM_R63_MAX_CHANNELS) return;
  volatile unsigned char *p=(volatile unsigned char*)buffer;
  const uint64_t bytes=count*sizeof(float);
  for (uint64_t i=0; i<bytes; ++i) p[i]=0U;
}
