#!/usr/bin/env python3
"""GEN-R22 independent *bounded* C11/CoreAudio source lifetime review.

Re-examines real pinned sources, R21's complete 11-gate JSON and the
historical owner R19 archive through re-computation. Software-only; neither
a C11 concurrency proof nor OS callback or physical-emission qualification.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

import r17_evidence_verifier as r17
import r19_evidence_archive as archive19
import r20_bureau_archive_review as r20
import r21_bureau_evidence_gaps as r21

SCHEMA = "FREQMED_GEN_R22_C11_COREAUDIO_LIFETIME_REVIEW"
VERDICT = "REVIEW_REQUIRED_NO_EMISSION"
GATE_IDS = (
    "C11_CALLBACK_RACE_FREEDOM",
    "ACTIVE_COREAUDIO_LIFETIME",
    "FAILED_OS_DISPOSAL_BEHAVIOR",
)
OPEN_FINDINGS = (
    ("C11_PCM_SINGLE_WRITER_NOT_PROVEN",
     "Non-atomic PCM fields are mutated by fill_audio; atomic_flag guards "
     "callback writers but independently establishing absence of controller/"
     "callback overlap needs a C11/OS happens-before proof."),
    ("CALLBACK_ENTRY_ACCOUNTING_WINDOW_UNPROVEN",
     "Atomic callback counters increment after the OS supplies the userdata "
     "pointer; observing zero does not by itself forbid a newly arriving callback "
     "after the check or prove safe heap reclamation."),
    ("FAILED_OS_DISPOSE_REAL_BEHAVIOR_UNTESTED",
     "Quarantine on unsuccessful AudioQueueDispose is source-visible but actual "
     "OS disposal failure, listener-removal ambiguity and callback quiescence "
     "have not been qualified on an approved non-emitting OS witness."),
)

class R22Error(ValueError):
    pass

def require(ok, message):
    if not ok:
        raise R22Error(message)

def sha(data):
    return hashlib.sha256(data).hexdigest()

def anchored(source, needle, source_hash):
    lines = source.splitlines()
    hits = [i + 1 for i, line in enumerate(lines) if needle in line]
    require(bool(hits), "missing expected real C anchor " + needle)
    return {"path": "src/acoustic_macos.c", "line": hits[0],
            "sha256": source_hash, "needle": needle}

def function_body(source, name):
    """Bounded brace extraction, not a C parser or interprocedural proof."""
    pattern = r"\b" + re.escape(name) + r"\s*\([^;{}]*\)\s*\{"
    occurrences = list(re.finditer(pattern, source, re.S))
    require(len(occurrences) == 1, "ambiguous C function definition: " + name)
    start = occurrences[0].end()
    depth = 1
    for i in range(start, len(source)):
        c = source[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return source[start:i]
    raise R22Error("unterminated function " + name)

def checks(source, runner):
    """17 bounded source contracts; each PASS is only a lexical observation."""
    output = function_body(source, "output_callback")
    listener = function_body(source, "queue_running_listener")
    pcm = function_body(source, "fill_audio")
    main = function_body(source, "acoustic_output_impl")
    public = function_body(source, "fm_acoustic_physical_output")
    whole = source
    data = []

    def check(identifier, condition, anchor):
        require(condition, "static contract failed: " + identifier)
        data.append((identifier, anchor))

    check("C11_ATOMIC_CALLBACK_FIELDS",
          "atomic_uint active_output_callbacks;" in whole
          and "atomic_uint active_property_listeners;" in whole
          and "atomic_flag pcm_writer_gate;" in whole,
          "atomic_uint active_output_callbacks;")
    check("C11_OUTPUT_ENTRY_COUNTED",
          "atomic_fetch_add_explicit(&ctx->active_output_callbacks" in output,
          "atomic_fetch_add_explicit(&ctx->active_output_callbacks")
    check("C11_OUTPUT_EXIT_COUNTED",
          "atomic_fetch_sub_explicit(&ctx->active_output_callbacks" in output,
          "atomic_fetch_sub_explicit(&ctx->active_output_callbacks")
    check("C11_LISTENER_ENTRY_COUNTED",
          "atomic_fetch_add_explicit(&ctx->active_property_listeners" in listener,
          "atomic_fetch_add_explicit(&ctx->active_property_listeners")
    check("C11_LISTENER_EXIT_COUNTED",
          "atomic_fetch_sub_explicit(&ctx->active_property_listeners" in listener,
          "atomic_fetch_sub_explicit(&ctx->active_property_listeners")
    check("C11_PCM_LOCK_ACQUIRE_AND_RELEASE",
          "atomic_flag_test_and_set_explicit(&ctx->pcm_writer_gate" in output
          and "memory_order_acquire" in output
          and "atomic_flag_clear_explicit(&ctx->pcm_writer_gate" in output
          and "memory_order_release" in output,
          "atomic_flag_test_and_set_explicit(&ctx->pcm_writer_gate")
    check("C11_OVERLAPPING_CALLBACK_FAIL_CLOSED",
          "FM_FAULT_OVERLAPPING_PCM_CALLBACK" in output
          and "fm_latch_first_fault" in output,
          "FM_FAULT_OVERLAPPING_PCM_CALLBACK")
    check("C11_NONATOMIC_PCM_STATE_IDENTIFIED",
          "ctx->phase+=" in pcm and "++ctx->frames_written" in pcm
          and "fill_audio(ctx,b)" in main
          and "fill_audio(ctx,buf)" in output,
          "ctx->phase+=")
    check("OS_CALLBACKS_USE_HEAP_OWNED_CONTEXT",
          "AcousticContext *owner_ctx=(AcousticContext*)calloc" in main
          and "AudioQueueNewOutput(&fmt,output_callback,ctx" in main
          and "queue_running_listener,ctx" in main,
          "AcousticContext *owner_ctx=(AcousticContext*)calloc")
    check("OS_CALLBACK_SHUTDOWN_GATED",
          "atomic_load(&ctx->shutdown_in_progress)" in output
          and "atomic_load(&ctx->shutdown_in_progress)" in listener
          and "atomic_exchange(&ctx->shutdown_in_progress,1)" in main,
          "atomic_exchange(&ctx->shutdown_in_progress,1)")
    check("DISPOSE_BIND_REJECTION_UNCERTAINTY_TRACKED",
          "const OSStatus bind_dispose_status=AudioQueueDispose(ctx->queue,true);" in main
          and "if (bind_dispose_status==noErr)" in main
          and "atomic_store_explicit(&fm_context_quarantined,1" in main,
          "const OSStatus bind_dispose_status=AudioQueueDispose(ctx->queue,true);")
    check("DISPOSE_LISTENER_REMOVAL_FAILURE_RECORDED",
          "listener_remove_failed=1;" in main
          and "FM_FAULT_LISTENER_REMOVAL" in main,
          "listener_remove_failed=1;")
    check("DISPOSE_TERMINAL_OS_ERROR_RECORDED",
          "if (AudioQueueDispose(ctx->queue,true)!=noErr)" in main
          and "FM_FAULT_DISPOSAL" in main,
          "if (AudioQueueDispose(ctx->queue,true)!=noErr)")
    check("DISPOSE_QUARANTINE_GUARDS_HEAP_RELEASE",
          "const int context_quiescent=" in main
          and "!listener_registration_uncertain" in main
          and "!listener_remove_failed" in main
          and "atomic_load(&ctx->dispose_confirmed)" in main
          and "free(owner_ctx);" in main
          and "atomic_store_explicit(&fm_context_quarantined,1" in main,
          "const int context_quiescent=")
    check("DISPOSE_BOTH_COUNTERS_CHECKED",
          "atomic_load_explicit(&ctx->active_output_callbacks" in main
          and "atomic_load_explicit(&ctx->active_property_listeners" in main,
          "const int context_quiescent=")
    check("PUBLIC_ACOUSTIC_OUTPUT_UNCONDITIONALLY_DENIED",
          re.sub(r"/\*.*?\*/|//[^\n]*", "", public, flags=re.S).strip()
          == "(void)command;\n  return -1;",
          "int fm_acoustic_physical_output")
    link = runner.split(' -o "$WORK/freqmed-gen"',1)
    clause = link[1].split("-framework CoreAudio",1)[0] if len(link)==2 else ""
    check("RUNNABLE_EXCLUDES_COREAUDIO_OUTPUT_BACKEND",
          "output_hard_denied.c" in clause
          and "acoustic_macos.c" not in clause
          and "R22_NONEMITTING_EXECUTABLE_SYMBOL_AUDIT=PASS" in runner,
          "int fm_acoustic_physical_output")
    require(len(data) == 17 and len(set(k for k, _ in data)) == 17,
            "bounded source check count/identifier mismatch")
    return data

def assess(root, source_text=None, runner_text=None):
    """Pure deterministic lexical review; optionally inspect software mutations."""
    root = Path(root)
    table, manifest_sha = r17.manifest_integrity(root)
    require(len(table) == 118, "R22 expected precisely 118 pinned generator sources")
    for path in ("audits/r22_coreaudio_lifetime_review.py",
                 "tests/test_r22_coreaudio_lifetime.py",
                 "RUN_GEN_R22_MAC_INTEL.command",
                 "docs/GEN_R22_C11_COREAUDIO_REVIEW.md",
                 "docs/GEN_R22_BUREAU_REVIEW.md"):
        require(path in table, "R22 component not pinned: " + path)
    for path, expected in (("src/acoustic_macos.c", r21.r19.PINNED_ACOUSTIC_SHA256),
                           ("src/em_backend.c", r21.r19.PINNED_EM_SHA256)):
        require(table[path] == expected, "physical backend source hash drift: " + path)
    source = (root / "src/acoustic_macos.c").read_text(encoding="utf-8")
    runner = (root / "RUN_GEN_R22_MAC_INTEL.command").read_text(encoding="utf-8")
    require(sha(source.encode("utf-8")) == table["src/acoustic_macos.c"],
            "pinned C source bytes mismatch")
    require(sha(runner.encode("utf-8")) == table["RUN_GEN_R22_MAC_INTEL.command"],
            "pinned R22 runner hash mismatch")
    data = checks(source if source_text is None else source_text,
                  runner if runner_text is None else runner)
    anchors = [{"id": key, "result": "STATIC_SOURCE_OBSERVED",
                "source": anchored(source, marker, table["src/acoustic_macos.c"])}
               for key, marker in data]
    return table, manifest_sha, anchors

def audit(root, archived_r19, report_paths, r21_json):
    root = Path(root).resolve()
    table, manifest_sha, anchors = assess(root)
    expected_r21 = r21.audit(root, archived_r19, report_paths)
    actual_r21 = archive19.parse_json(archive19.safe_read(r21_json))
    require(actual_r21 == expected_r21,
            "R21 evidence was altered or detached from sources/R19 archive")
    require(actual_r21["open_gates"] == 11
            and actual_r21["resolved_gates"] == 0
            and actual_r21["bureau_certification"] == "PENDING",
            "Bureau review has been silently promoted")
    first = actual_r21["gates"][:3]
    require([x["id"] for x in first] == list(GATE_IDS)
            and [x["status"] for x in first] == [
                "NOT_PROVEN", "NOT_TESTED", "NOT_TESTED"],
            "first three C11/CoreAudio gaps have changed status")
    return {
        "schema": SCHEMA,
        "verdict": VERDICT,
        "method": "BOUNDED_SOURCE_CODE_REVIEW_NOT_C11_MODEL_PROOF",
        "current_manifest_sha256": manifest_sha,
        "pinned_source_files": len(table),
        "acoustic_source_sha256": table["src/acoustic_macos.c"],
        "r21_evidence_sha256": sha(archive19.safe_read(r21_json)),
        "historical_r19_manifest_sha256": r20.R19_MANIFEST_SHA256,
        "source_contracts": anchors,
        "source_contracts_observed": len(anchors),
        "open_findings": [{"id": k, "explanation": reason, "status": "REVIEW_REQUIRED"}
                          for k, reason in OPEN_FINDINGS],
        "first_three_bureau_gates": first,
        "c11_race_freedom": "NOT_PROVEN",
        "active_coreaudio_callback_lifetime": "NOT_PROVEN",
        "actual_failed_os_disposal": "NOT_TESTED",
        "bureau_gates_open": 11,
        "bureau_gates_resolved": 0,
        "independent_reviewer_signatures": "NONE",
        "acoustic_output": "LOCKED", "em_output": "LOCKED",
        "physical_emission": "NONE", "scientific_simulation": "NONE",
        "biological_exposure": "NOT_AUTHORIZED",
        "real_output": "NOT_AUTHORIZED",
        "production": "NOT_AUTHORIZED",
        "bureau_certification": "PENDING",
    }

def markdown(report):
    tick = chr(96)
    rows = []
    for rec in report["source_contracts"]:
        source = rec["source"]
        rows.append("| " + rec["id"] + " | " + rec["result"] +
                    " | " + tick + source["path"] + ":" +
                    str(source["line"]) + tick + " |")
    findings = [("**"+rec["id"]+"** : "+rec["explanation"])
                for rec in report["open_findings"]]
    return ("# FREQMED GEN-R22 — Independent C11 / CoreAudio Lifetime Review\n\n"
            "Verdict : **REVIEW_REQUIRED_NO_EMISSION**. "
            "Ces contrôles sont purement statiques et bornés. "
            "**11 portes Bureau restent ouvertes, 0 résolue.**\n\n"
            "| Contrat source | Observation | Référence vérifiée |\n"
            "|---|---|---|\n" + "\n".join(rows) + "\n\n"
            "## Trois risques non certifiés\n\n" +
            "\n\n".join(findings) + "\n\n"
            "Les compteurs atomiques ne prouvent ni qu'un callback ne "
            "commencera plus ni que l'OS a fini tous les accès à userdata. "
            "Le drapeau d'écriture PCM ne prouve pas une sérialisation "
            "avec le thread de contrôle ; le comportement d'échec "
            "AudioQueueDispose n'a pas été observé sur appareil. "
            "La preuve de sécurité active, la qualification matérielle "
            "et les certifications indépendantes sont absentes.\n\n"
            "NEVER_SIMULATION=ENFORCED · ZERO_COST_FOSS=ENFORCED · "
            "ACOUSTIC_OUTPUT=LOCKED · EM_OUTPUT=LOCKED · "
            "REAL_OUTPUT=NOT_AUTHORIZED · PRODUCTION=NOT_AUTHORIZED\n")

def main():
    ap = argparse.ArgumentParser(description="GEN-R22 pinned C11 source-only review")
    ap.add_argument("--root", required=True, type=Path)
    ap.add_argument("--archive-r19", required=True, type=Path)
    for name in ("r16", "r17", "r18", "r19", "r20"):
        ap.add_argument("--" + name, required=True, type=Path)
    ap.add_argument("--r21", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument("--markdown", required=True, type=Path)
    args = ap.parse_args()
    try:
        paths = {n: getattr(args, n) for n in ("r16","r17","r18","r19","r20")}
        result = audit(args.root, args.archive_r19, paths, args.r21)
        args.output.write_text(json.dumps(result, sort_keys=True, indent=2,
                               ensure_ascii=False) + "\n", encoding="utf-8")
        args.markdown.write_text(markdown(result), encoding="utf-8")
    except (R22Error, ValueError, TypeError, KeyError, OSError,
            UnicodeError, IndexError) as ex:
        print("R22_C11_COREAUDIO_STATIC_REVIEW=FAIL_CLOSED", str(ex))
        return 2
    print("R22_C11_COREAUDIO_STATIC_REVIEW=PASS")
    print("R22_STATIC_OBSERVATIONS=17; R22_UNPROVEN_FINDINGS=3")
    print("R22_BUREAU_OPEN=11; R22_BUREAU_RESOLVED=0")
    print("R22_REVIEW_VERDICT=" + VERDICT)
    print("R22_C11_RACE_FREEDOM=NOT_PROVEN")
    print("R22_ACTIVE_COREAUDIO_LIFETIME=NOT_PROVEN")
    print("R22_ACTUAL_FAILED_OS_DISPOSAL=NOT_TESTED")
    print("R22_PHYSICAL_EMISSION=NONE; R22_SCIENTIFIC_SIMULATION=NONE")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
