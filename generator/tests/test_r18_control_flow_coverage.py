"""GEN-R18 static control-flow envelope and evidence-chain regression tests.

Only real pinned C source is analyzed. Tests alter in-memory text, never execute
modified C, synthesize a physical measurement, run hardware or simulate physics.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "audits"))
import r16_ownership_static_audit as previous
import r17_evidence_verifier as independent
import r18_control_flow_envelope as flow

SRC = (ROOT / "src/acoustic_macos.c").read_text(encoding="utf-8")
RUN = (ROOT / "RUN_GEN_R18_MAC_INTEL.command").read_text(encoding="utf-8")

class R18ControlFlowOwnership(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix="freqmed_r18_evidence_")
        cls.a = Path(cls.tmp.name) / "R16.json"
        cls.b = Path(cls.tmp.name) / "R17.json"
        r16 = previous.audit(ROOT)
        r17 = independent.verify(ROOT, r16)
        cls.a.write_text(json.dumps(r16), encoding="utf-8")
        cls.b.write_text(json.dumps(r17), encoding="utf-8")
        cls.report = flow.audit(ROOT, cls.a, cls.b)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def reject_source(self, source, replacement):
        self.assertEqual(1, SRC.count(source), "test source anchor drift")
        bad = SRC.replace(source, replacement, 1)
        with self.assertRaises(flow.EnvelopeError):
            flow.examine_source(bad)

    def test_source_hash_matches_real_mac_target(self):
        self.assertEqual(hashlib.sha256(SRC.encode("utf-8")).hexdigest(),
                         self.report["source_sha256"])

    def test_static_envelope_schema_and_method(self):
        self.assertEqual(flow.SCHEMA, self.report["schema"])
        self.assertEqual(flow.METHOD, self.report["method"])
        self.assertEqual("STATIC_CONTROL_FLOW_ENVELOPE_PASS",
                         self.report["verdict"])

    def test_exact_thirteen_exit_sites_classified(self):
        self.assertEqual(13, len(self.report["exit_sites"]))
        ids = [x["id"] for x in self.report["exit_sites"]]
        self.assertEqual([x[0] for x in flow.EXPECTED], ids)

    def test_exit_resource_phases_are_closed(self):
        self.assertEqual({
            "BEFORE_SESSION_CLAIM": 5,
            "CLAIMED_NO_ALLOCATION": 2,
            "ALLOCATED_BEFORE_OS_PUBLICATION": 3,
            "OS_CALLBACK_USERDATA_POSSIBLY_PUBLISHED": 2,
            "AFTER_FINAL_CLEANUP": 1,
        }, self.report["exit_phases"])

    def test_final_return_guard_is_top_level(self):
        final = self.report["exit_sites"][-1]
        self.assertEqual("final_controller_result", final["id"])
        self.assertIsNone(final["direct_guard_line"])
        self.assertEqual("AFTER_FINAL_CLEANUP", final["stage"])

    def test_every_early_return_is_under_specific_guard(self):
        for site in self.report["exit_sites"][:-1]:
            self.assertIsInstance(site["direct_guard_line"], int)
            self.assertGreater(site["direct_guard_line"], 0)

    def test_exact_four_heap_free_sites(self):
        sites = self.report["heap_free_sites"]
        self.assertEqual(4, len(sites))
        self.assertEqual(["UNPUBLISHED", "UNPUBLISHED",
                          "POST_DISPOSAL_GUARDED", "POST_DISPOSAL_GUARDED"],
                         [s["phase"] for s in sites])

    def test_exact_six_session_claim_release_sites(self):
        sites = self.report["session_release_sites"]
        self.assertEqual(6, len(sites))
        self.assertTrue(all(item["guard_line"] > 0 for item in sites))

    def test_exact_os_api_surface(self):
        counts = {k: v["count"] for k, v in self.report["os_api_sites"].items()}
        self.assertEqual(flow.OS_CALL_COUNTS, counts)

    def test_quarantine_accesses_require_atomic_order(self):
        self.assertEqual(2, self.report["quarantine_loads_acquire"])
        self.assertEqual(4, self.report["quarantine_stores_release_one"])

    def test_evidence_chain_binds_three_reports(self):
        self.assertEqual("PASS", self.report["r16_r17_evidence_binding"])
        self.assertEqual(hashlib.sha256(self.a.read_bytes()).hexdigest(),
                         self.report["r16_evidence_sha256"])
        self.assertEqual(hashlib.sha256(self.b.read_bytes()).hexdigest(),
                         self.report["r17_evidence_sha256"])
        self.assertEqual(hashlib.sha256(
            (ROOT / "KIT_SHA256SUMS.txt").read_bytes()).hexdigest(),
            self.report["manifest_sha256"])

    def test_current_r18_runner_never_links_output_backend(self):
        self.assertEqual(independent.LINK_C_ALLOWLIST,
                         frozenset(independent.link_sources(RUN)))
        self.assertIn("R18_NONEMITTING_EXECUTABLE_SYMBOL_AUDIT=PASS", RUN)
        self.assertIn("FREQMED_GEN_R18_BINARY", RUN)
        self.assertIn("FREQMED_GEN_R17_BINARY", RUN)

    def test_uncertainties_and_never_simulation_stay_explicit(self):
        self.assertIn("C11_CONCURRENT_MEMORY_SAFETY_NOT_PROVEN",
                      self.report["unresolved"])
        self.assertIn("OS_CALLBACK_QUIESCENCE_NOT_ESTABLISHED",
                      self.report["unresolved"])
        self.assertEqual("NONE", self.report["scientific_simulation"])
        self.assertEqual("NONE", self.report["physical_emission"])
        self.assertEqual("NOT_AUTHORIZED", self.report["real_output"])
        self.assertEqual("NOT_AUTHORIZED", self.report["production"])

    def test_real_mac_cli_has_no_emission_actions(self):
        executable = os.environ.get("FREQMED_GEN_R18_BINARY")
        if not executable:
            self.skipTest("Mac Intel native no-output executable required")
        result = subprocess.run([executable, "status"], capture_output=True,
                                text=True, timeout=5, check=True)
        status = json.loads(result.stdout)
        self.assertEqual("NONE", status["physical_emission"])
        self.assertEqual("NOT_LINKED_HARD_DENIED", status["acoustic_output"])
        self.assertEqual("BLOCKED_NO_QUALIFIED_EM_DEVICE",
                         status["electromagnetic_output"])
        for action in ("arm", "emit", "play", "transmit"):
            denied = subprocess.run([executable, action], capture_output=True,
                                    text=True, timeout=5)
            self.assertNotEqual(0, denied.returncode)

    def test_reject_early_success_return(self):
        self.reject_source(
            "if (!request || request->channel!=FM_ACOUSTIC) return -1;",
            "if (!request || request->channel!=FM_ACOUSTIC) return 0;")

    def test_reject_extra_hidden_early_return(self):
        self.reject_source(
            "AcousticContext *ctx=owner_ctx;",
            "AcousticContext *ctx=owner_ctx;\n  if (ctx) return -1;")

    def test_reject_unclassified_heap_free(self):
        self.reject_source(
            "AcousticContext *ctx=owner_ctx;",
            "AcousticContext *ctx=owner_ctx;\n  free(owner_ctx);")

    def test_reject_relaxed_claim_release(self):
        self.reject_source(
            "if (atomic_load_explicit(&fm_context_quarantined,memory_order_acquire)) {\n"
            "    atomic_flag_clear_explicit(&fm_session_claim,memory_order_release);",
            "if (atomic_load_explicit(&fm_context_quarantined,memory_order_acquire)) {\n"
            "    atomic_flag_clear_explicit(&fm_session_claim,memory_order_relaxed);")

    def test_reject_quarantine_reopening(self):
        self.reject_source(
            "atomic_store(&ctx->stop_requested,1);\n"
            "    atomic_store_explicit(&fm_context_quarantined,1,memory_order_release);",
            "atomic_store(&ctx->stop_requested,1);\n"
            "    atomic_store_explicit(&fm_context_quarantined,0,memory_order_release);")

    def test_reject_extra_os_start_call(self):
        self.reject_source(
            "if (!err && AudioQueueStart(ctx->queue,NULL)!=noErr) err=1;",
            "if (!err && AudioQueueStart(ctx->queue,NULL)!=noErr) err=1;\n"
            "  if (!err && AudioQueueStart(ctx->queue,NULL)!=noErr) err=1;")
