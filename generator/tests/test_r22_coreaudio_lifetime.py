"""GEN-R22 bounded C11/CoreAudio review regressions; no physical simulations.

Mutated source *text* is a software adversarial test, never an OS callback
schedule, synthetic measurement, or running audio/EM device.
"""
import hashlib
import os
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "audits"))
import r17_evidence_verifier as r17
import r19_adversarial_source_audit as r19
import r20_bureau_archive_review as r20
import r22_coreaudio_lifetime_review as r22

class R22CoreAudioSourceReview(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src = (ROOT / "src/acoustic_macos.c").read_text(encoding="utf-8")
        cls.runner = (ROOT / "RUN_GEN_R22_MAC_INTEL.command").read_text(encoding="utf-8")

    def mutate(self, needle, replacement):
        self.assertIn(needle, self.src)
        altered = self.src.replace(needle, replacement, 1)
        self.assertNotEqual(self.src, altered)
        with self.assertRaises(r22.R22Error):
            r22.checks(altered, self.runner)

    def test_17_bounded_contracts_present(self):
        checks = r22.checks(self.src, self.runner)
        self.assertEqual(17, len(checks))
        self.assertEqual(17, len(set(x[0] for x in checks)))

    def test_all_three_review_risks_remain_open(self):
        self.assertEqual(3, len(r22.OPEN_FINDINGS))
        self.assertTrue(all(len(reason) >= 60 for _, reason in r22.OPEN_FINDINGS))

    def test_first_three_bureau_ids_exact(self):
        self.assertEqual(("C11_CALLBACK_RACE_FREEDOM",
                          "ACTIVE_COREAUDIO_LIFETIME",
                          "FAILED_OS_DISPOSAL_BEHAVIOR"), r22.GATE_IDS)

    def test_118_source_hash_manifest_and_runner_pinned(self):
        table, sha, observations = r22.assess(ROOT)
        self.assertEqual(118, len(table))
        self.assertEqual(17, len(observations))
        self.assertEqual(sha, hashlib.sha256(
            (ROOT / "KIT_SHA256SUMS.txt").read_bytes()).hexdigest())

    def test_actual_C_backend_hash_unchanged_since_R19(self):
        sha = hashlib.sha256(self.src.encode("utf-8")).hexdigest()
        self.assertEqual(r19.PINNED_ACOUSTIC_SHA256, sha)

    def test_non_atomic_pcm_fields_are_not_misrepresented(self):
        self.assertIn("ctx->phase+=", self.src)
        self.assertIn("++ctx->frames_written", self.src)
        self.assertTrue(any(k == "C11_PCM_SINGLE_WRITER_NOT_PROVEN"
                            for k, _ in r22.OPEN_FINDINGS))

    def test_no_C11_or_OS_certification_claim_in_review(self):
        self.assertEqual("REVIEW_REQUIRED_NO_EMISSION", r22.VERDICT)
        text = r22.markdown({
            "source_contracts": [
                {"id": k, "result": "STATIC_SOURCE_OBSERVED",
                 "source": {"path": "src/acoustic_macos.c", "line": 1}}
                for k, _ in r22.checks(self.src, self.runner)],
            "open_findings": [
                {"id": k, "explanation": value}
                for k, value in r22.OPEN_FINDINGS],
        })
        self.assertIn("11 portes Bureau restent ouvertes", text)
        self.assertIn("PAS", text.upper())
        self.assertIn("NOT_AUTHORIZED", text)

    def test_public_executable_link_allowlist_is_preserved(self):
        self.assertEqual(r17.LINK_C_ALLOWLIST,
                         frozenset(r17.link_sources(self.runner)))
        self.assertNotIn('"$ROOT/src/acoustic_macos.c" "$ROOT/src/generator_core.c"',
                         self.runner)

    def test_mutated_output_callback_entry_counter_rejected(self):
        self.mutate("atomic_fetch_add_explicit(&ctx->active_output_callbacks",
                    "atomic_fetch_add_explicit(&ctx->absent_output_counter")

    def test_mutated_output_callback_exit_counter_rejected(self):
        self.mutate("atomic_fetch_sub_explicit(&ctx->active_output_callbacks",
                    "atomic_fetch_sub_explicit(&ctx->absent_output_counter")

    def test_mutated_property_listener_entry_rejected(self):
        self.mutate("atomic_fetch_add_explicit(&ctx->active_property_listeners",
                    "atomic_fetch_add_explicit(&ctx->absent_listener_counter")

    def test_mutated_property_listener_exit_rejected(self):
        self.mutate("atomic_fetch_sub_explicit(&ctx->active_property_listeners",
                    "atomic_fetch_sub_explicit(&ctx->absent_listener_counter")

    def test_mutated_PCM_writer_lock_rejected(self):
        self.mutate("atomic_flag_test_and_set_explicit(&ctx->pcm_writer_gate",
                    "atomic_flag_test_and_set_explicit(&ctx->some_other_gate")

    def test_mutated_overlapping_callback_fault_rejected(self):
        self.mutate("fm_latch_first_fault(ctx,FM_FAULT_OVERLAPPING_PCM_CALLBACK)",
                    "fm_latch_first_fault(ctx,FM_FAULT_BAD_BUFFER)")

    def test_mutated_shutdown_barrier_rejected(self):
        self.mutate("atomic_exchange(&ctx->shutdown_in_progress,1)",
                    "atomic_exchange(&ctx->shutdown_in_progress,0)")

    def test_mutated_bind_failure_disposal_tracking_rejected(self):
        self.mutate("if (bind_dispose_status==noErr)",
                    "if (bind_dispose_status!=noErr)")

    def test_mutated_listener_removal_fault_rejected(self):
        self.mutate("listener_remove_failed=1;", "listener_remove_failed=0;")

    def test_mutated_failed_disposal_status_rejected(self):
        self.mutate("if (AudioQueueDispose(ctx->queue,true)!=noErr)",
                    "if (AudioQueueDispose(ctx->queue,true)==noErr)")

    def test_mutated_public_acoustic_output_rejected(self):
        self.mutate("(void)command;\n  return -1;",
                    "(void)command;\n  return 0;")

    def test_actual_owner_R21_evidence_and_all_three_gates_still_open(self):
        work = os.environ.get("FREQMED_GEN_R22_EVIDENCE_DIR")
        archive = os.environ.get("FREQMED_GEN_R19_ARCHIVE_DIR")
        if not work or not archive:
            self.skipTest("actual owner Mac R16-R21 five reports required")
        work = Path(work)
        paths = {
            "r16": work / "GEN_R16_OWNERSHIP_EVIDENCE.json",
            "r17": work / "GEN_R17_VERIFIED_EVIDENCE.json",
            "r18": work / "GEN_R18_CONTROL_FLOW_EVIDENCE.json",
            "r19": work / "GEN_R19_ADVERSARIAL_EVIDENCE.json",
            "r20": work / "GEN_R20_BUREAU_VERIFICATION.json",
        }
        report = r22.audit(ROOT, Path(archive), paths, work / "GEN_R21_BUREAU_GAPS.json")
        self.assertEqual(11, report["bureau_gates_open"])
        self.assertEqual(0, report["bureau_gates_resolved"])
        self.assertEqual("NOT_PROVEN", report["c11_race_freedom"])
        self.assertEqual("NOT_PROVEN", report["active_coreaudio_callback_lifetime"])
        self.assertEqual("NOT_TESTED", report["actual_failed_os_disposal"])
        self.assertEqual("NONE", report["physical_emission"])
