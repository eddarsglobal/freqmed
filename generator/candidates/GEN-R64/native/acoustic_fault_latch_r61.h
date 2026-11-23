/* SPDX-License-Identifier: Apache-2.0 */
#ifndef FM_ACOUSTIC_FAULT_LATCH_R61_H
#define FM_ACOUSTIC_FAULT_LATCH_R61_H
#include <stdint.h>
/* Pure state control; NEVER a physical output, emergency cutoff or certification. */
#define FM_R61_CLEAR 0U
#define FM_R61_FAULT_LATCHED 1U
#define FM_R61_STOPPED 2U
#define FM_R61_REASON_NONE 0U
#define FM_R61_REASON_OS_UNAVAILABLE 1U
#define FM_R61_REASON_ROUTE_MISMATCH 2U
#define FM_R61_REASON_NATIVE_SESSION_INVALID 3U
#define FM_R61_REASON_CONTROL_LEASE_EXPIRED 4U
#define FM_R61_REASON_CONTROL_INTEGRITY 5U
#define FM_R61_REASON_OPERATOR_STOP 6U
typedef struct {uint32_t state;uint32_t reason;uint64_t fault_sequence;} FMR61Fault;
/* Fault is sticky even through STOP. Saturated generation cannot wrap. */
int fm_r61_fault_trip(FMR61Fault *f,uint32_t reason);
void fm_r61_fault_stop(FMR61Fault *f);
/* Explicit operator resume may clear STOPPED but NEVER FAULT_LATCHED. */
int fm_r61_fault_resume_observation(FMR61Fault *f);
/* Acknowledgement requires an empty route and session and a live OS monitor.
 * Caller MUST enforce those preconditions using native state and real OS. */
int fm_r61_fault_ack(FMR61Fault *f,int route_clear,int session_clear,int monitor_live);
int fm_r61_fault_can_bind(const FMR61Fault *f);
#endif
