"""GEN-R2: software security and parser/contract tests, no physical simulation."""
import pathlib,subprocess,os,json,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
SRC=ROOT/'src'

class R2Contract(unittest.TestCase):
    def test_coreaudio_elementmain_sdk_fix1(self):
        source=(SRC/'acoustic_probe_macos.c').read_text()
        self.assertEqual(3,source.count('kAudioObjectPropertyElementMain'))
        self.assertNotIn('kAudioObjectPropertyElementMaster',source)
    def test_real_default_output_query(self):
        text=(SRC/'acoustic_probe_macos.c').read_text()
        self.assertIn('kAudioHardwarePropertyDefaultOutputDevice',text)
        self.assertIn('AudioObjectGetPropertyData',text)
        self.assertIn('kAudioDevicePropertyScopeOutput',text)
    def test_no_device_activation_in_probe(self):
        text=(SRC/'acoustic_probe_macos.c').read_text()
        for forbidden in ('AudioQueueStart(', 'AudioDeviceStart(', 'AudioUnitRender(', 'AudioObjectSetPropertyData(', 'AudioQueueNewOutput(', 'AudioQueueEnqueueBuffer(', 'kAudioHardwarePropertyDefaultInputDevice'):
            self.assertNotIn(forbidden,text)
    def test_no_device_uid_export(self):
        text=(SRC/'acoustic_probe_macos.c').read_text()
        for forbidden in ('kAudioDevicePropertyDeviceUID', 'kAudioDevicePropertyDeviceName', 'kAudioDevicePropertyDeviceManufacturer'):
            self.assertNotIn(forbidden,text)
    def test_buffer_length_validated(self):
        text=(SRC/'acoustic_probe_macos.c').read_text()
        self.assertIn('offsetof(AudioBufferList,mBuffers)',text)
        self.assertIn('list->mNumberBuffers<=',text)
        self.assertIn('size>65536U',text)
    def test_output_impl_not_linked_by_runner(self):
        text=(ROOT/'RUN_GEN_R2_MAC_INTEL.command').read_text()
        self.assertIn('src/output_hard_denied.c',text)
        self.assertIn('src/acoustic_probe_macos.c',text)
        self.assertNotIn('src/acoustic_macos.c',text)
    def test_output_symbol_always_refuses(self):
        text=(SRC/'output_hard_denied.c').read_text()
        self.assertIn('return -1;',text)
        self.assertNotIn('AudioQueue',text.split('int fm_acoustic_physical_output',1)[1])
    def test_no_em_devices_or_emission(self):
        text=(SRC/'em_backend.c').read_text()
        self.assertIn('return -1;',text)
    def test_no_generated_scientific_measurements(self):
        self.assertEqual([],list(ROOT.rglob('*.csv')))
        self.assertEqual([],list(ROOT.rglob('*.wav')))
    def test_probe_has_no_unique_labels(self):
        text=(SRC/'main.c').read_text()
        self.assertIn('NOT_CERTIFIED',text)
        self.assertIn('NOT_VERIFIED',text)
        self.assertNotIn('device_uid',text.lower())
    def test_source_only_backend_is_segregated(self):
        self.assertTrue((SRC/'acoustic_macos.c').is_file())
        self.assertTrue((SRC/'output_hard_denied.c').is_file())
    def test_guardian_remains_hard_closed(self):
        text=(SRC/'generator_core.c').read_text()
        self.assertIn('g->state=FM_BLOCKED;',text)
        self.assertIn('R1_OUTPUT_HARD_LOCK_CERTIFICATION_REQUIRED',text)
    def test_no_network_dependency(self):
        for name in ('acoustic_probe_macos.c','output_hard_denied.c','main.c'):
            text=(SRC/name).read_text()
            for bad in ('connect(', 'socket(', 'curl(', 'fetch(', 'http://', 'https://'):
                self.assertNotIn(bad,text)

class R2Execution(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bin=os.getenv('FREQMED_GEN_R2_BINARY')
    def execute(self,arg):
        if not self.bin:self.skipTest('Binary unavailable in current test host')
        return subprocess.run([self.bin,arg],capture_output=True,text=True,timeout=5)
    def test_status_output_denied(self):
        r=self.execute('status')
        self.assertEqual(0,r.returncode)
        doc=json.loads(r.stdout)
        self.assertEqual('NONE',doc['physical_emission'])
        self.assertEqual('NOT_LINKED_HARD_DENIED',doc['acoustic_output'])
    def test_selftest_fails_closed(self):
        r=self.execute('selftest');self.assertEqual(0,r.returncode)
        self.assertIn('CORE_AUDIO_OUTPUT_SYMBOLS=NOT_LINKED',r.stdout)
    def test_probe_does_not_report_physical_emission(self):
        r=self.execute('probe');self.assertEqual(0,r.returncode)
        doc=json.loads(r.stdout)
        self.assertEqual('NOT_CERTIFIED',doc['hardware_identity'])
        self.assertEqual('NOT_LINKED_HARD_DENIED',doc['output'])
    def test_unknown_action_denied(self):
        for arg in ('emit','start','--play','unlock'):
            r=self.execute(arg);self.assertNotEqual(0,r.returncode)
            self.assertIn('UNKNOWN_COMMAND_NO_OUTPUT',r.stderr)
