/* SPDX-License-Identifier: Apache-2.0 */
#include "generator.h"
/* No EM driver can be truthful until a specific instrument has been
 * selected, inspected, and independently qualified. No port or radio I/O. */
int fm_em_backend_available(void) { return 0; }
int fm_em_physical_output(const FMCommand *command) {
  (void)command;
  return -1; /* BLOCKED_NO_QUALIFIED_EM_DEVICE */
}
