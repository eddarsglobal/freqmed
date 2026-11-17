#!/usr/bin/env python3
"""GEN-R21: source-anchored, fail-closed 11-gate Bureau evidence gap review.

Documentary/software only. All gates stay unresolved. No active callbacks,
acoustic/EM emission, scientific simulation or synthetic measurements.
"""
import argparse
import hashlib
import json
from pathlib import Path

import r16_ownership_static_audit as r16
import r17_evidence_verifier as r17
import r18_control_flow_envelope as r18
import r19_adversarial_source_audit as r19
import r19_evidence_archive as archive19
import r20_bureau_archive_review as r20

SCHEMA = "FREQMED_GEN_R21_BUREAU_GAP_REGISTER"
VERDICT = "EVIDENCE_GAPS_MAPPED_NOT_CERTIFIED"
LIMITS = (
    "STATIC_SOURCE_REFERENCES_DO_NOT_PROVE_C11_RACE_FREEDOM",
    "ARCHIVE_HASHES_DO_NOT_AUTHENTICATE_OR_SIGN_AN_AUTHOR",
    "NO_ACTIVE_COREAUDIO_CALLBACK_OR_FAILED_OS_DISPOSAL_REPLAY",
    "NO_INDEPENDENT_PHYSICAL_CUTOFF_OR_ACOUSTIC_EM_MEASUREMENT",
    "NO_QUALIFIED_EM_INSTRUMENT_OR_BIOLOGICAL_EXPOSURE",
    "NO_MEDICAL_EFFICACY_OR_INDEPENDENT_BUREAU_CERTIFICATION",
)
# Reviewed against R20's exact 11 named unresolved gates.
# Source anchors prove code locations, never future scientific evidence.
SPEC = (
    ("C11_CALLBACK_RACE_FREEDOM", "B09", "SOFTWARE_AND_INDEPENDENT_REVIEW",
     "src/acoustic_macos.c", "atomic_uint active_output_callbacks;",
     "Formal C11/OS callback interleaving and memory-lifetime proof; external scrutiny"),
    ("ACTIVE_COREAUDIO_LIFETIME", "B07,B09", "NATIVE_OS_QUALIFICATION_REQUIRED",
     "src/acoustic_macos.c", "atomic_uint active_property_listeners;",
     "Independent real OS callback-lifetime and quiescence qualification; no live test authorized"),
    ("FAILED_OS_DISPOSAL_BEHAVIOR", "B07,B09", "NATIVE_OS_QUALIFICATION_REQUIRED",
     "src/acoustic_macos.c", "AudioQueueDispose",
     "Real OS-disposal failure-path evidence with OS-safe test authorization"),
    ("INDEPENDENT_PHYSICAL_CUTOFF", "B06,B10", "PHYSICAL_QUALIFICATION_REQUIRED",
     "src/em_qualification_gate.c", "fm_em_hardware_qualified_in_r11",
     "Independent hardware cutoff implementation, calibration and physical witness"),
    ("ACOUSTIC_METROLOGY", "B04,B07", "PHYSICAL_QUALIFICATION_REQUIRED",
     "src/acoustic_macos.c", "normalized_level",
     "Calibrated transducer, real pressure/level and traceable instrument measurement"),
    ("EM_HARDWARE_AND_METROLOGY", "B05,B06", "PHYSICAL_QUALIFICATION_REQUIRED",
     "src/em_qualification_gate.c", "FM_EM_DOCUMENTS_PRESENT_UNVERIFIED",
     "Manufacturer-specific qualified EM instrument, RF/EMC assessment and measured fields"),
    ("BIOLOGICAL_EXPOSURE", "B01,B02,B10", "AUTHORIZATION_NOT_GRANTED",
     "src/output_hard_denied.c", "return -1;",
     "Ethics/institutional authorization would be separate; currently exposure forbidden"),
    ("MEDICAL_EFFICACY", "B01,B03", "CLINICAL_EVIDENCE_UNAVAILABLE",
     "docs/GEN_R20_BUREAU_READINESS.md", "Efficacité médicale",
     "Independent clinical-quality evidence, not source code or generated frequencies"),
    ("EXTERNAL_EVIDENCE_SIGNATURE", "B09,B10", "EXTERNAL_ATTESTATION_REQUIRED",
     "audits/r19_evidence_archive.py", "NO_TRUSTED_TIMESTAMP_OR_EXTERNAL_SIGNATURE",
     "Authentic independent signing and trusted timestamp, not owner-rewritable SHA manifest"),
    ("BUREAU_CERTIFICATION", "B01,B02,B03,B04,B05,B06,B07,B08,B09,B10",
     "INDEPENDENT_BUREAU_VERDICT_REQUIRED",
     "docs/GEN_R20_BUREAU_READINESS.md", "REVIEWABLE_NOT_CERTIFIED",
     "Named authorized reviewers and explicit traced independent verdict on each prerequisite"),
    ("PRODUCTION", "B09,B10", "PRODUCTION_NOT_AUTHORIZED",
     "src/output_hard_denied.c", "fm_acoustic_physical_output",
     "Prior gates closed through independent evidence and explicit owner/Bureau authorization"),
)

class GapError(ValueError):
    pass

def require(ok, reason):
    if not ok:
        raise GapError(reason)

def digest(data):
    return hashlib.sha256(data).hexdigest()

def match_source(root, relative, needle, table):
    require(relative in table, "untracked source: " + relative)
    p = root / relative
    require(p.is_file() and not p.is_symlink(),
            "missing/symlinked source: " + relative)
    raw = p.read_bytes()
    require(digest(raw) == table[relative],
            "supporting source SHA mismatch: " + relative)
    lines = raw.decode("utf-8").splitlines()
    hits = [i + 1 for i, line in enumerate(lines) if needle in line]
    require(bool(hits), "missing source anchor " + relative + " / " + needle)
    return {"path": relative, "line": hits[0],
            "source_sha256": digest(raw), "anchor_text": needle}

def gate_register(root, table, original_gates):
    require(len(SPEC) == len(r20.UNRESOLVED) == 11, "11-gate drift")
    expected = dict(r20.UNRESOLVED)
    require(dict(original_gates) == expected and len(original_gates) == 11,
            "original R20 Bureau statuses differ from evidence")
    require([item[0] for item in SPEC] == list(expected),
            "R20 Bureau gate identifiers/order drift")
    out = []
    for gate, roles, category, relative, needle, required in SPEC:
        status = expected[gate]
        require(status not in ("PASS", "CERTIFIED", "AUTHORIZED"),
                "cannot promote unresolved gate")
        require(bool(required) and len(required) > 24, "missing proof requirement")
        out.append({
            "id": gate, "status": status,
            "state": "OPEN_EVIDENCE_GAP",
            "owner_roles": roles.split(","),
            "qualification_kind": category,
            "supporting_existing_source": match_source(root, relative, needle, table),
            "missing_evidence": required,
            "software_source_proves_physical_safety": False,
            "independent_certification": "NONE",
        })
    require(len(out) == 11 and len({x["id"] for x in out}) == 11,
            "missing or duplicated gap")
    return out

def evidence_chain(root, paths, archived_r19):
    """Recompute five actual JSON reports using pinned source and original archive."""
    names = ("r16", "r17", "r18", "r19", "r20")
    require(set(paths) == set(names), "five exact report paths required")
    docs = {name: archive19.parse_json(archive19.safe_read(paths[name]))
            for name in names}
    a, b, c, d, e = (docs[name] for name in names)
    require(a == r16.audit(root), "R16 report detached from source")
    require(b == r17.verify(root, a), "R17 report detached from source")
    require(c == r18.audit(root, paths["r16"], paths["r17"]),
            "R18 report detached from R16/R17/source")
    require(d == r19.audit(root), "R19 report detached from source")
    require(e == r20.audit(root, archived_r19),
            "R20 report detached from old R19 archive")
    require(e["decision"] == "REVIEWABLE_NOT_CERTIFIED"
            and e["governance_verdict"] == "BUREAU_REVIEW_REQUIRED"
            and len(e["bureau_gates"]) == 11,
            "R20 report cannot establish Bureau certification")
    require(e["r19_verified"]["original_commit"] == r20.R19_COMMIT
            and e["r19_verified"]["original_manifest_sha256"] == r20.R19_MANIFEST_SHA256
            and e["r19_verified"]["original_generator_files"] == 103
            and e["r19_verified"]["reports_verified"] == 4,
            "historical R19 archive custody lost")
    return docs

def audit(root, archived_r19, report_paths):
    root = Path(root).resolve()
    table, manifest_sha = r20.source_manifest(root)
    for required in ("audits/r21_bureau_evidence_gaps.py",
                     "tests/test_r21_evidence_gaps.py",
                     "RUN_GEN_R21_MAC_INTEL.command",
                     "docs/GEN_R21_EVIDENCE_GAPS.md",
                     "docs/GEN_R21_BUREAU_REVIEW.md"):
        require(required in table, "R21 file missing from manifest: " + required)
    require(len(table) >= 113, "R21 source set incomplete")
    runner = (root / "RUN_GEN_R21_MAC_INTEL.command").read_text(encoding="utf-8")
    linked = r17.link_sources(runner)
    require(len(linked) == len(r17.LINK_C_ALLOWLIST)
            and set(linked) == r17.LINK_C_ALLOWLIST
            and "R21_NONEMITTING_EXECUTABLE_SYMBOL_AUDIT=PASS" in runner
            and "FREQMED_GEN_R21_BINARY" in runner,
            "R21 link allowlist not hard denied")
    docs = evidence_chain(root, report_paths, archived_r19)
    inherited = [(entry["name"], entry["status"])
                 for entry in docs["r20"]["bureau_gates"]]
    gaps = gate_register(root, table, inherited)
    return {
        "schema": SCHEMA, "verdict": VERDICT,
        "method": "REAL_PINNED_SOURCE_AND_R16_R20_EVIDENCE_CROSS_REVIEW",
        "r21_manifest_sha256": manifest_sha,
        "r21_pinned_sources": len(table),
        "r19_original_commit": r20.R19_COMMIT,
        "r19_original_manifest_sha256": r20.R19_MANIFEST_SHA256,
        "historical_r19_reports": 4,
        "current_evidence_sha256": {
            key: digest(archive19.safe_read(report_paths[key]))
            for key in sorted(report_paths)
        },
        "gates": gaps, "open_gates": 11, "resolved_gates": 0,
        "limitations": list(LIMITS),
        "bureau_readiness": "REVIEWABLE_NOT_CERTIFIED",
        "bureau_certification": "PENDING",
        "independent_bureau_approval": "NONE",
        "c11_race_freedom": "NOT_PROVEN",
        "physical_emission": "NONE",
        "scientific_simulation": "NONE",
        "acoustic_output": "LOCKED", "em_output": "LOCKED",
        "real_output": "NOT_AUTHORIZED",
        "biological_exposure": "NOT_AUTHORIZED",
        "production": "NOT_AUTHORIZED",
    }

def markdown(data):
    tick = chr(96)
    header = ("# FREQMED GEN-R21 - Bureau : 11 lacunes, AUCUNE certifiée\n\n"
              "**Verdict : EVIDENCE_GAPS_MAPPED_NOT_CERTIFIED** ; "
              "**11 portes OPEN**, **0 résolue**. "
              "Sources et cinq rapports R16-R20 contrôlés. "
              "Archive R19 examinée en lecture seule.\n\n"
              "| Porte | Bureau | État | Référence réelle | Preuve manquante |\n"
              "|---|---|---|---|---|\n")
    rows = []
    for gate in data["gates"]:
        source = gate["supporting_existing_source"]
        rows.append("| " + gate["id"] + " | " +
                    ",".join(gate["owner_roles"]) + " | " +
                    gate["status"] + " | " + tick + source["path"] +
                    ":" + str(source["line"]) + tick + " | " +
                    gate["missing_evidence"] + " |")
    return (header + "\n".join(rows) + "\n\n"
            "Les références de code sont des traces existantes, PAS des "
            "mesures, autorisations ou preuves de sécurité. Les rôles du "
            "Bureau ne sont pas présumés occupés. Aucune signature inventée.\n\n"
            "**Aucune simulation scientifique, émission acoustique/EM, "
            "exposition biologique ou production n'est autorisée.**\n")

def main():
    ap = argparse.ArgumentParser(description="GEN-R21 source-only 11-gate Bureau review")
    ap.add_argument("--root", type=Path, required=True)
    ap.add_argument("--archive-r19", type=Path, required=True)
    for item in ("r16", "r17", "r18", "r19", "r20"):
        ap.add_argument("--" + item, type=Path, required=True)
    ap.add_argument("--json", type=Path, required=True)
    ap.add_argument("--markdown", type=Path, required=True)
    args = ap.parse_args()
    paths = {name: getattr(args, name) for name in
             ("r16", "r17", "r18", "r19", "r20")}
    try:
        result = audit(args.root, args.archive_r19, paths)
        args.json.write_text(json.dumps(result, indent=2, sort_keys=True,
                           ensure_ascii=False) + "\n", encoding="utf-8")
        args.markdown.write_text(markdown(result), encoding="utf-8")
    except (GapError, ValueError, KeyError, TypeError, OSError, UnicodeError) as ex:
        print("R21_BUREAU_GAP_REVIEW=FAIL_CLOSED", str(ex))
        return 2
    print("R21_BUREAU_GAP_REVIEW=PASS")
    print("R21_BUREAU_GATES=11; R21_OPEN=11; R21_RESOLVED=0")
    print("R21_BUREAU_VERDICT=" + VERDICT)
    print("R21_PHYSICAL_EMISSION=NONE; R21_SCIENTIFIC_SIMULATION=NONE")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
