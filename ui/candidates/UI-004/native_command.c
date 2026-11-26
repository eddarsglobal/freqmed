/* SPDX-License-Identifier: Apache-2.0 */
#include "digital_signal.h"
#include "session_clock.h"
#include "mac_capture_pinned.inc"
#include <errno.h>
static int integer(const char *s,unsigned max,unsigned *out) {
    if(!s||!*s)return 0;
    unsigned n=0;
    for(;*s;s++){
        if(*s<'0'||*s>'9')return 0;
        unsigned d=(unsigned)(*s-'0');
        if(n>max/10U||(n==max/10U&&d>max%10U))return 0;
        n=n*10U+d;
    }
    if(!n)return 0;
    *out=n;return 1;
}
static int unavailable(const char *reason){
    printf("{\"source\":\"UNAVAILABLE\",\"reason\":\"%s\"}\n",reason);return 0;
}
int main(int argc,char **argv) {
    unsigned hz=0,level=0,ms=0;
    if(argc!=4||!integer(argv[1],22049,&hz)||!integer(argv[2],100,&level)||
       !integer(argv[3],10000,&ms))return unavailable("INVALID_COMMAND");
    FMDigital d;fm_digital_init(&d);
    FMReadinessProfile a={0},b={0},p={0};
    double samples[4096]={0};size_t count=0;uint64_t token=0,now=0;
    FMCommand command={FM_ACOUSTIC,(double)hz,(double)level/100.0,ms};
    if(!capture(&a)||!capture(&b))return unavailable("PROFILE_NOT_READY");
    if(!isfinite(b.endpoint.rate)||b.endpoint.rate<1||b.endpoint.rate>384000||
       floor(b.endpoint.rate)!=b.endpoint.rate||hz>=b.endpoint.rate/2.0)
        return unavailable("INVALID_NATIVE_RATE_OR_NYQUIST");
    if((uint64_t)b.endpoint.rate*ms/1000U<4096U)
        return unavailable("DURATION_TOO_SHORT_FOR_4096_SAMPLES");
    if(!fm_session_clock_ms(&now)||
       fm_digital_prepare(&d,&a,&b,&command,now,&token)!=FM_D_OK)
        return unavailable("PROFILE_NOT_READY");
    FMDigitalResult r=FM_D_ERROR;
    if(capture(&p)&&fm_session_clock_ms(&now))
        r=fm_digital_block(&d,&p,token,now,samples,4096,4096,&count);
    if(d.assembly.recovery.binding.token&&fm_digital_stop(&d,token)!=FM_D_OK)return 2;
    if(d.assembly.guardian.state!=FM_OFF||d.assembly.guardian.physical_output_enabled||
       d.assembly.recovery.binding.token||d.remaining||fm_acoustic_native_backend_available())return 2;
    if(r!=FM_D_OK&&r!=FM_D_DONE)return unavailable("SESSION_NOT_READY");
    if(count!=4096)return 2;
    for(size_t i=0;i<count;i++)
        if(!isfinite(samples[i])||fabs(samples[i])>command.normalized_level)return 2;
    printf("{\"source\":\"FREQMED_NATIVE_C_MEMORY_ONLY\",\"rate_hz\":%.17g,"
        "\"command_hz\":%u,\"digital_level\":%.17g,\"duration_ms\":%u,"
        "\"count\":%zu,\"samples\":[",b.endpoint.rate,hz,command.normalized_level,ms,count);
    for(size_t i=0;i<count;i++)printf("%s%.17g",i?",":"",samples[i]);
    puts("],\"session_closed\":true,\"guardian_off\":true,\"physical_output\":false,\"physical_measurement\":false}");
    return 0;
}
