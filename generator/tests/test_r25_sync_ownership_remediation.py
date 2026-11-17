"""GEN-R25 independent non-emitting C11 remediation evidence tests.

Only static source/string and genuine report verifications; no callback
scheduling, simulated signals, generated scientific measurements or OS output.
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
import r23_happens_before_obligations as r23
import r24_shared_state_contract_audit as r24
import r25_sync_ownership_remediation as r25

OBLIGATIONS=("HB01","HB02","HB03","HB04","HB05",
             "Q01","Q02","Q03","Q04","Q05",
             "D01","D02","D03","D04","D05")

def base_context():
    return {
        "open_r24_findings":[{"id":x[0]} for x in r24.GAPS],
        "r23_source_obligations":[{"id":x+"_SOURCE"} for x in OBLIGATIONS],
    }

class R25C11OwnershipRemediation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root=ROOT
        cls.source=(ROOT/"src/acoustic_macos.c").read_text(encoding="utf-8")
        cls.source_hash=hashlib.sha256(cls.source.encode("utf-8")).hexdigest()
        cls.plans=r25.review_plans(cls.source,cls.source_hash,base_context())

    def test_nine_independent_remediation_proposals(self):
        self.assertEqual(9,len(self.plans))
        self.assertEqual(9,len(set(x["id"] for x in self.plans)))

    def test_all_proposals_have_no_applied_patch(self):
        self.assertTrue(all(x["code_patch_applied"] is False and
                            x["design_status"]=="PROPOSED_NOT_APPLIED"
                            for x in self.plans))

    def test_all_proofs_and_output_authorizations_stay_false(self):
        self.assertTrue(all(x["proof_discharged"] is False and
                            x["physical_output_authorized"] is False
                            for x in self.plans))

    def test_all_seven_r24_findings_have_reviewed_candidates(self):
        mapped={gap for x in self.plans for gap in x["r24_findings"]}
        self.assertEqual({x[0] for x in r24.GAPS},mapped)

    def test_all_fifteen_r23_obligations_are_mapped(self):
        mapped={ob for x in self.plans for ob in x["r23_obligations"]}
        self.assertEqual(set(OBLIGATIONS),mapped)

    def test_two_anchored_real_C_lines_per_proposal(self):
        lines=self.source.splitlines()
        for plan in self.plans:
            self.assertEqual(2,len(plan["source_anchors"]))
            for site in plan["source_anchors"]:
                self.assertEqual("src/acoustic_macos.c",site["path"])
                self.assertEqual(self.source_hash,site["sha256"])
                self.assertIn(site["source_text"],lines[site["line"]-1])

    def test_native_source_is_identical_to_r19_pin(self):
        self.assertEqual(r19.PINNED_ACOUSTIC_SHA256,self.source_hash)

    def test_each_proposal_has_specific_evidence_and_roles(self):
        for p in self.plans:
            self.assertGreater(len(p["proposal"]),120)
            self.assertGreater(len(p["independent_proof_required"]),120)
            self.assertTrue(set(p["reviewer_roles"]) <= {"B07","B09","B10"})
            self.assertIn(p["priority"],("P1","P2"))

    def test_pcm_single_writer_fix_cannot_be_claimed_applied(self):
        pcm=[x for x in self.plans if x["id"]=="RM01_PCM_SINGLE_WRITER"][0]
        self.assertEqual("P1",pcm["priority"])
        self.assertFalse(pcm["code_patch_applied"])
        self.assertIn("fill_audio(ctx,b);",self.source)
        self.assertIn("fill_audio(ctx,buf)",self.source)

    def test_userdata_counter_window_stays_open(self):
        item=[x for x in self.plans
              if x["id"]=="RM04_USERDATA_ADMISSION_BARRIER"][0]
        self.assertIn("SH03_ATOMIC_COUNTER_ENTRY_WINDOW",item["r24_findings"])
        self.assertFalse(item["proof_discharged"])

    def test_early_and_terminal_disposal_have_separate_remediations(self):
        names={x["id"] for x in self.plans}
        self.assertIn("RM07_EARLY_BIND_ERROR_OWNERSHIP",names)
        self.assertIn("RM08_FINAL_DISPOSE_ERROR_QUARANTINE",names)

    def test_seven_proposed_ownership_states_are_explicit(self):
        self.assertEqual(7,len(r25.STATES))
        self.assertIn("DISPOSAL_UNCERTAIN",r25.STATES)
        self.assertIn("QUARANTINED",r25.STATES)

    def test_nine_proposed_transitions_not_code_claims(self):
        steps=r25.validate_state_machine()
        self.assertEqual(9,len(steps))
        self.assertTrue(all(x["status"]=="PROPOSED_NOT_APPLIED"
                            for x in steps))

    def test_terminal_quarantine_cannot_reopen_session(self):
        self.assertNotIn("QUARANTINED",tuple(a for a,b in r25.TRANSITIONS))
        self.assertIn(("DISPOSAL_UNCERTAIN","QUARANTINED"),
                      r25.TRANSITIONS)

    def test_missing_C_source_anchor_fails_closed(self):
        modified=self.source.replace("fill_audio(ctx,b);",
                                     "/* controller prefill removed */",1)
        self.assertNotEqual(modified,self.source)
        with self.assertRaises(r25.R25Error):
            r25.review_plans(modified,self.source_hash,base_context())

    def test_missing_r24_finding_fails_closed(self):
        context=base_context()
        context["open_r24_findings"].pop()
        with self.assertRaises(r25.R25Error):
            r25.review_plans(self.source,self.source_hash,context)

    def test_missing_r23_proof_obligation_fails_closed(self):
        context=base_context()
        context["r23_source_obligations"].pop()
        with self.assertRaises(r25.R25Error):
            r25.review_plans(self.source,self.source_hash,context)

    def test_readonly_linker_and_133_pinned_files(self):
        table,digest,plans,steps=r25.inspect(ROOT)
        self.assertGreaterEqual(len(table),133)  # historical GEN-R25 baseline
        self.assertEqual(9,len(plans))
        self.assertEqual(9,len(steps))
        runner=(ROOT/"RUN_GEN_R25_MAC_INTEL.command").read_text(encoding="utf-8")
        self.assertEqual(r17.LINK_C_ALLOWLIST,
                         frozenset(r17.link_sources(runner)))

    def test_markdown_never_misrepresents_a_C11_proof(self):
        rendered=r25.markdown({"owner_proof_proposals":self.plans})
        self.assertIn("0 patch appliqué",rendered)
        self.assertIn("0 preuve acquittée",rendered)
        self.assertIn("NOT_AUTHORIZED",rendered)
        for p in self.plans:
            self.assertIn(p["id"],rendered)

    def test_real_owner_mac_R16_R24_chain_all_premises_open(self):
        work=os.environ.get("FREQMED_GEN_R25_EVIDENCE_DIR")
        old=os.environ.get("FREQMED_GEN_R19_ARCHIVE_DIR")
        if not work or not old:
            self.skipTest("genuine owner Mac Intel R16-R24 evidence chain required")
        directory=Path(work)
        base={key:directory/name for key,name in {
            "r16":"GEN_R16_OWNERSHIP_EVIDENCE.json",
            "r17":"GEN_R17_VERIFIED_EVIDENCE.json",
            "r18":"GEN_R18_CONTROL_FLOW_EVIDENCE.json",
            "r19":"GEN_R19_ADVERSARIAL_EVIDENCE.json",
            "r20":"GEN_R20_BUREAU_VERIFICATION.json",
        }.items()}
        result=r25.audit(ROOT,Path(old),base,
                         directory/"GEN_R21_BUREAU_GAPS.json",
                         directory/"GEN_R22_COREAUDIO_REVIEW.json",
                         directory/"GEN_R23_PROOF_OBLIGATIONS.json",
                         directory/"GEN_R24_SHARED_STATE_CONTRACT.json")
        self.assertEqual(r25.VERDICT,result["verdict"])
        self.assertEqual(9,result["proposal_count"])
        self.assertEqual(0,result["proposals_applied"])
        self.assertEqual(15,result["r23_open_proof_obligations"])
        self.assertEqual(7,result["r24_open_findings"])
        self.assertEqual(11,result["bureau_open_gates"])
        self.assertEqual("NONE",result["physical_emission"])
