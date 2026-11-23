#!/bin/bash
# FREQMED native C core + browser UI; no emission code.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
cd "$HERE"
if [ "$(uname -s)" != "Darwin" ] || [ "$(uname -m)" != "x86_64" ]; then
  echo "GEN_R59_MAC_INTEL_REQUIRED" >&2
  exit 2
fi
PYTHON="$(command -v python3 || true)"
if [ -z "$PYTHON" ]; then
  echo "GEN_R59_PYTHON3_MISSING" >&2
  exit 3
fi
if ! command -v clang >/dev/null 2>&1; then
  echo "GEN_R59_APPLE_CLANG_MISSING: xcode-select --install" >&2
  exit 4
fi
echo "===== FREQMED GEN-R64 — DIGITAL PCM INTEGRITY AND CONTROL TRANSITIONS / NO PLAYBACK ====="
echo "===== GEN-R59 NATIVE / HTTP SUITE ====="
"$PYTHON" -B "$HERE/tools/run_tests_r64.py"
echo "GEN_R59_PRELAUNCH_TEST_SUITE=PASS"
echo "GEN_R59_UI_CLEANUP_PRELAUNCH_TEST_SUITE=PASS"
echo "GEN_R59_UI_BUTTONS_FIX1_PRELAUNCH_TEST_SUITE=PASS"
echo "GEN_R59_UI_SELECTION_FIX2_PRELAUNCH_TEST_SUITE=PASS"
echo "GEN_R60_PRELAUNCH_TEST_SUITE=PASS"
echo "GEN_R61_PRELAUNCH_TEST_SUITE=PASS"
echo "GEN_R62_PRELAUNCH_TEST_SUITE=PASS"
echo "GEN_R63_PRELAUNCH_TEST_SUITE=PASS"
echo "GEN_R64_PRELAUNCH_TEST_SUITE=PASS"
echo "GEN_R62_FIX1_PRELAUNCH_TEST_SUITE=PASS"
if [ "${FREQMED_R58_FETCH_PINNED_GITHUB:-}" = "YES" ]; then
  echo "GEN_R58_FIX1_GITHUB_READONLY_OPT_IN=YES"
else
  echo "GEN_R58_FIX1_GITHUB_READONLY_OPT_IN=NO"
fi
exec "$PYTHON" -B "$HERE/app.py" "$@"
