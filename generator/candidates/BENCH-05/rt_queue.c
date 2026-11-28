/* SPDX-License-Identifier: Apache-2.0 */
#include "rt_queue.h"
#include <stdatomic.h>
#include <stdlib.h>
#include <string.h>
#define SLOTS 4U
#define MAX_VALUES (4096U*64U)
struct FMRTQueue { atomic_uint head,tail,stop; size_t values; float *slots; };
FMRTQueue *fm_rt_create(size_t values){
    if(!values||values>MAX_VALUES)return NULL;
    FMRTQueue *q=calloc(1,sizeof(*q));if(!q)return NULL;
    atomic_init(&q->head,0);atomic_init(&q->tail,0);atomic_init(&q->stop,0);
    if(!atomic_is_lock_free(&q->head)||!atomic_is_lock_free(&q->tail)||!atomic_is_lock_free(&q->stop)){free(q);return NULL;}
    q->values=values;q->slots=calloc(SLOTS*values,sizeof(float));
    if(!q->slots){free(q);return NULL;}return q;
}
void fm_rt_stop(FMRTQueue *q){if(q)atomic_store_explicit(&q->stop,1,memory_order_release);}
int fm_rt_stopped(const FMRTQueue *q){return !q||atomic_load_explicit(&q->stop,memory_order_acquire)!=0;}
int fm_rt_push(FMRTQueue *q,const float *src,size_t values){
    if(fm_rt_stopped(q))return 0;
    if(!src||values!=q->values){fm_rt_stop(q);return 0;}
    unsigned h=atomic_load_explicit(&q->head,memory_order_relaxed);
    unsigned t=atomic_load_explicit(&q->tail,memory_order_acquire);
    if(h-t>=SLOTS){fm_rt_stop(q);return 0;}
    memcpy(q->slots+(h%SLOTS)*values,src,values*sizeof(float));
    if(fm_rt_stopped(q))return 0;
    atomic_store_explicit(&q->head,h+1,memory_order_release);return 1;
}
int fm_rt_pop(FMRTQueue *q,float *dst,size_t values){
    if(!q||!dst||values!=q->values){fm_rt_stop(q);return 0;}
    memset(dst,0,values*sizeof(float));
    if(fm_rt_stopped(q))return 0;
    unsigned t=atomic_load_explicit(&q->tail,memory_order_relaxed);
    unsigned h=atomic_load_explicit(&q->head,memory_order_acquire);
    if(h==t){fm_rt_stop(q);return 0;}
    memcpy(dst,q->slots+(t%SLOTS)*values,values*sizeof(float));
    atomic_store_explicit(&q->tail,t+1,memory_order_release);
    if(fm_rt_stopped(q)){memset(dst,0,values*sizeof(float));return 0;}return 1;
}
void fm_rt_destroy(FMRTQueue *q){if(q){fm_rt_stop(q);free(q->slots);free(q);}}
