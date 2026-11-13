"""GEN-R13 — CoreAudio context lifetime and failed-disposal containment.

These are source audits and checks of the actual *non-emitting* executable.
No fake hardware, numerical/physical simulation, synthesized signals, or
physical emission. The isolated CoreAudio output function is NEVER executed.
"""
from pathlib import Path
import json
import os
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = (ROOT / "src/acoustic_macos.c").read_text(encoding="utf-8")
RUN = (ROOT / "RUN_GEN_R13_MAC_INTEL.command").read_text(encoding="utf-8")
ENTRY = SRC.split("static __attribute__((unused)) int acoustic_output_impl(", 1)[1].split(
    "int fm_acoustic_native_backend_available(", 1)[0]
PUBLIC = SRC.split("int fm_acoustic_physical_output(", 1)[1]
EM = (ROOT / "src/em_backend.c").read_text(encoding="utf-8")

class R13ContextContainment(unittest.TestCase):
    def test_callback_context_heap_allocation_not_stack(self):
        self.assertIn("AcousticContext *owner_ctx=(AcousticContext*)calloc(1,sizeof(*owner_ctx));", ENTRY)
        self.assertNotIn("AcousticContext ctx;", ENTRY)

    def test_heap_alias_bounded_to_function(self):
        self.assertIn("#define ctx (*owner_ctx)", ENTRY)
        self.assertIn("#undef ctx", ENTRY)
        self.assertLess(ENTRY.index("#define ctx (*owner_ctx)"),
                        ENTRY.index("#undef ctx"))

    def test_process_quarantine_gate_is_atomic(self):
        self.assertIn("static atomic_int fm_context_quarantined = ATOMIC_VAR_INIT(0);", SRC)
        self.assertIn("atomic_load_explicit(&fm_context_quarantined,memory_order_acquire)", ENTRY)

    def test_session_admission_is_one_shot_atomic(self):
        self.assertIn("static atomic_flag fm_session_claim = ATOMIC_FLAG_INIT;", SRC)
        self.assertIn("atomic_flag_test_and_set_explicit(&fm_session_claim,memory_order_acquire)", ENTRY)

    def test_quarantine_checked_before_claim_and_allocation(self):
        self.assertLess(ENTRY.index("atomic_load_explicit(&fm_context_quarantined,"),
                        ENTRY.index("atomic_flag_test_and_set_explicit(&fm_session_claim"))
        self.assertLess(ENTRY.index("atomic_flag_test_and_set_explicit(&fm_session_claim"),
                        ENTRY.index("calloc(1,sizeof(*owner_ctx))"))

    def test_allocation_failure_releases_unexposed_claim(self):
        p=ENTRY.index("if (!owner_ctx) {")
        chunk=ENTRY[p:ENTRY.index("#define ctx",p)]
        self.assertIn("atomic_flag_clear_explicit(&fm_session_claim,memory_order_release)", chunk)
        self.assertIn("return -1;", chunk)

    def test_invalid_frame_count_cleans_up_before_any_queue(self):
        p=ENTRY.index("if (!ctx.total_frames) {")
        chunk=ENTRY[p:ENTRY.index("ctx.fade_frames=",p)]
        self.assertIn("free(owner_ctx);", chunk)
        self.assertIn("atomic_flag_clear_explicit(&fm_session_claim,memory_order_release)", chunk)

    def test_invalid_fade_count_cleans_up_before_any_queue(self):
        p=ENTRY.index("if (ctx.fade_frames==0U) {")
        chunk=ENTRY[p:ENTRY.index("AudioStreamBasicDescription fmt;",p)]
        self.assertIn("free(owner_ctx);", chunk)
        self.assertIn("atomic_flag_clear_explicit(&fm_session_claim,memory_order_release)", chunk)

    def test_queue_creation_failure_quarantines_even_null_ref(self):
        p=ENTRY.index("if (AudioQueueNewOutput(&fmt,output_callback,&ctx,NULL,NULL,0,&ctx.queue)!=noErr) {")
        chunk=ENTRY[p:ENTRY.index("/* Pin by CoreAudio device UID",p)]
        self.assertIn("atomic_store_explicit(&fm_context_quarantined,1,memory_order_release);",chunk)
        self.assertNotIn("free(owner_ctx);", chunk)

    def test_bind_failure_checks_dispose_result(self):
        p=ENTRY.index("if (fm_acoustic_bind_queue_to_route((void *)ctx.queue,&route)!=0) {")
        chunk=ENTRY[p:ENTRY.index("int err=0;",p)]
        self.assertIn("const OSStatus bind_dispose_status=AudioQueueDispose(ctx.queue,true);",chunk)
        self.assertIn("if (bind_dispose_status==noErr) {",chunk)

    def test_bind_disposal_failure_keeps_context(self):
        p=ENTRY.index("if (fm_acoustic_bind_queue_to_route((void *)ctx.queue,&route)!=0) {")
        chunk=ENTRY[p:ENTRY.index("int err=0;",p)]
        self.assertIn("atomic_store_explicit(&fm_context_quarantined,1,memory_order_release);",chunk)
        self.assertLess(chunk.index("if (bind_dispose_status==noErr)"),
                        chunk.index("atomic_store_explicit(&fm_context_quarantined"))

    def test_bind_disposal_success_releases_context(self):
        p=ENTRY.index("if (fm_acoustic_bind_queue_to_route((void *)ctx.queue,&route)!=0) {")
        chunk=ENTRY[p:ENTRY.index("int err=0;",p)]
        self.assertIn("free(owner_ctx);",chunk)
        self.assertIn("atomic_flag_clear_explicit(&fm_session_claim,memory_order_release);",chunk)

    def test_coreaudio_callback_pointer_is_heap_alias(self):
        self.assertIn("AudioQueueNewOutput(&fmt,output_callback,&ctx,NULL,NULL,0,&ctx.queue)", ENTRY)
        self.assertIn("#define ctx (*owner_ctx)", ENTRY)

    def test_final_dispose_failure_latches_fault(self):
        self.assertIn("if (AudioQueueDispose(ctx.queue,true)!=noErr) {", ENTRY)
        self.assertIn("fm_latch_first_fault(&ctx,FM_FAULT_DISPOSAL);", ENTRY)

    def test_final_dispose_success_confirmation_retained(self):
        self.assertIn("atomic_store(&ctx.dispose_confirmed,1);", ENTRY)
        self.assertIn("if (!atomic_load(&ctx.dispose_confirmed)) err=1;", ENTRY)

    def test_quiescence_checks_two_callback_types(self):
        self.assertIn("const int context_quiescent=", ENTRY)
        self.assertIn("atomic_load_explicit(&ctx.active_output_callbacks,", ENTRY)
        self.assertIn("atomic_load_explicit(&ctx.active_property_listeners,", ENTRY)
        self.assertIn("memory_order_acquire)==0U", ENTRY)

    def test_final_free_requires_quiescence(self):
        p=ENTRY.index("if (context_quiescent) {")
        tail=ENTRY[p:ENTRY.index("return err?-1:0;",p)]
        self.assertIn("free(owner_ctx);",tail)
        self.assertIn("atomic_flag_clear_explicit(&fm_session_claim,memory_order_release)",tail)

    def test_nonquiescent_cleanup_quarantines_without_free(self):
        p=ENTRY.index("if (context_quiescent) {")
        tail=ENTRY[p:ENTRY.index("return err?-1:0;",p)]
        failed=tail.split("} else {",1)[1]
        self.assertIn("atomic_store_explicit(&fm_context_quarantined,1,memory_order_release)", failed)
        self.assertNotIn("free(owner_ctx)",failed)
        self.assertIn("err=1;",failed)

    def test_public_output_and_em_remain_unconditionally_denied(self):
        self.assertIn("return -1;",PUBLIC)
        self.assertNotIn("acoustic_output_impl(", PUBLIC)
        self.assertIn("return -1;",EM)
        link=RUN.split(' -o "$WORK/freqmed-gen"',1)[1].split("-framework CoreAudio",1)[0]
        self.assertIn("output_hard_denied.c",link)
        self.assertNotIn("acoustic_macos.c",link)
        self.assertIn("R13_NONEMITTING_EXECUTABLE_SYMBOL_AUDIT=PASS",RUN)
        for version in ("R11","R12","R13"):
            self.assertIn("FREQMED_GEN_"+version+"_BINARY",RUN)

    def test_actual_native_no_output_executable(self):
        binary=os.environ.get("FREQMED_GEN_R13_BINARY")
        if not binary:
            self.skipTest("Owner Mac Intel native executable required, no synthetic equipment")
        status=subprocess.run([binary,"status"],capture_output=True,text=True,timeout=5,check=True)
        report=json.loads(status.stdout)
        self.assertEqual("NONE",report["physical_emission"])
        self.assertEqual("NOT_LINKED_HARD_DENIED",report["acoustic_output"])
        self.assertEqual("BLOCKED_NO_QUALIFIED_EM_DEVICE",report["electromagnetic_output"])
        for action in ("arm","emit","play","transmit"):
            p=subprocess.run([binary,action],capture_output=True,text=True,timeout=5)
            self.assertNotEqual(0,p.returncode)
