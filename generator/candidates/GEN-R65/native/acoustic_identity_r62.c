/* SPDX-License-Identifier: Apache-2.0 */
/* GEN-R62: read-only CoreAudio device UID pin on an actually selected default
 * output. Numeric AudioDeviceID and display name alone are NOT stable identity.
 * This code never generates PCM, calls AudioQueue or starts a device.
 */
#include "acoustic_identity_r62.h"
#include <math.h>
#include <string.h>
#if defined(__APPLE__)
#include <CoreAudio/CoreAudio.h>
#include <CoreFoundation/CoreFoundation.h>
static int read_default_and_uid(uint32_t *out_id,char out_uid[FM_R62_UID_CAP]) {
 AudioDeviceID before=kAudioObjectUnknown,after=kAudioObjectUnknown;
 AudioObjectPropertyAddress def={kAudioHardwarePropertyDefaultOutputDevice,
  kAudioObjectPropertyScopeGlobal,kAudioObjectPropertyElementMain};
 UInt32 bytes=(UInt32)sizeof(before);
 if(AudioObjectGetPropertyData(kAudioObjectSystemObject,&def,0,NULL,&bytes,&before)!=noErr ||
    bytes!=sizeof(before) || before==kAudioObjectUnknown)return 0;
 AudioObjectPropertyAddress uid_key={kAudioDevicePropertyDeviceUID,
  kAudioObjectPropertyScopeGlobal,kAudioObjectPropertyElementMain};
 CFStringRef uid=NULL;
 bytes=(UInt32)sizeof(uid);
 if(AudioObjectGetPropertyData(before,&uid_key,0,NULL,&bytes,&uid)!=noErr ||
    bytes!=sizeof(uid) || !uid)return 0;
 out_uid[0]='\0';
 Boolean converted=CFStringGetCString(uid,out_uid,(CFIndex)FM_R62_UID_CAP,kCFStringEncodingUTF8);
 CFRelease(uid);
 if(!converted || out_uid[0]=='\0') {memset(out_uid,0,FM_R62_UID_CAP);return 0;}
 bytes=(UInt32)sizeof(after);
 if(AudioObjectGetPropertyData(kAudioObjectSystemObject,&def,0,NULL,&bytes,&after)!=noErr ||
    bytes!=sizeof(after) || after!=before) {memset(out_uid,0,FM_R62_UID_CAP);return 0;}
 *out_id=(uint32_t)before;
 return 1;
}
#endif
static void private_clear(FMR62Identity *p) {
 p->device_id=0U; p->channels=0U; p->sample_rate_hz=0.0;
 memset(&p->command,0,sizeof(p->command));
 memset(p->name,0,sizeof(p->name));
 memset(p->os_uid,0,sizeof(p->os_uid));
}
void fm_r62_identity_invalidate(FMR62Identity *p,uint32_t reason) {
 if(!p)return;
 if(p->state==FM_R62_STOPPED || p->state==FM_R62_INVALIDATED)return;
 private_clear(p);
 p->state=FM_R62_INVALIDATED;
 p->reason=(reason>=FM_R62_OS_UNAVAILABLE && reason<=FM_R62_EXPLICIT_RESET)?
  reason:FM_R62_EXPLICIT_RESET;
}
void fm_r62_identity_stop(FMR62Identity *p) {
 if(!p)return;
 private_clear(p);p->state=FM_R62_STOPPED;p->reason=FM_R62_OPERATOR_STOP;
}
int fm_r62_identity_pin(FMR62Identity *p,const FMR59Session *s) {
 if(!p)return -1;
 if(!s || s->phase!=1U || s->device_id==0U || s->channels==0U ||
    !isfinite(s->sample_rate_hz) || s->sample_rate_hz<=0.0 || s->name[0]=='\0' ||
    !memchr(s->name,'\0',sizeof(s->name)) || s->command.channel!=1) {
  private_clear(p);p->state=FM_R62_INVALIDATED;p->reason=FM_R62_SESSION_CHANGED;
  return 0;
 }
#if defined(__APPLE__)
 uint32_t os_id=0U;char uid[FM_R62_UID_CAP]={0};
 if(!read_default_and_uid(&os_id,uid) || os_id!=s->device_id) {
  private_clear(p);p->state=FM_R62_INVALIDATED;
  p->reason=(os_id!=0U)?FM_R62_OS_IDENTITY_CHANGED:FM_R62_OS_UNAVAILABLE;
  memset(uid,0,sizeof(uid));return 0;
 }
 private_clear(p);
 p->device_id=s->device_id;p->channels=s->channels;p->sample_rate_hz=s->sample_rate_hz;
 p->command=s->command;
 memcpy(p->name,s->name,sizeof(p->name));
 memcpy(p->os_uid,uid,sizeof(uid));
 memset(uid,0,sizeof(uid));
 if(p->sequence<UINT64_MAX)p->sequence++;
 p->state=FM_R62_PINNED;p->reason=FM_R62_NONE;
 return 1;
#else
 private_clear(p);p->state=FM_R62_INVALIDATED;p->reason=FM_R62_OS_UNAVAILABLE;
 return 0; /* Never fabricate a CoreAudio device on Linux. */
#endif
}
int fm_r62_identity_check(FMR62Identity *p,const FMR59Session *s) {
 if(!p)return -1;
 if(p->state!=FM_R62_PINNED)return 0;
 if(!s || s->phase!=1U || s->device_id!=p->device_id ||
    s->channels!=p->channels || s->sample_rate_hz!=p->sample_rate_hz ||
    !memchr(s->name,'\0',sizeof(s->name)) || strcmp(s->name,p->name)!=0 ||
    s->command.channel!=p->command.channel ||
    s->command.frequency_hz!=p->command.frequency_hz ||
    s->command.normalized_level!=p->command.normalized_level ||
    s->command.duration_ms!=p->command.duration_ms) {
  fm_r62_identity_invalidate(p,FM_R62_SESSION_CHANGED);return 0;
 }
#if defined(__APPLE__)
 uint32_t id=0U;char uid[FM_R62_UID_CAP]={0};
 if(!read_default_and_uid(&id,uid)) {
  fm_r62_identity_invalidate(p,FM_R62_OS_UNAVAILABLE);return 0;
 }
 int same=(id==p->device_id && strcmp(uid,p->os_uid)==0);
 memset(uid,0,sizeof(uid));
 if(!same) {fm_r62_identity_invalidate(p,FM_R62_OS_IDENTITY_CHANGED);return 0;}
 return 1;
#else
 fm_r62_identity_invalidate(p,FM_R62_OS_UNAVAILABLE);return 0;
#endif
}
