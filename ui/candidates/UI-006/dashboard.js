/* SPDX-License-Identifier: Apache-2.0 */
(()=>{
"use strict";
const $=id=>document.getElementById(id),M=FIKDashboardMath;
const bars=["peak","rms"];
for(const kind of bars){
 const host=$("dash-"+kind+"-bar");
 for(let i=0;i<24;i++){const e=document.createElement("i");e.setAttribute("aria-hidden","true");host.appendChild(e);}
}
let last=null,phase="IDLE";
function setBar(kind,v,db){
 const host=$("dash-"+kind+"-bar"),n=M.segments(db);
 [...host.children].forEach((e,i)=>e.classList.toggle("lit",i<n));
 host.setAttribute("aria-valuenow",String(v??0));
 host.setAttribute("aria-valuetext",v===null?"Unavailable":db===null?"Digital zero":db.toFixed(2)+" dBFS");
 $("dash-"+kind+"-number").textContent=v===null?"—":db===null?"−∞ dBFS":db.toFixed(2)+" dBFS";
}
function empty(){
 last=null;for(const kind of bars)setBar(kind,null,null);
 $("dash-rate").textContent="—";$("dash-window").textContent="—";
 $("dash-percent").textContent="—";$("dash-ring").style.setProperty("--session-angle","0deg");
 $("dash-sequence").textContent="—";$("dash-coverage").textContent="—";
}
function state(s){
 phase=s;const stage=$("dash-stage");stage.textContent=s;
 $("dash-window-state").textContent=s==="STATUS UNKNOWN"?"Last received graph may be stale · connection unconfirmed":s==="STOP REQUESTED"||s==="STOPPING"?"Stop requested · waiting for native receipt":s==="COMPLETE"?"Final received digital window":"RUNNING"===s?"Waiting for next received digital window":"No received digital window";
 stage.dataset.state=s;document.documentElement.dataset.runtimeState=s;
 $("dash-ring").setAttribute("aria-label","Digital session: "+s);
 if(["IDLE","STARTING","STATUS UNKNOWN","START UNCONFIRMED","JOB NO LONGER AVAILABLE","STOPPED","EXPIRED","INVALIDATED","FAULT","REJECTED"].includes(s))empty();
}
function record(j){
 if(!j||!["RUNNING","COMPLETE","STOPPING"].includes(j.state))return;
 const d=j.record;
 if(!d||d.source!=="FREQMED_NATIVE_C_MEMORY_ONLY"||d.guardian_off!==true||d.physical_output!==false||d.physical_measurement!==false||
    !Number.isSafeInteger(d.rate_hz)||d.rate_hz<=0||d.rate_hz>384000||
    !Number.isSafeInteger(d.sequence)||d.sequence<1||!Number.isSafeInteger(d.count)||
    !Array.isArray(d.samples)||d.samples.length!==d.count||d.count>d.processed)return;
 const m=M.metrics(d.samples),p=M.progress(d.processed,d.expected);
 if(!m||p===null||!Number.isFinite(d.digital_level)||d.digital_level<=0||d.digital_level>1||m.peak>d.digital_level)return;
 last={m,p,d};
 $("dash-window-state").textContent=(j.state==="COMPLETE"?"Final":j.state==="STOPPING"?"Last before stop confirmation":"Latest")+" received digital window · block "+d.sequence+(d.count<4096?" · spectrum unavailable (short window)":"");
 setBar("peak",m.peak,m.peakDb);setBar("rms",m.rms,m.rmsDb);
 $("dash-rate").textContent=d.rate_hz.toLocaleString()+" Hz";
 $("dash-window").textContent=(1000*d.count/d.rate_hz).toFixed(2)+" ms";
 $("dash-percent").textContent=(p*100).toFixed(1)+"%";
 $("dash-ring").style.setProperty("--session-angle",p*360+"deg");
 $("dash-sequence").textContent=String(d.sequence);
 $("dash-coverage").textContent=d.processed.toLocaleString()+" / "+d.expected.toLocaleString();
}
window.addEventListener("fik-runtime-state",e=>state(e.detail));
window.addEventListener("fik-runtime-record",e=>record(e.detail));
window.addEventListener("fik-native-snapshot",e=>{if(e.detail?.source==="UNAVAILABLE"&&phase!=="COMPLETE")empty();});
$("dash-check").addEventListener("click",()=>{
 const checks=M.tests();
 checks.single_science_suite=document.querySelectorAll("#science-suite").length===1&&$("science-suite").closest(".center")!==null;
 checks.acquisition_separate=!!$("acquisition-disclosure").querySelector("#screen");
 checks.physical_disabled=document.querySelector(".start").disabled&&document.querySelector(".stop").disabled;
 checks.segments_dom=bars.every(k=>$("dash-"+k+"-bar").children.length===24);
 checks.source_label=$("dash-stage").textContent===phase;
 checks.meter_consistent=bars.every(k=>[...$("dash-"+k+"-bar").children].filter(e=>e.classList.contains("lit")).length===(last?M.segments(last.m[k+"Db"]):0));
 const n=Object.values(checks).filter(Boolean).length,total=Object.keys(checks).length;
 $("dash-check-result").textContent=n+"/"+total+" "+(n===total?"PASS":"FAIL");
 console.log("FIK_UI006_DASHBOARD_REPORT="+JSON.stringify({checks,passed:n,total,state:phase,native_window:!!last,physical_output:"NONE"}));
});
empty();state($("runtime-state").textContent);
})();
