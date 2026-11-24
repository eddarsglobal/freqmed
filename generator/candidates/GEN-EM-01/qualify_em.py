#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""GEN-EM-01: pinned native contracts and actual read-only IOKit inventory."""
import ctypes as C
import hashlib
import json
import platform
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent
PINS = {
    'em_device_contract.h': 'd577e6c0f96fed003f767ee62ca74ff14e8ab69d',
    'em_device_contract.c': 'f09603278215d960f9c7df5cc1aa812bffe0d365',
    'em_qualification_gate.h': '4c9d1821b0460b26ae59f61f8ec9590ab088253e',
    'em_qualification_gate.c': 'a9f0af6169f91606f2607258cee82e7d6e3bf06e',
    'em_hardware_discovery.h': '478c2c7bb624325946da39751fefc342fdf07188',
    'em_hardware_discovery_macos.c': '5097b9f45252d01fb51f80a71918219f08912cd5',
    'em_instrument_driver_abi.h': 'c57bc2930a1dca952b4f86b48dec827eeed6a357',
}

class Candidate(C.Structure):
    _fields_ = [(n, C.c_uint32) for n in ('vendor_id', 'product_id', 'interface_protocol')] + [('has_vendor_product', C.c_int)]

class Inventory(C.Structure):
    _fields_ = [(n, C.c_uint32) for n in ('usb_devices_reported', 'usb_interfaces_reported', 'serial_callout_nodes_reported', 'usbtmc_interfaces_reported', 'candidates_stored')] + [('listing_truncated', C.c_int), ('candidates', Candidate * 24)]


def git_blob(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()


def verify_sources(root):
    for name, pin in PINS.items():
        p = root / 'native' / name
        if p.is_symlink() or not p.is_file() or p.stat().st_size > 131072 or git_blob(p.read_bytes()) != pin:
            raise RuntimeError('SOURCE_PIN_MISMATCH:' + name)
    return len(PINS)


def report_inventory(inv):
    if inv.listing_truncated not in (0, 1) or inv.candidates_stored > 24:
        raise RuntimeError('INVENTORY_INVALID_CAPACITY')
    if inv.usbtmc_interfaces_reported > inv.usb_interfaces_reported or inv.candidates_stored != min(inv.usbtmc_interfaces_reported, 24):
        raise RuntimeError('INVENTORY_INVALID_COUNTS')
    if bool(inv.listing_truncated) != (inv.usbtmc_interfaces_reported > 24):
        raise RuntimeError('INVENTORY_INVALID_TRUNCATION')
    if max(inv.usb_devices_reported, inv.usb_interfaces_reported, inv.serial_callout_nodes_reported) > 4096:
        raise RuntimeError('INVENTORY_INVALID_SCAN_BOUND')
    valid_descriptor_ids = 0
    for i in range(inv.candidates_stored):
        c = inv.candidates[i]
        if c.interface_protocol not in (0, 1) or c.has_vendor_product not in (0, 1):
            raise RuntimeError('INVENTORY_INVALID_DESCRIPTOR')
        if c.has_vendor_product:
            if c.vendor_id > 65535 or c.product_id > 65535:
                raise RuntimeError('INVENTORY_INVALID_IDS')
            valid_descriptor_ids += 1
    return dict(usb_devices=inv.usb_devices_reported, usb_interfaces=inv.usb_interfaces_reported,
                serial_callout_nodes=inv.serial_callout_nodes_reported, usbtmc_interfaces=inv.usbtmc_interfaces_reported,
                candidates_stored=inv.candidates_stored, candidates_with_descriptor_ids=valid_descriptor_ids,
                listing_truncated=bool(inv.listing_truncated))


def base_report():
    return dict(schema='freqmed.gen-em-01.v1', platform=platform.system(), machine=platform.machine(),
                hardware_qualified=False, authorization='NONE', physical_output='HARD_DENIED',
                em_status='BLOCKED_NO_QUALIFIED_DEVICE', physical_measurement='NOT_PERFORMED',
                device_ports_opened=0, instrument_commands_sent=0, certification='NOT_ISSUED',
                inventory=None, inventory_status='NOT_PERFORMED', verdict='BLOCK')


def qualify(root):
    report = base_report()
    try:
        report['source_pins_verified'] = verify_sources(root)
        cc = shutil.which('cc')
        if not cc:
            raise RuntimeError('C_COMPILER_UNAVAILABLE')
        darwin = platform.system() == 'Darwin'
        with tempfile.TemporaryDirectory(prefix='freqmed-em01-') as tmp:
            out = Path(tmp) / ('em.dylib' if darwin else 'em.so')
            sources = [str(root / 'native' / n) for n in ('em_device_contract.c', 'em_qualification_gate.c', 'em_hardware_discovery_macos.c')]
            flags = ['-dynamiclib', '-framework', 'IOKit', '-framework', 'CoreFoundation'] if darwin else ['-shared', '-fPIC', '-lm']
            subprocess.run([cc, '-std=c11', '-O2', '-Wall', '-Wextra', *sources, '-o', str(out), *flags], check=True, timeout=90)
            lib = C.CDLL(str(out))
            for name, args in [('fm_em_try_physical_emission', [C.c_void_p, C.c_void_p]), ('fm_em_hardware_qualified_in_r11', [C.c_void_p]), ('fm_em_discover_readonly', [C.POINTER(Inventory)])]:
                fn = getattr(lib, name)
                fn.argtypes, fn.restype = args, C.c_int
            if lib.fm_em_try_physical_emission(None, None) != -1 or lib.fm_em_hardware_qualified_in_r11(None) != 0:
                raise RuntimeError('NATIVE_DENIAL_FAILED')
            report['native_denial'] = 'PASS'
            inv = Inventory()
            rc = lib.fm_em_discover_readonly(C.byref(inv))
            if not darwin:
                if rc != -1 or bytes(inv) != bytes(Inventory()):
                    raise RuntimeError('UNSUPPORTED_PLATFORM_REFUSAL_FAILED')
                report.update(inventory_status='UNSUPPORTED_PLATFORM', verdict='PASS_PORTABLE_ONLY_MAC_PENDING')
                return report, 77
            if rc != 0:
                raise RuntimeError('IOKIT_READONLY_SCAN_FAILED')
            report['inventory'] = report_inventory(inv)
            report.update(inventory_status='REAL_OS_REGISTRY_READ_ONLY', verdict='PASS_MAC_SOFTWARE_ONLY')
            return report, 0
    except (OSError, RuntimeError, subprocess.SubprocessError) as exc:
        report['error'] = str(exc)
        return report, 1


class Tests(unittest.TestCase):
    def test_blob_empty(self):
        self.assertEqual(git_blob(b''), 'e69de29bb2d1d6434b8b29ae775ad8c2e48c5391')
    def test_source_missing_refused(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(RuntimeError, 'SOURCE_PIN_MISMATCH'):
                verify_sources(Path(d))
    def test_source_modified_refused(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / 'native').mkdir()
            (root / 'native' / 'em_device_contract.h').write_bytes(b'invalid')
            with self.assertRaisesRegex(RuntimeError, 'SOURCE_PIN_MISMATCH'):
                verify_sources(root)
    def test_no_qualification_from_report(self):
        r = base_report()
        self.assertFalse(r['hardware_qualified'])
        self.assertEqual(r['em_status'], 'BLOCKED_NO_QUALIFIED_DEVICE')
        self.assertIsNone(r['inventory'])
    def test_abi(self):
        self.assertEqual(C.sizeof(Candidate), 16)
        self.assertEqual(C.sizeof(Inventory), 408)
        self.assertEqual(Inventory.candidates.offset, 24)
    # Invalid raw API records test software rejection, never claim hardware observations.
    def test_invalid_capacity(self):
        x = Inventory(); x.candidates_stored = 25
        with self.assertRaisesRegex(RuntimeError, 'CAPACITY'): report_inventory(x)
    def test_invalid_count(self):
        x = Inventory(); x.usbtmc_interfaces_reported = 1
        with self.assertRaisesRegex(RuntimeError, 'COUNTS'): report_inventory(x)
    def test_invalid_truncation(self):
        x = Inventory(); x.listing_truncated = 1
        with self.assertRaisesRegex(RuntimeError, 'TRUNCATION'): report_inventory(x)
    def test_invalid_scan_bound(self):
        x = Inventory(); x.usb_devices_reported = 4097
        with self.assertRaisesRegex(RuntimeError, 'SCAN_BOUND'): report_inventory(x)


if __name__ == '__main__':
    if sys.argv[1:] == ['--selftest']:
        unittest.main(argv=[sys.argv[0]], verbosity=2)
    if sys.argv[1:]:
        raise SystemExit('Usage: qualify_em.py [--selftest]')
    result, code = qualify(ROOT)
    print('BUREAU_REPORT=' + json.dumps(result, sort_keys=True), flush=True)
    raise SystemExit(code)
