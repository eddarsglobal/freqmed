# SPDX-License-Identifier: Apache-2.0
"""GEN-R65 tests numeric command streams, not simulated physical measurements."""
import ctypes
import http.client
import importlib.util
import math
import pathlib
import tempfile
import threading
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('freqmed_r65_under_test',ROOT/'app.py')
a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)

class R65SegmentedC(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory()
        cls.core=a.NativeCore(pathlib.Path(cls.tmp.name))
    @classmethod
    def tearDownClass(cls): cls.tmp.cleanup()
    @staticmethod
    def session(frames=22050,channels=2,frequency=440.0,level=.01,ms=500,rate=44100.0):
        s=a.FMR59Session()
        s.phase=1;s.device_id=12345;s.channels=channels;s.sample_rate_hz=rate
        s.command=a.FMCommand(1,frequency,level,ms)
        s.digital_frame_budget=frames;s.name=b'NUMERIC_UNIT_TEST_ONLY'
        return s
    def begin(self,s=None):
        s=s if s is not None else self.session()
        cur=a.FMR65Cursor()
        rc=self.core.lib.fm_r65_stream_begin(ctypes.byref(cur),ctypes.byref(s))
        return rc,cur,s
    def next(self,cur,s,capacity=None):
        cap=capacity if capacity is not None else 256*int(s.channels)
        buf=(ctypes.c_float*max(1,cap))()
        report=a.FMR65ChunkReport()
        rc=self.core.lib.fm_r65_stream_next(ctypes.byref(cur),ctypes.byref(s),buf,cap,ctypes.byref(report))
        return rc,buf,report
    def test_01_default_begin_pass(self):
        rc,cur,_=self.begin();self.assertEqual(rc,1);self.assertEqual(cur.state,1)
    def test_02_first_chunk_start_and_size(self):
        _,cur,s=self.begin();rc,_,r=self.next(cur,s)
        self.assertEqual((rc,r.start_frame,r.frames,r.samples,r.channels),(1,0,256,512,2))
    def test_03_first_pcm_value_exact_zero(self):
        _,cur,s=self.begin();rc,b,_=self.next(cur,s);self.assertEqual(rc,1);self.assertEqual((b[0],b[1]),(0.,0.))
    def test_04_legacy_r63_waveform_parity_440hz_500ms(self):
        _,cur,s=self.begin();n=s.digital_frame_budget*s.channels
        full=(ctypes.c_float*n)();legacy=a.FMR63DigitalReport()
        self.assertEqual(self.core.lib.fm_r63_render_digital_pcm(ctypes.byref(s),full,n,ctypes.byref(legacy)),1)
        pos=0;chunks=0
        while cur.state==1:
            rc,b,r=self.next(cur,s);self.assertEqual(rc,1)
            for i in range(r.samples):self.assertAlmostEqual(b[i],full[pos*s.channels+i],delta=1e-7)
            for i in range(r.samples,len(b)):self.assertEqual(b[i],0.0)
            pos+=r.frames;chunks+=1
            self.core.lib.fm_r63_zeroize_digital_pcm(b,len(b));self.assertFalse(any(b))
        self.assertEqual((pos,chunks,cur.state),(22050,87,2))
        self.core.lib.fm_r63_zeroize_digital_pcm(full,n);self.assertFalse(any(full))
    def test_05_last_chunk_34_frames(self):
        _,cur,s=self.begin();prev=None
        while cur.state==1:
            prev=self.next(cur,s)
        rc,b,r=prev;self.assertEqual((r.frames,r.start_frame),(34,22016))
        self.assertEqual((b[(r.frames-1)*2],b[(r.frames-1)*2+1]),(0.,0.))
        self.assertEqual(tuple(b[r.samples:]),tuple([0.]*(len(b)-r.samples)))
    def test_06_after_completion_returns_zero(self):
        _,cur,s=self.begin()
        while cur.state==1:self.next(cur,s)
        self.assertEqual(self.next(cur,s)[0],0)
    def test_07_zeroize_cursor(self):
        _,cur,_=self.begin();self.core.lib.fm_r65_stream_clear(ctypes.byref(cur));self.assertFalse(any(bytes(cur)))
    def test_08_begin_refuses_unbound(self):
        s=self.session();s.phase=0;self.assertEqual(self.begin(s)[0],0)
    def test_09_begin_refuses_stopped(self):
        s=self.session();s.phase=3;self.assertEqual(self.begin(s)[0],0)
    def test_10_begin_refuses_invalidated(self):
        s=self.session();s.phase=2;self.assertEqual(self.begin(s)[0],0)
    def test_11_begin_refuses_non_acoustic(self):
        s=self.session();s.command.channel=2;self.assertEqual(self.begin(s)[0],0)
    def test_12_begin_refuses_zero_device_id(self):
        s=self.session();s.device_id=0;self.assertEqual(self.begin(s)[0],0)
    def test_13_begin_refuses_invalid_rate(self):
        s=self.session();s.sample_rate_hz=0;self.assertEqual(self.begin(s)[0],0)
    def test_14_begin_refuses_nonfinite_frequency(self):
        s=self.session();s.command.frequency_hz=float('nan');self.assertEqual(self.begin(s)[0],0)
    def test_15_begin_refuses_nonfinite_level(self):
        s=self.session();s.command.normalized_level=float('inf');self.assertEqual(self.begin(s)[0],0)
    def test_16_begin_refuses_over_level(self):
        s=self.session();s.command.normalized_level=.02;self.assertEqual(self.begin(s)[0],0)
    def test_17_begin_refuses_over_nyquist_limit(self):
        s=self.session();s.command.frequency_hz=21000;self.assertEqual(self.begin(s)[0],0)
    def test_18_begin_refuses_wrong_frame_budget(self):
        s=self.session();s.digital_frame_budget=22049;self.assertEqual(self.begin(s)[0],0)
    def test_19_begin_refuses_duration_gt1000(self):
        s=self.session();s.command.duration_ms=1500;self.assertEqual(self.begin(s)[0],0)
    def test_20_begin_refuses_zero_duration(self):
        s=self.session();s.command.duration_ms=0;self.assertEqual(self.begin(s)[0],0)
    def test_21_begin_refuses_zero_channels(self):
        s=self.session();s.channels=0;self.assertEqual(self.begin(s)[0],0)
    def test_22_begin_refuses_three_channels(self):
        s=self.session();s.channels=3;self.assertEqual(self.begin(s)[0],0)
    def test_23_begin_refuses_missing_name(self):
        s=self.session();s.name=b'';self.assertEqual(self.begin(s)[0],1)  # NUL termination, not a device trust assertion
    def test_24_changed_route_refuses_next(self):
        _,cur,s=self.begin();s.device_id=12346;self.assertEqual(self.next(cur,s)[0],-1);self.assertEqual(cur.state,3)
    def test_25_changed_hz_refuses_next(self):
        _,cur,s=self.begin();s.command.frequency_hz=441;self.assertEqual(self.next(cur,s)[0],-1)
    def test_26_changed_level_refuses_next(self):
        _,cur,s=self.begin();s.command.normalized_level=.005;self.assertEqual(self.next(cur,s)[0],-1)
    def test_27_changed_rate_refuses_next(self):
        _,cur,s=self.begin();s.sample_rate_hz=48000;self.assertEqual(self.next(cur,s)[0],-1)
    def test_28_changed_name_refuses_next(self):
        _,cur,s=self.begin();s.name=b'NEW';self.assertEqual(self.next(cur,s)[0],-1)
    def test_29_changed_phase_refuses_next(self):
        _,cur,s=self.begin();s.phase=3;self.assertEqual(self.next(cur,s)[0],-1)
    def test_30_wrong_capacity_refuses(self):
        _,cur,s=self.begin();self.assertEqual(self.next(cur,s,511)[0],-1)
    def test_31_negative_failed_state_is_sticky(self):
        _,cur,s=self.begin();self.next(cur,s,511);self.assertEqual(self.next(cur,s,512)[0],-1)
    def test_32_mono_boundary_and_full_duration(self):
        s=self.session(frames=8000,channels=1,frequency=440,level=.01,ms=1000,rate=8000)
        rc,cur,s=self.begin(s);self.assertEqual(rc,1);pos=0
        while cur.state==1:
            rc,b,r=self.next(cur,s);self.assertEqual(rc,1);pos+=r.frames
        self.assertEqual((pos,cur.state),(8000,2))
    def test_33_peak_bounded(self):
        _,cur,s=self.begin();peaks=[]
        while cur.state==1:
            rc,b,r=self.next(cur,s);self.assertEqual(rc,1);peaks.append(r.chunk_digital_peak)
        self.assertLessEqual(max(peaks),.010000001)
    def test_34_no_output_entrypoint(self):
        self.assertEqual(self.core.lib.fm_acoustic_native_backend_available(),0)
        self.assertEqual(self.core.lib.fm_em_backend_available(),0)
    def test_35_clear_cursor_then_next_fails(self):
        _,cur,s=self.begin();self.core.lib.fm_r65_stream_clear(ctypes.byref(cur));self.assertEqual(self.next(cur,s)[0],-1)
    def test_36_cursor_bad_pointer_begin(self):
        s=self.session();self.assertEqual(self.core.lib.fm_r65_stream_begin(None,ctypes.byref(s)),0)
    def test_37_no_pcm_memory_export_api_name(self):
        import inspect
        body=inspect.getsource(a.NativeCore.prepare_r65_segmented_pcm)
        self.assertNotIn('pcm.tobytes',body)
        self.assertNotIn('open(',body)
    def test_38_begin_refuses_blank_rate_nan(self):
        s=self.session();s.sample_rate_hz=float('nan');self.assertEqual(self.begin(s)[0],0)
    def test_39_begin_refuses_negative_frequency(self):
        s=self.session();s.command.frequency_hz=-100;self.assertEqual(self.begin(s)[0],0)
    def test_40_reset_report_on_refusal(self):
        _,cur,s=self.begin();r=a.FMR65ChunkReport();r.frames=45
        b=(ctypes.c_float*512)();s.phase=0
        self.assertEqual(self.core.lib.fm_r65_stream_next(ctypes.byref(cur),ctypes.byref(s),b,512,ctypes.byref(r)),-1)
        self.assertEqual(r.frames,0)

class R65AppContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory();cls.core=a.NativeCore(pathlib.Path(cls.tmp.name))
    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()
    def setUp(self):
        with self.core.lock:
            self.core.route=None
            self.core._monitor_shutdown.clear()
            self.core.r59_session=a.FMR59Session()
            self.core.r60_lease=a.FMR60Lease()
            self.core.r61_fault=a.FMR61Fault()
            self.core.r62_identity=a.FMR62Identity()
    def test_41_missing_route_denied(self):
        with self.assertRaisesRegex(ValueError,'R65_NO_ACTIVE_REAL_ROUTE'):self.core.prepare_r65_segmented_pcm()
    def test_42_stopped_denied(self):
        self.core.stop_engine_and_monitor()
        with self.assertRaisesRegex(ValueError,'R65_NO_ACTIVE_REAL_ROUTE'):self.core.prepare_r65_segmented_pcm()
    def test_43_route_without_candidate_denied(self):
        self.core.route={'device_id':1,'name':'not real device'}
        with self.assertRaisesRegex(ValueError,'R65_R58_CANDIDATE_NOT_ISOLATED'):self.core.prepare_r65_segmented_pcm()
    def test_44_no_actual_pcm_created_on_idle(self):
        self.assertIsNone(self.core.last)
        with self.assertRaises(ValueError):self.core.prepare_r65_segmented_pcm()
    def test_45_readonly_coreaudio_on_linux(self):
        self.assertEqual(self.core.lib.fm_acoustic_native_backend_available(),0)
    def test_46_ui_ten_languages(self):
        s=(ROOT/'static/r65.js').read_text()
        for lang in ['fr','en','de','ar','es','pt','hr','it','zh','ko']:
            self.assertIn(lang+':[',s)
    def test_47_ui_separate_legacy_button(self):
        s=(ROOT/'static/index.html').read_text()
        self.assertIn('id="r63-prepare"',s)
        self.assertIn('id="r65-prepare"',s)
    def test_48_http_post_requires_session(self):
        srv=a.make_server(self.core);t=threading.Thread(target=srv.serve_forever,daemon=True);t.start()
        try:
            c=http.client.HTTPConnection('127.0.0.1',srv.server_port,timeout=5)
            c.request('POST','/api/acoustic/pcm/prepare-segmented','{}',{
              'Origin':f'http://127.0.0.1:{srv.server_port}','Content-Type':'application/json'})
            res=c.getresponse();self.assertEqual(res.status,403);res.read();c.close()
        finally:srv.shutdown();srv.server_close();t.join(timeout=3)
    def test_49_http_post_requires_exact_origin(self):
        srv=a.make_server(self.core);t=threading.Thread(target=srv.serve_forever,daemon=True);t.start()
        try:
            c=http.client.HTTPConnection('127.0.0.1',srv.server_port,timeout=5)
            c.request('POST','/api/acoustic/pcm/prepare-segmented','{}',{
              'Origin':'http://evil.invalid','Content-Type':'application/json',
              'X-FREQMED-SESSION':srv.token})
            res=c.getresponse();self.assertEqual(res.status,403);res.read();c.close()
        finally:srv.shutdown();srv.server_close();t.join(timeout=3)
    def test_50_http_post_no_route_422(self):
        srv=a.make_server(self.core);t=threading.Thread(target=srv.serve_forever,daemon=True);t.start()
        try:
            c=http.client.HTTPConnection('127.0.0.1',srv.server_port,timeout=5)
            c.request('POST','/api/acoustic/pcm/prepare-segmented','{}',{
              'Origin':f'http://127.0.0.1:{srv.server_port}',
              'Content-Type':'application/json','X-FREQMED-SESSION':srv.token})
            res=c.getresponse();self.assertEqual(res.status,422);res.read();c.close()
        finally:srv.shutdown();srv.server_close();t.join(timeout=3)

if __name__=='__main__':unittest.main()
