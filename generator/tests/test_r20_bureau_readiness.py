"""GEN-R20 independent re-verification tests over genuine source-derived evidence.

Temporary archives are software integrity fixtures created from the *actual*
checked-out source, never simulated physical measurements or synthetic signals.
The owner's original R19 archive remains untouched.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "audits"))
import r16_ownership_static_audit as r16
import r17_evidence_verifier as r17
import r18_control_flow_envelope as r18
import r19_adversarial_source_audit as r19
import r19_evidence_archive as local_archive
import r20_bureau_archive_review as review

class R20BureauReview(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix="freqmed_r20_software_")
        cls.temp = Path(cls.tmp.name)
        cls.paths = {name: cls.temp / name
                     for name in local_archive.ARTIFACTS[:4]}
        a = r16.audit(ROOT)
        b = r17.verify(ROOT, a)
        cls.paths[local_archive.ARTIFACTS[0]].write_text(
            json.dumps(a), encoding="utf-8")
        cls.paths[local_archive.ARTIFACTS[1]].write_text(
            json.dumps(b), encoding="utf-8")
        c = r18.audit(ROOT, cls.paths[local_archive.ARTIFACTS[0]],
                      cls.paths[local_archive.ARTIFACTS[1]])
        cls.paths[local_archive.ARTIFACTS[2]].write_text(
            json.dumps(c), encoding="utf-8")
        d = r19.audit(ROOT)
        cls.paths[local_archive.ARTIFACTS[3]].write_text(
            json.dumps(d), encoding="utf-8")
        cls.folder, _ = local_archive.create_archive(
            ROOT, cls.paths, cls.temp, review.R19_COMMIT)
        cls.current_sha = hashlib.sha256(
            (ROOT/"KIT_SHA256SUMS.txt").read_bytes()).hexdigest()
        cls.count = len((ROOT/"KIT_SHA256SUMS.txt").read_text(
            encoding="utf-8").splitlines())

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def verify_copy(self, mutate, commit=None, manifest=None, count=None):
        target = self.temp / ("copy_" + str(
            len(tuple(self.temp.glob("copy_*")))))
        shutil.copytree(self.folder, target, symlinks=True)
        mutate(target)
        return review.verify_bundle(
            target, commit or review.R19_COMMIT,
            manifest or self.current_sha,
            count or self.count,
            ROOT/"src/acoustic_macos.c")

    @staticmethod
    def reseal(folder):
        """Reseal *software tamper fixture* to challenge semantic validation."""
        idx_path = folder / "EVIDENCE_INDEX.json"
        idx = json.loads(idx_path.read_text(encoding="utf-8"))
        for name in local_archive.ARTIFACTS:
            idx["files"][name] = hashlib.sha256((folder/name).read_bytes()).hexdigest()
        idx_path.write_text(json.dumps(idx, indent=2, sort_keys=True)+"\n",
                            encoding="utf-8")
        checksum = {}
        for name in local_archive.ARTIFACTS + (local_archive.INDEX,):
            checksum[name] = hashlib.sha256((folder/name).read_bytes()).hexdigest()
        (folder/local_archive.CHECKSUMS).write_text("".join(
            checksum[name]+"  "+name+"\n" for name in sorted(checksum)),
            encoding="ascii")

    def test_source_only_reviewer_has_fixed_original_r19_commit(self):
        self.assertEqual(
            "e77b1ff47a0748d4e91118a865e2681680fd9c31",
            review.R19_COMMIT)

    def test_original_r19_source_manifest_sha_is_fixed(self):
        self.assertEqual(
            "c80091fd6d22e8e8bef076b4565f5640be70c53268c4238aa8d264b1207dfb28",
            review.R19_MANIFEST_SHA256)

    def test_current_manifest_and_nonemitting_link_allowlist(self):
        table, sha = review.source_manifest(ROOT)
        self.assertEqual(sha, self.current_sha)
        self.assertEqual(self.count, len(table))
        runner = (ROOT/"RUN_GEN_R20_MAC_INTEL.command").read_text(encoding="utf-8")
        self.assertEqual(r17.LINK_C_ALLOWLIST,
                         frozenset(r17.link_sources(runner)))

    def test_four_genuine_current_source_reports_can_be_reverified(self):
        result = review.verify_bundle(
            self.folder, review.R19_COMMIT, self.current_sha, self.count,
            ROOT/"src/acoustic_macos.c")
        self.assertEqual(4, result["reports_verified"])
        self.assertEqual("R16_R17_R18_R19_REVERIFIED", result["evidence_chain"])

    def test_original_c_code_is_byte_identical_to_r19_pin(self):
        self.assertEqual(r19.PINNED_ACOUSTIC_SHA256,
                         hashlib.sha256((ROOT/"src/acoustic_macos.c").read_bytes()).hexdigest())
        self.assertEqual(r19.PINNED_EM_SHA256,
                         hashlib.sha256((ROOT/"src/em_backend.c").read_bytes()).hexdigest())

    def test_review_gates_are_explicitly_unapproved(self):
        self.assertEqual(11, len(review.UNRESOLVED))
        self.assertTrue(all(value not in ("PASS", "CERTIFIED", "AUTHORIZED")
                            for _, value in review.UNRESOLVED))

    def test_bureau_markdown_does_not_misrepresent_certification(self):
        draft = {
            "r19_verified": {"original_commit": review.R19_COMMIT,
                             "original_generator_files": review.R19_SOURCE_COUNT},
            "r20_source_files": self.count,
            "bureau_gates": [{"name": k, "status": v} for k, v in review.UNRESOLVED],
        }
        text = review.markdown_report(draft)
        self.assertIn("REVIEWABLE_NOT_CERTIFIED", text)
        self.assertIn("NO", text.upper())
        self.assertIn("NOT_AUTHORIZED", text)

    def test_original_r19_archive_remains_read_only(self):
        files_before = {
            name: (self.folder/name).read_bytes()
            for name in local_archive.EXPECTED_ARCHIVE}
        review.verify_bundle(self.folder, review.R19_COMMIT,
                             self.current_sha, self.count)
        self.assertEqual(files_before, {
            name: (self.folder/name).read_bytes()
            for name in local_archive.EXPECTED_ARCHIVE})

    def test_strict_old_r19_manifest_rejects_new_r20_archive(self):
        with self.assertRaises(review.ReviewError):
            review.verify_bundle(self.folder, review.R19_COMMIT,
                                 review.R19_MANIFEST_SHA256,
                                 review.R19_SOURCE_COUNT)

    def test_wrong_pinned_commit_is_rejected(self):
        with self.assertRaises(review.ReviewError):
            self.verify_copy(lambda folder: None,
                             commit="0"*40)

    def test_wrong_manifest_anchor_is_rejected(self):
        with self.assertRaises(review.ReviewError):
            self.verify_copy(lambda folder: None,
                             manifest="0"*64)

    def test_wrong_generator_file_count_is_rejected(self):
        with self.assertRaises(review.ReviewError):
            self.verify_copy(lambda folder: None,
                             count=self.count+1)

    def test_extra_untracked_file_is_rejected(self):
        with self.assertRaises(review.ReviewError):
            self.verify_copy(
                lambda f: (f/"UNTRACKED").write_text("untrusted software file"))

    def test_symlinked_archived_report_is_rejected(self):
        def alter(folder):
            name = local_archive.ARTIFACTS[0]
            path = folder/name
            path.unlink()
            path.symlink_to(self.folder/name)
        with self.assertRaises(review.ReviewError):
            self.verify_copy(alter)

    def test_byte_modified_archived_report_is_rejected(self):
        def alter(folder):
            path = folder/local_archive.ARTIFACTS[1]
            path.write_bytes(path.read_bytes()+b"\n")
        with self.assertRaises(review.ReviewError):
            self.verify_copy(alter)

    def test_resealed_fake_r16_pass_count_is_rejected(self):
        def alter(folder):
            path = folder/local_archive.ARTIFACTS[0]
            data = json.loads(path.read_text(encoding="utf-8"))
            data["passed"] = 24
            path.write_text(json.dumps(data), encoding="utf-8")
            self.reseal(folder)
        with self.assertRaises(review.ReviewError):
            self.verify_copy(alter)

    def test_resealed_fake_r17_source_count_is_rejected(self):
        def alter(folder):
            path = folder/local_archive.ARTIFACTS[1]
            data = json.loads(path.read_text(encoding="utf-8"))
            data["manifest_files_verified"] = 0
            path.write_text(json.dumps(data), encoding="utf-8")
            self.reseal(folder)
        with self.assertRaises(review.ReviewError):
            self.verify_copy(alter)

    def test_resealed_fake_r18_evidence_chain_is_rejected(self):
        def alter(folder):
            path = folder/local_archive.ARTIFACTS[2]
            data = json.loads(path.read_text(encoding="utf-8"))
            data["r16_r17_evidence_binding"] = "NOT_CHECKED"
            path.write_text(json.dumps(data), encoding="utf-8")
            self.reseal(folder)
        with self.assertRaises(review.ReviewError):
            self.verify_copy(alter)

    def test_resealed_fake_r19_limitations_are_rejected(self):
        def alter(folder):
            path = folder/local_archive.ARTIFACTS[3]
            data = json.loads(path.read_text(encoding="utf-8"))
            data["limitations"] = []
            path.write_text(json.dumps(data), encoding="utf-8")
            self.reseal(folder)
        with self.assertRaises(review.ReviewError):
            self.verify_copy(alter)

    def test_native_mac_binary_always_refuses_emission(self):
        path = os.environ.get("FREQMED_GEN_R20_BINARY")
        if not path:
            self.skipTest("requires actual Mac Intel hard-denied executable")
        status = subprocess.run([path, "status"], capture_output=True,
                                text=True, timeout=5, check=True)
        info = json.loads(status.stdout)
        self.assertEqual("NONE", info["physical_emission"])
        self.assertEqual("NOT_LINKED_HARD_DENIED", info["acoustic_output"])
        self.assertEqual("BLOCKED_NO_QUALIFIED_EM_DEVICE",
                         info["electromagnetic_output"])
        for command in ("emit", "arm", "play", "transmit"):
            response = subprocess.run([path, command], capture_output=True,
                                      text=True, timeout=5)
            self.assertNotEqual(0, response.returncode)
