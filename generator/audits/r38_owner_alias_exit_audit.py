#!/usr/bin/env python3
"""FREQMED GEN-R38 — owner alias + callback exit-path completeness, SOURCE ONLY.

Observes SHA-pinned C31, C36 and C37 and replays genuine R16–R37 reports.
A static control-flow inventory is NOT a dynamic callback, proof of real OS
quiescence, C11 data-race freedom, or physical safety. No simulation.
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
import r37_adapter_ownership_proof_review as r37

SCHEMA="FREQMED_GEN_R38_CALLBACK_OWNER_ALIAS_EXIT_PATH_REVIEW"
VERDICT="OWNER_ALIAS_EXIT_PATHS_MAPPED_RUNTIME_LIFETIME_NOT_PROVEN"
FILES={"r31":r31.CANDIDATE,"r36":r36.CANDIDATE,"r37":r37.CANDIDATE}
FINDINGS=(
 ("AL38_01_C31_REAL_OS_DIRECT_OWNER_ALIAS","CRITICAL","B07",
  "NewOutput and listener still receive heap ctx, not the immortal token"),
 ("AL38_02_OS_ENTRY_BEFORE_R28_LEASE","CRITICAL","B07",
  "Pre-admission ctx->gate member access requires an already live heap owner"),
 ("AL38_03_EXTERNAL_OWNER_FREE_NOT_FORMALLY_EXCLUDED","CRITICAL","B09",
  "C36/C37 contracts cannot constrain all external references to owner"),
 ("AL38_04_FAILED_OS_OPERATION_RETAINS_UNCERTAINTY","CRITICAL","B07",
  "Stop, remove listener and dispose errors do not prove OS quiescence"),
 ("AL38_05_PHYSICAL_CUTOFF_NOT_PROVEN","CRITICAL","B10",
  "Retaining heap and sealing admission do not establish hardware cutoff"),
 ("AL38_06_C31_PUBLISH_BOUNDARY_FREE_CENSUS","HIGH","B09",
  "Two observed frees before NewOutput are not exhaustive pointer analysis"),
 ("AL38_07_CALLBACK_OUTPUT_ADMIT_LEAVE_STRUCTURE","HIGH","B09",
  "Output callback has one textual enter/leave, not verified scheduling"),
 ("AL38_08_CALLBACK_LISTENER_GOTO_EXIT_STRUCTURE","HIGH","B09",
  "Listener shared label covers visible exits but not all OS behaviors"),
 ("AL38_09_R37_LEASE_INITIALIZATION_EXTERNAL","HIGH","B09",
  "Each FM37Lease must be fresh, zero-initialized and not concurrently shared"),
 ("AL38_10_R37_LEASE_FINISH_MISSING_PATH","HIGH","B09",
  "No callback OS wrapper guarantees once-only finish on every successful entry"),
 ("AL38_11_R37_FINISH_ERROR_UNDERFLOW","HIGH","B09",
  "Local FINISHED is set before fm36_leave, even if leave returns an error"),
 ("AL38_12_R36_GLOBAL_ADMISSION_NOT_CALLBACK_ID","HIGH","B09",
  "Global admitted counter is not an independent callback-specific lease ID"),
 ("AL38_13_ALIAS_STORAGE_AND_PUBLICATION","HIGH","B09",
  "Anchor owner publication is atomic but field alias lifetime is external"),
 ("AL38_14_QUEUE_REF_NONATOMIC_C11","HIGH","B09",
  "ctx->queue is accessed on PCM side and cleared in controller without proof"),
 ("AL38_15_SESSION_EXHAUSTION_AND_QUARANTINE","HIGH","B07",
  "One-shot process lifetime policy and OS resource failure remain unqualified"),
 ("AL38_16_C36_C37_NOT_ABI_INTEGRATED","HIGH","B07",
  "No real AudioQueue callback uses the C36/C37 modules"),
 ("AL38_17_STATIC_TOKEN_CENSUS_LIMITS","HIGH","B09",
  "Lexical source census cannot prove absence of indirect alias paths"),
 ("AL38_18_NO_OUTPUT_LINK_PROOF_VS_PHYSICAL","HIGH","B10",
  "Unlinked candidate software does not certify physical instruments"),
)
# Every claim references two existing, exact source snippets; no invented lines.
ANCHORS=(
 ("AL38_01_C31_REAL_OS_DIRECT_OWNER_ALIAS",("r31","AudioQueueNewOutput(&fmt,output_callback,ctx"),("r31","queue_running_listener,ctx)")),
 ("AL38_02_OS_ENTRY_BEFORE_R28_LEASE",("r31","fm_r28_gate_try_enter(&ctx->queue_admission)"),("r31","AcousticContext *ctx=(AcousticContext*)ptr;")),
 ("AL38_03_EXTERNAL_OWNER_FREE_NOT_FORMALLY_EXCLUDED",("r36","* after this claim, even if preparing/publishing/OS creation fails."),("r37","* 2. After fm36_prepare_once claims owner, NO external alias releases owner.")),
 ("AL38_04_FAILED_OS_OPERATION_RETAINS_UNCERTAINTY",("r31","if (r31_immediate_stop_status!=noErr) {"),("r31","if (AudioQueueDispose(ctx->queue,true)!=noErr) {")),
 ("AL38_05_PHYSICAL_CUTOFF_NOT_PROVEN",("r31","/* CRITICAL: OS stop failed."),("r37","* 6. Closing admissions is NOT OS callback quiescence or physical cutoff.")),
 ("AL38_06_C31_PUBLISH_BOUNDARY_FREE_CENSUS",("r31","free(owner_ctx);"),("r31","AudioQueueNewOutput(&fmt,output_callback,ctx")),
 ("AL38_07_CALLBACK_OUTPUT_ADMIT_LEAVE_STRUCTURE",("r31","(void)atomic_fetch_add_explicit(&ctx->active_output_callbacks"),("r31","fm_r28_gate_leave(&ctx->queue_admission);")),
 ("AL38_08_CALLBACK_LISTENER_GOTO_EXIT_STRUCTURE",("r31","listener_exit:"),("r31","(void)atomic_fetch_sub_explicit(&ctx->active_property_listeners")),
 ("AL38_09_R37_LEASE_INITIALIZATION_EXTERNAL",("r37","FM37Lease lease={0};"),("r37","FM37LeasePhase phase;")),
 ("AL38_10_R37_LEASE_FINISH_MISSING_PATH",("r37","int fm37_finish(FM37Lease *lease)"),("r37","* 4. Every successful enter has exactly one matching leave on every path.")),
 ("AL38_11_R37_FINISH_ERROR_UNDERFLOW",("r37","lease->phase=FM37_LEASE_FINISHED;"),("r37","return fm36_leave(token);")),
 ("AL38_12_R36_GLOBAL_ADMISSION_NOT_CALLBACK_ID",("r36","atomic_uint admitted;"),("r36","int fm36_leave(void *userdata)")),
 ("AL38_13_ALIAS_STORAGE_AND_PUBLICATION",("r36","_Atomic(void *) owner;"),("r36","atomic_store_explicit(&fm36_anchor.owner,owner,memory_order_relaxed);")),
 ("AL38_14_QUEUE_REF_NONATOMIC_C11",("r31","AudioQueueEnqueueBuffer(ctx->queue,buf,0,NULL)"),("r31","ctx->queue=NULL;")),
 ("AL38_15_SESSION_EXHAUSTION_AND_QUARANTINE",("r36","static atomic_flag fm36_one_shot_claim=ATOMIC_FLAG_INIT;"),("r31","atomic_store_explicit(&fm_context_quarantined,1,memory_order_release);")),
 ("AL38_16_C36_C37_NOT_ABI_INTEGRATED",("r31","static void output_callback(void *ptr,"),("r37","* Signatures are NOT an AudioQueue ABI and MUST NOT be installed with OS.")),
 ("AL38_17_STATIC_TOKEN_CENSUS_LIMITS",("r31","AcousticContext *ctx=owner_ctx;"),("r36","* - The entire object is NEVER linked or loaded into the production binary.")),
 ("AL38_18_NO_OUTPUT_LINK_PROOF_VS_PHYSICAL",("r31","/* GEN-R3: unconditional hard denial"),("r37","* NEVER link, load, dispatch, activate, or call as real CoreAudio code.")),
)
# Explicit scopes document alias relationships. These are SOURCE-only, not edges
# of an executable model or an experiment.
ALIAS_ROWS=(
 ("R31_HEAP_OWNER","owner_ctx","heap allocator","owns until prepublish checks"),
 ("R31_LOCAL_ALIAS","ctx","owner_ctx","direct heap alias"),
 ("R31_NEWOUTPUT_USERDATA","ctx","AudioQueueNewOutput","OS holds direct alias"),
 ("R31_LISTENER_USERDATA","ctx","AudioQueueAddPropertyListener","OS holds direct alias"),
 ("R31_CALLBACK_ALIAS","ptr","output_callback","callback-local direct alias"),
 ("R31_LISTENER_ALIAS","data","queue_running_listener","callback-local direct alias"),
 ("R31_QUEUE_REFERENCE","ctx->queue","controller and PCM","non-atomic pointer field"),
 ("R36_STATIC_TOKEN","&fm36_anchor","process lifetime","separate unintegrated candidate"),
 ("R36_ATOMIC_OWNER","fm36_anchor.owner","fm36_prepare_once","no external alias enforcement"),
 ("R37_LOCAL_LEASE_OWNER","lease->owner","fm37_begin","non-atomic local lease"),
 ("R37_OUTPUT_ENTRY","FM37Lease","fm37_output_enter","non-OS wrapper"),
 ("R37_LISTENER_ENTRY","FM37Lease","fm37_property_enter","non-OS wrapper"),
)
CALLBACKS=("callback","listener")
LIMITATIONS=(
 "THIS_IS_STATIC_SOURCE_INVESTIGATION_NOT_A_FORMAL_C11_PROOF",
 "NO_C11_SCHEDULING_OR_OS_CALLBACK_EXECUTED",
 "NO_SCIENTIFIC_SIMULATION_OR_SYNTHETIC_INTERLEAVINGS",
 "NO_REAL_STOP_DISPOSE_OR_LISTENER_REMOVAL_FAILURE",
 "NO_COMPLETE_ALIAS_ANALYSIS_OF_EXTERNAL_NATIVE_LIBRARIES",
 "NO_OS_CALLBACK_QUIESCENCE_OR_PHYSICAL_CUTOFF_MEASUREMENT",
 "NO_INDEPENDENT_SIGNED_BUREAU_CERTIFICATION",
)
class R38Error(ValueError): pass

def require(ok,msg):
    if not ok: raise R38Error(msg)
def sha(x): return hashlib.sha256(x).hexdigest()

def ordered(scope,markers,label):
    require(all(m in scope for m in markers),"R38 missing source path marker: "+label)
    positions=[scope.index(m) for m in markers]
    require(positions==sorted(positions) and len(set(positions))==len(positions),
            "R38 source order changed: "+label)

def observe(r31src,r36src,r37src):
    r36.observe(r36src,r31src)
    r37.observe(r37src,r36src,r31src)
    controller=r29.function(r31src,"controller")
    output=r29.function(r31src,"callback")
    listener=r29.function(r31src,"listener")
    finish=r37.function(r37src,"fm37_finish")
    begin=r37.function(r37src,"fm37_begin")
    leave=r36.function_bounds(r36src,"fm36_leave")[2]
    expose=controller.index("AudioQueueNewOutput(&fmt,output_callback,ctx")
    require(controller[:expose].count("free(owner_ctx);")==2
           and controller[expose:].count("free(owner_ctx);")==0,
            "R38 ownership release crossed OS publication boundary")
    require(r31src.count("free(owner_ctx);")==2,
            "R38 unknown new C31 owner free site")
    require("free(" not in r36src and "free(" not in r37src,
            "R38 candidate C36/C37 frees or mentions allocator unexpectedly")
    ordered(output,("AcousticContext *ctx=(AcousticContext*)ptr;",
       "fm_r28_gate_try_enter(&ctx->queue_admission)",
       "atomic_fetch_add_explicit(&ctx->active_output_callbacks",
       "atomic_fetch_sub_explicit(&ctx->active_output_callbacks",
       "fm_r28_gate_leave(&ctx->queue_admission);"),"output callback")
    ordered(listener,("AcousticContext *ctx=(AcousticContext*)data;",
       "fm_r28_gate_try_enter(&ctx->queue_admission)",
       "atomic_fetch_add_explicit(&ctx->active_property_listeners",
       "listener_exit:",
       "atomic_fetch_sub_explicit(&ctx->active_property_listeners",
       "fm_r28_gate_leave(&ctx->queue_admission);"),"property listener")
    # No early C return after admission; explicit goto label is the listener
    # exit shared by the source. These cannot certify external OS callback ends.
    for scope,name in ((output,"output"),(listener,"listener")):
        gate=scope.index("fm_r28_gate_try_enter(&ctx->queue_admission)")
        end=scope.index("fm_r28_gate_leave(&ctx->queue_admission);")
        require(not re.search(r"\breturn\b",scope[gate:end]),
                "R38 unbalanced early return before "+name+" gate leave")
        require(scope.count("fm_r28_gate_leave(&ctx->queue_admission);")==1,
                "R38 callback gate leave cardinality changed")
        require(scope.count("fm_r28_gate_try_enter(&ctx->queue_admission)")==1,
                "R38 callback admission cardinality changed")
    require(listener.count("listener_exit:")==1 and
            listener.count("goto listener_exit;")>=1,
            "R38 listener shared exit label vanished")
    ordered(begin,("if (!lease || lease->phase!=FM37_LEASE_UNUSED) return -1;",
                   "fm36_try_enter(os_userdata,&owner)",
                   "lease->os_userdata=os_userdata;",
                   "lease->owner=owner;",
                   "lease->phase=FM37_LEASE_ACTIVE;"),"R37 entry")
    ordered(finish,("if (!lease || lease->phase!=FM37_LEASE_ACTIVE) return -1;",
                    "void *token=lease->os_userdata;",
                    "lease->phase=FM37_LEASE_FINISHED;",
                    "lease->owner=NULL;",
                    "lease->os_userdata=NULL;",
                    "return fm36_leave(token);"),"R37 finish")
    require("while (seen>0u)" in leave
            and "&fm36_anchor.admitted,&seen,seen-1u" in leave,
            "R38 R36 shared counter leave safety boundary drift")
    require("fm37_finish(" not in r31src and "fm37_output_enter(" not in r31src
            and "fm37_property_enter(" not in r31src,
            "R38 candidate incorrectly integrated without authorization")
    require(len(ALIAS_ROWS)==12 and len(FINDINGS)==18 and len(ANCHORS)==18
            and sum(f[1]=="CRITICAL" for f in FINDINGS)==5
            and [f[0] for f in FINDINGS]==[e[0] for e in ANCHORS],
            "R38 alias/proof ledgers changed cardinality")
    texts={"r31":r31src,"r36":r36src,"r37":r37src}
    for name,first,second in ANCHORS:
        for src,needle in (first,second):
            require(needle in texts[src],
                    "R38 missing proof anchor "+name+" / "+needle)
    return {f[0]:"OPEN_NOT_PROVEN" for f in FINDINGS}

def inspect(root,override=None):
    root=Path(root).resolve()
    table,manifest=r17.manifest_integrity(root)
    require(len(table)==213,"R38 requires exactly 213 source files SHA pinned")
    needed=("audits/r38_owner_alias_exit_audit.py",
            "tests/test_r38_owner_alias_exit_audit.py",
            "RUN_GEN_R38_MAC_INTEL.command",
            "docs/GEN_R38_ALIAS_EXIT_PATH_MATRIX.md",
            "docs/GEN_R38_BUREAU_REVIEW.md",
            "docs/GEN_R38_ADVERSARIAL_PROOF_OBLIGATIONS.md")
    require(all(x in table for x in needed),"R38 audit/test/docs unpinned")
    old=r37.inspect(root)
    require(old[2]==table[FILES["r37"]],"R37 source changed since baseline")
    require(table[r26.ORIGINAL]==r19.PINNED_ACOUSTIC_SHA256,
            "R38 real native backend source digest changed")
    raw={key:(root/rel).read_bytes() for key,rel in FILES.items()}
    require(all(sha(raw[key])==table[rel] for key,rel in FILES.items()),
            "R38 C31/C36/C37 original source digests drifted")
    proof=observe((override if override is not None else raw["r31"].decode("utf-8")),
                  raw["r36"].decode("utf-8"),raw["r37"].decode("utf-8"))
    runner=(root/"RUN_GEN_R38_MAC_INTEL.command").read_text(encoding="utf-8")
    require(set(r17.link_sources(runner))==r17.LINK_C_ALLOWLIST,
            "R38 CLI link allowlist changed")
    parts=runner.split(' -o "$WORK/freqmed-gen"')
    require(len(parts)==2,"R38 no-output executable link line missing")
    link=parts[1].split("-framework CoreAudio",1)[0]
    require("output_hard_denied.c" in link,"R38 CLI unconditional denial absent")
    for candidate in ("r37_callback_lease_adapter.c","r36_stable_userdata_anchor.c",
                      "acoustic_macos_r31.c","r28_callback_admission_gate.c",
                      "src/acoustic_macos.c"):
        require(candidate not in link,"R38 forbidden linked candidate "+candidate)
    for token in ("R38_ALIAS_EXIT_REVIEW=PASS",
                  "R38_R31_CANDIDATE_OBJECT=COMPILED_UNLINKED",
                  "R38_STABLE_ANCHOR_OBJECT=COMPILED_UNLINKED",
                  "R38_CALLBACK_LEASE_OBJECT=COMPILED_UNLINKED",
                  "R38_NONEMITTING_EXECUTABLE_SYMBOL_AUDIT=PASS",
                  "R38_BUREAU_PROOF_DOSSIER=38_FILES_SHA256_PASS",
                  "R38_TESTCASE_RUN_SLOT=PASS",
                  "FREQMED_GEN_R38_EVIDENCE_DIR","FREQMED_GEN_R38_BINARY"):
        require(token in runner,"R38 runner guard missing "+token)
    return table,manifest,{x:sha(raw[x]) for x in FILES},proof

def anchor(src,path,needle,digest):
    require(needle in src,"R38 source witness absent "+needle)
    return {"path":path,"line":src.count("\n",0,src.index(needle))+1,
            "sha256":digest,"exact_text":needle}

def audit(root,archive_r19,reports):
    table,manifest,digests,findings=inspect(root)
    past=r37.audit(root,archive_r19,reports)
    record=json.loads(Path(reports["r37"]).read_text(encoding="utf-8"))
    require(past==record,"R38 historical R37 witness not reproducible")
    require(past["r37_findings_open"]==14 and past["r37_critical_open"]==4
            and past["r36_findings_open"]==12 and past["r35_findings_open"]==12
            and past["r34_findings_open"]==14 and past["r33_findings_open"]==12
            and past["r32_findings_open"]==10 and past["r31_findings_open"]==8
            and past["r30_findings_open"]==12 and past["r29_findings_open"]==7
            and past["r28_gates_open"]==5 and past["r27_findings_open"]==9
            and past["r23_obligations_open"]==15
            and past["r24_findings_open"]==7
            and past["bureau_gates_open"]==11
            and past["bureau_gates_resolved"]==0,
            "R38 former Bureau blocks improperly discharged")
    src={x:(Path(root)/p).read_text(encoding="utf-8") for x,p in FILES.items()}
    entries=[]
    for (fid,severity,seat,obligation),(key,a,b) in zip(FINDINGS,ANCHORS):
        require(fid==key,"R38 anchor/findings misaligned")
        entries.append({"id":fid,"severity":severity,
          "bureau_seat":seat,"status":findings[fid],
          "unproven_obligation":obligation,"real_callbacks_executed":False,
          "source_anchors":[anchor(src[x],FILES[x],s,digests[x])
              for x,s in (a,b)]})
    return {
       "schema":SCHEMA,"verdict":VERDICT,
       "method":"SHA_PINNED_STATIC_OWNER_ALIAS_AND_EXIT_PATH_CENSUS_ONLY",
       "source_manifest_sha256":manifest,"source_count":len(table),
       "source_digests":digests,
       "previous_r37_report_sha256":sha(Path(reports["r37"]).read_bytes()),
       "r38_alias_rows":[dict(zip(("id","alias","origin","contract"),r))
           for r in ALIAS_ROWS],
       "r38_alias_count":len(ALIAS_ROWS),
       "r38_findings":entries,"r38_findings_open":18,"r38_critical_open":5,
       "r38_observed_prepublication_owner_frees":2,
       "r38_observed_postpublication_owner_frees":0,
       "r38_c31_output_gate_joins":1,"r38_c31_listener_gate_joins":1,
       "r38_adapter_integrated":False,"r38_OS_callback_coverage":0,
       "r38_coreaudio_activity":False,"r38_prior_C_modified":False,
       "r37_findings_open":14,"r37_critical_open":4,
       "r36_findings_open":12,"r36_critical_open":4,
       "r35_findings_open":12,"r35_critical_open":4,
       "r34_findings_open":14,"r34_critical_open":4,
       "r33_findings_open":12,"r33_critical_open":3,
       "r32_findings_open":10,"r32_critical_open":2,
       "r31_findings_open":8,"r31_critical_open":2,
       "r30_findings_open":12,"r30_critical_open":2,
       "r29_findings_open":7,"r28_gates_open":5,"r27_findings_open":9,
       "r23_obligations_open":15,"r24_findings_open":7,
       "bureau_gates_open":11,"bureau_gates_resolved":0,
       "owner_alias_lifetime":"NOT_PROVEN",
       "callback_exit_path_completeness":"NOT_PROVEN",
       "C11_happens_before":"NOT_PROVEN",
       "CoreAudio_callback_quiescence":"NOT_PROVEN",
       "physical_cutoff":"NOT_PROVEN",
       "Bureau_certification":"PENDING",
       "scientific_simulation":"NONE","physical_emission":"NONE",
       "acoustic_output":"LOCKED","em_output":"LOCKED",
       "real_output":"NOT_AUTHORIZED","biological_exposure":"NOT_AUTHORIZED",
       "production":"NOT_AUTHORIZED","limitations":list(LIMITATIONS),
    }

def markdown(r):
    rows=["| "+f["id"]+" | "+f["severity"]+" | OPEN_NOT_PROVEN |"
          for f in r["r38_findings"]]
    return ("# FREQMED GEN-R38 — Alias and Callback Exit Audit\n\n"
       "**Verdict: OWNER_ALIAS_EXIT_PATHS_MAPPED_RUNTIME_LIFETIME_NOT_PROVEN.**\n\n"
       "This is a STATIC source-only census. Two prepublication C31 "
       "owner frees and zero postpublication frees are OBSERVED; no "
       "complete static proof of external aliases follows. No real OS "
       "callback or scientific simulation was executed.\n\n"
       "| Finding | Severity | Status |\n|---|---|---|\n"
       +"\n".join(rows)+"\n\n"
       "R38: 18 OPEN (5 CRITICAL), R37 14, R36 12, R35 12, "
       "R34 14, R33 12, R32 10, R31 8, R30 12, R29 7, "
       "R28 5, R27 9, R23 15, R24 7, historical Bureau 11 OPEN.\n\n"
       "NEVER_SIMULATION=ENFORCED; ZERO_COST_FOSS=ENFORCED; "
       "ACOUSTIC_OUTPUT=LOCKED; EM_OUTPUT=LOCKED; REAL_OUTPUT=NOT_AUTHORIZED; "
       "BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED; PRODUCTION=NOT_AUTHORIZED.\n")

def main():
    p=argparse.ArgumentParser(description="R38 static callback alias audit")
    p.add_argument("--root",type=Path,required=True)
    p.add_argument("--archive-r19",type=Path,required=True)
    for n in range(16,38):
        p.add_argument("--r"+str(n),type=Path,required=True)
    p.add_argument("--json",type=Path,required=True)
    p.add_argument("--markdown",type=Path,required=True)
    args=p.parse_args()
    try:
        reports={"r"+str(n):getattr(args,"r"+str(n)) for n in range(16,38)}
        res=audit(args.root,args.archive_r19,reports)
        args.json.write_text(json.dumps(res,sort_keys=True,indent=2,
                             ensure_ascii=False)+"\n",encoding="utf-8")
        args.markdown.write_text(markdown(res),encoding="utf-8")
    except (R38Error,r37.R37Error,r36.R36Error,r35.R35Error,r34.R34Error,
            r33.R33Error,r32.R32Error,r31.R31Error,r30.R30Error,
            r29.R29Error,r28.R28Error,r27.R27Error,r26.R26Error,
            ValueError,TypeError,KeyError,IndexError,OSError,UnicodeError) as exc:
        print("R38_ALIAS_EXIT_REVIEW=FAIL_CLOSED",str(exc))
        return 2
    print("R38_ALIAS_EXIT_REVIEW=PASS")
    print("R38_OWNER_ALIASES=12_SOURCE_ROWS")
    print("R38_FINDINGS=18_OPEN; R38_CRITICAL=5_OPEN")
    print("R38_C31_PREPUBLICATION_FREES=2; R38_POSTPUBLICATION_FREES=0")
    print("R38_C31_CALLBACK_GATE_EXITS=2_DOCUMENTARY; R38_OS_CALLBACKS=0")
    print("R38_R37_FINDINGS=14_OPEN; R38_R36_FINDINGS=12_OPEN")
    print("R38_BUREAU_GATES=11_OPEN; R38_BUREAU_RESOLVED=0")
    print("R38_REVIEW_VERDICT="+VERDICT)
    print("R38_OWNER_LIFETIME=NOT_PROVEN; R38_EXIT_COMPLETENESS=NOT_PROVEN")
    print("R38_C11_HAPPENS_BEFORE=NOT_PROVEN; R38_OS_QUIESCENCE=NOT_PROVEN")
    print("R38_PHYSICAL_CUTOFF=NOT_PROVEN; R38_PHYSICAL_EMISSION=NONE")
    print("R38_SCIENTIFIC_SIMULATION=NONE")
    return 0
if __name__=="__main__":
    raise SystemExit(main())
