/* SPDX-License-Identifier: Apache-2.0 */
#include "digital_signal.h"
#include "session_clock.h"
#include <math.h>
#include <stdio.h>
#include "mac_capture_pinned.inc"
int main(void) {
    FMDigital d;fm_digital_init(&d);
    FMReadinessProfile a={0},b={0},c={0};
    int one=capture(&a),two=capture(&b),three=0;
    uint64_t now=0,token=0;
    double samples[64]={0};
    size_t written=0;
    int prepared=0,checked=0,stopped=0,error=0;
    const char *status="METADATA_NOT_READY";
    if(one&&two&&fm_readiness_assess(&a,&b)==FM_RD_METADATA_ONLY) {
        /* Numerical software test vector only. No audio output or file. */
        FMCommand cmd={FM_ACOUSTIC,1000.0,0.25,1000U};
        if(!fm_session_clock_ms(&now)) error=1;
        else {
            FMDigitalResult r=fm_digital_prepare(&d,&a,&b,&cmd,now,&token);
            if(r==FM_D_OK) {
                prepared=1;three=capture(&c);
                if(!fm_session_clock_ms(&now)) error=1;
                else {
                    r=fm_digital_block(&d,three?&c:NULL,token,now,samples,64,64,&written);
                    if(r==FM_D_OK&&written==64) {
                        checked=1;
                        for(size_t i=0;i<written;i++)
                            if(!isfinite(samples[i])||fabs(samples[i])>0.25)checked=0;
                        if(!checked)error=1;
                        status="MEMORY_VECTOR_CHECKED";
                    } else if(r==FM_D_INVALIDATED)status="PROFILE_INVALIDATED";
                    else if(r==FM_D_EXPIRED)status="SESSION_EXPIRED";
                    else error=1;
                }
                if(d.assembly.recovery.binding.token) {
                    stopped=fm_digital_stop(&d,token)==FM_D_OK;
                    if(!stopped)error=1;
                } else stopped=d.assembly.state==FM_A_OFF;
            } else if(r!=FM_D_REJECTED)error=1;
        }
    }
    int off=d.assembly.guardian.state==FM_OFF &&
        !d.assembly.guardian.physical_output_enabled &&
        !d.assembly.recovery.binding.token;
    if(!off||fm_acoustic_native_backend_available()!=0)error=1;
    if(prepared&&checked&&stopped&&!error)status="PASS_MEMORY_ONLY_NATIVE_PROFILE";
    printf("{\"native_digital\":\"%s\",\"captures_completed\":%d,"
        "\"session_prepared\":%s,\"samples_checked\":%zu,\"bounded_finite\":%s,"
        "\"session_closed\":%s,\"guardian_off\":%s,\"physical_backend_available\":false}\n",
        error?"NATIVE_ERROR":status,one+two+three,prepared?"true":"false",
        checked?written:0,checked?"true":"false",stopped?"true":"false",off?"true":"false");
    return error?2:0;
}
