#!/usr/bin/env python3
"""GEN-R36 isolated C11 stable-userdata anchor architecture/proof-gate review.
No CoreAudio calls, synthetic interleavings, hardware output or simulation.
Lexical evidence and standalone compilation are NOT OS/C11 race proofs.
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
import r33_failure_state_ownership_contract as r33
import r34_userdata_lifetime_review as r34
import r35_pre_admission_os_contract_review as r35

SCHEMA="FREQMED_GEN_R36_STATIC_ANCHOR_PRE_ADMISSION_PROOF_GATES"
VERDICT="STATIC_LIFETIME_ANCHOR_CANDIDATE_REVIEWABLE_NOT_INTEGRATED_NOT_CERTIFIED"
CANDIDATE="candidates/r36_stable_userdata_anchor.c"
R31=r31.CANDIDATE
FINDINGS=(
 ("SA36_01_REAL_OS_USERDATA_NOT_ANCHOR","CRITICAL","B07",
  "R31 still passes ctx directly to NewOutput and listener. The stable anchor is NOT integrated."),
 ("SA36_02_REAL_CALLBACKS_NOT_USING_ANCHOR","CRITICAL","B07",
  "Existing callbacks still read ctx->gate before lifetime protection; neither callback calls fm36_try_enter."),
 ("SA36_03_FAILURE_OS_QUIESCENCE_UNKNOWN","CRITICAL","B07",
  "No callback lifetime certificate on failed Stop/Dispose/RemoveListener or partial NewOutput creation."),
 ("SA36_04_PHYSICAL_STOP_UNPROVEN","CRITICAL","B10",
  "Never equate process-lifetime retention or seal with independent hardware cutoff."),
 ("SA36_05_OWNER_PROCESS_LIFETIME_ENFORCEMENT","HIGH","B09",
  "R36 presumes caller keeps ctx alive until process exit; this is a contract, not mechanically enforced ownership."),
 ("SA36_06_SINGLETON_CAPACITY_EXHAUSTION","HIGH","B09",
  "One static slot per process cannot be recycled; define fail-closed exhaustion and deny concurrent sessions."),
 ("SA36_07_NO_OWNER_FREE_OR_CLEAR","HIGH","B09",
  "Ensure the candidate never frees/clears the owner or resets phase, even on construction failure."),
 ("SA36_08_SEAL_ADMITTED_RACE","HIGH","B09",
  "An already admitted callback may proceed as seal occurs; requires separate HB and callback-pairing proof."),
 ("SA36_09_UNBALANCED_LEAVE_OWNER","HIGH","B09",
  "A global counter cannot prove per-callback balanced exit if a caller wrongly invokes leave."),
 ("SA36_10_OS_ABI_ADAPTER_BOUNDARY","HIGH","B07",
  "Actual callback ABI and OS listener arguments are not wired to static anchor; require independent integration review."),
 ("SA36_11_NM_UNLINKED_ENFORCEMENT","HIGH","B07",
  "C object must remain COMPILED_UNLINKED and source/linker allowlist must prevent all emitting symbols."),
 ("SA36_12_NO_MEM_MEASUREMENT_CERTIFICATION","HIGH","B10",
  "Static memory architecture is not a hardware measurement, medical certification, or permission to emit."),
)
ANCHORS=(
 ("SA36_01_REAL_OS_USERDATA_NOT_ANCHOR",("r31","AudioQueueNewOutput(&fmt,output_callback,ctx"),
  ("r31","queue_running_listener,ctx)")),
 ("SA36_02_REAL_CALLBACKS_NOT_USING_ANCHOR",("r31","fm_r28_gate_try_enter(&ctx->queue_admission)"),
  ("r36","int fm36_try_enter(void *userdata, void **owner_out)")),
 ("SA36_03_FAILURE_OS_QUIESCENCE_UNKNOWN",("r31","if (r31_immediate_stop_status!=noErr) {"),
  ("r31","if (AudioQueueDispose(ctx->queue,true)!=noErr) {")),
 ("SA36_04_PHYSICAL_STOP_UNPROVEN",("r36","* - Atomic publication/close does NOT prove OS/hardware stop"),
  ("r31","/* CRITICAL: OS stop failed.")),
 ("SA36_05_OWNER_PROCESS_LIFETIME_ENFORCEMENT",("r36","* after this claim, even if preparing/publishing/OS creation fails."),
  ("r36","atomic_store_explicit(&fm36_anchor.owner,owner,memory_order_relaxed);")),
 ("SA36_06_SINGLETON_CAPACITY_EXHAUSTION",("r36","static atomic_flag fm36_one_shot_claim=ATOMIC_FLAG_INIT;"),
  ("r36","atomic_flag_test_and_set_explicit(")),
 ("SA36_07_NO_OWNER_FREE_OR_CLEAR",("r36","static FM36StableAnchor fm36_anchor = {"),
  ("r36","* - No function here frees it, clears owner or re-opens after seal.")),
 ("SA36_08_SEAL_ADMITTED_RACE",("r36","(void)atomic_fetch_add_explicit(&fm36_anchor.admitted,1u,"),
  ("r36","int fm36_seal(void *userdata)")),
 ("SA36_09_UNBALANCED_LEAVE_OWNER",("r36","int fm36_leave(void *userdata)"),
  ("r36","atomic_compare_exchange_weak_explicit(")),
 ("SA36_10_OS_ABI_ADAPTER_BOUNDARY",("r31","static void output_callback(void *ptr,"),
  ("r36","/* The token equality comparison does not dereference untrusted userdata.")),
 ("SA36_11_NM_UNLINKED_ENFORCEMENT",("r36","#include <stdatomic.h>"),
  ("r36","int fm36_prepare_once(void *owner, void **userdata_out)")),
 ("SA36_12_NO_MEM_MEASUREMENT_CERTIFICATION",("r36","* - C11 admission counters do NOT certify OS callback quiescence."),
  ("r36","*   safety of unrelated real application code.")),
)
REQUIRED_FUNCTIONS=(
 "fm36_prepare_once","fm36_mark_exposed","fm36_try_enter",
 "fm36_leave","fm36_seal",
)
LIMITATIONS=(
 "CANDIDATE_R36_IS_NOT_INTEGRATED_WITH_REAL_COREAUDIO_CALLBACKS",
 "STATIC_C11_SOURCE_NOT_A_FORMAL_HAPPENS_BEFORE_PROOF",
 "NO_OSSTATUS_FAILURE_PATH_EXECUTED",
 "NO_ACTIVE_OS_CALLBACK_OR_COREAUDIO_AUDIOQUEUE",
 "NO_SIMULATION_OR_SYNTHETIC_INTERLEAVINGS",
 "NO_HARDWARE_PHYSICAL_CUTOFF_MEASUREMENT",
 "NO_INDEPENDENT_BUREAU_SIGNED_CERTIFICATION",
)
class R36Error(ValueError): pass
def require(ok,msg):
    if not ok: raise R36Error(msg)
def sha(data): return hashlib.sha256(data).hexdigest()

def function_bounds(text,name):
    import re
    found=list(re.finditer(r"^int\s+"+re.escape(name)+r"\s*\([^;]*\)\s*\{",
                           text,re.M|re.S))
    require(len(found)==1,"R36 exact function definition missing/duplicated "+name)
    a=found[0].start()
    brace=text.index("{",found[0].start())
    depth=0
    for i in range(brace,len(text)):
        if text[i]=="{": depth+=1
        elif text[i]=="}":
            depth-=1
            if depth==0: return a,i+1,text[a:i+1]
    raise R36Error("R36 unterminated C function "+name)

def observe(candidate,original):
    require(candidate.startswith("/* SPDX-License-Identifier: Apache-2.0 */"),
            "R36 candidate license/header drift")
    require("/* SPDX-License-Identifier: Apache-2.0 */" in original,
            "R36 baseline license drift")
    for phrase in (
        "#include <stdatomic.h>",
        "static FM36StableAnchor fm36_anchor = {",
        "static atomic_flag fm36_one_shot_claim=ATOMIC_FLAG_INIT;",
        "_Atomic(void *) owner;",
        "atomic_uint phase;","atomic_uint admitted;",
        "FM36_PREPARED=1u","FM36_EXPOSED=2u","FM36_SEALED=3u",
    ):
        require(phrase in candidate,"R36 source anchor absent: "+phrase)
    for banned in (
        "#include <AudioToolbox", "#include <CoreAudio",
        "AudioQueueStart(", "AudioQueueStop(", "AudioQueueDispose(",
        "AudioQueueNewOutput(", "AudioQueueEnqueueBuffer(", "AudioDeviceStart(",
        "free(", "malloc(", "calloc(", "realloc(", "pthread_create(",
        "asm(", "dlopen(", "dlsym(", "abort(",
    ):
        require(banned not in candidate,"R36 hardware/freed/unsafe action in candidate: "+banned)
    require(candidate.count("static FM36StableAnchor fm36_anchor = {")==1,
            "R36 process anchor not unique")
    require(candidate.count("static atomic_flag fm36_one_shot_claim")==1,
            "R36 one-shot guard not unique")
    parts={}
    for f in REQUIRED_FUNCTIONS:
        _,_,body=function_bounds(candidate,f)
        parts[f]=body
    require(len(parts)==5,"R36 function cardinality drift")
    prepare=parts["fm36_prepare_once"]
    require("atomic_flag_test_and_set_explicit(" in prepare
            and "atomic_store_explicit(&fm36_anchor.owner,owner,memory_order_relaxed);" in prepare
            and "atomic_store_explicit(&fm36_anchor.phase,FM36_PREPARED,memory_order_release);" in prepare
            and "*userdata_out=(void *)&fm36_anchor;" in prepare,
            "R36 prepare does not publish immortal anchor safely")
    expose=parts["fm36_mark_exposed"]
    require("unsigned expected=FM36_PREPARED;" in expose
            and "&fm36_anchor.phase,&expected,FM36_EXPOSED" in expose,
            "R36 expose transition changed")
    enter=parts["fm36_try_enter"]
    require(enter.count("userdata!=(void *)&fm36_anchor")==1
            and enter.index("userdata!=(void *)&fm36_anchor") <
            enter.index("*owner_out=NULL;") <
            enter.index("atomic_fetch_add_explicit(&fm36_anchor.admitted") <
            enter.index("void *owner=atomic_load_explicit(&fm36_anchor.owner,") <
            enter.index("*owner_out=owner;"),
            "R36 userdata must be checked and reserved before owner dereference")
    require(enter.count("!=FM36_EXPOSED")==2
            and enter.count("atomic_fetch_sub_explicit(&fm36_anchor.admitted")==2,
            "R36 two-stage phase review or rollback drift")
    leave=parts["fm36_leave"]
    require("while (seen>0u)" in leave
            and "atomic_compare_exchange_weak_explicit(" in leave
            and "&fm36_anchor.admitted,&seen,seen-1u" in leave,
            "R36 leave underflow protection changed")
    seal=parts["fm36_seal"]
    require("while (seen==FM36_PREPARED || seen==FM36_EXPOSED)" in seal
            and "&fm36_anchor.phase,&seen,FM36_SEALED" in seal,
            "R36 seal not monotone one-way")
    require(candidate.count("fm36_anchor.owner") == 2,
            "R36 owner alias accesses broadened")
    require("AudioQueueNewOutput(&fmt,output_callback,ctx" in original
            and "queue_running_listener,ctx)" in original
            and "fm36_try_enter" not in original,
            "R36 candidate incorrectly marked as integrated into R31")
    require(len(FINDINGS)==12 and len(ANCHORS)==12
            and [x[0] for x in FINDINGS]==[x[0] for x in ANCHORS]
            and sum(x[1]=="CRITICAL" for x in FINDINGS)==4,
            "R36 proof register cardinality/severity drift")
    for fid,a,b in ANCHORS:
        for scope,needle in (a,b):
            require(needle in (candidate if scope=="r36" else original),
                    "R36 missing anchored evidence "+fid+": "+needle)
    return {f[0]:"OPEN_NOT_PROVEN" for f in FINDINGS}

def inspect(root,override=None):
    root=Path(root).resolve()
    table,manifest=r17.manifest_integrity(root)
    require(len(table)==200,"R36 exactly 200 pinned source files")
    needed=(
      "candidates/r36_stable_userdata_anchor.c",
      "audits/r36_static_anchor_proof_gate.py",
      "tests/test_r36_static_anchor_proof_gate.py",
      "RUN_GEN_R36_MAC_INTEL.command",
      "docs/GEN_R36_STABLE_ANCHOR_ARCHITECTURE.md",
      "docs/GEN_R36_BUREAU_PROOF_GATES.md",
      "docs/GEN_R36_ADVERSARIAL_INTEGRATION_MATRIX.md",
    )
    require(all(x in table for x in needed),"R36 missing pinned candidate/review file")
    historical=r35.inspect(root)
    require(historical[2]==table[R31],"R36 R31 original C source changed")
    require(table[r26.ORIGINAL]==r19.PINNED_ACOUSTIC_SHA256,
            "R36 original production C backend changed")
    raw=(root/CANDIDATE).read_bytes()
    old=(root/R31).read_bytes()
    require(sha(raw)==table[CANDIDATE] and sha(old)==table[R31],
            "R36 candidate/baseline SHA integrity drift")
    checks=observe(raw.decode("utf-8") if override is None else override,
                   old.decode("utf-8"))
    runner=(root/"RUN_GEN_R36_MAC_INTEL.command").read_text(encoding="utf-8")
    require(set(r17.link_sources(runner))==r17.LINK_C_ALLOWLIST,
            "R36 executable source allowlist changed")
    piece=runner.split(' -o "$WORK/freqmed-gen"')
    require(len(piece)==2,"R36 executable link command missing")
    section=piece[1].split("-framework CoreAudio",1)[0]
    require("output_hard_denied.c" in section,
            "R36 mandatory hard denial not linked")
    for forbidden in (
      "r36_stable_userdata_anchor.c","acoustic_macos_r31.c",
      "acoustic_macos_r29.c","acoustic_macos_r26.c",
      "r28_callback_admission_gate.c","src/acoustic_macos.c",
    ):
        require(forbidden not in section,"R36 forbidden emitter/anchor linked: "+forbidden)
    for phrase in (
       "R36_STATIC_ANCHOR_REVIEW=PASS",
       "R36_STABLE_ANCHOR_OBJECT=COMPILED_UNLINKED",
       "R36_R31_CANDIDATE_OBJECT=COMPILED_UNLINKED",
       "R36_NONEMITTING_EXECUTABLE_SYMBOL_AUDIT=PASS",
       "R36_BUREAU_PROOF_DOSSIER=34_FILES_SHA256_PASS",
       "R36_TESTCASE_RUN_SLOT=PASS",
       "FREQMED_GEN_R36_EVIDENCE_DIR","FREQMED_GEN_R36_BINARY",
    ):
        require(phrase in runner,"R36 runner guard absent: "+phrase)
    return table,manifest,sha(raw),checks

def anchor(root,text,scope,needle,src_sha):
    require(needle in text,"R36 source anchor missing: "+needle)
    return {"path":CANDIDATE if scope=="r36" else R31,
            "line":text.count("\n",0,text.index(needle))+1,
            "sha256":src_sha,"needle":needle}

def audit(root,archive_r19,reports):
    table,manifest,csha,checks=inspect(root)
    old=r35.audit(root,archive_r19,reports)
    reported=json.loads(Path(reports["r35"]).read_text(encoding="utf-8"))
    require(old==reported,"R36 historical R35 report fails recomputation")
    require(old["r35_findings_open"]==12 and old["r35_critical_open"]==4
            and old["r34_findings_open"]==14 and old["r34_critical_open"]==4
            and old["r33_findings_open"]==12
            and old["r32_findings_open"]==10
            and old["r31_findings_open"]==8
            and old["r30_findings_open"]==12
            and old["r29_findings_open"]==7
            and old["r28_gates_open"]==5
            and old["r27_findings_open"]==9
            and old["r23_obligations_open"]==15
            and old["r24_findings_open"]==7
            and old["bureau_gates_open"]==11
            and old["bureau_gates_resolved"]==0,
            "R36 older proof obligations inappropriately discharged")
    root=Path(root)
    new=(root/CANDIDATE).read_text(encoding="utf-8")
    base=(root/R31).read_text(encoding="utf-8")
    ledger=[]
    for (fid,severity,role,needed),(key,a,b) in zip(FINDINGS,ANCHORS):
        require(fid==key,"R36 finding anchors misaligned")
        ledger.append({"id":fid,"severity":severity,"bureau_role":role,
          "status":checks[fid],"proof_missing":needed,"os_runtime_witness":False,
          "race_reproduced":False,"independent_signature":"NONE",
          "source_anchors":[anchor(root,new if a[0]=="r36" else base,
                             a[0],a[1],csha if a[0]=="r36" else table[R31]),
                            anchor(root,new if b[0]=="r36" else base,
                             b[0],b[1],csha if b[0]=="r36" else table[R31])]})
    return {
      "schema":SCHEMA,"verdict":VERDICT,
      "method":"ISOLATED_C11_ANCHOR_STATIC_SOURCE_ARCHITECTURE_REVIEW",
      "manifest_sha256":manifest,"pinned_generator_files":len(table),
      "candidate_r36_sha256":csha,"baseline_r31_sha256":table[R31],
      "original_C_sha256":table[r26.ORIGINAL],
      "r35_report_sha256":sha(Path(reports["r35"]).read_bytes()),
      "r36_findings":ledger,"r36_findings_open":12,"r36_critical_open":4,
      "r36_process_lifetime_singleton":True,
      "r36_one_shot_no_reuse":True,
      "r36_candidate_integrated":False,
      "r36_C_baseline_edits":0,"r36_emitter_linked":False,
      "r36_real_OS_callbacks":0,"r36_source_only_candidate":True,
      "r35_findings_open":12,"r35_critical_open":4,
      "r34_findings_open":14,"r34_critical_open":4,
      "r33_findings_open":12,"r33_critical_open":3,
      "r32_findings_open":10,"r32_critical_open":2,
      "r31_findings_open":8,"r31_critical_open":2,
      "r30_findings_open":12,"r30_critical_open":2,
      "r29_findings_open":7,"r28_gates_open":5,"r27_findings_open":9,
      "r23_obligations_open":15,"r24_findings_open":7,
      "bureau_gates_open":11,"bureau_gates_resolved":0,
      "userdata_pre_admission_lifetime_in_production":"NOT_PROVEN",
      "CoreAudio_callback_quiescence":"NOT_PROVEN",
      "C11_race_freedom":"NOT_PROVEN",
      "failed_OS_stop":"NOT_TESTED",
      "failed_OS_dispose":"NOT_TESTED",
      "physical_cutoff":"NOT_PROVEN",
      "bureau_certification":"PENDING",
      "limitations":list(LIMITATIONS),
      "scientific_simulation":"NONE","physical_emission":"NONE",
      "acoustic_output":"LOCKED","em_output":"LOCKED",
      "real_output":"NOT_AUTHORIZED",
      "biological_exposure":"NOT_AUTHORIZED",
      "production":"NOT_AUTHORIZED",
    }

def markdown(info):
    rows=["| "+x["id"]+" | "+x["severity"]+" | OPEN_NOT_PROVEN |"
         for x in info["r36_findings"]]
    return ("# FREQMED GEN-R36 — Static Process-Lifetime Userdata Anchor\n\n"
      "**Verdict: STATIC_LIFETIME_ANCHOR_CANDIDATE_REVIEWABLE_NOT_INTEGRATED_NOT_CERTIFIED.**\n\n"
      "The C11 candidate creates a one-shot, static process-lifetime anchor "
      "and retains owner forever, but no CoreAudio callback uses this anchor. "
      "OS failed-stop/failed-dispose and physical cutoff remain NOT_PROVEN.\n\n"
      "| Finding | Severity | Status |\n|---|---|---|\n"
      +"\n".join(rows)+"\n\n"
      "R36 12 OPEN (4 CRITICAL), R35 12 OPEN (4 CRITICAL), R34 14, "
      "R33 12, R32 10, R31 8, R30 12, R29 7, R28 5, R27 9, "
      "R23 15, R24 7, Bureau 11 OPEN/0 resolved. "
      "No real OS callback, no scientific simulation and no emission.\n\n"
      "NEVER_SIMULATION=ENFORCED; ZERO_COST_FOSS=ENFORCED; "
      "ACOUSTIC_OUTPUT=LOCKED; EM_OUTPUT=LOCKED; REAL_OUTPUT=NOT_AUTHORIZED; "
      "BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED; PRODUCTION=NOT_AUTHORIZED.\n")

def main():
    p=argparse.ArgumentParser(description="R36 nonemitting static anchor proof gate")
    p.add_argument("--root",required=True,type=Path)
    p.add_argument("--archive-r19",required=True,type=Path)
    for n in range(16,36): p.add_argument("--r"+str(n),required=True,type=Path)
    p.add_argument("--json",required=True,type=Path)
    p.add_argument("--markdown",required=True,type=Path)
    args=p.parse_args()
    try:
        reports={"r"+str(n):getattr(args,"r"+str(n)) for n in range(16,36)}
        obj=audit(args.root,args.archive_r19,reports)
        args.json.write_text(json.dumps(obj,sort_keys=True,indent=2,
                             ensure_ascii=False)+"\n",encoding="utf-8")
        args.markdown.write_text(markdown(obj),encoding="utf-8")
    except (R36Error,r35.R35Error,r34.R34Error,r33.R33Error,r32.R32Error,
            r31.R31Error,r30.R30Error,r29.R29Error,r28.R28Error,
            r27.R27Error,r26.R26Error,ValueError,TypeError,KeyError,
            IndexError,OSError,UnicodeError) as exc:
        print("R36_STATIC_ANCHOR_REVIEW=FAIL_CLOSED",str(exc))
        return 2
    print("R36_STATIC_ANCHOR_REVIEW=PASS")
    print("R36_FINDINGS=12_OPEN; R36_CRITICAL=4_OPEN")
    print("R36_STABLE_ANCHOR=STATIC_ONE_SHOT_NOT_INTEGRATED")
    print("R36_R35_FINDINGS=12_OPEN; R36_R34_FINDINGS=14_OPEN")
    print("R36_R33_FINDINGS=12_OPEN; R36_R32_FINDINGS=10_OPEN")
    print("R36_BUREAU_GATES=11_OPEN; R36_BUREAU_RESOLVED=0")
    print("R36_REVIEW_VERDICT="+VERDICT)
    print("R36_PRE_ADMISSION_LIFETIME_IN_PRODUCTION=NOT_PROVEN")
    print("R36_COREAUDIO_CALLBACK_QUIESCENCE=NOT_PROVEN")
    print("R36_C11_RACE_FREEDOM=NOT_PROVEN")
    print("R36_PHYSICAL_CUTOFF=NOT_PROVEN; R36_ACTUAL_OS_CALLBACKS=0")
    print("R36_PHYSICAL_EMISSION=NONE; R36_SCIENTIFIC_SIMULATION=NONE")
    return 0
if __name__=="__main__":
    raise SystemExit(main())
