# SPDX-License-Identifier: Apache-2.0
import ctypes
import http.client
import importlib.util
import json
import pathlib
import tempfile
import threading
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('freqmed_r58',ROOT/'app.py')
a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)

class R58Source(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();cls.core=a.NativeCore(pathlib.Path(cls.tmp.name))
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def test_01_r57_inherited_valid(self):self.assertEqual(self.core.status()['acoustic_output'],'NOT_LINKED_HARD_DENIED')
 def test_02_candidate_not_auto_exposed(self):self.assertIsNone(self.core.r58_candidate)
 def test_03_candidate_status_denies(self):self.assertEqual(self.core.candidate_status()['main_application_physical_output'],'HARD_DENIED')
 def test_04_candidate_state_struct(self):self.assertEqual(ctypes.sizeof(a.FMR58CandidateEvidence),16)
 def test_05_candidate_symbol_struct(self):self.assertEqual(a.FMR58CandidateEvidence.emitter_entrypoint_denied.offset,12)
 def test_06_safe_wrapper_only(self):
  code=(ROOT/'native/candidate_link_r58.c').read_text()
  self.assertIn('fm_r58_candidate_evidence',code)
  self.assertIn('fm_acoustic_physical_output((const FMCommand*)0)',code)
 def test_07_emitter_function_is_noop(self):
  self.assertNotEqual(self.core.lib.fm_acoustic_physical_output(None),0)
 def test_08_main_em_stays_absent(self):self.assertEqual(self.core.lib.fm_em_backend_available(),0)
 def test_09_original_emitter_not_in_archive(self):self.assertFalse((ROOT/'native/acoustic_macos.c').exists())
 def test_10_source_pins(self):
  pins=json.loads((ROOT/'SOURCE_PINS_R58.json').read_text())
  self.assertEqual(len(pins['files']),5)
  self.assertEqual(pins['files']['acoustic_macos.c'],'03f9c27c2f45154e45afcae5e0696c7b33a6874a')
 def test_11_git_hash_known(self):
  m=a.load_candidate_source_module();self.assertEqual(m.git_blob(b'example'), '96236f8158b12701d5e75c14fb876c4a0f31b963')
 def test_12_manifest_count(self):self.assertGreaterEqual(a.verify_manifest(),35)
 def test_13_compiler_visibility_contract(self):
  s=(ROOT/'app.py').read_text()
  self.assertIn("'-fvisibility=hidden'",s)
  self.assertIn("-Wl,-exported_symbol,_fm_r58_candidate_evidence",s)
 def test_14_no_runtime_emission_route(self):
  s=(ROOT/'app.py').read_text();self.assertNotIn('"/api/physical-start"',s)
 def test_15_candidate_not_returned_as_emission(self):self.assertEqual(self.core.candidate_status()['playback'],'NOT_PERFORMED')
 def test_16_source_extraction_fails_closed(self):
  m=a.load_candidate_source_module();self.assertFalse(m.PINS['acoustic_macos.c'].startswith('0'*8))
 def test_17_source_no_network(self):
  s=(ROOT/'candidate_source_r58.py').read_text()
  self.assertNotIn('curl ',s);self.assertNotIn('git fetch',s)
 def test_18_ui_has_r58(self):self.assertIn('id="r58-check"',(ROOT/'static/index.html').read_text())
 def test_19_gui_r58_no_play_control(self):self.assertNotIn('AudioQueueStart',(ROOT/'static/r58.js').read_text())
 def test_20_main_src_still_denied(self):self.assertIn('output_hard_denied.c',(ROOT/'app.py').read_text())
 def test_21_marker_r58(self):self.assertIn('GEN_R58_UI_READY',(ROOT/'app.py').read_text())
 def test_22_status_explicit(self):self.assertIn('emission_entrypoints_exported',self.core.candidate_status())
 def test_23_linux_no_candidate_claim(self):
  import sys
  if sys.platform.startswith('linux'):
   self.assertFalse(self.core.attach_candidate()['candidate_source_linked_isolated'])
 def test_24_archive_no_private_ids(self):
  self.assertNotIn('DeviceUID',(ROOT/'native/candidate_link_r58.c').read_text())
 def test_25_kits_stateless(self):self.assertIsNone(self.core.r58_evidence)

class R58HTTP(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();cls.core=a.NativeCore(pathlib.Path(cls.tmp.name));cls.s=a.make_server(cls.core)
  cls.t=threading.Thread(target=cls.s.serve_forever,daemon=True);cls.t.start()
 @classmethod
 def tearDownClass(cls):cls.s.shutdown();cls.s.server_close();cls.t.join(3);cls.tmp.cleanup()
 def req(self,method,path):
  c=http.client.HTTPConnection('127.0.0.1',self.s.server_port,timeout=5)
  c.request(method,path,headers={'Host':'127.0.0.1:'+str(self.s.server_port)})
  r=c.getresponse();b=r.read();status=r.status;c.close();return status,b
 def test_26_status(self):
  code,body=self.req('GET','/api/acoustic/candidate/status');self.assertEqual(code,200)
  self.assertEqual(json.loads(body)['playback'],'NOT_PERFORMED')
 def test_27_page(self):
  code,body=self.req('GET','/');self.assertEqual(code,200);self.assertIn(b'id="r58-check"',body)
 def test_28_r58_js(self):
  code,body=self.req('GET','/r58.js');self.assertEqual(code,200);self.assertIn(b'candidate/status',body)
 def test_29_r58_css(self):
  code,body=self.req('GET','/r58.css');self.assertEqual(code,200);self.assertIn(b'.r58-panel',body)
 def test_30_no_physical_output(self):
  code,body=self.req('GET','/api/status');self.assertEqual(code,200)
  self.assertEqual(json.loads(body)['acoustic_output'],'NOT_LINKED_HARD_DENIED')
 def test_31_no_activation_endpoint(self):
  code,body=self.req('GET','/api/physical-start');self.assertEqual(code,404)
 def test_32_preflight_still_exposed(self):
  code,body=self.req('GET','/api/acoustic/preflight/status');self.assertEqual(code,200)
 def test_33_backend_r57_still_exposed(self):
  code,body=self.req('GET','/api/acoustic/backend/status');self.assertEqual(code,200)
 def test_34_unknown_host_refused(self):
  c=http.client.HTTPConnection('127.0.0.1',self.s.server_port,timeout=5);c.request('GET','/api/acoustic/candidate/status',headers={'Host':'evil.invalid'});r=c.getresponse();self.assertEqual(r.status,403);r.read();c.close()
