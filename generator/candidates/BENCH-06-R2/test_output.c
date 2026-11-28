/* SPDX-License-Identifier: Apache-2.0 */
#include "output_resource.h"
#include <stdio.h>
#include <math.h>
#define C(x) do{if(!(x)){fprintf(stderr,"FAIL %d\n",__LINE__);return 1;}n++;}while(0)
int main(void){
    unsigned n=0;FMOutputSpec s={44100,4,2,0x6c70636d,9,32,8,1,8},bad=s;
    double v[4]={0.125,-0.25,0,0.5};float dst[8];
    C(fm_output_compatible(&s));bad.flags=41;C(!fm_output_create(&bad));bad=s;bad.rate=NAN;C(!fm_output_create(&bad));
    bad=s;bad.bytes_frame=4;C(!fm_output_create(&bad));bad=s;bad.frames=4097;C(!fm_output_create(&bad));
    FMOutputResource *r=fm_output_create(&s);C(r);C(fm_output_submit(r,v,4));C(fm_output_read(r,&s,dst,8));
    C(dst[0]==0.125f&&dst[1]==0.125f&&dst[2]==-0.25f&&dst[3]==-0.25f&&dst[4]==0&&dst[5]==0&&dst[6]==0.5f&&dst[7]==0.5f);
    C(fm_output_submit(r,v,4));bad=s;bad.rate=48000;C(!fm_output_read(r,&bad,dst,8));C(fm_output_closed(r));
    C(dst[0]==0&&dst[7]==0);C(!fm_output_submit(r,v,4));fm_output_destroy(r);
    r=fm_output_create(&s);C(r);for(unsigned i=0;i<4;i++)C(fm_output_submit(r,v,4));
    C(!fm_output_submit(r,v,4));C(fm_output_closed(r));fm_output_destroy(r);
    r=fm_output_create(&s);C(r);C(!fm_output_read(r,&s,dst,8));C(fm_output_closed(r));fm_output_destroy(r);
    r=fm_output_create(&s);C(r);C(!fm_output_submit(r,v,3));C(fm_output_closed(r));fm_output_destroy(r);
    r=fm_output_create(&s);C(r);C(fm_output_submit(r,v,4));fm_output_stop(r);fm_output_stop(r);
    C(fm_output_closed(r));C(!fm_output_read(r,&s,dst,8)&&dst[0]==0&&dst[7]==0);fm_output_destroy(r);
    printf("BENCH06_R2_RESOURCE_ASSERTIONS=%u PASS\n",n);return 0;
}
