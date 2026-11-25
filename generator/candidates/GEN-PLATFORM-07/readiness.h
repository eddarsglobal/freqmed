/* SPDX-License-Identifier: Apache-2.0 */
#ifndef FM_READINESS_H
#define FM_READINESS_H
#include "binding.h"
#define FM_RATE_CAP 64U
typedef struct { double minimum,maximum; } FMRateRange;
typedef struct {
    FMEndpoint endpoint;
    unsigned alive_known,alive,running_known,running;
    unsigned ranges_known,range_count;
    FMRateRange rates[FM_RATE_CAP];
    unsigned buffer_known,buffer_frames,buffer_range_known;
    double buffer_min,buffer_max;
} FMReadinessProfile;
typedef enum {
    FM_RD_INCOMPLETE=0,FM_RD_INCONSISTENT,FM_RD_CHANGED,
    FM_RD_NOT_CANDIDATE,FM_RD_BUSY,FM_RD_METADATA_ONLY
} FMReadinessResult;
/* Read-only metadata assessment. Never grants access to an output. */
FMReadinessResult fm_readiness_assess(const FMReadinessProfile *a,const FMReadinessProfile *b);
#endif
