/* SPDX-License-Identifier: Apache-2.0 */
/* Native output is intentionally never linked into this R54 hardware-selection kit. */
#include "generator.h"
int fm_acoustic_native_backend_available(void) { return 0; }
int fm_acoustic_physical_output(const FMCommand *command) {
  (void)command;
  return -1;
}
int fm_em_backend_available(void) { return 0; }
int fm_em_physical_output(const FMCommand *command) {
  (void)command;
  return -1;
}
