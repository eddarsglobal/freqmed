#!/usr/bin/env python3
"""GEN-R30 independent CoreAudio OS-quiescence and C11 queue-lifetime audit.
Exact, SHA-pinned SOURCE ONLY. No callbacks, OS API calls, synthetic signals,
scientific simulations, active CoreAudio, hardware output or formal race proof.
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

SCHEMA="FREQMED_GEN_R30_COREAUDIO_CALLBACK_QUIESCENCE_ADVERSARIAL_REVIEW"
VERDICT="ADVERSARIAL_COREAUDIO_LIFETIME_GAPS_CONFIRMED_UNCERTIFIED"
CANDIDATE=r29.CANDIDATE
# id, severity, bureau role, evidence needed. A race is NEVER claimed observed.
FINDINGS=(
 ("Q30_01_USERDATA_BEFORE_ATOMIC_ADMISSION","HIGH","B07",
  "Show from OS API contracts that all callback and listener userdata remains valid before try_enter, even for OS entries after close/removal."),
 ("Q30_02_LIVE_QUEUE_EARLY_EXIT","CRITICAL","B10",
  "Prove a safe independent stop and control transfer on the closed-but-nonempty path AFTER AudioQueueStart; current early return can skip Stop/Dispose."),
 ("Q30_03_CONTROLLER_STOP_WITHOUT_LEASE","HIGH","B09",
  "Prove exclusive controller ownership and happens-before across drain/stop and all callback queue use; controller uses AudioQueueRef without admission lease."),
 ("Q30_04_PREFILL_VS_CALLBACK_LEASE_COVERAGE","HIGH","B09",
  "Show that all controller prefill, allocation, start and route operations are synchronized with admitted callbacks, not only pcm_writer_gate."),
 ("Q30_05_ENQUEUE_UNDER_PCM_GATE","HIGH","B09",
  "Qualify actual AudioQueueEnqueueBuffer dispatch/reentrance and bounded time in PCM section with documented OS behavior."),
 ("Q30_06_CLOSE_EMPTY_OS_ADMISSION_GAP","HIGH","B07",
  "C11 closed-and-empty does not rule out late OS dispatch entering userdata; obtain OS quiescence contract and lifetime protocol."),
 ("Q30_07_DISPOSE_SUCCESS_QUEUE_CLEAR","HIGH","B09",
  "Prove all callback references to non-atomic ctx->queue are completed and ordered before successful OS disposal and ctx->queue=NULL."),
 ("Q30_08_LISTENER_REMOVE_FAILURE_STILL_DISPOSES","HIGH","B07",
  "Review remove-property-listener OSStatus failure followed by unconditional disposal, including in-flight listener ownership and quarantine."),
 ("Q30_09_DISPOSE_FAILURE_RETAINS_OS_OWNERSHIP","HIGH","B07",
  "Qualify failed AudioQueueDispose OSStatus and resource ownership; retaining userdata alone does not guarantee a valid queue reference or non-emission."),
 ("Q30_10_QUEUE_CREATION_FAILURE_UNKNOWN_PUBLICATION","HIGH","B07",
  "Analyze partial AudioQueueNewOutput failure and whether asynchronous callbacks or queue allocations can remain reachable despite API error."),
 ("Q30_11_LEASE_PAIRING_AND_LOCKFREE","HIGH","B09",
  "Formalize every try_enter/leave path, C11 release sequence and atomic lock-free timing on target architecture; lexical checks cannot certify."),
 ("Q30_12_QUARANTINE_NOT_HARDWARE_STOP","CRITICAL","B10",
  "A software process quarantine does not stop running hardware; demonstrate a hardware-safe stop/failure strategy before any future physical activation."),
)
LIMITATIONS=(
 "LEXICAL_FUNCTION_BOUNDARY_AND_ORDER_CHECKS_NOT_FULL_C11_AST",
 "SOURCE_FINDING_NOT_RACE_REPRODUCTION_OR_HAPPENS_BEFORE_PROOF",
 "NO_ACTUAL_COREAUDIO_CALLBACK_DISPATCH_STOP_OR_DISPOSE",
 "NO_FACILITY_TO_INFER_OSSTATUS_FAILURE_POSTCONDITIONS",
 "NO_SCIENTIFIC_SIMULATION_SYNTHETIC_SIGNAL_OR_PHYSICAL_OUTPUT",
 "NO_INDEPENDENT_BUREAU_SIGNATURE",
)

# Source anchors: two concrete sites each; OS-specific obligations remain OPEN.
ANCHORS=(
 ("Q30_01_USERDATA_BEFORE_ATOMIC_ADMISSION",
  ("callback","AcousticContext *ctx=(AcousticContext*)ptr;"),
  ("callback","if (!fm_r28_gate_try_enter(&ctx->queue_admission)) return;")),
 ("Q30_02_LIVE_QUEUE_EARLY_EXIT",
  ("controller","if (!err && AudioQueueStart(ctx->queue,NULL)!=noErr) err=1;"),
  ("controller","return -1;\n  }\n  if (ctx->queue) {")),
 ("Q30_03_CONTROLLER_STOP_WITHOUT_LEASE",
  ("controller","request_graceful_queue_drain(ctx);"),
  ("controller","AudioQueueStop(ctx->queue,true)")),
 ("Q30_04_PREFILL_VS_CALLBACK_LEASE_COVERAGE",
  ("controller","AudioQueueAllocateBuffer(ctx->queue,1024U,&b)"),
  ("callback","if (!fm_r28_gate_try_enter(&ctx->queue_admission)) return;")),
 ("Q30_05_ENQUEUE_UNDER_PCM_GATE",
  ("pcm","AudioQueueEnqueueBuffer(ctx->queue,buf,0,NULL)"),
  ("callback","atomic_flag_test_and_set_explicit(&ctx->pcm_writer_gate,")),
 ("Q30_06_CLOSE_EMPTY_OS_ADMISSION_GAP",
  ("controller","fm_r28_gate_close(&ctx->queue_admission);"),
  ("listener","if (!fm_r28_gate_try_enter(&ctx->queue_admission)) return;")),
 ("Q30_07_DISPOSE_SUCCESS_QUEUE_CLEAR",
  ("pcm","AudioQueueEnqueueBuffer(ctx->queue,buf,0,NULL)"),
  ("controller","ctx->queue=NULL;")),
 ("Q30_08_LISTENER_REMOVE_FAILURE_STILL_DISPOSES",
  ("controller","AudioQueueRemovePropertyListener(ctx->queue,"),
  ("controller","if (AudioQueueDispose(ctx->queue,true)!=noErr)")),
 ("Q30_09_DISPOSE_FAILURE_RETAINS_OS_OWNERSHIP",
  ("controller","fm_latch_first_fault(ctx,FM_FAULT_DISPOSAL);"),
  ("controller","ctx->queue=NULL;")),
 ("Q30_10_QUEUE_CREATION_FAILURE_UNKNOWN_PUBLICATION",
  ("controller","if (AudioQueueNewOutput(&fmt,output_callback,ctx,NULL,NULL,0,&ctx->queue)!=noErr)"),
  ("controller","fm_r28_gate_close(&ctx->queue_admission);")),
 ("Q30_11_LEASE_PAIRING_AND_LOCKFREE",
  ("listener","fm_r28_gate_leave(&ctx->queue_admission);"),
  ("callback","fm_r28_gate_leave(&ctx->queue_admission);")),
 ("Q30_12_QUARANTINE_NOT_HARDWARE_STOP",
  ("controller","atomic_store_explicit(&fm_context_quarantined,1,memory_order_release);"),
  ("controller","/* Seal admission before OS cleanup.")),
)
class R30Error(ValueError): pass
def require(ok,reason):
    if not ok: raise R30Error(reason)
def digest(data): return hashlib.sha256(data).hexdigest()
def fn(source,name): return r29.function(source,name)
def _once(s,needle,context):
    require(s.count(needle)>=1,"R30 anchor missing "+context+": "+needle)

def observe(source):
    """Strict bounded source invariants. No proof of OS/C11 safety is implied."""
    require(source.startswith("/* SPDX-License-Identifier: Apache-2.0 */"),
            "R30 C header/license changed")
    ctrl=fn(source,"controller")
    callback=fn(source,"callback")
    listener=fn(source,"listener")
    pcm=fn(source,"pcm")
    # Pairing still needs independent proof; inspect source structure only.
    require(source.count("fm_r28_gate_try_enter(&ctx->queue_admission)")==2,
            "R30 callback admission-site drift")
    require(source.count("fm_r28_gate_leave(&ctx->queue_admission);")==2,
            "R30 callback leave-site drift")
    require(ctrl.count("fm_r28_gate_close(&ctx->queue_admission);")==3,
            "R30 controller close-site drift")
    require(ctrl.count("if (!fm_r28_gate_closed_and_empty(&ctx->queue_admission))")==2,
            "R30 closed-and-empty branch drift")
    require("if (!ctx) return;" in callback and
            callback.index("if (!ctx) return;") <
            callback.index("if (!fm_r28_gate_try_enter(") <
            callback.index("fm_r28_gate_leave(&ctx->queue_admission);"),
            "R30 callback userdata/admission order changed")
    require("if (!ctx) return;" in listener and
            listener.index("if (!ctx) return;") <
            listener.index("if (!fm_r28_gate_try_enter(") <
            listener.index("fm_r28_gate_leave(&ctx->queue_admission);"),
            "R30 listener userdata/admission order changed")
    require("AudioQueueEnqueueBuffer(ctx->queue,buf,0,NULL)" in pcm and
            "atomic_flag_test_and_set_explicit(&ctx->pcm_writer_gate," in callback,
            "R30 PCM queue/lock site changed")
    require("AudioQueueStop(ctx->queue,false)" in source and
            "AudioQueueStop(ctx->queue,true)" in ctrl and
            "AudioQueueRemovePropertyListener(ctx->queue," in ctrl,
            "R30 stop/listener sites changed")
    # Assert the precise dangerous path is still visible; do NOT call it safe.
    start=ctrl.index("if (!err && AudioQueueStart(ctx->queue,NULL)!=noErr) err=1;")
    last_close=ctrl.rindex("fm_r28_gate_close(&ctx->queue_admission);")
    fail=ctrl.index("if (!fm_r28_gate_closed_and_empty(&ctx->queue_admission))",last_close)
    return_early=ctrl.index("return -1;",fail)
    stop=ctrl.index("AudioQueueStop(ctx->queue,true)",fail)
    dispose=ctrl.index("AudioQueueDispose(ctx->queue,true)",fail)
    require(start<last_close<fail<return_early<stop<dispose,
            "R30 critical early-exit-after-start site altered: re-review necessary")
    require("fm_context_quarantined,1,memory_order_release" in
            ctrl[fail:return_early],"R30 early exit quarantine site changed")
    remove=ctrl.index("AudioQueueRemovePropertyListener(ctx->queue,")
    failure=ctrl.index("listener_remove_failed=1;",remove)
    final_dispose=ctrl.index("if (AudioQueueDispose(ctx->queue,true)!=noErr)",failure)
    clear=ctrl.index("ctx->queue=NULL;",final_dispose)
    require(remove<failure<final_dispose<clear,
            "R30 failure/remove/dispose/clear order changed")
    new=ctrl.index("AudioQueueNewOutput(&fmt,output_callback,ctx")
    create_fail=ctrl.index("fm_r28_gate_close(&ctx->queue_admission);",new)
    require(new<create_fail<start,"R30 create failure seal order changed")
    require("request_graceful_queue_drain(ctx);" in ctrl,
            "R30 controller drain site missing")
    require("int fm_acoustic_physical_output(const FMCommand *command)" in source and
            "/* GEN-R3: unconditional hard denial" in source,
            "R30 external output denial missing")
    require(len(FINDINGS)==12 and len(ANCHORS)==12 and
            [x[0] for x in FINDINGS]==[x[0] for x in ANCHORS] and
            len(set(x[0] for x in FINDINGS))==12,"R30 findings drift")
    for key,site1,site2 in ANCHORS:
        for section,needle in (site1,site2):
            _once(fn(source,section),needle,key)
    return {x[0]:"OPEN_NOT_PROVEN" for x in FINDINGS}

def inspect(root,candidate_override=None):
    root=Path(root).resolve()
    table,manifest=r17.manifest_integrity(root)
    require(len(table)==162,"R30 requires exactly 162 SHA-pinned generator files")
    required=("audits/r30_coreaudio_quiescence_adversarial.py",
              "tests/test_r30_coreaudio_quiescence_adversarial.py",
              "RUN_GEN_R30_MAC_INTEL.command",
              "docs/GEN_R30_COREAUDIO_QUIESCENCE.md",
              "docs/GEN_R30_BUREAU_REVIEW.md",
              "docs/GEN_R30_OS_PROOF_MATRIX.md")
    require(all(p in table for p in required),"R30 review artifacts missing from manifest")
    historic=r29.inspect(root)
    require(table[r29.CANDIDATE]==historic[2],"R30 inherited R29 C candidate changed")
    require(table[r28.CANDIDATE]==r28.inspect(root)[2],"R30 R28 gate changed")
    require(table[r26.ORIGINAL]==r19.PINNED_ACOUSTIC_SHA256,
            "R30 original acoustic C changed")
    raw=(root/r29.CANDIDATE).read_bytes()
    require(digest(raw)==table[r29.CANDIDATE],"R30 R29 C SHA mismatch")
    checks=observe(raw.decode("utf-8") if candidate_override is None
                   else candidate_override)
    run=(root/"RUN_GEN_R30_MAC_INTEL.command").read_text(encoding="utf-8")
    require(set(r17.link_sources(run))==r17.LINK_C_ALLOWLIST,
            "R30 executable link allowlist changed")
    pieces=run.split(' -o "$WORK/freqmed-gen"')
    require(len(pieces)==2,"R30 runnable command link site missing")
    linked=pieces[1].split("-framework CoreAudio",1)[0]
    require("output_hard_denied.c" in linked,"R30 output denial source not linked")
    for forbidden in ("acoustic_macos_r29.c","acoustic_macos_r26.c",
                      "r28_callback_admission_gate.c","src/acoustic_macos.c"):
        require(forbidden not in linked,"R30 forbidden output source linked: "+forbidden)
    for token in ("R30_R29_CANDIDATE_OBJECT=COMPILED_UNLINKED",
                  "R30_NONEMITTING_EXECUTABLE_SYMBOL_AUDIT=PASS",
                  "R30_BUREAU_ADVERSARIAL_DOSSIER=22_FILES_SHA256_PASS",
                  "R30_TESTCASE_RUN_SLOT=PASS",
                  "FREQMED_GEN_R30_EVIDENCE_DIR",
                  "FREQMED_GEN_R30_BINARY"):
        require(token in run,"R30 runner guard missing: "+token)
    return table,manifest,digest(raw),checks

def anchor(source,section,needle,source_sha):
    return r29.anchor(source,section,needle,source_sha)

def audit(root,archive_r19,paths):
    table,manifest,csha,checks=inspect(root)
    expected=r29.audit(root,archive_r19,paths)
    recorded=json.loads(Path(paths["r29"]).read_text(encoding="utf-8"))
    require(recorded==expected,"R30 historical R29 report differs from recomputed evidence")
    require(expected["r29_findings_open"]==7 and
            expected["r28_gates_open"]==5 and
            expected["r27_findings_open"]==9 and
            expected["r23_obligations_open"]==15 and
            expected["r24_findings_open"]==7 and
            expected["bureau_gates_open"]==11 and
            expected["bureau_gates_resolved"]==0,
            "R30 inherited proof obligations unexpectedly resolved")
    source=(Path(root)/r29.CANDIDATE).read_text(encoding="utf-8")
    ledger=[]
    for (name,severity,role,proof),(ref,one,two) in zip(FINDINGS,ANCHORS):
        require(name==ref,"R30 finding-to-anchor drift")
        ledger.append({
         "id":name,"severity":severity,"bureau_role":role,
         "status":checks[name],"race_reproduced":False,
         "anchors":[anchor(source,*one,csha),anchor(source,*two,csha)],
         "required_independent_proof":proof,"approval":"NONE"
        })
    return {
     "schema":SCHEMA,"verdict":VERDICT,
     "method":"SHA_PINNED_SOURCE_ONLY_OS_QUIESCENCE_ADVERSARIAL_REVIEW",
     "manifest_sha256":manifest,"pinned_generator_files":len(table),
     "r29_candidate_sha256":csha,
     "r28_gate_sha256":table[r28.CANDIDATE],
     "original_C_sha256":table[r26.ORIGINAL],
     "r29_report_sha256":digest(Path(paths["r29"]).read_bytes()),
     "findings":ledger,"r30_findings_open":12,
     "r30_critical_open":2,"r30_proven_races":0,
     "r30_C_edits":0,"r30_linked_output":False,
     "r29_findings_open":7,"r28_gates_open":5,"r27_findings_open":9,
     "r23_obligations_open":15,"r24_findings_open":7,
     "bureau_gates_open":11,"bureau_gates_resolved":0,
     "C11_race_freedom":"NOT_PROVEN",
     "CoreAudio_callback_quiescence":"NOT_PROVEN",
     "post_start_shutdown_safety":"NOT_PROVEN",
     "failed_AudioQueueDispose":"NOT_TESTED",
     "independent_signatures":"NONE","bureau_certification":"PENDING",
     "limitations":list(LIMITATIONS),
     "physical_emission":"NONE","scientific_simulation":"NONE",
     "acoustic_output":"LOCKED","em_output":"LOCKED",
     "real_output":"NOT_AUTHORIZED",
     "biological_exposure":"NOT_AUTHORIZED","production":"NOT_AUTHORIZED",
    }
def markdown(report):
    lines=[
      "| "+f["id"]+" | "+f["severity"]+" | "+f["bureau_role"]+
      " | OPEN_NOT_PROVEN |" for f in report["findings"]
    ]
    return ("# FREQMED GEN-R30 — Independent CoreAudio Quiescence Adversarial Review\n\n"
      "**VERDICT: ADVERSARIAL_COREAUDIO_LIFETIME_GAPS_CONFIRMED_UNCERTIFIED.**\n\n"
      "The source contains an early return after AudioQueueStart which can "
      "skip Stop/Dispose when the admission gate is nonempty. **This is a "
      "critical unproven physical shutoff risk if activated; NEVER run this "
      "candidate.** No race or output was actually reproduced.\n\n"
      "| Source finding | Severity | Bureau | Status |\n|---|---|---|---|\n"+
      "\n".join(lines)+"\n\n"
      "All 12 R30 findings, 7 R29, 5 R28, 9 R27, 15 R23, 7 R24 "
      "and 11 Bureau gates remain OPEN. No scientific simulation, "
      "no active CoreAudio and no physical emission. These lexical source "
      "observations are not proof of C11 race freedom, OS quiescence or hardware cutoff.\n\n"
      "NEVER_SIMULATION=ENFORCED; ZERO_COST_FOSS=ENFORCED; "
      "ACOUSTIC_OUTPUT=LOCKED; EM_OUTPUT=LOCKED; REAL_OUTPUT=NOT_AUTHORIZED; "
      "BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED; PRODUCTION=NOT_AUTHORIZED.\n")
def main():
    p=argparse.ArgumentParser(description="GEN-R30 nonemitting CoreAudio adversarial audit")
    p.add_argument("--root",required=True,type=Path)
    p.add_argument("--archive-r19",required=True,type=Path)
    for number in range(16,30):
        p.add_argument("--r"+str(number),required=True,type=Path)
    p.add_argument("--json",required=True,type=Path)
    p.add_argument("--markdown",required=True,type=Path)
    a=p.parse_args()
    try:
        paths={"r"+str(n):getattr(a,"r"+str(n)) for n in range(16,30)}
        result=audit(a.root,a.archive_r19,paths)
        a.json.write_text(json.dumps(result,sort_keys=True,ensure_ascii=False,
                            indent=2)+"\n",encoding="utf-8")
        a.markdown.write_text(markdown(result),encoding="utf-8")
    except (R30Error,r29.R29Error,r28.R28Error,r27.R27Error,
            r26.R26Error,ValueError,TypeError,KeyError,IndexError,OSError,
            UnicodeError) as exc:
        print("R30_COREAUDIO_QUIESCENCE_REVIEW=FAIL_CLOSED",str(exc))
        return 2
    print("R30_COREAUDIO_QUIESCENCE_REVIEW=PASS")
    print("R30_OPEN_ADVERSARIAL_FINDINGS=12; R30_CRITICAL=2; R30_PROVEN_RACES=0")
    print("R30_R29_FINDINGS=7_OPEN; R30_R28_GATES=5_OPEN; R30_R27_FINDINGS=9_OPEN")
    print("R30_R23_OBLIGATIONS=15_OPEN; R30_R24_FINDINGS=7_OPEN")
    print("R30_BUREAU_GATES=11_OPEN; R30_BUREAU_RESOLVED=0")
    print("R30_REVIEW_VERDICT="+VERDICT)
    print("R30_POST_START_SHUTDOWN_SAFETY=NOT_PROVEN")
    print("R30_C11_RACE_FREEDOM=NOT_PROVEN")
    print("R30_CALLBACK_QUIESCENCE=NOT_PROVEN")
    print("R30_FAILED_OS_DISPOSAL=NOT_TESTED")
    print("R30_PHYSICAL_EMISSION=NONE; R30_SCIENTIFIC_SIMULATION=NONE")
    return 0
if __name__=="__main__":
    raise SystemExit(main())
