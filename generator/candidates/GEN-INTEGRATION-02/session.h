/* SPDX-License-Identifier: Apache-2.0 */
#ifndef FM_SESSION_02_H
#define FM_SESSION_02_H
#include "integration.h"
#include <stdint.h>
typedef enum {
    FM_S_EMPTY=0, FM_S_PREPARED, FM_S_EXPIRED, FM_S_CANCELLED, FM_S_FAULT
} FMSessionState;
typedef enum {
    FM_S_OK=0, FM_S_BAD_ARGUMENT, FM_S_INVALID_REQUEST, FM_S_BUSY,
    FM_S_STALE, FM_S_CLOCK_FAULT, FM_S_OVERFLOW, FM_S_NOT_LIVE
} FMSessionResult;
typedef struct {
    uint64_t generation, last_ms, deadline_ms;
    FMSessionState state;
    int seen_clock;
} FMSessionSlot;
typedef struct { FMSessionSlot acoustic, em; } FMSessionEngine;
/* Serialized caller, initialized once per process. No physical authority.
 * now_ms is supplied by a monotonic-clock adapter, not a measured emission.
 * Tokens are process-local and channel-scoped; no persistence or IPC. */
void fm_sessions_init(FMSessionEngine *e);
FMSessionResult fm_session_prepare(FMSessionEngine *e,
    const FMIntegrationRequest *r, uint64_t now_ms, uint64_t *token);
FMSessionResult fm_session_tick(FMSessionEngine *e, FMChannel channel,
    uint64_t token, uint64_t now_ms);
FMSessionResult fm_session_cancel(FMSessionEngine *e, FMChannel channel,
    uint64_t token);
FMSessionResult fm_session_close(FMSessionEngine *e, FMChannel channel,
    uint64_t token);
#endif
