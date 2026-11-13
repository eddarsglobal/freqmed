"""GEN-R11 code-contract and actual no-output executable tests.
No audio/EM hardware testing, invented device, or physical simulation.
"""
from pathlib import Path
import json
import os
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = (ROOT / "src/acoustic_macos.c").read_text(encoding="utf-8")
RUN = (ROOT / "RUN_GEN_R11_MAC_INTEL.command").read_text(encoding="utf-8")
EM_ABI = (ROOT / "src/em_instrument_driver_abi.h").read_text(encoding="utf-8")

class R11ShutdownIntegrity(unittest.TestCase):
    def test_fault_reasons_are_internal_not_physical_evidence(self):
        self.assertIn("FM_FAULT_BAD_BUFFER=1", SRC)
        self.assertIn("FM_FAULT_ROUTE_CHANGED=6", SRC)
        self.assertIn("FM_FAULT_SHUTDOWN=7", SRC)

    def test_first_fault_reason_is_atomic(self):
        self.assertIn("atomic_int first_fault_reason;", SRC)
        self.assertIn("atomic_init(&ctx.first_fault_reason,FM_FAULT_NONE)", SRC)

    def test_first_fault_wins_cas(self):
        self.assertIn("atomic_compare_exchange_strong(&ctx->first_fault_reason,", SRC)
        self.assertIn("&unset,(int)reason", SRC)

    def test_fault_latch_closes_success_path(self):
        self.assertIn("atomic_store(&ctx->failed,1);", SRC)
        self.assertIn("if (atomic_load(&ctx.first_fault_reason)!=FM_FAULT_NONE) err=1;", SRC)

    def test_bad_pcm_buffer_latches_fault(self):
        self.assertIn("fm_latch_first_fault(ctx,FM_FAULT_BAD_BUFFER)", SRC)

    def test_enqueue_failure_latches_fault(self):
        self.assertIn("fm_latch_first_fault(ctx,FM_FAULT_ENQUEUE)", SRC)
        self.assertIn("return; /* Failed enqueue", SRC)

    def test_graceful_stop_failure_latches_fault(self):
        self.assertIn("fm_latch_first_fault(ctx,FM_FAULT_GRACEFUL_STOP)", SRC)
        self.assertIn("AudioQueueStop(ctx->queue,false)", SRC)

    def test_listener_property_failure_latches_fault(self):
        self.assertIn("fm_latch_first_fault(ctx,FM_FAULT_PROPERTY_LISTENER)", SRC)
        self.assertIn("AudioQueueGetProperty(queue,kAudioQueueProperty_IsRunning", SRC)

    def test_monotonic_clock_failure_latches_fault(self):
        self.assertGreaterEqual(SRC.count("fm_latch_first_fault(&ctx,FM_FAULT_MONOTONIC_CLOCK)"),3)
        self.assertIn("clock_gettime(CLOCK_MONOTONIC,&stamp)", SRC)

    def test_route_drift_latches_fault(self):
        self.assertIn("fm_latch_first_fault(&ctx,FM_FAULT_ROUTE_CHANGED)", SRC)
        self.assertIn("atomic_store(&ctx.stop_requested,1)", SRC)

    def test_shutdown_uses_one_shot_atomic_barrier(self):
        self.assertIn("atomic_int shutdown_in_progress;", SRC)
        self.assertIn("atomic_exchange(&ctx.shutdown_in_progress,1)!=0", SRC)

    def test_shutdown_barrier_precedes_stop_gate(self):
        i=SRC.index("if (atomic_exchange(&ctx.shutdown_in_progress,1)!=0)")
        self.assertLess(i,SRC.index("atomic_store(&ctx.stop_requested,1);",i))

    def test_callback_observes_shutdown_barrier(self):
        cb=SRC.split("static void output_callback(",1)[1].split("static __attribute__",1)[0]
        self.assertIn("!atomic_load(&ctx->shutdown_in_progress)",cb)
        self.assertNotIn("AudioQueueStop(",cb)

    def test_drain_observes_shutdown_barrier_and_fault(self):
        drain=SRC.split("static void request_graceful_queue_drain(",1)[1].split("static void queue_running_listener(",1)[0]
        self.assertIn("atomic_load(&ctx->shutdown_in_progress)",drain)
        self.assertIn("atomic_load(&ctx->first_fault_reason)!=FM_FAULT_NONE",drain)

    def test_listener_cannot_mark_shutdown_as_normal(self):
        listener=SRC.split("static void queue_running_listener(",1)[1].split("static void output_callback(",1)[0]
        self.assertIn("!atomic_load(&ctx->shutdown_in_progress)",listener)
        self.assertIn("atomic_load(&ctx->first_fault_reason)==FM_FAULT_NONE",listener)

    def test_cleanup_still_uses_synchronous_disposal(self):
        self.assertLess(SRC.index("AudioQueueRemovePropertyListener("),SRC.rfind("AudioQueueDispose(ctx.queue,true)"))
        self.assertIn("if (AudioQueueDispose(ctx.queue,true)!=noErr) err=1;", SRC)

    def test_r10_buffer_and_watchdog_safety_retained(self):
        self.assertIn("!ctx || !buf || !buf->mAudioData",SRC)
        self.assertIn("now_ns-started_ns>max_elapsed_ns",SRC)
        self.assertIn("finished_ns-started_ns>max_elapsed_ns",SRC)

    def test_em_driver_abi_has_no_emit_or_arm_callbacks(self):
        self.assertIn("query_hardware_off_state",EM_ABI)
        self.assertIn("request_hardware_cutoff",EM_ABI)
        self.assertNotIn("(*emit)",EM_ABI)
        self.assertNotIn("(*arm)",EM_ABI)
        self.assertIn("return -1;",(ROOT/"src/em_backend.c").read_text())
        gate=(ROOT/"src/em_qualification_gate.c").read_text()
        boundary=(ROOT/"src/em_qualification_gate.h").read_text()
        self.assertIn("FM_EM_DOCUMENTS_PRESENT_UNVERIFIED",gate)
        self.assertIn("int fm_em_hardware_qualified_in_r11(",gate)
        self.assertIn("(void)evidence;\n  return 0;",gate)
        self.assertIn("char manufacturer[129];",boundary)
        self.assertIn("char protocol_document_sha256[65];",boundary)
        self.assertNotIn("IOServiceOpen(",gate)
        self.assertNotIn("AudioQueueStart(",gate)

    def test_runner_links_only_no_output_implementation(self):
        segment=RUN.split(' -o "$WORK/freqmed-gen"',1)[1].split("-framework CoreAudio",1)[0]
        self.assertIn("output_hard_denied.c",segment)
        self.assertNotIn("acoustic_macos.c",segment)
        self.assertIn("R11_NONEMITTING_EXECUTABLE_SYMBOL_AUDIT=PASS",RUN)
        self.assertIn("em_qualification_gate.c",RUN)
        self.assertIn("FIVE_BACKEND_OBJECTS=COMPILED_NOT_LINKED",RUN)
        for ver in ("R9","R10","R11"):
            self.assertIn("FREQMED_GEN_"+ver+"_BINARY",RUN)

    def test_real_native_denial_instead_of_any_emission(self):
        binary=os.environ.get("FREQMED_GEN_R11_BINARY")
        if not binary:
            self.skipTest("Owner Mac Intel no-output binary required")
        status=subprocess.run([binary,"status"],capture_output=True,text=True,timeout=5,check=True)
        payload=json.loads(status.stdout)
        self.assertEqual("NONE",payload["physical_emission"])
        self.assertEqual("NOT_LINKED_HARD_DENIED",payload["acoustic_output"])
        self.assertEqual("BLOCKED_NO_QUALIFIED_EM_DEVICE",payload["electromagnetic_output"])
        for action in ("emit","arm","play","transmit"):
            p=subprocess.run([binary,action],capture_output=True,text=True,timeout=5)
            self.assertNotEqual(0,p.returncode)
