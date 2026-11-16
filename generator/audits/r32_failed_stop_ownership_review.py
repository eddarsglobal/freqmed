#!/usr/bin/env python3
"""GEN-R32: independent FAILED AudioQueueStop containment/ownership review.
Static source evidence only; no CoreAudio dispatch, race simulation, or emission.
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
import r29_admission_integration_review as r29
import r30_coreaudio_quiescence_adversarial as r30
import r31_critical_shutdown_review as r31

SCHEMA="FREQMED_GEN_R32_FAILED_STOP_CONTAINMENT_OS_OWNERSHIP_AUDIT"
VERDICT="FAILED_STOP_CONTAINMENT_REVIEWED_PHYSICAL_SAFETY_UNPROVEN"
CANDIDATE=r31.CANDIDATE
FINDINGS=(
 ("FS32_01_FAILED_STOP_MAY_CONTINUE_OUTPUT","CRITICAL","B10",
  "Prove an independent safe output cutoff after nonzero AudioQueueStop OSStatus; quarantine cannot replace hardware evidence."),
 ("FS32_02_FAILURE_EXIT_RETAINS_LIVE_QUEUE","CRITICAL","B10",
  "Qualify the active queue/resource lifecycle when immediate Stop fails and the controller returns without disposal; no safe termination is currently proven."),
 ("FS32_03_C11_CLOSE_NOT_OS_CANCELLATION","HIGH","B07",
  "Prove that the OS can no longer enter callbacks/listeners and read userdata after the C11 admission gate closes."),
 ("FS32_04_CONTROLLER_QUEUE_REF_OWNERSHIP","HIGH","B09",
  "Prove all controller and callback accesses to non-atomic ctx->queue are ordered by C11/OS guarantees."),
 ("FS32_05_STOP_SUCCESS_IS_NOT_PHYSICAL_MEASUREMENT","HIGH","B10",
  "Distinguish successful OS stop postcondition from independent acoustic measurements and external-device behavior."),
 ("FS32_06_LISTENER_REMOVE_FAILURE","HIGH","B07",
  "Prove listener removal failure and in-flight callback effects on subsequent disposal and userdata ownership."),
 ("FS32_07_DISPOSE_FAILURE_AMBIGUOUS_OWNER","HIGH","B07",
  "Qualify disposal error OSStatus before reading/clearing AudioQueueRef and before any possible resource reclamation."),
 ("FS32_08_BUSY_ADMISSIONS_RETAIN_RESOURCES","HIGH","B09",
  "Prove admitted callback pairing and bound memory/OS resources retained after a successful stop but nonempty gate."),
 ("FS32_09_PCM_REENTRANCE_NOT_PROVEN","HIGH","B09",
  "Qualify enqueue under pcm_writer_gate and controller stop interactions, including nonblocking and callback reentrance."),
 ("FS32_10_QUARANTINE_PROCESS_EXIT_POLICY","HIGH","B10",
  "Specify fail-stop incident escalation and bounded resource retention without claiming that process exit forcibly stops devices."),
)
# Two real anchors per finding, all drawn from SHA-pinned R31 C.
ANCHORS=(
 ("FS32_01_FAILED_STOP_MAY_CONTINUE_OUTPUT",
  ("controller","const OSStatus r31_immediate_stop_status=AudioQueueStop(ctx->queue,true);"),
  ("controller","if (r31_immediate_stop_status!=noErr) {")),
 ("FS32_02_FAILURE_EXIT_RETAINS_LIVE_QUEUE",
  ("controller","if (r31_immediate_stop_status!=noErr) {"),
  ("controller","/* CRITICAL: OS stop failed.")),
 ("FS32_03_C11_CLOSE_NOT_OS_CANCELLATION",
  ("controller","fm_r28_gate_close(&ctx->queue_admission);"),
  ("callback","if (!fm_r28_gate_try_enter(&ctx->queue_admission)) return;")),
 ("FS32_04_CONTROLLER_QUEUE_REF_OWNERSHIP",
  ("controller","AudioQueueStop(ctx->queue,true)"),
  ("pcm","AudioQueueEnqueueBuffer(ctx->queue,buf,0,NULL)")),
 ("FS32_05_STOP_SUCCESS_IS_NOT_PHYSICAL_MEASUREMENT",
  ("controller","if (r31_admission_busy) {"),
  ("controller","/* Successful synchronous STOP was requested before this return.")),
 ("FS32_06_LISTENER_REMOVE_FAILURE",
  ("controller","AudioQueueRemovePropertyListener(ctx->queue,"),
  ("controller","listener_remove_failed=1;")),
 ("FS32_07_DISPOSE_FAILURE_AMBIGUOUS_OWNER",
  ("controller","if (AudioQueueDispose(ctx->queue,true)!=noErr) {"),
  ("controller","ctx->queue=NULL;")),
 ("FS32_08_BUSY_ADMISSIONS_RETAIN_RESOURCES",
  ("controller","if (r31_admission_busy) {"),
  ("callback","fm_r28_gate_leave(&ctx->queue_admission);")),
 ("FS32_09_PCM_REENTRANCE_NOT_PROVEN",
  ("callback","atomic_flag_test_and_set_explicit(&ctx->pcm_writer_gate,"),
  ("pcm","AudioQueueEnqueueBuffer(ctx->queue,buf,0,NULL)")),
 ("FS32_10_QUARANTINE_PROCESS_EXIT_POLICY",
  ("controller","atomic_store_explicit(&fm_context_quarantined,1,memory_order_release);"),
  ("controller","/* GEN-R31 SOURCE-ONLY: close admission")),
)
LIMITATIONS=(
 "LEXICAL_SOURCE_ONLY_REVIEW_NO_C11_FORMAL_PROOF",
 "NO_REAL_OS_AUDIOQUEUESTOP_ERROR_PATH_OBSERVED",
 "NO_OS_CALLBACK_DISPATCH_QUESCENCE_TEST",
 "NO_ACOUSTIC_EM_INSTRUMENTAL_MEASUREMENT",
 "NO_SCIENTIFIC_SIMULATION_OR_SYNTHETIC_INTERLEAVING",
 "NO_BUREAU_INDEPENDENT_SIGNED_CERTIFICATION",
)
class R32Error(ValueError): pass
def require(ok,reason):
    if not ok: raise R32Error(reason)
def digest(data): return hashlib.sha256(data).hexdigest()
def index(text,token,start=0):
    require(token in text[start:],"R32 critical C anchor absent: "+token)
    return text.index(token,start)

def observe(source):
    require(source.startswith("/* SPDX-License-Identifier: Apache-2.0 */"),
            "R32 C candidate license/header drift")
    ctrl=r29.function(source,"controller")
    callback=r29.function(source,"callback")
    listener=r29.function(source,"listener")
    pcm=r29.function(source,"pcm")
    start=index(ctrl,"AudioQueueStart(ctx->queue,NULL)")
    close=index(ctrl,"fm_r28_gate_close(&ctx->queue_admission);",start)
    stop=index(ctrl,"const OSStatus r31_immediate_stop_status=AudioQueueStop(ctx->queue,true);",close)
    failed=index(ctrl,"if (r31_immediate_stop_status!=noErr) {",stop)
    quar=index(ctrl,"atomic_store_explicit(&fm_context_quarantined,1,memory_order_release);",failed)
    exit_fail=index(ctrl,"return -1;",quar)
    busy=index(ctrl,"if (r31_admission_busy) {",exit_fail)
    exit_busy=index(ctrl,"return -1;",busy)
    listener_remove=index(ctrl,"AudioQueueRemovePropertyListener(ctx->queue,",exit_busy)
    dispose=index(ctrl,"if (AudioQueueDispose(ctx->queue,true)!=noErr) {",listener_remove)
    clear=index(ctrl,"ctx->queue=NULL;",dispose)
    require(start<close<stop<failed<quar<exit_fail<busy<exit_busy<
            listener_remove<dispose<clear,
            "R32 failed-stop ownership ordering changed")
    # The failed-stop block intentionally keeps ambiguous queue resources
    # but makes no physical cutoff guarantee. No disposal or session reopening.
    failure_body=ctrl[failed:exit_fail]
    require("fm_latch_first_fault(ctx,FM_FAULT_SHUTDOWN);" in failure_body,
            "R32 stop failure no longer latches the shutdown fault")
    require("AudioQueueDispose(" not in failure_body
            and "free(owner_ctx)" not in failure_body
            and "ctx->queue=NULL" not in failure_body,
            "R32 failed-stop now disposes/clears ambiguous resources")
    require(ctrl.count("AudioQueueStop(ctx->queue,true)")==1,
            "R32 immediate stop call count drift")
    require(ctrl.count("if (r31_immediate_stop_status!=noErr) {")==1,
            "R32 OSStatus failure guard drift")
    require(ctrl.count("if (r31_admission_busy) {")==1,
            "R32 busy-lease branch drift")
    require(ctrl.count("fm_r28_gate_close(&ctx->queue_admission);")==3,
            "R32 closing gate count drift")
    require(source.count("fm_r28_gate_try_enter(&ctx->queue_admission)")==2 and
            source.count("fm_r28_gate_leave(&ctx->queue_admission);")==2,
            "R32 callback/listener lease count drift")
    require("if (!fm_r28_gate_try_enter(&ctx->queue_admission)) return;" in callback
            and "if (!fm_r28_gate_try_enter(&ctx->queue_admission)) return;" in listener,
            "R32 late OS callback admission protection drift")
    require("AudioQueueEnqueueBuffer(ctx->queue,buf,0,NULL)" in pcm
            and "atomic_flag_test_and_set_explicit(&ctx->pcm_writer_gate," in callback,
            "R32 inherited PCM risk shifted without re-review")
    require("/* GEN-R3: unconditional hard denial" in source,
            "R32 physical-output hard denial removed")
    require(len(FINDINGS)==10 and len(ANCHORS)==10
            and [x[0] for x in FINDINGS]==[x[0] for x in ANCHORS]
            and len({x[0] for x in FINDINGS})==10,
            "R32 open finding-to-source ledger invalid")
    for fid,one,two in ANCHORS:
        for part,needle in (one,two):
            block={"controller":ctrl,"callback":callback,
                   "listener":listener,"pcm":pcm}[part]
            require(needle in block,"R32 source evidence missing "+fid+": "+needle)
    return {x[0]:"OPEN_NOT_PROVEN" for x in FINDINGS}

def inspect(root,source_override=None):
    root=Path(root).resolve()
    table,manifest=r17.manifest_integrity(root)
    require(len(table)>=175,"R32 historical review requires at least 175 SHA-pinned files")
    required=(
      "audits/r32_failed_stop_ownership_review.py",
      "tests/test_r32_failed_stop_ownership_review.py",
      "RUN_GEN_R32_MAC_INTEL.command",
      "docs/GEN_R32_FAILED_STOP_CONTAINMENT.md",
      "docs/GEN_R32_BUREAU_REVIEW.md",
      "docs/GEN_R32_FAILURE_CASE_MATRIX.md",
    )
    require(all(x in table for x in required),"R32 unpinned review artifacts")
    historical=r31.inspect(root)
    require(historical[2]==table[r31.CANDIDATE],
            "R32 R31 candidate changed since baseline")
    require(table[r26.ORIGINAL]==r19.PINNED_ACOUSTIC_SHA256,
            "R32 original output backend altered")
    raw=(root/r31.CANDIDATE).read_bytes()
    require(digest(raw)==table[r31.CANDIDATE],"R32 R31 C SHA changed")
    checks=observe(raw.decode("utf-8") if source_override is None else source_override)
    runner=(root/"RUN_GEN_R32_MAC_INTEL.command").read_text(encoding="utf-8")
    require(set(r17.link_sources(runner))==r17.LINK_C_ALLOWLIST,
            "R32 runnable source allowlist shifted")
    fragments=runner.split(' -o "$WORK/freqmed-gen"')
    require(len(fragments)==2,"R32 executable compile/link boundary changed")
    actual_link=fragments[1].split("-framework CoreAudio",1)[0]
    require("output_hard_denied.c" in actual_link,
            "R32 must link the no-output backend")
    for path in ("acoustic_macos_r31.c","acoustic_macos_r29.c",
                 "acoustic_macos_r26.c","r28_callback_admission_gate.c",
                 "src/acoustic_macos.c"):
        require(path not in actual_link,"R32 dangerous backend linked: "+path)
    for marker in ("R32_FAILED_STOP_OWNERSHIP_REVIEW=PASS",
                   "R32_R31_CANDIDATE_OBJECT=COMPILED_UNLINKED",
                   "R32_NONEMITTING_EXECUTABLE_SYMBOL_AUDIT=PASS",
                   "R32_BUREAU_EVIDENCE_DOSSIER=26_FILES_SHA256_PASS",
                   "R32_TESTCASE_RUN_SLOT=PASS",
                   "FREQMED_GEN_R32_EVIDENCE_DIR",
                   "FREQMED_GEN_R32_BINARY"):
        require(marker in runner,"R32 runner marker absent: "+marker)
    return table,manifest,digest(raw),checks

def anchor(source,part,needle,source_sha):
    start,_,body=r27.function_span(source,part)
    require(needle in body,"R32 source anchor missing: "+needle)
    at=start+body.index(needle)
    return {"path":CANDIDATE,"function":part,
            "line":source.count("\n",0,at)+1,
            "source_sha256":source_sha,"needle":needle}

def audit(root,archive_r19,reports):
    table,manifest,csha,checks=inspect(root)
    previous=r31.audit(root,archive_r19,reports)
    recorded=json.loads(Path(reports["r31"]).read_text(encoding="utf-8"))
    require(previous==recorded,"R32 historical R31 report differs from recomputation")
    require(previous["r31_findings_open"]==8
            and previous["r31_critical_open"]==2
            and previous["r30_findings_open"]==12
            and previous["r30_critical_open"]==2
            and previous["r29_findings_open"]==7
            and previous["r28_gates_open"]==5
            and previous["r27_findings_open"]==9
            and previous["r23_obligations_open"]==15
            and previous["r24_findings_open"]==7
            and previous["bureau_gates_open"]==11
            and previous["bureau_gates_resolved"]==0,
            "R32 prior open obligations promoted without evidence")
    source=(Path(root)/CANDIDATE).read_text(encoding="utf-8")
    ledger=[]
    for info,sites in zip(FINDINGS,ANCHORS):
        fid,severity,role,proof=info
        require(fid==sites[0],"R32 evidence anchors misaligned")
        ledger.append({
          "id":fid,"severity":severity,"bureau_role":role,
          "status":checks[fid],"race_reproduced":False,
          "independent_approval":"NONE",
          "source_anchors":[anchor(source,*sites[1],csha),
                            anchor(source,*sites[2],csha)],
          "evidence_required":proof,
        })
    return {
      "schema":SCHEMA,"verdict":VERDICT,
      "method":"SOURCE_ONLY_C11_OSSTATUS_FAILED_STOP_CONTAINMENT_REVIEW",
      "manifest_sha256":manifest,"pinned_generator_files":len(table),
      "candidate_r31_sha256":csha,
      "original_C_sha256":table[r26.ORIGINAL],
      "r31_report_sha256":digest(Path(reports["r31"]).read_bytes()),
      "r32_findings":ledger,"r32_findings_open":10,
      "r32_critical_open":2,"r32_races_reproduced":0,
      "r32_candidate_C_edits":0,"r32_active_output":False,
      "failed_stop_status":"NOT_TESTED","failed_stop_physical_cutoff":"NOT_PROVEN",
      "stop_success_hardware_measurement":"NONE",
      "r31_findings_open":8,"r31_critical_open":2,
      "r30_findings_open":12,"r30_critical_open":2,
      "r29_findings_open":7,"r28_gates_open":5,"r27_findings_open":9,
      "r23_obligations_open":15,"r24_findings_open":7,
      "bureau_gates_open":11,"bureau_gates_resolved":0,
      "C11_race_freedom":"NOT_PROVEN",
      "CoreAudio_callback_quiescence":"NOT_PROVEN",
      "physical_stop":"NOT_PROVEN",
      "failed_AudioQueueDispose":"NOT_TESTED",
      "independent_signatures":"NONE","bureau_certification":"PENDING",
      "limitations":list(LIMITATIONS),
      "physical_emission":"NONE","scientific_simulation":"NONE",
      "acoustic_output":"LOCKED","em_output":"LOCKED",
      "real_output":"NOT_AUTHORIZED","biological_exposure":"NOT_AUTHORIZED",
      "production":"NOT_AUTHORIZED",
    }

def markdown(report):
    rows=["| "+f["id"]+" | "+f["severity"]+" | "+f["bureau_role"]+
          " | OPEN_NOT_PROVEN |" for f in report["r32_findings"]]
    return (
      "# FREQMED GEN-R32 — Failed-Stop Containment and Queue Ownership Review\n\n"
      "**Verdict: FAILED_STOP_CONTAINMENT_REVIEWED_PHYSICAL_SAFETY_UNPROVEN.**\n\n"
      "This audit observes that AudioQueueStop(queue,true) is attempted "
      "before the busy return; its OSStatus error still returns with "
      "potentially live CoreAudio resources. Quarantine is NOT an independent "
      "hardware cutoff. No active AudioQueueStop or simulation was executed.\n\n"
      "| Finding | Severity | Bureau | Status |\n|---|---|---|---|\n"+
      "\n".join(rows)+"\n\n"
      "R32=10 OPEN (2 CRITICAL); R31=8 OPEN (2 CRITICAL); "
      "R30=12 OPEN (2 CRITICAL); R29=7, R28=5, R27=9, "
      "R23=15, R24=7, Bureau=11 OPEN/0 closed.\n\n"
      "NEVER_SIMULATION=ENFORCED; ZERO_COST_FOSS=ENFORCED; "
      "ACOUSTIC_OUTPUT=LOCKED; EM_OUTPUT=LOCKED; "
      "REAL_OUTPUT=NOT_AUTHORIZED; BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED; "
      "PRODUCTION=NOT_AUTHORIZED.\n"
    )
def main():
    p=argparse.ArgumentParser(description="GEN-R32 independent source-only failed-stop review")
    p.add_argument("--root",required=True,type=Path)
    p.add_argument("--archive-r19",required=True,type=Path)
    for n in range(16,32):
        p.add_argument("--r"+str(n),required=True,type=Path)
    p.add_argument("--json",required=True,type=Path)
    p.add_argument("--markdown",required=True,type=Path)
    a=p.parse_args()
    try:
        paths={"r"+str(n):getattr(a,"r"+str(n)) for n in range(16,32)}
        result=audit(a.root,a.archive_r19,paths)
        a.json.write_text(json.dumps(result,indent=2,sort_keys=True,
                          ensure_ascii=False)+"\n",encoding="utf-8")
        a.markdown.write_text(markdown(result),encoding="utf-8")
    except (R32Error,r31.R31Error,r30.R30Error,r29.R29Error,r28.R28Error,
            r27.R27Error,r26.R26Error,ValueError,TypeError,KeyError,
            IndexError,OSError,UnicodeError) as err:
        print("R32_FAILED_STOP_OWNERSHIP_REVIEW=FAIL_CLOSED",str(err))
        return 2
    print("R32_FAILED_STOP_OWNERSHIP_REVIEW=PASS")
    print("R32_OPEN_FINDINGS=10; R32_CRITICAL=2; R32_RACES_REPRODUCED=0")
    print("R32_R31_FINDINGS=8_OPEN; R32_R31_CRITICAL=2_OPEN")
    print("R32_R30_FINDINGS=12_OPEN; R32_R30_CRITICAL=2_OPEN")
    print("R32_R29_FINDINGS=7_OPEN; R32_R28_GATES=5_OPEN; R32_R27_FINDINGS=9_OPEN")
    print("R32_BUREAU_GATES=11_OPEN; R32_BUREAU_RESOLVED=0")
    print("R32_REVIEW_VERDICT="+VERDICT)
    print("R32_FAILED_OS_STOP=NOT_TESTED; R32_PHYSICAL_STOP=NOT_PROVEN")
    print("R32_CALLBACK_QUIESCENCE=NOT_PROVEN; R32_C11_RACE_FREEDOM=NOT_PROVEN")
    print("R32_PHYSICAL_EMISSION=NONE; R32_SCIENTIFIC_SIMULATION=NONE")
    return 0
if __name__=="__main__":
    raise SystemExit(main())
