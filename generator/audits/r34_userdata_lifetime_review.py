#!/usr/bin/env python3
"""GEN-R34: independent CoreAudio callback userdata lifetime and OS ownership
source review. Never calls AudioQueue APIs, runs callbacks or emits signals.
Text-source evidence is not a formal C11 proof or a measured OS contract.
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

SCHEMA="FREQMED_GEN_R34_USERDATA_LIFETIME_AND_OS_OWNERSHIP"
VERDICT="USERDATA_LIFETIME_OBLIGATIONS_MAPPED_OS_C11_PROOF_OPEN"
CANDIDATE=r31.CANDIDATE
APPLE_DOCS=(
 "https://developer.apple.com/documentation/audiotoolbox/audioqueuedispose%28_%3A_%3A%29",
 "https://developer.apple.com/documentation/audiotoolbox/audioqueuestop%28_%3A_%3A%29",
 "https://developer.apple.com/documentation/audiotoolbox/audioqueueremovepropertylistener%28_%3A_%3A_%3A_%3A%29",
)
# Each finding is an obligation; NONE is a reproduced race or safety PASS.
FINDINGS=(
 ("UD34_01_CALLBACK_USERDATA_BEFORE_GATE","CRITICAL","B07",
  "The callback must read the heap ctx to access its atomic admission gate. Establish an OS lifetime guarantee BEFORE that read."),
 ("UD34_02_LISTENER_USERDATA_BEFORE_GATE","CRITICAL","B07",
  "The property listener also dereferences userdata before admission. Prove no late entry uses a reclaimed pointer."),
 ("UD34_03_FAILED_STOP_PHYSICAL_ACTIVITY","CRITICAL","B10",
  "An AudioQueueStop error does not prove physical silence or callback completion. Hardware output must remain unauthorized."),
 ("UD34_04_FAILED_DISPOSE_RESOURCE_OWNERSHIP","CRITICAL","B07",
  "Prove queue/userdata ownership after AudioQueueDispose failure before any release, retry or process exit decision."),
 ("UD34_05_NEWOUTPUT_PARTIAL_PUBLICATION","HIGH","B07",
  "Qualify whether AudioQueueNewOutput failure can still have published callbacks or retained userdata."),
 ("UD34_06_LISTENER_REGISTER_FAILURE","HIGH","B07",
  "A failed listener registration is not proof of zero callbacks or safe destruction of its user data."),
 ("UD34_07_ROUTE_REJECT_SYNCHRONOUS_DISPOSE","HIGH","B07",
  "Distinguish a successful immediate disposal contract from the unproven handling of concurrent/previous callbacks."),
 ("UD34_08_CLOSE_AND_EMPTY_NOT_OS_QUIESCENCE","HIGH","B09",
  "The C11 gate only covers admitted callbacks; OS can enter a callback before its first atomic access."),
 ("UD34_09_ACTIVE_COUNTER_STARTS_AFTER_GATE","HIGH","B09",
  "Both active callback counters are incremented AFTER admission and cannot count attempts still before the gate."),
 ("UD34_10_LISTENER_REMOVE_FAILED","HIGH","B07",
  "Prove postconditions for OSStatus failure removing listener and any already-running listener."),
 ("UD34_11_DISPOSE_SUCCESS_RESOURCE_CLAIM","HIGH","B07",
  "Apple documents synchronous immediate disposal and no further callbacks after disposal; separately qualify C11 HB, already entered callbacks and errors."),
 ("UD34_12_QUEUE_REF_C11_LIFETIME","HIGH","B09",
  "Prove the controller's non-atomic ctx->queue clear is ordered after all callback uses and external queue references."),
 ("UD34_13_PCM_REENTRANCE_AND_STOP","HIGH","B09",
  "Prove that callback enqueue under pcm_writer_gate is safe against stop, reentrancy and realtime scheduling."),
 ("UD34_14_RETAIN_NOT_BOUNDED_OR_PHYSICAL_STOP","HIGH","B10",
  "Retaining context until process exit prevents some premature frees but does not bound OS resources or establish hardware cutoff."),
)
# Function names use the verified r29.function / r27.function_span helpers.
ANCHORS=(
 ("UD34_01_CALLBACK_USERDATA_BEFORE_GATE",
  ("callback","AcousticContext *ctx=(AcousticContext*)ptr;"),
  ("callback","if (!fm_r28_gate_try_enter(&ctx->queue_admission)) return;")),
 ("UD34_02_LISTENER_USERDATA_BEFORE_GATE",
  ("listener","AcousticContext *ctx=(AcousticContext*)data;"),
  ("listener","if (!fm_r28_gate_try_enter(&ctx->queue_admission)) return;")),
 ("UD34_03_FAILED_STOP_PHYSICAL_ACTIVITY",
  ("controller","const OSStatus r31_immediate_stop_status=AudioQueueStop(ctx->queue,true);"),
  ("controller","if (r31_immediate_stop_status!=noErr) {")),
 ("UD34_04_FAILED_DISPOSE_RESOURCE_OWNERSHIP",
  ("controller","if (AudioQueueDispose(ctx->queue,true)!=noErr) {"),
  ("controller","fm_latch_first_fault(ctx,FM_FAULT_DISPOSAL);")),
 ("UD34_05_NEWOUTPUT_PARTIAL_PUBLICATION",
  ("controller","AudioQueueNewOutput(&fmt,output_callback,ctx,NULL,NULL,0,&ctx->queue)"),
  ("controller","fm_r28_gate_close(&ctx->queue_admission);")),
 ("UD34_06_LISTENER_REGISTER_FAILURE",
  ("controller","AudioQueueAddPropertyListener(ctx->queue,kAudioQueueProperty_IsRunning,"),
  ("controller","listener_registration_uncertain=1;")),
 ("UD34_07_ROUTE_REJECT_SYNCHRONOUS_DISPOSE",
  ("controller","const OSStatus bind_dispose_status=AudioQueueDispose(ctx->queue,true);"),
  ("controller","if (bind_dispose_status==noErr) {")),
 ("UD34_08_CLOSE_AND_EMPTY_NOT_OS_QUIESCENCE",
  ("controller","fm_r28_gate_closed_and_empty(&ctx->queue_admission)"),
  ("callback","if (!fm_r28_gate_try_enter(&ctx->queue_admission)) return;")),
 ("UD34_09_ACTIVE_COUNTER_STARTS_AFTER_GATE",
  ("callback","atomic_fetch_add_explicit(&ctx->active_output_callbacks,1U,"),
  ("listener","atomic_fetch_add_explicit(&ctx->active_property_listeners,1U,")),
 ("UD34_10_LISTENER_REMOVE_FAILED",
  ("controller","AudioQueueRemovePropertyListener(ctx->queue,"),
  ("controller","listener_remove_failed=1;")),
 ("UD34_11_DISPOSE_SUCCESS_RESOURCE_CLAIM",
  ("controller","atomic_store(&ctx->dispose_confirmed,1);"),
  ("controller","ctx->queue=NULL;")),
 ("UD34_12_QUEUE_REF_C11_LIFETIME",
  ("pcm","AudioQueueEnqueueBuffer(ctx->queue,buf,0,NULL)"),
  ("controller","ctx->queue=NULL;")),
 ("UD34_13_PCM_REENTRANCE_AND_STOP",
  ("callback","atomic_flag_test_and_set_explicit(&ctx->pcm_writer_gate,"),
  ("pcm","AudioQueueEnqueueBuffer(ctx->queue,buf,0,NULL)")),
 ("UD34_14_RETAIN_NOT_BOUNDED_OR_PHYSICAL_STOP",
  ("controller","/* GEN-R26 candidate: diagnostic quiescence does not prove"),
  ("controller","atomic_store_explicit(&fm_context_quarantined,1,memory_order_release);")),
)
# Documentary witness/phase table, NOT an executable state machine.
PHASES=(
 ("BEFORE_PUBLISH","C_ONLY","No callback registration to OS yet",
  "Source path may release heap before NewOutput; complete proof still needed"),
 ("NEWOUTPUT_PUBLICATION","OS_MAY_HOLD_USERDATA","NewOutput receives ctx as userdata",
  "Heap remains retained on creation error; no OS failure guarantee inferred"),
 ("CALLBACK_ENTER_PRE_ADMISSION","OS_CALLBACK_UNCOUNTED","ptr/data converted into ctx before gate",
  "Cannot free ctx merely because gate is closed/empty"),
 ("ADMITTED_CALLBACK","C11_GATE_LEASE","Try-enter accepted; counter increments afterward",
  "Require C11 HB and per-path enter/leave pairing"),
 ("REJECTED_CALLBACK","OS_CALLBACK_UNCOUNTED","Try-enter rejects via ctx atomic gate",
  "Reading gate still assumes valid ctx memory"),
 ("SHUTDOWN_CLOSE","C11_GATE_CLOSED","Controller calls close and reads empty",
  "C11 closure does not establish no OS entry"),
 ("STOP_ERROR","OS_QUEUE_POSSIBLY_ACTIVE","Immediate stop OSStatus nonzero",
  "No free/dispose; physical stop NOT_PROVEN"),
 ("LISTENER_REMOVE_ERROR","OS_LISTENER_UNCERTAIN","Removal OSStatus nonzero",
  "No inference of callback quiescence"),
 ("DISPOSE_ERROR","OS_QUEUE_UNDETERMINED","Dispose OSStatus nonzero",
  "No free/retry; queue reference may be invalid or live"),
 ("DISPOSE_SUCCESS","OS_DISPOSE_SUCCEEDED","Immediate dispose OSStatus noErr",
  "Apple reports no further callbacks after disposal, but check entered callbacks and C11 HB before reclamation"),
 ("PROCESS_QUARANTINE","C_HEAP_RETAINED","Process denies new sessions",
  "Retaining memory does NOT establish hardware cutoff"),
)
LIMITATIONS=(
 "SOURCE_ORDERS_AND_API_TEXT_NOT_FORMAL_CONCURRENCY_PROOF",
 "NO_OS_CALLBACK_ENTRY_OR_LATE_DISPATCH_EXECUTED",
 "NO_ACTUAL_COREAUDIO_STOP_DISPOSE_ERRORS_INDUCED",
 "NO_PHYSICAL_ACOUSTIC_EMISSION_OR_MEASUREMENT",
 "NO_SCIENTIFIC_SIMULATION_OR_SYNTHETIC_INTERLEAVINGS",
 "NO_EXTERNAL_OS_C11_CERTIFICATION_SIGNATURE",
)
class R34Error(ValueError):
    pass

def require(condition,reason):
    if not condition:
        raise R34Error(reason)

def sha(data):
    return hashlib.sha256(data).hexdigest()

def position(source,needle,start=0):
    require(needle in source[start:],"R34 source obligation anchor missing: "+needle)
    return source.index(needle,start)

def block(source,which):
    try:
        return r29.function(source,which)
    except (ValueError,KeyError,IndexError) as exc:
        raise R34Error("R34 function envelope missing: "+which) from exc

def observe(source):
    require(source.startswith("/* SPDX-License-Identifier: Apache-2.0 */"),
            "R34 C source license/header changed")
    callback=block(source,"callback")
    listener=block(source,"listener")
    ctrl=block(source,"controller")
    pcm=block(source,"pcm")
    # The userdata conversion is not itself a dereference; the first ctx->gate
    # expression IS, and needs prior lifetime evidence. Do not assert UAF.
    for part,entry in ((callback,"AcousticContext *ctx=(AcousticContext*)ptr;"),
                       (listener,"AcousticContext *ctx=(AcousticContext*)data;")):
        convert=position(part,entry)
        checknull=position(part,"if (!ctx) return;",convert)
        gate=position(part,"if (!fm_r28_gate_try_enter(&ctx->queue_admission)) return;",checknull)
        counter=position(part,"atomic_fetch_add_explicit(&ctx->active_",gate)
        exitcounter=position(part,"atomic_fetch_sub_explicit(&ctx->active_",counter)
        leave=position(part,"fm_r28_gate_leave(&ctx->queue_admission);",exitcounter)
        require(convert<checknull<gate<counter<exitcounter<leave,
                "R34 callback/listener userdata entry-order drift")
        require(part.count("fm_r28_gate_try_enter(&ctx->queue_admission)")==1
                and part.count("fm_r28_gate_leave(&ctx->queue_admission);")==1,
                "R34 callback/listener admission site count drift")
    # Only the exact observable lexical scope is checked.
    init=position(ctrl,"fm_r28_gate_init(&ctx->queue_admission);")
    publish=position(ctrl,"AudioQueueNewOutput(&fmt,output_callback,ctx,NULL,NULL,0,&ctx->queue)")
    add_listener=position(ctrl,"AudioQueueAddPropertyListener(ctx->queue,kAudioQueueProperty_IsRunning,")
    close=position(ctrl,"fm_r28_gate_close(&ctx->queue_admission);",add_listener)
    stop=position(ctrl,"const OSStatus r31_immediate_stop_status=AudioQueueStop(ctx->queue,true);",close)
    stop_failed=position(ctrl,"if (r31_immediate_stop_status!=noErr) {",stop)
    busy=position(ctrl,"if (r31_admission_busy) {",stop_failed)
    remove=position(ctrl,"AudioQueueRemovePropertyListener(ctx->queue,",busy)
    dispose=position(ctrl,"if (AudioQueueDispose(ctx->queue,true)!=noErr) {",remove)
    flag=position(ctrl,"atomic_store(&ctx->dispose_confirmed,1);",dispose)
    clear=position(ctrl,"ctx->queue=NULL;",flag)
    keep=position(ctrl,"/* GEN-R26 candidate: diagnostic quiescence does not prove",clear)
    require(init<publish<add_listener<close<stop<stop_failed<busy<remove<dispose<flag<clear<keep,
            "R34 publication/shutdown/retention order changed")
    require(ctrl[:publish].count("free(owner_ctx);")==2 and
            ctrl[publish:].count("free(owner_ctx);")==0,
            "R34 post-publication userdata free added or prepublication contract shifted")
    require("return -1;" in ctrl[stop_failed:busy] and
            "AudioQueueDispose(" not in ctrl[stop_failed:busy] and
            "free(owner_ctx)" not in ctrl[stop_failed:busy],
            "R34 failed-stop branch now touches unsafe cleanup")
    require("return -1;" in ctrl[busy:remove] and
            "AudioQueueDispose(" not in ctrl[busy:remove],
            "R34 active-lease failure branch changed")
    require("listener_remove_failed=1;" in ctrl[remove:dispose] and
            "fm_latch_first_fault(ctx,FM_FAULT_LISTENER_REMOVAL);" in ctrl[remove:dispose],
            "R34 listener removal uncertainty lost")
    require("fm_latch_first_fault(ctx,FM_FAULT_DISPOSAL);" in ctrl[dispose:flag],
            "R34 disposal failure no longer latches fault")
    require("AudioQueueEnqueueBuffer(ctx->queue,buf,0,NULL)" in pcm
            and "/* GEN-R3: unconditional hard denial" in source,
            "R34 legacy queue use or public hard denial changed")
    require(len(FINDINGS)==14 and len(ANCHORS)==14
            and len(PHASES)==11
            and len({x[0] for x in FINDINGS})==14
            and len({x[0] for x in PHASES})==11
            and [a[0] for a in ANCHORS]==[x[0] for x in FINDINGS],
            "R34 finding/phase ID list changed")
    for name,one,two in ANCHORS:
        for section,needle in (one,two):
            require(needle in {"callback":callback,"listener":listener,
                "controller":ctrl,"pcm":pcm}[section],
                "R34 pinned source anchor absent: "+name+" / "+needle)
    return {x[0]:"OPEN_NOT_PROVEN" for x in FINDINGS}

def inspect(root,override=None):
    root=Path(root).resolve()
    table,manifest=r17.manifest_integrity(root)
    require(len(table)>=187,"R34 historical review needs at least 187 SHA-pinned generator files")
    files=(
     "audits/r34_userdata_lifetime_review.py",
     "tests/test_r34_userdata_lifetime_review.py",
     "RUN_GEN_R34_MAC_INTEL.command",
     "docs/GEN_R34_USERDATA_LIFETIME.md",
     "docs/GEN_R34_BUREAU_REVIEW.md",
     "docs/GEN_R34_OS_PROOF_WITNESSES.md",
    )
    require(all(p in table for p in files),"R34 dossier files missing from hash manifest")
    old=r33.inspect(root)
    require(old[2]==table[CANDIDATE],
            "R34 inherited R31 C candidate hash changed")
    require(table[r26.ORIGINAL]==r19.PINNED_ACOUSTIC_SHA256,
            "R34 original C backend changed")
    raw=(root/CANDIDATE).read_bytes()
    require(sha(raw)==table[CANDIDATE],"R34 R31 C source SHA mismatch")
    checks=observe(raw.decode("utf-8") if override is None else override)
    runner=(root/"RUN_GEN_R34_MAC_INTEL.command").read_text(encoding="utf-8")
    require(set(r17.link_sources(runner))==r17.LINK_C_ALLOWLIST,
            "R34 executable C link allowlist changed")
    parts=runner.split(' -o "$WORK/freqmed-gen"')
    require(len(parts)==2,"R34 no-output executable link boundary changed")
    linked=parts[1].split("-framework CoreAudio",1)[0]
    require("output_hard_denied.c" in linked,
            "R34 hard-denial output implementation not linked")
    for unsafe in ("acoustic_macos_r31.c","acoustic_macos_r29.c",
                   "acoustic_macos_r26.c","r28_callback_admission_gate.c",
                   "src/acoustic_macos.c"):
        require(unsafe not in linked,"R34 actual executable links forbidden source "+unsafe)
    for marker in (
       "R34_USERDATA_LIFETIME_REVIEW=PASS",
       "R34_R31_CANDIDATE_OBJECT=COMPILED_UNLINKED",
       "R34_NONEMITTING_EXECUTABLE_SYMBOL_AUDIT=PASS",
       "R34_BUREAU_PROOF_DOSSIER=30_FILES_SHA256_PASS",
       "R34_TESTCASE_RUN_SLOT=PASS",
       "FREQMED_GEN_R34_EVIDENCE_DIR",
       "FREQMED_GEN_R34_BINARY",
    ):
        require(marker in runner,"R34 required no-output runner marker missing: "+marker)
    return table,manifest,sha(raw),checks

def proof_anchor(source,section,needle,csha):
    start,_,function=r27.function_span(source,section)
    require(needle in function,"R34 review anchor disappeared: "+needle)
    pos=start+function.index(needle)
    return {"path":CANDIDATE,"function":section,
            "source_line":source.count("\n",0,pos)+1,
            "source_sha256":csha,"text":needle}

def audit(root,archive_r19,paths):
    table,manifest,csha,checks=inspect(root)
    prior=r33.audit(root,archive_r19,paths)
    observed=json.loads(Path(paths["r33"]).read_text(encoding="utf-8"))
    require(prior==observed,
            "R34 historical R33 report does not match independently recomputed evidence")
    require(prior["r33_findings_open"]==12 and prior["r33_critical_open"]==3
            and prior["r32_findings_open"]==10
            and prior["r31_findings_open"]==8
            and prior["r30_findings_open"]==12
            and prior["r29_findings_open"]==7
            and prior["r28_gates_open"]==5
            and prior["r27_findings_open"]==9
            and prior["r23_obligations_open"]==15
            and prior["r24_findings_open"]==7
            and prior["bureau_gates_open"]==11
            and prior["bureau_gates_resolved"]==0,
            "R34 historical safety obligations unexpectedly discharged")
    src=(Path(root)/CANDIDATE).read_text(encoding="utf-8")
    ledger=[]
    for finding,anchors in zip(FINDINGS,ANCHORS):
        fid,severity,role,proof=finding
        require(fid==anchors[0],"R34 mismatch in finding/source ledger")
        ledger.append({
         "id":fid,"severity":severity,"bureau_role":role,
         "status":checks[fid],"actual_os_callback_witness":False,
         "c11_race_reproduced":False,"independent_approval":"NONE",
         "anchors":[proof_anchor(src,*anchors[1],csha),
                    proof_anchor(src,*anchors[2],csha)],
         "independent_proof_required":proof})
    phases=[{"phase":name,"owner":owner,
             "source_observation":observation,"proof_boundary":boundary,
             "safe_free_proven":False}
            for name,owner,observation,boundary in PHASES]
    return {
      "schema":SCHEMA,"verdict":VERDICT,
      "method":"SOURCE_ONLY_SHA_PINNED_USERDATA_OWNERSHIP_CONTRACT",
      "manifest_sha256":manifest,"pinned_generator_files":len(table),
      "r31_candidate_sha256":csha,"original_C_sha256":table[r26.ORIGINAL],
      "r33_report_sha256":sha(Path(paths["r33"]).read_bytes()),
      "r34_findings":ledger,"r34_findings_open":14,
      "r34_critical_open":4,"r34_documentary_phases":len(phases),
      "r34_lifetime_phases":phases,
      "r34_source_C_edits":0,"r34_active_coreaudio":False,
      "r33_findings_open":12,"r33_critical_open":3,
      "r32_findings_open":10,"r32_critical_open":2,
      "r31_findings_open":8,"r31_critical_open":2,
      "r30_findings_open":12,"r30_critical_open":2,
      "r29_findings_open":7,"r28_gates_open":5,"r27_findings_open":9,
      "r23_obligations_open":15,"r24_findings_open":7,
      "bureau_gates_open":11,"bureau_gates_resolved":0,
      "C11_race_freedom":"NOT_PROVEN",
      "CoreAudio_callback_quiescence":"NOT_PROVEN",
      "userdata_lifetime":"NOT_PROVEN",
      "failed_AudioQueueStop":"NOT_TESTED",
      "failed_AudioQueueDispose":"NOT_TESTED",
      "physical_output_cutoff":"NOT_PROVEN",
      "independent_signatures":"NONE","bureau_certification":"PENDING",
      "apple_docs":list(APPLE_DOCS),
      "limitations":list(LIMITATIONS),
      "scientific_simulation":"NONE","physical_emission":"NONE",
      "acoustic_output":"LOCKED","em_output":"LOCKED",
      "real_output":"NOT_AUTHORIZED",
      "biological_exposure":"NOT_AUTHORIZED","production":"NOT_AUTHORIZED",
    }

def markdown(result):
    rows=["| "+f["id"]+" | "+f["severity"]+" | "+f["bureau_role"]+
          " | OPEN_NOT_PROVEN |" for f in result["r34_findings"]]
    phases=["| "+x["phase"]+" | "+x["owner"]+" | "+x["proof_boundary"]+" |"
            for x in result["r34_lifetime_phases"]]
    return (
      "# FREQMED GEN-R34 — Userdata Lifetime and OS Ownership Proof Review\n\n"
      "**Verdict: USERDATA_LIFETIME_OBLIGATIONS_MAPPED_OS_C11_PROOF_OPEN.**\n\n"
      "The first ctx->queue_admission read requires a VALID ctx. A closed "
      "atomic gate or zero counter is NOT proof that the OS cannot still "
      "enter with stale userdata. No actual UAF was observed.\n\n"
      "| Finding | Severity | Bureau | Status |\n|---|---|---|---|\n"
      +"\n".join(rows)+"\n\n"
      "| Source phase | Owner | Remaining proof |\n|---|---|---|\n"
      +"\n".join(phases)+"\n\n"
      "R34=14 OPEN (4 CRITICAL), R33=12 OPEN (3 CRITICAL), R32=10 OPEN "
      "(2 CRITICAL), R31=8, R30=12, R29=7, R28=5, R27=9, R23=15, "
      "R24=7 and Bureau=11 OPEN. This is a source review, not an executed "
      "OS proof, scientific simulation or physical emission.\n\n"
      "NEVER_SIMULATION=ENFORCED; ZERO_COST_FOSS=ENFORCED; "
      "ACOUSTIC_OUTPUT=LOCKED; EM_OUTPUT=LOCKED; "
      "REAL_OUTPUT=NOT_AUTHORIZED; BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED; "
      "PRODUCTION=NOT_AUTHORIZED.\n")

def main():
    p=argparse.ArgumentParser(description="GEN-R34 static userdata lifetime review")
    p.add_argument("--root",required=True,type=Path)
    p.add_argument("--archive-r19",required=True,type=Path)
    for n in range(16,34):
        p.add_argument("--r"+str(n),required=True,type=Path)
    p.add_argument("--json",required=True,type=Path)
    p.add_argument("--markdown",required=True,type=Path)
    a=p.parse_args()
    try:
        paths={"r"+str(n):getattr(a,"r"+str(n)) for n in range(16,34)}
        result=audit(a.root,a.archive_r19,paths)
        a.json.write_text(json.dumps(result,sort_keys=True,
                          indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
        a.markdown.write_text(markdown(result),encoding="utf-8")
    except (R34Error,r33.R33Error,r32.R32Error,r31.R31Error,r30.R30Error,
            r29.R29Error,r28.R28Error,r27.R27Error,r26.R26Error,
            ValueError,TypeError,KeyError,IndexError,OSError,UnicodeError) as exc:
        print("R34_USERDATA_LIFETIME_REVIEW=FAIL_CLOSED",str(exc))
        return 2
    print("R34_USERDATA_LIFETIME_REVIEW=PASS")
    print("R34_FINDINGS=14_OPEN; R34_CRITICAL=4_OPEN")
    print("R34_LIFETIME_PHASES=11_DOCUMENTARY; R34_OS_CALLBACK_WITNESSES=0")
    print("R34_R33_FINDINGS=12_OPEN; R34_R32_FINDINGS=10_OPEN")
    print("R34_R31_FINDINGS=8_OPEN; R34_R30_FINDINGS=12_OPEN")
    print("R34_R23_OBLIGATIONS=15_OPEN; R34_R24_FINDINGS=7_OPEN")
    print("R34_BUREAU_GATES=11_OPEN; R34_BUREAU_RESOLVED=0")
    print("R34_REVIEW_VERDICT="+VERDICT)
    print("R34_USERDATA_LIFETIME=NOT_PROVEN; R34_CALLBACK_QUIESCENCE=NOT_PROVEN")
    print("R34_C11_RACE_FREEDOM=NOT_PROVEN; R34_PHYSICAL_CUTOFF=NOT_PROVEN")
    print("R34_PHYSICAL_EMISSION=NONE; R34_SCIENTIFIC_SIMULATION=NONE")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
