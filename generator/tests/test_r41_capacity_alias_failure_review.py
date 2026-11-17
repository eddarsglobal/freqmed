"""GEN-R41: source-only capacity/handle/failure containment regression gates.
No callbacks executed; mutation tests alter TEXT only. No scientific simulation.
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

class R41CapacityAliasFailureReview(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c41=(ROOT/r41.CANDIDATE).read_text(encoding="utf-8")
        cls.h41=(ROOT/r41.HEADER).read_text(encoding="utf-8")
        cls.c40=(ROOT/r40.CANDIDATE).read_text(encoding="utf-8")
        cls.h40=(ROOT/r40.HEADER).read_text(encoding="utf-8")
        cls.c39=(ROOT/r39.CANDIDATE).read_text(encoding="utf-8")
        cls.c31=(ROOT/r31.CANDIDATE).read_text(encoding="utf-8")
        cls.c36=(ROOT/r36.CANDIDATE).read_text(encoding="utf-8")
        cls.c37=(ROOT/r37.CANDIDATE).read_text(encoding="utf-8")
        cls.runner=(ROOT/"RUN_GEN_R41_MAC_INTEL.command").read_text(encoding="utf-8")

    def mutated(self,old,new,header=False):
        source=self.h41 if header else self.c41
        self.assertIn(old,source)
        changed=source.replace(old,new,1)
        with self.assertRaises(r41.R41Error):
            r41.observe(self.c41 if header else changed,
                        changed if header else self.h41,
                        self.c40,self.h40,self.c39,self.c31,self.c36,self.c37)

    def test_nineteen_findings_remain_unproven(self):
        findings=r41.observe(self.c41,self.h41,self.c40,self.h40,
                             self.c39,self.c31,self.c36,self.c37)
        self.assertEqual(19,len(findings))
        self.assertEqual({"OPEN_NOT_PROVEN"},set(findings.values()))

    def test_five_critical_findings(self):
        self.assertEqual(5,sum(x[1]=="CRITICAL" for x in r41.FINDINGS))

    def test_six_documentary_contracts(self):
        self.assertEqual(6,len(r41.CONTRACTS))

    def test_fixed_four_process_lifetime_slots(self):
        self.assertEqual(4,self.c41.count("{ATOMIC_VAR_INIT(FM41_UNUSED),NULL}"))
        self.assertIn("static FM41PrivateSlot fm41_slots[FM41_MAX_LIFETIME_TICKETS]",self.c41)

    def test_copyable_handle_is_not_claimed_secure(self):
        self.assertIn("typedef struct { unsigned slot_id; } FM41TicketRef;",self.h41)
        self.assertIn("COPYABLE / FORGEABLE",self.h41)

    def test_capacity_bounded_and_no_recycling(self):
        self.assertIn("#define FM41_MAX_LIFETIME_TICKETS 4u",self.h41)
        self.assertNotIn("FM41_UNUSED,memory_order_release",self.c41)

    def test_no_physical_or_heap_calls(self):
        for blocked in ("AudioQueueStart(","AudioQueueStop(","AudioQueueDispose(",
                        "AudioQueueNewOutput(","malloc(","calloc(","free("):
            self.assertNotIn(blocked,self.c41)

    def test_sticky_fault_atomic_fetch_or(self):
        latch=r41.fn(self.c41,"fm41_latch")
        self.assertIn("atomic_fetch_or_explicit",latch)
        self.assertIn("memory_order_acq_rel",latch)

    def test_register_claim_before_expose(self):
        entry=r41.fn(self.c41,"fm41_register_owner_once")
        self.assertLess(entry.index("fm36_prepare_once(owner,userdata_out)"),
                        entry.index("fm36_mark_exposed(*userdata_out)"))

    def test_begin_denies_prior_faults(self):
        entry=r41.fn(self.c41,"fm41_begin")
        self.assertLess(entry.index("if (fm41_fault_snapshot()!=0u) return -1;"),
                        entry.index("&slot->phase,&expected,FM41_RESERVED,"))

    def test_begin_checks_fault_after_reservation(self):
        entry=r41.fn(self.c41,"fm41_begin")
        self.assertLess(entry.index("&slot->phase,&expected,FM41_RESERVED,"),
                        entry.index("if (fm41_fault_snapshot()!=0u) {"))

    def test_owner_handoff_after_admission(self):
        entry=r41.fn(self.c41,"fm41_begin")
        self.assertLess(entry.index("fm36_try_enter(userdata,&owner)"),
                        entry.index("*owner_out=owner;"))

    def test_null_owner_compensation_records_failure(self):
        entry=r41.fn(self.c41,"fm41_begin")
        self.assertIn("int leave_status=fm36_leave(userdata);",entry)
        self.assertIn("if (leave_status!=0) fm41_latch(FM41_FAULT_LEAVE_FAILURE);",entry)

    def test_complete_bounds_check_before_slot_access(self):
        finish=r41.fn(self.c41,"fm41_complete")
        self.assertLess(finish.index("ticket.slot_id>FM41_MAX_LIFETIME_TICKETS)"),
                        finish.index("FM41PrivateSlot *slot=&fm41_slots[ticket.slot_id-1u];"))

    def test_complete_one_cas_winner_and_failure_latch(self):
        finish=r41.fn(self.c41,"fm41_complete")
        self.assertEqual(1,finish.count("fm36_leave("))
        self.assertLess(finish.index("&slot->phase,&expected,FM41_FINISHED,"),
                        finish.index("int status=fm36_leave(slot->token);"))
        self.assertIn("fm41_latch(FM41_FAULT_DUPLICATE_LEAVE);",finish)

    def test_236_source_pins_and_backend_unchanged(self):
        table,_,_,_=r41.inspect(ROOT)
        self.assertGreaterEqual(len(table),236)
        for name in r41.FILES.values():
            self.assertEqual(table[name],
                hashlib.sha256((ROOT/name).read_bytes()).hexdigest())
        self.assertEqual(r19.PINNED_ACOUSTIC_SHA256,
            hashlib.sha256((ROOT/r26.ORIGINAL).read_bytes()).hexdigest())

    def test_mutation_capacity_fallback_refused(self):
        self.mutated("fm41_latch(FM41_FAULT_CAPACITY);","return 0;")

    def test_mutation_owner_published_early_refused(self):
        self.mutated("*owner_out=owner;","*owner_out=NULL;")

    def test_mutation_skip_terminal_cas_refused(self):
        self.mutated("&slot->phase,&expected,FM41_FINISHED,",
                     "&slot->phase,&expected,FM41_ACTIVE,")

    def test_real_R16_R40_history_and_no_emission(self):
        archive=os.environ.get("FREQMED_GEN_R19_ARCHIVE_DIR")
        folder=os.environ.get("FREQMED_GEN_R41_EVIDENCE_DIR")
        self.assertTrue(archive and folder,
                        "R41 requires authentic Mac R19 archive, reports R16-R40")
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
          "OWNER_EXIT_TICKET_PROOF","OPAQUE_TICKET_PROOF")
        self.assertEqual(25,len(stems))
        reports={"r"+str(n):Path(folder)/("GEN_R"+str(n)+"_"+stem+".json")
                 for n,stem in zip(range(16,41),stems)}
        result=r41.audit(ROOT,Path(archive),reports)
        self.assertEqual(r41.VERDICT,result["verdict"])
        self.assertEqual(19,result["r41_findings_open"])
        self.assertEqual(5,result["r41_critical_open"])
        self.assertEqual(11,result["bureau_gates_open"])
        self.assertFalse(result["r41_real_callback_integrated"])
