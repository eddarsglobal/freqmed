/* SPDX-License-Identifier: Apache-2.0 */
#include "recovery.h"
#include <string.h>
static int equal(const FMEndpoint *a,const FMEndpoint *b) {
    return !strcmp(a->uid,b->uid) && a->channels==b->channels &&
        a->rate==b->rate && a->route==b->route && a->is_default==b->is_default;
}
static int dirty(FMRecovery *r) {
    return atomic_load_explicit(&r->monitor.pending,memory_order_acquire)!=0;
}
static void reset(FMRecovery *r,FMRecoveryState state) {
    memset(&r->profile,0,sizeof(r->profile));r->state=state;
}
void fm_recovery_init(FMRecovery *r) {
    if(r) {fm_binding_init(&r->binding);fm_monitor_init(&r->monitor);
        reset(r,FM_R_DISCOVERY_REQUIRED);}
}
void fm_recovery_notify(FMRecovery *r) {if(r) fm_monitor_mark(&r->monitor);}
FMRecoveryResult fm_recovery_begin(FMRecovery *r) {
    if(!r || r->binding.token || r->state==FM_R_FAULT ||
       r->state==FM_R_CAPTURING || r->state==FM_R_PREPARED) return FM_R_BAD_STATE;
    reset(r,FM_R_CAPTURING);
    (void)atomic_exchange_explicit(&r->monitor.pending,0U,memory_order_acq_rel);
    return FM_R_OK;
}
FMRecoveryResult fm_recovery_finish(FMRecovery *r,const FMSnapshot *a,const FMSnapshot *b) {
    if(!r||r->state!=FM_R_CAPTURING) return FM_R_BAD_STATE;
    unsigned i=0,j=0;
    if(dirty(r)) {reset(r,FM_R_DISCOVERY_REQUIRED);return FM_R_RETRY;}
    if(fm_binding_select(a,&i)!=FM_B_OK||fm_binding_select(b,&j)!=FM_B_OK) {
        reset(r,FM_R_DISCOVERY_REQUIRED);return FM_R_NO_PROFILE;
    }
    if(!equal(&a->endpoints[i],&b->endpoints[j])||dirty(r)) {
        reset(r,FM_R_DISCOVERY_REQUIRED);return FM_R_RETRY;
    }
    r->profile=b->endpoints[j];r->state=FM_R_READY;
    return FM_R_OK;
}
FMRecoveryResult fm_recovery_prepare(FMRecovery *r,const FMSnapshot *s,const FMIntegrationRequest *req,uint64_t now,uint64_t *token) {
    if(!r||!token||r->state!=FM_R_READY||r->binding.token) return FM_R_BAD_STATE;
    *token=0;
    unsigned i=0;
    if(dirty(r)||fm_binding_select(s,&i)!=FM_B_OK||!equal(&r->profile,&s->endpoints[i])) {
        reset(r,FM_R_DISCOVERY_REQUIRED);return FM_R_RETRY;
    }
    uint64_t local=0;
    if(fm_binding_prepare(&r->binding,s,req,now,&local)!=FM_B_OK)
        return FM_R_ERROR;
    if(dirty(r)) {
        if(fm_binding_close(&r->binding,local)!=FM_B_OK) {
            reset(r,FM_R_FAULT);return FM_R_ERROR;
        }
        reset(r,FM_R_DISCOVERY_REQUIRED);return FM_R_RETRY;
    }
    r->state=FM_R_PREPARED;*token=local;return FM_R_OK;
}
FMRecoveryResult fm_recovery_poll(FMRecovery *r,const FMSnapshot *s,uint64_t token,uint64_t now) {
    if(!r) return FM_R_BAD_STATE;
    if(!token||token!=r->binding.token) return FM_R_STALE;
    if(r->state!=FM_R_PREPARED) return FM_R_BAD_STATE;
    FMMonitorResult m=fm_monitor_poll(&r->monitor,&r->binding,s,token,now);
    if(m==FM_M_STABLE) return FM_R_OK;
    if(fm_binding_close(&r->binding,token)!=FM_B_OK) {
        reset(r,FM_R_FAULT);return FM_R_ERROR;
    }
    if(m==FM_M_INVALIDATED) {reset(r,FM_R_DISCOVERY_REQUIRED);return FM_R_INVALIDATED;}
    if(m==FM_M_EXPIRED) {reset(r,FM_R_DISCOVERY_REQUIRED);return FM_R_EXPIRED;}
    reset(r,FM_R_FAULT);return FM_R_ERROR;
}
FMRecoveryResult fm_recovery_close(FMRecovery *r,uint64_t token) {
    if(!r) return FM_R_BAD_STATE;
    if(!token||token!=r->binding.token) return FM_R_STALE;
    if(r->state!=FM_R_PREPARED) return FM_R_BAD_STATE;
    if(fm_binding_close(&r->binding,token)!=FM_B_OK) {
        reset(r,FM_R_FAULT);return FM_R_ERROR;
    }
    reset(r,FM_R_DISCOVERY_REQUIRED);return FM_R_OK;
}
