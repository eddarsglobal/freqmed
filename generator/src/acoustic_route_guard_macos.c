/* SPDX-License-Identifier: Apache-2.0 */
/* Read-only OS metadata. SOURCE-ONLY: never linked to runnable R4. */
#include "acoustic_route_guard.h"
#include "generator.h"
#include <math.h>
#include <string.h>
#if defined(__APPLE__)
#include <CoreAudio/CoreAudio.h>
static int read_default_output(AudioDeviceID *out) {
  if (!out) return -1;
  *out=kAudioObjectUnknown;
  const AudioObjectPropertyAddress key={kAudioHardwarePropertyDefaultOutputDevice,
      kAudioObjectPropertyScopeGlobal,kAudioObjectPropertyElementMain};
  UInt32 n=(UInt32)sizeof(*out);
  if (AudioObjectGetPropertyData(kAudioObjectSystemObject,&key,0,NULL,&n,out)!=noErr ||
      n!=sizeof(*out) || *out==kAudioObjectUnknown) return -1;
  return 0;
}
int fm_route_capture(FMRouteFingerprint *out) {
  if (!out) return -1;
  memset(out,0,sizeof(*out));
  AudioDeviceID before=kAudioObjectUnknown,after=kAudioObjectUnknown;
  if (read_default_output(&before)!=0) return -1;
  FMOutputCapabilities caps={0};
  if (fm_acoustic_readonly_probe(&caps)!=0 || caps.metadata_observed!=1 ||
      caps.output_channels==0 || !isfinite(caps.nominal_sample_rate_hz) ||
      caps.nominal_sample_rate_hz<=0.0) return -1;
  if (read_default_output(&after)!=0 || before!=after) return -1;
  out->os_device_token=(uint32_t)before;
  out->nominal_sample_rate_hz=caps.nominal_sample_rate_hz;
  out->output_channels=caps.output_channels;
  return 0;
}
#else
int fm_route_capture(FMRouteFingerprint *out) {
  if (out) memset(out,0,sizeof(*out));
  return -1;
}
#endif
int fm_route_unchanged(const FMRouteFingerprint *first) {
  if (!first || first->os_device_token==0 || first->output_channels==0 ||
      !isfinite(first->nominal_sample_rate_hz) ||
      first->nominal_sample_rate_hz<=0.0) return 0;
  FMRouteFingerprint now={0};
  if (fm_route_capture(&now)!=0) return 0;
  return now.os_device_token==first->os_device_token &&
      now.nominal_sample_rate_hz==first->nominal_sample_rate_hz &&
      now.output_channels==first->output_channels;
}
