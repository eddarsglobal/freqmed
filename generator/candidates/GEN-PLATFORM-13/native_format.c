/* SPDX-License-Identifier: Apache-2.0 */
#include "native_format.h"
#include <math.h>
static int valid_format(const FMNativeFormat *f) {
    if(!f->format_id||!isfinite(f->rate)||f->rate<=0||
       !f->channels||f->channels>256||f->linear_pcm!=1||
       !f->bytes_frame||!f->bits||f->bits>64||
       !f->bytes_packet||!f->frames_packet)return 0;
    return (uint64_t)f->bytes_frame*f->frames_packet==f->bytes_packet &&
        (uint64_t)f->bytes_frame*8U>=f->bits;
}
static int valid_set(const FMStreamSet *s,const FMEndpoint *p) {
    if(!s->count||s->count>FM_STREAM_CAP)return 0;
    unsigned sum=0;
    for(unsigned i=0;i<s->count;i++){
        const FMStream *x=&s->streams[i];
        if(!x->local_id||!valid_format(&x->logical)||!valid_format(&x->physical)||
           x->logical.rate!=p->rate||sum>256U-x->logical.channels)return 0;
        sum+=x->logical.channels;
        for(unsigned j=0;j<i;j++)if(s->streams[j].local_id==x->local_id)return 0;
    }
    return sum==p->channels;
}
static int same_format(const FMNativeFormat *a,const FMNativeFormat *b){
    return a->rate==b->rate&&a->format_id==b->format_id&&a->flags==b->flags&&
        a->bytes_packet==b->bytes_packet&&a->frames_packet==b->frames_packet&&
        a->bytes_frame==b->bytes_frame&&a->channels==b->channels&&a->bits==b->bits&&
        a->linear_pcm==b->linear_pcm;
}
static int same_set(const FMStreamSet *a,const FMStreamSet *b){
    if(a->count!=b->count)return 0;
    for(unsigned i=0;i<a->count;i++){
        const FMStream *x=&a->streams[i],*y=&b->streams[i];
        if(x->local_id!=y->local_id||!same_format(&x->logical,&y->logical)||
           !same_format(&x->physical,&y->physical))return 0;
    }
    return 1;
}
FMNativeResult fm_native_assess(const FMNativeIOProfile *a,const FMNativeIOProfile *b) {
    if(!a||!b||!a->input.count||!a->output.count||!b->input.count||!b->output.count)
        return FM_N_INCOMPLETE;
    FMPairResult p=fm_pair_assess(&a->pair,&b->pair);
    if(p==FM_PAIR_INCOMPLETE)return FM_N_INCOMPLETE;
    if(p==FM_PAIR_CHANGED)return FM_N_CHANGED;
    if(p!=FM_PAIR_METADATA_ONLY)return FM_N_UNSUPPORTED;
    if(!valid_set(&a->input,&a->pair.input)||!valid_set(&b->input,&b->pair.input)||
       !valid_set(&a->output,&a->pair.output.endpoint)||!valid_set(&b->output,&b->pair.output.endpoint))
        return FM_N_UNSUPPORTED;
    return same_set(&a->input,&b->input)&&same_set(&a->output,&b->output)?
        FM_N_METADATA_ONLY:FM_N_CHANGED;
}
