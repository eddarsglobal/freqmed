/* SPDX-License-Identifier: Apache-2.0 */
#ifndef FREQMED_GENERATOR_H
#define FREQMED_GENERATOR_H
#include <stddef.h>

typedef enum { FM_ACOUSTIC=1, FM_ELECTROMAGNETIC=2 } FMChannel;
typedef enum { FM_OFF=0, FM_BLOCKED=1, FM_PREPARED=2, FM_ARMED=3, FM_ACTIVE=4, FM_FAULT=5 } FMState;
typedef struct {
  FMChannel channel;
  double frequency_hz;
  double normalized_level; /* digital command; NOT sound pressure / E-field */
  unsigned duration_ms;
} FMCommand;
typedef struct {
  FMState state;
  int hardware_profile_certified;
  int safety_review_certified;
  int bench_authorized;
  int physical_output_enabled;
} FMGuardian;

int fm_validate_command(const FMCommand *command, char *why, size_t capacity);
int fm_guardian_transition(FMGuardian *guardian, const FMCommand *command, char *why, size_t capacity);
void fm_stop(FMGuardian *guardian);
int fm_acoustic_native_backend_available(void);
int fm_acoustic_physical_output(const FMCommand *command);
int fm_em_backend_available(void);
int fm_em_physical_output(const FMCommand *command);
#endif
