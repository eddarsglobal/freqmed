/* SPDX-License-Identifier: Apache-2.0 */
#ifndef FM_INTEGRATED_BRIDGE_H
#define FM_INTEGRATED_BRIDGE_H
#include "unified_runtime.h"
typedef struct {
    FMReadinessProfile output;
    FMEndpoint input;
    unsigned input_alive_known,input_alive;
} FMIntegratedPair;
typedef enum {FM_PAIR_INCOMPLETE=0,FM_PAIR_UNSUITABLE,FM_PAIR_CHANGED,FM_PAIR_METADATA_ONLY} FMPairResult;
typedef struct {
    FMRuntime runtime;
    FMIntegratedPair pair;
    atomic_uint event_pending;
} FMIntegratedBridge;
/* Only metadata and a memory-only runtime. Equal nominal rates do not imply
 * a common clock or calibrated transfer function. Single owner except notify. */
FMPairResult fm_pair_assess(const FMIntegratedPair *a,const FMIntegratedPair *b);
void fm_bridge_init(FMIntegratedBridge *b);
void fm_bridge_notify(FMIntegratedBridge *b);
FMRuntimeResult fm_bridge_start(FMIntegratedBridge *b,const FMIntegratedPair *a,
    const FMIntegratedPair *p,const FMCommand *cmd,uint64_t now,uint64_t *token);
FMRuntimeResult fm_bridge_step(FMIntegratedBridge *b,const FMIntegratedPair *p,
    uint64_t token,uint64_t now,unsigned budget);
FMRuntimeResult fm_bridge_stop(FMIntegratedBridge *b,uint64_t token);
#endif
