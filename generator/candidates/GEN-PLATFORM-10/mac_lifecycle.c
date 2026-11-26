/* SPDX-License-Identifier: Apache-2.0 */
#include "buffer_lifecycle.h"
#include "session_clock.h"
#include <stdio.h>
#include "mac_capture_pinned.inc"

static int cleared(const FMLifecycle *l) {
    if(l->head||l->count||l->next_sequence||l->digital.remaining||
       l->digital.assembly.recovery.binding.token)return 0;
    for(unsigned i=0;i<FM_L_SLOTS;i++){
        const FMQueuedBlock *b=&l->queue[i];
        if(b->token||b->sequence||b->count)return 0;
        for(unsigned j=0;j<FM_L_BLOCK;j++)if(b->samples[j]!=0)return 0;
    }
    return 1;
}
int main(void) {
    FMLifecycle l;fm_lifecycle_init(&l);
    FMReadinessProfile a={0},b={0},p={0};
    int captures=capture(&a);
    int second=capture(&b);captures+=second;
    uint64_t now=0,token=0;
    unsigned queued=0,consumed=0;
    int prepared=0,closed=0,stale=0,error=0;
    const char *status="METADATA_NOT_READY";
    if(captures==2&&fm_readiness_assess(&a,&b)==FM_RD_METADATA_ONLY) {
        /* A numerical test vector only. No stream or audio file. */
        FMCommand cmd={FM_ACOUSTIC,1000.0,0.25,5000U};
        if(!fm_session_clock_ms(&now))error=1;
        else {
            FMLifecycleResult r=fm_lifecycle_prepare(&l,&a,&b,&cmd,now,&token);
            if(r==FM_L_OK) {
                prepared=1;status="PARTIAL_LIFECYCLE";
                for(unsigned i=0;i<2;i++) {
                    int got=capture(&p);captures+=got;
                    if(!fm_session_clock_ms(&now)){error=1;break;}
                    r=fm_lifecycle_enqueue(&l,got?&p:NULL,token,now);
                    if(r==FM_L_OK)++queued;
                    else if(r==FM_L_INVALIDATED||r==FM_L_EXPIRED) {
                        status="SESSION_INVALIDATED_OR_EXPIRED";break;
                    } else {error=1;break;}
                }
                if(queued==2&&!error) {
                    int got=capture(&p);captures+=got;
                    FMBlockReceipt receipt={0};
                    if(!fm_session_clock_ms(&now))error=1;
                    else {
                        r=fm_lifecycle_consume(&l,got?&p:NULL,token,now,&receipt);
                        if(r==FM_L_OK&&receipt.sequence==1&&receipt.count==FM_L_BLOCK)
                            consumed=1;
                        else if(r==FM_L_INVALIDATED||r==FM_L_EXPIRED)
                            status="SESSION_INVALIDATED_OR_EXPIRED";
                        else error=1;
                    }
                }
                if(l.digital.assembly.recovery.binding.token) {
                    closed=fm_lifecycle_stop(&l,token)==FM_L_OK;
                    if(!closed)error=1;
                } else closed=l.digital.assembly.state==FM_A_OFF;
                stale=fm_lifecycle_stop(&l,token)==FM_L_STALE;
                if(!stale)error=1;
            } else if(r!=FM_L_REJECTED)error=1;
        }
    }
    int empty=cleared(&l);
    int off=l.digital.assembly.guardian.state==FM_OFF&&
        !l.digital.assembly.guardian.physical_output_enabled;
    int backend=fm_acoustic_native_backend_available();
    if(!empty||!off||backend)error=1;
    if(prepared&&queued==2&&consumed==1&&closed&&stale&&empty&&!error)
        status="PASS_MEMORY_ONLY_LIFECYCLE";
    printf("{\"native_lifecycle\":\"%s\",\"captures_completed\":%d,"
        "\"session_prepared\":%s,\"blocks_enqueued\":%u,\"blocks_consumed\":%u,"
        "\"session_closed\":%s,\"stale_token_rejected\":%s,\"queue_cleared\":%s,"
        "\"guardian_off\":%s,\"physical_backend_available\":%s}\n",
        error?"NATIVE_ERROR":status,captures,prepared?"true":"false",queued,consumed,
        closed?"true":"false",stale?"true":"false",empty?"true":"false",
        off?"true":"false",backend?"true":"false");
    return error?2:0;
}
