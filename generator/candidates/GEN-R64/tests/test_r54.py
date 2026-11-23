# SPDX-License-Identifier: Apache-2.0
"""R54 checks actual C FFI contract and fail-closed route handling.
No synthetic hardware, physical output, or OS measurement is produced.
"""
import http.client
import importlib.util
import json
from pathlib import Path
import tempfile
import threading
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("freqmed_r54", ROOT / "app.py")
app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app)


class R54Native(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.core = app.NativeCore(Path(cls.tmp.name))

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_01_real_native_device_enumeration_symbol(self):
        self.assertTrue(callable(self.core.lib.fm_list_acoustic_outputs))

    def test_02_snapshot_struct_binary_sizes(self):
        import ctypes
        self.assertEqual(ctypes.sizeof(app.FMNativeAudioDevice), 152)
        self.assertEqual(ctypes.sizeof(app.FMNativeAudioSnapshot), 8 + 32*152)

    def test_03_never_invents_devices_without_os(self):
        r = self.core.audio_devices()
        self.assertIn("observed", r)
        self.assertIn("devices", r)
        if not r["observed"]:
            self.assertEqual(r["devices"], [])
            self.assertEqual(r["reason"], "COREAUDIO_ENUMERATION_UNAVAILABLE")

    def test_04_current_route_initially_missing(self):
        self.assertEqual(self.core.get_route_status()["reason"], "NO_EXPLICIT_DEVICE_SELECTED")

    def test_05_missing_route_refused(self):
        with self.assertRaisesRegex(ValueError, "AUDIO_DEVICE_MISSING|COREAUDIO_ENUMERATION"):
            self.core.select_audio({"device_id":4294967295})

    def test_06_reject_bad_types(self):
        for v in (True, "1", 0, -1, 4294967296, 1.2, None):
            with self.assertRaises(ValueError):
                self.core.select_audio({"device_id":v})

    def test_07_reject_extra_fields(self):
        with self.assertRaises(ValueError):
            self.core.select_audio({"device_id":4, "enable_audio": True})

    def test_08_real_route_selection_if_OS_outputs_exist(self):
        result = self.core.audio_devices()
        if result["observed"] and result["devices"] and not result["truncated"]:
            dev = result["devices"][0]
            try:
                selected = self.core.select_audio({"device_id":dev["device_id"]})
                # Device hot unplug can invalidate it immediately, which is safe.
                self.assertTrue(selected["selected"])
                self.assertEqual(selected["physical_output"], "HARD_DENIED")
            except ValueError as e:
                self.assertEqual(str(e), "AUDIO_DEVICE_MISSING_OR_NOT_OUTPUT_CAPABLE")
        self.assertEqual(self.core.clear_audio()["selected"], False)

    def test_09_reset_clears_route(self):
        self.assertEqual(self.core.stop()["guardian_state"], "OFF")
        self.assertFalse(self.core.get_route_status()["selected"])

    def test_10_no_acoustic_output_backend(self):
        self.assertEqual(self.core.lib.fm_acoustic_native_backend_available(), 0)
        self.assertNotEqual(self.core.lib.fm_acoustic_physical_output(None), 0)

    def test_11_no_em_output_backend(self):
        self.assertEqual(self.core.lib.fm_em_backend_available(), 0)
        self.assertNotEqual(self.core.lib.fm_em_physical_output(None), 0)

    def test_12_status_includes_native_route_state(self):
        r=self.core.status()
        self.assertEqual(r["schema"], "freqmed.gen-r54.local-ui.v1")
        self.assertIn("selected_acoustic_route",r)
        self.assertEqual(r["acoustic_output"], "NOT_LINKED_HARD_DENIED")

    def test_13_native_c_validation_still_locked(self):
        r=self.core.validate({"channel":"acoustic", "hz":440.0, "duration_ms":500, "level":.01})
        self.assertTrue(r["native_c_executed"])
        self.assertTrue(r["structurally_valid"])
        self.assertFalse(r["guardian_authorized"])

    def test_14_no_output_module_shipped(self):
        import re
        names={x.name for x in (ROOT / "native").iterdir()}
        self.assertNotIn("acoustic_macos.c",names)
        self.assertNotIn("em_instrument_driver.c",names)
        source=(ROOT/'native'/'audio_devices_macos.c').read_text()
        self.assertNotIn('AudioQueueNewOutput',source)
        self.assertNotIn('AudioQueueStart',source)
        self.assertNotIn('AudioUnitRender',source)
        self.assertIn('kAudioHardwarePropertyDevices',source)

    def test_15_legacy_v5_unchanged(self):
        import hashlib
        digest=hashlib.sha256((ROOT/'historical'/'FREQMED_V5_DIRECT.html').read_bytes()).hexdigest()
        self.assertEqual(digest,'e034913d551cbfaf6ee51c8ce971707dd811ebfebb8d8bc9307d71f9c7029ef8')

    def test_16_manifest(self):
        self.assertGreaterEqual(app.verify_manifest(),16)

    def test_30_native_C_ctypes_field_names_and_layout(self):
        """Real native C declaration and Python FFI must agree, not merely have equal sizeof()."""
        import ctypes
        import re
        native = (ROOT / "native" / "audio_devices.h").read_text(encoding="utf-8")
        marker = "} FMNativeAudioDevice;"
        self.assertEqual(native.count(marker), 1)
        declaration = native[:native.index(marker)].split("typedef struct {", 1)[1]
        c_fields = re.findall(r"^\s*(?:uint32_t|double|int32_t|char)\s+([A-Za-z_][A-Za-z_0-9]*)(?:\[FM_AUDIO_LABEL_MAX\])?\s*;", declaration, re.M)
        python_fields = [name for name, _ in app.FMNativeAudioDevice._fields_]
        self.assertEqual(c_fields, ["device_id", "output_channels", "nominal_rate_hz", "is_default", "name"])
        self.assertEqual(python_fields, c_fields)
        self.assertEqual(app.FMNativeAudioDevice.output_channels.offset, 4)
        self.assertEqual(app.FMNativeAudioDevice.nominal_rate_hz.offset, 8)
        self.assertEqual(ctypes.sizeof(app.FMNativeAudioDevice), 152)

    def test_31_native_snapshot_has_no_invalid_ctypes_access(self):
        """Statically reject Python dev.foo accesses not declared in the native ABI.

        No fabricated devices, physical simulation, or OS measurements are used.
        """
        import ast
        import inspect
        import textwrap
        tree = ast.parse(textwrap.dedent(inspect.getsource(app.NativeCore._snapshot)))
        used = {node.attr for node in ast.walk(tree)
                if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name)
                and node.value.id == "dev"}
        defined = {name for name, _ in app.FMNativeAudioDevice._fields_}
        self.assertTrue(used <= defined, f"Undeclared FFI fields: {used - defined}")
        self.assertIn("output_channels", used)


class R54HTTP(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory()
        cls.core=app.NativeCore(Path(cls.tmp.name))
        cls.server=app.make_server(cls.core)
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True)
        cls.thread.start()
        cls.port=cls.server.server_port

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(2)
        cls.tmp.cleanup()

    def req(self,method,path,body=None,headers=None):
        conn=http.client.HTTPConnection('127.0.0.1',self.port,timeout=5)
        head=dict(headers or {});head['Host']=f'127.0.0.1:{self.port}'
        if body is not None:
            head.setdefault('Content-Type','application/json');body=json.dumps(body)
        conn.request(method,path,body=body,headers=head)
        resp=conn.getresponse();result=resp.read();code=resp.status;headers=dict(resp.getheaders());conn.close()
        return code,json.loads(result) if path.startswith('/api/') else result,headers

    def auth(self):
        return {'Origin':f'http://127.0.0.1:{self.port}', 'X-FREQMED-SESSION':self.server.token}

    def test_17_device_api_returns_real_only(self):
        code,r,_=self.req('GET','/api/audio/devices')
        self.assertEqual(code,200)
        self.assertIn('selection',r)
        self.assertIn('devices',r)

    def test_18_native_route_not_selectable_without_token(self):
        code,r,_=self.req('POST','/api/audio/select',{'device_id':4})
        self.assertEqual(code,403)

    def test_19_native_route_not_selectable_from_foreign_origin(self):
        headers=self.auth();headers['Origin']='https://evil.example'
        code,r,_=self.req('POST','/api/audio/select',{'device_id':4},headers)
        self.assertEqual(code,403)

    def test_20_invalid_id_authenticated_refused(self):
        code,r,_=self.req('POST','/api/audio/select',{'device_id':True},self.auth())
        self.assertEqual(code,422)
        self.assertEqual(r['error'],'INVALID_EPHEMERAL_AUDIO_DEVICE_ID')

    def test_21_no_audio_route_can_be_invented(self):
        code,r,_=self.req('POST','/api/audio/select',{'device_id':4294967295},self.auth())
        self.assertEqual(code,422)
        self.assertTrue('MISSING' in r['error'] or 'UNAVAILABLE' in r['error'])

    def test_22_clear_audio_endpoint(self):
        code,r,_=self.req('POST','/api/audio/clear',{},self.auth())
        self.assertEqual(code,200)
        self.assertEqual(r['selected'],False)

    def test_23_clear_audio_rejects_payload(self):
        code,_,_=self.req('POST','/api/audio/clear',{'arbitrary':1},self.auth())
        self.assertEqual(code,422)

    def test_24_no_output_endpoint_even_authenticated(self):
        code,r,_=self.req('POST','/api/physical-start',{},self.auth())
        self.assertEqual(code,404)
        self.assertEqual(r['error'],'NO_SUCH_ROUTE')

    def test_25_browser_gets_r54_script(self):
        code,data,h=self.req('GET','/r54.js')
        self.assertEqual(code,200)
        self.assertIn(b'/api/audio/devices',data)
        self.assertIn('Content-Security-Policy',h)

    def test_26_browser_gets_r54_css(self):
        code,data,_=self.req('GET','/r54.css')
        self.assertEqual(code,200)
        self.assertIn(b'.r54-device-route',data)

    def test_27_real_ui_form_has_device_selection(self):
        code,data,_=self.req('GET','/')
        self.assertEqual(code,200)
        self.assertIn(b'id="r54-select"',data)
        self.assertIn(b'disabled-start',data)

    def test_28_existing_http_native_c_still_works(self):
        code,data,_=self.req('POST','/api/validate',{'channel':'acoustic','hz':440,'level':.01,'duration_ms':500},self.auth())
        self.assertEqual(code,200)
        self.assertTrue(data['native_c_executed'])
        self.assertFalse(data['guardian_authorized'])

    def test_29_no_server_dev_internet(self):
        code,_,_=self.req('GET','/api/evil')
        self.assertEqual(code,404)


if __name__=='__main__':
    unittest.main()
