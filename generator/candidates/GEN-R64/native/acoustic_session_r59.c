/* SPDX-License-Identifier: Apache-2.0 */
/* R59: real-CoreAudio route-to-command lifecycle, never an audio emitter.
 * This compilation unit has NO AudioQueue*, waveform synthesis or callback.
 * R58 original emitter remains an isolated, one-diagnostic-export binary. */
#include "acoustic_session_r59.h"
#include "acoustic_backend_route_r57.h"
#include "audio_devices.h"
#include <math.h>
#include <stddef.h>
#include <string.h>

static int valid_name(const char *name) {
  if (!name || !name[0]) return 0;
  for (size_t i=0;i<FM_R59_DEVICE_NAME_CAP;i++) {
    if (!name[i]) return 1;
  }
  return 0;
}
static void scrub_binding(FMR59Session *s) {
  if (!s) return;
  s->device_id=0U;
  s->channels=0U;
  s->sample_rate_hz=0.0;
  memset(&s->command,0,sizeof(s->command));
  s->digital_frame_budget=0U;
  memset(s->name,0,sizeof(s->name));
}
int fm_r59_session_bind(FMR59Session *session, const FMCommand *command,
   uint32_t device_id,const char *name,uint32_t channels,double rate_hz) {
  if (!session) return -1;
  scrub_binding(session);
  session->phase=FM_R59_PHASE_INVALIDATED;
  session->reason=FM_R59_REASON_INVALID_ARGUMENT;
  if (!command || command->channel!=FM_ACOUSTIC ||
      !fm_validate_command(command,NULL,0) ||
      !device_id || !valid_name(name) || channels==0U || channels>256U ||
      !isfinite(rate_hz) || rate_hz<=0.0) return 0;
  FMR57BackendRouteCheck checked;
  memset(&checked,0,sizeof(checked));
  if (fm_r57_backend_route_check(command,device_id,name,channels,rate_hz,&checked)!=0) {
    session->reason=FM_R59_REASON_OS_CHANGED_OR_UNAVAILABLE;
    return 0;
  }
  if (checked.result_code!=1U || !checked.default_route_matches ||
      !isfinite(checked.nominal_rate_hz) || checked.nominal_rate_hz!=rate_hz ||
      checked.digital_frame_budget==0U) {
    session->reason=FM_R59_REASON_ROUTE_OR_COMMAND_MISMATCH;
    return 0;
  }
  session->device_id=device_id;
  session->channels=channels;
  session->sample_rate_hz=rate_hz;
  session->command=*command;
  session->digital_frame_budget=checked.digital_frame_budget;
  memcpy(session->name,name,strlen(name)+1U);
  session->phase=FM_R59_PHASE_ROUTE_VERIFIED;
  session->reason=FM_R59_REASON_NONE;
  return 1;
}
int fm_r59_session_poll(FMR59Session *session) {
  if (!session) return -1;
  if (session->phase!=FM_R59_PHASE_ROUTE_VERIFIED ||
      !session->device_id || !valid_name(session->name)) return 0;
  FMR57BackendRouteCheck check;
  memset(&check,0,sizeof(check));
  if (fm_r57_backend_route_check(&session->command,session->device_id,
        session->name,session->channels,session->sample_rate_hz,&check)!=0 ||
      check.result_code!=1U || !check.default_route_matches ||
      check.nominal_rate_hz!=session->sample_rate_hz ||
      check.digital_frame_budget!=session->digital_frame_budget) {
    scrub_binding(session);
    session->phase=FM_R59_PHASE_INVALIDATED;
    session->reason=FM_R59_REASON_OS_CHANGED_OR_UNAVAILABLE;
    return 0;
  }
  return 1;
}
void fm_r59_session_invalidate(FMR59Session *session) {
  if (!session) return;
  scrub_binding(session);
  session->phase=FM_R59_PHASE_INVALIDATED;
  session->reason=FM_R59_REASON_ROUTE_RESET;
}
void fm_r59_session_stop(FMR59Session *session) {
  if (!session) return;
  scrub_binding(session);
  session->phase=FM_R59_PHASE_STOPPED;
  session->reason=FM_R59_REASON_OPERATOR_STOP;
}
