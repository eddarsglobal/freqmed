# SPDX-License-Identifier: Apache-2.0
"""GEN-R56: native acoustic/route preflight, no fabricated devices or physical output."""
import ctypes
import http.client
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('freqmed_r56', ROOT/'app.py')
a=importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)

class NativePreflight(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.temp=tempfile.TemporaryDirectory()
  cls.core=a.NativeCore(Path(cls.temp.name))
 @classmethod
 def tearDownClass(cls):cls.temp.cleanup()
 def test_01_c_preflight_symbol_linked(self):self.assertTrue(hasattr(self.core.lib,'fm_r56_acoustic_preflight'))
 def test_02_ffi_field_contract(self):
  self.assertEqual([x for x,_ in a.FMAcousticPreflight._fields_],['result_code','device_id','channels','os_rate_hz','requested_hz','duration_ms','digital_frame_count'])
  self.assertEqual(a.FMAcousticPreflight.os_rate_hz.offset,16)
  self.assertEqual(a.FMAcousticPreflight.digital_frame_count.offset,40)
 def test_03_no_route_refuses_preparation(self):
  with self.assertRaisesRegex(ValueError,'SELECT_REAL_COREAUDIO_OUTPUT_FIRST'):
   self.core.acoustic_preflight({'channel':'acoustic','hz':440.0,'level':.01,'duration_ms':500})
 def test_04_em_channel_refused(self):
  with self.assertRaisesRegex(ValueError,'ONLY_ACOUSTIC_CHANNEL_SUPPORTED'):
   self.core.acoustic_preflight({'channel':'em','hz':440.0,'level':.01,'duration_ms':500})
 def test_05_invalid_payload_additional_field(self):
  with self.assertRaisesRegex(ValueError,'INVALID_PREFLIGHT_SCHEMA'):
   self.core.acoustic_preflight({'channel':'acoustic','hz':440.0,'level':.01,'duration_ms':500,'unlock':True})
 def test_06_boolean_number_refused(self):
  with self.assertRaisesRegex(ValueError,'INVALID_NUMERIC_TYPE'):
   self.core.acoustic_preflight({'channel':'acoustic','hz':True,'level':.01,'duration_ms':500})
 def test_07_boolean_duration_refused(self):
  with self.assertRaisesRegex(ValueError,'INVALID_NUMERIC_TYPE'):
   self.core.acoustic_preflight({'channel':'acoustic','hz':440.0,'level':.01,'duration_ms':True})
 def test_08_nan_inf_refused(self):
  for hz in [float('nan'),float('inf'),-float('inf')]:
   with self.assertRaisesRegex(ValueError,'INVALID_NUMERIC_RANGE'):
    self.core.acoustic_preflight({'channel':'acoustic','hz':hz,'level':.01,'duration_ms':500})
 def test_09_c_fails_closed_on_em(self):
  out=a.FMAcousticPreflight();cmd=a.FMCommand(2,440.0,.01,500)
  self.assertEqual(self.core.lib.fm_r56_acoustic_preflight(ctypes.byref(cmd),1,b'none',2,48000.,ctypes.byref(out)),0)
  self.assertEqual(out.result_code,2)
 def test_10_c_fails_closed_on_zero_hz(self):
  out=a.FMAcousticPreflight();cmd=a.FMCommand(1,0.0,.01,500)
  self.assertEqual(self.core.lib.fm_r56_acoustic_preflight(ctypes.byref(cmd),1,b'none',2,48000.,ctypes.byref(out)),0)
  self.assertEqual(out.result_code,2)
 def test_11_c_requires_device_id(self):
  out=a.FMAcousticPreflight();cmd=a.FMCommand(1,440.0,.01,500)
  self.assertEqual(self.core.lib.fm_r56_acoustic_preflight(ctypes.byref(cmd),0,b'none',2,48000.,ctypes.byref(out)),0)
  self.assertEqual(out.result_code,7)
 def test_12_c_requires_name_and_channels(self):
  out=a.FMAcousticPreflight();cmd=a.FMCommand(1,440.0,.01,500)
  self.core.lib.fm_r56_acoustic_preflight(ctypes.byref(cmd),1,b'',2,48000.,ctypes.byref(out))
  self.assertEqual(out.result_code,7)
  self.core.lib.fm_r56_acoustic_preflight(ctypes.byref(cmd),1,b'none',0,48000.,ctypes.byref(out))
  self.assertEqual(out.result_code,7)
 def test_13_no_fabricated_os_route(self):
  out=a.FMAcousticPreflight();cmd=a.FMCommand(1,440.0,.01,500)
  self.core.lib.fm_r56_acoustic_preflight(ctypes.byref(cmd),4294967295,b'not-an-os-device',2,48000.,ctypes.byref(out))
  self.assertIn(out.result_code,(3,4)) # invalid real OS route or OS unavailable
 def test_14_output_always_denied(self):
  self.assertEqual(self.core.lib.fm_acoustic_native_backend_available(),0)
  self.assertNotEqual(self.core.lib.fm_acoustic_physical_output(None),0)
  self.assertEqual(self.core.lib.fm_em_backend_available(),0)
 def test_15_stop_invalidates_preflight(self):
  self.core.stop_engine_and_monitor()
  with self.assertRaisesRegex(ValueError,'OS_MONITOR_STOPPED'):
   self.core.acoustic_preflight({'channel':'acoustic','hz':440.0,'level':.01,'duration_ms':500})
  self.assertFalse(self.core.get_acoustic_preflight_status()['checked'])
 def test_16_resume_not_arm(self):
  self.core.resume_route_monitor()
  self.assertEqual(self.core.guardian.state,0)
  self.assertIsNone(self.core.route)
 def test_17_r56_source_is_non_emitting(self):
  source=(ROOT/'native/acoustic_preflight_r56.c').read_text()
  self.assertNotIn('AudioQueueStart',source)
  self.assertNotIn('AudioQueueNewOutput',source)
  self.assertNotIn('AudioDeviceStart',source)
  self.assertNotIn('fm_acoustic_physical_output(',source)
 def test_18_shared_C_device_struct(self):
  h=(ROOT/'native/audio_devices.h').read_text()
  c=(ROOT/'native/audio_devices_macos.c').read_text()
  assert 'FMNativeAudioDevice' in h
  self.assertIn('#include "audio_devices.h"',c)
  self.assertEqual(c.count('} FMNativeAudioDevice;'),0)
 def test_19_original_c_core_git_pins(self):
  import subprocess
  for file,git in [('generator.h','9839f4390d9f17560cf6ef2447501a314f335773'),('generator_core.c','80f35f7ec323a658699929a717d6d16ef74a3144')]:
   self.assertEqual(subprocess.check_output(['git','hash-object',str(ROOT/'native'/file)],text=True).strip(),git)

class HttpPreflight(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.temp=tempfile.TemporaryDirectory()
  cls.core=a.NativeCore(Path(cls.temp.name))
  cls.server=a.make_server(cls.core)
  cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
 @classmethod
 def tearDownClass(cls):
  cls.server.shutdown();cls.server.server_close();cls.thread.join(3);cls.temp.cleanup()
 def req(self,method,path,payload=None,authorized=False):
  con=http.client.HTTPConnection('127.0.0.1',self.server.server_port,timeout=6)
  headers={'Host':f'127.0.0.1:{self.server.server_port}'}
  if payload is not None:
   headers['Content-Type']='application/json';payload=json.dumps(payload)
  if authorized:
   headers['Origin']=f'http://127.0.0.1:{self.server.server_port}'
   headers['X-FREQMED-SESSION']=self.server.token
  con.request(method,path,body=payload,headers=headers)
  r=con.getresponse();data=r.read();status=r.status;con.close()
  return status,json.loads(data) if path.startswith('/api/') else data
 def test_20_home_shows_actual_preflight(self):
  s,b=self.req('GET','/');self.assertEqual(s,200)
  self.assertIn(b'id="r56-prepare"',b)
  self.assertIn(b'disabled-start',b)
 def test_21_r56_js_is_served(self):
  s,b=self.req('GET','/r56.js');self.assertEqual(s,200)
  self.assertIn(b'/api/acoustic/preflight',b)
 def test_22_r56_css_is_served(self):
  s,b=self.req('GET','/r56.css');self.assertEqual(s,200)
  self.assertIn(b'.r56-preflight',b)
 def test_23_auth_required(self):
  s,b=self.req('POST','/api/acoustic/preflight',{'channel':'acoustic','hz':440.,'level':.01,'duration_ms':500})
  self.assertEqual(s,403)
 def test_24_unknown_device_refused_no_crash(self):
  s,b=self.req('POST','/api/acoustic/preflight',{'channel':'acoustic','hz':440.,'level':.01,'duration_ms':500},True)
  self.assertEqual(s,422);self.assertIn('SELECT_REAL_COREAUDIO_OUTPUT_FIRST',b['error'])
 def test_25_illegal_em_refused(self):
  s,b=self.req('POST','/api/acoustic/preflight',{'channel':'em','hz':440.,'level':.01,'duration_ms':500},True)
  self.assertEqual(s,422)
 def test_26_preflight_status_has_no_certification(self):
  s,b=self.req('GET','/api/acoustic/preflight/status')
  self.assertEqual(s,200);self.assertFalse(b['checked'])
  self.assertEqual(b['physical_output'],'HARD_DENIED')
 def test_27_physical_start_still_absent(self):
  s,b=self.req('POST','/api/physical-start',{},True);self.assertEqual(s,404)
 def test_28_cross_origin_refused(self):
  s,b=self.req('POST','/api/acoustic/preflight',{},True)
  self.assertEqual(s,422) # authenticated, bad payload
  con=http.client.HTTPConnection('127.0.0.1',self.server.server_port,timeout=6)
  con.request('POST','/api/acoustic/preflight',body='{}',headers={'Host':f'127.0.0.1:{self.server.server_port}','Origin':'http://evil.invalid','X-FREQMED-SESSION':self.server.token,'Content-Type':'application/json'})
  r=con.getresponse();r.read();self.assertEqual(r.status,403);con.close()
 def test_29_report_is_not_a_measurement(self):
  source=(ROOT/'app.py').read_text()
  self.assertIn('"physical_measurement": "NOT_PERFORMED"',source)
  self.assertIn('"scientific_simulation": "NONE"',source)
  self.assertIn('"hardware_qualified": False',source)
 def test_30_stop_api_still_auth_protected(self):
  s,_=self.req('POST','/api/software-stop',{})
  self.assertEqual(s,403)

class R56StatusInvalidation(unittest.TestCase):
 def test_31_validate_clears_any_previous_contract(self):
  source=(ROOT/'app.py').read_text()
  v=source[source.index('    def validate(self, payload):'):source.index('    def stop(self):')]
  self.assertIn('self.r56_preflight = None',v)
 def test_32_native_device_invalidation_clears_contract(self):
  source=(ROOT/'app.py').read_text()
  watch=source[source.index('    def route_watch_tick(self):'):source.index('    def _route_monitor_status_locked(self):')]
  self.assertIn('self._r61_trip_locked(',watch)
  self.assertIn('self.r56_preflight = None',source[source.index('    def _r61_trip_locked('):source.index('    def _r61_status_locked(')])
 def test_33_stop_clears_contract(self):
  source=(ROOT/'app.py').read_text()
  stop=source[source.index('    def stop_engine_and_monitor(self):'):source.index('    def resume_route_monitor(self):')]
  self.assertIn('self.r56_preflight = None',stop)
 def test_34_js_clears_prior_success_on_route_change(self):
  js=(ROOT/'static/r56.js').read_text()
  for widget in ('r55-software-stop','r54-clear','r54-bind','reset','validate'):
   self.assertIn(widget,js)
  self.assertIn('/api/acoustic/preflight/status',js)
