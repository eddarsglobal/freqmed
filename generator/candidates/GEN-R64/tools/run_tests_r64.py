#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""GEN-R64 deterministic isolated test runner: do not share mutable test globals.

Only fixed, locally committed unittest modules are executed. No fake device,
no network/OS hardware output and no external test dependencies.
"""
from __future__ import annotations
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
TESTS = sorted(path.name for path in (ROOT / "tests").glob("test_*.py"))
if not TESTS or len(TESTS) != 19:
    raise SystemExit(f"GEN_R64_UNEXPECTED_TEST_MODULES={len(TESTS)}")
count = 0
skipped = 0
for name in TESTS:
    cmd = [sys.executable, "-B", "-m", "unittest", "discover", "-s", "tests", "-p", name, "-q"]
    try:
        completed = subprocess.run(cmd, cwd=ROOT, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT, text=True, timeout=90, check=False)
    except subprocess.TimeoutExpired as exc:
        raise SystemExit("GEN_R64_TEST_TIMEOUT=" + name) from exc
    # Print all failure details instead of a false overall green status.
    if completed.returncode != 0:
        sys.stdout.write(completed.stdout)
        raise SystemExit("GEN_R64_TEST_FAILED=" + name)
    match = re.search(r"^Ran (\d+) tests? in ", completed.stdout, re.M)
    if not match or "FAILED" in completed.stdout or not re.search(r"^OK(?: \(skipped=\d+\))?\s*$", completed.stdout, re.M):
        sys.stdout.write(completed.stdout)
        raise SystemExit("GEN_R64_TEST_REPORT_UNVERIFIED=" + name)
    total = int(match.group(1))
    skips = re.search(r"^OK \(skipped=(\d+)\)", completed.stdout, re.M)
    count += total
    skipped += int(skips.group(1)) if skips else 0
    print(f"GEN_R64_TEST_MODULE={name} TESTS={total} SKIPPED={int(skips.group(1)) if skips else 0} PASS", flush=True)
if count != 642:
    raise SystemExit(f"GEN_R64_TEST_COUNT_MISMATCH={count}_EXPECTED_642")
print(f"GEN_R64_SOFTWARE_TESTS={count}_SUCCESS_SKIPPED_{skipped}", flush=True)
