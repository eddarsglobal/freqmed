/* SPDX-License-Identifier: Apache-2.0 */
#ifndef FREQMED_ACOUSTIC_DEVICE_PIN_H
#define FREQMED_ACOUSTIC_DEVICE_PIN_H
#include "acoustic_route_guard.h"
/* Source-only Mac hardware route binding: AudioQueueRef passed opaque.
 * R5 runnable CLI never links or calls this function.
 */
int fm_acoustic_bind_queue_to_route(void *audio_queue,
                                    const FMRouteFingerprint *route);
#endif
