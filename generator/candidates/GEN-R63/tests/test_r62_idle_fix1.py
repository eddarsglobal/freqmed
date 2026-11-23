# SPDX-License-Identifier: Apache-2.0
"""No unsolicited monitoring: real CoreAudio remains read-only; no emitted signal."""
import importlib.util, pathlib, tempfile, unittest, time, threading
R=pathlib.Path(__file__).resolve().parents[1]
sp=importlib.util.spec_from_file_location('freqmed_r62_idle_fix1',R/'app.py')
a=importlib.util.module_from_spec(sp);sp.loader.exec_module(a)
class IdleFix(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.t=tempfile.TemporaryDirectory();cls.c=a.NativeCore(pathlib.Path(cls.t.name))
 @classmethod
 def tearDownClass(cls):cls.c.stop_route_monitor();cls.t.cleanup()
 def test_01_no_monitor_started_at_init(self):
  s=self.c.route_monitor_status();self.assertEqual((s['checks'],s['monitor_state'],s['monitor_running']),(0,'IDLE',False))
 def test_02_no_route_manual_watch_no_os_poll(self):
  s=self.c.route_watch_tick();self.assertEqual(s['checks'],0);self.assertEqual(s['last_os_poll'],'NOT_CHECKED')
 def test_03_no_route_background_monitor_cannot_poll(self):
  self.assertTrue(self.c.start_route_monitor(.5));time.sleep(.75)
  s=self.c.route_monitor_status();self.assertEqual(s['monitor_state'],'IDLE');self.assertEqual(s['checks'],0)
 def test_04_no_route_get_cannot_increase(self):
  s=self.c.route_monitor_status()['checks'];time.sleep(.6);self.assertEqual(self.c.route_monitor_status()['checks'],s)
 def test_05_no_route_coreaudio_dropdown_still_available(self):
  self.assertIn('observed',self.c.audio_devices());self.assertEqual(self.c.route_monitor_status()['checks'],0)
 def test_06_stop_state(self):
  r=self.c.stop_engine_and_monitor();self.assertEqual(r['monitor_state'],'STOPPED');self.assertEqual(r['monitor_checks_frozen_at'],0)
 def test_07_resume_no_route_stays_idle(self):
  self.assertEqual(self.c.resume_route_monitor()['monitor_state'],'IDLE');self.assertEqual(self.c.route_monitor_status()['checks'],0)
 def test_08_after_resume_no_unsolicited_checks(self):
  time.sleep(.6);self.assertEqual(self.c.route_monitor_status()['checks'],0)
 def test_09_native_off(self):
  self.assertNotEqual(self.c.lib.fm_acoustic_physical_output(None),0);self.assertNotEqual(self.c.lib.fm_em_physical_output(None),0)
 def test_10_selection_starts_observer_source_contract(self):
  src=(R/'app.py').read_text();sel=src[src.index('    def select_audio(self, payload):'):src.index('    def clear_audio(self):')]
  self.assertIn('self.start_route_monitor(interval_seconds=1.2)',sel)
 def test_11_main_no_auto_start(self):
  src=(R/'app.py').read_text();main=src[src.index('def main():'):];self.assertNotIn('core.start_route_monitor(interval_seconds=1.2)',main)
 def test_12_selftest_reset_event_and_counter(self):
  src=(R/'app.py').read_text();main=src[src.index('def main():'):]
  for literal in ('core.route_monitor_ticks = 0','core.route_monitor_event = "NO_SELECTION"','core._monitor_shutdown.clear()'):self.assertIn(literal,main)
 def test_13_frontend_idle_translation(self):
  js=(R/'static/r55.js').read_text();self.assertIn('idleText',js);self.assertIn("value.monitor_state==='IDLE'",js)
 def test_14_no_audio_queue(self):
  src=(R/'app.py').read_text();self.assertNotIn('AudioQueueStart',src)
 def test_15_manifest_inherited(self):
  self.assertGreaterEqual(a.verify_manifest(),64)
 def test_16_resume_hidden_at_idle(self):
  js=(R/'static/r55.js').read_text()
  self.assertIn("value.monitor_state!=='STOPPED'",js)
 def test_17_status_has_no_previous_test_stop_event(self):
  source=(R/'app.py').read_text()
  self.assertIn('core.route_monitor_event = "NO_SELECTION"',source)

