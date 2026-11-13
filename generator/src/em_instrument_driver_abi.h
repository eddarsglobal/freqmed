/* SPDX-License-Identifier: Apache-2.0 */
#ifndef FREQMED_EM_INSTRUMENT_DRIVER_ABI_H
#define FREQMED_EM_INSTRUMENT_DRIVER_ABI_H
#include "em_device_contract.h"
/* A future device-specific driver must implement the ABI below, but GEN-R6
 * instantiates NONE and links NONE into the runnable executable.
 * Implementations require a selected REAL instrument, written protocol,
 * a verified hardwired independent cutoff, and Bureau authorization.
 * No generic SCPI commands are invented or sent.
 */
typedef struct FMEmDriverContext FMEmDriverContext;
typedef struct {
  /* Read-only hardware identity must match an independently verified pin. */
  int (*identify_readonly)(FMEmDriverContext *context,
                           char observed_fingerprint_sha256[65]);
  /* Independent actual OFF state, not merely a cached software checkbox. */
  int (*query_hardware_off_state)(FMEmDriverContext *context);
  /* Hardware cutoff control is device-specific and not implemented in R6. */
  int (*request_hardware_cutoff)(FMEmDriverContext *context);
  /* No set-frequency, set-drive, arm, or emit callbacks exist in R6. */
} FMEmFutureDriverRequirements;
#endif
