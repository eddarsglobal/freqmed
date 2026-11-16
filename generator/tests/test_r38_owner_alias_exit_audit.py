"""GEN-R38 source-only ownership alias / exit-path regression tests.
No runtime callbacks, scheduling simulation, device activation, or emission.
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
import r36_static_anchor_proof_gate as r36
import r37_adapter_ownership_proof_review as r37
import r38_owner_alias_exit_audit as r38

class R38OwnerAliasExitAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c31=(ROOT/r31.CANDIDATE).read_text(encoding="utf-8")
        cls.c36=(ROOT/r36.CANDIDATE).read_text(encoding="utf-8")
        cls.c37=(ROOT/r37.CANDIDATE).read_text(encoding="utf-8")
        cls.runner=(ROOT/"RUN_GEN_R38_MAC_INTEL.command").read_text(encoding="utf-8")

    def deny(self,source,old,new):
        self.assertIn(old,source)
        with self.assertRaises((r38.R38Error,r37.R37Error,r36.R36Error)):
            if source is self.c31:
                r38.observe(source.replace(old,new,1),self.c36,self.c37)
            elif source is self.c36:
                r38.observe(self.c31,source.replace(old,new,1),self.c37)
            elif source is self.c37:
                r38.observe(self.c31,self.c36,source.replace(old,new,1))
            else:
                self.fail("unknown candidate scope")

    def test_eighteen_findings_all_open(self):
        data=r38.observe(self.c31,self.c36,self.c37)
        self.assertEqual(18,len(data))
        self.assertEqual({"OPEN_NOT_PROVEN"},set(data.values()))

    def test_five_critical_findings(self):
        self.assertEqual(5,sum(x[1]=="CRITICAL" for x in r38.FINDINGS))

    def test_twelve_alias_rows(self):
        self.assertEqual(12,len(r38.ALIAS_ROWS))
        self.assertEqual(12,len({x[0] for x in r38.ALIAS_ROWS}))

    def test_exact_two_c31_owner_frees_before_newoutput(self):
        import r29_admission_integration_review as r29
        ctrl=r29.function(self.c31,"controller")
        first=ctrl.index("AudioQueueNewOutput(&fmt,output_callback,ctx")
        self.assertEqual(2,ctrl[:first].count("free(owner_ctx);"))
        self.assertEqual(0,ctrl[first:].count("free(owner_ctx);"))

    def test_heap_owner_alias_c31(self):
        self.assertIn("AcousticContext *ctx=owner_ctx;",self.c31)
        self.assertIn("AudioQueueNewOutput(&fmt,output_callback,ctx",self.c31)

    def test_property_listener_still_direct_userdata(self):
        self.assertIn("queue_running_listener,ctx)",self.c31)

    def test_callback_output_pre_gate_dereference(self):
        import r29_admission_integration_review as r29
        part=r29.function(self.c31,"callback")
        self.assertLess(part.index("AcousticContext *ctx=(AcousticContext*)ptr;"),
                        part.index("fm_r28_gate_try_enter(&ctx->queue_admission)"))

    def test_callback_listener_pre_gate_dereference(self):
        import r29_admission_integration_review as r29
        part=r29.function(self.c31,"listener")
        self.assertLess(part.index("AcousticContext *ctx=(AcousticContext*)data;"),
                        part.index("fm_r28_gate_try_enter(&ctx->queue_admission)"))

    def test_output_exit_and_accounting(self):
        import r29_admission_integration_review as r29
        part=r29.function(self.c31,"callback")
        self.assertEqual(1,part.count("fm_r28_gate_leave(&ctx->queue_admission);"))
        self.assertEqual(1,part.count("atomic_fetch_add_explicit(&ctx->active_output_callbacks,1U"))
        self.assertEqual(1,part.count("atomic_fetch_sub_explicit(&ctx->active_output_callbacks,1U"))

    def test_listener_shared_exit_label(self):
        import r29_admission_integration_review as r29
        part=r29.function(self.c31,"listener")
        self.assertEqual(1,part.count("listener_exit:"))
        self.assertIn("goto listener_exit;",part)
        self.assertEqual(1,part.count("fm_r28_gate_leave(&ctx->queue_admission);"))

    def test_r37_leases_are_not_coreaudio_abi(self):
        self.assertNotIn("fm37_output_enter",self.c31)
        self.assertIn("FM37Lease lease={0};",self.c37)

    def test_r37_finish_resets_alias_before_leave(self):
        part=r37.function(self.c37,"fm37_finish")
        self.assertLess(part.index("lease->owner=NULL;"),
                        part.index("return fm36_leave(token);"))

    def test_r36_owner_is_atomic_but_external_ownership_not_enforced(self):
        self.assertIn("_Atomic(void *) owner;",self.c36)
        self.assertNotIn("free(",self.c36)
        self.assertIn("NO external alias releases owner",self.c37)

    def test_213_manifest_and_r19_original(self):
        table,_,_,_=r38.inspect(ROOT)
        self.assertEqual(213,len(table))
        for path in r38.FILES.values():
            self.assertEqual(table[path],
                             hashlib.sha256((ROOT/path).read_bytes()).hexdigest())
        self.assertEqual(r19.PINNED_ACOUSTIC_SHA256,
           hashlib.sha256((ROOT/r26.ORIGINAL).read_bytes()).hexdigest())

    def test_runner_denies_all_candidate_linking(self):
        for token in ("R38_R31_CANDIDATE_OBJECT=COMPILED_UNLINKED",
                      "R38_STABLE_ANCHOR_OBJECT=COMPILED_UNLINKED",
                      "R38_CALLBACK_LEASE_OBJECT=COMPILED_UNLINKED",
                      "R38_BUREAU_PROOF_DOSSIER=38_FILES_SHA256_PASS",
                      "R38_TESTCASE_RUN_SLOT=PASS"):
            self.assertIn(token,self.runner)

    def test_mutation_extra_postpublication_free_rejected(self):
        self.deny(self.c31,"if (r31_immediate_stop_status!=noErr) {",
                  "if (r31_immediate_stop_status!=noErr) { free(owner_ctx);")

    def test_mutation_gate_leave_removed_rejected(self):
        self.deny(self.c31,"fm_r28_gate_leave(&ctx->queue_admission);",
                  "/* removed gate leave */")

    def test_mutation_r37_finish_skips_decrement_rejected(self):
        self.deny(self.c37,"return fm36_leave(token);","return 0;")

    def test_mutation_c36_owner_free_rejected(self):
        self.deny(self.c36,"return -1;\n}\n\n/* Irreversible seal;",
                  "free(owner); return -1;\n}\n\n/* Irreversible seal;")

    def test_real_R16_R37_evidence_chain(self):
        original=os.environ.get("FREQMED_GEN_R19_ARCHIVE_DIR")
        folder=os.environ.get("FREQMED_GEN_R38_EVIDENCE_DIR")
        self.assertTrue(original and folder,"genuine owner R19 and R16–R37 needed")
        stems=("OWNERSHIP_EVIDENCE","VERIFIED_EVIDENCE",
               "CONTROL_FLOW_EVIDENCE","ADVERSARIAL_EVIDENCE",
               "BUREAU_VERIFICATION","BUREAU_GAPS","COREAUDIO_REVIEW",
               "PROOF_OBLIGATIONS","SHARED_STATE_CONTRACT",
               "REMEDIATION_REVIEW","PATCH_SAFETY_GATE",
               "ADVERSARIAL_REVIEW","QUEUE_ADMISSION_DESIGN",
               "ADMISSION_INTEGRATION_REVIEW","COREAUDIO_QUIESCENCE",
               "CRITICAL_SHUTDOWN","FAILED_STOP_OWNERSHIP",
               "FAILURE_STATE_OWNERSHIP","USERDATA_LIFETIME",
               "PRE_ADMISSION_OS_CONTRACT","STATIC_ANCHOR_PROOF",
               "CALLBACK_LEASE_PROOF")
        reports={"r"+str(n):Path(folder)/("GEN_R"+str(n)+"_"+stem+".json")
                 for n,stem in zip(range(16,38),stems)}
        result=r38.audit(ROOT,Path(original),reports)
        self.assertEqual(18,result["r38_findings_open"])
        self.assertEqual(5,result["r38_critical_open"])
        self.assertFalse(result["r38_adapter_integrated"])
        self.assertEqual(11,result["bureau_gates_open"])
