"""GEN-R27 source-only adversarial regressions; NO CoreAudio execution.

Text mutations check reviewer fail-closed recognition of changed C source;
they are not thread interleaving or scientific simulations.
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
import r26_isolated_patch_gate as r26
import r27_adversarial_ownership_review as r27

class R27AdversarialOwnershipReview(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original=(ROOT/r27.SOURCE).read_text(encoding="utf-8")
        cls.candidate=(ROOT/r27.CANDIDATE).read_text(encoding="utf-8")
        cls.candidate_sha=hashlib.sha256(cls.candidate.encode("utf-8")).hexdigest()
        cls.checks=r27.observe(cls.candidate)

    def reject_mutation(self,needle,replacement):
        self.assertIn(needle,self.candidate)
        altered=self.candidate.replace(needle,replacement,1)
        self.assertNotEqual(altered,self.candidate)
        with self.assertRaises((r27.R27Error,ValueError)):
            r27.observe(altered)

    def test_nine_distinct_adversarial_findings(self):
        self.assertEqual(9,len(r27.FINDINGS))
        self.assertEqual(9,len({item[0] for item in r27.FINDINGS}))

    def test_five_original_r26_risk_categories_mapped(self):
        self.assertEqual(set(r27.CATEGORIES),
                         {f[2] for f in r27.FINDINGS})

    def test_finding_severities_and_bureau_roles(self):
        self.assertTrue(all(x[1] in ("HIGH","MEDIUM") and
                            x[3] in ("B07","B09","B10") for x in r27.FINDINGS))
        self.assertEqual(8,sum(x[1]=="HIGH" for x in r27.FINDINGS))

    def test_eighteen_anchors_match_real_candidate_C_lines(self):
        for _,_,_,_,a,b,_ in r27.FINDINGS:
            for function,needle in (a,b):
                ref=r27.anchor(self.candidate,self.candidate_sha,
                               function,needle)
                self.assertEqual(self.candidate_sha,ref["source_sha256"])
                self.assertEqual(r27.CANDIDATE,ref["path"])
                self.assertIn(needle,self.candidate.splitlines()[ref["line"]-1])

    def test_original_R19_C_source_unchanged(self):
        digest=hashlib.sha256(self.original.encode("utf-8")).hexdigest()
        self.assertEqual(r19.PINNED_ACOUSTIC_SHA256,digest)

    def test_candidate_exact_three_isolated_C_edits(self):
        self.assertEqual(3,len(r26.PATCHES))
        self.assertEqual(self.candidate,r26.expected_candidate(self.original))

    def test_manifest_144_source_file_scope(self):
        table,_,observed,candidate_sha=r27.inspect(ROOT)
        self.assertGreaterEqual(len(table),144)
        self.assertEqual(9,len(observed))
        self.assertEqual(candidate_sha,table[r27.CANDIDATE])

    def test_linker_allowlist_is_hard_denied(self):
        run=(ROOT/"RUN_GEN_R27_MAC_INTEL.command").read_text(encoding="utf-8")
        self.assertEqual(r17.LINK_C_ALLOWLIST,
                         frozenset(r17.link_sources(run)))
        self.assertIn("R27_NONEMITTING_EXECUTABLE_SYMBOL_AUDIT=PASS",run)

    def test_isolated_candidate_compiled_but_never_linked(self):
        run=(ROOT/"RUN_GEN_R27_MAC_INTEL.command").read_text(encoding="utf-8")
        self.assertIn('"$ROOT/candidates/acoustic_macos_r26.c"',run)
        self.assertIn("R27_ISOLATED_CANDIDATE_OBJECT=COMPILED_UNLINKED",run)
        cmd=run.split(' -o "$WORK/freqmed-gen"',1)[1].split("-framework CoreAudio",1)[0]
        self.assertNotIn("acoustic_macos_r26.c",cmd)
        self.assertIn("output_hard_denied.c",cmd)

    def test_sixteen_private_reports_checksum_guard(self):
        run=(ROOT/"RUN_GEN_R27_MAC_INTEL.command").read_text(encoding="utf-8")
        self.assertIn("R27_BUREAU_ADVERSARIAL_DOSSIER=16_FILES_SHA256_PASS",run)
        self.assertIn("GEN_R27_ADVERSARIAL_REVIEW.json",run)
        self.assertIn("GEN_R27_ADVERSARIAL_REVIEW.md",run)

    def test_C11_queue_pointer_race_is_not_claimed_fixed(self):
        self.assertIn("AD03_NONATOMIC_QUEUE_NULL_VS_CALLBACK",self.checks)
        self.assertTrue(self.checks["AD03_NONATOMIC_QUEUE_NULL_VS_CALLBACK"])
        self.assertFalse(any("PROVEN" in item[0] for item in r27.FINDINGS))

    def test_no_race_reproduced_or_C11_proof_claimed(self):
        text=r27.markdown({
           "adversarial_findings":[
             {"id":f[0],"priority":f[1],"anchors":[
                 {"path":r27.CANDIDATE,"line":1},
                 {"path":r27.CANDIDATE,"line":2}]} for f in r27.FINDINGS]
        })
        self.assertIn("no reproduced race",text)
        self.assertIn("NOT_AUTHORIZED",text)

    def test_mutated_pcm_enqueue_call_fails_closed(self):
        self.reject_mutation("AudioQueueEnqueueBuffer(ctx->queue,buf,0,NULL)",
                             "AudioQueueEnqueueBuffer(NULL,buf,0,NULL)")

    def test_mutated_controller_gate_fails_closed(self):
        self.reject_mutation(
            "atomic_flag_test_and_set_explicit(&ctx->pcm_writer_gate,",
            "atomic_flag_test_and_set_explicit(&ctx->not_a_shared_gate,")

    def test_mutated_final_queue_clear_fails_closed(self):
        self.reject_mutation("ctx->queue=NULL;","ctx->queue=(AudioQueueRef)0;")

    def test_mutated_listener_entry_counter_fails_closed(self):
        self.reject_mutation(
            "atomic_fetch_add_explicit(&ctx->active_property_listeners",
            "atomic_fetch_add_explicit(&ctx->unrelated_listener_count")

    def test_mutated_callback_entry_counter_fails_closed(self):
        self.reject_mutation(
            "atomic_fetch_add_explicit(&ctx->active_output_callbacks",
            "atomic_fetch_add_explicit(&ctx->unrelated_callback_count")

    def test_mutated_early_disposal_branch_fails_closed(self):
        self.reject_mutation("if (bind_dispose_status==noErr)",
                             "if (bind_dispose_status!=noErr)")

    def test_mutated_final_disposal_branch_fails_closed(self):
        self.reject_mutation("if (AudioQueueDispose(ctx->queue,true)!=noErr)",
                             "if (AudioQueueDispose(ctx->queue,true)==noErr)")

    def test_genuine_owner_mac_R16_R26_evidence_chain(self):
        directory=os.environ.get("FREQMED_GEN_R27_EVIDENCE_DIR")
        archive=os.environ.get("FREQMED_GEN_R19_ARCHIVE_DIR")
        if not directory or not archive:
            self.skipTest("actual Mac Intel R16-R26 report chain required")
        d=Path(directory)
        historical={x:d/name for x,name in {
            "r16":"GEN_R16_OWNERSHIP_EVIDENCE.json",
            "r17":"GEN_R17_VERIFIED_EVIDENCE.json",
            "r18":"GEN_R18_CONTROL_FLOW_EVIDENCE.json",
            "r19":"GEN_R19_ADVERSARIAL_EVIDENCE.json",
            "r20":"GEN_R20_BUREAU_VERIFICATION.json",
        }.items()}
        result=r27.audit(ROOT,Path(archive),historical,
                         d/"GEN_R21_BUREAU_GAPS.json",
                         d/"GEN_R22_COREAUDIO_REVIEW.json",
                         d/"GEN_R23_PROOF_OBLIGATIONS.json",
                         d/"GEN_R24_SHARED_STATE_CONTRACT.json",
                         d/"GEN_R25_REMEDIATION_REVIEW.json",
                         d/"GEN_R26_PATCH_SAFETY_GATE.json")
        self.assertEqual(r27.VERDICT,result["verdict"])
        self.assertEqual(9,result["r27_open_findings"])
        self.assertEqual(0,result["r27_proven_races"])
        self.assertEqual(15,result["r23_obligations_open"])
        self.assertEqual(7,result["r24_findings_open"])
        self.assertEqual(11,result["bureau_gates_open"])
        self.assertEqual(0,result["bureau_gates_resolved"])
        self.assertEqual("NONE",result["physical_emission"])
