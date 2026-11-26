#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Build a local UI-003 from pinned UI-002 and the real digital C snapshot."""
import hashlib,json,math,pathlib,re,subprocess,sys,tempfile

ROOT=pathlib.Path(__file__).resolve().parent
BASE="015e75b7036d304156fde3a1f7244d419b1af2cc"
BASE_PINS={
  "qualify.py": "86af927316486fa962679def0121fb7d868cbe6c",
  "digital_export.c": "e5ff27782a55481cb5eae752a8b0cfa8c09d668f",
  "render.js": "536b85e9932035352409c745f7b25d22bb72cebb",
  "render.css": "ebd17b60eb14ee56451bfbbac172f8dd4098734d",
  "vendor/uPlot.iife.min.js": "047f29b64f200a4a872758256e5e66930353d757",
  "vendor/uPlot.min.css": "a030d63f20dafd22c0edbd181002dade612c8f4a",
  "vendor/LICENSE-uPlot.txt": "cde4b3f8352d147d5e626fea36358797c4fc06f2"
}
OWN_PINS={
  "science.js": "52cd5810859eea1b8e7c89717fc9e11226cc8aa4",
  "science.html": "d4b0624a7cdb666e77a67da332dff3cedfa77e52",
  "science.css": "aee7670391f00dd5010e24323c11819b0e0ad6e7",
  "science-ui.js": "4cb8a08a3dc252fabb88c9fad0a64579ce6eace7"
}

def verified(data,pin):
    digest=hashlib.sha1(("blob %d"%len(data)).encode()+b"\0"+data).hexdigest()
    if digest!=pin:raise SystemExit("BLOB_MISMATCH "+pin)
    return data
def once(s,a,b):
    if s.count(a)!=1:raise SystemExit("UI_BOUNDARY_MISMATCH "+a[:60])
    return s.replace(a,b,1)
def main():
    if len(sys.argv)!=2:raise SystemExit("usage: qualify.py REPO")
    repo=pathlib.Path(sys.argv[1]).resolve(strict=True)
    own={n:verified((ROOT/n).read_bytes(),pin).decode("utf-8") for n,pin in OWN_PINS.items()}
    with tempfile.TemporaryDirectory(prefix="freqmed_ui003_") as tmp:
        w=pathlib.Path(tmp)
        for name,pin in BASE_PINS.items():
            data=subprocess.check_output(["git","-C",str(repo),"show",BASE+":ui/candidates/UI-002/"+name],timeout=30)
            dest=w/name
            dest.parent.mkdir(parents=True,exist_ok=True)
            dest.write_bytes(verified(data,pin))
        subprocess.run([sys.executable,"-B",str(w/"qualify.py"),str(repo)],check=True,timeout=240)
        html=(w/"FREQMED_UI002.html").read_text(encoding="utf-8")
    match=re.findall(r'<script type="application/json" id="fik-source">(.*?)</script>',html,re.S)
    if len(match)!=1:raise SystemExit("SOURCE_BOUNDARY_MISMATCH")
    source=json.loads(match[0])
    good=source.get("source")=="FREQMED_NATIVE_C_MEMORY_ONLY"
    metrics=None
    if good:
        x=source["samples"];rate=source["rate_hz"]
        if not (source["count"]==len(x)==4096 and type(rate) in (int,float) and
                float(rate).is_integer() and 0<rate<=384000 and
                source["physical_output"] is False and source["physical_measurement"] is False and
                all(type(v) in (int,float) and math.isfinite(v) and abs(v)<=.25 for v in x)):
            raise SystemExit("INVALID_C_SNAPSHOT")
        metrics={"samples":len(x),"rate_hz":rate,"duration_ms":1000*len(x)/rate,
                 "peak_digital":max(map(abs,x)),"rms_digital":math.sqrt(sum(v*v for v in x)/len(x)),
                 "fft_bin_hz":rate/len(x),"stft_frames":29,"stft_bin_hz":rate/512}
    elif source.get("source")!="UNAVAILABLE":raise SystemExit("UNEXPECTED_SOURCE")
    if any("</script" in own[n].lower() for n in ("science.js","science-ui.js")):raise SystemExit("SCRIPT_BOUNDARY")
    html=html.replace("UI-002","UI-003")
    html=once(html,"</style>",own["science.css"]+"\n</style>")
    html=once(html,'<footer class="bottom">',own["science.html"]+'\n<footer class="bottom">')
    html=once(html,"</body>","<script>\n"+own["science.js"]+"\n</script>\n<script>\n"+own["science-ui.js"]+"\n</script>\n</body>")
    out=ROOT/"FREQMED_UI003.html"
    out.write_text(html,encoding="utf-8")
    print("UI002_SOURCE_PINS=7/7 PASS")
    print("UI003_SOURCE_PINS=4/4 PASS")
    print("FIK_UI003_BUILD_REPORT="+json.dumps({"source":source["source"],"metrics":metrics,"browser_scientific_checks":"NOT_EXECUTED","physical_output":"NONE","html":str(out)},sort_keys=True,allow_nan=False))
if __name__=="__main__":main()
