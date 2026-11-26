/* SPDX-License-Identifier: Apache-2.0 */
#include "native_format.h"
#include <math.h>
#include <stdio.h>
#define C(x) do{if(!(x)){fprintf(stderr,"FAIL %d: %s\n",__LINE__,#x);return 1;}++n;}while(0)
int main(void){
    unsigned n=0;FMNativeIOProfile a={0},b;
    a.pair.output.endpoint=(FMEndpoint){"OUT_TEST",2,48000,FM_ROUTE_BUILT_IN,1};
    a.pair.output.alive_known=a.pair.output.alive=a.pair.output.running_known=
        a.pair.output.ranges_known=a.pair.output.buffer_known=a.pair.output.buffer_range_known=1;
    a.pair.output.range_count=1;a.pair.output.rates[0]=(FMRateRange){48000,48000};
    a.pair.output.buffer_frames=256;a.pair.output.buffer_min=64;a.pair.output.buffer_max=1024;
    a.pair.input=(FMEndpoint){"IN_TEST",1,48000,FM_ROUTE_BUILT_IN,1};
    a.pair.input_alive_known=a.pair.input_alive=1;
    a.input.count=a.output.count=1;
    FMNativeFormat mono={48000,1,0,4,1,4,1,32,1};
    FMNativeFormat stereo={48000,1,0,8,1,8,2,32,1};
    a.input.streams[0]=(FMStream){1,mono,mono};
    a.output.streams[0]=(FMStream){2,stereo,stereo};
    C(fm_native_assess(NULL,&a)==FM_N_INCOMPLETE);
    C(fm_native_assess(&a,NULL)==FM_N_INCOMPLETE);
    C(fm_native_assess(&a,&a)==FM_N_METADATA_ONLY);
    b=a;b.input.count=0;C(fm_native_assess(&a,&b)==FM_N_INCOMPLETE);
    b=a;b.output.count=17;C(fm_native_assess(&a,&b)==FM_N_UNSUPPORTED);
    b=a;b.input.streams[0].local_id=0;C(fm_native_assess(&a,&b)==FM_N_UNSUPPORTED);
    b=a;b.input.streams[0].local_id=3;C(fm_native_assess(&a,&b)==FM_N_CHANGED);
    b=a;b.input.streams[0].logical.linear_pcm=0;C(fm_native_assess(&a,&b)==FM_N_UNSUPPORTED);
    b=a;b.input.streams[0].physical.linear_pcm=0;C(fm_native_assess(&a,&b)==FM_N_UNSUPPORTED);
    b=a;b.input.streams[0].logical.rate=NAN;C(fm_native_assess(&a,&b)==FM_N_UNSUPPORTED);
    b=a;b.input.streams[0].logical.rate=44100;C(fm_native_assess(&a,&b)==FM_N_UNSUPPORTED);
    b=a;b.input.streams[0].physical.rate=44100;C(fm_native_assess(&a,&b)==FM_N_CHANGED);
    b=a;b.input.streams[0].physical.flags=4;C(fm_native_assess(&a,&b)==FM_N_CHANGED);
    b=a;b.input.streams[0].logical.format_id=0;C(fm_native_assess(&a,&b)==FM_N_UNSUPPORTED);
    b=a;b.input.streams[0].logical.bytes_packet=3;C(fm_native_assess(&a,&b)==FM_N_UNSUPPORTED);
    b=a;b.input.streams[0].logical.frames_packet=0;C(fm_native_assess(&a,&b)==FM_N_UNSUPPORTED);
    b=a;b.input.streams[0].logical.bits=0;C(fm_native_assess(&a,&b)==FM_N_UNSUPPORTED);
    b=a;b.input.streams[0].logical.bits=64;C(fm_native_assess(&a,&b)==FM_N_UNSUPPORTED);
    b=a;b.input.streams[0].logical.channels=2;C(fm_native_assess(&a,&b)==FM_N_UNSUPPORTED);
    b=a;b.output.streams[0].logical.channels=1;C(fm_native_assess(&a,&b)==FM_N_UNSUPPORTED);
    b=a;b.output.count=2;b.output.streams[0].logical=mono;b.output.streams[1]=(FMStream){2,mono,mono};
    C(fm_native_assess(&a,&b)==FM_N_UNSUPPORTED);
    b.output.streams[1].local_id=3;C(fm_native_assess(&b,&b)==FM_N_METADATA_ONLY);
    C(fm_native_assess(&a,&b)==FM_N_CHANGED);
    b=a;b.pair.input_alive=0;C(fm_native_assess(&a,&b)==FM_N_UNSUPPORTED);
    b=a;b.pair.output.buffer_frames=512;C(fm_native_assess(&a,&b)==FM_N_CHANGED);
    C(fm_acoustic_native_backend_available()==0);
    printf("GEN_PLATFORM_13_ASSERTIONS=%u PASS\n",n);return 0;
}
