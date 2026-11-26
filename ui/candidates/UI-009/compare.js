/* SPDX-License-Identifier: Apache-2.0 */
const FIKCompare=(()=>{
"use strict";
function valid(d){return !!d&&d.source==="FREQMED_NATIVE_C_MEMORY_ONLY"&&d.guardian_off===true&&d.physical_output===false&&d.physical_measurement===false&&
 d.state==="COMPLETE"&&d.session_closed===true&&d.count===4096&&FIKScience.valid(d.samples,d.rate_hz)&&d.samples.length===4096&&Number.isFinite(d.digital_level)&&d.digital_level>0&&d.digital_level<=1&&
 Number.isFinite(d.command_hz)&&d.command_hz>0&&d.command_hz<d.rate_hz/2&&d.samples.every(v=>Math.abs(v)<=d.digital_level);}
function comparison(a,b){
 if(!valid(a)||!valid(b)||a.rate_hz!==b.rate_hz)return null;
 const x=FIKScience.stats(a.samples,a.rate_hz),y=FIKScience.stats(b.samples,b.rate_hz);
 let e=0;for(let i=0;i<4096;i++)e+=(b.samples[i]-a.samples[i])**2;
 return {frequency:b.command_hz-a.command_hz,rms:y.rms-x.rms,peak:y.peak-x.peak,pointwise:Math.sqrt(e/4096)};
}
function bands(x,rate){
 const s=FIKScience.spectrum(x,rate),out=[];
 for(let k=0;k<128;k++){let v=-120;for(let j=Math.floor(k*s.db.length/128);j<Math.floor((k+1)*s.db.length/128);j++)v=Math.max(v,s.db[j]);out.push(v);}
 return out;
}
function tests(){
 const d={source:"FREQMED_NATIVE_C_MEMORY_ONLY",guardian_off:true,physical_output:false,physical_measurement:false,state:"COMPLETE",session_closed:true,count:4096,rate_hz:44100,command_hz:828,digital_level:.5,samples:Array(4096).fill(.25)};
 const e={...d,command_hz:880,samples:Array(4096).fill(.5)},c=comparison(d,e);
 return {valid:valid(d),physical_denied:!valid({...d,physical_output:true}),not_final:!valid({...d,state:"RUNNING"}),invalid_samples:!valid({...d,samples:[NaN]}),incompatible:comparison(d,{...e,rate_hz:48000})===null,delta_frequency:c.frequency===52,delta_rms:c.rms===.25,delta_peak:c.peak===.25,pointwise:c.pointwise===.25,identity:comparison(d,d).pointwise===0,bands:bands(d.samples,44100).length===128};
}
return Object.freeze({valid,comparison,bands,tests});
})();
(()=>{
"use strict";
const $=id=>document.getElementById(id),M=FIKCompare,secret=$("native-token").textContent;
let current=null,refs=[],serial=0,epoch=0,history=[],archiveState="No completed session",rate=0,frame=0,activeView="science";
const views={science:$("science-suite"),spectral:$("spectral-suite"),compare:$("compare-suite")};
function navigate(name){
 activeView=name;for(const [k,v] of Object.entries(views))v.hidden=k!==name;
 for(const b of document.querySelectorAll("[data-workspace-view]"))b.setAttribute("aria-pressed",String(b.dataset.workspaceView===name));
 schedule();
}
for(const b of document.querySelectorAll("[data-workspace-view]"))b.onclick=()=>navigate(b.dataset.workspaceView);
$("compare-height").oninput=()=>{$("compare-suite").style.setProperty("--chart-height",$("compare-height").value+"px");schedule();};
function options(){
 for(const id of ["compare-a","compare-b"]){const e=$(id),old=e.value;e.replaceChildren(new Option("Select reference",""));
 for(const r of refs)e.add(new Option("#"+r.id+" · "+r.data.command_hz+" Hz · "+Math.round(r.data.digital_level*100)+"%",String(r.id)));
 if(refs.some(r=>String(r.id)===old))e.value=old;}
 $("compare-save").disabled=!current||refs.length>=4;
 $("compare-library").textContent=refs.length+" / 4 final windows retained in RAM";
}
function selected(id){return refs.find(r=>String(r.id)===$(id).value)?.data||null;}
$("compare-save").onclick=()=>{if(!current||refs.length>=4)return;refs.push({id:++serial,data:{...current,samples:current.samples.slice()}});options();if(!$("compare-a").value)$("compare-a").value=String(serial);else $("compare-b").value=String(serial);schedule();};
$("compare-delete").onclick=()=>{const id=$("compare-b").value||$("compare-a").value;refs=refs.filter(r=>String(r.id)!==id);options();schedule();};
$("compare-clear").onclick=()=>{refs=[];options();schedule();};
$("compare-a").onchange=$("compare-b").onchange=schedule;
window.addEventListener("fik-native-snapshot",e=>{current=M.valid(e.detail)?e.detail:null;options();});
window.addEventListener("fik-runtime-state",e=>{if(["STARTING","IDLE","STATUS UNKNOWN","START UNCONFIRMED","JOB NO LONGER AVAILABLE","STOPPED","EXPIRED","INVALIDATED","FAULT","REJECTED"].includes(e.detail)){epoch++;current=null;history=[];archiveState="No confirmed completed session";options();schedule();}});
async function replay(j){
 const mine=++epoch;history=[];rate=j.record.rate_hz;archiveState="Retrieving validated native windows";schedule();
 let after=0,total=j.record.sequence;
 try{
  while(after<total){
   const r=await fetch("/api/archive",{method:"POST",headers:{"Content-Type":"application/json","X-FIK-Token":secret},body:JSON.stringify({id:j.id,after}),cache:"no-store",credentials:"omit"});
   if(!r.ok)throw Error("Archive unavailable");
   const p=await r.json();if(mine!==epoch)return;
   if(p.available!==total||!Array.isArray(p.records)||!p.records.length||p.records.length>8||p.next!==after+p.records.length||p.next>total)throw Error("Invalid archive page");
   for(const d of p.records){
    if(d.sequence!==after+1||d.rate_hz!==rate||d.command_hz!==j.record.command_hz||d.digital_level!==j.record.digital_level||d.duration_ms!==j.record.duration_ms||d.expected!==j.record.expected||d.processed!==Math.min(d.sequence*4096,d.expected)||d.state!==(d.sequence===total?"COMPLETE":"RUNNING")||!Array.isArray(d.samples)||d.samples.length!==d.count||d.count!==Math.min(d.processed,4096)||d.samples.some(v=>!Number.isFinite(v)||Math.abs(v)>d.digital_level))throw Error("Archive record mismatch");
    history.push({seq:d.sequence,bands:d.count===4096?M.bands(d.samples,rate):null});after++;
   }
   archiveState=after+" / "+total+" validated records received";schedule();
   await new Promise(resolve=>setTimeout(resolve,0));
  }
  archiveState=after+" / "+total+" records replayed · "+history.filter(x=>x.bands).length+" full spectral windows";
 }catch(e){if(mine!==epoch)return;archiveState="Incomplete archive · "+after+" / "+total+" · "+e.message;}
 schedule();
}
window.addEventListener("fik-runtime-record",e=>{const j=e.detail;if(j.state==="COMPLETE"&&j.record&&Number.isSafeInteger(j.record.sequence)&&j.record.sequence>0&&j.record.sequence<=938)void replay(j);});
function ctx(id){
 const c=$(id),r=Math.min(devicePixelRatio||1,2),w=Math.max(1,Math.min(2400,Math.round(c.clientWidth*r))),h=Math.max(1,Math.min(1200,Math.round(c.clientHeight*r)));
 if(c.width!==w)c.width=w;if(c.height!==h)c.height=h;const g=c.getContext("2d");if(g)g.clearRect(0,0,w,h);return {g,w,h,r};
}
function draw(id,a,b,spectral){
 const {g,w,h,r}=ctx(id);if(!g)return;const L=48*r,R=w-12*r,T=10*r,B=h-25*r;if(R<=L||B<=T)return;
 const col=k=>getComputedStyle(document.documentElement).getPropertyValue(k).trim();
 g.font=11*r+"px system-ui";g.fillStyle=col("--muted");g.strokeStyle=col("--edge");
 for(let i=0;i<=4;i++){let y=T+i*(B-T)/4;g.beginPath();g.moveTo(L,y);g.lineTo(R,y);g.stroke();g.fillText(spectral?String(-30*i):String(1-i*.5),3*r,y+4*r);}
 if(!a||!b||!M.comparison(a,b)){g.fillText("Select two compatible final windows",L+8*r,h/2);return;}
 for(let i=0;i<=4;i++){let x=L+i*(R-L)/4;g.beginPath();g.moveTo(x,T);g.lineTo(x,B);g.stroke();g.fillText((spectral?a.rate_hz/2*i/4:4095/a.rate_hz*1000*i/4).toFixed(1),Math.min(x,R-32*r),B+15*r);}
 for(const [d,ink] of [[a,"#61cfe5"],[b,"#d59de9"]]){
  const v=spectral?FIKScience.spectrum(d.samples,d.rate_hz).db:d.samples;
  g.strokeStyle=ink;g.lineWidth=r;g.beginPath();for(let i=0;i<v.length;i++){const x=L+i/(v.length-1)*(R-L),y=T+(spectral?-Math.max(-120,Math.min(0,v[i]))/120:(1-v[i])/2)*(B-T);if(i)g.lineTo(x,y);else g.moveTo(x,y);}g.stroke();
 }
}
function heat(){
 const {g,w,h,r}=ctx("compare-history");if(!g)return;
 if(!history.length){g.fillStyle="#8294a8";g.font=12*r+"px system-ui";g.fillText("No replayed native windows",10*r,h/2);return;}
 for(let i=0;i<history.length;i++){const a=history[i],l=Math.floor(i*w/history.length),rr=Math.ceil((i+1)*w/history.length);
 if(!a.bands){g.fillStyle="#64748b";g.fillRect(l,0,rr-l,h);continue;}
 for(let k=0;k<128;k++){const v=Math.max(0,Math.min(1,(a.bands[k]+100)/100));g.fillStyle="hsl("+(240-200*v)+",70%,"+(8+65*v)+"%)";const t=Math.floor((127-k)*h/128),b=Math.ceil((128-k)*h/128);g.fillRect(l,t,rr-l,b-t);}}
}
function schedule(){if(!frame)frame=requestAnimationFrame(()=>{frame=0;$("compare-archive-state").textContent=archiveState;if(activeView!=="compare")return;const a=selected("compare-a"),b=selected("compare-b"),d=M.comparison(a,b);$("compare-delta").textContent=d?"Δ command "+d.frequency+" Hz · Δ RMS "+d.rms.toFixed(6)+" · Δ peak "+d.peak.toFixed(6)+" · index-wise difference RMS "+d.pointwise.toFixed(6):"Select two compatible references";draw("compare-wave",a,b,false);draw("compare-fft",a,b,true);heat();});}
$("compare-check").onclick=()=>{const c=M.tests();c.library_bound=refs.length<=4;c.archive_bound=history.length<=938;c.physical_disabled=document.querySelector(".start").disabled&&document.querySelector(".stop").disabled;c.unique_view=Object.values(views).filter(x=>!x.hidden).length===1;const n=Object.values(c).filter(Boolean).length;$("compare-result").textContent=n+"/"+Object.keys(c).length+" "+(Object.values(c).every(Boolean)?"PASS":"FAIL");console.log("FIK_UI009_REPORT="+JSON.stringify({checks:c,archive_records:history.length,reference_count:refs.length,physical_output:"NONE"}));};
window.addEventListener("resize",schedule);$("theme").addEventListener("change",schedule);options();navigate("science");
})();
