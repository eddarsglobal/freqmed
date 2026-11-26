/* SPDX-License-Identifier: Apache-2.0 */
(()=>{
"use strict";
const get=id=>document.getElementById(id),run=get("native-calculate"),result=get("native-result");
const secret=get("native-token").textContent;
let running=false,revision=0;
const dict={
en:["Calculate digital block","Calculating…","Digital block only; no sound or physical output.","Ready"],
fr:["Calculer le bloc numérique","Calcul en cours…","Bloc numérique uniquement ; aucun son ni sortie physique.","Prêt"],
de:["Digitalblock berechnen","Berechnung…","Nur Digitalblock; keine physische Ausgabe.","Bereit"],
ar:["احسب الكتلة الرقمية","جارٍ الحساب…","كتلة رقمية فقط؛ لا صوت أو خرج فيزيائي.","جاهز"],
es:["Calcular bloque digital","Calculando…","Solo bloque digital; sin salida física.","Listo"],
pt:["Calcular bloco digital","A calcular…","Só bloco digital; sem saída física.","Pronto"],
hr:["Izračunaj digitalni blok","Izračun…","Samo digitalni blok; bez fizičkog izlaza.","Spremno"],
it:["Calcola blocco digitale","Calcolo…","Solo blocco digitale; nessuna uscita fisica.","Pronto"],
zh:["计算数字数据块","正在计算…","仅数字数据块；无物理输出。","就绪"],
ko:["디지털 블록 계산","계산 중…","디지털 블록 전용; 물리 출력 없음.","준비"]
};
function words(){return dict[document.documentElement.lang]||dict.en;}
function sync(){run.disabled=running||channel!=="acoustic";run.textContent=words()[running?1:0];get("native-notice").textContent=words()[2];}
function publish(data){window.dispatchEvent(new CustomEvent("fik-native-snapshot",{detail:data}));}
function valid(data,cmd){return data.source==="FREQMED_NATIVE_C_MEMORY_ONLY"&&data.session_closed===true&&data.guardian_off===true&&
 data.physical_output===false&&data.physical_measurement===false&&Number.isInteger(data.rate_hz)&&data.rate_hz>0&&data.rate_hz<=384000&&
 data.command_hz===cmd.frequency_hz&&data.digital_level===cmd.level_percent/100&&data.duration_ms===cmd.duration_ms&&
 data.count===4096&&FIKScience.valid(data.samples,data.rate_hz)&&data.samples.length===4096&&data.samples.every(v=>Math.abs(v)<=data.digital_level);}
function invalidate(){revision++;publish({source:"UNAVAILABLE",reason:"DRAFT_CHANGED"});result.textContent="Draft changed · calculate again";}
function dirty(){if(!running)invalidate();else revision++;}
for(const id of ["freq","level","duration"])get(id).addEventListener("change",dirty);
get("fader").addEventListener("input",dirty);
for(const knob of document.querySelectorAll("[data-knob]")){
 knob.addEventListener("pointerup",dirty);knob.addEventListener("keydown",e=>{if(["ArrowUp","ArrowDown","ArrowLeft","ArrowRight","Home","End"].includes(e.key))dirty();});
}
get("reset").addEventListener("click",dirty);
get("em").addEventListener("click",()=>{invalidate();sync();});
get("acoustic").addEventListener("click",sync);
get("language").addEventListener("change",sync);
run.addEventListener("click",async()=>{
 if(running||channel!=="acoustic")return;
 const cmd={frequency_hz:values.freq,level_percent:values.level,duration_ms:values.duration};
 if(cmd.level_percent===0){result.textContent="Digital level must be greater than zero";return;}
 const my=++revision;running=true;sync();publish({source:"UNAVAILABLE",reason:"CALCULATING"});
 result.textContent=words()[1];
 try{
  const response=await fetch("/api/digital",{method:"POST",headers:{"Content-Type":"application/json","X-FIK-Token":secret},body:JSON.stringify(cmd),cache:"no-store",credentials:"omit"});
  const data=await response.json();
  if(my!==revision||channel!=="acoustic"||values.freq!==cmd.frequency_hz||values.level!==cmd.level_percent||values.duration!==cmd.duration_ms){
   result.textContent="Draft changed · calculate again";return;
  }
  if(!response.ok||!valid(data,cmd)){result.textContent=String(data.reason||"NATIVE_RESULT_REJECTED");return;}
  publish(data);
  result.textContent=data.command_hz+" Hz · "+cmd.level_percent+"% digital · "+data.count+" samples · "+data.rate_hz+" Hz sample rate · session closed";
 }catch(_){result.textContent="Local runtime unavailable";}
 finally{running=false;sync();}
});
sync();result.textContent=words()[3];
})();
