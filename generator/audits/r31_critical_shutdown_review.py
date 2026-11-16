#!/usr/bin/env python3
"""GEN-R31 isolated C11/OS shutdown-design review, source-only.
No simulation, no live CoreAudio callback, no instrument, no physical output.
An attempted synchronous stop is not proof of physical stop or OS quiescence.
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

SCHEMA="FREQMED_GEN_R31_CRITICAL_SHUTDOWN_REMEDIATION_DESIGN"
VERDICT="SHUTDOWN_STOP_ATTEMPT_REORDERED_SOURCE_ONLY_OS_SAFETY_UNPROVEN"
CANDIDATE="candidates/acoustic_macos_r31.c"
SOURCE_HEADER=("/* GEN-R31 REMEDIATION CANDIDATE. ISOLATED. NEVER LINK, LOAD, CALL, OR EMIT.\n"
 " * This source changes control-flow structure only; NO OS or C11 proof. */\n")
OLD_START="  /* Seal admission before OS cleanup."
NEW_START="  /* GEN-R31 SOURCE-ONLY: close admission, then ATTEMPT immediate OS stop"
SHARED_TAIL="    if (listener_installed) {"

# id, severity, role, independently required proof. No proof is discharged.
FINDINGS=(
 ("SH31_01_STOP_BEFORE_BUSY_EXIT","CRITICAL","B10",
  "Prove actual OS stop success and bounded completion for a live callback; source-only ordering merely removes the known bypass."),
 ("SH31_02_FAILED_STOP_MAY_STILL_EMIT","CRITICAL","B10",
  "Qualify AudioQueueStop failure status and establish an independent physical safety strategy. Quarantine does not cut off audio."),
 ("SH31_03_BUSY_LEASES_KEEP_RESOURCES","HIGH","B09",
  "Prove that accepted callbacks finish, that userdata remains valid and queue is not disposed while leased."),
 ("SH31_04_STOP_CONTROLLER_QUEUE_RACE","HIGH","B09",
  "Prove exclusive controller lifetime authority and a C11 happens-before relationship for each ctx->queue access."),
 ("SH31_05_LISTENER_REMOVE_AND_DISPOSE","HIGH","B07",
  "Audit listener removal failure and disposal failure, including callbacks already dispatched and buffer ownership."),
 ("SH31_06_LATE_USERDATA_OS_ADMISSION","HIGH","B07",
  "Prove OS callback admission has terminated before any reclamation even after the gate is closed."),
 ("SH31_07_ENQUEUE_PCM_REENTRANCE","HIGH","B09",
  "Prove callback nonblocking and nonreentrance for AudioQueueEnqueueBuffer under pcm_writer_gate."),
 ("SH31_08_QUARANTINE_RESOURCE_BOUND","HIGH","B10",
  "Define bounded process quarantine, retained queue lifecycle, and an actual hardware safety case before activation."),
)
LIMITATIONS=(
 "BYTE_SCOPED_SOURCE_REWRITE_NOT_FORMAL_C11_CONTROL_FLOW_PROOF",
 "NO_ACTIVE_AUDIOQUEUESTOP_OR_OSSTATUS_FAILURE_EXECUTION",
 "NO_MEASUREMENT_OF_ACOUSTIC_HARDWARE_STOP_OR_OUTPUT",
 "NO_LATE_CALLBACK_OS_ADMISSION_OR_LISTENER_QUIESCENCE_PROOF",
 "NO_REENTRANCY_REALTIME_OR_FULL_HAPPENS_BEFORE_PROOF",
 "NO_INDEPENDENT_BUREAU_SIGNATURE",
)
class R31Error(ValueError): pass
def require(ok,why):
    if not ok: raise R31Error(why)
def sha(data): return hashlib.sha256(data).hexdigest()

def _shutdown_piece(text,start):
    section=r29.function(text,"controller")
    require(section.count(start)==1,"R31 shutdown marker count drift: "+start)
    a=section.index(start)
    b=section.index(SHARED_TAIL,a)
    require(a<b,"R31 shutdown slice missing")
    return section[a:b]

def exact_scope(old,new):
    """Demonstrate precisely one descriptive header and one shutdown-slice rewrite.
    Do not confuse that structural observation with runtime safety.
    """
    require(old.startswith("/* SPDX-License-Identifier: Apache-2.0 */"),
            "R31 historic R29 C baseline changed")
    require(new.count(SOURCE_HEADER)==1 and
            new.count(NEW_START)==1 and new.count(OLD_START)==0,
            "R31 new source/header markers drift")
    old_piece=_shutdown_piece(old,OLD_START)
    new_piece=_shutdown_piece(new,NEW_START)
    restored=new.replace(SOURCE_HEADER,"",1).replace(new_piece,old_piece,1)
    require(restored==old,"R31 edits outside isolated C header/shutdown block")
    return new_piece

def observe(old,new):
    piece=exact_scope(old,new)
    ctrl=r29.function(new,"controller")
    require(len(FINDINGS)==8 and len({x[0] for x in FINDINGS})==8,
            "R31 findings count/IDs drift")
    require(new.count("fm_r28_gate_try_enter(&ctx->queue_admission)")==2 and
            new.count("fm_r28_gate_leave(&ctx->queue_admission);")==2 and
            ctrl.count("fm_r28_gate_close(&ctx->queue_admission);")==3,
            "R31 callback admission/lease lifecycle drift")
    close=piece.index("fm_r28_gate_close(&ctx->queue_admission);")
    busy=piece.index("const int r31_admission_busy=")
    first_if=piece.index("if (ctx->queue) {",busy)
    stop=piece.index("const OSStatus r31_immediate_stop_status=AudioQueueStop(ctx->queue,true);")
    failure=piece.index("if (r31_immediate_stop_status!=noErr) {")
    quarantine=piece.index("atomic_store_explicit(&fm_context_quarantined,1,memory_order_release);",failure)
    fail_return=piece.index("return -1;",failure)
    busy_guard=piece.index("if (r31_admission_busy) {")
    busy_return=piece.index("return -1;",busy_guard)
    require(close<busy<first_if<stop<failure<quarantine<fail_return<
            busy_guard<busy_return,
            "R31 stop MUST precede any admission-busy return")
    require(piece.count("AudioQueueStop(ctx->queue,true)")==1 and
            piece.count("return -1;")==2,
            "R31 stop or early return count changed")
    require("if (r31_immediate_stop_status!=noErr)" in piece and
            "fm_latch_first_fault(ctx,FM_FAULT_SHUTDOWN);" in piece,
            "R31 failure path must latch, quarantine and fail closed")
    require("AudioQueueDispose(" not in piece and
            "free(owner_ctx)" not in piece and
            "atomic_flag_clear_explicit(&fm_session_claim" not in piece,
            "R31 uncertainty must retain OS resources, userdata, session gate")
    require("if (ctx->queue) {\n    if (listener_installed) {" in ctrl,
            "R31 listener cleanup remains outside busy branch")
    require("if (AudioQueueDispose(ctx->queue,true)!=noErr)" in ctrl,
            "R31 disposal-status handler changed")
    require("ctx->queue=NULL;" in ctrl and
            "AudioQueueEnqueueBuffer(ctx->queue,buf,0,NULL)" in new and
            "/* GEN-R3: unconditional hard denial" in new,
            "R31 inherited output/queue hazards or hard denial changed")
    # This is source-level detection of a specific bypass being removed.
    return {f[0]:"OPEN_NOT_PROVEN" for f in FINDINGS}

def inspect(root,override=None):
    root=Path(root).resolve()
    table,manifest=r17.manifest_integrity(root)
    require(len(table)==169,"R31 requires 169 SHA-pinned generator files")
    artifacts=(
        CANDIDATE,
        "audits/r31_critical_shutdown_review.py",
        "tests/test_r31_critical_shutdown_review.py",
        "RUN_GEN_R31_MAC_INTEL.command",
        "docs/GEN_R31_SHUTDOWN_REMEDIATION.md",
        "docs/GEN_R31_BUREAU_REVIEW.md",
        "docs/GEN_R31_PROOF_OBLIGATIONS.md",
    )
    require(all(a in table for a in artifacts),"R31 dossier artifact not pinned")
    baseline=r30.inspect(root)
    require(table[r29.CANDIDATE]==baseline[2],
            "R31 inherited R29 C source changed")
    require(table[r28.CANDIDATE]==r28.inspect(root)[2],
            "R31 R28 admission gate changed")
    require(table[r26.ORIGINAL]==r19.PINNED_ACOUSTIC_SHA256,
            "R31 original source changed")
    old=(root/r29.CANDIDATE).read_text(encoding="utf-8")
    raw=(root/CANDIDATE).read_bytes()
    require(sha(raw)==table[CANDIDATE],"R31 C candidate SHA mismatch")
    checks=observe(old,raw.decode("utf-8") if override is None else override)
    run=(root/"RUN_GEN_R31_MAC_INTEL.command").read_text(encoding="utf-8")
    require(set(r17.link_sources(run))==r17.LINK_C_ALLOWLIST,
            "R31 changed executable link allowlist")
    split=run.split(' -o "$WORK/freqmed-gen"')
    require(len(split)==2,"R31 executable link boundary missing")
    linked=split[1].split("-framework CoreAudio",1)[0]
    require("output_hard_denied.c" in linked,"R31 must keep hard-denial C linked")
    for deny in ("acoustic_macos_r31.c","acoustic_macos_r29.c",
                 "acoustic_macos_r26.c","r28_callback_admission_gate.c",
                 "src/acoustic_macos.c"):
        require(deny not in linked,"R31 candidate illegally linked "+deny)
    for marker in (
        "R31_REMEDIATION_CANDIDATE_OBJECT=COMPILED_UNLINKED",
        "R31_NONEMITTING_EXECUTABLE_SYMBOL_AUDIT=PASS",
        "R31_BUREAU_PROOF_DOSSIER=24_FILES_SHA256_PASS",
        "R31_TESTCASE_RUN_SLOT=PASS",
        "FREQMED_GEN_R31_EVIDENCE_DIR",
        "FREQMED_GEN_R31_BINARY",
    ):
        require(marker in run,"R31 runner guard absent: "+marker)
    return table,manifest,sha(raw),checks

def anchor(text,section,needle,source_sha):
    start,end,body=r27.function_span(text,section)
    require(needle in body,"R31 source proof anchor missing "+section+": "+needle)
    at=start+body.index(needle)
    return {"path":CANDIDATE,"function":section,
            "line":text.count("\n",0,at)+1,
            "source_sha256":source_sha,"needle":needle}

def audit(root,archive_r19,reports):
    table,manifest,csha,checks=inspect(root)
    prior=r30.audit(root,archive_r19,reports)
    recorded=json.loads(Path(reports["r30"]).read_text(encoding="utf-8"))
    require(prior==recorded,
            "R31 report R30 not identical to recalculated historical evidence")
    require(prior["r30_findings_open"]==12 and
            prior["r30_critical_open"]==2 and
            prior["r29_findings_open"]==7 and
            prior["r28_gates_open"]==5 and
            prior["r27_findings_open"]==9 and
            prior["r23_obligations_open"]==15 and
            prior["r24_findings_open"]==7 and
            prior["bureau_gates_open"]==11 and prior["bureau_gates_resolved"]==0,
            "R31 historical proof gates were improperly promoted")
    new=(Path(root)/CANDIDATE).read_text(encoding="utf-8")
    place=(
      ("SH31_01_STOP_BEFORE_BUSY_EXIT",
       ("controller","r31_immediate_stop_status=AudioQueueStop(ctx->queue,true);"),
       ("controller","if (r31_admission_busy) {")),
      ("SH31_02_FAILED_STOP_MAY_STILL_EMIT",
       ("controller","if (r31_immediate_stop_status!=noErr) {"),
       ("controller","fm_context_quarantined,1,memory_order_release")),
      ("SH31_03_BUSY_LEASES_KEEP_RESOURCES",
       ("controller","if (r31_admission_busy) {"),
       ("callback","fm_r28_gate_leave(&ctx->queue_admission);")),
      ("SH31_04_STOP_CONTROLLER_QUEUE_RACE",
       ("controller","r31_immediate_stop_status=AudioQueueStop(ctx->queue,true);"),
       ("pcm","AudioQueueEnqueueBuffer(ctx->queue,buf,0,NULL)")),
      ("SH31_05_LISTENER_REMOVE_AND_DISPOSE",
       ("controller","AudioQueueRemovePropertyListener(ctx->queue,"),
       ("controller","AudioQueueDispose(ctx->queue,true)")),
      ("SH31_06_LATE_USERDATA_OS_ADMISSION",
       ("callback","if (!fm_r28_gate_try_enter(&ctx->queue_admission))"),
       ("listener","if (!fm_r28_gate_try_enter(&ctx->queue_admission))")),
      ("SH31_07_ENQUEUE_PCM_REENTRANCE",
       ("pcm","AudioQueueEnqueueBuffer(ctx->queue,buf,0,NULL)"),
       ("callback","atomic_flag_test_and_set_explicit(&ctx->pcm_writer_gate,")),
      ("SH31_08_QUARANTINE_RESOURCE_BOUND",
       ("controller","if (r31_admission_busy) {"),
       ("controller","ctx->queue=NULL;")),
    )
    require([a[0] for a in place]==[a[0] for a in FINDINGS],
            "R31 anchor ledger order changed")
    ledger=[]
    for (name,severity,role,proof),(key,one,two) in zip(FINDINGS,place):
        require(name==key,"R31 source proof ID mismatch")
        ledger.append({
            "id":name,"severity":severity,"bureau_role":role,
            "status":checks[name],"source_only":True,
            "race_reproduced":False,
            "anchors":[anchor(new,*one,csha),anchor(new,*two,csha)],
            "evidence_required":proof,"independent_approval":"NONE",
        })
    return {
      "schema":SCHEMA,"verdict":VERDICT,
      "method":"EXACT_SCOPED_C11_C_REWRITE_SHA_ANCHORED_SOURCE_REVIEW",
      "manifest_sha256":manifest,
      "pinned_generator_files":len(table),
      "r31_candidate_sha256":csha,
      "r29_candidate_sha256":table[r29.CANDIDATE],
      "original_C_sha256":table[r26.ORIGINAL],
      "r30_report_sha256":sha(Path(reports["r30"]).read_bytes()),
      "r31_findings":ledger,"r31_findings_open":8,
      "r31_critical_open":2,
      "known_early_stop_bypass":"STOP_ATTEMPT_MOVED_BEFORE_BUSY_RETURN_SOURCE_ONLY",
      "stop_failure_physical_cutoff":"NOT_PROVEN",
      "r31_emitting_linkage":False,"r31_runtime_activation":False,
      "r31_original_C_edits":0,"r31_r29_candidate_edits":0,
      "r30_findings_open":12,"r30_critical_open":2,
      "r29_findings_open":7,"r28_gates_open":5,"r27_findings_open":9,
      "r23_obligations_open":15,"r24_findings_open":7,
      "bureau_gates_open":11,"bureau_gates_resolved":0,
      "C11_race_freedom":"NOT_PROVEN",
      "CoreAudio_callback_quiescence":"NOT_PROVEN",
      "physical_stop":"NOT_PROVEN",
      "failed_AudioQueueStop":"NOT_TESTED",
      "failed_AudioQueueDispose":"NOT_TESTED",
      "independent_signatures":"NONE","bureau_certification":"PENDING",
      "limitations":list(LIMITATIONS),
      "physical_emission":"NONE","scientific_simulation":"NONE",
      "acoustic_output":"LOCKED","em_output":"LOCKED",
      "real_output":"NOT_AUTHORIZED",
      "biological_exposure":"NOT_AUTHORIZED",
      "production":"NOT_AUTHORIZED",
    }
def markdown(report):
    rows=["| "+f["id"]+" | "+f["severity"]+" | "+f["bureau_role"]+
          " | OPEN_NOT_PROVEN |" for f in report["r31_findings"]]
    return (
      "# FREQMED GEN-R31 — Independent Critical Shutdown Remediation Design\n\n"
      "**Verdict: SHUTDOWN_STOP_ATTEMPT_REORDERED_SOURCE_ONLY_OS_SAFETY_UNPROVEN.**\n\n"
      "The isolated R31 candidate attempts AudioQueueStop(queue,true) before "
      "any close-but-busy admission return. This eliminates a specific source "
      "bypass of the STOP CALL, not a proof of stop success, physical cutoff, "
      "callback quiescence, pointer ownership or data-race freedom.\n\n"
      "| Finding | Severity | Bureau | Status |\n|---|---|---|---|\n"+
      "\n".join(rows)+"\n\n"
      "All 8 R31 and all 12 R30 findings including two original CRITICAL "
      "remain OPEN. Stop failure can leave a live queue; no physical cutoff is "
      "proven. R29=7, R28=5, R27=9, R23=15, R24=7, Bureau=11 OPEN.\n\n"
      "No active CoreAudio, no scientific simulation, no physical output. "
      "NEVER_SIMULATION=ENFORCED; ZERO_COST_FOSS=ENFORCED; "
      "ACOUSTIC_OUTPUT=LOCKED; EM_OUTPUT=LOCKED; "
      "REAL_OUTPUT=NOT_AUTHORIZED; BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED; "
      "PRODUCTION=NOT_AUTHORIZED.\n"
    )
def main():
    p=argparse.ArgumentParser(description="GEN-R31 isolated critical shutdown C review")
    p.add_argument("--root",type=Path,required=True)
    p.add_argument("--archive-r19",type=Path,required=True)
    for n in range(16,31):
        p.add_argument("--r"+str(n),type=Path,required=True)
    p.add_argument("--json",type=Path,required=True)
    p.add_argument("--markdown",type=Path,required=True)
    a=p.parse_args()
    try:
        paths={"r"+str(n):getattr(a,"r"+str(n)) for n in range(16,31)}
        result=audit(a.root,a.archive_r19,paths)
        a.json.write_text(json.dumps(result,sort_keys=True,
                          ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        a.markdown.write_text(markdown(result),encoding="utf-8")
    except (R31Error,r30.R30Error,r29.R29Error,r28.R28Error,r27.R27Error,
            r26.R26Error,ValueError,TypeError,KeyError,IndexError,
            OSError,UnicodeError) as exc:
        print("R31_CRITICAL_SHUTDOWN_REVIEW=FAIL_CLOSED",str(exc))
        return 2
    print("R31_CRITICAL_SHUTDOWN_REVIEW=PASS")
    print("R31_SOURCE_STOP_ORDER=STOP_ATTEMPT_BEFORE_BUSY_EXIT")
    print("R31_OPEN_FINDINGS=8; R31_CRITICAL=2; R31_PROVEN_RACES=0")
    print("R31_R30_FINDINGS=12_OPEN; R31_R30_CRITICAL=2_OPEN")
    print("R31_R29_FINDINGS=7_OPEN; R31_R28_GATES=5_OPEN; R31_R27_FINDINGS=9_OPEN")
    print("R31_R23_OBLIGATIONS=15_OPEN; R31_R24_FINDINGS=7_OPEN")
    print("R31_BUREAU_GATES=11_OPEN; R31_BUREAU_RESOLVED=0")
    print("R31_REVIEW_VERDICT="+VERDICT)
    print("R31_FAILED_OS_STOP=NOT_TESTED; R31_PHYSICAL_STOP=NOT_PROVEN")
    print("R31_CALLBACK_QUIESCENCE=NOT_PROVEN; R31_C11_RACE_FREEDOM=NOT_PROVEN")
    print("R31_PHYSICAL_EMISSION=NONE; R31_SCIENTIFIC_SIMULATION=NONE")
    return 0
if __name__=="__main__":
    raise SystemExit(main())
