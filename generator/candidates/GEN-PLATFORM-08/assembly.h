/* SPDX-License-Identifier: Apache-2.0 */
#ifndef FM_ASSEMBLY_H
#define FM_ASSEMBLY_H
#include "recovery.h"
#include "readiness.h"
typedef enum {FM_A_OFF=0,FM_A_PREPARED,FM_A_FAULT} FMAssemblyState;
typedef enum {FM_A_OK=0,FM_A_REJECTED,FM_A_BUSY,FM_A_STALE,FM_A_INVALIDATED,FM_A_EXPIRED,FM_A_ERROR} FMAssemblyResult;
typedef struct {
    FMRecovery recovery;
    FMReadinessProfile profile;
    FMGuardian guardian;
    FMAssemblyState state;
} FMAssembly;
/* Single owner, only notify is concurrent. No physical authority or output. */
void fm_assembly_init(FMAssembly *a);
void fm_assembly_notify(FMAssembly *a);
FMAssemblyResult fm_assembly_prepare(FMAssembly *a,const FMReadinessProfile *first,
    const FMReadinessProfile *second,const FMCommand *cmd,uint64_t now,uint64_t *token);
FMAssemblyResult fm_assembly_poll(FMAssembly *a,const FMReadinessProfile *p,uint64_t token,uint64_t now);
FMAssemblyResult fm_assembly_stop(FMAssembly *a,uint64_t token);
#endif
