/* SPDX-License-Identifier: Apache-2.0 */
/* USB descriptor spec classification ONLY. No instrument, no mock device. */
#include "em_hardware_discovery.h"
#include <stdio.h>
int main(void) {
  unsigned n=0;
#define VERIFY(x) do{if(!(x)){fprintf(stderr,"R7_USB_DESCRIPTOR_ASSERTION_FAILED_LINE=%d\n",__LINE__);return 1;}++n;}while(0)
  VERIFY(fm_em_descriptor_is_usbtmc(0xFE,0x03,0x00)==1);
  VERIFY(fm_em_descriptor_is_usbtmc(0xFE,0x03,0x01)==1);
  VERIFY(fm_em_descriptor_is_usbtmc(0xFE,0x03,0x02)==0);
  VERIFY(fm_em_descriptor_is_usbtmc(0xFF,0x03,0x00)==0);
  VERIFY(fm_em_descriptor_is_usbtmc(0xFE,0x04,0x00)==0);
  VERIFY(fm_em_descriptor_is_usbtmc(0x00,0x03,0x01)==0);
  VERIFY(fm_em_descriptor_is_usbtmc(0x00,0x00,0x00)==0);
  VERIFY(fm_em_descriptor_is_usbtmc(0x100,0x03,0x00)==0);
  VERIFY(fm_em_descriptor_is_usbtmc(0xFE,0x103,0x00)==0);
  VERIFY(fm_em_descriptor_is_usbtmc(0xFE,0x03,0x101)==0);
  VERIFY(fm_em_descriptor_is_usbtmc(0xFE,0x03,0xFFFFFFFFU)==0);
  printf("R7_USB_DESCRIPTOR_SPEC_ASSERTIONS=%u_PASS; PHYSICAL_EMISSION=NONE\n",n);
  return 0;
}
