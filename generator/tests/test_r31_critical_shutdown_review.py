"""GEN-R31 exact-source C shutdown order and OS/ownership evidence review.
No CoreAudio calls, no synthetic concurrency, no scientific simulation or output.
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

class R31CriticalShutdownReview(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original=(ROOT/r29.CANDIDATE).read_text(encoding="utf-8")
        cls.c=(ROOT/r31.CANDIDATE).read_text(encoding="utf-8")
        cls.runner=(ROOT/"RUN_GEN_R31_MAC_INTEL.command").read_text(encoding="utf-8")

    def reject(self,old,new):
        self.assertIn(old,self.c)
        with self.assertRaises(r31.R31Error):
            r31.observe(self.original,self.c.replace(old,new,1))

    def test_eight_findings_are_open_not_proven(self):
        states=r31.observe(self.original,self.c)
        self.assertEqual(8,len(states))
        self.assertEqual({"OPEN_NOT_PROVEN"},set(states.values()))

    def test_two_critical_design_gates_remain_open(self):
        self.assertEqual(2,sum(f[1]=="CRITICAL" for f in r31.FINDINGS))
        self.assertEqual({"SH31_01_STOP_BEFORE_BUSY_EXIT",
                          "SH31_02_FAILED_STOP_MAY_STILL_EMIT"},
                         {f[0] for f in r31.FINDINGS if f[1]=="CRITICAL"})

    def test_one_new_scoped_C_change_only(self):
        source=r31.exact_scope(self.original,self.c)
        self.assertIn("r31_immediate_stop_status",source)
        self.assertNotIn("AudioQueueDispose(",source)

    def test_stop_attempt_before_admission_busy_return(self):
        p=r31.exact_scope(self.original,self.c)
        self.assertLess(p.index("AudioQueueStop(ctx->queue,true)"),
                        p.index("if (r31_admission_busy) {"))

    def test_stop_failure_prevents_disposal_and_retains_userdata(self):
        p=r31.exact_scope(self.original,self.c)
        failure=p.index("if (r31_immediate_stop_status!=noErr) {")
        self.assertIn("return -1;",p[failure:])
        self.assertNotIn("free(owner_ctx)",p)
        self.assertNotIn("AudioQueueDispose(",p)

    def test_busy_admission_does_not_dispose_C_candidate(self):
        p=r31.exact_scope(self.original,self.c)
        self.assertIn("if (r31_admission_busy) {",p)
        self.assertIn("fm_context_quarantined,1,memory_order_release",p)

    def test_original_backend_sha_unchanged(self):
        self.assertEqual(r19.PINNED_ACOUSTIC_SHA256,
                         hashlib.sha256((ROOT/r26.ORIGINAL).read_bytes()).hexdigest())

    def test_r29_original_is_still_sha_pinned(self):
        table,_,_,_=r31.inspect(ROOT)
        self.assertEqual(hashlib.sha256((ROOT/r29.CANDIDATE).read_bytes()).hexdigest(),
                         table[r29.CANDIDATE])

    def test_r28_gate_still_unchanged(self):
        c=(ROOT/r28.CANDIDATE).read_text(encoding="utf-8")
        self.assertEqual(5,len(r28.observe(c)))

    def test_unresolved_r30_critical_findings_still_present(self):
        self.assertEqual(12,len(r30.observe(self.original)))
        self.assertEqual(2,sum(x[1]=="CRITICAL" for x in r30.FINDINGS))

    def test_manifest_has_169_exact_source_pins(self):
        table,_,_,_=r31.inspect(ROOT)
        self.assertEqual(169,len(table))

    def test_no_c31_in_runnable_link(self):
        self.assertIn("R31_REMEDIATION_CANDIDATE_OBJECT=COMPILED_UNLINKED",
                      self.runner)
        self.assertIn("R31_NONEMITTING_EXECUTABLE_SYMBOL_AUDIT=PASS",self.runner)

    def test_bureau_dossier_24_documents_sha256(self):
        self.assertIn("R31_BUREAU_PROOF_DOSSIER=24_FILES_SHA256_PASS",self.runner)

    def test_owner_mac_genuine_historical_R16_R30_evidence(self):
        archive=os.environ.get("FREQMED_GEN_R19_ARCHIVE_DIR")
        d=os.environ.get("FREQMED_GEN_R31_EVIDENCE_DIR")
        self.assertTrue(archive and d,
                        "R31 requires actual owner Mac R19 archive and R16-R30 report chain")
        stems=("OWNERSHIP_EVIDENCE","VERIFIED_EVIDENCE","CONTROL_FLOW_EVIDENCE",
               "ADVERSARIAL_EVIDENCE","BUREAU_VERIFICATION","BUREAU_GAPS",
               "COREAUDIO_REVIEW","PROOF_OBLIGATIONS","SHARED_STATE_CONTRACT",
               "REMEDIATION_REVIEW","PATCH_SAFETY_GATE","ADVERSARIAL_REVIEW",
               "QUEUE_ADMISSION_DESIGN","ADMISSION_INTEGRATION_REVIEW",
               "COREAUDIO_QUIESCENCE")
        paths={"r"+str(n):Path(d)/("GEN_R"+str(n)+"_"+s+".json")
               for n,s in zip(range(16,31),stems)}
        report=r31.audit(ROOT,Path(archive),paths)
        self.assertEqual(r31.VERDICT,report["verdict"])
        self.assertEqual(8,report["r31_findings_open"])
        self.assertEqual(12,report["r30_findings_open"])
        self.assertEqual(2,report["r30_critical_open"])
        self.assertEqual("NOT_PROVEN",report["physical_stop"])
        self.assertFalse(report["r31_emitting_linkage"])

    def test_mutated_stop_immediate_flag_rejected(self):
        self.reject("AudioQueueStop(ctx->queue,true)",
                    "AudioQueueStop(ctx->queue,false)")

    def test_mutated_stop_failure_condition_rejected(self):
        self.reject("if (r31_immediate_stop_status!=noErr)",
                    "if (r31_immediate_stop_status==noErr)")

    def test_mutated_stop_failure_quarantine_rejected(self):
        self.reject("fm_context_quarantined,1,memory_order_release",
                    "fm_context_quarantined,0,memory_order_release")

    def test_mutated_live_lease_guard_rejected(self):
        self.reject("if (r31_admission_busy) {",
                    "if (!r31_admission_busy) {")

    def test_mutated_immediate_stop_status_rejected(self):
        self.reject("const OSStatus r31_immediate_stop_status=AudioQueueStop",
                    "const OSStatus r31_immediate_stop_status=AudioQueuePause")

    def test_markdown_preserves_uncertainty_and_output_denial(self):
        report={"r31_findings":[{"id":f[0],"severity":f[1],
                  "bureau_role":f[2]} for f in r31.FINDINGS]}
        text=r31.markdown(report)
        self.assertIn("NOT_PROVEN",text)
        self.assertIn("stop success",text)
        self.assertIn("REAL_OUTPUT=NOT_AUTHORIZED",text)
