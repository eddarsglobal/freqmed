/* SPDX-License-Identifier: Apache-2.0 */
/* FREQMED GEN-R43 — ISOLATED, NONEMITTING, COMPILE-ONLY C11 interface.
 * Internal ticket pointers and bound userdata are NOT authentication secrets.
 * No Apple callback integration, simulation, audio or EM output.
 */
#ifndef FREQMED_R43_PUBLICATION_AUTHORITY_H
#define FREQMED_R43_PUBLICATION_AUTHORITY_H

#define FM43_LIFETIME_TICKETS 4u
typedef struct FM43Ticket FM43Ticket;

enum {
 FM43_FAULT_CAPACITY=1u, FM43_FAULT_ADMISSION=2u,
 FM43_FAULT_OWNER_NULL=4u, FM43_FAULT_BAD_TICKET=8u,
 FM43_FAULT_DUPLICATE_EXIT=16u, FM43_FAULT_LEAVE=32u,
 FM43_FAULT_REGISTER=64u, FM43_FAULT_SEAL=128u,
 FM43_FAULT_PUBLISH=256u, FM43_FAULT_TOKEN_MISMATCH=512u
};

int fm43_register_owner_once(void *owner,void **userdata_out);
int fm43_begin(void *userdata,FM43Ticket **ticket_out,void **owner_out);
int fm43_complete(FM43Ticket *ticket,void *expected_userdata);
int fm43_seal(void *userdata);
unsigned fm43_fault_snapshot(void);

#endif /* FREQMED_R43_PUBLICATION_AUTHORITY_H */
