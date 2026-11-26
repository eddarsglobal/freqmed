/* SPDX-License-Identifier: Apache-2.0 */
#include "integrated_bridge.h"
#include <math.h>
#include <string.h>
static FMPairResult check(const FMIntegratedPair *p) {
    if(!p||!p->input_alive_known)return FM_PAIR_INCOMPLETE;
    if(p->input_alive_known!=1||p->input_alive!=1||
       p->input.route!=FM_ROUTE_BUILT_IN||p->output.endpoint.route!=FM_ROUTE_BUILT_IN||
       p->input.is_default!=1||!p->input.uid[0]||
       !memchr(p->input.uid,0,sizeof(p->input.uid))||
       !p->input.channels||p->input.channels>256||
       !isfinite(p->input.rate)||p->input.rate<=0||
       p->input.rate!=p->output.endpoint.rate)return FM_PAIR_UNSUITABLE;
    return FM_PAIR_METADATA_ONLY;
}
FMPairResult fm_pair_assess(const FMIntegratedPair *a,const FMIntegratedPair *b) {
    FMPairResult x=check(a),y=check(b);
    if(x!=FM_PAIR_METADATA_ONLY)return x;
    if(y!=FM_PAIR_METADATA_ONLY)return y;
    FMReadinessResult r=fm_readiness_assess(&a->output,&b->output);
    if(r==FM_RD_CHANGED)return FM_PAIR_CHANGED;
    if(r!=FM_RD_METADATA_ONLY)return FM_PAIR_UNSUITABLE;
    if(strcmp(a->input.uid,b->input.uid)||a->input.channels!=b->input.channels||
       a->input.rate!=b->input.rate)return FM_PAIR_CHANGED;
    return FM_PAIR_METADATA_ONLY;
}
void fm_bridge_init(FMIntegratedBridge *b) {
    if(b){fm_runtime_init(&b->runtime);memset(&b->pair,0,sizeof(b->pair));
        atomic_init(&b->event_pending,0U);}
}
void fm_bridge_notify(FMIntegratedBridge *b) {
    if(b)atomic_store_explicit(&b->event_pending,1U,memory_order_release);
}
static void clear(FMIntegratedBridge *b){memset(&b->pair,0,sizeof(b->pair));}
FMRuntimeResult fm_bridge_start(FMIntegratedBridge *b,const FMIntegratedPair *a,
    const FMIntegratedPair *p,const FMCommand *cmd,uint64_t now,uint64_t *token) {
    if(!b||!token)return FM_U_REJECTED;
    *token=0;
    if(b->runtime.state==FM_U_RUNNING)return FM_U_REJECTED;
    if(atomic_exchange_explicit(&b->event_pending,0U,memory_order_acq_rel))
        return FM_U_REJECTED; /* require fresh captures after observed change */
    if(fm_pair_assess(a,p)!=FM_PAIR_METADATA_ONLY)return FM_U_REJECTED;
    FMRuntimeResult q=fm_runtime_start(&b->runtime,&a->output,&p->output,cmd,now,token);
    if(q==FM_U_OK)b->pair=*p;
    return q;
}
FMRuntimeResult fm_bridge_step(FMIntegratedBridge *b,const FMIntegratedPair *p,
    uint64_t token,uint64_t now,unsigned budget) {
    if(!b)return FM_U_REJECTED;
    if(!token||token!=b->runtime.token||b->runtime.state!=FM_U_RUNNING)return FM_U_STALE;
    if(!budget||budget>FM_U_BUDGET_MAX)return FM_U_REJECTED;
    unsigned dirty=atomic_exchange_explicit(&b->event_pending,0U,memory_order_acq_rel);
    int valid=fm_pair_assess(&b->pair,p)==FM_PAIR_METADATA_ONLY;
    if(dirty||!valid)fm_runtime_notify(&b->runtime);
    FMRuntimeResult q=fm_runtime_step(&b->runtime,valid?&p->output:NULL,token,now,budget);
    if(q==FM_U_OK&&atomic_exchange_explicit(&b->event_pending,0U,memory_order_acq_rel)) {
        fm_runtime_notify(&b->runtime);
        q=fm_runtime_step(&b->runtime,NULL,token,now,1);
    }
    if(q==FM_U_TERMINAL)clear(b);
    return q;
}
FMRuntimeResult fm_bridge_stop(FMIntegratedBridge *b,uint64_t token) {
    if(!b)return FM_U_REJECTED;
    FMRuntimeResult q=fm_runtime_stop(&b->runtime,token);
    if(q==FM_U_TERMINAL)clear(b);
    return q;
}
