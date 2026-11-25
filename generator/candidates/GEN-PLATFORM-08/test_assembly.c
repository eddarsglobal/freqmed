/* SPDX-License-Identifier: Apache-2.0 */
#include "assembly.h"
#include <stdio.h>
#define C(x) do{if(!(x)){fprintf(stderr,"FAIL %d: %s\n",__LINE__,#x);return 1;}++n;}while(0)
int main(void) {
    unsigned n=0;FMAssembly a;fm_assembly_init(&a);
    FMReadinessProfile p={0},q;
    p.endpoint=(FMEndpoint){"TEST",2,44100,FM_ROUTE_BUILT_IN,1};
    p.alive_known=p.alive=p.running_known=p.ranges_known=p.buffer_known=p.buffer_range_known=1;
    p.range_count=1;p.rates[0]=(FMRateRange){44100,44100};
    p.buffer_frames=256;p.buffer_min=64;p.buffer_max=1024;
    FMCommand cmd={FM_ACOUSTIC,1.0,0.5,10};
    uint64_t t=0,old=0,spare=0;
    C(a.state==FM_A_OFF&&a.guardian.state==FM_OFF);
    C(fm_assembly_prepare(NULL,&p,&p,&cmd,100,&t)==FM_A_REJECTED);
    C(fm_assembly_prepare(&a,&p,&p,&cmd,100,NULL)==FM_A_REJECTED);
    C(fm_assembly_prepare(&a,NULL,&p,&cmd,100,&t)==FM_A_REJECTED);
    C(fm_assembly_prepare(&a,&p,&p,NULL,100,&t)==FM_A_REJECTED);
    q=p;q.running=1;C(fm_assembly_prepare(&a,&p,&q,&cmd,100,&t)==FM_A_REJECTED);
    cmd.channel=FM_ELECTROMAGNETIC;C(fm_assembly_prepare(&a,&p,&p,&cmd,100,&t)==FM_A_REJECTED);
    cmd.channel=FM_ACOUSTIC;cmd.duration_ms=0;C(fm_assembly_prepare(&a,&p,&p,&cmd,100,&t)==FM_A_REJECTED);
    cmd.duration_ms=10;C(fm_assembly_prepare(&a,&p,&p,&cmd,100,&t)==FM_A_OK&&t==1);
    C(a.state==FM_A_PREPARED&&a.guardian.state==FM_OFF&&!a.guardian.physical_output_enabled);
    C(fm_assembly_prepare(&a,&p,&p,&cmd,100,&spare)==FM_A_BUSY);
    C(fm_assembly_poll(&a,&p,t+1,101)==FM_A_STALE);
    C(fm_assembly_poll(&a,&p,t,101)==FM_A_OK);
    q=p;q.buffer_frames=512;
    C(fm_assembly_poll(&a,&q,t,102)==FM_A_INVALIDATED);
    C(a.state==FM_A_OFF&&a.recovery.binding.token==0&&!a.profile.endpoint.uid[0]);
    old=t;C(fm_assembly_stop(&a,t)==FM_A_STALE);
    C(fm_assembly_prepare(&a,&p,&p,&cmd,103,&t)==FM_A_OK&&t==2);
    C(fm_assembly_stop(&a,old)==FM_A_STALE);
    fm_assembly_notify(&a);
    C(fm_assembly_poll(&a,&p,t,104)==FM_A_INVALIDATED);
    C(fm_assembly_prepare(&a,&p,&p,&cmd,105,&t)==FM_A_OK);
    C(fm_assembly_poll(&a,&p,t,115)==FM_A_EXPIRED);
    C(a.guardian.state==FM_OFF&&a.recovery.binding.token==0);
    C(fm_assembly_prepare(&a,&p,&p,&cmd,116,&t)==FM_A_OK);
    C(fm_assembly_stop(&a,t)==FM_A_OK);
    C(a.state==FM_A_OFF&&a.recovery.binding.sessions.em.state==FM_S_EMPTY);
    C(fm_assembly_prepare(&a,&p,&p,&cmd,117,&t)==FM_A_OK);
    C(fm_assembly_poll(&a,&p,t,116)==FM_A_ERROR);
    C(a.state==FM_A_FAULT&&a.guardian.state==FM_OFF);
    C(fm_assembly_prepare(&a,&p,&p,&cmd,118,&t)==FM_A_ERROR);
    C(fm_acoustic_native_backend_available()==0);
    printf("GEN_PLATFORM_08_ASSERTIONS=%u PASS\n",n);return 0;
}
