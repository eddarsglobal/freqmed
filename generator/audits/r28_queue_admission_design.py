#!/usr/bin/env python3
"""GEN-R28 source-only ownership admission blueprint audit; never run callbacks.
Only document and compile a separate C11 gate, not scientific simulation.
"""
import argparse
import hashlib
import json
from pathlib import Path
import r17_evidence_verifier as r17
import r19_adversarial_source_audit as r19
import r26_isolated_patch_gate as r26
import r27_adversarial_ownership_review as r27

SCHEMA = "FREQMED_GEN_R28_C11_QUEUE_ADMISSION_DESIGN"
VERDICT = "BOUNDED_C11_ADMISSION_DESIGN_UNCERTIFIED"
CANDIDATE = "candidates/r28_callback_admission_gate.c"
GATES = (
 ("D28_01_STABLE_USERDATA_BEFORE_ADMISSION","B07",
  "Prove that every OS entry has a valid lifetime-stable userdata pointer before reading an atomic gate, including callbacks arriving after removal."),
 ("D28_02_QUEUE_LEASE_AND_INVALIDATION","B09",
  "Bind all uses of AudioQueueRef and AudioQueueBufferRef to an accepted lease and prove a full C11 happens-before before controller invalidation."),
 ("D28_03_NONBLOCKING_CALLBACK_PATH","B09",
  "Independently prove that one bounded CAS and all callback error paths avoid blocking, retry loops and unsafe CoreAudio reentrance."),
 ("D28_04_FINAL_DISPOSAL_OWNERSHIP","B07",
  "Qualify all genuine AudioQueueDispose OSStatus outcomes and show that no queue or buffer remains owned by CoreAudio before reclamation."),
 ("D28_05_BOUNDED_PROCESS_QUARANTINE","B10",
  "Bound all process-retained memory and OS resources, demonstrate safe process shutdown and keep all outputs permanently denied."),
)
REQUIRED = (
 "FM_R28_CLOSED (UINT_FAST64_MAX ^ (UINT_FAST64_MAX >> 1))",
 "FM_R28_COUNT_MASK (FM_R28_CLOSED - (uint_fast64_t)1)",
 "atomic_uint_fast64_t state;",
 "void fm_r28_gate_init(FMR28AdmissionGate *gate)",
 "bool fm_r28_gate_try_enter(FMR28AdmissionGate *gate)",
 "atomic_compare_exchange_strong_explicit(",
 "memory_order_acq_rel,memory_order_acquire);",
 "void fm_r28_gate_leave(FMR28AdmissionGate *gate)",
 "atomic_fetch_sub_explicit(",
 "void fm_r28_gate_close(FMR28AdmissionGate *gate)",
 "atomic_fetch_or_explicit(",
 "FM_R28_CLOSED,memory_order_acq_rel);",
 "bool fm_r28_gate_closed_and_empty(const FMR28AdmissionGate *gate)",
 "(state & FM_R28_CLOSED)!=0 && (state & FM_R28_COUNT_MASK)==0;",
 "Strict PRECONDITION: exactly one leave",
 "MUST NOT BE LINKED, LOADED OR USED TO GENERATE PHYSICAL OUTPUT",
)
FORBIDDEN = (
 "AudioQueue", "AudioDevice", "AudioToolbox", "CoreAudio/",
 "IOServiceOpen", "dlopen(", "main(", "sin(", "cos(", "pthread_create(",
)
LIMITATIONS = (
 "DESIGN_C11_GATE_ONLY_NOT_CONNECTED_TO_COREAUDIO",
 "C11_ATOMIC_TOKENS_ARE_NOT_FORMAL_RACE_PROOF",
 "COUNTER_PAIRING_AND_CONTEXT_PUBLICATION_NOT_VERIFIED",
 "OS_ADMISSION_AND_DISPOSAL_CONTRACT_NOT_QUALIFIED",
 "NO_ACTIVE_CALLBACK_OR_SCIENTIFIC_SIMULATION_OR_PHYSICAL_OUTPUT",
 "NO_INDEPENDENT_BUREAU_SIGNATURE",
)
class R28Error(ValueError): pass
def require(ok, why):
    if not ok: raise R28Error(why)
def digest(data): return hashlib.sha256(data).hexdigest()

def observe(content):
    require(content.startswith("/* SPDX-License-Identifier: Apache-2.0 */"),
            "R28 source license/header drift")
    for token in REQUIRED:
        require(content.count(token)==1, "R28 C11 design token drift: "+token)
    # Literal CoreAudio references are explanatory comments only; strip them.
    import re
    code=re.sub(r"/\*[\s\S]*?\*/|//[^\n]*","",content)
    for token in FORBIDDEN:
        require(token not in code,"R28 active physical API or unexpected runtime: "+token)
    require("while (" not in code and "for (" not in code
            and "while(" not in code and "for(" not in code,
            "R28 callbacks must not spin or loop")
    require(len(GATES)==5 and len({x[0] for x in GATES})==5,
            "R28 design ledger drift")
    return {x[0]:"OPEN_NOT_PROVEN" for x in GATES}

def inspect(root,source_override=None):
    root=Path(root).resolve()
    table,manifest=r17.manifest_integrity(root)
    require(len(table)>=150,"R28 historical design baseline requires at least 150 SHA-pinned files")
    needed=(CANDIDATE,"audits/r28_queue_admission_design.py",
            "tests/test_r28_queue_admission_design.py",
            "RUN_GEN_R28_MAC_INTEL.command",
            "docs/GEN_R28_QUEUE_LIFETIME_DESIGN.md",
            "docs/GEN_R28_BUREAU_REVIEW.md")
    require(all(x in table for x in needed),"R28 missing manifest artifact")
    require(table[r26.ORIGINAL]==r19.PINNED_ACOUSTIC_SHA256,
            "R28 original acoustic C changed")
    earlier=r27.inspect(root)
    require(earlier[3]==table[r26.CANDIDATE],
            "R28 previous isolated R26 C changed")
    c=(root/CANDIDATE).read_bytes()
    require(digest(c)==table[CANDIDATE],"R28 separate C candidate hash mismatch")
    report=observe(c.decode("utf-8") if source_override is None else source_override)
    run=(root/"RUN_GEN_R28_MAC_INTEL.command").read_text(encoding="utf-8")
    require(set(r17.link_sources(run))==r17.LINK_C_ALLOWLIST,
            "R28 executable linker allowlist changed")
    pieces=run.split(' -o "$WORK/freqmed-gen"')
    require(len(pieces)==2,"R28 executable link command missing")
    linked=pieces[1].split("-framework CoreAudio",1)[0]
    require("r28_callback_admission_gate.c" not in linked
            and "acoustic_macos_r26.c" not in linked
            and "output_hard_denied.c" in linked,
            "R28 output or C11 design linked to executable")
    for marker in ("R28_ADMISSION_DESIGN_OBJECT=COMPILED_UNLINKED",
                   "R28_BUREAU_DESIGN_DOSSIER=18_FILES_SHA256_PASS",
                   "R28_NONEMITTING_EXECUTABLE_SYMBOL_AUDIT=PASS",
                   "FREQMED_GEN_R28_EVIDENCE_DIR",
                   "FREQMED_GEN_R28_BINARY"):
        require(marker in run, "R28 runtime guard missing: "+marker)
    return table,manifest,digest(c),report

def audit(root,archive_r19,paths):
    table,manifest,source_sha,checks=inspect(root)
    original={key:paths[key] for key in ("r16","r17","r18","r19","r20")}
    expected=r27.audit(root,archive_r19,original,
                        *(paths[key] for key in
                          ("r21","r22","r23","r24","r25","r26")))
    recorded=json.loads(Path(paths["r27"]).read_text(encoding="utf-8"))
    require(recorded==expected,"R28 historical R27 report has drifted")
    require(expected["r27_open_findings"]==9
            and expected["r27_proven_races"]==0
            and expected["r23_obligations_open"]==15
            and expected["r24_findings_open"]==7
            and expected["bureau_gates_open"]==11
            and expected["bureau_gates_resolved"]==0,
            "R28 historical proof gates silently promoted")
    return {
      "schema":SCHEMA,"verdict":VERDICT,
      "method":"SOURCE_ONLY_SEPARATE_C11_GATE_DESIGN_NOT_INTEGRATED",
      "manifest_sha256":manifest,"pinned_generator_files":len(table),
      "r28_design_source_sha256":source_sha,
      "r27_report_sha256":digest(Path(paths["r27"]).read_bytes()),
      "original_C_sha256":table[r26.ORIGINAL],
      "r26_candidate_sha256":table[r26.CANDIDATE],
      "r28_design_gates":[{"id":ident,"bureau_role":role,
         "evidence_needed":proof,"status":checks[ident]} for ident,role,proof in GATES],
      "r28_gates_open":5,"r28_applied_to_r26_candidate":False,
      "r28_applied_to_original_C":False,
      "r27_findings_open":9,"r23_obligations_open":15,
      "r24_findings_open":7,"bureau_gates_open":11,"bureau_gates_resolved":0,
      "C11_race_freedom":"NOT_PROVEN",
      "CoreAudio_callback_quiescence":"NOT_PROVEN",
      "failed_AudioQueueDispose":"NOT_TESTED",
      "independent_signatures":"NONE","bureau_certification":"PENDING",
      "limitations":list(LIMITATIONS),
      "physical_emission":"NONE","scientific_simulation":"NONE",
      "acoustic_output":"LOCKED","em_output":"LOCKED",
      "real_output":"NOT_AUTHORIZED","production":"NOT_AUTHORIZED",
      "biological_exposure":"NOT_AUTHORIZED",
    }
def markdown(report):
    rows=["| "+x["id"]+" | "+x["bureau_role"]+" | "+x["status"]+" |"
          for x in report["r28_design_gates"]]
    return ("# FREQMED GEN-R28 - C11 Queue Lifetime and Callback Admission Design\n\n"
       "**Design-only; not integrated; no C11/OS runtime safety proof.**\n\n"
       "| Control | Bureau | Verdict |\n|---|---|---|\n"
       + "\n".join(rows) + "\n\n"
       "A closed/empty C11 gate is necessary but NOT sufficient for CoreAudio "
       "quiescence or validity of AudioQueueRef. Userdata must remain alive "
       "even for callbacks attempting admission after sealing. A controller "
       "must not dispose a queue while accepted leases still use it. "
       "AudioQueueEnqueueBuffer reentrancy and OSStatus failures remain OPEN.\n\n"
       "No actual callback, science simulation, or physical emission occurred. "
       "NEVER_SIMULATION=ENFORCED; ZERO_COST_FOSS=ENFORCED; "
       "ACOUSTIC_OUTPUT=LOCKED; EM_OUTPUT=LOCKED; REAL_OUTPUT=NOT_AUTHORIZED; "
       "BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED; PRODUCTION=NOT_AUTHORIZED.\n")
def main():
    parser=argparse.ArgumentParser(description="GEN-R28 isolated C11 design review")
    parser.add_argument("--root",type=Path,required=True)
    parser.add_argument("--archive-r19",type=Path,required=True)
    for key in ("r16","r17","r18","r19","r20","r21","r22",
                "r23","r24","r25","r26","r27"):
        parser.add_argument("--"+key,type=Path,required=True)
    parser.add_argument("--json",type=Path,required=True)
    parser.add_argument("--markdown",type=Path,required=True)
    args=parser.parse_args()
    try:
        reports={key:getattr(args,key) for key in
                 ("r16","r17","r18","r19","r20","r21","r22",
                  "r23","r24","r25","r26","r27")}
        result=audit(args.root,args.archive_r19,reports)
        args.json.write_text(json.dumps(result,indent=2,sort_keys=True,
                             ensure_ascii=False)+"\n",encoding="utf-8")
        args.markdown.write_text(markdown(result),encoding="utf-8")
    except (R28Error,r27.R27Error,r26.R26Error,ValueError,
            KeyError,OSError,TypeError,UnicodeError,IndexError) as exc:
        print("R28_C11_QUEUE_ADMISSION_DESIGN=FAIL_CLOSED",str(exc))
        return 2
    print("R28_C11_QUEUE_ADMISSION_DESIGN=PASS")
    print("R28_DESIGN_GATES=5_OPEN; R28_INTEGRATED_C_PATCHES=0")
    print("R28_R27_ADVERSARIAL_FINDINGS=9_OPEN")
    print("R28_R23_PROOF_OBLIGATIONS=15_OPEN; R28_R24_FINDINGS=7_OPEN")
    print("R28_BUREAU_GATES=11_OPEN; R28_BUREAU_RESOLVED=0")
    print("R28_REVIEW_VERDICT="+VERDICT)
    print("R28_C11_RACE_FREEDOM=NOT_PROVEN")
    print("R28_CALLBACK_QUIESCENCE=NOT_PROVEN")
    print("R28_FAILED_OS_DISPOSAL=NOT_TESTED")
    print("R28_PHYSICAL_EMISSION=NONE; R28_SCIENTIFIC_SIMULATION=NONE")
    return 0
if __name__=="__main__":
    raise SystemExit(main())
