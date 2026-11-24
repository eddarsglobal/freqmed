/* SPDX-License-Identifier: Apache-2.0 */
#include "acoustic_fault_latch_r61.h"
#include <stdint.h>
int fm_r61_fault_trip(FMR61Fault *f,uint32_t reason) {
 if (!f) return -1;
 if (f->state==FM_R61_FAULT_LATCHED) return 0;
 f->state=FM_R61_FAULT_LATCHED;
 f->reason=(reason>=FM_R61_REASON_OS_UNAVAILABLE &&
            reason<=FM_R61_REASON_CONTROL_INTEGRITY)?reason:FM_R61_REASON_CONTROL_INTEGRITY;
 if (f->fault_sequence<UINT64_MAX) f->fault_sequence++;
 return 1;
}
void fm_r61_fault_stop(FMR61Fault *f) {
 if (!f || f->state==FM_R61_FAULT_LATCHED) return;
 f->state=FM_R61_STOPPED;
 f->reason=FM_R61_REASON_OPERATOR_STOP;
}
int fm_r61_fault_resume_observation(FMR61Fault *f) {
 if (!f) return -1;
 if (f->state!=FM_R61_STOPPED) return 0;
 f->state=FM_R61_CLEAR;f->reason=FM_R61_REASON_NONE;return 1;
}
int fm_r61_fault_ack(FMR61Fault *f,int route_clear,int session_clear,int monitor_live) {
 if (!f) return -1;
 if (f->state!=FM_R61_FAULT_LATCHED || route_clear!=1 ||
     session_clear!=1 || monitor_live!=1) return 0;
 f->state=FM_R61_CLEAR;f->reason=FM_R61_REASON_NONE;return 1;
}
int fm_r61_fault_can_bind(const FMR61Fault *f) {
 return f && f->state==FM_R61_CLEAR ? 1:0;
}
