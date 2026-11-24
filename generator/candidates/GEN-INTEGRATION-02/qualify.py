#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Offline C11 qualification. No physical I/O or simulation."""
import hashlib
import json
import os
import pathlib
import platform
import subprocess
import sys
import tempfile

AC = "54fd4e6cd4a8106da12bb57fa8208ce569a4185b"
EM = "0412c0fbe2b54298a3b1dd346c78d3b56dda0e63"
INT = "d4ae3fa35412595a194c5f7c323cefb169722d19"
PINS = [
    (AC, "GEN-R66/native/generator.h", "9839f4390d9f17560cf6ef2447501a314f335773"),
    (AC, "GEN-R66/native/generator_core.c", "80f35f7ec323a658699929a717d6d16ef74a3144"),
    (AC, "GEN-R66/native/output_hard_denied.c", "715b0981fb961b180df9e9dcf508a7608a224270"),
    (EM, "GEN-EM-01/native/em_device_contract.h", "d577e6c0f96fed003f767ee62ca74ff14e8ab69d"),
    (EM, "GEN-EM-01/native/em_device_contract.c", "f09603278215d960f9c7df5cc1aa812bffe0d365"),
    (INT, "GEN-INTEGRATION-01/integration.h", "490b09c4acb96ac9e857a6a55324c28c91c14f1f"),
    (INT, "GEN-INTEGRATION-01/integration.c", "c7fc2c90ea4b64aa5a5c9f25e0b202991b01b627"),
    (INT, "GEN-INTEGRATION-01/test_integration.c", "631aef08ca9e52ecbb24f6b067d35fe3de7a7b41"),
]
def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: qualify.py REPO")
    system = platform.system()
    if system not in ("Darwin", "Linux", "Windows"):
        raise SystemExit("UNSUPPORTED_PLATFORM")
    repo = pathlib.Path(sys.argv[1]).resolve(strict=True)
    own = pathlib.Path(__file__).resolve().parent
    cc = os.environ.get("CC", "gcc" if system == "Windows" else "cc")
    with tempfile.TemporaryDirectory(prefix="freqmed_int02_") as tmp:
        work = pathlib.Path(tmp)
        for ref, path, expected in PINS:
            data = subprocess.check_output(["git", "-C", str(repo), "show",
                ref + ":generator/candidates/" + path])
            digest = hashlib.sha1(("blob %d" % len(data)).encode() + bytes([0]) + data).hexdigest()
            if digest != expected:
                raise SystemExit("SOURCE_PIN_MISMATCH: " + path)
            (work / pathlib.Path(path).name).write_bytes(data)
        common = [str(work / name) for name in ("generator_core.c", "output_hard_denied.c",
                  "em_device_contract.c", "integration.c")]
        suites = [
            ("regression", [str(work / "test_integration.c")], "GEN_INTEGRATION_01_ASSERTIONS=23 PASS"),
            ("session", [str(own / "session.c"), str(own / "test_session.c")],
             "GEN_INTEGRATION_02_ASSERTIONS=38 PASS"),
            ("clock", [str(own / "session.c"), str(own / "session_clock.c"), str(own / "test_clock.c")],
             "GEN_INTEGRATION_02_CLOCK_ASSERTIONS=9 PASS"),
        ]
        for name, sources, expected in suites:
            exe = work / (name + (".exe" if system == "Windows" else ""))
            subprocess.run([cc, "-std=c11", "-Wall", "-Wextra", "-Werror", "-pedantic",
                            "-I", str(work), "-I", str(own), *common, *sources,
                            "-lm", "-o", str(exe)], check=True)
            actual = subprocess.check_output([str(exe)], text=True).strip()
            if actual != expected:
                raise SystemExit("UNEXPECTED_RESULT: " + actual)
            print(actual, flush=True)
        print("BUREAU_REPORT=" + json.dumps({
            "schema":"freqmed.gen-integration-02.v1", "platform":system,
            "machine":platform.machine(), "source_pins_verified":len(PINS),
            "regression_assertions":23, "session_assertions":38, "clock_assertions":9,
            "assertions":70, "verdict":"PASS_SOFTWARE_ONLY", "physical_output":"NOT_PERFORMED",
            "physical_measurement":"NOT_PERFORMED", "certification":"NOT_ISSUED",
            "authorization":"NONE"
        },sort_keys=True))
if __name__ == "__main__":
    main()
