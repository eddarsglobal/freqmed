/* SPDX-License-Identifier: Apache-2.0 */
#include "generator.h"
#include <math.h>
#include <stdio.h>
#include <string.h>

static void reason(char *out, size_t n, const char *s) {
  if (out && n) (void)snprintf(out,n,"%s",s);
}
int fm_validate_command(const FMCommand *c, char *why, size_t cap) {
  if (!c) { reason(why,cap,"MISSING_COMMAND"); return 0; }
  if (c->channel!=FM_ACOUSTIC && c->channel!=FM_ELECTROMAGNETIC) {
    reason(why,cap,"UNKNOWN_PHYSICAL_CHANNEL"); return 0;
  }
  /* These checks test input structure, NOT safety of any exposure. */
  if (!isfinite(c->frequency_hz) || c->frequency_hz <= 0) {
    reason(why,cap,"INVALID_HZ"); return 0;
  }
  if (!isfinite(c->normalized_level) || c->normalized_level <= 0.0 || c->normalized_level > 1.0) {
    reason(why,cap,"INVALID_NORMALIZED_LEVEL"); return 0;
  }
  if (c->duration_ms==0U) { reason(why,cap,"INVALID_DURATION"); return 0; }
  reason(why,cap,"STRUCTURALLY_VALID_NOT_SAFE_OR_CERTIFIED");
  return 1;
}
int fm_guardian_transition(FMGuardian *g, const FMCommand *c, char *why, size_t cap) {
  if (!g) { reason(why,cap,"MISSING_GUARDIAN"); return 0; }
  if (!fm_validate_command(c,why,cap)) { g->state=FM_BLOCKED; return 0; }
  /* Never allow a mere UI, command line argument, or boolean switch to
   * manufacture an authorization. This version has a compiled hard denial.
   * A separate future certification, code review, and new release are required.
   */
  (void)g->hardware_profile_certified;
  (void)g->safety_review_certified;
  (void)g->bench_authorized;
  (void)g->physical_output_enabled;
  g->state=FM_BLOCKED;
  reason(why,cap,"R1_OUTPUT_HARD_LOCK_CERTIFICATION_REQUIRED");
  return 0;
}
void fm_stop(FMGuardian *g) {
  if (g) g->state=FM_OFF;
}
