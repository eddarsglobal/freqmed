/* SPDX-License-Identifier: Apache-2.0 */
#include "readiness.h"
#include <math.h>
#include <stdio.h>
#include <string.h>
#define C(x) do{if(!(x)){fprintf(stderr,"FAIL %d: %s\n",__LINE__,#x);return 1;}++n;}while(0)
int main(void) {
    unsigned n=0;FMReadinessProfile a={0},b;
    /* Software vectors, not native hardware measurements. */
    a.endpoint=(FMEndpoint){"TEST_A",2,44100,FM_ROUTE_BUILT_IN,1};
    a.alive_known=a.alive=a.running_known=a.ranges_known=a.buffer_known=a.buffer_range_known=1;
    a.range_count=2;a.rates[0]=(FMRateRange){44100,44100};a.rates[1]=(FMRateRange){48000,48000};
    a.buffer_frames=256;a.buffer_min=64;a.buffer_max=1024;
    C(fm_readiness_assess(NULL,&a)==FM_RD_INCOMPLETE);
    C(fm_readiness_assess(&a,NULL)==FM_RD_INCOMPLETE);
    C(fm_readiness_assess(&a,&a)==FM_RD_METADATA_ONLY);
    b=a;b.alive_known=0;b.alive=0;C(fm_readiness_assess(&a,&b)==FM_RD_INCOMPLETE);
    b=a;b.alive_known=0;C(fm_readiness_assess(&a,&b)==FM_RD_INCONSISTENT);
    b=a;b.alive=0;C(fm_readiness_assess(&a,&b)==FM_RD_NOT_CANDIDATE);
    b=a;b.running=1;C(fm_readiness_assess(&a,&b)==FM_RD_BUSY);
    b=a;b.running_known=0;C(fm_readiness_assess(&a,&b)==FM_RD_INCOMPLETE);
    b=a;b.running=2;C(fm_readiness_assess(&a,&b)==FM_RD_INCONSISTENT);
    b=a;b.endpoint.route=FM_ROUTE_VIRTUAL;C(fm_readiness_assess(&a,&b)==FM_RD_NOT_CANDIDATE);
    b=a;b.endpoint.route=FM_ROUTE_UNKNOWN;C(fm_readiness_assess(&a,&b)==FM_RD_NOT_CANDIDATE);
    b=a;b.endpoint.is_default=0;C(fm_readiness_assess(&a,&b)==FM_RD_NOT_CANDIDATE);
    b=a;b.endpoint.is_default=2;C(fm_readiness_assess(&a,&b)==FM_RD_INCONSISTENT);
    b=a;b.endpoint.uid[0]=0;C(fm_readiness_assess(&a,&b)==FM_RD_INCONSISTENT);
    b=a;memset(b.endpoint.uid,'x',sizeof(b.endpoint.uid));C(fm_readiness_assess(&a,&b)==FM_RD_INCONSISTENT);
    b=a;strcpy(b.endpoint.uid,"TEST_B");C(fm_readiness_assess(&a,&b)==FM_RD_CHANGED);
    b=a;b.endpoint.channels=0;C(fm_readiness_assess(&a,&b)==FM_RD_INCONSISTENT);
    b=a;b.endpoint.channels=1;C(fm_readiness_assess(&a,&b)==FM_RD_CHANGED);
    b=a;b.endpoint.rate=NAN;C(fm_readiness_assess(&a,&b)==FM_RD_INCONSISTENT);
    b=a;b.endpoint.rate=48000;C(fm_readiness_assess(&a,&b)==FM_RD_CHANGED);
    b=a;b.endpoint.rate=32000;C(fm_readiness_assess(&a,&b)==FM_RD_INCONSISTENT);
    b=a;b.range_count=65;C(fm_readiness_assess(&a,&b)==FM_RD_INCONSISTENT);
    b=a;b.range_count=0;C(fm_readiness_assess(&a,&b)==FM_RD_INCONSISTENT);
    b=a;b.ranges_known=0;b.range_count=0;C(fm_readiness_assess(&a,&b)==FM_RD_INCOMPLETE);
    b=a;b.rates[0].maximum=40000;C(fm_readiness_assess(&a,&b)==FM_RD_INCONSISTENT);
    b=a;b.rates[1].maximum=INFINITY;C(fm_readiness_assess(&a,&b)==FM_RD_INCONSISTENT);
    b=a;b.rates[1].maximum=96000;C(fm_readiness_assess(&a,&b)==FM_RD_CHANGED);
    b=a;b.buffer_known=0;b.buffer_frames=0;C(fm_readiness_assess(&a,&b)==FM_RD_INCOMPLETE);
    b=a;b.buffer_frames=0;C(fm_readiness_assess(&a,&b)==FM_RD_INCONSISTENT);
    b=a;b.buffer_frames=2048;C(fm_readiness_assess(&a,&b)==FM_RD_INCONSISTENT);
    b=a;b.buffer_frames=512;C(fm_readiness_assess(&a,&b)==FM_RD_CHANGED);
    b=a;b.buffer_min=2048;C(fm_readiness_assess(&a,&b)==FM_RD_INCONSISTENT);
    b=a;b.buffer_max=2048;C(fm_readiness_assess(&a,&b)==FM_RD_CHANGED);
    b=a;b.buffer_range_known=0;b.buffer_min=0;b.buffer_max=0;C(fm_readiness_assess(&a,&b)==FM_RD_INCOMPLETE);
    b=a;b.endpoint.route=FM_ROUTE_USB;C(fm_readiness_assess(&b,&b)==FM_RD_METADATA_ONLY);
    printf("GEN_PLATFORM_07_ASSERTIONS=%u PASS\n",n);return 0;
}
