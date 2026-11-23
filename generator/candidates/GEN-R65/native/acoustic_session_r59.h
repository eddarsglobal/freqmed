/* SPDX-License-Identifier: Apache-2.0 */
#ifndef FREQMED_ACOUSTIC_SESSION_R59_H
#define FREQMED_ACOUSTIC_SESSION_R59_H
#include "generator.h"
#include <stdint.h>
/* Not a playback session. A memory-only native contract tied to a fresh OS
 * readback and an exact digital command. No AudioQueue or output symbols. */
#define FM_R59_DEVICE_NAME_CAP 128U
#define FM_R59_PHASE_UNBOUND 0U
#define FM_R59_PHASE_ROUTE_VERIFIED 1U
#define FM_R59_PHASE_INVALIDATED 2U
#define FM_R59_PHASE_STOPPED 3U
#define FM_R59_REASON_NONE 0U
#define FM_R59_REASON_NOT_READY 1U
#define FM_R59_REASON_INVALID_ARGUMENT 2U
#define FM_R59_REASON_ROUTE_OR_COMMAND_MISMATCH 3U
#define FM_R59_REASON_OS_CHANGED_OR_UNAVAILABLE 4U
#define FM_R59_REASON_OPERATOR_STOP 5U
#define FM_R59_REASON_ROUTE_RESET 6U

typedef struct {
  uint32_t phase;
  uint32_t reason;
  uint32_t device_id;
  uint32_t channels;
  double sample_rate_hz;
  FMCommand command;
  uint64_t digital_frame_budget;
  char name[FM_R59_DEVICE_NAME_CAP];
} FMR59Session;

/* Returns 1 iff fresh native CoreAudio R56/R57 checks accept the route and
 * exact command; 0 on refusal; -1 for invalid C pointers. Never arms output. */
int fm_r59_session_bind(FMR59Session *session, const FMCommand *command,
  uint32_t expected_device_id,const char *expected_name,
  uint32_t expected_channels,double expected_rate_hz);
/* Repeat the native OS check against the pinned command and exact route. */
int fm_r59_session_poll(FMR59Session *session);
/* Refuse all future status as ready; clearing route is explicit. */
void fm_r59_session_invalidate(FMR59Session *session);
void fm_r59_session_stop(FMR59Session *session);
#endif
