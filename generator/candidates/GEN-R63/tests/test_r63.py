# SPDX-License-Identifier: Apache-2.0
"""R63 tests are real C DSP computation, not fake output or metrology."""
import ctypes, pathlib, sys, tempfile, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import app

class R63DigitalPCM(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    cls.t=tempfile.TemporaryDirectory()
    cls.c=app.NativeCore(pathlib.Path(cls.t.name))

  @classmethod
  def tearDownClass(cls):cls.t.cleanup()

  def session(self,hz=440,level=.01,duration=500,rate=44100,channels=2,phase=1):
    s=app.FMR59Session();s.phase=phase;s.channels=channels;s.sample_rate_hz=rate
    s.command=app.FMCommand(1,hz,level,duration)
    s.digital_frame_budget=round(rate*duration/1000)
    return s

  def render(self,s):
    count=int(s.digital_frame_budget*s.channels)
    b=(ctypes.c_float*max(1,count))()
    report=app.FMR63DigitalReport()
    rc=self.c.lib.fm_r63_render_digital_pcm(ctypes.byref(s),b,count,ctypes.byref(report))
    return rc,b,report

  def test_01_real_digital_block(self):
    s=self.session();ok,b,r=self.render(s)
    self.assertEqual(ok,1);self.assertEqual(r.frames,22050);self.assertEqual(r.samples,44100)
    self.assertEqual(r.channels,2);self.assertLessEqual(r.digital_peak_normalized,.010001)
    self.assertEqual(b[0],0);self.assertEqual(b[1],0)
    self.assertEqual(b[-1],0);self.assertEqual(b[-2],0)
    self.assertTrue(any(abs(b[i])>.002 for i in range(1000,3000)))
    self.assertTrue(all(b[i]==b[i+1] for i in range(0,len(b),2)))
    self.c.lib.fm_r63_zeroize_digital_pcm(b,len(b));self.assertFalse(any(b))

  def test_02_refuse_unbound(self):self.assertEqual(self.render(self.session(phase=0))[0],0)
  def test_03_refuse_stopped(self):self.assertEqual(self.render(self.session(phase=3))[0],0)
  def test_04_refuse_invalidated(self):self.assertEqual(self.render(self.session(phase=2))[0],0)
  def test_05_refuse_excessive_level(self):self.assertEqual(self.render(self.session(level=.5))[0],0)
  def test_06_refuse_excessive_duration(self):self.assertEqual(self.render(self.session(duration=1500))[0],0)
  def test_07_refuse_invalid_rate(self):self.assertEqual(self.render(self.session(rate=100))[0],0)
  def test_08_refuse_nyquist(self):self.assertEqual(self.render(self.session(hz=23000))[0],0)
  def test_09_refuse_nan(self):self.assertEqual(self.render(self.session(hz=float('nan')))[0],0)
  def test_10_refuse_inf_level(self):self.assertEqual(self.render(self.session(level=float('inf')))[0],0)
  def test_11_refuse_mismatched_frame_budget(self):
    s=self.session();s.digital_frame_budget-=1;self.assertEqual(self.render(s)[0],0)
  def test_12_refuse_more_than_stereo(self):
    s=self.session(channels=3);self.assertEqual(self.render(s)[0],0)
  def test_13_refuse_null_pointer(self):
    r=app.FMR63DigitalReport();self.assertEqual(self.c.lib.fm_r63_render_digital_pcm(None,None,0,ctypes.byref(r)),0)
  def test_14_refuse_output_buffer_mismatch(self):
    s=self.session();b=(ctypes.c_float*5)();r=app.FMR63DigitalReport()
    self.assertEqual(self.c.lib.fm_r63_render_digital_pcm(ctypes.byref(s),b,5,ctypes.byref(r)),0)
  def test_15_no_physical_backend(self):
    self.assertEqual(self.c.lib.fm_acoustic_native_backend_available(),0)
    self.assertEqual(self.c.lib.fm_em_backend_available(),0)
  def test_16_http_prepare_refuses_without_route(self):
    with self.assertRaisesRegex(ValueError,'R63_NO_ACTIVE_REAL_ROUTE'):
      self.c.prepare_r63_digital_pcm()
  def test_17_route_uid_not_fabricated(self):
    self.assertFalse(self.c.get_r62_identity_status()['identity_confirmed_now'])
  def test_18_status_never_claims_physical_measurement(self):
    self.assertEqual(self.c.status()['physical_emission'],'NONE_BY_THIS_APPLICATION')
  def test_19_ui_assets_attached(self):
    html=(ROOT/'static/index.html').read_text()
    self.assertIn('/r63.js',html);self.assertIn('/r63.css',html)
    self.assertIn('id="r63-prepare"',html)
  def test_20_stop_disclaimer_hidden_at_idle(self):
    html=(ROOT/'static/index.html').read_text()
    self.assertIn('<p id="r55-stop-disclaimer" hidden>',html)
    js=(ROOT/'static/r55.js').read_text();self.assertIn("el('r55-stop-disclaimer').hidden=!hasActiveObserver",js)
  def test_21_no_playback_symbols(self):
    src=(ROOT/'native/acoustic_pcm_r63.c').read_text()
    for forbidden in ['AudioQueueStart','AudioQueueNewOutput','AudioUnitInitialize','system(','popen(']:
      self.assertNotIn(forbidden,src)
  def test_22_render_zero_frames_refused(self):
    s=self.session(duration=0);self.assertEqual(self.render(s)[0],0)
  def test_23_low_rate_pcm_refused(self):self.assertEqual(self.render(self.session(rate=4000))[0],0)
  def test_24_48k_pcm_success(self):
    s=self.session(rate=48000,duration=200);ok,b,r=self.render(s)
    self.assertEqual(ok,1);self.assertEqual(r.frames,9600)
    self.c.lib.fm_r63_zeroize_digital_pcm(b,len(b));self.assertFalse(any(b))

if __name__=='__main__':unittest.main()
