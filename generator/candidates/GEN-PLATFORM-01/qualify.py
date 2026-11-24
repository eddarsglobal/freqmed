#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Read-only native OS inventory. No device ports, streams or hardware commands."""
import argparse
import hashlib
import json
import os
import pathlib
import platform
import re
import subprocess
import tempfile
import unittest

BASE = "generator/candidates/"
PINS = [
    ("54fd4e6cd4a8106da12bb57fa8208ce569a4185b","GEN-R66/native/audio_devices.h","3bab6eef1608612f67550f90757791ea893c4a21"),
    ("54fd4e6cd4a8106da12bb57fa8208ce569a4185b","GEN-R66/native/audio_devices_macos.c","0ba4c6015786a3a263533036ca1025b7d2db2d09"),
    ("0412c0fbe2b54298a3b1dd346c78d3b56dda0e63","GEN-EM-01/native/em_hardware_discovery.h","478c2c7bb624325946da39751fefc342fdf07188"),
    ("0412c0fbe2b54298a3b1dd346c78d3b56dda0e63","GEN-EM-01/native/em_hardware_discovery_macos.c","5097b9f45252d01fb51f80a71918219f08912cd5"),
]
LIMIT = 4096
OWN = pathlib.Path(__file__).resolve().parent
def read_text(path, limit=65536):
    with path.open("rb") as f:
        data = f.read(limit+1)
    if len(data)>limit:
        raise ValueError("METADATA_SIZE_LIMIT")
    return data.decode("utf-8", errors="strict")

def entries(path):
    with os.scandir(path) as it:
        result=[]
        for item in it:
            if len(result)>=LIMIT:
                raise ValueError("INVENTORY_LIMIT")
            result.append(pathlib.Path(item.path))
    return result

def is_usbtmc(cls, sub, prot):
    return (cls,sub,prot) in ((254,3,0),(254,3,1))

def pcm_playback_count(data):
    # Count kernel PCM records reporting at least one playback substream.
    return sum(1 for line in data.splitlines()
               if re.match(r"^\d+-\d+:",line)
               and re.search(r"\bplayback\s+[1-9]\d*\b",line))

def linux_inventory():
    r={"audio_status":"UNAVAILABLE","audio_outputs":None,
       "audio_default_count":None,"audio_truncated":None,
       "usb_status":"UNAVAILABLE","usb_devices":None,"usb_interfaces":None,
       "serial_nodes":None,"usbtmc_signatures":None,
       "em_listing_truncated":None,"usb_descriptor_unreadable":None,
       "serial_status":"UNAVAILABLE"}
    try:
        data=read_text(pathlib.Path("/proc/asound/pcm"))
        r.update(audio_status="OBSERVED",audio_outputs=pcm_playback_count(data),
                 audio_truncated=False)
    except (OSError,ValueError):
        pass
    try:
        devices=interfaces=signatures=unreadable=0
        for p in entries(pathlib.Path("/sys/bus/usb/devices")):
            # Kernel bus names distinguish devices from interface records.
            if re.fullmatch(r"usb\d+|\d+-\d+(?:\.\d+)*",p.name):
                devices+=1
            elif re.fullmatch(r"\d+-\d+(?:\.\d+)*:\d+\.\d+",p.name):
                interfaces+=1
                try:
                    codes=[int(read_text(p/k,32).strip(),16) for k in
                           ("bInterfaceClass","bInterfaceSubClass","bInterfaceProtocol")]
                    if any(not 0<=v<=255 for v in codes):
                        raise ValueError("DESCRIPTOR_RANGE")
                    signatures+=int(is_usbtmc(*codes))
                except (OSError,ValueError):
                    unreadable+=1
        r.update(usb_status="PARTIAL" if unreadable else "OBSERVED",
                 usb_devices=devices,usb_interfaces=interfaces,
                 usbtmc_signatures=signatures,usb_descriptor_unreadable=unreadable,
                 em_listing_truncated=False)
    except (OSError,ValueError):
        pass
    try:
        # Count device-backed kernel TTY records, excluding virtual consoles.
        count=sum(1 for p in entries(pathlib.Path("/sys/class/tty"))
                  if (p/"device").exists())
        r.update(serial_status="OBSERVED",serial_nodes=count)
    except (OSError,ValueError):
        pass
    return r

def mac_inventory(repo):
    with tempfile.TemporaryDirectory(prefix="freqmed_platform_") as tmp:
        work=pathlib.Path(tmp)
        for ref,path,pin in PINS:
            data=subprocess.check_output(["git","-C",str(repo),"show",ref+":"+BASE+path],timeout=30)
            if hashlib.sha1(("blob %d"%len(data)).encode()+b"\0"+data).hexdigest()!=pin:
                raise ValueError("SOURCE_PIN_MISMATCH")
            (work/pathlib.Path(path).name).write_bytes(data)
        exe=work/"probe"
        subprocess.run(["cc","-std=c11","-Wall","-Wextra","-Werror",
                        "-I",str(work),str(OWN/"mac_probe.c"),
                        str(work/"audio_devices_macos.c"),
                        str(work/"em_hardware_discovery_macos.c"),
                        "-framework","CoreAudio","-framework","CoreFoundation",
                        "-framework","IOKit","-o",str(exe)],check=True,timeout=90)
        return json.loads(subprocess.check_output([str(exe)],text=True,timeout=30)),len(PINS)

def windows_inventory():
    root=os.environ.get("SystemRoot",r"C:\Windows")
    exe=pathlib.Path(root)/"System32"/"WindowsPowerShell"/"v1.0"/"powershell.exe"
    data=subprocess.check_output([str(exe),"-NoProfile","-NonInteractive",
                                  "-File",str(OWN/"windows_probe.ps1")],
                                 timeout=180)
    return json.loads(data.decode("utf-8-sig"))

COUNT_FIELDS=("audio_outputs","audio_default_count","audio_active","usb_devices",
              "usb_interfaces","serial_nodes","usbtmc_signatures",
              "usb_devnodes","usb_descriptor_unreadable")
def validate(r):
    for key in ("audio_status","usb_status"):
        if r.get(key) not in ("OBSERVED","PARTIAL","UNAVAILABLE"):
            raise ValueError("BAD_STATUS")
    for key in COUNT_FIELDS:
        v=r.get(key)
        if v is not None and (type(v) is not int or not 0<=v<=LIMIT):
            raise ValueError("BAD_COUNT_"+key)
    for key in ("audio_truncated","em_listing_truncated"):
        v=r.get(key)
        if v is not None and type(v) is not bool:
            raise ValueError("BAD_FLAG")
    if r.get("audio_status")=="UNAVAILABLE" and r.get("audio_outputs") is not None:
        raise ValueError("UNAVAILABLE_NOT_NULL")
    if r.get("audio_status")=="OBSERVED" and r.get("audio_outputs") is None:
        raise ValueError("OBSERVED_WITHOUT_COUNT")
    for key in ("audio_active","audio_default_count"):
        if r.get(key) is not None and (r.get("audio_outputs") is None or r[key]>r["audio_outputs"]):
            raise ValueError("AUDIO_COUNT_CONTRADICTION")
    if r.get("usb_status")=="UNAVAILABLE" and any(r.get(k) is not None for k in
            ("usb_devices","usb_interfaces","usb_devnodes","usbtmc_signatures")):
        raise ValueError("UNAVAILABLE_USB_NOT_NULL")
    if r.get("usb_status")!="UNAVAILABLE" and r.get("usbtmc_signatures") is None:
        raise ValueError("OBSERVED_USB_WITHOUT_COUNT")
    for key in ("usb_interfaces","usb_devnodes"):
        if r.get(key) is not None and r.get("usbtmc_signatures") is not None and r["usbtmc_signatures"]>r[key]:
            raise ValueError("USB_COUNT_CONTRADICTION")
    return r

class Tests(unittest.TestCase):
    # Parser/schema unit tests only. No fabricated instrument or measured data.
    def test_basic_signature(self): self.assertTrue(is_usbtmc(254,3,0))
    def test_usb488_signature(self): self.assertTrue(is_usbtmc(254,3,1))
    def test_other_class(self): self.assertFalse(is_usbtmc(255,3,0))
    def test_other_subclass(self): self.assertFalse(is_usbtmc(254,2,0))
    def test_other_protocol(self): self.assertFalse(is_usbtmc(254,3,2))
    def test_empty_pcm(self): self.assertEqual(pcm_playback_count(""),0)
    def test_pcm_parser(self):
        self.assertEqual(pcm_playback_count("00-00: parser : playback 2 : capture 1\n00-01: parser : capture 1"),1)
    def test_bad_status(self):
        with self.assertRaises(ValueError): validate({"audio_status":"UNKNOWN","usb_status":"UNAVAILABLE"})
    def test_unavailable(self):
        self.assertEqual(validate({"audio_status":"UNAVAILABLE","usb_status":"UNAVAILABLE"})["audio_status"],"UNAVAILABLE")
    def test_negative(self):
        with self.assertRaises(ValueError): validate({"audio_status":"OBSERVED","usb_status":"UNAVAILABLE","audio_outputs":-1})
    def test_boolean_count(self):
        with self.assertRaises(ValueError): validate({"audio_status":"OBSERVED","usb_status":"UNAVAILABLE","audio_outputs":True})
    def test_inconsistent_audio(self):
        with self.assertRaises(ValueError): validate({"audio_status":"OBSERVED","usb_status":"UNAVAILABLE","audio_outputs":0,"audio_active":1})
    def test_inconsistent_usb(self):
        with self.assertRaises(ValueError): validate({"audio_status":"UNAVAILABLE","usb_status":"OBSERVED","usb_interfaces":1,"usbtmc_signatures":2})
    def test_unknown_not_zero(self):
        with self.assertRaises(ValueError): validate({"audio_status":"UNAVAILABLE","usb_status":"UNAVAILABLE","audio_outputs":0})

def main():
    p=argparse.ArgumentParser()
    p.add_argument("repo",nargs="?")
    p.add_argument("--selftest",action="store_true")
    args=p.parse_args()
    test=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
    if not test.wasSuccessful(): return 1
    if args.selftest: return 0
    system=platform.system()
    pins=0
    if system=="Darwin":
        if not args.repo: p.error("repo required on macOS")
        inventory,pins=mac_inventory(pathlib.Path(args.repo).resolve(strict=True))
        sources="COREAUDIO_IOKIT_REGISTRY"
    elif system=="Linux":
        inventory=linux_inventory()
        sources="PROC_ASOUND_SYSFS"
    elif system=="Windows":
        inventory=windows_inventory()
        sources="RENDER_REGISTRY_PRESENT_PNP"
    else:
        raise SystemExit("UNSUPPORTED_OS")
    validate(inventory)
    status=("PASS_READONLY_METADATA" if inventory["audio_status"]=="OBSERVED"
            and inventory["usb_status"]=="OBSERVED"
            and inventory.get("serial_status","OBSERVED")=="OBSERVED"
            and not inventory.get("audio_truncated")
            and not inventory.get("em_listing_truncated") else "PARTIAL_OR_UNAVAILABLE")
    print("BUREAU_REPORT="+json.dumps({
        "schema":"freqmed.gen-platform-01.v1","platform":system,
        "machine":platform.machine(),"source_pins_verified":pins,
        "software_tests":test.testsRun,"inventory_source":sources,
        "inventory":inventory,"inventory_verdict":status,
        "hardware_qualified":False,"instrument_commands_sent":0,
        "physical_output":"NOT_PERFORMED","physical_measurement":"NOT_PERFORMED",
        "certification":"NOT_ISSUED","authorization":"NONE"
    },sort_keys=True))
    return 0
if __name__=="__main__":
    raise SystemExit(main())
