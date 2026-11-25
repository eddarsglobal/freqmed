/* SPDX-License-Identifier: Apache-2.0 */
#ifndef FM_EVENT_EVIDENCE_H
#define FM_EVENT_EVIDENCE_H
#include <stdint.h>
#include <stdatomic.h>
#define FM_EVENT_MASK 31U
typedef struct { unsigned category; uint64_t ms; } FMEvent;
typedef struct { atomic_uint phase; FMEvent first; } FMEventLatch;
/* One arm per process, concurrent producers, one reader. Storage remains live. */
void fm_event_init(FMEventLatch *l);
int fm_event_arm(FMEventLatch *l);
int fm_event_record(FMEventLatch *l,unsigned category,uint64_t ms);
int fm_event_read(const FMEventLatch *l,FMEvent *out);
typedef struct {
    uint64_t prepared_ms,event_ms,consumed_ms,rediscovered_ms;
    unsigned category,prepared,invalidated,closed,rediscovered,stale_rejected,new_session,cleanup;
} FMEventEvidence;
int fm_event_evidence_complete(const FMEventEvidence *e);
#endif
