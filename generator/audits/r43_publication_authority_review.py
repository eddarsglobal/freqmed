#!/usr/bin/env python3
"""FREQMED GEN-R43: source-only C11 publication authority and ticket binding audit.
No scientific simulation, callback execution, instruments, output or OS runtime.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path
import r17_evidence_verifier as r17
import r19_adversarial_source_audit as r19
import r26_isolated_patch_gate as r26
import r42_index_forgery_admission_review as r42

SCHEMA = "FREQMED_GEN_R43_POSTCLOSE_PUBLICATION_BINDING_CAPACITY_REVIEW"
VERDICT = "LOCAL_PUBLICATION_CAS_REVIEWED_OS_AUTHENTICITY_CAPACITY_UNPROVEN"
CANDIDATE = "candidates/r43_publication_authority.c"
HEADER = "candidates/r43_publication_authority.h"
FILES = dict(r42.FILES, r43=CANDIDATE, h43=HEADER)
FINDINGS = (
 ("G43_01_OS_CALLBACK_USERDATA_UNCHANGED", "CRITICAL", "B07", "C31 still hands real OS callbacks a direct heap ctx"),
 ("G43_02_POSTCLOSE_RETURN_STILL_POSSIBLE", "CRITICAL", "B09", "Pre-close authorization can return ticket/owner after close"),
 ("G43_03_VALID_TICKET_AND_USERDATA_CAN_BE_COPIED", "CRITICAL", "B09", "Two-pointer binding is not holder authentication"),
 ("G43_04_OWNER_EXTERNAL_ALIAS_LIFETIME", "CRITICAL", "B09", "R36 cannot own all external aliases of the owner"),
 ("G43_05_FOUR_TICKETS_CANNOT_SERVE_STREAM", "CRITICAL", "B09", "Lifetime capacity remains four process-wide"),
 ("G43_06_PHYSICAL_OS_CUTOFF_UNPROVEN", "CRITICAL", "B10", "No actual OS quiescence or physical cutoff witness"),
 ("G43_07_ONLY_LOCAL_AUTHORIZE_COMMIT", "HIGH", "B09", "CAS only orders authority, not external pointer handoff"),
 ("G43_08_COMPLETION_AT_MOST_ONCE", "HIGH", "B09", "At-most-once CAS does not force eventual completion"),
 ("G43_09_LEAKED_TICKET_POINTER", "HIGH", "B09", "Opaque address may be disclosed/copied/forged"),
 ("G43_10_LEAKED_USERDATA_POINTER", "HIGH", "B09", "Expected userdata is not secret or independently authenticated"),
 ("G43_11_ADMISSION_FAILURE_BURNS_CAPACITY", "HIGH", "B09", "Failed claimed slots remain consumed"),
 ("G43_12_RESERVATION_COUNT_NEVER_REFUNDED", "HIGH", "B09", "Monotone reservation count is not production throughput"),
 ("G43_13_POST_AUTH_CLOSE_WINDOW", "HIGH", "B09", "Close can occur after authorize and before owner publication"),
 ("G43_14_ERROR_REASON_TWO_WORD_WINDOW", "HIGH", "B09", "Gate closure precedes reason latch, snapshot not instantaneous"),
 ("G43_15_NULL_OWNER_COMPENSATION", "HIGH", "B09", "Failed fm36_leave compensation is not repaired"),
 ("G43_16_PUBLISH_DENIAL_COMPENSATION", "HIGH", "B09", "Failed fm36_leave after auth denial remains unresolved"),
 ("G43_17_OWNER_REGISTRATION_ONESHOT", "HIGH", "B09", "An already claimed owner must survive exposure error"),
 ("G43_18_NO_C11_HB_FOR_PCM_QUEUE", "HIGH", "B09", "Global shared C31 fields require independent proof"),
 ("G43_19_CANDIDATE_C11_NOT_LINKED", "HIGH", "B10", "Unlinked object cannot establish real OS behavior"),
 ("G43_20_FAILED_STOP_DISPOSE_UNKNOWN", "HIGH", "B07", "CoreAudio failed stop/dispose untested"),
 ("G43_21_NO_INDEPENDENT_BUREAU_ATTESTATION", "HIGH", "B10", "Source QA is not an independent safety certification"),
)
ANCHORS = (
 ("G43_01_OS_CALLBACK_USERDATA_UNCHANGED", ("r31", "AudioQueueNewOutput(&fmt,output_callback,ctx"), ("r31", "queue_running_listener,ctx)")),
 ("G43_02_POSTCLOSE_RETURN_STILL_POSSIBLE", ("r43", " * publication after CLOSED."), ("r43", "* actual pointer publication below. This remains a CRITICAL OPEN gate.")),
 ("G43_03_VALID_TICKET_AND_USERDATA_CAN_BE_COPIED", ("h43", "* Internal ticket pointers and bound userdata are NOT authentication secrets."), ("r43", "* Both are externally reproducible; this is binding, NOT authentication.")),
 ("G43_04_OWNER_EXTERNAL_ALIAS_LIFETIME", ("r36", "_Atomic(void *) owner;"), ("r43", "* callback quiescence, actual CoreAudio stop, or memory lifetime of owner.")),
 ("G43_05_FOUR_TICKETS_CANNOT_SERVE_STREAM", ("h43", "#define FM43_LIFETIME_TICKETS 4u"), ("r43", "* Four process-lifetime slots are never recycled. No production capacity.")),
 ("G43_06_PHYSICAL_OS_CUTOFF_UNPROVEN", ("r31", "/* CRITICAL: OS stop failed."), ("r43", "* callback quiescence, actual CoreAudio stop, or memory lifetime of owner.")),
 ("G43_07_ONLY_LOCAL_AUTHORIZE_COMMIT", ("r43", "static int fm43_authorize(void)"), ("r43", "&fm43_gate,&state,desired,")),
 ("G43_08_COMPLETION_AT_MOST_ONCE", ("r43", "&slot->phase,&expected,FM43_FINISHED,"), ("r43", "* A winning ACTIVE->FINISHED CAS allows at-most-once R36 leave.")),
 ("G43_09_LEAKED_TICKET_POINTER", ("h43", "typedef struct FM43Ticket FM43Ticket;"), ("r43", "* pointers can be copied/forged once known. No secure authentication.")),
 ("G43_10_LEAKED_USERDATA_POINTER", ("r43", "if (slot->os_userdata!=expected_userdata) {"), ("r43", "* A completion must match the ticket's bound OS userdata pointer")),
 ("G43_11_ADMISSION_FAILURE_BURNS_CAPACITY", ("r43", "FM43_REJECTED,memory_order_release"), ("r43", "* Four process-lifetime slots are never recycled. No production capacity.")),
 ("G43_12_RESERVATION_COUNT_NEVER_REFUNDED", ("r43", "FM43_RESERVATIONS_MASK=0x000000ffu"), ("r43", "unsigned desired=state+1u;")),
 ("G43_13_POST_AUTH_CLOSE_WINDOW", ("r43", "if (fm43_authorize()!=0) {"), ("r43", "* actual pointer publication below. This remains a CRITICAL OPEN gate.")),
 ("G43_14_ERROR_REASON_TWO_WORD_WINDOW", ("r43", "atomic_fetch_or_explicit(&fm43_gate,FM43_CLOSED,memory_order_acq_rel)"), ("r43", "atomic_fetch_or_explicit(&fm43_faults,fault,memory_order_acq_rel)")),
 ("G43_15_NULL_OWNER_COMPENSATION", ("r43", "int leave_rc=fm36_leave(userdata);"), ("r43", "if (leave_rc!=0) fm43_latch(FM43_FAULT_LEAVE);")),
 ("G43_16_PUBLISH_DENIAL_COMPENSATION", ("r43", "fm43_latch(FM43_FAULT_PUBLISH);"), ("r43", "if (fm43_authorize()!=0) {")),
 ("G43_17_OWNER_REGISTRATION_ONESHOT", ("r36", "static atomic_flag fm36_one_shot_claim=ATOMIC_FLAG_INIT;"), ("r43", "fm36_prepare_once(owner,userdata_out)")),
 ("G43_18_NO_C11_HB_FOR_PCM_QUEUE", ("r31", "AudioQueueEnqueueBuffer(ctx->queue,buf,0,NULL)"), ("r31", "ctx->queue=NULL;")),
 ("G43_19_CANDIDATE_C11_NOT_LINKED", ("r43", "* C11 object COMPILED UNLINKED ONLY. Never execute or dispatch OS callbacks."), ("r31", "/* GEN-R3: unconditional hard denial")),
 ("G43_20_FAILED_STOP_DISPOSE_UNKNOWN", ("r31", "if (AudioQueueDispose(ctx->queue,true)!=noErr) {"), ("r43", "* callback quiescence, actual CoreAudio stop, or memory lifetime of owner.")),
 ("G43_21_NO_INDEPENDENT_BUREAU_ATTESTATION", ("h43", "* No Apple callback integration, simulation, audio or EM output."), ("r43", "* No secure authentication.")),
)
CONTRACTS = (
 ("P43_AUTH_CAS", "SINGLE_GATE_RESERVE_AND_AUTHORIZE_CAS", "POSTCLOSE_RETURN_NOT_EXCLUDED"),
 ("P43_LOCAL_CLOSE", "CLOSED_BIT_SAME_MODIFICATION_ORDER", "OS_QUIESCENCE_NOT_PROVEN"),
 ("P43_TICKET_BINDING", "OPAQUE_TICKET_AND_USERDATA_EQUALITY", "NOT_AUTHENTICATION"),
 ("P43_CAPACITY", "FOUR_LIFETIME_SLOTS_NEVER_REUSED", "UNBOUNDED_CALLBACKS_UNSUPPORTED"),
 ("P43_EXIT", "ACTIVE_TO_FINISHED_CAS", "EXACTLY_ONCE_NOT_PROVEN"),
 ("P43_SCOPE", "COMPILE_ONLY_NEVER_LINK_OR_CALL", "NO_OS_OR_PHYSICAL_WITNESS"),
)
LIMITATIONS = (
 "NO_EXECUTED_C43_CALLBACK",
 "NO_SIMULATION_OR_INTERLEAVING_EXPERIMENT",
 "NO_POST_CLOSURE_EXTERNAL_HANDOFF_EXCLUSION",
 "NO_AUTHENTICATION_OF_COPIED_TICKET_USERDATA_PAIR",
 "NO_PRODUCTION_CAPACITY_OR_SLOT_REUSE",
 "NO_GLOBAL_OWNER_LIFETIME_OR_C11_RACE_PROOF",
 "NO_OS_QUIESCENCE_OR_HARDWARE_CUTOFF",
 "NO_BUREAU_CERTIFICATION",
)
class R43Error(ValueError):
    pass

def require(value, reason):
    if not value:
        raise R43Error(reason)

def sha(data):
    return hashlib.sha256(data).hexdigest()

def func(src, name):
    expression = r"^(?:static\s+)?(?:int|void|unsigned)\s+" + re.escape(name) + r"\s*\([^;]*\)\s*\{"
    matches = list(re.finditer(expression, src, re.M | re.S))
    require(len(matches) == 1, "R43 function missing or repeated: " + name)
    start = matches[0].start()
    brace = src.index("{", start)
    level = 0
    for n in range(brace, len(src)):
        if src[n] == "{":
            level += 1
        elif src[n] == "}":
            level -= 1
            if level == 0:
                return src[start:n + 1]
    raise R43Error("Unbalanced C source " + name)

def order(src, tokens, label):
    require(all(x in src for x in tokens), "Missing contract " + label)
    places = [src.index(x) for x in tokens]
    require(places == sorted(places) and len(set(places)) == len(places),
            "Contract order changed " + label)

def observe(c43, h43, sources):
    r42.observe(*[sources[k] for k in
        ("r42", "h42", "r41", "h41", "r40", "h40", "r39", "r31", "r36", "r37")])
    require(c43.startswith("/* SPDX-License-Identifier: Apache-2.0 */") and
            h43.startswith("/* SPDX-License-Identifier: Apache-2.0 */"),
            "R43 license missing")
    for forbidden in ("AudioQueueStart(", "AudioQueueStop(", "AudioQueueNewOutput(",
                      "AudioQueueDispose(", "AudioQueueEnqueueBuffer(",
                      "malloc(", "calloc(", "realloc(", "free(",
                      "pthread_create(", "dlopen(", "dlsym("):
        require(forbidden not in c43, "R43 forbidden output/allocator " + forbidden)
    require(h43.count("typedef struct FM43Ticket FM43Ticket;") == 1
            and "struct FM43Ticket {" not in h43
            and "#define FM43_LIFETIME_TICKETS 4u" in h43,
            "R43 must expose an incomplete ticket type and four lifetime slots")
    require(c43.count("struct FM43Ticket {") == 1
            and c43.count("{ATOMIC_VAR_INIT(FM43_UNUSED),NULL}") == 4
            and "static atomic_uint fm43_gate=ATOMIC_VAR_INIT(0u);" in c43
            and "static atomic_uint fm43_faults=ATOMIC_VAR_INIT(0u);" in c43
            and "FM43_AUTH_INCREMENT=0x00000100u" in c43,
            "R43 ticket structure or joint atomic CAS contract missing")
    for api in ("fm43_register_owner_once", "fm43_begin", "fm43_complete",
                "fm43_seal"):
        require("int " + api + "(" in h43, "R43 public API missing " + api)
        func(c43, api)
    require("unsigned fm43_fault_snapshot(void);" in h43,
            "R43 fault API missing")
    for dependency in ("fm36_prepare_once", "fm36_mark_exposed",
                       "fm36_try_enter", "fm36_leave", "fm36_seal"):
        require("extern int " + dependency + "(" in c43,
                "R43 R36 owner dependency missing " + dependency)
    latch = func(c43, "fm43_latch")
    order(latch, ("atomic_fetch_or_explicit(&fm43_gate,FM43_CLOSED",
                  "atomic_fetch_or_explicit(&fm43_faults,fault"),
          "R43 fault seals gate before reason")
    reserve = func(c43, "fm43_reserve")
    order(reserve, ("if ((state & FM43_CLOSED)!=0u) return -1;",
                    "if ((state & FM43_RESERVATIONS_MASK)>=FM43_LIFETIME_TICKETS)",
                    "unsigned desired=state+1u;",
                    "&fm43_gate,&state,desired,"),
          "R43 reservation closure and CAS")
    authorize = func(c43, "fm43_authorize")
    order(authorize, ("if ((state & FM43_CLOSED)!=0u) return -1;",
                      "unsigned used=state & FM43_RESERVATIONS_MASK;",
                      "unsigned authorized=(state & FM43_AUTH_MASK)>>FM43_AUTH_SHIFT;",
                      "if (authorized>=used) return -1;",
                      "unsigned desired=state+FM43_AUTH_INCREMENT;",
                      "&fm43_gate,&state,desired,"),
          "R43 authorize joint gate CAS")
    require("atomic_compare_exchange_weak_explicit(" in reserve
            and "atomic_compare_exchange_weak_explicit(" in authorize
            and authorize.count("&fm43_gate,&state,desired,") == 1,
            "R43 two-phase CAS not on same gate word")
    register = func(c43, "fm43_register_owner_once")
    order(register, ("*userdata_out=NULL;", "fm36_prepare_once(owner,userdata_out)",
                     "fm36_mark_exposed(*userdata_out)"),
          "R43 owner registration")
    begin = func(c43, "fm43_begin")
    order(begin, ("*ticket_out=NULL;", "*owner_out=NULL;",
                  "if (fm43_reserve()!=0) return -1;",
                  "&slot->phase,&expected,FM43_RESERVED,",
                  "fm36_try_enter(userdata,&owner)",
                  "if (fm43_authorize()!=0) {",
                  "slot->os_userdata=userdata;",
                  "FM43_ACTIVE,memory_order_release",
                  "*owner_out=owner;",
                  "*ticket_out=slot;"),
          "R43 entry handoff")
    require(begin.count("FM43_REJECTED,memory_order_release") == 3
            and begin.count("int leave_rc=fm36_leave(userdata);") == 2
            and begin.count("if (leave_rc!=0) fm43_latch(FM43_FAULT_LEAVE);") == 2
            and "fm43_latch(FM43_FAULT_CAPACITY);" in begin,
            "R43 fail closed and compensating leaves missing")
    complete = func(c43, "fm43_complete")
    order(complete, ("if (!ticket || !expected_userdata) {",
                     "if (ticket!=slot) continue;",
                     "atomic_load_explicit(&slot->phase,memory_order_acquire)",
                     "if (slot->os_userdata!=expected_userdata) {",
                     "&slot->phase,&expected,FM43_FINISHED,",
                     "int rc=fm36_leave(slot->os_userdata);"),
          "R43 pointer + userdata binding before at-most-once completion")
    require(complete.count("fm36_leave(") == 1 and
            "fm43_latch(FM43_FAULT_TOKEN_MISMATCH)" in complete and
            "fm43_latch(FM43_FAULT_DUPLICATE_EXIT)" in complete,
            "R43 ticket binding or terminal error missing")
    seal = func(c43, "fm43_seal")
    order(seal, ("atomic_fetch_or_explicit(&fm43_gate,FM43_CLOSED",
                 "fm36_seal(userdata)"), "R43 seal order")
    for key in ("r31", "r36", "r37", "r39", "r40", "r41", "r42"):
        require("fm43_" not in sources[key],
                "R43 integrated into earlier C candidate " + key)
    require(len(FINDINGS) == 21 and len(ANCHORS) == 21
            and len(CONTRACTS) == 6
            and sum(x[1] == "CRITICAL" for x in FINDINGS) == 6
            and [x[0] for x in FINDINGS] == [x[0] for x in ANCHORS],
            "R43 Bureau ledger cardinality drift")
    sources = dict(sources, r43=c43, h43=h43)
    for ident, first, second in ANCHORS:
        for key, needle in (first, second):
            require(needle in sources[key], "R43 evidence missing " + ident + ": " + needle)
    return {x[0]: "OPEN_NOT_PROVEN" for x in FINDINGS}

def inspect(root, override=None, header_override=None):
    root = Path(root).resolve()
    table, manifest = r17.manifest_integrity(root)
    require(len(table) == 252, "GEN-R43 exactly 252 SHA-pinned generator files expected")
    required = (CANDIDATE, HEADER,
                "audits/r43_publication_authority_review.py",
                "tests/test_r43_publication_authority_review.py",
                "RUN_GEN_R43_MAC_INTEL.command",
                "docs/GEN_R43_PUBLICATION_HANDOFF_DESIGN.md",
                "docs/GEN_R43_BUREAU_PROOF_GATES.md",
                "docs/GEN_R43_CAPACITY_BINDING_MATRIX.md")
    require(all(item in table for item in required),
            "R43 unpinned source, auditor, test or proof document")
    earlier = r42.inspect(root)
    for key in r42.FILES:
        require(earlier[2][key] == table[FILES[key]],
                "R43 historic C candidate changed " + key)
    require(table[r26.ORIGINAL] == r19.PINNED_ACOUSTIC_SHA256,
            "R43 original acoustic backend changed")
    raw = {key: (root / path).read_bytes() for key, path in FILES.items()}
    require(all(sha(raw[key]) == table[path] for key, path in FILES.items()),
            "R43 candidate/old-source SHA mismatch")
    sources = {key: value.decode("utf-8") for key, value in raw.items()}
    found = observe(sources["r43"] if override is None else override,
                    sources["h43"] if header_override is None else header_override,
                    sources)
    runner = (root / "RUN_GEN_R43_MAC_INTEL.command").read_text(encoding="utf-8")
    require(set(r17.link_sources(runner)) == r17.LINK_C_ALLOWLIST,
            "R43 hard-denied CLI allowlist changed")
    segments = runner.split(' -o "$WORK/freqmed-gen"')
    require(len(segments) == 2, "R43 hard-denied binary link command missing")
    linked = segments[1].split("-framework CoreAudio", 1)[0]
    require("output_hard_denied.c" in linked, "R43 explicit no-output implementation missing")
    for bad in ("r43_publication_authority.c", "r42_admission_gate_ticket.c",
                "r41_index_ticket.c", "r40_opaque_ticket.c",
                "r39_owner_lifetime_exit_ticket.c", "r37_callback_lease_adapter.c",
                "r36_stable_userdata_anchor.c", "acoustic_macos_r31.c",
                "src/acoustic_macos.c"):
        require(bad not in linked, "R43 candidate linked to CLI " + bad)
    for token in ("R43_PUBLICATION_AUTHORITY_REVIEW=PASS",
                  "R43_PUBLICATION_AUTHORITY_OBJECT=COMPILED_UNLINKED",
                  "R43_ATOMIC_GATE_OBJECT=COMPILED_UNLINKED",
                  "R43_INDEX_TICKET_OBJECT=COMPILED_UNLINKED",
                  "R43_OPAQUE_TICKET_OBJECT=COMPILED_UNLINKED",
                  "R43_EXIT_TICKET_OBJECT=COMPILED_UNLINKED",
                  "R43_CALLBACK_LEASE_OBJECT=COMPILED_UNLINKED",
                  "R43_STABLE_ANCHOR_OBJECT=COMPILED_UNLINKED",
                  "R43_R31_CANDIDATE_OBJECT=COMPILED_UNLINKED",
                  "R43_NONEMITTING_EXECUTABLE_SYMBOL_AUDIT=PASS",
                  "R43_BUREAU_PROOF_DOSSIER=48_FILES_SHA256_PASS",
                  "R43_TESTCASE_RUN_SLOT=PASS",
                  "FREQMED_GEN_R43_EVIDENCE_DIR",
                  "FREQMED_GEN_R43_BINARY"):
        require(token in runner, "R43 missing nonemitting runner gate " + token)
    return table, manifest, {key: sha(raw[key]) for key in FILES}, found

def anchor(source, path, fragment, digest):
    require(fragment in source, "R43 missing anchored evidence " + fragment)
    return {"path": path,
            "line": source.count("\n", 0, source.index(fragment)) + 1,
            "sha256": digest, "exact_text": fragment}

def audit(root, archive_r19, reports):
    table, manifest, digests, findings = inspect(root)
    previous = r42.audit(root, archive_r19, reports)
    actual = json.loads(Path(reports["r42"]).read_text(encoding="utf-8"))
    require(previous == actual, "R43 previous R42 report disagrees with recalculation")
    require(previous["r42_findings_open"] == 20 and
            previous["r42_critical_open"] == 6 and
            previous["r41_findings_open"] == 19 and
            previous["r40_findings_open"] == 18 and
            previous["r39_findings_open"] == 16 and
            previous["r38_findings_open"] == 18 and
            previous["r37_findings_open"] == 14 and
            previous["r36_findings_open"] == 12 and
            previous["r23_obligations_open"] == 15 and
            previous["r24_findings_open"] == 7 and
            previous["bureau_gates_open"] == 11 and
            previous["bureau_gates_resolved"] == 0,
            "R43 historic safety obligations cannot be discharged")
    raw = {key: (Path(root) / path).read_text(encoding="utf-8")
           for key, path in FILES.items()}
    rows = []
    for (ident, severity, seat, statement), (anchor_id, a, b) in zip(FINDINGS, ANCHORS):
        require(ident == anchor_id, "R43 ledger/evidence mismatch")
        rows.append({"id": ident, "severity": severity, "seat": seat,
                     "status": findings[ident], "open_obligation": statement,
                     "real_OS_callback_executed": False,
                     "source_anchors": [anchor(raw[k], FILES[k], fragment, digests[k])
                                        for k, fragment in (a, b)]})
    return {
      "schema": SCHEMA, "verdict": VERDICT,
      "method": "SHA_PINNED_C11_SOURCE_ONLY_PUBLICATION_AUTHORITY_AUDIT",
      "manifest_sha256": manifest, "source_count": len(table),
      "source_digests": digests, "r42_report_sha256": sha(Path(reports["r42"]).read_bytes()),
      "r43_findings": rows, "r43_findings_open": 21, "r43_critical_open": 6,
      "r43_contracts": [{"id": c[0], "source": c[1], "limitation": c[2]} for c in CONTRACTS],
      "r43_gate": "SHARED_CLOSED_RESERVE_AUTHORIZE_CAS",
      "r43_post_close_new_authorizations": "DENIED_IN_GATE_MODIFICATION_ORDER",
      "r43_post_close_pointer_return": "NOT_EXCLUDED",
      "r43_ticket_userdata_binding": "SOURCE_ONLY_NOT_AUTHENTICATION",
      "r43_ticket_authenticity": "NOT_PROVEN",
      "r43_process_lifetime_capacity": 4, "r43_slot_reuse": False,
      "r43_exactly_once_completion": "NOT_PROVEN",
      "r43_owner_lifetime": "NOT_PROVEN",
      "r43_real_OS_callbacks": 0, "r43_historical_C_changes": 0,
      "r42_findings_open": 20, "r42_critical_open": 6,
      "r41_findings_open": 19, "r41_critical_open": 5,
      "r40_findings_open": 18, "r40_critical_open": 5,
      "r39_findings_open": 16, "r39_critical_open": 4,
      "r38_findings_open": 18, "r38_critical_open": 5,
      "r37_findings_open": 14, "r37_critical_open": 4,
      "r36_findings_open": 12, "r36_critical_open": 4,
      "r23_obligations_open": 15, "r24_findings_open": 7,
      "bureau_gates_open": 11, "bureau_gates_resolved": 0,
      "C11_race_freedom": "NOT_PROVEN",
      "OS_callback_quiescence": "NOT_PROVEN",
      "physical_cutoff": "NOT_PROVEN",
      "Bureau_certification": "PENDING",
      "scientific_simulation": "NONE", "physical_emission": "NONE",
      "acoustic_output": "LOCKED", "em_output": "LOCKED",
      "real_output": "NOT_AUTHORIZED", "biological_exposure": "NOT_AUTHORIZED",
      "production": "NOT_AUTHORIZED", "limitations": list(LIMITATIONS),
    }

def markdown(report):
    table = "\n".join("| " + r["id"] + " | " + r["severity"] + " | OPEN_NOT_PROVEN |"
                      for r in report["r43_findings"])
    return (
      "# FREQMED GEN-R43 — Post-closure, Ticket Binding & Lifetime Capacity\n\n"
      "**Verdict: LOCAL_PUBLICATION_CAS_REVIEWED_OS_AUTHENTICITY_CAPACITY_UNPROVEN.**\n\n"
      "CLOSED/reservation/authorization share one C11 gate word. A post-CLOSED"
      " authorization CAS is impossible in that word's modification order,"
      " but the pointer handoff can still follow an earlier authorization."
      " Ticket/userdata binding does not authenticate the caller. Four"
      " never-recycled slots cannot support unbounded OS callbacks.\n\n"
      "| Obligation | Severity | Status |\n|---|---|---|\n" + table + "\n\n"
      "21 OPEN (6 CRITICAL); historical Bureau 11 OPEN/0 resolved.\n"
      "NEVER_SIMULATION=ENFORCED; ZERO_COST_FOSS=ENFORCED; "
      "ACOUSTIC_OUTPUT=LOCKED; EM_OUTPUT=LOCKED; REAL_OUTPUT=NOT_AUTHORIZED; "
      "BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED; PRODUCTION=NOT_AUTHORIZED.\n")

def main():
    parser = argparse.ArgumentParser(description="GEN-R43 nonemitting source-only C11 review")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--archive-r19", type=Path, required=True)
    for n in range(16, 43):
        parser.add_argument("--r" + str(n), type=Path, required=True)
    parser.add_argument("--json", type=Path, required=True)
    parser.add_argument("--markdown", type=Path, required=True)
    args = parser.parse_args()
    try:
        reports = {"r" + str(n): getattr(args, "r" + str(n))
                   for n in range(16, 43)}
        result = audit(args.root, args.archive_r19, reports)
        args.json.write_text(json.dumps(result, sort_keys=True, indent=2,
                             ensure_ascii=False) + "\n", encoding="utf-8")
        args.markdown.write_text(markdown(result), encoding="utf-8")
    except (R43Error, r42.R42Error, ValueError, TypeError, KeyError,
            IndexError, OSError, UnicodeError) as err:
        print("R43_PUBLICATION_AUTHORITY_REVIEW=FAIL_CLOSED", str(err))
        return 2
    print("R43_PUBLICATION_AUTHORITY_REVIEW=PASS")
    print("R43_FINDINGS=21_OPEN; R43_CRITICAL=6_OPEN")
    print("R43_RESERVE_AUTHORIZE=CLOSED_SAME_C11_GATE")
    print("R43_POSTCLOSE_AUTHORIZATION=DENIED; RETURN_AFTER_CLOSE=NOT_EXCLUDED")
    print("R43_TICKET_USERDATA_BINDING=SOURCE_ONLY_NOT_AUTHENTICATION")
    print("R43_PROCESS_LIFETIME_CAPACITY=4; REUSE=NO")
    print("R43_R42_FINDINGS=20_OPEN; R43_BUREAU_GATES=11_OPEN")
    print("R43_BUREAU_RESOLVED=0; R43_OS_CALLBACKS=0")
    print("R43_REVIEW_VERDICT=" + VERDICT)
    print("R43_OWNER_LIFETIME=NOT_PROVEN; R43_EXACTLY_ONCE=NOT_PROVEN")
    print("R43_OS_QUIESCENCE=NOT_PROVEN; R43_PHYSICAL_CUTOFF=NOT_PROVEN")
    print("R43_PHYSICAL_EMISSION=NONE; R43_SCIENTIFIC_SIMULATION=NONE")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
