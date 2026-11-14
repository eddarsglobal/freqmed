#!/bin/bash
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "$0")" && pwd -P)"
MODE="selftest"
if [ "$#" -gt 0 ]; then MODE="$1"; fi
case "$MODE" in selftest|status|probe) ;; *) echo "REFUSED_UNKNOWN_COMMAND" >&2;exit 2;; esac
[ "$(uname -s)" = Darwin ] || { echo "MACOS_REQUIRED" >&2;exit 3; }
[ "$(uname -m)" = x86_64 ] || { echo "MAC_INTEL_REQUIRED" >&2;exit 3; }
(cd "$ROOT" && shasum -a 256 -c KIT_SHA256SUMS.txt)
command -v clang >/dev/null || { echo "MISSING_CLANG_NO_INSTALL" >&2;exit 4; }
command -v python3 >/dev/null || { echo "MISSING_PYTHON3_NO_INSTALL" >&2;exit 4; }
WORK="$(mktemp -d "$HOME/Downloads/FREQMED_GEN_R2_BUILD_XXXXXX")"
# Note: The CoreAudio emission translation unit is intentionally NOT linked.
clang -arch x86_64 -std=c11 -O2 -Wall -Wextra -Werror \
  -o "$WORK/freqmed-gen" \
  "$ROOT/src/main.c" "$ROOT/src/generator_core.c" \
  "$ROOT/src/acoustic_probe_macos.c" "$ROOT/src/output_hard_denied.c" \
  "$ROOT/src/em_backend.c" -framework CoreAudio -lm
# Symbol-level verification that the binary has no playback/start API imports.
NM_UNDEFINED="$(nm -u "$WORK/freqmed-gen")" || { echo "R2_SYMBOL_AUDIT_UNAVAILABLE=BLOCK" >&2; exit 8; }
if printf '%s\n' "$NM_UNDEFINED" | grep -Eq '_(AudioQueueStart|AudioQueueNewOutput|AudioDeviceStart|AudioObjectSetPropertyData|AudioQueueEnqueueBuffer|AudioUnitRender|AudioOutputUnitStart)($|[^A-Za-z])'; then
  echo "R2_FORBIDDEN_OUTPUT_SYMBOL_PRESENT=BLOCK" >&2
  exit 8
fi
echo "R2_NATIVE_OUTPUT_SYMBOL_GUARD=PASS"
case "$MODE" in
selftest)
  "$WORK/freqmed-gen" selftest
  (cd "$ROOT" && FREQMED_GEN_R1_BINARY="$WORK/freqmed-gen" FREQMED_GEN_R2_BINARY="$WORK/freqmed-gen" python3 -B -m unittest discover -s tests -v)
  "$WORK/freqmed-gen" status
  ;;
probe)
  "$WORK/freqmed-gen" probe
  "$WORK/freqmed-gen" status
  ;;
status)
  "$WORK/freqmed-gen" status
  ;;
esac
printf '%s\n' 'ACOUSTIC_OUTPUT=NOT_LINKED; EM_OUTPUT=BLOCKED; NETWORK=NONE; MICROPHONE=NONE; PRODUCTION=NOT_AUTHORIZED'
