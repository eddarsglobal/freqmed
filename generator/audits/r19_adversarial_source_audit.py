#!/usr/bin/env python3
"""GEN-R19 adversarial static guard around pinned non-emitting CoreAudio source.

Source-only lexical checks, no physical/numerical simulation and no device access.
Pinning prevents unreviewed changes; semantic checks detect selected bypass
patterns but are NOT formal C verification or proof of callback race freedom.
"""
import argparse
import hashlib
import json
from pathlib import Path

from r16_ownership_static_audit import lex, words, function, occurrence
from r18_control_flow_envelope import examine_source, EnvelopeError
from r17_evidence_verifier import (manifest_integrity, public_denial,
                                  link_sources, LINK_C_ALLOWLIST)

SCHEMA = "FREQMED_GEN_R19_ADVERSARIAL_STATIC_AUDIT"
PINNED_ACOUSTIC_SHA256 = "282708a8c52c1d8f4e0e1c58641f4b96cb64218003675a3e1fcd650043b7af4c"
PINNED_EM_SHA256 = "332e98378acb431588806c94c259eebc5275983f7fda0bbf75cc1f2b501177c5"
LIMITS = (
    "SOURCE_PIN_IS_NOT_AUTHOR_SIGNATURE",
    "LEXICAL_AUDIT_NOT_COMPLETE_C_CONTROL_FLOW",
    "PREPROCESSOR_VARIANTS_NOT_FORMALLY_VERIFIED",
    "C11_CONCURRENT_RACE_FREEDOM_NOT_PROVEN",
    "ACTIVE_COREAUDIO_CALLBACKS_NOT_EXECUTED",
    "ACTUAL_FAILED_OS_DISPOSAL_NOT_EXECUTED",
    "INDEPENDENT_PHYSICAL_CUTOFF_NOT_QUALIFIED",
    "ACOUSTIC_EM_METROLOGY_NOT_PERFORMED",
    "EM_HARDWARE_NOT_QUALIFIED",
    "BUREAU_CERTIFICATION_PENDING",
)
FORBIDDEN_TOKENS = frozenset((
    "#", "asm", "__asm__", "__asm", "__builtin_apply",
    "__builtin_call_with_static_chain", "setjmp", "longjmp",
    "siglongjmp", "fork", "system", "dlopen", "dlsym",
))
EXPECTED_QUIESCENCE = (
    "atomic_load(&ctx->dispose_confirmed) && "
    "!listener_registration_uncertain && "
    "!listener_remove_failed && "
    "atomic_load_explicit(&ctx->active_output_callbacks,memory_order_acquire)==0U && "
    "atomic_load_explicit(&ctx->active_property_listeners,memory_order_acquire)==0U"
)

class AdversarialError(ValueError):
    pass

def require(ok, issue):
    if not ok:
        raise AdversarialError(issue)

def sha(data):
    return hashlib.sha256(data).hexdigest()

def exact(tokens, expression):
    return words(tokens) == words(lex(expression))

def inspect_source(source):
    """Structural review intentionally independent of pinned-byte seal."""
    try:
        r18 = examine_source(source)
        all_tokens = lex(source)
        controller = function(all_tokens, "acoustic_output_impl")
        callback = function(all_tokens, "output_callback")
        listener = function(all_tokens, "queue_running_listener")
    except (EnvelopeError, ValueError, IndexError) as e:
        raise AdversarialError("unclassified source structure: " + str(e)) from e

    checks = []
    def check(name, ok):
        require(ok, name + ": FAIL_CLOSED")
        checks.append(name)

    check("r18_exit_and_release_envelope",
          r18["verdict"] == "STATIC_CONTROL_FLOW_ENVELOPE_PASS"
          and len(r18["exit_sites"]) == 13
          and len(r18["heap_free_sites"]) == 4
          and len(r18["session_release_sites"]) == 6)
    check("no_preprocessor_in_callback_or_controller",
          all("#" not in words(t) for t in (controller, callback, listener)))
    check("no_unclassified_escaping_or_dynamic_loader_tokens",
          not any(token in FORBIDDEN_TOKENS or token.startswith("__builtin_")
                  for t in (controller, callback, listener)
                  for token in words(t)))

    start = occurrence(controller, "const int context_quiescent=")
    check("single_final_quiescence_initializer", len(start) == 1)
    i = start[0] + len(lex("const int context_quiescent="))
    j = next((k for k in range(i, len(controller))
              if controller[k][0] == ";"), None)
    check("quiescence_expression_complete_and_exact",
          j is not None and exact(controller[i:j], EXPECTED_QUIESCENCE))

    check("callbacks_counted_using_acquire_release",
          len(occurrence(callback,
              "atomic_fetch_add_explicit(&ctx->active_output_callbacks,1U,memory_order_acq_rel)")) == 1
          and len(occurrence(callback,
              "atomic_fetch_sub_explicit(&ctx->active_output_callbacks,1U,memory_order_acq_rel)")) == 1
          and len(occurrence(listener,
              "atomic_fetch_add_explicit(&ctx->active_property_listeners,1U,memory_order_acq_rel)")) == 1
          and len(occurrence(listener,
              "atomic_fetch_sub_explicit(&ctx->active_property_listeners,1U,memory_order_acq_rel)")) == 1)
    check("callback_does_not_control_queue_or_emission",
          not any(tok.startswith("AudioQueue") or tok in ("IOServiceOpen", "AudioDeviceStart")
                  for tok in words(callback))
          and not any(tok.startswith("AudioQueueStop") or tok == "IOServiceOpen"
                      for tok in words(listener)))
    check("pcm_writer_gate_is_acquire_release",
          len(occurrence(callback,
              "atomic_flag_test_and_set_explicit(&ctx->pcm_writer_gate,memory_order_acquire)")) == 1
          and len(occurrence(callback,
              "atomic_flag_clear_explicit(&ctx->pcm_writer_gate,memory_order_release)")) == 1)
    check("process_quarantine_declaration_remains_initially_zero",
          len(occurrence(all_tokens,
              "static atomic_int fm_context_quarantined=ATOMIC_VAR_INIT(0)")) == 1)
    check("quarantine_variable_not_accessed_outside_audited_controller",
          len(occurrence(all_tokens, "fm_context_quarantined")) == 7)
    check("no_reopening_atomic_state",
          not occurrence(all_tokens,
              "atomic_store_explicit(&fm_context_quarantined,0")
          and not occurrence(all_tokens,
              "atomic_store(&fm_context_quarantined,0"))
    check("new_and_dispose_not_called_from_output_callback",
          not any(t.startswith("AudioQueue") for t in words(callback)))
    check("guarded_source_has_no_new_return_or_heap_release",
          r18["exit_phases"] == {
              "BEFORE_SESSION_CLAIM": 5, "CLAIMED_NO_ALLOCATION": 2,
              "ALLOCATED_BEFORE_OS_PUBLICATION": 3,
              "OS_CALLBACK_USERDATA_POSSIBLY_PUBLISHED": 2,
              "AFTER_FINAL_CLEANUP": 1,
          })
    return {"static_checks": checks, "exit_count": 13,
            "free_count": 4, "claim_release_count": 6}

def audit(root):
    root = Path(root).resolve()
    source = (root / "src/acoustic_macos.c").read_bytes()
    em = (root / "src/em_backend.c").read_bytes()
    manifest, manifest_sha = manifest_integrity(root)
    require(sha(source) == PINNED_ACOUSTIC_SHA256, "acoustic source pin changed")
    require(sha(em) == PINNED_EM_SHA256, "EM source pin changed")
    source_text = source.decode("utf-8")
    reviewed = inspect_source(source_text)
    require(public_denial(source_text, "fm_acoustic_physical_output"),
            "physical acoustic public entry not hard denied")
    require(public_denial(em.decode("utf-8"), "fm_em_physical_output"),
            "physical EM public entry not hard denied")
    runner = (root / "RUN_GEN_R19_MAC_INTEL.command").read_text(encoding="utf-8")
    sources = link_sources(runner)
    require(len(sources) == len(LINK_C_ALLOWLIST)
            and set(sources) == LINK_C_ALLOWLIST,
            "R19 runnable source allowlist changed")
    require("R19_NONEMITTING_EXECUTABLE_SYMBOL_AUDIT=PASS" in runner
            and "FREQMED_GEN_R19_BINARY" in runner,
            "R19 executable symbol contract absent")
    for required in ("audits/r16_ownership_static_audit.py",
                     "audits/r17_evidence_verifier.py",
                     "audits/r18_control_flow_envelope.py",
                     "audits/r19_adversarial_source_audit.py",
                     "audits/r19_evidence_archive.py",
                     "tests/test_r19_adversarial_evidence.py",
                     "RUN_GEN_R19_MAC_INTEL.command"):
        require(required in manifest, "missing pinned R19 component: " + required)
    return {
        "schema": SCHEMA, "verdict": "SOURCE_ONLY_ADVERSARIAL_PASS",
        "method": "PINNED_C_TOKENS_AND_SELECTED_BYPASS_GUARDS",
        "source_sha256": sha(source), "em_source_sha256": sha(em),
        "manifest_sha256": manifest_sha,
        "files_verified": len(manifest),
        "checks": reviewed["static_checks"],
        "checks_passed": len(reviewed["static_checks"]),
        "exit_count": reviewed["exit_count"],
        "free_count": reviewed["free_count"],
        "claim_release_count": reviewed["claim_release_count"],
        "limitations": list(LIMITS),
        "physical_emission": "NONE", "scientific_simulation": "NONE",
        "real_output": "NOT_AUTHORIZED", "production": "NOT_AUTHORIZED",
        "bureau_certification": "PENDING",
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--root", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    a = p.parse_args()
    try:
        report = audit(a.root)
        a.output.write_text(json.dumps(report, indent=2,
                         sort_keys=True, ensure_ascii=False)+"\n",
                         encoding="utf-8")
    except (AdversarialError, OSError, ValueError, TypeError, KeyError) as ex:
        print("R19_ADVERSARIAL_STATIC_AUDIT=FAIL_CLOSED", str(ex))
        return 2
    print("R19_ADVERSARIAL_STATIC_AUDIT=PASS")
    print("R19_ADVERSARIAL_CHECKS=%d" % report["checks_passed"])
    print("R19_SOURCE_FILES_VERIFIED=%d" % report["files_verified"])
    print("R19_COREAUDIO_RACE_FREEDOM=NOT_PROVEN")
    print("R19_PHYSICAL_EMISSION=NONE; R19_SCIENTIFIC_SIMULATION=NONE")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
