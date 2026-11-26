#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
import hashlib,html as htmlmod,importlib.util,json,math,pathlib,platform,secrets,subprocess,sys,tempfile
from http.server import HTTPServer,BaseHTTPRequestHandler
import hmac

ROOT=pathlib.Path(__file__).resolve().parent
PINS=[["base.html","e97bbe39c3a62ed53b7d99acb38d3eb40e814cfd","ui/candidates/UI-001/index.html","35d625e00f47bea44fe969841aa69d323ba572a5"],["qualify.py","015e75b7036d304156fde3a1f7244d419b1af2cc","ui/candidates/UI-002/qualify.py","86af927316486fa962679def0121fb7d868cbe6c"],["render.js","015e75b7036d304156fde3a1f7244d419b1af2cc","ui/candidates/UI-002/render.js","536b85e9932035352409c745f7b25d22bb72cebb"],["render.css","015e75b7036d304156fde3a1f7244d419b1af2cc","ui/candidates/UI-002/render.css","ebd17b60eb14ee56451bfbbac172f8dd4098734d"],["vendor/uPlot.iife.min.js","015e75b7036d304156fde3a1f7244d419b1af2cc","ui/candidates/UI-002/vendor/uPlot.iife.min.js","047f29b64f200a4a872758256e5e66930353d757"],["vendor/uPlot.min.css","015e75b7036d304156fde3a1f7244d419b1af2cc","ui/candidates/UI-002/vendor/uPlot.min.css","a030d63f20dafd22c0edbd181002dade612c8f4a"],["vendor/LICENSE-uPlot.txt","015e75b7036d304156fde3a1f7244d419b1af2cc","ui/candidates/UI-002/vendor/LICENSE-uPlot.txt","cde4b3f8352d147d5e626fea36358797c4fc06f2"],["science.js","dbfd60f6be44b559941c8317f62d5d1d2eed2966","ui/candidates/UI-003/science.js","52cd5810859eea1b8e7c89717fc9e11226cc8aa4"],["science-ui.js","dbfd60f6be44b559941c8317f62d5d1d2eed2966","ui/candidates/UI-003/science-ui.js","4cb8a08a3dc252fabb88c9fad0a64579ce6eace7"],["science.html","dbfd60f6be44b559941c8317f62d5d1d2eed2966","ui/candidates/UI-003/science.html","d4b0624a7cdb666e77a67da332dff3cedfa77e52"],["science.css","dbfd60f6be44b559941c8317f62d5d1d2eed2966","ui/candidates/UI-003/science.css","aee7670391f00dd5010e24323c11819b0e0ad6e7"]]
OWN={"native_command.c":"95f80c6e01e6bc644e2c0825746949f3ff9883dc","bridge.js":"0463afd64b5967c02e7e28f531f4a41242331875","bridge.css":"9da1d4176c30a424c9c5e3eb3422e793ee8a6c20"}
RENDER_PATCH=[["const source=JSON.parse(id(\"fik-source\").textContent);\nconst good=source.source===\"FREQMED_NATIVE_C_MEMORY_ONLY\"&&source.physical_output===false&&source.physical_measurement===false&&\n Number.isInteger(source.rate_hz)&&source.rate_hz>0&&source.rate_hz<=384000&&source.count===4096&&\n Array.isArray(source.samples)&&source.samples.length===source.count&&source.samples.every(v=>Number.isFinite(v)&&Math.abs(v)<=.25);\n","let source={source:\"UNAVAILABLE\"},good=false;\nconst validSource=d=>d.source===\"FREQMED_NATIVE_C_MEMORY_ONLY\"&&d.session_closed===true&&d.guardian_off===true&&d.physical_output===false&&d.physical_measurement===false&&Number.isInteger(d.rate_hz)&&d.rate_hz>0&&d.rate_hz<=384000&&d.count===4096&&Number.isFinite(d.digital_level)&&d.digital_level>0&&d.digital_level<=1&&Array.isArray(d.samples)&&d.samples.length===4096&&d.samples.every(v=>Number.isFinite(v)&&Math.abs(v)<=d.digital_level);\n"],["if(good)showDigital();\nconst original=runChecks;","window.addEventListener(\"fik-native-snapshot\",e=>{source=e.detail;good=validSource(source);tab.disabled=!good;id(\"digital-info\").textContent=good?\"C11 · \"+source.command_hz+\" Hz · \"+source.count+\" samples · \"+source.rate_hz+\" Hz · DIGITAL ONLY\":\"No native digital snapshot available\";if(good)showDigital();else showAcquisition();});\nconst original=runChecks;"],["y:{range:[-.27,.27]}","y:{range:[-1.05,1.05]}"]]
SCIENCE_PATCH=[["const $=id=>document.getElementById(id), source=JSON.parse($(\"fik-source\").textContent);\nconst good=source.source===\"FREQMED_NATIVE_C_MEMORY_ONLY\"&&source.physical_output===false&&source.physical_measurement===false&&\n source.count===4096&&source.samples?.length===4096&&FIKScience.valid(source.samples,source.rate_hz)&&source.samples.every(v=>Math.abs(v)<=.25);\nconst x=good?source.samples:null,rate=good?source.rate_hz:0;\nconst spec=good?FIKScience.spectrum(x,rate):null,st=good?FIKScience.spectrogram(x,rate):null,stats=good?FIKScience.stats(x,rate):null;\nconst times=good?x.map((_,i)=>i*1000/rate):[];\n","const $=id=>document.getElementById(id);\nlet source={source:\"UNAVAILABLE\"},good=false,x=null,rate=0,spec=null,st=null,stats=null,times=[];\nconst validSource=d=>d.source===\"FREQMED_NATIVE_C_MEMORY_ONLY\"&&d.session_closed===true&&d.guardian_off===true&&d.physical_output===false&&d.physical_measurement===false&&Number.isInteger(d.rate_hz)&&d.rate_hz>0&&d.rate_hz<=384000&&d.count===4096&&Number.isFinite(d.digital_level)&&d.digital_level>0&&d.digital_level<=1&&Array.isArray(d.samples)&&d.samples.length===4096&&d.samples.every(v=>Number.isFinite(v)&&Math.abs(v)<=d.digital_level);\nfunction update(d){source=d;good=validSource(d);x=good?d.samples:null;rate=good?d.rate_hz:0;spec=good?FIKScience.spectrum(x,rate):null;st=good?FIKScience.spectrogram(x,rate):null;stats=good?FIKScience.stats(x,rate):null;times=good?x.map((_,i)=>i*1000/rate):[];}\n"],["stats.peak<=.25","stats.peak<=source.digital_level"],["freq?[-120,0]:[-.27,.27]","freq?[-120,0]:[-1.05,1.05]"],["if(!good){$(\"sc-readout\").textContent=\"—\";return;}","if(!good){$(\"sc-readout\").textContent=\"—\";$(\"sc-method\").textContent=\"\";return;}"],["translate();setMetrics();render();","window.addEventListener(\"fik-native-snapshot\",e=>{update(e.detail);setMetrics();select(mode);});\ntranslate();setMetrics();render();"]]

def verify(data,pin):
    if hashlib.sha1(("blob %d"%len(data)).encode()+b"\0"+data).hexdigest()!=pin:
        raise RuntimeError("BLOB_MISMATCH "+pin)
    return data
def once(s,a,b):
    if s.count(a)!=1:raise RuntimeError("BOUNDARY_MISMATCH "+a[:80])
    return s.replace(a,b,1)
def valid_command(d):
    return type(d) is dict and set(d)=={"frequency_hz","level_percent","duration_ms"} and all(
        type(d[k]) is int and 1<=d[k]<=limit for k,limit in
        (("frequency_hz",22049),("level_percent",100),("duration_ms",10000)))
def run_native(exe,cmd):
    if not valid_command(cmd):return {"source":"UNAVAILABLE","reason":"INVALID_COMMAND"}
    try:
        raw=subprocess.check_output([str(exe),str(cmd["frequency_hz"]),str(cmd["level_percent"]),str(cmd["duration_ms"])],timeout=5)
        if len(raw)>180000:raise ValueError("oversize result")
        d=json.loads(raw)
        if d.get("source")=="UNAVAILABLE":
            return {"source":"UNAVAILABLE","reason":str(d.get("reason","NATIVE_UNAVAILABLE"))[:100]}
        x=d["samples"];rate=d["rate_hz"]
        if not (d["source"]=="FREQMED_NATIVE_C_MEMORY_ONLY" and d["session_closed"] is True and d["guardian_off"] is True and
                d["physical_output"] is False and d["physical_measurement"] is False and
                type(rate) in (int,float) and float(rate).is_integer() and 0<rate<=384000 and
                d["command_hz"]==cmd["frequency_hz"] and d["digital_level"]==cmd["level_percent"]/100 and
                d["duration_ms"]==cmd["duration_ms"] and d["count"]==len(x)==4096 and
                all(type(v) in (float,int) and math.isfinite(v) and abs(v)<=d["digital_level"] for v in x)):
            raise ValueError("invalid native result")
        return d
    except (OSError,subprocess.SubprocessError,ValueError,KeyError,TypeError):
        return {"source":"UNAVAILABLE","reason":"NATIVE_PROCESS_OR_RESULT_REJECTED"}
def build(repo,w,secret):
    src={}
    for name,ref,path,pin in PINS:
        data=subprocess.check_output(["git","-C",str(repo),"show",ref+":"+path],timeout=30)
        src[name]=verify(data,pin).decode("utf-8")
    own={name:verify((ROOT/name).read_bytes(),pin).decode("utf-8") for name,pin in OWN.items()}
    runner=w/"pinned_runner.py";runner.write_text(src["qualify.py"],encoding="utf-8")
    spec=importlib.util.spec_from_file_location("pinned_runner",runner)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    for ref,path,pin in mod.PINS:
        (w/pathlib.Path(path).name).write_bytes(mod.get(repo,ref,"generator/candidates/"+path,pin))
    s=(w/"mac_readiness.c").read_text(encoding="utf-8")
    marker="static const char *verdict(FMReadinessResult r) {"
    if s.count(marker)!=1:raise RuntimeError("COLLECTOR_BOUNDARY")
    (w/"mac_capture_pinned.inc").write_text(s.split(marker,1)[0].removeprefix("#define _POSIX_C_SOURCE 200809L\n"),encoding="utf-8")
    names=["generator_core.c","output_hard_denied.c","em_device_contract.c","integration.c","session.c","session_clock.c","binding.c","monitor.c","recovery.c","readiness.c","assembly.c","digital_signal.c"]
    exe=w/"native_command"
    subprocess.run(["cc","-std=c11","-Wall","-Wextra","-Werror","-pedantic","-I",str(w),*[str(w/n) for n in names],
                    str(ROOT/"native_command.c"),"-lm","-framework","CoreAudio","-framework","CoreFoundation","-o",str(exe)],check=True,timeout=120)
    for name,patches in (("render.js",RENDER_PATCH),("science-ui.js",SCIENCE_PATCH)):
        for a,b in patches:src[name]=once(src[name],a,b)
    page=src["base.html"].replace("UI-001","UI-004").replace("UI check","UI / renderer check")
    page=once(page,"connect-src 'none'","connect-src 'self'")
    page=once(page,"</style>",src["vendor/uPlot.min.css"]+"\n"+src["render.css"]+"\n"+src["science.css"]+"\n"+own["bridge.css"]+"\n</style>")
    page=once(page,'<div class="screen" id="screen">','<button id="digital-tab" type="button" aria-pressed="false">Digital command</button><div class="renderer-status" id="renderer-status" aria-live="polite"></div><div class="digital-plot" id="digital-plot" hidden></div><div class="digital-info" id="digital-info" hidden></div><div class="screen" id="screen"><canvas class="fik-grid" id="gpu-grid" aria-hidden="true" hidden></canvas><canvas class="fik-grid" id="cpu-grid" aria-hidden="true" hidden></canvas>')
    science=src["science.html"].replace("Independent of the draft controls.","Explicit digital calculation only.")
    page=once(page,'<footer class="bottom">',science+'\n<footer class="bottom">')
    page=once(page,'<p class="notice" data-t="notice">','<div class="native-bridge"><button id="native-calculate" type="button">Calculate digital block</button><output id="native-result" aria-live="polite"></output><span class="tiny" id="native-notice"></span></div><p class="notice" data-t="notice">')
    scripts=[src["vendor/uPlot.iife.min.js"],src["render.js"],src["science.js"],src["science-ui.js"],own["bridge.js"]]
    if any("</script" in x.lower() for x in scripts):raise RuntimeError("SCRIPT_BOUNDARY")
    page=once(page,"</body>",'<script type="application/json" id="fik-source">{"source":"UNAVAILABLE"}</script><span id="native-token" hidden>'+htmlmod.escape(secret)+'</span>'+"".join("\n<script>\n"+s+"\n</script>" for s in scripts)+"\n</body>")
    print("UI_SOURCE_PINS="+str(len(PINS)+len(OWN))+" PASS",flush=True)
    print("NATIVE_SOURCE_PINS="+str(len(mod.PINS))+" PASS",flush=True)
    return page.encode("utf-8"),exe
def handler(page,exe,secret):
    class Handler(BaseHTTPRequestHandler):
        def setup(self):
            super().setup();self.connection.settimeout(6)
        def log_message(self,*args):pass
        def reply(self,status,data,content="application/json; charset=utf-8"):
            if not isinstance(data,bytes):data=json.dumps(data,allow_nan=False,separators=(",",":")).encode()
            self.send_response(status);self.send_header("Content-Type",content)
            self.send_header("Content-Length",str(len(data)));self.send_header("Cache-Control","no-store")
            self.send_header("X-Content-Type-Options","nosniff");self.send_header("X-Frame-Options","DENY")
            self.send_header("Content-Security-Policy","frame-ancestors 'none'")
            self.send_header("Referrer-Policy","no-referrer");self.end_headers()
            try:self.wfile.write(data)
            except (BrokenPipeError,ConnectionResetError,TimeoutError):pass
        def reject(self,status,reason):self.reply(status,{"source":"UNAVAILABLE","reason":reason})
        def host(self):return self.headers.get_all("Host")==["127.0.0.1:"+str(self.server.server_port)]
        def do_GET(self):
            if not self.host():return self.reject(403,"HOST_REJECTED")
            if self.path!="/":return self.reject(404,"ROUTE_REJECTED")
            self.reply(200,page,"text/html; charset=utf-8")
        def do_POST(self):
            if not self.host() or self.headers.get_all("Origin")!=["http://127.0.0.1:"+str(self.server.server_port)]:
                return self.reject(403,"ORIGIN_REJECTED")
            if self.path!="/api/digital":return self.reject(404,"ROUTE_REJECTED")
            tokens=self.headers.get_all("X-FIK-Token") or []
            if len(tokens)!=1 or not hmac.compare_digest(tokens[0].encode(),secret.encode()):
                return self.reject(403,"TOKEN_REJECTED")
            if self.headers.get_all("Content-Type")!=["application/json"] or self.headers.get("Transfer-Encoding"):
                return self.reject(415,"CONTENT_REJECTED")
            lengths=self.headers.get_all("Content-Length") or []
            if len(lengths)!=1 or not lengths[0].isascii() or not lengths[0].isdigit() or len(lengths[0])>4:
                return self.reject(400,"LENGTH_REJECTED")
            n=int(lengths[0])
            if not 1<=n<=512:return self.reject(400,"LENGTH_REJECTED")
            try:
                raw=self.rfile.read(n)
                if len(raw)!=n:raise ValueError("short body")
                def unique(pairs):
                    d={}
                    for k,v in pairs:
                        if k in d:raise ValueError("duplicate")
                        d[k]=v
                    return d
                cmd=json.loads(raw,object_pairs_hook=unique)
            except (ValueError,UnicodeError,RecursionError,OSError):return self.reject(400,"JSON_REJECTED")
            if not valid_command(cmd):return self.reject(400,"INVALID_COMMAND")
            result=run_native(exe,cmd)
            self.reply(200 if result["source"]!="UNAVAILABLE" else 422,result)
    return Handler
def qualify(server,secret):
    import http.client,threading
    t=threading.Thread(target=server.serve_forever,daemon=True);t.start()
    host="127.0.0.1:"+str(server.server_port)
    headers={"Origin":"http://"+host,"X-FIK-Token":secret,"Content-Type":"application/json"}
    cmd={"frequency_hz":440,"level_percent":25,"duration_ms":1000}
    def request(method,path,body=None,h=None):
        conn=http.client.HTTPConnection("127.0.0.1",server.server_port,timeout=12)
        try:
            conn.request(method,path,body=body,headers=h or {})
            r=conn.getresponse();data=r.read()
            return r.status,data
        finally:conn.close()
    try:
        checks={}
        checks["page"]=request("GET","/")[0]==200
        checks["host"]=request("GET","/",h={"Host":"example.invalid"})[0]==403
        checks["route"]=request("GET","/unknown")[0]==404
        body=json.dumps(cmd)
        checks["origin"]=request("POST","/api/digital",body,{**headers,"Origin":"http://example.invalid"})[0]==403
        checks["token"]=request("POST","/api/digital",body,{**headers,"X-FIK-Token":"invalid"})[0]==403
        checks["schema"]=request("POST","/api/digital",json.dumps({**cmd,"extra":1}),headers)[0]==400
        checks["zero_level"]=request("POST","/api/digital",json.dumps({**cmd,"level_percent":0}),headers)[0]==400
        checks["bool"]=request("POST","/api/digital",json.dumps({**cmd,"frequency_hz":True}),headers)[0]==400
        checks["duplicate"]=request("POST","/api/digital",'{"frequency_hz":440,"frequency_hz":880,"level_percent":25,"duration_ms":1000}',headers)[0]==400
        checks["oversize"]=request("POST","/api/digital","x"*513,headers)[0]==400
        a,raw=request("POST","/api/digital",body,headers);d1=json.loads(raw)
        b,raw=request("POST","/api/digital",json.dumps({**cmd,"frequency_hz":880,"level_percent":15}),headers);d2=json.loads(raw)
        native=a==b==200 and d1["samples"]!=d2["samples"] and d1["command_hz"]==440 and d2["command_hz"]==880
        report={"http_checks":checks,"http_passed":sum(checks.values()),"http_total":len(checks),"native_two_commands":native,
                "native_results":[d.get("reason",d.get("command_hz")) for d in (d1,d2)],"physical_output":"NONE","browser":"NOT_EXECUTED"}
        print("FIK_UI004_REPORT="+json.dumps(report,sort_keys=True),flush=True)
        if not all(checks.values()):raise RuntimeError("HTTP_QUALIFICATION_FAILED")
    finally:server.shutdown();t.join()
def main():
    if len(sys.argv)!=2 or platform.system()!="Darwin":raise SystemExit("Usage on macOS: python3 -B serve.py REPO")
    repo=pathlib.Path(sys.argv[1]).resolve(strict=True)
    secret=secrets.token_urlsafe(32)
    with tempfile.TemporaryDirectory(prefix="freqmed_ui004_") as tmp:
        page,exe=build(repo,pathlib.Path(tmp),secret)
        with HTTPServer(("127.0.0.1",0),handler(page,exe,secret)) as server:
            qualify(server,secret)
            url="http://127.0.0.1:"+str(server.server_port)+"/"
            print("FREQMED_UI004_URL="+url,flush=True)
            print("Stop local server with Ctrl-C; no physical backend.",flush=True)
            subprocess.run(["open","-a","Safari",url],check=False)
            try:server.serve_forever()
            except KeyboardInterrupt:print("FREQMED_UI004_SERVER_STOPPED",flush=True)
if __name__=="__main__":main()
