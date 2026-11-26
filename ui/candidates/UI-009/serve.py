#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""UI-009: multi-instrument workspace and bounded native record archive."""
import hashlib,importlib.util,inspect,json,pathlib,platform,secrets,subprocess,sys,tempfile,time,threading,http.client
from html.parser import HTMLParser
from http.server import HTTPServer
ROOT=pathlib.Path(__file__).resolve().parent
BASE="81560b87b63f3ec307e00c3f254201e828eec213"
PARENT={"serve.py":"2df643da8ab48eb0cbfb0a38dcabb29d5f2e39b9","spectral.js":"5f614ebc2bb7ead97193f7f188e4249bfad0473d","spectral-ui.js":"2733c61e9464594defb1ed208eda9f9244faa0ed","spectral.html":"53e28561f6cdbb18b2138b01f89e35da140ecb30","spectral.css":"76f0e6663ae1e077a55a2d20f384beb83aac2ff7"}
OWN={"archive.py":"abfd2f668b6cf226574c10daa290818adda863a9","compare.js":"a8fec98ed182f28b3cac825c59eca9f2922e1d5d","compare.html":"98a2881b988443d4915bfd5fc38ac14ce2a7267d","compare.css":"fb724f3376f1e38fa7b1419a8ee32afa4b63fe03"}
JOBS_PATCH=[["\"record\":None,\"reason\":\"\"}","\"record\":None,\"reason\":\"\",\"archive\":Archive()}"],["                        j[\"record\"]=d","                        j[\"archive\"].append(d)\n                        j[\"record\"]=d"],["                else:j.update(state=last[\"state\"],record=last if last[\"state\"]!=\"REJECTED\" else None,reason=last.get(\"reason\",\"\"))","                else:\n                    if last[\"state\"]==\"COMPLETE\":\n                        try:j[\"archive\"].append(last)\n                        except ValueError:\n                            j.update(state=\"FAULT\",record=None,reason=\"ARCHIVE_TERMINAL_REJECTED\");return\n                    j.update(state=last[\"state\"],record=last if last[\"state\"]!=\"REJECTED\" else None,reason=last.get(\"reason\",\"\"))"],["    def stop(self,ident):","    def archive(self,ident,after):\n        with self.lock:\n            j=self.job\n            if not j or j[\"id\"]!=ident or j[\"state\"]!=\"COMPLETE\":return None\n            return j[\"archive\"].page(after)\n    def stop(self,ident):"]]
HANDLER_PATCH=[["(\"/api/start\",\"/api/status\",\"/api/stop\",\"/api/ping\")","(\"/api/start\",\"/api/status\",\"/api/stop\",\"/api/ping\",\"/api/archive\")"],["            if type(cmd) is not dict or set(cmd)!={\"id\"}","            if self.path==\"/api/archive\":\n                if type(cmd) is not dict or set(cmd)!={\"id\",\"after\"} or type(cmd[\"id\"]) is not str or len(cmd[\"id\"])!=32 or type(cmd[\"after\"]) is not int or not 0<=cmd[\"after\"]<=938:\n                    return self.reject(400,\"INVALID_ARCHIVE_CURSOR\")\n                p=jobs.archive(cmd[\"id\"],cmd[\"after\"])\n                if p is None:return self.reject(404,\"ARCHIVE_UNAVAILABLE\")\n                return self.reply(200,p)\n            if type(cmd) is not dict or set(cmd)!={\"id\"}"]]
NAV="<nav class=\"workspace-nav\" aria-label=\"Scientific workspaces\"><button type=\"button\" data-workspace-view=\"science\" aria-pressed=\"true\">Instruments</button><button type=\"button\" data-workspace-view=\"spectral\" aria-pressed=\"false\">Spectral intelligence</button><button type=\"button\" data-workspace-view=\"compare\" aria-pressed=\"false\">Comparison & archive</button></nav>"

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
    page=page.replace("UI-008","UI-009")
    start=page.index('<section id="spectral-suite"')
    end=page.index("</section>",start)+len("</section>")
    spectral=page[start:end]
    page=page[:start]+page[end:]
    page=once(page,'<section class="panel science-suite"',NAV+'<section class="panel science-suite"')
    page=once(page,'</section>\n<section class="panel right">',spectral+'\n'+own["compare.html"]+'\n</section>\n<section class="panel right">')
    page=once(page,"</style>",own["compare.css"]+"\n</style>")
    if "</script" in own["compare.js"].lower():raise RuntimeError("SCRIPT_BOUNDARY")
    return once(page,"</body>","<script>\n"+own["compare.js"]+"\n</script>\n</body>")
class Scan(HTMLParser):
    def __init__(self):super().__init__();self.ids=[];self.physical=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if "id" in a:self.ids.append(a["id"])
        if tag=="button" and a.get("class") in ("start","stop"):self.physical.append("disabled" in a)
def check(page):
    s=Scan();s.feed(page)
    required={"compare-suite","compare-wave","compare-fft","compare-history","compare-a","compare-b","compare-save","compare-check","digital-stop","spectral-suite","science-suite"}
    checks={"unique_ids":len(s.ids)==len(set(s.ids)),"required_controls":required<=set(s.ids),
      "physical_disabled":s.physical==[True,True],"three_views":page.count('data-workspace-view=')==3,
      "science_once":s.ids.count("science-suite")==1,"spectral_once":s.ids.count("spectral-suite")==1,
      "comparison_inside_center":page.index('id="compare-suite"')<page.index('class="panel right"'),
      "local_policy":"connect-src 'self'" in page}
    print("FIK_UI009_BUILD_REPORT="+json.dumps({"checks":checks,"passed":sum(checks.values()),"total":len(checks),"native_c":"UNCHANGED","browser":"NOT_EXECUTED","physical_output":"NONE"},sort_keys=True),flush=True)
    if not all(checks.values()):raise RuntimeError("WORKSPACE_BUILD_FAILED")
def patched_runtime(core,jobsmod,archive):
    src=inspect.getsource(jobsmod)
    for a,b in JOBS_PATCH:src=once(src,a,b)
    ns={"Archive":archive.Archive}
    exec(compile(src,"pinned_jobs_UI009","exec"),ns)
    src=inspect.getsource(core.handler)
    for a,b in HANDLER_PATCH:src=once(src,a,b)
    env=dict(vars(core))
    exec(compile(src,"pinned_handler_UI009","exec"),env)
    return ns["Jobs"],env["handler"]
def qualify_archive(server,secret):
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    host="127.0.0.1:"+str(server.server_port)
    headers={"Origin":"http://"+host,"X-FIK-Token":secret,"Content-Type":"application/json"}
    def post(route,body,h=None):
        c=http.client.HTTPConnection("127.0.0.1",server.server_port,timeout=12)
        try:
            c.request("POST","/api/"+route,json.dumps(body),h or headers)
            r=c.getresponse();return r.status,json.loads(r.read())
        finally:c.close()
    try:
        code,j=post("start",{"frequency_hz":828,"level_percent":18,"duration_ms":10000})
        if code!=200:raise RuntimeError("ARCHIVE_TEST_START")
        ident=j["id"];deadline=time.monotonic()+17
        while time.monotonic()<deadline:
            code,j=post("status",{"id":ident})
            if code!=200:raise RuntimeError("ARCHIVE_TEST_STATUS")
            if j["state"] in {"COMPLETE","STOPPED","FAULT","INVALIDATED","EXPIRED","REJECTED"}:break
            time.sleep(.03)
        d=j.get("record") or {};after=0;total=d.get("sequence",0)
        checks={"stale_id":post("archive",{"id":"0"*32,"after":0})[0]==404,
                "bad_cursor":post("archive",{"id":ident,"after":-1})[0]==400,
                "token_rejected":post("archive",{"id":ident,"after":0},{**headers,"X-FIK-Token":"invalid"})[0]==403,
                "origin_rejected":post("archive",{"id":ident,"after":0},{**headers,"Origin":"http://example.invalid"})[0]==403}
        complete=j["state"]=="COMPLETE" and d.get("session_closed") is True and d.get("processed")==d.get("expected")
        ordered=True;last=None
        if complete:
            while after<total:
                code,p=post("archive",{"id":ident,"after":after})
                if code!=200 or p["available"]!=total or not 1<=len(p["records"])<=8 or p["next"]!=after+len(p["records"]):
                    ordered=False;break
                for row in p["records"]:
                    after+=1
                    if row["sequence"]!=after:ordered=False
                    last=row
            checks["empty_end"]=post("archive",{"id":ident,"after":total})[1].get("records")==[]
        full=complete and ordered and after==total and last is not None and last["samples"]==d["samples"]
        print("FIK_UI009_ARCHIVE_REPORT="+json.dumps({"http_checks":checks,"native_state":j["state"],"expected_records":total,"replayed_records":after,"full_replay":full,"physical_output":"NONE"},sort_keys=True),flush=True)
        if not all(checks.values()) or not full:raise RuntimeError("ARCHIVE_QUALIFICATION_FAILED")
    finally:server.shutdown();thread.join()
def main():
    if len(sys.argv)!=2 or platform.system()!="Darwin":raise SystemExit("Usage on macOS: python3 -B serve.py REPO")
    repo=pathlib.Path(sys.argv[1]).resolve(strict=True)
    own={n:verify((ROOT/n).read_bytes(),pin).decode("utf-8") for n,pin in OWN.items()}
    with tempfile.TemporaryDirectory(prefix="freqmed_ui009_") as tmp:
        root=pathlib.Path(tmp);p=root/"ui007";p.mkdir()
        for name,pin in PARENT.items():
            data=subprocess.check_output(["git","-C",str(repo),"show",BASE+":ui/candidates/UI-008/"+name],timeout=30)
            (p/name).write_bytes(verify(data,pin))
        eight=load(p/"serve.py")
        spectral={n:eight.verify((p/n).read_bytes(),pin).decode("utf-8") for n,pin in eight.OWN.items()}
        pp=root/"actual007";pp.mkdir()
        for name,pin in eight.PARENT.items():
            data=subprocess.check_output(["git","-C",str(repo),"show",eight.BASE+":ui/candidates/UI-007/"+name],timeout=30)
            (pp/name).write_bytes(eight.verify(data,pin))
        prev=eight.load(pp/"serve.py")
        old={n:prev.verify((pp/n).read_bytes(),pin).decode("utf-8") for n,pin in prev.OWN.items()}
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
        baseline=eight.compose(baseline,spectral);eight.check(baseline)
        page=compose(baseline,own);check(page)
        archive=load(ROOT/"archive.py")
        checks=archive.tests()
        print("FIK_UI009_ARCHIVE_UNIT="+json.dumps(checks,sort_keys=True),flush=True)
        if not all(checks.values()):raise RuntimeError("ARCHIVE_UNIT_FAILED")
        Jobs,handler=patched_runtime(core,jobsmod,archive)
        jobs=Jobs(exe)
        try:
            with HTTPServer(("127.0.0.1",0),handler(page.encode("utf-8"),jobs,secret)) as server:
                core.qualify(server,secret)
                qualify_archive(server,secret)
                url="http://127.0.0.1:"+str(server.server_port)+"/"
                print("FREQMED_UI009_URL="+url,flush=True)
                subprocess.run(["open","-a","Safari",url],check=False)
                try:server.serve_forever()
                except KeyboardInterrupt:print("FREQMED_UI009_SERVER_STOPPED",flush=True)
        finally:jobs.close()
if __name__=="__main__":main()
