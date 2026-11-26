/* SPDX-License-Identifier: Apache-2.0 */
#define _POSIX_C_SOURCE 200809L
#include "digital_signal.h"
#include "session_clock.h"
#include "mac_capture_pinned.inc"
#include <inttypes.h>
#include <signal.h>
#include <time.h>
#include <string.h>
static volatile sig_atomic_t stopped=0;
static void stop_signal(int sig){(void)sig;stopped=1;}
static int integer(const char *s,unsigned max,unsigned *out){
    if(!s||!*s)return 0;
    unsigned n=0;
    for(;*s;s++){
        if(*s<'0'||*s>'9')return 0;
        unsigned d=(unsigned)(*s-'0');
        if(n>max/10U||(n==max/10U&&d>max%10U))return 0;
        n=n*10U+d;
    }
    if(!n)return 0;
    *out=n;return 1;
}
static int unavailable(const char *reason){
    printf("{\"state\":\"REJECTED\",\"reason\":\"%s\"}\n",reason);return 0;
}
static int clean(const FMDigital *d){
    return d->assembly.guardian.state==FM_OFF&&!d->assembly.guardian.physical_output_enabled&&
        !d->assembly.recovery.binding.token&&!d->remaining&&!d->phase&&!d->step&&!d->level;
}
static int emit(const char *state,uint64_t total,uint64_t expected,uint64_t seq,
    unsigned hz,unsigned level,unsigned ms,double rate,const double *window,size_t count,int closed){
    printf("{\"state\":\"%s\",\"processed\":%" PRIu64 ",\"expected\":%" PRIu64
        ",\"sequence\":%" PRIu64 ",\"source\":\"FREQMED_NATIVE_C_MEMORY_ONLY\","
        "\"rate_hz\":%.17g,\"command_hz\":%u,\"digital_level\":%.17g,\"duration_ms\":%u,"
        "\"count\":%zu,\"samples\":[",state,total,expected,seq,rate,hz,(double)level/100.0,ms,count);
    for(size_t i=0;i<count;i++)printf("%s%.17g",i?",":"",window[i]);
    printf("],\"session_closed\":%s,\"guardian_off\":true,\"physical_output\":false,"
        "\"physical_measurement\":false}\n",closed?"true":"false");
    return fflush(stdout)==0;
}
int main(int argc,char **argv){
    unsigned hz=0,level=0,ms=0;
    if(argc!=4||!integer(argv[1],22049,&hz)||!integer(argv[2],100,&level)||
       !integer(argv[3],10000,&ms))return unavailable("INVALID_COMMAND");
    if(signal(SIGTERM,stop_signal)==SIG_ERR||signal(SIGINT,stop_signal)==SIG_ERR)return 2;
    FMDigital d;fm_digital_init(&d);
    FMReadinessProfile a={0},b={0},p={0};
    FMCommand cmd={FM_ACOUSTIC,(double)hz,(double)level/100.0,ms};
    uint64_t token=0,now=0,start=0,total=0,seq=0;
    if(!capture(&a)||!capture(&b)||!fm_session_clock_ms(&now))return unavailable("PROFILE_NOT_READY");
    if(stopped)return unavailable("STOP_BEFORE_PREPARE");
    if(fm_digital_prepare(&d,&a,&b,&cmd,now,&token)!=FM_D_OK)return unavailable("PREPARE_REJECTED");
    start=now;uint64_t expected=d.remaining;
    double block[4096]={0},window[4096]={0};size_t count=0;
    const char *state="FAULT";
    while(!stopped&&d.remaining){
        size_t n=0;
        if(!capture(&p)||!fm_session_clock_ms(&now)){state="INVALIDATED";break;}
        FMDigitalResult r=fm_digital_block(&d,&p,token,now,block,4096,4096,&n);
        if(r!=FM_D_OK&&r!=FM_D_DONE){
            state=r==FM_D_EXPIRED?"EXPIRED":r==FM_D_INVALIDATED?"INVALIDATED":"FAULT";break;
        }
        if(!n||n>4096||n>expected-total){state="FAULT";break;}
        int valid=1;
        for(size_t i=0;i<n;i++)if(!isfinite(block[i])||fabs(block[i])>cmd.normalized_level)valid=0;
        if(!valid){state="FAULT";break;}
        if(count+n>4096){
            size_t drop=count+n-4096;
            memmove(window,window+drop,(count-drop)*sizeof(double));count-=drop;
        }
        memcpy(window+count,block,n*sizeof(double));count+=n;total+=n;++seq;
        if(d.assembly.guardian.state!=FM_OFF||d.assembly.guardian.physical_output_enabled||
           fm_acoustic_native_backend_available())break;
        if(r==FM_D_DONE){state=total==expected&&clean(&d)?"COMPLETE":"FAULT";break;}
        if(!emit("RUNNING",total,expected,seq,hz,level,ms,b.endpoint.rate,window,count,0))break;
        /* Bounded display pacing at up to 4x nominal sample time. No realtime audio.
           The existing native session deadline remains authoritative. */
        uint64_t target=start+(total*250U)/(uint64_t)b.endpoint.rate;
        if(fm_session_clock_ms(&now)&&target>now&&!stopped){
            uint64_t delay=target-now;if(delay>25)delay=25;
            struct timespec nap={(time_t)(delay/1000U),(long)(delay%1000U)*1000000L};
            (void)nanosleep(&nap,NULL);
        }
    }
    if(stopped&&strcmp(state,"COMPLETE"))state="STOPPED";
    if(d.assembly.recovery.binding.token&&fm_digital_stop(&d,token)!=FM_D_OK)return 2;
    if(!clean(&d)||fm_acoustic_native_backend_available())return 2;
    if(strcmp(state,"COMPLETE"))count=0;
    return emit(state,total,expected,seq,hz,level,ms,b.endpoint.rate,window,count,1)?0:2;
}
