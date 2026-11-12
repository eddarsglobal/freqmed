/* SPDX-License-Identifier: Apache-2.0 */
/* Physical CoreAudio path — isolated source candidate, NOT LINKED in GEN-R3.
 * Caution: a PCM command does NOT establish emitted sound pressure, safety,
 * acoustic level or calibration. This backend cannot be enabled by changing
 * runtime flags. A separate certified source revision is required.
 */
#include "generator.h"
#include "acoustic_route_guard.h"

#if defined(__APPLE__)
#include <AudioToolbox/AudioToolbox.h>
#include <CoreFoundation/CoreFoundation.h>
#include <math.h>
#include <stdint.h>
#include <stdatomic.h>
#include <stdbool.h>
#include <string.h>

/* GEN-R3 compiles this file to a SEPARATE OBJECT for review, never links it
 * into the executable, never loads it and never executes it. Full safety,
 * output-device pinning, and independent hardware interlocks are pending. */
typedef struct {
  AudioQueueRef queue;
  double phase, phase_step, normalized_level;
  uint64_t frames_written, total_frames, fade_frames;
  atomic_int last_frame_enqueued;
  atomic_int failed;
  atomic_int stop_requested;
} AcousticContext;

static void fill_audio(AcousticContext *ctx, AudioQueueBufferRef buf) {
  const uint32_t cap=(uint32_t)(buf->mAudioDataBytesCapacity / sizeof(int16_t));
  int16_t *p=(int16_t*)buf->mAudioData;
  uint32_t count=0;
  while (count<cap && ctx->frames_written<ctx->total_frames) {
    /* Smooth edges reduce digital clicks; not an acoustic safety guarantee. */
    const uint64_t at=ctx->frames_written;
    const uint64_t remaining=ctx->total_frames-at;
    double envelope=1.0;
    if (at<ctx->fade_frames) envelope=(double)at/(double)ctx->fade_frames;
    if (remaining<ctx->fade_frames &&
        (double)remaining/(double)ctx->fade_frames<envelope)
      envelope=(double)remaining/(double)ctx->fade_frames;
    const double value=sin(ctx->phase)*ctx->normalized_level*envelope;
    p[count]=(int16_t)(value*32767.0);
    ctx->phase+=ctx->phase_step;
    if (ctx->phase >= 6.28318530717958647693)
      ctx->phase-=6.28318530717958647693;
    ++count; ++ctx->frames_written;
  }
  buf->mAudioDataByteSize=count*(uint32_t)sizeof(int16_t);
  if (count>0) {
    if (AudioQueueEnqueueBuffer(ctx->queue,buf,0,NULL)!=noErr)
      atomic_store(&ctx->failed,1);
  }
  if (ctx->frames_written >= ctx->total_frames)
    atomic_store(&ctx->last_frame_enqueued,1);
}
static void output_callback(void *ptr, AudioQueueRef queue, AudioQueueBufferRef buf) {
  AcousticContext *ctx=(AcousticContext*)ptr;
  (void)queue;
  if (!atomic_load(&ctx->stop_requested) &&
      !atomic_load(&ctx->failed) && !atomic_load(&ctx->last_frame_enqueued))
    fill_audio(ctx,buf);
}
static __attribute__((unused)) int acoustic_output_impl(const FMCommand *request) {
  if (!request || request->channel!=FM_ACOUSTIC) return -1;
  /* Prevent hard-coded 48 kHz PCM on a 44.1 kHz default output, as observed
   * by the owner Mac in GEN-R2. This is only a preflight OS metadata value;
   * it is NOT a proof of physical output frequency or device pinning. */
  FMRouteFingerprint route={0};
  if (fm_route_capture(&route)!=0 || route.output_channels==0 ||
      !isfinite(route.nominal_sample_rate_hz) ||
      route.nominal_sample_rate_hz<8000.0 ||
      route.nominal_sample_rate_hz>384000.0) return -1;
  if (!fm_route_unchanged(&route)) return -1;
  const double sr=route.nominal_sample_rate_hz;
  /* Technical format constraints, not biological safety limits. */
  if (!isfinite(request->frequency_hz) || request->frequency_hz<=0.0 || request->frequency_hz>=sr/2.0 ||
      !isfinite(request->normalized_level) || request->normalized_level<=0.0 || request->normalized_level>1.0 ||
      request->duration_ms==0U || request->duration_ms>60000U) return -1;
  AcousticContext ctx;
  memset(&ctx,0,sizeof(ctx));
  atomic_init(&ctx.last_frame_enqueued,0);
  atomic_init(&ctx.failed,0);
  atomic_init(&ctx.stop_requested,0);
  ctx.phase_step=6.28318530717958647693*request->frequency_hz/sr;
  ctx.normalized_level=request->normalized_level;
  ctx.total_frames=(uint64_t)((sr*(double)request->duration_ms)/1000.0);
  if (!ctx.total_frames) return -1;
  ctx.fade_frames=(uint64_t)(sr/100.0); /* nominal 10 ms digital ramp */
  if (ctx.fade_frames==0U) return -1;
  AudioStreamBasicDescription fmt;
  memset(&fmt,0,sizeof(fmt));
  fmt.mSampleRate=sr;
  fmt.mFormatID=kAudioFormatLinearPCM;
  fmt.mFormatFlags=kLinearPCMFormatFlagIsSignedInteger|kLinearPCMFormatFlagIsPacked;
  fmt.mChannelsPerFrame=1;
  fmt.mFramesPerPacket=1;
  fmt.mBitsPerChannel=16;
  fmt.mBytesPerFrame=2;
  fmt.mBytesPerPacket=2;
  if (AudioQueueNewOutput(&fmt,output_callback,&ctx,NULL,NULL,0,&ctx.queue)!=noErr) return -1;
  int err=0;
  for (int k=0;k<3;k++) {
    AudioQueueBufferRef b=NULL;
    if (AudioQueueAllocateBuffer(ctx.queue,1024U,&b)!=noErr || !b) {err=1;break;}
    fill_audio(&ctx,b);
    if (atomic_load(&ctx.failed)) {err=1;break;}
  }
  /* Recheck default output before start; not a physical hardware pin. */
  if (!err && !fm_route_unchanged(&route)) err=1;
  if (!err && AudioQueueStart(ctx.queue,NULL)!=noErr) err=1;
  if (!err) {
    /* A bounded watchdog; AudioQueueStop(..., false) drains the queue. */
    unsigned wait_cycles=0;
    const unsigned max_cycles=request->duration_ms/10U+300U;
    while (!atomic_load(&ctx.last_frame_enqueued) &&
           !atomic_load(&ctx.failed) &&
           !atomic_load(&ctx.stop_requested) && wait_cycles<max_cycles) {
      (void)CFRunLoopRunInMode(kCFRunLoopDefaultMode,0.01,false);
      ++wait_cycles;
      /* Read-only drift check at intervals; never a safety certification. */
      if ((wait_cycles%10U)==0U && !fm_route_unchanged(&route)) {
        atomic_store(&ctx.stop_requested,1);
        err=1;
        break;
      }
    }
    if (atomic_load(&ctx.failed) || atomic_load(&ctx.stop_requested) ||
        wait_cycles>=max_cycles) err=1;
  }
  /* Immediate stop: never drain queued output after route drift/fault. */
  atomic_store(&ctx.stop_requested,1);
  if (ctx.queue) {
    (void)AudioQueueStop(ctx.queue,true);
    (void)AudioQueueDispose(ctx.queue,true);
  }
  return err?-1:0;
}
int fm_acoustic_native_backend_available(void) { return 1; }
#else
int fm_acoustic_native_backend_available(void) { return 0; }
#endif

int fm_acoustic_physical_output(const FMCommand *command) {
  /* GEN-R3: unconditional hard denial, even if a caller forges all
   * guardian flags. acoustic_output_impl is never called. */
  (void)command;
  return -1;
}
