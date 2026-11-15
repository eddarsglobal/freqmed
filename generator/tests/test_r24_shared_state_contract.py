"""GEN-R24 real pinned C11 source matrix and CoreAudio contract tests.

No active callbacks, device output, scientific simulation, synthetic
measurements, or false race-freedom certification.
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
import r23_happens_before_obligations as r23
import r24_shared_state_contract_audit as r24

class R24C11SharedStateContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=(ROOT/"src/acoustic_macos.c").read_text(encoding="utf-8")
        cls.source_sha=hashlib.sha256(cls.source.encode("utf-8")).hexdigest()
        cls.fields,cls.calls=r24.inventory(cls.source,cls.source_sha)

    def broken(self,old,replacement):
        self.assertIn(old,self.source)
        changed=self.source.replace(old,replacement,1)
        self.assertNotEqual(changed,self.source)
        with self.assertRaises(r24.R24Error):
            r24.inventory(changed,self.source_sha)

    def test_19_distinct_context_fields(self):
        self.assertEqual(19,len(self.fields))
        self.assertEqual(19,len(set(self.fields)))

    def test_112_context_field_references(self):
        self.assertEqual(112,sum(x["reference_count"] for x in self.fields.values()))

    def test_exact_atomic_and_nonatomic_declarations(self):
        self.assertEqual(12,sum(x["atomic_in_declaration"]
                                for x in self.fields.values()))
        self.assertEqual(7,sum(not x["atomic_in_declaration"]
                               for x in self.fields.values()))

    def test_all_context_anchors_are_actual_source_lines(self):
        lines=self.source.splitlines()
        for field,rec in self.fields.items():
            for site in rec["sites"]:
                self.assertIn("ctx->"+field,lines[site["line"]-1])

    def test_function_roles_bound_to_real_context_access(self):
        for record in self.fields.values():
            for site in record["sites"]:
                self.assertIn(site["function"],r24.FUNC_DOMAIN)
                self.assertEqual(r24.FUNC_DOMAIN[site["function"]],
                                 site["domain_hypothesis"])

    def test_all_fields_are_uncertified(self):
        self.assertTrue(all(x["proof_of_synchronization"] is False
                            for x in self.fields.values()))

    def test_PCM_phase_modified_from_helper_used_by_two_callers(self):
        self.assertEqual({"fill_audio"},
                         {x["function"] for x in self.fields["phase"]["sites"]})
        self.assertIn("fill_audio(ctx,b);",self.source)
        self.assertIn("fill_audio(ctx,buf)",self.source)
        self.assertFalse(self.fields["phase"]["atomic_in_declaration"])

    def test_queue_is_a_nonatomic_cross_function_pointer(self):
        self.assertFalse(self.fields["queue"]["atomic_in_declaration"])
        functions={x["function"] for x in self.fields["queue"]["sites"]}
        self.assertIn("acoustic_output_impl",functions)
        self.assertIn("fill_audio",functions)
        self.assertIn("request_graceful_queue_drain",functions)

    def test_callback_entry_counters_are_not_quiescence_proof(self):
        self.assertTrue(self.fields["active_output_callbacks"]
                        ["atomic_in_declaration"])
        self.assertTrue(self.fields["active_property_listeners"]
                        ["atomic_in_declaration"])
        self.assertTrue(any(x[0]=="SH03_ATOMIC_COUNTER_ENTRY_WINDOW"
                            for x in r24.GAPS))

    def test_direct_audioqueue_call_site_count_and_roles(self):
        self.assertEqual(11,len(self.calls))
        self.assertTrue(all(rec["function"] in r24.FUNC_DOMAIN
                            for rec in self.calls))

    def test_disposal_has_two_distinct_real_call_sites(self):
        calls=[c for c in self.calls if c["api"]=="AudioQueueDispose"]
        self.assertEqual(2,len(calls))
        self.assertEqual(2,len({x["line"] for x in calls}))

    def test_apple_and_C11_contracts_are_bounded(self):
        self.assertEqual(4,len(r24.CONTRACTS))
        self.assertTrue(all(item[2].startswith("https://") and
                            len(item[4])>90 for item in r24.CONTRACTS))
        self.assertTrue(all("CERTIFIED" not in item[3] for item in r24.CONTRACTS))

    def test_seven_findings_are_open_and_linked_to_primary_gates(self):
        self.assertEqual(7,len(r24.GAPS))
        self.assertTrue(all(gate in r23.GATES and len(reason)>85
                            for _,gate,reason in r24.GAPS))

    def test_source_hash_remains_previous_coreaudio_pin(self):
        self.assertEqual(r19.PINNED_ACOUSTIC_SHA256,self.source_sha)

    def test_manifest_and_no_output_binary_link_allowlist(self):
        table,_,matrix,calls=r24.inspect(ROOT)
        self.assertEqual(128,len(table))
        self.assertEqual(19,len(matrix))
        self.assertEqual(11,len(calls))
        runner=(ROOT/"RUN_GEN_R24_MAC_INTEL.command").read_text(encoding="utf-8")
        self.assertEqual(r17.LINK_C_ALLOWLIST,
                         frozenset(r17.link_sources(runner)))

    def test_unreviewed_extra_context_field_fails_closed(self):
        self.broken("ctx->phase+=ctx->phase_step;",
                    "ctx->phase+=ctx->unreviewed_extra;")

    def test_removed_known_nonatomic_field_reference_fails_closed(self):
        self.broken("ctx->phase+=ctx->phase_step;",
                    "ctx->phase+=0.5;")

    def test_additional_field_access_not_silently_accepted(self):
        self.broken("++ctx->frames_written;",
                    "++ctx->frames_written; ++ctx->frames_written;")

    def test_unreviewed_os_API_surface_fails_closed(self):
        self.broken("AudioQueueRemovePropertyListener(ctx->queue,",
                    "AudioQueueAddPropertyListener(ctx->queue,")

    def test_real_owner_mac_evidence_chain_all_gates_still_open(self):
        work=os.environ.get("FREQMED_GEN_R24_EVIDENCE_DIR")
        archive=os.environ.get("FREQMED_GEN_R19_ARCHIVE_DIR")
        if not work or not archive:
            self.skipTest("owner Mac Intel historical R16-R23 reports required")
        work=Path(work)
        base={key:work/name for key,name in {
            "r16":"GEN_R16_OWNERSHIP_EVIDENCE.json",
            "r17":"GEN_R17_VERIFIED_EVIDENCE.json",
            "r18":"GEN_R18_CONTROL_FLOW_EVIDENCE.json",
            "r19":"GEN_R19_ADVERSARIAL_EVIDENCE.json",
            "r20":"GEN_R20_BUREAU_VERIFICATION.json",
        }.items()}
        report=r24.audit(ROOT,Path(archive),base,
                         work/"GEN_R21_BUREAU_GAPS.json",
                         work/"GEN_R22_COREAUDIO_REVIEW.json",
                         work/"GEN_R23_PROOF_OBLIGATIONS.json")
        self.assertEqual("SHARED_STATE_MAPPED_CONTRACT_GAPS_OPEN",report["verdict"])
        self.assertEqual(19,report["shared_field_count"])
        self.assertEqual(112,report["context_field_references"])
        self.assertEqual(11,report["direct_audioqueue_calls"])
        self.assertEqual(15,report["r23_proof_obligations"])
        self.assertEqual(0,report["r23_obligations_discharged"])
        self.assertEqual(11,report["bureau_gates_open"])
        self.assertEqual(0,report["bureau_gates_resolved"])
        self.assertEqual("NONE",report["physical_emission"])
