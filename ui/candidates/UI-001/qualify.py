#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Offline source qualification; browser interaction checks are separate."""
import hashlib
import json
import pathlib
import re
from html.parser import HTMLParser

ROOT=pathlib.Path(__file__).resolve().parent
PIN="35d625e00f47bea44fe969841aa69d323ba572a5"
data=(ROOT/"index.html").read_bytes()
html=data.decode("utf-8")
assert hashlib.sha1(("blob %d"%len(data)).encode()+b"\0"+data).hexdigest()==PIN,"HTML_BLOB_MISMATCH"

class Scan(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids=[]
        self.keys=[]
        self.external=[]
        self.knobs=[]
        self.disabled=set()
        self.csp=""
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if "id" in a:self.ids.append(a["id"])
        if "data-t" in a:self.keys.append(a["data-t"])
        if tag in ("script","link","img","iframe","audio","video","source","object","embed") and any(k in a for k in ("src","href","data")):
            self.external.append(tag)
        if a.get("role")=="slider" and "data-knob" in a:self.knobs.append(a["data-knob"])
        if tag=="button" and "disabled" in a:self.disabled.add(a.get("class"))
        if tag=="meta" and a.get("http-equiv","").lower()=="content-security-policy":
            self.csp=a.get("content","")
scan=Scan()
scan.feed(html)
keys=re.search(r'const keys="([^"]+)"',html).group(1).split()
dicts=dict(re.findall(r'^(en|fr|de|ar|es|pt|hr|it|zh|ko):"([^"]+)"',html,re.M))
checks={
 "exact_blob":True,
 "unique_ids":len(scan.ids)==len(set(scan.ids)),
 "languages":set(dicts)==set("en fr de ar es pt hr it zh ko".split()),
 "translation_count":all(len(s.split("|"))==len(keys) and all(s.split("|")) for s in dicts.values()),
 "translation_keys":set(scan.keys)<=set(keys),
 "knobs":set(scan.knobs)=={"freq","level","duration"} and len(scan.knobs)==3,
 "physical_controls_disabled":{"start","stop"}<=scan.disabled,
 "offline_csp":all(s in scan.csp for s in ("default-src 'none'","connect-src 'none'","media-src 'none'","object-src 'none'")),
 "no_external_resources":not scan.external,
 "no_hardware_api":not re.search(r"\b(?:AudioContext|webkitAudioContext|getUserMedia|requestDevice|WebSocket|RTCPeerConnection|XMLHttpRequest|fetch)\s*\(",html),
 "browser_check_count":len(re.findall(r'\bcheck\("',html))==23,
}
for key,value in checks.items():print(key+"="+("PASS" if value else "FAIL"))
print("FIK_SOURCE_REPORT="+json.dumps({"passed":sum(checks.values()),"total":len(checks),"browser_dom":"NOT_EXECUTED_BY_SOURCE_CHECK","hardware":"NOT_CONNECTED","scope":"STATIC_SOURCE_ONLY"},sort_keys=True))
if not all(checks.values()):raise SystemExit(1)
