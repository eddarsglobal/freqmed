/* SPDX-License-Identifier: Apache-2.0 */
'use strict';
/* Native fault-latch observation and explicit authenticated acknowledgement only. */
(()=>{
 const $=id=>document.getElementById(id);
 const langs={
  fr:['Défauts natifs','NORMAL · SANS ÉMISSION','DÉFAUT VERROUILLÉ','ARRÊTÉ','Acquitter le défaut'],
  en:['Native faults','NORMAL · NO EMISSION','FAULT LATCHED','STOPPED','Acknowledge fault'],
  de:['Native Fehler','NORMAL · KEINE AUSGABE','FEHLER VERRIEGELT','GESTOPPT','Fehler quittieren'],
  ar:['الأعطال الأصلية','طبيعي · دون إصدار','عطل مقفل','متوقف','الإقرار بالعطل'],
  es:['Fallos nativos','NORMAL · SIN EMISIÓN','FALLO BLOQUEADO','DETENIDO','Reconocer fallo'],
  pt:['Falhas nativas','NORMAL · SEM EMISSÃO','FALHA BLOQUEADA','PARADO','Reconhecer falha'],
  hr:['Izvorne greške','NORMALNO · BEZ EMISIJE','GREŠKA ZAKLJUČANA','ZAUSTAVLJENO','Potvrdi grešku'],
  it:['Guasti nativi','NORMALE · SENZA EMISSIONE','GUASTO BLOCCATO','FERMATO','Conferma guasto'],
  zh:['原生故障','正常 · 无输出','故障锁定','已停止','确认故障'],
  ko:['네이티브 오류','정상 · 출력 없음','오류 잠김','중지됨','오류 확인']};
 let latest=null,epoch=0;
 const L=()=>langs[$('lang')?.value]||langs.fr;
 function render(){const p=$('r61-fault-panel');if(!p)return;
  $('r61-fault-label').textContent=L()[0];$('r61-fault-ack').textContent=L()[4];
  const f=latest?.state==='FAULT_LATCHED',s=latest?.state==='STOPPED';
  p.dataset.fault=String(f);$('r61-fault-status').textContent=L()[f?2:s?3:1];
  $('r61-fault-status').title=latest?.reason||'';
  $('r61-fault-ack').hidden=!f;
 }
 async function poll(){let e=++epoch;
  try{const r=await fetch('/api/acoustic/fault/status',{cache:'no-store'});
   if(!r.ok)throw Error('R61_FAULT_STATUS_UNAVAILABLE');const obj=await r.json();if(e!==epoch)return;latest=obj;
  }catch(_){if(e===epoch)latest={state:'FAULT_LATCHED',reason:'STATUS_UNAVAILABLE'};}
  render();
 }
 async function ack(){const btn=$('r61-fault-ack');btn.disabled=true;
  try{const s=await fetch('/api/session',{cache:'no-store'});if(!s.ok)throw Error('SESSION_UNAVAILABLE');
   const token=(await s.json()).session;
   const r=await fetch('/api/acoustic/fault/ack',{method:'POST',cache:'no-store',headers:{'Content-Type':'application/json','X-FREQMED-SESSION':token},body:'{}'});
   const obj=await r.json();if(!r.ok)throw Error(obj.error||'R61_ACK_REFUSED');latest=obj;
  }catch(e){$('r61-fault-status').title=String(e.message);}
  finally{btn.disabled=false;render();poll();}
 }
 document.addEventListener('DOMContentLoaded',()=>{render();poll();$('lang')?.addEventListener('change',render);
  $('r61-fault-ack')?.addEventListener('click',ack);window.setInterval(poll,1700);});
})();
