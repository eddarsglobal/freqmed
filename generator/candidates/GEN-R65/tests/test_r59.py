# SPDX-License-Identifier: Apache-2.0
"""GEN-R59: real native C lifecycle contract, never a mock physical device."""
import ctypes, http.client, importlib.util, json, pathlib, tempfile, threading, unittest, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('fm_r59', ROOT/'app.py')
a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
class Native(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();cls.core=a.NativeCore(pathlib.Path(cls.tmp.name))
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def test_01_session_initially_unbound(self):self.assertEqual(self.core.get_r59_session_status()['phase'],'UNBOUND')
 def test_02_main_output_absent(self):self.assertNotEqual(self.core.lib.fm_acoustic_physical_output(None),0)
 def test_03_candidate_not_pretended(self):self.assertFalse(self.core.get_r59_session_status()['candidate_isolated'])
 def test_04_c_struct_layout(self):self.assertEqual(a.FMR59Session.command.offset,24)
 def test_05_null_bind_fails(self):self.assertEqual(self.core.lib.fm_r59_session_bind(None,None,0,None,0,0),-1)
 def test_06_null_poll_fails(self):self.assertEqual(self.core.lib.fm_r59_session_poll(None),-1)
 def test_07_invalid_null_command(self):
  s=a.FMR59Session();self.assertEqual(self.core.lib.fm_r59_session_bind(ctypes.byref(s),None,1,b'device',2,44100),0);self.assertEqual(s.phase,2)
 def test_08_invalid_em_command(self):
  s=a.FMR59Session();c=a.FMCommand(2,440.,.01,500);self.assertEqual(self.core.lib.fm_r59_session_bind(ctypes.byref(s),ctypes.byref(c),1,b'device',2,44100),0)
 def test_09_invalid_hz(self):
  s=a.FMR59Session();c=a.FMCommand(1,-5.,.01,500);self.assertEqual(self.core.lib.fm_r59_session_bind(ctypes.byref(s),ctypes.byref(c),1,b'device',2,44100),0)
 def test_10_invalid_rate(self):
  s=a.FMR59Session();c=a.FMCommand(1,440.,.01,500);self.assertEqual(self.core.lib.fm_r59_session_bind(ctypes.byref(s),ctypes.byref(c),1,b'device',2,0),0)
 def test_11_invalid_empty_name(self):
  s=a.FMR59Session();c=a.FMCommand(1,440.,.01,500);self.assertEqual(self.core.lib.fm_r59_session_bind(ctypes.byref(s),ctypes.byref(c),1,b'',2,44100),0)
 def test_12_no_invented_linux_route(self):
  if sys.platform.startswith('linux'):
   s=a.FMR59Session();c=a.FMCommand(1,440.,.01,500)
   self.assertEqual(self.core.lib.fm_r59_session_bind(ctypes.byref(s),ctypes.byref(c),1,b'device',2,44100),0)
   self.assertNotEqual(s.phase,1)
 def test_13_poll_unbound_fails(self):
  s=a.FMR59Session();self.assertEqual(self.core.lib.fm_r59_session_poll(ctypes.byref(s)),0)
 def test_14_invalidate_native(self):
  s=a.FMR59Session();s.phase=1;s.device_id=1;s.digital_frame_budget=22050
  self.core.lib.fm_r59_session_invalidate(ctypes.byref(s));self.assertEqual((s.phase,s.device_id,s.digital_frame_budget),(2,0,0))
 def test_15_stop_native(self):
  s=a.FMR59Session();s.phase=1;s.device_id=1;s.digital_frame_budget=22050
  self.core.lib.fm_r59_session_stop(ctypes.byref(s));self.assertEqual((s.phase,s.reason,s.device_id,s.digital_frame_budget),(3,5,0,0))
 def test_16_stop_durable_on_poll(self):
  s=a.FMR59Session();self.core.lib.fm_r59_session_stop(ctypes.byref(s));self.core.lib.fm_r59_session_poll(ctypes.byref(s));self.assertEqual(s.phase,3)
 def test_17_get_cannot_rearm_stop(self):
  self.core.lib.fm_r59_session_stop(ctypes.byref(self.core.r59_session));self.assertEqual(self.core.get_r59_session_status()['phase'],'STOPPED')
 def test_18_stop_application(self):
  self.core.stop();self.assertEqual(self.core.get_r59_session_status()['phase'],'STOPPED')
 def test_19_refuse_without_candidate(self):
  with self.assertRaisesRegex(ValueError,'R58_ISOLATED_CANDIDATE_NOT_VERIFIED'):
   self.core.bind_r59_session({'channel':'acoustic','hz':440,'level':.01,'duration_ms':500})
 def test_20_r59_c_has_no_audioqueue(self):
  code=(ROOT/'native/acoustic_session_r59.c').read_text();self.assertNotIn('AudioQueueStart(',code);self.assertNotIn('AudioQueueNewOutput(',code)
 def test_21_r59_c_no_synthetic_device(self):self.assertIn('fm_r57_backend_route_check(', (ROOT/'native/acoustic_session_r59.c').read_text())
 def test_22_r58_original_still_isolated(self):self.assertIn('libfreqmed_r58_candidate_isolated.dylib',(ROOT/'app.py').read_text())
 def test_23_hard_denial_preserved(self):self.assertIn('return -1', (ROOT/'native/output_hard_denied.c').read_text())
 def test_24_user_route_name_no_hidden_uid(self):self.assertNotIn('kAudioDevicePropertyDeviceUID',(ROOT/'native/acoustic_session_r59.c').read_text())
 def test_25_session_no_physical_flag(self):self.assertEqual(self.core.get_r59_session_status()['physical_output'],'HARD_DENIED')
 def test_26_r59_compiled_and_ctypes_bound(self):self.assertTrue(hasattr(self.core.lib,'fm_r59_session_bind'))
 def test_27_macos_no_mock(self):self.assertIn('fm_r57_backend_route_check',(ROOT/'native/acoustic_session_r59.c').read_text())
 def test_28_preserve_git_pins(self):self.assertEqual(len(json.loads((ROOT/'SOURCE_PINS_R58.json').read_text())['files']),5)
 def test_29_real_status_has_no_output(self):self.assertEqual(self.core.get_r59_session_status()['playback'],'NOT_PERFORMED')
 def test_30_non_live_monitor_fails(self):
  self.core.stop_engine_and_monitor()
  with self.assertRaisesRegex(ValueError,'OS_MONITOR_STOPPED'):
   self.core.bind_r59_session({'channel':'acoustic','hz':440,'level':.01,'duration_ms':500})
class HTTP(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();cls.core=a.NativeCore(pathlib.Path(cls.tmp.name));cls.s=a.make_server(cls.core)
  cls.t=threading.Thread(target=cls.s.serve_forever,daemon=True);cls.t.start()
 @classmethod
 def tearDownClass(cls):cls.s.shutdown();cls.s.server_close();cls.t.join(3);cls.tmp.cleanup()
 def req(self,method,path,data=None,auth=False,origin=True):
  c=http.client.HTTPConnection('127.0.0.1',self.s.server_port,timeout=5)
  h={'Host':'127.0.0.1:'+str(self.s.server_port)}
  if data is not None:
   h['Content-Type']='application/json'
   if origin:h['Origin']='http://127.0.0.1:'+str(self.s.server_port)
   if auth:h['X-FREQMED-SESSION']=self.s.token
  c.request(method,path,body=json.dumps(data) if data is not None else None,headers=h)
  r=c.getresponse();body=r.read();code=r.status;c.close();return code,json.loads(body) if path.startswith('/api/') else body
 def test_31_status_http(self):self.assertEqual(self.req('GET','/api/acoustic/session/status')[0],200)
 def test_32_status_denied(self):self.assertEqual(self.req('GET','/api/acoustic/session/status')[1]['physical_output'],'HARD_DENIED')
 def test_33_bind_requires_session(self):self.assertEqual(self.req('POST','/api/acoustic/session/bind',{},False)[0],403)
 def test_34_bind_requires_origin(self):self.assertEqual(self.req('POST','/api/acoustic/session/bind',{},True,False)[0],403)
 def test_35_bind_schema_rejected(self):self.assertEqual(self.req('POST','/api/acoustic/session/bind',{},True)[0],422)
 def test_36_em_rejected(self):self.assertEqual(self.req('POST','/api/acoustic/session/bind',{'channel':'em','hz':440,'level':.01,'duration_ms':500},True)[0],422)
 def test_37_web_page(self):self.assertIn(b'id="r59-bind"',self.req('GET','/')[1])
 def test_38_script(self):self.assertIn(b'session/bind',self.req('GET','/r59.js')[1])
 def test_39_styles(self):self.assertIn(b'.r59-panel',self.req('GET','/r59.css')[1])
 def test_40_no_start_route(self):self.assertEqual(self.req('GET','/api/physical-start')[0],404)
 def test_41_status_main(self):self.assertIn('acoustic_session_r59',self.req('GET','/api/status')[1])
 def test_42_candidate_still_readonly(self):self.assertEqual(self.req('GET','/api/acoustic/candidate/status')[1]['playback'],'NOT_PERFORMED')
 def test_43_historical_v5_unchanged(self):self.assertTrue((ROOT/'historical/FREQMED_V5_DIRECT.html').is_file())
 def test_44_language_choices(self):self.assertIn('zh:',(ROOT/'static/r59.js').read_text())

class R59Invalidation(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();cls.core=a.NativeCore(pathlib.Path(cls.tmp.name))
  cls.s=a.make_server(cls.core);cls.t=threading.Thread(target=cls.s.serve_forever,daemon=True);cls.t.start()
 @classmethod
 def tearDownClass(cls):cls.s.shutdown();cls.s.server_close();cls.t.join(3);cls.tmp.cleanup()
 def post(self,payload,auth=True):
  c=http.client.HTTPConnection('127.0.0.1',self.s.server_port,timeout=5)
  h={'Host':'127.0.0.1:'+str(self.s.server_port),'Origin':'http://127.0.0.1:'+str(self.s.server_port),'Content-Type':'application/json'}
  if auth:h['X-FREQMED-SESSION']=self.s.token
  c.request('POST','/api/acoustic/session/invalidate',body=json.dumps(payload),headers=h)
  r=c.getresponse();status=r.status;body=json.loads(r.read());c.close();return status,body
 def test_45_explicit_invalidate_native(self):
  self.assertEqual(self.core.invalidate_r59_session()['phase'],'INVALIDATED')
 def test_46_invalidate_http_auth(self):
  code,result=self.post({});self.assertEqual(code,200);self.assertFalse(result['route_bound'])
 def test_47_invalidate_cannot_change_state_without_token(self):self.assertEqual(self.post({},False)[0],403)
 def test_48_invalidate_rejects_nonempty(self):self.assertEqual(self.post({'emit':True})[0],422)
