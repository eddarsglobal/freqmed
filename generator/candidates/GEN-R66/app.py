#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""FREQMED R55: real C core + local macOS hardware metadata + GUI, with no output API.

This application MUST NOT be described as a physical generator. The compiled
C Guardian is hard-locked; code for CoreAudio emission and EM instrument driving
is deliberately absent. No simulated physical readings are generated.
"""
from __future__ import annotations

import argparse
import importlib.util
import ctypes
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import math
import os
from pathlib import Path
import secrets
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent
NATIVE = ROOT / "native"
STATIC = ROOT / "static"
HISTORICAL = ROOT / "historical" / "FREQMED_V5_DIRECT.html"
STATE_NAMES = {0: "OFF", 1: "BLOCKED", 2: "PREPARED", 3: "ARMED", 4: "ACTIVE", 5: "FAULT"}


class FMCommand(ctypes.Structure):
    _fields_ = [("channel", ctypes.c_int), ("frequency_hz", ctypes.c_double),
                ("normalized_level", ctypes.c_double), ("duration_ms", ctypes.c_uint)]


class FMGuardian(ctypes.Structure):
    _fields_ = [("state", ctypes.c_int), ("hardware_profile_certified", ctypes.c_int),
                ("safety_review_certified", ctypes.c_int), ("bench_authorized", ctypes.c_int),
                ("physical_output_enabled", ctypes.c_int)]


class FMOutputCapabilities(ctypes.Structure):
    _fields_ = [("output_channels", ctypes.c_uint), ("nominal_sample_rate_hz", ctypes.c_double),
                ("metadata_observed", ctypes.c_int)]


class FMNativeAudioDevice(ctypes.Structure):
    _fields_ = [("device_id", ctypes.c_uint32), ("output_channels", ctypes.c_uint32),
                ("nominal_rate_hz", ctypes.c_double), ("is_default", ctypes.c_int32),
                ("name", ctypes.c_char * 128)]


class FMNativeAudioSnapshot(ctypes.Structure):
    _fields_ = [("count", ctypes.c_uint32), ("truncated", ctypes.c_int32),
                ("devices", FMNativeAudioDevice * 32)]


class FMAcousticPreflight(ctypes.Structure):
    _fields_ = [("result_code", ctypes.c_int32), ("device_id", ctypes.c_uint32),
                ("channels", ctypes.c_uint32), ("os_rate_hz", ctypes.c_double),
                ("requested_hz", ctypes.c_double), ("duration_ms", ctypes.c_uint32),
                ("digital_frame_count", ctypes.c_uint64)]

class FMR57BackendRouteCheck(ctypes.Structure):
    _fields_ = [("result_code", ctypes.c_int32), ("default_route_matches", ctypes.c_uint32),
                ("nominal_rate_hz", ctypes.c_double), ("digital_frame_budget", ctypes.c_uint64)]

class FMR59Session(ctypes.Structure):
    _fields_ = [("phase", ctypes.c_uint32), ("reason", ctypes.c_uint32),
                ("device_id", ctypes.c_uint32), ("channels", ctypes.c_uint32),
                ("sample_rate_hz", ctypes.c_double), ("command", FMCommand),
                ("digital_frame_budget", ctypes.c_uint64), ("name", ctypes.c_char * 128)]

class FMR60Lease(ctypes.Structure):
    _fields_ = [("state", ctypes.c_uint32), ("reason", ctypes.c_uint32),
                ("generation", ctypes.c_uint64), ("verified_at_ns", ctypes.c_uint64),
                ("expires_at_ns", ctypes.c_uint64), ("bound", FMR59Session)]

class FMR61Fault(ctypes.Structure):
    _fields_ = [("state", ctypes.c_uint32), ("reason", ctypes.c_uint32),
                ("fault_sequence", ctypes.c_uint64)]

class FMR63DigitalReport(ctypes.Structure):
    _fields_ = [("frames", ctypes.c_uint64), ("samples", ctypes.c_uint64),
                ("channels", ctypes.c_uint32), ("digital_peak_normalized", ctypes.c_float)]


class FMR64DigitalIntegrity(ctypes.Structure):
    _fields_ = [("checked_samples", ctypes.c_uint64),
                ("channels", ctypes.c_uint32),
                ("digital_peak_normalized", ctypes.c_float),
                ("zero_edges", ctypes.c_uint32)]


class FMR65Cursor(ctypes.Structure):
    _fields_ = [("contract", FMR59Session), ("next_frame", ctypes.c_uint64),
                ("digital_peak_normalized", ctypes.c_float), ("state", ctypes.c_uint32)]


class FMR65ChunkReport(ctypes.Structure):
    _fields_ = [("start_frame", ctypes.c_uint64), ("frames", ctypes.c_uint64),
                ("samples", ctypes.c_uint64), ("channels", ctypes.c_uint32),
                ("chunk_digital_peak", ctypes.c_float), ("zero_edges_verified", ctypes.c_uint32)]


class FMR66Audit(ctypes.Structure):
    _fields_ = [("expected_frames", ctypes.c_uint64),
                ("checked_frames", ctypes.c_uint64),
                ("checked_samples", ctypes.c_uint64),
                ("channels", ctypes.c_uint32),
                ("segments", ctypes.c_uint32),
                ("state", ctypes.c_uint32),
                ("observed_digital_peak", ctypes.c_float)]


class FMR62Identity(ctypes.Structure):
    _fields_ = [("state", ctypes.c_uint32), ("reason", ctypes.c_uint32),
                ("sequence", ctypes.c_uint64), ("device_id", ctypes.c_uint32),
                ("channels", ctypes.c_uint32), ("sample_rate_hz", ctypes.c_double),
                ("command", FMCommand), ("name", ctypes.c_char * 128),
                ("os_uid", ctypes.c_char * 256)]

R62_STATES = {0: "UNBOUND", 1: "PINNED_NO_EMISSION", 2: "INVALIDATED", 3: "STOPPED"}
R62_REASONS = {0: "NONE", 1: "OS_UNAVAILABLE", 2: "OS_IDENTITY_CHANGED",
               3: "SESSION_CHANGED", 4: "EXPLICIT_RESET", 5: "OPERATOR_STOP"}

R61_STATES = {0: "NORMAL_NO_OUTPUT", 1: "FAULT_LATCHED", 2: "STOPPED"}
R61_REASONS = {0: "NONE", 1: "OS_UNAVAILABLE", 2: "ROUTE_MISMATCH",
               3: "NATIVE_SESSION_INVALID", 4: "CONTROL_LEASE_EXPIRED",
               5: "CONTROL_INTEGRITY", 6: "OPERATOR_STOP"}

R60_STATES = {0: "UNBOUND", 1: "CONTROL_LEASE_VALID_NO_EMISSION",
              2: "REVOKED", 3: "EXPIRED", 4: "STOPPED"}
R60_REASONS = {0: "NONE", 1: "NOT_BOUND", 2: "SESSION_CHANGED",
               3: "WATCHDOG_STALE", 4: "ROUTE_RESET", 5: "OPERATOR_STOP",
               6: "CLOCK_FAILURE", 7: "MONITOR_UNAVAILABLE"}

R59_PHASES = {0: "UNBOUND", 1: "ROUTE_VERIFIED_NO_EMISSION",
              2: "INVALIDATED", 3: "STOPPED"}
R59_REASONS = {0: "NONE", 1: "NOT_READY", 2: "INVALID_ARGUMENT",
               3: "ROUTE_OR_COMMAND_MISMATCH", 4: "OS_CHANGED_OR_UNAVAILABLE",
               5: "OPERATOR_STOP", 6: "ROUTE_RESET"}


class FMR58CandidateEvidence(ctypes.Structure):
    _fields_ = [("abi_version", ctypes.c_uint32), ("original_candidate_compiled", ctypes.c_uint32),
                ("macos_backend_declared", ctypes.c_uint32), ("emitter_entrypoint_denied", ctypes.c_uint32)]


def load_candidate_source_module():
    spec = importlib.util.spec_from_file_location("freqmed_r58_sources", ROOT / "candidate_source_r58.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


R57_RESULTS = {1: "DEFAULT_ROUTE_MATCHED_BACKEND_SOURCE_ONLY",
               2: "INVALID_ACOUSTIC_COMMAND", 3: "SELECTED_ROUTE_CHANGED_OR_MISSING",
               4: "COREAUDIO_OS_UNAVAILABLE", 5: "DIGITAL_NYQUIST_EXCEEDED",
               6: "FRAME_BUDGET_EXCEEDED", 7: "INVALID_ROUTE_METADATA",
               8: "SELECTED_OUTPUT_IS_NOT_MACOS_DEFAULT", 9: "DEFAULT_ROUTE_CHANGED_OR_CAPABILITIES_MISMATCH"}

R56_RESULT = {1: "OS_ROUTE_AND_DIGITAL_ENVELOPE_MATCHED_NOT_AUTHORIZED",
              2: "INVALID_ACOUSTIC_COMMAND", 3: "SELECTED_ROUTE_CHANGED_OR_MISSING",
              4: "COREAUDIO_OS_UNAVAILABLE", 5: "FREQUENCY_EXCEEDS_DIGITAL_NYQUIST",
              6: "DIGITAL_FRAME_ENVELOPE_EXCEEDED", 7: "INVALID_ROUTE_METADATA"}


def verify_manifest():
    path = ROOT / "SHA256SUMS.txt"
    if not path.is_file():
        raise RuntimeError("KIT_MANIFEST_MISSING")
    entries = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        digest, sep, relative = line.partition("  ")
        if sep != "  " or len(digest) != 64 or not all(c in "0123456789abcdef" for c in digest):
            raise RuntimeError("KIT_MANIFEST_INVALID")
        p = Path(relative)
        if p.is_absolute() or ".." in p.parts or relative in entries or not relative:
            raise RuntimeError("KIT_PATH_INVALID_OR_DUPLICATED")
        entries.add(relative)
        dest = ROOT / p
        if dest.is_symlink() or not dest.is_file() or hashlib.sha256(dest.read_bytes()).hexdigest() != digest:
            raise RuntimeError("KIT_HASH_MISMATCH:" + relative)
    expected = {str(p.relative_to(ROOT)) for subdir in ["native", "static", "historical", "tests", "tools"]
                for p in (ROOT/subdir).rglob("*") if p.is_file() and "__pycache__" not in p.parts}
    expected.update({"app.py", "RUN_GEN_R66_MAC_INTEL.command", "SYNC_R66_GITHUB_MAC_INTEL.command", "README_FR.md", "PROVENANCE.md", "BUREAU_GEN_R65_REPORT.md", "BUREAU_GEN_R66_REPORT.md", "SOURCE_PINS_R58.json", "candidate_source_r58.py"})
    if entries != expected:
        raise RuntimeError("KIT_MANIFEST_INCOMPLETE_OR_EXTRA")
    return len(entries)


class NativeCore:
    def __init__(self, builddir: Path):
        clang = shutil.which("clang") or shutil.which("cc")
        if not clang:
            raise RuntimeError("CLANG_MISSING_INSTALL_APPLE_COMMAND_LINE_TOOLS")
        if sys.platform == "darwin":
            dylib = builddir / "libfreqmed_r54.dylib"
            args = [clang, "-std=c11", "-O2", "-fPIC", "-dynamiclib", "-Wall", "-Wextra",
                    "-Werror", "-o", str(dylib), str(NATIVE/"generator_core.c"),
                    str(NATIVE/"acoustic_probe_macos.c"), str(NATIVE/"audio_devices_macos.c"), str(NATIVE/"acoustic_preflight_r56.c"), str(NATIVE/"acoustic_backend_route_r57.c"), str(NATIVE/"acoustic_session_r59.c"), str(NATIVE/"acoustic_control_lease_r60.c"), str(NATIVE/"acoustic_fault_latch_r61.c"), str(NATIVE/"acoustic_identity_r62.c"), str(NATIVE/"acoustic_pcm_r63.c"), str(NATIVE/"acoustic_integrity_r64.c"), str(NATIVE/"acoustic_segment_r65.c"), str(NATIVE/"acoustic_sequence_audit_r66.c"), str(NATIVE/"output_hard_denied.c"),
                    "-framework", "CoreAudio", "-framework", "CoreFoundation", "-lm"]
        elif sys.platform.startswith("linux"):
            # Linux can execute only the portable C tests. Audio probe returns unavailable.
            dylib = builddir / "libfreqmed_r54.so"
            args = [clang, "-std=c11", "-O2", "-fPIC", "-shared", "-Wall", "-Wextra",
                    "-Werror", "-o", str(dylib), str(NATIVE/"generator_core.c"),
                    str(NATIVE/"acoustic_probe_macos.c"), str(NATIVE/"audio_devices_macos.c"), str(NATIVE/"acoustic_preflight_r56.c"), str(NATIVE/"acoustic_backend_route_r57.c"), str(NATIVE/"acoustic_session_r59.c"), str(NATIVE/"acoustic_control_lease_r60.c"), str(NATIVE/"acoustic_fault_latch_r61.c"), str(NATIVE/"acoustic_identity_r62.c"), str(NATIVE/"acoustic_pcm_r63.c"), str(NATIVE/"acoustic_integrity_r64.c"), str(NATIVE/"acoustic_segment_r65.c"), str(NATIVE/"acoustic_sequence_audit_r66.c"), str(NATIVE/"output_hard_denied.c"), "-lm"]
        else:
            raise RuntimeError("UNSUPPORTED_OS_MAC_INTEL_REQUIRED")
        result = subprocess.run(args, cwd=str(ROOT), capture_output=True, text=True, timeout=35, check=False)
        if result.returncode:
            raise RuntimeError("NATIVE_C_COMPILE_FAILED:" + result.stderr[-2000:])
        self.lib = ctypes.CDLL(str(dylib))
        self.lib.fm_validate_command.argtypes = [ctypes.POINTER(FMCommand), ctypes.c_void_p, ctypes.c_size_t]
        self.lib.fm_validate_command.restype = ctypes.c_int
        self.lib.fm_guardian_transition.argtypes = [ctypes.POINTER(FMGuardian), ctypes.POINTER(FMCommand), ctypes.c_void_p, ctypes.c_size_t]
        self.lib.fm_guardian_transition.restype = ctypes.c_int
        self.lib.fm_stop.argtypes = [ctypes.POINTER(FMGuardian)]
        self.lib.fm_stop.restype = None
        self.lib.fm_acoustic_readonly_probe.argtypes = [ctypes.POINTER(FMOutputCapabilities)]
        self.lib.fm_acoustic_readonly_probe.restype = ctypes.c_int
        self.lib.fm_acoustic_native_backend_available.restype = ctypes.c_int
        self.lib.fm_em_backend_available.restype = ctypes.c_int
        self.lib.fm_acoustic_physical_output.argtypes = [ctypes.POINTER(FMCommand)]
        self.lib.fm_acoustic_physical_output.restype = ctypes.c_int
        self.lib.fm_em_physical_output.argtypes = [ctypes.POINTER(FMCommand)]
        self.lib.fm_em_physical_output.restype = ctypes.c_int
        self.lib.fm_list_acoustic_outputs.argtypes = [ctypes.POINTER(FMNativeAudioSnapshot)]
        self.lib.fm_list_acoustic_outputs.restype = ctypes.c_int
        self.lib.fm_r56_acoustic_preflight.argtypes = [ctypes.POINTER(FMCommand), ctypes.c_uint32,
            ctypes.c_char_p, ctypes.c_uint32, ctypes.c_double, ctypes.POINTER(FMAcousticPreflight)]
        self.lib.fm_r56_acoustic_preflight.restype = ctypes.c_int
        self.lib.fm_r57_backend_route_check.argtypes = [ctypes.POINTER(FMCommand), ctypes.c_uint32,
            ctypes.c_char_p, ctypes.c_uint32, ctypes.c_double, ctypes.POINTER(FMR57BackendRouteCheck)]
        self.lib.fm_r57_backend_route_check.restype = ctypes.c_int
        self.lib.fm_r59_session_bind.argtypes = [ctypes.POINTER(FMR59Session), ctypes.POINTER(FMCommand),
            ctypes.c_uint32, ctypes.c_char_p, ctypes.c_uint32, ctypes.c_double]
        self.lib.fm_r59_session_bind.restype = ctypes.c_int
        self.lib.fm_r59_session_poll.argtypes = [ctypes.POINTER(FMR59Session)]
        self.lib.fm_r59_session_poll.restype = ctypes.c_int
        self.lib.fm_r59_session_invalidate.argtypes = [ctypes.POINTER(FMR59Session)]
        self.lib.fm_r59_session_invalidate.restype = None
        self.lib.fm_r59_session_stop.argtypes = [ctypes.POINTER(FMR59Session)]
        self.lib.fm_r59_session_stop.restype = None
        self.lib.fm_r60_lease_begin.argtypes = [ctypes.POINTER(FMR60Lease), ctypes.POINTER(FMR59Session)]
        self.lib.fm_r60_lease_begin.restype = ctypes.c_int
        self.lib.fm_r60_lease_renew.argtypes = [ctypes.POINTER(FMR60Lease), ctypes.POINTER(FMR59Session)]
        self.lib.fm_r60_lease_renew.restype = ctypes.c_int
        self.lib.fm_r60_lease_check.argtypes = [ctypes.POINTER(FMR60Lease), ctypes.POINTER(FMR59Session)]
        self.lib.fm_r60_lease_check.restype = ctypes.c_int
        self.lib.fm_r60_lease_revoke.argtypes = [ctypes.POINTER(FMR60Lease), ctypes.c_uint32]
        self.lib.fm_r60_lease_revoke.restype = None
        self.lib.fm_r60_lease_stop.argtypes = [ctypes.POINTER(FMR60Lease)]
        self.lib.fm_r60_lease_stop.restype = None
        self.lib.fm_r61_fault_trip.argtypes = [ctypes.POINTER(FMR61Fault), ctypes.c_uint32]
        self.lib.fm_r61_fault_trip.restype = ctypes.c_int
        self.lib.fm_r61_fault_stop.argtypes = [ctypes.POINTER(FMR61Fault)]
        self.lib.fm_r61_fault_stop.restype = None
        self.lib.fm_r61_fault_resume_observation.argtypes = [ctypes.POINTER(FMR61Fault)]
        self.lib.fm_r61_fault_resume_observation.restype = ctypes.c_int
        self.lib.fm_r61_fault_ack.argtypes = [ctypes.POINTER(FMR61Fault), ctypes.c_int,
                                             ctypes.c_int, ctypes.c_int]
        self.lib.fm_r61_fault_ack.restype = ctypes.c_int
        self.lib.fm_r61_fault_can_bind.argtypes = [ctypes.POINTER(FMR61Fault)]
        self.lib.fm_r61_fault_can_bind.restype = ctypes.c_int
        self.lib.fm_r63_render_digital_pcm.argtypes = [ctypes.POINTER(FMR59Session),
            ctypes.POINTER(ctypes.c_float), ctypes.c_uint64, ctypes.POINTER(FMR63DigitalReport)]
        self.lib.fm_r63_render_digital_pcm.restype = ctypes.c_int
        self.lib.fm_r63_zeroize_digital_pcm.argtypes = [ctypes.POINTER(ctypes.c_float), ctypes.c_uint64]
        self.lib.fm_r63_zeroize_digital_pcm.restype = None
        self.lib.fm_r64_verify_digital_pcm.argtypes = [ctypes.POINTER(ctypes.c_float),
                ctypes.c_uint64, ctypes.c_uint32, ctypes.c_float,
                ctypes.POINTER(FMR64DigitalIntegrity)]
        self.lib.fm_r64_verify_digital_pcm.restype = ctypes.c_int
        self.lib.fm_r65_stream_begin.argtypes = [ctypes.POINTER(FMR65Cursor), ctypes.POINTER(FMR59Session)]
        self.lib.fm_r65_stream_begin.restype = ctypes.c_int
        self.lib.fm_r65_stream_next.argtypes = [ctypes.POINTER(FMR65Cursor), ctypes.POINTER(FMR59Session),
                        ctypes.POINTER(ctypes.c_float), ctypes.c_uint64,
                        ctypes.POINTER(FMR65ChunkReport)]
        self.lib.fm_r65_stream_next.restype = ctypes.c_int
        self.lib.fm_r65_stream_clear.argtypes = [ctypes.POINTER(FMR65Cursor)]
        self.lib.fm_r65_stream_clear.restype = None
        self.lib.fm_r66_audit_begin.argtypes = [ctypes.POINTER(FMR66Audit),
                                                 ctypes.c_uint64, ctypes.c_uint32]
        self.lib.fm_r66_audit_begin.restype = ctypes.c_int
        self.lib.fm_r66_audit_chunk.argtypes = [ctypes.POINTER(FMR66Audit),
                                                 ctypes.POINTER(FMR65ChunkReport),
                                                 ctypes.POINTER(ctypes.c_float), ctypes.c_uint64]
        self.lib.fm_r66_audit_chunk.restype = ctypes.c_int
        self.lib.fm_r66_audit_finish.argtypes = [ctypes.POINTER(FMR66Audit)]
        self.lib.fm_r66_audit_finish.restype = ctypes.c_int
        self.lib.fm_r66_audit_clear.argtypes = [ctypes.POINTER(FMR66Audit)]
        self.lib.fm_r66_audit_clear.restype = None
        self.lib.fm_r62_identity_pin.argtypes = [ctypes.POINTER(FMR62Identity), ctypes.POINTER(FMR59Session)]
        self.lib.fm_r62_identity_pin.restype = ctypes.c_int
        self.lib.fm_r62_identity_check.argtypes = [ctypes.POINTER(FMR62Identity), ctypes.POINTER(FMR59Session)]
        self.lib.fm_r62_identity_check.restype = ctypes.c_int
        self.lib.fm_r62_identity_invalidate.argtypes = [ctypes.POINTER(FMR62Identity), ctypes.c_uint32]
        self.lib.fm_r62_identity_invalidate.restype = None
        self.lib.fm_r62_identity_stop.argtypes = [ctypes.POINTER(FMR62Identity)]
        self.lib.fm_r62_identity_stop.restype = None
        self.builddir = builddir
        self.r58_candidate = None
        self.r58_evidence = None
        self.r58_candidate_error = 'NOT_LOADED'
        self.guardian = FMGuardian(0, 0, 0, 0, 0)
        self.lock = threading.Lock()
        self.last = None
        self.route = None
        self.r56_preflight = None
        self.r57_backend = None
        self.r59_session = FMR59Session()
        self.r60_lease = FMR60Lease()
        self.r61_fault = FMR61Fault()
        self.r62_identity = FMR62Identity()
        self.r59_candidate_epoch = 0
        self.audit = []
        # GEN-R55: observe the actual OS registry periodically. A probe is
        # never a physical safety interlock or device-UID authentication.
        self.route_monitor_ticks = 0
        self.route_monitor_ever_observed = False
        self.route_monitor_last = "NOT_CHECKED"
        self.route_monitor_event = "NO_SELECTION"
        self.route_monitor_event_seq = 0
        self._monitor_shutdown = threading.Event()
        self._monitor_thread = None
        # Independent binary gate: no physical output is linked, no alternative unlock flag.
        if self.lib.fm_acoustic_native_backend_available() != 0 or self.lib.fm_em_backend_available() != 0:
            raise RuntimeError("FATAL_OUTPUT_BACKEND_NOT_DENIED")
        assert self.lib.fm_acoustic_physical_output(None) != 0
        assert self.lib.fm_em_physical_output(None) != 0

    def status(self):
        with self.lock:
            g = STATE_NAMES.get(self.guardian.state, "FAULT")
            last = self.last
        return {"schema": "freqmed.gen-r54.local-ui.v1", "native_c_compiled_and_loaded": True,
                "guardian_state": g, "last_command": last,
                "selected_acoustic_route": self.get_route_status(),
                "route_monitor": self.route_monitor_status(),
                "acoustic_preflight": self.get_acoustic_preflight_status(),
                "acoustic_backend_contract": self.get_r57_backend_status(),
                "acoustic_candidate_r58": self.candidate_status(),
                "acoustic_session_r59": self.get_r59_session_status(),
                "acoustic_control_r60": self.get_r60_control_status(),
                "acoustic_fault_r61": self.get_r61_fault_status(),
                "acoustic_identity_r62": self.get_r62_identity_status(),
                "acoustic_output": "NOT_LINKED_HARD_DENIED", "em_output": "NO_DRIVER_HARD_DENIED",
                "physical_emission": "NONE_BY_THIS_APPLICATION", "simulation": "NONE",
                "production": "NOT_AUTHORIZED", "p001": "IN_PROGRESS_REBASE_REVIEW",
                "note": "Software integration and OS metadata; not physical metrology or certification."}

    def _r64_retire_previous_binding_locked(self, reason=4):
        """Clear only existing native control contracts; never invent a prior lease.

        First route selection or first command edit starts with native UNBOUND.
        Replaced active/expired contracts remain invalidated fail-closed.
        STOPPED is sticky until explicit OS monitor resume and a new native bind.
        Must be called under self.lock, never alters the R61 fault latch.
        """
        if self.r59_session.phase != 3:
            self.lib.fm_r59_session_invalidate(ctypes.byref(self.r59_session))
        if self.r62_identity.state not in (0, 3):
            self.lib.fm_r62_identity_invalidate(ctypes.byref(self.r62_identity), reason)
        if self.r60_lease.state not in (0, 4):
            self.lib.fm_r60_lease_revoke(ctypes.byref(self.r60_lease), reason)

    def _r61_trip_locked(self, reason, event):
        """Under self.lock only. Native fault latch is sticky across STOP."""
        self.lib.fm_r61_fault_trip(ctypes.byref(self.r61_fault), reason)
        self.lib.fm_stop(ctypes.byref(self.guardian))
        self.route = None
        self.last = None
        self.r56_preflight = None
        self.r57_backend = None
        self.lib.fm_r59_session_invalidate(ctypes.byref(self.r59_session))
        self.lib.fm_r62_identity_invalidate(ctypes.byref(self.r62_identity), 4)
        self.lib.fm_r60_lease_revoke(ctypes.byref(self.r60_lease), 4)
        self.route_monitor_event = event
        self.route_monitor_event_seq += 1
        self.audit = (self.audit + [{"action": "r61_fault_latched",
                                     "reason": R61_REASONS.get(int(self.r61_fault.reason), "UNKNOWN")}])[-12:]

    def _r61_status_locked(self):
        f = self.r61_fault
        return {"state": R61_STATES.get(int(f.state), "FAULT_LATCHED"),
                "reason": R61_REASONS.get(int(f.reason), "CONTROL_INTEGRITY"),
                "fault_latched": bool(f.state == 1),
                "can_bind": bool(self.lib.fm_r61_fault_can_bind(ctypes.byref(f))),
                "fault_sequence": int(f.fault_sequence),
                "ack_requires": "ROUTE_CLEAR_SESSION_CLEAR_OS_MONITOR_LIVE",
                "physical_output": "HARD_DENIED", "physical_interlock": "NONE_NOT_CERTIFIED"}

    def _r62_status_locked(self):
        p = self.r62_identity
        return {"state": R62_STATES.get(int(p.state), "INVALIDATED"),
                "reason": R62_REASONS.get(int(p.reason), "OS_UNAVAILABLE"),
                "os_uid_private_not_disclosed": True,
                "identity_confirmed_now": bool(p.state == 1),
                "sequence": int(p.sequence),
                "physical_output": "HARD_DENIED", "playback": "NOT_PERFORMED",
                "note": "MacOS OS-provided device UID only; not hardware trust or metrology."}

    def _r62_check_locked(self):
        if self.r62_identity.state != 1:
            return False
        if self._monitor_shutdown.is_set() or self.route is None or self.r59_session.phase != 1:
            self.lib.fm_r62_identity_invalidate(ctypes.byref(self.r62_identity), 4)
            return False
        if self.lib.fm_r62_identity_check(ctypes.byref(self.r62_identity),
                                           ctypes.byref(self.r59_session)) != 1:
            # This read-only OS identity mismatch is a sticky native control fault.
            self._r61_trip_locked(5, "R62_FAULT_COREAUDIO_IDENTITY_MISMATCH")
            return False
        return True

    def get_r62_identity_status(self):
        with self.lock:
            self._r62_check_locked()
            return self._r62_status_locked()

    def get_r61_fault_status(self):
        with self.lock:
            return self._r61_status_locked()

    def acknowledge_r61_fault(self):
        """Operator-only, session authenticated. No arming, output or automatic rebind."""
        # Reconfirm the real CoreAudio registry outside the lock: no stale
        # monitor flag, cached UI value or fabricated device can clear a fault.
        try:
            fresh_os = self._snapshot()
        except Exception:
            fresh_os = None
        if fresh_os is None or fresh_os.get("truncated", True):
            raise ValueError("R61_REAL_COREAUDIO_RECOVERY_NOT_CONFIRMED")
        with self.lock:
            if self.r61_fault.state != 1:
                raise ValueError("NO_LATCHED_FAULT_TO_ACKNOWLEDGE")
            if self.route is not None or self.r59_session.phase == 1:
                raise ValueError("R61_CLEAR_ROUTE_AND_SESSION_FIRST")
            if self._monitor_shutdown.is_set() or not (self._monitor_thread and self._monitor_thread.is_alive()):
                raise ValueError("R61_RESUME_REAL_OS_MONITOR_FIRST")
            if self.lib.fm_r61_fault_ack(ctypes.byref(self.r61_fault), 1, 1, 1) != 1:
                raise ValueError("R61_NATIVE_ACK_DENIED")
            self.route_monitor_event = "R61_OPERATOR_FAULT_ACKNOWLEDGED"
            self.route_monitor_event_seq += 1
            self.audit = (self.audit + [{"action": "r61_operator_fault_ack"}])[-12:]
            return self._r61_status_locked()

    def validate(self, payload):
        if not isinstance(payload, dict) or set(payload) != {"channel", "hz", "level", "duration_ms"}:
            raise ValueError("INVALID_COMMAND_SCHEMA")
        if payload["channel"] not in ("acoustic", "em"):
            raise ValueError("UNKNOWN_CHANNEL")
        # bool is int in Python; refuse it as a frequency or duration.
        vals = [payload[k] for k in ("hz", "level", "duration_ms")]
        if any(type(v) not in (float, int) for v in vals):
            raise ValueError("INVALID_NUMERIC_TYPE")
        hz, level, duration = vals
        if not (math.isfinite(hz) and math.isfinite(level)):
            raise ValueError("NONFINITE_NUMERIC_INPUT")
        if type(duration) is not int or not (0 <= duration <= 4294967295):
            raise ValueError("INVALID_DURATION_RANGE")
        cmd = FMCommand(1 if payload["channel"] == "acoustic" else 2, float(hz), float(level), duration)
        buff = ctypes.create_string_buffer(128)
        with self.lock:
            structurally_valid = bool(self.lib.fm_validate_command(ctypes.byref(cmd), buff, len(buff)))
            structural_reason = buff.value.decode("ascii", "replace")
            buff = ctypes.create_string_buffer(128)
            guardian_authorized = bool(self.lib.fm_guardian_transition(ctypes.byref(self.guardian), ctypes.byref(cmd), buff, len(buff)))
            guardian_reason = buff.value.decode("ascii", "replace")
            # Any new command makes a previous digital route preparation stale.
            self.r56_preflight = None
            self.r57_backend = None
            self._r64_retire_previous_binding_locked()
            self.last = {"channel": payload["channel"], "hz": hz, "level": level,
                         "duration_ms": duration, "structure_valid": structurally_valid}
            g = STATE_NAMES.get(self.guardian.state, "FAULT")
            self.audit = (self.audit + [{"action": "validate", "channel": payload["channel"],
                                          "structurally_valid": structurally_valid,
                                          "guardian_state": g}])[-12:]
        return {"structurally_valid": structurally_valid, "structural_reason": structural_reason,
                "guardian_authorized": guardian_authorized, "guardian_reason": guardian_reason,
                "guardian_state": g, "physical_output": "BLOCKED", "native_c_executed": True}

    def stop(self):
        # GEN-R55 explicit software stop: native C fm_stop + discard selected
        # route. This is NOT an independent physical safety disconnect.
        with self.lock:
            self.lib.fm_stop(ctypes.byref(self.guardian))
            self.last = None
            self.route = None
            self.r56_preflight = None
            self.r57_backend = None
            self.lib.fm_r59_session_stop(ctypes.byref(self.r59_session))
            self.lib.fm_r62_identity_stop(ctypes.byref(self.r62_identity))
            self.lib.fm_r60_lease_stop(ctypes.byref(self.r60_lease))
            # Guardian reset is not a monitor STOP. Keep the fault latch as-is;
            # never strand a healthy session in STOPPED while monitoring runs.
            self.route_monitor_event = "OPERATOR_SOFTWARE_STOP"
            self.route_monitor_event_seq += 1
            self.audit = (self.audit + [{"action": "software_stop", "guardian_state": "OFF"}])[-12:]
        return {"guardian_state": "OFF", "physical_output": "NONE_BY_DESIGN",
                "route_selected": False, "software_stop": "EXECUTED_NATIVE_FM_STOP",
                "note": "Software Guardian and route reset; NOT a physical emergency cutoff."}

    def _snapshot(self):
        snap = FMNativeAudioSnapshot()
        success = self.lib.fm_list_acoustic_outputs(ctypes.byref(snap)) == 0
        if not success or snap.count > 32:
            return None
        results = []
        for dev in list(snap.devices)[:snap.count]:
            results.append({"device_id": int(dev.device_id), "channels": int(dev.output_channels),
                            "nominal_sample_rate_hz": float(dev.nominal_rate_hz),
                            "is_default": bool(dev.is_default),
                            "name": bytes(dev.name).split(b"\0",1)[0].decode("utf-8", "replace")})
        return {"observed": True, "devices": results, "truncated": bool(snap.truncated)}

    @staticmethod
    def _route_matches_snapshot(route, snapshot):
        # Compare actual OS observations, never a fabricated device record.
        if snapshot is None or snapshot.get("truncated", False):
            return False
        return any(dev["device_id"] == route["device_id"] and
                   dev["name"] == route["name"] and
                   dev["channels"] == route["channels"] and
                   dev["nominal_sample_rate_hz"] == route["nominal_sample_rate_hz"]
                   for dev in snapshot["devices"])

    def route_watch_tick(self):
        """One real read-only CoreAudio registry poll, no sound or EM access.

        If a selected route is missing/changed/OS-unobservable, clear the
        selection and reset the native software Guardian immediately.
        """
        # Never poll or count with no operator-confirmed output route.
        # The discovery dropdown uses separate, one-shot CoreAudio reads.
        with self.lock:
            if self._monitor_shutdown.is_set() or self.route is None:
                return self._route_monitor_status_locked()
        try:
            snapshot = self._snapshot()
        except Exception:
            # Fail closed on OS/FFI exceptions; never invent a measurement.
            snapshot = None
        observed = snapshot is not None
        with self.lock:
            # A concurrent STOP/clear cannot publish an in-flight OS result.
            if self._monitor_shutdown.is_set() or self.route is None:
                return self._route_monitor_status_locked()
            self.route_monitor_ticks += 1
            self.route_monitor_ever_observed |= observed
            self.route_monitor_last = "COREAUDIO_OBSERVED" if observed else "COREAUDIO_UNAVAILABLE"
            route = dict(self.route) if self.route is not None else None
            if route is None:
                return self._route_monitor_status_locked()
            if self._route_matches_snapshot(route, snapshot):
                if self.r59_session.phase == 1:
                    if not self._r62_check_locked():
                        self._r61_trip_locked(5, "R62_FAULT_DEVICE_IDENTITY_OS_CHECK")
                    elif self.lib.fm_r59_session_poll(ctypes.byref(self.r59_session)) != 1:
                        self._r61_trip_locked(3, "R61_FAULT_NATIVE_SESSION_OS_RECHECK")
                    elif self.lib.fm_r60_lease_renew(ctypes.byref(self.r60_lease),
                                                     ctypes.byref(self.r59_session)) != 1:
                        self._r61_trip_locked(4, "R61_FAULT_CONTROL_LEASE_EXPIRED")
                    else:
                        self.route_monitor_event = "SELECTED_ROUTE_METADATA_MATCHES_OS"
                else:
                    self.route_monitor_event = "SELECTED_ROUTE_METADATA_MATCHES_OS"
            else:
                self._r61_trip_locked(1 if snapshot is None else 2,
                    "R61_FAULT_OS_UNAVAILABLE" if snapshot is None else
                    "R61_FAULT_ROUTE_CHANGED_OR_MISSING")
            return self._route_monitor_status_locked()

    def _route_monitor_status_locked(self):
        active_thread = bool(self._monitor_thread and self._monitor_thread.is_alive())
        monitor_state = ("STOPPING" if self._monitor_shutdown.is_set() and active_thread
                         else "STOPPED" if self._monitor_shutdown.is_set()
                         else "IDLE" if self.route is None or not active_thread
                         else "RUNNING")
        return {"checks": self.route_monitor_ticks,
                "monitor_state": monitor_state,
                "monitor_running": monitor_state == "RUNNING",
                "last_os_poll": self.route_monitor_last,
                "ever_observed_real_os": self.route_monitor_ever_observed,
                "selected": self.route is not None,
                "event": self.route_monitor_event,
                "event_sequence": self.route_monitor_event_seq,
                "physical_stop_capability": "NONE_NOT_AN_INTERLOCK",
                "physical_emission": "NOT_POSSIBLE_IN_THIS_BUILD"}

    def route_monitor_status(self):
        with self.lock:
            return self._route_monitor_status_locked()

    def start_route_monitor(self, interval_seconds=1.2):
        if not 0.5 <= interval_seconds <= 10.0:
            raise ValueError("MONITOR_INTERVAL_OUT_OF_RANGE")
        with self.lock:
            if self._monitor_thread and self._monitor_thread.is_alive():
                return False
            self._monitor_shutdown.clear()
            def run():
                # One immediate OS observation; periodic interval avoids
                # high frequency or uncontrolled device access.
                while not self._monitor_shutdown.is_set():
                    self.route_watch_tick()
                    if self._monitor_shutdown.wait(interval_seconds):
                        break
            self._monitor_thread = threading.Thread(target=run, daemon=True,
                                                    name="FREQMED-R56-READONLY-ROUTE-WATCH")
            thread = self._monitor_thread
        thread.start()
        return True

    def stop_route_monitor(self):
        self._monitor_shutdown.set()
        with self.lock:
            thread = self._monitor_thread
        if thread and thread is not threading.current_thread():
            thread.join(timeout=3)
        return thread is None or not thread.is_alive()

    def stop_engine_and_monitor(self):
        """Operator STOP: native C stop, route cleared, periodic OS work stopped.

        A running CoreAudio query may finish after the stop request, but its
        result cannot increment the counter or update route state. No hardware
        cutoff or physical emission capability is claimed.
        """
        with self.lock:
            self._monitor_shutdown.set()
            self.lib.fm_stop(ctypes.byref(self.guardian))
            self.last = None
            self.route = None
            self.r56_preflight = None
            self.r57_backend = None
            self.lib.fm_r59_session_stop(ctypes.byref(self.r59_session))
            self.lib.fm_r62_identity_stop(ctypes.byref(self.r62_identity))
            self.lib.fm_r60_lease_stop(ctypes.byref(self.r60_lease))
            self.lib.fm_r61_fault_stop(ctypes.byref(self.r61_fault))
            self.route_monitor_event = "OPERATOR_SOFTWARE_STOP_MONITOR_STOPPED"
            self.route_monitor_event_seq += 1
            self.audit = (self.audit + [{"action": "software_stop_monitor_stop",
                                         "guardian_state": "OFF"}])[-12:]
            thread = self._monitor_thread
        # Never join while holding self.lock: the observer needs it to exit.
        if thread and thread is not threading.current_thread():
            thread.join(timeout=3)
        state = self.route_monitor_status()
        return {"guardian_state": "OFF", "physical_output": "NONE_BY_DESIGN",
                "route_selected": False, "software_stop": "EXECUTED_NATIVE_FM_STOP",
                "monitor_state": state["monitor_state"],
                "monitor_running": False,
                "monitor_checks_frozen_at": state["checks"],
                "note": "Software motor and periodic observer stopped; NOT a physical emergency cutoff."}

    def resume_route_monitor(self):
        """Explicit operator re-enable of read-only OS observation only."""
        with self.lock:
            if not self._monitor_shutdown.is_set():
                raise ValueError("MONITOR_ALREADY_RUNNING")
            thread = self._monitor_thread
            if thread and thread.is_alive():
                raise ValueError("MONITOR_STOP_IN_PROGRESS")
            # The route stays cleared and Guardian stays OFF on resume.
            self.route_monitor_event = "OPERATOR_MONITOR_RESUMED"
            self.route_monitor_event_seq += 1
        if not self.start_route_monitor(interval_seconds=1.2):
            raise ValueError("MONITOR_RESUME_REFUSED")
        with self.lock:
            self.lib.fm_r61_fault_resume_observation(ctypes.byref(self.r61_fault))
        return self.route_monitor_status()

    def audio_devices(self):
        snap = self._snapshot()
        if snap is None:
            return {"observed": False, "devices": [], "selection": self.get_route_status(),
                    "reason": "COREAUDIO_ENUMERATION_UNAVAILABLE"}
        snap["selection"] = self.get_route_status(snapshot=snap)
        snap["note"] = "Live read-only CoreAudio device list. IDs are temporary; not qualified or calibrated."
        return snap

    def get_route_status(self, snapshot=None):
        with self.lock:
            route = dict(self.route) if self.route is not None else None
        if route is None:
            return {"selected": False, "verified_now": False, "reason": "NO_EXPLICIT_DEVICE_SELECTED"}
        if snapshot is None:
            snapshot = self._snapshot()
        if snapshot is None:
            return {"selected": True, "verified_now": False, "reason": "DEVICE_REGISTRY_UNAVAILABLE",
                    "device_id": route["device_id"]}
        for dev in snapshot["devices"]:
            if dev["device_id"] == route["device_id"] and dev["name"] == route["name"] and \
                    dev["channels"] == route["channels"] and \
                    dev["nominal_sample_rate_hz"] == route["nominal_sample_rate_hz"]:
                return {"selected": True, "verified_now": True, "reason": "MATCHED_LIVE_DEVICE_METADATA",
                        **route, "physical_output": "HARD_DENIED"}
        return {"selected": True, "verified_now": False, "reason": "SELECTED_ROUTE_CHANGED_OR_DISCONNECTED",
                "device_id": route["device_id"], "physical_output": "HARD_DENIED"}

    def select_audio(self, payload):
        if not isinstance(payload, dict) or set(payload) != {"device_id"} or \
                type(payload["device_id"]) is not int or not (0 < payload["device_id"] <= 4294967295):
            raise ValueError("INVALID_EPHEMERAL_AUDIO_DEVICE_ID")
        snap = self._snapshot()
        if snap is None:
            raise ValueError("COREAUDIO_ENUMERATION_UNAVAILABLE")
        if snap["truncated"]:
            raise ValueError("DEVICE_LIST_TRUNCATED_SELECTION_REFUSED")
        for dev in snap["devices"]:
            if dev["device_id"] == payload["device_id"]:
                with self.lock:
                    self.r56_preflight = None
                    self.r57_backend = None
                    self._r64_retire_previous_binding_locked()
                    self.route = {"device_id": dev["device_id"], "name": dev["name"],
                                  "channels": dev["channels"],
                                  "nominal_sample_rate_hz": dev["nominal_sample_rate_hz"]}
                    self.route_monitor_event = "DEVICE_SELECTED_AWAITING_NEXT_OS_WATCH"
                    self.route_monitor_event_seq += 1
                    self.audit = (self.audit + [{"action":"select_audio", "device_id":dev["device_id"]}])[-12:]
                # Start the background watcher only after an explicit OS route
                # selection. After operator STOP, an explicit Resume is still
                # required; selecting alone never defeats a STOP latch.
                if not self._monitor_shutdown.is_set():
                    self.start_route_monitor(interval_seconds=1.2)
                return self.get_route_status()
        raise ValueError("AUDIO_DEVICE_MISSING_OR_NOT_OUTPUT_CAPABLE")

    def clear_audio(self):
        with self.lock:
            self.route = None
            self.r56_preflight = None
            self.r57_backend = None
            self._r64_retire_previous_binding_locked()
            self.route_monitor_event = "OPERATOR_CLEARED_SELECTION"
            self.route_monitor_event_seq += 1
        return self.get_route_status()

    def get_acoustic_preflight_status(self):
        with self.lock:
            return dict(self.r56_preflight) if self.r56_preflight is not None else {
                "checked": False, "physical_output": "HARD_DENIED"}

    def acoustic_preflight(self, payload):
        """One real native C/CoreAudio command-to-device digital envelope check.

        Neither constructs PCM samples nor opens an output queue or arms Guardian.
        Preflight validity never means physical authorization or calibration.
        """
        if not isinstance(payload, dict) or set(payload) != {"channel", "hz", "level", "duration_ms"}:
            raise ValueError("INVALID_PREFLIGHT_SCHEMA")
        if payload["channel"] != "acoustic":
            raise ValueError("ONLY_ACOUSTIC_CHANNEL_SUPPORTED")
        if any(type(payload[k]) not in (float, int) for k in ("hz", "level")) or \
           type(payload["duration_ms"]) is not int:
            raise ValueError("INVALID_NUMERIC_TYPE")
        hz, level, duration = payload["hz"], payload["level"], payload["duration_ms"]
        if not math.isfinite(hz) or not math.isfinite(level) or not 0 <= duration <= 4294967295:
            raise ValueError("INVALID_NUMERIC_RANGE")
        with self.lock:
            self.r57_backend = None
            self._r64_retire_previous_binding_locked()
            if self._monitor_shutdown.is_set():
                raise ValueError("OS_MONITOR_STOPPED")
            selected = dict(self.route) if self.route is not None else None
        if selected is None:
            raise ValueError("SELECT_REAL_COREAUDIO_OUTPUT_FIRST")
        cmd = FMCommand(1, float(hz), float(level), duration)
        packet = FMAcousticPreflight()
        error = self.lib.fm_r56_acoustic_preflight(ctypes.byref(cmd),
            selected["device_id"], selected["name"].encode("utf-8"),
            selected["channels"], selected["nominal_sample_rate_hz"], ctypes.byref(packet))
        if error != 0:
            raise ValueError("NATIVE_ACOUSTIC_PREFLIGHT_ERROR")
        with self.lock:
            if self._monitor_shutdown.is_set() or self.route != selected:
                self.r56_preflight = None
                self.r57_backend = None
                raise ValueError("ROUTE_CHANGED_DURING_PREFLIGHT")
            result = {"checked": True,
                "native_c_coreaudio_executed": True,
                "digital_contract_valid": packet.result_code == 1,
                "result": R56_RESULT.get(packet.result_code,"NATIVE_UNEXPECTED_STATUS"),
                "device_id": selected["device_id"],
                "requested_hz": hz, "duration_ms": duration,
                "os_nominal_sample_rate_hz": packet.os_rate_hz if packet.result_code in (1,5,6) else None,
                "digital_frame_budget": packet.digital_frame_count if packet.result_code == 1 else None,
                "physical_output": "HARD_DENIED",
                "hardware_qualified": False, "physical_measurement": "NOT_PERFORMED",
                "scientific_simulation": "NONE"}
            self.r56_preflight = result
            self.audit = (self.audit + [{"action":"acoustic_preflight", "digital_valid":result["digital_contract_valid"]}])[-12:]
            return dict(result)

    def get_r57_backend_status(self):
        """Revalidate an actual CoreAudio default-route match on every read.

        A green GUI state is never a safety certificate and expires when OS
        or command changes. No output backend is loaded by this check.
        """
        with self.lock:
            stage = dict(self.r57_backend) if self.r57_backend else None
            selected = dict(self.route) if self.route else None
            stopped = self._monitor_shutdown.is_set()
        if stage is None:
            return {"checked": False, "physical_output": "HARD_DENIED", "backend_linked": False}
        if stopped or selected is None or selected != stage["route"]:
            with self.lock: self.r57_backend = None
            return {"checked": False, "reason": "ROUTE_OR_MONITOR_CHANGED", "physical_output": "HARD_DENIED", "backend_linked": False}
        packet = FMR57BackendRouteCheck()
        args = stage["command"]
        cmd = FMCommand(1, float(args["hz"]), float(args["level"]), int(args["duration_ms"]))
        rc = self.lib.fm_r57_backend_route_check(ctypes.byref(cmd), selected["device_id"],
             selected["name"].encode("utf-8"), selected["channels"],
             selected["nominal_sample_rate_hz"], ctypes.byref(packet))
        with self.lock:
            if self.r57_backend != stage or self.route != selected or self._monitor_shutdown.is_set():
                self.r57_backend = None
                return {"checked": False, "reason": "STATE_CHANGED_DURING_READ", "physical_output": "HARD_DENIED", "backend_linked": False}
            if rc != 0 or packet.result_code != 1:
                self.r57_backend = None
                return {"checked": False, "reason": R57_RESULTS.get(packet.result_code, "NATIVE_ERROR"), "physical_output": "HARD_DENIED", "backend_linked": False}
        return {"checked": True, "default_route_matches": True, "digital_frame_budget": int(packet.digital_frame_budget),
                "result": "DEFAULT_ROUTE_MATCHED_BACKEND_SOURCE_ONLY", "physical_output": "HARD_DENIED",
                "backend_linked": False, "physical_measurement": "NOT_PERFORMED", "hardware_qualified": False}

    def r57_backend_check(self, payload):
        """Native bridge contract for the source-only DEFAULT-route backend.

        Does not compile, link, load, invoke, arm or call a playback backend.
        C verifies current OS DEFAULT metadata independently of R56.
        """
        if not isinstance(payload,dict) or set(payload) != {"channel","hz","level","duration_ms"}:
            raise ValueError("INVALID_BACKEND_CONTRACT_SCHEMA")
        if payload["channel"] != "acoustic":
            raise ValueError("ONLY_ACOUSTIC_CHANNEL_SUPPORTED")
        if any(type(payload[k]) not in (float,int) for k in ("hz","level")) or type(payload["duration_ms"]) is not int:
            raise ValueError("INVALID_NUMERIC_TYPE")
        hz,level,duration=payload["hz"],payload["level"],payload["duration_ms"]
        if not math.isfinite(hz) or not math.isfinite(level) or not 0<=duration<=4294967295:
            raise ValueError("INVALID_NUMERIC_RANGE")
        with self.lock:
            self.r57_backend = None
            self._r64_retire_previous_binding_locked()
            if self._monitor_shutdown.is_set():
                raise ValueError("OS_MONITOR_STOPPED")
            selected=dict(self.route) if self.route else None
        if selected is None:
            raise ValueError("SELECT_REAL_COREAUDIO_OUTPUT_FIRST")
        cmd=FMCommand(1,float(hz),float(level),duration)
        result=FMR57BackendRouteCheck()
        rc=self.lib.fm_r57_backend_route_check(ctypes.byref(cmd),selected["device_id"],
            selected["name"].encode("utf-8"),selected["channels"],
            selected["nominal_sample_rate_hz"],ctypes.byref(result))
        if rc != 0: raise ValueError("R57_NATIVE_BACKEND_CONTRACT_ERROR")
        accepted=result.result_code==1
        with self.lock:
            if self._monitor_shutdown.is_set() or self.route != selected:
                self.r57_backend=None
                raise ValueError("ROUTE_CHANGED_DURING_BACKEND_CHECK")
            if accepted:
                self.r57_backend={"route":selected,"command":{"hz":hz,"level":level,"duration_ms":duration}}
        return {"checked": True,"route_contract_valid":accepted,
                "result":R57_RESULTS.get(result.result_code,"UNKNOWN_NATIVE_RESULT"),
                "default_route_matches":bool(result.default_route_matches),
                "digital_frame_budget":int(result.digital_frame_budget) if accepted else None,
                "os_nominal_sample_rate_hz":result.nominal_rate_hz if accepted else None,
                "backend_linked":False,"physical_output":"HARD_DENIED",
                "hardware_qualified":False,"physical_measurement":"NOT_PERFORMED", "scientific_simulation":"NONE"}

    def get_r59_session_status(self):
        """Return the native session phase, never a playback authorization.

        When the route is present and monitor live, this re-checks OS metadata
        through the native R57/CoreAudio contract. STOPPED is never reset by GET.
        """
        with self.lock:
            if self.r59_session.phase == 1:
                if self._monitor_shutdown.is_set() or self.route is None:
                    self.lib.fm_r59_session_invalidate(ctypes.byref(self.r59_session))
                    self.lib.fm_r62_identity_invalidate(ctypes.byref(self.r62_identity), 4)
                    self.lib.fm_r60_lease_revoke(ctypes.byref(self.r60_lease), 4)
                else:
                    if not self._r62_check_locked():
                        self._r61_trip_locked(5, "R62_FAULT_DEVICE_IDENTITY_READ_CHECK")
                    elif self.lib.fm_r59_session_poll(ctypes.byref(self.r59_session)) != 1:
                        self._r61_trip_locked(3, "R61_FAULT_NATIVE_SESSION_READ_CHECK")
            if self.r59_session.phase != 1 and self.r60_lease.state == 1:
                self.lib.fm_r60_lease_revoke(ctypes.byref(self.r60_lease), 2)
            session=self.r59_session
            return {"phase": R59_PHASES.get(int(session.phase),"INVALIDATED"),
                    "reason": R59_REASONS.get(int(session.reason),"UNKNOWN"),
                    "route_bound": bool(session.phase == 1),
                    "digital_frame_budget": int(session.digital_frame_budget) if session.phase == 1 else None,
                    "native_route_contract": "R56_AND_R57_REAL_COREAUDIO",
                    "candidate_isolated": self.r58_candidate is not None,
                    "emitter_entrypoint": ("NOT_EXPORTED_R58_VERIFIED" if self.r58_candidate is not None
                                            else "CANDIDATE_NOT_VERIFIED"),
                    "physical_output": "HARD_DENIED", "playback": "NOT_PERFORMED",
                    "hardware_cutoff_certified": False, "physical_measurement": "NOT_PERFORMED"}

    def get_r60_control_status(self):
        """Read a bounded native software lease; this can never authorize audio."""
        with self.lock:
            if self._monitor_shutdown.is_set() or self.route is None:
                if self.r60_lease.state == 1:
                    self.lib.fm_r60_lease_revoke(ctypes.byref(self.r60_lease), 7)
            elif self.r60_lease.state == 1:
                if not self._r62_check_locked():
                    self._r61_trip_locked(5, "R62_FAULT_DEVICE_IDENTITY_LEASE_CHECK")
                elif self.lib.fm_r60_lease_check(ctypes.byref(self.r60_lease),
                                           ctypes.byref(self.r59_session)) != 1:
                    self._r61_trip_locked(4, "R61_FAULT_LEASE_CHECK_FAILED")
            lease=self.r60_lease
            return {"state": R60_STATES.get(int(lease.state), "REVOKED"),
                    "reason": R60_REASONS.get(int(lease.reason), "UNKNOWN"),
                    "valid_control_lease": bool(lease.state == 1),
                    "generation": int(lease.generation),
                    "ttl_ms": 4000,
                    "last_coreaudio_confirmation_ns": int(lease.verified_at_ns) if lease.state == 1 else None,
                    "device_id": int(lease.bound.device_id) if lease.state == 1 else None,
                    "physical_output": "HARD_DENIED", "playback": "NOT_PERFORMED",
                    "physical_interlock": "NOT_PRESENT_NOT_CERTIFIED",
                    "note": "Control metadata only; cannot arm, start or stop a physical emitter."}

    def invalidate_r59_session(self):
        """Authenticated explicit removal of one native route-to-command contract.

        The UI calls this on command edits; a reset cannot enable emission.
        """
        with self.lock:
            self._r64_retire_previous_binding_locked()
        return self.get_r59_session_status()

    def bind_r59_session(self,payload):
        """Bind exact command to macOS default route after real C checks.

        No AudioQueue or emission entrypoint is linked in this library. A
        verified route remains a non-emitting contract, not an armed device.
        """
        if not isinstance(payload,dict) or set(payload)!={"channel","hz","level","duration_ms"}:
            raise ValueError("INVALID_R59_BIND_SCHEMA")
        if payload["channel"]!="acoustic":
            raise ValueError("R59_ACOUSTIC_ONLY")
        if any(type(payload[k]) not in (int,float) for k in ("hz","level")) or type(payload["duration_ms"]) is not int:
            raise ValueError("INVALID_R59_COMMAND_TYPES")
        if not (math.isfinite(payload["hz"]) and math.isfinite(payload["level"]) and
                0 < payload["duration_ms"] <= 30000):
            raise ValueError("INVALID_R59_COMMAND_BOUNDS")
        with self.lock:
            self._r64_retire_previous_binding_locked()
            if self._monitor_shutdown.is_set():
                raise ValueError("OS_MONITOR_STOPPED")
            if self.r58_candidate is None or not self.r58_evidence or not self.r58_evidence.emitter_entrypoint_denied:
                raise ValueError("R58_ISOLATED_CANDIDATE_NOT_VERIFIED")
            if self.lib.fm_r61_fault_can_bind(ctypes.byref(self.r61_fault)) != 1:
                raise ValueError("R61_NATIVE_FAULT_LATCHED_OR_STOPPED")
            selected=dict(self.route) if self.route is not None else None
            if selected is None:
                raise ValueError("SELECT_REAL_COREAUDIO_OUTPUT_FIRST")
            cmd=FMCommand(1,float(payload["hz"]),float(payload["level"]),payload["duration_ms"])
            rc=self.lib.fm_r59_session_bind(ctypes.byref(self.r59_session),ctypes.byref(cmd),
                selected["device_id"],selected["name"].encode("utf-8"),
                selected["channels"],selected["nominal_sample_rate_hz"])
            if rc<0:
                raise ValueError("NATIVE_R59_BIND_FFI_ERROR")
            if rc == 1:
                if self.lib.fm_r62_identity_pin(ctypes.byref(self.r62_identity),
                                                ctypes.byref(self.r59_session)) != 1:
                    self._r61_trip_locked(5, "R62_FAULT_INITIAL_DEVICE_UID_READ")
                    raise ValueError("R62_COREAUDIO_IDENTITY_PIN_REFUSED")
                if self.lib.fm_r60_lease_begin(ctypes.byref(self.r60_lease),
                                               ctypes.byref(self.r59_session)) != 1:
                    self.lib.fm_r59_session_invalidate(ctypes.byref(self.r59_session))
                    self.lib.fm_r62_identity_invalidate(ctypes.byref(self.r62_identity), 4)
                    self.lib.fm_r60_lease_revoke(ctypes.byref(self.r60_lease), 2)
                    raise ValueError("R60_NATIVE_CONTROL_LEASE_REFUSED")
            state={"phase":R59_PHASES.get(int(self.r59_session.phase),"INVALIDATED"),
                   "reason":R59_REASONS.get(int(self.r59_session.reason),"UNKNOWN"),
                   "route_bound": bool(rc == 1),
                   "digital_frame_budget": int(self.r59_session.digital_frame_budget) if rc == 1 else None,
                   "candidate_isolated":True,
                   "native_route_contract":"R56_AND_R57_REAL_COREAUDIO",
                   "physical_output":"HARD_DENIED", "playback":"NOT_PERFORMED"}
            self.audit=(self.audit+[{"action":"r59_bind","route_bound":rc==1}])[-12:]
            return state

    def prepare_r63_digital_pcm(self):
        """Build and immediately erase a bounded digital PCM command block.

        Requires a real OS UID, active native session, validated lease and
        no fault. No AudioQueue, playback, device write or PCM API response.
        """
        with self.lock:
            if self._monitor_shutdown.is_set() or self.route is None:
                raise ValueError("R63_NO_ACTIVE_REAL_ROUTE")
            if self.r58_candidate is None or not self.r58_evidence or not self.r58_evidence.emitter_entrypoint_denied:
                raise ValueError("R63_R58_CANDIDATE_NOT_ISOLATED")
            if self.lib.fm_r61_fault_can_bind(ctypes.byref(self.r61_fault)) != 1:
                raise ValueError("R63_FAULT_OR_STOP_REFUSED")
            if self.r59_session.phase != 1:
                raise ValueError("R63_NATIVE_SESSION_UNBOUND")
            if not self._r62_check_locked():
                raise ValueError("R63_REAL_COREAUDIO_UID_INVALID")
            if self.lib.fm_r59_session_poll(ctypes.byref(self.r59_session)) != 1:
                self._r61_trip_locked(3, "R63_ROUTE_READBACK_INVALID")
                raise ValueError("R63_REAL_COREAUDIO_ROUTE_INVALID")
            if self.lib.fm_r60_lease_check(ctypes.byref(self.r60_lease),
                                            ctypes.byref(self.r59_session)) != 1:
                self._r61_trip_locked(4, "R63_CONTROL_LEASE_INVALID")
                raise ValueError("R63_NATIVE_LEASE_EXPIRED")
            s=self.r59_session
            frames=int(s.digital_frame_budget)
            ch=int(s.channels)
            if not (1 <= frames <= 96000 and 1 <= ch <= 2):
                raise ValueError("R63_DIGITAL_FRAME_CAP_REFUSED")
            samples=frames*ch
            pcm=(ctypes.c_float*samples)()
            report=FMR63DigitalReport()
            try:
                if self.lib.fm_r63_render_digital_pcm(ctypes.byref(s),pcm,samples,ctypes.byref(report)) != 1:
                    raise ValueError("R63_NATIVE_PCM_BOUNDS_REFUSED")
                integrity=FMR64DigitalIntegrity()
                if self.lib.fm_r64_verify_digital_pcm(
                        pcm, samples, ch, ctypes.c_float(0.01),
                        ctypes.byref(integrity)) != 1:
                    raise ValueError("R64_DIGITAL_PCM_INTEGRITY_REFUSED")
                if (int(integrity.checked_samples) != samples or
                        int(integrity.channels) != ch or
                        integrity.zero_edges != 1):
                    raise ValueError("R64_DIGITAL_PCM_PROOF_INCONSISTENT")
                result={"prepared":True,"digital_frames":int(report.frames),
                        "digital_samples":int(report.samples),"channels":int(report.channels),
                        "digital_peak_normalized":round(float(report.digital_peak_normalized),8),
                        "physical_measurement":"NOT_PERFORMED","playback":"NOT_PERFORMED",
                        "physical_output":"HARD_DENIED","authorization":"NONE",
                        "digital_integrity_r64":"PASS_NUMERIC_ONLY_NO_PLAYBACK",
                        "digital_envelope_verified":True,"digital_zero_edges":True}
            finally:
                self.lib.fm_r63_zeroize_digital_pcm(pcm,samples)
                if any(pcm):
                    raise RuntimeError("R63_TRANSIENT_PCM_NOT_ZEROIZED")
            result["transient_pcm_zeroized"]=True
            self.audit=(self.audit+[{"action":"r63_digital_pcm_prepared_then_zeroized",
                                      "frames":result["digital_frames"]}])[-12:]
            return result

    def prepare_r65_segmented_pcm(self):
        """Produce numeric PCM in bounded, ephemeral 256-frame segments.

        No hardware output, PCM export, disk write or scientific measurement.
        Re-read native OS route/UID and monotonic R60 lease before and after.
        Holding the control lock prevents concurrent GUI STOP/route edits from
        reporting a successful result with stale contracts. Since the loop is
        bounded to 375 short segments and never emits, this is not a physical
        emergency-stop guarantee.
        """
        with self.lock:
            if self._monitor_shutdown.is_set() or self.route is None:
                raise ValueError("R65_NO_ACTIVE_REAL_ROUTE")
            if self.r58_candidate is None or not self.r58_evidence or not self.r58_evidence.emitter_entrypoint_denied:
                raise ValueError("R65_R58_CANDIDATE_NOT_ISOLATED")
            if self.lib.fm_r61_fault_can_bind(ctypes.byref(self.r61_fault)) != 1 or self.r59_session.phase != 1:
                raise ValueError("R65_NATIVE_SESSION_OR_FAULT_REFUSED")
            if not self._r62_check_locked():
                raise ValueError("R65_OS_UID_REFUSED")
            if self.lib.fm_r59_session_poll(ctypes.byref(self.r59_session)) != 1:
                self._r61_trip_locked(3, "R65_START_ROUTE_READBACK_INVALID")
                raise ValueError("R65_REAL_ROUTE_REFUSED")
            if self.lib.fm_r60_lease_check(ctypes.byref(self.r60_lease),
                                           ctypes.byref(self.r59_session)) != 1:
                self._r61_trip_locked(4, "R65_START_LEASE_INVALID")
                raise ValueError("R65_LEASE_EXPIRED")
            session = self.r59_session
            total = int(session.digital_frame_budget)
            channels = int(session.channels)
            if not (1 <= total <= 96000 and 1 <= channels <= 2):
                raise ValueError("R65_DIGITAL_FRAME_CAP_REFUSED")
            cursor = FMR65Cursor()
            if self.lib.fm_r65_stream_begin(ctypes.byref(cursor), ctypes.byref(session)) != 1:
                raise ValueError("R65_CURSOR_BEGIN_REFUSED")
            audit66 = FMR66Audit()
            if self.lib.fm_r66_audit_begin(ctypes.byref(audit66), total, channels) != 1:
                self.lib.fm_r65_stream_clear(ctypes.byref(cursor))
                raise ValueError("R66_AUDIT_BEGIN_REFUSED")
            capacity = 256*channels
            chunk = (ctypes.c_float*capacity)()
            chunks = 0
            prepared_frames = 0
            peak = 0.0
            try:
                while cursor.state == 1:
                    report = FMR65ChunkReport()
                    try:
                        ok = self.lib.fm_r65_stream_next(ctypes.byref(cursor),
                                ctypes.byref(session), chunk, capacity, ctypes.byref(report))
                        if ok != 1:
                            raise ValueError("R65_NATIVE_SEGMENT_REFUSED")
                        if (int(report.start_frame) != prepared_frames or
                            not (1 <= int(report.frames) <= 256) or
                            int(report.samples) != int(report.frames)*channels or
                            int(report.channels) != channels or
                            not math.isfinite(float(report.chunk_digital_peak)) or
                            float(report.chunk_digital_peak) > 0.010000001):
                            raise ValueError("R65_SEGMENT_PROOF_INCONSISTENT")
                        if self.lib.fm_r66_audit_chunk(ctypes.byref(audit66),
                                ctypes.byref(report), chunk, capacity) != 1:
                            raise ValueError("R66_NATIVE_SEQUENCE_AUDIT_REFUSED")
                        prepared_frames += int(report.frames)
                        chunks += 1
                        peak = max(peak, float(report.chunk_digital_peak))
                    finally:
                        self.lib.fm_r63_zeroize_digital_pcm(chunk, capacity)
                        if any(chunk):
                            raise RuntimeError("R65_SEGMENT_NOT_ZEROIZED")
                    if chunks > 375:
                        raise ValueError("R65_SEGMENT_COUNT_CAP_REFUSED")
                if (cursor.state != 2 or prepared_frames != total or
                    int(cursor.next_frame) != total or
                    chunks != (total+255)//256 or
                    not math.isfinite(peak)):
                    raise ValueError("R65_STREAM_NOT_COMPLETE")
                if self.lib.fm_r66_audit_finish(ctypes.byref(audit66)) != 1 or \
                        int(audit66.checked_frames) != total or \
                        int(audit66.checked_samples) != total*channels or \
                        int(audit66.segments) != chunks:
                    raise ValueError("R66_NATIVE_SEQUENCE_NOT_COMPLETE")
                if not self._r62_check_locked():
                    raise ValueError("R65_OS_UID_CHANGED_DURING_PREPARATION")
                if self.lib.fm_r59_session_poll(ctypes.byref(session)) != 1:
                    self._r61_trip_locked(3, "R65_END_ROUTE_READBACK_INVALID")
                    raise ValueError("R65_END_ROUTE_INVALID")
                if self.lib.fm_r60_lease_check(ctypes.byref(self.r60_lease),
                                                ctypes.byref(session)) != 1:
                    self._r61_trip_locked(4, "R65_END_LEASE_INVALID")
                    raise ValueError("R65_END_LEASE_EXPIRED")
                result = {"prepared": True, "digital_frames": total,
                          "digital_samples": total*channels, "channels": channels,
                          "digital_peak_normalized": round(peak, 8),
                          "segment_frames_max": 256, "segment_count": chunks,
                          "peak_pcm_buffer_samples": capacity,
                          "stream_integrity_r65": "CONTIGUOUS_BOUNDED_NUMERIC_NO_PLAYBACK",
                          "sequence_audit_r66": "PASS_NATIVE_DIGITAL_SAMPLES_NO_PLAYBACK",
                          "all_segments_zeroized": True,
                          "physical_measurement": "NOT_PERFORMED",
                          "playback": "NOT_PERFORMED", "physical_output": "HARD_DENIED",
                          "authorization": "NONE"}
                self.audit = (self.audit+[{
                    "action": "r65_segmented_digital_pcm_prepared_then_zeroized",
                    "segments": chunks, "frames": total}])[-12:]
                return result
            finally:
                self.lib.fm_r63_zeroize_digital_pcm(chunk, capacity)
                self.lib.fm_r65_stream_clear(ctypes.byref(cursor))
                self.lib.fm_r66_audit_clear(ctypes.byref(audit66))
                if any(chunk) or any(bytes(cursor)) or any(bytes(audit66)):
                    raise RuntimeError("R65_EPHEMERAL_CONTROL_MEMORY_NOT_ZEROIZED")

    def attach_candidate(self):
        """Build and link exact source-only CoreAudio candidate as a second *isolated* library.

        Main command library remains output_hard_denied. The candidate exports ONLY
        fm_r58_candidate_evidence. Emitting entrypoints and static native playback (unreachable)
        path are not reachable from ctypes, HTTP, or GUI.
        """
        if self.r58_candidate is not None:
            return self.candidate_status()
        if sys.platform != 'darwin':
            self.r58_candidate_error = 'MACOS_ONLY_NOT_COMPILED'
            return self.candidate_status()
        if os.uname().machine != 'x86_64':
            self.r58_candidate_error = 'MAC_INTEL_REQUIRED'
            return self.candidate_status()
        source_dir = self.builddir / 'r58_original_git_sources'
        try:
            module=load_candidate_source_module()
            meta=module.extract_pinned(source_dir)
            clang=shutil.which('clang')
            if not clang:
                raise RuntimeError('APPLE_CLANG_NOT_FOUND')
            libpath=self.builddir / 'libfreqmed_r58_candidate_isolated.dylib'
            args=[clang,'-std=c11','-O2','-fPIC','-dynamiclib','-fvisibility=hidden',
                  '-Wall','-Wextra','-Werror','-I',str(NATIVE),'-I',str(source_dir),
                  '-Wl,-exported_symbol,_fm_r58_candidate_evidence','-o',str(libpath),
                  str(source_dir/'acoustic_macos.c'),
                  str(source_dir/'acoustic_route_guard_macos.c'),
                  str(source_dir/'acoustic_device_pin_macos.c'),
                  str(NATIVE/'acoustic_probe_macos.c'),
                  str(NATIVE/'candidate_link_r58.c'),
                  '-framework','AudioToolbox','-framework','CoreAudio',
                  '-framework','CoreFoundation','-lm']
            build=subprocess.run(args,cwd=str(ROOT),capture_output=True,text=True,timeout=60,check=False)
            if build.returncode:
                raise RuntimeError('R58_CANDIDATE_NATIVE_COMPILE_FAILED:'+build.stderr[-1200:])
            candidate=ctypes.CDLL(str(libpath))
            candidate.fm_r58_candidate_evidence.argtypes=[ctypes.POINTER(FMR58CandidateEvidence)]
            candidate.fm_r58_candidate_evidence.restype=ctypes.c_int
            # No playback, backend availability or stop/start symbols may escape.
            for forbidden in ('fm_acoustic_physical_output','fm_acoustic_native_backend_available',
                              'fm_route_capture','fm_acoustic_bind_queue_to_route','acoustic_output_impl'):
                try:
                    getattr(candidate,forbidden)
                except AttributeError:
                    continue
                raise RuntimeError('R58_FORBIDDEN_CANDIDATE_EXPORT:'+forbidden)
            evidence=FMR58CandidateEvidence()
            if candidate.fm_r58_candidate_evidence(ctypes.byref(evidence)) != 0 or (
                evidence.abi_version, evidence.original_candidate_compiled,
                evidence.macos_backend_declared, evidence.emitter_entrypoint_denied)!=(1,1,1,1):
                raise RuntimeError('R58_CANDIDATE_ABI_OR_DENIAL_MISMATCH')
            self.r58_candidate=candidate
            self.r58_evidence=evidence
            self.r58_candidate_error='NONE'
            self.r58_provenance={'verified_blobs':meta['verified_blobs']}
        except (RuntimeError, OSError, subprocess.TimeoutExpired) as e:
            self.r58_candidate=None
            self.r58_candidate_error=str(e)[:200]
        return self.candidate_status()

    def candidate_status(self):
        evidence=self.r58_evidence
        return {'candidate_source_linked_isolated': bool(self.r58_candidate is not None),
                'original_acoustic_backend_compiled': bool(evidence and evidence.original_candidate_compiled),
                'candidate_mac_backend_declared': bool(evidence and evidence.macos_backend_declared),
                'hard_denial_verified_in_candidate': bool(evidence and evidence.emitter_entrypoint_denied),
                'source_git_blobs_verified': self.r58_provenance['verified_blobs'] if evidence else 0,
                'emission_entrypoints_exported':False if evidence else None,
                'main_application_physical_output':'HARD_DENIED',
                'candidate_route_binding':'NOT_PERFORMED',
                'playback':'NOT_PERFORMED', 'physical_measurement':'NOT_PERFORMED',
                'error':self.r58_candidate_error}

    def acoustic_probe(self):
        caps = FMOutputCapabilities()
        ok = self.lib.fm_acoustic_readonly_probe(ctypes.byref(caps)) == 0
        if not ok:
            return {"observed": False, "hardware_qualified": False,
                    "reason": "READ_ONLY_COREAUDIO_METADATA_UNAVAILABLE_OR_UNSUPPORTED"}
        return {"observed": True, "hardware_qualified": False,
                "type": "MACOS_DEFAULT_OUTPUT_METADATA", "channels": caps.output_channels,
                "nominal_sample_rate_hz": caps.nominal_sample_rate_hz,
                "transducer_verified": False, "calibration_verified": False}


def usb_inventory():
    if sys.platform != "darwin":
        return {"observed": False, "reason": "MACOS_REQUIRED"}
    # Only an OS-provided read-only inventory; no ports, no driver operations.
    try:
        p = subprocess.run(["/usr/sbin/system_profiler", "SPUSBDataType", "-json", "-detailLevel", "mini"],
                           capture_output=True, text=True, timeout=18, check=False)
        if p.returncode or len(p.stdout) > 2_000_000:
            return {"observed": False, "reason": "OS_USB_INVENTORY_UNAVAILABLE"}
        parsed = json.loads(p.stdout)
        count = 0
        def walk(node):
            nonlocal count
            if isinstance(node, dict):
                if "vendor_id" in node and "product_id" in node:
                    count += 1
                for v in node.values(): walk(v)
            elif isinstance(node, list):
                for v in node: walk(v)
        walk(parsed)
        return {"observed": True, "usb_vendor_product_entries": count,
                "qualified_em_generators": 0,
                "note": "USB metadata only. Zero qualified generators means none have been qualified here, not that none physically exist."}
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return {"observed": False, "reason": "OS_USB_INVENTORY_UNAVAILABLE"}


class AppHandler(BaseHTTPRequestHandler):
    server_version = "FREQMED-R58/1.0"
    sys_version = ""

    def log_message(self, fmt, *args):
        # Do not log user command values or session tokens.
        return

    def send_bytes(self, status, content, mime, *, csp=True):
        self.send_response(status)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "no-referrer")
        if csp:
            self.send_header("Content-Security-Policy", "default-src 'none'; style-src 'self'; script-src 'self'; connect-src 'self'; img-src 'self' data:; base-uri 'none'; form-action 'none'; frame-ancestors 'none'")
        self.end_headers()
        self.wfile.write(content)

    def send_json(self, status, data):
        self.send_bytes(status, json.dumps(data, ensure_ascii=False, allow_nan=False, separators=(",", ":")).encode("utf-8"),
                        "application/json; charset=utf-8")

    def allowed_host(self):
        return self.headers.get("Host", "") in (f"127.0.0.1:{self.server.server_port}",)

    def do_GET(self):
        if not self.allowed_host():
            self.send_json(403, {"error": "HOST_REFUSED"}); return
        route = urlsplit(self.path).path
        if route in ("/", "/index.html"):
            p, mime = STATIC/"index.html", "text/html; charset=utf-8"
        elif route == "/style.css":
            p, mime = STATIC/"style.css", "text/css; charset=utf-8"
        elif route == "/app.js":
            p, mime = STATIC/"app.js", "text/javascript; charset=utf-8"
        elif route == "/r54.js":
            p, mime = STATIC/"r54.js", "text/javascript; charset=utf-8"
        elif route == "/r54.css":
            p, mime = STATIC/"r54.css", "text/css; charset=utf-8"
        elif route == "/r55.js":
            p, mime = STATIC/"r55.js", "text/javascript; charset=utf-8"
        elif route == "/r57.js":
            p, mime = STATIC/"r57.js", "text/javascript; charset=utf-8"
        elif route == "/r59.js":
            p, mime = STATIC/"r59.js", "text/javascript; charset=utf-8"
        elif route == "/r61.js":
            p, mime = STATIC/"r61.js", "text/javascript; charset=utf-8"
        elif route == "/r65.js":
            p, mime = STATIC/"r65.js", "text/javascript; charset=utf-8"
        elif route == "/r63.js":
            p, mime = STATIC/"r63.js", "text/javascript; charset=utf-8"
        elif route == "/r63.css":
            p, mime = STATIC/"r63.css", "text/css; charset=utf-8"
        elif route == "/r62.js":
            p, mime = STATIC/"r62.js", "text/javascript; charset=utf-8"
        elif route == "/r62.css":
            p, mime = STATIC/"r62.css", "text/css; charset=utf-8"
        elif route == "/r61.css":
            p, mime = STATIC/"r61.css", "text/css; charset=utf-8"
        elif route == "/r60.js":
            p, mime = STATIC/"r60.js", "text/javascript; charset=utf-8"
        elif route == "/r60.css":
            p, mime = STATIC/"r60.css", "text/css; charset=utf-8"
        elif route == "/r59.css":
            p, mime = STATIC/"r59.css", "text/css; charset=utf-8"
        elif route == "/cleanup.css":
            p, mime = STATIC/"cleanup.css", "text/css; charset=utf-8"
        elif route == "/cleanup.js":
            p, mime = STATIC/"cleanup.js", "text/javascript; charset=utf-8"
        elif route == "/r58.js":
            p, mime = STATIC/"r58.js", "text/javascript; charset=utf-8"
        elif route == "/r58.css":
            p, mime = STATIC/"r58.css", "text/css; charset=utf-8"
        elif route == "/r57.css":
            p, mime = STATIC/"r57.css", "text/css; charset=utf-8"
        elif route == "/r56.js":
            p, mime = STATIC/"r56.js", "text/javascript; charset=utf-8"
        elif route == "/r56.css":
            p, mime = STATIC/"r56.css", "text/css; charset=utf-8"
        elif route == "/r55.css":
            p, mime = STATIC/"r55.css", "text/css; charset=utf-8"
        elif route == "/historical/v5":
            p, mime = HISTORICAL, "text/html; charset=utf-8"
        elif route == "/api/session":
            self.send_json(200, {"session": self.server.token}); return
        elif route == "/api/status":
            self.send_json(200, self.server.core.status()); return
        elif route == "/api/audio":
            self.send_json(200, self.server.core.acoustic_probe()); return
        elif route == "/api/usb":
            self.send_json(200, usb_inventory()); return
        elif route == "/api/audio/devices":
            self.send_json(200, self.server.core.audio_devices()); return
        elif route == "/api/acoustic/session/status":
            self.send_json(200, self.server.core.get_r59_session_status()); return
        elif route == "/api/acoustic/control/status":
            self.send_json(200, self.server.core.get_r60_control_status()); return
        elif route == "/api/acoustic/fault/status":
            self.send_json(200, self.server.core.get_r61_fault_status()); return
        elif route == "/api/acoustic/identity/status":
            self.send_json(200, self.server.core.get_r62_identity_status()); return
        elif route == "/api/acoustic/candidate/status":
            self.send_json(200, self.server.core.candidate_status()); return
        elif route == "/api/acoustic/backend/status":
            self.send_json(200, self.server.core.get_r57_backend_status()); return
        elif route == "/api/acoustic/preflight/status":
            self.send_json(200, self.server.core.get_acoustic_preflight_status()); return
        elif route == "/api/route/monitor":
            self.send_json(200, self.server.core.route_monitor_status()); return
        else:
            self.send_json(404, {"error": "NO_SUCH_ROUTE"}); return
        self.send_bytes(200, p.read_bytes(), mime, csp=(route != "/historical/v5"))

    def do_POST(self):
        if not self.allowed_host():
            self.send_json(403, {"error": "HOST_REFUSED"}); return
        exact_origin = f"http://127.0.0.1:{self.server.server_port}"
        if self.headers.get("Origin", "") != exact_origin:
            self.send_json(403, {"error": "ORIGIN_REFUSED"}); return
        if self.headers.get("X-FREQMED-SESSION", "") != self.server.token:
            self.send_json(403, {"error": "SESSION_REFUSED"}); return
        if self.headers.get("Content-Type", "").split(";")[0] != "application/json":
            self.send_json(415, {"error": "JSON_REQUIRED"}); return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 2048:
                raise ValueError("INVALID_REQUEST_SIZE")
            payload = json.loads(self.rfile.read(length))
            if self.path == "/api/acoustic/fault/ack":
                if payload != {}: raise ValueError("EMPTY_PAYLOAD_REQUIRED")
                result = self.server.core.acknowledge_r61_fault()
            elif self.path == "/api/acoustic/pcm/prepare-segmented":
                if payload != {}: raise ValueError("EMPTY_PAYLOAD_REQUIRED")
                result = self.server.core.prepare_r65_segmented_pcm()
            elif self.path == "/api/acoustic/pcm/prepare":
                if payload != {}: raise ValueError("EMPTY_PAYLOAD_REQUIRED")
                result = self.server.core.prepare_r63_digital_pcm()
            elif self.path == "/api/acoustic/session/invalidate":
                if payload != {}: raise ValueError("EMPTY_PAYLOAD_REQUIRED")
                result = self.server.core.invalidate_r59_session()
            elif self.path == "/api/acoustic/session/bind":
                result = self.server.core.bind_r59_session(payload)
            elif self.path == "/api/acoustic/backend/inspect":
                result = self.server.core.r57_backend_check(payload)
            elif self.path == "/api/acoustic/preflight":
                result = self.server.core.acoustic_preflight(payload)
            elif self.path == "/api/validate":
                result = self.server.core.validate(payload)
            elif self.path == "/api/reset":
                if payload != {}: raise ValueError("EMPTY_PAYLOAD_REQUIRED")
                result = self.server.core.stop()
            elif self.path == "/api/audio/select":
                result = self.server.core.select_audio(payload)
            elif self.path == "/api/audio/clear":
                if payload != {}: raise ValueError("EMPTY_PAYLOAD_REQUIRED")
                result = self.server.core.clear_audio()
            elif self.path == "/api/software-stop":
                if payload != {}: raise ValueError("EMPTY_PAYLOAD_REQUIRED")
                result = self.server.core.stop_engine_and_monitor()
            elif self.path == "/api/route/monitor/resume":
                if payload != {}: raise ValueError("EMPTY_PAYLOAD_REQUIRED")
                result = self.server.core.resume_route_monitor()
            else:
                self.send_json(404, {"error": "NO_SUCH_ROUTE"}); return
        except (ValueError, json.JSONDecodeError) as e:
            self.send_json(422, {"error": str(e)[:128]}); return
        self.send_json(200, result)


def make_server(core):
    server = ThreadingHTTPServer(("127.0.0.1", 0), AppHandler)
    server.core = core
    server.token = secrets.token_urlsafe(32)
    server.daemon_threads = True
    return server


def internal_tests(core):
    valid = core.validate({"channel": "acoustic", "hz": 440.0, "level": 0.01, "duration_ms": 500})
    assert valid["structurally_valid"] and valid["native_c_executed"]
    assert not valid["guardian_authorized"] and valid["guardian_state"] == "BLOCKED"
    assert valid["guardian_reason"] == "R1_OUTPUT_HARD_LOCK_CERTIFICATION_REQUIRED"
    for bad in (0, -1, float("nan"), float("inf")):
        try:
            v = core.validate({"channel": "em", "hz": bad, "level": 0.01, "duration_ms": 500})
            assert not v["structurally_valid"]
        except ValueError:
            pass
    assert core.stop()["guardian_state"] == "OFF"
    assert core.lib.fm_acoustic_native_backend_available() == 0
    assert core.lib.fm_em_backend_available() == 0
    assert core.audio_devices()["observed"] in (True, False)
    assert core.get_route_status()["selected"] is False
    monitor = core.route_watch_tick()
    assert monitor["checks"] == 0  # Unselected startup MUST NOT poll OS periodically.
    assert monitor["physical_stop_capability"] == "NONE_NOT_AN_INTERLOCK"
    stopped = core.stop_engine_and_monitor()
    assert stopped["guardian_state"] == "OFF"
    assert not stopped["monitor_running"]
    assert core.route_monitor_status()["checks"] == stopped["monitor_checks_frozen_at"]
    assert core.get_r60_control_status()["physical_output"] == "HARD_DENIED"
    assert core.get_r60_control_status()["valid_control_lease"] is False
    assert core.get_r61_fault_status()["physical_output"] == "HARD_DENIED"
    assert core.lib.fm_r61_fault_can_bind(ctypes.byref(core.r61_fault)) == 0
    print("GEN_R61_NATIVE_FAULT_LATCH_SELFTEST=PASS")
    print("GEN_R60_NATIVE_CONTROL_LEASE_SELFTEST=PASS")
    print("GEN_R59_NATIVE_C_SELFTEST=PASS")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()
    count = verify_manifest()
    print(f"GEN_R59_KIT_HASHES={count}_PASS", flush=True)
    print(f"GEN_R60_KIT_HASHES={count}_PASS", flush=True)
    print(f"GEN_R61_KIT_HASHES={count}_PASS", flush=True)
    print(f"GEN_R63_KIT_HASHES={count}_PASS", flush=True)
    print(f"GEN_R64_KIT_HASHES={count}_PASS", flush=True)
    print(f"GEN_R66_KIT_HASHES={count}_PASS", flush=True)
    if sys.platform == "darwin" and os.uname().machine != "x86_64":
        raise SystemExit("GEN_R59_MAC_INTEL_ONLY")
    with tempfile.TemporaryDirectory(prefix="FREQMED_GEN_R59_BUILD_") as directory:
        core = NativeCore(Path(directory))
        internal_tests(core)
        linked=core.attach_candidate()
        if sys.platform == 'darwin' and not linked['candidate_source_linked_isolated']:
            raise RuntimeError('R58_MAC_CANDIDATE_LINK_NOT_QUALIFIED:'+linked['error'])
        print('GEN_R64_DIGITAL_INTEGRITY=BOUND_PCM_ZERO_EDGES_FAIL_CLOSED_NO_EMISSION',flush=True)
        print('GEN_R66_NATIVE_AUDIT=BOUNDED_SEQUENCE_SAMPLE_CHECK_FAIL_CLOSED_NO_PLAYBACK',flush=True)
        print('GEN_R62_IDENTITY=LIVE_COREAUDIO_UID_FAIL_CLOSED_NO_EMISSION',flush=True)
        print('GEN_R62_FIX1_IDLE_MONITOR=NO_PERIODIC_OS_POLL_UNTIL_ROUTE_SELECTED',flush=True)
        print('GEN_R61_FAULT_LATCH=STICKY_FAIL_CLOSED_NO_EMISSION',flush=True)
        print('GEN_R60_CONTROL_LEASE=MONOTONIC_TIMEOUT_FAIL_CLOSED_NO_EMISSION',flush=True)
        print('GEN_R59_NATIVE_SESSION=COMPILED_NO_EMISSION',flush=True)
        print('GEN_R58_CANDIDATE_LINK='+('ISOLATED_SOURCE_ONLY_HARD_DENIED' if linked['candidate_source_linked_isolated'] else linked['error']),flush=True)
        if args.selftest:
            return 0
        # Internal selftests used STOP intentionally. Never leak their STOP
        # event or test counts into a fresh GUI, and do not auto-start polling.
        with core.lock:
            core.r59_session = FMR59Session()
            core.r60_lease = FMR60Lease()
            core.r61_fault = FMR61Fault()
            core.r62_identity = FMR62Identity()
            core.route_monitor_ticks = 0
            core.route_monitor_ever_observed = False
            core.route_monitor_last = "NOT_CHECKED"
            core.route_monitor_event = "NO_SELECTION"
            core.route_monitor_event_seq = 0
            core._monitor_shutdown.clear()
        server = make_server(core)
        url = f"http://127.0.0.1:{server.server_port}/"
        print("GEN_R59_GUI_NATIVE_C=LINKED_AND_TESTED", flush=True)
        print("GEN_R58_AUDIO_PROBE=COREAUDIO_READONLY", flush=True)
        print("GEN_R58_ACOUSTIC_OUTPUT=HARD_DENIED", flush=True)
        print("GEN_R58_EM_OUTPUT=HARD_DENIED", flush=True)
        print("GEN_R58_SIMULATION=NONE", flush=True)
        print("GEN_R66_UI_READY=" + url, flush=True)
        print("GEN_R64_UI_READY=" + url, flush=True)
        print("GEN_R63_UI_READY=" + url, flush=True)
        print("GEN_R61_UI_READY=" + url, flush=True)
        print("GEN_R60_UI_READY=" + url, flush=True)
        print("GEN_R59_UI_READY=" + url, flush=True)
        if not args.no_browser and sys.platform == "darwin":
            subprocess.run(["/usr/bin/open", "-a", "Safari", url], check=False)
        try:
            server.serve_forever(poll_interval=0.2)
        except KeyboardInterrupt:
            print("GEN_R59_SHUTDOWN=USER_REQUEST", flush=True)
        finally:
            core.stop_route_monitor()
            server.server_close()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, OSError, subprocess.TimeoutExpired) as exc:
        print("GEN_R59_FAIL_CLOSED=" + str(exc)[:1500], file=sys.stderr)
        raise SystemExit(1)

# LEGACY_R58_MARKER_FOR_SOURCE_LINEAGE=GEN_R58_UI_READY
