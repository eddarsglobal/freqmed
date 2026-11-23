# SPDX-License-Identifier: Apache-2.0
"""GEN-R61 state-machine/software safety checks, NO physical-output experiment."""
import ctypes, http.client, importlib.util, json, pathlib, tempfile, threading, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('freqmed_r61', ROOT/'app.py')
a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)

class NativeFaultLatch(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();cls.c=a.NativeCore(pathlib.Path(cls.tmp.name))
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def fault(self):return a.FMR61Fault()
 def trip(self,f,reason=1):return self.c.lib.fm_r61_fault_trip(ctypes.byref(f),reason)
 def ack(self,f,route=1,session=1,monitor=1):return self.c.lib.fm_r61_fault_ack(ctypes.byref(f),route,session,monitor)
 def test_01_zero_state(self):self.assertEqual(self.fault().state,0)
 def test_02_clear_can_bind(self):self.assertEqual(self.c.lib.fm_r61_fault_can_bind(ctypes.byref(self.fault())),1)
 def test_03_trip_os(self):
  f=self.fault();self.assertEqual(self.trip(f,1),1);self.assertEqual((f.state,f.reason,f.fault_sequence),(1,1,1))
 def test_04_trip_route_changed(self):
  f=self.fault();self.trip(f,2);self.assertEqual(f.reason,2)
 def test_05_trip_native_session(self):
  f=self.fault();self.trip(f,3);self.assertEqual(f.reason,3)
 def test_06_trip_lease_expired(self):
  f=self.fault();self.trip(f,4);self.assertEqual(f.reason,4)
 def test_07_trip_integrity(self):
  f=self.fault();self.trip(f,5);self.assertEqual(f.reason,5)
 def test_08_trip_invalid_reason_fails_closed(self):
  f=self.fault();self.trip(f,999);self.assertEqual(f.reason,5)
 def test_09_trip_idempotent(self):
  f=self.fault();self.trip(f,1);self.assertEqual(self.trip(f,2),0);self.assertEqual((f.reason,f.fault_sequence),(1,1))
 def test_10_stop_preserves_latched_fault(self):
  f=self.fault();self.trip(f,2);self.c.lib.fm_r61_fault_stop(ctypes.byref(f));self.assertEqual((f.state,f.reason),(1,2))
 def test_11_stop_clear_state(self):
  f=self.fault();self.c.lib.fm_r61_fault_stop(ctypes.byref(f));self.assertEqual((f.state,f.reason),(2,6))
 def test_12_stop_blocks_binding(self):
  f=self.fault();self.c.lib.fm_r61_fault_stop(ctypes.byref(f));self.assertEqual(self.c.lib.fm_r61_fault_can_bind(ctypes.byref(f)),0)
 def test_13_resume_operator_stop_only(self):
  f=self.fault();self.c.lib.fm_r61_fault_stop(ctypes.byref(f));self.assertEqual(self.c.lib.fm_r61_fault_resume_observation(ctypes.byref(f)),1);self.assertEqual(f.state,0)
 def test_14_resume_never_clears_latched_fault(self):
  f=self.fault();self.trip(f,1);self.assertEqual(self.c.lib.fm_r61_fault_resume_observation(ctypes.byref(f)),0);self.assertEqual(f.state,1)
 def test_15_ack_no_fault_refused(self):self.assertEqual(self.ack(self.fault()),0)
 def test_16_ack_route_not_clear_refused(self):
  f=self.fault();self.trip(f);self.assertEqual(self.ack(f,0,1,1),0);self.assertEqual(f.state,1)
 def test_17_ack_session_not_clear_refused(self):
  f=self.fault();self.trip(f);self.assertEqual(self.ack(f,1,0,1),0);self.assertEqual(f.state,1)
 def test_18_ack_monitor_not_live_refused(self):
  f=self.fault();self.trip(f);self.assertEqual(self.ack(f,1,1,0),0);self.assertEqual(f.state,1)
 def test_19_ack_requires_exact_boolean_true(self):
  f=self.fault();self.trip(f);self.assertEqual(self.ack(f,2,1,1),0);self.assertEqual(f.state,1)
 def test_20_ack_explicit_releases_only_control_latch(self):
  f=self.fault();self.trip(f);self.assertEqual(self.ack(f),1);self.assertEqual((f.state,f.reason,f.fault_sequence),(0,0,1))
 def test_21_repeated_fault_generation(self):
  f=self.fault();self.trip(f);self.ack(f);self.trip(f,2);self.assertEqual(f.fault_sequence,2)
 def test_22_fault_generation_saturates(self):
  f=self.fault();f.fault_sequence=2**64-1;self.trip(f);self.assertEqual(f.fault_sequence,2**64-1)
 def test_23_null_trip(self):self.assertEqual(self.c.lib.fm_r61_fault_trip(None,1),-1)
 def test_24_null_ack(self):self.assertEqual(self.c.lib.fm_r61_fault_ack(None,1,1,1),-1)
 def test_25_null_resume(self):self.assertEqual(self.c.lib.fm_r61_fault_resume_observation(None),-1)
 def test_26_null_bind(self):self.assertEqual(self.c.lib.fm_r61_fault_can_bind(None),0)
 def test_27_main_output_denied(self):self.assertNotEqual(self.c.lib.fm_acoustic_physical_output(None),0)
 def test_28_r61_no_output_api(self):
  code=(ROOT/'native/acoustic_fault_latch_r61.c').read_text()
  for forbidden in ('AudioQueueNewOutput(', 'AudioQueueStart(', 'fm_acoustic_physical_output(', 'fm_em_physical_output('):self.assertNotIn(forbidden,code)
 def test_29_status_unbound(self):
  self.assertEqual(self.c.get_r61_fault_status()['state'],'NORMAL_NO_OUTPUT')
 def test_30_status_hard_denied(self):self.assertEqual(self.c.get_r61_fault_status()['physical_output'],'HARD_DENIED')
 def test_31_stop_state_app(self):
  self.c.stop_engine_and_monitor();self.assertEqual(self.c.get_r61_fault_status()['state'],'STOPPED')
 def test_32_unmonitored_ack_rejected(self):
  c=self.c
  with c.lock:
   c.lib.fm_r61_fault_trip(ctypes.byref(c.r61_fault),2)
  c._snapshot=lambda:{'observed':True,'devices':[],'truncated':False}
  with self.assertRaisesRegex(ValueError,'R61_RESUME_REAL_OS_MONITOR_FIRST'):c.acknowledge_r61_fault()
 def test_33_bad_os_probe_latches_and_clears(self):
  # Error injection to test fail-closed state only; NOT a device or measurement simulation.
  with tempfile.TemporaryDirectory() as t:
   c=a.NativeCore(pathlib.Path(t));c.route={'device_id':100,'name':'TEST_CONTROL_ONLY', 'channels':2,'nominal_sample_rate_hz':44100.0}
   c._snapshot=lambda: None
   c.route_watch_tick()
   self.assertEqual(c.get_r61_fault_status()['reason'],'OS_UNAVAILABLE')
   self.assertIsNone(c.route)
   self.assertEqual(c.get_r59_session_status()['route_bound'],False)
   self.assertEqual(c.get_r60_control_status()['valid_control_lease'],False)
 def test_34_stop_does_not_erase_fault_app(self):
  with tempfile.TemporaryDirectory() as t:
   c=a.NativeCore(pathlib.Path(t))
   with c.lock:c.lib.fm_r61_fault_trip(ctypes.byref(c.r61_fault),2)
   c.stop_engine_and_monitor();self.assertEqual(c.get_r61_fault_status()['state'],'FAULT_LATCHED')
 def test_35_rearm_after_stop_only(self):
  with tempfile.TemporaryDirectory() as t:
   c=a.NativeCore(pathlib.Path(t));c.stop_engine_and_monitor()
   c.resume_route_monitor();self.assertEqual(c.get_r61_fault_status()['state'],'NORMAL_NO_OUTPUT')
   c.stop_route_monitor()
 def test_36_ack_authenticated_control_requires_live_monitor(self):
  with tempfile.TemporaryDirectory() as t:
   c=a.NativeCore(pathlib.Path(t))
   with c.lock:c.lib.fm_r61_fault_trip(ctypes.byref(c.r61_fault),1)
   c.start_route_monitor()
   # Unit-level fresh-registry guard: an empty observed registry has NO fake device.
   # The production path always calls native CoreAudio, never this test stub.
   c._snapshot=lambda:{'observed':True,'devices':[],'truncated':False}
   self.assertEqual(c.acknowledge_r61_fault()['state'],'NORMAL_NO_OUTPUT')
   c.stop_route_monitor()

class HTTPFault(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();cls.c=a.NativeCore(pathlib.Path(cls.tmp.name));cls.s=a.make_server(cls.c)
  cls.t=threading.Thread(target=cls.s.serve_forever,daemon=True);cls.t.start()
 @classmethod
 def tearDownClass(cls):cls.s.shutdown();cls.s.server_close();cls.t.join(4);cls.tmp.cleanup()
 def call(self,method,path,payload=None,authorized=False,origin=True):
  c=http.client.HTTPConnection('127.0.0.1',self.s.server_port,timeout=7)
  headers={'Host':'127.0.0.1:'+str(self.s.server_port)}
  body=None
  if method=='POST':
   headers['Content-Type']='application/json';body=json.dumps(payload if payload is not None else {})
   if origin:headers['Origin']='http://127.0.0.1:'+str(self.s.server_port)
   if authorized:headers['X-FREQMED-SESSION']=self.s.token
  c.request(method,path,body=body,headers=headers);r=c.getresponse();out=(r.status,r.read());c.close();return out
 def test_37_fault_status_200(self):self.assertEqual(self.call('GET','/api/acoustic/fault/status')[0],200)
 def test_38_fault_status_json(self):self.assertEqual(json.loads(self.call('GET','/api/acoustic/fault/status')[1])['state'],'NORMAL_NO_OUTPUT')
 def test_39_main_status_includes_r61(self):self.assertIn(b'acoustic_fault_r61',self.call('GET','/api/status')[1])
 def test_40_js_served(self):self.assertIn(b'FAULT LATCHED',self.call('GET','/r61.js')[1])
 def test_41_css_served(self):self.assertIn(b'.fm-r61-fault',self.call('GET','/r61.css')[1])
 def test_42_ui_has_status_and_button(self):
  html=self.call('GET','/')[1];self.assertIn(b'id="r61-fault-status"',html);self.assertIn(b'id="r61-fault-ack"',html)
 def test_43_post_without_token_rejected(self):self.assertEqual(self.call('POST','/api/acoustic/fault/ack',{})[0],403)
 def test_44_post_wrong_origin_rejected(self):self.assertEqual(self.call('POST','/api/acoustic/fault/ack',{},True,False)[0],403)
 def test_45_empty_payload_required(self):self.assertEqual(self.call('POST','/api/acoustic/fault/ack',{'x':1},True)[0],422)
 def test_46_no_fault_to_ack_rejected(self):self.assertEqual(self.call('POST','/api/acoustic/fault/ack',{},True)[0],422)
 def test_47_status_get_no_state_mutation(self):
  x=json.loads(self.call('GET','/api/acoustic/fault/status')[1]);y=json.loads(self.call('GET','/api/acoustic/fault/status')[1]);self.assertEqual(x['fault_sequence'],y['fault_sequence'])
 def test_48_physical_start_absent(self):self.assertEqual(self.call('GET','/api/physical-start')[0],404)
 def test_49_ten_translations(self):
  js=(ROOT/'static/r61.js').read_text()
  for lang in ('fr:','en:','de:','ar:','es:','pt:','hr:','it:','zh:','ko:'):self.assertIn(lang,js)
 def test_50_native_only_no_emission(self):
  self.assertIn('"HARD_DENIED"',(ROOT/'app.py').read_text())

class RecoveryGuard(unittest.TestCase):
 def test_51_absent_os_observation_refuses_ack(self):
  with tempfile.TemporaryDirectory() as t:
   c=a.NativeCore(pathlib.Path(t))
   with c.lock:c.lib.fm_r61_fault_trip(ctypes.byref(c.r61_fault),1)
   c._snapshot=lambda: None
   with self.assertRaisesRegex(ValueError,'R61_REAL_COREAUDIO_RECOVERY_NOT_CONFIRMED'):c.acknowledge_r61_fault()
 def test_52_truncated_os_observation_refuses_ack(self):
  with tempfile.TemporaryDirectory() as t:
   c=a.NativeCore(pathlib.Path(t))
   with c.lock:c.lib.fm_r61_fault_trip(ctypes.byref(c.r61_fault),1)
   c._snapshot=lambda:{'observed':True,'devices':[],'truncated':True}
   with self.assertRaisesRegex(ValueError,'R61_REAL_COREAUDIO_RECOVERY_NOT_CONFIRMED'):c.acknowledge_r61_fault()

class GuardianResetRegression(unittest.TestCase):
 def test_53_reset_while_monitor_running_does_not_strand_r61(self):
  with tempfile.TemporaryDirectory() as t:
   c=a.NativeCore(pathlib.Path(t))
   c.stop()  # Original GUI Guardian reset, NOT watchdog STOP.
   self.assertEqual(c.get_r61_fault_status()['state'],'NORMAL_NO_OUTPUT')
 def test_54_reset_does_not_clear_existing_fault(self):
  with tempfile.TemporaryDirectory() as t:
   c=a.NativeCore(pathlib.Path(t))
   with c.lock:c.lib.fm_r61_fault_trip(ctypes.byref(c.r61_fault),2)
   c.stop()
   self.assertEqual(c.get_r61_fault_status()['state'],'FAULT_LATCHED')
