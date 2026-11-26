/* SPDX-License-Identifier: Apache-2.0 */
#include "integrated_bridge.h"
#include <stdio.h>
#include <string.h>
#define C(x) do{if(!(x)){fprintf(stderr,"FAIL %d: %s\n",__LINE__,#x);return 1;}++n;}while(0)
int main(void) {
    unsigned n=0;FMIntegratedBridge b;fm_bridge_init(&b);
    FMIntegratedPair p={0},q;
    p.output.endpoint=(FMEndpoint){"OUTPUT_TEST",2,48000,FM_ROUTE_BUILT_IN,1};
    p.output.alive_known=p.output.alive=p.output.running_known=p.output.ranges_known=
        p.output.buffer_known=p.output.buffer_range_known=1;
    p.output.range_count=1;p.output.rates[0]=(FMRateRange){48000,48000};
    p.output.buffer_frames=256;p.output.buffer_min=64;p.output.buffer_max=1024;
    p.input=(FMEndpoint){"INPUT_TEST",1,48000,FM_ROUTE_BUILT_IN,1};
    p.input_alive_known=p.input_alive=1;
    FMCommand cmd={FM_ACOUSTIC,1000,0.25,40};
    uint64_t t=0,old=0;
    C(fm_runtime_clean(&b.runtime));
    C(fm_pair_assess(NULL,&p)==FM_PAIR_INCOMPLETE);
    C(fm_pair_assess(&p,&p)==FM_PAIR_METADATA_ONLY);
    q=p;q.input_alive_known=0;C(fm_pair_assess(&p,&q)==FM_PAIR_INCOMPLETE);
    q=p;q.input_alive=0;C(fm_pair_assess(&p,&q)==FM_PAIR_UNSUITABLE);
    q=p;q.input.rate=44100;C(fm_pair_assess(&p,&q)==FM_PAIR_UNSUITABLE);
    q=p;q.input.route=FM_ROUTE_USB;C(fm_pair_assess(&p,&q)==FM_PAIR_UNSUITABLE);
    q=p;q.output.endpoint.route=FM_ROUTE_USB;C(fm_pair_assess(&p,&q)==FM_PAIR_UNSUITABLE);
    q=p;q.input.channels=0;C(fm_pair_assess(&p,&q)==FM_PAIR_UNSUITABLE);
    q=p;strcpy(q.input.uid,"OTHER");C(fm_pair_assess(&p,&q)==FM_PAIR_CHANGED);
    q=p;q.input.channels=2;C(fm_pair_assess(&p,&q)==FM_PAIR_CHANGED);
    q=p;q.output.buffer_frames=512;C(fm_pair_assess(&p,&q)==FM_PAIR_CHANGED);
    C(fm_bridge_start(&b,&p,&q,&cmd,100,&t)==FM_U_REJECTED&&t==0);
    fm_bridge_notify(&b);
    C(fm_bridge_start(&b,&p,&p,&cmd,100,&t)==FM_U_REJECTED);
    C(fm_bridge_start(&b,&p,&p,&cmd,100,&t)==FM_U_OK&&t==1);
    C(fm_bridge_step(&b,&p,t,100,4)==FM_U_OK&&b.runtime.lifecycle.count==4);
    C(fm_bridge_step(&b,&p,t,101,16)==FM_U_TERMINAL&&b.runtime.state==FM_U_COMPLETE);
    C(b.runtime.consumed==1920&&fm_runtime_clean(&b.runtime)&&!b.pair.input.uid[0]);
    old=t;C(fm_bridge_start(&b,&p,&p,&cmd,102,&t)==FM_U_OK&&t==2);
    C(fm_bridge_step(&b,&p,t,102,1)==FM_U_OK);
    fm_bridge_notify(&b);
    C(fm_bridge_step(&b,&p,old,103,1)==FM_U_STALE);
    C(fm_bridge_step(&b,&p,t,103,1)==FM_U_TERMINAL&&b.runtime.state==FM_U_INVALIDATED);
    C(fm_runtime_clean(&b.runtime)&&!b.pair.input.uid[0]);
    C(fm_bridge_start(&b,&p,&p,&cmd,104,&t)==FM_U_OK);
    C(fm_bridge_step(&b,&p,t,104,1)==FM_U_OK);
    q=p;q.input_alive=0;
    C(fm_bridge_step(&b,&q,t,105,1)==FM_U_TERMINAL&&b.runtime.state==FM_U_INVALIDATED);
    C(fm_runtime_clean(&b.runtime));
    C(fm_bridge_start(&b,&p,&p,&cmd,106,&t)==FM_U_OK);
    C(fm_bridge_step(&b,&p,t,106,1)==FM_U_OK);
    C(fm_bridge_stop(&b,old)==FM_U_STALE);
    C(fm_bridge_stop(&b,t)==FM_U_TERMINAL&&b.runtime.state==FM_U_STOPPED);
    C(fm_runtime_clean(&b.runtime)&&!b.pair.input.uid[0]);
    C(fm_acoustic_native_backend_available()==0);
    printf("GEN_PLATFORM_12_ASSERTIONS=%u PASS\n",n);return 0;
}
