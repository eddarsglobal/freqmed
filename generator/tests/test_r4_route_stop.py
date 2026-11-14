"""Software invariants only; no scientific simulation or acoustic output."""
from pathlib import Path
import json, os, subprocess, unittest
R = Path(__file__).resolve().parents[1]
A = (R/'src/acoustic_macos.c').read_text()
G = (R/'src/acoustic_route_guard_macos.c').read_text()
H = (R/'src/acoustic_route_guard.h').read_text()
SH = (R/'RUN_GEN_R4_MAC_INTEL.command').read_text()

class RouteAndStop(unittest.TestCase):
    def test_route_guard_is_actual_coreaudio_read(self):
        self.assertIn('AudioObjectGetPropertyData(', G)
        self.assertIn('kAudioHardwarePropertyDefaultOutputDevice',G)
    def test_route_checks_both_sides_of_metadata_probe(self):
        self.assertIn('read_default_output(&before)',G)
        self.assertIn('read_default_output(&after)',G)
        self.assertIn('before!=after',G)
    def test_current_route_comparison_checks_all_factors(self):
        for x in ('os_device_token','nominal_sample_rate_hz','output_channels'):
            self.assertIn('now.'+x+'==first->'+x,G)
    def test_missing_route_fails_closed(self):
        self.assertIn('if (!first || first->os_device_token==0',G)
        self.assertIn('if (fm_route_capture(&now)!=0) return 0',G)
    def test_device_token_stays_internal(self):
        self.assertIn('os_device_token', H)
        self.assertNotIn('os_device_token', (R/'src/main.c').read_text())
        self.assertNotIn('printf(', G)
    def test_no_device_mutation_in_guard(self):
        for bad in ('AudioObjectSetPropertyData(', 'AudioDeviceStart(', 'AudioQueueStart(', 'kAudioHardwarePropertyDefaultInputDevice'):
            self.assertNotIn(bad,G)
    def test_backend_checks_route_before_setting_queue(self):
        i=A.index('fm_route_capture(&route)')
        j=A.index('AudioQueueNewOutput(')
        self.assertLess(i,j)
        self.assertIn('if (!fm_route_unchanged(&route)) return -1;',A[i:j])
    def test_backend_checks_route_immediately_before_start(self):
        i=A.index('if (!err && !fm_route_unchanged(&route)) err=1;')
        j=A.index('AudioQueueStart(ctx->queue,NULL)')
        self.assertLess(i,j)
    def test_backend_periodically_checks_during_running(self):
        self.assertIn('if ((wait_cycles%10U)==0U && !fm_route_unchanged(&route))',A)
        self.assertIn('atomic_store(&ctx->stop_requested,1)',A)
    def test_callback_observes_stop_flag(self):
        self.assertIn('atomic_int stop_requested;',A)
        self.assertIn('!atomic_load(&ctx->stop_requested)',A)
    def test_immediate_queue_stop(self):
        self.assertIn('AudioQueueStop(ctx->queue,true)',A)
        self.assertNotIn('AudioQueueStop(ctx->queue,err?true:false)',A)
    def test_runner_compiles_both_objects_separately(self):
        for p in ('src/acoustic_macos.c','src/acoustic_route_guard_macos.c'):
            self.assertIn('"$ROOT/'+p+'"',SH)
        self.assertIn(' -Werror -c ',SH)
    def test_runner_does_not_link_output_object(self):
        block=SH.split(' -o "$WORK/freqmed-gen"',1)[1].split('-framework CoreAudio',1)[0]
        for bad in ('acoustic_macos.c','acoustic_route_guard_macos.c','acoustic_output_isolated.o','acoustic_route_isolated.o'):
            self.assertNotIn(bad,block)
        self.assertIn('output_hard_denied.c',block)
    def test_runner_uses_nm_block(self):
        self.assertIn('nm -u "$WORK/freqmed-gen"',SH)
        self.assertIn('R4_FORBIDDEN_OUTPUT_SYMBOL=BLOCK',SH)
        self.assertIn('R4_SYMBOL_AUDIT_UNAVAILABLE=BLOCK',SH)
    def test_guardian_hard_deny_retained(self):
        t=(R/'src/generator_core.c').read_text()
        self.assertIn('g->state=FM_BLOCKED;',t)
    def test_em_backend_still_no_output(self):
        t=(R/'src/em_backend.c').read_text()
        self.assertIn('return -1;',t)
    def test_no_fake_scientific_measurement_fixtures(self):
        self.assertFalse(list(R.rglob('*.csv')))
        self.assertFalse(list(R.rglob('*.wav')))
    def test_no_new_output_cli(self):
        t=(R/'src/main.c').read_text()
        self.assertNotIn('strcmp(argv[1],"emit")',t)
        self.assertIn('R4_UNKNOWN_ACTION_BLOCK',SH)

class NativeStatus(unittest.TestCase):
    def test_real_binary_remains_hard_blocked(self):
        exe=os.environ.get('FREQMED_GEN_R4_BINARY')
        if not exe:self.skipTest('Native R4 binary not built')
        p=subprocess.run([exe,'status'],capture_output=True,text=True,timeout=4)
        self.assertEqual(0,p.returncode)
        x=json.loads(p.stdout)
        self.assertEqual('NONE',x['physical_emission'])
        self.assertEqual('NOT_LINKED_HARD_DENIED',x['acoustic_output'])
    def test_unauthorized_command_refused(self):
        exe=os.environ.get('FREQMED_GEN_R4_BINARY')
        if not exe:self.skipTest('Native R4 binary not built')
        for mode in ('emit','play','unlock','--force'):
            p=subprocess.run([exe,mode],capture_output=True,text=True,timeout=4)
            self.assertNotEqual(0,p.returncode)
