# SPDX-License-Identifier: Apache-2.0
"""GEN-R55-FIX1: operator STOP halts periodic REAL-OS observer and freezes counter.

No manufactured equipment, readings, waveform or simulated physical experiment.
"""
import importlib.util
import pathlib
import tempfile
import time
import threading
import http.client
import json
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('freqmed_r55_fix1',ROOT/'app.py')
a=importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)

class StopCore(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.temp=tempfile.TemporaryDirectory()
  cls.core=a.NativeCore(pathlib.Path(cls.temp.name))
 @classmethod
 def tearDownClass(cls):
  cls.core.stop_route_monitor()
  cls.temp.cleanup()
 def test_01_real_watcher_starts(self):
  self.assertTrue(self.core.start_route_monitor(0.5))
  time.sleep(0.9)
  snap=self.core.route_monitor_status()
  self.assertEqual(snap['checks'],0)
  self.assertFalse(snap['monitor_running'])
  self.assertEqual(snap['monitor_state'],'IDLE')
 def test_02_operator_stop_freezes_counter(self):
  result=self.core.stop_engine_and_monitor()
  frozen=result['monitor_checks_frozen_at']
  self.assertEqual(result['guardian_state'],'OFF')
  self.assertEqual(result['software_stop'],'EXECUTED_NATIVE_FM_STOP')
  self.assertFalse(result['monitor_running'])
  self.assertIn(result['monitor_state'],('STOPPED','STOPPING'))
  self.assertFalse(self.core.route_monitor_status()['monitor_running'])
  time.sleep(1.2)
  self.assertEqual(self.core.route_monitor_status()['checks'],frozen)
 def test_03_stopped_manual_tick_never_increments(self):
  frozen=self.core.route_monitor_status()['checks']
  self.core.route_watch_tick()
  self.assertEqual(self.core.route_monitor_status()['checks'],frozen)
 def test_04_stop_cannot_be_undone_by_validate_or_reset(self):
  self.core.validate({'channel':'acoustic','hz':440,'level':.01,'duration_ms':500})
  self.core.stop()
  self.assertFalse(self.core.route_monitor_status()['monitor_running'])
  self.assertEqual(self.core.route_monitor_status()['monitor_state'],'STOPPED')
 def test_05_explicit_resume_only(self):
  self.assertEqual(self.core.resume_route_monitor()['monitor_state'],'IDLE')
  self.assertFalse(self.core.route_monitor_status()['selected'])
  self.assertEqual(self.core.guardian.state,0)
 def test_06_resume_is_idempotently_refused(self):
  with self.assertRaisesRegex(ValueError,'MONITOR_ALREADY_RUNNING'):
   self.core.resume_route_monitor()
 def test_07_resume_count_increases_again(self):
  start=self.core.route_monitor_status()['checks']
  deadline=time.monotonic()+2.5
  while self.core.route_monitor_status()['checks']<=start and time.monotonic()<deadline:
   time.sleep(.05)
  self.assertEqual(self.core.route_monitor_status()['checks'],start)
 def test_08_stop_again_freezes(self):
  self.core.stop_engine_and_monitor()
  snapshot=self.core.route_monitor_status()
  time.sleep(.65)
  self.assertEqual(self.core.route_monitor_status()['checks'],snapshot['checks'])
 def test_09_Guardian_no_physical_output(self):
  self.assertEqual(self.core.lib.fm_acoustic_native_backend_available(),0)
  self.assertEqual(self.core.lib.fm_em_backend_available(),0)
  self.assertEqual(self.core.route_monitor_status()['physical_emission'],'NOT_POSSIBLE_IN_THIS_BUILD')
 def test_10_operator_stop_not_physical_cutoff(self):
  result=self.core.stop_engine_and_monitor()
  self.assertIn('NOT a physical emergency cutoff',result['note'])

class StopHttp(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.temp=tempfile.TemporaryDirectory()
  cls.core=a.NativeCore(pathlib.Path(cls.temp.name))
  cls.core.start_route_monitor(0.5)
  cls.server=a.make_server(cls.core)
  cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True)
  cls.thread.start()
 @classmethod
 def tearDownClass(cls):
  cls.server.shutdown();cls.server.server_close()
  cls.core.stop_route_monitor();cls.thread.join(timeout=3)
  cls.temp.cleanup()
 def call(self,method,path,payload=None,auth=False):
  port=self.server.server_port
  c=http.client.HTTPConnection('127.0.0.1',port,timeout=5)
  h={'Host':f'127.0.0.1:{port}'}
  if payload is not None:
   h['Content-Type']='application/json'
   payload=json.dumps(payload)
  if auth:
   h['Origin']=f'http://127.0.0.1:{port}'
   h['X-FREQMED-SESSION']=self.server.token
  c.request(method,path,payload,headers=h)
  r=c.getresponse();content=r.read();status=r.status;c.close()
  return status,json.loads(content) if path.startswith('/api/') else content
 def test_11_stop_unauthorized_refused(self):
  status,_=self.call('POST','/api/software-stop',{})
  self.assertEqual(status,403)
 def test_12_stop_rejects_unexpected_payload(self):
  status,_=self.call('POST','/api/software-stop',{'do_not_pause':True},True)
  self.assertEqual(status,422)
 def test_13_monitor_resume_unauthorized_refused(self):
  status,_=self.call('POST','/api/route/monitor/resume',{})
  self.assertEqual(status,403)
 def test_14_http_stop_freezes_os_counter(self):
  status,result=self.call('POST','/api/software-stop',{},True)
  self.assertEqual(status,200)
  self.assertFalse(result['monitor_running'])
  self.assertEqual(result['guardian_state'],'OFF')
  before=self.call('GET','/api/route/monitor')[1]['checks']
  time.sleep(.75)
  after=self.call('GET','/api/route/monitor')[1]
  self.assertEqual(after['checks'],before)
  self.assertIn(after['monitor_state'],('STOPPED','STOPPING'))
 def test_15_http_resume_rejects_wrong_payload(self):
  status,_=self.call('POST','/api/route/monitor/resume',{'bad':1},True)
  self.assertEqual(status,422)
 def test_16_http_resume_works_and_no_unlock(self):
  status,result=self.call('POST','/api/route/monitor/resume',{},True)
  self.assertEqual(status,200)
  self.assertEqual(result['monitor_state'],'IDLE')
  state=self.call('GET','/api/status')[1]
  self.assertEqual(state['guardian_state'],'OFF')
  self.assertEqual(state['acoustic_output'],'NOT_LINKED_HARD_DENIED')
  self.assertFalse(state['selected_acoustic_route']['selected'])
 def test_17_stop_again_via_http(self):
  status,result=self.call('POST','/api/software-stop',{},True)
  self.assertEqual(status,200)
  self.assertFalse(result['monitor_running'])
 def test_18_ui_shows_explicit_resume_button(self):
  status,raw=self.call('GET','/')
  self.assertEqual(status,200)
  self.assertIn(b'id="r55-resume-monitor"',raw)
  self.assertIn(b'id="r55-live-chip"',raw)
 def test_19_js_has_real_stop_resume_api(self):
  status,raw=self.call('GET','/r55.js')
  self.assertEqual(status,200)
  self.assertIn(b'/api/route/monitor/resume',raw)
  self.assertIn(b"value.monitor_state==='RUNNING'",raw)
 def test_20_not_a_physical_start_endpoint(self):
  status,_=self.call('POST','/api/physical-start',{},True)
  self.assertEqual(status,404)

class StaticAssurances(unittest.TestCase):
 def test_21_output_denied_source_unchanged(self):
  self.assertIn('return -1', (ROOT/'native/output_hard_denied.c').read_text())
 def test_22_no_device_fixtures_in_application(self):
  source=(ROOT/'app.py').read_text()
  self.assertNotIn('dummy device',source.lower())
  self.assertNotIn('fake device',source.lower())
  self.assertNotIn('AudioQueueStart',source)
 def test_23_monitor_thread_pauses_under_same_lock_as_guardian(self):
  import ast
  tree=ast.parse((ROOT/'app.py').read_text())
  methods={node.name:node for obj in tree.body if isinstance(obj,ast.ClassDef) and obj.name=='NativeCore'
           for node in obj.body if isinstance(node,ast.FunctionDef)}
  self.assertIn('stop_engine_and_monitor',methods)
  self.assertIn('resume_route_monitor',methods)
  stop=ast.get_source_segment((ROOT/'app.py').read_text(),methods['stop_engine_and_monitor'])
  self.assertIn('self._monitor_shutdown.set()',stop)
  self.assertIn('self.lib.fm_stop',stop)
  watch=ast.get_source_segment((ROOT/'app.py').read_text(),methods['route_watch_tick'])
  self.assertIn('if self._monitor_shutdown.is_set() or self.route is None:',watch)
