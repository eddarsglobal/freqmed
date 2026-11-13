"""GEN-R16 real-source static ownership evidence tests.

No fabricated OS returns, scientific signals, numerical model, mock device,
physical output, or exposure. A bounded lexical audit is NOT formal C proof.
"""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "audits"))
from r16_ownership_static_audit import audit, lex, words, function, if_blocks, one, contains, occurrence

SRC = (ROOT / "src/acoustic_macos.c").read_text(encoding="utf-8")
EM = (ROOT / "src/em_backend.c").read_text(encoding="utf-8")
RUN = (ROOT / "RUN_GEN_R16_MAC_INTEL.command").read_text(encoding="utf-8")
TOKENS = lex(SRC)
ENTRY = function(TOKENS, "acoustic_output_impl")
BLOCKS = if_blocks(ENTRY)
EVIDENCE = audit(ROOT)
BY_ID = {item["id"]: item for item in EVIDENCE["checks"]}

class R16StaticOwnershipEvidence(unittest.TestCase):
    def test_schema_identifies_static_source_only(self):
        self.assertEqual("FREQMED_GEN_R16_STATIC_OWNERSHIP_EVIDENCE", EVIDENCE["schema"])
        self.assertEqual("SOURCE_ONLY_NON_EMITTING", EVIDENCE["analysis_scope"])
        self.assertEqual("BOUNDED_C_TOKEN_AND_BRACE_AUDIT", EVIDENCE["method"])

    def test_evidence_references_actual_source_hash(self):
        self.assertEqual(hashlib.sha256(SRC.encode("utf-8")).hexdigest(),
                         EVIDENCE["source_sha256"])
        self.assertEqual("src/acoustic_macos.c", EVIDENCE["source"])

    def test_all_reported_checks_have_unique_ids(self):
        ids = [record["id"] for record in EVIDENCE["checks"]]
        self.assertGreaterEqual(len(ids), 20)
        self.assertEqual(len(ids), len(set(ids)))

    def test_all_static_contracts_pass(self):
        self.assertEqual(0, EVIDENCE["failed"])
        self.assertEqual(len(EVIDENCE["checks"]), EVIDENCE["passed"])
        self.assertEqual("STATIC_SOURCE_CONTRACT_PASS", EVIDENCE["verdict"])

    def test_each_check_has_actual_source_line(self):
        total_lines = len(SRC.splitlines())
        for record in EVIDENCE["checks"]:
            self.assertGreaterEqual(record["source_line"], 1, record["id"])
            self.assertLessEqual(record["source_line"], total_lines, record["id"])
            self.assertEqual("STATIC_C_TOKENS", record["basis"])

    def test_c_lexer_discards_comments_from_real_source(self):
        self.assertNotIn("Caution", words(TOKENS))
        self.assertIn("AudioQueueDispose", words(TOKENS))
        self.assertIn("AudioQueueNewOutput", words(TOKENS))

    def test_callback_functions_are_structurally_found(self):
        for name in ("output_callback", "queue_running_listener",
                     "acoustic_output_impl", "fm_acoustic_physical_output"):
            self.assertGreater(len(function(TOKENS, name)), 5)

    def test_heap_owner_and_claim_audited(self):
        for name in ("admission_claim_precedes_heap_allocation",
                     "quarantine_checked_before_and_after_claim",
                     "recheck_releases_unpublished_session_claim",
                     "callback_context_is_heap_owned"):
            self.assertEqual("PASS", BY_ID[name]["result"])

    def test_all_unpublished_cleanup_paths_accounted(self):
        for name in ("alloc_failure_releases_claim",
                     "zero_frames_releases_unpublished_heap",
                     "zero_fade_releases_unpublished_heap"):
            self.assertEqual("PASS", BY_ID[name]["result"])

    def test_queue_creation_never_frees_on_uncertain_os_error(self):
        self.assertEqual("PASS",
                         BY_ID["queue_creation_failure_quarantines_without_free"]["result"])

    def test_route_binding_disposal_cannot_free_on_uncertainty(self):
        for name in ("rejected_route_disposes_synchronously",
                     "binding_cleanup_checks_both_callback_counters",
                     "binding_disposal_failure_never_frees"):
            self.assertEqual("PASS", BY_ID[name]["result"])

    def test_listener_registration_and_removal_uncertainty(self):
        for name in ("listener_registration_failure_records_uncertainty",
                     "listener_removal_failure_records_uncertainty"):
            self.assertEqual("PASS", BY_ID[name]["result"])

    def test_callback_accounting_and_pcm_writer_gate(self):
        for name in ("callback_entry_exit_accounting",
                     "callback_pcm_writer_gate",
                     "callback_does_not_request_stop"):
            self.assertEqual("PASS", BY_ID[name]["result"])

    def test_shutdown_barrier_precedes_final_disposal(self):
        self.assertEqual("PASS",
                         BY_ID["shutdown_barrier_precedes_listener_removal_and_dispose"]["result"])

    def test_failed_disposal_does_not_clear_pointer(self):
        result = BY_ID["failed_disposal_retains_queue_and_heap"]
        self.assertEqual("PASS", result["result"])
        failure = one(BLOCKS, "AudioQueueDispose(ctx->queue,true)!=noErr")["then"]
        self.assertFalse(contains(failure, "ctx->queue=NULL"))
        self.assertFalse(contains(failure, "free(owner_ctx)"))

    def test_success_disposal_only_confirms_release(self):
        self.assertEqual("PASS",
                         BY_ID["successful_disposal_alone_confirms_and_clears"]["result"])
        success = one(BLOCKS, "AudioQueueDispose(ctx->queue,true)!=noErr")["else"]
        self.assertTrue(contains(success, "atomic_store(&ctx->dispose_confirmed,1)"))

    def test_all_free_sites_are_classified(self):
        self.assertEqual("PASS", BY_ID["every_heap_free_site_classified"]["result"])
        self.assertEqual(4, len(occurrence(ENTRY, "free(owner_ctx)")))

    def test_final_cleanup_needs_quiescence_or_quarantine(self):
        for name in ("final_release_requires_disposal_and_listener_clarity",
                     "final_quarantine_keeps_context_and_claim"):
            self.assertEqual("PASS", BY_ID[name]["result"])

    def test_public_binaries_are_denied_and_unknowns_reported(self):
        self.assertEqual("PASS",
                         BY_ID["public_acoustic_entry_unconditionally_denied"]["result"])
        self.assertEqual("PASS",
                         BY_ID["em_public_entry_unconditionally_denied"]["result"])
        self.assertEqual("PASS", BY_ID["runnable_excludes_output_backend"]["result"])
        self.assertEqual("NONE", EVIDENCE["scientific_simulation"])
        self.assertEqual("NONE", EVIDENCE["physical_emission"])
        self.assertEqual("NOT_AUTHORIZED", EVIDENCE["real_output"])
        self.assertEqual("NOT_AUTHORIZED", EVIDENCE["production"])
        self.assertIn("ACTIVE_COREAUDIO_CALLBACK_LIFETIME_UNTESTED", EVIDENCE["unresolved"])
        self.assertIn("NO_FORMAL_C_CONCURRENCY_OR_MEMORY_MODEL_PROOF", EVIDENCE["unresolved"])
        self.assertIn("BUREAU_CERTIFICATION_PENDING", EVIDENCE["unresolved"])

    def test_real_mac_binary_hard_denies_all_output_actions(self):
        binary = os.environ.get("FREQMED_GEN_R16_BINARY")
        if not binary:
            self.skipTest("Real Mac Intel nonemitting executable required")
        status = subprocess.run([binary, "status"], capture_output=True,
                                text=True, timeout=5, check=True)
        data = json.loads(status.stdout)
        self.assertEqual("NONE", data["physical_emission"])
        self.assertEqual("NOT_LINKED_HARD_DENIED", data["acoustic_output"])
        self.assertEqual("BLOCKED_NO_QUALIFIED_EM_DEVICE", data["electromagnetic_output"])
        for action in ("emit", "arm", "play", "transmit"):
            refused = subprocess.run([binary, action], capture_output=True,
                                     text=True, timeout=5)
            self.assertNotEqual(0, refused.returncode)
