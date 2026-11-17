#!/usr/bin/env python3
"""GEN-R29: source-only C11 admission integration review, no CoreAudio run.
All observations are bounded checks, NOT proof of race freedom or OS safety.
"""
import argparse
import hashlib
import json
from pathlib import Path
import r17_evidence_verifier as r17
import r19_adversarial_source_audit as r19
import r26_isolated_patch_gate as r26
import r27_adversarial_ownership_review as r27
import r28_queue_admission_design as r28

SCHEMA="FREQMED_GEN_R29_C11_ADMISSION_INTEGRATION_PROOF_REVIEW"
VERDICT="ISOLATED_INTEGRATION_REVIEWED_C11_OS_PROOF_OPEN"
CANDIDATE="candidates/acoustic_macos_r29.c"
FINDINGS=(
 ("I29_01_LATE_USERDATA_ADMISSION","HIGH","B07",
  "An OS callback receives userdata before try_enter. Its validity, even after close, requires a documented CoreAudio admission and object-lifetime guarantee."),
 ("I29_02_CLOSE_EMPTY_NOT_OS_QUIESCENCE","HIGH","B07",
  "Closed and empty is only a C11 gate predicate. A late OS callback can still attempt an atomic access to userdata, and a failed OS dispose leaves resource ownership ambiguous."),
 ("I29_03_QUEUE_HAPPENS_BEFORE_CONDITIONAL","HIGH","B09",
  "Prove the C11 release-sequence observation and all controller-only queue accesses, including any pointer clear after successful dispose. No general OS race freedom follows."),
 ("I29_04_LISTENER_AND_DISPOSAL_ERRORS","HIGH","B07",
  "Verify actual AudioQueueRemovePropertyListener and AudioQueueDispose OSStatus failure contracts, callbacks already dispatched, buffer ownership and the stop/dispose ordering."),
 ("I29_05_ENQUEUE_REENTRANCY_UNRESOLVED","HIGH","B09",
  "AudioQueueEnqueueBuffer still executes inside the R26 PCM writer gate. Independently prove no dangerous CoreAudio reentrancy or unbounded real-time latency."),
 ("I29_06_EARLY_QUARANTINE_RESOURCE_RISK","HIGH","B10",
  "Early return on a live lease intentionally skips disposal and permanently quarantines the process. This is not a physical cutoff or resource release; bound the retained OS resources."),
 ("I29_07_LEASE_PAIRING_AND_LOCK_FREEDOM","HIGH","B09",
  "Establish every path calls leave once after enter, absence of counter wrap or underflow, and actual callback timing/lock-free suitability of C11 atomics on supported devices."),
)
LIMITATIONS=(
 "SOURCE_LEVEL_ANCHOR_REVIEW_NOT_FULL_C11_AST_OR_FORMAL_PROOF",
 "GATE_ENTRY_IS_AFTER_OS_USERDATA_POINTER_ACQUISITION",
 "NO_REAL_OS_CALLBACK_ADMISSION_QUIESCENCE_OR_FAILED_DISPOSAL",
 "NO_REAL_TIME_REENTRANCY_OR_NONBLOCKING_OS_PROOF",
 "NO_ACTIVATION_OR_SCIENTIFIC_SIMULATION_OR_PHYSICAL_EMISSION",
 "NO_INDEPENDENT_BUREAU_SIGNATURE",
)
class R29Error(ValueError): pass
def require(ok,why):
    if not ok: raise R29Error(why)
def sha(data): return hashlib.sha256(data).hexdigest()
def function(source,name):
    return r27.function_span(source,name)[2]

def observe(source):
    require(source.startswith("/* SPDX-License-Identifier: Apache-2.0 */"),
            "R29 source license drift")
    require("GEN-R29 ISOLATED INTEGRATION CANDIDATE" in source,
            "R29 isolated purpose removed")
    require(source.count('#include "r28_callback_admission_gate.c"')==1,
            "R29 R28 C11 gate inclusion drift")
    require(source.count("FMR28AdmissionGate queue_admission;")==1,
            "R29 context admission field missing")
    ctrl=function(source,"controller")
    callback=function(source,"callback")
    listener=function(source,"listener")
    pcm=function(source,"pcm")
    require(ctrl.index("fm_r28_gate_init(&ctx->queue_admission);") <
            ctrl.index("AudioQueueNewOutput(&fmt,output_callback,ctx"),
            "R29 gate must initialize before callback publication")
    assert_callback=lambda b,n: require(
        b.index("if (!ctx) return;") <
        b.index("if (!fm_r28_gate_try_enter(&ctx->queue_admission)) return;") <
        b.index("atomic_fetch_add_explicit(&ctx->active_"+n) <
        b.index("atomic_fetch_sub_explicit(&ctx->active_"+n) <
        b.index("fm_r28_gate_leave(&ctx->queue_admission);"),
        "R29 "+n+" admission/exit pairing order")
    assert_callback(callback,"output_callbacks")
    assert_callback(listener,"property_listeners")
    require(source.count("fm_r28_gate_try_enter(&ctx->queue_admission)")==2,
            "R29 unexpected admission counts")
    require(source.count("fm_r28_gate_leave(&ctx->queue_admission);")==2,
            "R29 unexpected leave counts")
    require(ctrl.count("fm_r28_gate_close(&ctx->queue_admission);")==3,
            "R29 missing three closure sites")
    require(ctrl.count("if (!fm_r28_gate_closed_and_empty(&ctx->queue_admission))")==2,
            "R29 missing fail-closed disposal guards")
    require(ctrl.index("fm_r28_gate_close(&ctx->queue_admission);",
                       ctrl.index("const OSStatus bind_dispose_status")-800) <
            ctrl.index("const OSStatus bind_dispose_status=AudioQueueDispose(ctx->queue,true);"),
            "R29 bind-rejection closure must precede dispose")
    final=ctrl.index("  /* Seal admission before OS cleanup.")
    require(ctrl.index("fm_r28_gate_close(&ctx->queue_admission);",final) <
            ctrl.index("if (!fm_r28_gate_closed_and_empty(&ctx->queue_admission))",final) <
            ctrl.index("if (ctx->queue) {",final) <
            ctrl.index("if (AudioQueueDispose(ctx->queue,true)!=noErr)",final) <
            ctrl.index("ctx->queue=NULL;",final),
            "R29 final close/empty/dispose/clear ordering drift")
    require("AudioQueueEnqueueBuffer(ctx->queue,buf,0,NULL)" in pcm,
            "R29 unresolved enqueue risk removed or changed without review")
    require(source.count("free(owner_ctx);")==2 and
            ctrl.rindex("free(owner_ctx);") <
            ctrl.index("AudioQueueNewOutput(&fmt,output_callback,ctx"),
            "R29 source must retain all published userdata")
    require("int fm_acoustic_physical_output(const FMCommand *command)" in source and
            "/* GEN-R3: unconditional hard denial" in source,
            "R29 hard-denied external output entry modified")
    return {item[0]:"OPEN_NOT_PROVEN" for item in FINDINGS}

def anchor(source,where,needle,source_sha):
    start,end,body=r27.function_span(source,where)
    require(needle in body,"R29 proof anchor absent "+where+" "+needle)
    position=start+body.index(needle)
    return {"path":CANDIDATE,"function":where,
            "line":source.count("\n",0,position)+1,
            "source_sha256":source_sha,"needle":needle}

def inspect(root,candidate_override=None):
    root=Path(root).resolve()
    table,manifest=r17.manifest_integrity(root)
    require(len(table)>=156,"R29 historical review requires at least 156 SHA-pinned generator files")
    required=(CANDIDATE,"audits/r29_admission_integration_review.py",
             "tests/test_r29_admission_integration_review.py",
             "RUN_GEN_R29_MAC_INTEL.command",
             "docs/GEN_R29_C11_ADMISSION_INTEGRATION.md",
             "docs/GEN_R29_BUREAU_REVIEW.md")
    require(all(x in table for x in required),"R29 artifact not manifest-pinned")
    require(table[r26.ORIGINAL]==r19.PINNED_ACOUSTIC_SHA256,
            "R29 original C changed")
    # R26/R28 and earlier evidence are rechecked using the genuine source
    # manifest and their separate historical auditors.
    old=r28.inspect(root)
    require(old[2]==table[r28.CANDIDATE],
            "R29 R28 C11 gate changed")
    require(table[r26.CANDIDATE]==r27.inspect(root)[3],
            "R29 inherited R26 patch changed")
    raw=(root/CANDIDATE).read_bytes()
    require(sha(raw)==table[CANDIDATE],"R29 candidate SHA drift")
    content=raw.decode("utf-8") if candidate_override is None else candidate_override
    checks=observe(content)
    run=(root/"RUN_GEN_R29_MAC_INTEL.command").read_text(encoding="utf-8")
    require(set(r17.link_sources(run))==r17.LINK_C_ALLOWLIST,
            "R29 executable source allowlist changed")
    chunks=run.split(' -o "$WORK/freqmed-gen"')
    require(len(chunks)==2,"R29 executable link command missing")
    link=chunks[1].split("-framework CoreAudio",1)[0]
    for forbidden in ("acoustic_macos_r29.c","acoustic_macos_r26.c",
                      "r28_callback_admission_gate.c","src/acoustic_macos.c"):
        require(forbidden not in link, "R29 output candidate linked: "+forbidden)
    require("output_hard_denied.c" in link,"R29 runnable no-output source missing")
    for token in ("R29_INTEGRATED_CANDIDATE_OBJECT=COMPILED_UNLINKED",
                  "R29_ADMISSION_DESIGN_OBJECT=COMPILED_UNLINKED",
                  "R29_NONEMITTING_EXECUTABLE_SYMBOL_AUDIT=PASS",
                  "R29_BUREAU_REVIEW_DOSSIER=20_FILES_SHA256_PASS",
                  "FREQMED_GEN_R29_EVIDENCE_DIR",
                  "FREQMED_GEN_R29_BINARY"):
        require(token in run,"R29 runner marker absent "+token)
    return table,manifest,sha(raw),checks

def audit(root,archive_r19,paths):
    table,manifest,digest,checks=inspect(root)
    expected=r28.audit(root,archive_r19,paths)
    actual=json.loads(Path(paths["r28"]).read_text(encoding="utf-8"))
    require(actual==expected,"R29 R28 report changed from independently recomputed chain")
    require(expected["r28_gates_open"]==5 and
            expected["r27_findings_open"]==9 and
            expected["r23_obligations_open"]==15 and
            expected["r24_findings_open"]==7 and
            expected["bureau_gates_open"]==11 and
            expected["bureau_gates_resolved"]==0,
            "R29 historical research obligations improperly promoted")
    c=(Path(root)/CANDIDATE).read_text(encoding="utf-8")
    proposed=(
     ("I29_01_LATE_USERDATA_ADMISSION",("callback","if (!fm_r28_gate_try_enter"),
       ("listener","if (!fm_r28_gate_try_enter")),
     ("I29_02_CLOSE_EMPTY_NOT_OS_QUIESCENCE",("controller","if (!fm_r28_gate_closed_and_empty"),
       ("controller","AudioQueueDispose(ctx->queue,true)")),
     ("I29_03_QUEUE_HAPPENS_BEFORE_CONDITIONAL",("pcm","AudioQueueEnqueueBuffer(ctx->queue"),
       ("controller","ctx->queue=NULL;")),
     ("I29_04_LISTENER_AND_DISPOSAL_ERRORS",("controller","AudioQueueRemovePropertyListener(ctx->queue"),
       ("controller","if (AudioQueueDispose(ctx->queue,true)!=noErr)")),
     ("I29_05_ENQUEUE_REENTRANCY_UNRESOLVED",("pcm","AudioQueueEnqueueBuffer(ctx->queue"),
       ("callback","atomic_flag_test_and_set_explicit(&ctx->pcm_writer_gate")),
     ("I29_06_EARLY_QUARANTINE_RESOURCE_RISK",("controller","no disposal. Quarantine and leak."),
       ("controller","fm_context_quarantined,1,memory_order_release")),
     ("I29_07_LEASE_PAIRING_AND_LOCK_FREEDOM",("callback","fm_r28_gate_leave(&ctx->queue_admission)"),
       ("listener","fm_r28_gate_leave(&ctx->queue_admission)")),
    )
    require([x[0] for x in proposed]==[x[0] for x in FINDINGS],
            "R29 proof anchors not aligned with finding ledger")
    ledger=[]
    for finding,one,two in proposed:
        info=next(x for x in FINDINGS if x[0]==finding)
        ledger.append({
         "id":finding,"priority":info[1],"bureau_role":info[2],
         "status":checks[finding],"race_reproduced":False,
         "anchors":[anchor(c,*one,digest),anchor(c,*two,digest)],
         "evidence_needed_for_resolution":info[3],
         "independent_approval":"NONE",
        })
    return {
     "schema":SCHEMA,"verdict":VERDICT,
     "method":"SHA_PINNED_SOURCE_ONLY_ADMISSION_INTEGRATION_REVIEW",
     "manifest_sha256":manifest,"pinned_generator_files":len(table),
     "r29_candidate_sha256":digest,
     "r28_contract_sha256":table[r28.CANDIDATE],
     "r26_candidate_sha256":table[r26.CANDIDATE],
     "original_C_sha256":table[r26.ORIGINAL],
     "r28_report_sha256":sha(Path(paths["r28"]).read_bytes()),
     "r29_findings":ledger,"r29_findings_open":7,
     "r29_integrated_source_only":True,
     "r29_linked_or_executed":False,"r29_original_C_edits":0,
     "r29_r26_C_edits":0,"r29_r28_gate_edits":0,
     "r28_gates_open":5,"r27_findings_open":9,
     "r23_obligations_open":15,"r24_findings_open":7,
     "bureau_gates_open":11,"bureau_gates_resolved":0,
     "C11_race_freedom":"NOT_PROVEN",
     "CoreAudio_callback_quiescence":"NOT_PROVEN",
     "failed_AudioQueueDispose":"NOT_TESTED",
     "independent_signatures":"NONE","bureau_certification":"PENDING",
     "limitations":list(LIMITATIONS),
     "physical_emission":"NONE","scientific_simulation":"NONE",
     "acoustic_output":"LOCKED","em_output":"LOCKED",
     "real_output":"NOT_AUTHORIZED",
     "biological_exposure":"NOT_AUTHORIZED","production":"NOT_AUTHORIZED",
    }
def markdown(report):
    lines=["| "+item["id"]+" | "+item["priority"]+" | "+item["bureau_role"]+
           " | OPEN_NOT_PROVEN |" for item in report["r29_findings"]]
    return ("# FREQMED GEN-R29: Independent C11 Admission Integration & Queue Ownership Proof Review\n\n"
      "**Verdict: ISOLATED_INTEGRATION_REVIEWED_C11_OS_PROOF_OPEN.** "
      "Source-only R29 candidate integrates R28 gate into callback/listener entry "
      "and seals admission before cleanup, yet does NOT prove CoreAudio quiescence, "
      "OS lifetime, PCM reentrancy, nonblocking behavior or physical safety.\n\n"
      "| Finding | Priority | Bureau | State |\n|---|---|---|---|\n"+
      "\n".join(lines)+
      "\n\nSeven new findings stay OPEN; five R28 designs, nine R27 findings, "
      "15 R23 obligations, seven R24 findings and 11 Bureau gates remain OPEN. "
      "No callbacks executed and no scientific simulation.\n"
      "NEVER_SIMULATION=ENFORCED; ZERO_COST_FOSS=ENFORCED; "
      "ACOUSTIC_OUTPUT=LOCKED; EM_OUTPUT=LOCKED; REAL_OUTPUT=NOT_AUTHORIZED; "
      "BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED; PRODUCTION=NOT_AUTHORIZED.\n")
def main():
    p=argparse.ArgumentParser(description="FREQMED GEN-R29 nonemitting source review")
    p.add_argument("--root",required=True,type=Path)
    p.add_argument("--archive-r19",required=True,type=Path)
    for n in range(16,29):
        p.add_argument("--r"+str(n),required=True,type=Path)
    p.add_argument("--json",required=True,type=Path)
    p.add_argument("--markdown",required=True,type=Path)
    a=p.parse_args()
    try:
        paths={"r"+str(n):getattr(a,"r"+str(n)) for n in range(16,29)}
        result=audit(a.root,a.archive_r19,paths)
        a.json.write_text(json.dumps(result,sort_keys=True,ensure_ascii=False,
                            indent=2)+"\n",encoding="utf-8")
        a.markdown.write_text(markdown(result),encoding="utf-8")
    except (R29Error,r28.R28Error,r27.R27Error,r26.R26Error,
            ValueError,TypeError,KeyError,IndexError,OSError,UnicodeError) as error:
        print("R29_C11_ADMISSION_INTEGRATION_REVIEW=FAIL_CLOSED",str(error))
        return 2
    print("R29_C11_ADMISSION_INTEGRATION_REVIEW=PASS")
    print("R29_OPEN_INTEGRATION_FINDINGS=7; R29_C11_PROVEN_RACES=0")
    print("R29_SOURCE_ONLY_INTEGRATION=1; R29_ORIGINAL_C_EDITS=0")
    print("R29_R28_GATES=5_OPEN; R29_R27_FINDINGS=9_OPEN")
    print("R29_R23_OBLIGATIONS=15_OPEN; R29_R24_FINDINGS=7_OPEN")
    print("R29_BUREAU_GATES=11_OPEN; R29_BUREAU_RESOLVED=0")
    print("R29_REVIEW_VERDICT="+VERDICT)
    print("R29_C11_RACE_FREEDOM=NOT_PROVEN")
    print("R29_CALLBACK_QUIESCENCE=NOT_PROVEN")
    print("R29_FAILED_OS_DISPOSAL=NOT_TESTED")
    print("R29_PHYSICAL_EMISSION=NONE; R29_SCIENTIFIC_SIMULATION=NONE")
    return 0
if __name__=="__main__":
    raise SystemExit(main())
