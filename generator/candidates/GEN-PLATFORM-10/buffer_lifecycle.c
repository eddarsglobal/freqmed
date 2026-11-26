/* SPDX-License-Identifier: Apache-2.0 */
#include "buffer_lifecycle.h"
#include <math.h>
#include <string.h>
static void purge(FMLifecycle *l) {
    memset(l->queue,0,sizeof(l->queue));l->head=0;l->count=0;l->next_sequence=0;
}
static void reset_numeric(FMLifecycle *l) {
    l->digital.phase=0;l->digital.step=0;l->digital.level=0;l->digital.remaining=0;
}
void fm_lifecycle_init(FMLifecycle *l) {if(l){fm_digital_init(&l->digital);purge(l);}}
void fm_lifecycle_notify(FMLifecycle *l) {if(l)fm_digital_notify(&l->digital);}
static FMLifecycleResult digital_result(FMDigitalResult r) {
    switch(r) {
        case FM_D_OK:return FM_L_OK;
        case FM_D_DONE:return FM_L_DONE;
        case FM_D_REJECTED:case FM_D_BUSY:return FM_L_REJECTED;
        case FM_D_STALE:return FM_L_STALE;
        case FM_D_INVALIDATED:return FM_L_INVALIDATED;
        case FM_D_EXPIRED:return FM_L_EXPIRED;
        default:return FM_L_ERROR;
    }
}
static FMLifecycleResult check(FMLifecycle *l,const FMReadinessProfile *p,uint64_t token,uint64_t now) {
    if(!l)return FM_L_REJECTED;
    if(!token||token!=l->digital.assembly.recovery.binding.token)return FM_L_STALE;
    FMAssemblyResult r=fm_assembly_poll(&l->digital.assembly,p,token,now);
    if(r==FM_A_OK)return FM_L_OK;
    purge(l);reset_numeric(l);
    if(r==FM_A_INVALIDATED)return FM_L_INVALIDATED;
    if(r==FM_A_EXPIRED)return FM_L_EXPIRED;
    return FM_L_ERROR;
}
static FMLifecycleResult abort_session(FMLifecycle *l,uint64_t token) {
    if(l->digital.assembly.recovery.binding.token==token && token)
        (void)fm_digital_stop(&l->digital,token);
    purge(l);reset_numeric(l);return FM_L_ERROR;
}
static int valid_block(const FMQueuedBlock *b,uint64_t token) {
    if(b->token!=token||!b->count||b->count>FM_L_BLOCK)return 0;
    for(size_t i=0;i<b->count;i++)
        if(!isfinite(b->samples[i])||fabs(b->samples[i])>1.0)return 0;
    return 1;
}
FMLifecycleResult fm_lifecycle_prepare(FMLifecycle *l,const FMReadinessProfile *a,
    const FMReadinessProfile *b,const FMCommand *cmd,uint64_t now,uint64_t *token) {
    if(!l||!token)return FM_L_REJECTED;
    *token=0;
    if(l->digital.assembly.recovery.binding.token)return FM_L_REJECTED;
    purge(l);
    FMLifecycleResult r=digital_result(fm_digital_prepare(&l->digital,a,b,cmd,now,token));
    if(r==FM_L_OK)l->next_sequence=1;
    return r;
}
FMLifecycleResult fm_lifecycle_enqueue(FMLifecycle *l,const FMReadinessProfile *p,uint64_t token,uint64_t now) {
    FMLifecycleResult r=check(l,p,token,now);
    if(r!=FM_L_OK)return r;
    if(l->digital.remaining<=FM_L_BLOCK)
        return l->count?FM_L_DRAIN_REQUIRED:FM_L_FINAL_REQUIRED;
    if(l->count==FM_L_SLOTS)return FM_L_FULL;
    if(!l->next_sequence||l->next_sequence==UINT64_MAX)return abort_session(l,token);
    unsigned tail=(l->head+l->count)%FM_L_SLOTS;
    FMQueuedBlock *b=&l->queue[tail];
    size_t written=0;
    r=digital_result(fm_digital_block(&l->digital,p,token,now,b->samples,FM_L_BLOCK,FM_L_BLOCK,&written));
    if(r!=FM_L_OK){purge(l);reset_numeric(l);return r==FM_L_DONE?FM_L_ERROR:r;}
    b->token=token;b->sequence=l->next_sequence++;b->count=written;
    if(written!=FM_L_BLOCK||!valid_block(b,token))return abort_session(l,token);
    ++l->count;return FM_L_OK;
}
FMLifecycleResult fm_lifecycle_consume(FMLifecycle *l,const FMReadinessProfile *p,uint64_t token,uint64_t now,FMBlockReceipt *receipt) {
    if(!receipt)return FM_L_REJECTED;
    *receipt=(FMBlockReceipt){0};
    FMLifecycleResult r=check(l,p,token,now);
    if(r!=FM_L_OK)return r;
    if(!l->count)return FM_L_EMPTY;
    FMQueuedBlock *b=&l->queue[l->head];
    if(!valid_block(b,token))return abort_session(l,token);
    FMBlockReceipt local={b->sequence,b->count};
    r=check(l,p,token,now);
    if(r!=FM_L_OK)return r;
    memset(b,0,sizeof(*b));
    l->head=(l->head+1)%FM_L_SLOTS;--l->count;
    *receipt=local;return FM_L_OK;
}
FMLifecycleResult fm_lifecycle_finish(FMLifecycle *l,const FMReadinessProfile *p,uint64_t token,uint64_t now,FMBlockReceipt *receipt) {
    if(!receipt)return FM_L_REJECTED;
    *receipt=(FMBlockReceipt){0};
    FMLifecycleResult r=check(l,p,token,now);
    if(r!=FM_L_OK)return r;
    if(l->count)return FM_L_DRAIN_REQUIRED;
    if(!l->digital.remaining||l->digital.remaining>FM_L_BLOCK)return FM_L_REJECTED;
    if(!l->next_sequence||l->next_sequence==UINT64_MAX)return abort_session(l,token);
    /* PLATFORM-09 closes its session on the final block. Consume this block
     * internally in the same operation; never leave a queue after closure. */
    FMQueuedBlock *b=&l->queue[0];
    size_t written=0;uint64_t sequence=l->next_sequence;
    r=digital_result(fm_digital_block(&l->digital,p,token,now,b->samples,FM_L_BLOCK,FM_L_BLOCK,&written));
    b->token=token;b->sequence=sequence;b->count=written;
    int valid=r==FM_L_DONE&&valid_block(b,token);
    purge(l);reset_numeric(l);
    if(!valid)return r==FM_L_DONE?FM_L_ERROR:r;
    if(atomic_load_explicit(&l->digital.assembly.recovery.monitor.pending,memory_order_acquire))
        return FM_L_INVALIDATED;
    *receipt=(FMBlockReceipt){sequence,written};return FM_L_DONE;
}
FMLifecycleResult fm_lifecycle_stop(FMLifecycle *l,uint64_t token) {
    if(!l)return FM_L_REJECTED;
    FMLifecycleResult r=digital_result(fm_digital_stop(&l->digital,token));
    if(r!=FM_L_STALE){purge(l);reset_numeric(l);}
    return r;
}
