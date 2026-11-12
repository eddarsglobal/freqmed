/* SPDX-License-Identifier: Apache-2.0 */
#include "generator.h"
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
  if (argc!=2) {fputs("USAGE: freqmed-gen status|probe|selftest\n",stderr);return 2;}
  if (strcmp(argv[1],"status")==0) return status();
  if (strcmp(argv[1],"probe")==0) return probe();
  if (strcmp(argv[1],"selftest")==0) return selftest();
  fputs("UNKNOWN_COMMAND_NO_OUTPUT\n",stderr);
  return 2;
}
