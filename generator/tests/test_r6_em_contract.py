"""Pure software admission checks; never simulation or instrument I/O."""
from pathlib import Path
import os
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'src'
CONTRACT = (SRC / 'em_device_contract.c').read_text()
HEADER = (SRC / 'em_device_contract.h').read_text()
DRIVER = (SRC / 'em_instrument_driver_abi.h').read_text()
RUNNER = (ROOT / 'RUN_GEN_R6_MAC_INTEL.command').read_text()


class EmSafetyContract(unittest.TestCase):
    def test_typed_hardware_outputs(self):
        for token in ('FM_EM_DRIVE_V_RMS', 'FM_EM_DRIVE_A_RMS',
                      'FM_EM_DRIVE_DBM', 'FMEmDriveUnit'):
            self.assertIn(token, HEADER)

    def test_no_fake_transducer_or_hardware(self):
        for forbidden in ('fake_device', 'simulator', 'virtual_rf', 'pyvisa_sim'):
            self.assertNotIn(forbidden, CONTRACT.lower())

    def test_no_universal_physical_safety_limits(self):
        self.assertIn('device_min_hz', HEADER)
        self.assertIn('device_max_hz', HEADER)
        self.assertIn('device_min_drive', HEADER)
        self.assertIn('device_max_drive', HEADER)
        self.assertIn('device_max_duration_ms', HEADER)
        self.assertNotIn('SAFE_FREQUENCY_HZ', HEADER)

    def test_profile_identity_requires_sha256_format(self):
        self.assertIn('device_identity_sha256[65]', HEADER)
        self.assertIn('hex_identity_pinned(', CONTRACT)
        self.assertIn('any_nonzero && h[64] == 0', CONTRACT)

    def test_profile_range_finite_and_monotone(self):
        self.assertIn('!isfinite(p->device_min_hz)', CONTRACT)
        self.assertIn('p->device_max_hz <= p->device_min_hz', CONTRACT)
        self.assertIn('p->device_max_drive <= p->device_min_drive', CONTRACT)

    def test_no_implicit_normalized_drive_to_physical_unit(self):
        self.assertIn('request->drive_unit != profile->drive_unit', CONTRACT)
        self.assertNotIn('normalized_level', CONTRACT)
        self.assertIn('FM_EM_SETPOINT_REJECTED', CONTRACT)

    def test_no_signal_or_physics_generation(self):
        for term in ('sin(', 'cos(', 'AudioQueue', 'coil_field=', 'sample_buffer', 'waveform'):
            self.assertNotIn(term, CONTRACT)

    def test_no_io_api_in_em_admission_module(self):
        for token in ('open(', 'write(', 'socket(', 'connect(',
                      'IOServiceOpen(', 'AudioObjectSetPropertyData('):
            self.assertNotIn(token, CONTRACT)

    def test_hard_denial_is_unconditional(self):
        segment = CONTRACT.split('int fm_em_try_physical_emission(', 1)[1]
        self.assertIn('(void)profile;', segment)
        self.assertIn('(void)request;', segment)
        self.assertIn('return -1;', segment)

    def test_no_runtime_flag_bypasses(self):
        for token in ('override_safety', 'force_emit', 'enable_output', 'certified=1'):
            self.assertNotIn(token, CONTRACT)

    def test_device_abi_requires_readonly_identity(self):
        self.assertIn('identify_readonly', DRIVER)
        self.assertIn('observed_fingerprint_sha256', DRIVER)

    def test_device_abi_requires_cutoff(self):
        self.assertIn('request_hardware_cutoff', DRIVER)
        self.assertIn('query_hardware_off_state', DRIVER)

    def test_device_abi_excludes_activation(self):
        for forbidden in ('(*arm_output)', '(*enable_output)', '(*transmit)', '(*set_frequency)'):
            self.assertNotIn(forbidden, DRIVER)

    def test_em_backend_still_failclosed(self):
        old = (SRC / 'em_backend.c').read_text()
        self.assertIn('int fm_em_physical_output(', old)
        self.assertIn('return -1;', old)

    def test_compilation_is_source_only(self):
        self.assertIn('src/em_device_contract.c', RUNNER)
        self.assertIn('em_contract.isolated.o', RUNNER)
        user_link = RUNNER.split(' -o "$WORK/freqmed-gen"', 1)[1].split('-framework CoreAudio', 1)[0]
        self.assertNotIn('em_device_contract.c', user_link)
        self.assertNotIn('em_contract.isolated.o', user_link)

    def test_r5_acoustic_backend_is_still_isolated(self):
        self.assertIn('acoustic_macos acoustic_route_guard_macos acoustic_device_pin_macos', RUNNER)
        self.assertIn('output_hard_denied.c', RUNNER)

    def test_native_symbol_audit_failclosed(self):
        self.assertIn('R6_FORBIDDEN_NATIVE_SYMBOL=BLOCK', RUNNER)
        self.assertIn('R6_NM_UNAVAILABLE=BLOCK', RUNNER)

    def test_unknown_runner_action_is_blocked(self):
        self.assertIn('R6_UNKNOWN_ACTION_BLOCK', RUNNER)
        self.assertIn('selftest|status|probe', RUNNER)

    def test_no_scientific_data_fixtures(self):
        self.assertEqual([], list(ROOT.rglob('*.wav')))
        self.assertEqual([], list(ROOT.rglob('*.csv')))

    def test_no_instrument_protocol_guessed(self):
        for term in ('OUTP ON', 'FREQ ', ':SOUR:FREQ', 'RF:ON'):
            self.assertNotIn(term, CONTRACT)

    def test_native_selftest_binary_still_locked(self):
        exe = os.environ.get('FREQMED_GEN_R6_BINARY')
        if not exe:
            self.skipTest('Requires native Mac or software host binary')
        result = subprocess.run([exe, 'status'], text=True, capture_output=True, timeout=5)
        self.assertEqual(result.returncode, 0)
        self.assertIn('"physical_emission":"NONE"', result.stdout)
        self.assertIn('"electromagnetic_output":"BLOCKED_NO_QUALIFIED_EM_DEVICE"', result.stdout)


if __name__ == '__main__':
    unittest.main()
