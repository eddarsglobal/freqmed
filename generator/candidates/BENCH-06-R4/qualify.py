#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Consolidate retained owner evidence; never run a historical executable."""
import hashlib
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent
EVIDENCE_PIN = "a4af3c539898d78cdda498d46cee50412f3bcab3"
STAGES = ("BENCH-01", "BENCH-02", "BENCH-03 FIX1", "BENCH-04",
          "BENCH-05 FIX1", "BENCH-06 R1", "BENCH-06 R2", "BENCH-06 R3")
LOGS = (
    ("R1", "FREQMED_BENCH06_MAC.log", "BENCH06_REPORT=", (
        "BENCH06_SOURCE_PINS=8/8 PASS", "BENCH06_LAYOUT_ASSERTIONS=13 PASS",
        "BENCH06_NATIVE_DESCRIPTOR_CAPTURE=PASS", "BENCH06_PHYSICAL_ADMISSION=HARD_DENIED")),
    ("R2", "FREQMED_BENCH06_R2_MAC.log", "BENCH06_R2_NATIVE_REPORT=", (
        "BENCH06_R2_SOURCE_PINS=38/38 PASS", "BENCH06_R2_RESOURCE_ASSERTIONS=31 PASS",
        "BENCH06_R2_NATIVE_RESOURCE=PASS", "BENCH06_R2_PHYSICAL_ADMISSION=HARD_DENIED")),
    ("R3", "FREQMED_BENCH06_R3_MAC.log", "BENCH06_R3_NATIVE_REPORT=", (
        "BENCH06_R3_SOURCE_PINS=41/41 PASS", "BENCH06_R3_INTERLOCK_ASSERTIONS=28 PASS",
        "BENCH06_R3_NATIVE_BACKEND=PASS", "BENCH06_R3_PHYSICAL_ADMISSION=HARD_DENIED")),
)
BLOCKERS = {
    "G0": "Independent review and licensing closure not attested",
    "G2": "Qualified nonbiological hardware, physical limits and interlocks missing",
    "G3": "Specific bench authorization missing",
    "INDEPENDENT_STOP": "Hardware stop and independent witness missing",
    "METROLOGY": "Calibrated independent instrument and uncertainty missing",
    "RT_QUIESCENCE": "Actual callback/stream timing and hardware quiescence unproven",
    "BACKEND": "Physical stream adapter not implemented in these candidates",
}

def require(condition, message):
    if not condition:
        raise RuntimeError(message)

def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args], timeout=30)

def blob(data):
    return hashlib.sha1(("blob %d" % len(data)).encode() + b"\0" + data).hexdigest()

def load_evidence(repo):
    raw = (ROOT / "evidence.json").read_bytes()
    require(blob(raw) == EVIDENCE_PIN, "EVIDENCE_BLOB_MISMATCH")
    e = json.loads(raw)
    require(e["schema"] == "freqmed.bench-06-r4.evidence.v1", "SCHEMA")
    require(tuple(r["stage"] for r in e["records"]) == STAGES, "STAGES")
    require(len({r["commit"] for r in e["records"]}) == 8, "DUPLICATE_COMMIT")
    require(len({r["comment_id"] for r in e["records"]}) == 8, "DUPLICATE_COMMENT")
    for r in e["records"]:
        require(re.fullmatch("[0-9a-f]{40}", r["commit"]), "COMMIT_FORMAT")
        require(r["commit"] in r["body"], "COMMENT_SOURCE_MISMATCH")
        require(r["provenance"] == "OWNER_REPORTED_ASSISTANT_TRANSCRIBED_NOT_INDEPENDENT", "PROVENANCE")
        git(repo, "cat-file", "-e", r["commit"] + "^{commit}")
        git(repo, "merge-base", "--is-ancestor", r["commit"], e["base"])
    require(e["base"] == e["records"][-1]["commit"], "BASE")
    road = e["roadmap"]
    require(git(repo, "rev-parse", "origin/main").decode().strip() == road["commit"], "ROADMAP_HEAD_CHANGED")
    require(blob(git(repo, "show", road["commit"] + ":RoadMap.md")) == road["blob"], "ROADMAP_BLOB")
    git(repo, "merge-base", "--is-ancestor", road["commit"], e["base"])
    return e

def verify_report(stage, report):
    require(report["audio_ioproc_registered"] is False and report["stream_opened"] is False
            and report["physical_output"] == "NOT_PERFORMED" and report["authorization"] == "NONE",
            stage + "_SCOPE")
    if stage == "R1":
        require(report["metadata_stable"] is True and report["output_float32_layout_candidate"] is True
                and report["pair_binding"] == "READONLY_PAIR_CANDIDATE"
                and report["activation"] == "HARD_DENIED"
                and report["physical_backend_available"] is False
                and report["configuration_sha256"] == "02dd8da04ea9cb809e273b177895e5b81031d576396e1e30d25f5be831e5be5a",
                "R1_PROFILE")
    else:
        require(report["guardian_off"] is True and report["resources_closed"] is True
                and report["registered"] == report["removed"] == 9
                and report["property_change_observed"] is False and report["reason"] == "NONE"
                and report["destination"] == "PRIVATE_RAM_ONLY"
                and report["nominal_rate_hz"] == 44100 and report["frames"] == 512
                and report["channels"] == 2 and report["blocks"] == 2
                and report["numerical_frames"] == 1024 and report["float_values"] == 2048,
                stage + "_RESOURCE")
        if stage == "R2":
            require(report["status"] == "PASS_PRIVATE_OUTPUT_RESOURCE", "R2_STATUS")
        else:
            require(report["status"] == "PASS_PRIVATE_BACKEND_INTERLOCK"
                    and report["stop_verified_software"] is True
                    and report["native_abi_denied"] is True and report["interlock_reasons"] == 1
                    and report["independent_physical_stop"] == "NOT_VERIFIED", "R3_INTERLOCK")

def verify_log(folder, stage, filename, prefix, markers):
    path = folder / filename
    with path.open("rb") as stream:
        raw = stream.read(2_000_001)
    require(len(raw) <= 2_000_000, stage + "_LOG_TOO_LARGE")
    lines = raw.decode("utf-8").splitlines()
    require(all(lines.count(marker) == 1 for marker in markers), stage + "_MARKERS")
    reports = [line[len(prefix):] for line in lines if line.startswith(prefix)]
    require(len(reports) == 1, stage + "_REPORT_COUNT")
    verify_report(stage, json.loads(reports[0]))
    return {"stage": stage, "file": filename, "sha256": hashlib.sha256(raw).hexdigest(),
            "status": "CONSISTENT_WITH_OWNER_REPORT", "independent_authentication": "NONE"}

def main():
    if len(sys.argv) != 4:
        raise SystemExit("USAGE: python3 -B qualify.py REPO LOG_DIR OUTPUT_JSON")
    repo = pathlib.Path(sys.argv[1]).resolve(strict=True)
    logs = pathlib.Path(sys.argv[2]).resolve(strict=True)
    output = pathlib.Path(sys.argv[3])
    e = load_evidence(repo)
    print("BENCH06_R4_EVIDENCE_RECORDS=8/8 PASS", flush=True)
    print("BENCH06_R4_REMEDIATION_RECORDS=%d" % len(e["remediation_history"]), flush=True)
    results = []
    for stage, name, prefix, markers in LOGS:
        try:
            result = verify_log(logs, stage, name, prefix, markers)
        except (OSError, ValueError, KeyError, TypeError, RuntimeError) as exc:
            result = {"stage": stage, "file": name, "status": "BLOCK", "reason": str(exc)}
        results.append(result)
        print("BENCH06_R4_LOG_" + stage + "=" + result["status"], flush=True)
    ok = all(r["status"] == "CONSISTENT_WITH_OWNER_REPORT" for r in results)
    report = {"schema": "freqmed.bench-06-r4.decision.v1", "roadmap": e["roadmap"],
              "base": e["base"], "evidence_blob": EVIDENCE_PIN, "historical_records": len(e["records"]),
              "historical_log_scope": "R1_R2_R3_ONLY", "local_logs": results,
              "consolidation": "PASS" if ok else "BLOCK",
              "physical_admission": "HARD_DENIED", "physical_backend_available": False,
              "independent_certification": "NOT_ISSUED", "blockers": BLOCKERS,
              "historical_tests_repeated": "NONE", "build": "NONE", "installation": "NONE",
              "physical_output": "NOT_PERFORMED", "independent_stop": "NOT_VERIFIED"}
    with output.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2, sort_keys=True)
        stream.write("\n")
    print("BENCH06_R4_CONSOLIDATION=" + report["consolidation"], flush=True)
    print("BENCH06_R4_PHYSICAL_ADMISSION=HARD_DENIED", flush=True)
    print("BENCH06_R4_DECISION=" + str(output), flush=True)
    return 0 if ok else 75

if __name__ == "__main__":
    raise SystemExit(main())
