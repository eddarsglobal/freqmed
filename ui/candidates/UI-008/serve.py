#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""UI-008: spectral suite on the pinned UI-007 runtime and workspace."""
import hashlib,importlib.util,json,pathlib,platform,secrets,subprocess,sys,tempfile
from html.parser import HTMLParser
from http.server import HTTPServer
ROOT=pathlib.Path(__file__).resolve().parent
BASE="5b2b81e694896bd01ea6d2208bdd8569f0db8e60"
PARENT={"serve.py":"6358dcdcecfa4b02a685d84210cfe6f37e1279c4","precision-math.js":"508e1194bcb80a423f3d1dc658b7b879bf810b9b","workspace.js":"b2da93cbef7530ebf07ee03bc6a451d4c2c9dba1","workspace.css":"bb8cb0c83f6bf7063b8d1a6610a350405800b96d"}
OWN={"spectral.js":"5f614ebc2bb7ead97193f7f188e4249bfad0473d","spectral-ui.js":"2733c61e9464594defb1ed208eda9f9244faa0ed","spectral.html":"53e28561f6cdbb18b2138b01f89e35da140ecb30","spectral.css":"76f0e6663ae1e077a55a2d20f384beb83aac2ff7"}

def verify(data,pin):
    if hashlib.sha1(("blob %d"%len(data)).encode()+b"\0"+data).hexdigest()!=pin:
        raise RuntimeError("BLOB_MISMATCH "+pin)
    return data
def load(path):
    spec=importlib.util.spec_from_file_location("freqmed_parent007",path)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    return mod
def once(s,a,b):
    if s.count(a)!=1:raise RuntimeError("SPECTRAL_BOUNDARY "+a[:80])
    return s.replace(a,b,1)
def compose(page,own):
    page=page.replace("UI-007","UI-008")
    page=once(page,'<details class="acquisition-disclosure" id="acquisition-disclosure">',own["spectral.html"]+'\n<details class="acquisition-disclosure" id="acquisition-disclosure">')
    page=once(page,"</style>",own["spectral.css"]+"\n</style>")
    scripts=[own["spectral.js"],own["spectral-ui.js"]]
    if any("</script" in x.lower() for x in scripts):raise RuntimeError("SCRIPT_BOUNDARY")
    return once(page,"</body>","".join("\n<script>\n"+s+"\n</script>" for s in scripts)+"\n</body>")
class Scan(HTMLParser):
    def __init__(self):super().__init__();self.ids=[];self.physical=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if "id" in a:self.ids.append(a["id"])
        if tag=="button" and a.get("class") in ("start","stop"):self.physical.append("disabled" in a)
def check(page):
    s=Scan();s.feed(page)
    required={"spectral-suite","spectral-canvas","spectral-history","spectral-scale","spectral-fit","spectral-freeze","spectral-clear","spectral-peaks","spectral-harmonics","spectral-comparison","spectral-check","digital-stop"}
    checks={"unique_ids":len(s.ids)==len(set(s.ids)),"required_controls":required<=set(s.ids),
      "physical_disabled":s.physical==[True,True],"single_science":s.ids.count("science-suite")==1,
      "single_spectral":s.ids.count("spectral-suite")==1,"local_policy":"connect-src 'self'" in page,
      "source_event":'window.addEventListener("fik-native-snapshot",e=>receive(e.detail))' in page,
      "bounded_history":"if(history.length>24)history.shift();" in page}
    print("FIK_UI008_BUILD_REPORT="+json.dumps({"checks":checks,"passed":sum(checks.values()),"total":len(checks),"parent_pins":len(PARENT),"spectral_pins":len(OWN),"native_runtime":"UI005_UNCHANGED","browser":"NOT_EXECUTED","physical_output":"NONE"},sort_keys=True),flush=True)
    if not all(checks.values()):raise RuntimeError("SPECTRAL_BUILD_FAILED")
def main():
    if len(sys.argv)!=2 or platform.system()!="Darwin":raise SystemExit("Usage on macOS: python3 -B serve.py REPO")
    repo=pathlib.Path(sys.argv[1]).resolve(strict=True)
    own={n:verify((ROOT/n).read_bytes(),pin).decode("utf-8") for n,pin in OWN.items()}
    with tempfile.TemporaryDirectory(prefix="freqmed_ui008_") as tmp:
        root=pathlib.Path(tmp);p=root/"ui007";p.mkdir()
        for name,pin in PARENT.items():
            data=subprocess.check_output(["git","-C",str(repo),"show",BASE+":ui/candidates/UI-007/"+name],timeout=30)
            (p/name).write_bytes(verify(data,pin))
        prev=load(p/"serve.py")
        old={n:prev.verify((p/n).read_bytes(),pin).decode("utf-8") for n,pin in prev.OWN.items()}
        q=root/"ui006";q.mkdir()
        for name,pin in prev.PARENT.items():
            data=subprocess.check_output(["git","-C",str(repo),"show",prev.BASE+":ui/candidates/UI-006/"+name],timeout=30)
            (q/name).write_bytes(prev.verify(data,pin))
        parent=prev.load(q/"serve.py")
        dash={n:parent.verified((q/n).read_bytes(),pin).decode("utf-8") for n,pin in parent.OWN.items()}
        core,jobsmod=parent.prepare_parent(repo,root/"ui005")
        work=root/"build";work.mkdir();secret=secrets.token_urlsafe(32)
        raw,exe=core.build(repo,work,secret)
        baseline=parent.compose(raw,dash);parent.check_page(baseline)
        baseline=prev.compose(baseline,old);prev.check(baseline)
        page=compose(baseline,own);check(page)
        jobs=jobsmod.Jobs(exe)
        try:
            with HTTPServer(("127.0.0.1",0),core.handler(page.encode("utf-8"),jobs,secret)) as server:
                core.qualify(server,secret)
                url="http://127.0.0.1:"+str(server.server_port)+"/"
                print("FREQMED_UI008_URL="+url,flush=True)
                subprocess.run(["open","-a","Safari",url],check=False)
                try:server.serve_forever()
                except KeyboardInterrupt:print("FREQMED_UI008_SERVER_STOPPED",flush=True)
        finally:jobs.close()
if __name__=="__main__":main()
