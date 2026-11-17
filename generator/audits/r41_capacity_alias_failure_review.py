#!/usr/bin/env python3
"""GEN-R41: SHA-pinned static ticket capacity, index alias and failure audit.
No callbacks executed, no scheduling simulation, no physical emission.
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
import r40_ticket_copy_completion_review as r40

SCHEMA="FREQMED_GEN_R41_CAPACITY_INDEX_ALIAS_FAILURE_CONTAINMENT"
VERDICT="INDEX_TICKET_FAULT_CONTAINMENT_REVIEWABLE_OS_OWNER_COMPLETION_NOT_PROVEN"
CANDIDATE="candidates/r41_index_ticket.c"
HEADER="candidates/r41_index_ticket.h"
FILES={"r31":r31.CANDIDATE,"r36":r36.CANDIDATE,
       "r37":r37.CANDIDATE,"r39":r39.CANDIDATE,
       "r40":r40.CANDIDATE,"h40":r40.HEADER,
       "r41":CANDIDATE,"h41":HEADER}
FINDINGS=(
 ("IX41_01_REAL_OS_DIRECT_CTX","CRITICAL","B07","C31 still hands direct owner ctx to real callbacks"),
 ("IX41_02_EXTERNAL_OWNER_LIFETIME","CRITICAL","B09","No control over all external owner pointer aliases"),
 ("IX41_03_EXACTLY_ONCE_UNPROVEN","CRITICAL","B09","No guarantee each admitted callback invokes complete"),
 ("IX41_04_OS_QUIESCENCE_UNKNOWN","CRITICAL","B07","No evidence CoreAudio stops delivering callbacks after failure"),
 ("IX41_05_PHYSICAL_CUTOFF_UNKNOWN","CRITICAL","B10","No instrumental physical stop or emission qualification"),
 ("IX41_06_CAPACITY_FOUR_FINITE","HIGH","B09","Only four nonrecycled slots per process cannot support unbounded callbacks"),
 ("IX41_07_HANDLE_COPIABLE","HIGH","B09","Integer ticket index can be copied and forged"),
 ("IX41_08_PREMATURE_FORGED_COMPLETION","HIGH","B09","A valid forged index may close someone else's ACTIVE slot"),
 ("IX41_09_OWNER_OUT_EXTERNAL_ALIAS","HIGH","B09","Owner pointer escapes to caller without provable lifetime"),
 ("IX41_10_STICKY_FAULT_NOT_OS_STOP","HIGH","B07","Fault latch records local errors but cannot stop CoreAudio"),
 ("IX41_11_STICKY_FAULT_ADMISSION_RACE","HIGH","B09","Latching fault may race with a concurrent admission after snapshot"),
 ("IX41_12_FAILED_ADMISSION_SLOT_BURN","HIGH","B09","Every reserved failure permanently consumes a slot"),
 ("IX41_13_LEAVE_FAILURE_COUNTER_UNKNOWN","HIGH","B09","Error after FINISHED leaves global admission accounting unproven"),
 ("IX41_14_NULL_OWNER_COMPENSATION","HIGH","B09","Failed compensating fm36_leave does not recover a slot"),
 ("IX41_15_REGISTER_ONE_SHOT_FAILURE","HIGH","B09","R36 owner claim cannot be reclaimed after exposure failure"),
 ("IX41_16_NO_GLOBAL_HAPPENS_BEFORE","HIGH","B09","Ticket CAS does not prove C31 PCM/queue field freedom from races"),
 ("IX41_17_C40_C41_NOT_INTEGRATED","HIGH","B07","Neither R40 nor R41 is a real Apple callback ABI"),
 ("IX41_18_FOUR_SLOTS_ARE_NOT_QUOTA_PLAN","HIGH","B09","No process restart or production capacity/recycling design"),
 ("IX41_19_SOURCE_ONLY_AND_NO_PHYSICAL_PROOF","HIGH","B10","Source and isolated compiler evidence cannot certify physical behavior"),
)
ANCHORS=(
 ("IX41_01_REAL_OS_DIRECT_CTX",("r31","AudioQueueNewOutput(&fmt,output_callback,ctx"),("r31","queue_running_listener,ctx)")),
 ("IX41_02_EXTERNAL_OWNER_LIFETIME",("r36","_Atomic(void *) owner;"),("r41","* and FORGEABLE; it is NOT a secure capability. Owner aliases are EXTERNAL.")),
 ("IX41_03_EXACTLY_ONCE_UNPROVEN",("r41","int fm41_complete(FM41TicketRef ticket)"),("r41","* Exactly one CAS winner can call leave; nobody enforces completion.")),
 ("IX41_04_OS_QUIESCENCE_UNKNOWN",("r31","if (r31_immediate_stop_status!=noErr) {"),("r41","/* Sealing cannot prove OS quiescence or physical cutoff. */")),
 ("IX41_05_PHYSICAL_CUTOFF_UNKNOWN",("r31","/* CRITICAL: OS stop failed."),("h41","* NOT an Apple CoreAudio callback, security capability, or production API.")),
 ("IX41_06_CAPACITY_FOUR_FINITE",("h41","#define FM41_MAX_LIFETIME_TICKETS 4u"),("r41","static FM41PrivateSlot fm41_slots[FM41_MAX_LIFETIME_TICKETS]={")),
 ("IX41_07_HANDLE_COPIABLE",("h41","typedef struct { unsigned slot_id; } FM41TicketRef;"),("h41","* Ticket indices are COPYABLE / FORGEABLE.")),
 ("IX41_08_PREMATURE_FORGED_COMPLETION",("r41","FM41PrivateSlot *slot=&fm41_slots[ticket.slot_id-1u];"),("r41","&slot->phase,&expected,FM41_FINISHED,")),
 ("IX41_09_OWNER_OUT_EXTERNAL_ALIAS",("r41","*owner_out=owner;"),("r40","*owner_out=owner;")),
 ("IX41_10_STICKY_FAULT_NOT_OS_STOP",("r41","static atomic_uint fm41_fault_latch=ATOMIC_VAR_INIT(0u);"),("r41","* The sticky fault mask records selected local errors, not OS quiescence.")),
 ("IX41_11_STICKY_FAULT_ADMISSION_RACE",("r41","if (fm41_fault_snapshot()!=0u) return -1;"),("r41","if (fm41_fault_snapshot()!=0u) {")),
 ("IX41_12_FAILED_ADMISSION_SLOT_BURN",("r41","FM41_REJECTED,memory_order_release"),("r41","* Fixed four process-lifetime slots, NEVER RECYCLED.")),
 ("IX41_13_LEAVE_FAILURE_COUNTER_UNKNOWN",("r41","if (status!=0) fm41_latch(FM41_FAULT_LEAVE_FAILURE);"),("r36","int fm36_leave(void *userdata)")),
 ("IX41_14_NULL_OWNER_COMPENSATION",("r41","int leave_status=fm36_leave(userdata);"),("r41","if (leave_status!=0) fm41_latch(FM41_FAULT_LEAVE_FAILURE);")),
 ("IX41_15_REGISTER_ONE_SHOT_FAILURE",("r41","fm36_prepare_once(owner,userdata_out)"),("r36","static atomic_flag fm36_one_shot_claim=ATOMIC_FLAG_INIT;")),
 ("IX41_16_NO_GLOBAL_HAPPENS_BEFORE",("r31","AudioQueueEnqueueBuffer(ctx->queue,buf,0,NULL)"),("r31","ctx->queue=NULL;")),
 ("IX41_17_C40_C41_NOT_INTEGRATED",("r40","int fm40_begin(void *userdata,FM40Ticket **ticket_out,void **owner_out)"),("r41","int fm41_begin(void *userdata,FM41TicketRef *ticket_out,void **owner_out)")),
 ("IX41_18_FOUR_SLOTS_ARE_NOT_QUOTA_PLAN",("r41","* capacity-limited research candidate, NOT suitable for unbounded callbacks."),("r41","FM41_FAULT_CAPACITY")),
 ("IX41_19_SOURCE_ONLY_AND_NO_PHYSICAL_PROOF",("r41","* Compile-only, never linked/loaded/called, no CoreAudio/physical output."),("r31","/* GEN-R3: unconditional hard denial")),
)
CONTRACTS=(
 ("R41_FIXED_LIFETIME_CAPACITY","FOUR_NONRECYCLED_SLOTS","UNBOUNDED_CALLBACKS=NOT_SUPPORTED"),
 ("R41_INDEX_HANDLE","NO_TICKET_POINTER_EXPOSED","HANDLE_COPY_FORGERY=NOT_PREVENTED"),
 ("R41_STICKY_FAULT","ATOMIC_FETCH_OR","OS_STOP=NOT_PROVEN"),
 ("R41_ADMISSION","R36_GATE_BEFORE_OWNER_OUT","EXTERNAL_OWNER_LIFETIME=NOT_PROVEN"),
 ("R41_COMPLETE","ACTIVE_TO_FINISHED_CAS","EXACTLY_ONCE=NOT_PROVEN"),
 ("R41_NATIVE_SCOPE","COMPILED_UNLINKED","NO_OS_CALLBACKS_OR_PHYSICAL_MEASUREMENTS"),
)
LIMITATIONS=(
 "NO_REAL_OS_CALLBACKS_EXECUTED",
 "NO_SCIENTIFIC_OR_SCHEDULING_SIMULATION",
 "NO_PRODUCTION_TICKET_CAPACITY_OR_RECYCLING",
 "INDEX_HANDLES_ARE_COPYABLE_AND_FORGEABLE",
 "NO_OWNER_ALIAS_LIFETIME_ENFORCEMENT",
 "FAULT_LATCH_IS_NOT_AN_OS_STOP",
 "NO_EXACTLY_ONCE_COMPLETION_PROOF",
 "NO_PHYSICAL_CUTOFF_OR_BIOLOGICAL_TEST",
 "NO_SIGNED_BUREAU_CERTIFICATION",
)
class R41Error(ValueError): pass
def require(ok,msg):
    if not ok: raise R41Error(msg)
def sha(x): return hashlib.sha256(x).hexdigest()

def fn(src,name):
    matches=list(re.finditer(r"^(?:static\s+)?(?:int|unsigned|void)\s+"+
                  re.escape(name)+r"\s*\([^;]*\)\s*\{",src,re.M|re.S))
    require(len(matches)==1,"R41 function signature missing/duplicated "+name)
    a=matches[0].start()
    pos=src.index("{",a)
    d=0
    for i in range(pos,len(src)):
        if src[i]=="{":d+=1
        elif src[i]=="}":
            d-=1
            if d==0:return src[a:i+1]
    raise R41Error("Unbalanced source "+name)
def ordered(src,parts,name):
    require(all(x in src for x in parts),"Missing "+name+" source contract")
    pos=[src.index(x) for x in parts]
    require(pos==sorted(pos) and len(set(pos))==len(pos),
            "Order drift in "+name+" C11 contract")
def observe(c41,h41,c40,h40,c39,c31,c36,c37):
    r40.observe(c40,h40,c39,c31,c36,c37)
    require(c41.startswith("/* SPDX-License-Identifier: Apache-2.0 */") and
            h41.startswith("/* SPDX-License-Identifier: Apache-2.0 */"),
            "R41 license/source header mismatch")
    for forbidden in ("AudioQueueStart(","AudioQueueStop(","AudioQueueNewOutput(",
         "AudioQueueDispose(","AudioQueueEnqueueBuffer(","AudioDeviceStart(",
         "malloc(","calloc(","free(","realloc(","pthread_create(",
         "dlopen(","dlsym("):
        require(forbidden not in c41,"R41 prohibited output or allocator "+forbidden)
    require(h41.count("typedef struct { unsigned slot_id; } FM41TicketRef;")==1 and
            "#define FM41_INVALID_SLOT 0u" in h41 and
            "#define FM41_MAX_LIFETIME_TICKETS 4u" in h41,
            "R41 public index handle ABI changed")
    require(c41.count("{ATOMIC_VAR_INIT(FM41_UNUSED),NULL}")==4 and
            "static FM41PrivateSlot fm41_slots[FM41_MAX_LIFETIME_TICKETS]" in c41 and
            "static atomic_uint fm41_fault_latch=ATOMIC_VAR_INIT(0u);" in c41,
            "R41 private monotonic slot/fault storage altered")
    for api in ("fm41_register_owner_once","fm41_begin","fm41_complete",
                "fm41_seal"):
        require("int "+api+"(" in h41,"R41 header missing API "+api)
        fn(c41,api)
    require("unsigned fm41_fault_snapshot(void);" in h41,
            "R41 error snapshot API not declared")
    fn(c41,"fm41_fault_snapshot")
    for dep in ("fm36_prepare_once","fm36_mark_exposed","fm36_try_enter",
                "fm36_leave","fm36_seal"):
        require("extern int "+dep+"(" in c41,"R41 R36 ABI dependency missing")
    latch=fn(c41,"fm41_latch")
    require("atomic_fetch_or_explicit(&fm41_fault_latch,fault,memory_order_acq_rel)" in latch,
            "R41 fault record not monotonic atomic OR")
    snapshot=fn(c41,"fm41_fault_snapshot")
    require("atomic_load_explicit(&fm41_fault_latch,memory_order_acquire)" in snapshot,
            "R41 snapshot no acquire load")
    registration=fn(c41,"fm41_register_owner_once")
    ordered(registration,("*userdata_out=NULL;",
         "fm36_prepare_once(owner,userdata_out)",
         "fm36_mark_exposed(*userdata_out)"),"R41 registration")
    begin=fn(c41,"fm41_begin")
    ordered(begin,("ticket_out->slot_id=FM41_INVALID_SLOT;","*owner_out=NULL;",
          "if (fm41_fault_snapshot()!=0u) return -1;",
          "for (size_t i=0u;i<FM41_MAX_LIFETIME_TICKETS;i++) {",
          "&slot->phase,&expected,FM41_RESERVED,",
          "if (fm41_fault_snapshot()!=0u) {",
          "fm36_try_enter(userdata,&owner)",
          "slot->token=userdata;",
          "FM41_ACTIVE,memory_order_release",
          "*owner_out=owner;",
          "ticket_out->slot_id=(unsigned)i+1u;"),"R41 admission")
    require(begin.count("FM41_REJECTED,memory_order_release")==3 and
            "fm41_latch(FM41_FAULT_CAPACITY);" in begin and
            "(void)fm36_leave(userdata)" not in begin and
            "int leave_status=fm36_leave(userdata);" in begin,
            "R41 rejected admission must be sticky and slot unrecycled")
    ending=fn(c41,"fm41_complete")
    ordered(ending,("if (ticket.slot_id==FM41_INVALID_SLOT ||",
        "ticket.slot_id>FM41_MAX_LIFETIME_TICKETS)",
        "FM41PrivateSlot *slot=&fm41_slots[ticket.slot_id-1u];",
        "&slot->phase,&expected,FM41_FINISHED,",
        "int status=fm36_leave(slot->token);",
        "if (status!=0) fm41_latch(FM41_FAULT_LEAVE_FAILURE);"),
        "R41 at-most-once indexed completion")
    require(ending.count("fm36_leave(")==1 and
            "fm41_latch(FM41_FAULT_INVALID_HANDLE);" in ending and
            "fm41_latch(FM41_FAULT_DUPLICATE_LEAVE);" in ending,
            "R41 index bounds and repeat leave refusal missing")
    seal=fn(c41,"fm41_seal")
    require("int status=fm36_seal(userdata);" in seal and
            "if (status!=0) fm41_latch(FM41_FAULT_SEAL);" in seal,
            "R41 seal failure not latched")
    for prior in (c31,c36,c37,c39,c40):
        require("fm41_" not in prior,"R41 unexpectedly integrated into older C")
    require("AudioQueueNewOutput(&fmt,output_callback,ctx" in c31,
            "R41 true C31 OS userdata changed")
    require(len(FINDINGS)==19 and len(ANCHORS)==19 and
            sum(x[1]=="CRITICAL" for x in FINDINGS)==5 and
            [x[0] for x in FINDINGS]==[x[0] for x in ANCHORS] and
            len(CONTRACTS)==6,"R41 proof ledger cardinality drift")
    allsrc={"r31":c31,"r36":c36,"r37":c37,"r39":c39,
            "r40":c40,"h40":h40,"r41":c41,"h41":h41}
    for ident,a,b in ANCHORS:
        for scope,needle in (a,b):
            require(needle in allsrc[scope],"R41 missing proof anchor "+ident+": "+needle)
    return {x[0]:"OPEN_NOT_PROVEN" for x in FINDINGS}
def inspect(root,override=None,header_override=None):
    root=Path(root).resolve()
    table,manifest=r17.manifest_integrity(root)
    require(len(table)==236,"R41 exactly 236 SHA-pinned source files required")
    new=(CANDIDATE,HEADER,"audits/r41_capacity_alias_failure_review.py",
         "tests/test_r41_capacity_alias_failure_review.py",
         "RUN_GEN_R41_MAC_INTEL.command",
         "docs/GEN_R41_CAPACITY_ALIAS_ARCHITECTURE.md",
         "docs/GEN_R41_BUREAU_GATE_REVIEW.md",
         "docs/GEN_R41_FAILURE_CONTAINMENT_MATRIX.md")
    require(all(x in table for x in new),"R41 new files not pinned")
    earlier=r40.inspect(root)
    for key in ("r31","r36","r37","r39","r40","h40"):
        require(earlier[2][key]==table[FILES[key]],
                "R41 historical source unexpectedly altered "+key)
    require(table[r26.ORIGINAL]==r19.PINNED_ACOUSTIC_SHA256,
            "R41 original native generator changed")
    raw={key:(root/path).read_bytes() for key,path in FILES.items()}
    require(all(sha(raw[key])==table[path] for key,path in FILES.items()),
            "R41 source hash mismatch")
    val={k:x.decode("utf-8") for k,x in raw.items()}
    checks=observe(val["r41"] if override is None else override,
                   val["h41"] if header_override is None else header_override,
                   val["r40"],val["h40"],val["r39"],val["r31"],
                   val["r36"],val["r37"])
    runner=(root/"RUN_GEN_R41_MAC_INTEL.command").read_text(encoding="utf-8")
    require(set(r17.link_sources(runner))==r17.LINK_C_ALLOWLIST,
            "R41 nonemitting executable source allowlist drift")
    parts=runner.split(' -o "$WORK/freqmed-gen"')
    require(len(parts)==2,"R41 executable linker command absent")
    link=parts[1].split("-framework CoreAudio",1)[0]
    require("output_hard_denied.c" in link,"R41 no-output CLI missing")
    for unwanted in ("r41_index_ticket.c","r40_opaque_ticket.c",
        "r39_owner_lifetime_exit_ticket.c","r37_callback_lease_adapter.c",
        "r36_stable_userdata_anchor.c","acoustic_macos_r31.c",
        "r28_callback_admission_gate.c","src/acoustic_macos.c"):
        require(unwanted not in link,"R41 forbidden source linked "+unwanted)
    for flag in ("R41_CAPACITY_ALIAS_FAILURE_REVIEW=PASS",
       "R41_INDEX_TICKET_OBJECT=COMPILED_UNLINKED",
       "R41_OPAQUE_TICKET_OBJECT=COMPILED_UNLINKED",
       "R41_EXIT_TICKET_OBJECT=COMPILED_UNLINKED",
       "R41_CALLBACK_LEASE_OBJECT=COMPILED_UNLINKED",
       "R41_STABLE_ANCHOR_OBJECT=COMPILED_UNLINKED",
       "R41_R31_CANDIDATE_OBJECT=COMPILED_UNLINKED",
       "R41_NONEMITTING_EXECUTABLE_SYMBOL_AUDIT=PASS",
       "R41_BUREAU_PROOF_DOSSIER=44_FILES_SHA256_PASS",
       "R41_TESTCASE_RUN_SLOT=PASS",
       "FREQMED_GEN_R41_EVIDENCE_DIR","FREQMED_GEN_R41_BINARY"):
        require(flag in runner,"R41 runner protection missing "+flag)
    return table,manifest,{k:sha(raw[k]) for k in FILES},checks
def anchor(src,path,needle,digest):
    require(needle in src,"R41 witness absent "+needle)
    return {"path":path,"line":src.count("\n",0,src.index(needle))+1,
            "sha256":digest,"exact_text":needle}
def audit(root,archive_r19,reports):
    table,manifest,digests,checks=inspect(root)
    previous=r40.audit(root,archive_r19,reports)
    actual=json.loads(Path(reports["r40"]).read_text(encoding="utf-8"))
    require(previous==actual,"R41 historic R40 report could not be recalculated")
    require(previous["r40_findings_open"]==18 and
        previous["r40_critical_open"]==5 and
        previous["r39_findings_open"]==16 and
        previous["r38_findings_open"]==18 and
        previous["r37_findings_open"]==14 and
        previous["r36_findings_open"]==12 and
        previous["r35_findings_open"]==12 and
        previous["r34_findings_open"]==14 and
        previous["r33_findings_open"]==12 and
        previous["r32_findings_open"]==10 and
        previous["r31_findings_open"]==8 and
        previous["r30_findings_open"]==12 and
        previous["r29_findings_open"]==7 and
        previous["r28_gates_open"]==5 and
        previous["r27_findings_open"]==9 and
        previous["r23_obligations_open"]==15 and
        previous["r24_findings_open"]==7 and
        previous["bureau_gates_open"]==11 and
        previous["bureau_gates_resolved"]==0,
        "R41 historical Bureau controls improperly cleared")
    sources={key:(Path(root)/path).read_text(encoding="utf-8")
             for key,path in FILES.items()}
    entries=[]
    for (fid,severity,seat,problem),(anchor_id,a,b) in zip(FINDINGS,ANCHORS):
        require(fid==anchor_id,"R41 ledger mismatch")
        entries.append({"id":fid,"severity":severity,"seat":seat,
           "status":checks[fid],"obligation":problem,
           "real_OS_callback_executed":False,
           "source_anchors":[anchor(sources[k],FILES[k],txt,digests[k])
                             for k,txt in (a,b)]})
    return {
       "schema":SCHEMA,"verdict":VERDICT,
       "method":"SHA_PINNED_SOURCE_ONLY_INDEX_TICKET_FAILURE_CONTAINMENT",
       "manifest_sha256":manifest,"source_count":len(table),
       "source_digests":digests,
       "r40_report_sha256":sha(Path(reports["r40"]).read_bytes()),
       "r41_findings":entries,"r41_findings_open":19,"r41_critical_open":5,
       "r41_contracts":[{"id":x[0],"source":x[1],"limit":x[2]} for x in CONTRACTS],
       "r41_private_process_lifetime_slots":4,
       "r41_slot_reuse":False,
       "r41_index_handle_copyable":True,
       "r41_index_handle_forgeable":True,
       "r41_sticky_fault_mask":True,
       "r41_sticky_fault_is_OS_stop":False,
       "r41_exactly_once_completion":"NOT_PROVEN",
       "r41_owner_alias_lifetime":"NOT_PROVEN",
       "r41_real_callback_integrated":False,
       "r41_real_OS_callbacks":0,
       "r41_existing_C_modified":False,
       "r40_findings_open":18,"r40_critical_open":5,
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
       "r24_findings_open":7,"bureau_gates_open":11,"bureau_gates_resolved":0,
       "C11_race_freedom":"NOT_PROVEN",
       "OS_callback_quiescence":"NOT_PROVEN",
       "physical_cutoff":"NOT_PROVEN",
       "Bureau_certification":"PENDING",
       "scientific_simulation":"NONE","physical_emission":"NONE",
       "acoustic_output":"LOCKED","em_output":"LOCKED",
       "real_output":"NOT_AUTHORIZED","biological_exposure":"NOT_AUTHORIZED",
       "production":"NOT_AUTHORIZED","limitations":list(LIMITATIONS),
    }
def markdown(report):
    rows=["| "+x["id"]+" | "+x["severity"]+" | OPEN_NOT_PROVEN |"
          for x in report["r41_findings"]]
    return ("# GEN-R41 — Index Ticket Capacity, Alias & Failure Containment\n\n"
       "**Verdict: INDEX_TICKET_FAULT_CONTAINMENT_REVIEWABLE_OS_OWNER_COMPLETION_NOT_PROVEN.**\n\n"
       "A static index avoids returning a ticket object pointer but is copyable "
       "and forgeable. Four never-recycled slots and sticky fault bits provide "
       "local fail-closed signals only. No real OS callback or physical output.\n\n"
       "| Finding | Severity | Status |\n|---|---|---|\n"
       +"\n".join(rows)+"\n\n"
       "R41: 19 OPEN / 5 CRITICAL; R40: 18/5; R39: 16/4; "
       "historical Bureau: 11 OPEN / 0 resolved. No simulation.\n\n"
       "NEVER_SIMULATION=ENFORCED; ZERO_COST_FOSS=ENFORCED; "
       "ACOUSTIC_OUTPUT=LOCKED; EM_OUTPUT=LOCKED; REAL_OUTPUT=NOT_AUTHORIZED; "
       "BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED; PRODUCTION=NOT_AUTHORIZED.\n")
def main():
    p=argparse.ArgumentParser(description="GEN-R41 offline source-only C11 review")
    p.add_argument("--root",required=True,type=Path)
    p.add_argument("--archive-r19",required=True,type=Path)
    for n in range(16,41):
        p.add_argument("--r"+str(n),required=True,type=Path)
    p.add_argument("--json",required=True,type=Path)
    p.add_argument("--markdown",required=True,type=Path)
    args=p.parse_args()
    try:
        reports={"r"+str(n):getattr(args,"r"+str(n)) for n in range(16,41)}
        result=audit(args.root,args.archive_r19,reports)
        args.json.write_text(json.dumps(result,indent=2,sort_keys=True,
                            ensure_ascii=False)+"\n",encoding="utf-8")
        args.markdown.write_text(markdown(result),encoding="utf-8")
    except (R41Error,r40.R40Error,r39.R39Error,r38.R38Error,r37.R37Error,
            r36.R36Error,r35.R35Error,r34.R34Error,r33.R33Error,
            r32.R32Error,r31.R31Error,r30.R30Error,r29.R29Error,
            r28.R28Error,r27.R27Error,r26.R26Error,
            ValueError,TypeError,KeyError,IndexError,OSError,UnicodeError) as error:
        print("R41_CAPACITY_ALIAS_FAILURE_REVIEW=FAIL_CLOSED",str(error))
        return 2
    print("R41_CAPACITY_ALIAS_FAILURE_REVIEW=PASS")
    print("R41_FINDINGS=19_OPEN; R41_CRITICAL=5_OPEN")
    print("R41_FIXED_CAPACITY=4_PROCESS_LIFETIME; REUSE=NO")
    print("R41_INDEX_HANDLE=COPYABLE_FORGEABLE_NOT_A_CAPABILITY")
    print("R41_STICKY_FAULT=ATOMIC_LOCAL_ONLY; OS_STOP=NOT_PROVEN")
    print("R41_R40_FINDINGS=18_OPEN; R41_R39_FINDINGS=16_OPEN")
    print("R41_BUREAU_GATES=11_OPEN; R41_BUREAU_RESOLVED=0")
    print("R41_REVIEW_VERDICT="+VERDICT)
    print("R41_EXACTLY_ONCE=NOT_PROVEN; R41_OWNER_LIFETIME=NOT_PROVEN")
    print("R41_OS_QUIESCENCE=NOT_PROVEN; R41_PHYSICAL_CUTOFF=NOT_PROVEN")
    print("R41_PHYSICAL_EMISSION=NONE; R41_SCIENTIFIC_SIMULATION=NONE")
    return 0
if __name__=="__main__":
    raise SystemExit(main())
