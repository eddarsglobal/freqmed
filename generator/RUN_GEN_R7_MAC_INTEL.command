#!/bin/bash
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "$0")" && pwd -P)"
MODE="${1:-selftest}"
case "$MODE" in selftest|status|probe|em-discover) ;; *) echo 'R7_UNKNOWN_ACTION_BLOCK' >&2;exit 2;; esac
[ "$(uname -s)" = Darwin ] || { echo 'MACOS_REQUIRED' >&2;exit 3; }
[ "$(uname -m)" = x86_64 ] || { echo 'MAC_INTEL_REQUIRED' >&2;exit 3; }
(cd "$ROOT" && shasum -a 256 -c KIT_SHA256SUMS.txt)
command -v clang >/dev/null || { echo 'MISSING_CLANG' >&2;exit 4; }
command -v nm >/dev/null || { echo 'MISSING_NM' >&2;exit 4; }
command -v python3 >/dev/null || { echo 'MISSING_PYTHON3' >&2;exit 4; }
WORK="$(mktemp -d "$HOME/Downloads/FREQMED_GEN_R7_NATIVE_XXXXXX")"
# Actual acoustic CoreAudio backend and EM command contract remain source-only.
for name in acoustic_macos acoustic_route_guard_macos acoustic_device_pin_macos; do
  clang -arch x86_64 -std=c11 -O2 -Wall -Wextra -Werror -c \
    "$ROOT/src/$name.c" -o "$WORK/$name.isolated.o"
  test -s "$WORK/$name.isolated.o"
done
clang -arch x86_64 -std=c11 -O2 -Wall -Wextra -Werror -c \
  -I"$ROOT/src" "$ROOT/src/em_device_contract.c" \
  -o "$WORK/em_contract.isolated.o"
test -s "$WORK/em_contract.isolated.o"
echo 'R7_FOUR_OUTPUT_BACKEND_OBJECTS=COMPILED_NOT_LINKED'
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
UNDEFINED="$(nm -u "$WORK/freqmed-gen")" || { echo 'R7_NM_UNAVAILABLE=BLOCK' >&2;exit 8; }
if printf '%s\n' "$UNDEFINED" | grep -Eq '_(AudioQueueStart|AudioQueueNewOutput|AudioQueueSetProperty|AudioDeviceStart|AudioObjectSetPropertyData|AudioQueueEnqueueBuffer|AudioUnitRender|AudioOutputUnitStart|IOServiceOpen|IORegistryEntrySetCFProperty|IORegistryEntrySetCFProperties|USBDeviceOpen|open|write|connect)($|[^A-Za-z])'; then
 echo 'R7_FORBIDDEN_NATIVE_SYMBOL=BLOCK' >&2;exit 8
fi
ALL_SYMBOLS="$(nm "$WORK/freqmed-gen")" || { echo 'R7_NM_UNAVAILABLE=BLOCK' >&2;exit 8; }
if printf '%s\n' "$ALL_SYMBOLS" | grep -Eq '_(acoustic_output_impl|fm_acoustic_bind_queue_to_route|fm_route_capture|fm_route_unchanged|fm_em_check_setpoint|fm_em_try_physical_emission)($|[^A-Za-z])'; then
 echo 'R7_OUTPUT_BACKEND_LINKED=BLOCK' >&2;exit 8
fi
echo 'R7_READONLY_DISCOVERY_BINARY_SYMBOL_AUDIT=PASS'
case "$MODE" in
 selftest)
  "$WORK/freqmed-gen" selftest
  (cd "$ROOT" && FREQMED_GEN_R1_BINARY="$WORK/freqmed-gen" \
    FREQMED_GEN_R2_BINARY="$WORK/freqmed-gen" FREQMED_GEN_R3_BINARY="$WORK/freqmed-gen" \
    FREQMED_GEN_R4_BINARY="$WORK/freqmed-gen" FREQMED_GEN_R5_BINARY="$WORK/freqmed-gen" \
    FREQMED_GEN_R6_BINARY="$WORK/freqmed-gen" FREQMED_GEN_R7_BINARY="$WORK/freqmed-gen" \
    python3 -B -m unittest discover -s tests -p 'test_*.py' -v)
  "$WORK/freqmed-gen" status ;;
 status) "$WORK/freqmed-gen" status ;;
 probe) "$WORK/freqmed-gen" probe ;;
 em-discover) "$WORK/freqmed-gen" em-discover ;;
esac
printf '%s\n' 'GEN_R7_EM_HARDWARE=READ_ONLY_REGISTRY; INSTRUMENT_CLAIMS=NONE; ACOUSTIC_EMISSION=NONE; EM_EMISSION=NONE; SCIENTIFIC_SIMULATION=NONE; PRODUCTION=NOT_AUTHORIZED'
