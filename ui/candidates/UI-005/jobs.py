# SPDX-License-Identifier: Apache-2.0
import json,math,secrets,subprocess,threading
TERMINAL={"COMPLETE","STOPPED","EXPIRED","INVALIDATED","FAULT","REJECTED"}
def valid_record(d,cmd,prior):
    if type(d) is not dict:return False
    state=d.get("state")
    if state=="REJECTED":
        return prior is None and type(d.get("reason")) is str and len(d["reason"])<=100
    if state not in TERMINAL|{"RUNNING"}:return False
    try:
        r,t,e,s,n,x=(d[k] for k in ("rate_hz","processed","expected","sequence","count","samples"))
        if (type(r) not in (int,float) or not float(r).is_integer() or not 0<r<=384000 or
            any(type(v) is not int for v in (t,e,s,n)) or
            e!=int(r)*cmd["duration_ms"]//1000 or not 0<=t<=e or s!=(t+4095)//4096 or
            d["source"]!="FREQMED_NATIVE_C_MEMORY_ONLY" or d["guardian_off"] is not True or
            d["physical_output"] is not False or d["physical_measurement"] is not False or
            d["session_closed"] is not (state!="RUNNING") or
            d["command_hz"]!=cmd["frequency_hz"] or d["digital_level"]!=cmd["level_percent"]/100 or
            d["duration_ms"]!=cmd["duration_ms"] or not 0<=n<=4096 or type(x) is not list or len(x)!=n or
            any(type(v) not in (int,float) or not math.isfinite(v) or abs(v)>d["digital_level"] for v in x)):
            return False
        old=prior["processed"] if prior else 0
        if prior and (r!=prior["rate_hz"] or e!=prior["expected"]):return False
        if state=="RUNNING":return t==old+4096 and t<e and n==min(t,4096)
        if state=="COMPLETE":return 0<t-old<=4096 and t==e and n==min(t,4096)
        return old<=t<=old+4096 and n==0
    except (KeyError,TypeError,ValueError,OverflowError):return False
class Jobs:
    def __init__(self,exe):
        self.exe=exe;self.lock=threading.Lock();self.job=None;self.worker=None
    def start(self,cmd):
        with self.lock:
            if self.job and self.job["state"] not in TERMINAL:return None
            proc=subprocess.Popen([str(self.exe),str(cmd["frequency_hz"]),str(cmd["level_percent"]),str(cmd["duration_ms"])],
                stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
            j={"id":secrets.token_hex(16),"state":"STARTING","proc":proc,"record":None,"reason":""}
            self.job=j
            self.worker=threading.Thread(target=self.read,args=(j,cmd),daemon=True);self.worker.start()
            return j["id"]
    def read(self,j,cmd):
        p=j["proc"];prior=None;last=None;reason=""
        watchdog=threading.Timer(15,lambda:p.kill() if p.poll() is None else None)
        watchdog.daemon=True;watchdog.start()
        try:
            while True:
                raw=p.stdout.readline(180001)
                if not raw:break
                if len(raw)>180000 or not raw.endswith(b"\n") or last is not None:raise ValueError("FRAMING")
                d=json.loads(raw)
                if not valid_record(d,cmd,prior):raise ValueError("NATIVE_RECORD_INVALID")
                if d["state"]=="RUNNING":
                    prior=d
                    with self.lock:
                        j["record"]=d
                        if j["state"]!="STOPPING":j["state"]="RUNNING"
                else:last=d
            if p.wait(timeout=2)!=0 or last is None:raise ValueError("NATIVE_EXIT_OR_TERMINAL_MISSING")
        except (ValueError,TypeError,OSError,subprocess.SubprocessError) as e:
            reason=str(e)[:120];last=None
        finally:
            watchdog.cancel()
            if p.poll() is None:
                p.kill();p.wait()
            p.stdout.close()
            with self.lock:
                if last is None:j.update(state="FAULT",record=None,reason=reason or "NATIVE_FAULT")
                else:j.update(state=last["state"],record=last if last["state"]!="REJECTED" else None,reason=last.get("reason",""))
    def status(self,ident):
        with self.lock:
            j=self.job
            if not j or j["id"]!=ident:return None
            return {k:j[k] for k in ("id","state","record","reason")}
    def stop(self,ident):
        with self.lock:
            j=self.job
            if not j or j["id"]!=ident:return None
            if j["state"] not in TERMINAL:
                j["state"]="STOPPING"
                if j["proc"].poll() is None:
                    try:j["proc"].terminate()
                    except ProcessLookupError:pass
            return j["state"]
    def close(self):
        with self.lock:ident=self.job["id"] if self.job else None
        if ident:self.stop(ident)
        if self.worker:
            self.worker.join(timeout=2)
            if self.worker.is_alive():
                with self.lock:p=self.job["proc"]
                if p.poll() is None:p.kill()
                self.worker.join(timeout=3)
