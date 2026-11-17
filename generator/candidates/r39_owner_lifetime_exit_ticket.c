/* SPDX-License-Identifier: Apache-2.0 */
/*
 * FREQMED GEN-R39 isolated C11 owner lifetime and exit ticket.
 * UNLINKED, COMPILE ONLY. Never run, dispatch a callback, activate audio,
 * simulate science, or grant authority to emit.
 *
 * AT-MOST-ONCE local leave does not mean EXACTLY-ONCE, callback quiescence,
 * real C11 race freedom, owner lifetime enforcement outside this object,
 * OS stop success, or physical cutoff. Those proof obligations remain OPEN.
 * Caller initializes each distinct living ticket with FM39_LEASE_INITIALIZER.
 * Never copy/reinitialize a published ticket or release its storage.
 * C36 owner retains process lifetime, including all OS failure paths.
 */
#include <stdatomic.h>
#include <stddef.h>

extern int fm36_prepare_once(void *owner,void **userdata_out);
extern int fm36_mark_exposed(void *userdata);
extern int fm36_try_enter(void *userdata,void **owner_out);
extern int fm36_leave(void *userdata);
extern int fm36_seal(void *userdata);

typedef enum {
    FM39_UNUSED=0u, FM39_RESERVING=1u, FM39_ACTIVE=2u,
    FM39_FINISHED=3u, FM39_REJECTED=4u
} FM39Phase;

typedef struct {
    atomic_uint phase;
    void *os_userdata;
    void *owner;
} FM39Lease;

#define FM39_LEASE_INITIALIZER { ATOMIC_VAR_INIT(FM39_UNUSED), NULL, NULL }

/* After a successful one-shot claim, external aliases MUST retain owner
 * until process termination even if exposing the token fails.
 */
int fm39_register_owner_once(void *owner,void **userdata_out) {
    if (!owner || !userdata_out) return -1;
    *userdata_out=NULL;
    if (fm36_prepare_once(owner,userdata_out)!=0) return -1;
    if (fm36_mark_exposed(*userdata_out)!=0) return -1;
    return 0;
}

/* Owner is acquired through the static R36 gate before publication to
 * the ticket. State release synchronizes with a reader's acquire; it is
 * NOT a proof about all unrelated owner fields in a real CoreAudio app.
 */
int fm39_enter_once(void *userdata,FM39Lease *ticket) {
    if (!ticket) return -1;
    unsigned expected=FM39_UNUSED;
    if (!atomic_compare_exchange_strong_explicit(
            &ticket->phase,&expected,FM39_RESERVING,
            memory_order_acq_rel,memory_order_acquire)) return -1;
    void *owner=NULL;
    if (fm36_try_enter(userdata,&owner)!=0) {
        atomic_store_explicit(&ticket->phase,FM39_REJECTED,memory_order_release);
        return -1;
    }
    if (!owner) {
        (void)fm36_leave(userdata);
        atomic_store_explicit(&ticket->phase,FM39_REJECTED,memory_order_release);
        return -1;
    }
    ticket->os_userdata=userdata;
    ticket->owner=owner;
    atomic_store_explicit(&ticket->phase,FM39_ACTIVE,memory_order_release);
    return 0;
}

/* Immutable ticket owner pointer, never cleared; its allocation remains
 * an external lifetime requirement. No callback work is performed.
 */
void *fm39_owner_if_active(const FM39Lease *ticket) {
    if (!ticket) return NULL;
    if (atomic_load_explicit(&ticket->phase,memory_order_acquire)
            !=FM39_ACTIVE) return NULL;
    return ticket->owner;
}

/* Exactly one successful CAS winner can call R36 leave per valid ticket.
 * If no caller completes, an admission is leaked. If R36 leave fails,
 * FINISHED stays terminal and that error remains an unresolved obligation.
 */
int fm39_complete_at_most_once(FM39Lease *ticket) {
    if (!ticket) return -1;
    unsigned expected=FM39_ACTIVE;
    if (!atomic_compare_exchange_strong_explicit(
            &ticket->phase,&expected,FM39_FINISHED,
            memory_order_acq_rel,memory_order_acquire)) return -1;
    return fm36_leave(ticket->os_userdata);
}

/* Denial of new admissions is not an OS stop nor physical cutoff. */
int fm39_seal_without_release(void *userdata) {
    return fm36_seal(userdata);
}
