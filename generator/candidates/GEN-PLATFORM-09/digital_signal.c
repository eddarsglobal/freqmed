/* SPDX-License-Identifier: Apache-2.0 */
#include "digital_signal.h"
#include <math.h>
static void clear(FMDigital *d) {d->phase=0;d->step=0;d->level=0;d->remaining=0;}
void fm_digital_init(FMDigital *d) {if(d){fm_assembly_init(&d->assembly);clear(d);}}
void fm_digital_notify(FMDigital *d) {if(d)fm_assembly_notify(&d->assembly);}
static FMDigitalResult mapped(FMAssemblyResult r) {
    switch(r) {
        case FM_A_OK:return FM_D_OK;
        case FM_A_REJECTED:return FM_D_REJECTED;
        case FM_A_BUSY:return FM_D_BUSY;
        case FM_A_STALE:return FM_D_STALE;
        case FM_A_INVALIDATED:return FM_D_INVALIDATED;
        case FM_A_EXPIRED:return FM_D_EXPIRED;
        default:return FM_D_ERROR;
    }
}
FMDigitalResult fm_digital_prepare(FMDigital *d,const FMReadinessProfile *a,
    const FMReadinessProfile *b,const FMCommand *cmd,uint64_t now,uint64_t *token) {
    if(!d||!token)return FM_D_REJECTED;
    *token=0;
    if(d->assembly.state==FM_A_PREPARED)return FM_D_BUSY;
    if(!b||!cmd||cmd->channel!=FM_ACOUSTIC||
        !fm_validate_command(cmd,NULL,0))return FM_D_REJECTED;
    double rate=b->endpoint.rate;
    if(!isfinite(rate)||rate<1||rate>FM_DIGITAL_RATE_MAX||floor(rate)!=rate||
        cmd->frequency_hz>=rate/2)return FM_D_REJECTED;
    double step=cmd->frequency_hz/rate;
    if(step<=0||!isfinite(step))return FM_D_REJECTED;
    uint64_t frames=((uint64_t)rate*cmd->duration_ms)/1000U;
    if(!frames)return FM_D_REJECTED;
    FMDigitalResult r=mapped(fm_assembly_prepare(&d->assembly,a,b,cmd,now,token));
    if(r!=FM_D_OK)return r;
    d->phase=0;d->step=step;d->level=cmd->normalized_level;d->remaining=frames;
    return FM_D_OK;
}
FMDigitalResult fm_digital_stop(FMDigital *d,uint64_t token) {
    if(!d)return FM_D_ERROR;
    FMDigitalResult r=mapped(fm_assembly_stop(&d->assembly,token));
    if(r!=FM_D_STALE)clear(d);
    return r;
}
FMDigitalResult fm_digital_block(FMDigital *d,const FMReadinessProfile *p,uint64_t token,
    uint64_t now,double *out,size_t capacity,size_t requested,size_t *written) {
    if(!written)return FM_D_REJECTED;
    *written=0;
    if(!out||!requested||requested>FM_DIGITAL_BLOCK_MAX||requested>capacity)
        return FM_D_REJECTED;
    for(size_t i=0;i<requested;i++)out[i]=0;
    if(!d)return FM_D_ERROR;
    FMDigitalResult r=mapped(fm_assembly_poll(&d->assembly,p,token,now));
    if(r!=FM_D_OK){if(r!=FM_D_STALE)clear(d);return r;}
    size_t n=requested;
    if(d->remaining<n)n=(size_t)d->remaining;
    for(size_t i=0;i<n;i++) {
        out[i]=d->level*sin(6.283185307179586476925286766559*d->phase);
        d->phase+=d->step;
        if(d->phase>=1.0)d->phase-=1.0;
    }
    d->remaining-=n;
    /* Recheck the logical session and pending notification before publishing
     * the block. A subsequent asynchronous event can still arrive. */
    r=mapped(fm_assembly_poll(&d->assembly,p,token,now));
    if(r!=FM_D_OK) {
        for(size_t i=0;i<requested;i++)out[i]=0;
        clear(d);return r;
    }
    if(!d->remaining) {
        r=fm_digital_stop(d,token);
        if(r!=FM_D_OK) {
            for(size_t i=0;i<requested;i++)out[i]=0;
            return r;
        }
        *written=n;return FM_D_DONE;
    }
    *written=n;return FM_D_OK;
}
