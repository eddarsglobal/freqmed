"""GEN-R29 independent source review: no CoreAudio runtime, no simulation."""
import hashlib
import os
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"audits"))
import r19_adversarial_source_audit as r19
import r26_isolated_patch_gate as r26
import r27_adversarial_ownership_review as r27
import r28_queue_admission_design as r28
import r29_admission_integration_review as r29

class R29AdmissionIntegrationReview(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c=(ROOT/r29.CANDIDATE).read_text(encoding="utf-8")
        cls.runner=(ROOT/"RUN_GEN_R29_MAC_INTEL.command").read_text(encoding="utf-8")
    def reject(self,old,new):
        self.assertIn(old,self.c)
        with self.assertRaises((r29.R29Error,ValueError)):
            r29.observe(self.c.replace(old,new,1))
    def test_seven_source_findings_all_open(self):
        result=r29.observe(self.c)
        self.assertEqual(7,len(result))
        self.assertEqual({"OPEN_NOT_PROVEN"},set(result.values()))
    def test_gate_included_only_in_r29(self):
        self.assertEqual(1,self.c.count('#include "r28_callback_admission_gate.c"'))
    def test_admission_before_callback_counters(self):
        r29.observe(self.c)
        self.assertEqual(2,self.c.count("fm_r28_gate_try_enter(&ctx->queue_admission)"))
    def test_exact_two_callback_leave_sites(self):
        self.assertEqual(2,self.c.count("fm_r28_gate_leave(&ctx->queue_admission);"))
    def test_three_controller_close_sites(self):
        self.assertEqual(3,self.c.count("fm_r28_gate_close(&ctx->queue_admission);"))
    def test_two_cleanup_closed_empty_checks(self):
        self.assertEqual(2,self.c.count("if (!fm_r28_gate_closed_and_empty(&ctx->queue_admission))"))
    def test_original_r19_source_unchanged(self):
        data=(ROOT/r26.ORIGINAL).read_bytes()
        self.assertEqual(r19.PINNED_ACOUSTIC_SHA256,hashlib.sha256(data).hexdigest())
    def test_r26_candidate_unchanged(self):
        original=(ROOT/r26.ORIGINAL).read_text(encoding="utf-8")
        candidate=(ROOT/r26.CANDIDATE).read_text(encoding="utf-8")
        self.assertEqual(candidate,r26.expected_candidate(original))
    def test_r28_gate_source_is_still_pinned(self):
        c=(ROOT/r28.CANDIDATE).read_text(encoding="utf-8")
        self.assertEqual(5,len(r28.observe(c)))
    def test_156_manifest_pins_and_isolated_runner(self):
        table,_,_,_=r29.inspect(ROOT)
        self.assertGreaterEqual(len(table),156)
    def test_runner_never_links_r29_to_cli(self):
        self.assertIn("R29_NONEMITTING_EXECUTABLE_SYMBOL_AUDIT=PASS",self.runner)
        self.assertIn("R29_INTEGRATED_CANDIDATE_OBJECT=COMPILED_UNLINKED",self.runner)
    def test_r29_report_dossier_is_sha_checked(self):
        self.assertIn("R29_BUREAU_REVIEW_DOSSIER=20_FILES_SHA256_PASS",self.runner)
    def test_owner_mac_historical_evidence_chain(self):
        archive=os.environ.get("FREQMED_GEN_R19_ARCHIVE_DIR")
        directory=os.environ.get("FREQMED_GEN_R29_EVIDENCE_DIR")
        if not archive or not directory:
            self.skipTest("Mac Intel owner R16-R28 report chain required")
        d=Path(directory)
        names=("GEN_R16_OWNERSHIP_EVIDENCE.json",
               "GEN_R17_VERIFIED_EVIDENCE.json",
               "GEN_R18_CONTROL_FLOW_EVIDENCE.json",
               "GEN_R19_ADVERSARIAL_EVIDENCE.json",
               "GEN_R20_BUREAU_VERIFICATION.json",
               "GEN_R21_BUREAU_GAPS.json",
               "GEN_R22_COREAUDIO_REVIEW.json",
               "GEN_R23_PROOF_OBLIGATIONS.json",
               "GEN_R24_SHARED_STATE_CONTRACT.json",
               "GEN_R25_REMEDIATION_REVIEW.json",
               "GEN_R26_PATCH_SAFETY_GATE.json",
               "GEN_R27_ADVERSARIAL_REVIEW.json",
               "GEN_R28_QUEUE_ADMISSION_DESIGN.json")
        paths={"r"+str(n):d/name for n,name in zip(range(16,29),names)}
        outcome=r29.audit(ROOT,Path(archive),paths)
        self.assertEqual(7,outcome["r29_findings_open"])
        self.assertEqual("NOT_PROVEN",outcome["C11_race_freedom"])
        self.assertEqual(11,outcome["bureau_gates_open"])
        self.assertFalse(outcome["r29_linked_or_executed"])
    def test_mutated_callback_try_enter_rejected(self):
        self.reject("if (!fm_r28_gate_try_enter(&ctx->queue_admission)) return;",
                    "if (!fm_r28_gate_closed_and_empty(&ctx->queue_admission)) return;")
    def test_mutated_callback_leave_rejected(self):
        self.reject("fm_r28_gate_leave(&ctx->queue_admission);",
                    "fm_r28_gate_close(&ctx->queue_admission);")
    def test_mutated_initialization_rejected(self):
        self.reject("fm_r28_gate_init(&ctx->queue_admission);",
                    "fm_r28_gate_close(&ctx->queue_admission);")
    def test_mutated_final_gate_seal_rejected(self):
        self.reject("fm_r28_gate_close(&ctx->queue_admission);",
                    "fm_r28_gate_init(&ctx->queue_admission);")
    def test_mutated_final_cleanup_guard_rejected(self):
        self.reject("if (!fm_r28_gate_closed_and_empty(&ctx->queue_admission))",
                    "if (fm_r28_gate_closed_and_empty(&ctx->queue_admission))")
    def test_mutated_queue_clear_rejected(self):
        self.reject("ctx->queue=NULL;","ctx->queue=(AudioQueueRef)0;")
    def test_r29_markdown_is_not_certification(self):
        report={"r29_findings":[{"id":x[0],"priority":x[1],
                  "bureau_role":x[2]} for x in r29.FINDINGS]}
        text=r29.markdown(report)
        self.assertIn("NOT prove",text)
        self.assertIn("NOT_AUTHORIZED",text)
