#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""UI-007: precision workspace over exact UI-006 composition."""
import hashlib,importlib.util,json,pathlib,platform,secrets,subprocess,sys,tempfile
from html.parser import HTMLParser
from http.server import HTTPServer
ROOT=pathlib.Path(__file__).resolve().parent
BASE="0217bf3f61977da8ba2fb3ba37e2fb9f2defee66"
PARENT={"serve.py":"0b2ae837b642c2b9c0d51c9e31dc1cedb98b5482","dashboard-math.js":"844553160502e17b3c4ebba54ced8fd06ebf6f89","dashboard.js":"0595d8b2d82474c5bab1cf0b1e27f324289cf586","dashboard.css":"5be81c821d168a39b988063dc9ab8c4c45ecdda5"}
OWN={"precision-math.js":"508e1194bcb80a423f3d1dc658b7b879bf810b9b","workspace.js":"b2da93cbef7530ebf07ee03bc6a451d4c2c9dba1","workspace.css":"bb8cb0c83f6bf7063b8d1a6610a350405800b96d"}
PATCHES=[["<div id=\"ac-controls\" class=\"controls\">","<div id=\"ac-controls\" class=\"controls\"><div class=\"precision-controls\"><label for=\"precision-scale\">Frequency scale</label><select id=\"precision-scale\"><option value=\"log\">Logarithmic</option><option value=\"linear\">Linear</option></select><label for=\"precision-mode\">Adjustment precision</label><select id=\"precision-mode\"><option value=\"fine\">Fine · 1 unit</option><option value=\"coarse\">Coarse</option></select><div class=\"precision-nudge\"><button id=\"precision-minus\" type=\"button\" aria-label=\"Decrease frequency\">− Hz</button><button id=\"precision-plus\" type=\"button\" aria-label=\"Increase frequency\">+ Hz</button></div><span class=\"tiny\">Shift = fine · integer native commands</span></div>"],["<div class=\"science-notice\"","<div class=\"precision-toolbar\"><label class=\"tiny\" for=\"precision-layout\">Workspace</label><select id=\"precision-layout\"><option value=\"standard\">Standard</option><option value=\"wide\">Wide monitor</option></select><button id=\"precision-expand\" type=\"button\" aria-pressed=\"false\">Expand workspace</button></div><div class=\"science-notice\""],["<div class=\"science-foot\">","<div class=\"precision-cursors\"><div class=\"science-kicker\">A/B · DIGITAL DIFFERENTIAL</div><span class=\"tiny\" id=\"precision-source\">No digital window</span><div class=\"precision-cursor-row\"><label for=\"precision-a\">A</label><input id=\"precision-a\" type=\"range\" min=\"0\" max=\"0\" value=\"0\" disabled><output id=\"precision-readout-a\">—</output></div><div class=\"precision-cursor-row\"><label for=\"precision-b\">B</label><input id=\"precision-b\" type=\"range\" min=\"0\" max=\"0\" value=\"0\" disabled><output id=\"precision-readout-b\">—</output></div><div class=\"precision-deltas\"><div><span class=\"tiny\">Δ X · B − A</span><output id=\"precision-delta-x\">—</output></div><div><span class=\"tiny\">Δ Y · B − A</span><output id=\"precision-delta-y\">—</output></div></div><button id=\"precision-reset\" type=\"button\">Reset A/B</button></div><div class=\"science-foot\">"],["<footer class=\"bottom\">","<footer class=\"bottom\"><span><button id=\"precision-check\" type=\"button\">Precision checks</button> <output id=\"precision-check-result\" aria-live=\"polite\"></output></span>"],["function paint(){","let precisionMode=\"fine\",frequencyScale=\"log\";\nfunction paint(){"],["(270*(v-min)/(max-min))+\"deg\"","(270*FIKPrecision.ratio(v,min,max,id===\"freq\"?frequencyScale:\"linear\"))+\"deg\""],["270*(values.freq-1)/22048+\"deg\"","270*FIKPrecision.ratio(values.freq,1,22049,frequencyScale)+\"deg\""],["const step=ev.shiftKey?10:1;","const step=FIKPrecision.step(id,precisionMode,ev.shiftKey);"],["const scale=ev.shiftKey?1:Math.max(1,(Number(e.max)-Number(e.min))/240);set(id,drag.v+(drag.y-ev.clientY)*scale);","set(id,FIKPrecision.drag(drag.v,drag.y-ev.clientY,Number(e.min),Number(e.max),id===\"freq\"?frequencyScale:\"linear\",precisionMode,ev.shiftKey));"],["$(\"fader\").addEventListener(\"input\",()=>set(\"level\",$(\"fader\").valueAsNumber));","$(\"precision-mode\").addEventListener(\"change\",()=>{precisionMode=$(\"precision-mode\").value;});\n$(\"precision-scale\").addEventListener(\"change\",()=>{frequencyScale=$(\"precision-scale\").value;paint();});\nfor(const [id,sign] of [[\"precision-minus\",-1],[\"precision-plus\",1]])$(id).addEventListener(\"click\",()=>{if($(id).disabled)return;set(\"freq\",values.freq+sign*FIKPrecision.step(\"freq\",precisionMode,false));window.dispatchEvent(new CustomEvent(\"fik-precision-draft\"));});\n$(\"fader\").addEventListener(\"input\",()=>set(\"level\",$(\"fader\").valueAsNumber));"],["const prior={...values},previous={lang,channel,zoom,monitorMode,theme:$(\"theme\").value};","const prior={...values},previous={lang,channel,zoom,monitorMode,theme:$(\"theme\").value,precisionMode};precisionMode=\"fine\";"],["Object.assign(values,prior);change(\"language\",previous.lang);","Object.assign(values,prior);precisionMode=previous.precisionMode;change(\"language\",previous.lang);"],["#ac-controls input,#ac-controls select,#acoustic","#ac-controls input,#ac-controls select,#ac-controls button,#acoustic"],[" e.addEventListener(\"pointerup\",dirty);"," e.addEventListener(\"pointerup\",dirty);e.addEventListener(\"pointercancel\",dirty);e.addEventListener(\"lostpointercapture\",dirty);"],["$(\"reset\").addEventListener(\"click\",dirty);","window.addEventListener(\"fik-precision-draft\",()=>dirty());\n$(\"reset\").addEventListener(\"click\",dirty);"],["hooks:{setCursor:[u=>","hooks:{draw:[u=>window.dispatchEvent(new CustomEvent(\"fik-precision-chart\",{detail:u}))],setCursor:[u=>"],["translate();setMetrics();render();","window.addEventListener(\"fik-precision-redraw\",()=>{if(plot)plot.redraw(false,false);});\ntranslate();setMetrics();render();"]]

def verify(data,pin):
    if hashlib.sha1(("blob %d"%len(data)).encode()+b"\0"+data).hexdigest()!=pin:
        raise RuntimeError("BLOB_MISMATCH "+pin)
    return data
def once(s,a,b):
    if s.count(a)!=1:raise RuntimeError("PRECISION_BOUNDARY "+a[:90])
    return s.replace(a,b,1)
def load(path):
    spec=importlib.util.spec_from_file_location("freqmed_parent006",path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
def compose(page,own):
    page=page.replace("UI-006","UI-007")
    for a,b in PATCHES:page=once(page,a,b)
    if any("</script" in own[n].lower() for n in ("precision-math.js","workspace.js")):raise RuntimeError("SCRIPT_BOUNDARY")
    page=once(page,"</head>","<script>\n"+own["precision-math.js"]+"\n</script>\n</head>")
    page=once(page,"</style>",own["workspace.css"]+"\n</style>")
    page=once(page,"</body>","<script>\n"+own["workspace.js"]+"\n</script>\n</body>")
    return page
class Scan(HTMLParser):
    def __init__(self):super().__init__();self.ids=[];self.physical=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if "id" in a:self.ids.append(a["id"])
        if tag=="button" and a.get("class") in ("start","stop"):self.physical.append("disabled" in a)
def check(page):
    s=Scan();s.feed(page)
    required={"precision-scale","precision-mode","precision-minus","precision-plus","precision-layout","precision-expand","precision-a","precision-b","precision-delta-x","precision-delta-y","precision-check","digital-stop"}
    checks={"unique_ids":len(s.ids)==len(set(s.ids)),"required_controls":required<=set(s.ids),"physical_disabled":s.physical==[True,True],
        "single_science":page.count('id="science-suite"')==1,"integer_native_bounds":'id="freq" type="number" min="1" max="22049" step="1"' in page,
        "draft_lock":"#ac-controls input,#ac-controls select,#ac-controls button" in page,
        "chart_hook":page.count('new CustomEvent("fik-precision-chart"')==1,
        "stop_in_workspace":page.index("<main>")<page.index('id="digital-stop"')<page.index("</main>"),
        "local_policy":"connect-src 'self'" in page}
    print("FIK_UI007_BUILD_REPORT="+json.dumps({"checks":checks,"passed":sum(checks.values()),"total":len(checks),"parent_pins":len(PARENT),"workspace_pins":len(OWN),"native_runtime":"UI005_UNCHANGED","browser":"NOT_EXECUTED","physical_output":"NONE"},sort_keys=True),flush=True)
    if not all(checks.values()):raise RuntimeError("PRECISION_BUILD_FAILED")
def main():
    if len(sys.argv)!=2 or platform.system()!="Darwin":raise SystemExit("Usage on macOS: python3 -B serve.py REPO")
    repo=pathlib.Path(sys.argv[1]).resolve(strict=True)
    own={n:verify((ROOT/n).read_bytes(),pin).decode("utf-8") for n,pin in OWN.items()}
    with tempfile.TemporaryDirectory(prefix="freqmed_ui007_") as tmp:
        root=pathlib.Path(tmp);p=root/"ui006";p.mkdir()
        for name,pin in PARENT.items():
            data=subprocess.check_output(["git","-C",str(repo),"show",BASE+":ui/candidates/UI-006/"+name],timeout=30)
            (p/name).write_bytes(verify(data,pin))
        parent=load(p/"serve.py")
        old={n:parent.verified((p/n).read_bytes(),pin).decode("utf-8") for n,pin in parent.OWN.items()}
        core,jobsmod=parent.prepare_parent(repo,root/"ui005")
        work=root/"build";work.mkdir();secret=secrets.token_urlsafe(32)
        raw,exe=core.build(repo,work,secret)
        baseline=parent.compose(raw,old);parent.check_page(baseline)
        page=compose(baseline,own);check(page)
        jobs=jobsmod.Jobs(exe)
        try:
            with HTTPServer(("127.0.0.1",0),core.handler(page.encode("utf-8"),jobs,secret)) as server:
                core.qualify(server,secret)
                url="http://127.0.0.1:"+str(server.server_port)+"/"
                print("FREQMED_UI007_URL="+url,flush=True)
                subprocess.run(["open","-a","Safari",url],check=False)
                try:server.serve_forever()
                except KeyboardInterrupt:print("FREQMED_UI007_SERVER_STOPPED",flush=True)
        finally:jobs.close()
if __name__=="__main__":main()
