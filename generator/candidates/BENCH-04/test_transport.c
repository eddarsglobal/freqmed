/* SPDX-License-Identifier: Apache-2.0 */
#include "transport.h"
#include <math.h>
#include <stdio.h>
#define CHECK(x) do{if(!(x)){fprintf(stderr,"FAIL %d\n",__LINE__);return 1;}n++;}while(0)
int main(void){
    unsigned n=0; double v[]={0.25,-0.5,1.0,0.0};float out[8];size_t w=0;
    CHECK(!fm_transport_create(0,1,4,2));
    CHECK(!fm_transport_create(4,1,4,65));
    FMTransport *t=fm_transport_create(4,1,4,2);CHECK(t);
    CHECK(fm_transport_push(t,v,3));CHECK(fm_transport_take(t,out,8,&w)&&w==3);
    CHECK(out[0]==0.25f&&out[1]==0.25f&&out[2]==-0.5f&&out[3]==-0.5f);
    CHECK(out[4]==1&&out[5]==1&&out[6]==0&&out[7]==0);
    CHECK(fm_transport_push(t,v,4));CHECK(!fm_transport_push(t,v,4));
    CHECK(!fm_transport_take(t,out,8,&w)&&w==0);fm_transport_destroy(t);
    t=fm_transport_create(4,1,4,1);CHECK(t);CHECK(fm_transport_push(t,v,4));
    CHECK(fm_transport_take(t,out,4,&w)&&w==4&&out[0]==0.25f&&out[1]==-0.5f&&out[2]==1);
    CHECK(!fm_transport_take(t,out,4,&w)&&w==0);CHECK(!fm_transport_push(t,v,4));fm_transport_destroy(t);
    t=fm_transport_create(4,1,4,2);CHECK(t);CHECK(fm_transport_push(t,v,4));
    CHECK(!fm_transport_take(t,out,7,&w)&&w==0);CHECK(!fm_transport_push(t,v,4));fm_transport_destroy(t);
    t=fm_transport_create(4,1,4,2);CHECK(t);v[0]=NAN;CHECK(!fm_transport_push(t,v,4));fm_transport_destroy(t);
    t=fm_transport_create(4,1,4,2);CHECK(t);v[0]=1.01;CHECK(!fm_transport_push(t,v,4));fm_transport_destroy(t);
    t=fm_transport_create(4,1,4,2);CHECK(t);v[0]=0;CHECK(!fm_transport_push(t,v,5));fm_transport_destroy(t);
    t=fm_transport_create(4,1,4,2);CHECK(t);CHECK(fm_transport_push(t,v,4));fm_transport_stop(t);fm_transport_stop(t);
    CHECK(!fm_transport_take(t,out,8,&w)&&w==0);CHECK(!fm_transport_push(t,v,4));fm_transport_destroy(t);
    printf("BENCH04_TRANSPORT_ASSERTIONS=%u PASS\n",n);return 0;
}
