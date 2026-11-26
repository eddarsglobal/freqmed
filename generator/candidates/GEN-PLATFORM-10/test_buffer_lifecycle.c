/* SPDX-License-Identifier: Apache-2.0 */
#include "buffer_lifecycle.h"
#include <stdio.h>
#define C(x) do{if(!(x)){fprintf(stderr,"FAIL %d: %s\n",__LINE__,#x);return 1;}++n;}while(0)
static int empty(const FMLifecycle *l) {
    if(l->count||l->head||l->next_sequence)return 0;
    for(unsigned i=0;i<FM_L_SLOTS;i++){
        const FMQueuedBlock *b=&l->queue[i];
        if(b->count||b->token||b->sequence)return 0;
        for(unsigned j=0;j<FM_L_BLOCK;j++)if(b->samples[j]!=0)return 0;
    }
    return 1;
}
int main(void) {
    unsigned n=0;FMLifecycle l;fm_lifecycle_init(&l);
    FMReadinessProfile p={0},q;
    p.endpoint=(FMEndpoint){"SOFTWARE_TEST",2,48000,FM_ROUTE_BUILT_IN,1};
    p.alive_known=p.alive=p.running_known=p.ranges_known=p.buffer_known=p.buffer_range_known=1;
    p.range_count=1;p.rates[0]=(FMRateRange){48000,48000};
    p.buffer_frames=256;p.buffer_min=64;p.buffer_max=1024;
    FMCommand cmd={FM_ACOUSTIC,1000,0.25,40};
    uint64_t t=0,old=0,u=0;FMBlockReceipt r={0};
    C(empty(&l));
    C(fm_lifecycle_enqueue(&l,&p,0,100)==FM_L_STALE);
    C(fm_lifecycle_prepare(&l,&p,&p,&cmd,100,&t)==FM_L_OK&&t==1);
    C(fm_lifecycle_prepare(&l,&p,&p,&cmd,100,&u)==FM_L_REJECTED&&u==0);
    C(fm_lifecycle_consume(&l,&p,t,100,&r)==FM_L_EMPTY);
    C(fm_lifecycle_finish(&l,&p,t,100,&r)==FM_L_REJECTED);
    C(fm_lifecycle_enqueue(&l,&p,t,100)==FM_L_OK);
    C(fm_lifecycle_enqueue(&l,&p,t,100)==FM_L_OK);
    C(fm_lifecycle_enqueue(&l,&p,t,100)==FM_L_OK);
    C(fm_lifecycle_enqueue(&l,&p,t,100)==FM_L_OK&&l.count==4);
    C(fm_lifecycle_enqueue(&l,&p,t,100)==FM_L_FULL);
    C(fm_lifecycle_consume(&l,&p,t+1,101,&r)==FM_L_STALE&&r.count==0&&l.count==4);
    C(fm_lifecycle_consume(&l,&p,t,101,&r)==FM_L_OK&&r.sequence==1&&r.count==256);
    C(l.queue[0].count==0&&l.queue[0].samples[12]==0);
    C(fm_lifecycle_enqueue(&l,&p,t,101)==FM_L_OK&&l.count==4&&l.queue[0].sequence==5);
    C(fm_lifecycle_consume(&l,&p,t,101,&r)==FM_L_OK&&r.sequence==2);
    C(fm_lifecycle_consume(&l,&p,t,101,&r)==FM_L_OK&&r.sequence==3);
    C(fm_lifecycle_consume(&l,&p,t,101,&r)==FM_L_OK&&r.sequence==4);
    C(fm_lifecycle_consume(&l,&p,t,101,&r)==FM_L_OK&&r.sequence==5);
    C(fm_lifecycle_enqueue(&l,&p,t,101)==FM_L_OK);
    C(fm_lifecycle_enqueue(&l,&p,t,101)==FM_L_OK);
    C(fm_lifecycle_enqueue(&l,&p,t,101)==FM_L_DRAIN_REQUIRED);
    C(fm_lifecycle_finish(&l,&p,t,101,&r)==FM_L_DRAIN_REQUIRED);
    C(fm_lifecycle_consume(&l,&p,t,101,&r)==FM_L_OK&&r.sequence==6);
    C(fm_lifecycle_consume(&l,&p,t,101,&r)==FM_L_OK&&r.sequence==7);
    C(fm_lifecycle_enqueue(&l,&p,t,101)==FM_L_FINAL_REQUIRED);
    C(fm_lifecycle_finish(&l,&p,t,101,&r)==FM_L_DONE&&r.sequence==8&&r.count==128);
    C(empty(&l)&&l.digital.remaining==0&&l.digital.assembly.state==FM_A_OFF);
    old=t;C(fm_lifecycle_consume(&l,&p,old,102,&r)==FM_L_STALE&&r.count==0);
    C(fm_lifecycle_prepare(&l,&p,&p,&cmd,102,&t)==FM_L_OK&&t==2);
    C(fm_lifecycle_enqueue(&l,&p,t,102)==FM_L_OK);
    C(fm_lifecycle_stop(&l,old)==FM_L_STALE&&l.count==1);
    fm_lifecycle_notify(&l);
    C(fm_lifecycle_consume(&l,&p,t,103,&r)==FM_L_INVALIDATED&&r.count==0);
    C(empty(&l)&&l.digital.remaining==0);
    C(fm_lifecycle_prepare(&l,&p,&p,&cmd,104,&t)==FM_L_OK);
    C(fm_lifecycle_enqueue(&l,&p,t,104)==FM_L_OK);
    C(fm_lifecycle_consume(&l,&p,t,144,&r)==FM_L_EXPIRED&&r.count==0&&empty(&l));
    C(fm_lifecycle_prepare(&l,&p,&p,&cmd,145,&t)==FM_L_OK);
    C(fm_lifecycle_enqueue(&l,&p,t,145)==FM_L_OK);
    q=p;q.buffer_frames=512;
    C(fm_lifecycle_enqueue(&l,&q,t,146)==FM_L_INVALIDATED&&empty(&l));
    C(fm_lifecycle_prepare(&l,&p,&p,&cmd,147,&t)==FM_L_OK);
    C(fm_lifecycle_enqueue(&l,&p,t,147)==FM_L_OK);
    C(fm_lifecycle_stop(&l,t)==FM_L_OK&&empty(&l));
    C(fm_lifecycle_prepare(&l,&p,&p,&cmd,148,&t)==FM_L_OK);
    C(fm_lifecycle_enqueue(&l,&p,t,148)==FM_L_OK);
    C(fm_lifecycle_consume(&l,&p,t,147,&r)==FM_L_ERROR&&empty(&l)&&r.count==0);
    C(l.digital.assembly.state==FM_A_FAULT&&l.digital.assembly.guardian.state==FM_OFF);
    C(fm_acoustic_native_backend_available()==0);
    printf("GEN_PLATFORM_10_ASSERTIONS=%u PASS\n",n);return 0;
}
