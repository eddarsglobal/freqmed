"""GEN-R32 static failed-stop ownership audit: no OS calls or simulations."""
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
import r30_coreaudio_quiescence_adversarial as r30
import r31_critical_shutdown_review as r31
import r32_failed_stop_ownership_review as r32

class R32FailedStopOwnershipReview(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=(ROOT/r31.CANDIDATE).read_text(encoding="utf-8")
        cls.runner=(ROOT/"RUN_GEN_R32_MAC_INTEL.command").read_text(encoding="utf-8")

    def reject(self,old,new):
        self.assertIn(old,self.source)
        with self.assertRaises(r32.R32Error):
            r32.observe(self.source.replace(old,new,1))

    def test_ten_findings_stay_open(self):
        found=r32.observe(self.source)
        self.assertEqual(10,len(found))
        self.assertEqual({"OPEN_NOT_PROVEN"},set(found.values()))

    def test_exactly_two_critical_stop_findings(self):
        severe={x[0] for x in r32.FINDINGS if x[1]=="CRITICAL"}
        self.assertEqual({"FS32_01_FAILED_STOP_MAY_CONTINUE_OUTPUT",
                          "FS32_02_FAILURE_EXIT_RETAINS_LIVE_QUEUE"},severe)

    def test_stop_attempt_before_failure_exit(self):
        ctrl=r29.function(self.source,"controller")
        stop=ctrl.index("const OSStatus r31_immediate_stop_status=AudioQueueStop")
        failed=ctrl.index("if (r31_immediate_stop_status!=noErr) {",stop)
        exit_line=ctrl.index("return -1;",failed)
        self.assertLess(stop,failed)
        self.assertLess(failed,exit_line)

    def test_failed_stop_keeps_ambiguous_queue(self):
        ctrl=r29.function(self.source,"controller")
        start=ctrl.index("if (r31_immediate_stop_status!=noErr) {")
        end=ctrl.index("return -1;",start)
        self.assertNotIn("AudioQueueDispose(",ctrl[start:end])
        self.assertNotIn("ctx->queue=NULL",ctrl[start:end])

    def test_software_quarantine_not_hardware_cutoff(self):
        self.assertEqual("OPEN_NOT_PROVEN",
                         r32.observe(self.source)[
                           "FS32_01_FAILED_STOP_MAY_CONTINUE_OUTPUT"])

    def test_successful_stop_not_os_callback_quiescence(self):
        self.assertEqual("OPEN_NOT_PROVEN",
                         r32.observe(self.source)[
                           "FS32_03_C11_CLOSE_NOT_OS_CANCELLATION"])

    def test_original_backend_r19_sha_unchanged(self):
        actual=hashlib.sha256((ROOT/r26.ORIGINAL).read_bytes()).hexdigest()
        self.assertEqual(r19.PINNED_ACOUSTIC_SHA256,actual)

    def test_r31_candidate_pinned_without_edits(self):
        table,_,_,_=r32.inspect(ROOT)
        actual=hashlib.sha256((ROOT/r31.CANDIDATE).read_bytes()).hexdigest()
        self.assertEqual(table[r31.CANDIDATE],actual)

    def test_r28_c11_gate_remains_unmodified(self):
        c=(ROOT/r28.CANDIDATE).read_text(encoding="utf-8")
        self.assertEqual(5,len(r28.observe(c)))

    def test_history_r30_and_r31_critical_still_open(self):
        self.assertEqual(2,sum(x[1]=="CRITICAL" for x in r30.FINDINGS))
        self.assertEqual(2,sum(x[1]=="CRITICAL" for x in r31.FINDINGS))

    def test_exact_manifest_175_files(self):
        table,_,_,_=r32.inspect(ROOT)
        self.assertEqual(175,len(table))

    def test_runner_links_no_coreaudio_emitter(self):
        self.assertIn("R32_NONEMITTING_EXECUTABLE_SYMBOL_AUDIT=PASS",self.runner)
        self.assertIn("R32_R31_CANDIDATE_OBJECT=COMPILED_UNLINKED",self.runner)

    def test_26_bureau_evidence_reports(self):
        self.assertIn("R32_BUREAU_EVIDENCE_DOSSIER=26_FILES_SHA256_PASS",
                      self.runner)

    def test_actual_owner_mac_r16_r31_chain(self):
        archive=os.environ.get("FREQMED_GEN_R19_ARCHIVE_DIR")
        folder=os.environ.get("FREQMED_GEN_R32_EVIDENCE_DIR")
        self.assertTrue(archive and folder,
                        "R32 authentic R19 evidence and R16-R31 reports required")
        names=("OWNERSHIP_EVIDENCE","VERIFIED_EVIDENCE",
               "CONTROL_FLOW_EVIDENCE","ADVERSARIAL_EVIDENCE",
               "BUREAU_VERIFICATION","BUREAU_GAPS","COREAUDIO_REVIEW",
               "PROOF_OBLIGATIONS","SHARED_STATE_CONTRACT",
               "REMEDIATION_REVIEW","PATCH_SAFETY_GATE",
               "ADVERSARIAL_REVIEW","QUEUE_ADMISSION_DESIGN",
               "ADMISSION_INTEGRATION_REVIEW","COREAUDIO_QUIESCENCE",
               "CRITICAL_SHUTDOWN")
        d=Path(folder)
        reports={"r"+str(n):d/("GEN_R"+str(n)+"_"+name+".json")
                 for n,name in zip(range(16,32),names)}
        result=r32.audit(ROOT,Path(archive),reports)
        self.assertEqual(r32.VERDICT,result["verdict"])
        self.assertEqual(10,result["r32_findings_open"])
        self.assertEqual(2,result["r32_critical_open"])
        self.assertEqual(8,result["r31_findings_open"])
        self.assertEqual(11,result["bureau_gates_open"])
        self.assertFalse(result["r32_active_output"])

    def test_mutated_stop_status_condition_rejected(self):
        self.reject("if (r31_immediate_stop_status!=noErr) {",
                    "if (r31_immediate_stop_status==noErr) {")

    def test_mutated_stop_immediate_flag_rejected(self):
        self.reject("AudioQueueStop(ctx->queue,true);",
                    "AudioQueueStop(ctx->queue,false);")

    def test_mutated_quarantine_refused(self):
        self.reject("fm_context_quarantined,1,memory_order_release",
                    "fm_context_quarantined,0,memory_order_release")

    def test_mutated_callback_admission_rejected(self):
        self.reject("if (!fm_r28_gate_try_enter(&ctx->queue_admission)) return;",
                    "if (fm_r28_gate_try_enter(&ctx->queue_admission)) return;")

    def test_mutated_disposal_site_rejected(self):
        self.reject("if (AudioQueueDispose(ctx->queue,true)!=noErr) {",
                    "if (AudioQueueDispose(ctx->queue,false)!=noErr) {")

    def test_markdown_keeps_unsolved_safety_and_denials(self):
        report={"r32_findings":[{"id":f[0],"severity":f[1],
                  "bureau_role":f[2]} for f in r32.FINDINGS]}
        doc=r32.markdown(report)
        self.assertIn("NOT an independent",doc)
        self.assertIn("REAL_OUTPUT=NOT_AUTHORIZED",doc)
        self.assertIn("CRITICAL",doc)
