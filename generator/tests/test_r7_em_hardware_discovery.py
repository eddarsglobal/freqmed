"""Real IOKit inventory contract tests. No mock devices or physical simulation."""
from pathlib import Path
import json
import os
import re
import subprocess
import unittest
ROOT=Path(__file__).resolve().parents[1]
SRC=(ROOT/'src/em_hardware_discovery_macos.c').read_text()
HEAD=(ROOT/'src/em_hardware_discovery.h').read_text()
MAIN=(ROOT/'src/main.c').read_text()
RUN=(ROOT/'RUN_GEN_R7_MAC_INTEL.command').read_text()

class HardwareEnumerationGuards(unittest.TestCase):
    def test_uses_real_iokit_registry(self):
        self.assertIn('IOServiceGetMatchingServices(',SRC)
        self.assertIn('IOServiceMatching(',SRC)
    def test_detects_actual_usb_host_service_classes(self):
        self.assertIn('"IOUSBHostDevice"',SRC)
        self.assertIn('"IOUSBHostInterface"',SRC)
    def test_detects_actual_serial_os_services(self):
        self.assertIn('"IOSerialBSDClient"',SRC)
        self.assertIn('CFSTR("IOCalloutDevice")',SRC)
    def test_never_opens_ports_or_claims_usb(self):
        for forbidden in ('IOServiceOpen(', 'USBDeviceOpen(', 'open(',
                          'IOConnectCallMethod(', 'write(', 'socket(', 'connect('):
            self.assertNotIn(forbidden,SRC)
    def test_never_writes_registry(self):
        for forbidden in ('IORegistryEntrySetCFProperty(', 'IORegistryEntrySetCFProperties(',
                          'IORegistryEntrySetProperties(', 'IOServiceAddMatchingNotification('):
            self.assertNotIn(forbidden,SRC)
    def test_uses_readonly_properties(self):
        self.assertIn('IORegistryEntryCreateCFProperty(',SRC)
        self.assertIn('IORegistryEntrySearchCFProperty(',SRC)
    def test_usbtmc_correct_usb_if_codes(self):
        for literal in ('class_code==0xFEU', 'subclass_code==0x03U',
                        'protocol_code==0x00U', 'protocol_code==0x01U'):
            self.assertIn(literal,SRC)
    def test_will_not_count_any_usb_as_usbtmc(self):
        self.assertIn('descriptor_ok && fm_em_descriptor_is_usbtmc',SRC)
        self.assertIn('partial.usbtmc_interfaces_reported++',SRC)
    def test_has_bounded_enumeration(self):
        self.assertIn('#define FM_SCAN_MAX 4096U',SRC)
        self.assertIn('#define FM_EM_USB_CANDIDATES_CAP 24U',HEAD)
    def test_cf_reference_cleanup(self):
        self.assertIn('CFRelease(prop);',SRC)
        self.assertIn('IOObjectRelease(service);',SRC)
        self.assertIn('IOObjectRelease(iter);',SRC)
    def test_no_unique_serial_number_or_device_uid_print(self):
        self.assertNotIn('kUSBSerialNumberString',SRC)
        self.assertNotIn('kAudioDevicePropertyDeviceUID',SRC)
        self.assertNotIn('printf(',SRC)
        self.assertIn('Device name is intentionally discarded',SRC)
    def test_does_not_claim_em_device_based_on_usb_descriptor(self):
        self.assertIn('"em_generator_qualified\\\":false',MAIN)
        self.assertIn('hardware_ports_opened\\\":0',MAIN)
    def test_return_unavailable_instead_of_invented_zero(self):
        self.assertIn('"usbtmc_interfaces\\\":null',MAIN)
        self.assertIn('UNAVAILABLE_OR_INCOMPLETE',MAIN)
    def test_r7_binary_exposes_em_discover_command_only(self):
        self.assertIn('strcmp(argv[1],"em-discover")',MAIN)
        self.assertNotIn('strcmp(argv[1],"emit")',MAIN)
    def test_legacy_r6_does_not_need_r7_new_module(self):
        self.assertIn('#if defined(FREQMED_GEN_R7_DISCOVERY)',MAIN)
        self.assertIn('#endif',MAIN)
    def test_new_launcher_has_opt_in_discovery(self):
        self.assertIn('selftest|status|probe|em-discover',RUN)
        self.assertIn('R7_UNKNOWN_ACTION_BLOCK',RUN)
    def test_em_output_contract_unchanged(self):
        self.assertIn('return -1;', (ROOT/'src/em_backend.c').read_text())
        self.assertIn('return -1;', (ROOT/'src/em_device_contract.c').read_text())
    def test_r7_still_compiles_no_output_objects(self):
        self.assertIn('isolated.o',RUN)
        link=RUN.split(' -o "$WORK/freqmed-gen"',1)[1].split('-framework CoreAudio',1)[0]
        for forbidden in ('acoustic_macos.c','acoustic_route_guard_macos.c',
                          'acoustic_device_pin_macos.c','em_device_contract.c'):
            self.assertNotIn(forbidden,link)
        self.assertIn('output_hard_denied.c',link)
    def test_native_security_audit_blocks_write_and_output(self):
        self.assertIn('nm -u "$WORK/freqmed-gen"',RUN)
        for x in ('AudioQueueStart','IOServiceOpen','IORegistryEntrySetCFProperty','USBDeviceOpen'):
            self.assertIn(x,RUN)
    def test_no_fabricated_measurement_files(self):
        self.assertFalse(list(ROOT.rglob('*.csv')))
        self.assertFalse(list(ROOT.rglob('*.wav')))
    def test_never_prints_usb_or_serial_uuid(self):
        self.assertNotIn('serial_number',MAIN)
        self.assertNotIn('device_uid',MAIN)
    def test_runtime_action_not_a_generator(self):
        binary=os.getenv('FREQMED_GEN_R7_BINARY')
        if not binary:self.skipTest('Requires actual compiled R7 binary')
        p=subprocess.run([binary,'em-discover'],capture_output=True,text=True,timeout=12)
        self.assertEqual(p.returncode,0,p.stderr)
        obj=json.loads(p.stdout)
        self.assertEqual('FREQMED_GEN_R7_EM_DISCOVERY_V1',obj['schema'])
        self.assertFalse(obj['em_generator_qualified'])
        self.assertEqual('NONE',obj['physical_emission'])
        if obj['os_registry']=='IOKIT_READ_ONLY':
            self.assertEqual(0,obj['hardware_ports_opened'])
            self.assertIsInstance(obj['usbtmc_interfaces'],int)
        else:
            self.assertIsNone(obj['usbtmc_interfaces'])
    def test_runtime_emit_action_rejected(self):
        binary=os.getenv('FREQMED_GEN_R7_BINARY')
        if not binary:self.skipTest('Requires actual compiled R7 binary')
        for mode in ('emit','arm','--force','transmit'):
            p=subprocess.run([binary,mode],capture_output=True,text=True,timeout=4)
            self.assertNotEqual(0,p.returncode)

if __name__=='__main__':unittest.main()
