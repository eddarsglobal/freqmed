/* SPDX-License-Identifier: Apache-2.0 */
#include "binding.h"
#include <math.h>
#include <string.h>
static int valid(const FMSnapshot *s) {
    if (!s || s->usable!=1 || s->count>FM_BIND_MAX) return 0;
    unsigned defaults=0;
    for(unsigned i=0;i<s->count;i++) {
        const FMEndpoint *p=&s->endpoints[i];
        if (!p->uid[0] || !memchr(p->uid,0,sizeof(p->uid)) ||
            p->channels<1 || p->channels>256 || !isfinite(p->rate) || p->rate<=0 ||
            (unsigned)p->route>(unsigned)FM_ROUTE_OTHER ||
            (p->is_default!=0 && p->is_default!=1)) return 0;
        defaults+=(unsigned)p->is_default;
        for(unsigned j=0;j<i;j++)
            if (!strcmp(p->uid,s->endpoints[j].uid)) return 0;
    }
    return defaults<=1;
}
FMBResult fm_binding_select(const FMSnapshot *s,unsigned *index) {
    if (!index) return FM_B_INVALID;
    *index=0;
    if (!valid(s)) return FM_B_INVALID;
    for(unsigned i=0;i<s->count;i++) {
        const FMEndpoint *p=&s->endpoints[i];
        if (p->is_default && (p->route==FM_ROUTE_BUILT_IN || p->route==FM_ROUTE_USB)) {
            *index=i; return FM_B_OK;
        }
    }
    return FM_B_NO_CANDIDATE;
}
void fm_binding_init(FMBinding *b) {
    if(b) { memset(b,0,sizeof(*b)); fm_sessions_init(&b->sessions); }
}
FMBResult fm_binding_prepare(FMBinding *b,const FMSnapshot *s,const FMIntegrationRequest *r,uint64_t now,uint64_t *token) {
    if(!b||!r||!token||r->channel!=FM_ACOUSTIC) return FM_B_INVALID;
    if(b->token) return FM_B_BUSY;
    *token=0;
    unsigned index=0;
    FMBResult rc=fm_binding_select(s,&index);
    if(rc!=FM_B_OK) return rc;
    if(fm_session_prepare(&b->sessions,r,now,&b->token)!=FM_S_OK) return FM_B_SESSION_ERROR;
    b->chosen=s->endpoints[index];
    *token=b->token;
    return FM_B_OK;
}
FMBResult fm_binding_refresh(FMBinding *b,const FMSnapshot *s,uint64_t token,uint64_t now) {
    if(!b) return FM_B_INVALID;
    if(!token||token!=b->token) return FM_B_STALE;
    if(b->sessions.acoustic.state!=FM_S_PREPARED) return FM_B_SESSION_ERROR;
    unsigned index=0;
    FMBResult rc=fm_binding_select(s,&index);
    if(rc!=FM_B_OK || strcmp(b->chosen.uid,s->endpoints[index].uid) ||
       b->chosen.channels!=s->endpoints[index].channels ||
       b->chosen.rate!=s->endpoints[index].rate ||
       b->chosen.route!=s->endpoints[index].route) {
        if(fm_session_cancel(&b->sessions,FM_ACOUSTIC,token)!=FM_S_OK) return FM_B_SESSION_ERROR;
        return FM_B_CHANGED;
    }
    return fm_session_tick(&b->sessions,FM_ACOUSTIC,token,now)==FM_S_OK ? FM_B_OK:FM_B_SESSION_ERROR;
}
FMBResult fm_binding_close(FMBinding *b,uint64_t token) {
    if(!b) return FM_B_INVALID;
    if(!token||token!=b->token) return FM_B_STALE;
    if(b->sessions.acoustic.state==FM_S_PREPARED &&
       fm_session_cancel(&b->sessions,FM_ACOUSTIC,token)!=FM_S_OK) return FM_B_SESSION_ERROR;
    if(fm_session_close(&b->sessions,FM_ACOUSTIC,token)!=FM_S_OK) return FM_B_SESSION_ERROR;
    memset(&b->chosen,0,sizeof(b->chosen));
    b->token=0;
    return FM_B_OK;
}
