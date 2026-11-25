/* SPDX-License-Identifier: Apache-2.0 */
#ifndef FM_RECOVERY_H
#define FM_RECOVERY_H
#include "monitor.h"
typedef enum {FM_R_DISCOVERY_REQUIRED=0,FM_R_CAPTURING,FM_R_READY,FM_R_PREPARED,FM_R_FAULT} FMRecoveryState;
typedef enum {FM_R_OK=0,FM_R_BAD_STATE,FM_R_NO_PROFILE,FM_R_RETRY,FM_R_STALE,FM_R_INVALIDATED,FM_R_EXPIRED,FM_R_ERROR} FMRecoveryResult;
typedef struct {
    FMBinding binding;
    FMMonitor monitor;
    FMEndpoint profile;
    FMRecoveryState state;
} FMRecovery;
/* Only notify may run concurrently. All other operations have one owner.
 * Initialize once; never copy the atomic-containing object or mutate internals.
 * Discovery receipts are process-local metadata, not permission to emit. */
void fm_recovery_init(FMRecovery *r);
void fm_recovery_notify(FMRecovery *r);
FMRecoveryResult fm_recovery_begin(FMRecovery *r);
FMRecoveryResult fm_recovery_finish(FMRecovery *r,const FMSnapshot *a,const FMSnapshot *b);
FMRecoveryResult fm_recovery_prepare(FMRecovery *r,const FMSnapshot *s,const FMIntegrationRequest *req,uint64_t now,uint64_t *token);
FMRecoveryResult fm_recovery_poll(FMRecovery *r,const FMSnapshot *s,uint64_t token,uint64_t now);
FMRecoveryResult fm_recovery_close(FMRecovery *r,uint64_t token);
#endif
