#!/usr/bin/env python3
"""GEN-R26 isolated CoreAudio patch design and safety gate.

Reconstructs the ONLY three permitted edits to the pinned R19 native source,
proves byte-for-byte scope of the *candidate file*, verifies R25 evidence, and
keeps this source outside executable linkage. Not a formal C11/OS proof.
"""
import argparse
import hashlib
import json
from pathlib import Path

import r17_evidence_verifier as r17
import r19_adversarial_source_audit as r19
import r19_evidence_archive as evidence
import r25_sync_ownership_remediation as r25

SCHEMA="FREQMED_GEN_R26_C11_NATIVE_ISOLATED_PATCH_DESIGN_GATE"
VERDICT="ISOLATED_PATCH_REVIEW_REQUIRED_NO_EMISSION"
CANDIDATE="candidates/acoustic_macos_r26.c"
ORIGINAL="src/acoustic_macos.c"
PREFIX = """/* GEN-R26 ISOLATED CANDIDATE. CONTAINS CoreAudio source-only APIs.
 * MUST NEVER BE LINKED, LOADED OR ACTIVATED FOR PHYSICAL OUTPUT.
 * This is an *unqualified* technical remediation experiment in source review.
 * Source owner context is intentionally retained after publication.
 * The original pinned generator/src/acoustic_macos.c remains unchanged.
 */
"""
PATCHES = (
    ("R26_PCM_CONTROLLER_SHARED_GATE",
     "    fill_audio(ctx,b);\n    if (atomic_load(&ctx->failed)) {err=1;break;}",
     """    /* GEN-R26 isolated candidate: share the PCM writer gate with callback.
     * Contended entry fails closed. Not a CoreAudio lifetime proof. */
    if (atomic_flag_test_and_set_explicit(&ctx->pcm_writer_gate,
                                          memory_order_acquire)) {
      fm_latch_first_fault(ctx,FM_FAULT_OVERLAPPING_PCM_CALLBACK);
      err=1;
      break;
    }
    fill_audio(ctx,b);
    atomic_flag_clear_explicit(&ctx->pcm_writer_gate,memory_order_release);
    if (atomic_load(&ctx->failed)) {err=1;break;}"""),
    ("R26_BIND_ERROR_RETAIN_USERDATA",
     """      if (atomic_load_explicit(&ctx->active_output_callbacks,
                               memory_order_acquire)==0U &&
          atomic_load_explicit(&ctx->active_property_listeners,
                               memory_order_acquire)==0U) {
        free(owner_ctx);
        atomic_flag_clear_explicit(&fm_session_claim,memory_order_release);
      } else {
        atomic_store_explicit(&fm_context_quarantined,1,memory_order_release);
      }""",
     """      /* GEN-R26 candidate: even reported successful disposal cannot
       * qualify all callback/listener lifetime paths in this review.
       * Preserve userdata and permanently deny another session. */
      atomic_store_explicit(&fm_context_quarantined,1,memory_order_release);"""),
    ("R26_PUBLISHED_CONTEXT_FAIL_CLOSED",
     """  if (context_quiescent) {
    free(owner_ctx);
    atomic_flag_clear_explicit(&fm_session_claim,memory_order_release);
  } else {
    atomic_store_explicit(&fm_context_quarantined,1,memory_order_release);
    err=1;
  }
  return err?-1:0;""",
     """  /* GEN-R26 candidate: diagnostic quiescence does not prove the absence
   * of later or still-running CoreAudio/listener callbacks. Retain owner_ctx
   * after any publication to the OS. One-shot process admission remains
   * closed; no successful native output result is possible in this draft. */
  (void)context_quiescent;
  atomic_store_explicit(&fm_context_quarantined,1,memory_order_release);
  err=1;
  return -1;"""),
)
RISKS=(
    ("R26_C11_OS_ENTRY_NOT_PROVEN","Even a common flag does not prove callback admission timing or all happens-before relations."),
    ("R26_LONG_LIVED_OS_POINTERS_NOT_QUALIFIED","Keeping the allocation alive does not prove that OS callbacks cease or that their accesses are race-free."),
    ("R26_LEAK_UNTIL_PROCESS_TERMINATION","A published context is permanently retained and the process gate poisoned; bounded allocation count is a design hypothesis."),
    ("R26_COREAUDIO_DISPOSAL_FAILURE_NOT_TESTED","Actual failed AudioQueueDispose and listener-removal behavior remain unobserved."),
    ("R26_REAL_TIME_AND_ERROR_PATHS_UNREVIEWED","The callback flag and controller error handling still require independent timing, starvation and lifecycle review."),
)
ROLES=("B07","B09","B10")
class R26Error(ValueError):
    pass
def require(ok,why):
    if not ok: raise R26Error(why)
def sha(data): return hashlib.sha256(data).hexdigest()

def expected_candidate(original):
    require(original.startswith("/* SPDX-License-Identifier: Apache-2.0 */\n"),
            "original license header changed")
    expected=original.replace("/* SPDX-License-Identifier: Apache-2.0 */\n",
                              "/* SPDX-License-Identifier: Apache-2.0 */\n"+PREFIX,1)
    for ident,old,new in PATCHES:
        require(original.count(old)==1 and expected.count(old)==1,
                "R26 source baseline ambiguous: "+ident)
        expected=expected.replace(old,new,1)
    return expected

def inspect(root,candidate_override=None):
    root=Path(root).resolve()
    table,manifest_sha=r17.manifest_integrity(root)
    require(len(table)>=139,"R26 historical baseline requires at least 139 SHA-pinned generator files")
    for path in (CANDIDATE,"audits/r26_isolated_patch_gate.py",
                 "tests/test_r26_isolated_patch_gate.py",
                 "RUN_GEN_R26_MAC_INTEL.command",
                 "docs/GEN_R26_PATCH_DESIGN.md",
                 "docs/GEN_R26_BUREAU_REVIEW.md"):
        require(path in table,"R26 required candidate artifact not SHA pinned "+path)
    require(table[ORIGINAL]==r19.PINNED_ACOUSTIC_SHA256,
            "original CoreAudio C source changed from pinned baseline")
    old=(root/ORIGINAL).read_bytes()
    raw=(root/CANDIDATE).read_bytes()
    runner=(root/"RUN_GEN_R26_MAC_INTEL.command").read_bytes()
    require(sha(old)==table[ORIGINAL],"original C SHA mismatch")
    require(sha(raw)==table[CANDIDATE],"candidate C SHA mismatch")
    require(sha(runner)==table["RUN_GEN_R26_MAC_INTEL.command"],
            "R26 runner SHA mismatch")
    orig=old.decode("utf-8")
    actual=raw.decode("utf-8") if candidate_override is None else candidate_override
    expected=expected_candidate(orig)
    require(actual==expected,"isolated candidate differs from exactly three allowed C edits")
    require(actual.count("free(owner_ctx);")==2,
            "published callback context must not be freed in R26 candidate")
    require(actual.count("atomic_flag_clear_explicit(&fm_session_claim,memory_order_release);")==4,
            "claim release count inconsistent with original prepublication paths")
    require("  return -1;\n\n}\nint fm_acoustic_native_backend_available" in actual,
            "candidate backend may return success")
    require("  (void)command;\n  return -1;" in actual,
            "public acoustic API must always deny")
    for value in ("AudioQueueNewOutput(", "AudioQueueStart(", "AudioQueueDispose("):
        require(value in actual,"candidate source lost documented CoreAudio API "+value)
    runtext=runner.decode("utf-8")
    linked=r17.link_sources(runtext)
    require(len(linked)==len(r17.LINK_C_ALLOWLIST)
            and set(linked)==r17.LINK_C_ALLOWLIST,
            "linked runnable C sources not exactly nonemitting allowlist")
    link=runtext.split(' -o "$WORK/freqmed-gen"',1)
    require(len(link)==2,"output executable linker clause absent")
    command=link[1].split("-framework CoreAudio",1)[0]
    require(CANDIDATE not in command
            and "acoustic_macos_r26.c" not in command
            and "acoustic_macos.c" not in command
            and "output_hard_denied.c" in command,
            "runnable could link physical backend")
    require("R26_NONEMITTING_EXECUTABLE_SYMBOL_AUDIT=PASS" in runtext
            and "R26_ISOLATED_CANDIDATE_OBJECT=COMPILED_UNLINKED" in runtext
            and "FREQMED_GEN_R26_BINARY" in runtext
            and "R26_BUREAU_PATCH_DOSSIER=14_FILES_SHA256_PASS" in runtext,
            "R26 native guards or private evidence contract absent")
    return table,manifest_sha,sha(raw),sha(old)

def audit(root,archive_r19,older,r21,r22,r23,r24,r25_report):
    table,manifest_sha,candidate_sha,baseline_sha=inspect(root)
    actual=evidence.parse_json(evidence.safe_read(r25_report))
    recalculated=r25.audit(root,archive_r19,older,r21,r22,r23,r24)
    require(actual==recalculated,
            "R25 real evidence detached from historical source chain")
    require(actual["proposal_count"]==9 and actual["proposals_applied"]==0
            and actual["independent_proofs_discharged"]==0
            and actual["r23_open_proof_obligations"]==15
            and actual["r24_open_findings"]==7
            and actual["bureau_open_gates"]==11
            and actual["bureau_gates_resolved"]==0,
            "R25 governance was silently promoted")
    original=(root/ORIGINAL).read_text(encoding="utf-8")
    proposed=(root/CANDIDATE).read_text(encoding="utf-8")
    anchors=[]
    for ident,old,new in PATCHES:
        # The whole old block, not its first line, is uniquely anchored.
        require(original.count(old)==1,"original C patch anchor missing: "+ident)
        baseline_line=original[:original.index(old)].count("\n")+1
        anchors.append({"id":ident,"baseline_path":ORIGINAL,
                        "baseline_line":baseline_line,
                        "baseline_sha256":baseline_sha,
                        "candidate_sha256":candidate_sha,
                        "exact_code_replacement_present":new in proposed,
                        "status":"ISOLATED_UNLINKED_NOT_CERTIFIED"})
    return {
        "schema":SCHEMA,"verdict":VERDICT,
        "method":"BYTE_EXACT_THREE_EDIT_C_CANDIDATE_REPLAY_AND_NONEMITTING_LINK_GATE",
        "source_manifest_sha256":manifest_sha,"pinned_files":len(table),
        "original_acoustic_sha256":baseline_sha,
        "candidate_sha256":candidate_sha,
        "applied_to_original_C":False,
        "isolated_native_candidate_patches":3,
        "isolated_candidate_compiled_only":"PENDING_NATIVE_WITNESS",
        "candidate_patch_anchors":anchors,
        "synchronization_candidate":"CONTROLLER_AND_CALLBACK_COMMON_ATOMIC_FLAG",
        "published_context_ownership":"RETAIN_HEAP_AND_QUARANTINE_AFTER_OS_PUBLICATION",
        "successful_physical_output_possible":"NO_AUTHORIZED_PATH",
        "r25_report_sha256":sha(evidence.safe_read(r25_report)),
        "r25_plans":9,"r25_plans_applied_to_baseline":0,
        "r23_proof_obligations_open":15,"r24_findings_open":7,
        "bureau_gates_open":11,"bureau_gates_resolved":0,
        "unresolved_r26_risks":[{"id":id,"reason":desc,"status":"NOT_PROVEN"}
                               for id,desc in RISKS],
        "formal_C11_happens_before_proof":"NOT_PROVEN",
        "actual_CoreAudio_callback_quiescence":"NOT_PROVEN",
        "failed_OS_disposal_witness":"NOT_TESTED",
        "independent_reviewer_roles":list(ROLES),
        "independent_signatures":"NONE","bureau_certification":"PENDING",
        "physical_emission":"NONE","scientific_simulation":"NONE",
        "acoustic_output":"LOCKED","em_output":"LOCKED",
        "real_output":"NOT_AUTHORIZED",
        "biological_exposure":"NOT_AUTHORIZED","production":"NOT_AUTHORIZED",
    }

def markdown(result):
    rows="".join("| "+x["id"]+" | "+str(x["baseline_line"])+" | ISOLATED_ONLY |\n"
                 for x in result["candidate_patch_anchors"])
    riskrows="".join("| "+x["id"]+" | NOT_PROVEN |\n"
                     for x in result["unresolved_r26_risks"])
    return ("# FREQMED GEN-R26 — independent C11 isolated patch safety gate\n\n"
            "**Verdict : ISOLATED_PATCH_REVIEW_REQUIRED_NO_EMISSION**. "
            "**Trois modifications C dans un fichier candidat isolé, zéro modification "
            "du backend épinglé, zéro preuve C11 acquittée.**\n\n"
            "| Modification | Ligne source d'origine | Portée |\n"
            "|---|---|---|\n"+rows+
            "\n| Risque restant | État |\n|---|---|\n"+riskrows+
            "\nCe code candidat utilise le verrou PCM des deux chemins et "
            "conserve les contextes publiés après dispose, au prix d'une fuite "
            "bornée hypothétique et d'un processus définitivement verrouillé. "
            "Il n'est jamais lié, chargé ni exécuté. Ces modifications ne "
            "prouvent ni l'absence de race C11 ni la fin des callbacks OS. "
            "15 obligations R23 OPEN, 7 risques R24 OPEN, 11 portes Bureau OPEN.\n\n"
            "NEVER_SIMULATION=ENFORCED ; ZERO_COST_FOSS=ENFORCED ; "
            "ACOUSTIC_OUTPUT=LOCKED ; EM_OUTPUT=LOCKED ; "
            "REAL_OUTPUT=NOT_AUTHORIZED ; BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED ; "
            "PRODUCTION=NOT_AUTHORIZED.\n")

def main():
    p=argparse.ArgumentParser(description="GEN-R26 isolated C source patch safety gate")
    p.add_argument("--root",required=True,type=Path)
    p.add_argument("--archive-r19",required=True,type=Path)
    for n in ("r16","r17","r18","r19","r20","r21","r22","r23","r24","r25"):
        p.add_argument("--"+n,required=True,type=Path)
    p.add_argument("--json",required=True,type=Path)
    p.add_argument("--markdown",required=True,type=Path)
    a=p.parse_args()
    try:
        prev={n:getattr(a,n) for n in ("r16","r17","r18","r19","r20")}
        result=audit(a.root,a.archive_r19,prev,a.r21,a.r22,a.r23,a.r24,a.r25)
        a.json.write_text(json.dumps(result,sort_keys=True,indent=2,
                          ensure_ascii=False)+"\n",encoding="utf-8")
        a.markdown.write_text(markdown(result),encoding="utf-8")
    except (R26Error,r25.R25Error,ValueError,KeyError,TypeError,
            OSError,UnicodeError,IndexError) as exc:
        print("R26_ISOLATED_PATCH_DESIGN_GATE=FAIL_CLOSED",str(exc))
        return 2
    print("R26_ISOLATED_PATCH_DESIGN_GATE=PASS")
    print("R26_CANDIDATE_C_EDITS=3; R26_ORIGINAL_C_EDITS=0")
    print("R26_NATIVE_CANDIDATE=SOURCE_ONLY_UNLINKED")
    print("R26_R23_OBLIGATIONS=15_OPEN; R26_R24_FINDINGS=7_OPEN")
    print("R26_BUREAU_GATES=11_OPEN; R26_RESOLVED=0")
    print("R26_REVIEW_VERDICT="+VERDICT)
    print("R26_C11_RACE_FREEDOM=NOT_PROVEN")
    print("R26_OS_CALLBACK_QUIESCENCE=NOT_PROVEN")
    print("R26_FAILED_OS_DISPOSAL=NOT_TESTED")
    print("R26_PHYSICAL_EMISSION=NONE; R26_SCIENTIFIC_SIMULATION=NONE")
    return 0
if __name__=="__main__":
    raise SystemExit(main())
