/* SPDX-License-Identifier: Apache-2.0 */
/*
 * FREQMED GEN-R40 — ISOLATED OPAQUE C11 TICKET / COMPLETION DESIGN.
 * Compile to object only; NEVER link, load, call or dispatch any callback.
 * No CoreAudio operations, simulations, audio or EM device output.
 *
 * R40 reduces ordinary client copy/reinit of a ticket by making the type
 * opaque, providing a fixed array of four process-lifetime private slots,
 * and refusing all slot reuse. It does NOT prevent pointer aliasing, an
 * omitted completion, owner lifetime violations or real OS callbacks.
 */
#include "r40_opaque_ticket.h"
#include <stdatomic.h>
#include <stddef.h>

extern int fm36_prepare_once(void *owner,void **userdata_out);
extern int fm36_mark_exposed(void *userdata);
extern int fm36_try_enter(void *userdata,void **owner_out);
extern int fm36_leave(void *userdata);
extern int fm36_seal(void *userdata);

enum {
    FM40_UNUSED=0u, FM40_RESERVED=1u, FM40_ACTIVE=2u,
    FM40_FINISHED=3u, FM40_REJECTED=4u
};

struct FM40Ticket {
    atomic_uint phase;
    void *token;
};

static struct FM40Ticket fm40_slots[FM40_MAX_TICKETS]={
    {ATOMIC_VAR_INIT(FM40_UNUSED),NULL},
    {ATOMIC_VAR_INIT(FM40_UNUSED),NULL},
    {ATOMIC_VAR_INIT(FM40_UNUSED),NULL},
    {ATOMIC_VAR_INIT(FM40_UNUSED),NULL}
};

/* A claimed owner is retained by EXTERNAL contract until process exit.
 * Expose failure consumes the C36 claim without reclaiming owner.
 */
int fm40_register_owner_once(void *owner,void **userdata_out) {
    if (!owner || !userdata_out) return -1;
    *userdata_out=NULL;
    if (fm36_prepare_once(owner,userdata_out)!=0) return -1;
    if (fm36_mark_exposed(*userdata_out)!=0) return -1;
    return 0;
}

/* One distinct private slot per admitted callback, up to four LIFETIME
 * attempts per process. No ticket allocation, recycling or callback run.
 * Denial or slot exhaustion is terminal: fail closed, never fallback heap.
 * A successful caller MUST pair this admission with fm40_complete exactly
 * once on EVERY callback exit; C40 itself cannot enforce eventual calls.
 */
int fm40_begin(void *userdata,FM40Ticket **ticket_out,void **owner_out) {
    if (!ticket_out || !owner_out) return -1;
    *ticket_out=NULL;
    *owner_out=NULL;
    for (size_t i=0u;i<FM40_MAX_TICKETS;i++) {
        struct FM40Ticket *slot=&fm40_slots[i];
        unsigned expected=FM40_UNUSED;
        if (!atomic_compare_exchange_strong_explicit(
                &slot->phase,&expected,FM40_RESERVED,
                memory_order_acq_rel,memory_order_acquire)) continue;
        void *owner=NULL;
        if (fm36_try_enter(userdata,&owner)!=0) {
            atomic_store_explicit(&slot->phase,FM40_REJECTED,memory_order_release);
            return -1;
        }
        if (!owner) {
            (void)fm36_leave(userdata);
            atomic_store_explicit(&slot->phase,FM40_REJECTED,memory_order_release);
            return -1;
        }
        slot->token=userdata;
        atomic_store_explicit(&slot->phase,FM40_ACTIVE,memory_order_release);
        *owner_out=owner;
        *ticket_out=slot;
        return 0;
    }
    return -1;
}

/* Pointer identity is checked WITHOUT dereferencing untrusted ticket.
 * Only the CAS ACTIVE->FINISHED winner invokes a single fm36_leave.
 * This proves at-most-once per valid slot, NOT exactly-once callback exit.
 * A failed leave is terminal and remains an OPEN proof obligation.
 */
int fm40_complete(FM40Ticket *ticket) {
    if (!ticket) return -1;
    for (size_t i=0u;i<FM40_MAX_TICKETS;i++) {
        struct FM40Ticket *slot=&fm40_slots[i];
        if (ticket!=slot) continue;
        unsigned expected=FM40_ACTIVE;
        if (!atomic_compare_exchange_strong_explicit(
                &slot->phase,&expected,FM40_FINISHED,
                memory_order_acq_rel,memory_order_acquire)) return -1;
        return fm36_leave(slot->token);
    }
    return -1;
}

/* Admission seal is not an OS callback quiescence or physical cutoff. */
int fm40_seal(void *userdata) {
    return fm36_seal(userdata);
}
