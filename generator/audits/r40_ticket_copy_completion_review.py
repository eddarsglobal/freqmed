#!/usr/bin/env python3
"""GEN-R40: independent opaque-ticket copy and completion coverage review.
SHA-pinned static source-only audit. No callbacks, C11 scheduling simulation,
CoreAudio, devices, instruments, physical output or biological trials.
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
import r39_owner_lifetime_exit_ticket_review as r39

SCHEMA="FREQMED_GEN_R40_OPAQUE_TICKET_COPY_COMPLETION_REVIEW"
VERDICT="OPAQUE_PRIVATE_TICKET_CANDIDATE_REVIEWED_COMPLETION_AND_OS_PROOFS_OPEN"
HEADER="candidates/r40_opaque_ticket.h"
CANDIDATE="candidates/r40_opaque_ticket.c"
FILES={"r31":r31.CANDIDATE,"r36":r36.CANDIDATE,
       "r37":r37.CANDIDATE,"r39":r39.CANDIDATE,
       "r40":CANDIDATE,"h40":HEADER}
FINDINGS=(
 ("OP40_01_REAL_C31_DIRECT_CTX_USERDATA","CRITICAL","B07","Real CoreAudio output and listener still receive heap ctx"),
 ("OP40_02_OWNER_LIFETIME_EXTERNAL","CRITICAL","B09","External aliases can release owner; private tickets do not own it"),
 ("OP40_03_COMPLETION_COVERAGE_NOT_PROVEN","CRITICAL","B09","At-most-once CAS cannot require a callback to call complete"),
 ("OP40_04_OS_FAILED_STOP_QUIESCENCE_UNKNOWN","CRITICAL","B07","Neither stop/dispose error nor late callback OS completion proven"),
 ("OP40_05_PHYSICAL_STOP_UNPROVEN","CRITICAL","B10","No emission stop or instrument-level cutoff qualification"),
 ("OP40_06_TYPED_COPY_PREVENTION_LIMITED","HIGH","B09","Opaque type prevents ordinary copy-by-value only; pointer aliases/casts remain possible"),
 ("OP40_07_FIXED_TICKET_CAPACITY_EXHAUSTS","HIGH","B09","Four never-reused tickets cannot cover unbounded OS callback volume"),
 ("OP40_08_TICKET_POINTER_LIFETIME_STATIC","HIGH","B09","Static slot memory valid process-lifetime, but misuse/invalid pointer remains possible"),
 ("OP40_09_OWNER_POINTER_OUTLIVES_COMPLETION","HIGH","B09","Returning owner_out permits external aliases after ticket completes"),
 ("OP40_10_PRE_ADMISSION_SLOT_CONSUMPTION","HIGH","B09","Failed admission consumes a slot and may leave owner protected externally"),
 ("OP40_11_CONCURRENT_COMPLETE_AT_MOST_ONCE_ONLY","HIGH","B09","CAS prevents repeat leave per slot, not lost completions"),
 ("OP40_12_R36_LEAVE_FAILURE_TERMINAL","HIGH","B09","Slot remains FINISHED after failed fm36_leave"),
 ("OP40_13_SCOPE_OS_CALLBACK_WRAPPERS_ABSENT","HIGH","B07","Opaque API is not an Apple output or listener callback"),
 ("OP40_14_SHARED_C31_CONTEXT_FIELDS","HIGH","B09","C31 queue and PCM fields need independent global C11 HB proof"),
 ("OP40_15_SOURCE_SCAN_LIMITS","HIGH","B09","Source anchors and AST tests do not prove C11 scheduling or OS behavior"),
 ("OP40_16_BINARY_LINK_EXCLUSION_VS_HARDWARE","HIGH","B10","Object unlinked prevents candidate execution, not hardware safety certification"),
 ("OP40_17_PROCESS_SINGLE_OWNER_ONE_SHOT","HIGH","B09","C36 one-shot owner claim and permanent retention cannot handle multi-session demand"),
 ("OP40_18_INDIRECT_COPY_AND_EXTERNAL_LIFETIME","HIGH","B09","C opacity cannot prevent memcpy/casts or incorrect external owner free"),
)
ANCHORS=(
 ("OP40_01_REAL_C31_DIRECT_CTX_USERDATA",("r31","AudioQueueNewOutput(&fmt,output_callback,ctx"),("r31","queue_running_listener,ctx)")),
 ("OP40_02_OWNER_LIFETIME_EXTERNAL",("r36","_Atomic(void *) owner;"),("r40","* omitted completion, owner lifetime violations or real OS callbacks.")),
 ("OP40_03_COMPLETION_COVERAGE_NOT_PROVEN",("r40","int fm40_complete(FM40Ticket *ticket)"),("r40","* once on EVERY callback exit; C40 itself cannot enforce eventual calls.")),
 ("OP40_04_OS_FAILED_STOP_QUIESCENCE_UNKNOWN",("r31","if (r31_immediate_stop_status!=noErr) {"),("r31","if (AudioQueueDispose(ctx->queue,true)!=noErr) {")),
 ("OP40_05_PHYSICAL_STOP_UNPROVEN",("r31","/* CRITICAL: OS stop failed."),("r40","/* Admission seal is not an OS callback quiescence or physical cutoff. */")),
 ("OP40_06_TYPED_COPY_PREVENTION_LIMITED",("h40","typedef struct FM40Ticket FM40Ticket;"),("r40","struct FM40Ticket {")),
 ("OP40_07_FIXED_TICKET_CAPACITY_EXHAUSTS",("h40","#define FM40_MAX_TICKETS 4u"),("r40","static struct FM40Ticket fm40_slots[FM40_MAX_TICKETS]={")),
 ("OP40_08_TICKET_POINTER_LIFETIME_STATIC",("r40","struct FM40Ticket *slot=&fm40_slots[i];"),("r40","if (ticket!=slot) continue;")),
 ("OP40_09_OWNER_POINTER_OUTLIVES_COMPLETION",("r40","*owner_out=owner;"),("r40","return fm36_leave(slot->token);")),
 ("OP40_10_PRE_ADMISSION_SLOT_CONSUMPTION",("r40","&slot->phase,&expected,FM40_RESERVED,"),("r40","FM40_REJECTED,memory_order_release")),
 ("OP40_11_CONCURRENT_COMPLETE_AT_MOST_ONCE_ONLY",("r40","&slot->phase,&expected,FM40_FINISHED,"),("r40","return fm36_leave(slot->token);")),
 ("OP40_12_R36_LEAVE_FAILURE_TERMINAL",("r40","FM40_FINISHED,"),("r36","int fm36_leave(void *userdata)")),
 ("OP40_13_SCOPE_OS_CALLBACK_WRAPPERS_ABSENT",("h40","int fm40_begin(void *userdata, FM40Ticket **ticket_out, void **owner_out);"),("r31","static void queue_running_listener(")),
 ("OP40_14_SHARED_C31_CONTEXT_FIELDS",("r31","AudioQueueEnqueueBuffer(ctx->queue,buf,0,NULL)"),("r31","ctx->queue=NULL;")),
 ("OP40_15_SOURCE_SCAN_LIMITS",("r40","* Compile to object only; NEVER link, load, call or dispatch any callback."),("h40","* copying by value, or modifying struct fields.")),
 ("OP40_16_BINARY_LINK_EXCLUSION_VS_HARDWARE",("r40","* No CoreAudio operations, simulations, audio or EM device output."),("r31","/* GEN-R3: unconditional hard denial")),
 ("OP40_17_PROCESS_SINGLE_OWNER_ONE_SHOT",("r36","static atomic_flag fm36_one_shot_claim=ATOMIC_FLAG_INIT;"),("r40","fm36_prepare_once(owner,userdata_out)")),
 ("OP40_18_INDIRECT_COPY_AND_EXTERNAL_LIFETIME",("h40","* of the POINTER, void* casts, invalid memory operations, or an omitted exit."),("r40","* and refusing all slot reuse.")),
)
CONTRACTS=(
 ("C40_OPAQUE_API","INCOMPLETE_TYPE","NO_TYPED_BY_VALUE_COPY","EXTERNAL_POINTER_ALIAS_RISK"),
 ("C40_STATIC_STORAGE","FOUR_PRIVATE_SLOTS","NEVER_REUSE","FINITE_CALLBACK_CAPACITY"),
 ("C40_ADMISSION","R36_GATE_BEFORE_OWNER","REJECTED_FINAL","OWNER_ALIAS_EXTERNAL"),
 ("C40_PUBLICATION","RELEASE_ACTIVE_AFTER_TOKEN","ACQUIRE_CAS_COMPLETE","GLOBAL_C11_HB_NOT_PROVEN"),
 ("C40_COMPLETION","ONE_CAS_WINNER_PER_SLOT","AT_MOST_ONCE","EXACTLY_ONCE_NOT_PROVEN"),
 ("C40_OS_SCOPE","NO_CALLBACK_ABI","NO_HARDWARE_OUTPUT","OS_QUIESCENCE_NOT_PROVEN"),
)
LIMITATIONS=(
 "NO_REAL_OS_CALLBACKS_OR_QUEUES",
 "C40_CANDIDATE_COMPILED_UNLINKED_NEVER_DISPATCHED",
 "NO_SCIENTIFIC_SIMULATION_OR_SCHEDULING_INTERLEAVING",
 "OPAQUE_C_TYPE_DOES_NOT_PREVENT_RAW_C_MEMORY_OPERATIONS",
 "NO_EXTERNAL_OWNER_ALIAS_LIFETIME_PROOF",
 "NO_EXACTLY_ONCE_COMPLETION_OR_OS_STOP_PROOF",
 "NO_PHYSICAL_CUTOFF_MEASUREMENT",
 "NO_INDEPENDENT_SIGNED_BUREAU_CERTIFICATION",
)
class R40Error(ValueError): pass

def require(x,reason):
    if not x: raise R40Error(reason)

def sha(x): return hashlib.sha256(x).hexdigest()

def fn(src,name):
    pattern=r"^(?:static\s+)?int\s+"+re.escape(name)+r"\s*\([^;]*\)\s*\{"
    matches=list(re.finditer(pattern,src,re.M|re.S))
    require(len(matches)==1,"R40 function missing or duplicate "+name)
    first=matches[0].start()
    start=src.index("{",matches[0].start())
    depth=0
    for i in range(start,len(src)):
        if src[i]=="{": depth+=1
        elif src[i]=="}":
            depth-=1
            if depth==0: return src[first:i+1]
    raise R40Error("R40 C function not balanced: "+name)

def order(body,tokens,name):
    require(all(tok in body for tok in tokens),"R40 missing "+name+" source token")
    indices=[body.index(tok) for tok in tokens]
    require(indices==sorted(indices) and len(set(indices))==len(indices),
            "R40 safety sequence altered: "+name)

def observe(c40,h40,c39,c31,c36,c37):
    r39.observe(c39,c31,c36,c37)
    require(c40.startswith("/* SPDX-License-Identifier: Apache-2.0 */"),
            "R40 candidate header missing")
    require(h40.startswith("/* SPDX-License-Identifier: Apache-2.0 */"),
            "R40 opaque API license header missing")
    require(h40.count("typedef struct FM40Ticket FM40Ticket;")==1
            and "struct FM40Ticket {" not in h40
            and "FM40_LEASE_INITIALIZER" not in h40
            and "FM40_MAX_TICKETS 4u" in h40,
            "R40 public ABI must not expose ticket struct or initializer")
    require(c40.count("struct FM40Ticket {")==1
            and c40.count("atomic_uint phase;")==1
            and c40.count("FM40_UNUSED),NULL}")==4
            and "static struct FM40Ticket fm40_slots[FM40_MAX_TICKETS]" in c40,
            "R40 fixed private process-lifetime ticket array altered")
    for forbidden in (
        "AudioQueueStart(","AudioQueueStop(","AudioQueueNewOutput(",
        "AudioQueueDispose(","AudioQueueEnqueueBuffer(","AudioDeviceStart(",
        "malloc(","calloc(","free(","realloc(","pthread_create(",
        "dlopen(","dlsym("):
        require(forbidden not in c40,"R40 forbidden output/allocator in candidate "+forbidden)
    for api in ("fm40_register_owner_once","fm40_begin","fm40_complete","fm40_seal"):
        require("int "+api+"(" in h40,"R40 missing opaque header entry "+api)
        fn(c40,api)
    for dep in ("fm36_prepare_once","fm36_mark_exposed","fm36_try_enter",
                "fm36_leave","fm36_seal"):
        require("extern int "+dep+"(" in c40,
                "R40 must depend on static lifetime R36 ABI "+dep)
    register=fn(c40,"fm40_register_owner_once")
    order(register,("*userdata_out=NULL;",
                    "fm36_prepare_once(owner,userdata_out)",
                    "fm36_mark_exposed(*userdata_out)"),"owner one-shot")
    begin=fn(c40,"fm40_begin")
    order(begin,("if (!ticket_out || !owner_out) return -1;",
                 "*ticket_out=NULL;","*owner_out=NULL;",
                 "for (size_t i=0u;i<FM40_MAX_TICKETS;i++) {",
                 "&slot->phase,&expected,FM40_RESERVED,",
                 "fm36_try_enter(userdata,&owner)",
                 "slot->token=userdata;",
                 "FM40_ACTIVE,memory_order_release",
                 "*owner_out=owner;",
                 "*ticket_out=slot;"),"callback entry")
    require("if (!owner) {" in begin
            and "(void)fm36_leave(userdata);" in begin
            and begin.count("FM40_REJECTED,memory_order_release")==2,
            "R40 fail-closed rejection/compensation missing")
    require(begin.count("return 0;")==1 and
            "return -1;\n}" in begin,
            "R40 exhausted tickets must refuse without heap fallback")
    end=fn(c40,"fm40_complete")
    order(end,("if (!ticket) return -1;",
               "for (size_t i=0u;i<FM40_MAX_TICKETS;i++) {",
               "if (ticket!=slot) continue;",
               "unsigned expected=FM40_ACTIVE;",
               "&slot->phase,&expected,FM40_FINISHED,",
               "return fm36_leave(slot->token);"),"callback completion")
    require("atomic_compare_exchange_strong_explicit(" in end
            and end.count("fm36_leave(")==1
            and "memory_order_acq_rel,memory_order_acquire)) return -1;" in end,
            "R40 CAS-at-most-once completion missing")
    seal=fn(c40,"fm40_seal")
    require("return fm36_seal(userdata);" in seal,
            "R40 seal must remain R36 denial-only")
    for old in (c31,c36,c37,c39):
        require("fm40_" not in old,
                "R40 must not be integrated into any prior C candidate")
    require("AudioQueueNewOutput(&fmt,output_callback,ctx" in c31,
            "R40 real CoreAudio ctx handoff status changed")
    require(len(FINDINGS)==18 and len(ANCHORS)==18
            and sum(x[1]=="CRITICAL" for x in FINDINGS)==5
            and [f[0] for f in FINDINGS]==[a[0] for a in ANCHORS]
            and len(CONTRACTS)==6,
            "R40 finding/contract register drift")
    src={"r31":c31,"r36":c36,"r37":c37,"r39":c39,"r40":c40,"h40":h40}
    for fid,first,second in ANCHORS:
        for scope,needle in (first,second):
            require(needle in src[scope],
                    "R40 source witness missing "+fid+": "+needle)
    return {f[0]:"OPEN_NOT_PROVEN" for f in FINDINGS}

def inspect(root,override=None,header_override=None):
    root=Path(root).resolve()
    table,manifest=r17.manifest_integrity(root)
    require(len(table)>=228,"R40 historical audit accepts later manifests with at least 228 pinned sources")
    needed=(CANDIDATE,HEADER,
            "audits/r40_ticket_copy_completion_review.py",
            "tests/test_r40_ticket_copy_completion_review.py",
            "RUN_GEN_R40_MAC_INTEL.command",
            "docs/GEN_R40_OPAQUE_TICKET_ARCHITECTURE.md",
            "docs/GEN_R40_BUREAU_PROOF_REVIEW.md",
            "docs/GEN_R40_EXIT_COVERAGE_MATRIX.md")
    require(all(item in table for item in needed),
            "R40 unpinned candidate/headers/auditor/tests/docs")
    old=r39.inspect(root)
    for key in ("r31","r36","r37","r39"):
        require(old[2][key]==table[FILES[key]],
                "R40 changed earlier C candidate SHA "+key)
    require(table[r26.ORIGINAL]==r19.PINNED_ACOUSTIC_SHA256,
            "R40 original hardware backend source changed")
    raw={key:(root/path).read_bytes() for key,path in FILES.items()}
    require(all(sha(raw[k])==table[p] for k,p in FILES.items()),
            "R40 source/header SHA changed")
    texts={key:data.decode("utf-8") for key,data in raw.items()}
    result=observe(texts["r40"] if override is None else override,
                   texts["h40"] if header_override is None else header_override,
                   texts["r39"],texts["r31"],texts["r36"],texts["r37"])
    runner=(root/"RUN_GEN_R40_MAC_INTEL.command").read_text(encoding="utf-8")
    require(set(r17.link_sources(runner))==r17.LINK_C_ALLOWLIST,
            "R40 no-output binary allowlist altered")
    split=runner.split(' -o "$WORK/freqmed-gen"')
    require(len(split)==2 and "output_hard_denied.c" in split[1].split("-framework CoreAudio")[0],
            "R40 hard-denied executable link source invalid")
    for forbidden in ("r40_opaque_ticket.c","r39_owner_lifetime_exit_ticket.c",
        "r37_callback_lease_adapter.c","r36_stable_userdata_anchor.c",
        "acoustic_macos_r31.c","r28_callback_admission_gate.c","src/acoustic_macos.c"):
        require(forbidden not in split[1].split("-framework CoreAudio")[0],
                "R40 candidate erroneously linked "+forbidden)
    for item in ("R40_TICKET_COPY_COMPLETION_REVIEW=PASS",
                 "R40_OPAQUE_TICKET_OBJECT=COMPILED_UNLINKED",
                 "R40_EXIT_TICKET_OBJECT=COMPILED_UNLINKED",
                 "R40_CALLBACK_LEASE_OBJECT=COMPILED_UNLINKED",
                 "R40_STABLE_ANCHOR_OBJECT=COMPILED_UNLINKED",
                 "R40_R31_CANDIDATE_OBJECT=COMPILED_UNLINKED",
                 "R40_NONEMITTING_EXECUTABLE_SYMBOL_AUDIT=PASS",
                 "R40_BUREAU_PROOF_DOSSIER=42_FILES_SHA256_PASS",
                 "R40_TESTCASE_RUN_SLOT=PASS",
                 "FREQMED_GEN_R40_EVIDENCE_DIR","FREQMED_GEN_R40_BINARY"):
        require(item in runner,"R40 runner safety/evidence marker missing "+item)
    return table,manifest,{k:sha(raw[k]) for k in raw},result

def witness(src,path,needle,digest):
    require(needle in src,"R40 source evidence not found "+needle)
    return {"path":path,"line":src.count("\n",0,src.index(needle))+1,
            "sha256":digest,"needle":needle}

def audit(root,archive_r19,reports):
    table,manifest,digests,observations=inspect(root)
    earlier=r39.audit(root,archive_r19,reports)
    real=json.loads(Path(reports["r39"]).read_text(encoding="utf-8"))
    require(earlier==real,"R40 historic R39 JSON report differs from recomputation")
    require(earlier["r39_findings_open"]==16
            and earlier["r39_critical_open"]==4
            and earlier["r38_findings_open"]==18
            and earlier["r37_findings_open"]==14
            and earlier["r36_findings_open"]==12
            and earlier["r35_findings_open"]==12
            and earlier["r34_findings_open"]==14
            and earlier["r33_findings_open"]==12
            and earlier["r32_findings_open"]==10
            and earlier["r31_findings_open"]==8
            and earlier["r30_findings_open"]==12
            and earlier["r29_findings_open"]==7
            and earlier["r28_gates_open"]==5
            and earlier["r27_findings_open"]==9
            and earlier["r23_obligations_open"]==15
            and earlier["r24_findings_open"]==7
            and earlier["bureau_gates_open"]==11
            and earlier["bureau_gates_resolved"]==0,
            "R40 historic Bureau safety gates incorrectly discharged")
    texts={key:(Path(root)/path).read_text(encoding="utf-8") for key,path in FILES.items()}
    data=[]
    for (fid,severity,seat,problem),(aid,first,second) in zip(FINDINGS,ANCHORS):
        require(fid==aid,"R40 proof ledger pairing drift")
        data.append({"id":fid,"severity":severity,"bureau_seat":seat,
                     "status":observations[fid],"open_obligation":problem,
                     "real_OS_callback_executed":False,
                     "source_anchors":[witness(texts[scope],FILES[scope],needle,
                                               digests[scope])
                                       for scope,needle in (first,second)]})
    return {"schema":SCHEMA,"verdict":VERDICT,
            "method":"C11_OPAQUE_TICKET_SHA_PINNED_SOURCE_ONLY_REVIEW",
            "source_manifest_sha256":manifest,"source_pins":len(table),
            "source_digests":digests,
            "r39_report_sha256":sha(Path(reports["r39"]).read_bytes()),
            "r40_findings":data,"r40_findings_open":18,"r40_critical_open":5,
            "r40_contracts":[{"id":c[0],"source_claim":c[1],
                               "obligation":c[2],"limit":c[3]} for c in CONTRACTS],
            "r40_private_slots":4,"r40_slot_reuse":False,
            "r40_c_type_opaque":True,
            "r40_typed_by_value_copy":"BLOCKED_BY_INCOMPLETE_TYPE",
            "r40_raw_pointer_copy":"NOT_PREVENTED",
            "r40_completion":"AT_MOST_ONCE_SOURCE_CANDIDATE",
            "r40_exactly_once_completion":"NOT_PROVEN",
            "r40_external_owner_lifetime":"NOT_PROVEN",
            "r40_real_callback_integrated":False,
            "r40_actual_OS_callbacks":0,
            "r40_existing_C_changed":False,
            "r39_findings_open":16,"r39_critical_open":4,
            "r38_findings_open":18,"r38_critical_open":5,
            "r37_findings_open":14,"r37_critical_open":4,
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
            "C11_global_race_freedom":"NOT_PROVEN",
            "CoreAudio_callback_quiescence":"NOT_PROVEN",
            "physical_cutoff":"NOT_PROVEN",
            "Bureau_certification":"PENDING",
            "scientific_simulation":"NONE","physical_emission":"NONE",
            "acoustic_output":"LOCKED","em_output":"LOCKED",
            "real_output":"NOT_AUTHORIZED",
            "biological_exposure":"NOT_AUTHORIZED",
            "production":"NOT_AUTHORIZED","limitations":list(LIMITATIONS)}

def markdown(report):
    rows=["| "+f["id"]+" | "+f["severity"]+" | OPEN_NOT_PROVEN |"
          for f in report["r40_findings"]]
    return ("# FREQMED GEN-R40 — Opaque Ticket & Completion Coverage\n\n"
      "**Verdict: OPAQUE_PRIVATE_TICKET_CANDIDATE_REVIEWED_COMPLETION_AND_OS_PROOFS_OPEN.**\n\n"
      "Opaque C ticket type blocks ordinary well-typed by-value copies; "
      "the private fixed array has four never-reused slots. The CAS ensures "
      "at-most-once leave for a valid slot, but does NOT guarantee callback "
      "completion, owner lifetime, OS quiescence or physical cutoff.\n\n"
      "| Obligation | Severity | Status |\n|---|---|---|\n"
      +"\n".join(rows)+"\n\n"
      "R40 18 OPEN (5 CRITICAL), R39 16, R38 18, R37 14, R36 12, "
      "Bureau 11 OPEN/0 resolved. No CoreAudio callback or scientific simulation.\n\n"
      "NEVER_SIMULATION=ENFORCED; ZERO_COST_FOSS=ENFORCED; "
      "ACOUSTIC_OUTPUT=LOCKED; EM_OUTPUT=LOCKED; REAL_OUTPUT=NOT_AUTHORIZED; "
      "BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED; PRODUCTION=NOT_AUTHORIZED.\n")

def main():
    parser=argparse.ArgumentParser(description="GEN-R40 opaque ticket static source auditor")
    parser.add_argument("--root",type=Path,required=True)
    parser.add_argument("--archive-r19",type=Path,required=True)
    for n in range(16,40):
        parser.add_argument("--r"+str(n),type=Path,required=True)
    parser.add_argument("--json",type=Path,required=True)
    parser.add_argument("--markdown",type=Path,required=True)
    args=parser.parse_args()
    try:
        history={"r"+str(n):getattr(args,"r"+str(n)) for n in range(16,40)}
        result=audit(args.root,args.archive_r19,history)
        args.json.write_text(json.dumps(result,sort_keys=True,indent=2,
                             ensure_ascii=False)+"\n",encoding="utf-8")
        args.markdown.write_text(markdown(result),encoding="utf-8")
    except (R40Error,r39.R39Error,r38.R38Error,r37.R37Error,r36.R36Error,
            r35.R35Error,r34.R34Error,r33.R33Error,r32.R32Error,
            r31.R31Error,r30.R30Error,r29.R29Error,r28.R28Error,
            r27.R27Error,r26.R26Error,ValueError,TypeError,KeyError,
            IndexError,OSError,UnicodeError) as exc:
        print("R40_TICKET_COPY_COMPLETION_REVIEW=FAIL_CLOSED",str(exc))
        return 2
    print("R40_TICKET_COPY_COMPLETION_REVIEW=PASS")
    print("R40_FINDINGS=18_OPEN; R40_CRITICAL=5_OPEN")
    print("R40_OPAQUE_TICKETS=4_PROCESS_LIFETIME; R40_SLOT_REUSE=NO")
    print("R40_TYPED_COPY=BLOCKED; POINTER_ALIASING=NOT_PREVENTED")
    print("R40_COMPLETION=AT_MOST_ONCE; EXACTLY_ONCE=NOT_PROVEN")
    print("R40_OS_CALLBACKS=0; R40_R39_FINDINGS=16_OPEN")
    print("R40_BUREAU_GATES=11_OPEN; R40_BUREAU_RESOLVED=0")
    print("R40_REVIEW_VERDICT="+VERDICT)
    print("R40_OWNER_LIFETIME=NOT_PROVEN; R40_C11_RACE_FREEDOM=NOT_PROVEN")
    print("R40_OS_QUIESCENCE=NOT_PROVEN; R40_PHYSICAL_CUTOFF=NOT_PROVEN")
    print("R40_PHYSICAL_EMISSION=NONE; R40_SCIENTIFIC_SIMULATION=NONE")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
