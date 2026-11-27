/* SPDX-License-Identifier: Apache-2.0 */
#ifndef FM_BENCH03_LIFECYCLE_H
#define FM_BENCH03_LIFECYCLE_H
#include <stddef.h>
#include <stdint.h>
typedef enum { FM_IDLE, FM_RESERVED, FM_INVALIDATED, FM_CLOSED } FMState;
typedef struct { FMState state; float *input, *output; size_t in_values, out_values; } FMBuffers;
int fm_reserve(FMBuffers *b, uint32_t inf, uint32_t inc, uint32_t outf, uint32_t outc);
void fm_invalidate(FMBuffers *b);
void fm_close(FMBuffers *b);
#endif
