/* SPDX-License-Identifier: Apache-2.0 */
#include "recovery.h"
#include <stdio.h>
#include <string.h>
#define C(x) do{if(!(x)){fprintf(stderr,"FAIL %d: %s\n",__LINE__,#x);return 1;}++n;}while(0)
int main(void) {
    unsigned n=0;FMRecovery r;fm_recovery_init(&r);
    FMSnapshot a={0};a.usable=1;a.count=1;
    a.endpoints[0]=(FMEndpoint){"TEST_A",2,44100,FM_ROUTE_BUILT_IN,1};
    FMSnapshot b=a;
    FMCommand cmd={FM_ACOUSTIC,1.0,0.5,10};
    FMIntegrationRequest req={FM_ACOUSTIC,&cmd,NULL,NULL};
    uint64_t t=0,old=0;
    C(r.state==FM_R_DISCOVERY_REQUIRED && r.binding.token==0);
    C(fm_recovery_prepare(&r,&a,&req,100,&t)==FM_R_BAD_STATE);
    C(fm_recovery_finish(&r,&a,&b)==FM_R_BAD_STATE);
    C(fm_recovery_begin(NULL)==FM_R_BAD_STATE);
    C(fm_recovery_begin(&r)==FM_R_OK);
    C(fm_recovery_begin(&r)==FM_R_BAD_STATE);
    fm_recovery_notify(&r);
    C(fm_recovery_finish(&r,&a,&b)==FM_R_RETRY);
    C(r.state==FM_R_DISCOVERY_REQUIRED);
    C(fm_recovery_begin(&r)==FM_R_OK);
    C(fm_recovery_finish(&r,&a,NULL)==FM_R_NO_PROFILE);
    C(fm_recovery_begin(&r)==FM_R_OK);
    b.endpoints[0].rate=48000;
    C(fm_recovery_finish(&r,&a,&b)==FM_R_RETRY);
    C(fm_recovery_begin(&r)==FM_R_OK);
    C(fm_recovery_finish(&r,&a,&a)==FM_R_OK);
    C(r.state==FM_R_READY && r.binding.token==0);
    C(fm_recovery_prepare(&r,&b,&req,100,&t)==FM_R_RETRY);
    C(fm_recovery_begin(&r)==FM_R_OK);
    C(fm_recovery_finish(&r,&a,&a)==FM_R_OK);
    fm_recovery_notify(&r);
    C(fm_recovery_prepare(&r,&a,&req,100,&t)==FM_R_RETRY);
    C(fm_recovery_begin(&r)==FM_R_OK);
    C(fm_recovery_finish(&r,&a,&a)==FM_R_OK);
    C(fm_recovery_prepare(&r,&a,&req,100,&t)==FM_R_OK && t==1);
    C(r.state==FM_R_PREPARED);
    C(fm_recovery_begin(&r)==FM_R_BAD_STATE);
    C(fm_recovery_poll(&r,&a,t,101)==FM_R_OK);
    fm_recovery_notify(&r);
    C(fm_recovery_poll(&r,&a,t+1,102)==FM_R_STALE);
    C(atomic_load(&r.monitor.pending)==1);
    C(fm_recovery_poll(&r,&a,t,102)==FM_R_INVALIDATED);
    C(r.state==FM_R_DISCOVERY_REQUIRED && r.binding.token==0);
    C(r.binding.sessions.acoustic.state==FM_S_EMPTY && !r.profile.uid[0]);
    old=t;
    C(fm_recovery_poll(&r,&a,old,103)==FM_R_STALE);
    C(fm_recovery_begin(&r)==FM_R_OK);
    C(fm_recovery_finish(&r,&b,&b)==FM_R_OK);
    C(r.binding.token==0 && r.state==FM_R_READY);
    C(fm_recovery_prepare(&r,&b,&req,103,&t)==FM_R_OK && t==2);
    C(fm_recovery_close(&r,old)==FM_R_STALE);
    C(fm_recovery_poll(&r,&b,t,113)==FM_R_EXPIRED);
    C(r.state==FM_R_DISCOVERY_REQUIRED && r.binding.token==0);
    C(fm_recovery_begin(&r)==FM_R_OK);
    C(fm_recovery_finish(&r,&b,&b)==FM_R_OK);
    C(fm_recovery_prepare(&r,&b,&req,114,&t)==FM_R_OK);
    C(fm_recovery_close(&r,t)==FM_R_OK);
    C(r.state==FM_R_DISCOVERY_REQUIRED);
    C(fm_recovery_begin(&r)==FM_R_OK);
    C(fm_recovery_finish(&r,&b,&b)==FM_R_OK);
    C(fm_recovery_prepare(&r,&b,&req,115,&t)==FM_R_OK);
    C(fm_recovery_poll(&r,&b,t,114)==FM_R_ERROR);
    C(r.state==FM_R_FAULT && r.binding.token==0);
    C(fm_recovery_begin(&r)==FM_R_BAD_STATE);
    C(r.binding.sessions.em.state==FM_S_EMPTY);
    printf("GEN_PLATFORM_05_ASSERTIONS=%u PASS\n",n);return 0;
}
