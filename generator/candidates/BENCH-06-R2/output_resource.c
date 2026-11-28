/* SPDX-License-Identifier: Apache-2.0 */
#include "output_resource.h"
#include "transport.h"
#include "rt_queue.h"
#include <math.h>
#include <stdlib.h>
#include <string.h>
struct FMOutputResource { FMOutputSpec spec; FMTransport *transport; FMRTQueue *queue; float *scratch; size_t values; int closed; };
int fm_output_compatible(const FMOutputSpec *s){
    return s&&isfinite(s->rate)&&s->rate>=1&&s->rate<=384000&&floor(s->rate)==s->rate&&
        s->frames>=1&&s->frames<=4096&&s->channels>=1&&s->channels<=64&&
        s->format==UINT32_C(0x6c70636d)&&s->flags==9&&s->bits==32&&sizeof(float)==4&&
        s->bytes_frame==4*s->channels&&s->frames_packet==1&&s->bytes_packet==s->bytes_frame;
}
static int equal(const FMOutputSpec *a,const FMOutputSpec *b){
    return fm_output_compatible(b)&&a->rate==b->rate&&a->frames==b->frames&&a->channels==b->channels&&
        a->format==b->format&&a->flags==b->flags&&a->bits==b->bits&&a->bytes_frame==b->bytes_frame&&
        a->frames_packet==b->frames_packet&&a->bytes_packet==b->bytes_packet;
}
void fm_output_stop(FMOutputResource *r){
    if(!r||r->closed)return;
    fm_rt_stop(r->queue);fm_rt_destroy(r->queue);r->queue=NULL;
    fm_transport_stop(r->transport);fm_transport_destroy(r->transport);r->transport=NULL;
    free(r->scratch);r->scratch=NULL;r->closed=1;
}
int fm_output_closed(const FMOutputResource *r){return r&&r->closed&&!r->queue&&!r->transport&&!r->scratch;}
void fm_output_destroy(FMOutputResource *r){if(r){fm_output_stop(r);free(r);}}
FMOutputResource *fm_output_create(const FMOutputSpec *s){
    if(!fm_output_compatible(s))return NULL;
    FMOutputResource *r=calloc(1,sizeof(*r));if(!r)return NULL;
    r->spec=*s;r->values=(size_t)s->frames*s->channels;
    r->transport=fm_transport_create(s->frames,1,s->frames,s->channels);
    r->queue=fm_rt_create(r->values);r->scratch=calloc(r->values,sizeof(float));
    if(!r->transport||!r->queue||!r->scratch){fm_output_destroy(r);return NULL;}
    return r;
}
int fm_output_submit(FMOutputResource *r,const double *mono,size_t frames){
    if(!r||r->closed)return 0;
    size_t written=0;
    if(frames!=r->spec.frames||!fm_transport_push(r->transport,mono,frames)||
       !fm_transport_take(r->transport,r->scratch,r->values,&written)||written!=frames||
       !fm_rt_push(r->queue,r->scratch,r->values)){fm_output_stop(r);return 0;}
    return 1;
}
int fm_output_read(FMOutputResource *r,const FMOutputSpec *current,float *dst,size_t values){
    if(!r)return 0;
    if(!dst||values!=r->values){fm_output_stop(r);return 0;}
    memset(dst,0,values*sizeof(float));
    if(r->closed)return 0;
    if(!equal(&r->spec,current)||!fm_rt_pop(r->queue,dst,values)){fm_output_stop(r);return 0;}
    return 1;
}
