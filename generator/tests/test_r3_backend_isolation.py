"""Software guards of real audio backend source, without emitting sound or simulating physics."""
from pathlib import Path
import json,os,subprocess,unittest
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'src'
RUN=(ROOT/'RUN_GEN_R3_MAC_INTEL.command').read_text()
AUD=(SRC/'acoustic_macos.c').read_text()

class AcousticBackendR3Guards(unittest.TestCase):
    def test_nonemitting_compilation_only(self):
        self.assertIn('"$ROOT/src/acoustic_macos.c" -o "$WORK/isolated_acoustic_backend.o"',RUN)
        self.assertIn('-Werror -c',RUN)
    def test_compiled_object_not_linked(self):
        link=RUN.split('"$ROOT/src/main.c"',1)[1].split('-framework CoreAudio',1)[0]
        self.assertNotIn('acoustic_macos.c',link)
        self.assertNotIn('isolated_acoustic_backend.o',link)
        self.assertIn('output_hard_denied.c',link)
    def test_object_not_loaded(self):
        for bad in ('dlopen(', 'open "$WORK/isolated_acoustic_backend.o"', 'source "$WORK/isolated_acoustic_backend.o"'):
            self.assertNotIn(bad,RUN)
    def test_no_output_cli(self):
        self.assertIn('case "$MODE" in selftest|probe|status)',RUN)
        self.assertIn('R3_UNKNOWN_ACTION_BLOCK',RUN)
    def test_hard_denial_retained_in_backend(self):
        source=AUD.split('int fm_acoustic_physical_output(',1)[1]
        self.assertIn('return -1;',source)
        self.assertNotIn('acoustic_output_impl(',source)
    def test_backend_uses_actual_os_nominal_rate(self):
        self.assertIn('fm_route_capture(&route)',AUD)
        self.assertIn('route.nominal_sample_rate_hz',AUD)
        self.assertIn('const double sr=route.nominal_sample_rate_hz;',AUD)
    def test_no_assumed_48khz_sample_rate(self):
        self.assertNotIn('const double sr=48000.0',AUD)
        self.assertNotIn('48000.0',AUD)
    def test_dynamic_10ms_digital_ramp(self):
        self.assertIn('ctx.fade_frames=(uint64_t)(sr/100.0)',AUD)
        self.assertIn('ctx->fade_frames',AUD)
        self.assertNotIn('if (at<480U)',AUD)
    def test_numerical_boundaries_in_source(self):
        for expected in ('!isfinite(route.nominal_sample_rate_hz)',
                         'route.nominal_sample_rate_hz<8000.0',
                         'route.nominal_sample_rate_hz>384000.0',
                         'request->frequency_hz>=sr/2.0',
                         'request->duration_ms>60000U',
                         'request->normalized_level>1.0'):
            self.assertIn(expected,AUD)
    def test_unqualified_em_still_denied(self):
        src=(SRC/'em_backend.c').read_text()
        self.assertIn('return -1;',src)
        self.assertIn('return 0;',src)
    def test_no_os_input_or_capture(self):
        probe=(SRC/'acoustic_probe_macos.c').read_text()
        self.assertNotIn('kAudioHardwarePropertyDefaultInputDevice',probe)
        for bad in ('AudioQueueNewInput(', 'AudioDeviceStart('):
            self.assertNotIn(bad,AUD+probe)
    def test_no_mac_os_deprecated_selector(self):
        self.assertNotIn('kAudioObjectPropertyElementMaster',(SRC/'acoustic_probe_macos.c').read_text())
    def test_native_symbol_guard(self):
        self.assertIn('nm -u "$WORK/freqmed-gen"',RUN)
        self.assertIn('R3_SYMBOL_AUDIT_FAILED=BLOCK',RUN)
        self.assertIn('AudioQueueStart',RUN)
    def test_does_not_invent_measurement_artifacts(self):
        self.assertFalse(list(ROOT.rglob('*.csv')))
        self.assertFalse(list(ROOT.rglob('*.wav')))
    def test_bureau_review_pending(self):
        t=(ROOT/'docs/GEN_R3_BUREAU_PENDING.md').read_text()
        for role in ('B04','B05','B07','B09','B10'): self.assertIn(role,t)
    def test_explicit_output_disabled(self):
        self.assertIn('R3_REAL_ACOUSTIC_OUTPUT=NONE',RUN)
        self.assertIn('R3_EM_OUTPUT=NONE',RUN)
    def test_binary_never_offers_emission(self):
        src=(SRC/'main.c').read_text()
        self.assertNotIn('strcmp(argv[1],"emit")',src)
        self.assertNotIn('strcmp(argv[1],"play")',src)

class NativeExecutableR3Guards(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.binary=os.environ.get('FREQMED_GEN_R3_BINARY')
    def invoke(self,arg):
        if not self.binary:self.skipTest('Native executable not built on this host')
        return subprocess.run([self.binary,arg],capture_output=True,text=True,timeout=4)
    def test_native_status(self):
        p=self.invoke('status');self.assertEqual(0,p.returncode)
        j=json.loads(p.stdout)
        self.assertEqual('NONE',j['physical_emission'])
        self.assertEqual('NOT_LINKED_HARD_DENIED',j['acoustic_output'])
    def test_native_denies_emit(self):
        for arg in ('emit','play','--force-output'):
            p=self.invoke(arg);self.assertNotEqual(0,p.returncode)
    def test_native_selftest(self):
        p=self.invoke('selftest');self.assertEqual(0,p.returncode)
        self.assertIn('GUARDIAN=FAIL_CLOSED',p.stdout)
