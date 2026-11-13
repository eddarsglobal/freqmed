"""Pure code-contract tests for acoustic generator lifecycle; no output or physical simulation."""
from pathlib import Path
import json
import os
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = (ROOT / 'src/acoustic_macos.c').read_text()
RUN = (ROOT / 'RUN_GEN_R8_MAC_INTEL.command').read_text()


class AudioQueueLifecycleCode(unittest.TestCase):
    def test_actual_native_queue_output_backend_is_present(self):
        self.assertIn('AudioQueueNewOutput(&fmt,output_callback,&ctx', SRC)
        self.assertIn('AudioQueueEnqueueBuffer(ctx->queue,buf,0,NULL)', SRC)

    def test_draining_is_asynchronous_normal_completion(self):
        self.assertIn('AudioQueueStop(ctx->queue,false)', SRC)
        self.assertIn('request_graceful_queue_drain', SRC)

    def test_queue_is_running_property_listener(self):
        self.assertIn('AudioQueueAddPropertyListener(ctx.queue,kAudioQueueProperty_IsRunning', SRC)
        self.assertIn('queue_running_listener', SRC)
        self.assertIn('AudioQueueGetProperty(queue,kAudioQueueProperty_IsRunning', SRC)

    def test_only_listener_confirms_stopped_state(self):
        self.assertIn('running==0U && atomic_load(&ctx->graceful_drain_requested)', SRC)
        self.assertIn('atomic_store(&ctx->queue_stopped,1)', SRC)
        self.assertIn('while (!atomic_load(&ctx.queue_stopped)', SRC)

    def test_enqueue_not_assumed_playback_completion(self):
        self.assertIn('atomic_store(&ctx->last_frame_enqueued,1)', SRC)
        self.assertNotIn('while (!atomic_load(&ctx.last_frame_enqueued)', SRC)

    def test_no_normal_immediate_stop(self):
        self.assertIn('if (err) (void)AudioQueueStop(ctx.queue,true)', SRC)
        self.assertNotIn('  (void)AudioQueueStop(ctx.queue,true);\n    (void)AudioQueueDispose', SRC)

    def test_normal_drain_latched_once(self):
        self.assertIn('atomic_compare_exchange_strong(&ctx->graceful_drain_requested,&pending,1)', SRC)

    def test_never_drain_prior_to_start(self):
        self.assertIn('!atomic_load(&ctx->queue_started)', SRC)
        self.assertIn('atomic_store(&ctx.queue_started,1)', SRC)
        start = SRC.index('if (!err && AudioQueueStart(ctx.queue,NULL)!=noErr) err=1;')
        post = SRC.index('atomic_store(&ctx.queue_started,1)', start)
        drain = SRC.index('request_graceful_queue_drain(&ctx)', post)
        self.assertLess(start, post)
        self.assertLess(post, drain)

    def test_short_commands_get_drain_request(self):
        self.assertIn('Short runs can enqueue every frame BEFORE AudioQueueStart', SRC)
        self.assertIn('request_graceful_queue_drain(&ctx)', SRC)

    def test_callback_avoids_enqueue_after_stop(self):
        self.assertIn('!atomic_load(&ctx->stop_requested) && !atomic_load(&ctx->failed)', SRC)
        self.assertIn('!atomic_load(&ctx->last_frame_enqueued)', SRC)

    def test_fault_from_property_listener_is_fail_closed(self):
        self.assertIn('atomic_store(&ctx->failed,1)', SRC)
        self.assertIn('!atomic_load(&ctx.failed)', SRC)

    def test_drift_failure_can_force_immediate_stop(self):
        self.assertIn('!fm_route_unchanged(&route)', SRC)
        self.assertIn('atomic_store(&ctx.stop_requested,1)', SRC)
        self.assertIn('if (err) (void)AudioQueueStop(ctx.queue,true)', SRC)

    def test_watchdog_remains_bounded(self):
        self.assertIn('const unsigned max_cycles=request->duration_ms/10U+300U', SRC)
        self.assertIn('wait_cycles<max_cycles', SRC)
        self.assertIn('wait_cycles>=max_cycles', SRC)

    def test_atomic_queue_state(self):
        for field in ('atomic_int queue_started;', 'atomic_int queue_stopped;',
                      'atomic_int graceful_drain_requested;', 'atomic_int stop_requested;'):
            self.assertIn(field, SRC)

    def test_compiled_only_not_linked(self):
        self.assertIn('acoustic_macos acoustic_route_guard_macos acoustic_device_pin_macos', RUN)
        link = RUN.split(' -o "$WORK/freqmed-gen"', 1)[1].split('-framework CoreAudio', 1)[0]
        self.assertNotIn('acoustic_macos.c', link)
        self.assertNotIn('acoustic_macos.isolated.o', link)
        self.assertIn('output_hard_denied.c', link)

    def test_r8_launcher_does_not_offer_emission(self):
        self.assertIn('selftest|status|probe|em-discover', RUN)
        self.assertIn('R8_UNKNOWN_ACTION_BLOCK', RUN)

    def test_hard_denied_public_acoustic_api(self):
        public = SRC.split('int fm_acoustic_physical_output(', 1)[1]
        self.assertIn('return -1;', public)
        self.assertNotIn('acoustic_output_impl(', public)

    def test_em_still_blocked(self):
        self.assertIn('return -1;', (ROOT / 'src/em_backend.c').read_text())
        self.assertIn('return -1;', (ROOT / 'src/em_device_contract.c').read_text())

    def test_no_scientific_simulation_or_fake_measurement(self):
        self.assertEqual([], list(ROOT.rglob('*.csv')))
        self.assertEqual([], list(ROOT.rglob('*.wav')))

    def test_r8_symbols_guard(self):
        self.assertIn('AudioQueueStart', RUN)
        self.assertIn('AudioQueueNewOutput', RUN)
        self.assertIn('fm_acoustic_bind_queue_to_route', RUN)
        self.assertIn('R8_OUTPUT_BACKEND_LINKED=BLOCK', RUN)

    def test_real_r8_program_still_not_emitting(self):
        binary = os.environ.get('FREQMED_GEN_R8_BINARY')
        if not binary:
            self.skipTest('Requires compiled actual no-output executable')
        r = subprocess.run([binary, 'status'], capture_output=True, text=True, timeout=5)
        self.assertEqual(0, r.returncode)
        status = json.loads(r.stdout)
        self.assertEqual('NONE', status['physical_emission'])
        self.assertEqual('NOT_LINKED_HARD_DENIED', status['acoustic_output'])
        for action in ('emit', 'arm', 'play', 'transmit'):
            r = subprocess.run([binary, action], capture_output=True, text=True, timeout=5)
            self.assertNotEqual(0, r.returncode)


if __name__ == '__main__':
    unittest.main()
