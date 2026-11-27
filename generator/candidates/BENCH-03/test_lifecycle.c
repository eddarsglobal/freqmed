/* SPDX-License-Identifier: Apache-2.0 */
#include "lifecycle.h"
#include <stdio.h>
#define CHECK(x) do{if(!(x)){fprintf(stderr,"FAIL line %d\n",__LINE__);return 1;}n++;}while(0)
int main(void){
    int n=0; FMBuffers b={0};
    CHECK(!fm_reserve(NULL,512,1,512,2));
    CHECK(!fm_reserve(&b,0,1,512,2));
    CHECK(!fm_reserve(&b,16385,1,512,2));
    CHECK(!fm_reserve(&b,512,65,512,2));
    CHECK(!fm_reserve(&b,512,1,0,2));
    CHECK(!fm_reserve(&b,512,1,512,0));
    CHECK(b.state==FM_IDLE&&!b.input&&!b.output);
    CHECK(fm_reserve(&b,512,1,512,2));
    CHECK(b.state==FM_RESERVED&&b.input&&b.output&&b.input!=b.output);
    CHECK(b.in_values==512&&b.out_values==1024);
    CHECK(!fm_reserve(&b,512,1,512,2));
    fm_invalidate(&b);
    CHECK(b.state==FM_INVALIDATED&&!b.input&&!b.output&&!b.in_values&&!b.out_values);
    CHECK(!fm_reserve(&b,512,1,512,2));
    fm_close(&b);fm_close(&b);fm_invalidate(&b);
    CHECK(b.state==FM_CLOSED&&!b.input&&!b.output);
    CHECK(!fm_reserve(&b,512,1,512,2));
    FMBuffers c={0};CHECK(fm_reserve(&c,256,2,1024,2));
    CHECK(c.in_values==512&&c.out_values==2048);fm_close(&c);
    CHECK(c.state==FM_CLOSED&&!c.input&&!c.output&&!c.in_values&&!c.out_values);
    printf("BENCH03_LIFECYCLE_ASSERTIONS=%d PASS\n",n);return 0;
}
