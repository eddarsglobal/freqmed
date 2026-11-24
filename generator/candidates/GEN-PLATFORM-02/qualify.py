#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Read-only capabilities, not a physical calibration or authority."""
import argparse
import hashlib
import json
import math
import os
import pathlib
import platform
import re
import subprocess
import tempfile
import unittest

OWN=pathlib.Path(__file__).resolve().parent
BASE="generator/candidates/"
AC="54fd4e6cd4a8106da12bb57fa8208ce569a4185b"
EM="0412c0fbe2b54298a3b1dd346c78d3b56dda0e63"
PREV="0fa5c3962f8b34d96c19f4711ce5dbd252e1aa24"
PINS=[
 (AC,"GEN-R66/native/audio_devices.h","3bab6eef1608612f67550f90757791ea893c4a21"),
 (AC,"GEN-R66/native/audio_devices_macos.c","0ba4c6015786a3a263533036ca1025b7d2db2d09"),
 (EM,"GEN-EM-01/native/em_hardware_discovery.h","478c2c7bb624325946da39751fefc342fdf07188"),
 (EM,"GEN-EM-01/native/em_hardware_discovery_macos.c","5097b9f45252d01fb51f80a71918219f08912cd5"),
 (PREV,"GEN-PLATFORM-01/windows_probe.ps1","c91abec37368d3ffe2c72a4c1211a978609c0ec2"),
]
LIMIT=4096
def read(path,limit=65536):
    with path.open("rb") as f: data=f.read(limit+1)
    if len(data)>limit: raise ValueError("METADATA_LIMIT")
    return data.decode("utf-8")
def entries(path):
    result=[]
    with os.scandir(path) as it:
        for item in it:
            if len(result)>=LIMIT: raise ValueError("SCAN_LIMIT")
            result.append(pathlib.Path(item.path))
    return sorted(result)
def pcm_rows(text):
    rows=[]
    for line in text.splitlines():
        m=re.match(r"^(\d+)-(\d+):",line)
        if m and re.search(r"\bplayback\s+[1-9]\d*\b",line):
            rows.append((int(m[1]),int(m[2])))
    if len(rows)>32 or len(set(rows))!=len(rows): raise ValueError("PCM_BOUND_OR_DUPLICATE")
    return rows
def parse_hw(text):
    c=re.search(r"^channels:\s*([0-9]+)\s*$",text,re.M)
    r=re.search(r"^rate:\s*([0-9]+)(?:\s+\([0-9]+/[0-9]+\))?\s*$",text,re.M)
    if not c or not r: return None
    channels,rate=int(c[1]),int(r[1])
    if not 1<=channels<=256 or not 1<=rate<=10000000: return None
    return channels,rate
def linux_probe():
    out={"audio_status":"UNAVAILABLE","audio_profiles":None,
         "em_status":"UNAVAILABLE","em_candidates":None,"usbtmc_count":None,
         "serial_nodes":None}
    try:
        profiles=[]
        for card,dev in pcm_rows(read(pathlib.Path("/proc/asound/pcm"))):
            base=pathlib.Path("/proc/asound")/("card%d"%card)/("pcm%dp"%dev)
            formats=set()
            incomplete=False
            try:
                for sub in entries(base):
                    if not re.fullmatch(r"sub\d+",sub.name): continue
                    try:
                        data=read(sub/"hw_params")
                        fmt=parse_hw(data)
                        if fmt: formats.add(fmt)
                        elif data.strip()!="closed": incomplete=True
                    except (OSError,ValueError): incomplete=True
            except (OSError,ValueError): incomplete=True
            fmt=next(iter(formats)) if len(formats)==1 and not incomplete else None
            profiles.append({"index":len(profiles)+1,
                "channels":fmt[0] if fmt else None,"sample_rate_hz":fmt[1] if fmt else None,
                "format_source":"LINUX_EXISTING_PCM_STREAM" if fmt else "UNKNOWN",
                "transport":"UNKNOWN","default":None})
        out.update(audio_status="OBSERVED",audio_profiles=profiles)
    except (OSError,ValueError): pass
    try:
        n=missing=0
        candidates=[]
        for p in entries(pathlib.Path("/sys/bus/usb/devices")):
            if not re.fullmatch(r"\d+-\d+(?:\.\d+)*:\d+\.\d+",p.name): continue
            try:
                codes=tuple(int(read(p/k,32).strip(),16) for k in
                    ("bInterfaceClass","bInterfaceSubClass","bInterfaceProtocol"))
                if any(not 0<=v<=255 for v in codes): raise ValueError("BYTE")
            except (OSError,ValueError):
                missing+=1
                continue
            if codes not in ((254,3,0),(254,3,1)): continue
            n+=1
            if len(candidates)>=24: continue
            vid=pid=None
            try:
                parent=p.resolve(strict=True).parent
                v=int(read(parent/"idVendor",32).strip(),16)
                q=int(read(parent/"idProduct",32).strip(),16)
                if 0<=v<=65535 and 0<=q<=65535: vid,pid=v,q
            except (OSError,ValueError): pass
            candidates.append({"index":len(candidates)+1,"transport":"USBTMC",
                "protocol":codes[2],"vendor_id":vid,"product_id":pid})
        out.update(em_status="PARTIAL" if missing or n>24 else "OBSERVED",
                   em_candidates=candidates,usbtmc_count=n)
    except (OSError,ValueError): pass
    try:
        out["serial_nodes"]=sum(1 for p in entries(pathlib.Path("/sys/class/tty"))
                                if (p/"device").exists())
    except (OSError,ValueError): pass
    return out
def extract(repo,work,pins):
    for ref,path,digest in pins:
        data=subprocess.check_output(["git","-C",str(repo),"show",ref+":"+BASE+path],timeout=30)
        if hashlib.sha1(("blob %d"%len(data)).encode()+b"\0"+data).hexdigest()!=digest:
            raise ValueError("SOURCE_PIN_MISMATCH")
        (work/pathlib.Path(path).name).write_bytes(data)
    return len(pins)
def native(repo,system):
    if system=="Linux": return linux_probe(),0
    with tempfile.TemporaryDirectory(prefix="freqmed_cap02_") as t:
        work=pathlib.Path(t)
        if system=="Darwin":
            n=extract(repo,work,PINS[:4])
            exe=work/"probe"
            subprocess.run(["cc","-std=c11","-Wall","-Wextra","-Werror","-I",str(work),
                str(OWN/"mac_capabilities.c"),str(work/"audio_devices_macos.c"),
                str(work/"em_hardware_discovery_macos.c"),"-framework","CoreAudio",
                "-framework","CoreFoundation","-framework","IOKit","-o",str(exe)],
                check=True,timeout=90)
            return json.loads(subprocess.check_output([str(exe)],timeout=30)),n
        if system=="Windows":
            n=extract(repo,work,PINS[4:])
            exe=work/"probe.exe"
            subprocess.run([os.environ.get("CXX","g++"),"-std=c++17","-Wall","-Wextra",
                str(OWN/"windows_audio.cpp"),"-lole32","-luuid","-o",str(exe)],
                check=True,timeout=90)
            audio=json.loads(subprocess.check_output([str(exe)],timeout=30))
            ps=pathlib.Path(os.environ.get("SystemRoot",r"C:\Windows"))/"System32"/"WindowsPowerShell"/"v1.0"/"powershell.exe"
            em=json.loads(subprocess.check_output([str(ps),"-NoProfile","-NonInteractive",
                "-File",str(work/"windows_probe.ps1")],timeout=180).decode("utf-8-sig"))
            count=em.get("usbtmc_signatures")
            # Prior Windows collector exposes counts only, not per-interface identities.
            return {"audio_status":"OBSERVED","audio_profiles":audio,
                "em_status":"UNAVAILABLE" if count is None else "PARTIAL",
                "em_candidates":None,"usbtmc_count":count,
                "serial_nodes":em.get("serial_nodes")},n
    raise ValueError("UNSUPPORTED_OS")
def integer(value,lo,hi):
    return type(value) is int and lo<=value<=hi
FORMATS={"COREAUDIO_NOMINAL","LINUX_EXISTING_PCM_STREAM","WINDOWS_SHARED_DEVICE_FORMAT","UNKNOWN"}
TRANSPORTS={"BUILT_IN","USB","BLUETOOTH","VIRTUAL","AGGREGATE","OTHER_OS_REPORTED","UNKNOWN"}
def validate(r):
    for status in ("audio_status","em_status"):
        if r.get(status) not in ("OBSERVED","PARTIAL","UNAVAILABLE"): raise ValueError("STATUS")
    a=r.get("audio_profiles")
    if r["audio_status"]=="UNAVAILABLE":
        if a is not None: raise ValueError("AUDIO_UNAVAILABLE")
    elif not isinstance(a,list) or len(a)>32: raise ValueError("AUDIO_LIST")
    for i,p in enumerate(a or [],1):
        if set(p)!={"index","channels","sample_rate_hz","format_source","transport","default"}:
            raise ValueError("AUDIO_FIELDS")
        if not integer(p["index"],i,i) or p["transport"] not in TRANSPORTS or p["format_source"] not in FORMATS:
            raise ValueError("AUDIO_METADATA")
        if p["default"] is not None and type(p["default"]) is not bool: raise ValueError("DEFAULT")
        c,f=p["channels"],p["sample_rate_hz"]
        if p["format_source"]=="UNKNOWN":
            if c is not None or f is not None: raise ValueError("UNKNOWN_FORMAT")
        elif not integer(c,1,256) or type(f) not in (int,float) or not math.isfinite(f) or not 0<f<=10000000:
            raise ValueError("FORMAT")
    for key in ("serial_nodes","usbtmc_count"):
        if r.get(key) is not None and not integer(r[key],0,LIMIT): raise ValueError("COUNT")
    e,n=r.get("em_candidates"),r.get("usbtmc_count")
    if r["em_status"]=="UNAVAILABLE":
        if e is not None or n is not None: raise ValueError("EM_UNAVAILABLE")
    elif n is None: raise ValueError("EM_COUNT")
    if r["em_status"]=="OBSERVED" and (not isinstance(e,list) or len(e)!=n):
        raise ValueError("EM_COMPLETE")
    if e is not None:
        if not isinstance(e,list) or len(e)>24 or n is None or len(e)>n: raise ValueError("EM_LIST")
        for i,p in enumerate(e,1):
            if set(p)!={"index","transport","protocol","vendor_id","product_id"}:
                raise ValueError("EM_FIELDS")
            if not integer(p["index"],i,i) or p["transport"]!="USBTMC" or not integer(p["protocol"],0,1):
                raise ValueError("EM_METADATA")
            v,q=p["vendor_id"],p["product_id"]
            if not ((v is None and q is None) or (integer(v,0,65535) and integer(q,0,65535))):
                raise ValueError("EM_IDS")
    return r

class Tests(unittest.TestCase):
    # Software parser/schema vectors only; not physical observations.
    def base(self):
        return {"audio_status":"OBSERVED","audio_profiles":[],"em_status":"OBSERVED",
                "em_candidates":[],"usbtmc_count":0,"serial_nodes":None}
    def test_empty(self): self.assertEqual(validate(self.base()),self.base())
    def test_pcm(self): self.assertEqual(pcm_rows("00-02: x : playback 1\n00-03: x : capture 1"),[(0,2)])
    def test_closed(self): self.assertIsNone(parse_hw("closed"))
    def test_params(self): self.assertEqual(parse_hw("channels: 2\nrate: 48000 (48000/1)\n"),(2,48000))
    def test_missing_rate(self): self.assertIsNone(parse_hw("channels: 2\n"))
    def test_invalid_channels(self): self.assertIsNone(parse_hw("channels: 0\nrate: 48000\n"))
    def test_duplicate_pcm(self):
        with self.assertRaises(ValueError): pcm_rows("00-02: playback 1\n00-02: playback 1")
    def test_missing_status(self):
        with self.assertRaises(ValueError): validate({})
    def test_unknown_audio(self):
        r=self.base();r.update(audio_status="UNAVAILABLE",audio_profiles=None);validate(r)
    def test_bad_audio(self):
        r=self.base();r.update(audio_status="UNAVAILABLE")
        with self.assertRaises(ValueError): validate(r)
    def audio(self):
        return {"index":1,"channels":None,"sample_rate_hz":None,"format_source":"UNKNOWN","transport":"UNKNOWN","default":None}
    def test_unknown_format(self):
        r=self.base();r["audio_profiles"]=[self.audio()];validate(r)
    def test_unknown_format_has_rate(self):
        r=self.base();a=self.audio();a["sample_rate_hz"]=1;r["audio_profiles"]=[a]
        with self.assertRaises(ValueError): validate(r)
    def test_boolean_channels(self):
        r=self.base();a=self.audio();a.update(channels=True,sample_rate_hz=1,format_source="COREAUDIO_NOMINAL");r["audio_profiles"]=[a]
        with self.assertRaises(ValueError): validate(r)
    def test_nan(self):
        r=self.base();a=self.audio();a.update(channels=1,sample_rate_hz=float("nan"),format_source="COREAUDIO_NOMINAL");r["audio_profiles"]=[a]
        with self.assertRaises(ValueError): validate(r)
    def test_em_count(self):
        r=self.base();r["usbtmc_count"]=1
        with self.assertRaises(ValueError): validate(r)
    def test_partial_count(self):
        r=self.base();r.update(em_status="PARTIAL",em_candidates=None,usbtmc_count=1);validate(r)
    def test_em_bad_ids(self):
        r=self.base();r.update(usbtmc_count=1,em_candidates=[{"index":1,"transport":"USBTMC","protocol":0,"vendor_id":1,"product_id":None}])
        with self.assertRaises(ValueError): validate(r)
    def test_em_unknown_not_zero(self):
        r=self.base();r.update(em_status="UNAVAILABLE",em_candidates=None)
        with self.assertRaises(ValueError): validate(r)
def main():
    p=argparse.ArgumentParser()
    p.add_argument("repo",nargs="?")
    p.add_argument("--selftest",action="store_true")
    a=p.parse_args()
    tests=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
    if not tests.wasSuccessful(): return 1
    if a.selftest:return 0
    system=platform.system()
    if system not in ("Darwin","Linux","Windows"): raise SystemExit("UNSUPPORTED_OS")
    if system!="Linux" and not a.repo: p.error("repo required for pinned native sources")
    r,n=native(pathlib.Path(a.repo or ".").resolve(strict=True),system)
    validate(r)
    print("BUREAU_REPORT="+json.dumps({"schema":"freqmed.gen-platform-02.v1",
        "platform":system,"machine":platform.machine(),"software_tests":tests.testsRun,
        "source_pins_verified":n,"profiles":r,"verdict":"PASS_PROFILE_SCHEMA_ONLY",
        "hardware_qualified":False,"physical_frequency_limits":None,
        "physical_output":"NOT_PERFORMED","physical_measurement":"NOT_PERFORMED",
        "instrument_commands_sent":0,"certification":"NOT_ISSUED","authorization":"NONE"},
        sort_keys=True,allow_nan=False))
    return 0
if __name__=="__main__":raise SystemExit(main())
