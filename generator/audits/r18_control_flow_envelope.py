#!/usr/bin/env python3
"""FREQMED GEN-R18: bounded lexical exit/ownership control-flow envelope.

Audits actual pinned C source, never calls CoreAudio, creates no scientific
simulation, reads no device and emits no signal. This is not a formal C CFG,
interprocedural soundness proof, memory-model proof or safety certification.
"""
import argparse
import hashlib
import json
from pathlib import Path
from r16_ownership_static_audit import lex, words, function, matching, occurrence

SCHEMA = "FREQMED_GEN_R18_CONTROL_FLOW_ENVELOPE"
METHOD = "BOUNDED_C_EXIT_GUARD_AND_OWNERSHIP_ENVELOPE"
EXPECTED = (
    ("request_rejected", "BEFORE_SESSION_CLAIM",
     "!request || request->channel!=FM_ACOUSTIC"),
    ("route_metadata_rejected", "BEFORE_SESSION_CLAIM",
     "fm_route_capture(&route)!=0 || route.output_channels==0 || "
     "!isfinite(route.nominal_sample_rate_hz) || "
     "route.nominal_sample_rate_hz<8000.0 || "
     "route.nominal_sample_rate_hz>384000.0"),
    ("route_change_rejected", "BEFORE_SESSION_CLAIM",
     "!fm_route_unchanged(&route)"),
    ("parameters_rejected", "BEFORE_SESSION_CLAIM",
     "!isfinite(request->frequency_hz) || request->frequency_hz<=0.0 || "
     "request->frequency_hz>=sr/2.0 || "
     "!isfinite(request->normalized_level) || "
     "request->normalized_level<=0.0 || request->normalized_level>1.0 || "
     "request->duration_ms==0U || request->duration_ms>60000U"),
    ("preclaim_quarantine", "BEFORE_SESSION_CLAIM",
     "atomic_load_explicit(&fm_context_quarantined,memory_order_acquire)"),
    ("session_claim_conflict", "CLAIMED_NO_ALLOCATION",
     "atomic_flag_test_and_set_explicit(&fm_session_claim,memory_order_acquire)"),
    ("postclaim_quarantine", "CLAIMED_NO_ALLOCATION",
     "atomic_load_explicit(&fm_context_quarantined,memory_order_acquire)"),
    ("allocation_failed", "ALLOCATED_BEFORE_OS_PUBLICATION", "!owner_ctx"),
    ("zero_frames", "ALLOCATED_BEFORE_OS_PUBLICATION", "!ctx->total_frames"),
    ("zero_fade", "ALLOCATED_BEFORE_OS_PUBLICATION", "ctx->fade_frames==0U"),
    ("queue_creation_failed", "OS_CALLBACK_USERDATA_POSSIBLY_PUBLISHED",
     "AudioQueueNewOutput(&fmt,output_callback,ctx,NULL,NULL,0,&ctx->queue)!=noErr"),
    ("route_binding_failed", "OS_CALLBACK_USERDATA_POSSIBLY_PUBLISHED",
     "fm_acoustic_bind_queue_to_route((void *)ctx->queue,&route)!=0"),
    ("final_controller_result", "AFTER_FINAL_CLEANUP", None),
)
FREE_GUARDS = (
    "!ctx->total_frames",
    "ctx->fade_frames==0U",
    "atomic_load_explicit(&ctx->active_output_callbacks,memory_order_acquire)==0U && "
    "atomic_load_explicit(&ctx->active_property_listeners,memory_order_acquire)==0U",
    "context_quiescent",
)
CLAIM_RELEASE_GUARDS = (
    "atomic_load_explicit(&fm_context_quarantined,memory_order_acquire)",
    "!owner_ctx", "!ctx->total_frames", "ctx->fade_frames==0U",
    FREE_GUARDS[2], "context_quiescent",
)
OS_CALL_COUNTS = {
    "AudioQueueNewOutput": 1,
    "AudioQueueDispose": 2,
    "AudioQueueStart": 1,
    "AudioQueueStop": 1,
    "AudioQueueAddPropertyListener": 1,
    "AudioQueueRemovePropertyListener": 1,
    "AudioQueueAllocateBuffer": 1,
}
UNRESOLVED = (
    "BOUNDED_LEXICAL_ANALYSIS_NOT_FORMAL_C_CFG",
    "UNBRACED_AND_PREPROCESSOR_BRANCHES_NOT_FULLY_MODELED",
    "C11_CONCURRENT_MEMORY_SAFETY_NOT_PROVEN",
    "ACTIVE_COREAUDIO_CALLBACK_LIFETIME_UNTESTED",
    "FAILED_OS_DISPOSAL_RUNTIME_UNTESTED",
    "OS_CALLBACK_QUIESCENCE_NOT_ESTABLISHED",
    "PHYSICAL_HARDWARE_CUTOFF_NOT_QUALIFIED",
    "ACOUSTIC_AND_EM_METROLOGY_NOT_PERFORMED",
    "EM_INSTRUMENT_NOT_QUALIFIED",
    "BUREAU_CERTIFICATION_PENDING",
)

class EnvelopeError(ValueError):
    pass

def require(test, reason):
    if not test:
        raise EnvelopeError(reason)

def norm(expr):
    return tuple(words(lex(expr)))

def find(tokens, expr):
    return occurrence(tokens, expr)

def one_index(tokens, expr):
    found = find(tokens, expr)
    require(len(found) == 1, "unexpected number of source sites: " + expr)
    return found[0]

def guards(tokens):
    """Read if-then token spans; handle braced and single-statement ifs."""
    result = []
    for i, (word, _) in enumerate(tokens):
        if word != "if" or i+1 >= len(tokens) or tokens[i+1][0] != "(":
            continue
        end = matching(tokens, i+1, "(", ")")
        start = end+1
        require(start < len(tokens), "missing conditional body")
        if tokens[start][0] == "{":
            body_end = matching(tokens, start, "{", "}")
            first, last = start+1, body_end-1
        else:
            first = start
            last = next((k for k in range(start, len(tokens))
                         if tokens[k][0] == ";"), None)
            require(last is not None, "unterminated unbraced conditional")
        result.append({
            "start": i, "first": first, "last": last,
            "condition": tuple(words(tokens[i+2:end])),
            "line": tokens[i][1],
        })
    return result

def direct_guard(guard_sites, index):
    enclosing = [g for g in guard_sites if g["first"] <= index <= g["last"]]
    return max(enclosing, key=lambda g: g["start"]) if enclosing else None

def statements(tokens, keyword):
    found = []
    for i, (value, line) in enumerate(tokens):
        if value != keyword:
            continue
        terminator = next((j for j in range(i+1, len(tokens))
                           if tokens[j][0] == ";"), None)
        require(terminator is not None, "unterminated " + keyword)
        found.append({
            "at": i, "line": line,
            "expression": tuple(words(tokens[i+1:terminator])),
            "until": terminator,
        })
    return found

def describe_site(stmt, guard, name, stage):
    return {
        "id": name,
        "stage": stage,
        "source_line": stmt["line"],
        "direct_guard_line": guard["line"] if guard else None,
        "direct_guard_sha256": hashlib.sha256(
            " ".join(guard["condition"] if guard else ()).encode("utf-8")
        ).hexdigest(),
    }

def examine_source(code):
    tokens = function(lex(code), "acoustic_output_impl")
    gs = guards(tokens)
    returns = statements(tokens, "return")
    require(len(returns) == 13, "unclassified/missing return site")
    claim = one_index(tokens,
        "atomic_flag_test_and_set_explicit(&fm_session_claim,memory_order_acquire)")
    allocation = one_index(tokens, "calloc(1,sizeof(*owner_ctx))")
    create = one_index(tokens,
        "AudioQueueNewOutput(&fmt,output_callback,ctx,NULL,NULL,0,&ctx->queue)")
    final_cleanup = one_index(tokens, "if (context_quiescent)")
    require(claim < allocation < create < final_cleanup,
            "invalid resource publication phase ordering")

    exits = []
    stages = {
        "BEFORE_SESSION_CLAIM": 0, "CLAIMED_NO_ALLOCATION": 0,
        "ALLOCATED_BEFORE_OS_PUBLICATION": 0,
        "OS_CALLBACK_USERDATA_POSSIBLY_PUBLISHED": 0,
        "AFTER_FINAL_CLEANUP": 0,
    }
    for n, (stmt, spec) in enumerate(zip(returns, EXPECTED)):
        name, stage, condition = spec
        guard = direct_guard(gs, stmt["at"])
        if n == len(returns)-1:
            require(guard is None, "final return is not top-level")
            require(stmt["expression"] == norm("err?-1:0"),
                    "success must be guarded by err and cleanup outcome")
            require(stmt["until"] == len(tokens)-1,
                    "new instructions after final return")
        else:
            require(guard is not None, "early exit no longer guarded")
            require(stmt["expression"] == norm("-1"),
                    "early return can claim success")
            require(guard["condition"] == norm(condition),
                    "exit guard unexpectedly widened/narrowed: " + name)
        if stage == "BEFORE_SESSION_CLAIM":
            require(stmt["at"] < claim, "preclaim exit moved after claim")
        elif stage == "CLAIMED_NO_ALLOCATION":
            require(claim < stmt["at"] < allocation,
                    "claim stage exit shifted into wrong resource lifetime")
        elif stage == "ALLOCATED_BEFORE_OS_PUBLICATION":
            require(allocation < stmt["at"] < create,
                    "allocation stage exit shifted after OS publication")
        elif stage == "OS_CALLBACK_USERDATA_POSSIBLY_PUBLISHED":
            require(create < stmt["at"] < final_cleanup,
                    "OS publication exit shifted outside controlled phase")
        else:
            require(stmt["at"] > final_cleanup, "final cleanup bypassed")
        stages[stage] += 1
        exits.append(describe_site(stmt, guard, name, stage))
    require(list(stages.values()) == [5, 2, 3, 2, 1],
            "exit site coverage per phase changed")

    frees = find(tokens, "free(owner_ctx)")
    require(len(frees) == len(FREE_GUARDS), "heap frees changed")
    releases = find(tokens,
        "atomic_flag_clear_explicit(&fm_session_claim,memory_order_release)")
    require(len(releases) == len(CLAIM_RELEASE_GUARDS),
            "session lock releases changed")
    free_records, release_records = [], []
    for i, (at, cond) in enumerate(zip(frees, FREE_GUARDS)):
        guard = direct_guard(gs, at)
        require(guard is not None and guard["condition"] == norm(cond),
                "heap free not owned by approved guard " + str(i))
        require(i < 2 and at < create or i >= 2 and at > create,
                "heap free moved across OS publication boundary")
        free_records.append({"id": "heap_release_%d" % (i+1),
                             "source_line": tokens[at][1],
                             "guard_line": guard["line"],
                             "phase": "UNPUBLISHED" if i < 2 else "POST_DISPOSAL_GUARDED"})
    for i, (at, cond) in enumerate(zip(releases, CLAIM_RELEASE_GUARDS)):
        guard = direct_guard(gs, at)
        require(guard is not None and guard["condition"] == norm(cond),
                "session release outside approved guard " + str(i))
        if i >= 2:
            free_at = frees[i-2]
            require(free_at < at and not any(
                x[0] == "return" for x in tokens[free_at:at]),
                "session claim released before owned heap")
        release_records.append({"id": "claim_release_%d" % (i+1),
                                "source_line": tokens[at][1],
                                "guard_line": guard["line"]})
    # Bind-accepted free requires BOTH successful synchronous disposal
    # and explicit zeros for BOTH callback classes, not just the direct guard.
    binding_free = frees[2]
    ancestors = [g["condition"] for g in gs
                 if g["first"] <= binding_free <= g["last"]]
    for cond in (
        "bind_dispose_status==noErr",
        "fm_acoustic_bind_queue_to_route((void *)ctx->queue,&route)!=0"):
        require(norm(cond) in ancestors, "bind free escaped disposal control")
    require(free_records[-1]["guard_line"] >= tokens[final_cleanup][1],
            "last free no longer protected by context_quiescent")

    api = {}
    for name, expected in OS_CALL_COUNTS.items():
        count = len(find(tokens, name + "("))
        require(count == expected, "new or missing OS call: " + name)
        api[name] = {"count": count,
                     "source_lines": [tokens[i][1] for i in find(tokens, name+"(")]}
    prebind_dispose, final_dispose = find(tokens, "AudioQueueDispose(")
    order = [
        one_index(tokens, "AudioQueueNewOutput("),
        prebind_dispose,
        one_index(tokens, "AudioQueueAddPropertyListener("),
        one_index(tokens, "AudioQueueAllocateBuffer("),
        one_index(tokens, "AudioQueueStart("),
        one_index(tokens, "atomic_exchange(&ctx->shutdown_in_progress,1)"),
        one_index(tokens, "AudioQueueRemovePropertyListener("),
        final_dispose,
    ]
    require(order == sorted(order), "queue lifecycle steps reordered")
    for forbidden in ("goto", "longjmp", "setjmp", "abort", "exit"):
        require(not find(tokens, forbidden), "new unclassified control escape: " + forbidden)

    quarantine_writes = find(tokens,
        "atomic_store_explicit(&fm_context_quarantined,1,memory_order_release)")
    quarantine_reads = find(tokens,
        "atomic_load_explicit(&fm_context_quarantined,memory_order_acquire)")
    require(len(quarantine_writes) == 4 and len(quarantine_reads) == 2,
            "quarantine memory order or monotonic writes changed")
    # Validate any reference to quarantine is in an expected atomic operation.
    all_quarantine = find(tokens, "fm_context_quarantined")
    require(len(all_quarantine) == 6,
            "additional unclassified quarantine variable access")
    require(len(find(tokens, "atomic_store_explicit(&fm_context_quarantined,0")) == 0,
            "quarantine can be reopened")
    require(len(find(tokens,
        "atomic_flag_test_and_set_explicit(&fm_session_claim,memory_order_acquire)")) == 1,
        "session claim must be acquire")
    require(len(find(tokens, "atomic_flag_clear_explicit(&fm_session_claim")) == 6,
            "session release order weakened or unclassified")

    return {
        "exit_sites": exits, "exit_phases": stages,
        "heap_free_sites": free_records,
        "session_release_sites": release_records,
        "os_api_sites": api,
        "quarantine_loads_acquire": len(quarantine_reads),
        "quarantine_stores_release_one": len(quarantine_writes),
        "method": METHOD,
        "source_sha256": hashlib.sha256(code.encode("utf-8")).hexdigest(),
        "output_backend_executed": False,
        "scientific_simulation": "NONE",
        "physical_emission": "NONE",
        "formal_c_memory_safety": "NOT_PROVEN",
        "unresolved": list(UNRESOLVED),
        "verdict": "STATIC_CONTROL_FLOW_ENVELOPE_PASS",
    }

def verify_chain(root, r16_path, r17_path, evidence):
    """Cross-bind R16/R17 proof files to the same pinned source and manifest."""
    root = Path(root)
    a = json.loads(Path(r16_path).read_text(encoding="utf-8"))
    b = json.loads(Path(r17_path).read_text(encoding="utf-8"))
    source = (root / "src/acoustic_macos.c").read_bytes()
    manifest = (root / "KIT_SHA256SUMS.txt").read_bytes()
    digest = lambda value: hashlib.sha256(value).hexdigest()
    canonical = json.dumps(a, ensure_ascii=False, sort_keys=True,
                           separators=(",", ":")).encode("utf-8")
    require(a.get("schema") == "FREQMED_GEN_R16_STATIC_OWNERSHIP_EVIDENCE"
            and a.get("verdict") == "STATIC_SOURCE_CONTRACT_PASS"
            and type(a.get("passed")) is int and a["passed"] == 25
            and type(a.get("failed")) is int and a["failed"] == 0,
            "R16 baseline evidence rejected")
    require(b.get("schema") == "FREQMED_GEN_R17_INDEPENDENT_EVIDENCE_VERIFICATION"
            and b.get("verification") == "PASS",
            "R17 independent evidence rejected")
    require(evidence["source_sha256"] == digest(source)
            and a.get("source_sha256") == digest(source)
            and b.get("source_sha256") == digest(source),
            "evidence not bound to same physical source bytes")
    require(b.get("manifest_sha256") == digest(manifest),
            "R17 verification detached from pinned manifest")
    require(b.get("evidence_canonical_sha256") == digest(canonical),
            "R17 verification detached from exact R16 evidence")
    require(b.get("static_checks_verified") == 25
            and type(b.get("manifest_files_verified")) is int
            and b.get("manifest_files_verified") ==
                len(manifest.decode("utf-8").splitlines()),
            "R17 verification counters incorrect")
    # R18 has a new executable runner. R17 only audits the R17 link line;
    # independently verify the current one too before trusting its evidence.
    from r17_evidence_verifier import link_sources, LINK_C_ALLOWLIST
    runner = (root / "RUN_GEN_R18_MAC_INTEL.command").read_text(encoding="utf-8")
    sources = link_sources(runner)
    require(len(sources) == len(LINK_C_ALLOWLIST)
            and set(sources) == LINK_C_ALLOWLIST
            and "R18_NONEMITTING_EXECUTABLE_SYMBOL_AUDIT=PASS" in runner
            and "FREQMED_GEN_R18_BINARY" in runner,
            "current executable is not pinned to denied source allowlist")
    return {
        "r16_evidence_sha256": digest(Path(r16_path).read_bytes()),
        "r17_evidence_sha256": digest(Path(r17_path).read_bytes()),
        "manifest_sha256": digest(manifest),
        "r16_r17_evidence_binding": "PASS",
    }

def audit(root, r16=None, r17=None):
    root = Path(root).resolve()
    code = (root / "src/acoustic_macos.c").read_text(encoding="utf-8")
    report = examine_source(code)
    report["schema"] = SCHEMA
    report["analysis_scope"] = "REAL_PINNED_SOURCE_STATIC_ONLY"
    report["real_output"] = "NOT_AUTHORIZED"
    report["production"] = "NOT_AUTHORIZED"
    report["bureau_certification"] = "PENDING"
    if r16 is not None or r17 is not None:
        require(r16 is not None and r17 is not None,
                "both independent prior evidence paths required")
        report.update(verify_chain(root, r16, r17, report))
    else:
        report["r16_r17_evidence_binding"] = "NOT_CHECKED"
    return report

def main():
    parser = argparse.ArgumentParser(description="GEN-R18 no-emission C exit envelope")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--r16-evidence", type=Path, required=True)
    parser.add_argument("--r17-evidence", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        report = audit(args.root, args.r16_evidence, args.r17_evidence)
        require(report["r16_r17_evidence_binding"] == "PASS",
                "evidence chain not independently bound")
        args.output.write_text(json.dumps(report, indent=2, sort_keys=True,
                            ensure_ascii=False)+"\n", encoding="utf-8")
    except (EnvelopeError, ValueError, OSError, TypeError, KeyError) as e:
        print("R18_CONTROL_FLOW_ENVELOPE=FAIL_CLOSED", str(e))
        return 2
    print("R18_CONTROL_FLOW_ENVELOPE=PASS")
    print("R18_EXIT_SITES=13; R18_HEAP_FREE_SITES=4; R18_CLAIM_RELEASE_SITES=6")
    print("R18_EVIDENCE_CHAIN=R16_R17_R18_BOUND")
    print("R18_COREAUDIO_RACE_FREEDOM=NOT_PROVEN")
    print("R18_PHYSICAL_EMISSION=NONE; R18_SCIENTIFIC_SIMULATION=NONE")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
