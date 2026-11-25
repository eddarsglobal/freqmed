/* SPDX-License-Identifier: Apache-2.0 */
#include "event_evidence.h"
#include <stdio.h>
#define C(x) do{if(!(x)){fprintf(stderr,"FAIL %d: %s\n",__LINE__,#x);return 1;}++n;}while(0)
int main(void) {
    unsigned n=0;FMEventLatch l;FMEvent event={0};fm_event_init(&l);
    C(!fm_event_read(&l,&event));
    C(!fm_event_record(&l,1,10));
    C(!fm_event_arm(NULL));
    C(fm_event_arm(&l));
    C(!fm_event_arm(&l));
    C(!fm_event_record(&l,0,11));
    C(!fm_event_record(&l,32,11));
    C(!fm_event_record(NULL,1,11));
    C(fm_event_record(&l,3,12));
    C(!fm_event_record(&l,4,13));
    C(fm_event_read(&l,&event));
    C(event.category==3 && event.ms==12);
    C(!fm_event_read(NULL,&event));
    C(!fm_event_read(&l,NULL));
    C(!fm_event_arm(&l));
    FMEventEvidence e={10,12,14,15,3,1,1,1,1,1,0,1},x=e;
    C(fm_event_evidence_complete(&e));
    C(!fm_event_evidence_complete(NULL));
    x.category=0;C(!fm_event_evidence_complete(&x));
    x=e;x.category=33;C(!fm_event_evidence_complete(&x));
    x=e;x.prepared=0;C(!fm_event_evidence_complete(&x));
    x=e;x.invalidated=0;C(!fm_event_evidence_complete(&x));
    x=e;x.closed=0;C(!fm_event_evidence_complete(&x));
    x=e;x.rediscovered=0;C(!fm_event_evidence_complete(&x));
    x=e;x.stale_rejected=0;C(!fm_event_evidence_complete(&x));
    x=e;x.new_session=1;C(!fm_event_evidence_complete(&x));
    x=e;x.cleanup=0;C(!fm_event_evidence_complete(&x));
    x=e;x.event_ms=9;C(!fm_event_evidence_complete(&x));
    x=e;x.consumed_ms=11;C(!fm_event_evidence_complete(&x));
    x=e;x.rediscovered_ms=13;C(!fm_event_evidence_complete(&x));
    x=e;x.prepared=2;C(!fm_event_evidence_complete(&x));
    printf("GEN_PLATFORM_06_ASSERTIONS=%u PASS\n",n);return 0;
}
