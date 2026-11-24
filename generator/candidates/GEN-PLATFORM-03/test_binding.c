/* SPDX-License-Identifier: Apache-2.0 */
#include "binding.h"
#include <math.h>
#include <stdio.h>
#include <string.h>
#define C(x) do {if(!(x)){fprintf(stderr,"FAIL %d: %s\n",__LINE__,#x);return 1;}++n;}while(0)
int main(void) {
    unsigned n=0,index=99;
    /* Artificial software records only; no physical inventory or simulation. */
    FMSnapshot s={0}; s.usable=1; s.count=2;
    s.endpoints[0]=(FMEndpoint){"TEST_A",2,44100,FM_ROUTE_BUILT_IN,1};
    s.endpoints[1]=(FMEndpoint){"TEST_B",2,48000,FM_ROUTE_VIRTUAL,0};
    FMSnapshot t=s;
    FMBinding b;fm_binding_init(&b);
    FMCommand cmd={FM_ACOUSTIC,1.0,0.5,10};
    FMIntegrationRequest r={FM_ACOUSTIC,&cmd,NULL,NULL};
    uint64_t token=0,old=0,spare=0;
    C(fm_binding_select(NULL,&index)==FM_B_INVALID);
    C(fm_binding_select(&s,NULL)==FM_B_INVALID);
    C(fm_binding_select(&s,&index)==FM_B_OK && index==0);
    t.usable=0;C(fm_binding_select(&t,&index)==FM_B_INVALID);
    t=s;t.count=33;C(fm_binding_select(&t,&index)==FM_B_INVALID);
    t=s;t.endpoints[0].uid[0]=0;C(fm_binding_select(&t,&index)==FM_B_INVALID);
    t=s;memset(t.endpoints[0].uid,'x',sizeof(t.endpoints[0].uid));C(fm_binding_select(&t,&index)==FM_B_INVALID);
    t=s;strcpy(t.endpoints[1].uid,"TEST_A");C(fm_binding_select(&t,&index)==FM_B_INVALID);
    t=s;t.endpoints[0].channels=0;C(fm_binding_select(&t,&index)==FM_B_INVALID);
    t=s;t.endpoints[0].rate=NAN;C(fm_binding_select(&t,&index)==FM_B_INVALID);
    t=s;t.endpoints[1].is_default=1;C(fm_binding_select(&t,&index)==FM_B_INVALID);
    t=s;t.endpoints[0].is_default=0;C(fm_binding_select(&t,&index)==FM_B_NO_CANDIDATE);
    t.endpoints[1].is_default=1;C(fm_binding_select(&t,&index)==FM_B_NO_CANDIDATE);
    t=s;t.endpoints[0].route=FM_ROUTE_UNKNOWN;C(fm_binding_select(&t,&index)==FM_B_NO_CANDIDATE);
    t=s;t.endpoints[0].route=FM_ROUTE_USB;C(fm_binding_select(&t,&index)==FM_B_OK);
    r.channel=FM_ELECTROMAGNETIC;C(fm_binding_prepare(&b,&s,&r,100,&token)==FM_B_INVALID);
    r.channel=FM_ACOUSTIC;cmd.duration_ms=0;C(fm_binding_prepare(&b,&s,&r,100,&token)==FM_B_SESSION_ERROR);
    cmd.duration_ms=10;C(fm_binding_prepare(&b,&s,&r,100,&token)==FM_B_OK && token==1);
    C(fm_binding_prepare(&b,&s,&r,100,&spare)==FM_B_BUSY);
    C(fm_binding_refresh(&b,&s,token+1,101)==FM_B_STALE);
    t=s;t.endpoints[0]=s.endpoints[1];t.endpoints[1]=s.endpoints[0];
    C(fm_binding_refresh(&b,&t,token,101)==FM_B_OK);
    C(b.sessions.acoustic.state==FM_S_PREPARED);
    t=s;t.endpoints[0].rate=48000;
    C(fm_binding_refresh(&b,&t,token,102)==FM_B_CHANGED);
    C(b.sessions.acoustic.state==FM_S_CANCELLED);
    C(b.sessions.em.state==FM_S_EMPTY);
    C(fm_binding_close(&b,token)==FM_B_OK);
    C(b.chosen.uid[0]==0 && b.token==0);
    old=token;C(fm_binding_prepare(&b,&s,&r,103,&token)==FM_B_OK && token==2);
    C(fm_binding_close(&b,old)==FM_B_STALE);
    t=s;strcpy(t.endpoints[0].uid,"TEST_C");
    C(fm_binding_refresh(&b,&t,token,104)==FM_B_CHANGED);
    C(fm_binding_close(&b,token)==FM_B_OK);
    C(fm_binding_prepare(&b,&s,&r,105,&token)==FM_B_OK);
    C(fm_binding_refresh(&b,NULL,token,106)==FM_B_CHANGED);
    C(fm_binding_close(&b,token)==FM_B_OK);
    C(fm_binding_prepare(&b,&s,&r,107,&token)==FM_B_OK);
    C(fm_binding_refresh(&b,&s,token,117)==FM_B_OK);
    C(b.sessions.acoustic.state==FM_S_EXPIRED);
    C(fm_binding_close(&b,token)==FM_B_OK);
    C(fm_binding_prepare(&b,&s,&r,118,&token)==FM_B_OK);
    C(fm_binding_refresh(&b,&s,token,117)==FM_B_SESSION_ERROR);
    C(b.sessions.acoustic.state==FM_S_FAULT);
    C(fm_binding_close(&b,token)==FM_B_OK);
    C(fm_binding_prepare(&b,&s,&r,119,&token)==FM_B_OK);
    t=s;t.endpoints[0].is_default=0;t.endpoints[1].is_default=1;
    C(fm_binding_refresh(&b,&t,token,120)==FM_B_CHANGED);
    C(fm_binding_close(&b,token)==FM_B_OK);
    printf("GEN_PLATFORM_03_ASSERTIONS=%u PASS\n",n);
    return 0;
}
