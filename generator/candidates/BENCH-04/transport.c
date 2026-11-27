/* SPDX-License-Identifier: Apache-2.0 */
#include "transport.h"
#include "lifecycle.h"
#include <math.h>
#include <stdlib.h>
#include <string.h>
struct FMTransport { FMBuffers b; size_t frames,channels,written; int pending; };
FMTransport *fm_transport_create(uint32_t inf,uint32_t inc,uint32_t outf,uint32_t outc) {
    FMTransport *t=calloc(1,sizeof(*t));
    if(!t)return NULL;
    if(!fm_reserve(&t->b,inf,inc,outf,outc)){fm_close(&t->b);free(t);return NULL;}
    t->frames=outf;t->channels=outc;return t;
}
void fm_transport_stop(FMTransport *t) {
    if(t){fm_invalidate(&t->b);t->pending=0;t->written=0;}
}
int fm_transport_push(FMTransport *t,const double *mono,size_t frames) {
    if(!t||t->b.state!=FM_RESERVED)return 0;
    if(t->pending||!mono||!frames||frames>t->frames){fm_transport_stop(t);return 0;}
    for(size_t i=0;i<frames;i++)if(!isfinite(mono[i])||fabs(mono[i])>1.0){fm_transport_stop(t);return 0;}
    memset(t->b.output,0,t->b.out_values*sizeof(float));
    for(size_t i=0;i<frames;i++)for(size_t c=0;c<t->channels;c++)t->b.output[i*t->channels+c]=(float)mono[i];
    t->written=frames;t->pending=1;return 1;
}
int fm_transport_take(FMTransport *t,float *out,size_t capacity,size_t *frames) {
    if(!frames)return 0;
    *frames=0;
    if(!t||t->b.state!=FM_RESERVED)return 0;
    if(!out||capacity<t->b.out_values||!t->pending){fm_transport_stop(t);return 0;}
    memcpy(out,t->b.output,t->b.out_values*sizeof(float));
    *frames=t->written;memset(t->b.output,0,t->b.out_values*sizeof(float));t->pending=0;t->written=0;return 1;
}
void fm_transport_destroy(FMTransport *t) {if(t){fm_close(&t->b);free(t);}}
