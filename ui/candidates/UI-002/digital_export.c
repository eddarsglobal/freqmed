/* SPDX-License-Identifier: Apache-2.0 */
#include "digital_signal.h"
#include "session_clock.h"
#include "mac_capture_pinned.inc"
int main(void) {
    FMDigital d;fm_digital_init(&d);
    FMReadinessProfile a={0},b={0},p={0};
    double samples[4096]={0};
    size_t count=0;uint64_t token=0,now=0;
    FMCommand command={FM_ACOUSTIC,440.0,0.25,1000};
    if(!capture(&a)||!capture(&b)||!fm_session_clock_ms(&now)||
       fm_digital_prepare(&d,&a,&b,&command,now,&token)!=FM_D_OK) {
        puts("{\"source\":\"UNAVAILABLE\",\"reason\":\"PROFILE_NOT_READY\"}");return 0;
    }
    FMDigitalResult r=FM_D_ERROR;
    if(capture(&p)&&fm_session_clock_ms(&now))
        r=fm_digital_block(&d,&p,token,now,samples,4096,4096,&count);
    if(d.assembly.recovery.binding.token&&fm_digital_stop(&d,token)!=FM_D_OK)return 2;
    if(d.assembly.guardian.state!=FM_OFF||d.assembly.guardian.physical_output_enabled||
       d.assembly.recovery.binding.token||fm_acoustic_native_backend_available())return 2;
    if(r!=FM_D_OK&&r!=FM_D_DONE){
        puts("{\"source\":\"UNAVAILABLE\",\"reason\":\"SESSION_NOT_READY\"}");return 0;
    }
    if(count!=4096)return 2;
    for(size_t i=0;i<count;i++)if(!isfinite(samples[i])||fabs(samples[i])>0.25)return 2;
    printf("{\"source\":\"FREQMED_NATIVE_C_MEMORY_ONLY\",\"rate_hz\":%.17g,"
        "\"command_hz\":440,\"digital_level\":0.25,\"count\":%zu,\"samples\":[",b.endpoint.rate,count);
    for(size_t i=0;i<count;i++)printf("%s%.17g",i?",":"",samples[i]);
    puts("],\"physical_output\":false,\"physical_measurement\":false}");
    return 0;
}
