/* SPDX-License-Identifier: Apache-2.0 */
#ifndef FM_BUFFER_LIFECYCLE_H
#define FM_BUFFER_LIFECYCLE_H
#include "digital_signal.h"
#define FM_L_SLOTS 4U
#define FM_L_BLOCK 256U
typedef enum {FM_L_OK=0,FM_L_DONE,FM_L_FULL,FM_L_EMPTY,FM_L_FINAL_REQUIRED,
    FM_L_DRAIN_REQUIRED,FM_L_REJECTED,FM_L_STALE,FM_L_INVALIDATED,FM_L_EXPIRED,FM_L_ERROR} FMLifecycleResult;
typedef struct {uint64_t token,sequence;size_t count;double samples[FM_L_BLOCK];} FMQueuedBlock;
typedef struct {uint64_t sequence;size_t count;} FMBlockReceipt;
typedef struct {
    FMDigital digital;
    FMQueuedBlock queue[FM_L_SLOTS];
    unsigned head,count;
    uint64_t next_sequence;
} FMLifecycle;
/* Single serialized owner, except notify. No pointer to queued samples escapes
 * through these operations. Receipts contain only counts and sequence numbers.
 * Caller must not mutate internals or alias output receipts to engine storage. */
void fm_lifecycle_init(FMLifecycle *l);
void fm_lifecycle_notify(FMLifecycle *l);
FMLifecycleResult fm_lifecycle_prepare(FMLifecycle *l,const FMReadinessProfile *a,
    const FMReadinessProfile *b,const FMCommand *cmd,uint64_t now,uint64_t *token);
FMLifecycleResult fm_lifecycle_enqueue(FMLifecycle *l,const FMReadinessProfile *p,uint64_t token,uint64_t now);
FMLifecycleResult fm_lifecycle_consume(FMLifecycle *l,const FMReadinessProfile *p,uint64_t token,uint64_t now,FMBlockReceipt *receipt);
FMLifecycleResult fm_lifecycle_finish(FMLifecycle *l,const FMReadinessProfile *p,uint64_t token,uint64_t now,FMBlockReceipt *receipt);
FMLifecycleResult fm_lifecycle_stop(FMLifecycle *l,uint64_t token);
#endif
