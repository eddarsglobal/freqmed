/* SPDX-License-Identifier: Apache-2.0 */
#ifndef FM_SESSION_CLOCK_H
#define FM_SESSION_CLOCK_H
#include <stdint.h>
/* Native elapsed-time clock, not a physical output watchdog or measurement. */
int fm_session_clock_ms(uint64_t *out);
#endif
