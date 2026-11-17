/* SPDX-License-Identifier: Apache-2.0 */
/*
 * FREQMED GEN-R37 — ISOLATED C11 callback entry/exit adapter PROPOSAL.
 *
 * NEVER link, load, dispatch, activate, or call as real CoreAudio code.
 * NO AudioQueue calls, no output devices, no scientific simulation.
 * This is a candidate C11 translation unit whose symbols are unresolved
 * until a future separately reviewed integration. R31 is NOT modified.
 *
 * ASSUMPTIONS NOT ENFORCED HERE:
 * 1. One initialized FM37Lease on each callback's own stack, NEVER shared.
 * 2. After fm36_prepare_once claims owner, NO external alias releases owner.
 * 3. Only one session per process; no generation/address reuse.
 * 4. Every successful enter has exactly one matching leave on every path.
 * 5. OS callbacks receive the stable anchor token rather than heap owner.
 * 6. Closing admissions is NOT OS callback quiescence or physical cutoff.
 * 
 * This file proves no C11 happens-before relation for external ctx fields,
 * OSStatus failure recovery, hardware safety, or process-exit semantics.
 */
#include <stddef.h>
#include <stdint.h>

extern int fm36_prepare_once(void *owner, void **userdata_out);
extern int fm36_mark_exposed(void *userdata);
extern int fm36_try_enter(void *userdata, void **owner_out);
extern int fm36_leave(void *userdata);
extern int fm36_seal(void *userdata);

typedef enum {
    FM37_LEASE_UNUSED=0u,
    FM37_LEASE_ACTIVE=1u,
    FM37_LEASE_FINISHED=2u
} FM37LeasePhase;

typedef struct {
    void *os_userdata;
    void *owner;
    FM37LeasePhase phase;
} FM37Lease;

/* For a fresh automatic object only: FM37Lease lease={0};
 * Caller MUST NOT reuse or reinitialize an already-active lease.
 */
int fm37_prepare_token(void *owner, void **os_userdata_out) {
    if (!owner || !os_userdata_out) return -1;
    *os_userdata_out=NULL;
    if (fm36_prepare_once(owner,os_userdata_out)!=0) return -1;
    if (fm36_mark_exposed(*os_userdata_out)!=0) return -1;
    return 0;
}

/* Local callback entry — token check and C11 admission happen in R36
 * BEFORE any access to the owner. This function does NOT call user code.
 */
static int fm37_begin(void *os_userdata, FM37Lease *lease) {
    if (!lease || lease->phase!=FM37_LEASE_UNUSED) return -1;
    void *owner=NULL;
    if (fm36_try_enter(os_userdata,&owner)!=0) return -1;
    if (!owner) {
        (void)fm36_leave(os_userdata);
        return -1;
    }
    lease->os_userdata=os_userdata;
    lease->owner=owner;
    lease->phase=FM37_LEASE_ACTIVE;
    return 0;
}

/* Separate entry functions make both OS callback obligations explicit.
 * Signatures are NOT an AudioQueue ABI and MUST NOT be installed with OS.
 */
int fm37_output_enter(void *os_userdata, FM37Lease *lease) {
    return fm37_begin(os_userdata,lease);
}
int fm37_property_enter(void *os_userdata, FM37Lease *lease) {
    return fm37_begin(os_userdata,lease);
}

/* The owner is only available after an admitted lease.
 * Caller must not store this pointer or use it after finish.
 */
void *fm37_lease_owner(const FM37Lease *lease) {
    if (!lease || lease->phase!=FM37_LEASE_ACTIVE) return NULL;
    return lease->owner;
}

/* A once-only local exit guard protects straightforward sequential
 * double-exit. It does NOT prove pairing with arbitrary external callers
 * or concurrent access to the same lease (which is prohibited).
 */
int fm37_finish(FM37Lease *lease) {
    if (!lease || lease->phase!=FM37_LEASE_ACTIVE) return -1;
    void *token=lease->os_userdata;
    lease->phase=FM37_LEASE_FINISHED;
    lease->owner=NULL;
    lease->os_userdata=NULL;
    return fm36_leave(token);
}

/* Irreversible: denial of future admission, NOT an OS stop.
 * The owner memory remains retained until process termination.
 */
int fm37_seal_token(void *os_userdata) {
    return fm36_seal(os_userdata);
}
