"""Software review of native CoreAudio device binding. No physical simulation."""
from pathlib import Path
import json
import os
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
BIND = (ROOT / 'src/acoustic_device_pin_macos.c').read_text()
EMIT = (ROOT / 'src/acoustic_macos.c').read_text()
HEADER = (ROOT / 'src/acoustic_device_pin.h').read_text()
RUNNER = (ROOT / 'RUN_GEN_R5_MAC_INTEL.command').read_text()

class DeviceBindingContract(unittest.TestCase):
    def test_device_uid_is_from_selected_device_token(self):
        self.assertIn('(AudioDeviceID)route->os_device_token', BIND)
        self.assertIn('AudioObjectGetPropertyData(device,&uid_addr', BIND)
    def test_device_uid_only_from_output_scope(self):
        self.assertIn('kAudioDevicePropertyDeviceUID', BIND)
        self.assertIn('kAudioDevicePropertyScopeOutput', BIND)
        self.assertNotIn('kAudioDevicePropertyScopeInput', BIND)
    def test_current_device_is_set_explicitly(self):
        self.assertIn('AudioQueueSetProperty(', BIND)
        self.assertIn('kAudioQueueProperty_CurrentDevice', BIND)
    def test_current_device_is_read_back(self):
        self.assertIn('AudioQueueGetProperty(', BIND)
        self.assertIn('CFEqual(expected_uid,actual_uid)', BIND)
    def test_corefoundation_uid_refs_are_released(self):
        self.assertIn('CFRelease(expected_uid);', BIND)
        self.assertIn('CFRelease(actual_uid);', BIND)
    def test_rejected_device_name_does_not_escape_to_output(self):
        for bad in ('printf(', 'fprintf(', 'NSLog(', 'syslog(', 'kAudioDevicePropertyDeviceName'):
            self.assertNotIn(bad, BIND)
    def test_binds_before_buffer_enqueuing(self):
        bind_idx = EMIT.index('fm_acoustic_bind_queue_to_route((void *)ctx->queue,&route)')
        enqueue_idx = EMIT.index('AudioQueueAllocateBuffer(', bind_idx)
        start_idx = EMIT.index('AudioQueueStart(', bind_idx)
        self.assertLess(bind_idx, enqueue_idx)
        self.assertLess(bind_idx, start_idx)
    def test_binding_failure_disposes_without_start(self):
        after = EMIT.split('if (fm_acoustic_bind_queue_to_route', 1)[1]
        self.assertIn('AudioQueueDispose(ctx->queue,true);', after)
        self.assertLess(after.index('return -1;'), after.index('AudioQueueAllocateBuffer('))
    def test_checks_nominal_rate_tolerance_and_channels(self):
        self.assertIn('kAudioQueueDeviceProperty_SampleRate', BIND)
        self.assertIn('fabs(actual_rate-route->nominal_sample_rate_hz)>0.5', BIND)
        self.assertIn('kAudioQueueDeviceProperty_NumberChannels', BIND)
        self.assertIn('actual_channels!=route->output_channels', BIND)
    def test_rejects_null_opaque_queue_or_route(self):
        self.assertIn('if (!opaque_queue || !route', BIND)
    def test_rejects_invalid_rate_or_token(self):
        self.assertIn('route->os_device_token==0U', BIND)
        self.assertIn('!isfinite(route->nominal_sample_rate_hz)', BIND)
        self.assertIn('route->nominal_sample_rate_hz<=0.0', BIND)
    def test_uses_element_main_not_deprecated_master(self):
        self.assertIn('kAudioObjectPropertyElementMain', BIND)
        self.assertNotIn('kAudioObjectPropertyElementMaster', BIND)
    def test_checks_route_before_and_after_binding(self):
        self.assertIn('if (!fm_route_unchanged(route)) return -1;', BIND)
        self.assertIn('return fm_route_unchanged(route) ? 0 : -1;', BIND)
    def test_header_requires_private_route_fingerprint(self):
        self.assertIn('#include "acoustic_route_guard.h"', HEADER)
        self.assertIn('const FMRouteFingerprint *route', HEADER)
    def test_backend_impl_remains_unreachable_from_public_api(self):
        public = EMIT.split('int fm_acoustic_physical_output(', 1)[1]
        self.assertIn('return -1;', public)
        self.assertNotIn('acoustic_output_impl(', public)
    def test_runner_compiles_all_three_objects_unlinked(self):
        self.assertIn('acoustic_macos acoustic_route_guard_macos acoustic_device_pin_macos', RUNNER)
        link = RUNNER.split(' -o "$WORK/freqmed-gen"', 1)[1].split('-framework CoreAudio', 1)[0]
        for forbidden in ('acoustic_macos.c', 'acoustic_route_guard_macos.c',
                          'acoustic_device_pin_macos.c', '.isolated.o'):
            self.assertNotIn(forbidden, link)
        self.assertIn('output_hard_denied.c', link)
    def test_runner_audits_native_and_internal_symbols(self):
        self.assertIn('AudioQueueSetProperty', RUNNER)
        self.assertIn('fm_acoustic_bind_queue_to_route', RUNNER)
        self.assertIn('R5_ISOLATION_SYMBOL_PRESENT=BLOCK', RUNNER)
    def test_runner_has_no_emit_cli_mode(self):
        self.assertIn('case "$MODE" in selftest|status|probe)', RUNNER)
        self.assertIn('R5_UNKNOWN_ACTION_BLOCK', RUNNER)
    def test_cannot_generate_em_or_fake_experimental_data(self):
        self.assertIn('return -1;', (ROOT/'src/em_backend.c').read_text())
        self.assertEqual([], list(ROOT.rglob('*.csv')))
        self.assertEqual([], list(ROOT.rglob('*.wav')))

class RealNativeNoOutputContract(unittest.TestCase):
    def test_compiled_program_blocks_emission(self):
        exe = os.getenv('FREQMED_GEN_R5_BINARY')
        if not exe:
            self.skipTest('Requires compiled native no-output program')
        status = subprocess.run([exe, 'status'], capture_output=True, text=True, timeout=4)
        self.assertEqual(status.returncode, 0)
        j = json.loads(status.stdout)
        self.assertEqual(j['physical_emission'], 'NONE')
        self.assertEqual(j['acoustic_output'], 'NOT_LINKED_HARD_DENIED')
        for action in ('emit', 'play', '--force', 'unlock'):
            p = subprocess.run([exe, action], capture_output=True, text=True, timeout=4)
            self.assertNotEqual(p.returncode, 0)
