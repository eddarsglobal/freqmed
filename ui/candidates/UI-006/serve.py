#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""UI-006: pinned UI-005 runtime, dashboard-only composition."""
import hashlib,importlib.util,json,pathlib,platform,re,secrets,subprocess,sys,tempfile
from html.parser import HTMLParser
from http.server import HTTPServer
ROOT=pathlib.Path(__file__).resolve().parent
BASE="a44cdc3eb40fa90d87c5e2d62002f044206e5996"
PARENT={"serve.py":"fbca044b43087d57a1f66c0660c9df314b679ecd","native_stream.c":"c2b8acd3c60e8be5878a40726c761ed02e1fab91","jobs.py":"731d71b4ff0b066101a393d5f6853b71976ed100","bridge.js":"9ec581fd9105f09b35a4781b8a8258190d958a50","bridge.css":"d0e3b8bbf45e0962c84284d04124d749d1a52724"}
OWN={"dashboard-math.js":"844553160502e17b3c4ebba54ced8fd06ebf6f89","dashboard.js":"01ea339123ea65a325cc3bc0afb61e85c95429d4","dashboard.css":"5be81c821d168a39b988063dc9ab8c4c45ecdda5"}
PATCHES=[["<div class=\"dial-wrap\"><div class=\"dial\" id=\"dial\">","<div class=\"dashboard-hero\"><div class=\"dial-wrap\"><div id=\"dash-ring\" role=\"img\" aria-label=\"Digital session: IDLE\"><div class=\"dial\" id=\"dial\">"],["<span class=\"chip\">PHYSICAL NOT OPENED</span></div></div></div>","<span class=\"chip\">PHYSICAL NOT OPENED</span></div></div></div></div><div class=\"dash-overview\"><div class=\"dash-stat wide\"><span>Digital session</span><strong id=\"dash-stage\" role=\"status\">IDLE</strong></div><div class=\"dash-stat\"><span>Progress</span><strong id=\"dash-percent\">—</strong></div><div class=\"dash-stat\"><span>Digital sample rate</span><strong id=\"dash-rate\">—</strong></div><div class=\"dash-stat\"><span>Window duration</span><strong id=\"dash-window\">—</strong></div><div class=\"dash-stat\"><span>Native block sequence</span><strong id=\"dash-sequence\">—</strong></div><div class=\"dash-stat wide\"><span>Processed / expected samples</span><strong id=\"dash-coverage\">—</strong></div></div></div>"],["<div class=\"right-body\"><div class=\"meters\">","<div class=\"right-body\"><div class=\"dash-meters\"><div><div class=\"dash-meter-label\"><span>DIGITAL PEAK</span><output id=\"dash-peak-number\">—</output></div><div id=\"dash-peak-bar\" class=\"dash-bar\" role=\"meter\" aria-label=\"Digital peak\" aria-valuemin=\"0\" aria-valuemax=\"1\" aria-valuenow=\"0\"></div><div class=\"dash-scale\"><span>−60</span><span>−30</span><span>0 dBFS</span></div></div><div><div class=\"dash-meter-label\"><span>DIGITAL RMS</span><output id=\"dash-rms-number\">—</output></div><div id=\"dash-rms-bar\" class=\"dash-bar\" role=\"meter\" aria-label=\"Digital RMS\" aria-valuemin=\"0\" aria-valuemax=\"1\" aria-valuenow=\"0\"></div><div class=\"dash-scale\"><span>−60</span><span>−30</span><span>0 dBFS</span></div></div><div class=\"tiny\">Latest received window · normalized digital values · not SPL</div></div><div class=\"meters\">"],["<div class=\"action\"><button class=\"start\" disabled data-t=\"start\">START</button><button class=\"stop\" disabled data-t=\"stop\">STOP</button>","<div class=\"action\"><details class=\"physical-disclosure\"><summary>Physical interfaces · not opened</summary><button class=\"start\" disabled data-t=\"start\">START</button><button class=\"stop\" disabled data-t=\"stop\">STOP</button></details>"],["<div class=\"digital-label\"><span>Window RMS · digital</span><output id=\"digital-rms\">—</output></div>","<div class=\"digital-label\" hidden><span>Window RMS · digital</span><output id=\"digital-rms\">—</output></div>"],["<footer class=\"bottom\">","<footer class=\"bottom\"><span><button id=\"dash-check\" type=\"button\">Dashboard checks</button> <output id=\"dash-check-result\" aria-live=\"polite\"></output></span>"],["function status(s){$(\"runtime-state\").textContent=s;}","function status(s){$(\"runtime-state\").textContent=s;window.dispatchEvent(new CustomEvent(\"fik-runtime-state\",{detail:s}));}"],["  sync();\n }\n}\nasync function poll(my){","  sync();\n }\n window.dispatchEvent(new CustomEvent(\"fik-runtime-record\",{detail:j}));\n}\nasync function poll(my){"],["window.addEventListener(\"fik-native-snapshot\",e=>{update(e.detail);setMetrics();render();});","window.addEventListener(\"fik-native-snapshot\",e=>{const oldRate=rate;update(e.detail);setMetrics();if(good&&plot&&oldRate===rate&&(mode===\"time\"||mode===\"fft\")){plot.setData(mode===\"fft\"?[spec.hz,spec.db]:[times,x],false);readout();}else render();});"]]

def verified(data,pin):
    if hashlib.sha1(("blob %d"%len(data)).encode()+b"\0"+data).hexdigest()!=pin:
        raise RuntimeError("BLOB_MISMATCH "+pin)
    return data
def once(s,a,b):
    if s.count(a)!=1:raise RuntimeError("DASHBOARD_BOUNDARY "+a[:90])
    return s.replace(a,b,1)
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
def prepare_parent(repo,root):
    root.mkdir()
    for name,pin in PARENT.items():
        data=subprocess.check_output(["git","-C",str(repo),"show",BASE+":ui/candidates/UI-005/"+name],timeout=30)
        (root/name).write_bytes(verified(data,pin))
    return load("freqmed_parent005",root/"serve.py"),load("freqmed_jobs005",root/"jobs.py")
def compose(page,own):
    page=page.decode("utf-8").replace("UI-005","UI-006")
    # Move, do not duplicate, the scientific suite and legacy acquisition monitor.
    start=page.index('<div class="monitor">')
    end=page.index('</section>\n<section class="panel right">',start)
    monitor=page[start:end]
    page=page[:start]+page[end:]
    start=page.index('<section class="panel science-suite"')
    end=page.index("</section>",start)+len("</section>")
    science=page[start:end]
    page=page[:start]+page[end:]
    page=once(page,'</section>\n<section class="panel right">',science+'\n</section>\n<section class="panel right">')
    page=once(page,'<footer class="bottom">','<details class="acquisition-disclosure" id="acquisition-disclosure"><summary>Acquisition / secondary digital view</summary>'+monitor+'</details><footer class="bottom">')
    for a,b in PATCHES:page=once(page,a,b)
    page=once(page,'<div class="science-notice"','<div id="dash-window-state" class="tiny" role="status">No received digital window</div><div class="science-notice"')
    page=once(page,"</style>",own["dashboard.css"]+"\n</style>")
    scripts=[own["dashboard-math.js"],own["dashboard.js"]]
    if any("</script" in s.lower() for s in scripts):raise RuntimeError("SCRIPT_BOUNDARY")
    page=once(page,"</body>","".join("\n<script>\n"+s+"\n</script>" for s in scripts)+"\n</body>")
    return page
class Scan(HTMLParser):
    def __init__(self):
        super().__init__();self.ids=[];self.physical=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if "id" in a:self.ids.append(a["id"])
        if tag=="button" and a.get("class") in ("start","stop"):self.physical.append("disabled" in a)
def check_page(page):
    scan=Scan();scan.feed(page)
    required={"science-suite","screen","dash-ring","dash-peak-bar","dash-rms-bar","dash-stage","dash-check","acquisition-disclosure","native-calculate","digital-stop"}
    checks={"unique_ids":len(scan.ids)==len(set(scan.ids)),"required_controls":required<=set(scan.ids),
            "physical_buttons_disabled":scan.physical==[True,True],
            "science_before_runtime_panel":page.index('id="science-suite"')<page.index('class="panel right"'),
            "acquisition_after_runtime_panel":page.index('id="acquisition-disclosure"')>page.index('class="panel right"'),
            "one_science_suite":page.count('id="science-suite"')==1,
            "runtime_event":page.count('new CustomEvent("fik-runtime-record"')==1,
            "incremental_chart":page.count('plot.setData(mode==="fft"?[spec.hz,spec.db]:[times,x],false)')==1,
            "local_connection_policy":"connect-src 'self'" in page}
    print("FIK_UI006_BUILD_REPORT="+json.dumps({"checks":checks,"passed":sum(checks.values()),"total":len(checks),
        "parent_pins":len(PARENT),"dashboard_pins":len(OWN),"native_runtime":"UI005_UNCHANGED","browser":"NOT_EXECUTED","physical_output":"NONE"},sort_keys=True),flush=True)
    if not all(checks.values()):raise RuntimeError("DASHBOARD_BUILD_CHECK_FAILED")
def main():
    if len(sys.argv)!=2 or platform.system()!="Darwin":raise SystemExit("Usage on macOS: python3 -B serve.py REPO")
    repo=pathlib.Path(sys.argv[1]).resolve(strict=True)
    own={n:verified((ROOT/n).read_bytes(),pin).decode("utf-8") for n,pin in OWN.items()}
    with tempfile.TemporaryDirectory(prefix="freqmed_ui006_") as tmp:
        root=pathlib.Path(tmp)
        parent,jobmodule=prepare_parent(repo,root/"parent")
        work=root/"build";work.mkdir()
        secret=secrets.token_urlsafe(32)
        raw,exe=parent.build(repo,work,secret)
        page=compose(raw,own)
        check_page(page)
        jobs=jobmodule.Jobs(exe)
        try:
            with HTTPServer(("127.0.0.1",0),parent.handler(page.encode("utf-8"),jobs,secret)) as server:
                parent.qualify(server,secret)
                url="http://127.0.0.1:"+str(server.server_port)+"/"
                print("FREQMED_UI006_URL="+url,flush=True)
                subprocess.run(["open","-a","Safari",url],check=False)
                try:server.serve_forever()
                except KeyboardInterrupt:print("FREQMED_UI006_SERVER_STOPPED",flush=True)
        finally:jobs.close()
if __name__=="__main__":main()
