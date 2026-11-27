#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""BENCH-01: real read-only discovery, never a physical admission decision."""
import hashlib
import json
import math
import pathlib
import platform
import re
import subprocess
import sys
import tempfile
import time

EM_REF = "0412c0fbe2b54298a3b1dd346c78d3b56dda0e63"
EM_PINS = {"em_hardware_discovery.h": "478c2c7bb624325946da39751fefc342fdf07188",
           "em_hardware_discovery_macos.c": "5097b9f45252d01fb51f80a71918219f08912cd5"}
ROUTES = {"BUILT_IN", "USB", "VIRTUAL", "AGGREGATE", "BLUETOOTH", "OTHER", "UNKNOWN"}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def parse_mac(text):
    audio, usb, em = [], [], None
    seen = set()
    for line in text.splitlines():
        p = line.split("\t")
        if p[0] == "A" and len(p) == 11:
            ident, ic, oc, di, do, clock, alive = map(int, [p[1], *p[3:7], *p[8:10]])
            rate = float(p[7])
            if (ident <= 0 or ident in seen or p[2] not in ROUTES or not -1 <= ic <= 256 or not -1 <= oc <= 256
                    or di not in (0, 1) or do not in (0, 1) or not math.isfinite(rate) or rate < 0
                    or not -1 <= clock <= 4294967295 or alive not in (-1, 0, 1)):
                raise ValueError("INVALID_AUDIO_METADATA")
            seen.add(ident)
            uid = None if p[10] == "-" else bytes.fromhex(p[10])
            if uid is not None and not 1 <= len(uid) <= 1023:
                raise ValueError("INVALID_UID")
            audio.append(dict(os_id=ident, identity_sha256=digest(uid) if uid else None,
                              route=p[2], input_channels=ic if ic >= 0 else None,
                              output_channels=oc if oc >= 0 else None, default_input=bool(di),
                              default_output=bool(do), nominal_rate_hz=rate or None,
                              clock_domain=clock if clock >= 0 else None, alive=bool(alive) if alive >= 0 else None))
        elif p[0] == "E" and em is None:
            if p == ["E", "UNKNOWN"]:
                em = {"status": "UNKNOWN"}
            elif len(p) == 6:
                a, b, c, d, tr = map(int, p[1:])
                if not all(0 <= x <= 4096 for x in (a,b,c,d)) or d>b or tr not in (0,1):
                    raise ValueError("INVALID_USB_METADATA")
                em = dict(status="REGISTRY_OBSERVED", usb_devices=a, usb_interfaces=b,
                          serial_callout_nodes=c, usbtmc_interfaces=d, truncated=bool(tr))
            else:
                raise ValueError("INVALID_EM_ROW")
        elif p[0] == "U" and len(p) == 5 and em and em["status"] == "REGISTRY_OBSERVED":
            v, d, proto, known = map(int, p[1:])
            if proto not in (0,1) or known not in (0,1) or (known and not (0<=v<=65535 and 0<=d<=65535)):
                raise ValueError("INVALID_USBTMC_ROW")
            usb.append(dict(vendor_id=v if known else None, product_id=d if known else None, protocol=proto))
        else:
            raise ValueError("INVALID_ROW")
    if not audio or len(audio)>256 or em is None or sum(x["default_input"] for x in audio)!=1 or sum(x["default_output"] for x in audio)!=1:
        raise ValueError("INCOMPLETE_INVENTORY")
    if em["status"] == "REGISTRY_OBSERVED" and (len(usb)!=min(24,em["usbtmc_interfaces"]) or em["truncated"]!=(em["usbtmc_interfaces"]>24)):
        raise ValueError("INCOMPLETE_USB_INVENTORY")
    return {"audio": sorted(audio,key=lambda a:a["os_id"]), "em":em, "usbtmc":sorted(usb,key=lambda x:json.dumps(x,sort_keys=True))}


def read_hex(path):
    try:
        s=path.read_text(encoding="ascii").strip()
        return int(s,16) if re.fullmatch(r"[0-9a-fA-F]{2}",s) else None
    except (OSError, UnicodeError):
        return None


def linux_inventory():
    sound=pathlib.Path("/sys/class/sound")
    usb=pathlib.Path("/sys/bus/usb/devices")
    audio=[]; candidates=[]; missing=0
    if sound.is_dir():
        for p in sorted(sound.iterdir()):
            m=re.fullmatch(r"pcmC(\d+)D(\d+)([cp])",p.name)
            if m:
                audio.append({"os_endpoint":p.name,"direction":"INPUT" if m[3]=="c" else "OUTPUT",
                              "card_index":int(m[1]),"device_index":int(m[2]),"identity_sha256":None})
    if usb.is_dir():
        for p in sorted(usb.iterdir()):
            if ":" not in p.name:continue
            vals=[read_hex(p/k) for k in ("bInterfaceClass","bInterfaceSubClass","bInterfaceProtocol")]
            if None in vals:missing+=1
            elif vals[:2]==[254,3] and vals[2] in (0,1):
                candidates.append({"protocol":vals[2]})
    return {"audio":audio,"audio_status":"SYSFS_OBSERVED" if sound.is_dir() else "UNAVAILABLE",
            "em":{"status":"SYSFS_OBSERVED" if usb.is_dir() else "UNAVAILABLE","unreadable_interfaces":missing},"usbtmc":candidates}


def mac_inventory(repo):
    with tempfile.TemporaryDirectory(prefix="freqmed_bench01_") as t:
        work=pathlib.Path(t)
        for name,pin in EM_PINS.items():
            data=subprocess.check_output(["git","-C",str(repo),"show",EM_REF+":generator/candidates/GEN-EM-01/native/"+name],timeout=30)
            if hashlib.sha1(("blob %d"%len(data)).encode()+b"\0"+data).hexdigest()!=pin:
                raise RuntimeError("PIN_MISMATCH "+name)
            (work/name).write_bytes(data)
        source=pathlib.Path(__file__).resolve().parent/"mac_bench.c"
        exe=work/"bench"
        subprocess.run(["/usr/bin/cc","-std=c11","-Wall","-Wextra","-Werror","-pedantic","-I",str(work),str(source),str(work/"em_hardware_discovery_macos.c"),"-framework","CoreAudio","-framework","CoreFoundation","-framework","IOKit","-o",str(exe)],check=True,timeout=120)
        return [parse_mac(subprocess.check_output([str(exe)],text=True,timeout=30)) for _ in range(2)]


def assess(first,second,system):
    stable=first==second
    pairs=[]
    if system=="Darwin" and stable:
        audio=second["audio"]
        for out in audio:
            if not (out["default_output"] and out["alive"] is True and out["output_channels"] and out["route"] in {"BUILT_IN","USB"} and out["identity_sha256"]):continue
            for inp in audio:
                if inp["alive"] is True and inp["input_channels"] and inp["route"]=="USB" and inp["identity_sha256"] and inp["identity_sha256"]!=out["identity_sha256"]:
                    a,b=out["clock_domain"],inp["clock_domain"]
                    pairs.append({"output_identity":out["identity_sha256"],"input_identity":inp["identity_sha256"],
                                  "clock_domains_distinct_reported":bool(a and b and a!=b),"status":"CANDIDATE_ONLY"})
    return {"schema":"freqmed.bench-01.v1","platform":system,"machine":platform.machine(),
            "metadata_stable_across_two_captures":stable,"inventory":second,"separate_usb_input_candidates":pairs,
            "independent_measurement":"NOT_VERIFIED","calibration":"NOT_VERIFIED","physical_limits":"NOT_MEASURED",
            "independent_stop":"NOT_VERIFIED","em_generator":"NOT_QUALIFIED","hardware_qualified":False,
            "physical_output":"NOT_PERFORMED","physical_measurement":"NOT_PERFORMED","microphone_stream_opened":False,
            "authorization":"NONE","certification":"NOT_ISSUED","verdict":"READONLY_INVENTORY_ONLY"}


def tests():
    # Parser/contract vectors only: not instrument readings and never included in inventory.
    a="A\t1\tBUILT_IN\t1\t2\t1\t1\t44100\t0\t1\t6161\nE\t0\t0\t0\t0\t0\n"
    b=a.replace("E\t", "A\t2\tUSB\t1\t0\t0\t0\t44100\t3\t1\t6262\nE\t")
    x,y=parse_mac(a),parse_mac(b)
    def reject(s):
        try:parse_mac(s)
        except ValueError:return True
        return False
    r=assess(y,y,"Darwin")
    checks={"metadata_parsed":x["audio"][0]["nominal_rate_hz"]==44100,
            "uid_hashed":x["audio"][0]["identity_sha256"]==digest(b"aa"),
            "integrated_not_independent":not assess(x,x,"Darwin")["separate_usb_input_candidates"],
            "separate_usb_candidate":len(r["separate_usb_input_candidates"])==1,
            "unknown_clock_not_distinct":not r["separate_usb_input_candidates"][0]["clock_domains_distinct_reported"],
            "unstable_denied":not assess(x,y,"Darwin")["separate_usb_input_candidates"],
            "hardware_not_qualified":r["hardware_qualified"] is False and r["authorization"]=="NONE",
            "duplicate_device_rejected":reject(a.replace("E\t",a.splitlines()[0]+"\nE\t")),
            "nonfinite_rejected":reject(a.replace("44100","nan")),
            "missing_default_rejected":reject(a.replace("\t1\t1\t44100","\t0\t1\t44100")),
            "usb_count_mismatch_rejected":reject(a.replace("E\t0\t0\t0\t0\t0","E\t1\t1\t0\t1\t0")),
            "unknown_em_distinct":parse_mac(a.splitlines()[0]+"\nE\tUNKNOWN\n")["em"]["status"]=="UNKNOWN"}
    print("BENCH01_SOFTWARE_CHECKS="+json.dumps(checks,sort_keys=True))
    if not all(checks.values()):raise SystemExit("BENCH01_SOFTWARE_FAIL")
    print("BENCH01_SOFTWARE_PASS=12/12")


def main():
    tests()
    if sys.argv[1:]==["--self-test"]:return
    system=platform.system()
    if system=="Darwin" and len(sys.argv)==2:
        first,second=mac_inventory(pathlib.Path(sys.argv[1]).resolve(strict=True))
    elif system=="Linux" and len(sys.argv)==1:
        first=linux_inventory();time.sleep(.05);second=linux_inventory()
    else:raise SystemExit("NATIVE_ADAPTER_NOT_IMPLEMENTED_OR_REPO_REQUIRED")
    print("BENCH01_REPORT="+json.dumps(assess(first,second,system),sort_keys=True,allow_nan=False))


if __name__=="__main__":main()
