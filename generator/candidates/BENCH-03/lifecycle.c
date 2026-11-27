/* SPDX-License-Identifier: Apache-2.0 */
#include "lifecycle.h"
#include <stdlib.h>
#define MAX_FRAMES 16384U
#define MAX_CHANNELS 64U
static void release(FMBuffers *b) {
    free(b->input); free(b->output);
    b->input=NULL; b->output=NULL; b->in_values=0; b->out_values=0;
}
int fm_reserve(FMBuffers *b, uint32_t inf, uint32_t inc, uint32_t outf, uint32_t outc) {
    if(!b || b->state!=FM_IDLE || b->input || b->output || b->in_values || b->out_values)return 0;
    if(!inf || inf>MAX_FRAMES || !outf || outf>MAX_FRAMES || !inc || inc>MAX_CHANNELS || !outc || outc>MAX_CHANNELS)return 0;
    b->in_values=(size_t)inf*inc; b->out_values=(size_t)outf*outc;
    b->input=calloc(b->in_values,sizeof(float)); b->output=calloc(b->out_values,sizeof(float));
    if(!b->input || !b->output){release(b);b->state=FM_INVALIDATED;return 0;}
    b->state=FM_RESERVED;return 1;
}
void fm_invalidate(FMBuffers *b) {
    if(b && b->state!=FM_CLOSED){release(b);b->state=FM_INVALIDATED;}
}
void fm_close(FMBuffers *b) {
    if(b){release(b);b->state=FM_CLOSED;}
}
