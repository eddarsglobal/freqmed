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
WORK="$(mktemp -d "$HOME/Downloads/FREQMED_GEN_R27_NATIVE_XXXXXX")"
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






# GEN-R27 quarantined native C candidate: compile into a separate object.
# Do NOT link or load this object in any runnable binary or test harness.
clang -arch x86_64 -std=c11 -O2 -Wall -Wextra -Werror -c \
  -I"$ROOT/src" "$ROOT/candidates/acoustic_macos_r26.c" \
  -o "$WORK/acoustic_macos_r26.candidate.isolated.o"
test -s "$WORK/acoustic_macos_r26.candidate.isolated.o"
echo 'R27_ISOLATED_CANDIDATE_OBJECT=COMPILED_UNLINKED'

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
case "$MODE" in
 selftest)
  "$WORK/freqmed-gen" selftest
  (cd "$ROOT" && FREQMED_GEN_R21_EVIDENCE_DIR="$WORK" FREQMED_GEN_R22_EVIDENCE_DIR="$WORK" FREQMED_GEN_R23_EVIDENCE_DIR="$WORK" FREQMED_GEN_R24_EVIDENCE_DIR="$WORK" FREQMED_GEN_R25_EVIDENCE_DIR="$WORK" FREQMED_GEN_R26_EVIDENCE_DIR="$WORK" FREQMED_GEN_R27_EVIDENCE_DIR="$WORK" FREQMED_GEN_R1_BINARY="$WORK/freqmed-gen" \
    FREQMED_GEN_R2_BINARY="$WORK/freqmed-gen" FREQMED_GEN_R3_BINARY="$WORK/freqmed-gen" \
    FREQMED_GEN_R4_BINARY="$WORK/freqmed-gen" FREQMED_GEN_R5_BINARY="$WORK/freqmed-gen" \
    FREQMED_GEN_R6_BINARY="$WORK/freqmed-gen" FREQMED_GEN_R7_BINARY="$WORK/freqmed-gen" FREQMED_GEN_R8_BINARY="$WORK/freqmed-gen" FREQMED_GEN_R9_BINARY="$WORK/freqmed-gen" FREQMED_GEN_R10_BINARY="$WORK/freqmed-gen" FREQMED_GEN_R11_BINARY="$WORK/freqmed-gen" FREQMED_GEN_R12_BINARY="$WORK/freqmed-gen" FREQMED_GEN_R13_BINARY="$WORK/freqmed-gen" FREQMED_GEN_R14_BINARY="$WORK/freqmed-gen" FREQMED_GEN_R15_BINARY="$WORK/freqmed-gen" FREQMED_GEN_R16_BINARY="$WORK/freqmed-gen" FREQMED_GEN_R17_BINARY="$WORK/freqmed-gen" FREQMED_GEN_R18_BINARY="$WORK/freqmed-gen" FREQMED_GEN_R19_BINARY="$WORK/freqmed-gen" FREQMED_GEN_R20_BINARY="$WORK/freqmed-gen" FREQMED_GEN_R21_BINARY="$WORK/freqmed-gen" FREQMED_GEN_R22_BINARY="$WORK/freqmed-gen" FREQMED_GEN_R23_BINARY="$WORK/freqmed-gen" FREQMED_GEN_R24_BINARY="$WORK/freqmed-gen" FREQMED_GEN_R25_BINARY="$WORK/freqmed-gen" FREQMED_GEN_R26_BINARY="$WORK/freqmed-gen" FREQMED_GEN_R27_BINARY="$WORK/freqmed-gen" \
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
  REVIEW_DIR="$(mktemp -d "$HOME/Downloads/FREQMED_GEN_R27_C11_ADVERSARIAL_XXXXXX")"
  for NAME in \
    GEN_R20_BUREAU_VERIFICATION.json GEN_R20_BUREAU_READINESS.md \
    GEN_R21_BUREAU_GAPS.json GEN_R21_BUREAU_GAPS.md \
    GEN_R22_COREAUDIO_REVIEW.json GEN_R22_COREAUDIO_REVIEW.md \
    GEN_R23_PROOF_OBLIGATIONS.json GEN_R23_PROOF_OBLIGATIONS.md \
    GEN_R24_SHARED_STATE_CONTRACT.json GEN_R24_SHARED_STATE_CONTRACT.md \
    GEN_R25_REMEDIATION_REVIEW.json GEN_R25_REMEDIATION_REVIEW.md \
    GEN_R26_PATCH_SAFETY_GATE.json GEN_R26_PATCH_SAFETY_GATE.md \
    GEN_R27_ADVERSARIAL_REVIEW.json GEN_R27_ADVERSARIAL_REVIEW.md; do
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
      > REVIEW_SHA256SUMS.txt &&
    shasum -a 256 -c REVIEW_SHA256SUMS.txt)
  echo 'R27_BUREAU_ADVERSARIAL_DOSSIER=16_FILES_SHA256_PASS'
  echo "R27_BUREAU_ADVERSARIAL_DIR=$REVIEW_DIR"
fi
printf '%s\n' 'GEN_R27_EM_HARDWARE=READ_ONLY_REGISTRY; INSTRUMENT_CLAIMS=NONE; ACOUSTIC_EMISSION=NONE; EM_EMISSION=NONE; SCIENTIFIC_SIMULATION=NONE; PRODUCTION=NOT_AUTHORIZED'
