/* SPDX-License-Identifier: Apache-2.0 */
#ifndef FM_UNIFIED_RUNTIME_H
#define FM_UNIFIED_RUNTIME_H
#include "buffer_lifecycle.h"
#define FM_U_BUDGET_MAX 16U
typedef enum {FM_U_IDLE=0,FM_U_RUNNING,FM_U_COMPLETE,FM_U_STOPPED,FM_U_INVALIDATED,FM_U_EXPIRED,FM_U_FAULT} FMRuntimeState;
typedef enum {FM_U_OK=0,FM_U_REJECTED,FM_U_STALE,FM_U_TERMINAL} FMRuntimeResult;
typedef struct {
    FMLifecycle lifecycle;
    FMRuntimeState state;
    uint64_t token,expected,consumed,blocks;
} FMRuntime;
/* Serialized owner; only notify may be concurrent. Never copy or mutate internals.
 * Each step uses a fresh caller-provided profile and monotonic timestamp.
 * No thread, physical backend or sample export. */
void fm_runtime_init(FMRuntime *r);
void fm_runtime_notify(FMRuntime *r);
int fm_runtime_clean(const FMRuntime *r);
FMRuntimeResult fm_runtime_start(FMRuntime *r,const FMReadinessProfile *a,
    const FMReadinessProfile *b,const FMCommand *cmd,uint64_t now,uint64_t *token);
FMRuntimeResult fm_runtime_step(FMRuntime *r,const FMReadinessProfile *p,uint64_t token,uint64_t now,unsigned budget);
FMRuntimeResult fm_runtime_stop(FMRuntime *r,uint64_t token);
#endif
