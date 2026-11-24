/* SPDX-License-Identifier: Apache-2.0 */
#include "session.h"
static FMSessionSlot *slot(FMSessionEngine *e, FMChannel c) {
    if (!e) return NULL;
    if (c==FM_ACOUSTIC) return &e->acoustic;
    if (c==FM_ELECTROMAGNETIC) return &e->em;
    return NULL;
}
void fm_sessions_init(FMSessionEngine *e) {
    if (e) *e=(FMSessionEngine){0};
}
static int clock_ok(FMSessionSlot *s, uint64_t now) {
    if (s->seen_clock && now<s->last_ms) return 0;
    s->seen_clock=1; s->last_ms=now; return 1;
}
static FMSessionResult check(FMSessionSlot *s, uint64_t token) {
    if (!s) return FM_S_BAD_ARGUMENT;
    if (!token || token!=s->generation || s->state==FM_S_EMPTY)
        return FM_S_STALE;
    return FM_S_OK;
}
FMSessionResult fm_session_prepare(FMSessionEngine *e,
    const FMIntegrationRequest *r, uint64_t now, uint64_t *token) {
    if (!r || !token) return FM_S_BAD_ARGUMENT;
    /* token must be a separate writable object, not an alias of inputs/engine. */
    *token=0;
    FMSessionSlot *s=slot(e,r->channel);
    if (!s) return FM_S_BAD_ARGUMENT;
    if (s->state!=FM_S_EMPTY) return FM_S_BUSY;
    FMIntegrationResult v=fm_integration_validate(r);
    uint64_t duration;
    if (v==FM_INT_ACOUSTIC_STRUCTURE_ONLY) duration=r->acoustic->duration_ms;
    else if (v==FM_INT_EM_STRUCTURE_ONLY) duration=r->em_setpoint->duration_ms;
    else return FM_S_INVALID_REQUEST;
    if (s->seen_clock && now<s->last_ms) return FM_S_CLOCK_FAULT;
    if (s->generation==UINT64_MAX || duration>UINT64_MAX-now)
        return FM_S_OVERFLOW;
    (void)clock_ok(s,now);
    ++s->generation; s->deadline_ms=now+duration;
    s->state=FM_S_PREPARED; *token=s->generation;
    return FM_S_OK;
}
FMSessionResult fm_session_tick(FMSessionEngine *e, FMChannel c,
    uint64_t token, uint64_t now) {
    FMSessionSlot *s=slot(e,c);
    FMSessionResult v=check(s,token);
    if (v!=FM_S_OK) return v;
    if (s->state!=FM_S_PREPARED) return FM_S_NOT_LIVE;
    if (!clock_ok(s,now)) { s->state=FM_S_FAULT; return FM_S_CLOCK_FAULT; }
    if (now>=s->deadline_ms) s->state=FM_S_EXPIRED;
    return FM_S_OK;
}
FMSessionResult fm_session_cancel(FMSessionEngine *e, FMChannel c,
    uint64_t token) {
    FMSessionSlot *s=slot(e,c);
    FMSessionResult v=check(s,token);
    if (v!=FM_S_OK) return v;
    if (s->state!=FM_S_PREPARED) return FM_S_NOT_LIVE;
    s->state=FM_S_CANCELLED; return FM_S_OK;
}
FMSessionResult fm_session_close(FMSessionEngine *e, FMChannel c,
    uint64_t token) {
    FMSessionSlot *s=slot(e,c);
    FMSessionResult v=check(s,token);
    if (v!=FM_S_OK) return v;
    if (s->state==FM_S_PREPARED) return FM_S_BUSY;
    s->state=FM_S_EMPTY; s->deadline_ms=0;
    return FM_S_OK;
}
