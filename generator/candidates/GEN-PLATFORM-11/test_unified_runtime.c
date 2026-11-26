/* SPDX-License-Identifier: Apache-2.0 */
#include "unified_runtime.h"
#include <stdio.h>
#define C(x) do{if(!(x)){fprintf(stderr,"FAIL %d: %s\n",__LINE__,#x);return 1;}++n;}while(0)
int main(void) {
    unsigned n=0;FMRuntime r;fm_runtime_init(&r);
    FMReadinessProfile p={0},q;
    p.endpoint=(FMEndpoint){"SOFTWARE_TEST",2,48000,FM_ROUTE_BUILT_IN,1};
    p.alive_known=p.alive=p.running_known=p.ranges_known=p.buffer_known=p.buffer_range_known=1;
    p.range_count=1;p.rates[0]=(FMRateRange){48000,48000};
    p.buffer_frames=256;p.buffer_min=64;p.buffer_max=1024;
    FMCommand cmd={FM_ACOUSTIC,1000,0.25,40};
    uint64_t t=0,u=0,old=0;
    C(r.state==FM_U_IDLE&&fm_runtime_clean(&r));
    C(!fm_runtime_clean(NULL));
    C(fm_runtime_start(NULL,&p,&p,&cmd,100,&t)==FM_U_REJECTED);
    C(fm_runtime_start(&r,&p,&p,&cmd,100,NULL)==FM_U_REJECTED);
    C(fm_runtime_step(&r,&p,0,100,1)==FM_U_STALE);
    q=p;q.running=1;
    C(fm_runtime_start(&r,&p,&q,&cmd,100,&t)==FM_U_REJECTED);
    C(fm_runtime_start(&r,&p,&p,&cmd,100,&t)==FM_U_OK&&t==1);
    C(r.expected==1920&&r.state==FM_U_RUNNING);
    C(fm_runtime_start(&r,&p,&p,&cmd,100,&u)==FM_U_REJECTED&&u==0);
    C(fm_runtime_step(&r,&p,t+1,100,1)==FM_U_STALE);
    C(fm_runtime_step(&r,&p,t,100,0)==FM_U_REJECTED);
    C(fm_runtime_step(&r,&p,t,100,17)==FM_U_REJECTED);
    C(fm_runtime_step(&r,&p,t,100,4)==FM_U_OK&&r.lifecycle.count==4);
    C(fm_runtime_step(&r,&p,t,101,1)==FM_U_OK&&r.consumed==256&&r.blocks==1);
    C(fm_runtime_step(&r,&p,t,101,16)==FM_U_TERMINAL);
    C(r.state==FM_U_COMPLETE&&r.consumed==1920&&r.blocks==8);
    C(fm_runtime_clean(&r)&&r.token==0);
    old=t;
    C(fm_runtime_stop(&r,old)==FM_U_STALE);
    C(fm_runtime_start(&r,&p,&p,&cmd,102,&t)==FM_U_OK&&t==2);
    C(fm_runtime_stop(&r,old)==FM_U_STALE);
    C(fm_runtime_step(&r,&p,t,102,2)==FM_U_OK&&r.lifecycle.count==2);
    C(fm_runtime_stop(&r,t)==FM_U_TERMINAL&&r.state==FM_U_STOPPED);
    C(fm_runtime_clean(&r));
    C(fm_runtime_start(&r,&p,&p,&cmd,103,&t)==FM_U_OK);
    C(fm_runtime_step(&r,&p,t,103,1)==FM_U_OK);
    fm_runtime_notify(&r);
    C(fm_runtime_step(&r,&p,t,104,1)==FM_U_TERMINAL&&r.state==FM_U_INVALIDATED);
    C(fm_runtime_clean(&r));
    C(fm_runtime_start(&r,&p,&p,&cmd,105,&t)==FM_U_OK);
    C(fm_runtime_step(&r,&p,t,145,1)==FM_U_TERMINAL&&r.state==FM_U_EXPIRED);
    C(fm_runtime_clean(&r));
    C(fm_runtime_start(&r,&p,&p,&cmd,146,&t)==FM_U_OK);
    q=p;q.buffer_frames=512;
    C(fm_runtime_step(&r,&q,t,147,1)==FM_U_TERMINAL&&r.state==FM_U_INVALIDATED);
    C(fm_runtime_clean(&r));
    cmd.duration_ms=1;
    C(fm_runtime_start(&r,&p,&p,&cmd,148,&t)==FM_U_OK&&r.expected==48);
    C(fm_runtime_step(&r,&p,t,148,1)==FM_U_TERMINAL&&r.state==FM_U_COMPLETE);
    C(r.consumed==48&&r.blocks==1&&fm_runtime_clean(&r));
    cmd.duration_ms=40;
    C(fm_runtime_start(&r,&p,&p,&cmd,149,&t)==FM_U_OK);
    C(fm_runtime_step(&r,&p,t,149,1)==FM_U_OK);
    C(fm_runtime_step(&r,&p,t,148,1)==FM_U_TERMINAL&&r.state==FM_U_FAULT);
    C(fm_runtime_clean(&r));
    C(fm_runtime_start(&r,&p,&p,&cmd,150,&t)==FM_U_REJECTED);
    C(fm_acoustic_native_backend_available()==0);
    printf("GEN_PLATFORM_11_ASSERTIONS=%u PASS\n",n);return 0;
}
