"""GEN-R35 static Apple OS callback-contract / pre-admission proof tests.
Mutation means altering Python strings, NOT running a concurrency simulation.
"""
import hashlib
import os
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"audits"))
import r19_adversarial_source_audit as r19
import r26_isolated_patch_gate as r26
import r28_queue_admission_design as r28
import r29_admission_integration_review as r29
import r31_critical_shutdown_review as r31
import r34_userdata_lifetime_review as r34
import r35_pre_admission_os_contract_review as r35

class R35PreAdmissionOSContractReview(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=(ROOT/r31.CANDIDATE).read_text(encoding="utf-8")
        cls.runner=(ROOT/"RUN_GEN_R35_MAC_INTEL.command").read_text(encoding="utf-8")

    def reject(self,before,after):
        self.assertIn(before,self.source)
        with self.assertRaises(r35.R35Error):
            r35.observe(self.source.replace(before,after,1))

    def test_twelve_unproven_source_findings(self):
        d=r35.observe(self.source)
        self.assertEqual(12,len(d))
        self.assertEqual({"OPEN_NOT_PROVEN"},set(d.values()))

    def test_four_critical_proof_blockers(self):
        self.assertEqual({
            "PA35_01_OUTPUT_PRE_ADMISSION_LIFETIME",
            "PA35_02_LISTENER_PRE_ADMISSION_LIFETIME",
            "PA35_03_FAILED_DISPOSE_CALLBACKS",
            "PA35_04_FAILED_STOP_PHYSICAL_CUTOFF",
        },{row[0] for row in r35.FINDINGS if row[1]=="CRITICAL"})

    def test_nine_apple_api_evidence_classes(self):
        self.assertEqual(9,len(r35.API_EVIDENCE))
        self.assertEqual(9,len({e[0] for e in r35.API_EVIDENCE}))

    def test_api_pages_do_not_prove_failed_stop_or_disposal(self):
        classes={e[0]:e[1] for e in r35.API_EVIDENCE}
        self.assertEqual("NOT_ESTABLISHED_BY_PAGES",
                         classes["API35_09_FAILED_OSSTATUS"])
        self.assertEqual("DOCUMENTED_POST_DISPOSAL_ONLY",
                         classes["API35_05_DISPOSE_CALLBACKS"])

    def test_thirteen_documentary_callback_phases(self):
        self.assertEqual(13,len(r35.PHASES))
        self.assertEqual(13,len({e[0] for e in r35.PHASES}))

    def test_output_userdata_access_before_first_gate(self):
        s=r29.function(self.source,"callback")
        self.assertLess(s.index("AcousticContext *ctx=(AcousticContext*)ptr;"),
                        s.index("fm_r28_gate_try_enter(&ctx->queue_admission)"))

    def test_listener_userdata_access_before_first_gate(self):
        s=r29.function(self.source,"listener")
        self.assertLess(s.index("AcousticContext *ctx=(AcousticContext*)data;"),
                        s.index("fm_r28_gate_try_enter(&ctx->queue_admission)"))

    def test_active_counters_start_after_gate(self):
        for name in ("callback","listener"):
            part=r29.function(self.source,name)
            self.assertLess(part.index("fm_r28_gate_try_enter(&ctx->queue_admission)"),
                            part.index("atomic_fetch_add_explicit(&ctx->active_"))

    def test_successful_disposal_not_failed_status_evidence(self):
        grades={e[0]:e[1] for e in r35.API_EVIDENCE}
        self.assertNotIn("FAILED",grades["API35_04_DISPOSE_TRUE"])
        self.assertEqual("OPEN_NOT_PROVEN",
                         r35.observe(self.source)["PA35_03_FAILED_DISPOSE_CALLBACKS"])

    def test_stop_error_remains_no_physical_cutoff_proof(self):
        self.assertEqual("OPEN_NOT_PROVEN",
                         r35.observe(self.source)["PA35_04_FAILED_STOP_PHYSICAL_CUTOFF"])

    def test_original_C_unchanged_r19_sha(self):
        actual=hashlib.sha256((ROOT/r26.ORIGINAL).read_bytes()).hexdigest()
        self.assertEqual(r19.PINNED_ACOUSTIC_SHA256,actual)

    def test_candidate_c31_sha_pinned_and_r28_gate_preserved(self):
        table,_,_,_=r35.inspect(ROOT)
        self.assertEqual(table[r31.CANDIDATE],
                         hashlib.sha256((ROOT/r31.CANDIDATE).read_bytes()).hexdigest())
        self.assertEqual(5,len(r28.observe(
            (ROOT/r28.CANDIDATE).read_text(encoding="utf-8"))))

    def test_exact_193_pinned_sources(self):
        table,_,_,_=r35.inspect(ROOT)
        self.assertGreaterEqual(len(table),193)

    def test_runner_nonemitting_32_report_contract(self):
        self.assertIn("R35_R31_CANDIDATE_OBJECT=COMPILED_UNLINKED",self.runner)
        self.assertIn("R35_NONEMITTING_EXECUTABLE_SYMBOL_AUDIT=PASS",self.runner)
        self.assertIn("R35_BUREAU_API_DOSSIER=32_FILES_SHA256_PASS",self.runner)

    def test_real_owner_mac_r16_r34_history(self):
        archive=os.environ.get("FREQMED_GEN_R19_ARCHIVE_DIR")
        folder=os.environ.get("FREQMED_GEN_R35_EVIDENCE_DIR")
        self.assertTrue(archive and folder,
                        "R35 requires actual unchanged Mac R19 archive and R16-R34 evidence")
        stems=("OWNERSHIP_EVIDENCE","VERIFIED_EVIDENCE",
               "CONTROL_FLOW_EVIDENCE","ADVERSARIAL_EVIDENCE",
               "BUREAU_VERIFICATION","BUREAU_GAPS","COREAUDIO_REVIEW",
               "PROOF_OBLIGATIONS","SHARED_STATE_CONTRACT",
               "REMEDIATION_REVIEW","PATCH_SAFETY_GATE",
               "ADVERSARIAL_REVIEW","QUEUE_ADMISSION_DESIGN",
               "ADMISSION_INTEGRATION_REVIEW","COREAUDIO_QUIESCENCE",
               "CRITICAL_SHUTDOWN","FAILED_STOP_OWNERSHIP",
               "FAILURE_STATE_OWNERSHIP","USERDATA_LIFETIME")
        parent=Path(folder)
        reports={"r"+str(n):parent/("GEN_R"+str(n)+"_"+stem+".json")
                 for n,stem in zip(range(16,35),stems)}
        report=r35.audit(ROOT,Path(archive),reports)
        self.assertEqual(r35.VERDICT,report["verdict"])
        self.assertEqual(12,report["r35_findings_open"])
        self.assertEqual(4,report["r35_critical_open"])
        self.assertEqual(14,report["r34_findings_open"])
        self.assertEqual(11,report["bureau_gates_open"])
        self.assertFalse(report["r35_active_coreaudio"])

    def test_mutation_output_pre_gate_rejected(self):
        self.reject(
            "if (!fm_r28_gate_try_enter(&ctx->queue_admission)) return;\n"
            "  (void)atomic_fetch_add_explicit(&ctx->active_output_callbacks",
            "if (fm_r28_gate_try_enter(&ctx->queue_admission)) return;\n"
            "  (void)atomic_fetch_add_explicit(&ctx->active_output_callbacks")

    def test_mutation_listener_pre_gate_rejected(self):
        self.reject(
            "if (!fm_r28_gate_try_enter(&ctx->queue_admission)) return;\n"
            "  (void)atomic_fetch_add_explicit(&ctx->active_property_listeners",
            "if (fm_r28_gate_try_enter(&ctx->queue_admission)) return;\n"
            "  (void)atomic_fetch_add_explicit(&ctx->active_property_listeners")

    def test_mutation_stop_osstatus_guard_rejected(self):
        self.reject("if (r31_immediate_stop_status!=noErr) {",
                    "if (r31_immediate_stop_status==noErr) {")

    def test_mutation_listener_remove_failure_rejected(self):
        self.reject("listener_remove_failed=1;","listener_remove_failed=0;")

    def test_report_keeps_os_uncertainty_and_hard_denial(self):
        report={"r35_findings":[{"id":f[0],"severity":f[1],
               "bureau_role":f[2]} for f in r35.FINDINGS],
               "r35_api_evidence":[{"id":a,"classification":b,"url":c}
               for a,b,c,_ in r35.API_EVIDENCE]}
        text=r35.markdown(report)
        self.assertIn("NOT proof",text)
        self.assertIn("REAL_OUTPUT=NOT_AUTHORIZED",text)
        self.assertIn("CRITICAL",text)
