/* SPDX-License-Identifier: Apache-2.0 */
/*
 * FREQMED GEN-R42 — ISOLATED C11 ADMISSION GATE + OPAQUE TICKET.
 * COMPILE ONLY: never link/load/call/dispatch, no CoreAudio or EM output.
 *
 * A single C11 CAS word joins local CLOSED with lifetime permit count.
 * Any successful permit reservation linearizes BEFORE a concurrent CLOSED
 * transition; an already reserved admission may still publish afterwards.
 * This is NOT a global callback quiescence or OS stop guarantee.
 *
 * Four process-lifetime slots are never reused; exhaustion closes locally.
 * Opaque ticket pointers hide index-only guessing, NOT pointer duplication,
 * disclosure, address forgery, illicit memory access, or missed completion.
 * Owner lifetime, exactly-once completion and physical cutoff UNPROVEN.
 */
#include "r42_admission_gate_ticket.h"
#include <stddef.h>
#include <stdatomic.h>

extern int fm36_prepare_once(void *owner,void **userdata_out);
extern int fm36_mark_exposed(void *userdata);
extern int fm36_try_enter(void *userdata,void **owner_out);
extern int fm36_leave(void *userdata);
extern int fm36_seal(void *userdata);

enum {
 FM42_UNUSED=0u, FM42_RESERVED=1u, FM42_ACTIVE=2u,
 FM42_FINISHED=3u, FM42_REJECTED=4u
};
enum { FM42_CLOSED=0x80000000u, FM42_COUNT_MASK=0x0000ffffu };

struct FM42Ticket {
 atomic_uint phase;
 void *token;
};
static struct FM42Ticket fm42_slots[FM42_LIFETIME_CAPACITY]={
 {ATOMIC_VAR_INIT(FM42_UNUSED),NULL},
 {ATOMIC_VAR_INIT(FM42_UNUSED),NULL},
 {ATOMIC_VAR_INIT(FM42_UNUSED),NULL},
 {ATOMIC_VAR_INIT(FM42_UNUSED),NULL}
};
static atomic_uint fm42_gate=ATOMIC_VAR_INIT(0u);
static atomic_uint fm42_faults=ATOMIC_VAR_INIT(0u);

/* Close first, THEN publish reason. A closed gate is not a stopped OS queue. */
static void fm42_latch(unsigned fault) {
 (void)atomic_fetch_or_explicit(&fm42_gate,FM42_CLOSED,memory_order_acq_rel);
 (void)atomic_fetch_or_explicit(&fm42_faults,fault,memory_order_acq_rel);
}
unsigned fm42_fault_snapshot(void) {
 return atomic_load_explicit(&fm42_faults,memory_order_acquire);
}

/* Reserve a finite lifetime permit with one CLOSED/count CAS word.
 * Once CLOSED is visible in the modification order, NO NEW reservation CAS
 * can succeed. Existing reservations and callbacks remain outstanding.
 */
static int fm42_reserve_permit(void) {
 unsigned state=atomic_load_explicit(&fm42_gate,memory_order_acquire);
 for (;;) {
  if ((state & FM42_CLOSED)!=0u) return -1;
  if ((state & FM42_COUNT_MASK)>=FM42_LIFETIME_CAPACITY) {
   fm42_latch(FM42_FAULT_CAPACITY); return -1;
  }
  unsigned desired=state+1u;
  if (atomic_compare_exchange_weak_explicit(
       &fm42_gate,&state,desired,
       memory_order_acq_rel,memory_order_acquire)) return 0;
 }
}

/* R36 claim is one-shot; owner must remain alive until process exit even
 * if exposure/registration fails, by EXTERNAL lifetime contract.
 */
int fm42_register_owner_once(void *owner,void **userdata_out) {
 if (!owner || !userdata_out) {
  fm42_latch(FM42_FAULT_REGISTRATION); return -1;
 }
 *userdata_out=NULL;
 if (fm36_prepare_once(owner,userdata_out)!=0) {
  fm42_latch(FM42_FAULT_REGISTRATION); return -1;
 }
 if (fm36_mark_exposed(*userdata_out)!=0) {
  fm42_latch(FM42_FAULT_REGISTRATION); return -1;
 }
 return 0;
}

/* No fallback allocation, no slot recycle, no callback dispatch.
 * A fault may close the gate AFTER reservation or even AFTER the last
 * observed gate check; there is no publication/closure joint CAS.
 */
int fm42_begin(void *userdata,FM42Ticket **ticket_out,void **owner_out) {
 if (!ticket_out || !owner_out) {
  fm42_latch(FM42_FAULT_ADMISSION); return -1;
 }
 *ticket_out=NULL;
 *owner_out=NULL;
 if (fm42_reserve_permit()!=0) return -1;
 for (size_t i=0u;i<FM42_LIFETIME_CAPACITY;i++) {
  struct FM42Ticket *slot=&fm42_slots[i];
  unsigned expected=FM42_UNUSED;
  if (!atomic_compare_exchange_strong_explicit(
       &slot->phase,&expected,FM42_RESERVED,
       memory_order_acq_rel,memory_order_acquire)) continue;
  if ((atomic_load_explicit(&fm42_gate,memory_order_acquire)
        & FM42_CLOSED)!=0u) {
   atomic_store_explicit(&slot->phase,FM42_REJECTED,memory_order_release);
   return -1;
  }
  void *owner=NULL;
  if (fm36_try_enter(userdata,&owner)!=0) {
   fm42_latch(FM42_FAULT_ADMISSION);
   atomic_store_explicit(&slot->phase,FM42_REJECTED,memory_order_release);
   return -1;
  }
  if (!owner) {
   int rc=fm36_leave(userdata);
   fm42_latch(FM42_FAULT_NO_OWNER);
   if (rc!=0) fm42_latch(FM42_FAULT_LEAVE);
   atomic_store_explicit(&slot->phase,FM42_REJECTED,memory_order_release);
   return -1;
  }
  if ((atomic_load_explicit(&fm42_gate,memory_order_acquire)
        & FM42_CLOSED)!=0u) {
   int rc=fm36_leave(userdata);
   if (rc!=0) fm42_latch(FM42_FAULT_LEAVE);
   atomic_store_explicit(&slot->phase,FM42_REJECTED,memory_order_release);
   return -1;
  }
  slot->token=userdata;
  atomic_store_explicit(&slot->phase,FM42_ACTIVE,memory_order_release);
  *owner_out=owner;
  *ticket_out=slot;
  return 0;
 }
 fm42_latch(FM42_FAULT_INTERNAL);
 return -1;
}

/* Compare private addresses BEFORE any pointer dereference. A leaked or
 * guessed valid private address may still prematurely complete the ticket.
 * At-most-once CAS prevents double leave, NOT absent or stolen exits.
 */
int fm42_complete(FM42Ticket *ticket) {
 if (!ticket) {
  fm42_latch(FM42_FAULT_BAD_TICKET); return -1;
 }
 for (size_t i=0u;i<FM42_LIFETIME_CAPACITY;i++) {
  struct FM42Ticket *slot=&fm42_slots[i];
  if (ticket!=slot) continue;
  unsigned expected=FM42_ACTIVE;
  if (!atomic_compare_exchange_strong_explicit(
       &slot->phase,&expected,FM42_FINISHED,
       memory_order_acq_rel,memory_order_acquire)) {
   fm42_latch(FM42_FAULT_DUPLICATE_EXIT);
   return -1;
  }
  int rc=fm36_leave(slot->token);
  if (rc!=0) fm42_latch(FM42_FAULT_LEAVE);
  return rc;
 }
 fm42_latch(FM42_FAULT_BAD_TICKET);
 return -1;
}

/* A CLOSED gate forbids new permit reservations; OS and all preexisting
 * callbacks are NOT drained by this local operation.
 */
int fm42_seal(void *userdata) {
 (void)atomic_fetch_or_explicit(&fm42_gate,FM42_CLOSED,memory_order_acq_rel);
 int rc=fm36_seal(userdata);
 if (rc!=0) fm42_latch(FM42_FAULT_SEAL);
 return rc;
}
