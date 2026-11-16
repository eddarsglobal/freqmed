"""GEN-R34 source-only userdata lifetime and OS ownership regression tests.
No native callback/OS calls, no simulation and no physical emission.
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
import r33_failure_state_ownership_contract as r33
import r34_userdata_lifetime_review as r34

class R34UserdataLifetimeReview(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=(ROOT/r31.CANDIDATE).read_text(encoding="utf-8")
        cls.runner=(ROOT/"RUN_GEN_R34_MAC_INTEL.command").read_text(encoding="utf-8")

    def reject(self,before,after):
        self.assertIn(before,self.source)
        altered=self.source.replace(before,after,1)
        with self.assertRaises(r34.R34Error):
            r34.observe(altered)

    def test_fourteen_obligations_all_open(self):
        results=r34.observe(self.source)
        self.assertEqual(14,len(results))
        self.assertEqual({"OPEN_NOT_PROVEN"},set(results.values()))

    def test_four_critical_obligations_not_certified(self):
        names={f[0] for f in r34.FINDINGS if f[1]=="CRITICAL"}
        self.assertEqual({
          "UD34_01_CALLBACK_USERDATA_BEFORE_GATE",
          "UD34_02_LISTENER_USERDATA_BEFORE_GATE",
          "UD34_03_FAILED_STOP_PHYSICAL_ACTIVITY",
          "UD34_04_FAILED_DISPOSE_RESOURCE_OWNERSHIP"},names)

    def test_eleven_documentary_phases_not_runtime_states(self):
        self.assertEqual(11,len(r34.PHASES))
        self.assertEqual(11,len({p[0] for p in r34.PHASES}))

    def test_callback_has_ctx_before_gate(self):
        s=r29.function(self.source,"callback")
        self.assertLess(s.index("AcousticContext *ctx=(AcousticContext*)ptr;"),
                        s.index("if (!fm_r28_gate_try_enter(&ctx->queue_admission))"))

    def test_listener_has_ctx_before_gate(self):
        s=r29.function(self.source,"listener")
        self.assertLess(s.index("AcousticContext *ctx=(AcousticContext*)data;"),
                        s.index("if (!fm_r28_gate_try_enter(&ctx->queue_admission))"))

    def test_active_counters_increment_only_after_admission(self):
        for section in ("callback","listener"):
            s=r29.function(self.source,section)
            self.assertLess(s.index("fm_r28_gate_try_enter(&ctx->queue_admission)"),
                            s.index("atomic_fetch_add_explicit(&ctx->active_"))

    def test_only_two_prepublication_heap_release_sites(self):
        controller=r29.function(self.source,"controller")
        publish=controller.index("AudioQueueNewOutput(&fmt,output_callback,ctx")
        self.assertEqual(2,controller[:publish].count("free(owner_ctx);"))
        self.assertEqual(0,controller[publish:].count("free(owner_ctx);"))

    def test_error_dispose_does_not_make_free_safe(self):
        report=r34.observe(self.source)
        self.assertEqual("OPEN_NOT_PROVEN",
                         report["UD34_04_FAILED_DISPOSE_RESOURCE_OWNERSHIP"])

    def test_no_output_backend_changes(self):
        actual=hashlib.sha256((ROOT/r26.ORIGINAL).read_bytes()).hexdigest()
        self.assertEqual(r19.PINNED_ACOUSTIC_SHA256,actual)

    def test_candidate_sha_pinned_without_edits(self):
        table,_,_,_=r34.inspect(ROOT)
        actual=hashlib.sha256((ROOT/r31.CANDIDATE).read_bytes()).hexdigest()
        self.assertEqual(table[r31.CANDIDATE],actual)

    def test_c11_admission_contract_not_modified(self):
        source=(ROOT/r28.CANDIDATE).read_text(encoding="utf-8")
        self.assertEqual(5,len(r28.observe(source)))

    def test_187_source_files_sha_pinned(self):
        table,_,_,_=r34.inspect(ROOT)
        self.assertEqual(187,len(table))

    def test_runner_keeps_candidate_unlinked(self):
        self.assertIn("R34_R31_CANDIDATE_OBJECT=COMPILED_UNLINKED",self.runner)
        self.assertIn("R34_NONEMITTING_EXECUTABLE_SYMBOL_AUDIT=PASS",self.runner)
        self.assertIn("R34_BUREAU_PROOF_DOSSIER=30_FILES_SHA256_PASS",self.runner)

    def test_actual_owner_r16_r33_provenance(self):
        archive=os.environ.get("FREQMED_GEN_R19_ARCHIVE_DIR")
        folder=os.environ.get("FREQMED_GEN_R34_EVIDENCE_DIR")
        self.assertTrue(archive and folder,
                        "R34 authentic R19 archive and R16-R33 reports required")
        stems=("OWNERSHIP_EVIDENCE","VERIFIED_EVIDENCE",
               "CONTROL_FLOW_EVIDENCE","ADVERSARIAL_EVIDENCE",
               "BUREAU_VERIFICATION","BUREAU_GAPS","COREAUDIO_REVIEW",
               "PROOF_OBLIGATIONS","SHARED_STATE_CONTRACT",
               "REMEDIATION_REVIEW","PATCH_SAFETY_GATE",
               "ADVERSARIAL_REVIEW","QUEUE_ADMISSION_DESIGN",
               "ADMISSION_INTEGRATION_REVIEW","COREAUDIO_QUIESCENCE",
               "CRITICAL_SHUTDOWN","FAILED_STOP_OWNERSHIP",
               "FAILURE_STATE_OWNERSHIP")
        folder=Path(folder)
        paths={"r"+str(n):folder/("GEN_R"+str(n)+"_"+stem+".json")
               for n,stem in zip(range(16,34),stems)}
        result=r34.audit(ROOT,Path(archive),paths)
        self.assertEqual(r34.VERDICT,result["verdict"])
        self.assertEqual(14,result["r34_findings_open"])
        self.assertEqual(4,result["r34_critical_open"])
        self.assertEqual(11,result["r34_documentary_phases"])
        self.assertEqual(11,result["bureau_gates_open"])
        self.assertFalse(result["r34_active_coreaudio"])

    def test_mutated_output_callback_gate_rejected(self):
        self.reject("if (!fm_r28_gate_try_enter(&ctx->queue_admission)) return;\n  (void)atomic_fetch_add_explicit(&ctx->active_output_callbacks",
                    "if (fm_r28_gate_try_enter(&ctx->queue_admission)) return;\n  (void)atomic_fetch_add_explicit(&ctx->active_output_callbacks")

    def test_mutated_listener_gate_rejected(self):
        self.reject("if (!fm_r28_gate_try_enter(&ctx->queue_admission)) return;\n  (void)atomic_fetch_add_explicit(&ctx->active_property_listeners",
                    "if (fm_r28_gate_try_enter(&ctx->queue_admission)) return;\n  (void)atomic_fetch_add_explicit(&ctx->active_property_listeners")

    def test_mutated_postpublish_user_free_rejected(self):
        self.reject("if (r31_immediate_stop_status!=noErr) {",
                    "if (r31_immediate_stop_status!=noErr) { free(owner_ctx);")

    def test_mutated_dispose_success_clearing_rejected(self):
        self.reject("atomic_store(&ctx->dispose_confirmed,1);",
                    "atomic_store(&ctx->dispose_confirmed,0);")

    def test_mutated_listener_failure_tracking_rejected(self):
        self.reject("listener_remove_failed=1;",
                    "listener_remove_failed=0;")

    def test_markdown_preserves_c11_os_and_output_limits(self):
        report={"r34_findings":[{"id":f[0],"severity":f[1],
                                "bureau_role":f[2]} for f in r34.FINDINGS],
                "r34_lifetime_phases":[{"phase":p[0],"owner":p[1],
                    "proof_boundary":p[3]} for p in r34.PHASES]}
        text=r34.markdown(report)
        self.assertIn("NOT proof",text)
        self.assertIn("REAL_OUTPUT=NOT_AUTHORIZED",text)
        self.assertIn("CRITICAL",text)
