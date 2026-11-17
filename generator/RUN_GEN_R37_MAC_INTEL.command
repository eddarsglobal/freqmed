#!/bin/bash
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "$0")" && pwd -P)"
MODE="${1:-selftest}"
case "$MODE" in selftest|status|probe|em-discover) ;; *) echo 'R27_UNKNOWN_ACTION_BLOCK' >&2;exit 2;; esac
[ "$(uname -s)" = Darwin ] || { echo 'MACOS_REQUIRED' >&2;exit 3; }
[ "$(uname -m)" = x86_64 ] || { echo 'MAC_INTEL_REQUIRED' >&2;exit 3; }
(cd "$ROOT" && shasum -a 256 -c KIT_SHA256SUMS.txt)
command -v clang >/dev/null || { echo 'MISSING_CLANG' >&2;exit 4; }
command -v nm >/dev/null || { echo 'MISSING_NM' >&2;exit 4; }
command -v python3 >/dev/null || { echo 'MISSING_PYTHON3' >&2;exit 4; }
WORK="$(mktemp -d "$HOME/Downloads/FREQMED_GEN_R37_NATIVE_XXXXXX")"
# GEN-R27 source-only lexical control-block audit; not simulation or CoreAudio playback.
# Evidence is written under isolated WORK, never into pinned GitHub sources.
python3 -B "$ROOT/audits/r16_ownership_static_audit.py" \
  --root "$ROOT" --output "$WORK/GEN_R16_OWNERSHIP_EVIDENCE.json"
test -s "$WORK/GEN_R16_OWNERSHIP_EVIDENCE.json"
grep -q '"verdict": "STATIC_SOURCE_CONTRACT_PASS"' "$WORK/GEN_R16_OWNERSHIP_EVIDENCE.json" || {
  echo 'R27_STATIC_VERDICT=FAIL_CLOSED' >&2
  exit 8
}
echo "R16_STATIC_EVIDENCE_JSON=$WORK/GEN_R16_OWNERSHIP_EVIDENCE.json"
# R27: independently validate actual R16 evidence and all pinned source hashes.
# This is SOURCE ONLY and cannot enable output, access a device or simulate physics.
python3 -B "$ROOT/audits/r17_evidence_verifier.py" \
  --root "$ROOT" \
  --evidence "$WORK/GEN_R16_OWNERSHIP_EVIDENCE.json" \
  --output "$WORK/GEN_R17_VERIFIED_EVIDENCE.json"
test -s "$WORK/GEN_R17_VERIFIED_EVIDENCE.json"
grep -q '"verification": "PASS"' "$WORK/GEN_R17_VERIFIED_EVIDENCE.json" || {
  echo 'R27_INDEPENDENT_EVIDENCE=FAIL_CLOSED' >&2
  exit 8
}
echo "R17_VERIFIED_EVIDENCE_JSON=$WORK/GEN_R17_VERIFIED_EVIDENCE.json"
# R27: classify actual C exit sites, heap frees, claim releases and API ordering.
# Prior R16/R17 evidences are used ONLY as source-integrity inputs.
python3 -B "$ROOT/audits/r18_control_flow_envelope.py" \
  --root "$ROOT" \
  --r16-evidence "$WORK/GEN_R16_OWNERSHIP_EVIDENCE.json" \
  --r17-evidence "$WORK/GEN_R17_VERIFIED_EVIDENCE.json" \
  --output "$WORK/GEN_R18_CONTROL_FLOW_EVIDENCE.json"
test -s "$WORK/GEN_R18_CONTROL_FLOW_EVIDENCE.json"
grep -q '"verdict": "STATIC_CONTROL_FLOW_ENVELOPE_PASS"' "$WORK/GEN_R18_CONTROL_FLOW_EVIDENCE.json" || {
  echo 'R18_CONTROL_FLOW_VERDICT=FAIL_CLOSED' >&2
  exit 8
}
grep -q '"r16_r17_evidence_binding": "PASS"' "$WORK/GEN_R18_CONTROL_FLOW_EVIDENCE.json" || {
  echo 'R18_EVIDENCE_CHAIN=FAIL_CLOSED' >&2
  exit 8
}
echo "R18_CONTROL_FLOW_JSON=$WORK/GEN_R18_CONTROL_FLOW_EVIDENCE.json"
# GEN-R27: real-source adversarial static audit; no hardware/simulation.
python3 -B "$ROOT/audits/r19_adversarial_source_audit.py" \
  --root "$ROOT" --output "$WORK/GEN_R19_ADVERSARIAL_EVIDENCE.json"
test -s "$WORK/GEN_R19_ADVERSARIAL_EVIDENCE.json"
grep -q '"verdict": "SOURCE_ONLY_ADVERSARIAL_PASS"' \
  "$WORK/GEN_R19_ADVERSARIAL_EVIDENCE.json" || {
  echo 'R19_ADVERSARIAL_VERDICT=FAIL_CLOSED' >&2
  exit 8
}
echo "R19_ADVERSARIAL_JSON=$WORK/GEN_R19_ADVERSARIAL_EVIDENCE.json"
# GEN-R27: mandatory READ-ONLY review of owner-preserved original R19 evidence.
# No hardware, output, simulation or alteration of the R19 archive.
: "$FREQMED_GEN_R19_ARCHIVE_DIR"
python3 -B "$ROOT/audits/r20_bureau_archive_review.py" \
  --root "$ROOT" \
  --archive-r19 "$FREQMED_GEN_R19_ARCHIVE_DIR" \
  --report "$WORK/GEN_R20_BUREAU_VERIFICATION.json" \
  --review-md "$WORK/GEN_R20_BUREAU_READINESS.md"
test -s "$WORK/GEN_R20_BUREAU_VERIFICATION.json"
test -s "$WORK/GEN_R20_BUREAU_READINESS.md"
grep -q '"decision": "REVIEWABLE_NOT_CERTIFIED"' \
  "$WORK/GEN_R20_BUREAU_VERIFICATION.json" || {
    echo 'R27_BUREAU_DECISION_MISSING=FAIL_CLOSED' >&2
    exit 8
  }
echo "R20_BUREAU_JSON=$WORK/GEN_R20_BUREAU_VERIFICATION.json"
# GEN-R27: cross-check all five genuine source reports and map the
# 11 OPEN Bureau gates to current SHA-pinned C/doc lines, never certify.
python3 -B "$ROOT/audits/r21_bureau_evidence_gaps.py" \
  --root "$ROOT" --archive-r19 "$FREQMED_GEN_R19_ARCHIVE_DIR" \
  --r16 "$WORK/GEN_R16_OWNERSHIP_EVIDENCE.json" \
  --r17 "$WORK/GEN_R17_VERIFIED_EVIDENCE.json" \
  --r18 "$WORK/GEN_R18_CONTROL_FLOW_EVIDENCE.json" \
  --r19 "$WORK/GEN_R19_ADVERSARIAL_EVIDENCE.json" \
  --r20 "$WORK/GEN_R20_BUREAU_VERIFICATION.json" \
  --json "$WORK/GEN_R21_BUREAU_GAPS.json" \
  --markdown "$WORK/GEN_R21_BUREAU_GAPS.md"
test -s "$WORK/GEN_R21_BUREAU_GAPS.json"
test -s "$WORK/GEN_R21_BUREAU_GAPS.md"
grep -q '"verdict": "EVIDENCE_GAPS_MAPPED_NOT_CERTIFIED"' \
  "$WORK/GEN_R21_BUREAU_GAPS.json" || {
  echo 'R21_BUREAU_GAP_EVIDENCE=FAIL_CLOSED' >&2
  exit 8
}
echo "R21_GAP_JSON=$WORK/GEN_R21_BUREAU_GAPS.json"
# GEN-R27: independently re-review actual C11/CoreAudio callback ownership
# and failed OS disposal on SOURCE ONLY. Three gates MUST remain unresolved.
python3 -B "$ROOT/audits/r22_coreaudio_lifetime_review.py" \
  --root "$ROOT" --archive-r19 "$FREQMED_GEN_R19_ARCHIVE_DIR" \
  --r16 "$WORK/GEN_R16_OWNERSHIP_EVIDENCE.json" \
  --r17 "$WORK/GEN_R17_VERIFIED_EVIDENCE.json" \
  --r18 "$WORK/GEN_R18_CONTROL_FLOW_EVIDENCE.json" \
  --r19 "$WORK/GEN_R19_ADVERSARIAL_EVIDENCE.json" \
  --r20 "$WORK/GEN_R20_BUREAU_VERIFICATION.json" \
  --r21 "$WORK/GEN_R21_BUREAU_GAPS.json" \
  --output "$WORK/GEN_R22_COREAUDIO_REVIEW.json" \
  --markdown "$WORK/GEN_R22_COREAUDIO_REVIEW.md"
test -s "$WORK/GEN_R22_COREAUDIO_REVIEW.json"
test -s "$WORK/GEN_R22_COREAUDIO_REVIEW.md"
grep -q '"verdict": "REVIEW_REQUIRED_NO_EMISSION"' \
  "$WORK/GEN_R22_COREAUDIO_REVIEW.json" || {
  echo 'R22_C11_COREAUDIO_REVIEW_VERDICT=FAIL_CLOSED' >&2
  exit 8
}
echo "R22_COREAUDIO_REVIEW_JSON=$WORK/GEN_R22_COREAUDIO_REVIEW.json"
# GEN-R27: source-anchored C11 HB and OS-quiescence proof obligations;
# the 15 obligations stay OPEN; no callback execution or physical output.
python3 -B "$ROOT/audits/r23_happens_before_obligations.py" \
  --root "$ROOT" --archive-r19 "$FREQMED_GEN_R19_ARCHIVE_DIR" \
  --r16 "$WORK/GEN_R16_OWNERSHIP_EVIDENCE.json" \
  --r17 "$WORK/GEN_R17_VERIFIED_EVIDENCE.json" \
  --r18 "$WORK/GEN_R18_CONTROL_FLOW_EVIDENCE.json" \
  --r19 "$WORK/GEN_R19_ADVERSARIAL_EVIDENCE.json" \
  --r20 "$WORK/GEN_R20_BUREAU_VERIFICATION.json" \
  --r21 "$WORK/GEN_R21_BUREAU_GAPS.json" \
  --r22 "$WORK/GEN_R22_COREAUDIO_REVIEW.json" \
  --json "$WORK/GEN_R23_PROOF_OBLIGATIONS.json" \
  --markdown "$WORK/GEN_R23_PROOF_OBLIGATIONS.md"
test -s "$WORK/GEN_R23_PROOF_OBLIGATIONS.json"
test -s "$WORK/GEN_R23_PROOF_OBLIGATIONS.md"
grep -q '"verdict": "PROOF_OBLIGATIONS_OPEN_NO_EMISSION"' \
  "$WORK/GEN_R23_PROOF_OBLIGATIONS.json" || {
  echo 'R23_PROOF_OBLIGATION_VERDICT=FAIL_CLOSED' >&2
  exit 8
}
echo "R23_PROOF_OBLIGATION_JSON=$WORK/GEN_R23_PROOF_OBLIGATIONS.json"
# GEN-R27: rebind 19 shared C11 fields and 11 AudioQueue calls
# to real SHA-pinned source lines and documented OS API contracts.
# This is a source-only review. All seven findings stay OPEN.
python3 -B "$ROOT/audits/r24_shared_state_contract_audit.py" \
  --root "$ROOT" --archive-r19 "$FREQMED_GEN_R19_ARCHIVE_DIR" \
  --r16 "$WORK/GEN_R16_OWNERSHIP_EVIDENCE.json" \
  --r17 "$WORK/GEN_R17_VERIFIED_EVIDENCE.json" \
  --r18 "$WORK/GEN_R18_CONTROL_FLOW_EVIDENCE.json" \
  --r19 "$WORK/GEN_R19_ADVERSARIAL_EVIDENCE.json" \
  --r20 "$WORK/GEN_R20_BUREAU_VERIFICATION.json" \
  --r21 "$WORK/GEN_R21_BUREAU_GAPS.json" \
  --r22 "$WORK/GEN_R22_COREAUDIO_REVIEW.json" \
  --r23 "$WORK/GEN_R23_PROOF_OBLIGATIONS.json" \
  --json "$WORK/GEN_R24_SHARED_STATE_CONTRACT.json" \
  --markdown "$WORK/GEN_R24_SHARED_STATE_CONTRACT.md"
test -s "$WORK/GEN_R24_SHARED_STATE_CONTRACT.json"
test -s "$WORK/GEN_R24_SHARED_STATE_CONTRACT.md"
grep -q '"verdict": "SHARED_STATE_MAPPED_CONTRACT_GAPS_OPEN"' \
  "$WORK/GEN_R24_SHARED_STATE_CONTRACT.json" || {
  echo 'R24_SHARED_STATE_REVIEW_VERDICT=FAIL_CLOSED' >&2
  exit 8
}
echo "R24_SHARED_STATE_CONTRACT_JSON=$WORK/GEN_R24_SHARED_STATE_CONTRACT.json"
# GEN-R27: read-only independent remediation review. Review 9 proposed
# C11/OS ownership changes but apply none. All proof obligations stay OPEN.
python3 -B "$ROOT/audits/r25_sync_ownership_remediation.py" \
  --root "$ROOT" --archive-r19 "$FREQMED_GEN_R19_ARCHIVE_DIR" \
  --r16 "$WORK/GEN_R16_OWNERSHIP_EVIDENCE.json" \
  --r17 "$WORK/GEN_R17_VERIFIED_EVIDENCE.json" \
  --r18 "$WORK/GEN_R18_CONTROL_FLOW_EVIDENCE.json" \
  --r19 "$WORK/GEN_R19_ADVERSARIAL_EVIDENCE.json" \
  --r20 "$WORK/GEN_R20_BUREAU_VERIFICATION.json" \
  --r21 "$WORK/GEN_R21_BUREAU_GAPS.json" \
  --r22 "$WORK/GEN_R22_COREAUDIO_REVIEW.json" \
  --r23 "$WORK/GEN_R23_PROOF_OBLIGATIONS.json" \
  --r24 "$WORK/GEN_R24_SHARED_STATE_CONTRACT.json" \
  --json "$WORK/GEN_R25_REMEDIATION_REVIEW.json" \
  --markdown "$WORK/GEN_R25_REMEDIATION_REVIEW.md"
test -s "$WORK/GEN_R25_REMEDIATION_REVIEW.json"
test -s "$WORK/GEN_R25_REMEDIATION_REVIEW.md"
grep -q '"verdict": "REMEDIATION_PLANS_REVIEWABLE_NOT_APPLIED"' \
  "$WORK/GEN_R25_REMEDIATION_REVIEW.json" || {
  echo 'R25_REMEDIATION_VERDICT=FAIL_CLOSED' >&2
  exit 8
}
echo "R25_REMEDIATION_REVIEW_JSON=$WORK/GEN_R25_REMEDIATION_REVIEW.json"
# GEN-R27: independently recompute R16-R25 source evidence; a strictly
# three-edit C candidate is reviewed separately from the pinned native C.
# The candidate MUST NEVER be linked, loaded, executed or enabled for output.
python3 -B "$ROOT/audits/r26_isolated_patch_gate.py" \
  --root "$ROOT" --archive-r19 "$FREQMED_GEN_R19_ARCHIVE_DIR" \
  --r16 "$WORK/GEN_R16_OWNERSHIP_EVIDENCE.json" \
  --r17 "$WORK/GEN_R17_VERIFIED_EVIDENCE.json" \
  --r18 "$WORK/GEN_R18_CONTROL_FLOW_EVIDENCE.json" \
  --r19 "$WORK/GEN_R19_ADVERSARIAL_EVIDENCE.json" \
  --r20 "$WORK/GEN_R20_BUREAU_VERIFICATION.json" \
  --r21 "$WORK/GEN_R21_BUREAU_GAPS.json" \
  --r22 "$WORK/GEN_R22_COREAUDIO_REVIEW.json" \
  --r23 "$WORK/GEN_R23_PROOF_OBLIGATIONS.json" \
  --r24 "$WORK/GEN_R24_SHARED_STATE_CONTRACT.json" \
  --r25 "$WORK/GEN_R25_REMEDIATION_REVIEW.json" \
  --json "$WORK/GEN_R26_PATCH_SAFETY_GATE.json" \
  --markdown "$WORK/GEN_R26_PATCH_SAFETY_GATE.md"
test -s "$WORK/GEN_R26_PATCH_SAFETY_GATE.json"
test -s "$WORK/GEN_R26_PATCH_SAFETY_GATE.md"
grep -q '"verdict": "ISOLATED_PATCH_REVIEW_REQUIRED_NO_EMISSION"' \
  "$WORK/GEN_R26_PATCH_SAFETY_GATE.json" || {
  echo 'R26_CANDIDATE_REVIEW_VERDICT=FAIL_CLOSED' >&2
  exit 8
}
echo "R26_CANDIDATE_REVIEW_JSON=$WORK/GEN_R26_PATCH_SAFETY_GATE.json"
# GEN-R27: independent source-only adversarial review of pinned R26 native
# candidate; the R19 backend stays unchanged, and no candidate is executed.
python3 -B "$ROOT/audits/r27_adversarial_ownership_review.py" \
  --root "$ROOT" --archive-r19 "$FREQMED_GEN_R19_ARCHIVE_DIR" \
  --r16 "$WORK/GEN_R16_OWNERSHIP_EVIDENCE.json" \
  --r17 "$WORK/GEN_R17_VERIFIED_EVIDENCE.json" \
  --r18 "$WORK/GEN_R18_CONTROL_FLOW_EVIDENCE.json" \
  --r19 "$WORK/GEN_R19_ADVERSARIAL_EVIDENCE.json" \
  --r20 "$WORK/GEN_R20_BUREAU_VERIFICATION.json" \
  --r21 "$WORK/GEN_R21_BUREAU_GAPS.json" \
  --r22 "$WORK/GEN_R22_COREAUDIO_REVIEW.json" \
  --r23 "$WORK/GEN_R23_PROOF_OBLIGATIONS.json" \
  --r24 "$WORK/GEN_R24_SHARED_STATE_CONTRACT.json" \
  --r25 "$WORK/GEN_R25_REMEDIATION_REVIEW.json" \
  --r26 "$WORK/GEN_R26_PATCH_SAFETY_GATE.json" \
  --json "$WORK/GEN_R27_ADVERSARIAL_REVIEW.json" \
  --markdown "$WORK/GEN_R27_ADVERSARIAL_REVIEW.md"
test -s "$WORK/GEN_R27_ADVERSARIAL_REVIEW.json"
test -s "$WORK/GEN_R27_ADVERSARIAL_REVIEW.md"
grep -q '"verdict": "ADVERSARIAL_GAPS_CONFIRMED_NO_RUNTIME_SAFETY_PROOF"' \
  "$WORK/GEN_R27_ADVERSARIAL_REVIEW.json" || {
  echo 'R27_ADVERSARIAL_VERDICT=FAIL_CLOSED' >&2
  exit 8
}
echo "R27_ADVERSARIAL_REVIEW_JSON=$WORK/GEN_R27_ADVERSARIAL_REVIEW.json"
# GEN-R28: independent design review of a separate, unlinked C11 gate.
python3 -B "$ROOT/audits/r28_queue_admission_design.py" \
  --root "$ROOT" --archive-r19 "$FREQMED_GEN_R19_ARCHIVE_DIR" \
  --r16 "$WORK/GEN_R16_OWNERSHIP_EVIDENCE.json" \
  --r17 "$WORK/GEN_R17_VERIFIED_EVIDENCE.json" \
  --r18 "$WORK/GEN_R18_CONTROL_FLOW_EVIDENCE.json" \
  --r19 "$WORK/GEN_R19_ADVERSARIAL_EVIDENCE.json" \
  --r20 "$WORK/GEN_R20_BUREAU_VERIFICATION.json" \
  --r21 "$WORK/GEN_R21_BUREAU_GAPS.json" \
  --r22 "$WORK/GEN_R22_COREAUDIO_REVIEW.json" \
  --r23 "$WORK/GEN_R23_PROOF_OBLIGATIONS.json" \
  --r24 "$WORK/GEN_R24_SHARED_STATE_CONTRACT.json" \
  --r25 "$WORK/GEN_R25_REMEDIATION_REVIEW.json" \
  --r26 "$WORK/GEN_R26_PATCH_SAFETY_GATE.json" \
  --r27 "$WORK/GEN_R27_ADVERSARIAL_REVIEW.json" \
  --json "$WORK/GEN_R28_QUEUE_ADMISSION_DESIGN.json" \
  --markdown "$WORK/GEN_R28_QUEUE_ADMISSION_DESIGN.md"
test -s "$WORK/GEN_R28_QUEUE_ADMISSION_DESIGN.json"
test -s "$WORK/GEN_R28_QUEUE_ADMISSION_DESIGN.md"
grep -q '"verdict": "BOUNDED_C11_ADMISSION_DESIGN_UNCERTIFIED"' \
  "$WORK/GEN_R28_QUEUE_ADMISSION_DESIGN.json" || {
  echo 'R28_DESIGN_VERDICT=FAIL_CLOSED' >&2; exit 8
}
echo "R28_QUEUE_ADMISSION_DESIGN_JSON=$WORK/GEN_R28_QUEUE_ADMISSION_DESIGN.json"
# GEN-R29: review real candidate C admission at source-only boundaries.
python3 -B "$ROOT/audits/r29_admission_integration_review.py" \
  --root "$ROOT" --archive-r19 "$FREQMED_GEN_R19_ARCHIVE_DIR" \
  --r16 "$WORK/GEN_R16_OWNERSHIP_EVIDENCE.json" \
  --r17 "$WORK/GEN_R17_VERIFIED_EVIDENCE.json" \
  --r18 "$WORK/GEN_R18_CONTROL_FLOW_EVIDENCE.json" \
  --r19 "$WORK/GEN_R19_ADVERSARIAL_EVIDENCE.json" \
  --r20 "$WORK/GEN_R20_BUREAU_VERIFICATION.json" \
  --r21 "$WORK/GEN_R21_BUREAU_GAPS.json" \
  --r22 "$WORK/GEN_R22_COREAUDIO_REVIEW.json" \
  --r23 "$WORK/GEN_R23_PROOF_OBLIGATIONS.json" \
  --r24 "$WORK/GEN_R24_SHARED_STATE_CONTRACT.json" \
  --r25 "$WORK/GEN_R25_REMEDIATION_REVIEW.json" \
  --r26 "$WORK/GEN_R26_PATCH_SAFETY_GATE.json" \
  --r27 "$WORK/GEN_R27_ADVERSARIAL_REVIEW.json" \
  --r28 "$WORK/GEN_R28_QUEUE_ADMISSION_DESIGN.json" \
  --json "$WORK/GEN_R29_ADMISSION_INTEGRATION_REVIEW.json" \
  --markdown "$WORK/GEN_R29_ADMISSION_INTEGRATION_REVIEW.md"
test -s "$WORK/GEN_R29_ADMISSION_INTEGRATION_REVIEW.json"
test -s "$WORK/GEN_R29_ADMISSION_INTEGRATION_REVIEW.md"
grep -q '"verdict": "ISOLATED_INTEGRATION_REVIEWED_C11_OS_PROOF_OPEN"' \
  "$WORK/GEN_R29_ADMISSION_INTEGRATION_REVIEW.json" || {
  echo 'R29_SOURCE_INTEGRATION_VERDICT=FAIL_CLOSED' >&2;exit 8
}
echo "R29_ADMISSION_INTEGRATION_REVIEW_JSON=$WORK/GEN_R29_ADMISSION_INTEGRATION_REVIEW.json"
# GEN-R30 independent CoreAudio source-only adversarial OS/C11 review.
# Observe exact C lines; NEVER run a queue, callback, simulation or emission.
python3 -B "$ROOT/audits/r30_coreaudio_quiescence_adversarial.py" \
  --root "$ROOT" --archive-r19 "$FREQMED_GEN_R19_ARCHIVE_DIR" \
  --r16 "$WORK/GEN_R16_OWNERSHIP_EVIDENCE.json" \
  --r17 "$WORK/GEN_R17_VERIFIED_EVIDENCE.json" \
  --r18 "$WORK/GEN_R18_CONTROL_FLOW_EVIDENCE.json" \
  --r19 "$WORK/GEN_R19_ADVERSARIAL_EVIDENCE.json" \
  --r20 "$WORK/GEN_R20_BUREAU_VERIFICATION.json" \
  --r21 "$WORK/GEN_R21_BUREAU_GAPS.json" \
  --r22 "$WORK/GEN_R22_COREAUDIO_REVIEW.json" \
  --r23 "$WORK/GEN_R23_PROOF_OBLIGATIONS.json" \
  --r24 "$WORK/GEN_R24_SHARED_STATE_CONTRACT.json" \
  --r25 "$WORK/GEN_R25_REMEDIATION_REVIEW.json" \
  --r26 "$WORK/GEN_R26_PATCH_SAFETY_GATE.json" \
  --r27 "$WORK/GEN_R27_ADVERSARIAL_REVIEW.json" \
  --r28 "$WORK/GEN_R28_QUEUE_ADMISSION_DESIGN.json" \
  --r29 "$WORK/GEN_R29_ADMISSION_INTEGRATION_REVIEW.json" \
  --json "$WORK/GEN_R30_COREAUDIO_QUIESCENCE.json" \
  --markdown "$WORK/GEN_R30_COREAUDIO_QUIESCENCE.md"
test -s "$WORK/GEN_R30_COREAUDIO_QUIESCENCE.json"
test -s "$WORK/GEN_R30_COREAUDIO_QUIESCENCE.md"
grep -q '"verdict": "ADVERSARIAL_COREAUDIO_LIFETIME_GAPS_CONFIRMED_UNCERTIFIED"' \
  "$WORK/GEN_R30_COREAUDIO_QUIESCENCE.json" || {
  echo 'R30_COREAUDIO_REVIEW_VERDICT=FAIL_CLOSED' >&2;exit 8
}
grep -q '"r30_findings_open": 12' "$WORK/GEN_R30_COREAUDIO_QUIESCENCE.json" || exit 8
grep -q '"r30_critical_open": 2' "$WORK/GEN_R30_COREAUDIO_QUIESCENCE.json" || exit 8
echo "R30_COREAUDIO_QUIESCENCE_JSON=$WORK/GEN_R30_COREAUDIO_QUIESCENCE.json"
# GEN-R31: exact-scoped C31 shutdown reorder proof-gap audit, SOURCE ONLY.
python3 -B "$ROOT/audits/r31_critical_shutdown_review.py" \
  --root "$ROOT" --archive-r19 "$FREQMED_GEN_R19_ARCHIVE_DIR" \
  --r16 "$WORK/GEN_R16_OWNERSHIP_EVIDENCE.json" \
  --r17 "$WORK/GEN_R17_VERIFIED_EVIDENCE.json" \
  --r18 "$WORK/GEN_R18_CONTROL_FLOW_EVIDENCE.json" \
  --r19 "$WORK/GEN_R19_ADVERSARIAL_EVIDENCE.json" \
  --r20 "$WORK/GEN_R20_BUREAU_VERIFICATION.json" \
  --r21 "$WORK/GEN_R21_BUREAU_GAPS.json" \
  --r22 "$WORK/GEN_R22_COREAUDIO_REVIEW.json" \
  --r23 "$WORK/GEN_R23_PROOF_OBLIGATIONS.json" \
  --r24 "$WORK/GEN_R24_SHARED_STATE_CONTRACT.json" \
  --r25 "$WORK/GEN_R25_REMEDIATION_REVIEW.json" \
  --r26 "$WORK/GEN_R26_PATCH_SAFETY_GATE.json" \
  --r27 "$WORK/GEN_R27_ADVERSARIAL_REVIEW.json" \
  --r28 "$WORK/GEN_R28_QUEUE_ADMISSION_DESIGN.json" \
  --r29 "$WORK/GEN_R29_ADMISSION_INTEGRATION_REVIEW.json" \
  --r30 "$WORK/GEN_R30_COREAUDIO_QUIESCENCE.json" \
  --json "$WORK/GEN_R31_CRITICAL_SHUTDOWN.json" \
  --markdown "$WORK/GEN_R31_CRITICAL_SHUTDOWN.md"
test -s "$WORK/GEN_R31_CRITICAL_SHUTDOWN.json"
test -s "$WORK/GEN_R31_CRITICAL_SHUTDOWN.md"
grep -q '"verdict": "SHUTDOWN_STOP_ATTEMPT_REORDERED_SOURCE_ONLY_OS_SAFETY_UNPROVEN"' \
  "$WORK/GEN_R31_CRITICAL_SHUTDOWN.json" || {
  echo 'R31_SHUTDOWN_VERDICT=FAIL_CLOSED' >&2; exit 8
}
grep -q '"r31_findings_open": 8' "$WORK/GEN_R31_CRITICAL_SHUTDOWN.json" || exit 8
grep -q '"r31_critical_open": 2' "$WORK/GEN_R31_CRITICAL_SHUTDOWN.json" || exit 8
echo "R31_CRITICAL_SHUTDOWN_JSON=$WORK/GEN_R31_CRITICAL_SHUTDOWN.json"
# GEN-R32 independent failed-stop containment audit, source only.
python3 -B "$ROOT/audits/r32_failed_stop_ownership_review.py" \
  --root "$ROOT" --archive-r19 "$FREQMED_GEN_R19_ARCHIVE_DIR" \
  --r16 "$WORK/GEN_R16_OWNERSHIP_EVIDENCE.json" \
  --r17 "$WORK/GEN_R17_VERIFIED_EVIDENCE.json" \
  --r18 "$WORK/GEN_R18_CONTROL_FLOW_EVIDENCE.json" \
  --r19 "$WORK/GEN_R19_ADVERSARIAL_EVIDENCE.json" \
  --r20 "$WORK/GEN_R20_BUREAU_VERIFICATION.json" \
  --r21 "$WORK/GEN_R21_BUREAU_GAPS.json" \
  --r22 "$WORK/GEN_R22_COREAUDIO_REVIEW.json" \
  --r23 "$WORK/GEN_R23_PROOF_OBLIGATIONS.json" \
  --r24 "$WORK/GEN_R24_SHARED_STATE_CONTRACT.json" \
  --r25 "$WORK/GEN_R25_REMEDIATION_REVIEW.json" \
  --r26 "$WORK/GEN_R26_PATCH_SAFETY_GATE.json" \
  --r27 "$WORK/GEN_R27_ADVERSARIAL_REVIEW.json" \
  --r28 "$WORK/GEN_R28_QUEUE_ADMISSION_DESIGN.json" \
  --r29 "$WORK/GEN_R29_ADMISSION_INTEGRATION_REVIEW.json" \
  --r30 "$WORK/GEN_R30_COREAUDIO_QUIESCENCE.json" \
  --r31 "$WORK/GEN_R31_CRITICAL_SHUTDOWN.json" \
  --json "$WORK/GEN_R32_FAILED_STOP_OWNERSHIP.json" \
  --markdown "$WORK/GEN_R32_FAILED_STOP_OWNERSHIP.md"
test -s "$WORK/GEN_R32_FAILED_STOP_OWNERSHIP.json"
test -s "$WORK/GEN_R32_FAILED_STOP_OWNERSHIP.md"
grep -q '"verdict": "FAILED_STOP_CONTAINMENT_REVIEWED_PHYSICAL_SAFETY_UNPROVEN"' \
  "$WORK/GEN_R32_FAILED_STOP_OWNERSHIP.json" || {
  echo 'R32_FAILED_STOP_VERDICT=FAIL_CLOSED' >&2; exit 8
}
grep -q '"r32_findings_open": 10' "$WORK/GEN_R32_FAILED_STOP_OWNERSHIP.json" || exit 8
grep -q '"r32_critical_open": 2' "$WORK/GEN_R32_FAILED_STOP_OWNERSHIP.json" || exit 8
echo 'R32_FAILED_STOP_OWNERSHIP_REVIEW=PASS'
echo "R32_FAILED_STOP_JSON=$WORK/GEN_R32_FAILED_STOP_OWNERSHIP.json"
# GEN-R33 SOURCE-ONLY ownership/abandonment contract; no OS callback or output.
python3 -B "$ROOT/audits/r33_failure_state_ownership_contract.py" \
  --root "$ROOT" --archive-r19 "$FREQMED_GEN_R19_ARCHIVE_DIR" \
  --r16 "$WORK/GEN_R16_OWNERSHIP_EVIDENCE.json" \
  --r17 "$WORK/GEN_R17_VERIFIED_EVIDENCE.json" \
  --r18 "$WORK/GEN_R18_CONTROL_FLOW_EVIDENCE.json" \
  --r19 "$WORK/GEN_R19_ADVERSARIAL_EVIDENCE.json" \
  --r20 "$WORK/GEN_R20_BUREAU_VERIFICATION.json" \
  --r21 "$WORK/GEN_R21_BUREAU_GAPS.json" \
  --r22 "$WORK/GEN_R22_COREAUDIO_REVIEW.json" \
  --r23 "$WORK/GEN_R23_PROOF_OBLIGATIONS.json" \
  --r24 "$WORK/GEN_R24_SHARED_STATE_CONTRACT.json" \
  --r25 "$WORK/GEN_R25_REMEDIATION_REVIEW.json" \
  --r26 "$WORK/GEN_R26_PATCH_SAFETY_GATE.json" \
  --r27 "$WORK/GEN_R27_ADVERSARIAL_REVIEW.json" \
  --r28 "$WORK/GEN_R28_QUEUE_ADMISSION_DESIGN.json" \
  --r29 "$WORK/GEN_R29_ADMISSION_INTEGRATION_REVIEW.json" \
  --r30 "$WORK/GEN_R30_COREAUDIO_QUIESCENCE.json" \
  --r31 "$WORK/GEN_R31_CRITICAL_SHUTDOWN.json" \
  --r32 "$WORK/GEN_R32_FAILED_STOP_OWNERSHIP.json" \
  --json "$WORK/GEN_R33_FAILURE_STATE_OWNERSHIP.json" \
  --markdown "$WORK/GEN_R33_FAILURE_STATE_OWNERSHIP.md"
test -s "$WORK/GEN_R33_FAILURE_STATE_OWNERSHIP.json"
test -s "$WORK/GEN_R33_FAILURE_STATE_OWNERSHIP.md"
grep -q '"verdict": "FAILURE_STATE_OWNERSHIP_CONTRACT_DOCUMENTED_NOT_CERTIFIED"' \
  "$WORK/GEN_R33_FAILURE_STATE_OWNERSHIP.json" || {
  echo 'R33_OWNERSHIP_VERDICT=FAIL_CLOSED' >&2; exit 8
}
grep -q '"r33_findings_open": 12' "$WORK/GEN_R33_FAILURE_STATE_OWNERSHIP.json" || exit 8
grep -q '"r33_critical_open": 3' "$WORK/GEN_R33_FAILURE_STATE_OWNERSHIP.json" || exit 8
grep -q '"r33_documentary_states": 10' "$WORK/GEN_R33_FAILURE_STATE_OWNERSHIP.json" || exit 8
echo 'R33_FAILURE_STATE_OWNERSHIP_REVIEW=PASS'
echo "R33_FAILURE_STATE_OWNERSHIP_JSON=$WORK/GEN_R33_FAILURE_STATE_OWNERSHIP.json"
# GEN-R34: independent userdata lifetime/C11/OS proof-gap review, SOURCE ONLY.
# No active callbacks, no AudioQueue operation, no scientific simulation.
python3 -B "$ROOT/audits/r34_userdata_lifetime_review.py" \
  --root "$ROOT" --archive-r19 "$FREQMED_GEN_R19_ARCHIVE_DIR" \
  --r16 "$WORK/GEN_R16_OWNERSHIP_EVIDENCE.json" \
  --r17 "$WORK/GEN_R17_VERIFIED_EVIDENCE.json" \
  --r18 "$WORK/GEN_R18_CONTROL_FLOW_EVIDENCE.json" \
  --r19 "$WORK/GEN_R19_ADVERSARIAL_EVIDENCE.json" \
  --r20 "$WORK/GEN_R20_BUREAU_VERIFICATION.json" \
  --r21 "$WORK/GEN_R21_BUREAU_GAPS.json" \
  --r22 "$WORK/GEN_R22_COREAUDIO_REVIEW.json" \
  --r23 "$WORK/GEN_R23_PROOF_OBLIGATIONS.json" \
  --r24 "$WORK/GEN_R24_SHARED_STATE_CONTRACT.json" \
  --r25 "$WORK/GEN_R25_REMEDIATION_REVIEW.json" \
  --r26 "$WORK/GEN_R26_PATCH_SAFETY_GATE.json" \
  --r27 "$WORK/GEN_R27_ADVERSARIAL_REVIEW.json" \
  --r28 "$WORK/GEN_R28_QUEUE_ADMISSION_DESIGN.json" \
  --r29 "$WORK/GEN_R29_ADMISSION_INTEGRATION_REVIEW.json" \
  --r30 "$WORK/GEN_R30_COREAUDIO_QUIESCENCE.json" \
  --r31 "$WORK/GEN_R31_CRITICAL_SHUTDOWN.json" \
  --r32 "$WORK/GEN_R32_FAILED_STOP_OWNERSHIP.json" \
  --r33 "$WORK/GEN_R33_FAILURE_STATE_OWNERSHIP.json" \
  --json "$WORK/GEN_R34_USERDATA_LIFETIME.json" \
  --markdown "$WORK/GEN_R34_USERDATA_LIFETIME.md"
test -s "$WORK/GEN_R34_USERDATA_LIFETIME.json"
test -s "$WORK/GEN_R34_USERDATA_LIFETIME.md"
grep -q '"verdict": "USERDATA_LIFETIME_OBLIGATIONS_MAPPED_OS_C11_PROOF_OPEN"' \
  "$WORK/GEN_R34_USERDATA_LIFETIME.json" || {
  echo 'R34_LIFETIME_REVIEW_VERDICT=FAIL_CLOSED' >&2; exit 8
}
grep -q '"r34_findings_open": 14' "$WORK/GEN_R34_USERDATA_LIFETIME.json" || exit 8
grep -q '"r34_critical_open": 4' "$WORK/GEN_R34_USERDATA_LIFETIME.json" || exit 8
grep -q '"r34_documentary_phases": 11' "$WORK/GEN_R34_USERDATA_LIFETIME.json" || exit 8
echo 'R34_USERDATA_LIFETIME_REVIEW=PASS'
echo "R34_USERDATA_LIFETIME_JSON=$WORK/GEN_R34_USERDATA_LIFETIME.json"
# GEN-R35: public Apple contract vs pre-admission userdata source review ONLY.
# No CoreAudio callbacks or physical/scientific simulation are executed.
python3 -B "$ROOT/audits/r35_pre_admission_os_contract_review.py" \
  --root "$ROOT" --archive-r19 "$FREQMED_GEN_R19_ARCHIVE_DIR" \
  --r16 "$WORK/GEN_R16_OWNERSHIP_EVIDENCE.json" \
  --r17 "$WORK/GEN_R17_VERIFIED_EVIDENCE.json" \
  --r18 "$WORK/GEN_R18_CONTROL_FLOW_EVIDENCE.json" \
  --r19 "$WORK/GEN_R19_ADVERSARIAL_EVIDENCE.json" \
  --r20 "$WORK/GEN_R20_BUREAU_VERIFICATION.json" \
  --r21 "$WORK/GEN_R21_BUREAU_GAPS.json" \
  --r22 "$WORK/GEN_R22_COREAUDIO_REVIEW.json" \
  --r23 "$WORK/GEN_R23_PROOF_OBLIGATIONS.json" \
  --r24 "$WORK/GEN_R24_SHARED_STATE_CONTRACT.json" \
  --r25 "$WORK/GEN_R25_REMEDIATION_REVIEW.json" \
  --r26 "$WORK/GEN_R26_PATCH_SAFETY_GATE.json" \
  --r27 "$WORK/GEN_R27_ADVERSARIAL_REVIEW.json" \
  --r28 "$WORK/GEN_R28_QUEUE_ADMISSION_DESIGN.json" \
  --r29 "$WORK/GEN_R29_ADMISSION_INTEGRATION_REVIEW.json" \
  --r30 "$WORK/GEN_R30_COREAUDIO_QUIESCENCE.json" \
  --r31 "$WORK/GEN_R31_CRITICAL_SHUTDOWN.json" \
  --r32 "$WORK/GEN_R32_FAILED_STOP_OWNERSHIP.json" \
  --r33 "$WORK/GEN_R33_FAILURE_STATE_OWNERSHIP.json" \
  --r34 "$WORK/GEN_R34_USERDATA_LIFETIME.json" \
  --json "$WORK/GEN_R35_PRE_ADMISSION_OS_CONTRACT.json" \
  --markdown "$WORK/GEN_R35_PRE_ADMISSION_OS_CONTRACT.md"
test -s "$WORK/GEN_R35_PRE_ADMISSION_OS_CONTRACT.json"
test -s "$WORK/GEN_R35_PRE_ADMISSION_OS_CONTRACT.md"
grep -q '"verdict": "PUBLIC_OS_CONTRACTS_CLASSIFIED_PRE_ADMISSION_LIFETIME_NOT_PROVEN"' \
  "$WORK/GEN_R35_PRE_ADMISSION_OS_CONTRACT.json" || {
  echo 'R35_API_CONTRACT_VERDICT=FAIL_CLOSED' >&2; exit 8
}
grep -q '"r35_findings_open": 12' "$WORK/GEN_R35_PRE_ADMISSION_OS_CONTRACT.json" || exit 8
grep -q '"r35_critical_open": 4' "$WORK/GEN_R35_PRE_ADMISSION_OS_CONTRACT.json" || exit 8
grep -q '"r35_public_api_classifications": 9' "$WORK/GEN_R35_PRE_ADMISSION_OS_CONTRACT.json" || exit 8
grep -q '"r35_documentary_phase_count": 13' "$WORK/GEN_R35_PRE_ADMISSION_OS_CONTRACT.json" || exit 8
echo 'R35_PRE_ADMISSION_OS_CONTRACT_REVIEW=PASS'
echo "R35_PRE_ADMISSION_OS_CONTRACT_JSON=$WORK/GEN_R35_PRE_ADMISSION_OS_CONTRACT.json"
# GEN-R36: independent C11 static anchor architecture review; source only.
# No callback dispatch, CoreAudio operation or scientific simulation.
python3 -B "$ROOT/audits/r36_static_anchor_proof_gate.py" \
  --root "$ROOT" --archive-r19 "$FREQMED_GEN_R19_ARCHIVE_DIR" \
  --r16 "$WORK/GEN_R16_OWNERSHIP_EVIDENCE.json" \
  --r17 "$WORK/GEN_R17_VERIFIED_EVIDENCE.json" \
  --r18 "$WORK/GEN_R18_CONTROL_FLOW_EVIDENCE.json" \
  --r19 "$WORK/GEN_R19_ADVERSARIAL_EVIDENCE.json" \
  --r20 "$WORK/GEN_R20_BUREAU_VERIFICATION.json" \
  --r21 "$WORK/GEN_R21_BUREAU_GAPS.json" \
  --r22 "$WORK/GEN_R22_COREAUDIO_REVIEW.json" \
  --r23 "$WORK/GEN_R23_PROOF_OBLIGATIONS.json" \
  --r24 "$WORK/GEN_R24_SHARED_STATE_CONTRACT.json" \
  --r25 "$WORK/GEN_R25_REMEDIATION_REVIEW.json" \
  --r26 "$WORK/GEN_R26_PATCH_SAFETY_GATE.json" \
  --r27 "$WORK/GEN_R27_ADVERSARIAL_REVIEW.json" \
  --r28 "$WORK/GEN_R28_QUEUE_ADMISSION_DESIGN.json" \
  --r29 "$WORK/GEN_R29_ADMISSION_INTEGRATION_REVIEW.json" \
  --r30 "$WORK/GEN_R30_COREAUDIO_QUIESCENCE.json" \
  --r31 "$WORK/GEN_R31_CRITICAL_SHUTDOWN.json" \
  --r32 "$WORK/GEN_R32_FAILED_STOP_OWNERSHIP.json" \
  --r33 "$WORK/GEN_R33_FAILURE_STATE_OWNERSHIP.json" \
  --r34 "$WORK/GEN_R34_USERDATA_LIFETIME.json" \
  --r35 "$WORK/GEN_R35_PRE_ADMISSION_OS_CONTRACT.json" \
  --json "$WORK/GEN_R36_STATIC_ANCHOR_PROOF.json" \
  --markdown "$WORK/GEN_R36_STATIC_ANCHOR_PROOF.md"
test -s "$WORK/GEN_R36_STATIC_ANCHOR_PROOF.json"
test -s "$WORK/GEN_R36_STATIC_ANCHOR_PROOF.md"
grep -q '"verdict": "STATIC_LIFETIME_ANCHOR_CANDIDATE_REVIEWABLE_NOT_INTEGRATED_NOT_CERTIFIED"' \
 "$WORK/GEN_R36_STATIC_ANCHOR_PROOF.json" || {
 echo 'R36_ANCHOR_VERDICT=FAIL_CLOSED' >&2; exit 8
}
grep -q '"r36_findings_open": 12' "$WORK/GEN_R36_STATIC_ANCHOR_PROOF.json" || exit 8
grep -q '"r36_critical_open": 4' "$WORK/GEN_R36_STATIC_ANCHOR_PROOF.json" || exit 8
grep -q '"r36_candidate_integrated": false' "$WORK/GEN_R36_STATIC_ANCHOR_PROOF.json" || exit 8
echo 'R36_STATIC_ANCHOR_REVIEW=PASS'
echo "R36_STATIC_ANCHOR_JSON=$WORK/GEN_R36_STATIC_ANCHOR_PROOF.json"
# GEN-R37: source-only callback lease integration/ownership review.
# NEVER execute either C11 candidate or any CoreAudio OS callback.
python3 -B "$ROOT/audits/r37_adapter_ownership_proof_review.py" \
  --root "$ROOT" --archive-r19 "$FREQMED_GEN_R19_ARCHIVE_DIR" \
  --r16 "$WORK/GEN_R16_OWNERSHIP_EVIDENCE.json" \
  --r17 "$WORK/GEN_R17_VERIFIED_EVIDENCE.json" \
  --r18 "$WORK/GEN_R18_CONTROL_FLOW_EVIDENCE.json" \
  --r19 "$WORK/GEN_R19_ADVERSARIAL_EVIDENCE.json" \
  --r20 "$WORK/GEN_R20_BUREAU_VERIFICATION.json" \
  --r21 "$WORK/GEN_R21_BUREAU_GAPS.json" \
  --r22 "$WORK/GEN_R22_COREAUDIO_REVIEW.json" \
  --r23 "$WORK/GEN_R23_PROOF_OBLIGATIONS.json" \
  --r24 "$WORK/GEN_R24_SHARED_STATE_CONTRACT.json" \
  --r25 "$WORK/GEN_R25_REMEDIATION_REVIEW.json" \
  --r26 "$WORK/GEN_R26_PATCH_SAFETY_GATE.json" \
  --r27 "$WORK/GEN_R27_ADVERSARIAL_REVIEW.json" \
  --r28 "$WORK/GEN_R28_QUEUE_ADMISSION_DESIGN.json" \
  --r29 "$WORK/GEN_R29_ADMISSION_INTEGRATION_REVIEW.json" \
  --r30 "$WORK/GEN_R30_COREAUDIO_QUIESCENCE.json" \
  --r31 "$WORK/GEN_R31_CRITICAL_SHUTDOWN.json" \
  --r32 "$WORK/GEN_R32_FAILED_STOP_OWNERSHIP.json" \
  --r33 "$WORK/GEN_R33_FAILURE_STATE_OWNERSHIP.json" \
  --r34 "$WORK/GEN_R34_USERDATA_LIFETIME.json" \
  --r35 "$WORK/GEN_R35_PRE_ADMISSION_OS_CONTRACT.json" \
  --r36 "$WORK/GEN_R36_STATIC_ANCHOR_PROOF.json" \
  --json "$WORK/GEN_R37_CALLBACK_LEASE_PROOF.json" \
  --markdown "$WORK/GEN_R37_CALLBACK_LEASE_PROOF.md"
test -s "$WORK/GEN_R37_CALLBACK_LEASE_PROOF.json"
test -s "$WORK/GEN_R37_CALLBACK_LEASE_PROOF.md"
grep -q '"verdict": "ISOLATED_C11_LEASE_ADAPTER_REVIEWED_OS_INTEGRATION_NOT_PROVEN"' \
  "$WORK/GEN_R37_CALLBACK_LEASE_PROOF.json" || {
  echo 'R37_CALLBACK_LEASE_VERDICT=FAIL_CLOSED' >&2; exit 8
}
grep -q '"r37_findings_open": 14' "$WORK/GEN_R37_CALLBACK_LEASE_PROOF.json" || exit 8
grep -q '"r37_critical_open": 4' "$WORK/GEN_R37_CALLBACK_LEASE_PROOF.json" || exit 8
grep -q '"r37_candidate_integrated": false' "$WORK/GEN_R37_CALLBACK_LEASE_PROOF.json" || exit 8
echo 'R37_ADAPTER_OWNERSHIP_REVIEW=PASS'
echo "R37_CALLBACK_LEASE_PROOF_JSON=$WORK/GEN_R37_CALLBACK_LEASE_PROOF.json"
















# GEN-R27 quarantined native C candidate: compile into a separate object.
# Do NOT link or load this object in any runnable binary or test harness.
clang -arch x86_64 -std=c11 -O2 -Wall -Wextra -Werror -c \
  -I"$ROOT/src" "$ROOT/candidates/acoustic_macos_r26.c" \
  -o "$WORK/acoustic_macos_r26.candidate.isolated.o"
test -s "$WORK/acoustic_macos_r26.candidate.isolated.o"
echo 'R27_ISOLATED_CANDIDATE_OBJECT=COMPILED_UNLINKED'

# GEN-R28 C11 design compiled in isolation and never linked or loaded.
clang -arch x86_64 -std=c11 -O2 -Wall -Wextra -Werror -c \
  "$ROOT/candidates/r28_callback_admission_gate.c" \
  -o "$WORK/r28_callback_admission_gate.design.unlinked.o"
test -s "$WORK/r28_callback_admission_gate.design.unlinked.o"
echo 'R28_ADMISSION_DESIGN_OBJECT=COMPILED_UNLINKED'

# GEN-R29 C11 integration candidate: compile separately, NEVER link or load.
clang -arch x86_64 -std=c11 -O2 -Wall -Wextra -Werror -c \
  -I"$ROOT/src" "$ROOT/candidates/acoustic_macos_r29.c" \
  -o "$WORK/acoustic_macos_r29.candidate.isolated.o"
test -s "$WORK/acoustic_macos_r29.candidate.isolated.o"
echo 'R29_INTEGRATED_CANDIDATE_OBJECT=COMPILED_UNLINKED'
echo 'R30_R29_CANDIDATE_OBJECT=COMPILED_UNLINKED'
echo 'R29_ADMISSION_DESIGN_OBJECT=COMPILED_UNLINKED'
# GEN-R31: separate C11/OS shutdown remediation candidate, NEVER LINK/LOAD.
clang -arch x86_64 -std=c11 -O2 -Wall -Wextra -Werror -c \
  -I"$ROOT/src" "$ROOT/candidates/acoustic_macos_r31.c" \
  -o "$WORK/acoustic_macos_r31.candidate.isolated.o"
test -s "$WORK/acoustic_macos_r31.candidate.isolated.o"
echo 'R31_REMEDIATION_CANDIDATE_OBJECT=COMPILED_UNLINKED'
echo 'R32_R31_CANDIDATE_OBJECT=COMPILED_UNLINKED'
echo 'R33_R31_CANDIDATE_OBJECT=COMPILED_UNLINKED'
echo 'R34_R31_CANDIDATE_OBJECT=COMPILED_UNLINKED'
echo 'R35_R31_CANDIDATE_OBJECT=COMPILED_UNLINKED'
echo 'R36_R31_CANDIDATE_OBJECT=COMPILED_UNLINKED'
echo 'R37_R31_CANDIDATE_OBJECT=COMPILED_UNLINKED'
# GEN-R36: compile standalone static anchor C11, NEVER LINK or execute it.
clang -arch x86_64 -std=c11 -O2 -Wall -Wextra -Werror -c \
  "$ROOT/candidates/r36_stable_userdata_anchor.c" \
  -o "$WORK/r36_stable_userdata_anchor.isolated.o"
test -s "$WORK/r36_stable_userdata_anchor.isolated.o"
# C11 candidate has no OS audio/physical output references.
if nm -u "$WORK/r36_stable_userdata_anchor.isolated.o" | \
   grep -Eq '_(AudioQueue|AudioDevice|AudioObjectSetPropertyData|AudioOutputUnitStart|IOServiceOpen|dlopen|dlsym|free|malloc|calloc)'; then
 echo 'R36_STABLE_ANCHOR_OBJECT_FORBIDDEN_SYMBOL=BLOCK' >&2; exit 8
fi
echo 'R36_STABLE_ANCHOR_OBJECT=COMPILED_UNLINKED'
echo 'R37_STABLE_ANCHOR_OBJECT=COMPILED_UNLINKED'
# GEN-R37: compile the NEW C11 adapter as a separate UNLINKED object.
# fm36 symbols are unresolved on purpose; linker must NEVER see this object.
clang -arch x86_64 -std=c11 -O2 -Wall -Wextra -Werror -c \
  "$ROOT/candidates/r37_callback_lease_adapter.c" \
  -o "$WORK/r37_callback_lease_adapter.isolated.o"
test -s "$WORK/r37_callback_lease_adapter.isolated.o"
if nm -u "$WORK/r37_callback_lease_adapter.isolated.o" | \
   grep -Eq '_(AudioQueue|AudioDevice|AudioObjectSetPropertyData|AudioOutputUnitStart|IOServiceOpen|dlopen|dlsym|free|malloc|calloc)'; then
 echo 'R37_ADAPTER_OBJECT_FORBIDDEN_SYMBOL=BLOCK' >&2; exit 8
fi
echo 'R37_CALLBACK_LEASE_OBJECT=COMPILED_UNLINKED'




# CoreAudio output and EM devices remain SOURCE ONLY; never load or link output.
# R27 audits failure-path ownership without linking or running output backends.
# Compile isolated CoreAudio and EM sources only; retain nonemitting CLI.
# No physical output, scientific simulation, or real CoreAudio callbacks executed.
# No AudioQueue constructor/stop/dispose is ever linked to runnable executable.
for name in acoustic_macos acoustic_route_guard_macos acoustic_device_pin_macos; do
  clang -arch x86_64 -std=c11 -O2 -Wall -Wextra -Werror -c \
    "$ROOT/src/$name.c" -o "$WORK/$name.isolated.o"
  test -s "$WORK/$name.isolated.o"
done
clang -arch x86_64 -std=c11 -O2 -Wall -Wextra -Werror -c \
  -I"$ROOT/src" "$ROOT/src/em_device_contract.c" \
  -o "$WORK/em_contract.isolated.o"
test -s "$WORK/em_contract.isolated.o"
# Documentary EM evidence screen is source-only, never linked/loaded or used
# to unlock an instrument. Compile only for native C review.
clang -arch x86_64 -std=c11 -O2 -Wall -Wextra -Werror -c \
  -I"$ROOT/src" "$ROOT/src/em_qualification_gate.c" \
  -o "$WORK/em_qualification.isolated.o"
test -s "$WORK/em_qualification.isolated.o"
echo 'R27_ACOUSTIC_LIFECYCLE_OBJECT=COMPILED_UNLINKED; FIVE_BACKEND_OBJECTS=COMPILED_NOT_LINKED'
# Real software admission tests only; USB descriptor codes are USB-IF facts.
clang -arch x86_64 -std=c11 -O2 -Wall -Wextra -Werror \
  -I"$ROOT/src" -o "$WORK/em-contract-software-tests" \
  "$ROOT/tests/test_em_contract_native.c" "$ROOT/src/em_device_contract.c" -lm
"$WORK/em-contract-software-tests"
clang -arch x86_64 -std=c11 -O2 -Wall -Wextra -Werror \
  -I"$ROOT/src" -o "$WORK/em-discovery-descriptor-tests" \
  "$ROOT/tests/test_em_discovery_native.c" \
  "$ROOT/src/em_hardware_discovery_macos.c" \
  -framework IOKit -framework CoreFoundation
"$WORK/em-discovery-descriptor-tests"
# Runnable includes ONLY IOKit registry READ-ONLY discovery + denied outputs.
clang -arch x86_64 -std=c11 -O2 -Wall -Wextra -Werror \
 -DFREQMED_GEN_R7_DISCOVERY -o "$WORK/freqmed-gen" \
 "$ROOT/src/main.c" "$ROOT/src/generator_core.c" \
 "$ROOT/src/acoustic_probe_macos.c" "$ROOT/src/output_hard_denied.c" \
 "$ROOT/src/em_backend.c" "$ROOT/src/em_hardware_discovery_macos.c" \
 -framework CoreAudio -framework CoreFoundation -framework IOKit -lm
UNDEFINED="$(nm -u "$WORK/freqmed-gen")" || { echo 'R27_NM_UNAVAILABLE=BLOCK' >&2;exit 8; }
if printf '%s\n' "$UNDEFINED" | grep -Eq '_(AudioQueueStart|AudioQueueNewOutput|AudioQueueStop|AudioQueueDispose|AudioQueueAddPropertyListener|AudioQueueRemovePropertyListener|AudioQueueSetProperty|AudioDeviceStart|AudioObjectSetPropertyData|AudioQueueEnqueueBuffer|AudioUnitRender|AudioOutputUnitStart|IOServiceOpen|IORegistryEntrySetCFProperty|IORegistryEntrySetCFProperties|USBDeviceOpen|open|write|connect)($|[^A-Za-z])'; then
 echo 'R27_FORBIDDEN_NATIVE_SYMBOL=BLOCK' >&2;exit 8
fi
ALL_SYMBOLS="$(nm "$WORK/freqmed-gen")" || { echo 'R27_NM_UNAVAILABLE=BLOCK' >&2;exit 8; }
if printf '%s\n' "$ALL_SYMBOLS" | grep -Eq '_(acoustic_output_impl|fm_acoustic_bind_queue_to_route|fm_route_capture|fm_route_unchanged|fm_em_check_setpoint|fm_em_try_physical_emission)($|[^A-Za-z])'; then
 echo 'R27_OUTPUT_BACKEND_LINKED=BLOCK' >&2;exit 8
fi
echo 'R27_NONEMITTING_EXECUTABLE_SYMBOL_AUDIT=PASS'
echo 'R28_NONEMITTING_EXECUTABLE_SYMBOL_AUDIT=PASS'
echo 'R29_NONEMITTING_EXECUTABLE_SYMBOL_AUDIT=PASS'
echo 'R30_NONEMITTING_EXECUTABLE_SYMBOL_AUDIT=PASS'
echo 'R31_NONEMITTING_EXECUTABLE_SYMBOL_AUDIT=PASS'
echo 'R32_NONEMITTING_EXECUTABLE_SYMBOL_AUDIT=PASS'
echo 'R33_NONEMITTING_EXECUTABLE_SYMBOL_AUDIT=PASS'
echo 'R34_NONEMITTING_EXECUTABLE_SYMBOL_AUDIT=PASS'
echo 'R35_NONEMITTING_EXECUTABLE_SYMBOL_AUDIT=PASS'
echo 'R36_NONEMITTING_EXECUTABLE_SYMBOL_AUDIT=PASS'
echo 'R37_NONEMITTING_EXECUTABLE_SYMBOL_AUDIT=PASS'
# FIX1: reject unittest.TestCase.run shadowing BEFORE invoking the suite.
# This is pure Python syntax-tree inspection, not a callback or simulation.
python3 -B - "$ROOT/tests/test_r29_admission_integration_review.py" <<'PY'
import ast
import sys
from pathlib import Path
file=Path(sys.argv[1])
tree=ast.parse(file.read_text(encoding="utf-8"),filename=str(file))
classes=[node for node in tree.body if isinstance(node,ast.ClassDef)
         and node.name=="R29AdmissionIntegrationReview"]
if len(classes)!=1:
    raise SystemExit("R29_TESTCASE_RUN_SLOT=BLOCK: missing review class")
cls=classes[0]
for node in ast.walk(cls):
    if isinstance(node,(ast.Assign,ast.AnnAssign)):
        targets=node.targets if isinstance(node,ast.Assign) else [node.target]
        for target in targets:
            if (isinstance(target,ast.Attribute) and target.attr=="run"
                    and isinstance(target.value,ast.Name)
                    and target.value.id in ("cls","self")):
                raise SystemExit("R29_TESTCASE_RUN_SLOT=BLOCK: runner shadows TestCase.run")
print("R29_TESTCASE_RUN_SLOT=PASS")
PY
# GEN-R30: independent class-slot guard against the R29 FIX1 regression.
python3 -B - "$ROOT/tests/test_r30_coreaudio_quiescence_adversarial.py" <<'PY'
import ast
import sys
from pathlib import Path
file=Path(sys.argv[1])
tree=ast.parse(file.read_text(encoding="utf-8"),filename=str(file))
targets=[x for x in tree.body if isinstance(x,ast.ClassDef)
         and x.name=="R30CoreAudioQuiescenceReview"]
if len(targets)!=1:
    raise SystemExit("R30_TESTCASE_RUN_SLOT=BLOCK: class absent")
for node in ast.walk(targets[0]):
    if isinstance(node,(ast.Assign,ast.AnnAssign)):
        dest=node.targets if isinstance(node,ast.Assign) else [node.target]
        for target in dest:
            if isinstance(target,ast.Attribute) and target.attr=="run" and isinstance(target.value,ast.Name) and target.value.id in ("cls","self"):
                raise SystemExit("R30_TESTCASE_RUN_SLOT=BLOCK: unittest.TestCase.run shadowed")
print("R30_TESTCASE_RUN_SLOT=PASS")
PY
# GEN-R31: prevent inherited unittest.TestCase.run shadowing (R29 FIX1).
python3 -B - "$ROOT/tests/test_r31_critical_shutdown_review.py" <<'PY'
import ast
import sys
from pathlib import Path
f=Path(sys.argv[1])
tree=ast.parse(f.read_text(encoding="utf-8"),filename=str(f))
classes=[n for n in tree.body if isinstance(n,ast.ClassDef)
         and n.name=="R31CriticalShutdownReview"]
if len(classes)!=1:
    raise SystemExit("R31_TESTCASE_RUN_SLOT=BLOCK: review class absent")
for node in ast.walk(classes[0]):
    if isinstance(node,(ast.Assign,ast.AnnAssign)):
        targets=node.targets if isinstance(node,ast.Assign) else [node.target]
        for target in targets:
            if isinstance(target,ast.Attribute) and target.attr=="run" and isinstance(target.value,ast.Name) and target.value.id in ("self","cls"):
                raise SystemExit("R31_TESTCASE_RUN_SLOT=BLOCK: unittest.TestCase.run shadowed")
print("R31_TESTCASE_RUN_SLOT=PASS")
PY
# GEN-R32: fail closed on unittest.TestCase.run shadowing.
python3 -B - "$ROOT/tests/test_r32_failed_stop_ownership_review.py" <<'PY'
import ast
import sys
from pathlib import Path
f=Path(sys.argv[1])
nodes=ast.parse(f.read_text(encoding="utf-8"),filename=str(f))
classes=[x for x in nodes.body if isinstance(x,ast.ClassDef)
         and x.name=="R32FailedStopOwnershipReview"]
if len(classes)!=1: raise SystemExit("R32_TESTCASE_RUN_SLOT=BLOCK")
for n in ast.walk(classes[0]):
    if isinstance(n,(ast.Assign,ast.AnnAssign)):
        targets=n.targets if isinstance(n,ast.Assign) else [n.target]
        for target in targets:
            if isinstance(target,ast.Attribute) and target.attr=="run" and isinstance(target.value,ast.Name) and target.value.id in ("self","cls"):
                raise SystemExit("R32_TESTCASE_RUN_SLOT=BLOCK: run shadowed")
print("R32_TESTCASE_RUN_SLOT=PASS")
PY
# GEN-R33: fail closed on inherited unittest.TestCase.run shadowing.
python3 -B - "$ROOT/tests/test_r33_failure_state_ownership_contract.py" <<'PY'
import ast
import sys
from pathlib import Path
f=Path(sys.argv[1])
tree=ast.parse(f.read_text(encoding="utf-8"),filename=str(f))
classes=[n for n in tree.body if isinstance(n,ast.ClassDef)
         and n.name=="R33FailureStateOwnershipReview"]
if len(classes)!=1:
    raise SystemExit("R33_TESTCASE_RUN_SLOT=BLOCK: review class absent")
for n in ast.walk(classes[0]):
    if isinstance(n,(ast.Assign,ast.AnnAssign)):
        dest=n.targets if isinstance(n,ast.Assign) else [n.target]
        for t in dest:
            if isinstance(t,ast.Attribute) and t.attr=="run" and isinstance(t.value,ast.Name) and t.value.id in ("self","cls"):
                raise SystemExit("R33_TESTCASE_RUN_SLOT=BLOCK: unittest.TestCase.run overwritten")
print("R33_TESTCASE_RUN_SLOT=PASS")
PY
# GEN-R34: no Python unittest.TestCase.run shadowing.
python3 -B - "$ROOT/tests/test_r34_userdata_lifetime_review.py" <<'PY'
import ast
import sys
from pathlib import Path
file=Path(sys.argv[1])
parsed=ast.parse(file.read_text(encoding="utf-8"),filename=str(file))
classes=[x for x in parsed.body if isinstance(x,ast.ClassDef)
         and x.name=="R34UserdataLifetimeReview"]
if len(classes)!=1: raise SystemExit("R34_TESTCASE_RUN_SLOT=BLOCK: class missing")
for node in ast.walk(classes[0]):
    if isinstance(node,(ast.Assign,ast.AnnAssign)):
        targets=node.targets if isinstance(node,ast.Assign) else [node.target]
        for target in targets:
            if isinstance(target,ast.Attribute) and target.attr=="run" and isinstance(target.value,ast.Name) and target.value.id in ("self","cls"):
                raise SystemExit("R34_TESTCASE_RUN_SLOT=BLOCK: unittest.TestCase.run shadowed")
print("R34_TESTCASE_RUN_SLOT=PASS")
PY
# GEN-R35: block unittest.TestCase.run shadowing, source-only.
python3 -B - "$ROOT/tests/test_r35_pre_admission_os_contract_review.py" <<'PY'
import ast
import sys
from pathlib import Path
f=Path(sys.argv[1])
nodes=ast.parse(f.read_text(encoding="utf-8"),filename=str(f))
cls=[node for node in nodes.body if isinstance(node,ast.ClassDef)
     and node.name=="R35PreAdmissionOSContractReview"]
if len(cls)!=1: raise SystemExit("R35_TESTCASE_RUN_SLOT=BLOCK: review class absent")
for node in ast.walk(cls[0]):
    if isinstance(node,(ast.Assign,ast.AnnAssign)):
        dest=node.targets if isinstance(node,ast.Assign) else [node.target]
        for t in dest:
            if isinstance(t,ast.Attribute) and t.attr=="run" and isinstance(t.value,ast.Name) and t.value.id in ("self","cls"):
                raise SystemExit("R35_TESTCASE_RUN_SLOT=BLOCK: unittest.TestCase.run overwritten")
print("R35_TESTCASE_RUN_SLOT=PASS")
PY
# GEN-R36: forbid unittest.TestCase.run overriding the native runner.
python3 -B - "$ROOT/tests/test_r36_static_anchor_proof_gate.py" <<'PY'
import ast
import sys
from pathlib import Path
f=Path(sys.argv[1])
tree=ast.parse(f.read_text(encoding="utf-8"),filename=str(f))
classes=[x for x in tree.body if isinstance(x,ast.ClassDef)
         and x.name=="R36StaticAnchorProofGate"]
if len(classes)!=1:
    raise SystemExit("R36_TESTCASE_RUN_SLOT=BLOCK: review class missing")
for node in ast.walk(classes[0]):
    if isinstance(node,(ast.Assign,ast.AnnAssign)):
        targets=node.targets if isinstance(node,ast.Assign) else [node.target]
        for target in targets:
            if isinstance(target,ast.Attribute) and target.attr=="run" and isinstance(target.value,ast.Name) and target.value.id in ("self","cls"):
                raise SystemExit("R36_TESTCASE_RUN_SLOT=BLOCK: TestCase.run overwritten")
print("R36_TESTCASE_RUN_SLOT=PASS")
PY
# GEN-R37: fail closed when unittest.TestCase.run is accidentally shadowed.
python3 -B - "$ROOT/tests/test_r37_adapter_ownership_proof_review.py" <<'PY'
import ast
import sys
from pathlib import Path
p=Path(sys.argv[1])
tree=ast.parse(p.read_text(encoding="utf-8"),filename=str(p))
classes=[x for x in tree.body if isinstance(x,ast.ClassDef)
         and x.name=="R37AdapterOwnershipProofReview"]
if len(classes)!=1: raise SystemExit("R37_TESTCASE_RUN_SLOT=BLOCK: class missing")
for node in ast.walk(classes[0]):
    if isinstance(node,(ast.Assign,ast.AnnAssign)):
        targets=node.targets if isinstance(node,ast.Assign) else [node.target]
        for target in targets:
            if isinstance(target,ast.Attribute) and target.attr=="run" and isinstance(target.value,ast.Name) and target.value.id in ("self","cls"):
                raise SystemExit("R37_TESTCASE_RUN_SLOT=BLOCK: TestCase.run overwritten")
print("R37_TESTCASE_RUN_SLOT=PASS")
PY
case "$MODE" in
 selftest)
  "$WORK/freqmed-gen" selftest
  (cd "$ROOT" && FREQMED_GEN_R21_EVIDENCE_DIR="$WORK" FREQMED_GEN_R22_EVIDENCE_DIR="$WORK" FREQMED_GEN_R23_EVIDENCE_DIR="$WORK" FREQMED_GEN_R24_EVIDENCE_DIR="$WORK" FREQMED_GEN_R25_EVIDENCE_DIR="$WORK" FREQMED_GEN_R26_EVIDENCE_DIR="$WORK" FREQMED_GEN_R27_EVIDENCE_DIR="$WORK" FREQMED_GEN_R28_EVIDENCE_DIR="$WORK" FREQMED_GEN_R29_EVIDENCE_DIR="$WORK" FREQMED_GEN_R30_EVIDENCE_DIR="$WORK" FREQMED_GEN_R31_EVIDENCE_DIR="$WORK" FREQMED_GEN_R32_EVIDENCE_DIR="$WORK" FREQMED_GEN_R33_EVIDENCE_DIR="$WORK" FREQMED_GEN_R34_EVIDENCE_DIR="$WORK" FREQMED_GEN_R35_EVIDENCE_DIR="$WORK" FREQMED_GEN_R36_EVIDENCE_DIR="$WORK" FREQMED_GEN_R37_EVIDENCE_DIR="$WORK" FREQMED_GEN_R1_BINARY="$WORK/freqmed-gen" \
    FREQMED_GEN_R2_BINARY="$WORK/freqmed-gen" FREQMED_GEN_R3_BINARY="$WORK/freqmed-gen" \
    FREQMED_GEN_R4_BINARY="$WORK/freqmed-gen" FREQMED_GEN_R5_BINARY="$WORK/freqmed-gen" \
    FREQMED_GEN_R6_BINARY="$WORK/freqmed-gen" FREQMED_GEN_R7_BINARY="$WORK/freqmed-gen" FREQMED_GEN_R8_BINARY="$WORK/freqmed-gen" FREQMED_GEN_R9_BINARY="$WORK/freqmed-gen" FREQMED_GEN_R10_BINARY="$WORK/freqmed-gen" FREQMED_GEN_R11_BINARY="$WORK/freqmed-gen" FREQMED_GEN_R12_BINARY="$WORK/freqmed-gen" FREQMED_GEN_R13_BINARY="$WORK/freqmed-gen" FREQMED_GEN_R14_BINARY="$WORK/freqmed-gen" FREQMED_GEN_R15_BINARY="$WORK/freqmed-gen" FREQMED_GEN_R16_BINARY="$WORK/freqmed-gen" FREQMED_GEN_R17_BINARY="$WORK/freqmed-gen" FREQMED_GEN_R18_BINARY="$WORK/freqmed-gen" FREQMED_GEN_R19_BINARY="$WORK/freqmed-gen" FREQMED_GEN_R20_BINARY="$WORK/freqmed-gen" FREQMED_GEN_R21_BINARY="$WORK/freqmed-gen" FREQMED_GEN_R22_BINARY="$WORK/freqmed-gen" FREQMED_GEN_R23_BINARY="$WORK/freqmed-gen" FREQMED_GEN_R24_BINARY="$WORK/freqmed-gen" FREQMED_GEN_R25_BINARY="$WORK/freqmed-gen" FREQMED_GEN_R26_BINARY="$WORK/freqmed-gen" FREQMED_GEN_R27_BINARY="$WORK/freqmed-gen" FREQMED_GEN_R28_BINARY="$WORK/freqmed-gen" FREQMED_GEN_R29_BINARY="$WORK/freqmed-gen" FREQMED_GEN_R30_BINARY="$WORK/freqmed-gen" FREQMED_GEN_R31_BINARY="$WORK/freqmed-gen" FREQMED_GEN_R32_BINARY="$WORK/freqmed-gen" FREQMED_GEN_R33_BINARY="$WORK/freqmed-gen" FREQMED_GEN_R34_BINARY="$WORK/freqmed-gen" FREQMED_GEN_R35_BINARY="$WORK/freqmed-gen" FREQMED_GEN_R36_BINARY="$WORK/freqmed-gen" FREQMED_GEN_R37_BINARY="$WORK/freqmed-gen" \
    python3 -B -m unittest discover -s tests -p 'test_*.py' -v)
  "$WORK/freqmed-gen" status ;;
 status) "$WORK/freqmed-gen" status ;;
 probe) "$WORK/freqmed-gen" probe ;;
 em-discover) "$WORK/freqmed-gen" em-discover ;;
esac
# GEN-R27 owner-private review ONLY after all nonemitting tests pass.
# Real R19 archive untouched; native C candidates remain unlinked/unloaded.
if [ "$MODE" = selftest ]; then
  umask 077
  REVIEW_DIR="$(mktemp -d "$HOME/Downloads/FREQMED_GEN_R37_CALLBACK_LEASE_XXXXXX")"
  for NAME in \
    GEN_R20_BUREAU_VERIFICATION.json GEN_R20_BUREAU_READINESS.md \
    GEN_R21_BUREAU_GAPS.json GEN_R21_BUREAU_GAPS.md \
    GEN_R22_COREAUDIO_REVIEW.json GEN_R22_COREAUDIO_REVIEW.md \
    GEN_R23_PROOF_OBLIGATIONS.json GEN_R23_PROOF_OBLIGATIONS.md \
    GEN_R24_SHARED_STATE_CONTRACT.json GEN_R24_SHARED_STATE_CONTRACT.md \
    GEN_R25_REMEDIATION_REVIEW.json GEN_R25_REMEDIATION_REVIEW.md \
    GEN_R26_PATCH_SAFETY_GATE.json GEN_R26_PATCH_SAFETY_GATE.md \
    GEN_R27_ADVERSARIAL_REVIEW.json GEN_R27_ADVERSARIAL_REVIEW.md \
    GEN_R28_QUEUE_ADMISSION_DESIGN.json GEN_R28_QUEUE_ADMISSION_DESIGN.md \
    GEN_R29_ADMISSION_INTEGRATION_REVIEW.json GEN_R29_ADMISSION_INTEGRATION_REVIEW.md \
    GEN_R30_COREAUDIO_QUIESCENCE.json GEN_R30_COREAUDIO_QUIESCENCE.md \
    GEN_R31_CRITICAL_SHUTDOWN.json GEN_R31_CRITICAL_SHUTDOWN.md \
    GEN_R32_FAILED_STOP_OWNERSHIP.json GEN_R32_FAILED_STOP_OWNERSHIP.md \
    GEN_R33_FAILURE_STATE_OWNERSHIP.json GEN_R33_FAILURE_STATE_OWNERSHIP.md \
    GEN_R34_USERDATA_LIFETIME.json GEN_R34_USERDATA_LIFETIME.md \
    GEN_R35_PRE_ADMISSION_OS_CONTRACT.json GEN_R35_PRE_ADMISSION_OS_CONTRACT.md \
    GEN_R36_STATIC_ANCHOR_PROOF.json GEN_R36_STATIC_ANCHOR_PROOF.md \
     GEN_R37_CALLBACK_LEASE_PROOF.json GEN_R37_CALLBACK_LEASE_PROOF.md; do
    cp "$WORK/$NAME" "$REVIEW_DIR/"
  done
  (cd "$REVIEW_DIR" &&
    shasum -a 256 \
      GEN_R20_BUREAU_VERIFICATION.json GEN_R20_BUREAU_READINESS.md \
      GEN_R21_BUREAU_GAPS.json GEN_R21_BUREAU_GAPS.md \
      GEN_R22_COREAUDIO_REVIEW.json GEN_R22_COREAUDIO_REVIEW.md \
      GEN_R23_PROOF_OBLIGATIONS.json GEN_R23_PROOF_OBLIGATIONS.md \
      GEN_R24_SHARED_STATE_CONTRACT.json GEN_R24_SHARED_STATE_CONTRACT.md \
      GEN_R25_REMEDIATION_REVIEW.json GEN_R25_REMEDIATION_REVIEW.md \
      GEN_R26_PATCH_SAFETY_GATE.json GEN_R26_PATCH_SAFETY_GATE.md \
      GEN_R27_ADVERSARIAL_REVIEW.json GEN_R27_ADVERSARIAL_REVIEW.md \
       GEN_R28_QUEUE_ADMISSION_DESIGN.json GEN_R28_QUEUE_ADMISSION_DESIGN.md \
       GEN_R29_ADMISSION_INTEGRATION_REVIEW.json GEN_R29_ADMISSION_INTEGRATION_REVIEW.md \
       GEN_R30_COREAUDIO_QUIESCENCE.json GEN_R30_COREAUDIO_QUIESCENCE.md \
       GEN_R31_CRITICAL_SHUTDOWN.json GEN_R31_CRITICAL_SHUTDOWN.md \
       GEN_R32_FAILED_STOP_OWNERSHIP.json GEN_R32_FAILED_STOP_OWNERSHIP.md \
        GEN_R33_FAILURE_STATE_OWNERSHIP.json GEN_R33_FAILURE_STATE_OWNERSHIP.md \
       GEN_R34_USERDATA_LIFETIME.json GEN_R34_USERDATA_LIFETIME.md \
       GEN_R35_PRE_ADMISSION_OS_CONTRACT.json GEN_R35_PRE_ADMISSION_OS_CONTRACT.md \
       GEN_R36_STATIC_ANCHOR_PROOF.json GEN_R36_STATIC_ANCHOR_PROOF.md \
        GEN_R37_CALLBACK_LEASE_PROOF.json GEN_R37_CALLBACK_LEASE_PROOF.md \
      > REVIEW_SHA256SUMS.txt &&
    shasum -a 256 -c REVIEW_SHA256SUMS.txt)
  echo 'R37_BUREAU_PROOF_DOSSIER=36_FILES_SHA256_PASS'
  echo "R37_BUREAU_PROOF_DIR=$REVIEW_DIR"
fi
printf '%s\n' 'GEN_R37_EM_HARDWARE=READ_ONLY_REGISTRY; INSTRUMENT_CLAIMS=NONE; ACOUSTIC_EMISSION=NONE; EM_EMISSION=NONE; SCIENTIFIC_SIMULATION=NONE; PRODUCTION=NOT_AUTHORIZED'
