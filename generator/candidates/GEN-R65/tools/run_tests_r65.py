#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""GEN-R65 deterministic isolated test runner: do not share mutable test globals.

Only fixed, locally committed unittest modules are executed. No fake device,
no network/OS hardware output and no external test dependencies.
"""
from __future__ import annotations
import pathlib
from concurrent.futures import ThreadPoolExecutor
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
TESTS = sorted(path.name for path in (ROOT / "tests").glob("test_*.py"))
if not TESTS or len(TESTS) != 20:
    raise SystemExit(f"GEN_R65_UNEXPECTED_TEST_MODULES={len(TESTS)}")
def run_module(name):
    cmd = [sys.executable, "-B", "-m", "unittest", "discover", "-s", "tests", "-p", name, "-q"]
    try:
        result = subprocess.run(cmd, cwd=ROOT, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, text=True, timeout=120, check=False)
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("GEN_R65_TEST_TIMEOUT=" + name) from exc
    if result.returncode != 0:
        raise RuntimeError("GEN_R65_TEST_FAILED=" + name + "\n" + result.stdout)
    match = re.search(r"^Ran (\d+) tests? in ", result.stdout, re.M)
    if not match or "FAILED" in result.stdout or not re.search(
            r"^OK(?: \(skipped=\d+\))?\s*$", result.stdout, re.M):
        raise RuntimeError("GEN_R65_TEST_REPORT_UNVERIFIED=" + name + "\n" + result.stdout)
    skip = re.search(r"^OK \(skipped=(\d+)\)", result.stdout, re.M)
    return name, int(match.group(1)), int(skip.group(1)) if skip else 0

# Each test module runs in a separate Python process and temporary native build.
# Concurrency is bounded to 4 processes and reporting stays deterministic.
count = 0
skipped = 0
with ThreadPoolExecutor(max_workers=4) as pool:
    for name, passed, omitted in pool.map(run_module, TESTS):
        count += passed
        skipped += omitted
        print(f"GEN_R65_TEST_MODULE={name} TESTS={passed} SKIPPED={omitted} PASS", flush=True)
if count != 692:
    raise SystemExit(f"GEN_R65_TEST_COUNT_MISMATCH={count}_EXPECTED_R65")
print(f"GEN_R65_SOFTWARE_TESTS={count}_SUCCESS_SKIPPED_{skipped}", flush=True)
