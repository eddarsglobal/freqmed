"""FREQMED GEN-R42: real source-only C11 atomic gate and opaque ticket tests.
Mutations are text changes only; no simulated race, OS callback or emission.
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
import r39_owner_lifetime_exit_ticket_review as r39
import r40_ticket_copy_completion_review as r40
import r41_capacity_alias_failure_review as r41
import r42_index_forgery_admission_review as r42

class R42IndexForgeryAdmissionReview(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources={key:(ROOT/path).read_text(encoding="utf-8")
                     for key,path in r42.FILES.items()}
        cls.runner=(ROOT/"RUN_GEN_R42_MAC_INTEL.command").read_text(encoding="utf-8")

    def reject(self,needle,new,header=False):
        key="h42" if header else "r42"
        old=self.sources[key]
        self.assertIn(needle,old)
        mutated=old.replace(needle,new,1)
        with self.assertRaises(r42.R42Error):
            r42.observe(
                mutated if not header else self.sources["r42"],
                mutated if header else self.sources["h42"],
                *[self.sources[k] for k in
                  ("r41","h41","r40","h40","r39","r31","r36","r37")])

    def test_twenty_obligations_all_open(self):
        found=r42.observe(*[self.sources[k] for k in
            ("r42","h42","r41","h41","r40","h40","r39","r31","r36","r37")])
        self.assertEqual(20,len(found))
        self.assertEqual({"OPEN_NOT_PROVEN"},set(found.values()))

    def test_six_critical_obligations(self):
        self.assertEqual(6,sum(f[1]=="CRITICAL" for f in r42.FINDINGS))

    def test_opaque_header_no_public_ticket_definition(self):
        h=self.sources["h42"]
        self.assertIn("typedef struct FM42Ticket FM42Ticket;",h)
        self.assertNotIn("struct FM42Ticket {",h)

    def test_four_static_slots_not_recycled(self):
        c=self.sources["r42"]
        self.assertEqual(4,c.count("{ATOMIC_VAR_INIT(FM42_UNUSED),NULL}"))
        self.assertNotIn("FM42_UNUSED,memory_order_release",c)

    def test_gate_closed_and_count_share_single_atomic(self):
        c=self.sources["r42"]
        self.assertIn("static atomic_uint fm42_gate=ATOMIC_VAR_INIT(0u);",c)
        self.assertIn("FM42_CLOSED=0x80000000u",c)
        self.assertIn("FM42_COUNT_MASK=0x0000ffffu",c)

    def test_reservation_checks_close_before_CAS(self):
        f=r42.fn(self.sources["r42"],"fm42_reserve_permit")
        self.assertLess(f.index("if ((state & FM42_CLOSED)!=0u) return -1;"),
                        f.index("&fm42_gate,&state,desired,"))

    def test_saturation_latches_fault_and_denies(self):
        f=r42.fn(self.sources["r42"],"fm42_reserve_permit")
        self.assertIn("fm42_latch(FM42_FAULT_CAPACITY); return -1;",f)
        self.assertNotIn("malloc(",f)

    def test_latch_closes_before_reason_publication(self):
        f=r42.fn(self.sources["r42"],"fm42_latch")
        self.assertLess(f.index("atomic_fetch_or_explicit(&fm42_gate,FM42_CLOSED"),
                        f.index("atomic_fetch_or_explicit(&fm42_faults,fault"))

    def test_owner_gate_precedes_publication(self):
        f=r42.fn(self.sources["r42"],"fm42_begin")
        self.assertLess(f.index("fm36_try_enter(userdata,&owner)"),
                        f.index("*owner_out=owner;"))

    def test_two_post_reservation_close_checks(self):
        f=r42.fn(self.sources["r42"],"fm42_begin")
        self.assertEqual(2,f.count("FM42_CLOSED)!=0u"))
        self.assertEqual(3,f.count("FM42_REJECTED,memory_order_release"))

    def test_compensating_leave_checks_result(self):
        f=r42.fn(self.sources["r42"],"fm42_begin")
        self.assertEqual(2,f.count("int rc=fm36_leave(userdata);"))
        self.assertEqual(2,f.count("if (rc!=0) fm42_latch(FM42_FAULT_LEAVE);"))

    def test_ticket_member_check_precedes_CAS(self):
        f=r42.fn(self.sources["r42"],"fm42_complete")
        self.assertLess(f.index("if (ticket!=slot) continue;"),
                        f.index("&slot->phase,&expected,FM42_FINISHED,"))

    def test_complete_at_most_once_never_free(self):
        f=r42.fn(self.sources["r42"],"fm42_complete")
        self.assertEqual(1,f.count("fm36_leave("))
        self.assertNotIn("free(",f)

    def test_original_C31_and_R36_R41_unchanged(self):
        self.assertIn("AudioQueueNewOutput(&fmt,output_callback,ctx",
                      self.sources["r31"])
        for key in ("r31","r36","r37","r39","r40","r41"):
            self.assertNotIn("fm42_",self.sources[key])

    def test_manifest_244_and_no_emitting_linkage(self):
        table,_,_,_=r42.inspect(ROOT)
        self.assertEqual(244,len(table))
        for key,path in r42.FILES.items():
            self.assertEqual(table[path],
                hashlib.sha256((ROOT/path).read_bytes()).hexdigest())
        self.assertEqual(r19.PINNED_ACOUSTIC_SHA256,
            hashlib.sha256((ROOT/r26.ORIGINAL).read_bytes()).hexdigest())
        self.assertIn("R42_ATOMIC_GATE_OBJECT=COMPILED_UNLINKED",self.runner)

    def test_mutation_remove_gate_close_refused(self):
        self.reject("FM42_CLOSED=0x80000000u","FM42_CLOSED=0u")

    def test_mutation_skip_count_CAS_refused(self):
        self.reject("&fm42_gate,&state,desired,","&fm42_faults,&state,desired,")

    def test_mutation_premature_owner_publication_refused(self):
        self.reject("*owner_out=owner;","*owner_out=NULL;")

    def test_mutation_double_leave_refused(self):
        self.reject("int rc=fm36_leave(slot->token);",
                    "fm36_leave(slot->token); int rc=fm36_leave(slot->token);")

    def test_real_R16_R41_evidence_and_Bureau_veto(self):
        archive=os.environ.get("FREQMED_GEN_R19_ARCHIVE_DIR")
        folder=os.environ.get("FREQMED_GEN_R42_EVIDENCE_DIR")
        self.assertTrue(archive and folder,"R42 needs original R19 and R16–R41 proof chain")
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
          "CALLBACK_LEASE_PROOF","OWNER_ALIAS_EXIT_PROOF",
          "OWNER_EXIT_TICKET_PROOF","OPAQUE_TICKET_PROOF",
          "CAPACITY_ALIAS_PROOF")
        self.assertEqual(26,len(stems))
        reports={"r"+str(n):Path(folder)/("GEN_R"+str(n)+"_"+stem+".json")
                 for n,stem in zip(range(16,42),stems)}
        obj=r42.audit(ROOT,Path(archive),reports)
        self.assertEqual(r42.VERDICT,obj["verdict"])
        self.assertEqual(20,obj["r42_findings_open"])
        self.assertEqual(6,obj["r42_critical_open"])
        self.assertEqual(19,obj["r41_findings_open"])
        self.assertEqual(11,obj["bureau_gates_open"])
        self.assertFalse(obj["r42_integrated_into_C31"])
