#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""UI-010 consolidation over the exact UI-009 implementation."""
import contextlib,io,json,os,pathlib,platform,resource,subprocess,sys,tempfile,time
import importlib.util,hashlib
ROOT=pathlib.Path(__file__).resolve().parent
BASE="8e068bb77457b15efc5cbe27e0f744074c644ea9"
PARENT={"serve.py":"0b643ff1a1af77fa55d40b06a800d601273cc300","archive.py":"abfd2f668b6cf226574c10daa290818adda863a9","compare.js":"a8fec98ed182f28b3cac825c59eca9f2922e1d5d","compare.html":"98a2881b988443d4915bfd5fc38ac14ce2a7267d","compare.css":"fb724f3376f1e38fa7b1419a8ee32afa4b63fe03"}
OWN={"performance.js":"98918e7588aefeb5ec3251820f806be2b7a68d68","performance.html":"b315c2e63027d553bc3050f6802ea6af838266b6","performance.css":"fee628db9cf0ef173626690741befb50f5ca90cf","qualification-ui.js":"caf2524b1a55d4bdac1491f15d2a0a9f2a1e7285"}
PATCHES=[["function spectrum(x,rate){","function spectrumRaw(x,rate){"],["function spectrogram(x,rate,size=512,hop=128){","function spectrum(x,rate){return FIKPerf.spectrum(spectrumRaw,x,rate);}\nfunction spectrogram(x,rate,size=512,hop=128){"],["st=good?FIKScience.spectrogram(x,rate):null;","st=null;"],["function render(){\n clearPlot();","function render(){\n if(document.getElementById(\"science-suite\").hidden){clearPlot();return;}\n if(good&&mode===\"stft\"&&!st)st=FIKScience.spectrogram(x,rate);\n clearPlot();"],["   checks.actual_stft=st.frames.length===29","   if(!st)st=FIKScience.spectrogram(x,rate);\n   checks.actual_stft=st.frames.length===29"],["if(good&&plot&&oldRate===rate&&(mode===\"time\"||mode===\"fft\"))","if(good&&plot&&!document.getElementById(\"science-suite\").hidden&&oldRate===rate&&(mode===\"time\"||mode===\"fft\"))"],["samples:current.samples.slice()","samples:Object.freeze(current.samples.slice())"],["function schedule(){if(!frame)frame=requestAnimationFrame(()=>{frame=0;graph();heat();});}","function schedule(){if(!frame)frame=requestAnimationFrame(()=>{frame=0;if(!document.getElementById(\"spectral-suite\").hidden){graph();heat();}});}"],["window.addEventListener(\"fik-precision-redraw\",()=>{if(plot)plot.redraw(false,false);});","window.addEventListener(\"fik-precision-redraw\",()=>{if(plot)plot.redraw(false,false);});\nwindow.addEventListener(\"fik-workspace-visible\",e=>{if(e.detail===\"science\")redraw();});"],[" activeView=name;for(const [k,v] of Object.entries(views))v.hidden=k!==name;"," activeView=name;for(const [k,v] of Object.entries(views))v.hidden=k!==name;\n window.dispatchEvent(new CustomEvent(\"fik-workspace-visible\",{detail:name}));"],["$(\"theme\").addEventListener(\"change\",schedule);window.addEventListener(\"resize\",schedule);","window.addEventListener(\"fik-workspace-visible\",e=>{if(e.detail===\"spectral\")schedule();});\n$(\"theme\").addEventListener(\"change\",schedule);window.addEventListener(\"resize\",schedule);"],["window.addEventListener(\"fik-native-snapshot\",e=>{current=M.valid(e.detail)?e.detail:null;options();});","window.addEventListener(\"fik-native-snapshot\",e=>{const next=M.valid(e.detail)?e.detail:null;if(current!==next){current=next;options();}});"]]

def verify(data,pin):
    if hashlib.sha1(("blob %d"%len(data)).encode()+b"\0"+data).hexdigest()!=pin:
        raise RuntimeError("BLOB_MISMATCH "+pin)
    return data
def once(s,a,b):
    if s.count(a)!=1:raise RuntimeError("CONSOLIDATION_BOUNDARY "+a[:100])
    return s.replace(a,b,1)
class Tee:
    def __init__(self,real):self.real=real;self.buffer=io.StringIO()
    def write(self,s):self.buffer.write(s);return self.real.write(s)
    def flush(self):self.real.flush()
def report(log,prefix):
    rows=[s[len(prefix):] for s in log.splitlines() if s.startswith(prefix)]
    if len(rows)!=1:raise RuntimeError("REPORT_MISSING_OR_DUPLICATE "+prefix)
    return json.loads(rows[0])
def measure(call,tag):
    out=Tee(sys.stdout);t=time.monotonic()
    before=resource.getrusage(resource.RUSAGE_SELF);child=resource.getrusage(resource.RUSAGE_CHILDREN)
    with contextlib.redirect_stdout(out):call()
    after=resource.getrusage(resource.RUSAGE_SELF);end=resource.getrusage(resource.RUSAGE_CHILDREN)
    print("FIK_UI010_RESOURCE_REPORT="+json.dumps({"phase":tag,"wall_seconds":time.monotonic()-t,
        "python_cpu_seconds":after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime,
        "reaped_children_cpu_seconds":end.ru_utime+end.ru_stime-child.ru_utime-child.ru_stime,
        "python_peak_rss_bytes_process_lifetime":after.ru_maxrss,
        "children_peak_rss_bytes_lifetime":end.ru_maxrss,
        "platform":platform.system(),"machine":platform.machine(),"gpu_utilization":"NOT_MEASURED"},sort_keys=True),flush=True)
    return out.buffer.getvalue()
def main():
    if len(sys.argv)!=2 or platform.system()!="Darwin":raise SystemExit("Usage on macOS: python3 -B serve.py REPO")
    repo=pathlib.Path(sys.argv[1]).resolve(strict=True)
    assets={n:verify((ROOT/n).read_bytes(),pin).decode("utf-8") for n,pin in OWN.items()}
    with tempfile.TemporaryDirectory(prefix="freqmed_ui010_parent_") as tmp:
        p=pathlib.Path(tmp)
        for name,pin in PARENT.items():
            data=subprocess.check_output(["git","-C",str(repo),"show",BASE+":ui/candidates/UI-009/"+name],timeout=30)
            (p/name).write_bytes(verify(data,pin))
        spec=importlib.util.spec_from_file_location("freqmed_ui009",p/"serve.py")
        nine=importlib.util.module_from_spec(spec);spec.loader.exec_module(nine)
        original_compose=nine.compose
        def compose(page,old):
            page=original_compose(page,old)
            page=page.replace("UI-009","UI-010")
            for a,b in PATCHES:page=once(page,a,b)
            for n in ("performance.js","qualification-ui.js"):
                if "</script" in assets[n].lower():raise RuntimeError("SCRIPT_BOUNDARY")
            page=once(page,"</head>","<script>\n"+assets["performance.js"]+"\n</script>\n</head>")
            page=once(page,"</style>",assets["performance.css"]+"\n</style>")
            page=once(page,'<details class="acquisition-disclosure" id="acquisition-disclosure">',assets["performance.html"]+'\n<details class="acquisition-disclosure" id="acquisition-disclosure">')
            page=once(page,"</body>","<script>\n"+assets["qualification-ui.js"]+"\n</script>\n</body>")
            scan=nine.Scan();scan.feed(page)
            checks={"unique_ids":len(scan.ids)==len(set(scan.ids)),"physical_disabled":scan.physical==[True,True],
             "performance_controls":{"performance-panel","perf-refresh","perf-frames","perf-check","digital-stop"}<=set(scan.ids),
             "native_cache_hook":page.count("return FIKPerf.spectrum(spectrumRaw,x,rate);")==1,
             "lazy_stft":page.count("if(good&&mode===\"stft\"&&!st)")==1,
             "three_views":page.count('data-workspace-view=')==3,
             "local_policy":"connect-src 'self'" in page}
            print("FIK_UI010_BUILD_REPORT="+json.dumps({"checks":checks,"passed":sum(checks.values()),"total":len(checks),"browser":"NOT_EXECUTED","physical_output":"NONE"},sort_keys=True),flush=True)
            if not all(checks.values()):raise RuntimeError("CONSOLIDATION_BUILD_FAILED")
            return page
        nine.compose=compose
        # Parent checks its original structure again after composition; all UI-009 IDs remain.
        original_runtime=nine.patched_runtime
        def runtime(core,jobsmod,archive):
            original=core.qualify
            def strict(server,secret):
                log=measure(lambda:original(server,secret),"HTTP_NATIVE_COMPLETE_STOP")
                d=report(log,"FIK_UI005_REPORT=")
                if not (d.get("http_total")==13 and d.get("http_passed")==13 and d.get("native_full_duration") is True and d.get("native_stop_confirmed") is True and d.get("physical_output")=="NONE"):
                    raise RuntimeError("NATIVE_COMPLETE_OR_STOP_NOT_CONFIRMED")
            core.qualify=strict
            return original_runtime(core,jobsmod,archive)
        nine.patched_runtime=runtime
        original_archive=nine.qualify_archive
        def strict_archive(server,secret):
            log=measure(lambda:original_archive(server,secret),"NATIVE_ARCHIVE_REPLAY")
            d=report(log,"FIK_UI009_ARCHIVE_REPORT=")
            if not (d.get("full_replay") is True and d.get("replayed_records")==d.get("expected_records") and d.get("expected_records",0)>0 and d.get("native_state")=="COMPLETE"):
                raise RuntimeError("ARCHIVE_NOT_CONFIRMED")
            print("FIK_UI010_NATIVE_GATE=PASS",flush=True)
        nine.qualify_archive=strict_archive
        # Preserve original launch and clean-up; parent URL marker remains UI009.
        nine.main()
if __name__=="__main__":main()
