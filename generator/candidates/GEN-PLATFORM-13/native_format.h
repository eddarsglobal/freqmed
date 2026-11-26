/* SPDX-License-Identifier: Apache-2.0 */
#ifndef FM_NATIVE_FORMAT_H
#define FM_NATIVE_FORMAT_H
#include "integrated_bridge.h"
#define FM_STREAM_CAP 16U
typedef struct {
    double rate;
    uint32_t format_id,flags,bytes_packet,frames_packet,bytes_frame,channels,bits;
    unsigned linear_pcm;
} FMNativeFormat;
typedef struct {uint32_t local_id;FMNativeFormat logical,physical;} FMStream;
typedef struct {unsigned count;FMStream streams[FM_STREAM_CAP];} FMStreamSet;
typedef struct {FMIntegratedPair pair;FMStreamSet input,output;} FMNativeIOProfile;
typedef enum {FM_N_INCOMPLETE=0,FM_N_UNSUPPORTED,FM_N_CHANGED,FM_N_METADATA_ONLY} FMNativeResult;
/* Read-only descriptors. No audio stream opening, format conversion or output. */
FMNativeResult fm_native_assess(const FMNativeIOProfile *a,const FMNativeIOProfile *b);
#endif
