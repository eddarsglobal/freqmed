#!/bin/bash
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "$0")" && pwd -P)"
MODE="${1:-selftest}"
case "$MODE" in selftest|status|probe) ;; *) echo 'R4_UNKNOWN_ACTION_BLOCK' >&2;exit 2;; esac
[ "$(uname -s)" = Darwin ] || { echo 'MACOS_REQUIRED' >&2;exit 3; }
[ "$(uname -m)" = x86_64 ] || { echo 'MAC_INTEL_REQUIRED' >&2;exit 3; }
(cd "$ROOT" && shasum -a 256 -c KIT_SHA256SUMS.txt)
command -v clang >/dev/null || { echo 'MISSING_CLANG' >&2;exit 4; }
command -v nm >/dev/null || { echo 'MISSING_NM' >&2;exit 4; }
command -v python3 >/dev/null || { echo 'MISSING_PYTHON3' >&2;exit 4; }
WORK="$(mktemp -d "$HOME/Downloads/FREQMED_GEN_R4_NATIVE_XXXXXX")"
# Compile-only: real CoreAudio output backend and default-route guard.
# Neither is linked, loaded or executed by the R4 command-line program.
clang -arch x86_64 -std=c11 -O2 -Wall -Wextra -Werror -c \
 "$ROOT/src/acoustic_macos.c" -o "$WORK/acoustic_output_isolated.o"
clang -arch x86_64 -std=c11 -O2 -Wall -Wextra -Werror -c \
 "$ROOT/src/acoustic_route_guard_macos.c" -o "$WORK/acoustic_route_isolated.o"
test -s "$WORK/acoustic_output_isolated.o"
test -s "$WORK/acoustic_route_isolated.o"
echo 'R4_NATIVE_BACKEND_AND_ROUTE_COMPILE=PASS; OUTPUT_OBJECTS=ISOLATED'
# Separately link ONLY the previously proven read-only and hard-denied code.
clang -arch x86_64 -std=c11 -O2 -Wall -Wextra -Werror \
 -o "$WORK/freqmed-gen" \
 "$ROOT/src/main.c" "$ROOT/src/generator_core.c" \
 "$ROOT/src/acoustic_probe_macos.c" "$ROOT/src/output_hard_denied.c" \
 "$ROOT/src/em_backend.c" -framework CoreAudio -lm
UNDEFINED="$(nm -u "$WORK/freqmed-gen")" || { echo 'R4_SYMBOL_AUDIT_UNAVAILABLE=BLOCK' >&2;exit 8; }
if printf '%s\n' "$UNDEFINED" | grep -Eq '_(AudioQueueStart|AudioQueueNewOutput|AudioDeviceStart|AudioObjectSetPropertyData|AudioQueueEnqueueBuffer|AudioUnitRender|AudioOutputUnitStart)($|[^A-Za-z])'; then
 echo 'R4_FORBIDDEN_OUTPUT_SYMBOL=BLOCK' >&2;exit 8
fi
echo 'R4_EXECUTABLE_OUTPUT_SYMBOL_AUDIT=PASS'
case "$MODE" in
  selftest)
   "$WORK/freqmed-gen" selftest
   (cd "$ROOT" && FREQMED_GEN_R1_BINARY="$WORK/freqmed-gen" FREQMED_GEN_R2_BINARY="$WORK/freqmed-gen" FREQMED_GEN_R3_BINARY="$WORK/freqmed-gen" FREQMED_GEN_R4_BINARY="$WORK/freqmed-gen" python3 -B -m unittest discover -s tests -v)
   "$WORK/freqmed-gen" status
   ;;
  status) "$WORK/freqmed-gen" status ;;
  probe) "$WORK/freqmed-gen" probe; "$WORK/freqmed-gen" status ;;
esac
printf '%s\n' 'R4_ACOUSTIC_EMISSION=NONE; R4_EM_EMISSION=NONE; SCIENTIFIC_SIMULATION=NONE; PRODUCTION=NOT_AUTHORIZED'
