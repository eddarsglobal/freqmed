/* SPDX-License-Identifier: Apache-2.0 */
(()=>{
"use strict";
const $=id=>document.getElementById(id),secret=$("native-token").textContent;
const start=$("native-calculate"),stop=$("digital-stop"),result=$("native-result");
let active=false,ident=null,epoch=0,latest=-1,terminal="",pendingStop=false;
const states=["COMPLETE","STOPPED","EXPIRED","INVALIDATED","FAULT","REJECTED"];
const publish=data=>window.dispatchEvent(new CustomEvent("fik-native-snapshot",{detail:data}));
const words={
en:["Start digital","Stop digital","Digital processing only — physical interfaces unopened."],
fr:["Démarrer numérique","Arrêter numérique","Traitement numérique uniquement — interfaces physiques non ouvertes."],
de:["Digital starten","Digital stoppen","Nur digitale Verarbeitung — physische Schnittstellen ungeöffnet."],
ar:["بدء رقمي","إيقاف رقمي","معالجة رقمية فقط — الواجهات الفيزيائية غير مفتوحة."],
es:["Iniciar digital","Detener digital","Solo procesamiento digital — interfaces físicas sin abrir."],
pt:["Iniciar digital","Parar digital","Apenas processamento digital — interfaces físicas não abertas."],
hr:["Pokreni digitalno","Zaustavi digitalno","Samo digitalna obrada — fizička sučelja nisu otvorena."],
it:["Avvia digitale","Arresta digitale","Solo elaborazione digitale — interfacce fisiche non aperte."],
zh:["启动数字处理","停止数字处理","仅数字处理 — 未打开物理接口。"],
ko:["디지털 시작","디지털 정지","디지털 처리 전용 — 물리 인터페이스 미개방."]
};
function sync(){
 const w=words[document.documentElement.lang]||words.en;
 start.textContent=w[0];stop.textContent=w[1];$("native-notice").textContent=w[2];
 start.disabled=active||channel!=="acoustic";stop.disabled=!active||pendingStop;
 for(const e of document.querySelectorAll("#ac-controls input,#ac-controls select,#acoustic,#em,#reset,#selftest,#science-test"))e.disabled=active;
 for(const e of document.querySelectorAll("[data-knob]")){e.tabIndex=active?-1:0;e.style.pointerEvents=active?"none":"";e.setAttribute("aria-disabled",String(active));}
}
function status(s){$("runtime-state").textContent=s;}
function connection(s){$("bridge-status").textContent=s;}
function clear(){publish({source:"UNAVAILABLE"});$("digital-progress").value=0;$("digital-count").textContent="—";$("digital-time").textContent="—";$("digital-rms").textContent="—";$("digital-meter").value=0;}
async function request(path,body){
 const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),7000);
 try{
  const r=await fetch("/api/"+path,{method:"POST",headers:{"Content-Type":"application/json","X-FIK-Token":secret},body:JSON.stringify(body),cache:"no-store",credentials:"omit",signal:controller.signal});
  const d=await r.json();connection("LOCAL BRIDGE · CONNECTED");
  if(!r.ok){const e=Error(d.reason||"REQUEST_REJECTED");e.httpStatus=r.status;throw e;}return d;
 }finally{clearTimeout(timer);}
}
function view(j){
 status(j.state);
 const d=j.record;
 if(d){
  $("digital-progress").value=d.expected?d.processed/d.expected:0;
  $("digital-count").textContent=d.processed.toLocaleString()+" / "+d.expected.toLocaleString()+" samples";
  $("digital-time").textContent=(1000*d.processed/d.rate_hz).toFixed(2)+" ms / "+d.duration_ms+" ms · digital";
  if(d.count&&d.samples.length===d.count){
   let energy=0,peak=0;for(const x of d.samples){energy+=x*x;peak=Math.max(peak,Math.abs(x));}
   $("digital-rms").textContent=Math.sqrt(energy/d.count).toFixed(5);$("digital-meter").value=peak;
  }
  if(d.count===4096&&(d.sequence!==latest||j.state!==terminal)){
   latest=d.sequence;terminal=j.state;publish(d);
  }
 }
 if(states.includes(j.state)){
  active=false;pendingStop=false;
  if(j.state!=="COMPLETE"){publish({source:"UNAVAILABLE"});$("digital-rms").textContent="—";$("digital-meter").value=0;}
  result.textContent=j.state+(j.reason?" · "+j.reason:"")+(d&&d.session_closed?" · native session closed":"");
  if(j.state==="COMPLETE"&&d&&d.count<4096){publish({source:"UNAVAILABLE"});result.textContent+=" · fewer than 4096 samples: spectral window unavailable";}
  sync();
 }
}
async function poll(my){
 if(my!==epoch||!ident)return;
 try{
  const j=await request("status",{id:ident});
  if(my!==epoch)return;
  view(j);
  if(active)setTimeout(()=>poll(my),120);
 }catch(e){
  if(my!==epoch)return;
  if(e.httpStatus===404){active=false;pendingStop=false;clear();status("JOB NO LONGER AVAILABLE");result.textContent="Previous terminal state not confirmed";sync();return;}
  connection("BRIDGE STATUS UNKNOWN");status("STATUS UNKNOWN");result.textContent="Retrying status · "+e.message;
  if(active)setTimeout(()=>poll(my),500);
 }
}
start.addEventListener("click",async()=>{
 if(active||channel!=="acoustic")return;
 if(values.level===0){result.textContent="Digital level must be greater than zero";return;}
 const cmd={frequency_hz:values.freq,level_percent:values.level,duration_ms:values.duration};
 const my=++epoch;active=true;pendingStop=false;ident=null;latest=-1;terminal="";clear();sync();status("STARTING");result.textContent="Starting native digital session";
 try{
  const j=await request("start",cmd);
  if(my!==epoch)return;
  ident=j.id;
  if(pendingStop)await stopJob();
  poll(my);
 }catch(e){
  active=false;pendingStop=false;status("START UNCONFIRMED");result.textContent=e.message+" · native job may remain bounded until its deadline";sync();
 }
});
async function stopJob(){
 if(!ident)return;
 try{await request("stop",{id:ident});}
 catch(e){result.textContent="Stop unconfirmed · "+e.message;pendingStop=false;sync();}
}
stop.addEventListener("click",()=>{if(!active)return;pendingStop=true;sync();status("STOP REQUESTED");void stopJob();});
function dirty(ev){if(active||(ev&&!ev.isTrusted))return;epoch++;clear();status("IDLE");result.textContent="Draft changed · start a new digital session";}
for(const id of ["freq","level","duration"])$(id).addEventListener("change",dirty);
$("fader").addEventListener("input",dirty);
for(const e of document.querySelectorAll("[data-knob]")){
 e.addEventListener("pointerup",dirty);
 e.addEventListener("keydown",ev=>{if(["ArrowUp","ArrowDown","ArrowLeft","ArrowRight","Home","End"].includes(ev.key))dirty(ev);});
}
$("reset").addEventListener("click",dirty);$("em").addEventListener("click",ev=>{dirty(ev);sync();});$("acoustic").addEventListener("click",sync);
$("language").addEventListener("change",sync);
sync();clear();status("IDLE");request("ping",{}).catch(()=>connection("BRIDGE STATUS UNKNOWN"));
})();
