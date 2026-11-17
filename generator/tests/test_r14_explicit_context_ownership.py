"""GEN-R14 explicit heap context owner contracts; NO simulated hardware, NO physical emission.
These source assertions and actual no-output CLI checks do not certify active CoreAudio.
"""
from pathlib import Path
import json
import os
import subprocess
import unittest

ROOT=Path(__file__).resolve().parents[1]
SRC=(ROOT/'src/acoustic_macos.c').read_text(encoding='utf-8')
RUN=(ROOT/'RUN_GEN_R14_MAC_INTEL.command').read_text(encoding='utf-8')
ENTRY=SRC.split('static __attribute__((unused)) int acoustic_output_impl(')[1].split('int fm_acoustic_native_backend_available(')[0]
PUBLIC=SRC.split('int fm_acoustic_physical_output(')[1]
EM=(ROOT/'src/em_backend.c').read_text(encoding='utf-8')

class R14ExplicitContextOwnership(unittest.TestCase):
    def test_no_alias(self):
        self.assertNotIn('#define ctx', SRC); self.assertNotIn('#undef ctx', SRC)

    def test_explicit_heap_pointer(self):
        self.assertIn('AcousticContext *owner_ctx=(AcousticContext*)calloc(1,sizeof(*owner_ctx));', ENTRY); self.assertIn('AcousticContext *ctx=owner_ctx;', ENTRY)

    def test_no_stack_callback(self):
        self.assertNotIn('AcousticContext ctx;', ENTRY); self.assertNotIn('AudioQueueNewOutput(&fmt,output_callback,&ctx', ENTRY)

    def test_pointer_memset(self):
        self.assertIn('memset(ctx,0,sizeof(*ctx));', ENTRY); self.assertNotIn('memset(&ctx,0,sizeof(ctx));', ENTRY)

    def test_atomic_member_initialization(self):
        [self.assertIn('atomic_init(&ctx->'+name+',',ENTRY) for name in ('failed','queue_started','queue_stopped','shutdown_in_progress','first_fault_reason','active_output_callbacks','active_property_listeners','dispose_confirmed')]

    def test_exclusive_session_claim(self):
        self.assertLess(ENTRY.index('atomic_flag_test_and_set_explicit(&fm_session_claim'),ENTRY.index('calloc(1,sizeof(*owner_ctx))'))

    def test_allocation_failure(self):
        self.assertIn('atomic_flag_clear_explicit(&fm_session_claim,memory_order_release)', ENTRY.split('if (!owner_ctx) {',1)[1].split('AcousticContext *ctx=owner_ctx;',1)[0])

    def test_invalid_frame_cleanup(self):
        part=ENTRY.split('if (!ctx->total_frames) {',1)[1].split('ctx->fade_frames=',1)[0]
        self.assertIn('free(owner_ctx);',part); self.assertIn('atomic_flag_clear_explicit(&fm_session_claim',part)

    def test_invalid_fade_cleanup(self):
        part=ENTRY.split('if (ctx->fade_frames==0U) {',1)[1].split('AudioStreamBasicDescription fmt;',1)[0]
        self.assertIn('free(owner_ctx);',part); self.assertIn('atomic_flag_clear_explicit(&fm_session_claim',part)

    def test_queue_creation_userdata(self):
        self.assertIn('AudioQueueNewOutput(&fmt,output_callback,ctx,NULL,NULL,0,&ctx->queue)',ENTRY)

    def test_creation_failure_quarantine(self):
        part=ENTRY.split('if (AudioQueueNewOutput(&fmt,output_callback,ctx,NULL,NULL,0,&ctx->queue)!=noErr) {',1)[1].split('/* Pin by CoreAudio device UID',1)[0]
        self.assertIn('atomic_store(&ctx->shutdown_in_progress,1)',part); self.assertIn('atomic_store_explicit(&fm_context_quarantined,1,memory_order_release)',part); self.assertNotIn('free(owner_ctx)',part)

    def test_route_bind_pointer(self):
        self.assertIn('fm_acoustic_bind_queue_to_route((void *)ctx->queue,&route)',ENTRY)

    def test_route_reject_dispose(self):
        part=ENTRY.split('if (fm_acoustic_bind_queue_to_route((void *)ctx->queue,&route)!=0) {',1)[1].split('int err=0;',1)[0]
        self.assertIn('const OSStatus bind_dispose_status=AudioQueueDispose(ctx->queue,true);',part); self.assertIn('if (bind_dispose_status==noErr)',part)

    def test_route_reject_quarantine(self):
        part=ENTRY.split('if (fm_acoustic_bind_queue_to_route((void *)ctx->queue,&route)!=0) {',1)[1].split('int err=0;',1)[0].split('} else {',1)[1]
        self.assertIn('atomic_store_explicit(&fm_context_quarantined,1,memory_order_release)',part); self.assertNotIn('free(owner_ctx)',part)

    def test_listener_userdata(self):
        self.assertIn('kAudioQueueProperty_IsRunning,queue_running_listener,ctx)!=noErr',ENTRY)

    def test_buffer_and_drain(self):
        self.assertIn('fill_audio(ctx,b);',ENTRY); self.assertIn('request_graceful_queue_drain(ctx);',ENTRY)

    def test_shutdown_before_dispose(self):
        b=ENTRY.index('if (atomic_exchange(&ctx->shutdown_in_progress,1)!=0)'); x=ENTRY.index('atomic_store(&ctx->stop_requested,1);',b); l=ENTRY.index('AudioQueueRemovePropertyListener(',x); d=ENTRY.rfind('if (AudioQueueDispose(ctx->queue,true)!=noErr)')
        self.assertTrue(b<x<l<d)

    def test_quiescence_before_free(self):
        self.assertIn('const int context_quiescent=',ENTRY); self.assertIn('atomic_load_explicit(&ctx->active_output_callbacks,',ENTRY); self.assertIn('atomic_load_explicit(&ctx->active_property_listeners,',ENTRY); self.assertIn('if (context_quiescent) {\n    free(owner_ctx);',ENTRY)

    def test_fail_closed_output_linkage(self):
        self.assertIn('return -1;',PUBLIC); self.assertNotIn('acoustic_output_impl(',PUBLIC); self.assertIn('return -1;',EM); link=RUN.split(' -o "$WORK/freqmed-gen"',1)[1].split('-framework CoreAudio',1)[0]
        self.assertIn('output_hard_denied.c',link); self.assertNotIn('acoustic_macos.c',link); self.assertIn('R14_NONEMITTING_EXECUTABLE_SYMBOL_AUDIT=PASS',RUN)

    def test_native_no_output_status(self):
        binary=os.environ.get('FREQMED_GEN_R14_BINARY')
        if not binary: self.skipTest('Owner Mac Intel native non-emitting executable required')
        p=subprocess.run([binary,'status'],capture_output=True,text=True,timeout=5,check=True)
        o=json.loads(p.stdout)
        self.assertEqual('NONE',o['physical_emission']); self.assertEqual('NOT_LINKED_HARD_DENIED',o['acoustic_output']); self.assertEqual('BLOCKED_NO_QUALIFIED_EM_DEVICE',o['electromagnetic_output'])
        for action in ('arm','emit','play','transmit'):
            result=subprocess.run([binary,action],capture_output=True,text=True,timeout=5)
            self.assertNotEqual(result.returncode,0)

