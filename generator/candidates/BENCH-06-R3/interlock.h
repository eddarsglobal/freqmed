/* SPDX-License-Identifier: Apache-2.0 */
#ifndef FM_BENCH06_R3_INTERLOCK_H
#define FM_BENCH06_R3_INTERLOCK_H
#include <stdint.h>
#include <stdatomic.h>
enum { FM_R3_STOP=1u, FM_R3_CHANGE=2u, FM_R3_CLOCK=4u, FM_R3_TIMEOUT=8u, FM_R3_FAULT=16u };
typedef struct { atomic_uint reasons; uint64_t deadline,last; int prepared; } FMInterlock;
/* Single owner of prepare/poll; asynchronous notify may only set reasons.
 * One lifetime, no reset. No physical permission or device handle. */
int fm_interlock_init(FMInterlock *g,uint64_t now,uint64_t lease_ms);
void fm_interlock_trip(FMInterlock *g,unsigned reason);
unsigned fm_interlock_reasons(const FMInterlock *g);
int fm_interlock_poll(FMInterlock *g,uint64_t now);
int fm_interlock_physical_allowed(const FMInterlock *g);
#endif
