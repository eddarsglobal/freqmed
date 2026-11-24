/* SPDX-License-Identifier: Apache-2.0 */
#include "monitor.h"
#include <stdio.h>
#define C(x) do{if(!(x)){fprintf(stderr,"FAIL %d: %s\n",__LINE__,#x);return 1;}++n;}while(0)
int main(void) {
    unsigned n=0;FMMonitor m;fm_monitor_init(&m);FMBinding b;fm_binding_init(&b);
    FMSnapshot s={0};s.usable=1;s.count=1;
    s.endpoints[0]=(FMEndpoint){"SOFTWARE_TEST",2,44100,FM_ROUTE_BUILT_IN,1};
    FMCommand cmd={FM_ACOUSTIC,1.0,0.5,10};
    FMIntegrationRequest r={FM_ACOUSTIC,&cmd,NULL,NULL};
    uint64_t t=0,old=0;
    C(fm_monitor_poll(NULL,&b,&s,0,0)==FM_M_ERROR);
    C(fm_monitor_poll(&m,NULL,&s,0,0)==FM_M_ERROR);
    C(fm_monitor_poll(&m,&b,&s,0,0)==FM_M_IDLE);
    C(fm_binding_prepare(&b,&s,&r,100,&t)==FM_B_OK);
    C(fm_monitor_poll(&m,&b,&s,t,101)==FM_M_STABLE);
    fm_monitor_mark(&m);fm_monitor_mark(&m);
    C(fm_monitor_poll(&m,&b,&s,t+1,102)==FM_M_STALE);
    C(fm_monitor_poll(&m,&b,&s,0,102)==FM_M_STALE);
    C(atomic_load(&m.pending)==1);
    C(fm_monitor_poll(&m,&b,&s,t,102)==FM_M_INVALIDATED);
    C(b.sessions.acoustic.state==FM_S_CANCELLED);
    C(b.sessions.em.state==FM_S_EMPTY);
    C(fm_monitor_poll(&m,&b,&s,t,103)==FM_M_ERROR);
    C(fm_binding_close(&b,t)==FM_B_OK);
    old=t;
    C(fm_binding_prepare(&b,&s,&r,104,&t)==FM_B_OK);
    C(fm_monitor_poll(&m,&b,&s,old,105)==FM_M_STALE);
    C(fm_monitor_poll(&m,&b,&s,t,105)==FM_M_STABLE);
    FMSnapshot changed=s;changed.endpoints[0].rate=48000;
    C(fm_monitor_poll(&m,&b,&changed,t,106)==FM_M_INVALIDATED);
    C(fm_binding_close(&b,t)==FM_B_OK);
    C(fm_binding_prepare(&b,&s,&r,107,&t)==FM_B_OK);
    C(fm_monitor_poll(&m,&b,NULL,t,108)==FM_M_INVALIDATED);
    C(fm_binding_close(&b,t)==FM_B_OK);
    C(fm_binding_prepare(&b,&s,&r,109,&t)==FM_B_OK);
    C(fm_monitor_poll(&m,&b,&s,t,119)==FM_M_EXPIRED);
    C(fm_binding_close(&b,t)==FM_B_OK);
    C(fm_binding_prepare(&b,&s,&r,120,&t)==FM_B_OK);
    C(fm_monitor_poll(&m,&b,&s,t,119)==FM_M_ERROR);
    C(b.sessions.acoustic.state==FM_S_FAULT);
    C(fm_binding_close(&b,t)==FM_B_OK);
    fm_monitor_mark(&m);
    C(fm_monitor_poll(&m,&b,&s,0,121)==FM_M_IDLE);
    C(fm_binding_prepare(&b,&s,&r,121,&t)==FM_B_OK);
    C(fm_monitor_poll(&m,&b,&s,t,122)==FM_M_INVALIDATED);
    C(fm_binding_close(&b,t)==FM_B_OK);
    printf("GEN_PLATFORM_04_ASSERTIONS=%u PASS\n",n);return 0;
}
