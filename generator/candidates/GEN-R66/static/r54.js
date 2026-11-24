/* SPDX-License-Identifier: Apache-2.0 */
'use strict';
/* Live OS observation and temporary route bind. No signal or waveform APIs. */
(() => {
 const id=(key)=>document.getElementById(key);
 const dict={
  fr:['Sorties audio réelles macOS','Périphériques lus via CoreAudio natif. Aucun signal émis.','Choisir une sortie audio','Actualiser CoreAudio','Sélectionner le périphérique','Effacer','Aucune sortie sélectionnée','Identifiants temporaires du système · sélection sans émission · pas de calibrage ni qualification matérielle.','Aucun périphérique disponible','Lecture CoreAudio indisponible','Périphérique sélectionné (route observée)','Sélection invalidée : périphérique changé ou déconnecté','Choisir une sortie avant validation','Impossible de sélectionner',"— Choisir une sortie audio —","À confirmer : {device}. Cliquez sur « Sélectionner le périphérique ». Aucune route n’est encore associée.","À confirmer : {device}. Route actuellement associée : {active}.","Aucune route associée. Choisissez un périphérique ci-dessus, puis confirmez."],
  en:['Real macOS audio outputs','Devices read via native CoreAudio. No signal emitted.','Choose an audio output','Refresh CoreAudio','Select physical device','Clear selection','No output selected','Temporary OS IDs · selection without emission · no calibration or qualification.','No devices available','CoreAudio read unavailable','Device selected (observed route)','Route invalid: device changed or disconnected','Choose a device first','Unable to select',"— Choose an audio output —","Pending confirmation: {device}. Click “Select physical device”. No route is bound yet.","Pending confirmation: {device}. Currently bound route: {active}.","No route bound. Choose a device above, then confirm."],
  de:['Echte macOS-Audioausgänge','Geräte über CoreAudio gelesen. Keine Ausgabe.','Audioausgang auswählen','CoreAudio aktualisieren','Gerät auswählen','Auswahl löschen','Kein Ausgang ausgewählt','Temporäre OS-IDs · keine Ausgabe · keine Kalibrierung.','Keine Geräte','CoreAudio nicht verfügbar','Gerät ausgewählt','Gerät geändert oder getrennt','Zuerst Gerät auswählen','Auswahl fehlgeschlagen',"— Audioausgang wählen —","Bestätigung ausstehend: {device}. Bitte „Gerät auswählen“ drücken. Noch keine Route verbunden.","Bestätigung ausstehend: {device}. Aktuelle Route: {active}.","Keine Route verbunden. Gerät wählen und bestätigen."],
  ar:['مخارج صوت macOS الفعلية','قراءة أجهزة CoreAudio الأصلية دون إصدار صوت.','اختر مخرج الصوت','تحديث CoreAudio','اختيار الجهاز','مسح','لم يتم اختيار مخرج','معرفات مؤقتة للنظام · دون إصدار · دون معايرة.','لا توجد أجهزة','CoreAudio غير متاح','تم اختيار الجهاز','الجهاز تغير أو انقطع','اختر جهازًا أولًا','فشل الاختيار',"— اختر مخرج الصوت —","بانتظار التأكيد: {device}. اضغط «اختيار الجهاز». لا يوجد مسار مرتبط بعد.","بانتظار التأكيد: {device}. المسار المرتبط حاليًا: {active}.","لا يوجد مسار مرتبط. اختر جهازًا أعلاه ثم أكّد."],
  es:['Salidas de audio reales de macOS','Dispositivos leídos con CoreAudio. Sin señal emitida.','Elegir salida de audio','Actualizar CoreAudio','Seleccionar dispositivo','Borrar','Sin salida seleccionada','IDs temporales · sin emisión ni calibración.','Sin dispositivos','CoreAudio no disponible','Dispositivo seleccionado','Ruta desconectada o cambiada','Elige un dispositivo','Selección fallida',"— Elegir una salida de audio —","Pendiente de confirmación: {device}. Pulsa «Seleccionar dispositivo». Aún no hay ruta vinculada.","Pendiente de confirmación: {device}. Ruta actual: {active}.","No hay ruta vinculada. Elige y confirma un dispositivo."],
  pt:['Saídas de áudio reais do macOS','Dispositivos lidos via CoreAudio. Sem emissão.','Escolher saída de áudio','Atualizar CoreAudio','Selecionar dispositivo','Limpar','Nenhuma saída selecionada','IDs temporários · sem emissão ou calibração.','Sem dispositivos','CoreAudio indisponível','Dispositivo selecionado','Rota alterada ou desconectada','Escolha um dispositivo','Falha na seleção',"— Escolher saída de áudio —","Aguardando confirmação: {device}. Clique em «Selecionar dispositivo». Ainda sem rota vinculada.","Aguardando confirmação: {device}. Rota atual: {active}.","Nenhuma rota vinculada. Escolha e confirme um dispositivo."],
  hr:['Stvarni macOS audio izlazi','Uređaji očitani putem CoreAudio. Bez emitiranja.','Odaberi audio izlaz','Osvježi CoreAudio','Odaberi uređaj','Poništi','Nema odabranog izlaza','Privremeni OS ID · bez emitiranja i kalibracije.','Nema uređaja','CoreAudio nije dostupan','Uređaj odabran','Veza promijenjena ili prekinuta','Odaberi uređaj','Odabir nije uspio',"— Odaberi audio izlaz —","Čeka potvrdu: {device}. Pritisnite „Odaberi uređaj”. Još nema povezane rute.","Čeka potvrdu: {device}. Trenutna ruta: {active}.","Nema povezane rute. Odaberite i potvrdite uređaj."],
  it:['Uscite audio reali macOS','Dispositivi letti tramite CoreAudio. Nessuna emissione.','Scegli uscita audio','Aggiorna CoreAudio','Seleziona dispositivo','Cancella','Nessuna uscita selezionata','ID OS temporanei · senza emissioni né taratura.','Nessun dispositivo','CoreAudio non disponibile','Dispositivo selezionato','Dispositivo cambiato o disconnesso','Scegli un dispositivo','Selezione non riuscita',"— Scegli uscita audio —","Da confermare: {device}. Premi «Seleziona dispositivo». Nessuna rotta ancora associata.","Da confermare: {device}. Rotta attuale: {active}.","Nessuna rotta associata. Scegli e conferma un dispositivo."],
  zh:['真实 macOS 音频输出','通过原生 CoreAudio 读取设备。不发出信号。','选择音频输出','刷新 CoreAudio','选择设备','清除','未选择输出','临时系统 ID · 不发射 · 未校准。','无设备','CoreAudio 不可用','已选择设备','设备已更改或断开','请先选择设备','选择失败',"— 选择音频输出 —","待确认：{device}。点击“选择设备”。尚未绑定输出路径。","待确认：{device}。当前绑定的输出路径：{active}。","尚未绑定路径。请选择并确认设备。"],
  ko:['실제 macOS 오디오 출력','CoreAudio로 장치를 읽습니다. 신호 출력 없음.','오디오 출력 선택','CoreAudio 새로고침','장치 선택','지우기','선택한 출력 없음','임시 OS ID · 출력 및 교정 없음.','장치 없음','CoreAudio 사용 불가','장치 선택됨','장치 변경 또는 연결 해제','장치를 선택하세요','선택 실패',"— 오디오 출력 선택 —","확인 대기: {device}. “장치 선택”을 누르세요. 아직 연결된 경로가 없습니다.","확인 대기: {device}. 현재 연결된 경로: {active}.","연결된 경로가 없습니다. 장치를 선택하고 확인하세요."]
 };
 const lang=()=>id('lang')?.value||'fr';
 const label=(i)=>((dict[lang()]||dict.en)[i]||dict.en[i]);
 function textLabels(){
  const fields=['r54-route-title','r54-route-caption','r54-route-label','r54-refresh-label','r54-bind-label','r54-clear-label',null,'r54-disclaimer'];
  fields.forEach((v,i)=>{if(v)id(v).textContent=label(i)});
 }
 const select=id('r54-select');
 let confirmed=null;
 let epoch=0;
 const desc=(s)=>`${s.name} · ${s.channels} ch · ${s.nominal_sample_rate_hz} Hz`;
 const fill=(template,device,active)=>template.replace('{device}',device||'').replace('{active}',active||'');
 function state(text,kind){
  const e=id('r54-route-state');e.textContent=text;
  e.dataset.verified=kind==='yes'?'yes':kind==='pending'?'pending':'no';
 }
 function canConfirm(){id('r54-bind').disabled=!/^\d+$/.test(select.value)|| (confirmed!==null&&Number(select.value)===confirmed.device_id);}
 function placeholder(text){
  const o=document.createElement('option');o.value='';o.textContent=text;o.disabled=true;
  select.prepend(o);select.value='';
 }
 function clearDropdown(){
  if(select.querySelector('option[value=""]'))select.value='';
  else placeholder(label(14));
  confirmed=null;canConfirm();
 }
 function selectionState(s){
  if(!s||!s.selected){confirmed=null;state(label(17),'no');return;}
  if(s.verified_now){confirmed=s;state(`${label(10)}: ${desc(s)}`,'yes');}
  else {confirmed=null;state(`${label(11)}: ${s.reason||''}`,'no');}
 }
 function pendingChoice(){
  const val=select.value;
  if(!/^\d+$/.test(val)){
   if(confirmed)selectionState(confirmed);
   else state(label(17),'no');
  }else if(confirmed&&Number(val)===confirmed.device_id){
   selectionState(confirmed);
  }else{
   const proposed=select.selectedOptions[0]?.textContent||val;
   state(confirmed?fill(label(16),proposed,desc(confirmed)):fill(label(15),proposed),'pending');
  }
  canConfirm();
 }
 async function get(path){const r=await fetch(path,{cache:'no-store'});if(!r.ok)throw Error('HTTP_'+r.status);return await r.json()}
 async function post(path,body){const token=await get('/api/session');const r=await fetch(path,{method:'POST',headers:{'Content-Type':'application/json','X-FREQMED-SESSION':token.session},cache:'no-store',body:JSON.stringify(body)});const data=await r.json();if(!r.ok)throw Error(data.error||'HTTP_'+r.status);return data}
 async function refresh(){
  const current=++epoch;const b=id('r54-refresh');b.disabled=true;
  try{
   const r=await get('/api/audio/devices');if(current!==epoch)return;
   select.replaceChildren();
   if(!r.observed||!r.devices.length){
    placeholder(r.observed?label(8):label(9));
    confirmed=null;state(r.observed?label(8):label(9),'no');return;
   }
   placeholder(label(14)); // A detected device must not be mistaken for a confirmed route.
   for(const dev of r.devices){
    const o=document.createElement('option');o.value=String(dev.device_id);
    o.textContent=`${desc(dev)}${dev.is_default?' ★':''}`;select.append(o);
   }
   const route=r.selection;
   if(route?.selected&&route.verified_now&&r.devices.some(d=>d.device_id===route.device_id)){
    confirmed=route;select.value=String(route.device_id);selectionState(route);
   }else{
    selectionState(route); // Retain invalid-route diagnostics; do not auto-pick device #1.
   }
  }catch(e){if(current===epoch){clearDropdown();state(label(9)+': '+e.message,'no');}}
  finally{b.disabled=false;canConfirm();}
 }
 async function choose(){
  const value=select.value;
  if(!/^\d+$/.test(value)){state(label(12),'no');canConfirm();return;}
  const current=++epoch;const b=id('r54-bind');b.disabled=true;
  try{
   const r=await post('/api/audio/select',{device_id:Number(value)});
   if(current!==epoch)return;
   selectionState(r);
   if(r.selected&&r.verified_now){select.value=String(r.device_id);}
   else select.value='';
  }catch(e){if(current===epoch){pendingChoice();state(label(13)+': '+e.message,'no');}}
  finally{canConfirm();}
 }
 async function clear(){
  const current=++epoch;
  try{
   const r=await post('/api/audio/clear',{});
   if(current!==epoch)return;
   clearDropdown();selectionState(r);
  }catch(e){if(current===epoch)state('FAIL_CLOSED: '+e.message,'no');}
 }
 function clearedByStop(){
  ++epoch;clearDropdown();state(label(17),'no');
 }
 id('r54-refresh').addEventListener('click',refresh);
 id('r54-bind').addEventListener('click',choose);
 id('r54-clear').addEventListener('click',clear);
 select.addEventListener('change',pendingChoice);
 window.addEventListener('freqmed:route-cleared',clearedByStop);
 id('lang').addEventListener('change',async()=>{textLabels();await refresh()});
 id('reset').addEventListener('click',()=>{clearedByStop()});
 textLabels();canConfirm();refresh();
})();
