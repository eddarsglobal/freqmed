# SPDX-License-Identifier: Apache-2.0
"""R55: real CoreAudio polling and authenticated software-stop integration.
No invented hardware, no simulated physical experiments or measurements.
"""
import importlib.util, tempfile, pathlib, unittest, threading, time, http.client, json, ast
R=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('freqmed_r55',R/'app.py')
a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
class R55Native(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.temp=tempfile.TemporaryDirectory();cls.core=a.NativeCore(pathlib.Path(cls.temp.name))
 @classmethod
 def tearDownClass(cls):cls.core.stop_route_monitor();cls.temp.cleanup()
 def test_01_monitor_counts_actual_calls(self):
  first=self.core.route_monitor_status()['checks'];result=self.core.route_watch_tick()
  self.assertEqual(result['checks'],first)  # No selected route => no CoreAudio polling
  self.assertEqual(result['last_os_poll'],'NOT_CHECKED')
 def test_02_no_os_no_invented_device(self):
  s=self.core.audio_devices();self.assertIn('observed',s)
  if not s['observed']:self.assertEqual(s['devices'],[])
 def test_03_monitor_never_authorizes_output(self):
  self.core.route_watch_tick();r=self.core.route_monitor_status()
  self.assertEqual(r['physical_emission'],'NOT_POSSIBLE_IN_THIS_BUILD')
  self.assertEqual(r['physical_stop_capability'],'NONE_NOT_AN_INTERLOCK')
  self.assertEqual(self.core.lib.fm_acoustic_native_backend_available(),0)
 def test_04_software_stop_is_real_native_C(self):
  self.core.validate({'channel':'acoustic','hz':440,'level':.01,'duration_ms':500})
  self.assertEqual(self.core.stop()['software_stop'],'EXECUTED_NATIVE_FM_STOP')
  self.assertEqual(self.core.guardian.state,0)
  self.assertIsNone(self.core.route)
 def test_05_monitor_event_no_empty_fake_device(self):
  self.core.clear_audio();self.core.route_watch_tick()
  self.assertEqual(self.core.route_monitor_status()['selected'],False)
 def test_06_monitor_lifecycle(self):
  self.assertTrue(self.core.start_route_monitor(0.5))
  self.assertFalse(self.core.start_route_monitor(0.5))
  deadline=time.monotonic()+2
  while time.monotonic()<deadline and self.core.route_monitor_status()['checks']!=0:time.sleep(.02)
  self.assertEqual(self.core.route_monitor_status()['checks'],0)
  self.assertTrue(self.core.stop_route_monitor())
 def test_07_reject_unbounded_polling(self):
  for v in (0,-1,0.01,100):
   with self.assertRaises(ValueError):self.core.start_route_monitor(v)
 def test_08_original_C_provenance_preserved(self):
  import subprocess
  pins={'generator.h':'9839f4390d9f17560cf6ef2447501a314f335773',
  'generator_core.c':'80f35f7ec323a658699929a717d6d16ef74a3144',
  'acoustic_probe_macos.c':'d70f9457c2b6c2f3668681247fa895f3a2720b5e'}
  for filename,sha in pins.items():
   self.assertEqual(subprocess.check_output(['git','hash-object',str(R/'native'/filename)],text=True).strip(),sha)
 def test_09_runner_no_emission_compilation(self):
  s=(R/'app.py').read_text()
  self.assertNotIn('"acoustic_macos.c"',s)
  self.assertIn('"output_hard_denied.c"',s)
  self.assertNotIn('AudioQueueStart',(R/'native'/'audio_devices_macos.c').read_text())
 def test_10_manifest_and_V5(self):
  import hashlib
  self.assertGreaterEqual(a.verify_manifest(),19)
  self.assertEqual(hashlib.sha256((R/'historical'/'FREQMED_V5_DIRECT.html').read_bytes()).hexdigest(),'e034913d551cbfaf6ee51c8ce971707dd811ebfebb8d8bc9307d71f9c7029ef8')
 def test_11_first_poll_before_ui(self):
  r=self.core.route_watch_tick();self.assertEqual(r['checks'],0)
  self.assertIn('event',r)
  self.assertEqual(r['physical_stop_capability'],'NONE_NOT_AN_INTERLOCK')
 def test_12_guardian_stop_not_hardware_cutoff(self):
  stop=self.core.stop()
  self.assertIn('NOT a physical emergency cutoff',stop['note'])
 def test_13_field_abi_fix_retained(self):
  names=[name for name,_ in a.FMNativeAudioDevice._fields_]
  self.assertIn('output_channels',names)
  self.assertNotIn('channels',names)

class R55HTTP(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.temp=tempfile.TemporaryDirectory();cls.core=a.NativeCore(pathlib.Path(cls.temp.name))
  cls.server=a.make_server(cls.core)
  cls.th=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.th.start()
 @classmethod
 def tearDownClass(cls):
  cls.server.shutdown();cls.server.server_close();cls.th.join(2);cls.temp.cleanup()
 def req(self,method,path,body=None,head=None):
  p=self.server.server_port;conn=http.client.HTTPConnection('127.0.0.1',p,timeout=5)
  headers={'Host':f'127.0.0.1:{p}',**(head or {})}
  if body is not None:headers['Content-Type']='application/json';body=json.dumps(body)
  conn.request(method,path,body,headers);r=conn.getresponse();raw=r.read();code=r.status;conn.close()
  return code,json.loads(raw) if path.startswith('/api/') else raw
 def auth(self):return {'Origin':f'http://127.0.0.1:{self.server.server_port}', 'X-FREQMED-SESSION':self.server.token}
 def test_14_monitor_endpoint_real_os_only(self):
  code,data=self.req('GET','/api/route/monitor');self.assertEqual(code,200)
  self.assertIn('checks',data);self.assertEqual(data['physical_emission'],'NOT_POSSIBLE_IN_THIS_BUILD')
 def test_15_stop_endpoint_needs_auth(self):
  code,data=self.req('POST','/api/software-stop',{})
  self.assertEqual(code,403)
 def test_16_stop_endpoint_refuses_untrusted_origin(self):
  h=self.auth();h['Origin']='https://untrusted.example'
  code,data=self.req('POST','/api/software-stop',{},h);self.assertEqual(code,403)
 def test_17_stop_endpoint_rejects_data(self):
  code,data=self.req('POST','/api/software-stop',{'unlock':True},self.auth());self.assertEqual(code,422)
 def test_18_stop_executes_native_C(self):
  code,data=self.req('POST','/api/software-stop',{},self.auth());self.assertEqual(code,200)
  self.assertEqual(data['guardian_state'],'OFF');self.assertEqual(data['software_stop'],'EXECUTED_NATIVE_FM_STOP')
 def test_19_no_start_route(self):
  code,data=self.req('POST','/api/physical-start',{},self.auth());self.assertEqual(code,404)
 def test_20_UI_monitor_markup(self):
  code,raw=self.req('GET','/');self.assertEqual(code,200)
  self.assertIn(b'id="r55-software-stop"',raw);self.assertIn(b'/r55.js',raw)
 def test_21_monitor_JS_valid(self):
  code,raw=self.req('GET','/r55.js');self.assertEqual(code,200)
  self.assertIn(b'/api/route/monitor',raw);self.assertIn(b'/api/software-stop',raw)
 def test_22_monitor_CSS_valid(self):
  code,raw=self.req('GET','/r55.css');self.assertEqual(code,200)
  self.assertIn(b'.r55-live-monitor',raw)
 def test_23_r54_selection_retained(self):
  code,data=self.req('GET','/api/audio/devices');self.assertEqual(code,200)
  self.assertIn('selection',data)
 def test_24_session_refusal(self):
  code,data=self.req('POST','/api/software-stop',{}, {'Origin':f'http://127.0.0.1:{self.server.server_port}','X-FREQMED-SESSION':'bogus'})
  self.assertEqual(code,403)
 def test_25_C_guardian_route_stays_closed(self):
  code,data=self.req('POST','/api/validate',{'channel':'acoustic','hz':440,'level':.01,'duration_ms':250},self.auth())
  self.assertEqual(code,200);self.assertFalse(data['guardian_authorized'])
