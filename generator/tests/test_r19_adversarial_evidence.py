"""GEN-R19 adversarial static regressions and preservation integrity.

Uses genuine pinned source and genuine auditor output. The only mutations
are software text/JSON tamper checks; no modified C is compiled, no device
is opened, no physical or numerical scientific simulation is performed.
"""
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "audits"))
import r16_ownership_static_audit as r16
import r17_evidence_verifier as r17
import r18_control_flow_envelope as r18
import r19_adversarial_source_audit as adversarial
import r19_evidence_archive as archive

SRC = (ROOT / "src/acoustic_macos.c").read_text(encoding="utf-8")
RUN = (ROOT / "RUN_GEN_R19_MAC_INTEL.command").read_text(encoding="utf-8")
PARENT_PIN = "1d4b36fb6dcd5c4dab7155d5ee9fae3fd2623033"

class R19AdversarialEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dir = tempfile.TemporaryDirectory(prefix="freqmed_r19_real_evidence_")
        home = Path(cls.dir.name)
        names = archive.ARTIFACTS[:-1]
        a = r16.audit(ROOT)
        b = r17.verify(ROOT, a)
        cls.paths = {name: home / name for name in names}
        cls.paths[names[0]].write_text(json.dumps(a), encoding="utf-8")
        cls.paths[names[1]].write_text(json.dumps(b), encoding="utf-8")
        c = r18.audit(ROOT, cls.paths[names[0]], cls.paths[names[1]])
        cls.paths[names[2]].write_text(json.dumps(c), encoding="utf-8")
        d = adversarial.audit(ROOT)
        cls.paths[names[3]].write_text(json.dumps(d), encoding="utf-8")
        cls.audit = d

    @classmethod
    def tearDownClass(cls):
        cls.dir.cleanup()

    def reject_source(self, before, after):
        self.assertEqual(1, SRC.count(before), "original C anchor drift")
        changed = SRC.replace(before, after, 1)
        with self.assertRaises(adversarial.AdversarialError):
            adversarial.inspect_source(changed)

    def evidence_copy(self, altered_name=None, changed=None):
        target = Path(self.dir.name)
        new_paths = {}
        for name, source in self.paths.items():
            path = target / ("TAMPER_" + name)
            value = source.read_bytes()
            if name == altered_name:
                d = json.loads(value.decode("utf-8"))
                changed(d)
                value = json.dumps(d).encode("utf-8")
            path.write_bytes(value)
            new_paths[name] = path
        return new_paths

    def test_actual_adversarial_baseline_is_pinned(self):
        self.assertEqual("SOURCE_ONLY_ADVERSARIAL_PASS", self.audit["verdict"])
        self.assertEqual(adversarial.PINNED_ACOUSTIC_SHA256,
                         self.audit["source_sha256"])
        self.assertGreaterEqual(self.audit["files_verified"], 103)

    def test_twelve_semantic_checks_present(self):
        self.assertEqual(12, self.audit["checks_passed"])
        self.assertEqual(12, len(set(self.audit["checks"])))

    def test_baseline_quarantine_and_ownership_sites(self):
        self.assertEqual(13, self.audit["exit_count"])
        self.assertEqual(4, self.audit["free_count"])
        self.assertEqual(6, self.audit["claim_release_count"])

    def test_public_entries_remain_unconditionally_denied(self):
        self.assertTrue(r17.public_denial(SRC, "fm_acoustic_physical_output"))
        em = (ROOT / "src/em_backend.c").read_text(encoding="utf-8")
        self.assertTrue(r17.public_denial(em, "fm_em_physical_output"))
        self.assertEqual(r17.LINK_C_ALLOWLIST, frozenset(r17.link_sources(RUN)))

    def test_all_ten_unresolved_limitations_preserved(self):
        self.assertEqual(set(adversarial.LIMITS),
                         set(self.audit["limitations"]))
        self.assertEqual("NONE", self.audit["scientific_simulation"])
        self.assertEqual("NONE", self.audit["physical_emission"])
        self.assertEqual("NOT_AUTHORIZED", self.audit["real_output"])

    def test_quiescence_disjunction_bypass_rejected(self):
        self.reject_source(
            "atomic_load(&ctx->dispose_confirmed) &&\n"
            "      !listener_registration_uncertain",
            "atomic_load(&ctx->dispose_confirmed) ||\n"
            "      !listener_registration_uncertain")

    def test_removed_callback_quiescence_guard_rejected(self):
        self.reject_source(
            "      !listener_remove_failed &&",
            "      !listener_remove_failed ||")

    def test_preprocessor_directive_in_controller_rejected(self):
        self.reject_source("AcousticContext *ctx=owner_ctx;",
                           "AcousticContext *ctx=owner_ctx;\n#define R19_OVERRIDE 1")

    def test_preprocessor_in_callback_rejected(self):
        self.reject_source(
            "AcousticContext *ctx=(AcousticContext*)ptr;",
            "AcousticContext *ctx=(AcousticContext*)ptr;\n#if 0\n#endif")

    def test_direct_dynamic_loader_bypass_rejected(self):
        self.reject_source("AcousticContext *ctx=owner_ctx;",
                           "AcousticContext *ctx=owner_ctx;\n  dlopen(0,0);")

    def test_unapproved_assembly_bypass_rejected(self):
        self.reject_source(
            "AcousticContext *ctx=(AcousticContext*)ptr;",
            "AcousticContext *ctx=(AcousticContext*)ptr;\n  __asm__(\"nop\");")

    def test_callback_queue_disposal_escape_rejected(self):
        self.reject_source(
            "AcousticContext *ctx=(AcousticContext*)ptr;",
            "AcousticContext *ctx=(AcousticContext*)ptr;\n"
            "  AudioQueueDispose(queue,true);")

    def test_extra_early_success_return_rejected(self):
        self.reject_source(
            "if (!request || request->channel!=FM_ACOUSTIC) return -1;",
            "if (!request || request->channel!=FM_ACOUSTIC) return 0;")

    def test_actual_source_evidence_recomputes_four_reports(self):
        files, table = archive.pack_inputs(ROOT, self.paths)
        self.assertEqual(set(archive.ARTIFACTS), set(files))
        self.assertGreaterEqual(len(table), 103)

    def test_local_archive_preserves_exact_evidence_bytes(self):
        folder, result = archive.create_archive(
            ROOT, self.paths, Path(self.dir.name), PARENT_PIN)
        self.assertEqual("PASS", result["verification"])
        self.assertEqual(6, result["files_verified"])
        for name, source in self.paths.items():
            self.assertEqual(source.read_bytes(), (folder / name).read_bytes())
        self.assertFalse(result["local_archive_is_immutable"])

    def test_local_archive_has_owner_private_permissions(self):
        folder, _ = archive.create_archive(
            ROOT, self.paths, Path(self.dir.name), PARENT_PIN)
        self.assertEqual(0o700, stat.S_IMODE(folder.stat().st_mode))
        for name in archive.EXPECTED_ARCHIVE:
            self.assertEqual(0o600,
                             stat.S_IMODE((folder / name).stat().st_mode))

    def test_local_archive_detects_byte_tampering(self):
        folder, _ = archive.create_archive(
            ROOT, self.paths, Path(self.dir.name), PARENT_PIN)
        path = folder / archive.ARTIFACTS[2]
        path.write_bytes(path.read_bytes() + b"\n")
        with self.assertRaises(archive.ArchiveError):
            archive.verify_archive(folder, expected_commit=PARENT_PIN)

    def test_local_archive_detects_added_unknown_file(self):
        folder, _ = archive.create_archive(
            ROOT, self.paths, Path(self.dir.name), PARENT_PIN)
        (folder / "UNKNOWN.txt").write_text("not a trusted evidence file")
        with self.assertRaises(archive.ArchiveError):
            archive.verify_archive(folder)

    def test_archive_refuses_a_rewritten_r17_report(self):
        changed = self.evidence_copy(
            archive.ARTIFACTS[1],
            lambda d: d.__setitem__("source_sha256", "0" * 64))
        with self.assertRaises(archive.ArchiveError):
            archive.pack_inputs(ROOT, changed)

    def test_real_mac_binary_refuses_emission_actions(self):
        exe = os.environ.get("FREQMED_GEN_R19_BINARY")
        if not exe:
            self.skipTest("Actual Mac Intel no-output binary required")
        status = subprocess.run([exe, "status"], capture_output=True,
                                text=True, timeout=5, check=True)
        info = json.loads(status.stdout)
        self.assertEqual("NONE", info["physical_emission"])
        self.assertEqual("NOT_LINKED_HARD_DENIED", info["acoustic_output"])
        self.assertEqual("BLOCKED_NO_QUALIFIED_EM_DEVICE",
                         info["electromagnetic_output"])
        for action in ("emit", "arm", "play", "transmit"):
            denial = subprocess.run([exe, action], capture_output=True,
                                    text=True, timeout=5)
            self.assertNotEqual(0, denial.returncode)
