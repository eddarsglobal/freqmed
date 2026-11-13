/* SPDX-License-Identifier: Apache-2.0 */
/* Physical CoreAudio path — isolated source candidate, NOT LINKED in GEN-R14.
 * Caution: a PCM command does NOT establish emitted sound pressure, safety,
 * acoustic level or calibration. This backend cannot be enabled by changing
 * runtime flags. A separate certified source revision is required.
 */
#include "generator.h"
#include "acoustic_route_guard.h"
#include "acoustic_device_pin.h"

#if defined(__APPLE__)
#include <AudioToolbox/AudioToolbox.h>
#include <CoreFoundation/CoreFoundation.h>
#include <math.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdatomic.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>

/* GEN-R14 keeps this file as a SEPARATE OBJECT for review, never links it
 * into the executable, never loads it and never executes it. Full safety,
 * output-device pinning, and independent hardware interlocks are pending. */
/* Internal diagnostic causes; not measurements, device states or permissions.
 * The first recorded fault wins. This is an unlinked candidate only. */
typedef enum {
  FM_FAULT_NONE=0,
  FM_FAULT_BAD_BUFFER=1,
  FM_FAULT_ENQUEUE=2,
  FM_FAULT_GRACEFUL_STOP=3,
  FM_FAULT_PROPERTY_LISTENER=4,
  FM_FAULT_MONOTONIC_CLOCK=5,
  FM_FAULT_ROUTE_CHANGED=6,
  FM_FAULT_SHUTDOWN=7,
  FM_FAULT_DISPOSAL=8,
  FM_FAULT_OUTPUT_CALLBACK_INFLIGHT=9,
  FM_FAULT_PROPERTY_LISTENER_INFLIGHT=10,
  FM_FAULT_OVERLAPPING_PCM_CALLBACK=11
} FMInternalAcousticFault;

typedef struct {
  AudioQueueRef queue;
  double phase, phase_step, normalized_level;
  uint64_t frames_written, total_frames, fade_frames;
  atomic_int last_frame_enqueued;
  atomic_int failed;
  atomic_int stop_requested;
  atomic_int queue_started;
  atomic_int queue_stopped;
  atomic_int graceful_drain_requested;
  atomic_int shutdown_in_progress;
  atomic_int first_fault_reason;
  /* Diagnostic counters, not sufficient by themselves to prove lifetime safety. */
  atomic_uint active_output_callbacks;
  atomic_uint active_property_listeners;
  atomic_int dispose_confirmed;
  /* Fail closed if two output callbacks attempt to change PCM state at once. */
  atomic_flag pcm_writer_gate;
} AcousticContext;

/* Only one source-only CoreAudio session may exist per process. If disposal
 * cannot establish quiescence, poison this process gate permanently.
 * This is a lifetime precaution, NOT proof of a physical cutoff. */
static atomic_flag fm_session_claim = ATOMIC_FLAG_INIT;
static atomic_int fm_context_quarantined = ATOMIC_VAR_INIT(0);

/* Single-assignment fault evidence, bounded to this invocation only.
 * No identity, hardware readings, or measurements are written to logs. */
static void fm_latch_first_fault(AcousticContext *ctx, FMInternalAcousticFault reason) {
  if (!ctx || reason==FM_FAULT_NONE) return;
  int unset=FM_FAULT_NONE;
  (void)atomic_compare_exchange_strong(&ctx->first_fault_reason,
                                        &unset,(int)reason);
  atomic_store(&ctx->failed,1);
}

/* Actual OS monotonic timer, never a simulated clock or measurement. */
static int fm_read_monotonic_ns(uint64_t *out) {
  if (!out) return -1;
  struct timespec stamp;
  if (clock_gettime(CLOCK_MONOTONIC,&stamp)!=0 ||
      stamp.tv_sec<0 || stamp.tv_nsec<0 ||
      stamp.tv_nsec>=1000000000L) return -1;
  const uint64_t seconds=(uint64_t)stamp.tv_sec;
  if (seconds>(UINT64_MAX-(uint64_t)stamp.tv_nsec)/1000000000ULL) return -1;
  *out=seconds*1000000000ULL+(uint64_t)stamp.tv_nsec;
  return 0;
}

static void fill_audio(AcousticContext *ctx, AudioQueueBufferRef buf) {
  if (!ctx || !buf || !buf->mAudioData ||
      buf->mAudioDataBytesCapacity < (UInt32)sizeof(int16_t) ||
      (buf->mAudioDataBytesCapacity % (UInt32)sizeof(int16_t))!=0U) {
    if (ctx) fm_latch_first_fault(ctx,FM_FAULT_BAD_BUFFER);
    if (ctx) atomic_store(&ctx->failed,1);
    return;
  }
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
    if (AudioQueueEnqueueBuffer(ctx->queue,buf,0,NULL)!=noErr) {
      fm_latch_first_fault(ctx,FM_FAULT_ENQUEUE);
      atomic_store(&ctx->failed,1);
      return; /* Failed enqueue cannot confirm a final queued frame. */
    }
  }
  if (ctx->frames_written >= ctx->total_frames)
    atomic_store(&ctx->last_frame_enqueued,1);
}
/* Apple AudioQueueStop(false) drains queued buffers asynchronously.
 * The previous R7 code stopped immediately on the *enqueue* of the last
 * frame, potentially cutting short actual playback. This callback-based
 * stop path is a SOURCE-ONLY candidate: no R8 runnable links this code.
 */
static void request_graceful_queue_drain(AcousticContext *ctx) {
  if (!atomic_load(&ctx->queue_started) ||
      !atomic_load(&ctx->last_frame_enqueued) ||
      atomic_load(&ctx->stop_requested) || atomic_load(&ctx->failed) ||
      atomic_load(&ctx->shutdown_in_progress) ||
      atomic_load(&ctx->first_fault_reason)!=FM_FAULT_NONE) return;
  int pending=0;
  if (atomic_compare_exchange_strong(&ctx->graceful_drain_requested,&pending,1)) {
    if (AudioQueueStop(ctx->queue,false)!=noErr) {
      fm_latch_first_fault(ctx,FM_FAULT_GRACEFUL_STOP);
      atomic_store(&ctx->failed,1);
    }
  }
}

static void queue_running_listener(void *data, AudioQueueRef queue,
                                   AudioQueuePropertyID property) {
  AcousticContext *ctx=(AcousticContext*)data;
  if (!ctx) return;
  (void)atomic_fetch_add_explicit(&ctx->active_property_listeners,1U,
                                  memory_order_acq_rel);
  if (property!=kAudioQueueProperty_IsRunning) goto listener_exit;
  UInt32 running=1U, n=(UInt32)sizeof(running);
  if (AudioQueueGetProperty(queue,kAudioQueueProperty_IsRunning,
                            &running,&n)!=noErr || n!=sizeof(running)) {
    fm_latch_first_fault(ctx,FM_FAULT_PROPERTY_LISTENER);
    atomic_store(&ctx->failed,1);
    goto listener_exit;
  }
  if (running==0U && atomic_load(&ctx->graceful_drain_requested) &&
      atomic_load(&ctx->queue_started) && !atomic_load(&ctx->failed) &&
      !atomic_load(&ctx->stop_requested) &&
      !atomic_load(&ctx->shutdown_in_progress) &&
      atomic_load(&ctx->first_fault_reason)==FM_FAULT_NONE)
    atomic_store(&ctx->queue_stopped,1);
listener_exit:
  (void)atomic_fetch_sub_explicit(&ctx->active_property_listeners,1U,
                                  memory_order_acq_rel);
}

static void output_callback(void *ptr, AudioQueueRef queue, AudioQueueBufferRef buf) {
  AcousticContext *ctx=(AcousticContext*)ptr;
  (void)queue;
  if (!ctx) return;
  (void)atomic_fetch_add_explicit(&ctx->active_output_callbacks,1U,
                                  memory_order_acq_rel);
  if (!atomic_load(&ctx->stop_requested) && !atomic_load(&ctx->failed) &&
      !atomic_load(&ctx->shutdown_in_progress)) {
    if (atomic_flag_test_and_set_explicit(&ctx->pcm_writer_gate,
                                           memory_order_acquire)) {
      fm_latch_first_fault(ctx,FM_FAULT_OVERLAPPING_PCM_CALLBACK);
    } else {
      if (!atomic_load(&ctx->last_frame_enqueued) &&
          !atomic_load(&ctx->stop_requested) && !atomic_load(&ctx->failed) &&
          !atomic_load(&ctx->shutdown_in_progress)) fill_audio(ctx,buf);
      atomic_flag_clear_explicit(&ctx->pcm_writer_gate,
                                 memory_order_release);
    }
    /* Callback never requests stop: the control loop owns the drain. */
  }
  (void)atomic_fetch_sub_explicit(&ctx->active_output_callbacks,1U,
                                  memory_order_acq_rel);
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
  /* GEN-R14: CoreAudio receives a heap-owned context pointer with
   * explicit member access. No preprocessor aliases, no stack callback
   * userdata, and no automatic retry on uncertain queue disposal.
   * The backend remains compiled only, not linked into executable. */
  if (atomic_load_explicit(&fm_context_quarantined,memory_order_acquire))
    return -1;
  if (atomic_flag_test_and_set_explicit(&fm_session_claim,memory_order_acquire))
    return -1;
  AcousticContext *owner_ctx=(AcousticContext*)calloc(1,sizeof(*owner_ctx));
  if (!owner_ctx) {
    atomic_flag_clear_explicit(&fm_session_claim,memory_order_release);
    return -1;
  }
AcousticContext *ctx=owner_ctx;
  memset(ctx,0,sizeof(*ctx));
  atomic_init(&ctx->last_frame_enqueued,0);
  atomic_init(&ctx->failed,0);
  atomic_init(&ctx->stop_requested,0);
  atomic_init(&ctx->queue_started,0);
  atomic_init(&ctx->queue_stopped,0);
  atomic_init(&ctx->graceful_drain_requested,0);
  atomic_init(&ctx->shutdown_in_progress,0);
  atomic_init(&ctx->first_fault_reason,FM_FAULT_NONE);
  atomic_init(&ctx->active_output_callbacks,0U);
  atomic_init(&ctx->active_property_listeners,0U);
  atomic_init(&ctx->dispose_confirmed,0);
  atomic_flag_clear(&ctx->pcm_writer_gate);
  ctx->phase_step=6.28318530717958647693*request->frequency_hz/sr;
  ctx->normalized_level=request->normalized_level;
  ctx->total_frames=(uint64_t)((sr*(double)request->duration_ms)/1000.0);
  if (!ctx->total_frames) {
    free(owner_ctx);
    atomic_flag_clear_explicit(&fm_session_claim,memory_order_release);
    return -1;
  }
  ctx->fade_frames=(uint64_t)(sr/100.0); /* nominal 10 ms digital ramp */
  if (ctx->fade_frames==0U) {
    free(owner_ctx);
    atomic_flag_clear_explicit(&fm_session_claim,memory_order_release);
    return -1;
  }
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
  if (AudioQueueNewOutput(&fmt,output_callback,ctx,NULL,NULL,0,&ctx->queue)!=noErr) {
    /* Even on a null queue ref, an API error is not an audited callback
     * lifetime guarantee. Retain one heap context; seal the session. */
    atomic_store(&ctx->shutdown_in_progress,1);
    atomic_store(&ctx->stop_requested,1);
    atomic_store_explicit(&fm_context_quarantined,1,memory_order_release);
    return -1;
  }
  /* Pin by CoreAudio device UID and read it back, before any sample is
   * queued. On rejection: dispose queue immediately with no playback. */
  if (fm_acoustic_bind_queue_to_route((void *)ctx->queue,&route)!=0) {
    /* No start: seal callbacks first, dispose synchronously, and never free
     * the context when OS disposal reports an uncertain result. */
    atomic_store(&ctx->shutdown_in_progress,1);
    atomic_store(&ctx->stop_requested,1);
    const OSStatus bind_dispose_status=AudioQueueDispose(ctx->queue,true);
    if (bind_dispose_status==noErr) {
      free(owner_ctx);
      atomic_flag_clear_explicit(&fm_session_claim,memory_order_release);
    } else {
      atomic_store_explicit(&fm_context_quarantined,1,memory_order_release);
    }
    return -1;
  }
  int err=0;
  int listener_installed=0;
  /* Subscribe to running -> stopped transition; queued frames are not
   * considered played merely because they have been enqueued. */
  if (AudioQueueAddPropertyListener(ctx->queue,kAudioQueueProperty_IsRunning,
                                    queue_running_listener,ctx)!=noErr) err=1;
  else listener_installed=1;
  for (int k=0;!err && k<3;k++) {
    AudioQueueBufferRef b=NULL;
    if (AudioQueueAllocateBuffer(ctx->queue,1024U,&b)!=noErr || !b) {err=1;break;}
    fill_audio(ctx,b);
    if (atomic_load(&ctx->failed)) {err=1;break;}
  }
  /* Recheck default output before start; not a physical hardware pin. */
  if (!err && !fm_route_unchanged(&route)) err=1;
  if (!err && AudioQueueStart(ctx->queue,NULL)!=noErr) err=1;
  if (!err) {
    atomic_store(&ctx->queue_started,1);
    uint64_t started_ns=0U;
    if (fm_read_monotonic_ns(&started_ns)!=0) {
      fm_latch_first_fault(ctx,FM_FAULT_MONOTONIC_CLOCK);
      atomic_store(&ctx->failed,1);
      err=1;
    } else {
      const uint64_t max_elapsed_ns=
        ((uint64_t)request->duration_ms+3000ULL)*1000000ULL;
      /* Short runs can enqueue every frame BEFORE AudioQueueStart. */
      request_graceful_queue_drain(ctx);
      unsigned wait_cycles=0;
      const unsigned max_cycles=request->duration_ms/10U+300U;
      while (!atomic_load(&ctx->queue_stopped) &&
             !atomic_load(&ctx->failed) &&
             !atomic_load(&ctx->stop_requested) && wait_cycles<max_cycles) {
        uint64_t now_ns=0U;
        if (fm_read_monotonic_ns(&now_ns)!=0 || now_ns<started_ns ||
            now_ns-started_ns>max_elapsed_ns) {
          fm_latch_first_fault(ctx,FM_FAULT_MONOTONIC_CLOCK);
          atomic_store(&ctx->failed,1);
          err=1;
          break;
        }
        (void)CFRunLoopRunInMode(kCFRunLoopDefaultMode,0.01,false);
        ++wait_cycles;
        if ((wait_cycles%10U)==0U && !fm_route_unchanged(&route)) {
          fm_latch_first_fault(ctx,FM_FAULT_ROUTE_CHANGED);
          atomic_store(&ctx->stop_requested,1);
          err=1;
          break;
        }
        request_graceful_queue_drain(ctx);
      }
      uint64_t finished_ns=0U;
      if (fm_read_monotonic_ns(&finished_ns)!=0 ||
          finished_ns<started_ns ||
          finished_ns-started_ns>max_elapsed_ns) {
        fm_latch_first_fault(ctx,FM_FAULT_MONOTONIC_CLOCK);
        atomic_store(&ctx->failed,1);
        err=1;
      }
      if (atomic_load(&ctx->failed) || atomic_load(&ctx->stop_requested) ||
          wait_cycles>=max_cycles || !atomic_load(&ctx->queue_stopped)) err=1;
    }
  }
  /* GEN-R11: a one-shot barrier closes the drain and callback paths
   * before listener removal and synchronous disposal. This software
   * boundary is NOT an independently certified hardware stop. */
  if (atomic_exchange(&ctx->shutdown_in_progress,1)!=0) {
    fm_latch_first_fault(ctx,FM_FAULT_SHUTDOWN);
    err=1;
  }
  atomic_store(&ctx->stop_requested,1);
  if (ctx->queue) {
    if (err && atomic_load(&ctx->queue_started)) {
      if (AudioQueueStop(ctx->queue,true)!=noErr) err=1;
    }
    if (listener_installed) {
      if (AudioQueueRemovePropertyListener(ctx->queue,
            kAudioQueueProperty_IsRunning,queue_running_listener,ctx)!=noErr)
        err=1;
    }
    if (AudioQueueDispose(ctx->queue,true)!=noErr) {
      fm_latch_first_fault(ctx,FM_FAULT_DISPOSAL);
      err=1;
    } else {
      atomic_store(&ctx->dispose_confirmed,1);
    }
    ctx->queue=NULL;
  }
  /* The *successful* synchronous disposal is an OS API contract. Counters
   * are additional diagnostics, NOT a substitute for that contract. A
   * nonzero count means the heap-owned context cannot be certified
   * as quiescent by this code. No physical output is permitted here. */
  if (atomic_load_explicit(&ctx->active_output_callbacks,
                           memory_order_acquire)!=0U) {
    fm_latch_first_fault(ctx,FM_FAULT_OUTPUT_CALLBACK_INFLIGHT);
    err=1;
  }
  if (atomic_load_explicit(&ctx->active_property_listeners,
                           memory_order_acquire)!=0U) {
    fm_latch_first_fault(ctx,FM_FAULT_PROPERTY_LISTENER_INFLIGHT);
    err=1;
  }
  if (!atomic_load(&ctx->dispose_confirmed)) err=1;
  /* No successful return after a latched first fault or cleanup failure. */
  if (err) fm_latch_first_fault(ctx,FM_FAULT_SHUTDOWN);
  if (atomic_load(&ctx->first_fault_reason)!=FM_FAULT_NONE) err=1;

  /* Free only after verified synchronous disposal AND zero in-flight
   * callbacks/listeners. On any ambiguity retain heap memory until process
   * termination; this intentionally sacrifices one allocation to avoid
   * returning a dangling callback context. The gate stays irreversibly
   * closed and no retry is permitted. */
  const int context_quiescent=
      atomic_load(&ctx->dispose_confirmed) &&
      atomic_load_explicit(&ctx->active_output_callbacks,
                           memory_order_acquire)==0U &&
      atomic_load_explicit(&ctx->active_property_listeners,
                           memory_order_acquire)==0U;
  if (context_quiescent) {
    free(owner_ctx);
    atomic_flag_clear_explicit(&fm_session_claim,memory_order_release);
  } else {
    atomic_store_explicit(&fm_context_quarantined,1,memory_order_release);
    err=1;
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
