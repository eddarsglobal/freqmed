/* SPDX-License-Identifier: Apache-2.0 */
#ifndef FM_DIGITAL_SIGNAL_H
#define FM_DIGITAL_SIGNAL_H
#include "assembly.h"
#define FM_DIGITAL_BLOCK_MAX 4096U
#define FM_DIGITAL_RATE_MAX 384000U
typedef enum {FM_D_OK=0,FM_D_DONE,FM_D_REJECTED,FM_D_BUSY,FM_D_STALE,FM_D_INVALIDATED,FM_D_EXPIRED,FM_D_ERROR} FMDigitalResult;
typedef struct {
    FMAssembly assembly;
    double phase,step,level;
    uint64_t remaining;
} FMDigital;
/* Single owner except notify. Buffers and token output must be disjoint from engine
 * and input objects. Memory only; no audio device, file or playback interface.
 * A block is a mono numerical vector, not a hardware stream format. */
void fm_digital_init(FMDigital *d);
void fm_digital_notify(FMDigital *d);
FMDigitalResult fm_digital_prepare(FMDigital *d,const FMReadinessProfile *a,
    const FMReadinessProfile *b,const FMCommand *cmd,uint64_t now,uint64_t *token);
FMDigitalResult fm_digital_block(FMDigital *d,const FMReadinessProfile *p,uint64_t token,
    uint64_t now,double *out,size_t capacity,size_t requested,size_t *written);
FMDigitalResult fm_digital_stop(FMDigital *d,uint64_t token);
#endif
