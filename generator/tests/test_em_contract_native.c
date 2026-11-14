/* SPDX-License-Identifier: Apache-2.0 */
/* Software-only checks of C input parsing and unconditionally blocked output.
 * Numeric metadata are not physical measurements, not a virtual device,
 * and never used to produce a wave or field. */
#include "em_device_contract.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <string.h>

int main(void) {
  char message[120];
  FMEmDeviceContract p = {0};
  FMEmSetpoint c = {0};
  unsigned passed = 0;
#define TEST(expr) do {if (!(expr)) {fprintf(stderr,"EM_CONTRACT_ASSERT_FAIL_AT_LINE=%d\n",__LINE__);return 1;} ++passed;} while(0)
  TEST(fm_em_check_contract_shape(NULL,message,sizeof(message))==FM_EM_BAD_ARGUMENT);
  TEST(!strcmp(message,"R6_MISSING_DEVICE_CONTRACT"));
  TEST(fm_em_check_contract_shape(&p,message,sizeof(message))==FM_EM_INVALID_CONTRACT);
  TEST(fm_em_try_physical_emission(NULL,NULL)==-1);
  TEST(fm_em_try_physical_emission(&p,&c)==-1);
  /* These are structured metadata parsing cases ONLY, not an instrument. */
  memset(p.device_identity_sha256,'a',64);p.device_identity_sha256[64]='\0';
  p.transport=FM_EM_TRANSPORT_SERIAL; p.drive_unit=FM_EM_DRIVE_V_RMS;
  p.device_min_hz=1.0; p.device_max_hz=2.0;
  p.device_min_drive=0.1; p.device_max_drive=0.2;
  p.device_max_duration_ms=2U;
  TEST(fm_em_check_contract_shape(&p,message,sizeof(message))==FM_EM_STRUCTURAL_ONLY_NO_AUTHORIZATION);
  TEST(!strcmp(message,"R6_SHAPE_ONLY_DEVICE_NOT_ATTESTED"));
  c.frequency_hz=1.5;c.drive_value=0.15;c.duration_ms=1U;
  c.drive_unit=FM_EM_DRIVE_V_RMS;
  TEST(fm_em_check_setpoint(&p,&c,message,sizeof(message))==FM_EM_STRUCTURAL_ONLY_NO_AUTHORIZATION);
  TEST(!strcmp(message,"R6_SETPOINT_SHAPE_ONLY_NO_EMISSION"));
  TEST(fm_em_try_physical_emission(&p,&c)==-1);
  c.frequency_hz=NAN;
  TEST(fm_em_check_setpoint(&p,&c,message,sizeof(message))==FM_EM_SETPOINT_REJECTED);
  c.frequency_hz=INFINITY;
  TEST(fm_em_check_setpoint(&p,&c,message,sizeof(message))==FM_EM_SETPOINT_REJECTED);
  c.frequency_hz=1.5;c.drive_value=NAN;
  TEST(fm_em_check_setpoint(&p,&c,message,sizeof(message))==FM_EM_SETPOINT_REJECTED);
  c.drive_value=0.15;c.drive_unit=FM_EM_DRIVE_A_RMS;
  TEST(fm_em_check_setpoint(&p,&c,message,sizeof(message))==FM_EM_SETPOINT_REJECTED);
  c.drive_unit=FM_EM_DRIVE_V_RMS;c.duration_ms=3U;
  TEST(fm_em_check_setpoint(&p,&c,message,sizeof(message))==FM_EM_SETPOINT_REJECTED);
  c.duration_ms=1U;c.frequency_hz=0.9;
  TEST(fm_em_check_setpoint(&p,&c,message,sizeof(message))==FM_EM_SETPOINT_REJECTED);
  c.frequency_hz=1.5;c.drive_value=0.21;
  TEST(fm_em_check_setpoint(&p,&c,message,sizeof(message))==FM_EM_SETPOINT_REJECTED);
  c.drive_value=0.15;p.device_max_hz=INFINITY;
  TEST(fm_em_check_contract_shape(&p,message,sizeof(message))==FM_EM_INVALID_CONTRACT);
  p.device_max_hz=2.0;p.device_identity_sha256[0]='G';
  TEST(fm_em_check_contract_shape(&p,message,sizeof(message))==FM_EM_INVALID_CONTRACT);
  p.device_identity_sha256[0]='a';p.transport=FM_EM_TRANSPORT_INVALID;
  TEST(fm_em_check_contract_shape(&p,message,sizeof(message))==FM_EM_INVALID_CONTRACT);
  p.transport=FM_EM_TRANSPORT_USBTMC;
  TEST(fm_em_check_contract_shape(&p,message,sizeof(message))==FM_EM_STRUCTURAL_ONLY_NO_AUTHORIZATION);
  TEST(fm_em_try_physical_emission(&p,&c)==-1);
  printf("R6_EM_CONTRACT_NATIVE_ASSERTIONS=%u_PASS; HARDWARE_OPEN=NONE; PHYSICAL_EMISSION=NONE\n",passed);
  return 0;
}
