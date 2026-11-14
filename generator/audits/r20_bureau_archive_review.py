#!/usr/bin/env python3
"""GEN-R20 independent, read-only reverification of owner's R19 evidence archive.

Checks original R19 archive against literal R19 commit + source/manifest digests,
not against the later R20 working tree. The Bureau dossier lists open gates.
No physical emissions, scientific simulation, hardware access, or certification.
Python 3 standard library only.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path

import r16_ownership_static_audit as r16
import r17_evidence_verifier as r17
import r18_control_flow_envelope as r18
import r19_adversarial_source_audit as r19
import r19_evidence_archive as old_archive

R19_COMMIT = "e77b1ff47a0748d4e91118a865e2681680fd9c31"
R19_MANIFEST_SHA256 = "c80091fd6d22e8e8bef076b4565f5640be70c53268c4238aa8d264b1207dfb28"
R19_SOURCE_COUNT = 103
SCHEMA = "FREQMED_GEN_R20_BUREAU_READINESS_EVIDENCE"
ALLOWED = frozenset(old_archive.EXPECTED_ARCHIVE)
REPORT_NAMES = tuple(old_archive.ARTIFACTS[:4])
UNRESOLVED = (
    ("C11_CALLBACK_RACE_FREEDOM", "NOT_PROVEN"),
    ("ACTIVE_COREAUDIO_LIFETIME", "NOT_TESTED"),
    ("FAILED_OS_DISPOSAL_BEHAVIOR", "NOT_TESTED"),
    ("INDEPENDENT_PHYSICAL_CUTOFF", "NOT_QUALIFIED"),
    ("ACOUSTIC_METROLOGY", "NOT_PERFORMED"),
    ("EM_HARDWARE_AND_METROLOGY", "NOT_QUALIFIED"),
    ("BIOLOGICAL_EXPOSURE", "NOT_AUTHORIZED"),
    ("MEDICAL_EFFICACY", "NOT_ESTABLISHED"),
    ("EXTERNAL_EVIDENCE_SIGNATURE", "ABSENT"),
    ("BUREAU_CERTIFICATION", "PENDING"),
    ("PRODUCTION", "NOT_AUTHORIZED"),
)
class ReviewError(ValueError):
    pass

def require(ok, reason):
    if not ok:
        raise ReviewError(reason)

def h(value):
    return hashlib.sha256(value).hexdigest()

def source_manifest(root):
    table, digest = r17.manifest_integrity(root)
    for required in ("RUN_GEN_R20_MAC_INTEL.command",
                     "audits/r20_bureau_archive_review.py",
                     "tests/test_r20_bureau_readiness.py",
                     "docs/GEN_R20_EVIDENCE_REVERIFICATION.md",
                     "docs/GEN_R20_BUREAU_READINESS.md"):
        require(required in table, "new source file not pinned: "+required)
    require(len(table) >= 108, "R20 generator source set incomplete")
    for name, expected in (
        ("src/acoustic_macos.c", r19.PINNED_ACOUSTIC_SHA256),
        ("src/em_backend.c", r19.PINNED_EM_SHA256)):
        require(table[name] == expected, "generation backend changed: "+name)
    runner = (Path(root) / "RUN_GEN_R20_MAC_INTEL.command").read_text(encoding="utf-8")
    current = r17.link_sources(runner)
    require(len(current) == len(r17.LINK_C_ALLOWLIST)
            and set(current) == r17.LINK_C_ALLOWLIST
            and "R20_NONEMITTING_EXECUTABLE_SYMBOL_AUDIT=PASS" in runner
            and "FREQMED_GEN_R20_BINARY" in runner,
            "R20 runnable output symbols/allowlist changed")
    return table, digest

def read_json(path):
    return old_archive.parse_json(old_archive.safe_read(path))

def verify_bundle(archive_dir, expected_commit, expected_manifest_sha,
                  expected_files, source=None):
    """Verify internal archive, anchored manifest, four evidence reports.

    This is an independently recomputable *content consistency* check:
    it does not authenticate who created or modified the local archive.
    """
    archive = Path(archive_dir)
    require(archive.is_dir() and not archive.is_symlink(),
            "archive missing or symlinked")
    require({p.name for p in archive.iterdir()} == ALLOWED,
            "archive entries have changed")
    try:
        base = old_archive.verify_archive(archive,
                                         expected_commit=expected_commit)
    except (old_archive.ArchiveError, OSError, ValueError) as ex:
        raise ReviewError("R19 archive integrity: "+str(ex)) from ex
    require(base["verification"] == "PASS" and base["files_verified"] == 6,
            "archive manifest integrity or count invalid")
    old_manifest = old_archive.safe_read(archive / "KIT_SHA256SUMS.txt")
    require(h(old_manifest) == expected_manifest_sha,
            "archived original manifest hash differs from trusted witness")
    text = old_manifest.decode("utf-8")
    rows = text.splitlines()
    require(len(rows) == expected_files,
            "archived manifest original file count incorrect")
    table = {}
    for line in rows:
        m = r17.MANIFEST_ROW.fullmatch(line)
        require(m is not None, "archived file hash syntax invalid")
        digest, path = m.groups()
        require(path not in table and ".." not in Path(path).parts,
                "duplicate/unsafe archived source path")
        table[path] = digest
    require(len(table) == expected_files, "duplicate pinned R19 sources")
    require(table.get("src/acoustic_macos.c") ==
            r19.PINNED_ACOUSTIC_SHA256, "acoustic pin drift")
    require(table.get("src/em_backend.c") ==
            r19.PINNED_EM_SHA256, "EM pin drift")
    index = read_json(archive / old_archive.INDEX)
    require(index["commit"] == expected_commit
            and index["source_sha256"] == r19.PINNED_ACOUSTIC_SHA256
            and index["source_files_verified"] == expected_files
            and index["evidence_count"] == 4
            and index["race_freedom"] == "NOT_PROVEN"
            and index["source_output_backend"] == "COMPILED_ONLY_NOT_LINKED"
            and index["bureau_certification"] == "PENDING"
            and index["physical_emission"] == "NONE"
            and index["scientific_simulation"] == "NONE"
            and index["real_output"] == "NOT_AUTHORIZED"
            and index["production"] == "NOT_AUTHORIZED",
            "archived index claims or exact source count changed")
    reports = {name: read_json(archive / name) for name in REPORT_NAMES}
    a, b, c, d = (reports[name] for name in REPORT_NAMES)
    require(a["schema"] == "FREQMED_GEN_R16_STATIC_OWNERSHIP_EVIDENCE"
            and a["verdict"] == "STATIC_SOURCE_CONTRACT_PASS"
            and a["method"] == "BOUNDED_C_TOKEN_AND_BRACE_AUDIT"
            and type(a["passed"]) is int and a["passed"] == 25
            and type(a["failed"]) is int and a["failed"] == 0,
            "R16 semantic claims not upheld")
    controls = a["checks"]
    require(type(controls) is list and len(controls) == 25
            and len(set(x["id"] for x in controls)) == 25
            and {x["id"] for x in controls} == r17.EXPECTED_IDS
            and all(x["result"] == "PASS" for x in controls)
            and set(a["unresolved"]) == r17.UNRESOLVED,
            "R16 check IDs/status/caveats inconsistent")
    require(b["schema"] == "FREQMED_GEN_R17_INDEPENDENT_EVIDENCE_VERIFICATION"
            and b["verification"] == "PASS"
            and b["manifest_sha256"] == expected_manifest_sha
            and b["source_sha256"] == r19.PINNED_ACOUSTIC_SHA256
            and b["static_checks_verified"] == 25
            and b["manifest_files_verified"] == expected_files,
            "R17 verifier detached from original manifest")
    canonical = json.dumps(a, ensure_ascii=False, sort_keys=True,
                           separators=(",", ":")).encode("utf-8")
    require(b["evidence_canonical_sha256"] == h(canonical),
            "R17 canonical R16 report hash mismatch")
    require(c["schema"] == r18.SCHEMA
            and c["verdict"] == "STATIC_CONTROL_FLOW_ENVELOPE_PASS"
            and c["source_sha256"] == r19.PINNED_ACOUSTIC_SHA256
            and c["manifest_sha256"] == expected_manifest_sha
            and c["r16_r17_evidence_binding"] == "PASS"
            and c["r16_evidence_sha256"] ==
                h(old_archive.safe_read(archive/REPORT_NAMES[0]))
            and c["r17_evidence_sha256"] ==
                h(old_archive.safe_read(archive/REPORT_NAMES[1]))
            and len(c["exit_sites"]) == 13
            and len(c["heap_free_sites"]) == 4
            and len(c["session_release_sites"]) == 6
            and c["formal_c_memory_safety"] == "NOT_PROVEN",
            "R18 evidence/control-flow binding inconsistent")
    require(d["schema"] == r19.SCHEMA
            and d["verdict"] == "SOURCE_ONLY_ADVERSARIAL_PASS"
            and d["source_sha256"] == r19.PINNED_ACOUSTIC_SHA256
            and d["em_source_sha256"] == r19.PINNED_EM_SHA256
            and d["manifest_sha256"] == expected_manifest_sha
            and d["files_verified"] == expected_files
            and type(d["checks_passed"]) is int
            and d["checks_passed"] == 13
            and len(d["checks"]) == 13 and len(set(d["checks"])) == 13
            and set(d["limitations"]) == set(r19.LIMITS)
            and d["physical_emission"] == "NONE"
            and d["scientific_simulation"] == "NONE"
            and d["real_output"] == "NOT_AUTHORIZED"
            and d["production"] == "NOT_AUTHORIZED",
            "R19 source adversarial claims inconsistent")

    # The R19 C sources remain byte-identical in the R20 pinned tree.
    # Re-run source-structure checks without reconstructing the old Git tree.
    if source is not None:
        source = Path(source)
        actual_bytes = old_archive.safe_read(source)
        require(h(actual_bytes) == r19.PINNED_ACOUSTIC_SHA256,
                "current C source no longer matches old recorded C bytes")
        expected_r16 = r16.audit(source.parent.parent)
        require(a == expected_r16,
                "R16 archived result not reproducible from identical C source")
        expected_r18 = r18.examine_source(actual_bytes.decode("utf-8"))
        for key in ("exit_sites", "exit_phases", "heap_free_sites",
                    "session_release_sites", "os_api_sites",
                    "quarantine_loads_acquire",
                    "quarantine_stores_release_one"):
            require(c[key] == expected_r18[key],
                    "R18 archived C structure differs: "+key)
        require(d["checks"] ==
                r19.inspect_source(actual_bytes.decode("utf-8"))["static_checks"],
                "R19 archived adversarial checks are not reproducible")
    return {
        "original_commit": expected_commit,
        "original_manifest_sha256": expected_manifest_sha,
        "original_generator_files": expected_files,
        "archive_files_checked": base["files_verified"],
        "reports_verified": len(REPORT_NAMES),
        "report_sha256": {name: h(old_archive.safe_read(archive/name))
                          for name in REPORT_NAMES},
        "evidence_chain": "R16_R17_R18_R19_REVERIFIED",
        "physical_emission": "NONE",
        "scientific_simulation": "NONE",
        "archive_immutable": False,
        "external_signature": "NONE",
    }

def audit(root, archived_r19):
    root = Path(root).resolve()
    table, manifest_sha = source_manifest(root)
    old = verify_bundle(archived_r19, R19_COMMIT, R19_MANIFEST_SHA256,
                        R19_SOURCE_COUNT, root/"src/acoustic_macos.c")
    gates = [{"name": k, "status": v} for k, v in UNRESOLVED]
    require(all(g["status"] not in ("PASS", "AUTHORIZED", "CERTIFIED")
                for g in gates), "Bureau readiness cannot self-certify")
    return {
        "schema": SCHEMA,
        "decision": "REVIEWABLE_NOT_CERTIFIED",
        "method": "READ_ONLY_ORIGINAL_ARCHIVE_REVERIFICATION",
        "r20_source_files": len(table),
        "r20_manifest_sha256": manifest_sha,
        "r19_verified": old,
        "bureau_gates": gates,
        "independent_bureau_signatures": "NONE",
        "c11_coreaudio_race_freedom": "NOT_PROVEN",
        "acoustic_output": "LOCKED",
        "em_output": "LOCKED",
        "physical_emission": "NONE",
        "scientific_simulation": "NONE",
        "real_output": "NOT_AUTHORIZED",
        "biological_exposure": "NOT_AUTHORIZED",
        "production": "NOT_AUTHORIZED",
        "roadmap_p001": "IN_PROGRESS",
        "governance_verdict": "BUREAU_REVIEW_REQUIRED",
    }

def markdown_report(data):
    gates = "\n".join("| "+g["name"]+" | "+g["status"]+" |"
                      for g in data["bureau_gates"])
    return ("# FREQMED GEN-R20 — Dossier de revue du Bureau (NON CERTIFIÉ)\n\n"
            "Archive R19 examinée en lecture seule ; commit exact : \`"+
            data["r19_verified"]["original_commit"]+"\`.\n\n"
            "Preuves R16–R19 vérifiées : **4/4**, sources historiques : **"+
            str(data["r19_verified"]["original_generator_files"])+
            "**. Fichiers du générateur R20 : **"+
            str(data["r20_source_files"])+"**.\n\n"
            "Verdict documentaire : **REVIEWABLE_NOT_CERTIFIED**.\n\n"
            "| Condition indépendante | État |\n|---|---|\n"+gates+"\n\n"
            "La cohérence des SHA-256 ne prouve ni l'identité de l'auteur, "
            "ni l'absence de race C11, ni la sécurité ou l'efficacité physique. "
            "L'archive R19 reste modifiable par son propriétaire, sans "
            "signature tierce ni horodatage certifié. Aucun accès à un "
            "générateur acoustique/EM n'a été autorisé.\n\n"
            "NEVER_SIMULATION=ENFORCED · ZERO_COST_FOSS=ENFORCED · "
            "REAL_OUTPUT=NOT_AUTHORIZED · PRODUCTION=NOT_AUTHORIZED\n")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--root", required=True, type=Path)
    p.add_argument("--archive-r19", required=True, type=Path)
    p.add_argument("--report", required=True, type=Path)
    p.add_argument("--review-md", required=True, type=Path)
    args = p.parse_args()
    try:
        result = audit(args.root, args.archive_r19)
        args.report.write_text(json.dumps(result, indent=2,
                           ensure_ascii=False, sort_keys=True)+"\n",
                           encoding="utf-8")
        args.review_md.write_text(markdown_report(result), encoding="utf-8")
    except (ReviewError, old_archive.ArchiveError, OSError, ValueError,
            TypeError, KeyError, UnicodeError) as ex:
        print("R20_ORIGINAL_R19_ARCHIVE_REVERIFICATION=FAIL_CLOSED", str(ex))
        return 2
    print("R20_ORIGINAL_R19_ARCHIVE_REVERIFICATION=PASS")
    print("R20_ORIGINAL_R19_FILES=%d; R20_REPORTS_REVERIFIED=%d" %
          (result["r19_verified"]["original_generator_files"],
           result["r19_verified"]["reports_verified"]))
    print("R20_BUREAU_READINESS=REVIEWABLE_NOT_CERTIFIED")
    print("R20_PHYSICAL_EMISSION=NONE; R20_SCIENTIFIC_SIMULATION=NONE")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
