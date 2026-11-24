/* SPDX-License-Identifier: Apache-2.0 */
#ifndef FM_BINDING_H
#define FM_BINDING_H
#include "session.h"
#define FM_BIND_MAX 32
#define FM_UID_MAX 513
typedef enum {FM_ROUTE_UNKNOWN=0,FM_ROUTE_BUILT_IN,FM_ROUTE_USB,FM_ROUTE_VIRTUAL,FM_ROUTE_OTHER} FMRoute;
typedef struct {
    char uid[FM_UID_MAX]; /* native endpoint identity; never exported */
    unsigned channels;
    double rate;
    FMRoute route;
    int is_default;
} FMEndpoint;
typedef struct { unsigned count; int usable; FMEndpoint endpoints[FM_BIND_MAX]; } FMSnapshot;
typedef struct { FMSessionEngine sessions; FMEndpoint chosen; uint64_t token; } FMBinding;
typedef enum {FM_B_OK=0,FM_B_INVALID,FM_B_NO_CANDIDATE,FM_B_BUSY,FM_B_CHANGED,FM_B_SESSION_ERROR,FM_B_STALE} FMBResult;
/* Serialized callers, no concurrent mutation, process-local state only.
 * All results are software metadata decisions, not output authority. */
void fm_binding_init(FMBinding *b);
FMBResult fm_binding_select(const FMSnapshot *s, unsigned *index);
FMBResult fm_binding_prepare(FMBinding *b,const FMSnapshot *s,const FMIntegrationRequest *r,uint64_t now,uint64_t *token);
FMBResult fm_binding_refresh(FMBinding *b,const FMSnapshot *s,uint64_t token,uint64_t now);
FMBResult fm_binding_close(FMBinding *b,uint64_t token);
#endif
