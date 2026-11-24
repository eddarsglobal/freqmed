/* SPDX-License-Identifier: Apache-2.0 */
#ifndef FM_ACOUSTIC_CONTROL_LEASE_R60_H
#define FM_ACOUSTIC_CONTROL_LEASE_R60_H
#include "acoustic_session_r59.h"
#include <stdint.h>
/* PURE CONTROL PLANE: no physical activation, PCM buffer, AudioQueue or RF API. */
#define FM_R60_LEASE_TTL_MS 4000U
#define FM_R60_UNBOUND 0U
#define FM_R60_VALID 1U
#define FM_R60_REVOKED 2U
#define FM_R60_EXPIRED 3U
#define FM_R60_STOPPED 4U
#define FM_R60_REASON_NONE 0U
#define FM_R60_REASON_NOT_BOUND 1U
#define FM_R60_REASON_SESSION_CHANGED 2U
#define FM_R60_REASON_WATCHDOG_STALE 3U
#define FM_R60_REASON_ROUTE_RESET 4U
#define FM_R60_REASON_OPERATOR_STOP 5U
#define FM_R60_REASON_CLOCK_FAILURE 6U
#define FM_R60_REASON_MONITOR_UNAVAILABLE 7U
typedef struct {
  uint32_t state;
  uint32_t reason;
  uint64_t generation;
  uint64_t verified_at_ns;
  uint64_t expires_at_ns;
  FMR59Session bound;
} FMR60Lease;
/* Return 1 only for a live route-verified R59 session. The only meaning of
 * VALID is "recently confirmed software control metadata", NEVER ARMED. */
int fm_r60_lease_begin(FMR60Lease *lease, const FMR59Session *current);
/* Caller MUST perform new CoreAudio readback before renew. */
int fm_r60_lease_renew(FMR60Lease *lease, const FMR59Session *current);
/* Read without extending the lease; a stale lease becomes EXPIRED. */
int fm_r60_lease_check(FMR60Lease *lease, const FMR59Session *current);
/* Revoke/stop never permit a stale lease to become VALID. */
void fm_r60_lease_revoke(FMR60Lease *lease, uint32_t reason);
void fm_r60_lease_stop(FMR60Lease *lease);
#endif
