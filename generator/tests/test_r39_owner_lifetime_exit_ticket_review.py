"""FREQMED GEN-R39: source-only atomic exit ticket and owner lifetime tests.
Mutations are textual source edits; no simulated callback/interleaving/hardware.
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
import r39_owner_lifetime_exit_ticket_review as r39

class R39OwnerLifetimeExitTicketReview(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c39=(ROOT/r39.CANDIDATE).read_text(encoding="utf-8")
        cls.c31=(ROOT/r31.CANDIDATE).read_text(encoding="utf-8")
        cls.c36=(ROOT/r36.CANDIDATE).read_text(encoding="utf-8")
        cls.c37=(ROOT/r37.CANDIDATE).read_text(encoding="utf-8")
        cls.runner=(ROOT/"RUN_GEN_R39_MAC_INTEL.command").read_text(encoding="utf-8")

    def reject(self,old,new):
        self.assertIn(old,self.c39)
        with self.assertRaises(r39.R39Error):
            r39.observe(self.c39.replace(old,new,1),
                        self.c31,self.c36,self.c37)

    def test_sixteen_obligations_remain_open(self):
        result=r39.observe(self.c39,self.c31,self.c36,self.c37)
        self.assertEqual(16,len(result))
        self.assertEqual({"OPEN_NOT_PROVEN"},set(result.values()))

    def test_four_critical_bureau_obligations(self):
        self.assertEqual(4,sum(row[1]=="CRITICAL" for row in r39.FINDINGS))

    def test_six_documented_ticket_contracts(self):
        self.assertEqual(6,len(r39.CONTRACTS))
        self.assertEqual(6,len({c[0] for c in r39.CONTRACTS}))

    def test_no_audioqueue_or_heap_free_in_candidate(self):
        for forbidden in ("#include <AudioToolbox",
                          "AudioQueueStart(","AudioQueueStop(",
                          "AudioQueueNewOutput(","AudioQueueDispose(",
                          "free(","malloc(","calloc("):
            self.assertNotIn(forbidden,self.c39)

    def test_static_anchor_owner_registration_order(self):
        part=r39.func(self.c39,"fm39_register_owner_once")
        self.assertLess(part.index("fm36_prepare_once(owner,userdata_out)"),
                        part.index("fm36_mark_exposed(*userdata_out)"))

    def test_one_shot_reservation_before_owner_gate(self):
        part=r39.func(self.c39,"fm39_enter_once")
        self.assertLess(part.index("&ticket->phase,&expected,FM39_RESERVING,"),
                        part.index("fm36_try_enter(userdata,&owner)"))

    def test_owner_written_after_r36_admission_only(self):
        part=r39.func(self.c39,"fm39_enter_once")
        self.assertLess(part.index("fm36_try_enter(userdata,&owner)"),
                        part.index("ticket->owner=owner;"))

    def test_owner_published_by_release_phase_store(self):
        part=r39.func(self.c39,"fm39_enter_once")
        self.assertLess(part.index("ticket->owner=owner;"),
                        part.index("FM39_ACTIVE,memory_order_release"))

    def test_owner_reader_acquire_guard(self):
        part=r39.func(self.c39,"fm39_owner_if_active")
        self.assertIn("memory_order_acquire",part)
        self.assertLess(part.index("!=FM39_ACTIVE) return NULL;"),
                        part.index("return ticket->owner;"))

    def test_only_cas_winner_decrements(self):
        part=r39.func(self.c39,"fm39_complete_at_most_once")
        self.assertLess(part.index("&ticket->phase,&expected,FM39_FINISHED,"),
                        part.index("return fm36_leave(ticket->os_userdata);"))
        self.assertEqual(1,part.count("fm36_leave("))

    def test_no_owner_reset_on_completion(self):
        part=r39.func(self.c39,"fm39_complete_at_most_once")
        self.assertNotIn("ticket->owner=",part)
        self.assertNotIn("free(",part)

    def test_process_seal_not_physical_stop(self):
        part=r39.func(self.c39,"fm39_seal_without_release")
        self.assertIn("return fm36_seal(userdata);",part)
        self.assertNotIn("AudioQueue",part)

    def test_real_r31_not_connected_to_exit_ticket(self):
        self.assertIn("AudioQueueNewOutput(&fmt,output_callback,ctx",self.c31)
        self.assertNotIn("fm39_",self.c31)

    def test_exact_220_hashes_and_old_native_digest(self):
        table,_,_,_=r39.inspect(ROOT)
        self.assertGreaterEqual(len(table),220)
        for candidate in (r39.CANDIDATE,r36.CANDIDATE,
                          r37.CANDIDATE,r31.CANDIDATE):
            self.assertEqual(table[candidate],
                hashlib.sha256((ROOT/candidate).read_bytes()).hexdigest())
        self.assertEqual(r19.PINNED_ACOUSTIC_SHA256,
            hashlib.sha256((ROOT/r26.ORIGINAL).read_bytes()).hexdigest())

    def test_runner_keeps_every_candidate_unlinked(self):
        for token in ("R39_EXIT_TICKET_OBJECT=COMPILED_UNLINKED",
                      "R39_CALLBACK_LEASE_OBJECT=COMPILED_UNLINKED",
                      "R39_STABLE_ANCHOR_OBJECT=COMPILED_UNLINKED",
                      "R39_R31_CANDIDATE_OBJECT=COMPILED_UNLINKED",
                      "R39_BUREAU_PROOF_DOSSIER=40_FILES_SHA256_PASS"):
            self.assertIn(token,self.runner)

    def test_mutation_removes_reservation_cas_rejected(self):
        self.reject("&ticket->phase,&expected,FM39_RESERVING,",
                    "&ticket->phase,&expected,FM39_ACTIVE,")

    def test_mutation_owner_published_early_rejected(self):
        self.reject("ticket->owner=owner;",
                    "ticket->owner=NULL;")

    def test_mutation_double_leave_rejected(self):
        self.reject("return fm36_leave(ticket->os_userdata);",
                    "fm36_leave(ticket->os_userdata); return fm36_leave(ticket->os_userdata);")

    def test_mutation_unprotected_complete_rejected(self):
        self.reject("&ticket->phase,&expected,FM39_FINISHED,",
                    "&ticket->phase,&expected,FM39_ACTIVE,")

    def test_real_owner_r16_to_r38_evidence_reverified(self):
        archive=os.environ.get("FREQMED_GEN_R19_ARCHIVE_DIR")
        work=os.environ.get("FREQMED_GEN_R39_EVIDENCE_DIR")
        self.assertTrue(archive and work,
                        "R39 needs real R19 archive and R16–R38 owner proof chain")
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
               "CALLBACK_LEASE_PROOF","OWNER_ALIAS_EXIT_PROOF")
        self.assertEqual(23,len(stems))
        reports={"r"+str(n):Path(work)/("GEN_R"+str(n)+"_"+stem+".json")
                 for n,stem in zip(range(16,39),stems)}
        obj=r39.audit(ROOT,Path(archive),reports)
        self.assertEqual(r39.VERDICT,obj["verdict"])
        self.assertEqual(16,obj["r39_findings_open"])
        self.assertEqual(4,obj["r39_critical_open"])
        self.assertEqual(18,obj["r38_findings_open"])
        self.assertEqual(11,obj["bureau_gates_open"])
        self.assertFalse(obj["r39_real_callback_integrated"])
