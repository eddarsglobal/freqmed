/* SPDX-License-Identifier: Apache-2.0 */
#include "interlock.h"
int fm_interlock_init(FMInterlock *g,uint64_t now,uint64_t lease_ms){
    if(!g)return 0;
    atomic_init(&g->reasons,0);g->prepared=0;g->last=now;g->deadline=now;
    if(!atomic_is_lock_free(&g->reasons)||!lease_ms||lease_ms>10000||UINT64_MAX-now<lease_ms){
        atomic_store(&g->reasons,FM_R3_FAULT);return 0;
    }
    g->deadline=now+lease_ms;g->prepared=1;return 1;
}
void fm_interlock_trip(FMInterlock *g,unsigned reason){
    if(g)atomic_fetch_or_explicit(&g->reasons,reason?reason:FM_R3_FAULT,memory_order_release);
}
unsigned fm_interlock_reasons(const FMInterlock *g){
    return g?atomic_load_explicit(&g->reasons,memory_order_acquire):FM_R3_FAULT;
}
int fm_interlock_poll(FMInterlock *g,uint64_t now){
    if(!g||!g->prepared||fm_interlock_reasons(g))return 0;
    if(now<g->last)fm_interlock_trip(g,FM_R3_CLOCK);
    else if(now>=g->deadline)fm_interlock_trip(g,FM_R3_TIMEOUT);
    else g->last=now;
    return fm_interlock_reasons(g)==0;
}
int fm_interlock_physical_allowed(const FMInterlock *g){(void)g;return 0;}
