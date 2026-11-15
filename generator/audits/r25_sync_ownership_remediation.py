#!/usr/bin/env python3
"""GEN-R25 independent source-only C11/OS ownership remediation review.

9 proposed changes and a fail-closed ownership state-machine proposal are
documentary. No C fix is applied, no CoreAudio API called, no synthetic event
or measurement created, no scientific simulation or physical emission.
"""
import argparse
import hashlib
import json
from pathlib import Path

import r17_evidence_verifier as r17
import r19_adversarial_source_audit as r19
import r19_evidence_archive as archive19
import r23_happens_before_obligations as r23
import r24_shared_state_contract_audit as r24

SCHEMA = "FREQMED_GEN_R25_C11_OWNERSHIP_REMEDIATION_REVIEW"
VERDICT = "REMEDIATION_PLANS_REVIEWABLE_NOT_APPLIED"
STATUS = "PROPOSED_NOT_APPLIED"
STATES = (
    "UNPUBLISHED", "QUEUE_PUBLISHED", "SHUTDOWN_REQUESTED",
    "LISTENER_UNREGISTERED", "DISPOSAL_CONFIRMED",
    "DISPOSAL_UNCERTAIN", "QUARANTINED",
)
# Proposed *design* transitions, NOT a claim that source C implements them.
TRANSITIONS = (
    ("UNPUBLISHED", "QUEUE_PUBLISHED"),
    ("UNPUBLISHED", "QUARANTINED"),
    ("QUEUE_PUBLISHED", "SHUTDOWN_REQUESTED"),
    ("SHUTDOWN_REQUESTED", "LISTENER_UNREGISTERED"),
    ("SHUTDOWN_REQUESTED", "DISPOSAL_CONFIRMED"),
    ("SHUTDOWN_REQUESTED", "DISPOSAL_UNCERTAIN"),
    ("LISTENER_UNREGISTERED", "DISPOSAL_CONFIRMED"),
    ("LISTENER_UNREGISTERED", "DISPOSAL_UNCERTAIN"),
    ("DISPOSAL_UNCERTAIN", "QUARANTINED"),
)
# id, criticality, functional reviewer(s), R24 finding(s), R23 obligations,
# two real source anchors, concrete remediation design, proof obligation.
PLANS = (
    ("RM01_PCM_SINGLE_WRITER", "P1", ("B09","B07"),
     ("SH01_NONATOMIC_PCM_CONTROLLER_CALLBACK",),
     ("HB01","HB02","HB04"),
     ("fill_audio(ctx,b);", "fill_audio(ctx,buf)"),
     "Define a single writer domain for PCM phase and frame counters: move control prefill behind an explicitly proved callback-admission boundary OR use a common lock that every writer acquires before fill_audio. Do not accept callback-only locking as a fix.",
     "Independent C11 access matrix must show that every conflicting non-atomic PCM access is sequenced-before or synchronizes-with every other one; a documented CoreAudio admission contract is also required."),
    ("RM02_GATE_COVERAGE", "P1", ("B09",),
     ("SH07_C11_RELEASE_ACQUIRE_LIMIT",),
     ("HB03",),
     ("atomic_flag_test_and_set_explicit(&ctx->pcm_writer_gate",
      "atomic_flag_clear_explicit(&ctx->pcm_writer_gate"),
     "Review critical-section coverage, all early return paths and reentrancy. A common lock may be a candidate only if both controller and callback participate and locking never blocks a real-time callback indefinitely.",
     "Prove matching C11 acquire/release and that every write to the guarded PCM fields occurs within the same synchronization domain, without deadlock or unbounded real-time callback blocking."),
    ("RM03_PUBLICATION_TRANSFER", "P1", ("B07","B09"),
     ("SH01_NONATOMIC_PCM_CONTROLLER_CALLBACK",),
     ("HB05",),
     ("AudioQueueNewOutput(&fmt,output_callback,ctx",
      "AudioQueueStart(ctx->queue,NULL)"),
     "Propose an explicit ownership-transfer state from controller prefill to the callback domain and forbid fill_audio on the controller after transfer; preserve queue startup and buffer ownership invariants.",
     "Produce an API-contract-based ownership transfer and a C11 happens-before edge for all initialized non-atomic fields before the first legal callback access; confirm callback timing cannot race prefill."),
    ("RM04_USERDATA_ADMISSION_BARRIER", "P1", ("B07","B09"),
     ("SH03_ATOMIC_COUNTER_ENTRY_WINDOW",),
     ("Q02","Q03"),
     ("AcousticContext *ctx=(AcousticContext*)ptr;",
      "atomic_fetch_add_explicit(&ctx->active_output_callbacks"),
     "Add a documented no-new-callback admission barrier before free, not a counter-only test. Counter increments dereference userdata after the callback has already received the pointer.",
     "Demonstrate that no callback can obtain or dereference userdata after the barrier and all already entered callbacks have completed before heap reclamation, including failed OSStatus cases."),
    ("RM05_LISTENER_LIFETIME", "P1", ("B07","B09"),
     ("SH04_LISTENER_REMOVAL_QUIESCENCE",),
     ("Q04",),
     ("AudioQueueRemovePropertyListener(ctx->queue,",
      "atomic_fetch_add_explicit(&ctx->active_property_listeners"),
     "Represent property-listener registration, removal, in-flight invocation and uncertain OSStatus as distinct ownership states. A successful removal return must not be assumed to drain callbacks without an explicit contract.",
     "Obtain a precise API guarantee and independently review existing listener callback termination, late entry, and deregistration-failure ownership before permitting any free of callback userdata."),
    ("RM06_DISPOSE_SUCCESS_FREE_EDGE", "P1", ("B07","B09"),
     ("SH05_SUCCESSFUL_DISPOSAL_LIMIT",),
     ("Q05",),
     ("if (AudioQueueDispose(ctx->queue,true)!=noErr)",
      "const int context_quiescent="),
     "Make successful synchronous disposal and listener lifetime proof explicit mandatory preconditions for reclaiming userdata. Retain fallback quarantine if either premise is unknown.",
     "Establish the scope of Apple AudioQueueDispose success guarantees, absence of in-flight listener references and C11 ordering between callback exit and the final free before declaring the context quiescent."),
    ("RM07_EARLY_BIND_ERROR_OWNERSHIP", "P1", ("B07","B09"),
     ("SH06_DISPOSAL_ERROR_HEAP_RETENTION",),
     ("D01","D03"),
     ("const OSStatus bind_dispose_status=AudioQueueDispose(ctx->queue,true);",
      "listener_registration_uncertain=1;"),
     "Separate queue creation/bind rejection and listener registration errors in a documented state machine. If disposal or registration state is ambiguous, keep userdata alive and permanently refuse additional sessions.",
     "Trace each OSStatus path to an explicit queue/userdata owner, reason for quarantine and terminal no-retry action; do not infer that failed registration means no callback escaped."),
    ("RM08_FINAL_DISPOSE_ERROR_QUARANTINE", "P1", ("B07","B09","B10"),
     ("SH06_DISPOSAL_ERROR_HEAP_RETENTION",),
     ("D02","D04","D05"),
     ("if (AudioQueueDispose(ctx->queue,true)!=noErr)",
      "atomic_store_explicit(&fm_context_quarantined,1,memory_order_release)"),
     "Preserve both the native queue reference and allocated callback userdata on any unqualified final disposal/listener removal failure; make the quarantined session terminal, without reuse or automatic retry.",
     "Prove no use-after-free or reopening follows every failed disposal, registration or removal branch, and quantify the retained resource bound as a failure-containment property rather than cleanup success."),
    ("RM09_QUEUE_POINTER_OWNERSHIP", "P2", ("B07","B09"),
     ("SH02_NONATOMIC_QUEUE_REFERENCE_LIFETIME",),
     ("Q01",),
     ("AudioQueueRef queue;", "ctx->queue=NULL;"),
     "Give the non-atomic AudioQueueRef one documented owner; prohibit controller pointer clearing/disposal while any callback may still dereference queue through fill_audio. Require verified callback quiescence before ownership release.",
     "Show for every read and update of the queue pointer the owner, permitted lifecycle phase, synchronization rule and proof of no concurrent disposal or dangling reference."),
)
LIMITATIONS = (
    "NO_C11_RACE_FREEDOM_PROVEN",
    "NO_APPLE_ERROR_PATH_CALLBACK_QUIESCENCE_WITNESS",
    "NO_EXECUTABLE_C_REMEDIATION_PATCH_APPLIED",
    "NO_ACTIVE_COREAUDIO_QUEUE_OR_REALTIME_CALLBACK_EXERCISE",
    "NO_SCIENTIFIC_SIMULATION_OR_FAKE_MEASUREMENTS",
    "NO_INDEPENDENT_SIGNED_BUREAU_CERTIFICATION",
)

class R25Error(ValueError):
    pass

def require(condition, message):
    if not condition:
        raise R25Error(message)

def hashbytes(data):
    return hashlib.sha256(data).hexdigest()

def anchor(text, needle, pinned_hash):
    lines = text.splitlines()
    positions = [i + 1 for i,line in enumerate(lines) if needle in line]
    require(positions, "missing C source anchor: "+needle)
    return {"path":r24.SOURCE,"line":positions[0],
            "sha256":pinned_hash,"source_text":needle}

def review_plans(text, pinned_hash, context):
    require(len(PLANS)==9, "R25 nine-plan inventory drift")
    actual_gaps={item["id"] for item in context["open_r24_findings"]}
    require(actual_gaps=={x[0] for x in r24.GAPS},
            "original R24 seven findings no longer match real evidence")
    expected_obligations={x["id"].split("_",1)[0]
                          for x in context["r23_source_obligations"]}
    require(len(expected_obligations)==15,
            "R23 original fifteen obligations disappeared")
    results=[]
    for id,priority,roles,gaps,obligations,needles,change,proof in PLANS:
        require(priority in ("P1","P2") and len(roles)>=1,
                "remediation priority/owner missing")
        require(all(x in actual_gaps for x in gaps),
                "remediation references unknown R24 finding "+id)
        require(all(x in expected_obligations for x in obligations),
                "remediation references unknown R23 obligation "+id)
        require(len(change)>120 and len(proof)>120,
                "remediation design/proof obligations too shallow "+id)
        results.append({
            "id":id,"priority":priority,"reviewer_roles":list(roles),
            "r24_findings":list(gaps),"r23_obligations":list(obligations),
            "source_anchors":[anchor(text,n,pinned_hash) for n in needles],
            "proposal":change,"independent_proof_required":proof,
            "code_patch_applied":False,"proof_discharged":False,
            "design_status":STATUS,
            "physical_output_authorized":False,
        })
    require(len({x["id"] for x in results})==9,"duplicate proposal ids")
    require(set().union(*(set(x["r24_findings"]) for x in results))==actual_gaps,
            "R24 open finding left without a remediation candidate")
    require(set().union(*(set(x["r23_obligations"]) for x in results))
            ==expected_obligations,
            "R23 proof obligation left unmapped by remediations")
    return results

def validate_state_machine():
    require(len(STATES)==7 and len(set(STATES))==7,
            "duplicate/missing proposed ownership state")
    require(len(TRANSITIONS)==9 and len(set(TRANSITIONS))==9,
            "duplicate/missing proposed transitions")
    require(all(a in STATES and b in STATES for a,b in TRANSITIONS),
            "unknown proposed transition state")
    require(all(a not in ("DISPOSAL_CONFIRMED","QUARANTINED")
                for a,b in TRANSITIONS),
            "terminal ownership state can reenter")
    require(("DISPOSAL_UNCERTAIN","QUARANTINED") in TRANSITIONS,
            "disposal ambiguity must poison process")
    return [{"from":a,"to":b,"status":STATUS}
            for a,b in TRANSITIONS]

def inspect(root, source_override=None, plan_override=None):
    root=Path(root).resolve()
    table,manifest_sha=r17.manifest_integrity(root)
    require(len(table)==133,"GEN-R25 requires exactly 133 pinned generator files")
    for p in ("audits/r25_sync_ownership_remediation.py",
              "tests/test_r25_sync_ownership_remediation.py",
              "RUN_GEN_R25_MAC_INTEL.command",
              "docs/GEN_R25_REMEDIATION_DESIGN.md",
              "docs/GEN_R25_BUREAU_REVIEW.md"):
        require(p in table,"missing R25 source artifact: "+p)
    require(table[r24.SOURCE]==r19.PINNED_ACOUSTIC_SHA256,
            "the isolated native acoustic backend source changed")
    c_source=(root/r24.SOURCE).read_bytes()
    require(hashbytes(c_source)==table[r24.SOURCE],
            "C source SHA mismatch against manifest")
    runner_raw=(root/"RUN_GEN_R25_MAC_INTEL.command").read_bytes()
    require(hashbytes(runner_raw)==table["RUN_GEN_R25_MAC_INTEL.command"],
            "R25 runner not SHA-pinned")
    runner=runner_raw.decode("utf-8")
    linked=r17.link_sources(runner)
    require(len(linked)==len(r17.LINK_C_ALLOWLIST)
            and set(linked)==r17.LINK_C_ALLOWLIST,
            "R25 executable linker differs from denied six-source allowlist")
    require("R25_NONEMITTING_EXECUTABLE_SYMBOL_AUDIT=PASS" in runner
            and "FREQMED_GEN_R25_BINARY" in runner
            and "R25_REMEDIATION_DOSSIER=12_FILES_SHA256_PASS" in runner,
            "R25 output-denial/checksum contract missing")
    require("acoustic_macos.c" not in
            runner.split(' -o "$WORK/freqmed-gen"',1)[1]
                  .split("-framework CoreAudio",1)[0],
            "physical output backend linked into runnable executable")
    original=c_source.decode("utf-8")
    fields,calls=r24.inventory(original,table[r24.SOURCE])
    require(len(fields)==19 and len(calls)==11
            and sum(v["reference_count"] for v in fields.values())==112,
            "R24 known C shared-state surface is not retained")
    context={"open_r24_findings":[{"id":x[0]} for x in r24.GAPS],
             "r23_source_obligations":[{"id":x} for x in (
                 "HB01","HB02","HB03","HB04","HB05",
                 "Q01","Q02","Q03","Q04","Q05",
                 "D01","D02","D03","D04","D05")]}
    plans=review_plans(original if source_override is None
                       else source_override,
                       table[r24.SOURCE],
                       context if plan_override is None else plan_override)
    return table,manifest_sha,plans,validate_state_machine()

def audit(root,archive_r19,reports,r21,r22,r23,r24_report):
    table,digest,plans,transitions=inspect(root)
    actual=archive19.parse_json(archive19.safe_read(r24_report))
    expected=r24.audit(root,archive_r19,reports,r21,r22,r23)
    require(actual==expected,
            "R24 owner evidence has been detached from R16-R23 sources")
    require(actual["shared_field_count"]==19
            and actual["context_field_references"]==112
            and actual["direct_audioqueue_calls"]==11
            and len(actual["open_r24_findings"])==7
            and actual["r23_proof_obligations"]==15
            and actual["r23_obligations_discharged"]==0
            and actual["bureau_gates_open"]==11
            and actual["bureau_gates_resolved"]==0,
            "R24 original unresolved evidence silently altered")
    r23_evidence=archive19.parse_json(archive19.safe_read(r23))
    require(len(r23_evidence["source_only_obligations"])==15
            and all(x["proof_status"]=="OPEN_NOT_DISCHARGED"
                    for x in r23_evidence["source_only_obligations"]),
            "R23 original proof obligations are not all still OPEN")
    expected_r23={x["id"] for x in r23_evidence["source_only_obligations"]}
    require({item["id"].split("_",1)[0] for item in r23_evidence["source_only_obligations"]}
            == {"HB01","HB02","HB03","HB04","HB05",
                "Q01","Q02","Q03","Q04","Q05",
                "D01","D02","D03","D04","D05"},
            "unexpected R23 obligation identifier format")
    return {
        "schema":SCHEMA,"verdict":VERDICT,
        "method":"PINNED_C11_REMEDIATION_DESIGNS_AND_UNDISCHARGED_EVIDENCE",
        "current_generator_manifest_sha256":digest,
        "generator_file_count":len(table),
        "native_acoustic_source_sha256":table[r24.SOURCE],
        "r24_report_sha256":hashbytes(archive19.safe_read(r24_report)),
        "owner_proof_proposals":plans,"proposal_count":9,
        "proposals_applied":0,"independent_proofs_discharged":0,
        "ownership_states":list(STATES),
        "ownership_transitions_proposed":transitions,
        "r24_open_findings":7,
        "r23_open_proof_obligations":15,
        "bureau_open_gates":11,"bureau_gates_resolved":0,
        "c11_race_freedom":"NOT_PROVEN",
        "callback_quiescence":"NOT_PROVEN",
        "failed_os_disposal":"NOT_TESTED",
        "independent_signatures":"NONE",
        "coreaudio_active_callbacks":"NOT_PERFORMED",
        "physical_emission":"NONE","scientific_simulation":"NONE",
        "acoustic_output":"LOCKED","em_output":"LOCKED",
        "real_output":"NOT_AUTHORIZED",
        "biological_exposure":"NOT_AUTHORIZED",
        "production":"NOT_AUTHORIZED","bureau_certification":"PENDING",
        "limitations":list(LIMITATIONS),
    }

def markdown(report):
    tick=chr(96)
    rows=[]
    for x in report["owner_proof_proposals"]:
        spots=", ".join(tick+ref["path"]+":"+str(ref["line"])+tick
                        for ref in x["source_anchors"])
        rows.append("| "+x["id"]+" | "+x["priority"]+
                    " | "+",".join(x["reviewer_roles"])+" | "+spots+
                    " | PROPOSED_NOT_APPLIED |")
    trans="\n".join("- "+a+" → "+b+
                    " (**proposé, non implémenté**)"
                    for a,b in TRANSITIONS)
    return ("# FREQMED GEN-R25 — Independent C11 synchronization and ownership remediation\n\n"
            "**Verdict : REMEDIATION_PLANS_REVIEWABLE_NOT_APPLIED**. "
            "**9 remédiations proposées, 0 patch appliqué, 0 preuve acquittée.** "
            "Contrôle de l'ancienne chaîne R16-R24 et de 133 sources, sans aucune sortie.\n\n"
            "| Correction candidate | Priorité | Bureau | Lignes C | État |\n"
            "|---|---|---|---|---|\n"+"\n".join(rows)+
            "\n\n## Transitions de propriété proposées (NON implémentées)\n\n"+
            trans+"\n\n**Ce registre ne démontre pas une relation happens-before, "
            "la durée de vie de tous les callbacks CoreAudio ni les retours "
            "d'erreur système. Un verdict logiciel PASS laisse inchangées "
            "les 15 obligations R23, les 7 lacunes R24 et les 11 portes Bureau.**\n\n"
            "NEVER_SIMULATION=ENFORCED ; ZERO_COST_FOSS=ENFORCED ; "
            "ACOUSTIC_OUTPUT=LOCKED ; EM_OUTPUT=LOCKED ; "
            "REAL_OUTPUT=NOT_AUTHORIZED ; "
            "BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED ; PRODUCTION=NOT_AUTHORIZED.\n")

def main():
    p=argparse.ArgumentParser(description="GEN-R25 source-only remediation review")
    p.add_argument("--root",required=True,type=Path)
    p.add_argument("--archive-r19",required=True,type=Path)
    for key in ("r16","r17","r18","r19","r20","r21","r22","r23","r24"):
        p.add_argument("--"+key,required=True,type=Path)
    p.add_argument("--json",required=True,type=Path)
    p.add_argument("--markdown",required=True,type=Path)
    args=p.parse_args()
    try:
        base={x:getattr(args,x) for x in ("r16","r17","r18","r19","r20")}
        result=audit(args.root,args.archive_r19,base,
                     args.r21,args.r22,args.r23,args.r24)
        args.json.write_text(json.dumps(result,sort_keys=True,indent=2,
                             ensure_ascii=False)+"\n",encoding="utf-8")
        args.markdown.write_text(markdown(result),encoding="utf-8")
    except (R25Error,r24.R24Error,ValueError,KeyError,TypeError,OSError,
            UnicodeError,IndexError) as error:
        print("R25_C11_REMEDIATION_REVIEW=FAIL_CLOSED",str(error))
        return 2
    print("R25_C11_REMEDIATION_REVIEW=PASS")
    print("R25_REMEDIATION_PLANS=9; R25_APPLIED=0; R25_PROOFS_DISCHARGED=0")
    print("R25_OWNERSHIP_STATES=7; R25_TRANSITIONS_PROPOSED=9")
    print("R25_R23_OBLIGATIONS=15_OPEN; R25_R24_FINDINGS=7_OPEN")
    print("R25_BUREAU_GATES=11_OPEN; R25_BUREAU_RESOLVED=0")
    print("R25_REVIEW_VERDICT="+VERDICT)
    print("R25_C11_RACE_FREEDOM=NOT_PROVEN")
    print("R25_CALLBACK_QUIESCENCE=NOT_PROVEN")
    print("R25_FAILED_OS_DISPOSAL=NOT_TESTED")
    print("R25_PHYSICAL_EMISSION=NONE; R25_SCIENTIFIC_SIMULATION=NONE")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
