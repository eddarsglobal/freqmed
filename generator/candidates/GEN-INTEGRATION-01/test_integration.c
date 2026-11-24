/* SPDX-License-Identifier: Apache-2.0 */
#include "integration.h"
#include <math.h>
#include <stdio.h>
#include <string.h>
#define CHECK(expr) do { if (!(expr)) { fprintf(stderr,"FAIL line %d: %s\n",__LINE__,#expr); return 1; } ++count; } while (0)
int main(void) {
    unsigned count = 0;
    /* Software-only validation vectors; never device evidence or measurement. */
    FMCommand a = { FM_ACOUSTIC, 1.0, 0.5, 1U };
    FMIntegrationRequest r = { FM_ACOUSTIC, &a, NULL, NULL };
    FMEmSetpoint e = {1.0, 0.0, 1U, FM_EM_DRIVE_V_RMS};
    FMEmDeviceContract p = {0};
    CHECK(fm_integration_validate(NULL)==FM_INT_INVALID);
    CHECK(fm_integration_validate(&r)==FM_INT_ACOUSTIC_STRUCTURE_ONLY);
    a.frequency_hz=NAN;
    CHECK(fm_integration_validate(&r)==FM_INT_INVALID);
    a.frequency_hz=1.0; a.normalized_level=INFINITY;
    CHECK(fm_integration_validate(&r)==FM_INT_INVALID);
    a.normalized_level=0.5; a.duration_ms=0;
    CHECK(fm_integration_validate(&r)==FM_INT_INVALID);
    a.duration_ms=1; a.channel=FM_ELECTROMAGNETIC;
    CHECK(fm_integration_validate(&r)==FM_INT_INVALID);
    a.channel=FM_ACOUSTIC; r.em_setpoint=&e;
    CHECK(fm_integration_validate(&r)==FM_INT_INVALID);
    r.em_setpoint=NULL; r.acoustic=NULL;
    CHECK(fm_integration_validate(&r)==FM_INT_INVALID);
    r.channel=FM_ELECTROMAGNETIC; r.em_setpoint=&e;
    CHECK(fm_integration_validate(&r)==FM_INT_EM_PROFILE_REQUIRED);
    r.em_profile=&p;
    CHECK(fm_integration_validate(&r)==FM_INT_INVALID);
    /* Deliberately artificial structural input, not a qualified instrument. */
    memset(p.device_identity_sha256,'a',64);
    p.transport=FM_EM_TRANSPORT_SERIAL; p.drive_unit=FM_EM_DRIVE_V_RMS;
    p.device_min_hz=0.5; p.device_max_hz=2.0;
    p.device_min_drive=0.0; p.device_max_drive=1.0; p.device_max_duration_ms=1;
    CHECK(fm_integration_validate(&r)==FM_INT_EM_STRUCTURE_ONLY);
    e.drive_unit=FM_EM_DRIVE_DBM;
    CHECK(fm_integration_validate(&r)==FM_INT_INVALID);
    e.drive_unit=FM_EM_DRIVE_V_RMS; e.frequency_hz=NAN;
    CHECK(fm_integration_validate(&r)==FM_INT_INVALID);
    e.frequency_hz=1.0; e.duration_ms=2;
    CHECK(fm_integration_validate(&r)==FM_INT_INVALID);
    e.duration_ms=1; r.acoustic=&a;
    CHECK(fm_integration_validate(&r)==FM_INT_INVALID);
    r.acoustic=NULL; r.channel=(FMChannel)99;
    CHECK(fm_integration_validate(&r)==FM_INT_INVALID);
    FMGuardian g = {FM_OFF,1,1,1,1};
    CHECK(fm_guardian_transition(&g,&a,NULL,0)==0 && g.state==FM_BLOCKED);
    fm_stop(&g);
    CHECK(g.state==FM_OFF);
    CHECK(fm_acoustic_native_backend_available()==0);
    CHECK(fm_em_backend_available()==0);
    CHECK(fm_acoustic_physical_output(&a)==-1);
    CHECK(fm_em_physical_output(&a)==-1);
    CHECK(fm_em_try_physical_emission(&p,&e)==-1);
    printf("GEN_INTEGRATION_01_ASSERTIONS=%u PASS\n",count);
    return 0;
}
