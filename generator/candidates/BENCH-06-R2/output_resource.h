/* SPDX-License-Identifier: Apache-2.0 */
#ifndef FM_BENCH06_OUTPUT_RESOURCE_H
#define FM_BENCH06_OUTPUT_RESOURCE_H
#include <stddef.h>
#include <stdint.h>
typedef struct { double rate; uint32_t frames,channels,format,flags,bits,bytes_frame,frames_packet,bytes_packet; } FMOutputSpec;
typedef struct FMOutputResource FMOutputResource;
/* Single owner; no device handle or hardware destination. */
int fm_output_compatible(const FMOutputSpec *s);
FMOutputResource *fm_output_create(const FMOutputSpec *s);
int fm_output_submit(FMOutputResource *r,const double *mono,size_t frames);
int fm_output_read(FMOutputResource *r,const FMOutputSpec *current,float *dst,size_t values);
void fm_output_stop(FMOutputResource *r);
int fm_output_closed(const FMOutputResource *r);
void fm_output_destroy(FMOutputResource *r);
#endif
