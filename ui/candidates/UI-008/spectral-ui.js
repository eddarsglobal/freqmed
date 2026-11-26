/* SPDX-License-Identifier: Apache-2.0 */
(()=>{
"use strict";
const $=id=>document.getElementById(id),S=FIKSpectral;
let current=null,reference=null,history=[],fit=null,frame=0;
const fmt=(v,n=2)=>v==null?"—":v.toFixed(n);
const color=k=>getComputedStyle(document.documentElement).getPropertyValue(k).trim();
function valid(d){return d&&d.source==="FREQMED_NATIVE_C_MEMORY_ONLY"&&d.guardian_off===true&&d.physical_output===false&&d.physical_measurement===false&&
 ((d.state==="RUNNING"&&d.session_closed===false)||(d.state==="COMPLETE"&&d.session_closed===true))&&d.count===4096&&
 Number.isSafeInteger(d.sequence)&&d.sequence>0&&Number.isSafeInteger(d.processed)&&d.processed>=4096&&
 Number.isFinite(d.command_hz)&&d.command_hz>0&&d.command_hz<d.rate_hz/2&&
 Number.isFinite(d.digital_level)&&d.digital_level>0&&d.digital_level<=1&&FIKScience.valid(d.samples,d.rate_hz)&&d.samples.length===4096&&d.samples.every(v=>Math.abs(v)<=d.digital_level);}
function snapshot(d){const spectrum=FIKScience.spectrum(d.samples,d.rate_hz),m=FIKScience.stats(d.samples,d.rate_hz);return {rate:d.rate_hz,n:d.count,command:d.command_hz,seq:d.sequence,processed:d.processed,spectrum,peaks:S.peaks(spectrum),rms:m.rms,peak:m.peak,samples:d.samples.slice()};}
function rows(host,data){host.replaceChildren();for(const row of data){const tr=document.createElement("tr");for(const val of row){const td=document.createElement("td");td.textContent=val;tr.append(td);}host.append(tr);}}
function fitView(){
 $("spectral-thd").textContent=fit&&fit.thd!==null?fmt(fit.thd*100,6)+" %":"—";
 $("spectral-residual").textContent=fit&&fit.residual!==null?fmt(fit.residual*100,6)+" %":"—";
 rows($("spectral-harmonics"),fit?fit.harmonics.map(h=>[String(h.order),fmt(h.hz),fmt(h.amplitude,8)]):[]);
 $("spectral-fit-note").textContent=fit?"Joint fit at "+fit.commandHz+" Hz · "+fit.harmonics.length+" terms below Nyquist · THD excludes noise and unmodeled orders.":"Analyze a received window (at least four command cycles).";
}
function refresh(){
 const p=current?.peaks[0];
 $("spectral-source").textContent=current?"C11 · digital window #"+current.seq:"No digital window";
 $("spectral-estimate").textContent=p?fmt(p.estimateHz,3)+" Hz":"—";
 $("spectral-bin").textContent=p?fmt(p.binHz,3)+" Hz":"—";
 rows($("spectral-peaks"),current?current.peaks.map(p=>[fmt(p.binHz),fmt(p.estimateHz),fmt(p.db)]):[]);
 $("spectral-freeze").disabled=!current;$("spectral-fit").disabled=!current;
 const d=S.compare(reference,current);
 $("spectral-comparison").textContent=!reference?"No reference captured":!current?"Reference retained · no current window":!d?"Incompatible sample rate or window length":
 "Reference "+reference.command+" Hz · current "+current.command+" Hz · Δ command "+fmt(d.deltaCommand)+" Hz · Δ RMS "+fmt(d.deltaRms,6)+" · Δ peak "+fmt(d.deltaPeak,6);
 fitView();schedule();
}
function clear(){current=null;fit=null;refresh();}
function receive(d){
 if(!valid(d)){clear();return;}
 const next=snapshot(d);
 if(!history.length||history[history.length-1].processed!==next.processed){
  history.push({rate:next.rate,processed:next.processed,seq:next.seq,db:next.spectrum.db.slice()});
  if(history.length>24)history.shift();
 }
 if(!current||current.processed!==next.processed||current.command!==next.command)fit=null;
 current=next;refresh();
}
window.addEventListener("fik-native-snapshot",e=>receive(e.detail));
window.addEventListener("fik-runtime-state",e=>{
 if(["STARTING","IDLE"].includes(e.detail)){history=[];clear();}
 else if(["STATUS UNKNOWN","START UNCONFIRMED","JOB NO LONGER AVAILABLE","STOPPED","EXPIRED","INVALIDATED","FAULT","REJECTED"].includes(e.detail)){history=[];clear();}
});
$("spectral-freeze").onclick=()=>{if(current){reference=current;refresh();}};
$("spectral-clear").onclick=()=>{reference=null;refresh();};
$("spectral-fit").onclick=()=>{if(!current)return;fit=S.harmonicFit(current.samples,current.rate,current.command);fitView();if(!fit)$("spectral-fit-note").textContent="Fit unavailable: insufficient cycles, amplitude or conditioning.";};
$("spectral-scale").onchange=schedule;
function context(id){const c=$(id),r=Math.min(2,window.devicePixelRatio||1),w=Math.max(1,Math.min(2400,Math.round(c.clientWidth*r))),h=Math.max(1,Math.min(1000,Math.round(c.clientHeight*r)));if(c.width!==w)c.width=w;if(c.height!==h)c.height=h;const ctx=c.getContext("2d");if(ctx){ctx.clearRect(0,0,w,h);ctx.font=11*r+"px system-ui";ctx.fillStyle=color("--muted");}return {ctx,w,h,r};}
function empty(c,w,h,r,label){c.fillText(label,Math.max(8*r,w/2-c.measureText(label).width/2),h/2);}
function graph(){
 const {ctx:c,w,h,r}=context("spectral-canvas");if(!c)return;
 if(!current){empty(c,w,h,r,"No digital spectrum");$("spectral-axis-note").textContent="No digital data";return;}
 const log=$("spectral-scale").value==="log",lo=log?current.spectrum.binHz:0,hi=current.rate/2,L=47*r,R=w-15*r,T=14*r,B=h-28*r;
 if(R<=L||B<=T)return;
 const xx=f=>L+S.axis(f,lo,hi,log)*(R-L),yy=db=>T+(0-Math.max(-120,Math.min(0,db)))/120*(B-T);
 c.strokeStyle=color("--edge");c.fillStyle=color("--muted");
 for(const db of [0,-30,-60,-90,-120]){const y=yy(db);c.beginPath();c.moveTo(L,y);c.lineTo(R,y);c.stroke();c.fillText(String(db),4*r,y+4*r);}
 for(let i=0;i<=4;i++){const f=log?lo*Math.pow(hi/lo,i/4):lo+(hi-lo)*i/4,x=xx(f);c.beginPath();c.moveTo(x,T);c.lineTo(x,B);c.stroke();c.fillText(Math.round(f)+"",Math.min(R-24*r,x),B+15*r);}
 function line(s,ink){c.strokeStyle=ink;c.lineWidth=r;c.beginPath();let start=true;for(let k=log?1:0;k<s.hz.length;k++){const x=xx(s.hz[k]),y=yy(s.db[k]);if(start){c.moveTo(x,y);start=false;}else c.lineTo(x,y);}c.stroke();}
 c.save();c.beginPath();c.rect(L,T,R-L,B-T);c.clip();
 if(S.comparable(reference,current))line(reference.spectrum,color("--violet"));line(current.spectrum,color("--cyan"));
 for(const p of current.peaks){const x=xx(p.binHz),y=yy(p.db);c.fillStyle=color("--amber");c.beginPath();c.arc(x,y,3*r,0,2*Math.PI);c.fill();}
 c.restore();$("spectral-axis-note").textContent=(log?"Log axis · DC excluded":"Linear axis")+" · Hz / dBFS · cyan current, violet compatible reference, amber detected bins";
}
function palette(db){const v=Math.max(0,Math.min(1,(db+100)/100)),p=v*4,i=Math.min(3,Math.floor(p)),f=p-i,C=[[9,19,31],[36,79,157],[125,69,173],[237,123,89],[255,222,135]];return "rgb("+C[i].map((x,j)=>Math.round(x+(C[i+1][j]-x)*f)).join(",")+")";}
function heat(){
 const {ctx:c,w,h,r}=context("spectral-history");if(!c)return;
 if(!history.length){empty(c,w,h,r,"No received windows");$("spectral-history-note").textContent="No windows";return;}
 const rows=128,N=history.length;let skipped=0;
 for(let i=0;i<N;i++){
  const a=history[i];if(i)skipped+=Math.max(0,a.seq-history[i-1].seq-1);
  for(let k=0;k<rows;k++){const start=Math.floor(k*a.db.length/rows),end=Math.floor((k+1)*a.db.length/rows);let v=-120;for(let j=start;j<end;j++)v=Math.max(v,a.db[j]);
   c.fillStyle=palette(v);const l=Math.floor(i*w/N),rr=Math.ceil((i+1)*w/N),t=Math.floor((rows-1-k)*h/rows),b=Math.ceil((rows-k)*h/rows);c.fillRect(l,t,rr-l,b-t);}
  if(i&&a.seq-history[i-1].seq>1){c.fillStyle="#ffffff";c.fillRect(Math.floor(i*w/N),0,Math.max(1,r),h);}
 }
 $("spectral-history-note").textContent=N+" received windows · block "+history[0].seq+"–"+history[N-1].seq+" · "+skipped+" intervening block(s) not received · vertical 0–"+(history[N-1].rate/2)+" Hz · columns are observations, not uniform time";
}
function schedule(){if(!frame)frame=requestAnimationFrame(()=>{frame=0;graph();heat();});}
$("theme").addEventListener("change",schedule);window.addEventListener("resize",schedule);
if(typeof ResizeObserver==="function")new ResizeObserver(schedule).observe($("spectral-canvas"));
$("spectral-check").onclick=()=>{
 const checks=S.tests();checks.source_gate=!!current||$("spectral-fit").disabled;checks.bounded_history=history.length<=24;checks.physical_disabled=document.querySelector(".start").disabled&&document.querySelector(".stop").disabled;checks.reference_gate=!reference||reference.n===4096;
 const v=Object.values(checks),n=v.filter(Boolean).length;$("spectral-result").textContent=n+"/"+v.length+" "+(n===v.length?"PASS":"FAIL");console.log("FIK_UI008_REPORT="+JSON.stringify({checks,passed:n,total:v.length,native_window:!!current,physical_output:"NONE"}));
};
refresh();
})();
