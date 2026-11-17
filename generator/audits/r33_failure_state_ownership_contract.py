#!/usr/bin/env python3
"""GEN-R33: source-only CoreAudio failure-state ownership and safe-abandonment contract.
No CoreAudio OS calls, no synthetic interleavings, no scientific simulation and no
physical output. Lexical evidence is NOT a C11/OS lifetime proof.
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
import r32_failed_stop_ownership_review as r32

SCHEMA="FREQMED_GEN_R33_COREAUDIO_FAILURE_STATE_OWNERSHIP_CONTRACT"
VERDICT="FAILURE_STATE_OWNERSHIP_CONTRACT_DOCUMENTED_NOT_CERTIFIED"
CANDIDATE=r31.CANDIDATE
FINDINGS=(
 ("OWN33_01_FAILED_STOP_LIVE_OUTPUT","CRITICAL","B10",
  "AudioQueueStop OSStatus failure has no proven physical cutoff; identify an independently qualified stop before any activation."),
 ("OWN33_02_CALLBACK_USERDATA_BEFORE_GATE","CRITICAL","B07",
  "Provide OS guarantee that callback userdata stays valid until all possible late entries have finished before a free."),
 ("OWN33_03_AMBIGUOUS_OS_QUEUE_RESOURCE","CRITICAL","B07",
  "Prove queue ownership and device state after failed stop/dispose; retained C pointer does not prove valid OS handle."),
 ("OWN33_04_PREPUBLICATION_FREE_SCOPE","HIGH","B09",
  "Prove prepublication exits really precede ALL callbacks and do not overlap other OS publications."),
 ("OWN33_05_QUEUE_NEWOUTPUT_FAILURE","HIGH","B07",
  "Characterize partial AudioQueueNewOutput failure; a failed constructor may have captured userdata."),
 ("OWN33_06_ROUTE_REJECT_DISPOSAL","HIGH","B07",
  "After route rejection and synchronous disposal distinguish OS queue lifetime and still-retained userdata."),
 ("OWN33_07_LISTENER_REGISTRATION_UNCERTAINTY","HIGH","B07",
  "Clarify OS listener registration failure, potential callbacks and subsequent ownership."),
 ("OWN33_08_BUSY_ADMISSION_KEEP_HEAP","HIGH","B09",
  "Prove all accepted leases complete and that late OS callbacks cannot enter after the gate is closed."),
 ("OWN33_09_LISTENER_REMOVE_FAILURE","HIGH","B07",
  "Specify resource/callback state when removing a listener fails but disposal is attempted."),
 ("OWN33_10_SUCCESSFUL_DISPOSE_NOT_SAFE_FREE","HIGH","B09",
  "Prove callback quiescence and C11 happens-before before freeing userdata even after successful disposal."),
 ("OWN33_11_PCM_REENTRANCY_QUEUE_RACE","HIGH","B09",
  "Prove enqueue/stop concurrency and the absence of reentrancy under pcm_writer_gate."),
 ("OWN33_12_QUARANTINE_AND_ABANDONMENT_SCOPE","HIGH","B10",
  "Bound retained heap and OS resources and define process exit responsibility without claiming physical stop."),
)
# Conditional outcomes are review-policy descriptions, NEVER executable transitions.
STATES=(
 ("PRE_PUBLISH_INVALID_FRAMES","C_HEAP_OWNER","NO_QUEUE_PUBLISHED",
  "PREPUBLICATION_RELEASE_SOURCE_PATH","PHYSICAL_CUTOFF_NOT_APPLICABLE",
  ("free(owner_ctx);","if (!ctx->total_frames) {")),
 ("PRE_PUBLISH_INVALID_FADE","C_HEAP_OWNER","NO_QUEUE_PUBLISHED",
  "PREPUBLICATION_RELEASE_SOURCE_PATH","PHYSICAL_CUTOFF_NOT_APPLICABLE",
  ("if (ctx->fade_frames==0U) {","free(owner_ctx);")),
 ("NEW_OUTPUT_ERROR","PUBLISHED_POSSIBLE","OS_QUEUE_UNDETERMINED",
  "RETAIN_HEAP_NO_RETRY","NOT_PROVEN",
  ("if (AudioQueueNewOutput(&fmt,output_callback,ctx,NULL,NULL,0,&ctx->queue)!=noErr) {",
   "fm_r28_gate_close(&ctx->queue_admission);")),
 ("ROUTE_REJECT_DISPOSE_SUCCESS","PUBLISHED","OS_DISPOSE_SUCCESS_CLAIM",
  "RETAIN_USERDATA_NO_RETRY","NOT_PROVEN",
  ("if (fm_acoustic_bind_queue_to_route((void *)ctx->queue,&route)!=0) {",
   "if (bind_dispose_status==noErr) {")),
 ("ROUTE_REJECT_DISPOSE_FAILURE","PUBLISHED","OS_QUEUE_UNDETERMINED",
  "RETAIN_HEAP_AND_QUEUE_HANDLE_NO_RETRY","NOT_PROVEN",
  ("const OSStatus bind_dispose_status=AudioQueueDispose(ctx->queue,true);",
   "atomic_store_explicit(&fm_context_quarantined,1,memory_order_release);")),
 ("STOP_FAILURE","PUBLISHED","OS_QUEUE_POSSIBLY_ACTIVE",
  "RETAIN_HEAP_QUEUE_NO_RETRY","NOT_PROVEN",
  ("if (r31_immediate_stop_status!=noErr) {",
   "fm_latch_first_fault(ctx,FM_FAULT_SHUTDOWN);")),
 ("STOP_SUCCESS_BUSY_LEASE","PUBLISHED","OS_QUEUE_MAY_HAVE_LATE_CALLBACK",
  "RETAIN_HEAP_QUEUE_NO_DISPOSE","NOT_PROVEN",
  ("if (r31_admission_busy) {",
   "This does NOT establish OS callback quiescence")),
 ("LISTENER_REMOVE_FAILURE","PUBLISHED","LISTENER_STATE_UNDETERMINED",
  "RETAIN_USERDATA_NEEDS_OS_PROOF","NOT_PROVEN",
  ("listener_remove_failed=1;",
   "AudioQueueRemovePropertyListener(ctx->queue,")),
 ("FINAL_DISPOSE_FAILURE","PUBLISHED","OS_QUEUE_UNDETERMINED",
  "RETAIN_HEAP_QUEUE_NO_RETRY","NOT_PROVEN",
  ("if (AudioQueueDispose(ctx->queue,true)!=noErr) {",
   "no automatic retry is allowed")),
 ("FINAL_DISPOSE_SUCCESS","PUBLISHED","OS_DISPOSE_SUCCESS_CLAIM",
  "RETAIN_HEAP_PENDING_CALLBACK_PROOF","NOT_PROVEN",
  ("atomic_store(&ctx->dispose_confirmed,1);","ctx->queue=NULL;")),
)
LIMITATIONS=(
 "STATE_CLASSES_ARE_DOCUMENTARY_NOT_IMPLEMENTED_MACHINE",
 "NO_OSSTATUS_FAILED_STOP_DISPOSE_EXECUTED",
 "NO_HAPPENS_BEFORE_FORMAL_PROOF_OR_OS_CALLBACK_QUIESCENCE",
 "NO_INSTRUMENTAL_PHYSICAL_EMISSION_OR_CUTOFF_MEASUREMENT",
 "NO_COREAUDIO_API_LINKED_IN_EXECUTABLE",
 "NO_INDEPENDENT_BUREAU_SIGNATURE",
)
class R33Error(ValueError): pass
def require(ok,reason):
    if not ok: raise R33Error(reason)
def sha(data): return hashlib.sha256(data).hexdigest()
def locate(text,token,start=0):
    require(token in text[start:],"R33 missing source anchor: "+token)
    return text.index(token,start)

def observe(source):
    """Conservative text-level boundary and state presence checks ONLY."""
    require(source.startswith("/* SPDX-License-Identifier: Apache-2.0 */"),
            "R33 source license/header drift")
    ctrl=r29.function(source,"controller")
    pcm=r29.function(source,"pcm")
    callback=r29.function(source,"callback")
    listener=r29.function(source,"listener")
    create=locate(ctrl,"AudioQueueNewOutput(&fmt,output_callback,ctx")
    free_first=locate(ctrl,"if (!ctx->total_frames) {")
    free_second=locate(ctrl,"if (ctx->fade_frames==0U) {",free_first)
    require(free_first<free_second<create and
            ctrl[:create].count("free(owner_ctx);")==2 and
            ctrl[create:].count("free(owner_ctx);")==0,
            "R33 pre/post publication heap-release distinction lost")
    fail_new=locate(ctrl,"if (AudioQueueNewOutput(&fmt,output_callback,ctx,NULL,NULL,0,&ctx->queue)!=noErr) {",create-90)
    stop=locate(ctrl,"const OSStatus r31_immediate_stop_status=AudioQueueStop(ctx->queue,true);")
    fail_stop=locate(ctrl,"if (r31_immediate_stop_status!=noErr) {",stop)
    stop_ret=locate(ctrl,"return -1;",fail_stop)
    busy=locate(ctrl,"if (r31_admission_busy) {",stop_ret)
    busy_ret=locate(ctrl,"return -1;",busy)
    listener_remove=locate(ctrl,"AudioQueueRemovePropertyListener(ctx->queue,",busy_ret)
    dispose=locate(ctrl,"if (AudioQueueDispose(ctx->queue,true)!=noErr) {",listener_remove)
    dispose_clear=locate(ctrl,"ctx->queue=NULL;",dispose)
    require(fail_new<stop<fail_stop<stop_ret<busy<busy_ret<
            listener_remove<dispose<dispose_clear,
            "R33 OS failure-state source ordering drift")
    require("AudioQueueDispose(" not in ctrl[fail_stop:stop_ret]
            and "free(owner_ctx)" not in ctrl[fail_stop:stop_ret]
            and "ctx->queue=NULL" not in ctrl[fail_stop:stop_ret],
            "R33 stop failure now releases ambiguous resource")
    require("AudioQueueDispose(" not in ctrl[busy:busy_ret]
            and "free(owner_ctx)" not in ctrl[busy:busy_ret],
            "R33 busy admission now disposes/reclaims resources")
    require("listener_remove_failed=1;" in ctrl[listener_remove:dispose]
            and "fm_latch_first_fault(ctx,FM_FAULT_LISTENER_REMOVAL);" in ctrl[listener_remove:dispose],
            "R33 listener removal error not tracked")
    require("atomic_store(&ctx->dispose_confirmed,1);" in ctrl[dispose:dispose_clear]
            and "fm_latch_first_fault(ctx,FM_FAULT_DISPOSAL);" in ctrl[dispose:dispose_clear],
            "R33 disposal success/failure evidence lost")
    require("atomic_store_explicit(&fm_context_quarantined,1,memory_order_release);" in ctrl[fail_stop:stop_ret]
            and "atomic_store_explicit(&fm_context_quarantined,1,memory_order_release);" in ctrl[busy:busy_ret],
            "R33 uncertainty no longer imposes process quarantine")
    require("if (!fm_r28_gate_try_enter(&ctx->queue_admission)) return;" in callback
            and "if (!fm_r28_gate_try_enter(&ctx->queue_admission)) return;" in listener,
            "R33 OS entry still requires retained userdata before gate")
    require("AudioQueueEnqueueBuffer(ctx->queue,buf,0,NULL)" in pcm,
            "R33 PCM inherited queue ownership site missing")
    require("/* GEN-R3: unconditional hard denial" in source,
            "R33 public output denial altered")
    require(len(FINDINGS)==12 and len(STATES)==10 and
            len({f[0] for f in FINDINGS})==12 and len({s[0] for s in STATES})==10,
            "R33 expected finding/state cardinals changed")
    for name,owner,os_state,decision,physical,anchors in STATES:
        require(owner and os_state and decision and physical,
                "R33 undefined ownership/OS-state contract "+name)
        for token in anchors:
            require(token in ctrl,
                    "R33 source state anchor missing "+name+": "+token)
    return {x[0]:"OPEN_NOT_PROVEN" for x in FINDINGS}

def inspect(root,source_override=None):
    root=Path(root).resolve()
    table,manifest=r17.manifest_integrity(root)
    require(len(table)>=181,"R33 historical audit requires at least 181 SHA-pinned files")
    needed=(
       "audits/r33_failure_state_ownership_contract.py",
       "tests/test_r33_failure_state_ownership_contract.py",
       "RUN_GEN_R33_MAC_INTEL.command",
       "docs/GEN_R33_FAILURE_STATE_OWNERSHIP.md",
       "docs/GEN_R33_BUREAU_REVIEW.md",
       "docs/GEN_R33_SAFE_ABANDONMENT_MATRIX.md",
    )
    require(all(name in table for name in needed),
            "R33 source-only dossier files not hash pinned")
    old=r32.inspect(root)
    require(old[2]==table[r31.CANDIDATE],
            "R33 candidate R31 baseline changed")
    require(table[r26.ORIGINAL]==r19.PINNED_ACOUSTIC_SHA256,
            "R33 original C backend changed")
    raw=(root/CANDIDATE).read_bytes()
    require(sha(raw)==table[CANDIDATE],"R33 R31 candidate SHA mismatch")
    checks=observe(raw.decode("utf-8") if source_override is None
                   else source_override)
    runner=(root/"RUN_GEN_R33_MAC_INTEL.command").read_text(encoding="utf-8")
    require(set(r17.link_sources(runner))==r17.LINK_C_ALLOWLIST,
            "R33 executable allowlist changed")
    linked=runner.split(' -o "$WORK/freqmed-gen"')
    require(len(linked)==2,"R33 link command changed")
    section=linked[1].split("-framework CoreAudio",1)[0]
    require("output_hard_denied.c" in section,"R33 no-output link missing")
    for token in ("acoustic_macos_r31.c","acoustic_macos_r29.c",
                  "acoustic_macos_r26.c","r28_callback_admission_gate.c",
                  "src/acoustic_macos.c"):
        require(token not in section,"R33 output candidate linked "+token)
    for marker in ("R33_FAILURE_STATE_OWNERSHIP_REVIEW=PASS",
                   "R33_R31_CANDIDATE_OBJECT=COMPILED_UNLINKED",
                   "R33_NONEMITTING_EXECUTABLE_SYMBOL_AUDIT=PASS",
                   "R33_BUREAU_CONTRACT_DOSSIER=28_FILES_SHA256_PASS",
                   "R33_TESTCASE_RUN_SLOT=PASS",
                   "FREQMED_GEN_R33_EVIDENCE_DIR",
                   "FREQMED_GEN_R33_BINARY"):
        require(marker in runner,"R33 runner contract missing "+marker)
    return table,manifest,sha(raw),checks

def proof_anchor(text,section,needle,csha):
    start,_,body=r27.function_span(text,section)
    require(needle in body,"R33 proof source missing: "+needle)
    at=start+body.index(needle)
    return {"path":CANDIDATE,"function":section,
            "line":text.count("\n",0,at)+1,
            "sha256":csha,"needle":needle}

def audit(root,archive_r19,reports):
    table,manifest,csha,checks=inspect(root)
    prior=r32.audit(root,archive_r19,reports)
    recorded=json.loads(Path(reports["r32"]).read_text(encoding="utf-8"))
    require(recorded==prior,"R33 R32 historical report differs from recomputation")
    require(prior["r32_findings_open"]==10 and prior["r32_critical_open"]==2
            and prior["r31_findings_open"]==8 and prior["r31_critical_open"]==2
            and prior["r30_findings_open"]==12 and prior["r30_critical_open"]==2
            and prior["r29_findings_open"]==7 and prior["r28_gates_open"]==5
            and prior["r27_findings_open"]==9
            and prior["r23_obligations_open"]==15
            and prior["r24_findings_open"]==7
            and prior["bureau_gates_open"]==11
            and prior["bureau_gates_resolved"]==0,
            "R33 historical obligations improperly discharged")
    source=(Path(root)/CANDIDATE).read_text(encoding="utf-8")
    # Ledger does not grant runtime ownership transitions; only source anchors.
    anchors=(
      ("controller","if (r31_immediate_stop_status!=noErr) {"),
      ("callback","if (!fm_r28_gate_try_enter(&ctx->queue_admission)) return;"),
      ("controller","if (AudioQueueDispose(ctx->queue,true)!=noErr) {"),
      ("controller","free(owner_ctx);"),
      ("controller","if (AudioQueueNewOutput(&fmt,output_callback,ctx,NULL,NULL,0,&ctx->queue)!=noErr) {"),
      ("controller","if (bind_dispose_status==noErr) {"),
      ("controller","listener_registration_uncertain=1;"),
      ("controller","if (r31_admission_busy) {"),
      ("controller","listener_remove_failed=1;"),
      ("controller","atomic_store(&ctx->dispose_confirmed,1);"),
      ("pcm","AudioQueueEnqueueBuffer(ctx->queue,buf,0,NULL)"),
      ("controller","atomic_store_explicit(&fm_context_quarantined,1,memory_order_release);"),
    )
    ledger=[]
    for f,(section,needle) in zip(FINDINGS,anchors):
        fid,severity,role,missing=f
        ledger.append({"id":fid,"severity":severity,"bureau_role":role,
            "status":checks[fid],"actual_OS_failure_tested":False,
            "independent_approval":"NONE",
            "source_anchor":proof_anchor(source,section,needle,csha),
            "proof_required":missing})
    state_rows=[]
    for name,owner,os_state,policy,cutoff,anchors in STATES:
        state_rows.append({"state":name,"owner":owner,
         "os_queue_state":os_state,"conservative_source_policy":policy,
         "physical_cutoff":cutoff,"proven_safe_release":False,
         "source_anchors":[proof_anchor(source,"controller",token,csha)
                           for token in anchors]})
    return {
      "schema":SCHEMA,"verdict":VERDICT,
      "method":"SHA_PINNED_SOURCE_ONLY_OWNERSHIP_STATE_CONTRACT_REVIEW",
      "manifest_sha256":manifest,"pinned_generator_files":len(table),
      "candidate_r31_sha256":csha,
      "original_C_sha256":table[r26.ORIGINAL],
      "r32_report_sha256":sha(Path(reports["r32"]).read_bytes()),
      "r33_findings":ledger,"r33_findings_open":12,
      "r33_critical_open":3,"r33_state_rows":state_rows,
      "r33_documentary_states":len(STATES),
      "r33_real_OS_errors_observed":0,
      "r33_source_C_edits":0,"r33_output_linked":False,
      "r32_findings_open":10,"r32_critical_open":2,
      "r31_findings_open":8,"r31_critical_open":2,
      "r30_findings_open":12,"r30_critical_open":2,
      "r29_findings_open":7,"r28_gates_open":5,"r27_findings_open":9,
      "r23_obligations_open":15,"r24_findings_open":7,
      "bureau_gates_open":11,"bureau_gates_resolved":0,
      "C11_race_freedom":"NOT_PROVEN",
      "CoreAudio_callback_quiescence":"NOT_PROVEN",
      "failed_AudioQueueStop":"NOT_TESTED",
      "failed_AudioQueueDispose":"NOT_TESTED",
      "physical_cutoff":"NOT_PROVEN",
      "independent_signatures":"NONE","bureau_certification":"PENDING",
      "limitations":list(LIMITATIONS),
      "physical_emission":"NONE","scientific_simulation":"NONE",
      "acoustic_output":"LOCKED","em_output":"LOCKED",
      "real_output":"NOT_AUTHORIZED",
      "biological_exposure":"NOT_AUTHORIZED",
      "production":"NOT_AUTHORIZED",
    }
def markdown(report):
    body=["| "+x["id"]+" | "+x["severity"]+" | "+x["bureau_role"]+
          " | OPEN_NOT_PROVEN |" for x in report["r33_findings"]]
    matrix=["| "+x["state"]+" | "+x["conservative_source_policy"]+
            " | "+x["os_queue_state"]+" |" for x in report["r33_state_rows"]]
    return ("# FREQMED GEN-R33 — Failed CoreAudio State Ownership Contract\n\n"
      "**Verdict: FAILURE_STATE_OWNERSHIP_CONTRACT_DOCUMENTED_NOT_CERTIFIED.**\n\n"
      "The classes below are source-only documentary categories, not a "
      "runtime state machine or permission to release resources. Even a "
      "successful OS dispose does not by itself prove late callback quiescence.\n\n"
      "| Finding | Severity | Bureau | Status |\n|---|---|---|---|\n"
      +"\n".join(body)+"\n\n"
      "| State | Conservative source policy | OS queue state |\n"
      "|---|---|---|\n"+"\n".join(matrix)+"\n\n"
      "All 12 R33 obligations, including three CRITICAL, remain open. "
      "R32=10, R31=8, R30=12, R29=7, R28=5, R27=9, R23=15, "
      "R24=7 and Bureau=11 remain OPEN. No OS failure was induced, no "
      "scientific simulation and no physical emission.\n\n"
      "NEVER_SIMULATION=ENFORCED; ZERO_COST_FOSS=ENFORCED; "
      "ACOUSTIC_OUTPUT=LOCKED; EM_OUTPUT=LOCKED; REAL_OUTPUT=NOT_AUTHORIZED; "
      "BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED; PRODUCTION=NOT_AUTHORIZED.\n")
def main():
    p=argparse.ArgumentParser(description="GEN-R33 CoreAudio failure-state C11 review")
    p.add_argument("--root",type=Path,required=True)
    p.add_argument("--archive-r19",type=Path,required=True)
    for n in range(16,33):
        p.add_argument("--r"+str(n),type=Path,required=True)
    p.add_argument("--json",type=Path,required=True)
    p.add_argument("--markdown",type=Path,required=True)
    a=p.parse_args()
    try:
        paths={"r"+str(n):getattr(a,"r"+str(n)) for n in range(16,33)}
        report=audit(a.root,a.archive_r19,paths)
        a.json.write_text(json.dumps(report,sort_keys=True,indent=2,
                         ensure_ascii=False)+"\n",encoding="utf-8")
        a.markdown.write_text(markdown(report),encoding="utf-8")
    except (R33Error,r32.R32Error,r31.R31Error,r30.R30Error,r29.R29Error,
            r28.R28Error,r27.R27Error,r26.R26Error,ValueError,TypeError,
            KeyError,IndexError,OSError,UnicodeError) as err:
        print("R33_FAILURE_STATE_OWNERSHIP_REVIEW=FAIL_CLOSED",str(err))
        return 2
    print("R33_FAILURE_STATE_OWNERSHIP_REVIEW=PASS")
    print("R33_CONTRACT_STATES=10_DOCUMENTARY; R33_REAL_OS_FAILURES=0")
    print("R33_FINDINGS=12_OPEN; R33_CRITICAL=3_OPEN")
    print("R33_R32_FINDINGS=10_OPEN; R33_R32_CRITICAL=2_OPEN")
    print("R33_R31_FINDINGS=8_OPEN; R33_R30_FINDINGS=12_OPEN")
    print("R33_R23_OBLIGATIONS=15_OPEN; R33_R24_FINDINGS=7_OPEN")
    print("R33_BUREAU_GATES=11_OPEN; R33_BUREAU_RESOLVED=0")
    print("R33_REVIEW_VERDICT="+VERDICT)
    print("R33_PHYSICAL_CUTOFF=NOT_PROVEN; R33_C11_RACE_FREEDOM=NOT_PROVEN")
    print("R33_CALLBACK_QUIESCENCE=NOT_PROVEN")
    print("R33_PHYSICAL_EMISSION=NONE; R33_SCIENTIFIC_SIMULATION=NONE")
    return 0
if __name__=="__main__":
    raise SystemExit(main())
