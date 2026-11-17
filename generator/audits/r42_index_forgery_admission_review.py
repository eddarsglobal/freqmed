#!/usr/bin/env python3
"""GEN-R42 independent index-forgery, admission CAS and capacity remediation.
SHA-pinned REAL SOURCE evidence only. No execution of callbacks, scheduling
simulations, CoreAudio, instruments, emission or biological trials.
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
import r41_capacity_alias_failure_review as r41

SCHEMA="FREQMED_GEN_R42_INDEX_FORGERY_ATOMIC_ADMISSION_CAPACITY_PROOF_GATES"
VERDICT="CLOSED_COUNT_ATOMIC_RESERVATION_REVIEWED_OWNER_OS_AND_CAPACITY_PROOFS_OPEN"
CANDIDATE="candidates/r42_admission_gate_ticket.c"
HEADER="candidates/r42_admission_gate_ticket.h"
FILES={"r31":r31.CANDIDATE,"r36":r36.CANDIDATE,
       "r37":r37.CANDIDATE,"r39":r39.CANDIDATE,
       "r40":r40.CANDIDATE,"h40":r40.HEADER,
       "r41":r41.CANDIDATE,"h41":r41.HEADER,
       "r42":CANDIDATE,"h42":HEADER}
FINDINGS=(
 ("IX42_01_C31_REAL_OS_CTX_UNCHANGED","CRITICAL","B07","Real callback user data is still ctx, not a static gate token"),
 ("IX42_02_OWNER_LIFETIME_ALIASES","CRITICAL","B09","External owner aliases and lifetime remain uncontrolled"),
 ("IX42_03_VALID_POINTER_FORGERY","CRITICAL","B09","Opaque private address still forgeable if observed/leaked"),
 ("IX42_04_POST_CLOSURE_PUBLICATION_RACE","CRITICAL","B09","Existing reservation can publish after gate closure"),
 ("IX42_05_UNBOUNDED_CAPACITY_NOT_SUPPORTED","CRITICAL","B09","Four process-lifetime tickets cannot support unbounded callbacks"),
 ("IX42_06_PHYSICAL_STOP_NOT_PROVEN","CRITICAL","B10","No OS stop or physical cutoff evidence"),
 ("IX42_07_MISSED_COMPLETE_NOT_RECOVERED","HIGH","B09","At-most-once does not establish eventual completion"),
 ("IX42_08_R36_PRE_ADMISSION_TOKEN_NOT_INTEGRATED","HIGH","B07","R36 static token not passed to real callback OS ABI"),
 ("IX42_09_SINGLE_GATE_CAS_SCOPE_LOCAL","HIGH","B09","Closed/count CAS provides local reservation ordering, not global OS HB"),
 ("IX42_10_SATURATION_CONSUMES_PERMITS","HIGH","B09","Count is monotone and never replenished"),
 ("IX42_11_FAILED_ADMISSION_CONSUMES_SLOT","HIGH","B09","Rejected slot remains unavailable"),
 ("IX42_12_COMPENSATION_FAILURE_REMAINS","HIGH","B09","R36 leave may fail after null owner or closure cancellation"),
 ("IX42_13_COMPLETION_STOLEN_BY_ALIAS","HIGH","B09","Valid opaque pointer copy can complete a different caller's ticket"),
 ("IX42_14_INVALID_POINTER_REFUSAL_SCOPE","HIGH","B09","Address membership check not a capability authentication"),
 ("IX42_15_GATE_FAULT_OBSERVABILITY_ORDER","HIGH","B09","Closed gate becomes visible before reason word; not OS evidence"),
 ("IX42_16_EXPOSURE_FAILURE_RETAINS_OWNER","HIGH","B09","One-shot R36 claim must retain owner on registration failure"),
 ("IX42_17_FAILED_OS_DISPOSE_UNKNOWN","HIGH","B07","AudioQueueStop/Dispose errors and callback quiescence untested"),
 ("IX42_18_SHARED_CTX_HB_UNKNOWN","HIGH","B09","C11 context PCM/queue field race freedom unproven"),
 ("IX42_19_COMPILE_ONLY_EVIDENCE_LIMIT","HIGH","B10","Clang and SHA source checks cannot prove physical safety"),
 ("IX42_20_NO_INDEPENDENT_CERTIFICATION","HIGH","B10","Bureau gates and external authority still open"),
)
ANCHORS=(
 ("IX42_01_C31_REAL_OS_CTX_UNCHANGED",("r31","AudioQueueNewOutput(&fmt,output_callback,ctx"),("r31","queue_running_listener,ctx)")),
 ("IX42_02_OWNER_LIFETIME_ALIASES",("r36","_Atomic(void *) owner;"),("r42","* Owner lifetime, exactly-once completion and physical cutoff UNPROVEN.")),
 ("IX42_03_VALID_POINTER_FORGERY",("h42","* Opaque pointer may be copied/forged if its valid address becomes known."),("r42","* disclosure, address forgery, illicit memory access, or missed completion.")),
 ("IX42_04_POST_CLOSURE_PUBLICATION_RACE",("r42","* transition; an already reserved admission may still publish afterwards."),("r42","* observed gate check; there is no publication/closure joint CAS.")),
 ("IX42_05_UNBOUNDED_CAPACITY_NOT_SUPPORTED",("h42","#define FM42_LIFETIME_CAPACITY 4u"),("r42","* Four process-lifetime slots are never reused; exhaustion closes locally.")),
 ("IX42_06_PHYSICAL_STOP_NOT_PROVEN",("r31","/* CRITICAL: OS stop failed."),("r42","* callbacks are NOT drained by this local operation.")),
 ("IX42_07_MISSED_COMPLETE_NOT_RECOVERED",("r42","int fm42_complete(FM42Ticket *ticket)"),("r42","* At-most-once CAS prevents double leave, NOT absent or stolen exits.")),
 ("IX42_08_R36_PRE_ADMISSION_TOKEN_NOT_INTEGRATED",("r36","static atomic_flag fm36_one_shot_claim=ATOMIC_FLAG_INIT;"),("r42","fm36_prepare_once(owner,userdata_out)")),
 ("IX42_09_SINGLE_GATE_CAS_SCOPE_LOCAL",("r42","static atomic_uint fm42_gate=ATOMIC_VAR_INIT(0u);"),("r42","&fm42_gate,&state,desired,")),
 ("IX42_10_SATURATION_CONSUMES_PERMITS",("r42","if ((state & FM42_COUNT_MASK)>=FM42_LIFETIME_CAPACITY) {"),("r42","fm42_latch(FM42_FAULT_CAPACITY); return -1;")),
 ("IX42_11_FAILED_ADMISSION_CONSUMES_SLOT",("r42","FM42_REJECTED,memory_order_release"),("r42","* Four process-lifetime slots are never reused; exhaustion closes locally.")),
 ("IX42_12_COMPENSATION_FAILURE_REMAINS",("r42","int rc=fm36_leave(userdata);"),("r42","if (rc!=0) fm42_latch(FM42_FAULT_LEAVE);")),
 ("IX42_13_COMPLETION_STOLEN_BY_ALIAS",("r42","if (ticket!=slot) continue;"),("r42","* guessed valid private address may still prematurely complete the ticket.")),
 ("IX42_14_INVALID_POINTER_REFUSAL_SCOPE",("r42","fm42_latch(FM42_FAULT_BAD_TICKET);"),("h42","typedef struct FM42Ticket FM42Ticket;")),
 ("IX42_15_GATE_FAULT_OBSERVABILITY_ORDER",("r42","atomic_fetch_or_explicit(&fm42_gate,FM42_CLOSED,memory_order_acq_rel)"),("r42","atomic_fetch_or_explicit(&fm42_faults,fault,memory_order_acq_rel)")),
 ("IX42_16_EXPOSURE_FAILURE_RETAINS_OWNER",("r42","fm36_mark_exposed(*userdata_out)"),("r42","* if exposure/registration fails, by EXTERNAL lifetime contract.")),
 ("IX42_17_FAILED_OS_DISPOSE_UNKNOWN",("r31","if (AudioQueueDispose(ctx->queue,true)!=noErr) {"),("r42","* This is NOT a global callback quiescence or OS stop guarantee.")),
 ("IX42_18_SHARED_CTX_HB_UNKNOWN",("r31","AudioQueueEnqueueBuffer(ctx->queue,buf,0,NULL)"),("r31","ctx->queue=NULL;")),
 ("IX42_19_COMPILE_ONLY_EVIDENCE_LIMIT",("r42","* COMPILE ONLY: never link/load/call/dispatch, no CoreAudio or EM output."),("r31","/* GEN-R3: unconditional hard denial")),
 ("IX42_20_NO_INDEPENDENT_CERTIFICATION",("h42","* NO security capability or production certification is implied."),("r42","* Owner lifetime, exactly-once completion and physical cutoff UNPROVEN.")),
)
CONTRACTS=(
 ("G42_ATOMIC_RESERVATION","ONE_CLOSED_COUNT_CAS","NO_NEW_RESERVATION_AFTER_CLOSED"),
 ("G42_CAPACITY","FOUR_PROCESS_LIFETIME_PERMITS","NO_UNBOUNDED_CALLBACK_CAPACITY"),
 ("G42_OPAQUE_IDENTITY","PRIVATE_STATIC_POINTER_SLOTS","VALID_POINTER_FORGERY_NOT_PREVENTED"),
 ("G42_CANCEL","COMPENSATING_R36_LEAVE_ON_DETECTED_CLOSE","R36_LEAVE_FAILURE_OPEN"),
 ("G42_FAULT","CLOSE_GATE_THEN_PUBLISH_REASON","NO_OS_QUIESCENCE_OR_PHYSICAL_STOP"),
 ("G42_COMPLETION","CAS_ACTIVE_TO_FINISHED_ONCE","EXACTLY_ONCE_NOT_PROVEN"),
)
LIMITATIONS=(
 "NO_CANDIDATE_C_CODE_EXECUTION_OR_OS_CALLBACK",
 "NO_SIMULATION_OF_INTERLEAVINGS_OR_SCIENCE",
 "NO_AUTHENTICATED_TICKET_CAPABILITY",
 "NO_CAPACITY_SOLUTION_FOR_UNBOUNDED_CALLBACKS",
 "EXISTING_RESERVATIONS_MAY_COMPLETE_AFTER_LOCAL_CLOSURE",
 "NO_EXTERNAL_OWNER_MEMORY_LIFETIME_PROOF",
 "NO_EXACTLY_ONCE_COMPLETION_OR_C11_GLOBAL_RACE_PROOF",
 "NO_OS_CALLBACK_QUIESCENCE_OR_PHYSICAL_MEASUREMENT",
 "NO_BUREAU_INDEPENDENT_SIGNATURES",
)
class R42Error(ValueError): pass
def require(cond,why):
    if not cond: raise R42Error(why)
def sha(data): return hashlib.sha256(data).hexdigest()

def fn(src,name):
    pat=r"^(?:static\s+)?(?:int|unsigned|void)\s+"+re.escape(name)+r"\s*\([^;]*\)\s*\{"
    hits=list(re.finditer(pat,src,re.M|re.S))
    require(len(hits)==1,"R42 C function missing/duplicated "+name)
    start=hits[0].start()
    brace=src.index("{",hits[0].start())
    depth=0
    for p in range(brace,len(src)):
        if src[p]=="{": depth+=1
        elif src[p]=="}":
            depth-=1
            if depth==0:return src[start:p+1]
    raise R42Error("R42 C function braces unbalanced "+name)

def ordered(body,parts,label):
    require(all(p in body for p in parts),"R42 missing "+label+" required token")
    pos=[body.index(p) for p in parts]
    require(pos==sorted(pos) and len(set(pos))==len(pos),
            "R42 unsafe source order "+label)

def observe(c42,h42,c41,h41,c40,h40,c39,c31,c36,c37):
    r41.observe(c41,h41,c40,h40,c39,c31,c36,c37)
    require(c42.startswith("/* SPDX-License-Identifier: Apache-2.0 */")
            and h42.startswith("/* SPDX-License-Identifier: Apache-2.0 */"),
            "R42 license/method source header missing")
    for bad in ("AudioQueueStart(","AudioQueueStop(","AudioQueueNewOutput(",
                "AudioQueueDispose(","AudioQueueEnqueueBuffer(","AudioDeviceStart(",
                "malloc(","calloc(","free(","realloc(","pthread_create(",
                "dlopen(","dlsym("):
        require(bad not in c42,"R42 unsafe code path present "+bad)
    require(h42.count("typedef struct FM42Ticket FM42Ticket;")==1 and
            "struct FM42Ticket {" not in h42 and
            "#define FM42_LIFETIME_CAPACITY 4u" in h42,
            "R42 opaque API, capacity, or struct privacy drift")
    require(c42.count("struct FM42Ticket {")==1 and
            c42.count("static struct FM42Ticket fm42_slots[FM42_LIFETIME_CAPACITY]")==1 and
            c42.count("{ATOMIC_VAR_INIT(FM42_UNUSED),NULL}")==4 and
            "static atomic_uint fm42_gate=ATOMIC_VAR_INIT(0u);" in c42 and
            "static atomic_uint fm42_faults=ATOMIC_VAR_INIT(0u);" in c42 and
            "FM42_CLOSED=0x80000000u" in c42 and
            "FM42_COUNT_MASK=0x0000ffffu" in c42,
            "R42 private four tickets and shared closed/count gate altered")
    for dep in ("fm36_prepare_once","fm36_mark_exposed","fm36_try_enter",
                "fm36_leave","fm36_seal"):
        require("extern int "+dep+"(" in c42,"R42 missing R36 dependency "+dep)
    for api in ("fm42_register_owner_once","fm42_begin","fm42_complete",
                "fm42_seal"):
        require("int "+api+"(" in h42,"R42 public opaque API missing "+api)
        fn(c42,api)
    require("unsigned fm42_fault_snapshot(void);" in h42,
            "R42 public fault snapshot missing")
    latch=fn(c42,"fm42_latch")
    ordered(latch,("atomic_fetch_or_explicit(&fm42_gate,FM42_CLOSED,memory_order_acq_rel)",
                   "atomic_fetch_or_explicit(&fm42_faults,fault,memory_order_acq_rel)"),
            "close gate before fault reason")
    snapshot=fn(c42,"fm42_fault_snapshot")
    require("atomic_load_explicit(&fm42_faults,memory_order_acquire)" in snapshot,
            "R42 atomic fault snapshot missing")
    reserve=fn(c42,"fm42_reserve_permit")
    ordered(reserve,("atomic_load_explicit(&fm42_gate,memory_order_acquire)",
             "if ((state & FM42_CLOSED)!=0u) return -1;",
             "if ((state & FM42_COUNT_MASK)>=FM42_LIFETIME_CAPACITY) {",
             "unsigned desired=state+1u;",
             "&fm42_gate,&state,desired,"),
             "single-word close/count permit CAS")
    require("atomic_compare_exchange_weak_explicit(" in reserve and
            "memory_order_acq_rel,memory_order_acquire)) return 0;" in reserve and
            "fm42_latch(FM42_FAULT_CAPACITY)" in reserve,
            "R42 close/count CAS or capacity fail-closed missing")
    register=fn(c42,"fm42_register_owner_once")
    ordered(register,("*userdata_out=NULL;",
                      "fm36_prepare_once(owner,userdata_out)",
                      "fm36_mark_exposed(*userdata_out)"),"R42 registration")
    begin=fn(c42,"fm42_begin")
    ordered(begin,("if (!ticket_out || !owner_out) {",
                   "*ticket_out=NULL;","*owner_out=NULL;",
                   "if (fm42_reserve_permit()!=0) return -1;",
                   "&slot->phase,&expected,FM42_RESERVED,",
                   "fm36_try_enter(userdata,&owner)",
                   "slot->token=userdata;",
                   "FM42_ACTIVE,memory_order_release",
                   "*owner_out=owner;","*ticket_out=slot;"),
            "R42 admission and owner publication")
    require(begin.count("FM42_REJECTED,memory_order_release")==4 and
            begin.count("FM42_CLOSED)!=0u")==2 and
            begin.count("int rc=fm36_leave(userdata);")==2 and
            "fm42_latch(FM42_FAULT_INTERNAL);" in begin,
            "R42 strict post-reservation/after-admission closing and compensation absent")
    complete=fn(c42,"fm42_complete")
    ordered(complete,("if (!ticket) {",
                      "if (ticket!=slot) continue;",
                      "&slot->phase,&expected,FM42_FINISHED,",
                      "int rc=fm36_leave(slot->token);"),
            "R42 opaque ticket completion")
    require(complete.count("fm36_leave(")==1 and
            "fm42_latch(FM42_FAULT_DUPLICATE_EXIT)" in complete and
            "fm42_latch(FM42_FAULT_BAD_TICKET)" in complete and
            "if (rc!=0) fm42_latch(FM42_FAULT_LEAVE);" in complete,
            "R42 pointer membership, CAS or failure latch removed")
    seal=fn(c42,"fm42_seal")
    ordered(seal,("atomic_fetch_or_explicit(&fm42_gate,FM42_CLOSED,memory_order_acq_rel)",
                  "fm36_seal(userdata)"),"R42 seal order")
    for src in (c31,c36,c37,c39,c40,c41):
        require("fm42_" not in src,"R42 erroneously integrated into earlier C")
    require("AudioQueueNewOutput(&fmt,output_callback,ctx" in c31,
            "R42 actual OS callback handoff unexpectedly changed")
    require(len(FINDINGS)==20 and len(ANCHORS)==20 and
            sum(f[1]=="CRITICAL" for f in FINDINGS)==6 and
            len(CONTRACTS)==6 and
            [f[0] for f in FINDINGS]==[a[0] for a in ANCHORS],
            "R42 finding/contract ledger drift")
    sources={"r31":c31,"r36":c36,"r37":c37,"r39":c39,"r40":c40,
             "h40":h40,"r41":c41,"h41":h41,"r42":c42,"h42":h42}
    for ident,first,second in ANCHORS:
        for scope,needle in (first,second):
            require(needle in sources[scope],
                    "R42 exact source proof anchor missing "+ident+": "+needle)
    return {f[0]:"OPEN_NOT_PROVEN" for f in FINDINGS}

def inspect(root,override=None,header_override=None):
    root=Path(root).resolve()
    table,manifest=r17.manifest_integrity(root)
    require(len(table)==244,"R42 precisely 244 SHA pinned source files required")
    needed=(CANDIDATE,HEADER,
            "audits/r42_index_forgery_admission_review.py",
            "tests/test_r42_index_forgery_admission_review.py",
            "RUN_GEN_R42_MAC_INTEL.command",
            "docs/GEN_R42_ATOMIC_ADMISSION_DESIGN.md",
            "docs/GEN_R42_BUREAU_PROOF_GATES.md",
            "docs/GEN_R42_FORGERY_CAPACITY_MATRIX.md")
    require(all(p in table for p in needed),"R42 new source/audit/test/docs not pinned")
    prior=r41.inspect(root)
    for key in ("r31","r36","r37","r39","r40","h40","r41","h41"):
        require(prior[2][key]==table[FILES[key]],
                "R42 historic C unexpectedly changed "+key)
    require(table[r26.ORIGINAL]==r19.PINNED_ACOUSTIC_SHA256,
            "R42 original native generator source changed")
    raw={key:(root/path).read_bytes() for key,path in FILES.items()}
    require(all(sha(raw[key])==table[path] for key,path in FILES.items()),
            "R42 actual C/header bytes not SHA pinned")
    sources={key:raw[key].decode("utf-8") for key in FILES}
    checks=observe(sources["r42"] if override is None else override,
                   sources["h42"] if header_override is None else header_override,
                   sources["r41"],sources["h41"],sources["r40"],
                   sources["h40"],sources["r39"],sources["r31"],
                   sources["r36"],sources["r37"])
    runner=(root/"RUN_GEN_R42_MAC_INTEL.command").read_text(encoding="utf-8")
    require(set(r17.link_sources(runner))==r17.LINK_C_ALLOWLIST,
            "R42 nonemitting CLI source allowlist modified")
    chunks=runner.split(' -o "$WORK/freqmed-gen"')
    require(len(chunks)==2,"R42 hard-denied binary linker command missing")
    linker=chunks[1].split("-framework CoreAudio",1)[0]
    require("output_hard_denied.c" in linker,
            "R42 nonemitting binary missing denial implementation")
    for forbidden in ("r42_admission_gate_ticket.c","r41_index_ticket.c",
         "r40_opaque_ticket.c","r39_owner_lifetime_exit_ticket.c",
         "r37_callback_lease_adapter.c","r36_stable_userdata_anchor.c",
         "acoustic_macos_r31.c","r28_callback_admission_gate.c",
         "src/acoustic_macos.c"):
        require(forbidden not in linker,"R42 forbidden native source LINKED "+forbidden)
    for token in ("R42_INDEX_FORGERY_ADMISSION_REVIEW=PASS",
         "R42_ATOMIC_GATE_OBJECT=COMPILED_UNLINKED",
         "R42_INDEX_TICKET_OBJECT=COMPILED_UNLINKED",
         "R42_OPAQUE_TICKET_OBJECT=COMPILED_UNLINKED",
         "R42_EXIT_TICKET_OBJECT=COMPILED_UNLINKED",
         "R42_CALLBACK_LEASE_OBJECT=COMPILED_UNLINKED",
         "R42_STABLE_ANCHOR_OBJECT=COMPILED_UNLINKED",
         "R42_R31_CANDIDATE_OBJECT=COMPILED_UNLINKED",
         "R42_NONEMITTING_EXECUTABLE_SYMBOL_AUDIT=PASS",
         "R42_BUREAU_PROOF_DOSSIER=46_FILES_SHA256_PASS",
         "R42_TESTCASE_RUN_SLOT=PASS",
         "FREQMED_GEN_R42_EVIDENCE_DIR",
         "FREQMED_GEN_R42_BINARY"):
        require(token in runner,"R42 native review guard missing "+token)
    return table,manifest,{key:sha(raw[key]) for key in FILES},checks

def evidence(source,path,needle,digest):
    require(needle in source,"R42 evidence missing "+needle)
    return {"path":path,"line":source.count("\n",0,source.index(needle))+1,
            "sha256":digest,"source_text":needle}

def audit(root,archive_r19,reports):
    table,manifest,digests,checks=inspect(root)
    previous=r41.audit(root,archive_r19,reports)
    actual=json.loads(Path(reports["r41"]).read_text(encoding="utf-8"))
    require(previous==actual,"R42 historical R41 report recomputation mismatch")
    require(previous["r41_findings_open"]==19 and
            previous["r41_critical_open"]==5 and
            previous["r40_findings_open"]==18 and
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
            "R42 must keep old Bureau vetoes open")
    src={key:(Path(root)/path).read_text(encoding="utf-8")
         for key,path in FILES.items()}
    rows=[]
    for (fid,severity,seat,obligation),(ident,left,right) in zip(FINDINGS,ANCHORS):
        require(fid==ident,"R42 ledger identity mismatch")
        rows.append({"id":fid,"severity":severity,"seat":seat,
                     "status":checks[fid],"unproven_obligation":obligation,
                     "real_OS_callback_executed":False,
                     "source_anchors":[evidence(src[key],FILES[key],needle,
                                                digests[key])
                                       for key,needle in (left,right)]})
    return {"schema":SCHEMA,"verdict":VERDICT,
            "method":"SHA_PINNED_C11_SOURCE_ONLY_ATOMIC_GATE_AUDIT",
            "manifest_sha256":manifest,"sha_pinned_sources":len(table),
            "source_digests":digests,
            "r41_report_sha256":sha(Path(reports["r41"]).read_bytes()),
            "r42_findings":rows,"r42_findings_open":20,"r42_critical_open":6,
            "r42_contracts":[{"id":c[0],"contract":c[1],"limit":c[2]}
                              for c in CONTRACTS],
            "r42_gate":"SINGLE_C11_CLOSED_COUNT_CAS",
            "r42_permit_limit":4,"r42_slot_reuse":False,
            "r42_no_index_only_public_ticket":True,
            "r42_opaque_pointer_forgery":"NOT_PREVENTED",
            "r42_new_reservations_after_closed":"DENIED_BY_LOCAL_CAS",
            "r42_preexisting_reservation_publication_after_closed":"NOT_EXCLUDED",
            "r42_owner_lifetime":"NOT_PROVEN",
            "r42_exactly_once_completion":"NOT_PROVEN",
            "r42_real_OS_callbacks":0,
            "r42_integrated_into_C31":False,
            "r42_historical_C_edits":0,
            "r41_findings_open":19,"r41_critical_open":5,
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
            "r24_findings_open":7,
            "bureau_gates_open":11,"bureau_gates_resolved":0,
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
    lines=["| "+x["id"]+" | "+x["severity"]+" | OPEN_NOT_PROVEN |"
           for x in report["r42_findings"]]
    return ("# FREQMED GEN-R42 — Index Forgery, Admission Atomicity & Capacity\n\n"
      "**Verdict: CLOSED_COUNT_ATOMIC_RESERVATION_REVIEWED_OWNER_OS_AND_CAPACITY_PROOFS_OPEN.**\n\n"
      "A single atomic CAS orders new permit reservations against local closure, "
      "but pre-existing reservations can publish later. Four lifetime slots "
      "are not a production capacity plan. Opaque pointer tickets remove an "
      "index-only completion surface but do not prevent copied/forged addresses.\n\n"
      "| Finding | Severity | Status |\n|---|---|---|\n"
      +"\n".join(lines)+"\n\n"
      "R42 20 OPEN (6 CRITICAL), R41 19, R40 18, Bureau 11 OPEN/0 resolved.\n\n"
      "NEVER_SIMULATION=ENFORCED; ZERO_COST_FOSS=ENFORCED; "
      "ACOUSTIC_OUTPUT=LOCKED; EM_OUTPUT=LOCKED; REAL_OUTPUT=NOT_AUTHORIZED; "
      "BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED; PRODUCTION=NOT_AUTHORIZED.\n")

def main():
    p=argparse.ArgumentParser(description="GEN-R42 independent source-only C11 proof review")
    p.add_argument("--root",required=True,type=Path)
    p.add_argument("--archive-r19",required=True,type=Path)
    for n in range(16,42):
        p.add_argument("--r"+str(n),required=True,type=Path)
    p.add_argument("--json",required=True,type=Path)
    p.add_argument("--markdown",required=True,type=Path)
    args=p.parse_args()
    try:
        reports={"r"+str(n):getattr(args,"r"+str(n)) for n in range(16,42)}
        obj=audit(args.root,args.archive_r19,reports)
        args.json.write_text(json.dumps(obj,indent=2,sort_keys=True,
                             ensure_ascii=False)+"\n",encoding="utf-8")
        args.markdown.write_text(markdown(obj),encoding="utf-8")
    except (R42Error,r41.R41Error,r40.R40Error,r39.R39Error,r38.R38Error,
            r37.R37Error,r36.R36Error,r35.R35Error,r34.R34Error,
            r33.R33Error,r32.R32Error,r31.R31Error,r30.R30Error,
            r29.R29Error,r28.R28Error,r27.R27Error,r26.R26Error,
            ValueError,TypeError,KeyError,IndexError,OSError,UnicodeError) as err:
        print("R42_INDEX_FORGERY_ADMISSION_REVIEW=FAIL_CLOSED",str(err))
        return 2
    print("R42_INDEX_FORGERY_ADMISSION_REVIEW=PASS")
    print("R42_FINDINGS=20_OPEN; R42_CRITICAL=6_OPEN")
    print("R42_SINGLE_CAS_GATE=CLOSED_AND_COUNT; R42_MAX_PERMITS=4")
    print("R42_INDEX_ONLY_HANDLE=REMOVED; POINTER_FORGERY=NOT_PREVENTED")
    print("R42_CLOSED_NEW_RESERVATIONS=DENIED; EXISTING_RESERVATIONS=NOT_QUIESCED")
    print("R42_R41_FINDINGS=19_OPEN; R42_R40_FINDINGS=18_OPEN")
    print("R42_BUREAU_GATES=11_OPEN; R42_BUREAU_RESOLVED=0")
    print("R42_REVIEW_VERDICT="+VERDICT)
    print("R42_OWNER_LIFETIME=NOT_PROVEN; R42_EXACTLY_ONCE=NOT_PROVEN")
    print("R42_C11_RACE_FREEDOM=NOT_PROVEN; R42_OS_QUIESCENCE=NOT_PROVEN")
    print("R42_PHYSICAL_CUTOFF=NOT_PROVEN; R42_PHYSICAL_EMISSION=NONE")
    print("R42_SCIENTIFIC_SIMULATION=NONE")
    return 0
if __name__=="__main__":
    raise SystemExit(main())
