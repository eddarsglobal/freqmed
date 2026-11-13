"""GEN-R17 independent evidence verification and source regression sensitivity.

All modifications are in-memory JSON or copies of actual source in an isolated
temporary directory. No scientific simulation, physical generation, hardware
access, or invented experimental reading. Python stdlib only.
"""
import copy
import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "audits"))
import r16_ownership_static_audit as upstream
import r17_evidence_verifier as independent

class R17EvidenceIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r16 = upstream.audit(ROOT)
        cls.verified = independent.verify(ROOT, cls.r16)

    def reject(self, update):
        altered = copy.deepcopy(self.r16)
        update(altered)
        with self.assertRaises(independent.EvidenceError):
            independent.verify(ROOT, altered)

    def static_reject(self, needle, substitute):
        """Check a single isolated textual C-source regression; no C execution."""
        with tempfile.TemporaryDirectory(prefix="freqmed_r17_static_") as temp:
            base = Path(temp)
            (base / "src").mkdir()
            source = (ROOT / "src/acoustic_macos.c").read_text(encoding="utf-8")
            self.assertEqual(1, source.count(needle))
            (base / "src/acoustic_macos.c").write_text(
                source.replace(needle, substitute, 1), encoding="utf-8")
            shutil.copyfile(ROOT / "src/em_backend.c",
                            base / "src/em_backend.c")
            shutil.copyfile(ROOT / "RUN_GEN_R16_MAC_INTEL.command",
                            base / "RUN_GEN_R16_MAC_INTEL.command")
            try:
                report = upstream.audit(base)
                self.assertNotEqual("STATIC_SOURCE_CONTRACT_PASS",
                                    report["verdict"])
            except (ValueError, IndexError) as exc:
                self.assertTrue(str(exc))

    def test_baseline_is_real_sha_bound_evidence(self):
        self.assertEqual("PASS", self.verified["verification"])
        self.assertEqual(independent.OUTPUT_SCHEMA, self.verified["schema"])
        self.assertEqual(25, self.verified["static_checks_verified"])

    def test_all_pinned_files_are_verified(self):
        self.assertGreaterEqual(self.verified["manifest_files_verified"], 87)
        manifest = ROOT / "KIT_SHA256SUMS.txt"
        self.assertEqual(hashlib.sha256(manifest.read_bytes()).hexdigest(),
                         self.verified["manifest_sha256"])

    def test_independent_link_allowlist(self):
        runner = (ROOT / "RUN_GEN_R17_MAC_INTEL.command").read_text(encoding="utf-8")
        self.assertEqual(independent.LINK_C_ALLOWLIST,
                         frozenset(independent.link_sources(runner)))

    def test_public_acoustic_and_em_denied(self):
        source = (ROOT / "src/acoustic_macos.c").read_text(encoding="utf-8")
        em = (ROOT / "src/em_backend.c").read_text(encoding="utf-8")
        self.assertTrue(independent.public_denial(
            source, "fm_acoustic_physical_output"))
        self.assertTrue(independent.public_denial(
            em, "fm_em_physical_output"))

    def test_reject_changed_source_digest(self):
        self.reject(lambda e: e.__setitem__("source_sha256", "0" * 64))

    def test_reject_modified_success_count(self):
        self.reject(lambda e: e.__setitem__("passed", 24))

    def test_reject_missing_static_check(self):
        self.reject(lambda e: e["checks"].pop())

    def test_reject_duplicate_check_identifier(self):
        self.reject(lambda e: e["checks"][0].__setitem__(
            "id", e["checks"][1]["id"]))

    def test_reject_false_pass_from_a_failed_check(self):
        self.reject(lambda e: e["checks"][0].__setitem__("result", "FAIL"))

    def test_reject_forged_source_line(self):
        self.reject(lambda e: e["checks"][0].__setitem__("source_line", -1))

    def test_reject_missing_risk_caveat(self):
        self.reject(lambda e: e["unresolved"].pop())

    def test_reject_fake_physical_emission_claim(self):
        self.reject(lambda e: e.__setitem__("physical_emission", "MEASURED"))

    def test_reject_unrecognized_auditor_method(self):
        self.reject(lambda e: e.__setitem__("method", "UNREVIEWED_METHOD"))

    def test_reject_extra_untrusted_evidence_field(self):
        self.reject(lambda e: e.__setitem__("signature", "FAKE"))

    def test_reject_negative_owner_verdict(self):
        self.reject(lambda e: e.__setitem__("verdict", "REMEDIATE"))

    def test_r16_detects_removed_early_heap_release(self):
        self.static_reject("free(owner_ctx);",
                           "(void)owner_ctx;")

    def test_r16_detects_unsound_failed_disposal_pointer_clear(self):
        self.static_reject(
            "fm_latch_first_fault(ctx,FM_FAULT_DISPOSAL);\n      err=1;",
            "fm_latch_first_fault(ctx,FM_FAULT_DISPOSAL);\n"
            "      ctx->queue=NULL;\n      err=1;")

    def test_r16_detects_missing_callback_exit_counter(self):
        self.static_reject(
            "atomic_fetch_sub_explicit(&ctx->active_output_callbacks,1U,",
            "atomic_fetch_add_explicit(&ctx->active_output_callbacks,1U,")

    def test_r16_detects_disposal_confirmation_revocation(self):
        self.static_reject(
            "atomic_store(&ctx->dispose_confirmed,1);",
            "atomic_store(&ctx->dispose_confirmed,0);")

    def test_r16_detects_disabled_quarantine_on_queue_creation(self):
        self.static_reject(
            "atomic_store(&ctx->stop_requested,1);\n"
            "    atomic_store_explicit(&fm_context_quarantined,1,"
            "memory_order_release);",
            "atomic_store(&ctx->stop_requested,1);\n"
            "    atomic_store_explicit(&fm_context_quarantined,0,"
            "memory_order_release);")
