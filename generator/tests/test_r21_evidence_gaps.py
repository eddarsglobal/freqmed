"""GEN-R21 source-only noncertifying Bureau evidence gap regressions.

The test oracle is real pinned code and recorded unresolved statuses; software
tampering in memory does NOT simulate physical sound, EM, devices, or biology.
"""
import copy
import hashlib
import json
import os
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "audits"))
import r17_evidence_verifier as r17
import r20_bureau_archive_review as r20
import r21_bureau_evidence_gaps as r21

class R21BureauEvidenceGaps(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.table, cls.manifest_sha = r17.manifest_integrity(ROOT)
        cls.gates = r21.gate_register(ROOT, cls.table, r20.UNRESOLVED)

    def test_eleven_real_gates_are_preserved(self):
        self.assertEqual(11, len(self.gates))
        self.assertEqual(0, sum(g["state"] != "OPEN_EVIDENCE_GAP"
                                for g in self.gates))

    def test_identifiers_match_original_r20(self):
        self.assertEqual([x[0] for x in r20.UNRESOLVED],
                         [g["id"] for g in self.gates])

    def test_none_of_r20_statuses_are_promoted(self):
        self.assertEqual(dict(r20.UNRESOLVED),
                         {g["id"]: g["status"] for g in self.gates})

    def test_all_ten_historical_bureau_roles_are_accounted(self):
        roles = {role for gate in self.gates
                 for role in gate["owner_roles"]}
        self.assertEqual({"B%02d" % n for n in range(1, 11)}, roles)

    def test_all_anchors_are_in_source_manifest(self):
        self.assertTrue(all(g["supporting_existing_source"]["path"] in self.table
                            for g in self.gates))

    def test_source_anchor_hash_matches_exact_manifest(self):
        for gate in self.gates:
            ref = gate["supporting_existing_source"]
            self.assertEqual(self.table[ref["path"]], ref["source_sha256"])

    def test_anchors_reference_real_nonempty_source_lines(self):
        for gate in self.gates:
            ref = gate["supporting_existing_source"]
            lines = (ROOT / ref["path"]).read_text(encoding="utf-8").splitlines()
            self.assertGreater(ref["line"], 0)
            self.assertIn(ref["anchor_text"], lines[ref["line"] - 1])

    def test_no_gate_claims_software_physical_safety(self):
        self.assertTrue(all(g["software_source_proves_physical_safety"] is False
                            for g in self.gates))

    def test_no_independent_approvals_are_fabricated(self):
        self.assertTrue(all(g["independent_certification"] == "NONE"
                            for g in self.gates))

    def test_every_gate_has_explicit_missing_evidence(self):
        self.assertTrue(all(len(g["missing_evidence"]) > 24
                            for g in self.gates))

    def test_bureau_categories_do_not_claim_qualified_devices(self):
        categories = [g["qualification_kind"] for g in self.gates]
        self.assertTrue(all("CERTIFIED" not in x and
                            "AUTHORIZED_OUTPUT" not in x
                            for x in categories))

    def test_original_r19_manifest_pin_is_unchanged(self):
        self.assertEqual(
            "c80091fd6d22e8e8bef076b4565f5640be70c53268c4238aa8d264b1207dfb28",
            r20.R19_MANIFEST_SHA256)

    def test_nonemitting_runner_link_allowlist(self):
        runner = (ROOT / "RUN_GEN_R21_MAC_INTEL.command").read_text(encoding="utf-8")
        self.assertEqual(r17.LINK_C_ALLOWLIST,
                         frozenset(r17.link_sources(runner)))
        self.assertIn("R21_NONEMITTING_EXECUTABLE_SYMBOL_AUDIT=PASS", runner)

    def test_bureau_markdown_lists_all_eleven_gaps(self):
        report = {"gates": self.gates}
        text = r21.markdown(report)
        for name, _ in r20.UNRESOLVED:
            self.assertIn(name, text)
        self.assertIn("EVIDENCE_GAPS_MAPPED_NOT_CERTIFIED", text)

    def test_omitting_real_source_anchor_fails_closed(self):
        table = dict(self.table)
        table.pop(self.gates[0]["supporting_existing_source"]["path"])
        with self.assertRaises(r21.GapError):
            r21.gate_register(ROOT, table, r20.UNRESOLVED)

    def test_replacing_real_source_hash_fails_closed(self):
        table = dict(self.table)
        table["src/acoustic_macos.c"] = "0" * 64
        with self.assertRaises(r21.GapError):
            r21.gate_register(ROOT, table, r20.UNRESOLVED)

    def test_omitted_bureau_gate_fails_closed(self):
        with self.assertRaises(r21.GapError):
            r21.gate_register(ROOT, self.table, r20.UNRESOLVED[:-1])

    def test_fake_certification_status_fails_closed(self):
        statuses = list(r20.UNRESOLVED)
        statuses[0] = (statuses[0][0], "CERTIFIED")
        with self.assertRaises(r21.GapError):
            r21.gate_register(ROOT, self.table, statuses)

    def test_duplicated_gate_status_fails_closed(self):
        statuses = list(r20.UNRESOLVED)
        statuses[-1] = statuses[0]
        with self.assertRaises(r21.GapError):
            r21.gate_register(ROOT, self.table, statuses)

    def test_actual_r21_evidence_chain_and_zero_resolved(self):
        directory = os.environ.get("FREQMED_GEN_R21_EVIDENCE_DIR")
        history = os.environ.get("FREQMED_GEN_R19_ARCHIVE_DIR")
        if not directory or not history:
            self.skipTest("Mac Intel actual R16-R20 evidence files required")
        directory = Path(directory)
        paths = {
            "r16": directory/"GEN_R16_OWNERSHIP_EVIDENCE.json",
            "r17": directory/"GEN_R17_VERIFIED_EVIDENCE.json",
            "r18": directory/"GEN_R18_CONTROL_FLOW_EVIDENCE.json",
            "r19": directory/"GEN_R19_ADVERSARIAL_EVIDENCE.json",
            "r20": directory/"GEN_R20_BUREAU_VERIFICATION.json",
        }
        result = r21.audit(ROOT, Path(history), paths)
        self.assertEqual(r21.VERDICT, result["verdict"])
        self.assertEqual(11, result["open_gates"])
        self.assertEqual(0, result["resolved_gates"])
        self.assertEqual("NONE", result["physical_emission"])
        self.assertEqual("NOT_AUTHORIZED", result["production"])
