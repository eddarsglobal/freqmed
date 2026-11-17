/* SPDX-License-Identifier: Apache-2.0 */
#include "generator.h"
#if defined(FREQMED_GEN_R7_DISCOVERY)
#include "em_hardware_discovery.h"
#endif
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int status(void) {
  puts("{\"schema\":\"FREQMED_GENERATION_R2_STATUS\",\"mission\":\"PHYSICAL_ACOUSTIC_AND_EM_GENERATORS\",\"acoustic_output\":\"NOT_LINKED_HARD_DENIED\",\"electromagnetic_output\":\"BLOCKED_NO_QUALIFIED_EM_DEVICE\",\"physical_emission\":\"NONE\",\"scientific_simulation\":\"NONE\",\"production\":\"NOT_AUTHORIZED\"}");
  return 0;
}
static int probe(void) {
  FMOutputCapabilities caps={0};
  if (fm_acoustic_readonly_probe(&caps)==0) {
    printf("{\"schema\":\"FREQMED_GEN_R2_OS_AUDIO_PROBE_V1\",\"output_metadata\":\"READ_ONLY_OBSERVED\",\"channels\":%u,\"nominal_sample_rate_hz\":%.4f,\"hardware_identity\":\"NOT_CERTIFIED\",\"transducer\":\"NOT_VERIFIED\",\"output\":\"NOT_LINKED_HARD_DENIED\"}\n",caps.output_channels,caps.nominal_sample_rate_hz);
  } else {
    puts("{\"schema\":\"FREQMED_GEN_R2_OS_AUDIO_PROBE_V1\",\"output_metadata\":\"UNAVAILABLE_OR_INCOMPLETE\",\"hardware_identity\":\"NOT_CERTIFIED\",\"output\":\"NOT_LINKED_HARD_DENIED\"}");
  }
  return 0;
}
#if defined(FREQMED_GEN_R7_DISCOVERY)
/* Only IOKit enumeration. USB/serial presence is not proof of EM generation. */
static int em_discover(void) {
  FMEmReadonlyInventory inv={0};
  if (fm_em_discover_readonly(&inv)!=0) {
    puts("{\"schema\":\"FREQMED_GEN_R7_EM_DISCOVERY_V1\",\"os_registry\":\"UNAVAILABLE_OR_INCOMPLETE\",\"usbtmc_interfaces\":null,\"serial_callout_nodes\":null,\"em_generator_qualified\":false,\"physical_emission\":\"NONE\"}");
    return 0;
  }
  printf("{\"schema\":\"FREQMED_GEN_R7_EM_DISCOVERY_V1\",\"os_registry\":\"IOKIT_READ_ONLY\",\"usb_devices\":%u,\"usb_interfaces\":%u,\"serial_callout_nodes\":%u,\"usbtmc_interfaces\":%u,\"usbtmc_candidates_truncated\":%s,\"usbtmc_candidates\":[",
         inv.usb_devices_reported,inv.usb_interfaces_reported,
         inv.serial_callout_nodes_reported,inv.usbtmc_interfaces_reported,
         inv.listing_truncated ? "true":"false");
  for (unsigned i=0;i<inv.candidates_stored;i++) {
    const FMEmUsbInterfaceCandidate *c=&inv.candidates[i];
    if (i) putchar(',');
    if (c->has_vendor_product)
      printf("{\"vendor_id\":%u,\"product_id\":%u,\"protocol\":%u}",
            c->vendor_id,c->product_id,c->interface_protocol);
    else
      printf("{\"vendor_id\":null,\"product_id\":null,\"protocol\":%u}",
            c->interface_protocol);
  }
  puts("],\"em_generator_qualified\":false,\"physical_emission\":\"NONE\",\"hardware_ports_opened\":0}");
  return 0;
}
#endif
static int selftest(void) {
  char why[128];
  FMCommand c={FM_ACOUSTIC,440.0,0.001,100};
  FMGuardian g={FM_OFF,1,1,1,1};
  if (!fm_validate_command(&c,why,sizeof(why))) return 10;
  if (fm_guardian_transition(&g,&c,why,sizeof(why)) || g.state!=FM_BLOCKED) return 11;
  if (strcmp(why,"R1_OUTPUT_HARD_LOCK_CERTIFICATION_REQUIRED")) return 12;
  if (fm_acoustic_native_backend_available()!=0 || fm_acoustic_physical_output(&c)==0) return 13;
  c.channel=FM_ELECTROMAGNETIC;
  if (fm_em_backend_available()!=0 || fm_em_physical_output(&c)==0) return 14;
  if (fm_guardian_transition(&g,&c,why,sizeof(why)) || g.state!=FM_BLOCKED) return 15;
  fm_stop(&g);
  if (g.state!=FM_OFF) return 16;
  puts("R2_SELFTEST=PASS; ACOUSTIC_EMISSION=NONE; EM_EMISSION=NONE; CORE_AUDIO_OUTPUT_SYMBOLS=NOT_LINKED; GUARDIAN=FAIL_CLOSED");
  return 0;
}
int main(int argc,char **argv) {
  if (argc!=2) {fputs("USAGE: freqmed-gen status|probe|em-discover|selftest\n",stderr);return 2;}
  if (strcmp(argv[1],"status")==0) return status();
  if (strcmp(argv[1],"probe")==0) return probe();
#if defined(FREQMED_GEN_R7_DISCOVERY)
  if (strcmp(argv[1],"em-discover")==0) return em_discover();
#endif
  if (strcmp(argv[1],"selftest")==0) return selftest();
  fputs("UNKNOWN_COMMAND_NO_OUTPUT\n",stderr);
  return 2;
}
