/* SPDX-License-Identifier: Apache-2.0 */
/* GEN-R41: compile-only C11 finite index-ticket and terminal-fault contract.
 * NOT an Apple CoreAudio callback, security capability, or production API.
 * Ticket indices are COPYABLE / FORGEABLE. No output or simulation.
 */
#ifndef FREQMED_R41_INDEX_TICKET_H
#define FREQMED_R41_INDEX_TICKET_H
#define FM41_MAX_LIFETIME_TICKETS 4u
#define FM41_INVALID_SLOT 0u
typedef struct { unsigned slot_id; } FM41TicketRef;
enum {
 FM41_FAULT_CAPACITY=1u, FM41_FAULT_ADMISSION=2u,
 FM41_FAULT_NULL_OWNER=4u, FM41_FAULT_INVALID_HANDLE=8u,
 FM41_FAULT_DUPLICATE_LEAVE=16u, FM41_FAULT_LEAVE_FAILURE=32u,
 FM41_FAULT_REGISTER=64u, FM41_FAULT_SEAL=128u
};
int fm41_register_owner_once(void *owner,void **userdata_out);
int fm41_begin(void *userdata,FM41TicketRef *ticket_out,void **owner_out);
int fm41_complete(FM41TicketRef ticket);
int fm41_seal(void *userdata);
unsigned fm41_fault_snapshot(void);
#endif /* FREQMED_R41_INDEX_TICKET_H */
