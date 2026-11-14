#!/usr/bin/env python3
"""GEN-R19 durable local preservation of genuine R16/R17/R18/R19 evidence.

A SHA-256 consistency archive, NOT immutable storage, an external signature,
a signed timestamp, a certified physical measurement or a safety authorization.
No hardware access or scientific simulation. Python standard library only.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile

import r16_ownership_static_audit as r16
import r17_evidence_verifier as r17
import r18_control_flow_envelope as r18
import r19_adversarial_source_audit as r19

SCHEMA = "FREQMED_GEN_R19_LOCAL_EVIDENCE_ARCHIVE"
PINNED_COMMIT = "REPLACE_PINNED_COMMIT_AT_DELIVERY"
ARTIFACTS = (
    "GEN_R16_OWNERSHIP_EVIDENCE.json",
    "GEN_R17_VERIFIED_EVIDENCE.json",
    "GEN_R18_CONTROL_FLOW_EVIDENCE.json",
    "GEN_R19_ADVERSARIAL_EVIDENCE.json",
    "KIT_SHA256SUMS.txt",
)
INDEX = "EVIDENCE_INDEX.json"
CHECKSUMS = "EVIDENCE_SHA256SUMS.txt"
EXPECTED_ARCHIVE = set(ARTIFACTS) | {INDEX, CHECKSUMS}

class ArchiveError(ValueError):
    pass

def require(ok, reason):
    if not ok:
        raise ArchiveError(reason)

def digest(data):
    return hashlib.sha256(data).hexdigest()

def safe_read(path):
    path = Path(path)
    require(path.is_file() and not path.is_symlink(),
            "missing/symlinked evidence input " + path.name)
    fd = os.open(str(path), os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    try:
        size = os.fstat(fd).st_size
        require(0 < size <= 2000000, "evidence input size invalid")
        chunks = []
        while True:
            data = os.read(fd, 65536)
            if not data:
                break
            chunks.append(data)
        value = b"".join(chunks)
        require(len(value) == size, "evidence changed during read")
        return value
    finally:
        os.close(fd)

def parse_json(data):
    def unique(pairs):
        d = {}
        for key, value in pairs:
            require(key not in d, "duplicate JSON evidence key: " + key)
            d[key] = value
        return d
    try:
        return json.loads(data.decode("utf-8"), object_pairs_hook=unique)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ArchiveError("malformed UTF-8 JSON evidence") from exc

def pack_inputs(root, reports):
    """Recompute each source-only report, then seal its actual bytes."""
    root = Path(root).resolve()
    require(set(reports) == set(ARTIFACTS[:-1]),
            "four exact JSON reports required")
    manifest = safe_read(root / "KIT_SHA256SUMS.txt")
    table, manifest_sha = r17.manifest_integrity(root)
    require(manifest_sha == digest(manifest), "manifest source changed")
    blobs = {key: safe_read(reports[key]) for key in ARTIFACTS[:-1]}
    a, b, c, d = (parse_json(blobs[name]) for name in ARTIFACTS[:-1])
    try:
        require(a == r16.audit(root), "R16 report differs from real pinned source")
        require(b == r17.verify(root, a), "R17 report differs from source manifest")
        require(c == r18.audit(root, reports[ARTIFACTS[0]],
                              reports[ARTIFACTS[1]]),
                "R18 report detached from R16/R17 bytes")
        require(d == r19.audit(root), "R19 adversarial report not reproducible")
    except (ValueError, KeyError, TypeError, OSError) as exc:
        if isinstance(exc, ArchiveError):
            raise
        raise ArchiveError("failed closed on inconsistent evidence: " +
                           str(exc)) from exc
    require(len(table) >= 103, "GEN-R19 expected source file set incomplete")
    blobs["KIT_SHA256SUMS.txt"] = manifest
    return blobs, table

def create_archive(root, reports, parent):
    root = Path(root).resolve()
    parent = Path(parent).resolve()
    require(parent.is_dir() and not parent.is_symlink(),
            "destination parent must be a real existing directory")
    require(PINNED_COMMIT != "REPLACE_PINNED_COMMIT_AT_DELIVERY",
            "pinned GitHub commit was not finalized")
    blobs, table = pack_inputs(root, reports)
    folder = Path(tempfile.mkdtemp(
        prefix="FREQMED_GEN_R19_EVIDENCE_", dir=str(parent)))
    os.chmod(folder, 0o700)
    try:
        for name, data in blobs.items():
            target = folder / name
            fd = os.open(str(target), os.O_CREAT | os.O_EXCL | os.O_WRONLY |
                         getattr(os, "O_NOFOLLOW", 0), 0o600)
            try:
                with os.fdopen(fd, "wb") as out:
                    out.write(data)
                    out.flush()
                    os.fsync(out.fileno())
            except BaseException:
                raise
        index = {
            "schema": SCHEMA,
            "commit": PINNED_COMMIT,
            "files": {name: digest(blobs[name]) for name in sorted(blobs)},
            "source_files_verified": len(table),
            "source_sha256": table["src/acoustic_macos.c"],
            "evidence_count": 4,
            "method": "SHA256_SOURCE_BOUND_LOCAL_COPIES_NO_EXTERNAL_SIGNATURE",
            "source_output_backend": "COMPILED_ONLY_NOT_LINKED",
            "race_freedom": "NOT_PROVEN",
            "bureau_certification": "PENDING",
            "physical_emission": "NONE",
            "scientific_simulation": "NONE",
            "real_output": "NOT_AUTHORIZED",
            "production": "NOT_AUTHORIZED",
            "limitations": [
                "OWNER_CAN_EDIT_OR_DELETE_LOCAL_ARCHIVE",
                "NO_TRUSTED_TIMESTAMP_OR_EXTERNAL_SIGNATURE",
                "NO_FORMAL_COREAUDIO_CALLBACK_OR_C11_SAFETY_PROOF",
                "NO_PHYSICAL_MEASUREMENTS_OR_EM_HARDWARE_QUALIFICATION",
            ],
        }
        index_bytes = (json.dumps(index, sort_keys=True,
                        ensure_ascii=False, indent=2)+"\n").encode("utf-8")
        (folder / INDEX).write_bytes(index_bytes)
        os.chmod(folder / INDEX, 0o600)
        checks = dict(index["files"])
        checks[INDEX] = digest(index_bytes)
        checksum_bytes = ("".join(h + "  " + name + "\n"
                            for name, h in sorted(checks.items()))).encode("ascii")
        (folder / CHECKSUMS).write_bytes(checksum_bytes)
        os.chmod(folder / CHECKSUMS, 0o600)
        summary = verify_archive(folder)
        require(summary["files_verified"] == 6,
                "unexpected archive check count")
        return folder, summary
    except BaseException:
        shutil.rmtree(folder)
        raise

def verify_archive(folder):
    folder = Path(folder)
    require(folder.is_dir() and not folder.is_symlink(),
            "archive root missing or symlinked")
    actual = {p.name for p in folder.iterdir()}
    require(actual == EXPECTED_ARCHIVE, "archive file list mismatch")
    for name in actual:
        require((folder / name).is_file() and not (folder / name).is_symlink(),
                "archive symlink or nonregular file")
    lines = safe_read(folder / CHECKSUMS).decode("ascii").splitlines()
    require(len(lines) == 6, "archive manifest entry count invalid")
    entries = {}
    for line in lines:
        require(len(line) > 66 and line[64:66] == "  "
                and len(line[:64]) == 64
                and all(c in "0123456789abcdef" for c in line[:64]),
                "archive manifest row invalid")
        name = line[66:]
        require(name in EXPECTED_ARCHIVE and name != CHECKSUMS
                and name not in entries, "invalid/duplicate archive manifest name")
        entries[name] = line[:64]
    require(set(entries) == EXPECTED_ARCHIVE - {CHECKSUMS},
            "archive manifest missing or extra files")
    for name, expected in entries.items():
        require(digest(safe_read(folder / name)) == expected,
                "altered archived evidence: " + name)
    index = parse_json(safe_read(folder / INDEX))
    require(index.get("schema") == SCHEMA and index.get("commit") == PINNED_COMMIT,
            "archive commit or schema incorrect")
    require(index.get("files") == {
        name: entries[name] for name in ARTIFACTS
    }, "archived document hash index inconsistent")
    require(index.get("evidence_count") == 4
            and index.get("source_files_verified", 0) >= 103
            and index.get("physical_emission") == "NONE"
            and index.get("scientific_simulation") == "NONE"
            and index.get("real_output") == "NOT_AUTHORIZED"
            and index.get("production") == "NOT_AUTHORIZED"
            and index.get("bureau_certification") == "PENDING",
            "archived evidence governance claims altered")
    return {"schema": SCHEMA, "verification": "PASS",
            "files_verified": len(entries),
            "evidence_reports": 4,
            "commit": PINNED_COMMIT,
            "manifest_sha256": entries["KIT_SHA256SUMS.txt"],
            "local_archive_is_immutable": False}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path)
    p.add_argument("--r16", type=Path)
    p.add_argument("--r17", type=Path)
    p.add_argument("--r18", type=Path)
    p.add_argument("--r19", type=Path)
    p.add_argument("--destination-parent", type=Path)
    p.add_argument("--verify", type=Path)
    args = p.parse_args()
    try:
        if args.verify is not None:
            result = verify_archive(args.verify)
            folder = args.verify
        else:
            require(all([args.root, args.r16, args.r17, args.r18,
                         args.r19, args.destination_parent]),
                    "root, four evidence files and destination parent required")
            reports = dict(zip(ARTIFACTS[:-1],
                               (args.r16, args.r17, args.r18, args.r19)))
            folder, result = create_archive(args.root, reports,
                                            args.destination_parent)
    except (ArchiveError, OSError, ValueError, TypeError, KeyError) as exc:
        print("R19_EVIDENCE_PRESERVATION=FAIL_CLOSED", str(exc))
        return 2
    print("R19_EVIDENCE_PRESERVATION=PASS")
    print("R19_ARCHIVE_FILES_VERIFIED=%d; R19_EVIDENCE_REPORTS=%d" %
          (result["files_verified"], result["evidence_reports"]))
    print("R19_EVIDENCE_DIR=" + str(folder))
    print("R19_ARCHIVE_IMMUTABLE=NO; EXTERNAL_SIGNATURE=NONE")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
