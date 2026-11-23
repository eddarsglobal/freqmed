# SPDX-License-Identifier: Apache-2.0
"""R60 bounded control lease software tests; never fake a physical output."""
import ctypes, http.client, importlib.util, json, pathlib, sys, tempfile, threading, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('freqmed_r60',ROOT/'app.py')
a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)

class CLease(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();cls.core=a.NativeCore(pathlib.Path(cls.tmp.name))
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def lease(self):return a.FMR60Lease()
 def bound(self):
  # A C session struct, used to exercise lease state logic only; no OS device
  # is invented or represented as measured equipment and no sound is produced.
  s=a.FMR59Session();s.phase=1;s.reason=0;s.device_id=7;s.channels=2;s.sample_rate_hz=44100.0
  s.command=a.FMCommand(1,440.,.01,500);s.digital_frame_budget=22050;s.name=b'CONTROL_TEST_ONLY'
  return s
 def test_01_initial_zero(self):self.assertEqual(self.core.get_r60_control_status()['state'],'UNBOUND')
 def test_02_main_output_denied(self):self.assertNotEqual(self.core.lib.fm_acoustic_physical_output(None),0)
 def test_03_no_em_output(self):self.assertNotEqual(self.core.lib.fm_em_physical_output(None),0)
 def test_04_no_input_begin(self):self.assertEqual(self.core.lib.fm_r60_lease_begin(None,None),-1)
 def test_05_null_current_rejected(self):self.assertEqual(self.core.lib.fm_r60_lease_begin(ctypes.byref(self.lease()),None),0)
 def test_06_unbound_rejected(self):self.assertEqual(self.core.lib.fm_r60_lease_begin(ctypes.byref(self.lease()),ctypes.byref(a.FMR59Session())),0)
 def test_07_valid_control_only(self):
  l=self.lease();s=self.bound();self.assertEqual(self.core.lib.fm_r60_lease_begin(ctypes.byref(l),ctypes.byref(s)),1);self.assertEqual(l.state,1)
 def test_08_valid_check(self):
  l=self.lease();s=self.bound();self.core.lib.fm_r60_lease_begin(ctypes.byref(l),ctypes.byref(s));self.assertEqual(self.core.lib.fm_r60_lease_check(ctypes.byref(l),ctypes.byref(s)),1)
 def test_09_renew(self):
  l=self.lease();s=self.bound();self.core.lib.fm_r60_lease_begin(ctypes.byref(l),ctypes.byref(s));g=l.generation;self.assertEqual(self.core.lib.fm_r60_lease_renew(ctypes.byref(l),ctypes.byref(s)),1);self.assertEqual(l.generation,g)
 def test_10_no_renew_after_revoke(self):
  l=self.lease();s=self.bound();self.core.lib.fm_r60_lease_begin(ctypes.byref(l),ctypes.byref(s));self.core.lib.fm_r60_lease_revoke(ctypes.byref(l),4);self.assertEqual(self.core.lib.fm_r60_lease_renew(ctypes.byref(l),ctypes.byref(s)),0)
 def test_11_stop_clears(self):
  l=self.lease();s=self.bound();self.core.lib.fm_r60_lease_begin(ctypes.byref(l),ctypes.byref(s));self.core.lib.fm_r60_lease_stop(ctypes.byref(l));self.assertEqual((l.state,l.bound.device_id,l.expires_at_ns),(4,0,0))
 def test_12_expire_without_wait(self):
  l=self.lease();s=self.bound();self.core.lib.fm_r60_lease_begin(ctypes.byref(l),ctypes.byref(s));l.expires_at_ns=1;self.assertEqual(self.core.lib.fm_r60_lease_check(ctypes.byref(l),ctypes.byref(s)),0);self.assertEqual(l.state,3)
 def test_13_ttl_never_renew_after_expiration(self):
  l=self.lease();s=self.bound();self.core.lib.fm_r60_lease_begin(ctypes.byref(l),ctypes.byref(s));l.expires_at_ns=1;self.assertEqual(self.core.lib.fm_r60_lease_renew(ctypes.byref(l),ctypes.byref(s)),0)
 def test_14_wrong_device(self):
  l=self.lease();s=self.bound();self.core.lib.fm_r60_lease_begin(ctypes.byref(l),ctypes.byref(s));s.device_id=8;self.assertEqual(self.core.lib.fm_r60_lease_check(ctypes.byref(l),ctypes.byref(s)),0);self.assertEqual(l.reason,2)
 def test_15_frequency_change(self):
  l=self.lease();s=self.bound();self.core.lib.fm_r60_lease_begin(ctypes.byref(l),ctypes.byref(s));s.command.frequency_hz=441.;self.assertEqual(self.core.lib.fm_r60_lease_check(ctypes.byref(l),ctypes.byref(s)),0)
 def test_16_duration_change(self):
  l=self.lease();s=self.bound();self.core.lib.fm_r60_lease_begin(ctypes.byref(l),ctypes.byref(s));s.command.duration_ms=600;self.assertEqual(self.core.lib.fm_r60_lease_check(ctypes.byref(l),ctypes.byref(s)),0)
 def test_17_level_change(self):
  l=self.lease();s=self.bound();self.core.lib.fm_r60_lease_begin(ctypes.byref(l),ctypes.byref(s));s.command.normalized_level=.02;self.assertEqual(self.core.lib.fm_r60_lease_check(ctypes.byref(l),ctypes.byref(s)),0)
 def test_18_frame_change(self):
  l=self.lease();s=self.bound();self.core.lib.fm_r60_lease_begin(ctypes.byref(l),ctypes.byref(s));s.digital_frame_budget=22051;self.assertEqual(self.core.lib.fm_r60_lease_check(ctypes.byref(l),ctypes.byref(s)),0)
 def test_19_no_unbounded_name(self):
  l=self.lease();s=self.bound();s.name=b'A'*127;self.assertEqual(self.core.lib.fm_r60_lease_begin(ctypes.byref(l),ctypes.byref(s)),1)
 def test_20_invalid_channel(self):
  l=self.lease();s=self.bound();s.command.channel=2;self.assertEqual(self.core.lib.fm_r60_lease_begin(ctypes.byref(l),ctypes.byref(s)),0)
 def test_21_generation_increases(self):
  l=self.lease();s=self.bound();self.core.lib.fm_r60_lease_begin(ctypes.byref(l),ctypes.byref(s));self.core.lib.fm_r60_lease_begin(ctypes.byref(l),ctypes.byref(s));self.assertEqual(l.generation,2)
 def test_22_generation_overflow_refused(self):
  l=self.lease();l.generation=2**64-1;s=self.bound();self.assertEqual(self.core.lib.fm_r60_lease_begin(ctypes.byref(l),ctypes.byref(s)),0)
 def test_23_null_check(self):self.assertEqual(self.core.lib.fm_r60_lease_check(None,None),-1)
 def test_24_null_renew(self):self.assertEqual(self.core.lib.fm_r60_lease_renew(None,None),-1)
 def test_25_stopped_not_ready(self):
  l=self.lease();s=self.bound();self.core.lib.fm_r60_lease_stop(ctypes.byref(l));self.assertEqual(self.core.lib.fm_r60_lease_check(ctypes.byref(l),ctypes.byref(s)),0)
 def test_26_app_status_no_output(self):self.assertEqual(self.core.get_r60_control_status()['physical_output'],'HARD_DENIED')
 def test_27_stopped_app(self):
  self.core.stop_engine_and_monitor();self.assertEqual(self.core.get_r60_control_status()['state'],'STOPPED')
 def test_28_explicit_invalidate(self):
  # R64: a prior operator STOP is sticky across unrelated invalidation.
  self.core.invalidate_r59_session();self.assertEqual(self.core.get_r60_control_status()['state'],'STOPPED')
 def test_29_no_audio_calls_in_module(self):
  code=(ROOT/'native/acoustic_control_lease_r60.c').read_text();self.assertNotIn('AudioQueueNewOutput(',code);self.assertNotIn('AudioQueueStart(',code)
 def test_30_no_em_calls_in_module(self):
  code=(ROOT/'native/acoustic_control_lease_r60.c').read_text();self.assertNotIn('fm_em_physical_output(',code)

class HTTP(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();cls.core=a.NativeCore(pathlib.Path(cls.tmp.name));cls.s=a.make_server(cls.core)
  cls.t=threading.Thread(target=cls.s.serve_forever,daemon=True);cls.t.start()
 @classmethod
 def tearDownClass(cls):cls.s.shutdown();cls.s.server_close();cls.t.join(3);cls.tmp.cleanup()
 def req(self,path):
  c=http.client.HTTPConnection('127.0.0.1',self.s.server_port,timeout=5)
  c.request('GET',path,headers={'Host':'127.0.0.1:'+str(self.s.server_port)});r=c.getresponse();data=r.read();status=r.status;c.close();return status,data
 def test_31_status_200(self):self.assertEqual(self.req('/api/acoustic/control/status')[0],200)
 def test_32_status_json(self):self.assertEqual(json.loads(self.req('/api/acoustic/control/status')[1])['valid_control_lease'],False)
 def test_33_main_status_includes_r60(self):self.assertIn(b'acoustic_control_r60',self.req('/api/status')[1])
 def test_34_r60_js_served(self):self.assertIn(b'CONTROL_STATUS_UNAVAILABLE',self.req('/r60.js')[1])
 def test_35_r60_css_served(self):self.assertIn(b'.fm-r60-lease',self.req('/r60.css')[1])
 def test_36_new_ui_honest(self):self.assertIn(b'id="r60-control-status"',self.req('/')[1])
 def test_37_no_start(self):self.assertEqual(self.req('/api/physical-start')[0],404)
 def test_38_ttl_status(self):self.assertEqual(json.loads(self.req('/api/acoustic/control/status')[1])['ttl_ms'],4000)
 def test_39_missing_measurement(self):self.assertEqual(json.loads(self.req('/api/acoustic/control/status')[1])['playback'],'NOT_PERFORMED')
 def test_40_mac_readonly_preserved(self):self.assertNotIn(b'AudioQueueNewOutput(', (ROOT/'native/acoustic_control_lease_r60.c').read_bytes())
 def test_41_no_rewrite_r54_js(self):self.assertIn('— Choisir une sortie audio —',(ROOT/'static/index.html').read_text())
 def test_42_history_present(self):self.assertTrue((ROOT/'historical/FREQMED_V5_DIRECT.html').exists())
 def test_43_status_api_not_mutating(self):
  a=json.loads(self.req('/api/acoustic/control/status')[1]);b=json.loads(self.req('/api/acoustic/control/status')[1]);self.assertEqual(a['generation'],b['generation'])
 def test_44_no_false_interlock(self):self.assertEqual(json.loads(self.req('/api/acoustic/control/status')[1])['physical_interlock'],'NOT_PRESENT_NOT_CERTIFIED')
