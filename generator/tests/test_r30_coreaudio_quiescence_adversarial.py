"""GEN-R30 source-only C11/CoreAudio adversarial checks.
No CoreAudio callback dispatch, no scientific simulation and no physical output.
"""
import hashlib
import json
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

class R30CoreAudioQuiescenceReview(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c=(ROOT/r29.CANDIDATE).read_text(encoding="utf-8")
        cls.runner=(ROOT/"RUN_GEN_R30_MAC_INTEL.command").read_text(encoding="utf-8")

    def reject(self,old,new):
        self.assertIn(old,self.c)
        altered=self.c.replace(old,new,1)
        with self.assertRaises((r30.R30Error,ValueError)):
            r30.observe(altered)

    def test_twelve_findings_all_open(self):
        result=r30.observe(self.c)
        self.assertEqual(12,len(result))
        self.assertEqual({"OPEN_NOT_PROVEN"},set(result.values()))

    def test_two_critical_findings_never_promoted(self):
        self.assertEqual(2,sum(x[1]=="CRITICAL" for x in r30.FINDINGS))
        self.assertEqual({"Q30_02_LIVE_QUEUE_EARLY_EXIT",
                          "Q30_12_QUARANTINE_NOT_HARDWARE_STOP"},
                         {x[0] for x in r30.FINDINGS if x[1]=="CRITICAL"})

    def test_callback_and_listener_admission_are_not_os_proof(self):
        self.assertEqual(2,self.c.count("fm_r28_gate_try_enter(&ctx->queue_admission)"))
        self.assertEqual("OPEN_NOT_PROVEN",
                         r30.observe(self.c)["Q30_01_USERDATA_BEFORE_ATOMIC_ADMISSION"])

    def test_critical_early_exit_after_start_is_visible(self):
        ctrl=r30.fn(self.c,"controller")
        start=ctrl.index("AudioQueueStart(ctx->queue,NULL)")
        close=ctrl.rindex("fm_r28_gate_close(&ctx->queue_admission);")
        early=ctrl.index("return -1;",close)
        stop=ctrl.index("AudioQueueStop(ctx->queue,true)",close)
        self.assertTrue(start<close<early<stop)

    def test_early_exit_skips_stop_dispose(self):
        ctrl=r30.fn(self.c,"controller")
        pos=ctrl.rindex("fm_r28_gate_close(&ctx->queue_admission);")
        early=ctrl.index("return -1;",pos)
        self.assertNotIn("AudioQueueStop(",ctrl[pos:early])
        self.assertNotIn("AudioQueueDispose(",ctrl[pos:early])

    def test_nonatomic_queue_clear_after_dispose_remains_open(self):
        self.assertIn("ctx->queue=NULL;",r30.fn(self.c,"controller"))
        self.assertIn("AudioQueueEnqueueBuffer(ctx->queue",r30.fn(self.c,"pcm"))

    def test_pcm_critical_section_still_contains_enqueue(self):
        self.assertIn("AudioQueueEnqueueBuffer(ctx->queue,buf,0,NULL)",
                      r30.fn(self.c,"pcm"))
        self.assertIn("pcm_writer_gate",r30.fn(self.c,"callback"))

    def test_listener_failure_still_precedes_dispose(self):
        ctrl=r30.fn(self.c,"controller")
        self.assertLess(ctrl.index("listener_remove_failed=1;"),
                        ctrl.index("if (AudioQueueDispose(ctx->queue,true)!=noErr)"))

    def test_r29_C_original_never_modified(self):
        data=(ROOT/r26.ORIGINAL).read_bytes()
        self.assertEqual(r19.PINNED_ACOUSTIC_SHA256,
                         hashlib.sha256(data).hexdigest())

    def test_r29_C_candidate_remains_pinned(self):
        table,_,_,_=r30.inspect(ROOT)
        self.assertEqual(hashlib.sha256((ROOT/r29.CANDIDATE).read_bytes()).hexdigest(),
                         table[r29.CANDIDATE])

    def test_r28_atomic_gate_never_modified(self):
        source=(ROOT/r28.CANDIDATE).read_text(encoding="utf-8")
        self.assertEqual(5,len(r28.observe(source)))

    def test_exact_manifest_162_source_files(self):
        table,_,_,_=r30.inspect(ROOT)
        self.assertGreaterEqual(len(table),162)

    def test_r30_runner_excludes_all_output_candidates(self):
        self.assertIn("R30_NONEMITTING_EXECUTABLE_SYMBOL_AUDIT=PASS",self.runner)
        self.assertIn("R30_R29_CANDIDATE_OBJECT=COMPILED_UNLINKED",self.runner)

    def test_22_report_bureau_dossier_manifest(self):
        self.assertIn("R30_BUREAU_ADVERSARIAL_DOSSIER=22_FILES_SHA256_PASS",
                      self.runner)

    def test_real_owner_mac_historical_R16_R29_provenance(self):
        archive=os.environ.get("FREQMED_GEN_R19_ARCHIVE_DIR")
        directory=os.environ.get("FREQMED_GEN_R30_EVIDENCE_DIR")
        self.assertTrue(archive and directory,
                        "R30 requires genuine owner Mac archive and report directory")
        d=Path(directory)
        stems=("OWNERSHIP_EVIDENCE","VERIFIED_EVIDENCE",
               "CONTROL_FLOW_EVIDENCE","ADVERSARIAL_EVIDENCE",
               "BUREAU_VERIFICATION","BUREAU_GAPS","COREAUDIO_REVIEW",
               "PROOF_OBLIGATIONS","SHARED_STATE_CONTRACT",
               "REMEDIATION_REVIEW","PATCH_SAFETY_GATE",
               "ADVERSARIAL_REVIEW","QUEUE_ADMISSION_DESIGN",
               "ADMISSION_INTEGRATION_REVIEW")
        paths={"r"+str(n):d/("GEN_R"+str(n)+"_"+stem+".json")
               for n,stem in zip(range(16,30),stems)}
        outcome=r30.audit(ROOT,Path(archive),paths)
        self.assertEqual(r30.VERDICT,outcome["verdict"])
        self.assertEqual(12,outcome["r30_findings_open"])
        self.assertEqual(2,outcome["r30_critical_open"])
        self.assertEqual(11,outcome["bureau_gates_open"])
        self.assertFalse(outcome["r30_linked_output"])

    def test_mutated_callback_admission_rejected(self):
        self.reject("if (!fm_r28_gate_try_enter(&ctx->queue_admission)) return;",
                    "if (fm_r28_gate_try_enter(&ctx->queue_admission)) return;")

    def test_mutated_critical_early_return_rejected(self):
        self.reject("return -1;\n  }\n  if (ctx->queue) {",
                    "goto listener_exit;\n  }\n  if (ctx->queue) {")

    def test_mutated_final_stop_rejected(self):
        self.reject("AudioQueueStop(ctx->queue,true)","AudioQueueStop(ctx->queue,false)")

    def test_mutated_listener_remove_rejected(self):
        self.reject("AudioQueueRemovePropertyListener(ctx->queue,",
                    "AudioQueueAddPropertyListener(ctx->queue,")

    def test_markdown_cannot_claim_os_quiescence_or_activation(self):
        report={"findings":[{"id":x[0],"severity":x[1],
                 "bureau_role":x[2]} for x in r30.FINDINGS]}
        text=r30.markdown(report)
        self.assertIn("NEVER run this",text)
        self.assertIn("NOT_AUTHORIZED",text)
        self.assertIn("not proof of C11",text)
