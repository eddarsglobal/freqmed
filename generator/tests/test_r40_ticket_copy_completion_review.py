"""FREQMED GEN-R40 source-only opaque ticket proof contracts and regressions.
No callback dispatch, concurrency scheduling simulation, scientific emission.
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

class R40TicketCopyCompletionReview(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c40=(ROOT/r40.CANDIDATE).read_text(encoding="utf-8")
        cls.h40=(ROOT/r40.HEADER).read_text(encoding="utf-8")
        cls.c39=(ROOT/r39.CANDIDATE).read_text(encoding="utf-8")
        cls.c31=(ROOT/r31.CANDIDATE).read_text(encoding="utf-8")
        cls.c36=(ROOT/r36.CANDIDATE).read_text(encoding="utf-8")
        cls.c37=(ROOT/r37.CANDIDATE).read_text(encoding="utf-8")
        cls.runner=(ROOT/"RUN_GEN_R40_MAC_INTEL.command").read_text(encoding="utf-8")

    def reject(self,needle,replacement,header=False):
        source=self.h40 if header else self.c40
        self.assertIn(needle,source)
        changed=source.replace(needle,replacement,1)
        with self.assertRaises(r40.R40Error):
            r40.observe(self.c40 if header else changed,
                        changed if header else self.h40,
                        self.c39,self.c31,self.c36,self.c37)

    def test_eighteen_findings_remain_open(self):
        found=r40.observe(self.c40,self.h40,self.c39,self.c31,self.c36,self.c37)
        self.assertEqual(18,len(found))
        self.assertEqual({"OPEN_NOT_PROVEN"},set(found.values()))

    def test_five_critical_seat_obligations(self):
        self.assertEqual(5,sum(row[1]=="CRITICAL" for row in r40.FINDINGS))

    def test_six_c11_documented_contracts(self):
        self.assertEqual(6,len(r40.CONTRACTS))

    def test_header_only_incomplete_type(self):
        self.assertIn("typedef struct FM40Ticket FM40Ticket;",self.h40)
        self.assertNotIn("struct FM40Ticket {",self.h40)

    def test_four_static_slots_never_recycled(self):
        self.assertEqual(4,self.c40.count("ATOMIC_VAR_INIT(FM40_UNUSED),NULL"))
        self.assertIn("static struct FM40Ticket fm40_slots[FM40_MAX_TICKETS]",self.c40)
        self.assertNotIn("FM40_UNUSED,memory_order_release",self.c40)

    def test_bounded_lifetime_capacity_defined(self):
        self.assertIn("#define FM40_MAX_TICKETS 4u",self.h40)
        self.assertIn("for (size_t i=0u;i<FM40_MAX_TICKETS;i++)",self.c40)

    def test_no_audioqueue_or_heap_reclaim(self):
        for forbidden in ("AudioQueueStart(","AudioQueueStop(","AudioQueueDispose(",
                          "AudioQueueNewOutput(","malloc(","calloc(","free(",
                          "realloc("):
            self.assertNotIn(forbidden,self.c40)

    def test_admit_gate_before_token_release(self):
        entry=r40.fn(self.c40,"fm40_begin")
        self.assertLess(entry.index("fm36_try_enter(userdata,&owner)"),
                        entry.index("slot->token=userdata;"))

    def test_owner_publication_after_active_release(self):
        entry=r40.fn(self.c40,"fm40_begin")
        self.assertLess(entry.index("FM40_ACTIVE,memory_order_release"),
                        entry.index("*owner_out=owner;"))

    def test_denial_marks_slot_terminal_rejected(self):
        entry=r40.fn(self.c40,"fm40_begin")
        self.assertEqual(2,entry.count("FM40_REJECTED,memory_order_release"))
        self.assertIn("(void)fm36_leave(userdata);",entry)

    def test_pointer_identity_checked_prior_cas(self):
        ending=r40.fn(self.c40,"fm40_complete")
        self.assertLess(ending.index("if (ticket!=slot) continue;"),
                        ending.index("&slot->phase,&expected,FM40_FINISHED,"))

    def test_complete_cas_at_most_once(self):
        ending=r40.fn(self.c40,"fm40_complete")
        self.assertEqual(1,ending.count("fm36_leave("))
        self.assertLess(ending.index("&slot->phase,&expected,FM40_FINISHED,"),
                        ending.index("return fm36_leave(slot->token);"))

    def test_previous_C31_C36_C37_C39_unmodified(self):
        for old in (self.c31,self.c36,self.c37,self.c39):
            self.assertNotIn("fm40_",old)
        self.assertIn("AudioQueueNewOutput(&fmt,output_callback,ctx",self.c31)

    def test_compiler_negative_probe_in_runner(self):
        self.assertIn("R40_OPAQUE_BY_VALUE_COMPILER_DENIAL=PASS",self.runner)
        self.assertIn("FM40Ticket forbidden_copy;",self.runner)

    def test_228_SHA_pins_and_old_native_digest(self):
        table,_,_,_=r40.inspect(ROOT)
        self.assertGreaterEqual(len(table),228)
        for path in r40.FILES.values():
            self.assertEqual(table[path],
               hashlib.sha256((ROOT/path).read_bytes()).hexdigest())
        self.assertEqual(r19.PINNED_ACOUSTIC_SHA256,
           hashlib.sha256((ROOT/r26.ORIGINAL).read_bytes()).hexdigest())

    def test_mutation_public_header_exposes_type_rejected(self):
        self.reject("typedef struct FM40Ticket FM40Ticket;",
                    "struct FM40Ticket { int unsafe_public_phase; };",header=True)

    def test_mutation_double_complete_rejected(self):
        self.reject("return fm36_leave(slot->token);",
                    "fm36_leave(slot->token); return fm36_leave(slot->token);")

    def test_mutation_early_owner_publication_rejected(self):
        self.reject("*owner_out=owner;",
                    "*owner_out=NULL;")

    def test_mutation_cas_state_skipped_rejected(self):
        self.reject("&slot->phase,&expected,FM40_FINISHED,",
                    "&slot->phase,&expected,FM40_ACTIVE,")

    def test_real_R16_R39_provenance_and_Bureau_veto(self):
        archive=os.environ.get("FREQMED_GEN_R19_ARCHIVE_DIR")
        work=os.environ.get("FREQMED_GEN_R40_EVIDENCE_DIR")
        self.assertTrue(archive and work,"R40 requires genuine R19 archive and R16-R39 history")
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
               "OWNER_EXIT_TICKET_PROOF")
        self.assertEqual(24,len(stems))
        reports={"r"+str(n):Path(work)/("GEN_R"+str(n)+"_"+stem+".json")
                 for n,stem in zip(range(16,40),stems)}
        result=r40.audit(ROOT,Path(archive),reports)
        self.assertEqual(r40.VERDICT,result["verdict"])
        self.assertEqual(18,result["r40_findings_open"])
        self.assertEqual(5,result["r40_critical_open"])
        self.assertEqual(11,result["bureau_gates_open"])
        self.assertFalse(result["r40_real_callback_integrated"])
