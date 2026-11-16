"""GEN-R37 static callback lease source gates; NO callback execution/simulation."""
import hashlib
import os
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"audits"))
import r19_adversarial_source_audit as r19
import r26_isolated_patch_gate as r26
import r31_critical_shutdown_review as r31
import r36_static_anchor_proof_gate as r36
import r37_adapter_ownership_proof_review as r37

class R37AdapterOwnershipProofReview(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.adapter=(ROOT/r37.CANDIDATE).read_text(encoding="utf-8")
        cls.anchor=(ROOT/r36.CANDIDATE).read_text(encoding="utf-8")
        cls.baseline=(ROOT/r31.CANDIDATE).read_text(encoding="utf-8")
        cls.runner=(ROOT/"RUN_GEN_R37_MAC_INTEL.command").read_text(encoding="utf-8")

    def reject(self,old,new):
        self.assertIn(old,self.adapter)
        altered=self.adapter.replace(old,new,1)
        with self.assertRaises(r37.R37Error):
            r37.observe(altered,self.anchor,self.baseline)

    def test_fourteen_unproven_integration_findings(self):
        self.assertEqual({"OPEN_NOT_PROVEN"},
           set(r37.observe(self.adapter,self.anchor,self.baseline).values()))
        self.assertEqual(14,len(r37.FINDINGS))

    def test_four_critical_obligations(self):
        self.assertEqual(4,sum(f[1]=="CRITICAL" for f in r37.FINDINGS))

    def test_six_documentary_lease_contracts(self):
        self.assertEqual(6,len(r37.CONTRACTS))
        self.assertEqual(6,len({x[0] for x in r37.CONTRACTS}))

    def test_no_audioqueue_or_heap_output_calls(self):
        for forbidden in ("#include <AudioToolbox","AudioQueueStop(",
                          "AudioQueueNewOutput(","AudioQueueDispose(",
                          "malloc(","calloc(","free("):
            self.assertNotIn(forbidden,self.adapter)

    def test_separate_output_and_property_entry(self):
        for name in ("fm37_output_enter","fm37_property_enter"):
            self.assertIn("return fm37_begin(os_userdata,lease);",
                          r37.function(self.adapter,name))

    def test_gate_before_owner_publication(self):
        f=r37.function(self.adapter,"fm37_begin")
        self.assertLess(f.index("fm36_try_enter(os_userdata,&owner)"),
                        f.index("lease->owner=owner;"))

    def test_owner_access_only_after_admission(self):
        f=r37.function(self.adapter,"fm37_lease_owner")
        self.assertLess(f.index("lease->phase!=FM37_LEASE_ACTIVE"),
                        f.index("return lease->owner;"))

    def test_local_exit_refuses_sequential_double_release(self):
        f=r37.function(self.adapter,"fm37_finish")
        self.assertIn("lease->phase!=FM37_LEASE_ACTIVE",f)
        self.assertIn("lease->phase=FM37_LEASE_FINISHED;",f)

    def test_local_exit_invalidates_access_before_leave(self):
        f=r37.function(self.adapter,"fm37_finish")
        self.assertLess(f.index("lease->owner=NULL;"),
                        f.index("return fm36_leave(token);"))

    def test_prepare_claims_anchor_before_exposure(self):
        f=r37.function(self.adapter,"fm37_prepare_token")
        self.assertLess(f.index("fm36_prepare_once(owner,os_userdata_out)"),
                        f.index("fm36_mark_exposed(*os_userdata_out)"))

    def test_r31_real_callbacks_still_unintegrated(self):
        self.assertIn("AudioQueueNewOutput(&fmt,output_callback,ctx",
                      self.baseline)
        self.assertNotIn("fm37_",self.baseline)

    def test_old_original_C_still_r19_pinned(self):
        digest=hashlib.sha256((ROOT/r26.ORIGINAL).read_bytes()).hexdigest()
        self.assertEqual(r19.PINNED_ACOUSTIC_SHA256,digest)

    def test_exact_207_pinned_files_and_C36_unchanged(self):
        table,_,_,_=r37.inspect(ROOT)
        self.assertEqual(207,len(table))
        for candidate in (r37.CANDIDATE,r36.CANDIDATE,r31.CANDIDATE):
            self.assertEqual(table[candidate],
                hashlib.sha256((ROOT/candidate).read_bytes()).hexdigest())

    def test_runner_keeps_both_candidates_unlinked(self):
        self.assertIn("R37_CALLBACK_LEASE_OBJECT=COMPILED_UNLINKED",self.runner)
        self.assertIn("R37_STABLE_ANCHOR_OBJECT=COMPILED_UNLINKED",self.runner)
        self.assertIn("R37_NONEMITTING_EXECUTABLE_SYMBOL_AUDIT=PASS",self.runner)
        self.assertIn("R37_BUREAU_PROOF_DOSSIER=36_FILES_SHA256_PASS",self.runner)

    def test_actual_owner_r16_to_r36_history(self):
        archive=os.environ.get("FREQMED_GEN_R19_ARCHIVE_DIR")
        root=os.environ.get("FREQMED_GEN_R37_EVIDENCE_DIR")
        self.assertTrue(archive and root,
                "R37 requires real owner Mac R19 archive and R16-R36 reports")
        stems=("OWNERSHIP_EVIDENCE","VERIFIED_EVIDENCE",
               "CONTROL_FLOW_EVIDENCE","ADVERSARIAL_EVIDENCE",
               "BUREAU_VERIFICATION","BUREAU_GAPS","COREAUDIO_REVIEW",
               "PROOF_OBLIGATIONS","SHARED_STATE_CONTRACT",
               "REMEDIATION_REVIEW","PATCH_SAFETY_GATE",
               "ADVERSARIAL_REVIEW","QUEUE_ADMISSION_DESIGN",
               "ADMISSION_INTEGRATION_REVIEW","COREAUDIO_QUIESCENCE",
               "CRITICAL_SHUTDOWN","FAILED_STOP_OWNERSHIP",
               "FAILURE_STATE_OWNERSHIP","USERDATA_LIFETIME",
               "PRE_ADMISSION_OS_CONTRACT","STATIC_ANCHOR_PROOF")
        reports={"r"+str(n):Path(root)/("GEN_R"+str(n)+"_"+stem+".json")
                 for n,stem in zip(range(16,37),stems)}
        output=r37.audit(ROOT,Path(archive),reports)
        self.assertEqual(r37.VERDICT,output["verdict"])
        self.assertEqual(14,output["r37_findings_open"])
        self.assertEqual(11,output["bureau_gates_open"])
        self.assertFalse(output["r37_candidate_integrated"])

    def test_mutation_removes_required_gate_rejected(self):
        self.reject("if (fm36_try_enter(os_userdata,&owner)!=0) return -1;",
                    "if (owner!=NULL) return -1;")

    def test_mutation_corrupts_owner_storage_rejected(self):
        self.reject("lease->owner=owner;","lease->owner=NULL;")

    def test_mutation_reopens_finished_lease_rejected(self):
        self.reject("lease->phase=FM37_LEASE_FINISHED;",
                    "lease->phase=FM37_LEASE_UNUSED;")

    def test_mutation_drops_decrement_rejected(self):
        self.reject("return fm36_leave(token);","return 0;")

    def test_mutation_inserts_unsafe_heap_release_rejected(self):
        self.reject("lease->owner=NULL;","free(lease->owner); lease->owner=NULL;")
