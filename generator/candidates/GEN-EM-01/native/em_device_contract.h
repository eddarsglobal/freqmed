/* SPDX-License-Identifier: Apache-2.0 */
#ifndef FREQMED_EM_DEVICE_CONTRACT_H
#define FREQMED_EM_DEVICE_CONTRACT_H
#include <stddef.h>
#include <stdint.h>

/* These describe commands accepted by a SPECIFIC future physical device.
 * They do not describe a field intensity or assert any physical emission. */
typedef enum {
  FM_EM_TRANSPORT_INVALID = 0,
  FM_EM_TRANSPORT_SERIAL = 1,
  FM_EM_TRANSPORT_USBTMC = 2
} FMEmTransport;
typedef enum {
  FM_EM_DRIVE_INVALID = 0,
  FM_EM_DRIVE_V_RMS = 1, /* conducted generator RMS voltage */
  FM_EM_DRIVE_A_RMS = 2, /* conducted output RMS current */
  FM_EM_DRIVE_DBM = 3    /* conducted RF reference-plane power */
} FMEmDriveUnit;

typedef struct {
  char device_identity_sha256[65]; /* nonzero 64 hex chars, public fingerprint */
  FMEmTransport transport;
  FMEmDriveUnit drive_unit;
  double device_min_hz;
  double device_max_hz;
  double device_min_drive;
  double device_max_drive;
  uint32_t device_max_duration_ms;
} FMEmDeviceContract;

typedef struct {
  double frequency_hz;
  double drive_value; /* exact declared unit, never normalized 0..1 */
  uint32_t duration_ms;
  FMEmDriveUnit drive_unit;
} FMEmSetpoint;

typedef enum {
  FM_EM_BAD_ARGUMENT = -1,
  FM_EM_INVALID_CONTRACT = -2,
  FM_EM_SETPOINT_REJECTED = -3,
  FM_EM_STRUCTURAL_ONLY_NO_AUTHORIZATION = 1
} FMEmAdmission;

/* Structural checks ONLY. A successfully shaped profile may be fabricated,
 * so these checks NEVER certify that its device exists or is safe. */
FMEmAdmission fm_em_check_contract_shape(const FMEmDeviceContract *profile,
                                        char *reason, size_t reason_size);
FMEmAdmission fm_em_check_setpoint(const FMEmDeviceContract *profile,
                                  const FMEmSetpoint *request,
                                  char *reason, size_t reason_size);
/* Physical transport and emission have NO implementation in GEN-R6.
 * Even a structurally valid contract/request cannot enable output. */
int fm_em_try_physical_emission(const FMEmDeviceContract *profile,
                               const FMEmSetpoint *request);
#endif
