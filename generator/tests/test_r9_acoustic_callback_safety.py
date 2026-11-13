"""GEN-R9 source and real no-output executable tests. No simulated devices, measurements or output."""
from pathlib import Path
import json
import os
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = (ROOT / "src/acoustic_macos.c").read_text(encoding="utf-8")
RUN = (ROOT / "RUN_GEN_R9_MAC_INTEL.command").read_text(encoding="utf-8")

class R9SafetyContracts(unittest.TestCase):
    def test_callback_never_stops_queue(self):
        cb = SRC.split("static void output_callback(", 1)[1].split("static __attribute__", 1)[0]
        self.assertNotIn("AudioQueueStop(", cb)
        self.assertNotIn("request_graceful_queue_drain(", cb)

    def test_controller_owns_drain(self):
        self.assertIn("static void request_graceful_queue_drain(", SRC)
        self.assertGreaterEqual(SRC.count("request_graceful_queue_drain(&ctx)"), 2)

    def test_drain_only_after_start(self):
        self.assertIn("!atomic_load(&ctx->queue_started)", SRC)
        self.assertLess(SRC.index("atomic_store(&ctx.queue_started,1)"), SRC.index("request_graceful_queue_drain(&ctx)"))

    def test_no_drain_on_failure_or_stop(self):
        self.assertIn("atomic_load(&ctx->stop_requested) || atomic_load(&ctx->failed)", SRC)

    def test_drain_once(self):
        self.assertIn("atomic_compare_exchange_strong(&ctx->graceful_drain_requested,&pending,1)", SRC)

    def test_fault_stop_only_after_start(self):
        self.assertIn("if (err && atomic_load(&ctx.queue_started))", SRC)
        self.assertIn("if (AudioQueueStop(ctx.queue,true)!=noErr) err=1;", SRC)

    def test_callback_stop_gate(self):
        self.assertIn("!atomic_load(&ctx->stop_requested) && !atomic_load(&ctx->failed)", SRC)

    def test_listener_registration_tracked(self):
        self.assertIn("int listener_installed=0;", SRC)
        self.assertIn("else listener_installed=1;", SRC)

    def test_listener_removed_before_final_dispose(self):
        self.assertLess(SRC.index("AudioQueueRemovePropertyListener("), SRC.rfind("AudioQueueDispose(ctx.queue,true)"))

    def test_shutdown_gate_before_final_dispose(self):
        # GEN-R11 renamed the commentary. Assert executable C ordering,
        # not a version-specific source comment.
        begin = SRC.index("if (atomic_exchange(&ctx.shutdown_in_progress,1)!=0)")
        stop = SRC.index("atomic_store(&ctx.stop_requested,1);", begin)
        listener = SRC.index("AudioQueueRemovePropertyListener(", stop)
        dispose = SRC.rfind("AudioQueueDispose(ctx.queue,true)")
        self.assertLess(begin, stop)
        self.assertLess(stop, listener)
        self.assertLess(listener, dispose)

    def test_dispose_is_synchronous(self):
        self.assertIn("if (AudioQueueDispose(ctx.queue,true)!=noErr) err=1;", SRC)
        self.assertNotIn("AudioQueueDispose(ctx.queue,false)", SRC)

    def test_remove_failure_propagates(self):
        self.assertIn("kAudioQueueProperty_IsRunning,queue_running_listener,&ctx)!=noErr)", SRC)
        self.assertIn("return err?-1:0;", SRC)

    def test_listener_observes_running_property(self):
        self.assertIn("AudioQueueGetProperty(queue,kAudioQueueProperty_IsRunning", SRC)
        self.assertIn("running==0U && atomic_load(&ctx->graceful_drain_requested)", SRC)

    def test_public_acoustic_output_hard_denied(self):
        public = SRC.split("int fm_acoustic_physical_output(", 1)[1]
        self.assertIn("return -1;", public)
        self.assertNotIn("acoustic_output_impl(", public)

    def test_em_output_hard_denied(self):
        self.assertIn("return -1;", (ROOT / "src/em_backend.c").read_text())

    def test_output_objects_not_linked_by_runner(self):
        self.assertIn("acoustic_macos acoustic_route_guard_macos acoustic_device_pin_macos", RUN)
        linker = RUN.split(' -o "$WORK/freqmed-gen"', 1)[1].split("-framework CoreAudio", 1)[0]
        self.assertIn("output_hard_denied.c", linker)
        self.assertNotIn("acoustic_macos.c", linker)
        self.assertNotIn("acoustic_macos.isolated.o", linker)

    def test_symbol_guard_and_legacy_regressions(self):
        self.assertIn("R9_OUTPUT_BACKEND_LINKED=BLOCK", RUN)
        self.assertIn("R9_NONEMITTING_EXECUTABLE_SYMBOL_AUDIT=PASS", RUN)
        for tag in ("FREQMED_GEN_R7_BINARY", "FREQMED_GEN_R8_BINARY", "FREQMED_GEN_R9_BINARY"):
            self.assertIn(tag, RUN)

    def test_no_emitting_cli_option(self):
        self.assertIn("selftest|status|probe|em-discover", RUN)
        self.assertIn("R9_UNKNOWN_ACTION_BLOCK", RUN)

    def test_actual_native_no_output_executable(self):
        binary = os.environ.get("FREQMED_GEN_R9_BINARY")
        if not binary:
            self.skipTest("Requires owner Mac Intel native binary, no synthetic hardware")
        status = subprocess.run([binary, "status"], capture_output=True, text=True, timeout=5, check=True)
        payload = json.loads(status.stdout)
        self.assertEqual("NONE", payload["physical_emission"])
        self.assertEqual("NOT_LINKED_HARD_DENIED", payload["acoustic_output"])
        for action in ("emit", "arm", "play", "transmit"):
            p = subprocess.run([binary, action], capture_output=True, text=True, timeout=5)
            self.assertNotEqual(0, p.returncode)

    def test_no_fake_measurement_files(self):
        self.assertFalse(list(ROOT.rglob("*.csv")))
        self.assertFalse(list(ROOT.rglob("*.wav")))

if __name__ == "__main__":
    unittest.main()
