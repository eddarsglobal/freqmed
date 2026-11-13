#!/usr/bin/env python3
"""GEN-R16 offline static ownership evidence from actual FREQMED C source.

This is a bounded lexical/control-block audit, NOT a compiler-grade C CFG,
formal proof of race-freedom, simulation, physical test or hardware authorization.
No network, AudioQueue call, sensor reading or device access is performed.
Only Python 3 standard library; fails closed on unrecognized source structure.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

TOKEN = re.compile(
    r"/\*[\s\S]*?\*/|//[^\n]*|"
    r'"(?:\\.|[^"\\])*"|'
    r"'(?:\\.|[^'\\])*'|"
    r"[A-Za-z_][A-Za-z0-9_]*|->|==|!=|>=|<=|&&|\|\||[^\s]"
)

def lex(code):
    """Tokenize real C while discarding comments, retaining source line numbers."""
    result = []
    for hit in TOKEN.finditer(code):
        value = hit.group()
        if value.startswith("/*") or value.startswith("//"):
            continue
        result.append((value, code.count("\n", 0, hit.start()) + 1))
    return result

def words(tokens):
    return [v for v, _ in tokens]

def contains(tokens, pattern):
    target = words(lex(pattern))
    values = words(tokens)
    if not target:
        return False
    return any(values[i:i+len(target)] == target
               for i in range(len(values)-len(target)+1))

def occurrence(tokens, pattern):
    target = words(lex(pattern))
    values = words(tokens)
    if not target:
        return []
    return [i for i in range(len(values)-len(target)+1)
            if values[i:i+len(target)] == target]

def matching(tokens, at, opening, closing):
    if at >= len(tokens) or tokens[at][0] != opening:
        raise ValueError("unexpected delimiter at token index " + str(at))
    depth = 0
    for i in range(at, len(tokens)):
        v = tokens[i][0]
        if v == opening:
            depth += 1
        elif v == closing:
            depth -= 1
            if depth == 0:
                return i
    raise ValueError("unbalanced C delimiters")

def function(tokens, name):
    positions = [i for i, (v, _) in enumerate(tokens) if v == name
                 and i+1 < len(tokens) and tokens[i+1][0] == "("]
    bodies = []
    for i in positions:
        end = matching(tokens, i+1, "(", ")")
        if end+1 < len(tokens) and tokens[end+1][0] == "{":
            close = matching(tokens, end+1, "{", "}")
            bodies.append(tokens[end+2:close])
    if len(bodies) != 1:
        raise ValueError(name + ": expected one function definition, got " +
                         str(len(bodies)))
    return bodies[0]

def if_blocks(tokens):
    """Extract braces-delimited if/else blocks, including nested branches."""
    result = []
    for i, (v, _) in enumerate(tokens):
        if v != "if" or i+1 >= len(tokens) or tokens[i+1][0] != "(":
            continue
        end_cond = matching(tokens, i+1, "(", ")")
        if end_cond+1 >= len(tokens) or tokens[end_cond+1][0] != "{":
            continue
        end_then = matching(tokens, end_cond+1, "{", "}")
        following = end_then+1
        otherwise = []
        if (following+1 < len(tokens) and tokens[following][0] == "else"
                and tokens[following+1][0] == "{"):
            end_else = matching(tokens, following+1, "{", "}")
            otherwise = tokens[following+2:end_else]
        result.append({
            "condition": tokens[i+2:end_cond],
            "then": tokens[end_cond+2:end_then],
            "else": otherwise,
            "line": tokens[i][1],
            "at": i,
        })
    return result

def one(blocks, condition_marker):
    found = [b for b in blocks if contains(b["condition"], condition_marker)]
    if len(found) != 1:
        raise ValueError("expected one if-block for " + condition_marker +
                         ", got " + str(len(found)))
    return found[0]

def audit(root):
    root = Path(root).resolve()
    source_file = root / "src" / "acoustic_macos.c"
    denied_file = root / "src" / "em_backend.c"
    run_file = root / "RUN_GEN_R16_MAC_INTEL.command"
    source = source_file.read_text(encoding="utf-8")
    denied = denied_file.read_text(encoding="utf-8")
    runner = run_file.read_text(encoding="utf-8")
    tokens = lex(source)
    implementation = function(tokens, "acoustic_output_impl")
    callbacks = function(tokens, "output_callback")
    listeners = function(tokens, "queue_running_listener")
    public = function(tokens, "fm_acoustic_physical_output")
    blocks = if_blocks(implementation)
    checks = []

    def check(identifier, predicate, line):
        checks.append({"id": identifier, "result": "PASS" if predicate else "FAIL",
                       "source_line": int(line), "basis": "STATIC_C_TOKENS"})

    def index(pattern):
        p = occurrence(implementation, pattern)
        if len(p) != 1:
            raise ValueError("expected one marker: " + pattern + " got " + str(len(p)))
        return p[0]

    claim = index("atomic_flag_test_and_set_explicit(&fm_session_claim,memory_order_acquire)")
    allocate = index("calloc(1,sizeof(*owner_ctx))")
    check("admission_claim_precedes_heap_allocation", claim < allocate,
          implementation[claim][1])
    quarantine_uses = occurrence(implementation,
        "atomic_load_explicit(&fm_context_quarantined,memory_order_acquire)")
    check("quarantine_checked_before_and_after_claim",
          len(quarantine_uses) == 2 and quarantine_uses[0] < claim <
          quarantine_uses[1] < allocate, implementation[claim][1])
    recheck = one(blocks,
        "atomic_load_explicit(&fm_context_quarantined,memory_order_acquire)")
    check("recheck_releases_unpublished_session_claim",
          contains(recheck["then"], "atomic_flag_clear_explicit(&fm_session_claim,memory_order_release)")
          and contains(recheck["then"], "return -1"), recheck["line"])
    check("callback_context_is_heap_owned",
          contains(implementation, "AcousticContext *owner_ctx=(AcousticContext*)calloc(1,sizeof(*owner_ctx))")
          and contains(implementation, "AcousticContext *ctx=owner_ctx")
          and contains(implementation, "AudioQueueNewOutput(&fmt,output_callback,ctx,NULL,NULL,0,&ctx->queue)")
          and not contains(implementation, "AcousticContext ctx;"), implementation[allocate][1])

    alloc_failure = one(blocks, "!owner_ctx")
    frame_failure = one(blocks, "!ctx->total_frames")
    fade_failure = one(blocks, "ctx->fade_frames==0U")
    check("alloc_failure_releases_claim",
          contains(alloc_failure["then"], "atomic_flag_clear_explicit(&fm_session_claim,memory_order_release)")
          and not contains(alloc_failure["then"], "free(owner_ctx)"),
          alloc_failure["line"])
    for name, b in [("zero_frames_releases_unpublished_heap", frame_failure),
                    ("zero_fade_releases_unpublished_heap", fade_failure)]:
        check(name, contains(b["then"], "free(owner_ctx)") and
              contains(b["then"], "atomic_flag_clear_explicit(&fm_session_claim,memory_order_release)") and
              contains(b["then"], "return -1"), b["line"])

    creation = one(blocks,
        "AudioQueueNewOutput(&fmt,output_callback,ctx,NULL,NULL,0,&ctx->queue)!=noErr")
    check("queue_creation_failure_quarantines_without_free",
          contains(creation["then"], "atomic_store(&ctx->shutdown_in_progress,1)") and
          contains(creation["then"], "atomic_store(&ctx->stop_requested,1)") and
          contains(creation["then"], "atomic_store_explicit(&fm_context_quarantined,1,memory_order_release)") and
          not contains(creation["then"], "free(owner_ctx)") and
          contains(creation["then"], "return -1"), creation["line"])

    binding = one(blocks,
        "fm_acoustic_bind_queue_to_route((void *)ctx->queue,&route)!=0")
    binding_body = binding["then"]
    binding_dispose = one(if_blocks(binding_body), "bind_dispose_status==noErr")
    bind_success_children = if_blocks(binding_dispose["then"])
    count_guard = [b for b in bind_success_children
                   if contains(b["condition"], "ctx->active_output_callbacks")
                   and contains(b["condition"], "ctx->active_property_listeners")]
    check("rejected_route_disposes_synchronously",
          contains(binding_body, "AudioQueueDispose(ctx->queue,true)") and
          contains(binding_body, "atomic_store(&ctx->stop_requested,1)"),
          binding["line"])
    check("binding_cleanup_checks_both_callback_counters",
          len(count_guard) == 1 and contains(count_guard[0]["then"], "free(owner_ctx)") and
          contains(count_guard[0]["then"],
                   "atomic_flag_clear_explicit(&fm_session_claim,memory_order_release)"),
          binding_dispose["line"])
    check("binding_disposal_failure_never_frees",
          contains(binding_dispose["else"],
                   "atomic_store_explicit(&fm_context_quarantined,1,memory_order_release)")
          and not contains(binding_dispose["else"], "free(owner_ctx)") and
          len(count_guard) == 1 and
          contains(count_guard[0]["else"],
                   "atomic_store_explicit(&fm_context_quarantined,1,memory_order_release)"),
          binding_dispose["line"])

    registration = one(blocks,
        "AudioQueueAddPropertyListener(ctx->queue,kAudioQueueProperty_IsRunning,queue_running_listener,ctx)!=noErr")
    check("listener_registration_failure_records_uncertainty",
          contains(registration["then"], "listener_registration_uncertain=1") and
          contains(registration["then"],
                   "fm_latch_first_fault(ctx,FM_FAULT_LISTENER_REGISTRATION)") and
          contains(registration["then"], "err=1"),
          registration["line"])
    removal = one(blocks,
        "AudioQueueRemovePropertyListener(ctx->queue,kAudioQueueProperty_IsRunning,queue_running_listener,ctx)!=noErr")
    check("listener_removal_failure_records_uncertainty",
          contains(removal["then"], "listener_remove_failed=1") and
          contains(removal["then"],
                   "fm_latch_first_fault(ctx,FM_FAULT_LISTENER_REMOVAL)"),
          removal["line"])

    check("callback_entry_exit_accounting",
          len(occurrence(callbacks,
              "atomic_fetch_add_explicit(&ctx->active_output_callbacks,1U,memory_order_acq_rel)")) == 1 and
          len(occurrence(callbacks,
              "atomic_fetch_sub_explicit(&ctx->active_output_callbacks,1U,memory_order_acq_rel)")) == 1 and
          len(occurrence(listeners,
              "atomic_fetch_add_explicit(&ctx->active_property_listeners,1U,memory_order_acq_rel)")) == 1 and
          len(occurrence(listeners,
              "atomic_fetch_sub_explicit(&ctx->active_property_listeners,1U,memory_order_acq_rel)")) == 1,
          callbacks[0][1])
    check("callback_pcm_writer_gate",
          contains(callbacks, "atomic_flag_test_and_set_explicit(&ctx->pcm_writer_gate,memory_order_acquire)") and
          contains(callbacks, "atomic_flag_clear_explicit(&ctx->pcm_writer_gate,memory_order_release)") and
          contains(callbacks, "FM_FAULT_OVERLAPPING_PCM_CALLBACK"), callbacks[0][1])
    check("callback_does_not_request_stop",
          not contains(callbacks, "AudioQueueStop") and
          not contains(callbacks, "AudioQueueDispose") and
          not contains(listeners, "AudioQueueStop"), callbacks[0][1])

    barrier = index("atomic_exchange(&ctx->shutdown_in_progress,1)")
    stop = index("atomic_store(&ctx->stop_requested,1)")
    # There are other stop stores in early error branches: use the first stop
    # operation after the one-shot barrier.
    stop_after = [i for i in occurrence(implementation,
                  "atomic_store(&ctx->stop_requested,1)") if i > barrier]
    remover = index("AudioQueueRemovePropertyListener")
    dispose_call = index("AudioQueueDispose(ctx->queue,true)!=noErr")
    check("shutdown_barrier_precedes_listener_removal_and_dispose",
          len(stop_after) >= 1 and barrier < stop_after[0] < remover < dispose_call,
          implementation[barrier][1])

    disposed = one(blocks, "AudioQueueDispose(ctx->queue,true)!=noErr")
    check("failed_disposal_retains_queue_and_heap",
          contains(disposed["then"], "fm_latch_first_fault(ctx,FM_FAULT_DISPOSAL)") and
          contains(disposed["then"], "err=1") and
          not contains(disposed["then"], "ctx->queue=NULL") and
          not contains(disposed["then"], "free(owner_ctx)"), disposed["line"])
    check("successful_disposal_alone_confirms_and_clears",
          contains(disposed["else"], "atomic_store(&ctx->dispose_confirmed,1)") and
          contains(disposed["else"], "ctx->queue=NULL") and
          not contains(disposed["then"], "atomic_store(&ctx->dispose_confirmed,1)"),
          disposed["line"])

    quiescence_position = index("const int context_quiescent")
    quiescence_condition = implementation[quiescence_position:index("if (context_quiescent)")]
    quiescence = one(blocks, "context_quiescent")
    check("final_release_requires_disposal_and_listener_clarity",
          contains(quiescence_condition, "atomic_load(&ctx->dispose_confirmed)") and
          contains(quiescence_condition, "!listener_registration_uncertain") and
          contains(quiescence_condition, "!listener_remove_failed") and
          contains(quiescence_condition, "ctx->active_output_callbacks") and
          contains(quiescence_condition, "ctx->active_property_listeners") and
          contains(quiescence["then"], "free(owner_ctx)"),
          implementation[quiescence_position][1])
    check("final_quarantine_keeps_context_and_claim",
          contains(quiescence["else"],
                   "atomic_store_explicit(&fm_context_quarantined,1,memory_order_release)") and
          not contains(quiescence["else"], "free(owner_ctx)") and
          not contains(quiescence["else"], "atomic_flag_clear_explicit(&fm_session_claim"),
          quiescence["line"])

    # Fail closed on new, unaudited heap-free sites. Four authorized sites:
    # invalid-frame and invalid-fade pre-publication, rejected binding after
    # synchronous disposal and zero counters, and final quiescent cleanup.
    free_sites = occurrence(implementation, "free(owner_ctx)")
    expected = [frame_failure["then"], fade_failure["then"],
                count_guard[0]["then"] if len(count_guard) == 1 else [],
                quiescence["then"]]
    check("every_heap_free_site_classified",
          len(free_sites) == 4 and len(expected) == 4 and
          all(contains(part, "free(owner_ctx)") for part in expected),
          implementation[free_sites[0]][1] if free_sites else 1)

    check("public_acoustic_entry_unconditionally_denied",
          words(public) == words(lex("(void)command; return -1;")),
          public[0][1] if public else 1)
    check("em_source_contains_hard_denial",
          "return -1;" in denied and
          "fm_em_try_physical_emission" in denied, 1)
    # Read only the actual link command slice, not the isolated compile command.
    start = runner.find(' -o "$WORK/freqmed-gen"')
    finish = runner.find("-framework CoreAudio", start)
    link_clause = runner[start:finish] if start >= 0 and finish > start else ""
    check("runnable_excludes_output_backend",
          "output_hard_denied.c" in link_clause and
          "acoustic_macos.c" not in link_clause and
          "R16_NONEMITTING_EXECUTABLE_SYMBOL_AUDIT=PASS" in runner and
          "FREQMED_GEN_R16_BINARY" in runner, 1)

    # This is intentionally *not* a safety verdict on active CoreAudio.
    report = {
        "schema": "FREQMED_GEN_R16_STATIC_OWNERSHIP_EVIDENCE",
        "source": "src/acoustic_macos.c",
        "source_sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
        "method": "BOUNDED_C_TOKEN_AND_BRACE_AUDIT",
        "analysis_scope": "SOURCE_ONLY_NON_EMITTING",
        "checks": checks,
        "passed": sum(c["result"] == "PASS" for c in checks),
        "failed": sum(c["result"] == "FAIL" for c in checks),
        "unresolved": [
            "NO_FORMAL_C_CONCURRENCY_OR_MEMORY_MODEL_PROOF",
            "ACTIVE_COREAUDIO_CALLBACK_LIFETIME_UNTESTED",
            "ACTUAL_FAILED_OS_DISPOSAL_UNTESTED",
            "OS_CALLBACK_QUIESCENCE_NOT_ESTABLISHED_BY_COUNTERS_ALONE",
            "INDEPENDENT_HARDWARE_CUTOFF_NOT_QUALIFIED",
            "ACOUSTIC_AND_EM_METROLOGY_NOT_PERFORMED",
            "EM_INSTRUMENT_NOT_QUALIFIED",
            "BUREAU_CERTIFICATION_PENDING",
        ],
        "scientific_simulation": "NONE",
        "physical_emission": "NONE",
        "real_output": "NOT_AUTHORIZED",
        "production": "NOT_AUTHORIZED",
        "verdict": "STATIC_SOURCE_CONTRACT_PASS" if all(
            c["result"] == "PASS" for c in checks) else "REMEDIATE",
    }
    return report

def main():
    p = argparse.ArgumentParser(description="FREQMED GEN-R16 source-only audit")
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    try:
        report = audit(args.root)
    except (ValueError, IndexError, OSError) as e:
        print("R16_STATIC_OWNERSHIP_AUDIT=FAIL_CLOSED", str(e))
        return 2
    if args.output:
        args.output.write_text(json.dumps(report, sort_keys=True,
                            indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    print("R16_STATIC_OWNERSHIP_AUDIT=" +
          ("PASS" if report["failed"] == 0 else "FAIL_CLOSED"))
    print("R16_STATIC_CHECKS=%d; R16_STATIC_FAILURES=%d" %
          (len(report["checks"]), report["failed"]))
    print("R16_OS_CALLBACK_RACE_FREEDOM=NOT_PROVEN")
    print("R16_PHYSICAL_EMISSION=NONE; R16_SCIENTIFIC_SIMULATION=NONE")
    return 0 if report["failed"] == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
