/* SPDX-License-Identifier: Apache-2.0 */
#include "digital_signal.h"
#include <math.h>
#include <stdio.h>
#define C(x) do{if(!(x)){fprintf(stderr,"FAIL %d: %s\n",__LINE__,#x);return 1;}++n;}while(0)
static int zeros(const double *x,size_t n){for(size_t i=0;i<n;i++)if(x[i]!=0)return 0;return 1;}
int main(void) {
    unsigned n=0;FMDigital d,e;fm_digital_init(&d);fm_digital_init(&e);
    FMReadinessProfile p={0},q;
    p.endpoint=(FMEndpoint){"SOFTWARE_TEST",2,48000,FM_ROUTE_BUILT_IN,1};
    p.alive_known=p.alive=p.running_known=p.ranges_known=p.buffer_known=p.buffer_range_known=1;
    p.range_count=1;p.rates[0]=(FMRateRange){48000,48000};
    p.buffer_frames=256;p.buffer_min=64;p.buffer_max=1024;
    FMCommand cmd={FM_ACOUSTIC,1000.0,0.25,10};
    uint64_t t=0,u=0,old=0;size_t w=0;double x[512],y[512];
    C(d.assembly.state==FM_A_OFF && d.remaining==0);
    C(fm_digital_prepare(NULL,&p,&p,&cmd,100,&t)==FM_D_REJECTED);
    C(fm_digital_prepare(&d,&p,&p,&cmd,100,NULL)==FM_D_REJECTED);
    C(fm_digital_prepare(&d,&p,&p,NULL,100,&t)==FM_D_REJECTED);
    cmd.frequency_hz=24000;C(fm_digital_prepare(&d,&p,&p,&cmd,100,&t)==FM_D_REJECTED);
    cmd.frequency_hz=NAN;C(fm_digital_prepare(&d,&p,&p,&cmd,100,&t)==FM_D_REJECTED);
    cmd.frequency_hz=1000;cmd.channel=FM_ELECTROMAGNETIC;
    C(fm_digital_prepare(&d,&p,&p,&cmd,100,&t)==FM_D_REJECTED);
    cmd.channel=FM_ACOUSTIC;q=p;q.running=1;
    C(fm_digital_prepare(&d,&p,&q,&cmd,100,&t)==FM_D_REJECTED);
    C(fm_digital_prepare(&d,&p,&p,&cmd,100,&t)==FM_D_OK&&t==1&&d.remaining==480);
    C(d.assembly.guardian.state==FM_OFF);
    C(fm_digital_prepare(&d,&p,&p,&cmd,100,&u)==FM_D_BUSY);
    C(fm_digital_block(&d,&p,t,100,x,512,513,&w)==FM_D_REJECTED&&w==0);
    C(fm_digital_block(&d,&p,t,100,x,512,0,&w)==FM_D_REJECTED);
    C(fm_digital_block(&d,&p,t,100,NULL,512,1,&w)==FM_D_REJECTED);
    C(fm_digital_block(&d,&p,t+1,100,x,512,8,&w)==FM_D_STALE&&w==0&&zeros(x,8));
    C(d.remaining==480);
    C(fm_digital_block(&d,&p,t,100,x,512,17,&w)==FM_D_OK&&w==17);
    C(fm_digital_block(&d,&p,t,100,x+17,495,31,&w)==FM_D_OK&&w==31);
    C(fm_digital_prepare(&e,&p,&p,&cmd,100,&u)==FM_D_OK);
    C(fm_digital_block(&e,&p,u,100,y,512,48,&w)==FM_D_OK&&w==48);
    int identical=1,bounded=1;
    for(size_t i=0;i<48;i++){if(x[i]!=y[i])identical=0;if(!isfinite(x[i])||fabs(x[i])>0.25)bounded=0;}
    C(identical);
    C(bounded);
    C(fabs(x[0])<1e-12&&fabs(x[12]-0.25)<1e-12&&fabs(x[24])<1e-12&&fabs(x[36]+0.25)<1e-12);
    C(fm_digital_stop(&e,u)==FM_D_OK);
    C(fm_digital_block(&d,&p,t,101,x,512,512,&w)==FM_D_DONE&&w==432);
    C(zeros(x+432,80));
    C(d.remaining==0&&d.phase==0&&d.assembly.state==FM_A_OFF);
    old=t;
    C(fm_digital_block(&d,&p,old,102,x,512,8,&w)==FM_D_STALE&&zeros(x,8));
    C(fm_digital_prepare(&d,&p,&p,&cmd,102,&t)==FM_D_OK&&t==2);
    C(fm_digital_stop(&d,old)==FM_D_STALE);
    fm_digital_notify(&d);
    C(fm_digital_block(&d,&p,t,103,x,512,8,&w)==FM_D_INVALIDATED&&w==0&&zeros(x,8));
    C(d.remaining==0);
    C(fm_digital_prepare(&d,&p,&p,&cmd,104,&t)==FM_D_OK);
    C(fm_digital_block(&d,&p,t,114,x,512,8,&w)==FM_D_EXPIRED&&w==0&&zeros(x,8));
    C(fm_digital_prepare(&d,&p,&p,&cmd,115,&t)==FM_D_OK);
    q=p;q.buffer_frames=512;
    C(fm_digital_block(&d,&q,t,116,x,512,8,&w)==FM_D_INVALIDATED&&zeros(x,8));
    C(fm_digital_prepare(&d,&p,&p,&cmd,117,&t)==FM_D_OK);
    C(fm_digital_stop(&d,t)==FM_D_OK&&d.remaining==0);
    C(fm_digital_prepare(&d,&p,&p,&cmd,118,&t)==FM_D_OK);
    C(fm_digital_block(&d,&p,t,117,x,512,8,&w)==FM_D_ERROR&&zeros(x,8));
    C(d.assembly.state==FM_A_FAULT&&d.assembly.guardian.state==FM_OFF);
    C(fm_acoustic_native_backend_available()==0);
    printf("GEN_PLATFORM_09_ASSERTIONS=%u PASS\n",n);return 0;
}
