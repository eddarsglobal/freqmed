/* SPDX-License-Identifier: Apache-2.0 */
/* R60: monotonic, bounded control-plane lease for real OS-verified R59 routes.
 * No waveform creation, audio device opening, output or hardware cutoff. */
#define _POSIX_C_SOURCE 200809L
#include "acoustic_control_lease_r60.h"
#include <time.h>
#include <string.h>
#include <limits.h>

static int monotonic_ns(uint64_t *out) {
  struct timespec t;
  if (!out || clock_gettime(CLOCK_MONOTONIC, &t)!=0 || t.tv_sec<0 ||
      t.tv_nsec<0 || t.tv_nsec>=1000000000L) return 0;
  if ((uint64_t)t.tv_sec > (UINT64_MAX-(uint64_t)t.tv_nsec)/1000000000ULL) return 0;
  *out=(uint64_t)t.tv_sec*1000000000ULL+(uint64_t)t.tv_nsec;
  return 1;
}
static int same_binding(const FMR59Session *a,const FMR59Session *b) {
  if (!a || !b || a->phase!=FM_R59_PHASE_ROUTE_VERIFIED ||
      b->phase!=FM_R59_PHASE_ROUTE_VERIFIED || !a->device_id || !b->device_id ||
      !a->digital_frame_budget || !b->digital_frame_budget ||
      !memchr(a->name,0,FM_R59_DEVICE_NAME_CAP) ||
      !memchr(b->name,0,FM_R59_DEVICE_NAME_CAP)) return 0;
  return a->device_id==b->device_id && a->channels==b->channels &&
    a->sample_rate_hz==b->sample_rate_hz &&
    a->command.channel==b->command.channel &&
    a->command.frequency_hz==b->command.frequency_hz &&
    a->command.normalized_level==b->command.normalized_level &&
    a->command.duration_ms==b->command.duration_ms &&
    a->digital_frame_budget==b->digital_frame_budget &&
    strcmp(a->name,b->name)==0;
}
static void clear_binding(FMR60Lease *lease) {
  memset(&lease->bound,0,sizeof(lease->bound));
  lease->verified_at_ns=0;
  lease->expires_at_ns=0;
}
void fm_r60_lease_revoke(FMR60Lease *lease,uint32_t reason) {
  if (!lease) return;
  clear_binding(lease);
  lease->state=FM_R60_REVOKED;
  lease->reason=(reason>=FM_R60_REASON_NOT_BOUND &&
                reason<=FM_R60_REASON_MONITOR_UNAVAILABLE)?reason:FM_R60_REASON_ROUTE_RESET;
}
void fm_r60_lease_stop(FMR60Lease *lease) {
  if (!lease) return;
  clear_binding(lease);
  lease->state=FM_R60_STOPPED;
  lease->reason=FM_R60_REASON_OPERATOR_STOP;
}
int fm_r60_lease_begin(FMR60Lease *lease,const FMR59Session *current) {
  if (!lease) return -1;
  fm_r60_lease_revoke(lease,FM_R60_REASON_NOT_BOUND);
  if (!current || current->phase!=FM_R59_PHASE_ROUTE_VERIFIED ||
      current->reason!=FM_R59_REASON_NONE || !current->device_id ||
      !current->digital_frame_budget || current->command.channel!=FM_ACOUSTIC ||
      !memchr(current->name,0,FM_R59_DEVICE_NAME_CAP) || !current->name[0] ||
      !fm_validate_command(&current->command,NULL,0)) return 0;
  if (lease->generation==UINT64_MAX) {lease->reason=FM_R60_REASON_SESSION_CHANGED;return 0;}
  uint64_t now=0;
  if (!monotonic_ns(&now) || now>UINT64_MAX-((uint64_t)FM_R60_LEASE_TTL_MS*1000000ULL)) {
    lease->reason=FM_R60_REASON_CLOCK_FAILURE;return 0;
  }
  lease->bound=*current;
  lease->generation++;
  lease->verified_at_ns=now;
  lease->expires_at_ns=now+(uint64_t)FM_R60_LEASE_TTL_MS*1000000ULL;
  lease->state=FM_R60_VALID;
  lease->reason=FM_R60_REASON_NONE;
  return 1;
}
int fm_r60_lease_check(FMR60Lease *lease,const FMR59Session *current) {
  if (!lease) return -1;
  if (lease->state!=FM_R60_VALID) return 0;
  if (!same_binding(&lease->bound,current)) {
    fm_r60_lease_revoke(lease,FM_R60_REASON_SESSION_CHANGED);return 0;
  }
  uint64_t now=0;
  if (!monotonic_ns(&now)) {
    fm_r60_lease_revoke(lease,FM_R60_REASON_CLOCK_FAILURE);return 0;
  }
  if (now<lease->verified_at_ns || now>=lease->expires_at_ns) {
    fm_r60_lease_revoke(lease,FM_R60_REASON_WATCHDOG_STALE);
    lease->state=FM_R60_EXPIRED;
    return 0;
  }
  return 1;
}
int fm_r60_lease_renew(FMR60Lease *lease,const FMR59Session *current) {
  if (!lease) return -1;
  if (fm_r60_lease_check(lease,current)!=1) return 0;
  uint64_t now=0;
  if (!monotonic_ns(&now) || now>UINT64_MAX-((uint64_t)FM_R60_LEASE_TTL_MS*1000000ULL)) {
    fm_r60_lease_revoke(lease,FM_R60_REASON_CLOCK_FAILURE);return 0;
  }
  lease->verified_at_ns=now;
  lease->expires_at_ns=now+(uint64_t)FM_R60_LEASE_TTL_MS*1000000ULL;
  return 1;
}
