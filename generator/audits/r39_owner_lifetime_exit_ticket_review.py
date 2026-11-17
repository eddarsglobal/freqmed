#!/usr/bin/env python3
"""FREQMED GEN-R39: isolated C11 owner lifetime / atomic exit ticket audit.
Static real-source review only. NEVER calls CoreAudio, emits or simulates.
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
import r38_owner_alias_exit_audit as r38

SCHEMA="FREQMED_GEN_R39_OWNER_LIFETIME_ATOMIC_TICKET_PROOF_GATES"
VERDICT="AT_MOST_ONCE_EXIT_CANDIDATE_REVIEWED_EXACTLY_ONCE_AND_OS_PROOFS_OPEN"
FILES={
    "r31":r31.CANDIDATE,
    "r36":r36.CANDIDATE,
    "r37":r37.CANDIDATE,
    "r39":"candidates/r39_owner_lifetime_exit_ticket.c",
}
CANDIDATE=FILES["r39"]
FINDINGS=(
 ("LT39_01_C31_OS_RECEIVES_DIRECT_OWNER","CRITICAL","B07","C31 callbacks still pass heap ctx instead of immortal token"),
 ("LT39_02_OWNER_ALIASES_CAN_FREE_OUTSIDE_TICKET","CRITICAL","B09","C39 has no ownership control over external aliases or allocation"),
 ("LT39_03_EXACTLY_ONCE_CALLBACK_EXIT_NOT_PROVEN","CRITICAL","B09","CAS gives at-most-once leave, not guaranteed eventual exit on every OS callback"),
 ("LT39_04_FAILED_OS_STOP_PHYSICAL_CUTOFF","CRITICAL","B10","No real CoreAudio failure handling or hardware cutoff evidence"),
 ("LT39_05_TICKET_STORAGE_LIFETIME_EXTERNAL","HIGH","B09","Ticket storage must remain alive during concurrent enter and complete"),
 ("LT39_06_TICKET_NOT_COPIED_OR_REUSED","HIGH","B09","C cannot prevent copying, reinitializing or recycling ticket from external code"),
 ("LT39_07_OWNER_REGISTER_ONE_SHOT","HIGH","B09","C36 one-shot retains owner even if token exposure fails"),
 ("LT39_08_ENTER_BEFORE_OWNER_READ","HIGH","B09","Atomic state publication is only a local ticket contract"),
 ("LT39_09_OUTPUT_OS_ABI_NOT_CONNECTED","HIGH","B07","Real output callback never uses C39 adapter"),
 ("LT39_10_LISTENER_OS_ABI_NOT_CONNECTED","HIGH","B07","Real listener never uses C39 adapter"),
 ("LT39_11_R36_LEAVE_ERROR_NOT_RECOVERED","HIGH","B09","FINISHED becomes terminal even if fm36_leave fails"),
 ("LT39_12_R36_SHARED_COUNTER_NOT_IDENTITY","HIGH","B09","Global admitted counter is not a callback-identity witness"),
 ("LT39_13_C11_SHARED_QUEUE_FIELDS_NOT_PROVEN","HIGH","B09","C31 shared ctx queue and PCM fields require independent C11 proof"),
 ("LT39_14_OS_CALLBACK_QUIESCENCE_NOT_PROVEN","HIGH","B07","Seal does not establish disposal of all OS callbacks"),
 ("LT39_15_STATIC_SCAN_NOT_FORMAL_PROOF","HIGH","B09","Lexical source order and CAS syntax do not prove all interleavings"),
 ("LT39_16_NONEMITTING_BINARY_NOT_PHYSICAL_TEST","HIGH","B10","Unlinked source tests cannot certify emitted physical signals"),
)
ANCHORS=(
 ("LT39_01_C31_OS_RECEIVES_DIRECT_OWNER",("r31","AudioQueueNewOutput(&fmt,output_callback,ctx"),("r31","queue_running_listener,ctx)")),
 ("LT39_02_OWNER_ALIASES_CAN_FREE_OUTSIDE_TICKET",("r36","* after this claim, even if preparing/publishing/OS creation fails."),("r39","* C36 owner retains process lifetime, including all OS failure paths.")),
 ("LT39_03_EXACTLY_ONCE_CALLBACK_EXIT_NOT_PROVEN",("r39","int fm39_complete_at_most_once(FM39Lease *ticket)"),("r39","* AT-MOST-ONCE local leave does not mean EXACTLY-ONCE")),
 ("LT39_04_FAILED_OS_STOP_PHYSICAL_CUTOFF",("r31","if (r31_immediate_stop_status!=noErr) {"),("r39","* OS stop success, or physical cutoff.")),
 ("LT39_05_TICKET_STORAGE_LIFETIME_EXTERNAL",("r39","* Caller initializes each distinct living ticket with FM39_LEASE_INITIALIZER."),("r39","atomic_uint phase;")),
 ("LT39_06_TICKET_NOT_COPIED_OR_REUSED",("r39","* Never copy/reinitialize a published ticket or release its storage."),("r39","#define FM39_LEASE_INITIALIZER")),
 ("LT39_07_OWNER_REGISTER_ONE_SHOT",("r39","fm36_prepare_once(owner,userdata_out)"),("r36","static atomic_flag fm36_one_shot_claim=ATOMIC_FLAG_INIT;")),
 ("LT39_08_ENTER_BEFORE_OWNER_READ",("r39","fm36_try_enter(userdata,&owner)"),("r39","ticket->owner=owner;")),
 ("LT39_09_OUTPUT_OS_ABI_NOT_CONNECTED",("r31","static void output_callback(void *ptr,"),("r39","int fm39_enter_once(void *userdata,FM39Lease *ticket)")),
 ("LT39_10_LISTENER_OS_ABI_NOT_CONNECTED",("r31","static void queue_running_listener("),("r39","void *fm39_owner_if_active(const FM39Lease *ticket)")),
 ("LT39_11_R36_LEAVE_ERROR_NOT_RECOVERED",("r39","&ticket->phase,&expected,FM39_FINISHED,"),("r39","return fm36_leave(ticket->os_userdata);")),
 ("LT39_12_R36_SHARED_COUNTER_NOT_IDENTITY",("r36","atomic_uint admitted;"),("r36","int fm36_leave(void *userdata)")),
 ("LT39_13_C11_SHARED_QUEUE_FIELDS_NOT_PROVEN",("r31","AudioQueueEnqueueBuffer(ctx->queue,buf,0,NULL)"),("r31","ctx->queue=NULL;")),
 ("LT39_14_OS_CALLBACK_QUIESCENCE_NOT_PROVEN",("r39","int fm39_seal_without_release(void *userdata)"),("r36","* NOT an OS quiescence proof, and owner remains pinned until process exit.")),
 ("LT39_15_STATIC_SCAN_NOT_FORMAL_PROOF",("r39","memory_order_acq_rel,memory_order_acquire)) return -1;"),("r37","* This file proves no C11 happens-before relation for external ctx fields,")),
 ("LT39_16_NONEMITTING_BINARY_NOT_PHYSICAL_TEST",("r39","* UNLINKED, COMPILE ONLY. Never run, dispatch a callback, activate audio,"),("r31","/* GEN-R3: unconditional hard denial")),
)
CONTRACTS=(
 ("T39_INITIAL","FM39_LEASE_INITIALIZER","EXTERNAL_VALID_LIVE_TICKET","NOT_PROVEN"),
 ("T39_RESERVE","UNUSED_TO_RESERVING_CAS","NO_TICKET_COPY_OR_REUSE","NOT_PROVEN"),
 ("T39_ADMIT","fm36_try_enter_BEFORE_OWNER","OWNER_PROCESS_LIFETIME_EXTERNAL","NOT_PROVEN"),
 ("T39_PUBLISH","OWNER_AND_TOKEN_BEFORE_ACTIVE_RELEASE","CALLBACK_C11_HB_EXTERNAL","NOT_PROVEN"),
 ("T39_COMPLETE","ACTIVE_TO_FINISHED_CAS_ONCE","EVENTUAL_EXIT_NOT_ENFORCED","NOT_PROVEN"),
 ("T39_SEAL","fm36_seal_NO_FREE","OS_AND_PHYSICAL_STOP_UNPROVEN","NOT_PROVEN"),
)
LIMITATIONS=(
 "C39_OBJECT_IS_COMPILED_ONLY_UNLINKED_NEVER_CALLED",
 "AT_MOST_ONCE_DOES_NOT_PROVE_EXACTLY_ONCE",
 "R31_REAL_OS_USERDATA_REMAINS_DIRECT_CTX",
 "NO_EXTERNALLY_ENFORCED_OWNER_OR_TICKET_LIFETIME",
 "NO_C11_GLOBAL_HAPPENS_BEFORE_FORMAL_PROOF",
 "NO_OS_CALLBACK_OR_FAILED_OSSTATUS_EXECUTION",
 "NO_SCIENTIFIC_SIMULATION_OR_SYNTHETIC_INTERLEAVINGS",
 "NO_HARDWARE_CUTOFF_MEASUREMENT_OR_BIOLOGICAL_EXPOSURE",
 "BUREAU_SIGNATURES_NOT_OBTAINED",
)
class R39Error(ValueError): pass

def require(condition,why):
    if not condition: raise R39Error(why)

def sha(data): return hashlib.sha256(data).hexdigest()

def func(source,name):
    pat=r"^(?:static\s+)?(?:int\s+|void\s*\*\s*)"+re.escape(name)+r"\s*\([^;]*\)\s*\{"
    found=list(re.finditer(pat,source,re.M|re.S))
    require(len(found)==1,"R39 function absent or duplicated: "+name)
    start=found[0].start()
    brace=source.index("{",found[0].start())
    depth=0
    for pos in range(brace,len(source)):
        if source[pos]=="{": depth+=1
        elif source[pos]=="}":
            depth-=1
            if depth==0: return source[start:pos+1]
    raise R39Error("R39 unmatched C function: "+name)

def order(body,markers,label):
    require(all(x in body for x in markers),"R39 required "+label+" C anchor missing")
    indices=[body.index(x) for x in markers]
    require(indices==sorted(indices) and len(set(indices))==len(indices),
            "R39 "+label+" semantic source order changed")

def observe(c39,c31,c36,c37):
    r38.observe(c31,c36,c37)
    require(c39.startswith("/* SPDX-License-Identifier: Apache-2.0 */"),
            "R39 source copyright/license header absent")
    for forbidden in (
        "#include <AudioToolbox","#include <CoreAudio","AudioQueueStart(",
        "AudioQueueStop(","AudioQueueNewOutput(","AudioQueueDispose(",
        "AudioQueueEnqueueBuffer(","AudioDeviceStart(","malloc(","calloc(",
        "free(","realloc(","pthread_create(","dlopen(","dlsym(",
    ):
        require(forbidden not in c39,"R39 unsafe output/memory API in compile-only candidate: "+forbidden)
    for fn in ("fm36_prepare_once","fm36_mark_exposed","fm36_try_enter",
               "fm36_leave","fm36_seal"):
        require("extern int "+fn+"(" in c39,"R39 missing C36 declaration "+fn)
    for fn in ("fm39_register_owner_once","fm39_enter_once",
               "fm39_owner_if_active","fm39_complete_at_most_once",
               "fm39_seal_without_release"):
        func(c39,fn)
    require(c39.count("atomic_uint phase;")==1 and
            c39.count("FM39_LEASE_INITIALIZER")==2 and
            "FM39_UNUSED=0u" in c39 and
            "FM39_RESERVING=1u" in c39 and
            "FM39_ACTIVE=2u" in c39 and
            "FM39_FINISHED=3u" in c39 and
            "FM39_REJECTED=4u" in c39,
            "R39 one-use ticket phase/initialization contract drift")
    register=func(c39,"fm39_register_owner_once")
    order(register,("*userdata_out=NULL;",
                    "fm36_prepare_once(owner,userdata_out)",
                    "fm36_mark_exposed(*userdata_out)"),"owner registration")
    enter=func(c39,"fm39_enter_once")
    order(enter,("if (!ticket) return -1;",
                 "unsigned expected=FM39_UNUSED;",
                 "&ticket->phase,&expected,FM39_RESERVING,",
                 "void *owner=NULL;",
                 "fm36_try_enter(userdata,&owner)",
                 "ticket->os_userdata=userdata;",
                 "ticket->owner=owner;",
                 "atomic_store_explicit(&ticket->phase,FM39_ACTIVE,memory_order_release);"),
          "ticket admission and publication")
    require("if (!owner) {" in enter and
            "(void)fm36_leave(userdata);" in enter and
            enter.count("FM39_REJECTED,memory_order_release")==2,
            "R39 failed admission must deny ticket and release provisional count")
    read=func(c39,"fm39_owner_if_active")
    order(read,("atomic_load_explicit(&ticket->phase,memory_order_acquire)",
                "return ticket->owner;"),"owner release-acquire read")
    require("!=FM39_ACTIVE) return NULL;" in read,
            "R39 access to owner not gated by ACTIVE")
    finish=func(c39,"fm39_complete_at_most_once")
    order(finish,("if (!ticket) return -1;",
                  "unsigned expected=FM39_ACTIVE;",
                  "&ticket->phase,&expected,FM39_FINISHED,",
                  "return fm36_leave(ticket->os_userdata);"),"once-only completion")
    require("atomic_compare_exchange_strong_explicit(" in finish and
            "memory_order_acq_rel,memory_order_acquire)) return -1;" in finish and
            finish.count("fm36_leave(")==1,
            "R39 no at-most-once CAS before decrement")
    close=func(c39,"fm39_seal_without_release")
    require("return fm36_seal(userdata);" in close,
            "R39 closure no longer delegated to one-shot static anchor")
    require("fm39_" not in c31 and "fm39_" not in c36 and "fm39_" not in c37
            and "AudioQueueNewOutput(&fmt,output_callback,ctx" in c31,
            "R39 integration falsely claimed or older sources changed")
    require(len(FINDINGS)==16 and len(ANCHORS)==16 and
            sum(f[1]=="CRITICAL" for f in FINDINGS)==4 and
            [f[0] for f in FINDINGS]==[a[0] for a in ANCHORS] and
            len(CONTRACTS)==6,"R39 finding/contract registry drift")
    sources={"r31":c31,"r36":c36,"r37":c37,"r39":c39}
    for ident,first,second in ANCHORS:
        for scope,needle in (first,second):
            require(needle in sources[scope],
                    "R39 exact source witness missing "+ident+": "+needle)
    return {f[0]:"OPEN_NOT_PROVEN" for f in FINDINGS}

def inspect(root,override=None):
    root=Path(root).resolve()
    table,manifest=r17.manifest_integrity(root)
    require(len(table)>=220,"R39 historical audit requires at least 220 source SHA pins")
    needed=(
       CANDIDATE,
       "audits/r39_owner_lifetime_exit_ticket_review.py",
       "tests/test_r39_owner_lifetime_exit_ticket_review.py",
       "RUN_GEN_R39_MAC_INTEL.command",
       "docs/GEN_R39_OWNER_LIFETIME_ARCHITECTURE.md",
       "docs/GEN_R39_BUREAU_PROOF_GATES.md",
       "docs/GEN_R39_EXIT_TICKET_ADVERSARIAL_MATRIX.md",
    )
    require(all(n in table for n in needed),"R39 new source/test/docs not SHA-pinned")
    previous=r38.inspect(root)
    for key in ("r31","r36","r37"):
        require(previous[2][key]==table[FILES[key]],
                "R39 historic source hash diverges "+key)
    require(table[r26.ORIGINAL]==r19.PINNED_ACOUSTIC_SHA256,
            "R39 original native C changed")
    raw={scope:(root/path).read_bytes() for scope,path in FILES.items()}
    require(all(sha(raw[scope])==table[path] for scope,path in FILES.items()),
            "R39 source digest changed")
    checks=observe(raw["r39"].decode("utf-8") if override is None else override,
                   raw["r31"].decode("utf-8"),
                   raw["r36"].decode("utf-8"),
                   raw["r37"].decode("utf-8"))
    runner=(root/"RUN_GEN_R39_MAC_INTEL.command").read_text(encoding="utf-8")
    require(set(r17.link_sources(runner))==r17.LINK_C_ALLOWLIST,
            "R39 no-output CLI link source allowlist changed")
    segments=runner.split(' -o "$WORK/freqmed-gen"')
    require(len(segments)==2,"R39 no-output executable link command missing")
    linked=segments[1].split("-framework CoreAudio",1)[0]
    require("output_hard_denied.c" in linked,
            "R39 mandatory native denial not linked")
    for unwanted in ("r39_owner_lifetime_exit_ticket.c",
                     "r37_callback_lease_adapter.c","r36_stable_userdata_anchor.c",
                     "acoustic_macos_r31.c","r28_callback_admission_gate.c",
                     "src/acoustic_macos.c"):
        require(unwanted not in linked,"R39 forbidden C linked "+unwanted)
    for flag in ("R39_OWNER_EXIT_TICKET_REVIEW=PASS",
                 "R39_EXIT_TICKET_OBJECT=COMPILED_UNLINKED",
                 "R39_CALLBACK_LEASE_OBJECT=COMPILED_UNLINKED",
                 "R39_STABLE_ANCHOR_OBJECT=COMPILED_UNLINKED",
                 "R39_R31_CANDIDATE_OBJECT=COMPILED_UNLINKED",
                 "R39_NONEMITTING_EXECUTABLE_SYMBOL_AUDIT=PASS",
                 "R39_BUREAU_PROOF_DOSSIER=40_FILES_SHA256_PASS",
                 "R39_TESTCASE_RUN_SLOT=PASS",
                 "FREQMED_GEN_R39_EVIDENCE_DIR","FREQMED_GEN_R39_BINARY"):
        require(flag in runner,"R39 required nonemitting runner guard missing "+flag)
    return table,manifest,{key:sha(raw[key]) for key in FILES},checks

def source_anchor(source,path,needle,digest):
    require(needle in source,"R39 source line witness missing "+needle)
    return {"path":path,"line":source.count("\n",0,source.index(needle))+1,
            "sha256":digest,"text":needle}

def audit(root,archive_r19,reports):
    table,manifest,digests,checks=inspect(root)
    previous=r38.audit(root,archive_r19,reports)
    old_report=json.loads(Path(reports["r38"]).read_text(encoding="utf-8"))
    require(previous==old_report,"R39 historical R38 report recalculation drift")
    require(previous["r38_findings_open"]==18 and previous["r38_critical_open"]==5
            and previous["r37_findings_open"]==14
            and previous["r36_findings_open"]==12
            and previous["r35_findings_open"]==12
            and previous["r34_findings_open"]==14
            and previous["r33_findings_open"]==12
            and previous["r32_findings_open"]==10
            and previous["r31_findings_open"]==8
            and previous["r30_findings_open"]==12
            and previous["r29_findings_open"]==7
            and previous["r28_gates_open"]==5
            and previous["r27_findings_open"]==9
            and previous["r23_obligations_open"]==15
            and previous["r24_findings_open"]==7
            and previous["bureau_gates_open"]==11
            and previous["bureau_gates_resolved"]==0,
            "R39 inherited Bureau safety proof improperly promoted")
    texts={key:(Path(root)/path).read_text(encoding="utf-8")
           for key,path in FILES.items()}
    evidence=[]
    for (fid,severity,seat,why),(ident,a,b) in zip(FINDINGS,ANCHORS):
        require(fid==ident,"R39 finding anchor mismatch")
        evidence.append({
          "id":fid,"severity":severity,"bureau_seat":seat,
          "status":checks[fid],"unproven_obligation":why,
          "real_OS_callback_executed":False,
          "independent_certificate":"NONE",
          "source_anchors":[source_anchor(texts[scope],FILES[scope],needle,
                                           digests[scope])
                            for scope,needle in (a,b)],
        })
    return {
        "schema":SCHEMA,"verdict":VERDICT,
        "method":"ISOLATED_C11_EXIT_TICKET_STATIC_SOURCE_EVIDENCE_ONLY",
        "manifest_sha256":manifest,"source_files_sha_pinned":len(table),
        "source_digests":digests,
        "r38_report_sha256":sha(Path(reports["r38"]).read_bytes()),
        "r39_findings":evidence,"r39_findings_open":16,"r39_critical_open":4,
        "r39_contracts":[{"id":c[0],"source":c[1],"unproven":c[2],
                          "status":c[3]} for c in CONTRACTS],
        "r39_atomic_exit_at_most_once_candidate":True,
        "r39_exactly_once_callback_completion":"NOT_PROVEN",
        "r39_owner_lifetime_enforced_external":False,
        "r39_real_callback_integrated":False,
        "r39_real_OS_callbacks":0,
        "r39_existing_C_changes":0,
        "r38_findings_open":18,"r38_critical_open":5,
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
        "owner_lifetime_in_production":"NOT_PROVEN",
        "callback_exit_path_completeness":"NOT_PROVEN",
        "C11_global_race_freedom":"NOT_PROVEN",
        "OS_callback_quiescence":"NOT_PROVEN",
        "failed_OS_stop":"NOT_TESTED","failed_OS_dispose":"NOT_TESTED",
        "physical_cutoff":"NOT_PROVEN","bureau_certification":"PENDING",
        "scientific_simulation":"NONE","physical_emission":"NONE",
        "acoustic_output":"LOCKED","em_output":"LOCKED",
        "real_output":"NOT_AUTHORIZED","biological_exposure":"NOT_AUTHORIZED",
        "production":"NOT_AUTHORIZED","limitations":list(LIMITATIONS),
    }

def markdown(report):
    lines=["| "+f["id"]+" | "+f["severity"]+" | OPEN_NOT_PROVEN |"
           for f in report["r39_findings"]]
    return ("# FREQMED GEN-R39 — Atomic Exit Ticket & Owner Lifetime\n\n"
        "**Verdict: AT_MOST_ONCE_EXIT_CANDIDATE_REVIEWED_EXACTLY_ONCE_AND_OS_PROOFS_OPEN.**\n\n"
        "The SOURCE-ONLY C39 candidate uses a single atomic ACTIVE to FINISHED "
        "compare-exchange before one R36 leave. This bounds duplicate completion "
        "for a valid living ticket; it cannot guarantee any completion, lifetime "
        "of copied/external owner aliases or OS callback quiescence.\n\n"
        "| Obligation | Severity | Status |\n|---|---|---|\n"
        +"\n".join(lines)+"\n\n"
        "R39 16 OPEN (4 CRITICAL), R38 18 (5 CRITICAL), R37 14, R36 12, "
        "R35 12, R34 14, Bureau 11 OPEN/0 resolved. No simulation, "
        "no CoreAudio callback or physical output.\n\n"
        "NEVER_SIMULATION=ENFORCED; ZERO_COST_FOSS=ENFORCED; "
        "ACOUSTIC_OUTPUT=LOCKED; EM_OUTPUT=LOCKED; REAL_OUTPUT=NOT_AUTHORIZED; "
        "BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED; PRODUCTION=NOT_AUTHORIZED.\n")

def main():
    p=argparse.ArgumentParser(description="R39 atomic exit ticket ownership static audit")
    p.add_argument("--root",required=True,type=Path)
    p.add_argument("--archive-r19",required=True,type=Path)
    for n in range(16,39): p.add_argument("--r"+str(n),required=True,type=Path)
    p.add_argument("--json",required=True,type=Path)
    p.add_argument("--markdown",required=True,type=Path)
    args=p.parse_args()
    try:
        reports={"r"+str(n):getattr(args,"r"+str(n)) for n in range(16,39)}
        obj=audit(args.root,args.archive_r19,reports)
        args.json.write_text(json.dumps(obj,sort_keys=True,indent=2,
                              ensure_ascii=False)+"\n",encoding="utf-8")
        args.markdown.write_text(markdown(obj),encoding="utf-8")
    except (R39Error,r38.R38Error,r37.R37Error,r36.R36Error,r35.R35Error,
            r34.R34Error,r33.R33Error,r32.R32Error,r31.R31Error,
            r30.R30Error,r29.R29Error,r28.R28Error,r27.R27Error,
            r26.R26Error,ValueError,TypeError,KeyError,IndexError,
            OSError,UnicodeError) as exc:
        print("R39_OWNER_EXIT_TICKET_REVIEW=FAIL_CLOSED",str(exc))
        return 2
    print("R39_OWNER_EXIT_TICKET_REVIEW=PASS")
    print("R39_FINDINGS=16_OPEN; R39_CRITICAL=4_OPEN")
    print("R39_TICKET=AT_MOST_ONCE_SOURCE_CANDIDATE; R39_EXACTLY_ONCE=NOT_PROVEN")
    print("R39_C11_CONTRACTS=6_DOCUMENTARY; R39_OS_CALLBACKS=0")
    print("R39_R38_FINDINGS=18_OPEN; R39_R37_FINDINGS=14_OPEN")
    print("R39_BUREAU_GATES=11_OPEN; R39_BUREAU_RESOLVED=0")
    print("R39_REVIEW_VERDICT="+VERDICT)
    print("R39_OWNER_LIFETIME=NOT_PROVEN; R39_EXIT_COMPLETENESS=NOT_PROVEN")
    print("R39_C11_RACE_FREEDOM=NOT_PROVEN; R39_OS_QUIESCENCE=NOT_PROVEN")
    print("R39_PHYSICAL_CUTOFF=NOT_PROVEN; R39_PHYSICAL_EMISSION=NONE")
    print("R39_SCIENTIFIC_SIMULATION=NONE")
    return 0
if __name__=="__main__":
    raise SystemExit(main())
