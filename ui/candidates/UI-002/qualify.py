#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Assemble UI-002 from immutable UI-001, vendored uPlot and real native C samples."""
import hashlib,json,math,pathlib,platform,subprocess,sys,tempfile
AC="54fd4e6cd4a8106da12bb57fa8208ce569a4185b"
EM="0412c0fbe2b54298a3b1dd346c78d3b56dda0e63"
I1="d4ae3fa35412595a194c5f7c323cefb169722d19"
I2="1bd0fe8c8a07ca64301ee89e1d26b46a33d554a3"
B3="f20aa44d921c5455cd015eddb1bcde05549843a0"
M4="6da9688f384beb020fd7f311ce96dc29330de5db"
R5="19800411015599ab98c9b854024c0a125a4c7a4e"
E6="99ab2b85350961086a0a4ad856ebbded99547201"
R7="ef22815a739db53288d72890d6a3d217eb26417c"
A8="8a1b5ce4bc653c725bfe473dea7301a934907dff"
D9="ca86bb06b9f424716d277d4fa4a4998970062de6"
L10="6b2b3bf7eeb4d68cad0be4d9a83880862eb5e5c9"
U11="bd0fdd6f7817d06096b4befa5f99bc246f6000f0"
B12="ed957634a805ae330896499b7ce35d41c8913a3a"
PINS=[
 (AC,"GEN-R66/native/generator.h","9839f4390d9f17560cf6ef2447501a314f335773"),
 (AC,"GEN-R66/native/generator_core.c","80f35f7ec323a658699929a717d6d16ef74a3144"),
 (AC,"GEN-R66/native/output_hard_denied.c","715b0981fb961b180df9e9dcf508a7608a224270"),
 (EM,"GEN-EM-01/native/em_device_contract.h","d577e6c0f96fed003f767ee62ca74ff14e8ab69d"),
 (EM,"GEN-EM-01/native/em_device_contract.c","f09603278215d960f9c7df5cc1aa812bffe0d365"),
 (I1,"GEN-INTEGRATION-01/integration.h","490b09c4acb96ac9e857a6a55324c28c91c14f1f"),
 (I1,"GEN-INTEGRATION-01/integration.c","c7fc2c90ea4b64aa5a5c9f25e0b202991b01b627"),
 (I2,"GEN-INTEGRATION-02/session.h","2376cab6bda0afb65da3d26e463c3cefba5f039b"),
 (I2,"GEN-INTEGRATION-02/session.c","b674b1ba9b5baad7eed8f083efda1726d81ec6d9"),
 (I2,"GEN-INTEGRATION-02/session_clock.h","0bd6de2e64d51f46e9d705548f5b73f3d4f6691b"),
 (I2,"GEN-INTEGRATION-02/session_clock.c","2ff29e1b367fa7fe0982f9af58c9b233d0945230"),
 (B3,"GEN-PLATFORM-03/binding.h","f0c2cf430d59a46ffdf09938c86fea375d0a87f0"),
 (B3,"GEN-PLATFORM-03/binding.c","6c5194155ac8f6beaa782d0930b141bde6bdfa51"),
 (M4,"GEN-PLATFORM-04/monitor.h","ceebd9f876ba54788754c6b14b2bfdf5b288dedc"),
 (M4,"GEN-PLATFORM-04/monitor.c","3874ef72b7a597db14489c7cc384c7965dc00667"),
 (R5,"GEN-PLATFORM-05/recovery.h","13dfea669ce0a4409914b419521b2d704492aaf9"),
 (R5,"GEN-PLATFORM-05/recovery.c","42707299d531619b07ca1dba0288b5a41c1aaa54"),
 (R7,"GEN-PLATFORM-07/readiness.h","6cf37fdf6c67c53779215e2efac89ceda386050a"),
 (R7,"GEN-PLATFORM-07/readiness.c","f35962888553f03a8f3d193661ea5b5d2402ff8e"),
 (R7,"GEN-PLATFORM-07/mac_readiness.c","1dbb3d580dd7aec51048a7913012a4eb1fade2ae"),
 (A8,"GEN-PLATFORM-08/assembly.h","5fd071fe53c737bd1a8b744d6defcf0e9dfdbc14"),
 (A8,"GEN-PLATFORM-08/assembly.c","f508b864970512cdbc232bf831f222aa3cfe4fe1"),
 (D9,"GEN-PLATFORM-09/digital_signal.h","1c087aa661a238d0c69e592d47a6cea8dcc1d07e"),
 (D9,"GEN-PLATFORM-09/digital_signal.c","5239fc6f204fef96f84e09dee35ea74918f80d0c"),
]

BASE="e97bbe39c3a62ed53b7d99acb38d3eb40e814cfd"
BASE_BLOB="35d625e00f47bea44fe969841aa69d323ba572a5"
VENDOR={
 "uPlot.iife.min.js":"047f29b64f200a4a872758256e5e66930353d757",
 "uPlot.min.css":"a030d63f20dafd22c0edbd181002dade612c8f4a",
 "LICENSE-uPlot.txt":"cde4b3f8352d147d5e626fea36358797c4fc06f2",
}
ROOT=pathlib.Path(__file__).resolve().parent
def blob(data,pin):
    digest=hashlib.sha1(("blob %d"%len(data)).encode()+b"\0"+data).hexdigest()
    if digest!=pin:raise SystemExit("BLOB_MISMATCH "+pin)
    return data
def get(repo,ref,path,pin):
    return blob(subprocess.check_output(["git","-C",str(repo),"show",ref+":"+path],timeout=30),pin)
def replace_once(s,a,b):
    if s.count(a)!=1:raise SystemExit("UI_BASE_BOUNDARY_MISMATCH "+a[:80])
    return s.replace(a,b,1)
def export(repo):
    if platform.system()!="Darwin":return {"source":"UNAVAILABLE","reason":"NATIVE_ADAPTER_NOT_IMPLEMENTED"},0
    with tempfile.TemporaryDirectory(prefix="freqmed_ui002_") as tmp:
        w=pathlib.Path(tmp)
        for ref,path,pin in PINS:
            (w/pathlib.Path(path).name).write_bytes(get(repo,ref,"generator/candidates/"+path,pin))
        s=(w/"mac_readiness.c").read_text(encoding="utf-8")
        marker="static const char *verdict(FMReadinessResult r) {"
        if s.count(marker)!=1:raise SystemExit("COLLECTOR_BOUNDARY_MISMATCH")
        (w/"mac_capture_pinned.inc").write_text(s.split(marker,1)[0].removeprefix("#define _POSIX_C_SOURCE 200809L\n"),encoding="utf-8")
        names=["generator_core.c","output_hard_denied.c","em_device_contract.c","integration.c","session.c","session_clock.c","binding.c","monitor.c","recovery.c","readiness.c","assembly.c","digital_signal.c"]
        exe=w/"export"
        subprocess.run(["cc","-std=c11","-Wall","-Wextra","-Werror","-pedantic","-I",str(w),
           *[str(w/n) for n in names],str(ROOT/"digital_export.c"),"-lm","-framework","CoreAudio","-framework","CoreFoundation","-o",str(exe)],check=True,timeout=120)
        data=json.loads(subprocess.check_output([str(exe)],text=True,timeout=30))
        if data.get("source")=="FREQMED_NATIVE_C_MEMORY_ONLY":
            samples=data.get("samples",[])
            if not (data.get("physical_output") is False and data.get("physical_measurement") is False and
                data.get("count")==len(samples)==4096 and isinstance(data.get("rate_hz"),(int,float)) and
                math.isfinite(data["rate_hz"]) and 0<data["rate_hz"]<=384000 and
                data.get("command_hz")==440 and data.get("digital_level")==.25 and
                all(isinstance(v,(int,float)) and math.isfinite(v) and abs(v)<=.25 for v in samples)):
                raise SystemExit("DIGITAL_EXPORT_INVALID")
        elif data.get("source")!="UNAVAILABLE":raise SystemExit("UNEXPECTED_EXPORT")
        return data,len(PINS)
def main():
    if len(sys.argv)!=2:raise SystemExit("usage: qualify.py REPO")
    repo=pathlib.Path(sys.argv[1]).resolve(strict=True)
    base=get(repo,BASE,"ui/candidates/UI-001/index.html",BASE_BLOB).decode("utf-8")
    vendor={name:blob((ROOT/"vendor"/name).read_bytes(),pin).decode("utf-8") for name,pin in VENDOR.items()}
    data,pins=export(repo)
    base=base.replace("UI-001","UI-002").replace("UI check","UI / renderer check")
    base=replace_once(base,"</style>",vendor["uPlot.min.css"]+"\n"+(ROOT/"render.css").read_text(encoding="utf-8")+"\n</style>")
    base=replace_once(base,'<div class="screen" id="screen">','<button id="digital-tab" type="button" aria-pressed="false">Digital command</button><div class="renderer-status" id="renderer-status" aria-live="polite"></div><div class="digital-plot" id="digital-plot" hidden></div><div class="digital-info" id="digital-info" hidden></div><div class="screen" id="screen"><canvas class="fik-grid" id="gpu-grid" aria-hidden="true" hidden></canvas><canvas class="fik-grid" id="cpu-grid" aria-hidden="true" hidden></canvas>')
    extra=(ROOT/"render.js").read_text(encoding="utf-8")
    if "</script" in extra.lower() or "</script" in vendor["uPlot.iife.min.js"].lower():raise SystemExit("UNSAFE_SCRIPT_BOUNDARY")
    payload=json.dumps(data,allow_nan=False,separators=(",",":")).replace("<","\\u003c")
    base=replace_once(base,"</body>",'<script type="application/json" id="fik-source">'+payload+'</script>\n<script>\n'+vendor["uPlot.iife.min.js"]+'\n</script>\n<script>\n'+extra+'\n</script>\n</body>')
    output=ROOT/"FREQMED_UI002.html"
    output.write_text(base,encoding="utf-8")
    print("UI001_SOURCE_PIN=PASS")
    print("UPLOT_VENDOR_PINS=3/3 PASS")
    print("NATIVE_C_SOURCE_PINS="+str(pins))
    print("FIK_UI002_BUILD_REPORT="+json.dumps({"source":data["source"],"samples":data.get("count",0),"rate_hz":data.get("rate_hz"),"renderer_browser":"NOT_EXECUTED","pixi":"NOT_INTEGRATED","physical_output":"NONE","html":str(output)},sort_keys=True))
if __name__=="__main__":main()
