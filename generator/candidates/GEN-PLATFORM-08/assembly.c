/* SPDX-License-Identifier: Apache-2.0 */
#include "assembly.h"
#include <string.h>
static FMSnapshot snapshot(const FMReadinessProfile *p) {
    FMSnapshot s={0};
    if(p){s.usable=1;s.count=1;s.endpoints[0]=p->endpoint;}
    return s;
}
static void clear(FMAssembly *a,FMAssemblyState state) {
    memset(&a->profile,0,sizeof(a->profile));
    fm_stop(&a->guardian);a->state=state;
}
void fm_assembly_init(FMAssembly *a) {
    if(a){fm_recovery_init(&a->recovery);a->guardian=(FMGuardian){0};clear(a,FM_A_OFF);}
}
void fm_assembly_notify(FMAssembly *a) {if(a)fm_recovery_notify(&a->recovery);}
FMAssemblyResult fm_assembly_prepare(FMAssembly *a,const FMReadinessProfile *first,
    const FMReadinessProfile *second,const FMCommand *cmd,uint64_t now,uint64_t *token) {
    if(!a||!token) return FM_A_REJECTED;
    *token=0;
    if(a->state==FM_A_PREPARED) return FM_A_BUSY;
    if(a->state!=FM_A_OFF||a->recovery.binding.token) return FM_A_ERROR;
    char why[128]={0};
    if(!cmd||cmd->channel!=FM_ACOUSTIC||!fm_validate_command(cmd,why,sizeof(why))||
       fm_readiness_assess(first,second)!=FM_RD_METADATA_ONLY) return FM_A_REJECTED;
    /* No physical output operation; guardian remains OFF. */
    FMSnapshot x=snapshot(first),y=snapshot(second);
    if(fm_recovery_begin(&a->recovery)!=FM_R_OK) {
        clear(a,FM_A_FAULT);return FM_A_ERROR;
    }
    if(fm_recovery_finish(&a->recovery,&x,&y)!=FM_R_OK) return FM_A_REJECTED;
    FMIntegrationRequest req={FM_ACOUSTIC,cmd,NULL,NULL};
    FMRecoveryResult r=fm_recovery_prepare(&a->recovery,&y,&req,now,token);
    if(r!=FM_R_OK) {
        clear(a,r==FM_R_RETRY?FM_A_OFF:FM_A_FAULT);
        return r==FM_R_RETRY?FM_A_REJECTED:FM_A_ERROR;
    }
    a->profile=*second;a->state=FM_A_PREPARED;
    return FM_A_OK;
}
FMAssemblyResult fm_assembly_poll(FMAssembly *a,const FMReadinessProfile *p,uint64_t token,uint64_t now) {
    if(!a) return FM_A_ERROR;
    if(!token||token!=a->recovery.binding.token) return FM_A_STALE;
    if(a->state!=FM_A_PREPARED) return FM_A_ERROR;
    int valid=fm_readiness_assess(&a->profile,p)==FM_RD_METADATA_ONLY;
    FMSnapshot s={0};if(valid)s=snapshot(p);
    FMRecoveryResult r=fm_recovery_poll(&a->recovery,valid?&s:NULL,token,now);
    if(r==FM_R_OK)return FM_A_OK;
    if(r==FM_R_INVALIDATED||r==FM_R_EXPIRED) {
        clear(a,FM_A_OFF);return r==FM_R_INVALIDATED?FM_A_INVALIDATED:FM_A_EXPIRED;
    }
    clear(a,FM_A_FAULT);return FM_A_ERROR;
}
FMAssemblyResult fm_assembly_stop(FMAssembly *a,uint64_t token) {
    if(!a)return FM_A_ERROR;
    if(!token||token!=a->recovery.binding.token)return FM_A_STALE;
    if(fm_recovery_close(&a->recovery,token)!=FM_R_OK) {
        clear(a,FM_A_FAULT);return FM_A_ERROR;
    }
    clear(a,FM_A_OFF);return FM_A_OK;
}
