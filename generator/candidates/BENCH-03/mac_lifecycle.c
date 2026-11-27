/* SPDX-License-Identifier: Apache-2.0 */
/* Real CoreAudio property listeners; no audio IOProc, stream or device start. */
#define _POSIX_C_SOURCE 200809L
#include "bench02_prefix.inc"
#include "lifecycle.h"
#include <stdatomic.h>
#include <time.h>

typedef struct { AudioObjectID id; AudioObjectPropertyAddress address; } Subscription;
static Subscription subscriptions[16];
static size_t count;
static atomic_uint callbacks;
static OSStatus changed(AudioObjectID id, UInt32 n,
                        const AudioObjectPropertyAddress *addresses, void *context) {
    (void)id;(void)n;(void)addresses;(void)context;
    atomic_fetch_add_explicit(&callbacks,1U,memory_order_relaxed);
    return noErr;
}
static int subscribe(AudioObjectID id, AudioObjectPropertySelector selector, AudioObjectPropertyScope scope) {
    AudioObjectPropertyAddress address={selector,scope,kAudioObjectPropertyElementMain};
    if(count>=sizeof(subscriptions)/sizeof(subscriptions[0]))return 0;
    if(AudioObjectAddPropertyListener(id,&address,changed,NULL)!=noErr)return 0;
    subscriptions[count++]=(Subscription){id,address};return 1;
}
static int device(AudioDeviceID id,AudioObjectPropertyScope scope) {
    const AudioObjectPropertySelector global[]={kAudioDevicePropertyDeviceIsAlive,
        kAudioDevicePropertyNominalSampleRate,kAudioDevicePropertyBufferFrameSize,
        kAudioDevicePropertyDeviceIsRunningSomewhere,kAudioDevicePropertyClockDomain};
    for(size_t j=0;j<sizeof(global)/sizeof(global[0]);j++)
        if(!subscribe(id,global[j],kAudioObjectPropertyScopeGlobal))return 0;
    return subscribe(id,kAudioDevicePropertyLatency,scope)&&
           subscribe(id,kAudioDevicePropertySafetyOffset,scope);
}
static size_t unsubscribe_all(void) {
    size_t removed=0;
    while(count){
        Subscription s=subscriptions[--count];
        if(AudioObjectRemovePropertyListener(s.id,&s.address,changed,NULL)==noErr)removed++;
    }
    return removed;
}
static int snapshot(AudioDeviceID in,AudioDeviceID out) {
    AudioDeviceID a=0,b=0;
    return defaults(&a,&b)&&a==in&&b==out&&
           endpoint(out,kAudioDevicePropertyScopeOutput,'O')&&
           endpoint(in,kAudioDevicePropertyScopeInput,'I')&&
           defaults(&a,&b)&&a==in&&b==out;
}
int main(void) {
    AudioDeviceID in=0,out=0; FMBuffers buffers={0};
    int completed=0,reserved=0;size_t registered=0,removed=0,iv=0,ov=0;
    const char *stage="DEFAULT_ENDPOINTS";
    long long inf=-1,outf=-1,irun=-1,orun=-1;
    int inc=-1,outc=-1;
    atomic_init(&callbacks,0U);
    if(!defaults(&in,&out)||!in||!out||in==out)goto cleanup;
    stage="PROPERTY_SUBSCRIPTIONS";
    if(!subscribe(kAudioObjectSystemObject,kAudioHardwarePropertyDefaultInputDevice,kAudioObjectPropertyScopeGlobal)||
       !subscribe(kAudioObjectSystemObject,kAudioHardwarePropertyDefaultOutputDevice,kAudioObjectPropertyScopeGlobal)||
       !device(in,kAudioDevicePropertyScopeInput)||!device(out,kAudioDevicePropertyScopeOutput))goto cleanup;
    stage="FIRST_SNAPSHOT";
    puts("BEGIN_FIRST");
    if(!snapshot(in,out))goto cleanup;
    stage="BUFFER_DIMENSIONS";
    inf=prop(in,kAudioDevicePropertyBufferFrameSize,kAudioObjectPropertyScopeGlobal);
    outf=prop(out,kAudioDevicePropertyBufferFrameSize,kAudioObjectPropertyScopeGlobal);
    inc=channels(in,kAudioDevicePropertyScopeInput);outc=channels(out,kAudioDevicePropertyScopeOutput);
    irun=prop(in,kAudioDevicePropertyDeviceIsRunningSomewhere,kAudioObjectPropertyScopeGlobal);
    orun=prop(out,kAudioDevicePropertyDeviceIsRunningSomewhere,kAudioObjectPropertyScopeGlobal);
    if(inf<=0||inf>16384||outf<=0||outf>16384||inc<=0||inc>64||outc<=0||outc>64)goto cleanup;
    /* Heap allocation is independent of device activity. No device is opened.
       Running/unknown activity still blocks native binding in the verdict. */
    stage="MEMORY_ALLOCATION";
    reserved=fm_reserve(&buffers,(uint32_t)inf,(uint32_t)inc,(uint32_t)outf,(uint32_t)outc);
    if(!reserved)goto cleanup;
    iv=buffers.in_values;ov=buffers.out_values;
    struct timespec duration={0,250000000L};
    stage="OBSERVATION_SLEEP";
    if(nanosleep(&duration,NULL)!=0)goto cleanup;
    stage="SECOND_SNAPSHOT";
    puts("BEGIN_SECOND");
    if(!snapshot(in,out))goto cleanup;
    completed=1;stage="COMPLETE";
cleanup:
    registered=count;removed=unsubscribe_all();
    unsigned observed=atomic_load_explicit(&callbacks,memory_order_relaxed);
    if(observed||!completed||registered!=removed)fm_invalidate(&buffers);
    fm_close(&buffers);
    printf("DIAG\t%s\t%lld\t%d\t%lld\t%d\t%lld\t%lld\n",stage,inf,inc,outf,outc,irun,orun);
    printf("END\t%zu\t%zu\t%u\t%d\t%d\t%zu\t%zu\t%d\n",
        registered,removed,observed,completed,reserved,iv,ov,
        buffers.state==FM_CLOSED&&!buffers.input&&!buffers.output&&!buffers.in_values&&!buffers.out_values);
    return completed&&reserved&&registered==16&&removed==registered?0:2;
}
