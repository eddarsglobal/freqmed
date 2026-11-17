/* SPDX-License-Identifier: Apache-2.0 */
/* This translation unit is the ONLY acoustic output interface linked into
   the GEN-R2 executable. The CoreAudio emission backend stays SOURCE-ONLY. */
#include "generator.h"
int fm_acoustic_native_backend_available(void) { return 0; }
int fm_acoustic_physical_output(const FMCommand *command) {
  (void)command;
  return -1;
}
