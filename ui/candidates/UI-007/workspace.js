/* SPDX-License-Identifier: Apache-2.0 */
(()=>{
"use strict";
const M=FIKPrecision,by=id=>document.getElementById(id),suite=by("science-suite"),main=document.querySelector("main");
let source=null,frequency=null,mode="time",expanded=false,indices=[0,0],lastRate=0;
const controls=[by("precision-a"),by("precision-b")];
function valid(d){return d&&d.source==="FREQMED_NATIVE_C_MEMORY_ONLY"&&d.guardian_off===true&&d.physical_output===false&&d.physical_measurement===false&&
 ((d.state==="RUNNING"&&d.session_closed===false)||(d.state==="COMPLETE"&&d.session_closed===true))&&d.count===4096&&
 FIKScience.valid(d.samples,d.rate_hz)&&d.samples.length===4096&&Number.isFinite(d.digital_level)&&d.digital_level>0&&d.digital_level<=1&&d.samples.every(v=>Math.abs(v)<=d.digital_level);}
function series(){
 if(!source||!["time","fft"].includes(mode))return null;
 if(mode==="time")return {x:source.samples.map((_,i)=>1000*i/source.rate_hz),y:source.samples,xunit:"ms",yunit:"digital"};
 const band=by("sc-band").value,hi=band==="full"?source.rate_hz/2:Math.min(Number(band),source.rate_hz/2);
 const n=Math.floor(hi/frequency.binHz)+1;
 return {x:frequency.hz.slice(0,n),y:frequency.db.slice(0,n),xunit:"Hz",yunit:"dBFS"};
}
function notify(){window.dispatchEvent(new CustomEvent("fik-precision-redraw"));}
function paintCursors(redraw=true){
 const s=series(),ok=!!s;
 for(let i=0;i<2;i++){const el=controls[i];el.disabled=!ok;el.max=ok?String(s.x.length-1):"0";indices[i]=ok?Math.max(0,Math.min(s.x.length-1,indices[i])):0;el.value=String(indices[i]);}
 const d=ok?M.differential(indices[0],indices[1],s.x,s.y):null;
 const f=(v,u)=>v.toFixed(u==="digital"?6:3)+" "+u;
 by("precision-readout-a").textContent=d?f(d.ax,s.xunit)+" · "+f(d.ay,s.yunit):"—";
 by("precision-readout-b").textContent=d?f(d.bx,s.xunit)+" · "+f(d.by,s.yunit):"—";
 by("precision-delta-x").textContent=d?f(d.dx,s.xunit):"—";
 by("precision-delta-y").textContent=d?f(d.dy,mode==="fft"?"dB":s.yunit):"—";
 by("precision-source").textContent=d?"Same digital window · B − A":source?"Select Waveform or FFT for A/B":"No digital window";
 if(redraw)notify();
}
function resetCursors(){const s=series();indices=[0,s?Math.min(s.x.length-1,Math.max(1,Math.floor(s.x.length/4))):0];paintCursors();}
function readMode(){const active=suite.querySelector('[data-sc-mode][aria-pressed="true"]');return active?active.dataset.scMode:"time";}
window.addEventListener("fik-native-snapshot",e=>{
 const d=e.detail;
 if(!valid(d)){source=null;frequency=null;lastRate=0;paintCursors();return;}
 const fresh=!source||lastRate!==d.rate_hz;source=d;lastRate=d.rate_hz;frequency=FIKScience.spectrum(d.samples,d.rate_hz);
 if(fresh)resetCursors();else paintCursors();
});
for(const b of suite.querySelectorAll("[data-sc-mode]"))b.addEventListener("click",()=>{mode=readMode();resetCursors();});
by("sc-band").addEventListener("change",paintCursors);
for(let i=0;i<2;i++)controls[i].addEventListener("input",()=>{indices[i]=Number(controls[i].value);paintCursors();});
by("precision-reset").addEventListener("click",resetCursors);
window.addEventListener("fik-precision-chart",e=>{
 const u=e.detail,s=series();if(!s||!u||!u.ctx||!u.bbox||!u.scales.x)return;
 const {left,top,width,height}=u.bbox,c=u.ctx;
 c.save();c.beginPath();c.rect(left,top,width,height);c.clip();
 for(let i=0;i<2;i++){
  const v=s.x[indices[i]];
  if(!Number.isFinite(v)||v<u.scales.x.min||v>u.scales.x.max)continue;
  const px=u.valToPos(v,"x",true);if(!Number.isFinite(px))continue;
  c.strokeStyle=i?"#d59de9":"#61cfe5";c.fillStyle=c.strokeStyle;c.lineWidth=2;c.setLineDash(i?[6,4]:[]);
  c.beginPath();c.moveTo(px,top);c.lineTo(px,top+height);c.stroke();c.font="bold 12px system-ui";c.fillText(i?"B":"A",Math.min(left+width-12,px+4),top+14);
 }
 c.restore();
});
function layout(wide){main.classList.toggle("precision-wide",wide);by("precision-layout").value=wide?"wide":"standard";}
by("precision-layout").addEventListener("change",()=>layout(by("precision-layout").value==="wide"));
function focusState(){by("precision-expand").textContent=expanded?"Exit workspace":"Expand workspace";by("precision-expand").setAttribute("aria-pressed",String(expanded));main.classList.toggle("precision-expanded",expanded);}
by("precision-expand").addEventListener("click",async()=>{
 if(expanded){if(document.fullscreenElement&&document.exitFullscreen){try{await document.exitFullscreen();}catch(_){}}expanded=false;focusState();return;}
 expanded=true;focusState();
 if(main.requestFullscreen){try{await main.requestFullscreen();}catch(_){/* CSS enlargement fallback */}}
 suite.scrollIntoView({block:"nearest"});
});
document.addEventListener("fullscreenchange",()=>{if(!document.fullscreenElement){expanded=false;focusState();}});
document.addEventListener("keydown",e=>{if(e.key==="Escape"&&expanded&&!document.fullscreenElement){expanded=false;focusState();}});
by("precision-check").addEventListener("click",()=>{
 const checks=M.tests(),s=series();
 checks.two_cursors=controls.length===2&&controls.every(el=>el.type==="range");
 checks.source_gate=!!s||controls.every(el=>el.disabled);
 checks.cursor_bounds=controls.every(el=>Number(el.value)>=0&&Number(el.value)<=Number(el.max));
 checks.physical_disabled=document.querySelector(".start").disabled&&document.querySelector(".stop").disabled;
 checks.stop_reachable=main.contains(by("digital-stop"))&&getComputedStyle(by("digital-stop")).display!=="none";
 checks.layout=main.classList.contains("precision-wide")===(by("precision-layout").value==="wide");
 const vals=Object.values(checks),n=vals.filter(Boolean).length;
 by("precision-check-result").textContent=n+"/"+vals.length+" "+(n===vals.length?"PASS":"FAIL");
 console.log("FIK_UI007_REPORT="+JSON.stringify({checks,passed:n,total:vals.length,native_window:!!source,physical_output:"NONE"}));
});
mode=readMode();paintCursors(false);focusState();
})();
