"""GEN-R12: callback/lifetime source audits and real non-emitting executable contracts.

No fabricated device, synthetic signal, scientific simulation, port opening,
hardware activation or physical measurement is performed by these tests.
Static source contracts do NOT prove race freedom or physical cutoff timing.
"""
from pathlib import Path
import json
import os
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = (ROOT / "src/acoustic_macos.c").read_text(encoding="utf-8")
RUN = (ROOT / "RUN_GEN_R12_MAC_INTEL.command").read_text(encoding="utf-8")
EM = (ROOT / "src/em_backend.c").read_text(encoding="utf-8")
EM_GATE = (ROOT / "src/em_qualification_gate.c").read_text(encoding="utf-8")
OUTPUT_CALLBACK = SRC.split("static void output_callback(", 1)[1].split(
    "static __attribute__", 1)[0]
PROPERTY_LISTENER = SRC.split("static void queue_running_listener(", 1)[1].split(
    "static void output_callback(", 1)[0]

class R12CallbackLifetimeAudit(unittest.TestCase):
    def test_active_callback_counters_are_atomic(self):
        self.assertIn("atomic_uint active_output_callbacks;", SRC)
        self.assertIn("atomic_uint active_property_listeners;", SRC)

    def test_counters_initialized_to_zero(self):
        self.assertIn("atomic_init(&ctx->active_output_callbacks,0U);", SRC)
        self.assertIn("atomic_init(&ctx->active_property_listeners,0U);", SRC)

    def test_output_callback_counts_entry(self):
        self.assertIn("atomic_fetch_add_explicit(&ctx->active_output_callbacks,1U,", OUTPUT_CALLBACK)
        self.assertIn("memory_order_acq_rel", OUTPUT_CALLBACK)

    def test_output_callback_counts_exit(self):
        self.assertIn("atomic_fetch_sub_explicit(&ctx->active_output_callbacks,1U,", OUTPUT_CALLBACK)
        self.assertLess(OUTPUT_CALLBACK.index("atomic_fetch_add_explicit"),
                        OUTPUT_CALLBACK.index("atomic_fetch_sub_explicit"))

    def test_null_context_does_not_increment_counter(self):
        self.assertIn("if (!ctx) return;", OUTPUT_CALLBACK)
        self.assertLess(OUTPUT_CALLBACK.index("if (!ctx) return;"),
                        OUTPUT_CALLBACK.index("atomic_fetch_add_explicit"))

    def test_output_callback_never_owns_stop(self):
        self.assertNotIn("AudioQueueStop(", OUTPUT_CALLBACK)
        self.assertNotIn("request_graceful_queue_drain(", OUTPUT_CALLBACK)
        self.assertIn("atomic_flag_test_and_set_explicit(&ctx->pcm_writer_gate,", OUTPUT_CALLBACK)
        self.assertIn("atomic_flag_clear_explicit(&ctx->pcm_writer_gate,", OUTPUT_CALLBACK)
        self.assertIn("fm_latch_first_fault(ctx,FM_FAULT_OVERLAPPING_PCM_CALLBACK)", OUTPUT_CALLBACK)
        self.assertIn("atomic_flag_clear(&ctx->pcm_writer_gate);", SRC)

    def test_property_listener_counts_entry_exit(self):
        self.assertIn("atomic_fetch_add_explicit(&ctx->active_property_listeners,1U,", PROPERTY_LISTENER)
        self.assertIn("atomic_fetch_sub_explicit(&ctx->active_property_listeners,1U,", PROPERTY_LISTENER)

    def test_property_listener_has_single_exit_label(self):
        self.assertIn("listener_exit:", PROPERTY_LISTENER)
        self.assertEqual(1, PROPERTY_LISTENER.count("listener_exit:"))
        self.assertEqual(2, PROPERTY_LISTENER.count("goto listener_exit;"))

    def test_listener_mismatch_balances_counter(self):
        self.assertIn("if (property!=kAudioQueueProperty_IsRunning) goto listener_exit;", PROPERTY_LISTENER)

    def test_listener_property_failure_balances_counter(self):
        self.assertIn("fm_latch_first_fault(ctx,FM_FAULT_PROPERTY_LISTENER)", PROPERTY_LISTENER)
        self.assertIn("goto listener_exit;", PROPERTY_LISTENER)

    def test_dispose_confirmation_is_atomic(self):
        self.assertIn("atomic_int dispose_confirmed;", SRC)
        self.assertIn("atomic_init(&ctx->dispose_confirmed,0);", SRC)
        self.assertIn("atomic_store(&ctx->dispose_confirmed,1);", SRC)

    def test_dispose_error_is_a_first_fault(self):
        self.assertIn("fm_latch_first_fault(ctx,FM_FAULT_DISPOSAL);", SRC)
        self.assertIn("if (AudioQueueDispose(ctx->queue,true)!=noErr)", SRC)

    def test_accounting_checked_after_sync_dispose(self):
        dispose = SRC.rfind("if (AudioQueueDispose(ctx->queue,true)!=noErr)")
        outputs = SRC.index("atomic_load_explicit(&ctx->active_output_callbacks,", dispose)
        listener = SRC.index("atomic_load_explicit(&ctx->active_property_listeners,", dispose)
        self.assertLess(dispose, outputs)
        self.assertLess(outputs, listener)

    def test_inflight_output_is_never_success(self):
        self.assertIn("fm_latch_first_fault(ctx,FM_FAULT_OUTPUT_CALLBACK_INFLIGHT)", SRC)
        self.assertIn("memory_order_acquire)!=0U", SRC)

    def test_inflight_listener_is_never_success(self):
        self.assertIn("fm_latch_first_fault(ctx,FM_FAULT_PROPERTY_LISTENER_INFLIGHT)", SRC)
        self.assertIn("if (!atomic_load(&ctx->dispose_confirmed)) err=1;", SRC)

    def test_shutdown_precedes_listener_removal_dispose(self):
        barrier = SRC.index("if (atomic_exchange(&ctx->shutdown_in_progress,1)!=0)")
        stop = SRC.index("atomic_store(&ctx->stop_requested,1);", barrier)
        remove = SRC.index("AudioQueueRemovePropertyListener(", stop)
        dispose = SRC.rfind("AudioQueueDispose(ctx->queue,true)")
        self.assertTrue(barrier < stop < remove < dispose)

    def test_r10_watchdog_and_r11_fault_latch_remain(self):
        self.assertIn("clock_gettime(CLOCK_MONOTONIC,&stamp)", SRC)
        self.assertIn("fm_latch_first_fault(ctx,FM_FAULT_MONOTONIC_CLOCK)", SRC)
        self.assertIn("atomic_compare_exchange_strong(&ctx->first_fault_reason,", SRC)

    def test_em_document_screen_never_qualifies_hardware(self):
        self.assertIn("FM_EM_DOCUMENTS_PRESENT_UNVERIFIED", EM_GATE)
        self.assertIn("int fm_em_hardware_qualified_in_r11(", EM_GATE)
        self.assertIn("(void)evidence;\n  return 0;", EM_GATE)
        self.assertIn("return -1;", EM)

    def test_runner_still_excludes_output_backend(self):
        linker = RUN.split(' -o "$WORK/freqmed-gen"', 1)[1].split(
            "-framework CoreAudio", 1)[0]
        self.assertIn("output_hard_denied.c", linker)
        self.assertNotIn("acoustic_macos.c", linker)
        self.assertIn("R12_NONEMITTING_EXECUTABLE_SYMBOL_AUDIT=PASS", RUN)
        self.assertIn("R12_OUTPUT_BACKEND_LINKED=BLOCK", RUN)
        for v in ("R10", "R11", "R12"):
            self.assertIn("FREQMED_GEN_" + v + "_BINARY", RUN)
        self.assertIn("selftest|status|probe|em-discover", RUN)

    def test_actual_native_executable_is_nonemitting(self):
        binary = os.environ.get("FREQMED_GEN_R12_BINARY")
        if not binary:
            self.skipTest("Owner Mac Intel native non-emitting executable required")
        status = subprocess.run([binary, "status"], capture_output=True,
                                text=True, timeout=5, check=True)
        data = json.loads(status.stdout)
        self.assertEqual("NONE", data["physical_emission"])
        self.assertEqual("NOT_LINKED_HARD_DENIED", data["acoustic_output"])
        self.assertEqual("BLOCKED_NO_QUALIFIED_EM_DEVICE", data["electromagnetic_output"])
        for action in ("emit", "arm", "play", "transmit"):
            result = subprocess.run([binary, action], capture_output=True,
                                    text=True, timeout=5)
            self.assertNotEqual(0, result.returncode)
