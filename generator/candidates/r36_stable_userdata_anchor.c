/* SPDX-License-Identifier: Apache-2.0 */
/*
 * FREQMED GEN-R36: ISOLATED, UNLINKED, source-only C11 pre-admission anchor.
 * No AudioQueue symbols, hardware I/O, callback dispatch or runtime activation.
 *
 * Architectural candidate, NOT approved for insertion into R31:
 * - OS userdata would refer to a PROCESS-LIFETIME static anchor, not ctx.
 * - A single irrevocable claim prevents reuse or ABA across generations.
 * - A published owner's heap allocation MUST remain live until process exit.
 * - No function here frees it, clears owner or re-opens after seal.
 * - C11 admission counters do NOT certify OS callback quiescence.
 * - Atomic publication/close does NOT prove OS/hardware stop or memory
 *   safety of unrelated real application code.
 * - The entire object is NEVER linked or loaded into the production binary.
 */
#include <stdatomic.h>
#include <stddef.h>
#include <stdint.h>

typedef enum {
  FM36_EMPTY=0u,
  FM36_PREPARED=1u,
  FM36_EXPOSED=2u,
  FM36_SEALED=3u
} FM36Phase;

typedef struct {
  atomic_uint phase;
  _Atomic(void *) owner;
  atomic_uint admitted;
} FM36StableAnchor;

static FM36StableAnchor fm36_anchor = {
  ATOMIC_VAR_INIT(FM36_EMPTY),
  ATOMIC_VAR_INIT(NULL),
  ATOMIC_VAR_INIT(0u)
};
static atomic_flag fm36_one_shot_claim=ATOMIC_FLAG_INIT;

/* Return a stable process-lifetime userdata address, exactly once.
 * The owner is a caller-owned heap context and MUST NEVER be freed
 * after this claim, even if preparing/publishing/OS creation fails.
 * This deliberately sacrifices one owner to preserve its lifetime.
 */
int fm36_prepare_once(void *owner, void **userdata_out) {
  if (!owner || !userdata_out) return -1;
  if (atomic_flag_test_and_set_explicit(
          &fm36_one_shot_claim,memory_order_acq_rel)) return -1;
  atomic_store_explicit(&fm36_anchor.owner,owner,memory_order_relaxed);
  atomic_store_explicit(&fm36_anchor.admitted,0u,memory_order_relaxed);
  atomic_store_explicit(&fm36_anchor.phase,FM36_PREPARED,memory_order_release);
  *userdata_out=(void *)&fm36_anchor;
  return 0;
}

/* The controller MUST expose BEFORE passing userdata to the OS.
 * Does not call CoreAudio; this is a source-only integration contract.
 */
int fm36_mark_exposed(void *userdata) {
  if (userdata!=(void *)&fm36_anchor) return -1;
  unsigned expected=FM36_PREPARED;
  if (!atomic_compare_exchange_strong_explicit(
          &fm36_anchor.phase,&expected,FM36_EXPOSED,
          memory_order_acq_rel,memory_order_acquire)) return -1;
  return 0;
}

/* A callback would call this first, BEFORE dereferencing owner.
 * The token equality comparison does not dereference untrusted userdata.
 * A second phase check prevents an admission seen AFTER sealing.
 * Already admitted callbacks may race with sealing: active is diagnostic,
 * NOT an OS quiescence proof, and owner remains pinned until process exit.
 */
int fm36_try_enter(void *userdata, void **owner_out) {
  if (!owner_out || userdata!=(void *)&fm36_anchor) return -1;
  *owner_out=NULL;
  if (atomic_load_explicit(&fm36_anchor.phase,memory_order_acquire)
      !=FM36_EXPOSED) return -1;
  (void)atomic_fetch_add_explicit(&fm36_anchor.admitted,1u,
                                  memory_order_acq_rel);
  if (atomic_load_explicit(&fm36_anchor.phase,memory_order_acquire)
      !=FM36_EXPOSED) {
    (void)atomic_fetch_sub_explicit(&fm36_anchor.admitted,1u,
                                    memory_order_acq_rel);
    return -1;
  }
  void *owner=atomic_load_explicit(&fm36_anchor.owner,memory_order_acquire);
  if (!owner) {
    (void)atomic_fetch_sub_explicit(&fm36_anchor.admitted,1u,
                                    memory_order_acq_rel);
    return -1;
  }
  *owner_out=owner;
  return 0;
}

/* One leave per successful enter is an external callback contract.
 * CAS prevents underflow if a caller wrongly repeats leave.
 */
int fm36_leave(void *userdata) {
  if (userdata!=(void *)&fm36_anchor) return -1;
  unsigned seen=atomic_load_explicit(&fm36_anchor.admitted,
                                    memory_order_acquire);
  while (seen>0u) {
    if (atomic_compare_exchange_weak_explicit(
          &fm36_anchor.admitted,&seen,seen-1u,
          memory_order_acq_rel,memory_order_acquire)) return 0;
  }
  return -1;
}

/* Irreversible seal; NEVER free owner, reuse token or reset counters.
 * Cannot claim that OS has stopped invoking callbacks.
 */
int fm36_seal(void *userdata) {
  if (userdata!=(void *)&fm36_anchor) return -1;
  unsigned seen=atomic_load_explicit(&fm36_anchor.phase,
                                    memory_order_acquire);
  while (seen==FM36_PREPARED || seen==FM36_EXPOSED) {
    if (atomic_compare_exchange_weak_explicit(
          &fm36_anchor.phase,&seen,FM36_SEALED,
          memory_order_acq_rel,memory_order_acquire)) return 0;
  }
  return -1;
}
