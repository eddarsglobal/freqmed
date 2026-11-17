/* SPDX-License-Identifier: Apache-2.0 */
/*
 * FREQMED GEN-R43 — ISOLATED PUBLICATION-AUTHORITY CAS AND BOUND EXIT.
 * C11 object COMPILED UNLINKED ONLY. Never execute or dispatch OS callbacks.
 *
 * Gate word: CLOSED bit 31, lifetime reservations bits 0..7,
 * local authorization commits bits 8..15. All three are in ONE atomic_uint.
 * Reservation and authorization each have their own CAS linearization point.
 * Authorizations after CLOSED are refused in gate modification order.
 * IMPORTANT: even a pre-CLOSED authorization may cause a later owner_out
 * publication after CLOSED. This code does NOT guarantee post-close
 * callback quiescence, actual CoreAudio stop, or memory lifetime of owner.
 *
 * A completion must match the ticket's bound OS userdata pointer, but both
 * pointers can be copied/forged once known. No secure authentication.
 * Four process-lifetime slots are never recycled. No production capacity.
 */
#include "r43_publication_authority.h"
#include <stddef.h>
#include <stdatomic.h>

extern int fm36_prepare_once(void *owner,void **userdata_out);
extern int fm36_mark_exposed(void *userdata);
extern int fm36_try_enter(void *userdata,void **owner_out);
extern int fm36_leave(void *userdata);
extern int fm36_seal(void *userdata);

enum {
 FM43_UNUSED=0u, FM43_RESERVED=1u, FM43_ACTIVE=2u,
 FM43_FINISHED=3u, FM43_REJECTED=4u
};
enum {
 FM43_CLOSED=0x80000000u, FM43_RESERVATIONS_MASK=0x000000ffu,
 FM43_AUTH_SHIFT=8u, FM43_AUTH_INCREMENT=0x00000100u,
 FM43_AUTH_MASK=0x0000ff00u
};

struct FM43Ticket {
 atomic_uint phase;
 void *os_userdata;
};
static struct FM43Ticket fm43_slots[FM43_LIFETIME_TICKETS]={
 {ATOMIC_VAR_INIT(FM43_UNUSED),NULL},
 {ATOMIC_VAR_INIT(FM43_UNUSED),NULL},
 {ATOMIC_VAR_INIT(FM43_UNUSED),NULL},
 {ATOMIC_VAR_INIT(FM43_UNUSED),NULL}
};
static atomic_uint fm43_gate=ATOMIC_VAR_INIT(0u);
static atomic_uint fm43_faults=ATOMIC_VAR_INIT(0u);

static void fm43_latch(unsigned fault) {
 (void)atomic_fetch_or_explicit(&fm43_gate,FM43_CLOSED,memory_order_acq_rel);
 (void)atomic_fetch_or_explicit(&fm43_faults,fault,memory_order_acq_rel);
}
unsigned fm43_fault_snapshot(void) {
 return atomic_load_explicit(&fm43_faults,memory_order_acquire);
}

static int fm43_reserve(void) {
 unsigned state=atomic_load_explicit(&fm43_gate,memory_order_acquire);
 for (;;) {
  if ((state & FM43_CLOSED)!=0u) return -1;
  if ((state & FM43_RESERVATIONS_MASK)>=FM43_LIFETIME_TICKETS) {
   fm43_latch(FM43_FAULT_CAPACITY);
   return -1;
  }
  unsigned desired=state+1u;
  if (atomic_compare_exchange_weak_explicit(
       &fm43_gate,&state,desired,
       memory_order_acq_rel,memory_order_acquire)) return 0;
 }
}

/* A successful authorization is ordered against CLOSED in the same atomic
 * modification order. It is NOT equivalent to callback data handoff or
 * an OS-wide drain. Reservations already won are never rolled back.
 */
static int fm43_authorize(void) {
 unsigned state=atomic_load_explicit(&fm43_gate,memory_order_acquire);
 for (;;) {
  if ((state & FM43_CLOSED)!=0u) return -1;
  unsigned used=state & FM43_RESERVATIONS_MASK;
  unsigned authorized=(state & FM43_AUTH_MASK)>>FM43_AUTH_SHIFT;
  if (authorized>=used) return -1;
  unsigned desired=state+FM43_AUTH_INCREMENT;
  if (atomic_compare_exchange_weak_explicit(
       &fm43_gate,&state,desired,
       memory_order_acq_rel,memory_order_acquire)) return 0;
 }
}

/* Once R36 one-shot claim is taken, owner lifetime remains externally
 * obligated through process termination, including failed exposure.
 */
int fm43_register_owner_once(void *owner,void **userdata_out) {
 if (!owner || !userdata_out) {
  fm43_latch(FM43_FAULT_REGISTER); return -1;
 }
 *userdata_out=NULL;
 if (fm36_prepare_once(owner,userdata_out)!=0) {
  fm43_latch(FM43_FAULT_REGISTER); return -1;
 }
 if (fm36_mark_exposed(*userdata_out)!=0) {
  fm43_latch(FM43_FAULT_REGISTER); return -1;
 }
 return 0;
}

/* No heap fallback; exactly four lifetime reservations per process.
 * A successful auth CAS may still be followed by CLOSED before the
 * actual pointer publication below. This remains a CRITICAL OPEN gate.
 */
int fm43_begin(void *userdata,FM43Ticket **ticket_out,void **owner_out) {
 if (!ticket_out || !owner_out) {
  fm43_latch(FM43_FAULT_ADMISSION); return -1;
 }
 *ticket_out=NULL;
 *owner_out=NULL;
 if (fm43_reserve()!=0) return -1;
 for (size_t i=0u;i<FM43_LIFETIME_TICKETS;i++) {
  struct FM43Ticket *slot=&fm43_slots[i];
  unsigned expected=FM43_UNUSED;
  if (!atomic_compare_exchange_strong_explicit(
       &slot->phase,&expected,FM43_RESERVED,
       memory_order_acq_rel,memory_order_acquire)) continue;
  void *owner=NULL;
  if (fm36_try_enter(userdata,&owner)!=0) {
   fm43_latch(FM43_FAULT_ADMISSION);
   atomic_store_explicit(&slot->phase,FM43_REJECTED,memory_order_release);
   return -1;
  }
  if (!owner) {
   int leave_rc=fm36_leave(userdata);
   fm43_latch(FM43_FAULT_OWNER_NULL);
   if (leave_rc!=0) fm43_latch(FM43_FAULT_LEAVE);
   atomic_store_explicit(&slot->phase,FM43_REJECTED,memory_order_release);
   return -1;
  }
  if (fm43_authorize()!=0) {
   int leave_rc=fm36_leave(userdata);
   fm43_latch(FM43_FAULT_PUBLISH);
   if (leave_rc!=0) fm43_latch(FM43_FAULT_LEAVE);
   atomic_store_explicit(&slot->phase,FM43_REJECTED,memory_order_release);
   return -1;
  }
  slot->os_userdata=userdata;
  atomic_store_explicit(&slot->phase,FM43_ACTIVE,memory_order_release);
  *owner_out=owner;
  *ticket_out=slot;
  return 0;
 }
 fm43_latch(FM43_FAULT_CAPACITY);
 return -1;
}

/* Require ticket address membership and matching userdata for exit.
 * Both are externally reproducible; this is binding, NOT authentication.
 * A winning ACTIVE->FINISHED CAS allows at-most-once R36 leave.
 */
int fm43_complete(FM43Ticket *ticket,void *expected_userdata) {
 if (!ticket || !expected_userdata) {
  fm43_latch(FM43_FAULT_BAD_TICKET); return -1;
 }
 for (size_t i=0u;i<FM43_LIFETIME_TICKETS;i++) {
  struct FM43Ticket *slot=&fm43_slots[i];
  if (ticket!=slot) continue;
  if (atomic_load_explicit(&slot->phase,memory_order_acquire)!=FM43_ACTIVE) {
   fm43_latch(FM43_FAULT_DUPLICATE_EXIT); return -1;
  }
  if (slot->os_userdata!=expected_userdata) {
   fm43_latch(FM43_FAULT_TOKEN_MISMATCH); return -1;
  }
  unsigned expected=FM43_ACTIVE;
  if (!atomic_compare_exchange_strong_explicit(
       &slot->phase,&expected,FM43_FINISHED,
       memory_order_acq_rel,memory_order_acquire)) {
   fm43_latch(FM43_FAULT_DUPLICATE_EXIT); return -1;
  }
  int rc=fm36_leave(slot->os_userdata);
  if (rc!=0) fm43_latch(FM43_FAULT_LEAVE);
  return rc;
 }
 fm43_latch(FM43_FAULT_BAD_TICKET);
 return -1;
}

int fm43_seal(void *userdata) {
 (void)atomic_fetch_or_explicit(&fm43_gate,FM43_CLOSED,memory_order_acq_rel);
 int rc=fm36_seal(userdata);
 if (rc!=0) fm43_latch(FM43_FAULT_SEAL);
 return rc;
}
