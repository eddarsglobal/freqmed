/* SPDX-License-Identifier: Apache-2.0 */
/* GEN-R28 SOURCE-ONLY C11 ADMISSION DESIGN; NOT AN INTEGRATED PATCH.
 * MUST NOT BE LINKED, LOADED OR USED TO GENERATE PHYSICAL OUTPUT.
 * This gate does not qualify AudioQueueRef, OS callback admission, or
 * CoreAudio disposal. The OS contract requires independent review.
 */
#include <stdatomic.h>
#include <stdbool.h>
#include <stdint.h>

/* Top bit seals admission; low bits count successfully entered users. */
#define FM_R28_CLOSED (UINT_FAST64_MAX ^ (UINT_FAST64_MAX >> 1))
#define FM_R28_COUNT_MASK (FM_R28_CLOSED - (uint_fast64_t)1)

typedef struct {
  atomic_uint_fast64_t state;
} FMR28AdmissionGate;

void fm_r28_gate_init(FMR28AdmissionGate *gate) {
  if (gate) atomic_init(&gate->state,0);
}

/* A single CAS, never a callback spin-loop: contention denies admission.
 * The caller must latch a failure and must not touch queue resources.
 * Userdata must remain valid even if this function is invoked late.
 */
bool fm_r28_gate_try_enter(FMR28AdmissionGate *gate) {
  if (!gate) return false;
  uint_fast64_t old=atomic_load_explicit(&gate->state,memory_order_acquire);
  if ((old & FM_R28_CLOSED) || (old & FM_R28_COUNT_MASK)==FM_R28_COUNT_MASK)
    return false;
  return atomic_compare_exchange_strong_explicit(
      &gate->state,&old,old+(uint_fast64_t)1,
      memory_order_acq_rel,memory_order_acquire);
}

/* Strict PRECONDITION: exactly one leave for each successful admission.
 * Incorrect pairing is forbidden: an underflow would invalidate the count.
 */
void fm_r28_gate_leave(FMR28AdmissionGate *gate) {
  if (gate) (void)atomic_fetch_sub_explicit(
      &gate->state,(uint_fast64_t)1,memory_order_acq_rel);
}

/* Seal once; there is deliberately no open/reset-after-publication API. */
void fm_r28_gate_close(FMR28AdmissionGate *gate) {
  if (gate) (void)atomic_fetch_or_explicit(
      &gate->state,FM_R28_CLOSED,memory_order_acq_rel);
}

/* Necessary C11 admission condition, NOT sufficient OS quiescence:
 * queue and buffers may still have undiscovered CoreAudio owners.
 */
bool fm_r28_gate_closed_and_empty(const FMR28AdmissionGate *gate) {
  if (!gate) return false;
  const uint_fast64_t state=atomic_load_explicit(
      &gate->state,memory_order_acquire);
  return (state & FM_R28_CLOSED)!=0 && (state & FM_R28_COUNT_MASK)==0;
}
