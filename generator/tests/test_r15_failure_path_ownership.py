"""GEN-R15 failure-path ownership audit; source-only CoreAudio, no simulation.

Tests inspect actual source and actual non-emitting Mac Intel executable.
They cannot certify CoreAudio callbacks, OS disposal, or physical safety.
"""
from pathlib import Path
import json
import os
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = (ROOT / "src/acoustic_macos.c").read_text(encoding="utf-8")
RUN = (ROOT / "RUN_GEN_R15_MAC_INTEL.command").read_text(encoding="utf-8")
EM = (ROOT / "src/em_backend.c").read_text(encoding="utf-8")
ENTRY = SRC.split("static __attribute__((unused)) int acoustic_output_impl(", 1)[1].split(
    "int fm_acoustic_native_backend_available(", 1)[0]
PUBLIC = SRC.split("int fm_acoustic_physical_output(", 1)[1]

def segment(first, last):
    return ENTRY.split(first, 1)[1].split(last, 1)[0]

class R15OwnershipFailurePaths(unittest.TestCase):
    def test_prior_quarantine_blocks_before_claim(self):
        a = ENTRY.index("atomic_load_explicit(&fm_context_quarantined,memory_order_acquire)")
        b = ENTRY.index("atomic_flag_test_and_set_explicit(&fm_session_claim,memory_order_acquire)")
        self.assertLess(a, b)

    def test_quarantine_rechecked_after_claim(self):
        claim = ENTRY.index("atomic_flag_test_and_set_explicit(&fm_session_claim,memory_order_acquire)")
        recheck = ENTRY.index("if (atomic_load_explicit(&fm_context_quarantined,memory_order_acquire)) {",claim)
        allocation = ENTRY.index("calloc(1,sizeof(*owner_ctx))",claim)
        self.assertLess(claim,recheck)
        self.assertLess(recheck,allocation)

    def test_quarantine_recheck_releases_unexposed_claim(self):
        part = segment("if (atomic_load_explicit(&fm_context_quarantined,memory_order_acquire)) {",
                       "AcousticContext *owner_ctx=")
        self.assertIn("atomic_flag_clear_explicit(&fm_session_claim,memory_order_release)",part)
        self.assertIn("return -1;",part)

    def test_allocation_failure_releases_claim(self):
        part = segment("if (!owner_ctx) {","AcousticContext *ctx=owner_ctx;")
        self.assertIn("atomic_flag_clear_explicit(&fm_session_claim,memory_order_release)",part)
        self.assertNotIn("AudioQueueNewOutput",part)

    def test_unpublished_invalid_frames_can_be_freed(self):
        part = segment("if (!ctx->total_frames) {","ctx->fade_frames=")
        self.assertIn("free(owner_ctx);",part)
        self.assertIn("atomic_flag_clear_explicit(&fm_session_claim,memory_order_release)",part)

    def test_unpublished_invalid_fade_can_be_freed(self):
        part = segment("if (ctx->fade_frames==0U) {","AudioStreamBasicDescription fmt;")
        self.assertIn("free(owner_ctx);",part)
        self.assertIn("atomic_flag_clear_explicit(&fm_session_claim,memory_order_release)",part)

    def test_failed_queue_creation_quarantines_all_outcomes(self):
        part = segment("if (AudioQueueNewOutput(&fmt,output_callback,ctx,NULL,NULL,0,&ctx->queue)!=noErr) {",
                       "/* Pin by CoreAudio device UID")
        self.assertIn("atomic_store_explicit(&fm_context_quarantined,1,memory_order_release)",part)
        self.assertIn("atomic_store(&ctx->stop_requested,1)",part)
        self.assertNotIn("free(owner_ctx)",part)

    def test_bind_rejection_requires_successful_dispose(self):
        part = segment("if (fm_acoustic_bind_queue_to_route((void *)ctx->queue,&route)!=0) {",
                       "int err=0;")
        self.assertIn("const OSStatus bind_dispose_status=AudioQueueDispose(ctx->queue,true);",part)
        self.assertIn("if (bind_dispose_status==noErr)",part)

    def test_bind_disposal_success_requires_both_counters_zero(self):
        part = segment("if (fm_acoustic_bind_queue_to_route((void *)ctx->queue,&route)!=0) {",
                       "int err=0;")
        self.assertIn("atomic_load_explicit(&ctx->active_output_callbacks,",part)
        self.assertIn("atomic_load_explicit(&ctx->active_property_listeners,",part)
        self.assertIn("memory_order_acquire)==0U",part)
        self.assertIn("free(owner_ctx);",part)

    def test_bind_disposal_ambiguity_keeps_heap(self):
        part = segment("if (fm_acoustic_bind_queue_to_route((void *)ctx->queue,&route)!=0) {",
                       "int err=0;")
        self.assertGreaterEqual(part.count("atomic_store_explicit(&fm_context_quarantined,1,memory_order_release)"),2)
        self.assertIn("if (bind_dispose_status==noErr)",part)

    def test_registration_failure_seals_listener_evidence(self):
        self.assertIn("int listener_registration_uncertain=0;",ENTRY)
        part = segment("if (AudioQueueAddPropertyListener(ctx->queue,kAudioQueueProperty_IsRunning,",
                       "for (int k=0;!err && k<3;k++)")
        self.assertIn("listener_registration_uncertain=1;",part)
        self.assertIn("fm_latch_first_fault(ctx,FM_FAULT_LISTENER_REGISTRATION);",part)

    def test_listener_registration_success_is_tracked(self):
        self.assertIn("else listener_installed=1;",ENTRY)
        self.assertIn("int listener_installed=0;",ENTRY)

    def test_listener_removal_failure_latches_first_fault(self):
        self.assertIn("int listener_remove_failed=0;",ENTRY)
        self.assertIn("listener_remove_failed=1;",ENTRY)
        self.assertIn("fm_latch_first_fault(ctx,FM_FAULT_LISTENER_REMOVAL);",ENTRY)

    def test_listener_removal_precedes_disposal(self):
        a=ENTRY.index("AudioQueueRemovePropertyListener(")
        b=ENTRY.rfind("if (AudioQueueDispose(ctx->queue,true)!=noErr)")
        self.assertLess(a,b)

    def test_failed_dispose_does_not_drop_queue_reference(self):
        part=segment("if (AudioQueueDispose(ctx->queue,true)!=noErr) {",
                     "/* The *successful* synchronous disposal")
        failed=part.split("} else {",1)[0]
        self.assertIn("fm_latch_first_fault(ctx,FM_FAULT_DISPOSAL)",failed)
        self.assertNotIn("ctx->queue=NULL;",failed)

    def test_successful_dispose_releases_queue_reference(self):
        part=segment("if (AudioQueueDispose(ctx->queue,true)!=noErr) {",
                     "/* The *successful* synchronous disposal")
        successful=part.split("} else {",1)[1]
        self.assertIn("atomic_store(&ctx->dispose_confirmed,1);",successful)
        self.assertIn("ctx->queue=NULL;",successful)

    def test_listener_ambiguity_prevents_quiescence_and_free(self):
        part=segment("const int context_quiescent=","if (context_quiescent) {")
        self.assertIn("!listener_registration_uncertain",part)
        self.assertIn("!listener_remove_failed",part)
        self.assertIn("atomic_load(&ctx->dispose_confirmed)",part)

    def test_nonquiescent_context_retained_and_process_poisoned(self):
        part=segment("if (context_quiescent) {","return err?-1:0;")
        failure=part.split("} else {",1)[1]
        self.assertIn("atomic_store_explicit(&fm_context_quarantined,1,memory_order_release)",failure)
        self.assertNotIn("free(owner_ctx)",failure)
        self.assertIn("err=1;",failure)

    def test_output_backend_still_unlinked_and_hard_denied(self):
        self.assertIn("return -1;",PUBLIC)
        self.assertNotIn("acoustic_output_impl(",PUBLIC)
        self.assertIn("return -1;",EM)
        link=RUN.split(' -o "$WORK/freqmed-gen"',1)[1].split("-framework CoreAudio",1)[0]
        self.assertIn("output_hard_denied.c",link)
        self.assertNotIn("acoustic_macos.c",link)
        self.assertIn("R15_NONEMITTING_EXECUTABLE_SYMBOL_AUDIT=PASS",RUN)
        for version in ("R13","R14","R15"):
            self.assertIn("FREQMED_GEN_"+version+"_BINARY",RUN)

    def test_real_mac_executable_denies_emission(self):
        binary=os.environ.get("FREQMED_GEN_R15_BINARY")
        if not binary:
            self.skipTest("Actual Mac Intel native no-output executable needed")
        status=subprocess.run([binary,"status"],capture_output=True,text=True,timeout=5,check=True)
        data=json.loads(status.stdout)
        self.assertEqual("NONE",data["physical_emission"])
        self.assertEqual("NOT_LINKED_HARD_DENIED",data["acoustic_output"])
        self.assertEqual("BLOCKED_NO_QUALIFIED_EM_DEVICE",data["electromagnetic_output"])
        for action in ("emit","arm","play","transmit"):
            result=subprocess.run([binary,action],capture_output=True,text=True,timeout=5)
            self.assertNotEqual(0,result.returncode)
