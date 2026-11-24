/* SPDX-License-Identifier: Apache-2.0 */
#include "monitor.h"
void fm_monitor_init(FMMonitor *m) { if(m) atomic_init(&m->pending,0U); }
void fm_monitor_mark(FMMonitor *m) {
    if(m) atomic_store_explicit(&m->pending,1U,memory_order_release);
}
FMMonitorResult fm_monitor_poll(FMMonitor *m,FMBinding *b,const FMSnapshot *s,uint64_t token,uint64_t now) {
    if(!m||!b) return FM_M_ERROR;
    if(!token) return b->token?FM_M_STALE:FM_M_IDLE;
    if(token!=b->token) return FM_M_STALE;
    if(b->sessions.acoustic.state!=FM_S_PREPARED) return FM_M_ERROR;
    unsigned dirty=atomic_exchange_explicit(&m->pending,0U,memory_order_acq_rel);
    FMBResult r=fm_binding_refresh(b,dirty?NULL:s,token,now);
    if(r==FM_B_CHANGED) return FM_M_INVALIDATED;
    if(r!=FM_B_OK) return FM_M_ERROR;
    if(b->sessions.acoustic.state==FM_S_EXPIRED) return FM_M_EXPIRED;
    /* A notification concurrent with refresh must not be ignored. */
    if(atomic_exchange_explicit(&m->pending,0U,memory_order_acq_rel)) {
        return fm_binding_refresh(b,NULL,token,now)==FM_B_CHANGED?
            FM_M_INVALIDATED:FM_M_ERROR;
    }
    return FM_M_STABLE;
}
