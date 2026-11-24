#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Build the pure integration candidate from exact historical Git blobs.
No network, device discovery, hardware I/O, or physical simulation."""
import hashlib
import json
import pathlib
import subprocess
import sys
import tempfile

AC = "54fd4e6cd4a8106da12bb57fa8208ce569a4185b"
EM = "0412c0fbe2b54298a3b1dd346c78d3b56dda0e63"
PINS = [
    (AC, "GEN-R66", "generator.h", "9839f4390d9f17560cf6ef2447501a314f335773"),
    (AC, "GEN-R66", "generator_core.c", "80f35f7ec323a658699929a717d6d16ef74a3144"),
    (AC, "GEN-R66", "output_hard_denied.c", "715b0981fb961b180df9e9dcf508a7608a224270"),
    (EM, "GEN-EM-01", "em_device_contract.h", "d577e6c0f96fed003f767ee62ca74ff14e8ab69d"),
    (EM, "GEN-EM-01", "em_device_contract.c", "f09603278215d960f9c7df5cc1aa812bffe0d365"),
]
def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: qualify.py REPO")
    repo = pathlib.Path(sys.argv[1]).resolve(strict=True)
    own = pathlib.Path(__file__).resolve().parent
    with tempfile.TemporaryDirectory(prefix="freqmed_int01_") as tmp:
        work = pathlib.Path(tmp)
        for ref, folder, name, expected in PINS:
            obj = ref + ":generator/candidates/" + folder + "/native/" + name
            data = subprocess.check_output(["git", "-C", str(repo), "show", obj])
            blob = hashlib.sha1(("blob %d" % len(data)).encode() + bytes([0]) + data).hexdigest()
            if blob != expected:
                raise SystemExit("SOURCE_PIN_MISMATCH: " + name)
            (work / name).write_bytes(data)
        exe = work / "test_integration"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-pedantic", "-I", str(work), "-I", str(own),
                        str(own / "integration.c"), str(own / "test_integration.c"),
                        str(work / "generator_core.c"), str(work / "output_hard_denied.c"),
                        str(work / "em_device_contract.c"), "-lm", "-o", str(exe)], check=True)
        result = subprocess.check_output([str(exe)], text=True).strip()
        if result != "GEN_INTEGRATION_01_ASSERTIONS=23 PASS":
            raise SystemExit("UNEXPECTED_TEST_RESULT: " + result)
        print(result)
        print("BUREAU_REPORT=" + json.dumps({
            "verdict": "PASS_SOFTWARE_ONLY", "source_pins_verified": len(PINS),
            "assertions": 23, "physical_output": "NOT_PERFORMED",
            "physical_measurement": "NOT_PERFORMED",
            "certification": "NOT_ISSUED", "authorization": "NONE"
        }, sort_keys=True))
if __name__ == "__main__":
    main()
