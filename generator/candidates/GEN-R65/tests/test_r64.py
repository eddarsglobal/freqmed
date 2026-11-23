# SPDX-License-Identifier: Apache-2.0
"""GEN-R64: native digital PCM integrity + true control state semantics.

These are C/software controls only; no mock acoustic experiment, no hardware
measurements, no sound output. Test arrays are adversarial numeric data.
"""
import ctypes
import importlib.util
import pathlib
import tempfile
import unittest
import math

ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('freqmed_r64_under_test',ROOT/'app.py')
a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)

class R64Logic(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();cls.c=a.NativeCore(pathlib.Path(cls.tmp.name))
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def setUp(self):
  self.c.route=None
  self.c._monitor_shutdown.clear()
  with self.c.lock:
   self.c.r59_session=a.FMR59Session()
   self.c.r60_lease=a.FMR60Lease()
   self.c.r62_identity=a.FMR62Identity()
   self.c.r61_fault=a.FMR61Fault()
 def retire(self):
  with self.c.lock:self.c._r64_retire_previous_binding_locked()
 def test_01_true_unbound_initial(self):
  self.assertEqual(self.c.get_r60_control_status()['state'],'UNBOUND')
  self.assertEqual(self.c.get_r62_identity_status()['state'],'UNBOUND')
 def test_02_retire_unbound_idempotent(self):
  self.retire();self.retire()
  self.assertEqual((self.c.r60_lease.state,self.c.r62_identity.state,self.c.r59_session.phase),(0,0,2))
 def test_03_idle_explicit_invalidate_does_not_invent_previous_lease(self):
  self.c.invalidate_r59_session()
  self.assertEqual((self.c.r60_lease.state,self.c.r62_identity.state),(0,0))
 def test_04_validation_before_bind_is_unbound(self):
  got=self.c.validate({'channel':'acoustic','hz':440.0,'level':.01,'duration_ms':500})
  self.assertTrue(got['structurally_valid'])
  self.assertFalse(got['guardian_authorized'])
  self.assertEqual((self.c.r60_lease.state,self.c.r62_identity.state),(0,0))
 def test_05_invalid_command_schema_does_not_change_contract(self):
  with self.assertRaises(ValueError):self.c.validate({'channel':'acoustic','hz':True,'level':.01,'duration_ms':500})
  self.assertEqual((self.c.r60_lease.state,self.c.r62_identity.state),(0,0))
 def test_06_retire_valid_lease_revoke(self):
  self.c.r59_session.phase=1;self.c.r60_lease.state=1
  self.c.r60_lease.bound.device_id=12
  self.retire()
  self.assertEqual(self.c.r60_lease.state,2)
  self.assertEqual(self.c.r60_lease.bound.device_id,0)
  self.assertEqual(self.c.r59_session.phase,2)
 def test_07_retire_valid_identity_revoke_and_clear_secret(self):
  self.c.r62_identity.state=1;self.c.r62_identity.os_uid=b'PRIVATE_UID_SENTINEL'
  self.retire()
  self.assertEqual(self.c.r62_identity.state,2)
  self.assertEqual(self.c.r62_identity.os_uid,b'')
 def test_08_retire_expired_stays_revoked(self):
  self.c.r60_lease.state=3;self.retire();self.assertEqual(self.c.r60_lease.state,2)
 def test_09_retire_already_invalid_keeps_invalid(self):
  self.c.r62_identity.state=2;self.retire();self.assertEqual(self.c.r62_identity.state,2)
 def test_10_operator_stop_sticky(self):
  self.c.r59_session.phase=3;self.c.r60_lease.state=4;self.c.r62_identity.state=3
  self.retire()
  self.assertEqual((self.c.r59_session.phase,self.c.r60_lease.state,self.c.r62_identity.state),(3,4,3))
 def test_11_explicit_stop_preserves_off_state(self):
  self.c.stop_engine_and_monitor()
  self.assertEqual((self.c.r60_lease.state,self.c.r62_identity.state),(4,3))
 def test_12_pcm_denied_without_route(self):
  with self.assertRaisesRegex(ValueError,'R63_NO_ACTIVE_REAL_ROUTE'):self.c.prepare_r63_digital_pcm()
 def test_13_pcm_denied_after_stop(self):
  self.c.stop_engine_and_monitor()
  with self.assertRaisesRegex(ValueError,'R63_NO_ACTIVE_REAL_ROUTE'):self.c.prepare_r63_digital_pcm()
 def test_14_no_hardware_output_emitter(self):self.assertEqual(self.c.lib.fm_acoustic_native_backend_available(),0)
 def test_15_no_em_driver(self):self.assertEqual(self.c.lib.fm_em_backend_available(),0)
 def test_16_bureau_state_normal(self):self.assertEqual(self.c.get_r61_fault_status()['state'],'NORMAL_NO_OUTPUT')
 def test_17_change_native_identity_without_ever_pinned_remains_unbound(self):
  self.c.validate({'channel':'acoustic','hz':1000.0,'level':.005,'duration_ms':100})
  self.assertEqual(self.c.get_r62_identity_status()['state'],'UNBOUND')
 def test_18_unbound_secret_does_not_reach_api(self):self.assertNotIn('os_uid',self.c.get_r62_identity_status())

class R64Digital(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();cls.c=a.NativeCore(pathlib.Path(cls.tmp.name))
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def arr(self, values):
  return (ctypes.c_float*len(values))(*values)
 def verify(self, vals, channels=1, max_peak=.01):
  buf=self.arr(vals);proof=a.FMR64DigitalIntegrity()
  res=self.c.lib.fm_r64_verify_digital_pcm(buf,len(vals),channels,ctypes.c_float(max_peak),ctypes.byref(proof))
  return res,proof
 def test_19_zero_mono_valid(self):self.assertEqual(self.verify([0,0])[0],1)
 def test_20_zero_stereo_valid(self):self.assertEqual(self.verify([0,0,0,0],2)[0],1)
 def test_21_midpoint_numeric_nonzero_valid(self):self.assertEqual(self.verify([0,.003,0])[0],1)
 def test_22_peak_report(self):
  ok,p=self.verify([0,.003,0]);self.assertEqual(ok,1);self.assertEqual(p.checked_samples,3)
  self.assertAlmostEqual(p.digital_peak_normalized,.003,places=5)
 def test_23_bound_exceeded_refused(self):self.assertEqual(self.verify([0,.02,0])[0],0)
 def test_24_nan_refused(self):self.assertEqual(self.verify([0,float('nan'),0])[0],0)
 def test_25_positive_inf_refused(self):self.assertEqual(self.verify([0,float('inf'),0])[0],0)
 def test_26_negative_inf_refused(self):self.assertEqual(self.verify([0,-float('inf'),0])[0],0)
 def test_27_nonzero_first_refused(self):self.assertEqual(self.verify([.001,0,0])[0],0)
 def test_28_nonzero_last_refused(self):self.assertEqual(self.verify([0,0,.001])[0],0)
 def test_29_stereo_nonzero_second_channel_start_refused(self):self.assertEqual(self.verify([0,.001,0,0],2)[0],0)
 def test_30_stereo_nonzero_second_channel_end_refused(self):self.assertEqual(self.verify([0,0,0,.001],2)[0],0)
 def test_31_stereo_odd_total_refused(self):self.assertEqual(self.verify([0,0,0],2)[0],0)
 def test_32_zero_channels_refused(self):self.assertEqual(self.verify([0,0],0)[0],0)
 def test_33_more_than_stereo_refused(self):self.assertEqual(self.verify([0,0,0,0,0,0],3)[0],0)
 def test_34_short_input_refused(self):self.assertEqual(self.verify([0])[0],0)
 def test_35_zero_maximum_refuses_nonzero(self):self.assertEqual(self.verify([0,.003,0],max_peak=0)[0],0)
 def test_36_bad_maximum_negative(self):self.assertEqual(self.verify([0,0],max_peak=-1)[0],0)
 def test_37_bad_maximum_nan(self):self.assertEqual(self.verify([0,0],max_peak=float('nan'))[0],0)
 def test_38_bad_maximum_inf(self):self.assertEqual(self.verify([0,0],max_peak=float('inf'))[0],0)
 def test_39_bad_maximum_above_limit(self):self.assertEqual(self.verify([0,0],max_peak=.5)[0],0)
 def test_40_null_pcm_refused(self):
  p=a.FMR64DigitalIntegrity()
  self.assertEqual(self.c.lib.fm_r64_verify_digital_pcm(None,2,1,.01,ctypes.byref(p)),0)
 def test_41_null_report_refused(self):
  self.assertEqual(self.c.lib.fm_r64_verify_digital_pcm(self.arr([0,0]),2,1,.01,None),0)
 def test_42_failure_clears_previous_report(self):
  p=a.FMR64DigitalIntegrity();p.checked_samples=567;p.channels=2;p.digital_peak_normalized=.8;p.zero_edges=1
  self.assertEqual(self.c.lib.fm_r64_verify_digital_pcm(self.arr([0,.5,0]),3,1,.01,ctypes.byref(p)),0)
  self.assertEqual((p.checked_samples,p.channels,p.zero_edges),(0,0,0))
 def test_43_r63_full_block_integrity(self):
  s=a.FMR59Session();s.phase=1;s.channels=2;s.sample_rate_hz=44100.
  s.command=a.FMCommand(1,440.,.01,500);s.digital_frame_budget=22050
  buf=(ctypes.c_float*44100)();out=a.FMR63DigitalReport()
  self.assertEqual(self.c.lib.fm_r63_render_digital_pcm(ctypes.byref(s),buf,44100,ctypes.byref(out)),1)
  p=a.FMR64DigitalIntegrity()
  self.assertEqual(self.c.lib.fm_r64_verify_digital_pcm(buf,44100,2,.01,ctypes.byref(p)),1)
  self.assertEqual(p.checked_samples,44100);self.assertEqual(p.zero_edges,1)
  self.c.lib.fm_r63_zeroize_digital_pcm(buf,44100);self.assertFalse(any(buf))
 def test_44_r63_damage_after_render_rejected(self):
  s=a.FMR59Session();s.phase=1;s.channels=1;s.sample_rate_hz=48000.
  s.command=a.FMCommand(1,900.,.01,200);s.digital_frame_budget=9600
  buf=(ctypes.c_float*9600)();out=a.FMR63DigitalReport()
  self.assertEqual(self.c.lib.fm_r63_render_digital_pcm(ctypes.byref(s),buf,9600,ctypes.byref(out)),1)
  buf[100]=.5;p=a.FMR64DigitalIntegrity()
  self.assertEqual(self.c.lib.fm_r64_verify_digital_pcm(buf,9600,1,.01,ctypes.byref(p)),0)
  self.c.lib.fm_r63_zeroize_digital_pcm(buf,9600);self.assertFalse(any(buf))
 def test_45_r63_phase_stop_refuses(self):
  s=a.FMR59Session();s.phase=3;buf=(ctypes.c_float*4)();r=a.FMR63DigitalReport()
  self.assertEqual(self.c.lib.fm_r63_render_digital_pcm(ctypes.byref(s),buf,4,ctypes.byref(r)),0)
 def test_46_ffi_status_no_spl(self):self.assertNotIn('spl',a.FMR64DigitalIntegrity._fields_[0][0])
 def test_47_ffi_signed_no_measurement(self):self.assertEqual(self.c.status()['physical_emission'],'NONE_BY_THIS_APPLICATION')
 def test_48_report_only_counts(self):
  ok,p=self.verify([0,.001,0]);self.assertEqual(ok,1);self.assertEqual(p.channels,1)

class R64UI(unittest.TestCase):
 def test_49_ui_version(self):self.assertIn('v0.9.0',(ROOT/'static/index.html').read_text())
 def test_50_ui_route_identity_label(self):self.assertIn('GEN-R65',(ROOT/'static/index.html').read_text())
 def test_51_10_languages_integrity(self):
  js=(ROOT/'static/r63.js').read_text()
  for lang in ['en','fr','de','ar','es','pt','hr','it','zh','ko']:
   self.assertIn(lang+':[',js)
  self.assertIn('digital_envelope_verified',js)
 def test_52_command_validation_separated(self):
  js=(ROOT/'static/app.js').read_text()
  self.assertIn('indépendant de la préparation PCM',js)
  self.assertIn('C COMMAND VALIDATION',js)
 def test_53_no_output_symbols_in_r64_c(self):
  src=(ROOT/'native/acoustic_integrity_r64.c').read_text()
  for forbidden in ['AudioQueueStart','AudioQueueNewOutput','AudioUnitInitialize','popen(','system(','fm_acoustic_physical_output(']:self.assertNotIn(forbidden,src)
 def test_54_c_unchanged_guardian_hard_denied(self):self.assertIn('HARD_DENIED',(ROOT/'app.py').read_text())
 def test_55_old_stop_tooltip_hidden(self):self.assertIn('id="r55-stop-disclaimer" hidden',(ROOT/'static/index.html').read_text())
 def test_56_r64_preparation_performs_r59_r60_r61_r62_guard(self):
  source=(ROOT/'app.py').read_text()
  prep=source.split('def prepare_r63_digital_pcm(self):',1)[1].split('\n    def ',1)[0]
  for fragment in ['r59_session.phase','fm_r60_lease_check','_r62_check_locked','fm_r61_fault_can_bind','fm_r64_verify_digital_pcm','finally:','fm_r63_zeroize_digital_pcm']:
   self.assertIn(fragment,prep)
 def test_57_not_a_measurement(self):self.assertNotIn('CoreAudio', (ROOT/'native/acoustic_integrity_r64.c').read_text())
 def test_58_no_auto_start(self):self.assertNotIn('start_route_monitor(interval_seconds=1.2)\n        server =', (ROOT/'app.py').read_text())
 def test_59_uses_same_native_command_c(self):self.assertIn('fm_validate_command',(ROOT/'native/generator_core.c').read_text())
 def test_60_r64_runner_syntax_text(self):self.assertIn('GEN_R64_PRELAUNCH_TEST_SUITE=PASS',(ROOT/'RUN_GEN_R65_MAC_INTEL.command').read_text())

if __name__=='__main__':unittest.main()
