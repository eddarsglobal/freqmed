"""GEN-R28 static C11 admission design regressions; no callbacks, no output."""
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

class R28QueueAdmissionDesign(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.code=(ROOT/r28.CANDIDATE).read_text(encoding="utf-8")
        cls.runner=(ROOT/"RUN_GEN_R28_MAC_INTEL.command").read_text(encoding="utf-8")
    def reject(self,old,new):
        self.assertIn(old,self.code)
        with self.assertRaises(r28.R28Error):
            r28.observe(self.code.replace(old,new,1))
    def test_design_gates_five_open(self):
        self.assertEqual(5,len(r28.GATES))
        self.assertEqual(5,len(set(x[0] for x in r28.GATES)))
        self.assertEqual({"OPEN_NOT_PROVEN"},set(r28.observe(self.code).values()))
    def test_r28_source_header(self):
        self.assertTrue(self.code.startswith("/* SPDX-License-Identifier: Apache-2.0 */"))
    def test_one_shot_cas_not_spin(self):
        self.assertIn("atomic_compare_exchange_strong_explicit(",self.code)
        self.assertNotIn("while (",self.code)
    def test_close_irreversible_bit(self):
        self.assertIn("atomic_fetch_or_explicit(",self.code)
        self.assertNotIn("fm_r28_gate_reopen",self.code)
    def test_closed_and_empty_requires_both(self):
        self.assertIn("(state & FM_R28_CLOSED)!=0 && (state & FM_R28_COUNT_MASK)==0;",self.code)
    def test_release_precondition_explicit(self):
        self.assertIn("Strict PRECONDITION: exactly one leave",self.code)
    def test_c_no_coreaudio_execution_api(self):
        r28.observe(self.code)
        self.assertNotIn("#include <AudioToolbox",self.code)
    def test_original_r19_unchanged(self):
        old=(ROOT/r26.ORIGINAL).read_bytes()
        self.assertEqual(r19.PINNED_ACOUSTIC_SHA256,hashlib.sha256(old).hexdigest())
    def test_r26_candidate_unchanged(self):
        original=(ROOT/r26.ORIGINAL).read_text(encoding="utf-8")
        candidate=(ROOT/r26.CANDIDATE).read_text(encoding="utf-8")
        self.assertEqual(candidate,r26.expected_candidate(original))
    def test_manifest_150_sources(self):
        table,_,_,_=r28.inspect(ROOT)
        self.assertGreaterEqual(len(table),150)
    def test_nonemitting_r28_runner(self):
        self.assertIn("R28_NONEMITTING_EXECUTABLE_SYMBOL_AUDIT=PASS",self.runner)
        self.assertIn("R28_ADMISSION_DESIGN_OBJECT=COMPILED_UNLINKED",self.runner)
    def test_dossier_18(self):
        self.assertIn("R28_BUREAU_DESIGN_DOSSIER=18_FILES_SHA256_PASS",self.runner)
    def test_genuine_owner_mac_R16_R27_evidence_chain(self):
        archive=os.environ.get("FREQMED_GEN_R19_ARCHIVE_DIR")
        directory=os.environ.get("FREQMED_GEN_R28_EVIDENCE_DIR")
        if not archive or not directory:
            self.skipTest("owner Mac archival reports are required")
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
               "GEN_R27_ADVERSARIAL_REVIEW.json")
        reports={f"r{k}":d/name for k,name in zip(range(16,28),names)}
        result=r28.audit(ROOT,Path(archive),reports)
        self.assertEqual(r28.VERDICT,result["verdict"])
        self.assertEqual(5,result["r28_gates_open"])
        self.assertEqual(11,result["bureau_gates_open"])
        self.assertFalse(result["r28_applied_to_original_C"])
    def test_mutated_close_gate_rejected(self):
        self.reject("atomic_fetch_or_explicit(","atomic_exchange_explicit(")
    def test_mutated_entry_cas_rejected(self):
        self.reject("atomic_compare_exchange_strong_explicit(",
                    "atomic_compare_exchange_weak_explicit(")
    def test_mutated_entry_memory_order_rejected(self):
        self.reject("memory_order_acq_rel,memory_order_acquire);",
                    "memory_order_relaxed,memory_order_relaxed);")
    def test_mutated_release_rejected(self):
        self.reject("atomic_fetch_sub_explicit(","atomic_fetch_add_explicit(")
    def test_mutated_quiescence_rejected(self):
        self.reject("(state & FM_R28_CLOSED)!=0 && (state & FM_R28_COUNT_MASK)==0;",
                    "(state & FM_R28_COUNT_MASK)==0;")
    def test_mutated_counter_mask_rejected(self):
        self.reject("FM_R28_COUNT_MASK (FM_R28_CLOSED - (uint_fast64_t)1)",
                    "FM_R28_COUNT_MASK (FM_R28_CLOSED)")
    def test_markdown_explicitly_uncertified(self):
        m=r28.markdown({"r28_design_gates":[
            {"id":x[0],"bureau_role":x[1],"status":"OPEN_NOT_PROVEN"}
            for x in r28.GATES]})
        self.assertIn("NOT sufficient",m)
        self.assertIn("REAL_OUTPUT=NOT_AUTHORIZED",m)
