"""GEN-R33 failure-state ownership contract regressions: SOURCE ONLY.
No CoreAudio callbacks, forced OS failure or scientific simulation.
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
import r30_coreaudio_quiescence_adversarial as r30
import r31_critical_shutdown_review as r31
import r32_failed_stop_ownership_review as r32
import r33_failure_state_ownership_contract as r33

class R33FailureStateOwnershipReview(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=(ROOT/r31.CANDIDATE).read_text(encoding="utf-8")
        cls.runner=(ROOT/"RUN_GEN_R33_MAC_INTEL.command").read_text(encoding="utf-8")

    def reject(self,old,new):
        self.assertIn(old,self.source)
        with self.assertRaises(r33.R33Error):
            r33.observe(self.source.replace(old,new,1))

    def test_twelve_unproven_findings(self):
        found=r33.observe(self.source)
        self.assertEqual(12,len(found))
        self.assertEqual({"OPEN_NOT_PROVEN"},set(found.values()))

    def test_three_critical_r33_obligations(self):
        self.assertEqual(3,sum(f[1]=="CRITICAL" for f in r33.FINDINGS))

    def test_ten_documentary_states_not_executable(self):
        self.assertEqual(10,len(r33.STATES))
        self.assertEqual(10,len({s[0] for s in r33.STATES}))

    def test_prepublication_release_scope_explicit(self):
        self.assertEqual(2,sum(s[3]=="PREPUBLICATION_RELEASE_SOURCE_PATH"
                         for s in r33.STATES))
        r33.observe(self.source)

    def test_published_userdata_no_auto_release(self):
        ctrl=r29.function(self.source,"controller")
        i=ctrl.index("AudioQueueNewOutput(&fmt,output_callback,ctx")
        self.assertNotIn("free(owner_ctx);",ctrl[i:])

    def test_failed_stop_retains_owner_and_queue(self):
        self.assertEqual("OPEN_NOT_PROVEN",r33.observe(self.source)[
                         "OWN33_01_FAILED_STOP_LIVE_OUTPUT"])

    def test_failed_dispose_does_not_clear_reference(self):
        ctrl=r29.function(self.source,"controller")
        start=ctrl.index("if (AudioQueueDispose(ctx->queue,true)!=noErr) {")
        end=ctrl.index("} else {",start)
        self.assertNotIn("ctx->queue=NULL;",ctrl[start:end])

    def test_successful_dispose_not_safe_user_data_free(self):
        result=r33.observe(self.source)
        self.assertEqual("OPEN_NOT_PROVEN",
                         result["OWN33_10_SUCCESSFUL_DISPOSE_NOT_SAFE_FREE"])

    def test_original_source_sha_still_r19_pinned(self):
        actual=hashlib.sha256((ROOT/r26.ORIGINAL).read_bytes()).hexdigest()
        self.assertEqual(r19.PINNED_ACOUSTIC_SHA256,actual)

    def test_r31_c_source_unchanged(self):
        table,_,_,_=r33.inspect(ROOT)
        digest=hashlib.sha256((ROOT/r31.CANDIDATE).read_bytes()).hexdigest()
        self.assertEqual(table[r31.CANDIDATE],digest)

    def test_r28_c11_admission_still_unchanged(self):
        self.assertEqual(5,len(r28.observe(
            (ROOT/r28.CANDIDATE).read_text(encoding="utf-8"))))

    def test_181_source_pins_exact(self):
        table,_,_,_=r33.inspect(ROOT)
        self.assertGreaterEqual(len(table),181)

    def test_runner_nonemitting_and_28_reports(self):
        self.assertIn("R33_NONEMITTING_EXECUTABLE_SYMBOL_AUDIT=PASS",self.runner)
        self.assertIn("R33_BUREAU_CONTRACT_DOSSIER=28_FILES_SHA256_PASS",self.runner)
        self.assertIn("R33_R31_CANDIDATE_OBJECT=COMPILED_UNLINKED",self.runner)

    def test_real_owner_mac_r16_r32_chain(self):
        archive=os.environ.get("FREQMED_GEN_R19_ARCHIVE_DIR")
        folder=os.environ.get("FREQMED_GEN_R33_EVIDENCE_DIR")
        self.assertTrue(archive and folder,
                        "R33 requires actual owner R19 archive and R16-R32 reports")
        names=("OWNERSHIP_EVIDENCE","VERIFIED_EVIDENCE","CONTROL_FLOW_EVIDENCE",
               "ADVERSARIAL_EVIDENCE","BUREAU_VERIFICATION","BUREAU_GAPS",
               "COREAUDIO_REVIEW","PROOF_OBLIGATIONS","SHARED_STATE_CONTRACT",
               "REMEDIATION_REVIEW","PATCH_SAFETY_GATE",
               "ADVERSARIAL_REVIEW","QUEUE_ADMISSION_DESIGN",
               "ADMISSION_INTEGRATION_REVIEW","COREAUDIO_QUIESCENCE",
               "CRITICAL_SHUTDOWN","FAILED_STOP_OWNERSHIP")
        root=Path(folder)
        reports={"r"+str(n):root/("GEN_R"+str(n)+"_"+stem+".json")
                 for n,stem in zip(range(16,33),names)}
        result=r33.audit(ROOT,Path(archive),reports)
        self.assertEqual(r33.VERDICT,result["verdict"])
        self.assertEqual(12,result["r33_findings_open"])
        self.assertEqual(3,result["r33_critical_open"])
        self.assertEqual(10,result["r33_documentary_states"])
        self.assertEqual(11,result["bureau_gates_open"])
        self.assertFalse(result["r33_output_linked"])

    def test_mutated_stop_status_guard_rejected(self):
        self.reject("if (r31_immediate_stop_status!=noErr) {",
                    "if (r31_immediate_stop_status==noErr) {")

    def test_mutated_dispose_status_guard_rejected(self):
        self.reject("if (AudioQueueDispose(ctx->queue,true)!=noErr) {",
                    "if (AudioQueueDispose(ctx->queue,false)!=noErr) {")

    def test_mutated_prepublication_release_rejected(self):
        self.reject("if (!ctx->total_frames) {",
                    "if (ctx->total_frames) {")

    def test_mutated_busy_admission_guard_rejected(self):
        self.reject("if (r31_admission_busy) {",
                    "if (!r31_admission_busy) {")

    def test_mutated_quarantine_on_failed_stop_rejected(self):
        target=("fm_latch_first_fault(ctx,FM_FAULT_SHUTDOWN);\n"
                "      atomic_store_explicit(&fm_context_quarantined,1,memory_order_release);\n"
                "      return -1;")
        self.reject(target,target.replace("quarantined,1","quarantined,0"))

    def test_report_does_not_claim_safety_or_authorization(self):
        report={"r33_findings":[{"id":f[0],"severity":f[1],
                  "bureau_role":f[2]} for f in r33.FINDINGS],
                "r33_state_rows":[{"state":s[0],"conservative_source_policy":s[3],
                                   "os_queue_state":s[2]} for s in r33.STATES]}
        out=r33.markdown(report)
        self.assertIn("not a",out)
        self.assertIn("REAL_OUTPUT=NOT_AUTHORIZED",out)
        self.assertIn("CRITICAL",out)
