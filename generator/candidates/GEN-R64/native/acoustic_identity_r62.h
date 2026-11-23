/* SPDX-License-Identifier: Apache-2.0 */
#ifndef FM_ACOUSTIC_IDENTITY_R62_H
#define FM_ACOUSTIC_IDENTITY_R62_H
#include <stdint.h>
#include "acoustic_session_r59.h"
/* One-process ephemeral OS device identity pin: not calibration, attestation or an emitter. */
#define FM_R62_UID_CAP 256U
#define FM_R62_UNBOUND 0U
#define FM_R62_PINNED 1U
#define FM_R62_INVALIDATED 2U
#define FM_R62_STOPPED 3U
#define FM_R62_NONE 0U
#define FM_R62_OS_UNAVAILABLE 1U
#define FM_R62_OS_IDENTITY_CHANGED 2U
#define FM_R62_SESSION_CHANGED 3U
#define FM_R62_EXPLICIT_RESET 4U
#define FM_R62_OPERATOR_STOP 5U
typedef struct {
 uint32_t state;
 uint32_t reason;
 uint64_t sequence;
 uint32_t device_id;
 uint32_t channels;
 double sample_rate_hz;
 FMCommand command;
 char name[128];
 /* Private, never exposed by HTTP/UI or persisted. Cleared on invalidation and STOP. */
 char os_uid[FM_R62_UID_CAP];
} FMR62Identity;
int fm_r62_identity_pin(FMR62Identity *pin,const FMR59Session *session);
int fm_r62_identity_check(FMR62Identity *pin,const FMR59Session *session);
void fm_r62_identity_invalidate(FMR62Identity *pin,uint32_t reason);
void fm_r62_identity_stop(FMR62Identity *pin);
#endif
