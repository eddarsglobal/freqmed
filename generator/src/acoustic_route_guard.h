/* SPDX-License-Identifier: Apache-2.0 */
#ifndef FREQMED_ACOUSTIC_ROUTE_GUARD_H
#define FREQMED_ACOUSTIC_ROUTE_GUARD_H
#include <stdint.h>
/* Internal CoreAudio route fingerprint: NEVER export OS token in reports. */
typedef struct {
  uint32_t os_device_token;
  double nominal_sample_rate_hz;
  unsigned output_channels;
} FMRouteFingerprint;
int fm_route_capture(FMRouteFingerprint *out);
int fm_route_unchanged(const FMRouteFingerprint *original);
#endif
