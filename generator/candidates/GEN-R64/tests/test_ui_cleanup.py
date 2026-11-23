# SPDX-License-Identifier: Apache-2.0
"""UI cleanup contract: no removal of native features or route permissions."""
import hashlib
import http.client
from html.parser import HTMLParser
import importlib.util
import json
from pathlib import Path
import tempfile
import threading
import unittest

ROOT=Path(__file__).resolve().parents[1]
HTML=(ROOT/'static/index.html').read_text(encoding='utf-8')
CSS=(ROOT/'static/cleanup.css').read_text(encoding='utf-8')
JS=(ROOT/'static/cleanup.js').read_text(encoding='utf-8')

class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack=[];self.tags={};self.legacy_ids=set();self.duplicate=set()
        self.tag_count=0
    def handle_starttag(self,tag,attrs):
        props=dict(attrs);id=props.get('id')
        self.tag_count+=1
        if id:
            if id in self.tags:self.duplicate.add(id)
            self.tags[id]={'tag':tag,'attrs':props,'parents':tuple(self.stack)}
        if tag not in ('meta','link','br','img','input','hr','source','area'):
            self.stack.append((tag,props.get('id'),props.get('class','')))
    def handle_endtag(self,tag):
        for k in range(len(self.stack)-1,-1,-1):
            if self.stack[k][0]==tag:
                self.stack=self.stack[:k]
                break
p=Page();p.feed(HTML)

class CleanupStructure(unittest.TestCase):
    def test_01_doc_parses(self):self.assertGreater(p.tag_count,120)
    def test_02_no_duplicate_ids(self):self.assertFalse(p.duplicate)
    def test_03_four_step_layout(self):self.assertEqual(HTML.count('fm-step-num'),4)
    def test_04_command_visible(self):self.assertIn('command-section',p.tags)
    def test_05_route_visible(self):self.assertIn('r54-select',p.tags)
    def test_06_session_visible(self):self.assertIn('r59-bind',p.tags)
    def test_07_stop_visible(self):self.assertIn('r55-software-stop',p.tags)
    def test_08_resumption_preserved(self):self.assertIn('r55-resume-monitor',p.tags)
    def test_09_legacy_details_default_closed(self):
        self.assertEqual(p.tags['fm-advanced']['tag'],'details')
        self.assertNotIn('open',p.tags['fm-advanced']['attrs'])
    def test_10_r56_in_advanced(self):self.assertTrue(any(x[1]=='fm-advanced' for x in p.tags['r56-prepare']['parents']))
    def test_11_r57_in_advanced(self):self.assertTrue(any(x[1]=='fm-advanced' for x in p.tags['r57-inspect']['parents']))
    def test_12_r58_in_advanced(self):self.assertTrue(any(x[1]=='fm-advanced' for x in p.tags['r58-check']['parents']))
    def test_13_r59_not_hidden(self):self.assertFalse(any(x[0]=='details' for x in p.tags['r59-bind']['parents']))
    def test_14_route_not_hidden(self):self.assertFalse(any(x[0]=='details' for x in p.tags['r54-select']['parents']))
    def test_15_os_metadata_collapsed(self):self.assertTrue(any(x[1]=='fm-os-details' for x in p.tags['probe']['parents']))
    def test_16_last_event_separated(self):self.assertIn('data-clean="lastEvent"',HTML)
    def test_17_no_old_sidebar_milestone(self):self.assertNotIn('FREQMED · R58 · MAC INTEL',HTML)
    def test_18_correct_version(self):self.assertIn('v0.8.1',HTML)
    def test_19_main_c_guardian(self):self.assertIn('id="guardian-state"',HTML)
    def test_20_no_interactive_emission(self):self.assertIn('class="disabled-start" type="button" disabled',HTML)
    def test_21_historical_v5_still_exists(self):self.assertTrue((ROOT/'historical/FREQMED_V5_DIRECT.html').is_file())
    def test_22_historical_only_in_advanced(self):self.assertEqual(HTML.count('href="/historical/v5"'),1)
    def test_23_mobile_rule(self):self.assertIn('@media(max-width:650px)',CSS)
    def test_24_rtl_rule(self):self.assertIn('html[dir=rtl]',CSS)
    def test_25_no_network_code_in_cleanup_js(self):
        for x in ('fetch(', 'XMLHttpRequest','AudioQueue','/api/physical-start','new WebSocket'):
            self.assertNotIn(x,JS)
    def test_26_i18n_all_ten(self):
        for x in ('"fr":','"en":','"de":','"ar":','"es":','"pt":','"hr":','"it":','"zh":','"ko":'):
            self.assertIn(x,JS)
    def test_27_os_route_core_unchanged(self):self.assertIn('fm_list_acoustic_outputs', (ROOT/'native/audio_devices_macos.c').read_text())
    def test_28_native_hard_denial(self):self.assertIn('return -1', (ROOT/'native/output_hard_denied.c').read_text())
    def test_29_full_original_r59_api(self):
        app=(ROOT/'app.py').read_text()
        for route in ('/api/acoustic/session/bind','/api/acoustic/session/invalidate','/api/software-stop','/api/route/monitor/resume'):
            self.assertIn(route,app)
    def test_30_build_has_no_emission_symbol(self):
        self.assertNotIn('str(NATIVE/"acoustic_macos.c")', (ROOT/'app.py').read_text().split('class NativeCore:',1)[1].split('class ',1)[0])
    def test_31_c_historical_r59_unchanged(self):
        expected='acoustic_session_r59.c'
        self.assertTrue((ROOT/'native'/expected).is_file())
    def test_32_stylesheet_served(self):self.assertIn('"/cleanup.css"', (ROOT/'app.py').read_text())
    def test_33_script_served(self):self.assertIn('"/cleanup.js"', (ROOT/'app.py').read_text())

class CleanupHTTP(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec=importlib.util.spec_from_file_location('fm_app_cleanup',ROOT/'app.py')
        cls.a=importlib.util.module_from_spec(spec);spec.loader.exec_module(cls.a)
        cls.tmp=tempfile.TemporaryDirectory()
        cls.core=cls.a.NativeCore(Path(cls.tmp.name))
        cls.server=cls.a.make_server(cls.core)
        cls.worker=threading.Thread(target=cls.server.serve_forever,daemon=True)
        cls.worker.start()
    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown();cls.server.server_close();cls.worker.join(3);cls.tmp.cleanup()
    def get(self,path):
        conn=http.client.HTTPConnection('127.0.0.1',self.server.server_port,timeout=5)
        conn.request('GET',path,headers={'Host':f'127.0.0.1:{self.server.server_port}'})
        r=conn.getresponse();data=r.read();status=r.status;headers=dict(r.getheaders());conn.close();return status,data,headers
    def test_34_html_http(self):self.assertIn(b'id="fm-advanced"',self.get('/')[1])
    def test_35_css_http(self):self.assertEqual(self.get('/cleanup.css')[0],200)
    def test_36_js_http(self):self.assertEqual(self.get('/cleanup.js')[0],200)
    def test_37_csp_self(self):self.assertIn("script-src 'self'",self.get('/')[2]['Content-Security-Policy'])
    def test_38_unknown_route_404(self):self.assertEqual(self.get('/audio/start')[0],404)
    def test_39_guardian_kept_locked(self):self.assertEqual(json.loads(self.get('/api/status')[1])['acoustic_output'],'NOT_LINKED_HARD_DENIED')
    def test_40_r59_status_kept(self):self.assertEqual(self.get('/api/acoustic/session/status')[0],200)

if __name__=='__main__':unittest.main()
