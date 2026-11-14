#!/bin/bash
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "$0")" && pwd -P)"
MODE="selftest"
if [ "$#" -gt 0 ]; then MODE="$1"; fi
case "$MODE" in selftest|status) ;; *) echo "REFUSED_UNKNOWN_COMMAND" >&2;exit 2;; esac
[ "$(uname -s)" = "Darwin" ] || { echo "MACOS_REQUIRED" >&2;exit 3; }
[ "$(uname -m)" = "x86_64" ] || { echo "MAC_INTEL_REQUIRED" >&2;exit 3; }
if [ -f "$ROOT/KIT_SHA256SUMS.txt" ]; then
  (cd "$ROOT" && shasum -a 256 -c KIT_SHA256SUMS.txt)
fi
command -v clang >/dev/null || { echo "MISSING_CLANG_NO_INSTALL" >&2;exit 4; }
command -v python3 >/dev/null || { echo "MISSING_PYTHON3_NO_INSTALL" >&2;exit 4; }
WORK="$(mktemp -d "$HOME/Downloads/FREQMED_GEN_R1_BUILD_XXXXXX")"
clang -arch x86_64 -std=c11 -O2 -Wall -Wextra -Werror -Wno-unused-function \
  -o "$WORK/freqmed-gen" \
  "$ROOT/src/main.c" "$ROOT/src/generator_core.c" \
  "$ROOT/src/acoustic_macos.c" "$ROOT/src/em_backend.c" \
  -framework AudioToolbox -framework CoreFoundation -lm
if [ "$MODE" = selftest ]; then
  "$WORK/freqmed-gen" selftest
  (cd "$ROOT" && FREQMED_GEN_R1_BINARY="$WORK/freqmed-gen" python3 -B -m unittest discover -s tests -v)
fi
"$WORK/freqmed-gen" status
printf '%s\n' 'REAL_OUTPUT=NONE; EM_OUTPUT=NONE; NO_SIMULATION=ENFORCED; PRODUCTION=NOT_AUTHORIZED'
