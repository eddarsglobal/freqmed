/* SPDX-License-Identifier: Apache-2.0 */
/*
 * GEN-R41 — ISOLATED C11 TICKET CAPACITY, INDEX ALIAS & FAILURE CONTAINMENT.
 * Compile-only, never linked/loaded/called, no CoreAudio/physical output.
 * Fixed four process-lifetime slots, NEVER RECYCLED. This is an intentionally
 * capacity-limited research candidate, NOT suitable for unbounded callbacks.
 * An index handle eliminates exposure of the slot POINTER but is COPYABLE
 * and FORGEABLE; it is NOT a secure capability. Owner aliases are EXTERNAL.
 * The sticky fault mask records selected local errors, not OS quiescence.
 */
#include "r41_index_ticket.h"
#include <stddef.h>
#include <stdatomic.h>

extern int fm36_prepare_once(void *owner,void **userdata_out);
extern int fm36_mark_exposed(void *userdata);
extern int fm36_try_enter(void *userdata,void **owner_out);
extern int fm36_leave(void *userdata);
extern int fm36_seal(void *userdata);

enum {
 FM41_UNUSED=0u, FM41_RESERVED=1u, FM41_ACTIVE=2u,
 FM41_FINISHED=3u, FM41_REJECTED=4u
};
typedef struct {
 atomic_uint phase;
 void *token;
} FM41PrivateSlot;
static FM41PrivateSlot fm41_slots[FM41_MAX_LIFETIME_TICKETS]={
 {ATOMIC_VAR_INIT(FM41_UNUSED),NULL},
 {ATOMIC_VAR_INIT(FM41_UNUSED),NULL},
 {ATOMIC_VAR_INIT(FM41_UNUSED),NULL},
 {ATOMIC_VAR_INIT(FM41_UNUSED),NULL}
};
static atomic_uint fm41_fault_latch=ATOMIC_VAR_INIT(0u);

static void fm41_latch(unsigned fault) {
 (void)atomic_fetch_or_explicit(&fm41_fault_latch,fault,memory_order_acq_rel);
}

/* Sticky, process-lifetime fault record; snapshot is NOT proof of a safe OS stop. */
unsigned fm41_fault_snapshot(void) {
 return atomic_load_explicit(&fm41_fault_latch,memory_order_acquire);
}

/* If the C36 one-shot claim is consumed, owner must remain allocated
 * even on expose failure, by an EXTERNAL owner-lifetime obligation.
 */
int fm41_register_owner_once(void *owner,void **userdata_out) {
 if (!owner || !userdata_out) {
  fm41_latch(FM41_FAULT_REGISTER); return -1;
 }
 *userdata_out=NULL;
 if (fm36_prepare_once(owner,userdata_out)!=0) {
  fm41_latch(FM41_FAULT_REGISTER); return -1;
 }
 if (fm36_mark_exposed(*userdata_out)!=0) {
  fm41_latch(FM41_FAULT_REGISTER); return -1;
 }
 return 0;
}

/* No overflow allocation or slot reuse. Sticky previous faults deny entry
 * when OBSERVED, but do not prove global admission/stop atomicity with OS.
 */
int fm41_begin(void *userdata,FM41TicketRef *ticket_out,void **owner_out) {
 if (!ticket_out || !owner_out) {
  fm41_latch(FM41_FAULT_ADMISSION); return -1;
 }
 ticket_out->slot_id=FM41_INVALID_SLOT;
 *owner_out=NULL;
 if (fm41_fault_snapshot()!=0u) return -1;
 for (size_t i=0u;i<FM41_MAX_LIFETIME_TICKETS;i++) {
  FM41PrivateSlot *slot=&fm41_slots[i];
  unsigned expected=FM41_UNUSED;
  if (!atomic_compare_exchange_strong_explicit(
       &slot->phase,&expected,FM41_RESERVED,
       memory_order_acq_rel,memory_order_acquire)) continue;
  if (fm41_fault_snapshot()!=0u) {
   atomic_store_explicit(&slot->phase,FM41_REJECTED,memory_order_release);
   return -1;
  }
  void *owner=NULL;
  if (fm36_try_enter(userdata,&owner)!=0) {
   fm41_latch(FM41_FAULT_ADMISSION);
   atomic_store_explicit(&slot->phase,FM41_REJECTED,memory_order_release);
   return -1;
  }
  if (!owner) {
   int leave_status=fm36_leave(userdata);
   fm41_latch(FM41_FAULT_NULL_OWNER);
   if (leave_status!=0) fm41_latch(FM41_FAULT_LEAVE_FAILURE);
   atomic_store_explicit(&slot->phase,FM41_REJECTED,memory_order_release);
   return -1;
  }
  slot->token=userdata;
  atomic_store_explicit(&slot->phase,FM41_ACTIVE,memory_order_release);
  *owner_out=owner;
  ticket_out->slot_id=(unsigned)i+1u;
  return 0;
 }
 fm41_latch(FM41_FAULT_CAPACITY);
 return -1;
}

/* Index bounds validated before accessing slot. A COPIED or FORGED valid
 * index can still compete for an active slot: no authentication here.
 * Exactly one CAS winner can call leave; nobody enforces completion.
 */
int fm41_complete(FM41TicketRef ticket) {
 if (ticket.slot_id==FM41_INVALID_SLOT ||
     ticket.slot_id>FM41_MAX_LIFETIME_TICKETS) {
  fm41_latch(FM41_FAULT_INVALID_HANDLE);
  return -1;
 }
 FM41PrivateSlot *slot=&fm41_slots[ticket.slot_id-1u];
 unsigned expected=FM41_ACTIVE;
 if (!atomic_compare_exchange_strong_explicit(
      &slot->phase,&expected,FM41_FINISHED,
      memory_order_acq_rel,memory_order_acquire)) {
  fm41_latch(FM41_FAULT_DUPLICATE_LEAVE);
  return -1;
 }
 int status=fm36_leave(slot->token);
 if (status!=0) fm41_latch(FM41_FAULT_LEAVE_FAILURE);
 return status;
}

/* Sealing cannot prove OS quiescence or physical cutoff. */
int fm41_seal(void *userdata) {
 int status=fm36_seal(userdata);
 if (status!=0) fm41_latch(FM41_FAULT_SEAL);
 return status;
}
