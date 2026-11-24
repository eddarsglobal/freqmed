/* SPDX-License-Identifier: Apache-2.0 */
#ifndef FM_MONITOR_H
#define FM_MONITOR_H
#include "binding.h"
#include <stdatomic.h>
typedef struct { atomic_uint pending; } FMMonitor;
typedef enum { FM_M_IDLE=0,FM_M_STABLE,FM_M_INVALIDATED,FM_M_EXPIRED,FM_M_ERROR,FM_M_STALE } FMMonitorResult;
/* Notification producers only call mark. Binding is owned by one consumer.
 * Monitor storage must outlive all native callbacks. No physical watchdog. */
void fm_monitor_init(FMMonitor *m);
void fm_monitor_mark(FMMonitor *m);
FMMonitorResult fm_monitor_poll(FMMonitor *m,FMBinding *b,const FMSnapshot *s,uint64_t token,uint64_t now);
#endif
