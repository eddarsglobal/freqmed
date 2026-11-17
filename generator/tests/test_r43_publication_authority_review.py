"""FREQMED GEN-R43 static C11 publication CAS and bound ticket review.
Textual source mutations only. No OS callbacks, science simulation or output.
"""
import hashlib
import os
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "audits"))
import r19_adversarial_source_audit as r19
import r26_isolated_patch_gate as r26
import r43_publication_authority_review as r43

class R43PublicationAuthorityReview(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src = {key: (ROOT / path).read_text(encoding="utf-8")
                   for key, path in r43.FILES.items()}
        cls.runner = (ROOT / "RUN_GEN_R43_MAC_INTEL.command").read_text(encoding="utf-8")

    def reject(self, old, new, header=False):
        key = "h43" if header else "r43"
        source = self.src[key]
        self.assertIn(old, source)
        changed = source.replace(old, new, 1)
        with self.assertRaises(r43.R43Error):
            r43.observe(self.src["r43"] if header else changed,
                        changed if header else self.src["h43"], self.src)

    def test_21_open_obligations(self):
        found = r43.observe(self.src["r43"], self.src["h43"], self.src)
        self.assertEqual(21, len(found))
        self.assertEqual({"OPEN_NOT_PROVEN"}, set(found.values()))

    def test_six_critical_proof_gates(self):
        self.assertEqual(6, sum(item[1] == "CRITICAL" for item in r43.FINDINGS))

    def test_six_documentary_contracts(self):
        self.assertEqual(6, len(r43.CONTRACTS))
        self.assertEqual(6, len({item[0] for item in r43.CONTRACTS}))

    def test_incomplete_public_ticket_type(self):
        self.assertIn("typedef struct FM43Ticket FM43Ticket;", self.src["h43"])
        self.assertNotIn("struct FM43Ticket {", self.src["h43"])

    def test_exact_four_private_lifetime_slots(self):
        self.assertEqual(4, self.src["r43"].count("{ATOMIC_VAR_INIT(FM43_UNUSED),NULL}"))
        self.assertNotIn("FM43_UNUSED,memory_order_release", self.src["r43"])

    def test_close_reserve_authorize_one_gate(self):
        c = self.src["r43"]
        self.assertIn("FM43_CLOSED=0x80000000u", c)
        self.assertIn("FM43_AUTH_INCREMENT=0x00000100u", c)
        self.assertIn("static atomic_uint fm43_gate=ATOMIC_VAR_INIT(0u);", c)

    def test_reserve_cas_checks_closed_and_limit(self):
        f = r43.func(self.src["r43"], "fm43_reserve")
        self.assertLess(f.index("if ((state & FM43_CLOSED)!=0u) return -1;"),
                        f.index("&fm43_gate,&state,desired,"))
        self.assertIn("fm43_latch(FM43_FAULT_CAPACITY);", f)

    def test_authorize_cas_same_atomic_and_count(self):
        f = r43.func(self.src["r43"], "fm43_authorize")
        self.assertIn("unsigned authorized=(state & FM43_AUTH_MASK)>>FM43_AUTH_SHIFT;", f)
        self.assertLess(f.index("if ((state & FM43_CLOSED)!=0u) return -1;"),
                        f.index("&fm43_gate,&state,desired,"))

    def test_close_gate_precedes_fault_reason(self):
        f = r43.func(self.src["r43"], "fm43_latch")
        self.assertLess(f.index("atomic_fetch_or_explicit(&fm43_gate,FM43_CLOSED"),
                        f.index("atomic_fetch_or_explicit(&fm43_faults,fault"))

    def test_owner_registration_precedes_expose(self):
        f = r43.func(self.src["r43"], "fm43_register_owner_once")
        self.assertLess(f.index("fm36_prepare_once(owner,userdata_out)"),
                        f.index("fm36_mark_exposed(*userdata_out)"))

    def test_admission_before_authorization_and_handoff(self):
        f = r43.func(self.src["r43"], "fm43_begin")
        self.assertLess(f.index("fm36_try_enter(userdata,&owner)"),
                        f.index("if (fm43_authorize()!=0) {"))
        self.assertLess(f.index("if (fm43_authorize()!=0) {"),
                        f.index("*owner_out=owner;"))

    def test_three_terminal_slot_rejections(self):
        f = r43.func(self.src["r43"], "fm43_begin")
        self.assertEqual(3, f.count("FM43_REJECTED,memory_order_release"))
        self.assertEqual(2, f.count("int leave_rc=fm36_leave(userdata);"))

    def test_ticket_member_check_before_token_access(self):
        f = r43.func(self.src["r43"], "fm43_complete")
        self.assertLess(f.index("if (ticket!=slot) continue;"),
                        f.index("if (slot->os_userdata!=expected_userdata) {"))

    def test_userdata_binding_before_terminal_cas(self):
        f = r43.func(self.src["r43"], "fm43_complete")
        self.assertLess(f.index("if (slot->os_userdata!=expected_userdata) {"),
                        f.index("&slot->phase,&expected,FM43_FINISHED,"))
        self.assertEqual(1, f.count("fm36_leave("))

    def test_no_coreaudio_or_heap_in_candidate(self):
        for banned in ("AudioQueueStart(", "AudioQueueStop(", "AudioQueueDispose(",
                       "AudioQueueNewOutput(", "malloc(", "calloc(", "free("):
            self.assertNotIn(banned, self.src["r43"])

    def test_252_sha_pins_and_old_backend_unchanged(self):
        table, _, digests, _ = r43.inspect(ROOT)
        self.assertEqual(252, len(table))
        for key, path in r43.FILES.items():
            self.assertEqual(table[path], hashlib.sha256((ROOT / path).read_bytes()).hexdigest())
            self.assertEqual(table[path], digests[key])
        self.assertEqual(r19.PINNED_ACOUSTIC_SHA256,
                         hashlib.sha256((ROOT / r26.ORIGINAL).read_bytes()).hexdigest())

    def test_mutation_remove_closed_gate_rejected(self):
        self.reject("FM43_CLOSED=0x80000000u", "FM43_CLOSED=0u")

    def test_mutation_wrong_auth_cas_word_rejected(self):
        self.reject("unsigned desired=state+FM43_AUTH_INCREMENT;",
                    "unsigned desired=state+1u;")

    def test_mutation_skip_userdata_binding_rejected(self):
        self.reject("if (slot->os_userdata!=expected_userdata) {",
                    "if (slot->os_userdata==expected_userdata) {")

    def test_owner_R16_to_R42_history_and_Bureau_veto(self):
        archive = os.environ.get("FREQMED_GEN_R19_ARCHIVE_DIR")
        folder = os.environ.get("FREQMED_GEN_R43_EVIDENCE_DIR")
        self.assertTrue(archive and folder,
                        "R43 requires genuine R19 archive and R16–R42 evidence")
        stems = ("OWNERSHIP_EVIDENCE", "VERIFIED_EVIDENCE", "CONTROL_FLOW_EVIDENCE",
                 "ADVERSARIAL_EVIDENCE", "BUREAU_VERIFICATION", "BUREAU_GAPS",
                 "COREAUDIO_REVIEW", "PROOF_OBLIGATIONS", "SHARED_STATE_CONTRACT",
                 "REMEDIATION_REVIEW", "PATCH_SAFETY_GATE", "ADVERSARIAL_REVIEW",
                 "QUEUE_ADMISSION_DESIGN", "ADMISSION_INTEGRATION_REVIEW",
                 "COREAUDIO_QUIESCENCE", "CRITICAL_SHUTDOWN",
                 "FAILED_STOP_OWNERSHIP", "FAILURE_STATE_OWNERSHIP",
                 "USERDATA_LIFETIME", "PRE_ADMISSION_OS_CONTRACT",
                 "STATIC_ANCHOR_PROOF", "CALLBACK_LEASE_PROOF",
                 "OWNER_ALIAS_EXIT_PROOF", "OWNER_EXIT_TICKET_PROOF",
                 "OPAQUE_TICKET_PROOF", "CAPACITY_ALIAS_PROOF",
                 "ATOMIC_ADMISSION_PROOF")
        self.assertEqual(27, len(stems))
        reports = {"r" + str(n): Path(folder) / ("GEN_R" + str(n) + "_" + stem + ".json")
                   for n, stem in zip(range(16, 43), stems)}
        result = r43.audit(ROOT, Path(archive), reports)
        self.assertEqual(r43.VERDICT, result["verdict"])
        self.assertEqual(21, result["r43_findings_open"])
        self.assertEqual(6, result["r43_critical_open"])
        self.assertEqual(11, result["bureau_gates_open"])
        self.assertEqual(0, result["bureau_gates_resolved"])
        self.assertEqual(0, result["r43_real_OS_callbacks"])
