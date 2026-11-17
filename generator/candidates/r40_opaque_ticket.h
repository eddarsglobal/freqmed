/* SPDX-License-Identifier: Apache-2.0 */
/* FREQMED GEN-R40 — isolated opaque C11 ticket ABI proposal.
 * NEVER link/load/execute on CoreAudio; no OS callbacks or hardware I/O.
 * C type opacity prevents ordinary well-typed clients from stack-allocating,
 * copying by value, or modifying struct fields. It does NOT prevent copies
 * of the POINTER, void* casts, invalid memory operations, or an omitted exit.
 */
#ifndef FREQMED_R40_OPAQUE_TICKET_H
#define FREQMED_R40_OPAQUE_TICKET_H

#define FM40_MAX_TICKETS 4u
typedef struct FM40Ticket FM40Ticket;

int fm40_register_owner_once(void *owner, void **userdata_out);
int fm40_begin(void *userdata, FM40Ticket **ticket_out, void **owner_out);
int fm40_complete(FM40Ticket *ticket);
int fm40_seal(void *userdata);

#endif /* FREQMED_R40_OPAQUE_TICKET_H */
