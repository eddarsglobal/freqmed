# SPDX-License-Identifier: Apache-2.0
import http.client
import importlib.util
import json
from pathlib import Path
import tempfile
import threading
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("freqmed_app", ROOT / "app.py")
app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app)


class NativeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.core = app.NativeCore(Path(cls.temp.name))

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_01_repo_sources_are_git_blob_exact(self):
        import subprocess
        for name, blob in {
            "generator.h": "9839f4390d9f17560cf6ef2447501a314f335773",
            "generator_core.c": "80f35f7ec323a658699929a717d6d16ef74a3144",
            "acoustic_probe_macos.c": "d70f9457c2b6c2f3668681247fa895f3a2720b5e"
        }.items():
            result = subprocess.check_output(["git", "hash-object", str(ROOT/"native"/name)], text=True)
            self.assertEqual(result.strip(), blob)

    def test_02_real_c_core_accepts_structure_but_guardian_denies(self):
        res = self.core.validate({"channel": "acoustic", "hz": 440.0, "level": .01, "duration_ms": 500})
        self.assertTrue(res["structurally_valid"])
        self.assertFalse(res["guardian_authorized"])
        self.assertTrue(res["native_c_executed"])
        self.assertEqual(res["guardian_state"], "BLOCKED")

    def test_03_electromagnetic_uses_native_guardian(self):
        res = self.core.validate({"channel": "em", "hz": 1000.0, "level": .3, "duration_ms": 250})
        self.assertTrue(res["structurally_valid"])
        self.assertEqual(res["guardian_reason"], "R1_OUTPUT_HARD_LOCK_CERTIFICATION_REQUIRED")
        self.assertEqual(res["physical_output"], "BLOCKED")

    def test_04_invalid_C_frequency(self):
        res = self.core.validate({"channel": "acoustic", "hz": -1.0, "level": .3, "duration_ms": 250})
        self.assertFalse(res["structurally_valid"])
        self.assertEqual(res["structural_reason"], "INVALID_HZ")

    def test_05_reject_nan_inf(self):
        for hz in (float("nan"), float("inf"), -float("inf")):
            with self.assertRaises(ValueError):
                self.core.validate({"channel": "acoustic", "hz": hz, "level": .1, "duration_ms": 100})

    def test_06_no_boolean_numbers_and_unknown_keys(self):
        with self.assertRaises(ValueError):
            self.core.validate({"channel": "acoustic", "hz": True, "level": .1, "duration_ms": 100})
        with self.assertRaises(ValueError):
            self.core.validate({"channel": "acoustic", "hz": 1.0, "level": .1, "duration_ms": 100, "activate": True})

    def test_07_no_outputs_native(self):
        self.assertEqual(self.core.lib.fm_acoustic_native_backend_available(), 0)
        self.assertEqual(self.core.lib.fm_em_backend_available(), 0)
        self.assertNotEqual(self.core.lib.fm_acoustic_physical_output(None), 0)
        self.assertNotEqual(self.core.lib.fm_em_physical_output(None), 0)

    def test_08_stop_is_native_only(self):
        self.core.validate({"channel": "em", "hz": 150.0, "level": .01, "duration_ms": 100})
        self.assertEqual(self.core.stop()["guardian_state"], "OFF")
        self.assertIsNone(self.core.status()["last_command"])

    def test_09_probe_fails_closed_when_unavailable(self):
        probe = self.core.acoustic_probe()
        self.assertIn("observed", probe)
        self.assertFalse(probe["hardware_qualified"])
        if not probe["observed"]:
            self.assertIn("reason", probe)

    def test_10_no_em_qualifier_in_usb_inventory(self):
        result = app.usb_inventory()
        self.assertIn("observed", result)
        if result["observed"]:
            self.assertEqual(result["qualified_em_generators"], 0)

    def test_11_manifest_integrity(self):
        self.assertGreaterEqual(app.verify_manifest(), 10)

    def test_12_historical_V5_bitwise_preserved(self):
        import hashlib
        sha = hashlib.sha256((ROOT/"historical"/"FREQMED_V5_DIRECT.html").read_bytes()).hexdigest()
        self.assertEqual(sha, "e034913d551cbfaf6ee51c8ce971707dd811ebfebb8d8bc9307d71f9c7029ef8")


class HTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.core = app.NativeCore(Path(cls.temp.name))
        cls.server = app.make_server(cls.core)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.port = cls.server.server_port

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(2)
        cls.temp.cleanup()

    def request(self, method, path, body=None, headers=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        headers = headers or {}
        headers.setdefault("Host", f"127.0.0.1:{self.port}")
        if body is not None:
            headers.setdefault("Content-Type", "application/json")
            body = json.dumps(body)
        conn.request(method, path, body=body, headers=headers)
        r = conn.getresponse()
        data = r.read()
        headers_result = dict(r.getheaders())
        status = r.status
        conn.close()
        return status, json.loads(data) if path.startswith("/api/") else data, headers_result

    def authenticated_headers(self):
        return {"X-FREQMED-SESSION": self.server.token,
                "Origin": f"http://127.0.0.1:{self.port}"}

    def test_13_browser_home_uses_real_generator_form(self):
        s, data, hdr = self.request("GET", "/")
        self.assertEqual(s, 200)
        self.assertIn(b'control-form', data)
        self.assertIn(b'disabled-start', data)
        self.assertIn("Content-Security-Policy", hdr)

    def test_14_session_and_status(self):
        s, data, _ = self.request("GET", "/api/session")
        self.assertEqual(s, 200)
        self.assertEqual(data["session"], self.server.token)
        s, data, _ = self.request("GET", "/api/status")
        self.assertEqual(s, 200)
        self.assertEqual(data["acoustic_output"], "NOT_LINKED_HARD_DENIED")

    def test_15_auth_absent_does_not_validate(self):
        s, data, _ = self.request("POST", "/api/validate", {"channel":"acoustic", "hz":440, "level":.1, "duration_ms":500})
        self.assertEqual(s, 403)
        self.assertEqual(data["error"], "ORIGIN_REFUSED")

    def test_16_cross_origin_refused(self):
        h = self.authenticated_headers(); h["Origin"] = "http://evil.test"
        s, data, _ = self.request("POST", "/api/validate", {"channel":"acoustic", "hz":440, "level":.1, "duration_ms":500},h)
        self.assertEqual(s, 403)

    def test_17_invalid_token_refused(self):
        h = self.authenticated_headers(); h["X-FREQMED-SESSION"] = "invalid"
        s, _, _ = self.request("POST", "/api/reset", {}, h)
        self.assertEqual(s, 403)

    def test_18_actual_C_submission_via_http(self):
        s, data, _ = self.request("POST", "/api/validate", {"channel":"acoustic", "hz":440, "level":.1, "duration_ms":500},self.authenticated_headers())
        self.assertEqual(s, 200)
        self.assertTrue(data["native_c_executed"])
        self.assertTrue(data["structurally_valid"])
        self.assertFalse(data["guardian_authorized"])

    def test_19_no_output_route(self):
        s, data, _ = self.request("POST", "/api/physical-start", {}, self.authenticated_headers())
        self.assertEqual(s, 404)
        self.assertEqual(data["error"], "NO_SUCH_ROUTE")

    def test_20_native_stop_via_http(self):
        s, data, _ = self.request("POST", "/api/reset", {}, self.authenticated_headers())
        self.assertEqual(s, 200)
        self.assertEqual(data["guardian_state"], "OFF")

    def test_21_bad_host_refused(self):
        s, data, _ = self.request("GET", "/api/status", headers={"Host": "evil.test"})
        self.assertEqual(s, 403)

    def test_22_historical_original_served(self):
        s, data, hdr = self.request("GET", "/historical/v5")
        self.assertEqual(s, 200)
        self.assertEqual(len(data), 187550)
        self.assertIn(b'Real Observation Workspace V5', data)
        self.assertNotIn("Content-Security-Policy", hdr)  # historical HTML carries its own CSP hashes

    def test_23_disallow_path_traversal(self):
        s, data, _ = self.request("GET", "/../app.py")
        self.assertEqual(s, 404)

    def test_24_audio_probe_http_is_readonly(self):
        s, data, _ = self.request("GET", "/api/audio")
        self.assertEqual(s, 200)
        self.assertEqual(data["hardware_qualified"], False)

    def test_25_form_server_does_not_contain_actual_emission_source(self):
        names = [p.name for p in (ROOT/"native").iterdir()]
        self.assertNotIn("acoustic_macos.c", names)
        self.assertNotIn("em_instrument_driver.c", names)
        self.assertIn("output_hard_denied.c", names)


if __name__ == "__main__":
    unittest.main()
