/* SPDX-License-Identifier: Apache-2.0 */
#ifndef FM_BENCH04_TRANSPORT_H
#define FM_BENCH04_TRANSPORT_H
#include <stddef.h>
#include <stdint.h>
typedef struct FMTransport FMTransport;
/* Single owner; no device handles, no hardware buffers, no audio API. */
FMTransport *fm_transport_create(uint32_t input_frames,uint32_t input_channels,uint32_t output_frames,uint32_t output_channels);
/* Numerical vector only; one outstanding block. A rejected push invalidates the transport. */
int fm_transport_push(FMTransport *t,const double *mono,size_t frames);
/* Copy to caller-owned private memory, not a native audio buffer. */
int fm_transport_take(FMTransport *t,float *out,size_t capacity,size_t *frames);
void fm_transport_stop(FMTransport *t);
void fm_transport_destroy(FMTransport *t);
#endif
