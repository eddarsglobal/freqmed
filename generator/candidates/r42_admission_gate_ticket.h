/* SPDX-License-Identifier: Apache-2.0 */
/* FREQMED GEN-R42: isolated admission gate and opaque ticket proposal.
 * Compile only; NEVER link, load, invoke OS callbacks or emit signals.
 * Opaque pointer may be copied/forged if its valid address becomes known.
 * NO security capability or production certification is implied.
 */
#ifndef FREQMED_R42_ADMISSION_GATE_TICKET_H
#define FREQMED_R42_ADMISSION_GATE_TICKET_H

#define FM42_LIFETIME_CAPACITY 4u
typedef struct FM42Ticket FM42Ticket;

enum {
 FM42_FAULT_CAPACITY=1u, FM42_FAULT_ADMISSION=2u,
 FM42_FAULT_NO_OWNER=4u, FM42_FAULT_BAD_TICKET=8u,
 FM42_FAULT_DUPLICATE_EXIT=16u, FM42_FAULT_LEAVE=32u,
 FM42_FAULT_REGISTRATION=64u, FM42_FAULT_SEAL=128u,
 FM42_FAULT_INTERNAL=256u
};

int fm42_register_owner_once(void *owner,void **userdata_out);
int fm42_begin(void *userdata,FM42Ticket **ticket_out,void **owner_out);
int fm42_complete(FM42Ticket *ticket);
int fm42_seal(void *userdata);
unsigned fm42_fault_snapshot(void);

#endif /* FREQMED_R42_ADMISSION_GATE_TICKET_H */
