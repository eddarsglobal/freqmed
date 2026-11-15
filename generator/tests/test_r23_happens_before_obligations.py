"""GEN-R23 adversarial source-only C11 happens-before/quiescence regressions.

Software-only mutations of C text are regression checks, not concurrency
simulation, OS callback invocation, signal generation or scientific measurement.
"""
import hashlib
import os
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"audits"))
import r17_evidence_verifier as r17
import r19_adversarial_source_audit as r19
import r21_bureau_evidence_gaps as r21
import r22_coreaudio_lifetime_review as r22
import r23_happens_before_obligations as r23

class R23HappensBeforeObligations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src=(ROOT/"src/acoustic_macos.c").read_text(encoding="utf-8")
        cls.runner=(ROOT/"RUN_GEN_R23_MAC_INTEL.command").read_text(encoding="utf-8")
        cls.acoustic_hash=hashlib.sha256(cls.src.encode("utf-8")).hexdigest()
        cls.ledger=r23.obligations(cls.src,cls.runner,cls.acoustic_hash)

    def mutation(self,old,new):
        self.assertIn(old,self.src)
        changed=self.src.replace(old,new,1)
        self.assertNotEqual(changed,self.src)
        with self.assertRaises((r23.R23Error,r22.R22Error)):
            r23.obligations(changed,self.runner,self.acoustic_hash)

    def test_15_proof_obligations_have_exact_unique_ids(self):
        self.assertEqual(15,len(self.ledger))
        self.assertEqual(15,len({item["id"] for item in self.ledger}))

    def test_three_gate_categories_preserved(self):
        self.assertEqual([5,5,5],[sum(x["gate"]==gate for x in self.ledger)
                                  for gate in r23.GATES])
        self.assertEqual(r22.GATE_IDS,r23.GATES)

    def test_every_obligation_is_open_and_nonemitting(self):
        self.assertTrue(all(x["proof_status"]=="OPEN_NOT_DISCHARGED"
                            and x["formal_happens_before_established"] is False
                            and x["os_quiescence_verified"] is False
                            and x["allows_physical_emission"] is False
                            for x in self.ledger))

    def test_all_anchors_are_real_lines_of_pinned_C(self):
        table,_=r17.manifest_integrity(ROOT)
        for record in self.ledger:
            for place in record["anchors"]:
                self.assertEqual(table[place["path"]],place["sha256"])
                line=self.src.splitlines()[place["line"]-1]
                self.assertIn(place["needle"],line)

    def test_each_proof_obligation_has_substantive_missing_evidence(self):
        self.assertTrue(all(len(x["required_independent_proof"])>60
                            and x["responsible_functions"]
                            for x in self.ledger))

    def test_full_reviewer_scope_123_pins(self):
        table,_,obligations=r23.assess(ROOT)
        self.assertGreaterEqual(len(table),123)  # R23 historical baseline
        self.assertEqual(15,len(obligations))

    def test_coreaudio_source_byte_identical_to_R19(self):
        self.assertEqual(r19.PINNED_ACOUSTIC_SHA256,self.acoustic_hash)

    def test_R22_historical_118_minimum_is_backward_compatible(self):
        table,_,notes=r22.assess(ROOT)
        self.assertGreaterEqual(len(table),118)
        self.assertEqual(17,len(notes))

    def test_run_link_allowlist_keeps_public_output_denied(self):
        self.assertEqual(r17.LINK_C_ALLOWLIST,
                         frozenset(r17.link_sources(self.runner)))
        self.assertIn("R23_NONEMITTING_EXECUTABLE_SYMBOL_AUDIT=PASS",self.runner)

    def test_controller_prefill_is_not_claimed_synchronized(self):
        byid={x["id"]:x for x in self.ledger}
        self.assertIn("HB04_CONTROLLER_PREFILL_OUTSIDE_WRITER_GATE",byid)
        self.assertEqual("OPEN_NOT_DISCHARGED",
                         byid["HB04_CONTROLLER_PREFILL_OUTSIDE_WRITER_GATE"]["proof_status"])

    def test_moved_start_before_controller_prefill_is_rejected(self):
        old="fill_audio(ctx,b);\n    if (atomic_load(&ctx->failed))"
        self.mutation(old,"AudioQueueStart(ctx->queue,NULL);\n    if (atomic_load(&ctx->failed))")

    def test_removed_controller_prefill_is_rejected(self):
        self.mutation("fill_audio(ctx,b);", "/* no PCM fill */")

    def test_mutated_callback_gate_release_is_rejected(self):
        self.mutation("atomic_flag_clear_explicit(&ctx->pcm_writer_gate",
                      "atomic_flag_clear_explicit(&ctx->unrelated_flag")

    def test_mutated_callback_entry_counter_is_rejected(self):
        self.mutation("atomic_fetch_add_explicit(&ctx->active_output_callbacks",
                      "atomic_fetch_add_explicit(&ctx->unrelated_count")

    def test_mutated_listener_entry_counter_is_rejected(self):
        self.mutation("atomic_fetch_add_explicit(&ctx->active_property_listeners",
                      "atomic_fetch_add_explicit(&ctx->unrelated_count")

    def test_mutated_listener_remove_failure_is_rejected(self):
        self.mutation("listener_remove_failed=1;", "listener_remove_failed=0;")

    def test_mutated_failed_dispose_pointer_clear_is_rejected(self):
        self.mutation("if (AudioQueueDispose(ctx->queue,true)!=noErr) {",
                      "if (AudioQueueDispose(ctx->queue,true)==noErr) {")

    def test_process_session_claim_acquire_mutation_rejected(self):
        self.mutation("atomic_flag_test_and_set_explicit(&fm_session_claim,memory_order_acquire)",
                      "atomic_flag_test_and_set_explicit(&fm_session_claim,memory_order_relaxed)")

    def test_markdown_does_not_claim_concurrency_proof(self):
        text=r23.markdown({"source_only_obligations":self.ledger})
        self.assertIn("15 obligations, 0 preuve acquittée",text)
        self.assertIn("happens-before C11",text)
        self.assertIn("11 portes Bureau OPEN",text)
        self.assertIn("NOT_AUTHORIZED",text)

    def test_real_R22_chain_and_R23_obligations_pending(self):
        work=os.environ.get("FREQMED_GEN_R23_EVIDENCE_DIR")
        history=os.environ.get("FREQMED_GEN_R19_ARCHIVE_DIR")
        if not work or not history:
            self.skipTest("real Mac Intel R16-R22 reports and R19 archive required")
        work=Path(work)
        older={key:work/name for key,name in {
            "r16":"GEN_R16_OWNERSHIP_EVIDENCE.json",
            "r17":"GEN_R17_VERIFIED_EVIDENCE.json",
            "r18":"GEN_R18_CONTROL_FLOW_EVIDENCE.json",
            "r19":"GEN_R19_ADVERSARIAL_EVIDENCE.json",
            "r20":"GEN_R20_BUREAU_VERIFICATION.json",
        }.items()}
        report=r23.audit(ROOT,Path(history),older,
                         work/"GEN_R21_BUREAU_GAPS.json",
                         work/"GEN_R22_COREAUDIO_REVIEW.json")
        self.assertEqual(r23.VERDICT,report["verdict"])
        self.assertEqual(15,report["obligation_count"])
        self.assertEqual(0,report["obligations_discharged"])
        self.assertEqual(11,report["bureau_gates_open"])
        self.assertEqual(0,report["bureau_gates_resolved"])
        self.assertEqual("NONE",report["physical_emission"])
