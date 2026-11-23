/* SPDX-License-Identifier: Apache-2.0 */
'use strict';
// Actual OS monitor results only. No visualization or fabricated device data.
(() => {
 const tr={
 fr:['Surveillance réelle de la route audio','Contrôle périodique de la sortie choisie par CoreAudio. Aucun signal émis.','Arrêter la surveillance et libérer la route','Ce bouton arrête uniquement la surveillance logicielle et libère la route. Aucun générateur physique ne peut démarrer dans cette version.','Contrôle OS','Aucune sélection active','Aucune sortie sélectionnée','Métadonnées sélectionnées conformes à la lecture OS','Sortie invalidée ou déconnectée','Inventaire macOS indisponible','Lecture OS disponible, aucune sortie choisie','Arrêt logiciel exécuté, route effacée','Échec du contrôle matériel'],
 en:['Live audio route monitoring','Periodic CoreAudio checks of the selected real device. No output.','Stop monitoring and clear the route','This button stops software monitoring and clears the route only. Physical output cannot start in this build.','OS check','No active selection','No output selected','Selected metadata matches live OS','Route invalidated or disconnected','macOS registry unavailable','Real OS read available; no output selected','Software stop complete, route cleared','Hardware check failed'],
 de:['Echte Audio-Routenüberwachung','Regelmäßige CoreAudio-Abfrage ohne Emission.','Überwachung stoppen und Route freigeben','Dieser Knopf stoppt nur die Softwareüberwachung und gibt die Route frei. Keine physische Ausgabe verfügbar.','OS-Prüfung','Keine Auswahl','Keine Ausgabe gewählt','Echte OS-Daten stimmen überein','Route ungültig oder getrennt','CoreAudio nicht verfügbar','OS-Daten verfügbar; keine Route','Software gestoppt','Abfrage fehlgeschlagen'],
 ar:['مراقبة مسار الصوت الحقيقي','فحص دوري لأجهزة CoreAudio دون إصدار صوت.','إيقاف المراقبة وإلغاء ارتباط المخرج','هذا الزر يوقف مراقبة البرنامج ويزيل ربط المخرج فقط. الإخراج الفيزيائي غير متاح.','فحص النظام','لا يوجد تحديد','لم يتم اختيار مخرج','بيانات الجهاز تطابق النظام','المسار منقطع أو غير صالح','تعذر قراءة النظام','تمت القراءة دون اختيار','تم إيقاف البرنامج','فشل فحص العتاد'],
 es:['Vigilancia real de la ruta de audio','Verificación periódica con CoreAudio sin emisión.','Detener vigilancia y liberar la ruta','Solo detiene la vigilancia software y libera la ruta. No existe salida física activa.','Consulta OS','Sin selección','Ninguna salida elegida','Metadatos coinciden con el OS','Ruta inválida o desconectada','OS no disponible','OS leído sin selección','Software detenido','Consulta fallida'],
 pt:['Monitoramento real da rota de áudio','Verificação periódica CoreAudio sem emissão.','Parar monitoramento e liberar rota','O botão para somente o monitoramento e libera a rota. Nenhuma saída física pode iniciar.','Verificação OS','Sem seleção','Nenhuma saída escolhida','Dados de dispositivo correspondem','Rota inválida ou desconectada','OS indisponível','OS lido sem seleção','Software parado','Falha de leitura'],
 hr:['Stvarni nadzor audio izlaza','Povremena CoreAudio provjera bez emitiranja.','Zaustavi nadzor i oslobodi izlaz','Ovaj gumb zaustavlja samo programski nadzor i oslobađa rutu. Nema fizičkog izlaza.','OS provjera','Nema odabira','Nema izlaza','Podaci uređaja odgovaraju','Izlaz nije dostupan','OS nije dostupan','OS očitan bez odabira','Softver zaustavljen','Provjera neuspjela'],
 it:['Monitoraggio reale uscita audio','Lettura periodica CoreAudio senza emissioni.','Ferma monitoraggio e libera uscita','Arresta soltanto il monitoraggio software e libera la rotta. Nessuna uscita fisica disponibile.','Controllo OS','Nessuna selezione','Nessuna uscita','Metadati OS corrispondenti','Uscita non valida o disconnessa','OS non disponibile','OS letto senza selezione','Software fermato','Controllo fallito'],
 zh:['真实音频路由监控','定期查询 CoreAudio，无声音输出。','停止监控并清除路由','此按钮仅停止软件监控并清除路由。该版本无法启动物理输出。','系统检查','无选择','未选择输出','设备元数据与系统一致','路由失效或断开','系统无法读取','已读取系统但未选择','软件已停止','系统检查失败'],
 ko:['실제 오디오 경로 감시','CoreAudio 주기 조회, 신호 출력 없음.','감시 중지 및 경로 해제','이 버튼은 소프트웨어 감시를 중지하고 경로만 해제합니다. 물리적 출력은 실행할 수 없습니다.','OS 확인','선택 없음','선택된 출력 없음','실제 OS 정보와 일치','경로 해제 또는 변경','OS 사용 불가','OS 확인됨, 선택 없음','소프트웨어 중지됨','하드웨어 확인 실패']
 };
 // FIX1: operator STOP controls the native observer, not only the C state.
 const add={
  fr:['Surveillance arrêtée — compteur figé','Reprendre la surveillance OS','Arrêt demandé — lecture CoreAudio en cours'],
  en:['Monitoring stopped — counter frozen','Resume OS monitoring','Stopping — CoreAudio read in progress'],
  de:['Überwachung gestoppt — Zähler angehalten','OS-Überwachung fortsetzen','Stopp läuft — CoreAudio-Abfrage'],
  ar:['تم إيقاف المراقبة — العداد ثابت','استئناف مراقبة النظام','جارٍ الإيقاف — قراءة CoreAudio'],
  es:['Vigilancia detenida — contador fijo','Reanudar vigilancia del sistema','Deteniendo — consulta CoreAudio'],
  pt:['Monitoramento parado — contador fixo','Retomar monitoramento OS','Parando — consulta CoreAudio'],
  hr:['Praćenje zaustavljeno — brojilo miruje','Nastavi OS praćenje','Zaustavljanje — CoreAudio upit'],
  it:['Monitoraggio fermato — contatore fisso','Riprendi monitoraggio OS','Arresto — lettura CoreAudio'],
  zh:['监控已停止 — 计数器不再增加','恢复系统监控','正在停止 — CoreAudio 读取中'],
  ko:['감시 중지 — 카운터 고정','OS 감시 재개','중지 중 — CoreAudio 조회']
 };
 const eventTranslations={
  fr:['Surveillance arrêtée · route libérée','Surveillance OS reprise'],
  en:['Monitoring stopped · route cleared','OS monitoring resumed'],
  de:['Überwachung gestoppt · Route freigegeben','OS-Überwachung fortgesetzt'],
  ar:['المراقبة متوقفة · تم إلغاء ارتباط المخرج','استؤنفت مراقبة النظام'],
  es:['Vigilancia detenida · ruta liberada','Vigilancia del sistema reanudada'],
  pt:['Monitoramento parado · rota liberada','Monitoramento OS retomado'],
  hr:['Nadzor zaustavljen · izlaz oslobođen','OS praćenje nastavljeno'],
  it:['Monitoraggio fermo · uscita liberata','Monitoraggio OS ripreso'],
  zh:['监控已停止 · 路由已清除','系统监控已恢复'],
  ko:['감시 중지 · 경로 해제','OS 감시 재개됨']
 };
 const idleText={
  fr:['EN ATTENTE','En attente de la sélection d’une sortie audio','Aucune opération — sortie non sélectionnée'],
  en:['IDLE','Waiting for an audio output selection','No action — output not selected'],
  de:['BEREIT','Warten auf die Auswahl eines Audioausgangs','Keine Aktion — kein Ausgang ausgewählt'],
  ar:['في الانتظار','بانتظار تحديد مخرج الصوت','لا يوجد إجراء — لم يتم تحديد مخرج'],
  es:['EN ESPERA','Esperando la selección de una salida de audio','Sin acción — salida no seleccionada'],
  pt:['EM ESPERA','Aguardando a seleção de uma saída de áudio','Nenhuma ação — saída não selecionada'],
  hr:['NA ČEKANJU','Čeka se odabir audio izlaza','Nema radnje — izlaz nije odabran'],
  it:['IN ATTESA','In attesa di selezionare un’uscita audio','Nessuna azione — uscita non selezionata'],
  zh:['待选择','等待选择音频输出','无操作 — 未选择输出'],
  ko:['대기 중','오디오 출력을 선택하기 전입니다','동작 없음 — 선택된 출력 없음']
 };
 const nothingRunning={
  fr:'Aucune surveillance active. Aucun générateur acoustique ou EM n’a démarré.',
  en:'No monitoring active. No acoustic or EM generator has started.',
  de:'Keine Überwachung aktiv. Kein akustischer oder EM-Generator wurde gestartet.',
  ar:'لا توجد مراقبة نشطة. لم يبدأ أي مولد صوتي أو كهرومغناطيسي.',
  es:'Sin vigilancia activa. No se ha iniciado ningún generador acústico o EM.',
  pt:'Sem monitoramento ativo. Nenhum gerador acústico ou EM foi iniciado.',
  hr:'Nadzor nije aktivan. Nijedan akustični ni EM generator nije pokrenut.',
  it:'Nessun monitoraggio attivo. Nessun generatore acustico o EM è stato avviato.',
  zh:'监控未启动。声学或电磁发生器均未启动。',
  ko:'감시가 실행 중이지 않습니다. 음향 또는 EM 발생기가 시작되지 않았습니다.'
 };
 for(const key of Object.keys(tr))tr[key].push(...add[key],...eventTranslations[key]);
 const el=(id)=>document.getElementById(id);
 const t=(i)=>(tr[el('lang')?.value]||tr.fr)[i];
 function labels(){['r55-title','r55-description','r55-stop-label','r55-stop-disclaimer'].forEach((id,i)=>{el(id).textContent=t(i)});
  el('r55-resume-label').textContent=t(14);
 }
 async function query(){
  const r=await fetch('/api/route/monitor',{cache:'no-store'});
  if(!r.ok)throw Error('HTTP_'+r.status);
  return await r.json();
 }
 async function display(){
  try {
   const value=await query();
   el('r55-checks').textContent=t(4)+': '+value.checks;
   el('r55-event').textContent=value.event==='NO_SELECTION' ? (idleText[el('lang')?.value]||idleText.fr)[2]:value.event==='OPERATOR_SOFTWARE_STOP_MONITOR_STOPPED'?t(16):value.event==='OPERATOR_MONITOR_RESUMED'?t(17):value.event;
   const monitoring=value.monitor_state==='RUNNING';
   // STOP is an operation on an active *software* observer, not a generator
   // stop. Hide it altogether at boot (IDLE), after STOP or without a route.
   const hasActiveObserver=monitoring&&value.selected===true;
   el('r55-software-stop').hidden=!hasActiveObserver;
   el('r55-stop-disclaimer').hidden=!hasActiveObserver;
   el('r55-software-stop').disabled=!hasActiveObserver;
   el('r55-idle-note').hidden=value.monitor_state!=='IDLE';
   el('r55-idle-note').textContent=(nothingRunning[el('lang')?.value]||nothingRunning.fr);
   // Resume is an action only after an explicit STOP, never at initial IDLE.
   el('r55-resume-monitor').hidden=value.monitor_state!=='STOPPED';
   const idle=value.monitor_state==='IDLE';
   el('r55-live-chip').textContent=idle?(idleText[el('lang')?.value]||idleText.fr)[0]:monitoring?'OS LIVE':value.monitor_state;
   const present=value.last_os_poll==='COREAUDIO_OBSERVED';
   const valid=monitoring&&value.selected&&value.event==='SELECTED_ROUTE_METADATA_MATCHES_OS';
   el('r55-watch-status').dataset.verified=valid?'yes':'no';
   el('r55-watch-status').textContent=idle?(idleText[el('lang')?.value]||idleText.fr)[1]:!monitoring?(value.monitor_state==='STOPPING'?t(15):t(13)):
    valid?t(7):value.event.startsWith('ROUTE_INVALIDATED')?t(8):
    !present?t(9):present?t(10):t(6);
  } catch (error) {
   el('r55-watch-status').dataset.verified='no';
   el('r55-watch-status').textContent=t(12)+': '+error.message;
  }
 }
 async function stop(){
  const btn=el('r55-software-stop');btn.disabled=true;
  try {
   const s=await fetch('/api/session',{cache:'no-store'});if(!s.ok)throw Error('SESSION_UNAVAILABLE');
   const token=(await s.json()).session;
   const r=await fetch('/api/software-stop',{method:'POST',cache:'no-store',headers:{'Content-Type':'application/json','X-FREQMED-SESSION':token},body:'{}'});
   const data=await r.json();if(!r.ok)throw Error(data.error||'STOP_REFUSED');
   if(data.software_stop!=='EXECUTED_NATIVE_FM_STOP'||data.monitor_running!==false)throw Error('STOP_NOT_CONFIRMED');
   el('r55-watch-status').dataset.verified='no';
   el('r55-watch-status').textContent=t(11);
   // The existing route widget must also stop advertising a selected route.
   window.dispatchEvent(new Event('freqmed:route-cleared'));
   await display();
  }catch(e){el('r55-watch-status').textContent=t(12)+': '+e.message;}
  finally{await display();}
 }
 async function resume(){
  const btn=el('r55-resume-monitor');btn.disabled=true;
  try{
   const s=await fetch('/api/session',{cache:'no-store'});if(!s.ok)throw Error('SESSION_UNAVAILABLE');
   const token=(await s.json()).session;
   const r=await fetch('/api/route/monitor/resume',{method:'POST',cache:'no-store',headers:{'Content-Type':'application/json','X-FREQMED-SESSION':token},body:'{}'});
   const data=await r.json();if(!r.ok)throw Error(data.error||'RESUME_REFUSED');
   if(!['RUNNING','IDLE'].includes(data.monitor_state))throw Error('MONITOR_NOT_READY');
   await display();
  }catch(e){el('r55-watch-status').textContent=t(12)+': '+e.message;}
  finally{await display();}
 }
 el('r55-software-stop').addEventListener('click',stop);
 el('r55-resume-monitor').addEventListener('click',resume);
 el('lang').addEventListener('change',labels);
 labels();display();
 const poll=()=>{if(document.visibilityState==='visible')display();};
 window.setInterval(poll,1800);
 document.addEventListener('visibilitychange',poll);
})();
