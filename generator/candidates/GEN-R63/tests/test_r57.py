# SPDX-License-Identifier: Apache-2.0
import ctypes, http.client, importlib.util, json, pathlib, tempfile, threading, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("freqmed_r57",ROOT/"app.py")
a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
CMD={"channel":"acoustic","hz":440.0,"level":0.01,"duration_ms":500}
class R57Core(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.t=tempfile.TemporaryDirectory();cls.c=a.NativeCore(pathlib.Path(cls.t.name))
 @classmethod
 def tearDownClass(cls):cls.t.cleanup()
 def test_01_symbol_is_linked(self):self.assertTrue(hasattr(self.c.lib,'fm_r57_backend_route_check'))
 def test_02_result_struct_size(self):self.assertEqual(ctypes.sizeof(a.FMR57BackendRouteCheck),24)
 def test_03_default_flag_offset(self):self.assertEqual(a.FMR57BackendRouteCheck.default_route_matches.offset,4)
 def test_04_frames_offset(self):self.assertEqual(a.FMR57BackendRouteCheck.digital_frame_budget.offset,16)
 def test_05_empty_status(self):self.assertFalse(self.c.get_r57_backend_status()['checked'])
 def test_06_requires_route(self):
  with self.assertRaisesRegex(ValueError,'SELECT_REAL_COREAUDIO_OUTPUT_FIRST'):self.c.r57_backend_check(CMD)
 def test_07_reject_em(self):
  with self.assertRaisesRegex(ValueError,'ONLY_ACOUSTIC_CHANNEL_SUPPORTED'):self.c.r57_backend_check(dict(CMD,channel='em'))
 def test_08_reject_extra_authorization(self):
  with self.assertRaisesRegex(ValueError,'INVALID_BACKEND_CONTRACT_SCHEMA'):self.c.r57_backend_check(dict(CMD,unlock=True))
 def test_09_reject_bool_frequency(self):
  with self.assertRaisesRegex(ValueError,'INVALID_NUMERIC_TYPE'):self.c.r57_backend_check(dict(CMD,hz=True))
 def test_10_reject_nan(self):
  with self.assertRaisesRegex(ValueError,'INVALID_NUMERIC_RANGE'):self.c.r57_backend_check(dict(CMD,hz=float('nan')))
 def test_11_refuses_os_fake_device(self):
  out=a.FMR57BackendRouteCheck();cmd=a.FMCommand(1,440.,.01,500)
  rc=self.c.lib.fm_r57_backend_route_check(ctypes.byref(cmd),4294967295,b'fabricated',2,44100.,ctypes.byref(out))
  self.assertEqual(rc,0);self.assertIn(out.result_code,(3,4));self.assertEqual(out.default_route_matches,0)
 def test_12_output_stays_denied(self):
  self.assertEqual(self.c.lib.fm_acoustic_native_backend_available(),0);self.assertNotEqual(self.c.lib.fm_acoustic_physical_output(None),0)
 def test_13_never_em(self):self.assertEqual(self.c.lib.fm_em_backend_available(),0)
 def test_14_os_default_is_not_assumed(self):
  source=(ROOT/'native/acoustic_backend_route_r57.c').read_text()
  self.assertIn('kAudioHardwarePropertyDefaultOutputDevice',source);self.assertIn('before!=expected_device_id',source)
 def test_15_no_audiostart_in_bridge(self):
  source=(ROOT/'native/acoustic_backend_route_r57.c').read_text()
  for forbidden in ('AudioQueueStart','AudioQueueNewOutput','AudioDeviceStart','AudioQueueEnqueueBuffer'):
   self.assertNotIn(forbidden,source)
 def test_16_c_real_os_nondefault_refusal_branch(self):
  source=(ROOT/'native/acoustic_backend_route_r57.c').read_text();self.assertIn('out->result_code=8',source)
 def test_17_stop_clears_record(self):
  self.c.r57_backend={"route":{},"command":{}};self.c.stop();self.assertFalse(self.c.get_r57_backend_status()['checked'])
 def test_18_engine_stop_clears_record(self):
  self.c.r57_backend={"route":{},"command":{}};self.c.stop_engine_and_monitor();self.assertFalse(self.c.get_r57_backend_status()['checked'])
 def test_19_r56_preflight_clears_r57(self):
  self.c.resume_route_monitor();self.c.r57_backend={"route":{},"command":{}}
  with self.assertRaisesRegex(ValueError,'SELECT_REAL_COREAUDIO_OUTPUT_FIRST'):self.c.acoustic_preflight(CMD)
  self.assertFalse(self.c.get_r57_backend_status()['checked'])
 def test_20_manifest_integrity(self):self.assertGreater(a.verify_manifest(),28)
 def test_21_status_discloses_no_output(self):
  s=self.c.status();self.assertEqual(s['acoustic_output'],'NOT_LINKED_HARD_DENIED');self.assertFalse(s['acoustic_backend_contract']['checked'])
 def test_22_ffi_struct_matches_header(self):
  h=(ROOT/'native/acoustic_backend_route_r57.h').read_text();self.assertIn('FMR57BackendRouteCheck',h)
 def test_23_original_file_stays_unlinked(self):self.assertFalse((ROOT/'native/acoustic_macos.c').exists())
 def test_24_no_persisted_device_uid(self):
  s=(ROOT/'app.py').read_text();self.assertNotIn('kAudioQueueProperty_CurrentDevice',s)
class R57HTTP(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.t=tempfile.TemporaryDirectory();cls.c=a.NativeCore(pathlib.Path(cls.t.name));cls.s=a.make_server(cls.c)
  cls.th=threading.Thread(target=cls.s.serve_forever,daemon=True);cls.th.start()
 @classmethod
 def tearDownClass(cls):cls.s.shutdown();cls.s.server_close();cls.th.join(3);cls.t.cleanup()
 def req(self,m,path,body=None,auth=False):
  conn=http.client.HTTPConnection('127.0.0.1',self.s.server_port,timeout=5)
  headers={'Host':f'127.0.0.1:{self.s.server_port}'}
  if body is not None:headers['Content-Type']='application/json';body=json.dumps(body)
  if auth:headers['Origin']=f'http://127.0.0.1:{self.s.server_port}';headers['X-FREQMED-SESSION']=self.s.token
  conn.request(m,path,body=body,headers=headers);resp=conn.getresponse();data=resp.read();code=resp.status;conn.close()
  return code,json.loads(data) if path.startswith('/api/') else data
 def test_25_get_status(self):
  code,b=self.req('GET','/api/acoustic/backend/status');self.assertEqual(code,200);self.assertFalse(b['checked'])
 def test_26_post_needs_auth(self):
  code,_=self.req('POST','/api/acoustic/backend/inspect',CMD);self.assertEqual(code,403)
 def test_27_missing_route_fails_closed(self):
  code,b=self.req('POST','/api/acoustic/backend/inspect',CMD,True);self.assertEqual(code,422);self.assertIn('SELECT_REAL_COREAUDIO_OUTPUT_FIRST',b['error'])
 def test_28_unapproved_em_refused(self):
  code,b=self.req('POST','/api/acoustic/backend/inspect',dict(CMD,channel='em'),True);self.assertEqual(code,422)
 def test_29_no_physical_start_route(self):
  code,_=self.req('POST','/api/physical-start',{},True);self.assertEqual(code,404)
 def test_30_new_js_served(self):
  code,b=self.req('GET','/r57.js');self.assertEqual(code,200);self.assertIn(b'/api/acoustic/backend/inspect',b)
 def test_31_new_css_served(self):
  code,b=self.req('GET','/r57.css');self.assertEqual(code,200);self.assertIn(b'.r57-panel',b)
 def test_32_new_ui_rendered(self):
  code,b=self.req('GET','/');self.assertEqual(code,200);self.assertIn(b'id="r57-inspect"',b)
 def test_33_session_boundary(self):
  code,b=self.req('POST','/api/acoustic/backend/inspect',CMD,True);self.assertEqual(code,422)
  con=http.client.HTTPConnection('127.0.0.1',self.s.server_port,timeout=5)
  con.request('POST','/api/acoustic/backend/inspect',body=json.dumps(CMD),headers={'Host':f'127.0.0.1:{self.s.server_port}','Origin':'http://other.invalid','X-FREQMED-SESSION':self.s.token,'Content-Type':'application/json'})
  r=con.getresponse();r.read();self.assertEqual(r.status,403);con.close()
 def test_34_status_no_certification(self):
  code,b=self.req('GET','/api/status');self.assertEqual(code,200);self.assertEqual(b['production'],'NOT_AUTHORIZED')
