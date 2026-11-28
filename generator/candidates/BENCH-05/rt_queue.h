/* SPDX-License-Identifier: Apache-2.0 */
#ifndef FM_BENCH05_RT_QUEUE_H
#define FM_BENCH05_RT_QUEUE_H
#include <stddef.h>
typedef struct FMRTQueue FMRTQueue;
/* Exactly one producer and one consumer; caller joins both before destroy.
 * All buffers are private RAM. No physical audio device or I/O API. */
FMRTQueue *fm_rt_create(size_t values);
int fm_rt_push(FMRTQueue *q,const float *src,size_t values);
int fm_rt_pop(FMRTQueue *q,float *dst,size_t values);
void fm_rt_stop(FMRTQueue *q);
int fm_rt_stopped(const FMRTQueue *q);
void fm_rt_destroy(FMRTQueue *q);
#endif
