#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""BENCH-03: native property-listener and offline buffer lifecycle."""
import hashlib, importlib.util, json, pathlib, platform, subprocess, sys, tempfile
ROOT=pathlib.Path(__file__).resolve().parent
OWN={"lifecycle.h":"73a5b79606aada3e76b66e12c4c04142a92ac4b3","lifecycle.c":"c0214616a535f08f538da668c72b6b85f6fb0dc5","test_lifecycle.c":"3033cfc8c58ffd791dd9644f400abde0344b31bc","mac_lifecycle.c":"b9b0a4b8e59e85227956c7f39a6473d4908bca78"}
PINS=[
 ("cf797bff3a71e0d790fc7a0a01856200a8becf93","generator/candidates/BENCH-02/preflight.py","6102507fcc232d7e3689466ad55c5a82627611fc"),
 ("cf797bff3a71e0d790fc7a0a01856200a8becf93","generator/candidates/BENCH-02/mac_preflight.c","3c9835a4d9a0bba241405924ece79c451c7a9a83"),
 ("c5da76be8f33cd9e927772e6cc492745d180bebd","generator/candidates/BENCH-01/mac_bench.c","1f488aafa231e33b6866285cc6dbd84e2651adb9"),
 ("0412c0fbe2b54298a3b1dd346c78d3b56dda0e63","generator/candidates/GEN-EM-01/native/em_hardware_discovery.h","478c2c7bb624325946da39751fefc342fdf07188")]
def verify(data,pin):
    if hashlib.sha1(("blob %d"%len(data)).encode()+b"\0"+data).hexdigest()!=pin:raise RuntimeError("BLOB_MISMATCH "+pin)
    return data
def prefix(data,marker):
    s=data.decode("utf-8")
    if s.count(marker)!=1:raise RuntimeError("PREFIX_BOUNDARY")
    return s.split(marker,1)[0]
def main():
    if platform.system()!="Darwin" or len(sys.argv)!=2:raise SystemExit("USAGE_MAC: python3 -B qualify.py REPO")
    repo=pathlib.Path(sys.argv[1]).resolve(strict=True)
    with tempfile.TemporaryDirectory(prefix="freqmed_bench03_") as t:
        w=pathlib.Path(t)
        for n,p in OWN.items():(w/n).write_bytes(verify((ROOT/n).read_bytes(),p))
        for ref,path,pin in PINS:
            data=verify(subprocess.check_output(["git","-C",str(repo),"show",ref+":"+path],timeout=30),pin)
            name=pathlib.Path(path).name
            if name=="mac_bench.c":(w/"bench01_prefix.inc").write_text(prefix(data,"int main(void){"),encoding="utf-8")
            elif name=="mac_preflight.c":(w/"bench02_prefix.inc").write_text(prefix(data,"int main(void){"),encoding="utf-8")
            else:(w/name).write_bytes(data)
        print("BENCH03_SOURCE_PINS=8/8 PASS",flush=True)
        spec=importlib.util.spec_from_file_location("bench02",w/"preflight.py")
        parent=importlib.util.module_from_spec(spec);spec.loader.exec_module(parent)
        cc=["/usr/bin/cc","-std=c11","-Wall","-Wextra","-Werror","-pedantic","-I",str(w)]
        print("BENCH03_UNCHANGED_C11_TESTS=NOT_REPEATED",flush=True)
        subprocess.run(cc+[str(w/"mac_lifecycle.c"),str(w/"lifecycle.c"),"-framework","CoreAudio","-framework","CoreFoundation","-o",str(w/"native")],check=True,timeout=120)
        proc=subprocess.run([str(w/"native")],capture_output=True,text=True,timeout=20)
        lines=proc.stdout.splitlines()
        # Never disclose raw UIDs even on malformed native output.
        if not lines or not lines[-1].startswith("END\t"):raise RuntimeError("NATIVE_RECEIPT_MISSING")
        if len(lines)<2 or not lines[-2].startswith("DIAG\t"):raise RuntimeError("NATIVE_DIAGNOSTIC_MISSING")
        d=lines[-2].split("\t")
        if len(d)!=8 or d[1] not in {"DEFAULT_ENDPOINTS","PROPERTY_SUBSCRIPTIONS","FIRST_SNAPSHOT","BUFFER_DIMENSIONS","MEMORY_ALLOCATION","OBSERVATION_SLEEP","SECOND_SNAPSHOT","COMPLETE"}:raise RuntimeError("NATIVE_DIAGNOSTIC_INVALID")
        inf,inc,outf,outc,irun,orun=map(int,d[2:])
        diag=dict(stage=d[1],input_frames=inf,input_channels=inc,output_frames=outf,output_channels=outc,input_running=irun,output_running=orun)
        print("BENCH03_NATIVE_DIAGNOSTIC="+json.dumps(diag,sort_keys=True),flush=True)
        end=lines[-1].split("\t")
        if len(end)!=9:raise RuntimeError("NATIVE_RECEIPT_INVALID")
        registered,removed,events,completed,reserved,iv,ov,closed=map(int,end[1:])
        receipt={"registered":registered,"removed":removed,"property_callbacks":events,"buffer_reservation":bool(reserved),
                 "input_values_reserved":iv,"output_values_reserved":ov,"memory_released":closed==1}
        print("BENCH03_RESOURCE_RECEIPT="+json.dumps(receipt,sort_keys=True),flush=True)
        if proc.returncode or registered!=16 or removed!=registered or completed!=1 or reserved!=1 or closed!=1:
            print("BENCH03_NATIVE_RESOURCE_LIFECYCLE=BLOCK",flush=True)
            raise SystemExit(75)
        if len(lines)!=8 or lines[0]!="BEGIN_FIRST" or lines[3]!="BEGIN_SECOND":raise RuntimeError("NATIVE_SNAPSHOT_BOUNDARY")
        a,b=parent.parse("\n".join(lines[1:3])),parent.parse("\n".join(lines[4:6]))
        report=parent.assess(a,b)
        dimensions=all(b[k]["buffer_frames"] is not None and b[k]["channels"] is not None for k in ("I","O"))
        sizes_match=dimensions and iv==b["I"]["buffer_frames"]*b["I"]["channels"] and ov==b["O"]["buffer_frames"]*b["O"]["channels"]
        good=report["binding"]=="READONLY_PAIR_CANDIDATE" and events==0 and sizes_match and irun==0 and orun==0
        busy=irun==1 or orun==1 or any(p[k]["running_somewhere"] is True for p in (a,b) for k in ("I","O"))
        unknown=irun not in (0,1) or orun not in (0,1) or any(p[k]["running_somewhere"] is None for p in (a,b) for k in ("I","O"))
        reason=("NONE" if good else "DEVICE_BUSY" if busy else "DEVICE_ACTIVITY_UNKNOWN" if unknown else
                "PROPERTY_NOTIFICATION" if events else "METADATA_CHANGED" if a!=b else
                "DIMENSIONS_MISMATCH" if not sizes_match else "PAIR_NOT_ELIGIBLE")
        report["binding_block_reason"]=reason
        report["reservation_scope"]="PROCESS_HEAP_ONLY"
        report.update(schema="freqmed.bench-03.v1",resources=receipt,dimensions_match=bool(sizes_match),
                      binding="CLOSED_STABLE_METADATA_RESERVATION" if good else "INVALIDATED_OR_UNSTABLE",
                      observation_seconds_requested=0.25,actual_change_witnessed=events>0,
                      callback_scope="PROPERTY_NOTIFICATION_ONLY",audio_ioproc_registered=False,
                      independent_stop="NOT_VERIFIED",verdict="READONLY_LIFECYCLE_ONLY")
        print("BENCH03_REPORT="+json.dumps(report,sort_keys=True,allow_nan=False),flush=True)
        print("BENCH03_NATIVE_RESOURCE_LIFECYCLE=PASS",flush=True)
        print("BENCH03_BINDING="+("PASS" if good else "BLOCK_"+reason),flush=True)
        if not good:raise SystemExit(75)
if __name__=="__main__":main()
