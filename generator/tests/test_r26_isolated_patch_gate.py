"""GEN-R26 tests for byte-exact isolated native C patch, not a runtime OS test.

No real CoreAudio output, no simulated callbacks, no generated measurements.
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

class R26IsolatedNativePatchReview(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original=(ROOT/r26.ORIGINAL).read_text(encoding="utf-8")
        cls.candidate=(ROOT/r26.CANDIDATE).read_text(encoding="utf-8")
        cls.runner=(ROOT/"RUN_GEN_R26_MAC_INTEL.command").read_text(encoding="utf-8")

    def test_exact_three_source_edits(self):
        self.assertEqual(3,len(r26.PATCHES))
        self.assertEqual(self.candidate,r26.expected_candidate(self.original))

    def test_candidate_is_separate_from_original_C(self):
        self.assertNotEqual(self.original,self.candidate)
        self.assertTrue((ROOT/r26.CANDIDATE).is_file())

    def test_original_R19_pin_remains_unchanged(self):
        sha=hashlib.sha256(self.original.encode("utf-8")).hexdigest()
        self.assertEqual(r19.PINNED_ACOUSTIC_SHA256,sha)

    def test_manifest_has_139_pinned_sources(self):
        table,_,sha_candidate,sha_original=r26.inspect(ROOT)
        self.assertEqual(139,len(table))
        self.assertEqual(table[r26.ORIGINAL],sha_original)
        self.assertEqual(table[r26.CANDIDATE],sha_candidate)

    def test_all_source_changes_are_exactly_whitelisted(self):
        for ident,old,new in r26.PATCHES:
            self.assertEqual(1,self.original.count(old),ident)
            self.assertEqual(1,self.candidate.count(new),ident)

    def test_PCM_controller_acquires_common_gate(self):
        item=self.candidate.split("/* GEN-R26 isolated candidate: share",1)[1]
        self.assertIn("atomic_flag_test_and_set_explicit(&ctx->pcm_writer_gate",item)
        self.assertIn("memory_order_acquire",item)
        self.assertIn("fill_audio(ctx,b);",item)
        self.assertIn("atomic_flag_clear_explicit(&ctx->pcm_writer_gate,memory_order_release);",item)

    def test_callback_still_acquires_exact_same_gate(self):
        cb=self.candidate.split("static void output_callback(",1)[1].split(
            "static __attribute__((unused)) int acoustic_output_impl(",1)[0]
        self.assertIn("atomic_flag_test_and_set_explicit(&ctx->pcm_writer_gate",cb)
        self.assertIn("atomic_flag_clear_explicit(&ctx->pcm_writer_gate",cb)

    def test_controller_contention_fails_closed(self):
        self.assertIn("fm_latch_first_fault(ctx,FM_FAULT_OVERLAPPING_PCM_CALLBACK);",
                      self.candidate)
        self.assertIn("      err=1;\n      break;\n    }\n    fill_audio(ctx,b);",
                      self.candidate)

    def test_published_context_never_freed(self):
        self.assertEqual(2,self.candidate.count("free(owner_ctx);"))
        self.assertEqual(4,self.candidate.count(
            "atomic_flag_clear_explicit(&fm_session_claim,memory_order_release);"))

    def test_candidate_terminal_cleanup_quarantines_and_denies(self):
        self.assertIn("  (void)context_quiescent;\n"
                      "  atomic_store_explicit(&fm_context_quarantined,1,memory_order_release);\n"
                      "  err=1;\n  return -1;",self.candidate)

    def test_public_output_entry_unconditionally_denied(self):
        f=self.candidate.split("int fm_acoustic_physical_output(",1)[1]
        self.assertIn("(void)command;\n  return -1;",f)

    def test_no_active_coreaudio_executable_linkage(self):
        self.assertEqual(r17.LINK_C_ALLOWLIST,
                         frozenset(r17.link_sources(self.runner)))
        cmd=self.runner.split(' -o "$WORK/freqmed-gen"',1)[1].split(
            "-framework CoreAudio",1)[0]
        self.assertNotIn("acoustic_macos_r26.c",cmd)
        self.assertNotIn("acoustic_macos.c",cmd)
        self.assertIn("output_hard_denied.c",cmd)

    def test_native_candidate_compiled_isolated_only(self):
        self.assertIn('"$ROOT/candidates/acoustic_macos_r26.c"',self.runner)
        self.assertIn("R26_ISOLATED_CANDIDATE_OBJECT=COMPILED_UNLINKED",self.runner)
        self.assertIn("R26_NONEMITTING_EXECUTABLE_SYMBOL_AUDIT=PASS",self.runner)

    def test_missing_candidate_gate_rejected(self):
        mut=self.candidate.replace(
            "atomic_flag_test_and_set_explicit(&ctx->pcm_writer_gate",
            "atomic_flag_test_and_set_explicit(&ctx->unreviewed_gate",1)
        with self.assertRaises(r26.R26Error):
            self.assertEqual(mut,r26.expected_candidate(self.original))

    def test_unsafe_free_after_OS_publication_rejected(self):
        mut=self.candidate.replace(
            "  (void)context_quiescent;\n",
            "  free(owner_ctx);\n",1)
        with self.assertRaises(r26.R26Error):
            self.assertEqual(mut,r26.expected_candidate(self.original))

    def test_reopening_session_after_quarantine_rejected(self):
        mut=self.candidate.replace(
            "  err=1;\n  return -1;",
            "  err=0;\n  return 0;",1)
        with self.assertRaises(r26.R26Error):
            self.assertEqual(mut,r26.expected_candidate(self.original))

    def test_proposal_has_five_uncertified_risks(self):
        self.assertEqual(5,len(r26.RISKS))
        self.assertTrue(all(len(text)>70 for _,text in r26.RISKS))

    def test_no_formal_or_OS_evidence_assertion(self):
        rendered=r26.markdown({
            "candidate_patch_anchors":[{"id":x[0],"baseline_line":1}
                                       for x in r26.PATCHES],
            "unresolved_r26_risks":[{"id":r[0]} for r in r26.RISKS],
        })
        self.assertIn("zéro preuve C11 acquittée",rendered)
        self.assertIn("NOT_AUTHORIZED",rendered)
        self.assertIn("15 obligations R23 OPEN",rendered)

    def test_numerical_history_targets_unpromoted(self):
        self.assertEqual("ISOLATED_PATCH_REVIEW_REQUIRED_NO_EMISSION",r26.VERDICT)
        self.assertTrue(all("FM_FAULT" not in x[0] for x in r26.PATCHES))

    def test_genuine_owner_mac_R16_R25_evidence_chain(self):
        d=os.environ.get("FREQMED_GEN_R26_EVIDENCE_DIR")
        r19=os.environ.get("FREQMED_GEN_R19_ARCHIVE_DIR")
        if not d or not r19:
            self.skipTest("requires actual owner R16-R25 reports and R19 archive")
        path=Path(d)
        base={key:path/name for key,name in {
            "r16":"GEN_R16_OWNERSHIP_EVIDENCE.json",
            "r17":"GEN_R17_VERIFIED_EVIDENCE.json",
            "r18":"GEN_R18_CONTROL_FLOW_EVIDENCE.json",
            "r19":"GEN_R19_ADVERSARIAL_EVIDENCE.json",
            "r20":"GEN_R20_BUREAU_VERIFICATION.json",
        }.items()}
        result=r26.audit(ROOT,Path(r19),base,
                         path/"GEN_R21_BUREAU_GAPS.json",
                         path/"GEN_R22_COREAUDIO_REVIEW.json",
                         path/"GEN_R23_PROOF_OBLIGATIONS.json",
                         path/"GEN_R24_SHARED_STATE_CONTRACT.json",
                         path/"GEN_R25_REMEDIATION_REVIEW.json")
        self.assertEqual(r26.VERDICT,result["verdict"])
        self.assertEqual(3,result["isolated_native_candidate_patches"])
        self.assertFalse(result["applied_to_original_C"])
        self.assertEqual(11,result["bureau_gates_open"])
        self.assertEqual(0,result["bureau_gates_resolved"])
        self.assertEqual("NONE",result["physical_emission"])
