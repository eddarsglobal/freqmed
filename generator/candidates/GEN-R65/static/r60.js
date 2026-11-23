/* SPDX-License-Identifier: Apache-2.0 */
'use strict';
/* Real native C lease status only: does not generate, arm or emit sound. */
(()=>{
 const $=id=>document.getElementById(id);
 const tr={
  fr:['Contrôle logiciel temporel','NON LIÉ','VÉRIFIÉ · SANS ÉMISSION','EXPIRÉ','ARRÊTÉ','RÉVOQUÉ'],
  en:['Time-limited native control','UNBOUND','VERIFIED · NO EMISSION','EXPIRED','STOPPED','REVOKED'],
  de:['Zeitlich begrenzte native Steuerung','NICHT VERBUNDEN','GEPRÜFT · KEINE AUSGABE','ABGELAUFEN','GESTOPPT','WIDERRUFEN'],
  ar:['تحكم أصلي محدود الوقت','غير مرتبط','تم التحقق · دون إصدار','منتهي الصلاحية','متوقف','ملغى'],
  es:['Control nativo temporal','SIN ASOCIAR','VERIFICADO · SIN EMISIÓN','CADUCADO','DETENIDO','REVOCADO'],
  pt:['Controlo nativo temporário','SEM LIGAÇÃO','VERIFICADO · SEM EMISSÃO','EXPIRADO','PARADO','REVOGADO'],
  hr:['Vremenski ograničena izvorna kontrola','NIJE POVEZANO','PROVJERENO · BEZ EMISIJE','ISTEKLO','ZAUSTAVLJENO','OPOZVANO'],
  it:['Controllo nativo temporaneo','NON ASSOCIATO','VERIFICATO · SENZA EMISSIONE','SCADUTO','FERMATO','REVOCATO'],
  zh:['限时原生控制','未绑定','已核验 · 无输出','已过期','已停止','已撤销'],
  ko:['시간 제한 네이티브 제어','연결 안 됨','검증됨 · 출력 없음','만료','중지됨','취소됨']};
 const L=()=>tr[$('lang')?.value]||tr.fr;
 let latest=null;
 let generation=0;
 function render(){
  if(!$('r60-control-label'))return;
  $('r60-control-label').textContent=L()[0];
  const st=latest?.state||'UNBOUND';
  const idx=st==='CONTROL_LEASE_VALID_NO_EMISSION'?2:st==='EXPIRED'?3:st==='STOPPED'?4:st==='REVOKED'?5:1;
  $('r60-control-status').textContent=L()[idx];
  $('r60-control-status').title=latest?.reason||'';
  $('r60-control-status').parentElement.dataset.valid=String(!!latest?.valid_control_lease);
 }
 async function refresh(){
  const turn=++generation;
  try{
   const r=await fetch('/api/acoustic/control/status',{cache:'no-store'});
   if(!r.ok)throw Error('CONTROL_STATUS_UNAVAILABLE');
   const x=await r.json();if(turn!==generation)return;
   latest=x;
  }catch(_){if(turn===generation)latest={state:'REVOKED',reason:'STATUS_UNAVAILABLE',valid_control_lease:false};}
  render();
 }
 document.addEventListener('DOMContentLoaded',()=>{
  render();refresh();
  $('lang')?.addEventListener('change',render);
  window.setInterval(refresh,1500);
 });
})();
