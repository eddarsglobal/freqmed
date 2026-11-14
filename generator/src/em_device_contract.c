/* SPDX-License-Identifier: Apache-2.0 */
#include "em_device_contract.h"
#include <math.h>
#include <stdio.h>
#include <string.h>

static void fm_reason(char *out, size_t n, const char *why) {
  if (out && n) (void)snprintf(out, n, "%s", why);
}
static int hex_identity_pinned(const char h[65]) {
  int any_nonzero = 0;
  if (!h) return 0;
  for (size_t i=0; i<64; ++i) {
    unsigned char c=(unsigned char)h[i];
    if (c == 0) return 0;
    if (!((c >= '0' && c <= '9') ||
          (c >= 'a' && c <= 'f') || (c >= 'A' && c <= 'F'))) return 0;
    if (c != '0') any_nonzero = 1;
  }
  return any_nonzero && h[64] == 0;
}
static int known_transport(FMEmTransport transport) {
  return transport == FM_EM_TRANSPORT_SERIAL ||
         transport == FM_EM_TRANSPORT_USBTMC;
}
static int known_unit(FMEmDriveUnit unit) {
  return unit == FM_EM_DRIVE_V_RMS || unit == FM_EM_DRIVE_A_RMS ||
         unit == FM_EM_DRIVE_DBM;
}
static int shape_ok(const FMEmDeviceContract *p) {
  if (!p || !hex_identity_pinned(p->device_identity_sha256) ||
      !known_transport(p->transport) || !known_unit(p->drive_unit)) return 0;
  if (!isfinite(p->device_min_hz) || !isfinite(p->device_max_hz) ||
      p->device_min_hz <= 0 || p->device_max_hz <= p->device_min_hz) return 0;
  if (!isfinite(p->device_min_drive) || !isfinite(p->device_max_drive) ||
      p->device_max_drive <= p->device_min_drive ||
      p->device_max_duration_ms == 0) return 0;
  /* No universal 'safe' frequency, amplitude, or duration is hardcoded. */
  return 1;
}
FMEmAdmission fm_em_check_contract_shape(const FMEmDeviceContract *profile,
                                        char *reason, size_t size) {
  if (!profile) {
    fm_reason(reason,size,"R6_MISSING_DEVICE_CONTRACT");
    return FM_EM_BAD_ARGUMENT;
  }
  if (!shape_ok(profile)) {
    fm_reason(reason,size,"R6_INVALID_DEVICE_CONTRACT");
    return FM_EM_INVALID_CONTRACT;
  }
  fm_reason(reason,size,"R6_SHAPE_ONLY_DEVICE_NOT_ATTESTED");
  return FM_EM_STRUCTURAL_ONLY_NO_AUTHORIZATION;
}
FMEmAdmission fm_em_check_setpoint(const FMEmDeviceContract *profile,
                                  const FMEmSetpoint *request,
                                  char *reason, size_t size) {
  if (!request || !profile) {
    fm_reason(reason,size,"R6_MISSING_CONTRACT_OR_SETPOINT");
    return FM_EM_BAD_ARGUMENT;
  }
  if (!shape_ok(profile)) {
    fm_reason(reason,size,"R6_INVALID_DEVICE_CONTRACT");
    return FM_EM_INVALID_CONTRACT;
  }
  if (request->drive_unit != profile->drive_unit ||
      !isfinite(request->frequency_hz) ||
      request->frequency_hz < profile->device_min_hz ||
      request->frequency_hz > profile->device_max_hz ||
      !isfinite(request->drive_value) ||
      request->drive_value < profile->device_min_drive ||
      request->drive_value > profile->device_max_drive ||
      request->duration_ms == 0 ||
      request->duration_ms > profile->device_max_duration_ms) {
    fm_reason(reason,size,"R6_SETPOINT_OUTSIDE_DECLARED_PROFILE");
    return FM_EM_SETPOINT_REJECTED;
  }
  fm_reason(reason,size,"R6_SETPOINT_SHAPE_ONLY_NO_EMISSION");
  return FM_EM_STRUCTURAL_ONLY_NO_AUTHORIZATION;
}
int fm_em_try_physical_emission(const FMEmDeviceContract *profile,
                               const FMEmSetpoint *request) {
  /* A boolean approval flag or user-supplied hash MUST NOT unlock hardware.
   * No output driver/transport exists in R6; no writes, ports, sockets or RF.
   * An instrument-specific driver will be reviewed and built in a future
   * separately authorized revision, never by changing these runtime inputs. */
  (void)profile;
  (void)request;
  return -1;
}
