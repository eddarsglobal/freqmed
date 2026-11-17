#!/usr/bin/env python3
"""GEN-R27 bounded adversarial C11/OS ownership review of isolated R26 C.
No callbacks, no scientific simulation, no physical emission, no C11 proof.
"""
import argparse
import hashlib
import json
from pathlib import Path
import r17_evidence_verifier as r17
import r19_adversarial_source_audit as r19
import r19_evidence_archive as archive19
import r26_isolated_patch_gate as r26

SCHEMA="FREQMED_GEN_R27_NATIVE_C11_ADVERSARIAL_OWNERSHIP_REVIEW"
VERDICT="ADVERSARIAL_GAPS_CONFIRMED_NO_RUNTIME_SAFETY_PROOF"
CANDIDATE=r26.CANDIDATE
SOURCE=r26.ORIGINAL
FUNCTIONS={
    "pcm":"static void fill_audio(",
    "listener":"static void queue_running_listener(",
    "callback":"static void output_callback(",
    "controller":"static __attribute__((unused)) int acoustic_output_impl(",
}
# Each finding remains OPEN; these are source observations, not race witnesses.
# id, priority, related R26 open risk, reviewer role, two code anchors, proof.
FINDINGS=(
 ("AD01_COMMON_FLAG_NOT_WHOLE_LIFETIME","HIGH","R26_C11_OS_ENTRY_NOT_PROVEN","B09",
  ("controller","atomic_flag_test_and_set_explicit(&ctx->pcm_writer_gate,"),
  ("callback","atomic_flag_test_and_set_explicit(&ctx->pcm_writer_gate,"),
  "Prove the full C11 read-write set for every PCM field and prove that every path entering fill_audio participates in the same synchronization or an independently justified nonoverlap rule."),
 ("AD02_OS_ENQUEUE_WITHIN_PCM_GATE","HIGH","R26_REAL_TIME_AND_ERROR_PATHS_UNREVIEWED","B09",
  ("pcm","AudioQueueEnqueueBuffer(ctx->queue,buf,0,NULL)"),
  ("callback","fill_audio(ctx,buf)"),
  "Independently review AudioQueueEnqueueBuffer callback dispatch and reentrancy guarantees, bounded time inside the PCM critical section and fault behavior on a genuinely overlapping callback."),
 ("AD03_NONATOMIC_QUEUE_NULL_VS_CALLBACK","HIGH","R26_C11_OS_ENTRY_NOT_PROVEN","B09",
  ("pcm","AudioQueueEnqueueBuffer(ctx->queue,buf,0,NULL)"),
  ("controller","ctx->queue=NULL;"),
  "Establish an actual OS callback-admission stop and C11 happens-before relation between every callback use of non-atomic ctx->queue and the controller's disposal and pointer clear."),
 ("AD04_LISTENER_USERDATA_PRECOUNTER","HIGH","R26_LONG_LIVED_OS_POINTERS_NOT_QUALIFIED","B07",
  ("listener","AcousticContext *ctx=(AcousticContext*)data;"),
  ("listener","atomic_fetch_add_explicit(&ctx->active_property_listeners"),
  "Obtain a documented guarantee that a late listener cannot take or dereference userdata after queue removal/disposal, including cases where listener registration or removal fails."),
 ("AD05_OUTPUT_USERDATA_PRECOUNTER","HIGH","R26_LONG_LIVED_OS_POINTERS_NOT_QUALIFIED","B07",
  ("callback","AcousticContext *ctx=(AcousticContext*)ptr;"),
  ("callback","atomic_fetch_add_explicit(&ctx->active_output_callbacks"),
  "Demonstrate callback admission termination, publication visibility and full completion before any future reclamation; the active counter alone cannot exclude an entry before its increment."),
 ("AD06_FAILED_DISPOSAL_RETAINS_OS_RESOURCES","HIGH","R26_COREAUDIO_DISPOSAL_FAILURE_NOT_TESTED","B07",
  ("controller","if (AudioQueueDispose(ctx->queue,true)!=noErr)"),
  ("controller","fm_latch_first_fault(ctx,FM_FAULT_DISPOSAL);"),
  "Document or separately qualify OSStatus failure ownership, whether callbacks or queue buffers can still exist, and a strict process lifetime bound for retained OS references."),
 ("AD07_BIND_REJECTION_QUARANTINE","MEDIUM","R26_COREAUDIO_DISPOSAL_FAILURE_NOT_TESTED","B07",
  ("controller","const OSStatus bind_dispose_status=AudioQueueDispose(ctx->queue,true);"),
  ("controller","if (bind_dispose_status==noErr)"),
  "Prove ownership of a rejected or partially created queue and userdata on both disposal outcomes, without relying on a successful OSStatus to imply whole-program C11 safety."),
 ("AD08_PERMANENT_CONTEXT_RETENTION","HIGH","R26_LEAK_UNTIL_PROCESS_TERMINATION","B10",
  ("controller","AudioQueueNewOutput(&fmt,output_callback,ctx"),
  ("controller","atomic_store_explicit(&fm_context_quarantined,1,memory_order_release);"),
  "Qualify strict process-scoped allocation and OS queue resource upper bounds, process shutdown and retained userdata lifetime; fail-closed retention is containment, not cleanup."),
 ("AD09_LISTENER_REMOVE_BEFORE_FINAL_DISPOSE","HIGH","R26_REAL_TIME_AND_ERROR_PATHS_UNREVIEWED","B07",
  ("controller","if (AudioQueueRemovePropertyListener(ctx->queue,"),
  ("controller","if (AudioQueueDispose(ctx->queue,true)!=noErr)"),
  "Review listener deregistration and synchronous disposal contracts separately; establish whether already dispatched listeners have finished before pointer or queue state changes."),
)
CATEGORIES=tuple(x[0] for x in r26.RISKS)
LIMITATIONS=(
 "BOUNDED_FUNCTION_SOURCE_SCAN_NOT_FULL_C11_AST",
 "SOURCE_ORDER_AND_ATOMIC_TOKENS_NOT_HAPPENS_BEFORE_PROOF",
 "NEGATIVE_GAP_OBSERVATIONS_NOT_REAL_THREAD_INTERLEAVINGS",
 "NO_COREAUDIO_CALLBACK_REGISTRATION_DISPATCH_OR_DISPOSAL_TEST",
 "NO_PHYSICAL_ACOUSTIC_OR_EM_ACTIVATION",
 "NO_SCIENTIFIC_SIMULATION_OR_SYNTHETIC_MEASUREMENT",
 "NO_INDEPENDENT_SIGNATURE_OR_FORMAL_PROOF",
)
class R27Error(ValueError): pass
def require(ok,why):
    if not ok: raise R27Error(why)
def sha(data): return hashlib.sha256(data).hexdigest()

def function_span(source,name):
    marker=FUNCTIONS[name]
    require(source.count(marker)==1,"R27 C function drift: "+name)
    start=source.index(marker)
    begin=source.find("{",start)
    require(begin>=0,"R27 C function body absent: "+name)
    depth=1
    for pos in range(begin+1,len(source)):
        if source[pos]=="{": depth+=1
        elif source[pos]=="}":
            depth-=1
            if depth==0: return start,pos+1,source[start:pos+1]
    raise R27Error("R27 C braces unbalanced: "+name)

def anchor(source,digest,where,needle):
    lo,hi,body=function_span(source,where)
    require(needle in body,"R27 missing source evidence: "+where+" "+needle)
    pos=lo+body.index(needle)
    return {"path":CANDIDATE,"function":where,
            "line":source.count("\n",0,pos)+1,
            "source_sha256":digest,"needle":needle}

def observe(source):
    parts={key:function_span(source,key)[2] for key in FUNCTIONS}
    ctrl,cb,pcm,lis=(parts[x] for x in ("controller","callback","pcm","listener"))
    require(len(FINDINGS)==9,"R27 finding count changed")
    require({x[2] for x in FINDINGS}==set(CATEGORIES),
            "R27 omits an R26 unresolved category")
    checks={
      "AD01_COMMON_FLAG_NOT_WHOLE_LIFETIME":
          ctrl.count("atomic_flag_test_and_set_explicit(&ctx->pcm_writer_gate,")==1
          and cb.count("atomic_flag_test_and_set_explicit(&ctx->pcm_writer_gate,")==1
          and ctrl.index("atomic_flag_test_and_set_explicit(&ctx->pcm_writer_gate,")
              < ctrl.index("fill_audio(ctx,b);")
              < ctrl.index("atomic_flag_clear_explicit(&ctx->pcm_writer_gate,memory_order_release);")
          and cb.index("atomic_flag_test_and_set_explicit(&ctx->pcm_writer_gate,")
              < cb.index("fill_audio(ctx,buf)")
              < cb.index("atomic_flag_clear_explicit(&ctx->pcm_writer_gate,"),
      "AD02_OS_ENQUEUE_WITHIN_PCM_GATE":
          "AudioQueueEnqueueBuffer(ctx->queue,buf,0,NULL)" in pcm
          and "fill_audio(ctx,b);" in ctrl
          and "fill_audio(ctx,buf)" in cb,
      "AD03_NONATOMIC_QUEUE_NULL_VS_CALLBACK":
          "AudioQueueEnqueueBuffer(ctx->queue,buf,0,NULL)" in pcm
          and "ctx->queue=NULL;" in ctrl
          and ctrl.index("if (AudioQueueDispose(ctx->queue,true)!=noErr)")
              < ctrl.index("ctx->queue=NULL;")
          and "atomic_flag_test_and_set_explicit(&ctx->pcm_writer_gate" not in
              ctrl[ctrl.index("if (AudioQueueDispose(ctx->queue,true)!=noErr)"):],
      "AD04_LISTENER_USERDATA_PRECOUNTER":
          lis.index("AcousticContext *ctx=(AcousticContext*)data;")
              < lis.index("atomic_fetch_add_explicit(&ctx->active_property_listeners")
          and "AudioQueueGetProperty(queue," in lis,
      "AD05_OUTPUT_USERDATA_PRECOUNTER":
          cb.index("AcousticContext *ctx=(AcousticContext*)ptr;")
              < cb.index("atomic_fetch_add_explicit(&ctx->active_output_callbacks")
          and "fill_audio(ctx,buf)" in cb,
      "AD06_FAILED_DISPOSAL_RETAINS_OS_RESOURCES":
          "if (AudioQueueDispose(ctx->queue,true)!=noErr)" in ctrl
          and "fm_latch_first_fault(ctx,FM_FAULT_DISPOSAL);" in ctrl
          and "ctx->queue=NULL;" in ctrl
          and "free(owner_ctx);" not in ctrl[ctrl.index("if (AudioQueueDispose(ctx->queue,true)!=noErr)"):],
      "AD07_BIND_REJECTION_QUARANTINE":
          "const OSStatus bind_dispose_status=AudioQueueDispose(ctx->queue,true);" in ctrl
          and "if (bind_dispose_status==noErr)" in ctrl
          and ctrl.index("const OSStatus bind_dispose_status=")
              < ctrl.index("if (bind_dispose_status==noErr)")
          and "atomic_store_explicit(&fm_context_quarantined,1,memory_order_release);" in
              ctrl[ctrl.index("if (bind_dispose_status==noErr)"):],
      "AD08_PERMANENT_CONTEXT_RETENTION":
          ctrl.count("free(owner_ctx);")==2
          and "AudioQueueNewOutput(&fmt,output_callback,ctx" in ctrl
          and ctrl.rindex("free(owner_ctx);") <
              ctrl.index("AudioQueueNewOutput(&fmt,output_callback,ctx")
          and ctrl.rstrip().endswith("return -1;\n\n}")
          and "atomic_store_explicit(&fm_context_quarantined,1,memory_order_release);" in ctrl,
      "AD09_LISTENER_REMOVE_BEFORE_FINAL_DISPOSE":
          ctrl.index("if (AudioQueueRemovePropertyListener(ctx->queue,")
              < ctrl.index("if (AudioQueueDispose(ctx->queue,true)!=noErr)")
          and "listener_remove_failed=1;" in ctrl
          and "atomic_store(&ctx->dispose_confirmed,1);" in ctrl,
    }
    require(set(checks)=={f[0] for f in FINDINGS},
            "R27 observation/ledger mismatch")
    for key,val in checks.items():
        require(val,"R27 adversarial source finding drift: "+key)
    return checks

def inspect(root,candidate_override=None):
    root=Path(root).resolve()
    table,manifest=r17.manifest_integrity(root)
    require(len(table)>=144,"R27 historical baseline requires at least 144 pinned files")
    for path in (CANDIDATE,"audits/r27_adversarial_ownership_review.py",
                 "tests/test_r27_adversarial_ownership_review.py",
                 "RUN_GEN_R27_MAC_INTEL.command",
                 "docs/GEN_R27_ADVERSARIAL_FINDINGS.md",
                 "docs/GEN_R27_BUREAU_REVIEW.md"):
        require(path in table,"R27 missing pinned artifact "+path)
    require(table[SOURCE]==r19.PINNED_ACOUSTIC_SHA256,
            "original acoustic C pin changed")
    old=(root/SOURCE).read_bytes()
    new=(root/CANDIDATE).read_bytes()
    runbytes=(root/"RUN_GEN_R27_MAC_INTEL.command").read_bytes()
    require(sha(old)==table[SOURCE] and sha(new)==table[CANDIDATE],
            "R27 C file SHA mismatch")
    require(sha(runbytes)==table["RUN_GEN_R27_MAC_INTEL.command"],
            "R27 runner SHA mismatch")
    require(new.decode("utf-8")==r26.expected_candidate(old.decode("utf-8")),
            "R26 isolated candidate differs from exact three original edits")
    text=new.decode("utf-8") if candidate_override is None else candidate_override
    checks=observe(text)
    run=runbytes.decode("utf-8")
    sources=r17.link_sources(run)
    require(len(sources)==len(r17.LINK_C_ALLOWLIST)
            and set(sources)==r17.LINK_C_ALLOWLIST,
            "R27 executable linker allowlist changed")
    parts=run.split(' -o "$WORK/freqmed-gen"')
    require(len(parts)==2,"R27 runnable link command not found")
    link=parts[1].split("-framework CoreAudio")[0]
    require("acoustic_macos_r26.c" not in link
            and "acoustic_macos.c" not in link
            and "output_hard_denied.c" in link,
            "R27 physical output C linked to executable")
    for token in ("R27_NONEMITTING_EXECUTABLE_SYMBOL_AUDIT=PASS",
                  "R27_ISOLATED_CANDIDATE_OBJECT=COMPILED_UNLINKED",
                  "R27_BUREAU_ADVERSARIAL_DOSSIER=16_FILES_SHA256_PASS",
                  "FREQMED_GEN_R27_BINARY"):
        require(token in run,"R27 executable/report gate missing "+token)
    return table,manifest,checks,sha(new)

def audit(root,archive_r19,reports,r21,r22,r23,r24,r25,r26_report):
    table,manifest,checks,candidate_sha=inspect(root)
    actual=archive19.parse_json(archive19.safe_read(r26_report))
    expected=r26.audit(root,archive_r19,reports,r21,r22,r23,r24,r25)
    require(actual==expected,"R26 report inconsistent with original pinned evidence")
    require(actual["isolated_native_candidate_patches"]==3
            and actual["applied_to_original_C"] is False
            and actual["r23_proof_obligations_open"]==15
            and actual["r24_findings_open"]==7
            and actual["bureau_gates_open"]==11
            and actual["bureau_gates_resolved"]==0,
            "R26 source evidence or Bureau gates silently promoted")
    c=(Path(root)/CANDIDATE).read_text(encoding="utf-8")
    ledger=[]
    for ident,priority,parent,role,a,b,needed in FINDINGS:
        require(parent in CATEGORIES and role in ("B07","B09","B10")
                and len(needed)>130,"R27 proof requirement too weak")
        ledger.append({
          "id":ident,"priority":priority,
          "r26_unresolved_parent":parent,"bureau_role":role,
          "anchors":[anchor(c,candidate_sha,*a),anchor(c,candidate_sha,*b)],
          "evidence_needed_for_resolution":needed,
          "source_only_observed":bool(checks[ident]),
          "status":"OPEN_NOT_PROVEN","race_reproduced":False,
          "physical_output_authorized":False,
        })
    require(len(ledger)==9 and len({x["id"] for x in ledger})==9,
            "R27 finding ledger incomplete")
    return {
      "schema":SCHEMA,"verdict":VERDICT,
      "method":"PINNED_ISOLATED_C11_SOURCE_NEGATIVE_PROPERTY_REVIEW",
      "manifest_sha256":manifest,"pinned_generator_files":len(table),
      "r26_candidate_sha256":candidate_sha,
      "original_source_sha256":table[SOURCE],
      "r26_report_sha256":sha(archive19.safe_read(r26_report)),
      "adversarial_findings":ledger,"r27_open_findings":9,
      "r27_proven_races":0,"r26_candidate_edits":3,
      "r26_candidate_integrated":False,
      "r23_obligations_open":15,"r24_findings_open":7,
      "r25_proposals":9,"bureau_gates_open":11,"bureau_gates_resolved":0,
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
    tick=chr(96)
    rows=[]
    for item in report["adversarial_findings"]:
        places=", ".join(tick+x["path"]+":"+str(x["line"])+tick
                         for x in item["anchors"])
        rows.append("| "+item["id"]+" | "+item["priority"]+
                    " | "+places+" | OPEN_NOT_PROVEN |")
    return ("# FREQMED GEN-R27 - Independent Native C11 Adversarial Review\n\n"
            "**Verdict: ADVERSARIAL_GAPS_CONFIRMED_NO_RUNTIME_SAFETY_PROOF.** "
            "9 source observations, no reproduced race, no C source changes.\n\n"
            "| Finding | Priority | Actual SHA-pinned C lines | Status |\n"
            "|---|---|---|---|\n"+"\n".join(rows)+
            "\n\nRetaining user data is not a proof that AudioQueueRef remains "
            "usable or that callbacks have quiesced. The shared PCM flag "
            "does not prove the CoreAudio callback timing or the lack of "
            "reentrancy around AudioQueueEnqueueBuffer. "
            "15 R23 proof obligations, 7 R24 findings, 9 R25 proposals and "
            "11 Bureau gates remain uncertified.\n\n"
            "NEVER_SIMULATION=ENFORCED; ZERO_COST_FOSS=ENFORCED; "
            "ACOUSTIC_OUTPUT=LOCKED; EM_OUTPUT=LOCKED; "
            "REAL_OUTPUT=NOT_AUTHORIZED; BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED; "
            "PRODUCTION=NOT_AUTHORIZED.\n")

def main():
    parser=argparse.ArgumentParser(description="GEN-R27 source-only C11 adversarial review")
    parser.add_argument("--root",required=True,type=Path)
    parser.add_argument("--archive-r19",required=True,type=Path)
    for x in ("r16","r17","r18","r19","r20","r21","r22","r23","r24","r25","r26"):
        parser.add_argument("--"+x,required=True,type=Path)
    parser.add_argument("--json",required=True,type=Path)
    parser.add_argument("--markdown",required=True,type=Path)
    a=parser.parse_args()
    try:
        prev={x:getattr(a,x) for x in ("r16","r17","r18","r19","r20")}
        result=audit(a.root,a.archive_r19,prev,a.r21,a.r22,a.r23,
                     a.r24,a.r25,a.r26)
        a.json.write_text(json.dumps(result,indent=2,sort_keys=True,
                          ensure_ascii=False)+"\n",encoding="utf-8")
        a.markdown.write_text(markdown(result),encoding="utf-8")
    except (R27Error,r26.R26Error,ValueError,KeyError,TypeError,
            OSError,UnicodeError,IndexError) as error:
        print("R27_C11_ADVERSARIAL_OWNERSHIP_REVIEW=FAIL_CLOSED",str(error))
        return 2
    print("R27_C11_ADVERSARIAL_OWNERSHIP_REVIEW=PASS")
    print("R27_OPEN_ADVERSARIAL_FINDINGS=9; R27_PROVEN_RACES=0")
    print("R27_R26_CANDIDATE_EDITS=3; R27_ORIGINAL_C_EDITS=0")
    print("R27_R23_PROOF_OBLIGATIONS=15_OPEN; R27_R24_FINDINGS=7_OPEN")
    print("R27_BUREAU_GATES=11_OPEN; R27_BUREAU_RESOLVED=0")
    print("R27_REVIEW_VERDICT="+VERDICT)
    print("R27_C11_RACE_FREEDOM=NOT_PROVEN")
    print("R27_CALLBACK_QUIESCENCE=NOT_PROVEN")
    print("R27_FAILED_OS_DISPOSAL=NOT_TESTED")
    print("R27_PHYSICAL_EMISSION=NONE; R27_SCIENTIFIC_SIMULATION=NONE")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
