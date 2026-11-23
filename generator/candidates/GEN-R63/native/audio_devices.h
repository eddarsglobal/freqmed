/* SPDX-License-Identifier: Apache-2.0 */
#ifndef FREQMED_AUDIO_DEVICES_R56_H
#define FREQMED_AUDIO_DEVICES_R56_H
#include <stdint.h>
#define FM_AUDIO_MAX_DEVICES 32U
#define FM_AUDIO_LABEL_MAX 128U
typedef struct {
    uint32_t device_id;
    uint32_t output_channels;
    double nominal_rate_hz;
    int32_t is_default;
    char name[FM_AUDIO_LABEL_MAX];
} FMNativeAudioDevice;
typedef struct {
    uint32_t count;
    int32_t truncated;
    FMNativeAudioDevice devices[FM_AUDIO_MAX_DEVICES];
} FMNativeAudioSnapshot;
int fm_list_acoustic_outputs(FMNativeAudioSnapshot *out);
#endif
