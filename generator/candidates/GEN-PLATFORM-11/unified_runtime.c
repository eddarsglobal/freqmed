/* SPDX-License-Identifier: Apache-2.0 */
#include "unified_runtime.h"
void fm_runtime_init(FMRuntime *r) {
    if(r){fm_lifecycle_init(&r->lifecycle);r->state=FM_U_IDLE;
        r->token=r->expected=r->consumed=r->blocks=0;}
}
void fm_runtime_notify(FMRuntime *r){if(r)fm_lifecycle_notify(&r->lifecycle);}
int fm_runtime_clean(const FMRuntime *r) {
    if(!r)return 0;
    const FMLifecycle *l=&r->lifecycle;
    if(l->count||l->head||l->next_sequence||l->digital.remaining||
       l->digital.phase||l->digital.step||l->digital.level||
       l->digital.assembly.recovery.binding.token||
       l->digital.assembly.guardian.state!=FM_OFF||
       l->digital.assembly.guardian.physical_output_enabled)return 0;
    for(unsigned i=0;i<FM_L_SLOTS;i++) {
        const FMQueuedBlock *b=&l->queue[i];
        if(b->token||b->sequence||b->count)return 0;
        for(unsigned j=0;j<FM_L_BLOCK;j++)if(b->samples[j]!=0)return 0;
    }
    return 1;
}
static FMRuntimeResult terminal(FMRuntime *r,FMRuntimeState state) {
    uint64_t active=r->lifecycle.digital.assembly.recovery.binding.token;
    if(active&&fm_lifecycle_stop(&r->lifecycle,active)!=FM_L_OK)state=FM_U_FAULT;
    if(!fm_runtime_clean(r))state=FM_U_FAULT;
    r->token=0;r->state=state;return FM_U_TERMINAL;
}
FMRuntimeResult fm_runtime_start(FMRuntime *r,const FMReadinessProfile *a,
    const FMReadinessProfile *b,const FMCommand *cmd,uint64_t now,uint64_t *token) {
    if(!r||!token)return FM_U_REJECTED;
    *token=0;
    if(r->state==FM_U_RUNNING||r->state==FM_U_FAULT)return FM_U_REJECTED;
    if(!fm_runtime_clean(r))return terminal(r,FM_U_FAULT);
    uint64_t t=0;
    FMLifecycleResult result=fm_lifecycle_prepare(&r->lifecycle,a,b,cmd,now,&t);
    if(result!=FM_L_OK) {
        if(result==FM_L_REJECTED&&fm_runtime_clean(r))return FM_U_REJECTED;
        return terminal(r,FM_U_FAULT);
    }
    r->token=t;r->expected=r->lifecycle.digital.remaining;
    r->consumed=r->blocks=0;r->state=FM_U_RUNNING;*token=t;
    return FM_U_OK;
}
static int accept(FMRuntime *r,const FMBlockReceipt *receipt,size_t expected) {
    if(!expected||receipt->count!=expected||receipt->sequence!=r->blocks+1||
       r->consumed>r->expected||receipt->count>r->expected-r->consumed)return 0;
    r->consumed+=receipt->count;++r->blocks;return 1;
}
FMRuntimeResult fm_runtime_step(FMRuntime *r,const FMReadinessProfile *p,uint64_t token,uint64_t now,unsigned budget) {
    if(!r)return FM_U_REJECTED;
    if(!token||token!=r->token||r->state!=FM_U_RUNNING)return FM_U_STALE;
    if(!budget||budget>FM_U_BUDGET_MAX)return FM_U_REJECTED;
    FMLifecycle *l=&r->lifecycle;
    for(unsigned i=0;i<budget;i++) {
        FMLifecycleResult q;
        FMBlockReceipt receipt={0};
        if(l->digital.remaining>FM_L_BLOCK&&l->count<FM_L_SLOTS) {
            q=fm_lifecycle_enqueue(l,p,token,now);
            if(q==FM_L_OK)continue;
        } else if(l->count) {
            q=fm_lifecycle_consume(l,p,token,now,&receipt);
            if(q==FM_L_OK) {
                if(!accept(r,&receipt,FM_L_BLOCK))return terminal(r,FM_U_FAULT);
                continue;
            }
        } else {
            size_t last=(size_t)l->digital.remaining;
            q=fm_lifecycle_finish(l,p,token,now,&receipt);
            if(q==FM_L_DONE) {
                if(!accept(r,&receipt,last)||r->consumed!=r->expected)
                    return terminal(r,FM_U_FAULT);
                return terminal(r,FM_U_COMPLETE);
            }
        }
        if(q==FM_L_INVALIDATED)return terminal(r,FM_U_INVALIDATED);
        if(q==FM_L_EXPIRED)return terminal(r,FM_U_EXPIRED);
        return terminal(r,FM_U_FAULT);
    }
    return FM_U_OK;
}
FMRuntimeResult fm_runtime_stop(FMRuntime *r,uint64_t token) {
    if(!r)return FM_U_REJECTED;
    if(!token||token!=r->token||r->state!=FM_U_RUNNING)return FM_U_STALE;
    return terminal(r,FM_U_STOPPED);
}
