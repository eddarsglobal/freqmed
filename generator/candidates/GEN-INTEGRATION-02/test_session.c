/* SPDX-License-Identifier: Apache-2.0 */
#include "session.h"
#include <stdio.h>
#include <string.h>
#define C(x) do { if (!(x)) {fprintf(stderr,"FAIL %d: %s\n",__LINE__,#x); return 1;} ++n; } while(0)
int main(void) {
    unsigned n=0; FMSessionEngine e; fm_sessions_init(&e);
    uint64_t a=0,b=0,t=0;
    FMCommand ac={FM_ACOUSTIC,1.0,0.5,10};
    FMIntegrationRequest ar={FM_ACOUSTIC,&ac,NULL,NULL};
    /* Pure structural test vector; no instrument or physical data. */
    FMEmSetpoint ep={1.0,0.0,20,FM_EM_DRIVE_V_RMS};
    FMEmDeviceContract p={0};
    memset(p.device_identity_sha256,'a',64);
    p.transport=FM_EM_TRANSPORT_SERIAL; p.drive_unit=FM_EM_DRIVE_V_RMS;
    p.device_min_hz=0.5; p.device_max_hz=2.0;
    p.device_min_drive=0.0; p.device_max_drive=1.0; p.device_max_duration_ms=20;
    FMIntegrationRequest er={FM_ELECTROMAGNETIC,NULL,&p,&ep};
    C(e.acoustic.state==FM_S_EMPTY && e.em.state==FM_S_EMPTY);
    C(fm_session_prepare(NULL,&ar,100,&t)==FM_S_BAD_ARGUMENT);
    C(fm_session_prepare(&e,NULL,100,&t)==FM_S_BAD_ARGUMENT);
    C(fm_session_prepare(&e,&ar,100,NULL)==FM_S_BAD_ARGUMENT);
    C(fm_session_prepare(&e,&ar,100,&a)==FM_S_OK && a==1);
    C(e.acoustic.deadline_ms==110 && e.acoustic.state==FM_S_PREPARED);
    C(fm_session_prepare(&e,&ar,101,&t)==FM_S_BUSY && t==0);
    er.em_profile=NULL;
    C(fm_session_prepare(&e,&er,100,&b)==FM_S_INVALID_REQUEST);
    C(e.em.state==FM_S_EMPTY);
    er.em_profile=&p;
    C(fm_session_prepare(&e,&er,100,&b)==FM_S_OK && b==1);
    C(e.em.deadline_ms==120 && e.em.state==FM_S_PREPARED);
    C(fm_session_tick(&e,FM_ACOUSTIC,a+1,109)==FM_S_STALE);
    C(fm_session_tick(&e,FM_ACOUSTIC,a,109)==FM_S_OK);
    C(e.acoustic.state==FM_S_PREPARED);
    C(fm_session_close(&e,FM_ACOUSTIC,a)==FM_S_BUSY);
    C(fm_session_tick(&e,FM_ACOUSTIC,a,110)==FM_S_OK);
    C(e.acoustic.state==FM_S_EXPIRED && e.em.state==FM_S_PREPARED);
    C(fm_session_tick(&e,FM_ACOUSTIC,a,111)==FM_S_NOT_LIVE);
    C(fm_session_close(&e,FM_ACOUSTIC,a)==FM_S_OK);
    C(fm_session_cancel(&e,FM_ACOUSTIC,a)==FM_S_STALE);
    C(fm_session_prepare(&e,&ar,109,&t)==FM_S_CLOCK_FAULT);
    C(fm_session_prepare(&e,&ar,110,&t)==FM_S_OK && t==2);
    C(fm_session_cancel(&e,FM_ACOUSTIC,a)==FM_S_STALE);
    C(fm_session_tick(&e,FM_ACOUSTIC,t,109)==FM_S_CLOCK_FAULT);
    C(e.acoustic.state==FM_S_FAULT && e.em.state==FM_S_PREPARED);
    C(fm_session_cancel(&e,FM_ELECTROMAGNETIC,b)==FM_S_OK);
    C(e.em.state==FM_S_CANCELLED);
    C(fm_session_cancel(&e,FM_ELECTROMAGNETIC,b)==FM_S_NOT_LIVE);
    C(fm_session_close(&e,FM_ELECTROMAGNETIC,b)==FM_S_OK);
    C(fm_session_close(&e,FM_ACOUSTIC,t)==FM_S_OK);
    C(fm_session_prepare(&e,&ar,UINT64_MAX-5,&t)==FM_S_OVERFLOW);
    C(e.acoustic.state==FM_S_EMPTY);
    C(fm_session_tick(&e,(FMChannel)99,1,0)==FM_S_BAD_ARGUMENT);
    e.acoustic.generation=UINT64_MAX;
    C(fm_session_prepare(&e,&ar,120,&t)==FM_S_OVERFLOW);
    C(fm_session_prepare(&e,&er,120,&b)==FM_S_OK && b==2);
    C(fm_session_tick(&e,FM_ELECTROMAGNETIC,b,140)==FM_S_OK);
    C(e.em.state==FM_S_EXPIRED);
    C(fm_session_close(&e,FM_ELECTROMAGNETIC,b)==FM_S_OK);
    printf("GEN_INTEGRATION_02_ASSERTIONS=%u PASS\n",n);
    return 0;
}
