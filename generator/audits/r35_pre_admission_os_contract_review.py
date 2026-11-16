#!/usr/bin/env python3
"""FREQMED GEN-R35: independent pre-admission callback lifetime / OS contract review.
SHA-anchored source observations and documentary API classification ONLY.
Never executes CoreAudio, dispatches callbacks, simulates scientific data or emits.
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

SCHEMA="FREQMED_GEN_R35_PRE_ADMISSION_OS_CONTRACT_EVIDENCE"
VERDICT="PUBLIC_OS_CONTRACTS_CLASSIFIED_PRE_ADMISSION_LIFETIME_NOT_PROVEN"
CANDIDATE=r31.CANDIDATE

# Public Apple Developer pages consulted 2026-11-16. URLs are LIVE and not an
# immutable snapshot: these classifications are NOT independently certified.
STOP_URL="https://developer.apple.com/documentation/audiotoolbox/audioqueuestop%28_%3A_%3A%29"
DISPOSE_URL="https://developer.apple.com/documentation/audiotoolbox/audioqueuedispose%28_%3A_%3A%29"
LISTENER_URL="https://developer.apple.com/documentation/audiotoolbox/audioqueuepropertylistenerproc"
REMOVE_URL="https://developer.apple.com/documentation/audiotoolbox/audioqueueremovepropertylistener%28_%3A_%3A_%3A_%3A%29"
API_EVIDENCE=(
 ("API35_01_STOP_TRUE","DOCUMENTED_REQUEST_SUCCESS_PATH",STOP_URL,
  "true requests synchronous immediate queue stop; errors do not establish success"),
 ("API35_02_STOP_FALSE","DOCUMENTED_REQUEST_SUCCESS_PATH",STOP_URL,
  "false allows asynchronous draining with callbacks until stopped"),
 ("API35_03_STOP_HARDWARE","DOCUMENTED_CONDITIONAL",STOP_URL,
  "associated hardware stops only when not used by other audio services"),
 ("API35_04_DISPOSE_TRUE","DOCUMENTED_REQUEST_SUCCESS_PATH",DISPOSE_URL,
  "true requests synchronous immediate disposal of queue and its buffers"),
 ("API35_05_DISPOSE_CALLBACKS","DOCUMENTED_POST_DISPOSAL_ONLY",DISPOSE_URL,
  "no callbacks are invoked by the queue after disposal; failure not certified"),
 ("API35_06_LISTENER_USERDATA","DOCUMENTED_ARGUMENT_CONTRACT",LISTENER_URL,
  "property callback receives the custom inUserData registered with listener"),
 ("API35_07_REMOVE_LISTENER","DOCUMENTED_API_PARAMETERS",REMOVE_URL,
  "removal requires same userdata and matching callback/property arguments"),
 ("API35_08_PRE_ADMISSION_LIFETIME","NOT_ESTABLISHED_BY_PAGES",LISTENER_URL,
  "no complete C11 lifetime proof for userdata before the first atomic access"),
 ("API35_09_FAILED_OSSTATUS","NOT_ESTABLISHED_BY_PAGES",DISPOSE_URL,
  "no guaranteed callback quiescence asserted after nonzero OSStatus"),
)
FINDINGS=(
 ("PA35_01_OUTPUT_PRE_ADMISSION_LIFETIME","CRITICAL","B07",
  "Prove valid userdata at the instant CoreAudio invokes output_callback before the first ctx->gate access."),
 ("PA35_02_LISTENER_PRE_ADMISSION_LIFETIME","CRITICAL","B07",
  "Prove property-listener userdata lifetime before its gate access, including late or rejected callbacks."),
 ("PA35_03_FAILED_DISPOSE_CALLBACKS","CRITICAL","B07",
  "Qualify nonzero AudioQueueDispose OSStatus: no post-disposal success guarantee can be assumed."),
 ("PA35_04_FAILED_STOP_PHYSICAL_CUTOFF","CRITICAL","B10",
  "A nonzero AudioQueueStop status must not be treated as measured or certified physical cutoff."),
 ("PA35_05_COUNTERS_MISS_PRE_GATE","HIGH","B09",
  "Counters increment after gate acceptance and cannot count OS entries before admission."),
 ("PA35_06_GATE_CLOSE_NOT_OS_CANCEL","HIGH","B07",
  "C11 gate closure does not revoke a callback already dispatched by CoreAudio."),
 ("PA35_07_CONSTRUCTOR_PUBLICATION_ERROR","HIGH","B07",
  "Characterize userdata publication/ownership on AudioQueueNewOutput failure."),
 ("PA35_08_LISTENER_REGISTRATION_ERROR","HIGH","B07",
  "Qualify callback state on a failed AudioQueueAddPropertyListener call."),
 ("PA35_09_LISTENER_REMOVE_ERROR","HIGH","B07",
  "Determine postconditions for failed removal and callbacks already entered."),
 ("PA35_10_SYNC_DISPOSE_HB_SEPARATE","HIGH","B09",
  "Separate documented successful disposal from C11 happens-before evidence for context release."),
 ("PA35_11_QUEUE_POINTER_ORDER","HIGH","B09",
  "Prove non-atomic ctx->queue use/clear ordering between callbacks and controller."),
 ("PA35_12_ONE_SHOT_RETAIN_NOT_SAFE_SHUTDOWN","HIGH","B10",
  "Process quarantine and heap retention prevent some frees, not physical output or external callback activity."),
)
# Each finding has two exact source C anchors to avoid free-form claims.
ANCHORS=(
 ("PA35_01_OUTPUT_PRE_ADMISSION_LIFETIME",
  ("callback","AcousticContext *ctx=(AcousticContext*)ptr;"),
  ("callback","if (!fm_r28_gate_try_enter(&ctx->queue_admission)) return;")),
 ("PA35_02_LISTENER_PRE_ADMISSION_LIFETIME",
  ("listener","AcousticContext *ctx=(AcousticContext*)data;"),
  ("listener","if (!fm_r28_gate_try_enter(&ctx->queue_admission)) return;")),
 ("PA35_03_FAILED_DISPOSE_CALLBACKS",
  ("controller","if (AudioQueueDispose(ctx->queue,true)!=noErr) {"),
  ("controller","fm_latch_first_fault(ctx,FM_FAULT_DISPOSAL);")),
 ("PA35_04_FAILED_STOP_PHYSICAL_CUTOFF",
  ("controller","const OSStatus r31_immediate_stop_status=AudioQueueStop(ctx->queue,true);"),
  ("controller","if (r31_immediate_stop_status!=noErr) {")),
 ("PA35_05_COUNTERS_MISS_PRE_GATE",
  ("callback","atomic_fetch_add_explicit(&ctx->active_output_callbacks,1U,"),
  ("listener","atomic_fetch_add_explicit(&ctx->active_property_listeners,1U,")),
 ("PA35_06_GATE_CLOSE_NOT_OS_CANCEL",
  ("controller","fm_r28_gate_close(&ctx->queue_admission);"),
  ("callback","fm_r28_gate_try_enter(&ctx->queue_admission)")),
 ("PA35_07_CONSTRUCTOR_PUBLICATION_ERROR",
  ("controller","AudioQueueNewOutput(&fmt,output_callback,ctx,NULL,NULL,0,&ctx->queue)"),
  ("controller","fm_r28_gate_close(&ctx->queue_admission);")),
 ("PA35_08_LISTENER_REGISTRATION_ERROR",
  ("controller","AudioQueueAddPropertyListener(ctx->queue,kAudioQueueProperty_IsRunning,"),
  ("controller","listener_registration_uncertain=1;")),
 ("PA35_09_LISTENER_REMOVE_ERROR",
  ("controller","AudioQueueRemovePropertyListener(ctx->queue,"),
  ("controller","listener_remove_failed=1;")),
 ("PA35_10_SYNC_DISPOSE_HB_SEPARATE",
  ("controller","atomic_store(&ctx->dispose_confirmed,1);"),
  ("controller","/* GEN-R26 candidate: diagnostic quiescence does not prove")),
 ("PA35_11_QUEUE_POINTER_ORDER",
  ("pcm","AudioQueueEnqueueBuffer(ctx->queue,buf,0,NULL)"),
  ("controller","ctx->queue=NULL;")),
 ("PA35_12_ONE_SHOT_RETAIN_NOT_SAFE_SHUTDOWN",
  ("controller","atomic_store_explicit(&fm_context_quarantined,1,memory_order_release);"),
  ("controller","/* GEN-R26 candidate: diagnostic quiescence does not prove")),
)
# Source phases are DOCUMENTARY review checkpoints, not executable states.
PHASES=(
 ("PUBLISH_OUTPUT","NEWOUTPUT_USERDATA_SENT","OS ownership on failure NOT_PROVEN"),
 ("REGISTER_LISTENER","LISTENER_USERDATA_SENT","OS registration error state NOT_PROVEN"),
 ("OUTPUT_PRE_GATE","CTX_ACCESS_BEFORE_ENTER","Pre-admission lifetime NOT_PROVEN"),
 ("LISTENER_PRE_GATE","CTX_ACCESS_BEFORE_ENTER","Pre-admission lifetime NOT_PROVEN"),
 ("REJECTED_GATE","CTX_REQUIRED_FOR_REJECTION","Absence of late callback NOT_PROVEN"),
 ("ACCEPTED_GATE","C11_LEASE_AND_COUNTER","Happens-before to OS stop NOT_PROVEN"),
 ("CLOSE_ADMISSION","C11_GATE_CLOSED","OS callback cancellation NOT_PROVEN"),
 ("STOP_OS_SUCCESS","API_REQUEST_SYNCHRONOUS","Independent physical cutoff NOT_PROVEN"),
 ("STOP_OS_FAILURE","OS_STATE_AMBIGUOUS","Output may continue, cutoff NOT_PROVEN"),
 ("REMOVE_LISTENER_FAILURE","LISTENER_STATE_AMBIGUOUS","Callback quiescence NOT_PROVEN"),
 ("DISPOSE_OS_SUCCESS","DOCUMENTED_NO_LATER_QUEUE_CALLBACK","C11 HB / already-entered callback proof NOT_PROVEN"),
 ("DISPOSE_OS_FAILURE","OS_STATE_AMBIGUOUS","No safe-free or late-callback proof"),
 ("PROCESS_QUARANTINE","HEAP_RETAINED","Physical output shutdown NOT_PROVEN"),
)
LIMITATIONS=(
 "PUBLIC_APPLE_URLS_ARE_NOT_PINNED_IMMUTABLE_DOC_SNAPSHOTS",
 "PUBLISHED_API_TEXT_IS_NOT_A_FORMAL_C11_MEMORY_MODEL_PROOF",
 "NO_REAL_PRE_ADMISSION_OS_CALLBACK_WITNESSES",
 "NO_AUDIOQUEUE_STOP_OR_DISPOSE_FAILURE_EXECUTED",
 "NO_SCIENTIFIC_SIMULATION_OR_SYNTHETIC_CALLBACK_INTERLEAVING",
 "NO_ACOUSTIC_OR_EM_PHYSICAL_OUTPUT_MEASUREMENT",
 "NO_INDEPENDENT_SIGNED_BUREAU_CERTIFICATION",
)
class R35Error(ValueError):
    pass

def require(ok,why):
    if not ok:
        raise R35Error(why)

def sha(b):
    return hashlib.sha256(b).hexdigest()

def must_index(source,needle,start=0):
    require(needle in source[start:],"R35 C evidence anchor missing: "+needle)
    return source.index(needle,start)

def function(src,name):
    try:
        return r29.function(src,name)
    except (ValueError,KeyError,IndexError) as ex:
        raise R35Error("R35 required C function missing: "+name) from ex

def observe(src):
    require(src.startswith("/* SPDX-License-Identifier: Apache-2.0 */"),
            "R35 C source SPDX header changed")
    cb=function(src,"callback")
    listener=function(src,"listener")
    ctrl=function(src,"controller")
    pcm=function(src,"pcm")
    # Pointer conversion is NOT itself a dereference. Gate access IS.
    for body,token,field in (
        (cb,"AcousticContext *ctx=(AcousticContext*)ptr;","active_output_callbacks"),
        (listener,"AcousticContext *ctx=(AcousticContext*)data;","active_property_listeners"),
    ):
        conversion=must_index(body,token)
        null=must_index(body,"if (!ctx) return;",conversion)
        gate=must_index(body,"if (!fm_r28_gate_try_enter(&ctx->queue_admission)) return;",null)
        count=must_index(body,"atomic_fetch_add_explicit(&ctx->"+field+",1U,",gate)
        exitcount=must_index(body,"atomic_fetch_sub_explicit(&ctx->"+field+",1U,",count)
        leave=must_index(body,"fm_r28_gate_leave(&ctx->queue_admission);",exitcount)
        require(conversion<null<gate<count<exitcount<leave,
                "R35 pre-admission callback phase ordering changed")
        require(body.count("fm_r28_gate_try_enter(&ctx->queue_admission)")==1
                and body.count("fm_r28_gate_leave(&ctx->queue_admission);")==1,
                "R35 admission/exit pairing drifted")
    publish=must_index(ctrl,"AudioQueueNewOutput(&fmt,output_callback,ctx,NULL,NULL,0,&ctx->queue)")
    register=must_index(ctrl,"AudioQueueAddPropertyListener(ctx->queue,kAudioQueueProperty_IsRunning,",publish)
    close=must_index(ctrl,"fm_r28_gate_close(&ctx->queue_admission);",register)
    stop=must_index(ctrl,"const OSStatus r31_immediate_stop_status=AudioQueueStop(ctx->queue,true);",close)
    failed=must_index(ctrl,"if (r31_immediate_stop_status!=noErr) {",stop)
    busy=must_index(ctrl,"if (r31_admission_busy) {",failed)
    remove=must_index(ctrl,"AudioQueueRemovePropertyListener(ctx->queue,",busy)
    dispose=must_index(ctrl,"if (AudioQueueDispose(ctx->queue,true)!=noErr) {",remove)
    dispose_ok=must_index(ctrl,"atomic_store(&ctx->dispose_confirmed,1);",dispose)
    clear=must_index(ctrl,"ctx->queue=NULL;",dispose_ok)
    require(publish<register<close<stop<failed<busy<remove<dispose<dispose_ok<clear,
            "R35 publication/stop/remove/disposal order changed")
    require(ctrl[:publish].count("free(owner_ctx);")==2
            and ctrl[publish:].count("free(owner_ctx);")==0,
            "R35 source altered pre/publication memory release boundary")
    require("AudioQueueDispose(" not in ctrl[failed:busy]
            and "free(owner_ctx)" not in ctrl[failed:busy],
            "R35 failed stop now contains unsafe cleanup")
    require("listener_remove_failed=1;" in ctrl[remove:dispose],
            "R35 listener failure evidence deleted")
    require("/* GEN-R26 candidate: diagnostic quiescence does not prove" in ctrl[clear:],
            "R35 no post-dispose lifetime caution")
    require("AudioQueueEnqueueBuffer(ctx->queue,buf,0,NULL)" in pcm
            and "/* GEN-R3: unconditional hard denial" in src,
            "R35 output pathway/queue proof sites drifted")
    require(len(FINDINGS)==12 and len(ANCHORS)==12 and len(PHASES)==13
            and len(API_EVIDENCE)==9
            and [x[0] for x in FINDINGS]==[x[0] for x in ANCHORS]
            and len({x[0] for x in FINDINGS})==12
            and len({x[0] for x in PHASES})==13
            and len({x[0] for x in API_EVIDENCE})==9,
            "R35 proof registry cardinality or ordering drift")
    for fid,site1,site2 in ANCHORS:
        for section,needle in (site1,site2):
            block={"callback":cb,"listener":listener,"controller":ctrl,"pcm":pcm}[section]
            require(needle in block,"R35 anchored finding disappeared: "+fid+" / "+needle)
    return {f[0]:"OPEN_NOT_PROVEN" for f in FINDINGS}

def inspect(root,override=None):
    root=Path(root).resolve()
    table,manifest=r17.manifest_integrity(root)
    require(len(table)==193,"R35 requires 193 SHA-pinned generator files")
    needed=(
        "audits/r35_pre_admission_os_contract_review.py",
        "tests/test_r35_pre_admission_os_contract_review.py",
        "RUN_GEN_R35_MAC_INTEL.command",
        "docs/GEN_R35_PRE_ADMISSION_REVIEW.md",
        "docs/GEN_R35_BUREAU_REVIEW.md",
        "docs/GEN_R35_APPLE_OS_CONTRACT_MATRIX.md",
    )
    require(all(x in table for x in needed),"R35 unpinned evidence file")
    historic=r34.inspect(root)
    require(historic[2]==table[CANDIDATE],
            "R35 C31 candidate differs from R34 witness")
    require(table[r26.ORIGINAL]==r19.PINNED_ACOUSTIC_SHA256,
            "R35 original C source differs from R19 witness")
    raw=(root/CANDIDATE).read_bytes()
    require(sha(raw)==table[CANDIDATE],"R35 candidate digest differs from manifest")
    proof=observe(raw.decode("utf-8") if override is None else override)
    runner=(root/"RUN_GEN_R35_MAC_INTEL.command").read_text(encoding="utf-8")
    require(set(r17.link_sources(runner))==r17.LINK_C_ALLOWLIST,
            "R35 executable link allowlist drifted")
    linked=runner.split(' -o "$WORK/freqmed-gen"')
    require(len(linked)==2,"R35 no-output executable link command missing")
    scope=linked[1].split("-framework CoreAudio",1)[0]
    require("output_hard_denied.c" in scope,"R35 executable output hard denial absent")
    for prohibited in ("acoustic_macos_r31.c","acoustic_macos_r29.c",
                       "acoustic_macos_r26.c","r28_callback_admission_gate.c",
                       "src/acoustic_macos.c"):
        require(prohibited not in scope,"R35 forbidden backend linked: "+prohibited)
    for token in (
       "R35_PRE_ADMISSION_OS_CONTRACT_REVIEW=PASS",
       "R35_R31_CANDIDATE_OBJECT=COMPILED_UNLINKED",
       "R35_NONEMITTING_EXECUTABLE_SYMBOL_AUDIT=PASS",
       "R35_BUREAU_API_DOSSIER=32_FILES_SHA256_PASS",
       "R35_TESTCASE_RUN_SLOT=PASS",
       "FREQMED_GEN_R35_EVIDENCE_DIR",
       "FREQMED_GEN_R35_BINARY",
    ):
        require(token in runner,"R35 runner marker absent: "+token)
    return table,manifest,sha(raw),proof

def anchor(src,section,needle,c_sha):
    start,_,body=r27.function_span(src,section)
    require(needle in body,"R35 source proof anchor disappeared: "+needle)
    at=start+body.index(needle)
    return {"path":CANDIDATE,"function":section,
            "line":src.count("\n",0,at)+1,
            "source_sha256":c_sha,"needle":needle}

def audit(root,archive_r19,paths):
    table,manifest,c_sha,proof=inspect(root)
    historic=r34.audit(root,archive_r19,paths)
    recorded=json.loads(Path(paths["r34"]).read_text(encoding="utf-8"))
    require(historic==recorded,"R35 historical R34 report does not match recalculation")
    require(historic["r34_findings_open"]==14
            and historic["r34_critical_open"]==4
            and historic["r33_findings_open"]==12
            and historic["r32_findings_open"]==10
            and historic["r31_findings_open"]==8
            and historic["r30_findings_open"]==12
            and historic["r29_findings_open"]==7
            and historic["r28_gates_open"]==5
            and historic["r27_findings_open"]==9
            and historic["r23_obligations_open"]==15
            and historic["r24_findings_open"]==7
            and historic["bureau_gates_open"]==11
            and historic["bureau_gates_resolved"]==0,
            "R35 inherited obligations were improperly promoted")
    source=(Path(root)/CANDIDATE).read_text(encoding="utf-8")
    issues=[]
    for (fid,severity,role,missing),(key,a,b) in zip(FINDINGS,ANCHORS):
        require(fid==key,"R35 findings/anchors out of order")
        issues.append({
         "id":fid,"severity":severity,"bureau_role":role,
         "status":proof[fid],"os_callback_executed":False,
         "source_anchors":[anchor(source,*a,c_sha),anchor(source,*b,c_sha)],
         "proof_missing":missing,"independent_approval":"NONE",
        })
    api=[{"id":name,"classification":grade,"url":url,
          "bounded_summary":summary,"review_date":"2026-11-16",
          "immutable_public_doc_snapshot":False,"OS_failure_proof":False}
         for name,grade,url,summary in API_EVIDENCE]
    return {
      "schema":SCHEMA,"verdict":VERDICT,
      "method":"SHA_PINNED_C_SOURCE_AND_PUBLIC_OS_API_DOCUMENTARY_REVIEW",
      "manifest_sha256":manifest,"pinned_generator_files":len(table),
      "candidate_r31_sha256":c_sha,"original_C_sha256":table[r26.ORIGINAL],
      "r34_report_sha256":sha(Path(paths["r34"]).read_bytes()),
      "r35_findings":issues,"r35_findings_open":12,
      "r35_critical_open":4,
      "r35_api_evidence":api,"r35_public_api_classifications":len(api),
      "r35_documentary_phases":[{"phase":a,"source_boundary":b,
          "independent_proof_required":c,"safe_to_free":False}
         for a,b,c in PHASES],
      "r35_documentary_phase_count":len(PHASES),
      "r35_actual_OS_callback_witnesses":0,
      "r35_C_source_edits":0,"r35_active_coreaudio":False,
      "r34_findings_open":14,"r34_critical_open":4,
      "r33_findings_open":12,"r33_critical_open":3,
      "r32_findings_open":10,"r32_critical_open":2,
      "r31_findings_open":8,"r31_critical_open":2,
      "r30_findings_open":12,"r30_critical_open":2,
      "r29_findings_open":7,"r28_gates_open":5,"r27_findings_open":9,
      "r23_obligations_open":15,"r24_findings_open":7,
      "bureau_gates_open":11,"bureau_gates_resolved":0,
      "userdata_pre_admission_lifetime":"NOT_PROVEN",
      "C11_race_freedom":"NOT_PROVEN",
      "CoreAudio_callback_quiescence":"NOT_PROVEN",
      "failed_AudioQueueStop":"NOT_TESTED",
      "failed_AudioQueueDispose":"NOT_TESTED",
      "physical_cutoff":"NOT_PROVEN",
      "independent_signatures":"NONE","bureau_certification":"PENDING",
      "limitations":list(LIMITATIONS),
      "scientific_simulation":"NONE","physical_emission":"NONE",
      "acoustic_output":"LOCKED","em_output":"LOCKED",
      "real_output":"NOT_AUTHORIZED",
      "biological_exposure":"NOT_AUTHORIZED","production":"NOT_AUTHORIZED",
    }

def markdown(result):
    rows=["| "+f["id"]+" | "+f["severity"]+" | "+f["bureau_role"]+
          " | OPEN_NOT_PROVEN |" for f in result["r35_findings"]]
    api=["| "+c["id"]+" | "+c["classification"]+" | "+c["url"]+" |"
         for c in result["r35_api_evidence"]]
    return ("# GEN-R35 — Pre-admission OS Contract Evidence Review\n\n"
      "**Verdict: PUBLIC_OS_CONTRACTS_CLASSIFIED_PRE_ADMISSION_LIFETIME_NOT_PROVEN.**\n\n"
      "Apple's successful immediate dispose contract is NOT a postcondition "
      "of a nonzero OSStatus. Source C11 closure is NOT proof of no late "
      "CoreAudio entry. No race or use-after-free was reproduced.\n\n"
      "| Finding | Severity | Bureau | Status |\n|---|---|---|---|\n"
      +"\n".join(rows)+"\n\n"
      "| API class | Evidence class | Original public Apple URL |\n|---|---|---|\n"
      +"\n".join(api)+"\n\n"
      "R35 12 OPEN, 4 CRITICAL; R34 14, R33 12, R32 10, R31 8, "
      "R30 12, R29 7, R28 5, R27 9, R23 15, R24 7, Bureau 11 "
      "OPEN, zero discharged. Public URLs are live, not immutable snapshots.\n\n"
      "NEVER_SIMULATION=ENFORCED; ZERO_COST_FOSS=ENFORCED; "
      "ACOUSTIC_OUTPUT=LOCKED; EM_OUTPUT=LOCKED; "
      "REAL_OUTPUT=NOT_AUTHORIZED; BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED; "
      "PRODUCTION=NOT_AUTHORIZED.\n")

def main():
    p=argparse.ArgumentParser(description="GEN-R35 source-only Apple OS userdata contract review")
    p.add_argument("--root",type=Path,required=True)
    p.add_argument("--archive-r19",type=Path,required=True)
    for n in range(16,35):
        p.add_argument("--r"+str(n),type=Path,required=True)
    p.add_argument("--json",type=Path,required=True)
    p.add_argument("--markdown",type=Path,required=True)
    args=p.parse_args()
    try:
        paths={"r"+str(n):getattr(args,"r"+str(n)) for n in range(16,35)}
        report=audit(args.root,args.archive_r19,paths)
        args.json.write_text(json.dumps(report,sort_keys=True,
          indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
        args.markdown.write_text(markdown(report),encoding="utf-8")
    except (R35Error,r34.R34Error,r33.R33Error,r32.R32Error,r31.R31Error,
            r30.R30Error,r29.R29Error,r28.R28Error,r27.R27Error,
            r26.R26Error,ValueError,TypeError,KeyError,IndexError,
            OSError,UnicodeError) as e:
        print("R35_PRE_ADMISSION_OS_CONTRACT_REVIEW=FAIL_CLOSED",str(e))
        return 2
    print("R35_PRE_ADMISSION_OS_CONTRACT_REVIEW=PASS")
    print("R35_FINDINGS=12_OPEN; R35_CRITICAL=4_OPEN")
    print("R35_PUBLIC_API_CLASSIFICATIONS=9; R35_DOCUMENTARY_PHASES=13")
    print("R35_R34_FINDINGS=14_OPEN; R35_R33_FINDINGS=12_OPEN")
    print("R35_R32_FINDINGS=10_OPEN; R35_R31_FINDINGS=8_OPEN")
    print("R35_BUREAU_GATES=11_OPEN; R35_BUREAU_RESOLVED=0")
    print("R35_REVIEW_VERDICT="+VERDICT)
    print("R35_PRE_ADMISSION_LIFETIME=NOT_PROVEN")
    print("R35_OS_CALLBACK_QUIESCENCE=NOT_PROVEN; R35_C11_RACE_FREEDOM=NOT_PROVEN")
    print("R35_PHYSICAL_CUTOFF=NOT_PROVEN; R35_ACTUAL_OS_CALLBACKS=0")
    print("R35_PHYSICAL_EMISSION=NONE; R35_SCIENTIFIC_SIMULATION=NONE")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
