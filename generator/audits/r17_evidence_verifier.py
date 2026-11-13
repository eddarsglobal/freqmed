#!/usr/bin/env python3
"""GEN-R17 independent verification of R16 source-evidence JSON.

Python standard library only. Reads actual pinned source and evidence.
No hardware access, measurement fabrication, science simulation or output.
Not a formal C concurrency, OS quiescence, or physical safety proof.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

class EvidenceError(ValueError):
    """Evidence rejected closed."""

EXPECTED_IDS = frozenset((
    "admission_claim_precedes_heap_allocation",
    "quarantine_checked_before_and_after_claim",
    "recheck_releases_unpublished_session_claim",
    "callback_context_is_heap_owned",
    "alloc_failure_releases_claim",
    "zero_frames_releases_unpublished_heap",
    "zero_fade_releases_unpublished_heap",
    "queue_creation_failure_quarantines_without_free",
    "rejected_route_disposes_synchronously",
    "binding_cleanup_checks_both_callback_counters",
    "binding_disposal_failure_never_frees",
    "listener_registration_failure_records_uncertainty",
    "listener_removal_failure_records_uncertainty",
    "callback_entry_exit_accounting",
    "callback_pcm_writer_gate",
    "callback_does_not_request_stop",
    "shutdown_barrier_precedes_listener_removal_and_dispose",
    "failed_disposal_retains_queue_and_heap",
    "successful_disposal_alone_confirms_and_clears",
    "final_release_requires_disposal_and_listener_clarity",
    "final_quarantine_keeps_context_and_claim",
    "every_heap_free_site_classified",
    "public_acoustic_entry_unconditionally_denied",
    "em_public_entry_unconditionally_denied",
    "runnable_excludes_output_backend",
))
UNRESOLVED = frozenset((
    "NO_FORMAL_C_CONCURRENCY_OR_MEMORY_MODEL_PROOF",
    "ACTIVE_COREAUDIO_CALLBACK_LIFETIME_UNTESTED",
    "ACTUAL_FAILED_OS_DISPOSAL_UNTESTED",
    "OS_CALLBACK_QUIESCENCE_NOT_ESTABLISHED_BY_COUNTERS_ALONE",
    "INDEPENDENT_HARDWARE_CUTOFF_NOT_QUALIFIED",
    "ACOUSTIC_AND_EM_METROLOGY_NOT_PERFORMED",
    "EM_INSTRUMENT_NOT_QUALIFIED",
    "BUREAU_CERTIFICATION_PENDING",
))
LINK_C_ALLOWLIST = frozenset((
    "main.c", "generator_core.c", "acoustic_probe_macos.c",
    "output_hard_denied.c", "em_backend.c",
    "em_hardware_discovery_macos.c",
))
MANIFEST_ROW = re.compile(r"^([0-9a-f]{64})  ([A-Za-z0-9_./-]+)$")
OUTPUT_SCHEMA = "FREQMED_GEN_R17_INDEPENDENT_EVIDENCE_VERIFICATION"

def require(condition, message):
    if not condition:
        raise EvidenceError(message)

def sha(data):
    return hashlib.sha256(data).hexdigest()

def digest(path):
    return sha(path.read_bytes())

def unique_json_pairs(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise EvidenceError("duplicate JSON key: " + str(key))
        out[key] = value
    return out

def read_evidence(path):
    path = Path(path)
    require(path.is_file() and not path.is_symlink(),
            "evidence path must be an existing regular non-symlink file")
    data = path.read_bytes()
    require(0 < len(data) <= 1000000, "invalid JSON evidence size")
    try:
        content = json.loads(data.decode("utf-8"),
                             object_pairs_hook=unique_json_pairs)
    except (UnicodeError, json.JSONDecodeError) as ex:
        raise EvidenceError("invalid JSON evidence") from ex
    require(isinstance(content, dict), "evidence JSON must be an object")
    return content

def manifest_integrity(root):
    """Independently check EVERY pinned generator file and tree parity."""
    root = Path(root).resolve()
    path = root / "KIT_SHA256SUMS.txt"
    rows = path.read_text(encoding="utf-8").splitlines()
    require(rows, "empty generator source manifest")
    table = {}
    for row in rows:
        found = MANIFEST_ROW.fullmatch(row)
        require(found is not None, "invalid manifest entry syntax")
        expected_hash, rel = found.groups()
        relative = Path(rel)
        require(not relative.is_absolute() and ".." not in relative.parts
                and rel not in table, "unsafe or duplicate manifest entry")
        file = root / relative
        require(file.is_file() and not file.is_symlink(),
                "missing or symlinked generator source: " + rel)
        require(digest(file) == expected_hash,
                "source SHA-256 mismatch: " + rel)
        table[rel] = expected_hash
    actual = {
        file.relative_to(root).as_posix()
        for file in root.rglob("*") if file.is_file()
        and file.name != "KIT_SHA256SUMS.txt"
        and "__pycache__" not in file.parts
        and file.suffix not in (".pyc", ".pyo")
    }
    require(set(table) == actual, "generator tree differs from manifest")
    return table, digest(path)

def stripped_c(code):
    # Independent check for two tiny exported API bodies; NOT a full C parser.
    no_comments = re.sub(r"/\*[\s\S]*?\*/|//[^\n]*", "", code)
    return no_comments

def public_denial(code, name):
    source = stripped_c(code)
    found = re.search(r"\bint\s+" + re.escape(name) +
                      r"\s*\([^;{}]*\)\s*\{", source)
    require(found is not None, "public output function missing: " + name)
    close = source.find("}", found.end())
    require(close >= 0, "public output function unterminated: " + name)
    body = source[found.end():close]
    return bool(re.fullmatch(
        r"\s*\(\s*void\s*\)\s*command\s*;\s*return\s+-1\s*;\s*",
        body))

def link_sources(runner):
    # The native executable's EXACT source allowlist is independent of R16.
    source = runner.split(' -o "$WORK/freqmed-gen"', 1)
    require(len(source) == 2, "native executable link command missing")
    remainder = source[1].split("-framework CoreAudio", 1)
    require(len(remainder) == 2, "native executable link boundary missing")
    return re.findall(r'\$ROOT/src/([A-Za-z0-9_]+\.c)"', remainder[0])

def verify(root, evidence):
    """Reject missing, altered or detached evidence; return hash-bound verdict."""
    root = Path(root).resolve()
    require(isinstance(evidence, dict), "invalid evidence type")
    needed = {"schema", "source", "source_sha256", "method",
              "analysis_scope", "checks", "passed", "failed",
              "unresolved", "scientific_simulation", "physical_emission",
              "real_output", "production", "verdict"}
    require(set(evidence) == needed, "unexpected or missing evidence keys")
    require(evidence["schema"] == "FREQMED_GEN_R16_STATIC_OWNERSHIP_EVIDENCE",
            "invalid R16 evidence schema")
    require(evidence["source"] == "src/acoustic_macos.c",
            "unexpected source path")
    require(evidence["method"] == "BOUNDED_C_TOKEN_AND_BRACE_AUDIT"
            and evidence["analysis_scope"] == "SOURCE_ONLY_NON_EMITTING",
            "unsupported analysis method or scope")
    require(evidence["verdict"] == "STATIC_SOURCE_CONTRACT_PASS",
            "upstream R16 auditor did not pass")

    table, manifest_sha = manifest_integrity(root)
    require(len(table) >= 87, "unexpectedly small pinned generator tree")
    for expected_path in ("src/acoustic_macos.c", "src/em_backend.c",
                          "RUN_GEN_R17_MAC_INTEL.command",
                          "RUN_GEN_R16_MAC_INTEL.command",
                          "audits/r16_ownership_static_audit.py",
                          "audits/r17_evidence_verifier.py",
                          "tests/test_r17_evidence_integrity.py"):
        require(expected_path in table,
                "required pinned file absent: " + expected_path)
    source_file = root / "src/acoustic_macos.c"
    require(evidence["source_sha256"] == table["src/acoustic_macos.c"],
            "R16 evidence detached from pinned C source")
    require(evidence["source_sha256"] == digest(source_file),
            "R16 C source digest mismatch")

    checks = evidence["checks"]
    require(isinstance(checks, list) and len(checks) == len(EXPECTED_IDS),
            "incomplete or extra static checks")
    names = []
    source_line_count = len(source_file.read_text(encoding="utf-8").splitlines())
    for record in checks:
        require(isinstance(record, dict)
                and set(record) == {"id", "result", "source_line", "basis"},
                "invalid static check record")
        require(isinstance(record["id"], str),
                "invalid static check identifier")
        names.append(record["id"])
        require(record["result"] == "PASS"
                and record["basis"] == "STATIC_C_TOKENS",
                "failed or untrusted static check")
        line = record["source_line"]
        require(type(line) is int and 1 <= line <= source_line_count,
                "source line is not in pinned C source")
    require(set(names) == EXPECTED_IDS and len(names) == len(set(names)),
            "unexpected, missing or duplicated check IDs")
    require(type(evidence["passed"]) is int
            and evidence["passed"] == len(EXPECTED_IDS)
            and type(evidence["failed"]) is int
            and evidence["failed"] == 0,
            "check counters inconsistent")
    unresolved = evidence["unresolved"]
    require(isinstance(unresolved, list)
            and all(isinstance(x, str) for x in unresolved)
            and len(unresolved) == len(UNRESOLVED)
            and set(unresolved) == UNRESOLVED,
            "unresolved safety caveats removed or modified")
    for key, expected in (
        ("scientific_simulation", "NONE"), ("physical_emission", "NONE"),
        ("real_output", "NOT_AUTHORIZED"), ("production", "NOT_AUTHORIZED")):
        require(evidence[key] == expected, "unauthorized claim: " + key)

    acoustic_c = source_file.read_text(encoding="utf-8")
    em_c = (root / "src/em_backend.c").read_text(encoding="utf-8")
    require(public_denial(acoustic_c, "fm_acoustic_physical_output"),
            "acoustic API is not unconditionally hard-denied")
    require(public_denial(em_c, "fm_em_physical_output"),
            "EM API is not unconditionally hard-denied")
    runner = (root / "RUN_GEN_R17_MAC_INTEL.command").read_text(encoding="utf-8")
    found = link_sources(runner)
    require(len(found) == len(LINK_C_ALLOWLIST)
            and set(found) == LINK_C_ALLOWLIST,
            "native executable source allowlist changed")
    require("R17_NONEMITTING_EXECUTABLE_SYMBOL_AUDIT=PASS" in runner,
            "no output symbol audit asserted by R17 runner")
    require("FREQMED_GEN_R16_BINARY" in runner
            and "FREQMED_GEN_R17_BINARY" in runner,
            "historical and new non-emitting binary bindings missing")

    payload = json.dumps(evidence, ensure_ascii=False, sort_keys=True,
                         separators=(",", ":")).encode("utf-8")
    return {
        "schema": OUTPUT_SCHEMA,
        "verification": "PASS",
        "method": "INDEPENDENT_SOURCE_AND_JSON_INTEGRITY",
        "static_checks_verified": len(EXPECTED_IDS),
        "manifest_files_verified": len(table),
        "manifest_sha256": manifest_sha,
        "evidence_canonical_sha256": sha(payload),
        "source_sha256": digest(source_file),
        "auditor_r16_sha256": table["audits/r16_ownership_static_audit.py"],
        "verifier_r17_sha256": table["audits/r17_evidence_verifier.py"],
        "runner_r17_sha256": table["RUN_GEN_R17_MAC_INTEL.command"],
        "unresolved": sorted(UNRESOLVED),
        "physical_emission": "NONE",
        "scientific_simulation": "NONE",
        "real_output": "NOT_AUTHORIZED",
        "production": "NOT_AUTHORIZED",
        "bureau_certification": "PENDING",
        "c_concurrency_race_freedom": "NOT_PROVEN",
    }

def main():
    parser = argparse.ArgumentParser(description="FREQMED GEN-R17 evidence verifier")
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--evidence", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        evidence = read_evidence(args.evidence)
        report = verify(args.root, evidence)
        if args.output:
            require(not args.output.is_symlink(), "symlinked output forbidden")
            args.output.write_text(json.dumps(report, indent=2,
                                   ensure_ascii=False, sort_keys=True)+"\n",
                                   encoding="utf-8")
    except (EvidenceError, OSError, ValueError, TypeError, KeyError) as exc:
        print("R17_INDEPENDENT_EVIDENCE_VERIFIER=FAIL_CLOSED", str(exc))
        return 2
    print("R17_INDEPENDENT_EVIDENCE_VERIFIER=PASS")
    print("R17_STATIC_CHECKS_VERIFIED=%d" % report["static_checks_verified"])
    print("R17_PINNED_FILES_VERIFIED=%d" % report["manifest_files_verified"])
    print("R17_COREAUDIO_RACE_FREEDOM=NOT_PROVEN")
    print("R17_PHYSICAL_EMISSION=NONE; R17_SCIENTIFIC_SIMULATION=NONE")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
