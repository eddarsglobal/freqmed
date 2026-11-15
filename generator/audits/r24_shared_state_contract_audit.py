#!/usr/bin/env python3
"""GEN-R24: independent bounded C11 shared-state + CoreAudio contract matrix.

The audit inventories every syntactic ctx->FIELD and owner_ctx->FIELD access
to the unchanged pinned acoustic C source, maps it to real source/functions,
and compares expected Apple/C11 contracts with unresolved proof obligations.
It does NOT run callbacks, generate or simulate physical output, formally
prove data-race freedom, or certify safety.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

import r17_evidence_verifier as r17
import r19_adversarial_source_audit as r19
import r19_evidence_archive as archive19
import r23_happens_before_obligations as r23

SCHEMA = "FREQMED_GEN_R24_C11_SHARED_STATE_AND_OS_CONTRACT_AUDIT"
VERDICT = "SHARED_STATE_MAPPED_CONTRACT_GAPS_OPEN"
SOURCE = "src/acoustic_macos.c"
# This deliberately freezes the reviewed source surface, NOT a whitelist of
# acceptable future synchronization. Any source change requires new review.
FIELDS = (
    ("queue", "AudioQueueRef", 13),
    ("phase", "double", 4),
    ("phase_step", "double", 2),
    ("normalized_level", "double", 2),
    ("frames_written", "uint64_t", 4),
    ("total_frames", "uint64_t", 5),
    ("fade_frames", "uint64_t", 7),
    ("last_frame_enqueued", "atomic_int", 4),
    ("failed", "atomic_int", 16),
    ("stop_requested", "atomic_int", 11),
    ("queue_started", "atomic_int", 5),
    ("queue_stopped", "atomic_int", 4),
    ("graceful_drain_requested", "atomic_int", 3),
    ("shutdown_in_progress", "atomic_int", 8),
    ("first_fault_reason", "atomic_int", 5),
    ("active_output_callbacks", "atomic_uint", 6),
    ("active_property_listeners", "atomic_uint", 6),
    ("dispose_confirmed", "atomic_int", 4),
    ("pcm_writer_gate", "atomic_flag", 3),
)
# Calls in the current C source, not CoreAudio runtime behavior. Comments are
# removed before counting. FM helper API calls are accounted separately in
# R16-R23; this is the direct AudioQueue surface of this exact source file.
OS_CALLS = (
    ("AudioQueueNewOutput", 1),
    ("AudioQueueAddPropertyListener", 1),
    ("AudioQueueRemovePropertyListener", 1),
    ("AudioQueueDispose", 2),
    ("AudioQueueStart", 1),
    ("AudioQueueStop", 2),
    ("AudioQueueGetProperty", 1),
    ("AudioQueueAllocateBuffer", 1),
    ("AudioQueueEnqueueBuffer", 1),
)
FUNC_DOMAIN = {
    "fm_latch_first_fault": "SHARED_FAULT_HELPER",
    "fill_audio": "CONTROL_AND_OUTPUT_CALLBACK_CALLEE",
    "request_graceful_queue_drain": "CONTROL_PATH",
    "queue_running_listener": "COREAUDIO_PROPERTY_LISTENER",
    "output_callback": "COREAUDIO_OUTPUT_CALLBACK",
    "acoustic_output_impl": "CONTROLLER_PATH",
}
GAPS = (
    ("SH01_NONATOMIC_PCM_CONTROLLER_CALLBACK", "C11_CALLBACK_RACE_FREEDOM",
     "Proof of a common happens-before edge for controller prefill and all callback use of non-atomic phase and frames_written is absent."),
    ("SH02_NONATOMIC_QUEUE_REFERENCE_LIFETIME", "ACTIVE_COREAUDIO_LIFETIME",
     "The queue pointer is used through multiple source functions; ownership and no concurrent disposal while a callback uses the reference are not independently established."),
    ("SH03_ATOMIC_COUNTER_ENTRY_WINDOW", "ACTIVE_COREAUDIO_LIFETIME",
     "Callback userdata pointer is received before counter increment; a zero counter does not prohibit a later callback, absent an OS callback-admission stop proof."),
    ("SH04_LISTENER_REMOVAL_QUIESCENCE", "ACTIVE_COREAUDIO_LIFETIME",
     "Apple documents removal of a listener but this review has no independently verified synchronous drain guarantee for callbacks already executing."),
    ("SH05_SUCCESSFUL_DISPOSAL_LIMIT", "FAILED_OS_DISPOSAL_BEHAVIOR",
     "Apple documents synchronous disposal and no callbacks after dispose; that published successful-disposal contract does not qualify non-success OSStatus behavior."),
    ("SH06_DISPOSAL_ERROR_HEAP_RETENTION", "FAILED_OS_DISPOSAL_BEHAVIOR",
     "Source-level quarantine and heap retention are visible, but actual failing AudioQueueDispose OS paths, callback access windows and resource consequences were not witnessed."),
    ("SH07_C11_RELEASE_ACQUIRE_LIMIT", "C11_CALLBACK_RACE_FREEDOM",
     "Acquire-release on a particular atomic object is not a universal happens-before proof for unrelated non-atomic PCM accesses or all OS-managed callback threads."),
)
CONTRACTS = (
    ("APPLE_DISPOSE_SYNCHRONOUS_SUCCESS", "AudioQueueDispose",
     "https://developer.apple.com/documentation/audiotoolbox/audioqueuedispose",
     "DOCUMENTED_API_SUCCESS_SCOPE_ONLY",
     "Passing true requests immediate synchronous disposal; after disposal, callbacks are no longer invoked. Actual failed OSStatus and application C11 lifetime proof remain unqualified."),
    ("APPLE_LISTENER_REMOVE", "AudioQueueRemovePropertyListener",
     "https://developer.apple.com/documentation/audiotoolbox/audioqueueremovepropertylistener",
     "DOCUMENTED_REMOVE_OPERATION_ONLY",
     "Removes the specified listener and returns OSStatus. This review cannot infer a synchronous drain of already executing listener callbacks."),
    ("APPLE_NEW_OUTPUT", "AudioQueueNewOutput",
     "https://developer.apple.com/documentation/audiotoolbox/audioqueuenewoutput",
     "DOCUMENTED_CALLBACK_REGISTRATION_ONLY",
     "Creates an output AudioQueue with a callback and supplied userdata. No thread-start/publication proof is derived from this source review."),
    ("C11_MEMORY_ORDER", "atomic_flag_test_and_set_explicit",
     "https://en.cppreference.com/w/c/atomic/memory_order",
     "SPECIFICATION_NOT_FORMAL_APPLICATION_PROOF",
     "Release/acquire may create synchronization for matched atomic accesses; without read-from and complete thread-access analysis this does not settle the PCM data-race obligations."),
)
LIMITS = (
    "LEXICAL_C_SOURCE_REVIEW_NOT_FULL_C11_PARSER",
    "ALL_112_FIELD_REFERENCES_ARE_SYNTACTIC_OCCURRENCES_NOT_READ_WRITE_PROOF",
    "SOURCE_FUNCTION_ASSOCIATION_IS_NOT_RUNTIME_THREAD_OWNERSHIP_PROOF",
    "APPLE_API_DOCUMENTATION_NOT_OS_ERROR_PATH_WITNESS",
    "NO_THREAD_INTERLEAVING_SIMULATION_OR_ACTIVE_OS_CALLBACK_TEST",
    "NO_EXTERNAL_SIGNED_FORMAL_PROOF_OR_PHYSICAL_OUTPUT_QUALIFICATION",
)

class R24Error(ValueError):
    pass

def require(value, reason):
    if not value:
        raise R24Error(reason)

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def strip_comments(text):
    # Preserve each byte offset/newline for exact line references.
    return re.sub(r"/\*.*?\*/|//[^\n]*",
                  lambda m: "".join("\n" if c == "\n" else " "
                                    for c in m.group()),
                  text, flags=re.S)

def declared_fields(code):
    match = re.search(r"typedef\s+struct\s*\{(.*?)\}\s*AcousticContext\s*;",
                      code, re.S)
    require(match is not None, "AcousticContext definition missing")
    fields = []
    for m in re.finditer(
            r"(?m)^\s*(AudioQueueRef|double|uint64_t|atomic_int|atomic_uint|atomic_flag)\s+([^;]+);",
            match.group(1)):
        fields.extend((name.strip(), m.group(1))
                      for name in m.group(2).split(","))
    require(tuple(fields) == tuple((name, kind) for name,kind,_ in FIELDS),
            "context field type/name/order drift")
    return fields

def function_spans(code):
    pattern = (r"(?m)^\s*(?:static\s+)?"
               r"(?:__attribute__\s*\(\(unused\)\)\s*)?"
               r"(?:void|int)\s+([A-Za-z_]\w*)\s*\([^;{}]*\)\s*\{")
    spans = []
    for match in re.finditer(pattern, code, re.S):
        start=match.end()
        level=1
        end=None
        for offset in range(start, len(code)):
            if code[offset] == "{":
                level+=1
            elif code[offset] == "}":
                level-=1
                if level==0:
                    end=offset+1
                    break
        require(end is not None, "unterminated C function " + match.group(1))
        spans.append((match.group(1), match.start(), end))
    require(len(spans)>=8, "missing C function spans")
    return spans

def owner_of(offset, spans):
    names=[name for name,start,end in spans if start <= offset < end]
    require(len(names)==1, "C field/API reference outside one known function")
    return names[0]

def inventory(source, source_sha):
    code=strip_comments(source)
    declared_fields(code)
    # Covers the syntactic alias form used by the pinned C source. It is
    # intentionally fail closed if an unfamiliar alias or dereference appears.
    require(re.search(r"\(\s*\*\s*(?:ctx|owner_ctx)\s*\)\s*\.", code)
            is None, "new dereference syntax outside audited ctx-> surface")
    spans=function_spans(code)
    fields={}
    accesses=list(re.finditer(r"\b(?:ctx|owner_ctx)->([A-Za-z_]\w*)\b", code))
    require(len(accesses)==112, "C11 shared-state reference count drift")
    expected={name:(kind,count) for name,kind,count in FIELDS}
    require(set(m.group(1) for m in accesses)==set(expected),
            "unknown or missing AcousticContext fields")
    lines=source.splitlines()
    for name,kind,count in FIELDS:
        sites=[]
        for match in accesses:
            if match.group(1)!=name:
                continue
            function=owner_of(match.start(),spans)
            require(function in FUNC_DOMAIN,
                    "unrecognized context access function " + function)
            line=code.count("\n",0,match.start())+1
            require(0<line<=len(lines), "source position out of range")
            sites.append({"line":line, "function":function,
                          "domain_hypothesis":FUNC_DOMAIN[function],
                          "source_text":lines[line-1].strip()[:180]})
        require(len(sites)==count, "access count changed: "+name)
        fields[name]={"type":kind, "atomic_in_declaration":
                      kind.startswith("atomic_"),
                      "reference_count":count, "source_sha256":source_sha,
                      "sites":sites, "proof_of_synchronization":False}
    api=[]
    for name,expected_count in OS_CALLS:
        matches=list(re.finditer(r"\b"+re.escape(name)+r"\s*\(",code))
        require(len(matches)==expected_count, "OS API call surface drift: "+name)
        for match in matches:
            api.append({"api":name,
                        "line":code.count("\n",0,match.start())+1,
                        "function":owner_of(match.start(),spans),
                        "api_semantics_proven_by_source":False})
    require(len(api)==11,"expected eleven direct API calls")
    return fields,api

def inspect(root, source_override=None):
    root=Path(root).resolve()
    table,manifest_sha=r17.manifest_integrity(root)
    require(len(table)==128,"GEN-R24 requires exactly 128 pinned source files")
    for path in ("audits/r24_shared_state_contract_audit.py",
                 "tests/test_r24_shared_state_contract.py",
                 "RUN_GEN_R24_MAC_INTEL.command",
                 "docs/GEN_R24_SHARED_STATE_MATRIX.md",
                 "docs/GEN_R24_BUREAU_REVIEW.md"):
        require(path in table,"missing R24 pinned artifact: "+path)
    require(table[SOURCE]==r19.PINNED_ACOUSTIC_SHA256,
            "original C backend SHA has changed")
    raw=(root/SOURCE).read_bytes()
    require(digest(raw)==table[SOURCE],"C source not pinned by manifest")
    runner_raw=(root/"RUN_GEN_R24_MAC_INTEL.command").read_bytes()
    require(digest(runner_raw)==table["RUN_GEN_R24_MAC_INTEL.command"],
            "R24 native runner not SHA-pinned")
    runner=runner_raw.decode("utf-8")
    c_sources=r17.link_sources(runner)
    require(len(c_sources)==len(r17.LINK_C_ALLOWLIST)
            and set(c_sources)==r17.LINK_C_ALLOWLIST,
            "nonemitting linker allowlist changed")
    require("R24_NONEMITTING_EXECUTABLE_SYMBOL_AUDIT=PASS" in runner
            and "FREQMED_GEN_R24_BINARY" in runner,
            "R24 native no-output enforcement absent")
    original=raw.decode("utf-8")
    matrix,api=inventory(original if source_override is None
                         else source_override,table[SOURCE])
    return table,manifest_sha,matrix,api

def audit(root,archive_r19,reports,r21,r22,r23):
    table,manifest_sha,matrix,api=inspect(root)
    actual_r23=archive19.parse_json(archive19.safe_read(r23))
    recomputed=r23_audit(root,archive_r19,reports,r21,r22)
    require(actual_r23==recomputed,
            "R23 report inconsistent with R16-R22 or R19 archive")
    require(actual_r23["obligation_count"]==15
            and actual_r23["obligations_discharged"]==0
            and actual_r23["bureau_gates_open"]==11
            and actual_r23["bureau_gates_resolved"]==0,
            "R23 obligations have been silently promoted")
    for gap,gate,description in GAPS:
        require(len(description)>=85 and gate in r23_module.GATES,
                "unreviewed gap without original Bureau gate")
    contract_refs=[{"id":ident,"api":api_name,"url":url,
                    "scope":scope,"caveat":caveat,
                    "contract_proves_this_program_safe":False}
                   for ident,api_name,url,scope,caveat in CONTRACTS]
    require(sum(x["reference_count"] for x in matrix.values())==112
            and len(matrix)==19 and len(api)==11,
            "shared-state review completeness drift")
    return {
        "schema":SCHEMA,"verdict":VERDICT,
        "method":"PINNED_C11_FIELD_AND_APPLE_API_SOURCE_MATRIX",
        "manifest_sha256":manifest_sha,"source_files":len(table),
        "acoustic_source_sha256":table[SOURCE],
        "shared_field_count":19,"context_field_references":112,
        "shared_state_matrix":matrix,
        "direct_audioqueue_call_sites":api,
        "direct_audioqueue_calls":len(api),
        "contract_references":contract_refs,
        "open_r24_findings":[{"id":ident,"bureau_gate":gate,
                              "reason":reason,
                              "status":"OPEN_NOT_PROVEN"}
                             for ident,gate,reason in GAPS],
        "r23_evidence_sha256":digest(archive19.safe_read(r23)),
        "r23_proof_obligations":15,"r23_obligations_discharged":0,
        "bureau_gates_open":11,"bureau_gates_resolved":0,
        "c11_race_freedom":"NOT_PROVEN",
        "os_callback_quiescence":"NOT_PROVEN",
        "failed_audioqueue_disposal":"NOT_TESTED",
        "independent_bureau_certification":"PENDING",
        "independent_external_signature":"NONE",
        "limitations":list(LIMITS),
        "acoustic_output":"LOCKED","em_output":"LOCKED",
        "real_output":"NOT_AUTHORIZED",
        "physical_emission":"NONE","scientific_simulation":"NONE",
        "biological_exposure":"NOT_AUTHORIZED",
        "production":"NOT_AUTHORIZED",
    }

# Name the upstream verifier separately from R23 evidence Path.
r23_module=r23
r23_audit=r23.audit

def markdown(report):
    tick=chr(96)
    rows=[]
    for name,record in report["shared_state_matrix"].items():
        owners=",".join(sorted({x["function"] for x in record["sites"]}))
        rows.append("| "+tick+name+tick+" | "+record["type"]+
                    " | "+str(record["reference_count"])+" | "+owners+
                    " | NOT_PROVEN |")
    calls="\n".join("| "+x["api"]+" | "+str(x["line"])+
                    " | "+x["function"]+" |"
                    for x in report["direct_audioqueue_call_sites"])
    gaps="\n".join("| "+x["id"]+" | "+x["bureau_gate"]+
                   " | OPEN |" for x in report["open_r24_findings"])
    return ("# FREQMED GEN-R24 - C11 shared-state & CoreAudio contract review\n\n"
            "**Verdict : SHARED_STATE_MAPPED_CONTRACT_GAPS_OPEN**. "
            "**19 champs, 112 références lexicales, 11 appels AudioQueue**. "
            "Chaque localisation est liée au C SHA-256; ce n'est pas "
            "une preuve de race freedom ou de quiescence.\n\n"
            "| Champ | Déclaration | Références | Fonctions visibles | Preuve |\n"
            "|---|---|---|---|---|\n"+ "\n".join(rows)+
            "\n\n## Surface API AudioQueue directement présente\n\n"
            "| API | Ligne | Fonction |\n|---|---|---|\n"+calls+
            "\n\n## Risques ouverts du Bureau\n\n"
            "| Constat | Porte | État |\n|---|---|---|\n"+gaps+
            "\n\nApple documente le dispose(true) synchrone et l'arrêt des "
            "callbacks après disposition; ne pas extrapoler aux OSStatus "
            "en échec. La suppression de listener n'est pas une preuve "
            "indépendante d'attente de tous les callbacks en cours. "
            "L'acquire/release C11 ne prouve pas un ordre global entre "
            "le préremplissage du contrôleur et le callback.\n\n"
            "**GEN-R23 conserve 15 obligations OPEN, zéro acquittée. "
            "Les onze portes Bureau restent ouvertes.**\n\n"
            "NEVER_SIMULATION=ENFORCED; ZERO_COST_FOSS=ENFORCED; "
            "ACOUSTIC_OUTPUT=LOCKED; EM_OUTPUT=LOCKED; "
            "REAL_OUTPUT=NOT_AUTHORIZED; BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED; "
            "PRODUCTION=NOT_AUTHORIZED.\n")

def main():
    p=argparse.ArgumentParser(description="GEN-R24 C11 source + Apple contract review")
    p.add_argument("--root",required=True,type=Path)
    p.add_argument("--archive-r19",required=True,type=Path)
    for key in ("r16","r17","r18","r19","r20","r21","r22","r23"):
        p.add_argument("--"+key,required=True,type=Path)
    p.add_argument("--json",required=True,type=Path)
    p.add_argument("--markdown",required=True,type=Path)
    args=p.parse_args()
    try:
        reports={n:getattr(args,n) for n in ("r16","r17","r18","r19","r20")}
        result=audit(args.root,args.archive_r19,reports,
                     args.r21,args.r22,args.r23)
        args.json.write_text(json.dumps(result,indent=2,sort_keys=True,
                             ensure_ascii=False)+"\n",encoding="utf-8")
        args.markdown.write_text(markdown(result),encoding="utf-8")
    except (R24Error,r23_module.R23Error,ValueError,TypeError,KeyError,
            OSError,UnicodeError,IndexError) as exc:
        print("R24_C11_SHARED_STATE_CONTRACT_AUDIT=FAIL_CLOSED",str(exc))
        return 2
    print("R24_C11_SHARED_STATE_CONTRACT_AUDIT=PASS")
    print("R24_SHARED_FIELDS=19; R24_FIELD_REFERENCES=112")
    print("R24_AUDIOQUEUE_CALL_SITES=11; R24_OPEN_FINDINGS=7")
    print("R24_R23_PROOF_OBLIGATIONS=15; R24_DISCHARGED=0")
    print("R24_BUREAU_OPEN=11; R24_BUREAU_RESOLVED=0")
    print("R24_REVIEW_VERDICT="+VERDICT)
    print("R24_C11_RACE_FREEDOM=NOT_PROVEN")
    print("R24_OS_CALLBACK_QUIESCENCE=NOT_PROVEN")
    print("R24_FAILED_AUDIOQUEUE_DISPOSAL=NOT_TESTED")
    print("R24_PHYSICAL_EMISSION=NONE; R24_SCIENTIFIC_SIMULATION=NONE")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
