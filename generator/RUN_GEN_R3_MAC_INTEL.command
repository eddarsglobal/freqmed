#!/bin/bash
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "$0")" && pwd -P)"
MODE="selftest"
if [ "$#" -gt 0 ]; then MODE="$1"; fi
case "$MODE" in selftest|probe|status) ;; *) echo "R3_UNKNOWN_ACTION_BLOCK" >&2; exit 2;; esac
[ "$(uname -s)" = "Darwin" ] || { echo "MACOS_REQUIRED" >&2; exit 3; }
[ "$(uname -m)" = "x86_64" ] || { echo "MAC_INTEL_REQUIRED" >&2; exit 3; }
if [ -f "$ROOT/KIT_SHA256SUMS.txt" ]; then
  (cd "$ROOT" && shasum -a 256 -c KIT_SHA256SUMS.txt)
fi
command -v clang >/dev/null || { echo "MISSING_CLANG_NO_INSTALL" >&2;exit 4; }
command -v python3 >/dev/null || { echo "MISSING_PYTHON3_NO_INSTALL" >&2;exit 4; }
command -v nm >/dev/null || { echo "MISSING_NM_NO_INSTALL" >&2;exit 4; }
WORK="$(mktemp -d "$HOME/Downloads/FREQMED_GEN_R3_BUILD_XXXXXX")"
# Source-only native compilation; object NEVER linked or loaded.
clang -arch x86_64 -std=c11 -O2 -Wall -Wextra -Werror -c \
 "$ROOT/src/acoustic_macos.c" -o "$WORK/isolated_acoustic_backend.o"
test -s "$WORK/isolated_acoustic_backend.o"
echo "R3_COREAUDIO_BACKEND_NATIVE_COMPILE=PASS; OBJECT_NOT_LINKED=YES"
clang -arch x86_64 -std=c11 -O2 -Wall -Wextra -Werror \
 -o "$WORK/freqmed-gen" \
 "$ROOT/src/main.c" "$ROOT/src/generator_core.c" \
 "$ROOT/src/acoustic_probe_macos.c" "$ROOT/src/output_hard_denied.c" \
 "$ROOT/src/em_backend.c" -framework CoreAudio -lm
UNDEFINED="$(nm -u "$WORK/freqmed-gen")" || { echo "R3_SYMBOL_AUDIT_FAILED=BLOCK" >&2;exit 8; }
if printf '%s\n' "$UNDEFINED" | grep -Eq '_(AudioQueueStart|AudioQueueNewOutput|AudioDeviceStart|AudioObjectSetPropertyData|AudioQueueEnqueueBuffer|AudioUnitRender|AudioOutputUnitStart)($|[^A-Za-z])'; then
 echo "R3_FORBIDDEN_EMISSION_SYMBOL=BLOCK" >&2;exit 8
fi
echo "R3_EXECUTABLE_EMISSION_SYMBOL_GUARD=PASS"
case "$MODE" in
 selftest)
  "$WORK/freqmed-gen" selftest
  (cd "$ROOT" && FREQMED_GEN_R1_BINARY="$WORK/freqmed-gen" FREQMED_GEN_R2_BINARY="$WORK/freqmed-gen" FREQMED_GEN_R3_BINARY="$WORK/freqmed-gen" python3 -B -m unittest discover -s tests -v)
  "$WORK/freqmed-gen" status ;;
 probe)
  "$WORK/freqmed-gen" probe
  "$WORK/freqmed-gen" status ;;
 status) "$WORK/freqmed-gen" status ;;
esac
printf '%s\n' 'R3_REAL_ACOUSTIC_OUTPUT=NONE; R3_EM_OUTPUT=NONE; SCIENTIFIC_SIMULATION=NONE; PRODUCTION=NOT_AUTHORIZED'
