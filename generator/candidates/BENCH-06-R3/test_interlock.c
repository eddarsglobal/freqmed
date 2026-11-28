/* SPDX-License-Identifier: Apache-2.0 */
#include "interlock.h"
#include <stdio.h>
#include <pthread.h>
#define C(x) do{if(!(x)){fprintf(stderr,"FAIL %d\n",__LINE__);return 1;}n++;}while(0)
static void *notify(void *p){fm_interlock_trip(p,FM_R3_CHANGE);return NULL;}
int main(void){
    unsigned n=0;FMInterlock a,b,c,d,e,f,h;
    C(!fm_interlock_init(NULL,0,1));C(!fm_interlock_poll(NULL,0));C(!fm_interlock_physical_allowed(NULL));
    C(fm_interlock_init(&a,100,10));C(fm_interlock_poll(&a,100));C(fm_interlock_poll(&a,109));
    C(!fm_interlock_physical_allowed(&a));C(!fm_interlock_poll(&a,110));C(fm_interlock_reasons(&a)==FM_R3_TIMEOUT);
    C(!fm_interlock_poll(&a,101));C(!fm_interlock_physical_allowed(&a));
    C(fm_interlock_init(&b,100,10));C(!fm_interlock_poll(&b,99));C(fm_interlock_reasons(&b)==FM_R3_CLOCK);
    C(fm_interlock_init(&c,100,10));fm_interlock_trip(&c,FM_R3_STOP);fm_interlock_trip(&c,FM_R3_CHANGE);
    C(fm_interlock_reasons(&c)==(FM_R3_STOP|FM_R3_CHANGE));C(!fm_interlock_poll(&c,101));
    C(!fm_interlock_init(&d,UINT64_MAX,1));C(!fm_interlock_poll(&d,UINT64_MAX));
    C(!fm_interlock_init(&e,0,0));C(!fm_interlock_init(&f,0,10001));
    C(fm_interlock_init(&h,100,10));pthread_t t;C(pthread_create(&t,NULL,notify,&h)==0);C(pthread_join(t,NULL)==0);
    C(fm_interlock_reasons(&h)==FM_R3_CHANGE);C(!fm_interlock_poll(&h,101));fm_interlock_trip(&h,0);
    C(fm_interlock_reasons(&h)==(FM_R3_CHANGE|FM_R3_FAULT));C(!fm_interlock_physical_allowed(&h));
    printf("BENCH06_R3_INTERLOCK_ASSERTIONS=%u PASS\n",n);return 0;
}
