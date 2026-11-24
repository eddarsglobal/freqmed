/* SPDX-License-Identifier: Apache-2.0 */
#include "session_clock.h"
#include "session.h"
#include <stdio.h>
#define C(x) do { if (!(x)) {fprintf(stderr,"FAIL %d: %s\n",__LINE__,#x); return 1;} ++n; } while(0)
int main(void) {
    unsigned n=0;
    uint64_t a=0,b=0,token=0;
    C(!fm_session_clock_ms(NULL));
    C(fm_session_clock_ms(&a));
    C(fm_session_clock_ms(&b));
    C(b>=a);
    FMSessionEngine e; fm_sessions_init(&e);
    FMCommand ac={FM_ACOUSTIC,1.0,0.5,10};
    FMIntegrationRequest r={FM_ACOUSTIC,&ac,NULL,NULL};
    C(fm_session_prepare(&e,&r,b,&token)==FM_S_OK);
    C(fm_session_clock_ms(&a) && a>=b);
    C(fm_session_tick(&e,FM_ACOUSTIC,token,a)==FM_S_OK);
    C(e.acoustic.state==FM_S_PREPARED || e.acoustic.state==FM_S_EXPIRED);
    if (e.acoustic.state==FM_S_PREPARED) {
        if (fm_session_cancel(&e,FM_ACOUSTIC,token)!=FM_S_OK) return 1;
    }
    C(fm_session_close(&e,FM_ACOUSTIC,token)==FM_S_OK);
    printf("GEN_INTEGRATION_02_CLOCK_ASSERTIONS=%u PASS\n",n);
    return 0;
}
