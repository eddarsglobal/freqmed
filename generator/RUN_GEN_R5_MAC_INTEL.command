#!/bin/bash
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "$0")" && pwd -P)"
MODE="${1:-selftest}"
case "$MODE" in selftest|status|probe) ;; *) echo 'R5_UNKNOWN_ACTION_BLOCK' >&2;exit 2;; esac
[ "$(uname -s)" = Darwin ] || { echo 'MACOS_REQUIRED' >&2;exit 3; }
[ "$(uname -m)" = x86_64 ] || { echo 'MAC_INTEL_REQUIRED' >&2;exit 3; }
(cd "$ROOT" && shasum -a 256 -c KIT_SHA256SUMS.txt)
command -v clang >/dev/null || { echo 'MISSING_CLANG' >&2;exit 4; }
command -v nm >/dev/null || { echo 'MISSING_NM' >&2;exit 4; }
command -v python3 >/dev/null || { echo 'MISSING_PYTHON3' >&2;exit 4; }
WORK="$(mktemp -d "$HOME/Downloads/FREQMED_GEN_R5_NATIVE_XXXXXX")"
# Compile real CoreAudio backend, route guard and device pin independently.
# These three objects are NEVER linked into the runnable no-output program.
for name in acoustic_macos acoustic_route_guard_macos acoustic_device_pin_macos; do
  clang -arch x86_64 -std=c11 -O2 -Wall -Wextra -Werror -c \
    "$ROOT/src/$name.c" -o "$WORK/$name.isolated.o"
  test -s "$WORK/$name.isolated.o"
done
echo 'R5_NATIVE_THREE_COREAUDIO_OBJECTS_COMPILE=PASS; OBJECTS=ISOLATED'
# Executable: OS audio read-only metadata and hard-denied public outputs ONLY.
clang -arch x86_64 -std=c11 -O2 -Wall -Wextra -Werror \
 -o "$WORK/freqmed-gen" \
 "$ROOT/src/main.c" "$ROOT/src/generator_core.c" \
 "$ROOT/src/acoustic_probe_macos.c" "$ROOT/src/output_hard_denied.c" \
 "$ROOT/src/em_backend.c" -framework CoreAudio -lm
UNDEFINED="$(nm -u "$WORK/freqmed-gen")" || { echo 'R5_SYMBOL_AUDIT_UNAVAILABLE=BLOCK' >&2;exit 8; }
if printf '%s\n' "$UNDEFINED" | grep -Eq '_(AudioQueueStart|AudioQueueNewOutput|AudioQueueSetProperty|AudioDeviceStart|AudioObjectSetPropertyData|AudioQueueEnqueueBuffer|AudioUnitRender|AudioOutputUnitStart)($|[^A-Za-z])'; then
 echo 'R5_FORBIDDEN_OUTPUT_SYMBOL=BLOCK' >&2;exit 8
fi
# Inspect all linked symbols too, so an accidentally statically-linked output
# function cannot be mistaken for successful isolation.
ALL_SYMBOLS="$(nm "$WORK/freqmed-gen")" || { echo 'R5_SYMBOL_AUDIT_UNAVAILABLE=BLOCK' >&2;exit 8; }
if printf '%s\n' "$ALL_SYMBOLS" | grep -Eq '_(acoustic_output_impl|fm_acoustic_bind_queue_to_route|fm_route_capture|fm_route_unchanged)($|[^A-Za-z])'; then
 echo 'R5_ISOLATION_SYMBOL_PRESENT=BLOCK' >&2;exit 8
fi
echo 'R5_EXECUTABLE_NO_OUTPUT_SYMBOL_AUDIT=PASS'
case "$MODE" in
 selftest)
  "$WORK/freqmed-gen" selftest
  (cd "$ROOT" && FREQMED_GEN_R1_BINARY="$WORK/freqmed-gen" FREQMED_GEN_R2_BINARY="$WORK/freqmed-gen" FREQMED_GEN_R3_BINARY="$WORK/freqmed-gen" FREQMED_GEN_R4_BINARY="$WORK/freqmed-gen" FREQMED_GEN_R5_BINARY="$WORK/freqmed-gen" python3 -B -m unittest discover -s tests -v)
  "$WORK/freqmed-gen" status ;;
 status) "$WORK/freqmed-gen" status ;;
 probe) "$WORK/freqmed-gen" probe; "$WORK/freqmed-gen" status ;;
esac
printf '%s\n' 'R5_ACOUSTIC_EMISSION=NONE; R5_EM_EMISSION=NONE; SCIENTIFIC_SIMULATION=NONE; PRODUCTION=NOT_AUTHORIZED'
