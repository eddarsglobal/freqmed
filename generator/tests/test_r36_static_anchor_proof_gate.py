"""GEN-R36 stable userdata anchor static proof gates.
All mutations modify source strings only; NO simulation or OS execution.
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
import r31_critical_shutdown_review as r31
import r35_pre_admission_os_contract_review as r35
import r36_static_anchor_proof_gate as r36

class R36StaticAnchorProofGate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.candidate=(ROOT/r36.CANDIDATE).read_text(encoding="utf-8")
        cls.baseline=(ROOT/r31.CANDIDATE).read_text(encoding="utf-8")
        cls.runner=(ROOT/"RUN_GEN_R36_MAC_INTEL.command").read_text(encoding="utf-8")

    def reject(self,old,new):
        self.assertIn(old,self.candidate)
        with self.assertRaises(r36.R36Error):
            r36.observe(self.candidate.replace(old,new,1),self.baseline)

    def test_twelve_open_findings(self):
        findings=r36.observe(self.candidate,self.baseline)
        self.assertEqual(12,len(findings))
        self.assertEqual({"OPEN_NOT_PROVEN"},set(findings.values()))

    def test_four_critical_findings(self):
        self.assertEqual(4,sum(f[1]=="CRITICAL" for f in r36.FINDINGS))

    def test_no_real_coreaudio_bindings_in_candidate(self):
        for bad in ("#include <AudioToolbox","AudioQueueStart(",
                    "AudioQueueDispose(","AudioQueueNewOutput(",
                    "AudioQueueStop(","AudioDeviceStart("):
            self.assertNotIn(bad,self.candidate)

    def test_process_lifetime_singleton_only(self):
        self.assertEqual(1,self.candidate.count(
            "static FM36StableAnchor fm36_anchor = {"))
        self.assertEqual(1,self.candidate.count(
            "static atomic_flag fm36_one_shot_claim"))

    def test_irrevocable_one_shot_claim(self):
        self.assertIn("atomic_flag_test_and_set_explicit(",self.candidate)
        self.assertNotIn("atomic_flag_clear",self.candidate)

    def test_no_candidate_heap_reclamation(self):
        for forbidden in ("free(","malloc(","calloc(","realloc("):
            self.assertNotIn(forbidden,self.candidate)

    def test_anchor_return_is_static_not_owner(self):
        self.assertIn("*userdata_out=(void *)&fm36_anchor;",self.candidate)
        self.assertNotIn("*userdata_out=owner",self.candidate)

    def test_expose_must_follow_prepare_cas(self):
        _,_,body=r36.function_bounds(self.candidate,"fm36_mark_exposed")
        self.assertIn("unsigned expected=FM36_PREPARED;",body)
        self.assertIn("&fm36_anchor.phase,&expected,FM36_EXPOSED",body)

    def test_enter_token_checked_before_owner_load(self):
        _,_,body=r36.function_bounds(self.candidate,"fm36_try_enter")
        self.assertLess(body.index("userdata!=(void *)&fm36_anchor"),
                        body.index("atomic_load_explicit(&fm36_anchor.owner,"))

    def test_enter_phase_double_check(self):
        _,_,body=r36.function_bounds(self.candidate,"fm36_try_enter")
        self.assertEqual(2,body.count("!=FM36_EXPOSED"))

    def test_seal_is_one_way_and_never_frees(self):
        _,_,body=r36.function_bounds(self.candidate,"fm36_seal")
        self.assertIn("&fm36_anchor.phase,&seen,FM36_SEALED",body)
        self.assertNotIn("free(",body)

    def test_leave_counter_cas_prevents_underflow(self):
        _,_,body=r36.function_bounds(self.candidate,"fm36_leave")
        self.assertIn("while (seen>0u)",body)
        self.assertIn("&fm36_anchor.admitted,&seen,seen-1u",body)

    def test_real_r31_callbacks_still_unintegrated(self):
        self.assertIn("AudioQueueNewOutput(&fmt,output_callback,ctx",self.baseline)
        self.assertNotIn("fm36_try_enter",self.baseline)

    def test_original_and_candidate_manifest_pins(self):
        table,_,_,_=r36.inspect(ROOT)
        self.assertEqual(200,len(table))
        for name in (r36.CANDIDATE,r31.CANDIDATE):
            self.assertEqual(table[name],
                             hashlib.sha256((ROOT/name).read_bytes()).hexdigest())
        self.assertEqual(r19.PINNED_ACOUSTIC_SHA256,
            hashlib.sha256((ROOT/r26.ORIGINAL).read_bytes()).hexdigest())

    def test_runner_unlinked_and_34_reports(self):
        self.assertIn("R36_STABLE_ANCHOR_OBJECT=COMPILED_UNLINKED",self.runner)
        self.assertIn("R36_NONEMITTING_EXECUTABLE_SYMBOL_AUDIT=PASS",self.runner)
        self.assertIn("R36_BUREAU_PROOF_DOSSIER=34_FILES_SHA256_PASS",self.runner)

    def test_mutation_claim_removed_rejected(self):
        self.reject("atomic_flag_test_and_set_explicit(",
                    "atomic_flag_test_and_clear_explicit(")

    def test_mutation_owner_early_read_rejected(self):
        self.reject("*owner_out=NULL;","*owner_out=owner;")

    def test_mutation_seal_reopening_rejected(self):
        self.reject("&fm36_anchor.phase,&seen,FM36_SEALED",
                    "&fm36_anchor.phase,&seen,FM36_EXPOSED")

    def test_mutation_heap_free_rejected(self):
        self.reject("return 0;\n}\n\n/* Irreversible seal;",
                    "free(owner); return 0;\n}\n\n/* Irreversible seal;")

    def test_actual_owner_r16_to_r35_evidence_chain(self):
        archive=os.environ.get("FREQMED_GEN_R19_ARCHIVE_DIR")
        folder=os.environ.get("FREQMED_GEN_R36_EVIDENCE_DIR")
        self.assertTrue(archive and folder,"authentic owner Mac evidence required")
        stems=("OWNERSHIP_EVIDENCE","VERIFIED_EVIDENCE",
               "CONTROL_FLOW_EVIDENCE","ADVERSARIAL_EVIDENCE",
               "BUREAU_VERIFICATION","BUREAU_GAPS","COREAUDIO_REVIEW",
               "PROOF_OBLIGATIONS","SHARED_STATE_CONTRACT",
               "REMEDIATION_REVIEW","PATCH_SAFETY_GATE",
               "ADVERSARIAL_REVIEW","QUEUE_ADMISSION_DESIGN",
               "ADMISSION_INTEGRATION_REVIEW","COREAUDIO_QUIESCENCE",
               "CRITICAL_SHUTDOWN","FAILED_STOP_OWNERSHIP",
               "FAILURE_STATE_OWNERSHIP","USERDATA_LIFETIME",
               "PRE_ADMISSION_OS_CONTRACT")
        paths={"r"+str(n):Path(folder)/("GEN_R"+str(n)+"_"+stem+".json")
               for n,stem in zip(range(16,36),stems)}
        data=r36.audit(ROOT,Path(archive),paths)
        self.assertEqual(12,data["r36_findings_open"])
        self.assertEqual(4,data["r36_critical_open"])
        self.assertFalse(data["r36_candidate_integrated"])
        self.assertEqual(11,data["bureau_gates_open"])

