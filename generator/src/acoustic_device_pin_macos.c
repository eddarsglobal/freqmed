/* SPDX-License-Identifier: Apache-2.0 */
/* GEN-R5 source-only CoreAudio hardware pin candidate.
 * The queue belongs to the prospective acoustic emitter, NOT to the R5 CLI.
 * Binding is only a configuration step: no claim of safe physical output.
 */
#include "acoustic_device_pin.h"
#if defined(__APPLE__)
#include <AudioToolbox/AudioToolbox.h>
#include <CoreAudio/CoreAudio.h>
#include <CoreFoundation/CoreFoundation.h>
#include <math.h>
#include <stdint.h>

int fm_acoustic_bind_queue_to_route(void *opaque_queue,
                                    const FMRouteFingerprint *route) {
  if (!opaque_queue || !route || route->os_device_token==0U ||
      route->output_channels==0U ||
      !isfinite(route->nominal_sample_rate_hz) ||
      route->nominal_sample_rate_hz<=0.0) return -1;
  /* Abort if default route already changed. The OS route token is private. */
  if (!fm_route_unchanged(route)) return -1;
  const AudioDeviceID device=(AudioDeviceID)route->os_device_token;
  const AudioObjectPropertyAddress uid_addr = {
      kAudioDevicePropertyDeviceUID,
      kAudioDevicePropertyScopeOutput,
      kAudioObjectPropertyElementMain
  };
  CFStringRef expected_uid=NULL;
  UInt32 size=(UInt32)sizeof(expected_uid);
  if (AudioObjectGetPropertyData(device,&uid_addr,0,NULL,
                                 &size,&expected_uid)!=noErr ||
      size!=sizeof(expected_uid) || !expected_uid) {
    if (expected_uid) CFRelease(expected_uid);
    return -1;
  }
  if (CFGetTypeID(expected_uid)!=CFStringGetTypeID() ||
      CFStringGetLength(expected_uid)==0) {
    CFRelease(expected_uid);
    return -1;
  }
  AudioQueueRef queue=(AudioQueueRef)opaque_queue;
  const OSStatus set_rc=AudioQueueSetProperty(
      queue,kAudioQueueProperty_CurrentDevice,
      &expected_uid,(UInt32)sizeof(expected_uid));
  if (set_rc!=noErr) { CFRelease(expected_uid); return -1; }

  /* Verify that the queue accepted the exact device identity. Apple's
   * AudioQueueGetProperty returns a duplicated CFStringRef: release it.
   * UID stays internal; never print, persist or export it. */
  CFStringRef actual_uid=NULL;
  size=(UInt32)sizeof(actual_uid);
  const OSStatus get_rc=AudioQueueGetProperty(
      queue,kAudioQueueProperty_CurrentDevice,&actual_uid,&size);
  const int uid_ok=(get_rc==noErr && size==sizeof(actual_uid) &&
      actual_uid && CFGetTypeID(actual_uid)==CFStringGetTypeID() &&
      CFEqual(expected_uid,actual_uid));
  if (actual_uid) CFRelease(actual_uid);
  CFRelease(expected_uid);
  if (!uid_ok) return -1;

  /* Hardware rate and channels are independent queue properties, not
   * guarantees of SPL/physical output. Fail closed on unsupported formats. */
  Float64 actual_rate=0.0;
  size=(UInt32)sizeof(actual_rate);
  if (AudioQueueGetProperty(queue,kAudioQueueDeviceProperty_SampleRate,
                            &actual_rate,&size)!=noErr ||
      size!=sizeof(actual_rate) || !isfinite(actual_rate) ||
      fabs(actual_rate-route->nominal_sample_rate_hz)>0.5) return -1;
  UInt32 actual_channels=0U;
  size=(UInt32)sizeof(actual_channels);
  if (AudioQueueGetProperty(queue,kAudioQueueDeviceProperty_NumberChannels,
                            &actual_channels,&size)!=noErr ||
      size!=sizeof(actual_channels) ||
      actual_channels!=route->output_channels) return -1;
  /* Recheck route after binding; never claim safety across a race. */
  return fm_route_unchanged(route) ? 0 : -1;
}
#else
int fm_acoustic_bind_queue_to_route(void *audio_queue,
                                    const FMRouteFingerprint *route) {
  (void)audio_queue; (void)route; return -1;
}
#endif
