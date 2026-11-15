#!/usr/bin/env python3
"""GEN-R23: source-grounded C11 happens-before and quiescence obligations.

This is a bounded independent documentary/source review, NOT a concurrency
proof, active CoreAudio callback experiment, scientific simulation, or device
emission. Exact R16-R22 evidence is recomputed from owner-pinned sources.
"""
import argparse
import hashlib
import json
from pathlib import Path

import r17_evidence_verifier as r17
import r19_adversarial_source_audit as r19
import r19_evidence_archive as archive19
import r21_bureau_evidence_gaps as r21
import r22_coreaudio_lifetime_review as r22

SCHEMA = "FREQMED_GEN_R23_C11_HAPPENS_BEFORE_QUIESCENCE_OBLIGATIONS"
VERDICT = "PROOF_OBLIGATIONS_OPEN_NO_EMISSION"
GATES = r22.GATE_IDS
LIMITS = (
    "NO_FORMAL_C11_HAPPENS_BEFORE_PROOF",
    "NO_OS_CALLBACK_REGISTRATION_OR_DISPOSAL_QUIESCENCE_WITNESS",
    "NO_ACTIVE_AUDIOQUEUE_OR_PHYSICAL_DEVICE_ACCESS",
    "NO_SCIENTIFIC_SIMULATION_OR_FABRICATED_MEASUREMENT",
    "SOURCE_LOCATIONS_ARE_NOT_DERIVED_THREAD_INTERLEAVINGS",
    "NO_EXTERNAL_SIGNATURE_INDEPENDENT_CERTIFICATION_OR_PRODUCTION",
)

class R23Error(ValueError):
    pass

def require(condition, text):
    if not condition:
        raise R23Error(text)

def sha(data):
    return hashlib.sha256(data).hexdigest()

def order(body, *needles):
    """Textual source order observation only; not happens-before."""
    positions = []
    for word in needles:
        at = body.find(word)
        require(at >= 0, "missing source sequence: " + word)
        positions.append(at)
    return positions == sorted(positions) and len(set(positions)) == len(positions)

def obligations(source, runner, expected_sha):
    """15 fixed obligations, real code anchors, all proof_status=OPEN."""
    # Retain the exact 17 R22 observations with their ORIGINAL R22 runner.
    # R22 checks its own R22-specific symbol-audit marker; R23 separately
    # checks the new R23 runner allowlist/marker in assess(). Both are pinned.
    legacy = (Path(__file__).resolve().parents[1] /
              "RUN_GEN_R22_MAC_INTEL.command").read_text(encoding="utf-8")
    inherited = r22.checks(source, legacy)
    require(len(inherited) == 17, "R22 source-contract baseline drift")
    require("R23_NONEMITTING_EXECUTABLE_SYMBOL_AUDIT=PASS" in runner,
            "R23 source review missing current non-emission marker")
    out = r22.function_body(source, "output_callback")
    listener = r22.function_body(source, "queue_running_listener")
    pcm = r22.function_body(source, "fill_audio")
    controller = r22.function_body(source, "acoustic_output_impl")

    records = []
    def add(identifier, gate, roles, condition, anchors, required):
        require(gate in GATES, "unknown R23 Bureau gate " + gate)
        require(condition, "R23 source witness changed: " + identifier)
        require(len(anchors) == 2 and len(required) > 60,
                "incomplete R23 obligation: " + identifier)
        refs = [r22.anchored(source, anchor, expected_sha) for anchor in anchors]
        records.append({
            "id": identifier, "gate": gate, "responsible_functions": roles,
            "source_witness": "SOURCE_ONLY_BOUNDED_OBSERVATION",
            "anchors": refs, "proof_status": "OPEN_NOT_DISCHARGED",
            "required_independent_proof": required,
            "formal_happens_before_established": False,
            "os_quiescence_verified": False,
            "allows_physical_emission": False,
        })

    c11, life, dispose = GATES

    add("HB01_CONTROLLER_PREFILL_BEFORE_QUEUE_START", c11, ["B09", "B07"],
        order(controller, "AudioQueueNewOutput(&fmt,output_callback,ctx",
              "fill_audio(ctx,b);", "AudioQueueStart(ctx->queue,NULL)")
        and "fill_audio(ctx,buf)" in out,
        ("fill_audio(ctx,b);", "AudioQueueStart(ctx->queue,NULL)"),
        "Prove OS guarantees no concurrent buffer callback during prefill after queue creation and before start, or redesign ownership through one shared synchronization mechanism.")

    add("HB02_PCM_FIELDS_NONATOMIC", c11, ["B09"],
        "double phase, phase_step, normalized_level;" in source
        and "uint64_t frames_written, total_frames, fade_frames;" in source
        and "ctx->phase+=" in pcm and "++ctx->frames_written" in pcm,
        ("double phase, phase_step, normalized_level;",
         "++ctx->frames_written"),
        "Prove every non-atomic write and read of PCM state is ordered by happens-before and has no conflicting concurrent access under the C11 memory model.")

    add("HB03_CALLBACK_WRITER_GATE_SCOPE", c11, ["B09"],
        order(out, "atomic_flag_test_and_set_explicit(&ctx->pcm_writer_gate",
              "fill_audio(ctx,buf)",
              "atomic_flag_clear_explicit(&ctx->pcm_writer_gate")
        and "memory_order_acquire" in out and "memory_order_release" in out,
        ("atomic_flag_test_and_set_explicit(&ctx->pcm_writer_gate",
         "atomic_flag_clear_explicit(&ctx->pcm_writer_gate"),
        "Demonstrate the acquire/release lock covers all callback writers and that every competing writer participates in the same synchronization relation.")

    add("HB04_CONTROLLER_PREFILL_OUTSIDE_WRITER_GATE", c11, ["B09"],
        "fill_audio(ctx,b);" in controller
        and "atomic_flag_test_and_set_explicit(&ctx->pcm_writer_gate" not in controller
        and "atomic_flag_clear(&ctx->pcm_writer_gate);" in controller,
        ("fill_audio(ctx,b);", "atomic_flag_clear(&ctx->pcm_writer_gate);"),
        "Provide an explicit OS thread-start and callback-delivery proof that the controller prefill never overlaps the protected callback path; the callback-only spin gate does not establish this.")

    add("HB05_OS_PUBLICATION_BARRIER", c11, ["B07", "B09"],
        order(controller, "atomic_init(&ctx->active_output_callbacks,0U)",
              "AudioQueueNewOutput(&fmt,output_callback,ctx")
        and "AudioQueueStart(ctx->queue,NULL)" in controller,
        ("atomic_init(&ctx->active_output_callbacks,0U)",
         "AudioQueueNewOutput(&fmt,output_callback,ctx"),
        "Document and independently justify the visibility of all initialized context fields to OS callback threads after queue creation and startup, including the relevant publication edge.")

    add("Q01_HEAP_USERDATA_PUBLISHED_TO_TWO_CALLBACKS", life, ["B07","B09"],
        order(controller, "AcousticContext *owner_ctx=(AcousticContext*)calloc",
              "AudioQueueNewOutput(&fmt,output_callback,ctx",
              "queue_running_listener,ctx"),
        ("AcousticContext *owner_ctx=(AcousticContext*)calloc",
         "queue_running_listener,ctx"),
        "Prove a valid heap owner persists for every asynchronous callback reference from queue creation through listener removal and successful disposal.")

    add("Q02_CALLBACK_COUNTER_AFTER_RECEIVING_USERDATA", life, ["B07","B09"],
        order(out, "AcousticContext *ctx=(AcousticContext*)ptr;",
              "atomic_fetch_add_explicit(&ctx->active_output_callbacks")
        and order(listener, "AcousticContext *ctx=(AcousticContext*)data;",
                  "atomic_fetch_add_explicit(&ctx->active_property_listeners"),
        ("AcousticContext *ctx=(AcousticContext*)ptr;",
         "AcousticContext *ctx=(AcousticContext*)data;"),
        "Provide OS-level exclusion of new callback entry after disposal; callbacks obtain userdata before they increment counters, so the counters alone cannot protect entry.")

    add("Q03_ZERO_COUNTER_READ_BEFORE_FINAL_FREE", life, ["B07","B09"],
        order(controller, "const int context_quiescent=",
              "if (context_quiescent) {")
        and controller.find("free(owner_ctx);",
                            controller.find("if (context_quiescent) {")) >= 0
        and "atomic_load_explicit(&ctx->active_output_callbacks" in controller
        and "atomic_load_explicit(&ctx->active_property_listeners" in controller,
        ("const int context_quiescent=", "if (context_quiescent) {"),
        "Prove counter-zero observations occur after a final OS callback-admission barrier; acquire reads cannot alone exclude later increments or stale published pointers.")

    add("Q04_LISTENER_REMOVAL_BEFORE_TERMINAL_DISPOSAL", life, ["B07","B09"],
        controller.find("AudioQueueRemovePropertyListener") >= 0
        and controller.find("AudioQueueRemovePropertyListener") <
            controller.rfind("if (AudioQueueDispose(ctx->queue,true)!=noErr)"),
        ("AudioQueueRemovePropertyListener",
         "if (AudioQueueDispose(ctx->queue,true)!=noErr)"),
        "Establish callback-drain and listener-unregistration guarantees, including error semantics and absence of a late running-property listener after successful disposal.")

    add("Q05_SUCCESSFUL_DISPOSE_AND_USERDATA_RECLAIM", life, ["B07","B09"],
        order(controller, "if (AudioQueueDispose(ctx->queue,true)!=noErr)",
              "atomic_store(&ctx->dispose_confirmed,1)",
              "const int context_quiescent=")
        and "ctx->queue=NULL;" in controller,
        ("atomic_store(&ctx->dispose_confirmed,1)",
         "const int context_quiescent="),
        "Cite the exact Apple AudioQueueDispose synchronous-success contract and establish that all relevant registered callback lifetimes and accesses have ended before freeing userdata.")

    add("D01_BIND_REJECTION_DISPOSE_STATUS_BRANCH", dispose, ["B07","B09"],
        order(controller,
              "const OSStatus bind_dispose_status=AudioQueueDispose(ctx->queue,true);",
              "if (bind_dispose_status==noErr)")
        and "atomic_store_explicit(&fm_context_quarantined,1" in controller,
        ("const OSStatus bind_dispose_status=AudioQueueDispose(ctx->queue,true);",
         "if (bind_dispose_status==noErr)"),
        "Prove the true OS failure behavior of disposing a queue whose route-binding was rejected, including pending callback references and ownership of the retained heap.")

    failed = controller.split("if (AudioQueueDispose(ctx->queue,true)!=noErr) {", 1)
    err_body = failed[1].split("} else {",1)[0] if len(failed)==2 else ""
    add("D02_FAILED_TERMINAL_DISPOSE_PRESERVES_HEAP", dispose, ["B07","B09"],
        bool(err_body) and "FM_FAULT_DISPOSAL" in err_body
        and "free(owner_ctx);" not in err_body
        and "ctx->queue=NULL;" not in err_body
        and "atomic_load(&ctx->dispose_confirmed)" in controller,
        ("if (AudioQueueDispose(ctx->queue,true)!=noErr)",
         "atomic_load(&ctx->dispose_confirmed)"),
        "Independently qualify real failed AudioQueueDispose outcomes; confirm callback references remain valid, no use-after-free, no retry and bounded resource ownership under error.")

    add("D03_UNCERTAIN_LISTENER_REGISTRATION", dispose, ["B07","B09"],
        "listener_registration_uncertain=1;" in controller
        and "!listener_registration_uncertain" in controller,
        ("listener_registration_uncertain=1;",
         "!listener_registration_uncertain"),
        "Document real OS registration-error callback behavior, including whether a callback may already have been enqueued despite a non-success status.")

    add("D04_FAILED_LISTENER_REMOVAL_QUARANTINE", dispose, ["B07","B09"],
        "listener_remove_failed=1;" in controller
        and "FM_FAULT_LISTENER_REMOVAL" in controller
        and "!listener_remove_failed" in controller,
        ("listener_remove_failed=1;", "!listener_remove_failed"),
        "Prove actual failed listener-removal behavior and persistent listener or context lifetime, independent of the observed atomic listener counters.")

    add("D05_PROCESS_QUARANTINE_WITHOUT_RETRY", dispose, ["B09","B10"],
        "atomic_load_explicit(&fm_context_quarantined,memory_order_acquire)" in controller
        and "atomic_store_explicit(&fm_context_quarantined,1,memory_order_release)" in controller
        and "atomic_flag_test_and_set_explicit(&fm_session_claim,memory_order_acquire)" in controller,
        ("atomic_load_explicit(&fm_context_quarantined,memory_order_acquire)",
         "atomic_store_explicit(&fm_context_quarantined,1,memory_order_release)"),
        "Independently establish that quarantined process state cannot re-admit a queue or release an OS-owned pointer, across all error paths and program shutdown.")

    expected = ("HB01","HB02","HB03","HB04","HB05",
                "Q01","Q02","Q03","Q04","Q05",
                "D01","D02","D03","D04","D05")
    require(len(records)==15 and
            tuple(item["id"].split("_",1)[0] for item in records)==expected,
            "15 unique evidence obligations drifted")
    require(all(entry["proof_status"]=="OPEN_NOT_DISCHARGED"
                and len(entry["anchors"])==2 for entry in records),
            "evidence obligation promoted or incomplete")
    return records

def assess(root, source_override=None, runner_override=None):
    root = Path(root).resolve()
    table, manifest_sha = r17.manifest_integrity(root)
    require(len(table)==123, "GEN-R23 requires precisely 123 pinned files")
    for path in ("audits/r23_happens_before_obligations.py",
                 "tests/test_r23_happens_before_obligations.py",
                 "RUN_GEN_R23_MAC_INTEL.command",
                 "docs/GEN_R23_HAPPENS_BEFORE_PROOF_OBLIGATIONS.md",
                 "docs/GEN_R23_BUREAU_REVIEW.md"):
        require(path in table, "GEN-R23 audit file missing: " + path)
    require(table["src/acoustic_macos.c"] == r19.PINNED_ACOUSTIC_SHA256,
            "CoreAudio backend is not identical to previous source pin")
    assert_source = root/"src/acoustic_macos.c"
    raw = assert_source.read_bytes()
    require(sha(raw)==table["src/acoustic_macos.c"],
            "unverified source under R23")
    runner_raw=(root/"RUN_GEN_R23_MAC_INTEL.command").read_bytes()
    require(sha(runner_raw)==table["RUN_GEN_R23_MAC_INTEL.command"],
            "unverified runner under R23")
    runner=runner_raw.decode("utf-8")
    sources = r17.link_sources(runner)
    require(len(sources)==len(r17.LINK_C_ALLOWLIST)
            and set(sources)==r17.LINK_C_ALLOWLIST,
            "runnable linker allowlist changed")
    require("R23_NONEMITTING_EXECUTABLE_SYMBOL_AUDIT=PASS" in runner
            and "FREQMED_GEN_R23_BINARY" in runner,
            "missing native non-emission guard")
    original=raw.decode("utf-8")
    ledger=obligations(original if source_override is None else source_override,
                       runner if runner_override is None else runner_override,
                       table["src/acoustic_macos.c"])
    return table, manifest_sha, ledger

def audit(root, historical_r19_archive, current_reports, r21_report, r22_report):
    root=Path(root).resolve()
    table, digest, ledger=assess(root)
    actual_r22=archive19.parse_json(archive19.safe_read(r22_report))
    recomputed_r22=r22.audit(root,historical_r19_archive,current_reports,r21_report)
    require(actual_r22==recomputed_r22,
            "R22 evidence detached from R16-R21 sources/historical archive")
    require(actual_r22["source_contracts_observed"]==17
            and actual_r22["bureau_gates_open"]==11
            and actual_r22["bureau_gates_resolved"]==0
            and len(actual_r22["open_findings"])==3,
            "R22 review claims promotion or missing risk")
    r21_report_obj=archive19.parse_json(archive19.safe_read(r21_report))
    first=r21_report_obj["gates"][:3]
    require([x["id"] for x in first]==list(GATES)
            and [x["status"] for x in first]==[
                "NOT_PROVEN","NOT_TESTED","NOT_TESTED"],
            "Bureau first three source statuses silently changed")
    return {
        "schema":SCHEMA, "verdict":VERDICT,
        "method":"PINNED_C11_SOURCE_ORDER_AND_UNDISCHARGED_PROOF_LEDGER",
        "generator_manifest_sha256":digest, "generator_files":len(table),
        "acoustic_source_sha256":table["src/acoustic_macos.c"],
        "source_only_obligations":ledger, "obligation_count":len(ledger),
        "obligations_discharged":0, "proof_of_absence_of_races":False,
        "os_callback_quiescence_certified":False,
        "real_disposal_failure_witness":"NONE",
        "previous_r22_report_sha256":sha(archive19.safe_read(r22_report)),
        "history_r19_archive_read_only":"REVERIFIED_IN_R16_TO_R22_CHAIN",
        "three_primary_gates":[{"name":x["id"],"status":x["status"]}
                               for x in first],
        "bureau_gates_open":11,"bureau_gates_resolved":0,
        "independent_signatures":"NONE","limitations":list(LIMITS),
        "acoustic_output":"LOCKED","em_output":"LOCKED",
        "physical_emission":"NONE","scientific_simulation":"NONE",
        "real_output":"NOT_AUTHORIZED",
        "biological_exposure":"NOT_AUTHORIZED",
        "production":"NOT_AUTHORIZED","bureau_certification":"PENDING",
    }

def markdown(result):
    tick=chr(96)
    rows=[]
    for entry in result["source_only_obligations"]:
        places=", ".join(tick + p["path"] + ":" + str(p["line"]) + tick
                         for p in entry["anchors"])
        rows.append("| "+entry["id"]+" | "+entry["gate"]+" | "+
                    places+" | OPEN |")
    return ("# FREQMED GEN-R23 - Happens-Before & Callback Quiescence\n\n"
            "Verdict : **PROOF_OBLIGATIONS_OPEN_NO_EMISSION**. "
            "**15 obligations, 0 preuve acquittée.** "
            "11 portes Bureau OPEN, 0 résolue.\n\n"
            "| Obligation | Porte | Sources réellement épinglées | Preuve |\n"
            "|---|---|---|---|\n"+ "\n".join(rows) +
            "\n\nLes relations d'ordre textuelles ne constituent pas des "
            "relations happens-before C11. La lecture de compteurs à zéro "
            "n'empêche pas un nouveau callback, et les chemins d'échec de "
            "AudioQueueDispose restent sans témoin réel. "
            "Aucune personne du Bureau n'est réputée avoir signé ou certifié.\n\n"
            "NEVER_SIMULATION=ENFORCED ; ZERO_COST_FOSS=ENFORCED ; "
            "ACOUSTIC_OUTPUT=LOCKED ; EM_OUTPUT=LOCKED ; "
            "REAL_OUTPUT=NOT_AUTHORIZED ; "
            "BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED ; "
            "PRODUCTION=NOT_AUTHORIZED.\n")

def main():
    parser=argparse.ArgumentParser(description="GEN-R23 C11 source-only proof ledger")
    parser.add_argument("--root",required=True,type=Path)
    parser.add_argument("--archive-r19",required=True,type=Path)
    for name in ("r16","r17","r18","r19","r20","r21","r22"):
        parser.add_argument("--"+name,required=True,type=Path)
    parser.add_argument("--json",required=True,type=Path)
    parser.add_argument("--markdown",required=True,type=Path)
    args=parser.parse_args()
    try:
        older={name:getattr(args,name)
               for name in ("r16","r17","r18","r19","r20")}
        result=audit(args.root,args.archive_r19,older,args.r21,args.r22)
        args.json.write_text(json.dumps(result,sort_keys=True,indent=2,
                             ensure_ascii=False)+"\n",encoding="utf-8")
        args.markdown.write_text(markdown(result),encoding="utf-8")
    except (R23Error,r22.R22Error,ValueError,TypeError,KeyError,OSError,
            UnicodeError,IndexError) as exc:
        print("R23_C11_PROOF_OBLIGATIONS=FAIL_CLOSED",str(exc))
        return 2
    print("R23_C11_PROOF_OBLIGATIONS=PASS")
    print("R23_OBLIGATIONS=15; R23_DISCHARGED=0")
    print("R23_BUREAU_OPEN=11; R23_BUREAU_RESOLVED=0")
    print("R23_REVIEW_VERDICT="+VERDICT)
    print("R23_C11_RACE_FREEDOM=NOT_PROVEN")
    print("R23_CALLBACK_QUIESCENCE=NOT_PROVEN")
    print("R23_FAILED_OS_DISPOSAL=NOT_TESTED")
    print("R23_PHYSICAL_EMISSION=NONE; R23_SCIENTIFIC_SIMULATION=NONE")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
