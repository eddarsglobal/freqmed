/* SPDX-License-Identifier: Apache-2.0 */
#include "rt_queue.h"
#include <pthread.h>
#include <stdatomic.h>
#include <sched.h>
#include <stdio.h>
#define CHECK(x) do{if(!(x)){fprintf(stderr,"FAIL %d\n",__LINE__);return 1;}n++;}while(0)
#define COUNT 10000U
typedef struct { FMRTQueue *q; atomic_uint sent,received,failed; } Context;
static void *producer(void *arg){
    Context *c=arg;
    for(unsigned i=0;i<COUNT;i++){
        while(atomic_load(&c->received)!=i&&!atomic_load(&c->failed))sched_yield();
        if(atomic_load(&c->failed))break;
        float v[2]={(float)i,-(float)i};
        if(!fm_rt_push(c->q,v,2)){atomic_store(&c->failed,1);break;}
        atomic_store(&c->sent,i+1);
    }return NULL;
}
static void *consumer(void *arg){
    Context *c=arg;
    for(unsigned i=0;i<COUNT;i++){
        while(atomic_load(&c->sent)!=i+1&&!atomic_load(&c->failed))sched_yield();
        if(atomic_load(&c->failed))break;
        float v[2];
        if(!fm_rt_pop(c->q,v,2)||v[0]!=(float)i||v[1]!=-(float)i){atomic_store(&c->failed,1);break;}
        atomic_store(&c->received,i+1);
    }return NULL;
}
int main(void){
    unsigned n=0;float a[2]={1,-1},b[2]={8,8};
    CHECK(!fm_rt_create(0));CHECK(!fm_rt_create(4096U*64U+1));
    FMRTQueue *q=fm_rt_create(2);CHECK(q);CHECK(!fm_rt_stopped(q));
    CHECK(fm_rt_push(q,a,2));CHECK(fm_rt_pop(q,b,2)&&b[0]==1&&b[1]==-1);
    CHECK(!fm_rt_pop(q,b,2)&&b[0]==0&&b[1]==0);CHECK(fm_rt_stopped(q));
    CHECK(!fm_rt_push(q,a,2));fm_rt_destroy(q);
    q=fm_rt_create(2);CHECK(q);
    for(unsigned i=0;i<4;i++)CHECK(fm_rt_push(q,a,2));
    CHECK(!fm_rt_push(q,a,2));CHECK(fm_rt_stopped(q));CHECK(!fm_rt_pop(q,b,2)&&b[0]==0&&b[1]==0);fm_rt_destroy(q);
    q=fm_rt_create(2);CHECK(q);CHECK(!fm_rt_push(q,a,1));CHECK(fm_rt_stopped(q));fm_rt_destroy(q);
    q=fm_rt_create(2);CHECK(q);CHECK(fm_rt_push(q,a,2));fm_rt_stop(q);fm_rt_stop(q);
    CHECK(!fm_rt_pop(q,b,2)&&b[0]==0&&b[1]==0);fm_rt_destroy(q);
    Context c={0};c.q=fm_rt_create(2);CHECK(c.q);atomic_init(&c.sent,0);atomic_init(&c.received,0);atomic_init(&c.failed,0);
    pthread_t p,t;CHECK(pthread_create(&p,NULL,producer,&c)==0);
    if(pthread_create(&t,NULL,consumer,&c)!=0){atomic_store(&c.failed,1);pthread_join(p,NULL);fm_rt_destroy(c.q);return 1;}
    CHECK(pthread_join(p,NULL)==0);CHECK(pthread_join(t,NULL)==0);
    CHECK(!atomic_load(&c.failed)&&atomic_load(&c.received)==COUNT);CHECK(!fm_rt_stopped(c.q));fm_rt_destroy(c.q);
    printf("BENCH05_QUEUE_ASSERTIONS=%u PASS\nBENCH05_THREAD_BLOCKS=%u PASS\n",n,COUNT);return 0;
}
