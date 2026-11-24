# SPDX-License-Identifier: Apache-2.0
"""R66 independent C validation of digital PCM command chunks, NEVER physical measurements."""
import ctypes
import http.client
import importlib.util
import inspect
import pathlib
import tempfile
import threading
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('freqmed_r66_under_test',ROOT/'app.py')
a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)

class R66NativeAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.core = a.NativeCore(pathlib.Path(cls.tmp.name))
    @classmethod
    def tearDownClass(cls): cls.tmp.cleanup()
    def session(self, frames=22050, channels=2, duration=500, rate=44100):
        s = a.FMR59Session()
        s.phase=1;s.device_id=12345;s.channels=channels;s.sample_rate_hz=rate
        s.command=a.FMCommand(1,440.,.01,duration)
        s.digital_frame_budget=frames;s.name=b'NUMERIC_COMMAND_UNIT_TEST'
        return s
    def begin(self, session=None):
        s=session or self.session()
        cur=a.FMR65Cursor(); audit=a.FMR66Audit()
        self.assertEqual(self.core.lib.fm_r65_stream_begin(ctypes.byref(cur),ctypes.byref(s)),1)
        self.assertEqual(self.core.lib.fm_r66_audit_begin(ctypes.byref(audit),s.digital_frame_budget,s.channels),1)
        return s,cur,audit
    def chunk(self, s, cur, audit, mutate=None):
        capacity=256*s.channels
        pcm=(ctypes.c_float*capacity)(); report=a.FMR65ChunkReport()
        self.assertEqual(self.core.lib.fm_r65_stream_next(ctypes.byref(cur),ctypes.byref(s),pcm,capacity,ctypes.byref(report)),1)
        if mutate: mutate(pcm,report)
        return self.core.lib.fm_r66_audit_chunk(ctypes.byref(audit),ctypes.byref(report),pcm,capacity),pcm,report
    def fails(self,mutate):
        s,cur,audit=self.begin()
        rc,pcm,report=self.chunk(s,cur,audit,mutate)
        self.assertEqual(rc,0)
        self.assertEqual(audit.state,3)
        self.core.lib.fm_r63_zeroize_digital_pcm(pcm,len(pcm))
        self.assertFalse(any(pcm))
    def test_01_complete_87_segments(self):
        s,cur,audit=self.begin()
        while cur.state==1:
            ok,pcm,_=self.chunk(s,cur,audit);self.assertEqual(ok,1)
            self.core.lib.fm_r63_zeroize_digital_pcm(pcm,len(pcm));self.assertFalse(any(pcm))
        self.assertEqual(self.core.lib.fm_r66_audit_finish(ctypes.byref(audit)),1)
        self.assertEqual((audit.checked_frames,audit.checked_samples,audit.segments,audit.state),(22050,44100,87,2))
        self.assertTrue(0 < audit.observed_digital_peak <= .010000001)
    def test_02_exact_first_chunk(self):
        s,cur,audit=self.begin();ok,_,report=self.chunk(s,cur,audit)
        self.assertEqual((ok,report.start_frame,report.frames,audit.checked_frames),(1,0,256,256))
    def test_03_mono_full_duration(self):
        s=self.session(frames=8000,channels=1,duration=1000,rate=8000)
        s,cur,audit=self.begin(s)
        while cur.state==1:
            ok,_,_=self.chunk(s,cur,audit);self.assertEqual(ok,1)
        self.assertEqual((audit.checked_samples,audit.segments),(8000,32))
        self.assertEqual(self.core.lib.fm_r66_audit_finish(ctypes.byref(audit)),1)
    def test_04_tiny_last_segment(self):
        s=self.session(frames=1,channels=2,duration=1,rate=1000)
        # R65 has minimum OS rate 8000, use 8 frames at 8kHz for 1ms.
        s.sample_rate_hz=8000;s.digital_frame_budget=8
        s,cur,audit=self.begin(s)
        ok,pcm,report=self.chunk(s,cur,audit)
        self.assertEqual((ok,report.frames,report.samples),(1,8,16))
        self.assertEqual(self.core.lib.fm_r66_audit_finish(ctypes.byref(audit)),1)
    def test_05_clear_zeroizes_auditor(self):
        _,_,audit=self.begin();self.core.lib.fm_r66_audit_clear(ctypes.byref(audit))
        self.assertFalse(any(bytes(audit)))
    def test_06_begin_rejects_zero_frames(self):
        au=a.FMR66Audit();self.assertEqual(self.core.lib.fm_r66_audit_begin(ctypes.byref(au),0,2),0)
        self.assertEqual(au.state,3)
    def test_07_begin_rejects_frames_over_cap(self):
        au=a.FMR66Audit();self.assertEqual(self.core.lib.fm_r66_audit_begin(ctypes.byref(au),96001,2),0)
    def test_08_begin_rejects_zero_channels(self):
        au=a.FMR66Audit();self.assertEqual(self.core.lib.fm_r66_audit_begin(ctypes.byref(au),10,0),0)
    def test_09_begin_rejects_three_channels(self):
        au=a.FMR66Audit();self.assertEqual(self.core.lib.fm_r66_audit_begin(ctypes.byref(au),10,3),0)
    def test_10_begin_null_pointer(self):
        self.assertEqual(self.core.lib.fm_r66_audit_begin(None,10,2),0)
    def test_11_finish_before_first_chunk(self):
        _,_,au=self.begin();self.assertEqual(self.core.lib.fm_r66_audit_finish(ctypes.byref(au)),0)
        self.assertEqual(au.state,3)
    def test_12_wrong_start_offset(self): self.fails(lambda b,r:setattr(r,'start_frame',1))
    def test_13_wrong_frame_count(self): self.fails(lambda b,r:setattr(r,'frames',255))
    def test_14_wrong_sample_count(self): self.fails(lambda b,r:setattr(r,'samples',511))
    def test_15_wrong_channel_count(self): self.fails(lambda b,r:setattr(r,'channels',1))
    def test_16_zero_edges_flag_lie(self): self.fails(lambda b,r:setattr(r,'zero_edges_verified',0))
    def test_17_nan_sample(self): self.fails(lambda b,r:b.__setitem__(20,float('nan')))
    def test_18_inf_sample(self): self.fails(lambda b,r:b.__setitem__(20,float('inf')))
    def test_19_over_peak_sample(self): self.fails(lambda b,r:b.__setitem__(20,.2))
    def test_20_stereo_channel_mismatch(self): self.fails(lambda b,r:b.__setitem__(21,.0004))
    def test_21_forged_peak(self): self.fails(lambda b,r:setattr(r,'chunk_digital_peak',0.))
    def test_22_nonzero_first_frame(self): self.fails(lambda b,r:b.__setitem__(0,.001))
    def test_23_negative_report_peak(self): self.fails(lambda b,r:setattr(r,'chunk_digital_peak',-1.))
    def test_24_nan_report_peak(self): self.fails(lambda b,r:setattr(r,'chunk_digital_peak',float('nan')))
    def test_25_wrong_capacity(self):
        s,cur,au=self.begin();pcm=(ctypes.c_float*512)();rep=a.FMR65ChunkReport()
        self.assertEqual(self.core.lib.fm_r65_stream_next(ctypes.byref(cur),ctypes.byref(s),pcm,512,ctypes.byref(rep)),1)
        self.assertEqual(self.core.lib.fm_r66_audit_chunk(ctypes.byref(au),ctypes.byref(rep),pcm,511),0)
    def test_26_null_pcm(self):
        s,cur,au=self.begin();pcm=(ctypes.c_float*512)();rep=a.FMR65ChunkReport()
        self.assertEqual(self.core.lib.fm_r65_stream_next(ctypes.byref(cur),ctypes.byref(s),pcm,512,ctypes.byref(rep)),1)
        self.assertEqual(self.core.lib.fm_r66_audit_chunk(ctypes.byref(au),ctypes.byref(rep),None,512),0)
    def test_27_null_report(self):
        s,cur,au=self.begin();self.assertEqual(self.core.lib.fm_r66_audit_chunk(ctypes.byref(au),None,(ctypes.c_float*512)(),512),0)
    def test_28_sticky_failure(self):
        s,cur,au=self.begin();ok,_,_=self.chunk(s,cur,au,lambda b,r:setattr(r,'frames',255));self.assertEqual(ok,0)
        ok,_,_=self.chunk(s,cur,au);self.assertEqual(ok,0)
        self.assertEqual(self.core.lib.fm_r66_audit_finish(ctypes.byref(au)),0)
    def test_29_nonzero_last_frame(self):
        s,cur,au=self.begin();mutated=False
        while cur.state==1:
            pcm=(ctypes.c_float*512)();rep=a.FMR65ChunkReport()
            self.assertEqual(self.core.lib.fm_r65_stream_next(ctypes.byref(cur),ctypes.byref(s),pcm,512,ctypes.byref(rep)),1)
            if cur.state==2: pcm[(rep.frames-1)*2]=.001;mutated=True
            result=self.core.lib.fm_r66_audit_chunk(ctypes.byref(au),ctypes.byref(rep),pcm,512)
            if mutated:self.assertEqual(result,0)
            else:self.assertEqual(result,1)
        self.assertTrue(mutated)
    def test_30_nonzero_unused_tail(self):
        s,cur,au=self.begin()
        while cur.state==1:
            pcm=(ctypes.c_float*512)();rep=a.FMR65ChunkReport()
            self.assertEqual(self.core.lib.fm_r65_stream_next(ctypes.byref(cur),ctypes.byref(s),pcm,512,ctypes.byref(rep)),1)
            if cur.state==2:pcm[rep.samples]=.0001
            result=self.core.lib.fm_r66_audit_chunk(ctypes.byref(au),ctypes.byref(rep),pcm,512)
            self.assertEqual(result,0 if cur.state==2 else 1)
    def test_31_finish_double_denied(self):
        s,cur,au=self.begin()
        while cur.state==1:self.chunk(s,cur,au)
        self.assertEqual(self.core.lib.fm_r66_audit_finish(ctypes.byref(au)),1)
        self.assertEqual(self.core.lib.fm_r66_audit_finish(ctypes.byref(au)),0)
    def test_32_no_physical_output_exports(self):
        self.assertEqual(self.core.lib.fm_acoustic_native_backend_available(),0)
        self.assertEqual(self.core.lib.fm_em_backend_available(),0)

class R66AppIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory()
        cls.core=a.NativeCore(pathlib.Path(cls.tmp.name))
    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()
    def test_33_api_no_route_denied(self):
        self.core.route=None
        with self.assertRaisesRegex(ValueError,'R65_NO_ACTIVE_REAL_ROUTE'):
            self.core.prepare_r65_segmented_pcm()
    def test_34_c_audit_bound_to_prepare(self):
        source=inspect.getsource(a.NativeCore.prepare_r65_segmented_pcm)
        for phrase in ['fm_r66_audit_begin','fm_r66_audit_chunk','fm_r66_audit_finish','fm_r66_audit_clear']:
            self.assertIn(phrase,source)
    def test_35_audit_clear_in_finally(self):
        src=inspect.getsource(a.NativeCore.prepare_r65_segmented_pcm)
        self.assertIn('finally:',src)
        self.assertIn('any(bytes(audit66))',src)
    def test_36_r66_manifest_required(self):
        src=inspect.getsource(a.verify_manifest)
        self.assertIn('RUN_GEN_R66_MAC_INTEL.command',src)
        self.assertIn('BUREAU_GEN_R66_REPORT.md',src)
    def test_37_foss_no_audioqueue(self):
        code=(ROOT/'native/acoustic_sequence_audit_r66.c').read_text()
        for unsafe in ['AudioQueue','AudioUnitRender','AudioOutputUnitStart','IOBluetooth','rf_transmit']:
            self.assertNotIn(unsafe,code)
    def test_38_ui_10_locales(self):
        js=(ROOT/'static/r65.js').read_text()
        for language in ('fr','en','de','ar','es','pt','hr','it','zh','ko'):
            self.assertIn(language+':[',js)
        self.assertIn('PASS_NATIVE_DIGITAL_SAMPLES_NO_PLAYBACK',js)
    def test_39_status_server_only_no_pcm(self):
        src=inspect.getsource(a.NativeCore.prepare_r65_segmented_pcm)
        self.assertNotIn('tobytes()',src)
        self.assertIn('"sequence_audit_r66"',src)
    def test_40_single_r65_button(self):
        html=(ROOT/'static/index.html').read_text()
        self.assertEqual(html.count('id="r65-prepare"'),1)
        self.assertNotIn('id="r66-prepare"',html)
    def test_41_http_auth_before_prepare(self):
        srv=a.make_server(self.core);th=threading.Thread(target=srv.serve_forever,daemon=True);th.start()
        try:
            c=http.client.HTTPConnection('127.0.0.1',srv.server_port,timeout=5)
            c.request('POST','/api/acoustic/pcm/prepare-segmented','{}',{
                'Origin':f'http://127.0.0.1:{srv.server_port}',
                'Content-Type':'application/json'})
            res=c.getresponse();self.assertEqual(res.status,403);res.read();c.close()
        finally:
            srv.shutdown();srv.server_close();th.join(timeout=3)
    def test_42_http_invalid_origin_denied(self):
        srv=a.make_server(self.core);th=threading.Thread(target=srv.serve_forever,daemon=True);th.start()
        try:
            c=http.client.HTTPConnection('127.0.0.1',srv.server_port,timeout=5)
            c.request('POST','/api/acoustic/pcm/prepare-segmented','{}',{
                'Origin':'http://evil.invalid','Content-Type':'application/json',
                'X-FREQMED-SESSION':srv.token})
            res=c.getresponse();self.assertEqual(res.status,403);res.read();c.close()
        finally:srv.shutdown();srv.server_close();th.join(timeout=3)

if __name__=='__main__':unittest.main()
