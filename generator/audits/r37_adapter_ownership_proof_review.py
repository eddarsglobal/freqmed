#!/usr/bin/env python3
"""GEN-R37 isolated static-anchor C11 lease adapter and ownership proof gates.
Static source-only review of two UNLINKED candidate translation units.
No native callbacks, CoreAudio calls, measurements or scientific simulation.
"""
import argparse
import hashlib
import json
import re
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
import r36_static_anchor_proof_gate as r36

SCHEMA="FREQMED_GEN_R37_ISOLATED_CALLBACK_LEASE_INTEGRATION_FEASIBILITY"
VERDICT="ISOLATED_C11_LEASE_ADAPTER_REVIEWED_OS_INTEGRATION_NOT_PROVEN"
CANDIDATE="candidates/r37_callback_lease_adapter.c"
R36=r36.CANDIDATE
R31=r31.CANDIDATE

FINDINGS=(
 ("LA37_01_R31_STILL_PASSES_HEAP_USERDATA","CRITICAL","B07",
  "The real R31 output and listener callback APIs still receive ctx directly; the adapter is NOT integrated."),
 ("LA37_02_R31_CALLBACKS_STILL_PRE_GATE_DEREF","CRITICAL","B07",
  "Both R31 callback functions still dereference ctx->queue_admission before a lifetime gate."),
 ("LA37_03_OS_ERROR_CALLBACK_COMPLETION_UNKNOWN","CRITICAL","B07",
  "No actual OS failure/late-entry witness for stop, dispose, listener removal or creation."),
 ("LA37_04_HARDWARE_CUTOFF_UNPROVEN","CRITICAL","B10",
  "No real physical output cutoff or instrumental verification; retain hard denial."),
 ("LA37_05_OWNER_NOT_EXTERNALLY_PINNED","HIGH","B09",
  "Owner lifetime must be guaranteed by external aliases through process termination."),
 ("LA37_06_LEASE_STACK_INITIALIZATION_PRECONDITION","HIGH","B09",
  "Each FM37Lease must be a newly zero-initialized, callback-local object; this is not enforced across callers."),
 ("LA37_07_LEASE_NOT_THREAD_SHAREABLE","HIGH","B09",
  "FM37Lease phase is non-atomic; concurrent sharing would be undefined."),
 ("LA37_08_LEAVE_AFTER_EVERY_SUCCESS_NOT_PROVEN","HIGH","B09",
  "The adapter does not prove full callback control flow or guaranteed finish on all exceptional exits."),
 ("LA37_09_DOUBLE_EXIT_ONLY_LOCALLY_BLOCKED","HIGH","B09",
  "The adapter rejects sequential double-finish on a local lease; no global per-callback identity or concurrency proof."),
 ("LA37_10_PREPARE_FAILURE_LEAK_AND_ONE_SHOT","HIGH","B09",
  "After a one-shot prepare claim, failures must keep owner alive and reject further sessions."),
 ("LA37_11_C11_HAPPENS_BEFORE_CTX_FIELDS","HIGH","B09",
  "Atomic anchor publication does not validate other non-atomic context field accesses, PCM, or queue pointer."),
 ("LA37_12_OS_CALLBACK_ABI_NOT_WIRED","HIGH","B07",
  "Adapter signatures are NOT AudioQueue callback types; future OS ABI wrappers need separate review."),
 ("LA37_13_STOP_DISPOSE_SEAL_NOT_QUIESCENCE","HIGH","B07",
  "Seal prevents future admissions but cannot certify OS callback quiescence or disposal success."),
 ("LA37_14_OBJECT_LINK_DENY_AND_TEST_PROVENANCE","HIGH","B10",
  "C36/C37 must remain unlinked and audit evidence SHA-pinned, with all historical Bureau vetoes intact."),
)
ANCHORS=(
 ("LA37_01_R31_STILL_PASSES_HEAP_USERDATA",
  ("r31","AudioQueueNewOutput(&fmt,output_callback,ctx"),
  ("r31","queue_running_listener,ctx)")),
 ("LA37_02_R31_CALLBACKS_STILL_PRE_GATE_DEREF",
  ("r31","fm_r28_gate_try_enter(&ctx->queue_admission)"),
  ("r37","int fm37_output_enter(void *os_userdata, FM37Lease *lease)")),
 ("LA37_03_OS_ERROR_CALLBACK_COMPLETION_UNKNOWN",
  ("r31","if (r31_immediate_stop_status!=noErr) {"),
  ("r31","if (AudioQueueDispose(ctx->queue,true)!=noErr) {")),
 ("LA37_04_HARDWARE_CUTOFF_UNPROVEN",
  ("r31","/* CRITICAL: OS stop failed."),
  ("r37","* 6. Closing admissions is NOT OS callback quiescence or physical cutoff.")),
 ("LA37_05_OWNER_NOT_EXTERNALLY_PINNED",
  ("r36","* after this claim, even if preparing/publishing/OS creation fails."),
  ("r37","* 2. After fm36_prepare_once claims owner, NO external alias releases owner.")),
 ("LA37_06_LEASE_STACK_INITIALIZATION_PRECONDITION",
  ("r37","FM37Lease lease={0};"),
  ("r37","if (!lease || lease->phase!=FM37_LEASE_UNUSED) return -1;")),
 ("LA37_07_LEASE_NOT_THREAD_SHAREABLE",
  ("r37","FM37LeasePhase phase;"),
  ("r37","* 1. One initialized FM37Lease on each callback's own stack, NEVER shared.")),
 ("LA37_08_LEAVE_AFTER_EVERY_SUCCESS_NOT_PROVEN",
  ("r37","int fm37_finish(FM37Lease *lease)"),
  ("r37","return fm36_leave(token);")),
 ("LA37_09_DOUBLE_EXIT_ONLY_LOCALLY_BLOCKED",
  ("r37","lease->phase=FM37_LEASE_FINISHED;"),
  ("r37","if (!lease || lease->phase!=FM37_LEASE_ACTIVE) return -1;")),
 ("LA37_10_PREPARE_FAILURE_LEAK_AND_ONE_SHOT",
  ("r37","if (fm36_prepare_once(owner,os_userdata_out)!=0) return -1;"),
  ("r37","if (fm36_mark_exposed(*os_userdata_out)!=0) return -1;")),
 ("LA37_11_C11_HAPPENS_BEFORE_CTX_FIELDS",
  ("r36","_Atomic(void *) owner;"),
  ("r37","* This file proves no C11 happens-before relation for external ctx fields,")),
 ("LA37_12_OS_CALLBACK_ABI_NOT_WIRED",
  ("r37","* Signatures are NOT an AudioQueue ABI and MUST NOT be installed with OS."),
  ("r37","int fm37_property_enter(void *os_userdata, FM37Lease *lease)")),
 ("LA37_13_STOP_DISPOSE_SEAL_NOT_QUIESCENCE",
  ("r37","int fm37_seal_token(void *os_userdata)"),
  ("r36","int fm36_seal(void *userdata)")),
 ("LA37_14_OBJECT_LINK_DENY_AND_TEST_PROVENANCE",
  ("r37","* NEVER link, load, dispatch, activate, or call as real CoreAudio code."),
  ("r36","* - The entire object is NEVER linked or loaded into the production binary.")),
)
CONTRACTS=(
 ("C37_PREPARE","STATIC_TOKEN_ONLY","ONE_SHOT_NO_REUSE","OWNER_LIFETIME_EXTERNAL"),
 ("C37_OUTPUT_ENTRY","R36_GATE_BEFORE_OWNER","LOCAL_LEASE_REQUIRED","NO_REAL_OS_CALLBACK"),
 ("C37_LISTENER_ENTRY","R36_GATE_BEFORE_OWNER","LOCAL_LEASE_REQUIRED","NO_REAL_OS_LISTENER"),
 ("C37_OWNER_ACCESS","ONLY_ACTIVE_LEASE","NONATOMIC_OWNER_FIELDS_EXTERNAL","NO_C11_GLOBAL_PROOF"),
 ("C37_FINISH","ONCE_LOCAL_PHASE","EXTERNAL_ALL_PATH_PAIRING","NO_OS_QUIESCENCE"),
 ("C37_SEAL","R36_IRREVERSIBLE","OWNER_RETAINED","NO_PHYSICAL_STOP"),
)
LIMITATIONS=(
 "NO_REAL_AUDIOQUEUE_CALLBACK_ABI_ADAPTER",
 "R31_STILL_PASSES_DIRECT_HEAP_CTX_USERDATA",
 "NO_ACTUAL_OS_FAILURES_OR_CALLBACK_ENTRIES",
 "NO_FORMAL_C11_HAPPENS_BEFORE_PROOF",
 "OWNER_ALIAS_LIFETIME_NOT_MECHANICALLY_ENFORCED",
 "NO_SCIENTIFIC_SIMULATION_OR_TEST_CALLBACK_DISPATCH",
 "NO_HARDWARE_CUTOFF_MEASUREMENT",
 "NO_INDEPENDENT_SIGNED_BUREAU_CERTIFICATION",
)
class R37Error(ValueError): pass

def require(ok,msg):
    if not ok: raise R37Error(msg)
def sha(data): return hashlib.sha256(data).hexdigest()

def function(source,name):
    match=list(re.finditer(r"^(?:static\s+)?(?:int|void\s*\*)\s*"+
       re.escape(name)+r"\s*\([^;]*\)\s*\{",source,re.M|re.S))
    require(len(match)==1,"R37 function missing/duplicate: "+name)
    i=source.index("{",match[0].start())
    level=0
    for j in range(i,len(source)):
        if source[j]=="{": level+=1
        if source[j]=="}":
            level-=1
            if level==0: return source[match[0].start():j+1]
    raise R37Error("R37 unterminated function "+name)

def ordered(body,labels):
    require(all(s in body for s in labels),"R37 missing ordered entry/exit source anchor")
    indices=[body.index(s) for s in labels]
    require(indices==sorted(indices) and len(set(indices))==len(indices),
            "R37 safety-relevant source order changed")

def observe(adapter,r36src,r31src):
    require(adapter.startswith("/* SPDX-License-Identifier: Apache-2.0 */"),
            "R37 source SPDX header changed")
    require(r36src.startswith("/* SPDX-License-Identifier: Apache-2.0 */"),
            "R37 R36 source provenance drift")
    r36.observe(r36src,r31src)
    for forbidden in ("#include <AudioToolbox","#include <CoreAudio",
                      "AudioQueueStart(","AudioQueueStop(","AudioQueueDispose(",
                      "AudioQueueNewOutput(","AudioQueueEnqueueBuffer(",
                      "AudioDeviceStart(","malloc(","calloc(","realloc(",
                      "free(","pthread_create(","dlsym(","dlopen("):
        require(forbidden not in adapter,
                "R37 unlinked adapter invokes forbidden OS/allocator: "+forbidden)
    for symbol in ("fm36_prepare_once","fm36_mark_exposed",
                   "fm36_try_enter","fm36_leave","fm36_seal"):
        require("extern int "+symbol+"(" in adapter,
                "R37 missing R36 cross-unit ABI declaration: "+symbol)
    for symbol in ("fm37_prepare_token","fm37_begin","fm37_output_enter",
                   "fm37_property_enter","fm37_lease_owner",
                   "fm37_finish","fm37_seal_token"):
        function(adapter,symbol)
    require(adapter.count("FM37LeasePhase phase;")==1 and
            adapter.count("FM37_LEASE_ACTIVE=1u")==1 and
            adapter.count("FM37_LEASE_FINISHED=2u")==1,
            "R37 local lease type changed")
    prep=function(adapter,"fm37_prepare_token")
    ordered(prep,("*os_userdata_out=NULL;",
                  "fm36_prepare_once(owner,os_userdata_out)",
                  "fm36_mark_exposed(*os_userdata_out)"))
    require("if (!owner || !os_userdata_out) return -1;" in prep,
            "R37 preparation null-pointer guard missing")
    enter=function(adapter,"fm37_begin")
    ordered(enter,("if (!lease || lease->phase!=FM37_LEASE_UNUSED) return -1;",
                   "void *owner=NULL;",
                   "fm36_try_enter(os_userdata,&owner)",
                   "lease->os_userdata=os_userdata;",
                   "lease->owner=owner;",
                   "lease->phase=FM37_LEASE_ACTIVE;"))
    require("if (!owner) {" in enter and
            "(void)fm36_leave(os_userdata);" in enter,
            "R37 denied/null owner path must not retain admission")
    output=function(adapter,"fm37_output_enter")
    listener=function(adapter,"fm37_property_enter")
    require("return fm37_begin(os_userdata,lease);" in output and
            "return fm37_begin(os_userdata,lease);" in listener,
            "R37 both entry wrappers must acquire R36 gate before owner")
    access=function(adapter,"fm37_lease_owner")
    ordered(access,("lease->phase!=FM37_LEASE_ACTIVE","return lease->owner;"))
    finish=function(adapter,"fm37_finish")
    ordered(finish,("if (!lease || lease->phase!=FM37_LEASE_ACTIVE) return -1;",
                    "void *token=lease->os_userdata;",
                    "lease->phase=FM37_LEASE_FINISHED;",
                    "lease->owner=NULL;",
                    "lease->os_userdata=NULL;",
                    "return fm36_leave(token);"))
    seal=function(adapter,"fm37_seal_token")
    require("return fm36_seal(os_userdata);" in seal,
            "R37 irreversible admission closure no longer delegated to R36")
    require("fm37_" not in r31src and
            "fm36_try_enter" not in r31src and
            "AudioQueueNewOutput(&fmt,output_callback,ctx" in r31src and
            "queue_running_listener,ctx)" in r31src,
            "R37 false real CoreAudio integration claim / R31 baseline drift")
    require(len(FINDINGS)==14 and len(ANCHORS)==14 and
            [f[0] for f in FINDINGS]==[a[0] for a in ANCHORS] and
            sum(f[1]=="CRITICAL" for f in FINDINGS)==4 and
            len(CONTRACTS)==6,
            "R37 finding/contract registry drift")
    sources={"r31":r31src,"r36":r36src,"r37":adapter}
    for fid,first,second in ANCHORS:
        for scope,needle in (first,second):
            require(needle in sources[scope],
                    "R37 finding source anchor absent "+fid+": "+needle)
    return {x[0]:"OPEN_NOT_PROVEN" for x in FINDINGS}

def inspect(root,override=None):
    root=Path(root).resolve()
    table,manifest=r17.manifest_integrity(root)
    require(len(table)>=207,"R37 historical audit requires at least 207 SHA-pinned files")
    necessary=(
        "candidates/r37_callback_lease_adapter.c",
        "audits/r37_adapter_ownership_proof_review.py",
        "tests/test_r37_adapter_ownership_proof_review.py",
        "RUN_GEN_R37_MAC_INTEL.command",
        "docs/GEN_R37_CALLBACK_LEASE_ARCHITECTURE.md",
        "docs/GEN_R37_BUREAU_PROOF_GATE.md",
        "docs/GEN_R37_ADVERSARIAL_CONTRACT_MATRIX.md",
    )
    require(all(n in table for n in necessary),"R37 source-only evidence not SHA pinned")
    previous=r36.inspect(root)
    require(previous[2]==table[R36],"R37 altered C36 original candidate")
    require(table[R31]==table[r31.CANDIDATE] and
            table[r26.ORIGINAL]==r19.PINNED_ACOUSTIC_SHA256,
            "R37 altered historic C31/original native backend")
    adapter=(root/CANDIDATE).read_bytes()
    r36c=(root/R36).read_bytes()
    r31c=(root/R31).read_bytes()
    require(sha(adapter)==table[CANDIDATE],"R37 C37 source SHA mismatch")
    checks=observe(adapter.decode("utf-8") if override is None else override,
                   r36c.decode("utf-8"),r31c.decode("utf-8"))
    runner=(root/"RUN_GEN_R37_MAC_INTEL.command").read_text(encoding="utf-8")
    require(set(r17.link_sources(runner))==r17.LINK_C_ALLOWLIST,
            "R37 no-output executable linker allowlist drift")
    sections=runner.split(' -o "$WORK/freqmed-gen"')
    require(len(sections)==2,"R37 required output-denying executable missing")
    linked=sections[1].split("-framework CoreAudio",1)[0]
    require("output_hard_denied.c" in linked,"R37 hard-denied emitter not linked")
    for bad in ("r37_callback_lease_adapter.c","r36_stable_userdata_anchor.c",
                "acoustic_macos_r31.c","r28_callback_admission_gate.c",
                "src/acoustic_macos.c"):
        require(bad not in linked,"R37 forbidden CoreAudio/adapter linked "+bad)
    for tag in ("R37_ADAPTER_OWNERSHIP_REVIEW=PASS",
                "R37_CALLBACK_LEASE_OBJECT=COMPILED_UNLINKED",
                "R37_STABLE_ANCHOR_OBJECT=COMPILED_UNLINKED",
                "R37_R31_CANDIDATE_OBJECT=COMPILED_UNLINKED",
                "R37_NONEMITTING_EXECUTABLE_SYMBOL_AUDIT=PASS",
                "R37_BUREAU_PROOF_DOSSIER=36_FILES_SHA256_PASS",
                "R37_TESTCASE_RUN_SLOT=PASS",
                "FREQMED_GEN_R37_EVIDENCE_DIR","FREQMED_GEN_R37_BINARY"):
        require(tag in runner,"R37 required runner marker absent "+tag)
    return table,manifest,sha(adapter),checks

def source_anchor(source,path,needle,digest):
    require(needle in source,"R37 source proof line missing: "+needle)
    return {"path":path,"line":source.count("\n",0,source.index(needle))+1,
            "sha256":digest,"needle":needle}

def audit(root,archive_r19,reports):
    table,manifest,adaptersha,findings=inspect(root)
    past=r36.audit(root,archive_r19,reports)
    prior=json.loads(Path(reports["r36"]).read_text(encoding="utf-8"))
    require(past==prior,"R37 R36 historic report differs from recomputation")
    require(past["r36_findings_open"]==12
            and past["r35_findings_open"]==12
            and past["r34_findings_open"]==14
            and past["r33_findings_open"]==12
            and past["r32_findings_open"]==10
            and past["r31_findings_open"]==8
            and past["r30_findings_open"]==12
            and past["r29_findings_open"]==7
            and past["r28_gates_open"]==5
            and past["r27_findings_open"]==9
            and past["r23_obligations_open"]==15
            and past["r24_findings_open"]==7
            and past["bureau_gates_open"]==11
            and past["bureau_gates_resolved"]==0,
            "R37 historic proof gates wrongly discharged")
    root=Path(root)
    txts={"r31":(root/R31).read_text(encoding="utf-8"),
          "r36":(root/R36).read_text(encoding="utf-8"),
          "r37":(root/CANDIDATE).read_text(encoding="utf-8")}
    paths={"r31":R31,"r36":R36,"r37":CANDIDATE}
    findings_out=[]
    for (fid,severity,seat,why),(token,a,b) in zip(FINDINGS,ANCHORS):
        require(fid==token,"R37 finding ledger pairing drift")
        findings_out.append({"id":fid,"severity":severity,"bureau_seat":seat,
            "status":findings[fid],"proof_needed":why,
            "real_coreaudio_callback_executed":False,
            "independent_signature":"NONE",
            "source_anchors":[
               source_anchor(txts[a[0]],paths[a[0]],a[1],table[paths[a[0]]]),
               source_anchor(txts[b[0]],paths[b[0]],b[1],table[paths[b[0]]])]})
    return {
      "schema":SCHEMA,"verdict":VERDICT,
      "method":"ISOLATED_C11_CALLBACK_LEASE_FEASIBILITY_SOURCE_ONLY",
      "manifest_sha256":manifest,"source_files_sha_pinned":len(table),
      "r37_candidate_sha256":adaptersha,"r36_unchanged_sha256":table[R36],
      "r31_unchanged_sha256":table[R31],
      "r36_report_sha256":sha(Path(reports["r36"]).read_bytes()),
      "r37_findings":findings_out,"r37_findings_open":14,
      "r37_critical_open":4,
      "r37_contracts":[{"id":c[0],"source_claim":c[1],
          "external_obligation":c[2],"not_proven":c[3]} for c in CONTRACTS],
      "r37_candidate_integrated":False,"r37_os_abi_qualified":False,
      "r37_existing_native_C_edits":0,"r37_audioqueue_calls":0,
      "r37_real_os_callbacks":0,"r37_hardware_emission":"NONE",
      "r36_findings_open":12,"r36_critical_open":4,
      "r35_findings_open":12,"r35_critical_open":4,
      "r34_findings_open":14,"r34_critical_open":4,
      "r33_findings_open":12,"r33_critical_open":3,
      "r32_findings_open":10,"r32_critical_open":2,
      "r31_findings_open":8,"r31_critical_open":2,
      "r30_findings_open":12,"r30_critical_open":2,
      "r29_findings_open":7,"r28_gates_open":5,
      "r27_findings_open":9,"r23_obligations_open":15,
      "r24_findings_open":7,"bureau_gates_open":11,
      "bureau_gates_resolved":0,
      "C11_happens_before":"NOT_PROVEN",
      "owner_lifetime_in_real_callbacks":"NOT_PROVEN",
      "CoreAudio_callback_quiescence":"NOT_PROVEN",
      "failed_OS_stop":"NOT_TESTED","failed_OS_dispose":"NOT_TESTED",
      "physical_cutoff":"NOT_PROVEN","bureau_certification":"PENDING",
      "limitations":list(LIMITATIONS),
      "scientific_simulation":"NONE","physical_emission":"NONE",
      "acoustic_output":"LOCKED","em_output":"LOCKED",
      "real_output":"NOT_AUTHORIZED",
      "biological_exposure":"NOT_AUTHORIZED",
      "production":"NOT_AUTHORIZED",
    }

def markdown(report):
    rows=["| "+f["id"]+" | "+f["severity"]+" | OPEN_NOT_PROVEN |"
          for f in report["r37_findings"]]
    return (
        "# FREQMED GEN-R37 — Isolated C11 Callback Lease Feasibility\n\n"
        "**Verdict: ISOLATED_C11_LEASE_ADAPTER_REVIEWED_OS_INTEGRATION_NOT_PROVEN.**\n\n"
        "Two source-only entry wrappers acquire fm36_try_enter BEFORE returning "
        "the owner; a local lease rejects sequential double exit. This is NOT "
        "a real AudioQueue callback ABI, not linked into R31, and not a proof "
        "that callers initialize/finish every lease or retain owner aliases.\n\n"
        "| Finding | Severity | Status |\n|---|---|---|\n"
        +"\n".join(rows)+"\n\n"
        "R37=14 OPEN (4 CRITICAL), R36=12, R35=12, R34=14, "
        "R33=12, R32=10, R31=8, R30=12, R29=7, R28=5, "
        "R27=9, R23=15, R24=7, Bureau=11 OPEN/0 resolved.\n\n"
        "NEVER_SIMULATION=ENFORCED; ZERO_COST_FOSS=ENFORCED; "
        "ACOUSTIC_OUTPUT=LOCKED; EM_OUTPUT=LOCKED; "
        "REAL_OUTPUT=NOT_AUTHORIZED; BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED; "
        "PRODUCTION=NOT_AUTHORIZED.\n")

def main():
    p=argparse.ArgumentParser(description="GEN-R37 isolated callback lease proof gates")
    p.add_argument("--root",type=Path,required=True)
    p.add_argument("--archive-r19",type=Path,required=True)
    for n in range(16,37):
        p.add_argument("--r"+str(n),type=Path,required=True)
    p.add_argument("--json",type=Path,required=True)
    p.add_argument("--markdown",type=Path,required=True)
    a=p.parse_args()
    try:
        reports={"r"+str(n):getattr(a,"r"+str(n)) for n in range(16,37)}
        result=audit(a.root,a.archive_r19,reports)
        a.json.write_text(json.dumps(result,sort_keys=True,indent=2,
                            ensure_ascii=False)+"\n",encoding="utf-8")
        a.markdown.write_text(markdown(result),encoding="utf-8")
    except (R37Error,r36.R36Error,r35.R35Error,r34.R34Error,r33.R33Error,
            r32.R32Error,r31.R31Error,r30.R30Error,r29.R29Error,
            r28.R28Error,r27.R27Error,r26.R26Error,ValueError,
            TypeError,KeyError,IndexError,OSError,UnicodeError) as exc:
        print("R37_ADAPTER_OWNERSHIP_REVIEW=FAIL_CLOSED",str(exc))
        return 2
    print("R37_ADAPTER_OWNERSHIP_REVIEW=PASS")
    print("R37_FINDINGS=14_OPEN; R37_CRITICAL=4_OPEN")
    print("R37_LEASE_CONTRACTS=6_SOURCE_ONLY; REAL_OS_CALLBACKS=0")
    print("R37_OS_INTEGRATION=NO; R37_ABI_QUALIFIED=NO")
    print("R37_R36_FINDINGS=12_OPEN; R37_R35_FINDINGS=12_OPEN")
    print("R37_BUREAU_GATES=11_OPEN; R37_BUREAU_RESOLVED=0")
    print("R37_REVIEW_VERDICT="+VERDICT)
    print("R37_OWNER_LIFETIME=NOT_PROVEN; R37_C11_HB=NOT_PROVEN")
    print("R37_CALLBACK_QUIESCENCE=NOT_PROVEN; R37_PHYSICAL_CUTOFF=NOT_PROVEN")
    print("R37_PHYSICAL_EMISSION=NONE; R37_SCIENTIFIC_SIMULATION=NONE")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
