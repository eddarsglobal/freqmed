/* SPDX-License-Identifier: Apache-2.0 */
#include "readiness.h"
#include <math.h>
#include <string.h>
static int flag(unsigned v) {return v<=1;}
static int valid_range(double lo,double hi) {
    return isfinite(lo)&&isfinite(hi)&&lo>0&&lo<=hi;
}
static FMReadinessResult check(const FMReadinessProfile *p) {
    if(!p) return FM_RD_INCOMPLETE;
    if(!flag(p->alive_known)||!flag(p->alive)||!flag(p->running_known)||
       !flag(p->running)||!flag(p->ranges_known)||!flag(p->buffer_known)||
       !flag(p->buffer_range_known)||p->range_count>FM_RATE_CAP)
        return FM_RD_INCONSISTENT;
    if((!p->alive_known&&p->alive)||(!p->running_known&&p->running)||
       (!p->ranges_known&&p->range_count)||(!p->buffer_known&&p->buffer_frames)||
       (!p->buffer_range_known&&(p->buffer_min!=0||p->buffer_max!=0)))
        return FM_RD_INCONSISTENT;
    if(!p->endpoint.uid[0]||!memchr(p->endpoint.uid,0,sizeof(p->endpoint.uid))||
       !isfinite(p->endpoint.rate)||p->endpoint.rate<=0||
       !p->endpoint.channels||p->endpoint.channels>256||
       (unsigned)p->endpoint.route>(unsigned)FM_ROUTE_OTHER||
       (p->endpoint.is_default!=0&&p->endpoint.is_default!=1))
        return FM_RD_INCONSISTENT;
    if(!p->endpoint.is_default||
       (p->endpoint.route!=FM_ROUTE_BUILT_IN&&p->endpoint.route!=FM_ROUTE_USB))
        return FM_RD_NOT_CANDIDATE;
    if(!p->alive_known||!p->running_known||!p->ranges_known||
       !p->buffer_known||!p->buffer_range_known) return FM_RD_INCOMPLETE;
    if(!p->alive) return FM_RD_NOT_CANDIDATE;
    if(!p->range_count||!p->buffer_frames||
       !valid_range(p->buffer_min,p->buffer_max)||
       p->buffer_frames<p->buffer_min||p->buffer_frames>p->buffer_max)
        return FM_RD_INCONSISTENT;
    int contained=0;
    for(unsigned i=0;i<p->range_count;i++) {
        const FMRateRange *r=&p->rates[i];
        if(!valid_range(r->minimum,r->maximum)) return FM_RD_INCONSISTENT;
        if(p->endpoint.rate>=r->minimum&&p->endpoint.rate<=r->maximum) contained=1;
    }
    if(!contained) return FM_RD_INCONSISTENT;
    return p->running?FM_RD_BUSY:FM_RD_METADATA_ONLY;
}
FMReadinessResult fm_readiness_assess(const FMReadinessProfile *a,const FMReadinessProfile *b) {
    FMReadinessResult x=check(a),y=check(b);
    if(x!=FM_RD_METADATA_ONLY) return x;
    if(y!=FM_RD_METADATA_ONLY) return y;
    if(strcmp(a->endpoint.uid,b->endpoint.uid)||a->endpoint.channels!=b->endpoint.channels||
       a->endpoint.rate!=b->endpoint.rate||a->endpoint.route!=b->endpoint.route||
       a->range_count!=b->range_count||a->buffer_frames!=b->buffer_frames||
       a->buffer_min!=b->buffer_min||a->buffer_max!=b->buffer_max)
        return FM_RD_CHANGED;
    /* Compare reported range lists in order, conservatively rejecting reordering. */
    for(unsigned i=0;i<a->range_count;i++)
        if(a->rates[i].minimum!=b->rates[i].minimum||
           a->rates[i].maximum!=b->rates[i].maximum) return FM_RD_CHANGED;
    return FM_RD_METADATA_ONLY;
}
