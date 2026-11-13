"""GEN-R10 static contracts plus a real non-emitting executable witness.
No simulated devices, scientific measurement fixtures, or output.
"""
from pathlib import Path
import json
import os
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = (ROOT / "src/acoustic_macos.c").read_text(encoding="utf-8")
RUN = (ROOT / "RUN_GEN_R10_MAC_INTEL.command").read_text(encoding="utf-8")

class R10FailureRecoveryContracts(unittest.TestCase):
    def test_real_monotonic_clock(self):
        self.assertIn("clock_gettime(CLOCK_MONOTONIC,&stamp)", SRC)
    def test_monotonic_invalid_timestamp_rejected(self):
        self.assertIn("stamp.tv_sec<0 || stamp.tv_nsec<0", SRC)
    def test_monotonic_overflow_rejected(self):
        self.assertIn("UINT64_MAX-(uint64_t)stamp.tv_nsec", SRC)
    def test_monotonic_clock_failure_is_fatal(self):
        self.assertIn("if (fm_read_monotonic_ns(&started_ns)!=0)", SRC)
        self.assertIn("atomic_store(&ctx.failed,1);", SRC)
    def test_deadline_bound_is_from_requested_duration(self):
        self.assertIn("((uint64_t)request->duration_ms+3000ULL)*1000000ULL", SRC)
    def test_deadline_enforced_during_wait(self):
        self.assertIn("now_ns-started_ns>max_elapsed_ns", SRC)
        self.assertIn("now_ns<started_ns", SRC)
    def test_deadline_enforced_after_wait(self):
        self.assertIn("finished_ns-started_ns>max_elapsed_ns", SRC)
        self.assertIn("finished_ns<started_ns", SRC)
    def test_previous_cycle_fallback_preserved(self):
        self.assertIn("const unsigned max_cycles=request->duration_ms/10U+300U", SRC)
        self.assertIn("wait_cycles>=max_cycles", SRC)
    def test_null_buffer_and_data_rejected(self):
        self.assertIn("!ctx || !buf || !buf->mAudioData", SRC)
    def test_small_buffer_rejected(self):
        self.assertIn("buf->mAudioDataBytesCapacity < (UInt32)sizeof(int16_t)", SRC)
    def test_non_aligned_pcm_buffer_rejected(self):
        self.assertIn("(buf->mAudioDataBytesCapacity % (UInt32)sizeof(int16_t))!=0U", SRC)
    def test_enqueue_error_prevents_final_frame_claim(self):
        begin=SRC.index("if (AudioQueueEnqueueBuffer(ctx->queue,buf,0,NULL)!=noErr)")
        failure=SRC.index("return; /* Failed enqueue", begin)
        final=SRC.index("atomic_store(&ctx->last_frame_enqueued,1)", begin)
        self.assertLess(failure, final)
    def test_property_listener_rejects_fault_completion(self):
        self.assertIn("atomic_load(&ctx->queue_started) && !atomic_load(&ctx->failed)", SRC)
        self.assertIn("!atomic_load(&ctx->stop_requested)", SRC)
    def test_callback_never_stops_or_drains(self):
        cb=SRC.split("static void output_callback(",1)[1].split("static __attribute__",1)[0]
        self.assertNotIn("AudioQueueStop(", cb)
        self.assertNotIn("request_graceful_queue_drain(", cb)
    def test_cleanup_removes_listener_then_disposes(self):
        self.assertLess(SRC.index("AudioQueueRemovePropertyListener("), SRC.rfind("AudioQueueDispose(ctx.queue,true)"))
        # R12 preserves synchronous disposal and adds explicit fault evidence.
        self.assertRegex(SRC, r"if \(AudioQueueDispose\(ctx\.queue,true\)!=noErr\) \{\s*"
                              r"fm_latch_first_fault\(&ctx,FM_FAULT_DISPOSAL\);\s*"
                              r"err=1;\s*\} else \{\s*"
                              r"atomic_store\(&ctx\.dispose_confirmed,1\);")
        self.assertIn("if (!atomic_load(&ctx.dispose_confirmed)) err=1;", SRC)
    def test_fault_immediate_stop_retained(self):
        self.assertIn("if (err && atomic_load(&ctx.queue_started))", SRC)
        self.assertIn("AudioQueueStop(ctx.queue,true)", SRC)
    def test_executable_hard_denial_unmodified(self):
        entry=SRC.split("int fm_acoustic_physical_output(",1)[1]
        self.assertIn("return -1;", entry)
        self.assertNotIn("acoustic_output_impl(", entry)
        self.assertIn("return -1;", (ROOT/"src/em_backend.c").read_text())
    def test_no_output_backend_in_linker(self):
        linker=RUN.split(' -o "$WORK/freqmed-gen"',1)[1].split("-framework CoreAudio",1)[0]
        self.assertIn("output_hard_denied.c", linker)
        self.assertNotIn("acoustic_macos.c", linker)
        self.assertIn("R10_NONEMITTING_EXECUTABLE_SYMBOL_AUDIT=PASS", RUN)
    def test_legacy_witnesses_and_no_emit_cli(self):
        for ver in ("R8","R9","R10"):
            self.assertIn("FREQMED_GEN_"+ver+"_BINARY", RUN)
        self.assertIn("selftest|status|probe|em-discover", RUN)
        self.assertIn("R10_UNKNOWN_ACTION_BLOCK", RUN)
    def test_actual_no_output_binary(self):
        binary=os.environ.get("FREQMED_GEN_R10_BINARY")
        if not binary:
            self.skipTest("Actual owner Mac Intel executable required")
        state=subprocess.run([binary,"status"],capture_output=True,text=True,timeout=5,check=True)
        payload=json.loads(state.stdout)
        self.assertEqual("NONE",payload["physical_emission"])
        self.assertEqual("NOT_LINKED_HARD_DENIED",payload["acoustic_output"])
        self.assertEqual("BLOCKED_NO_QUALIFIED_EM_DEVICE",payload["electromagnetic_output"])
        for action in ("emit","arm","play","transmit"):
            p=subprocess.run([binary,action],capture_output=True,text=True,timeout=5)
            self.assertNotEqual(0,p.returncode)
