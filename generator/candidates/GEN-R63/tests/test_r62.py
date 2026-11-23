# SPDX-License-Identifier: Apache-2.0
"""R62 OS UID pin: control-state tests, not simulated devices or signals."""
import ctypes,importlib.util, pathlib, tempfile, unittest, http.client, json, threading, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('freqmed_r62', ROOT/'app.py')
a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)

class CIdentityChecks(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();cls.c=a.NativeCore(pathlib.Path(cls.tmp.name))
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def pin(self):return a.FMR62Identity()
 def test_01_zero_state(self):self.assertEqual(self.pin().state,0)
 def test_02_zero_reason(self):self.assertEqual(self.pin().reason,0)
 def test_03_zero_generation(self):self.assertEqual(self.pin().sequence,0)
 def test_04_null_pin_destination(self):self.assertEqual(self.c.lib.fm_r62_identity_pin(None,None),-1)
 def test_05_null_pin_session_fails(self):
  p=self.pin();self.assertEqual(self.c.lib.fm_r62_identity_pin(ctypes.byref(p),None),0);self.assertEqual(p.state,2)
 def test_06_invalid_session_fail_closed(self):
  p=self.pin();s=a.FMR59Session();self.assertEqual(self.c.lib.fm_r62_identity_pin(ctypes.byref(p),ctypes.byref(s)),0)
 def test_07_invalid_session_reason(self):
  p=self.pin();s=a.FMR59Session();self.c.lib.fm_r62_identity_pin(ctypes.byref(p),ctypes.byref(s));self.assertEqual(p.reason,3)
 def test_08_null_check(self):self.assertEqual(self.c.lib.fm_r62_identity_check(None,None),-1)
 def test_09_unbound_check_refused(self):
  p=self.pin();self.assertEqual(self.c.lib.fm_r62_identity_check(ctypes.byref(p),None),0)
 def test_10_invalidate_unbound(self):
  p=self.pin();self.c.lib.fm_r62_identity_invalidate(ctypes.byref(p),4);self.assertEqual((p.state,p.reason),(2,4))
 def test_11_invalidate_idempotent(self):
  p=self.pin();self.c.lib.fm_r62_identity_invalidate(ctypes.byref(p),3);self.c.lib.fm_r62_identity_invalidate(ctypes.byref(p),4);self.assertEqual(p.reason,3)
 def test_12_invalid_reason_defaults_safe(self):
  p=self.pin();self.c.lib.fm_r62_identity_invalidate(ctypes.byref(p),900);self.assertEqual(p.reason,4)
 def test_13_stop_clear(self):
  p=self.pin();self.c.lib.fm_r62_identity_stop(ctypes.byref(p));self.assertEqual((p.state,p.reason),(3,5))
 def test_14_stop_idempotent(self):
  p=self.pin();self.c.lib.fm_r62_identity_stop(ctypes.byref(p));self.c.lib.fm_r62_identity_stop(ctypes.byref(p));self.assertEqual(p.state,3)
 def test_15_invalidate_cannot_reopen_stopped(self):
  p=self.pin();self.c.lib.fm_r62_identity_stop(ctypes.byref(p));self.c.lib.fm_r62_identity_invalidate(ctypes.byref(p),1);self.assertEqual((p.state,p.reason),(3,5))
 def test_16_zero_private_uid_on_invalidate(self):
  p=self.pin();p.state=1;p.os_uid=b'CONTROL_TEST_PRIVATE_MEMORY';self.c.lib.fm_r62_identity_invalidate(ctypes.byref(p),4);self.assertEqual(bytes(p.os_uid),b'')
 def test_17_zero_private_uid_on_stop(self):
  p=self.pin();p.state=1;p.os_uid=b'CONTROL_TEST_PRIVATE_MEMORY';self.c.lib.fm_r62_identity_stop(ctypes.byref(p));self.assertEqual(bytes(p.os_uid),b'')
 def test_18_zero_command_on_stop(self):
  p=self.pin();p.command.frequency_hz=440.0;self.c.lib.fm_r62_identity_stop(ctypes.byref(p));self.assertEqual(p.command.frequency_hz,0)
 def test_19_zero_route_on_stop(self):
  p=self.pin();p.device_id=100;self.c.lib.fm_r62_identity_stop(ctypes.byref(p));self.assertEqual(p.device_id,0)
 def test_20_no_private_uid_on_json(self):self.assertNotIn('os_uid',self.c.get_r62_identity_status())
 def test_21_live_read_unbound(self):self.assertEqual(self.c.get_r62_identity_status()['state'],'UNBOUND')
 def test_22_hard_denied(self):self.assertEqual(self.c.get_r62_identity_status()['physical_output'],'HARD_DENIED')
 def test_23_no_playback(self):self.assertEqual(self.c.get_r62_identity_status()['playback'],'NOT_PERFORMED')
 def test_24_not_confirmed_without_pin(self):self.assertFalse(self.c.get_r62_identity_status()['identity_confirmed_now'])
 def test_25_no_uid_in_main_status(self):
  obj=self.c.status()['acoustic_identity_r62'];self.assertNotIn('os_uid',obj)
 def test_26_stop_to_stopped(self):
  with tempfile.TemporaryDirectory() as t:
   c=a.NativeCore(pathlib.Path(t));c.stop_engine_and_monitor();self.assertEqual(c.get_r62_identity_status()['state'],'STOPPED')
 def test_27_readonly_probe_no_output(self):self.assertNotEqual(self.c.lib.fm_acoustic_physical_output(None),0)
 def test_28_no_audioqueue_start(self):self.assertNotIn('AudioQueueStart(', (ROOT/'native/acoustic_identity_r62.c').read_text())
 def test_29_no_audioqueue_create(self):self.assertNotIn('AudioQueueNewOutput(', (ROOT/'native/acoustic_identity_r62.c').read_text())
 def test_30_no_rf_backend(self):self.assertNotIn('fm_em_physical_output(', (ROOT/'native/acoustic_identity_r62.c').read_text())
 def test_31_apple_sdk_only(self):
  content=(ROOT/'native/acoustic_identity_r62.c').read_text();self.assertIn('#if defined(__APPLE__)',content)
 def test_32_mac_uid_property(self):self.assertIn('kAudioDevicePropertyDeviceUID',(ROOT/'native/acoustic_identity_r62.c').read_text())
 def test_33_uid_not_logged(self):self.assertNotIn('printf(', (ROOT/'native/acoustic_identity_r62.c').read_text())
 def test_34_uid_not_persisted(self):self.assertNotIn('fopen(', (ROOT/'native/acoustic_identity_r62.c').read_text())
 def test_35_os_never_fake_on_linux(self):
  if not sys.platform.startswith('linux'):self.skipTest('Linux-only OS isolation negative test')
  p=self.pin();s=a.FMR59Session();s.phase=1;s.device_id=42;s.channels=2;s.sample_rate_hz=44100.0;s.name=b'UNIT_CONTROL_ONLY';s.command.channel=1
  self.assertEqual(self.c.lib.fm_r62_identity_pin(ctypes.byref(p),ctypes.byref(s)),0)
  self.assertEqual((p.state,p.reason),(2,1))
 def test_36_readable_status_privacy_flag(self):self.assertTrue(self.c.get_r62_identity_status()['os_uid_private_not_disclosed'])
 def test_37_no_emission_code_linked(self):self.assertEqual(self.c.lib.fm_acoustic_native_backend_available(),0)
 def test_38_private_uid_cap(self):self.assertEqual(len(self.pin().os_uid),0)

class HTTPIdentityChecks(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();cls.c=a.NativeCore(pathlib.Path(cls.tmp.name));cls.s=a.make_server(cls.c)
  cls.t=threading.Thread(target=cls.s.serve_forever,daemon=True);cls.t.start()
 @classmethod
 def tearDownClass(cls):cls.s.shutdown();cls.s.server_close();cls.t.join(5);cls.tmp.cleanup()
 def call(self,path):
  con=http.client.HTTPConnection('127.0.0.1',self.s.server_port,timeout=7);con.request('GET',path,headers={'Host':'127.0.0.1:'+str(self.s.server_port)})
  r=con.getresponse();body=r.read();status=r.status;con.close();return status,body
 def test_39_endpoint_status(self):self.assertEqual(self.call('/api/acoustic/identity/status')[0],200)
 def test_40_endpoint_json(self):self.assertEqual(json.loads(self.call('/api/acoustic/identity/status')[1])['state'],'UNBOUND')
 def test_41_api_no_private_uid(self):self.assertNotIn(b'CONTROL_TEST_PRIVATE_MEMORY',self.call('/api/acoustic/identity/status')[1])
 def test_42_asset_js(self):self.assertIn(b'CoreAudio identity',self.call('/r62.js')[1])
 def test_43_asset_css(self):self.assertIn(b'.fm-r62-identity',self.call('/r62.css')[1])
 def test_44_ui_indicator(self):self.assertIn(b'id="r62-identity-status"',self.call('/')[1])
 def test_45_ui_identity_version(self):self.assertIn(b'v0.8.0',self.call('/')[1])
 def test_46_main_api_contains_r62(self):self.assertIn(b'acoustic_identity_r62',self.call('/api/status')[1])
 def test_47_no_uid_property_in_json(self):self.assertNotIn(b'os_uid":',self.call('/api/status')[1])
 def test_48_no_physical_start(self):self.assertEqual(self.call('/api/physical-start')[0],404)
 def test_49_manifest_hashes(self):self.assertGreater(a.verify_manifest(),59)
 def test_50_ten_languages(self):
  js=(ROOT/'static/r62.js').read_text()
  for lang in ('fr:','en:','de:','ar:','es:','pt:','hr:','it:','zh:','ko:'):self.assertIn(lang,js)
 def test_51_uid_not_in_ui_text(self):self.assertNotIn(b'os_uid',self.call('/')[1])
 def test_52_native_r61_inherited(self):self.assertTrue((ROOT/'native/acoustic_fault_latch_r61.c').is_file())
 def test_53_r54_fixed_placeholder(self):self.assertIn(b'\xe2\x80\x94 Choisir une sortie audio',(ROOT/'static/index.html').read_bytes())
 def test_54_r58_source_pins(self):self.assertTrue((ROOT/'SOURCE_PINS_R58.json').is_file())
 def test_55_lifecycle_bind_guard(self):self.assertIn('R62_COREAUDIO_IDENTITY_PIN_REFUSED',(ROOT/'app.py').read_text())
 def test_56_unchanged_physical_denial(self):self.assertIn('HARD_DENIED',(ROOT/'native/output_hard_denied.c').read_text()) if 'HARD_DENIED' in (ROOT/'native/output_hard_denied.c').read_text() else self.assertIn('return -1',(ROOT/'native/output_hard_denied.c').read_text())
