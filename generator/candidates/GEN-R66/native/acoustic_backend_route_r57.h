/* SPDX-License-Identifier: Apache-2.0 */
#ifndef FREQMED_R57_BACKEND_ROUTE_H
#define FREQMED_R57_BACKEND_ROUTE_H
#include "generator.h"
#include <stdint.h>
/* Candidate backend requires DEFAULT output. Read-only admission contract.
 * 1 = route consistent with current DEFAULT CoreAudio device; NO output.
 * 2..7 = R56 refusal (invalid command, route, OS, digital constraints).
 * 8 = selected output not current default; 9 = default output changed / caps.
 */
typedef struct {
  int32_t result_code;
  uint32_t default_route_matches;
  double nominal_rate_hz;
  uint64_t digital_frame_budget;
} FMR57BackendRouteCheck;
int fm_r57_backend_route_check(const FMCommand *command, uint32_t expected_device_id,
    const char *expected_name, uint32_t expected_channels, double expected_rate_hz,
    FMR57BackendRouteCheck *out);
#endif
