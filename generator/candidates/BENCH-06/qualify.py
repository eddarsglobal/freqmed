#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""BENCH-06: targeted native stream descriptor and admission qualification."""
import hashlib, importlib.util, json, pathlib, platform, subprocess, sys, tempfile
ROOT=pathlib.Path(__file__).resolve().parent
OWN={"admission.py":"0152e6eb1bb07c9eef0f4808553db445e74a7e30","mac_admission.c":"6012da035a970feb0ae45667ca10a1141a0a4d73"}
PINS=[
 ("cf797bff3a71e0d790fc7a0a01856200a8becf93","generator/candidates/BENCH-02/preflight.py","6102507fcc232d7e3689466ad55c5a82627611fc"),
 ("cf797bff3a71e0d790fc7a0a01856200a8becf93","generator/candidates/BENCH-02/mac_preflight.c","3c9835a4d9a0bba241405924ece79c451c7a9a83"),
 ("c5da76be8f33cd9e927772e6cc492745d180bebd","generator/candidates/BENCH-01/mac_bench.c","1f488aafa231e33b6866285cc6dbd84e2651adb9"),
 ("0412c0fbe2b54298a3b1dd346c78d3b56dda0e63","generator/candidates/GEN-EM-01/native/em_hardware_discovery.h","478c2c7bb624325946da39751fefc342fdf07188"),
 ("732ef2a86a4ac85ad2fac4656f295fee27b131bc","generator/candidates/BENCH-05/mac_rt.c","6ff54e97335e5ac45e97681a0135cdc61083331c"),
 ("732ef2a86a4ac85ad2fac4656f295fee27b131bc","generator/candidates/BENCH-05/qualify.py","9f1ff0ac08c9c28a95cca12eba42fae626d6c49b")]
def verify(data,pin):
    if hashlib.sha1(("blob %d"%len(data)).encode()+b"\0"+data).hexdigest()!=pin:raise RuntimeError("BLOB_MISMATCH "+pin)
    return data
def prefix(data):
    s=data.decode();marker="int main(void){"
    if s.count(marker)!=1:raise RuntimeError("PREFIX_BOUNDARY")
    return s.split(marker,1)[0]
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
def main():
    if platform.system()!="Darwin" or len(sys.argv)!=2:raise SystemExit("USAGE_MAC: python3 -B qualify.py REPO")
    repo=pathlib.Path(sys.argv[1]).resolve(strict=True)
    with tempfile.TemporaryDirectory(prefix="freqmed_bench06_") as tmp:
        w=pathlib.Path(tmp)
        for name,pin in OWN.items():(w/name).write_bytes(verify((ROOT/name).read_bytes(),pin))
        for ref,path,pin in PINS:
            data=verify(subprocess.check_output(["git","-C",str(repo),"show",ref+":"+path],timeout=30),pin)
            if "/BENCH-05/" in path:continue  # provenance only; do not execute historical code
            name=pathlib.Path(path).name
            if name=="mac_bench.c":(w/"bench01_prefix.inc").write_text(prefix(data),encoding="utf-8")
            elif name=="mac_preflight.c":(w/"bench02_prefix.inc").write_text(prefix(data),encoding="utf-8")
            else:(w/name).write_bytes(data)
        print("BENCH06_SOURCE_PINS=8/8 PASS",flush=True)
        admission=load("admission",w/"admission.py")
        parent=load("preflight",w/"preflight.py")
        admission.self_test()
        exe=w/"native"
        subprocess.run(["/usr/bin/cc","-std=c11","-Wall","-Wextra","-Werror","-pedantic","-I",str(w),
                        str(w/"mac_admission.c"),"-framework","CoreAudio","-framework","CoreFoundation","-o",str(exe)],check=True,timeout=120)
        snapshots=[]
        for capture in range(2):
            proc=subprocess.run([str(exe)],capture_output=True,text=True,timeout=20)
            if proc.returncode:
                print("BENCH06_NATIVE_DESCRIPTOR_CAPTURE=BLOCK",flush=True);raise SystemExit(75)
            try:snapshots.append(admission.parse(proc.stdout,parent))
            except (ValueError,OverflowError):
                print("BENCH06_NATIVE_DESCRIPTOR_PARSE=BLOCK",flush=True);raise SystemExit(75) from None
        report=admission.assess(*snapshots,parent)
        print("BENCH06_REPORT="+json.dumps(report,sort_keys=True,allow_nan=False),flush=True)
        print("BENCH06_PHYSICAL_ADMISSION=HARD_DENIED",flush=True)
        print("BENCH06_NATIVE_DESCRIPTOR_CAPTURE="+("PASS" if report["metadata_stable"] else "BLOCK"),flush=True)
        if not report["metadata_stable"]:raise SystemExit(75)
if __name__=="__main__":main()
