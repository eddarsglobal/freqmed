/* SPDX-License-Identifier: Apache-2.0 */
#include "event_evidence.h"
static int category_ok(unsigned c) {return c && !(c&~FM_EVENT_MASK);}
void fm_event_init(FMEventLatch *l) {
    if(l){l->first=(FMEvent){0};atomic_init(&l->phase,0);}
}
int fm_event_arm(FMEventLatch *l) {
    unsigned expected=0;
    return l && atomic_compare_exchange_strong_explicit(&l->phase,&expected,1,
        memory_order_acq_rel,memory_order_acquire);
}
int fm_event_record(FMEventLatch *l,unsigned category,uint64_t ms) {
    unsigned expected=1;
    if(!l||!category_ok(category)||
        !atomic_compare_exchange_strong_explicit(&l->phase,&expected,2,
            memory_order_acq_rel,memory_order_acquire)) return 0;
    l->first=(FMEvent){category,ms};
    atomic_store_explicit(&l->phase,3,memory_order_release);
    return 1;
}
int fm_event_read(const FMEventLatch *l,FMEvent *out) {
    if(!l||!out||atomic_load_explicit(&l->phase,memory_order_acquire)!=3) return 0;
    *out=l->first;return 1;
}
int fm_event_evidence_complete(const FMEventEvidence *e) {
    return e && category_ok(e->category) && e->prepared==1 &&
        e->invalidated==1 && e->closed==1 && e->rediscovered==1 &&
        e->stale_rejected==1 && e->new_session==0 && e->cleanup==1 &&
        e->prepared_ms<=e->event_ms && e->event_ms<=e->consumed_ms &&
        e->consumed_ms<=e->rediscovered_ms;
}
