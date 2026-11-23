/* SPDX-License-Identifier: Apache-2.0 */
'use strict';
// R57: actual native C check against CURRENT macOS default audio route.
// Source-only backend, no AudioQueue, no PCM, no physical output.
(()=>{
 const $=id=>document.getElementById(id);
 const strings={
 fr:['Compatibilité avec le backend acoustique','Le backend candidat historique utilise la sortie audio par défaut du Mac. Vérification native de la route sélectionnée, sans émission.','Vérifier la compatibilité du backend C','Aucune vérification du backend effectuée.','Route compatible avec le backend candidat (source uniquement). AUCUNE ÉMISSION.','Route refusée : ','Aucune émission : backend non lié, protections physiques non certifiées.'],
 en:['Acoustic backend route contract','The historical candidate targets the Mac default output. Native route check, no emission.','Check native backend route','No backend check performed.','Route matches source-only backend. NO OUTPUT.','Route rejected: ','No emission: backend unlinked, hardware safeguards not qualified.'],
 de:['Akustisches Backend prüfen','Historischer Backend-Kandidat verwendet Standardausgabe. Ohne Ausgabe.','Backend-Route prüfen','Keine Prüfung','Route kompatibel, KEINE AUSGABE.','Abgelehnt: ','Backend nicht verbunden.'],
 ar:['التحقق من مسار المحرك الصوتي','المحرك المرشح يستعمل المخرج الافتراضي للماك، دون إصدار صوت.','تحقق من المسار','لا تحقق بعد','المسار متوافق دون تشغيل.','مرفوض: ','الإخراج غير متاح.'],
 es:['Ruta del motor acústico','El motor candidato usa la salida predeterminada. Sin emisión.','Verificar ruta','Sin verificar','Ruta compatible, SIN EMISIÓN.','Rechazado: ','Motor no conectado.'],
 pt:['Rota do motor acústico','O candidato usa a saída padrão do Mac. Sem emissão.','Verificar rota','Sem verificação','Rota compatível, SEM EMISSÃO.','Recusado: ','Motor não ligado.'],
 hr:['Akustički izlaz','Kandidat koristi zadani izlaz Maca. Bez emitiranja.','Provjeri izlaz','Nije provjereno','Izlaz odgovara; NEMA EMISIJE.','Odbijeno: ','Izlaz nije povezan.'],
 it:['Percorso acustico','Il candidato usa l’uscita predefinita del Mac. Nessun suono.','Verifica percorso','Nessuna verifica','Percorso compatibile, NESSUNA EMISSIONE.','Rifiutato: ','Backend non collegato.'],
 zh:['声学后端路径','候选后端使用 Mac 默认输出，不发声。','验证输出','未验证','路径匹配，但禁止输出。','拒绝: ','后端未连接。'],
 ko:['음향 백엔드 경로','후보 엔진은 Mac 기본 출력을 사용합니다. 소리 없음.','출력 확인','확인 전','경로 일치, 출력 차단.','거부: ','백엔드 연결 안 됨.']
 };
 let last=''; const t=i=>(strings[$('lang')?.value]||strings.fr)[i];
 function labels(){
   $('r57-title').textContent=t(0);$('r57-hint').textContent=t(1);
   $('r57-button-label').textContent=t(2);$('r57-foot').textContent=t(6);
   if(last!==$('lang').value){invalidate();last=$('lang').value;}
 }
 function invalidate(){ $('r57-result').dataset.ok='false';$('r57-result').textContent=t(3);}
 async function run(){
  const btn=$('r57-inspect');btn.disabled=true;
  try{
   const channel=document.querySelector('input[name="channel"]:checked')?.value;
   const hz=$('hz').valueAsNumber,level=$('level').valueAsNumber,duration=$('duration').valueAsNumber;
   if(channel!=='acoustic')throw Error('ONLY_ACOUSTIC_CHANNEL_SUPPORTED');
   if(!Number.isFinite(hz)||!Number.isFinite(level)||!Number.isSafeInteger(duration))throw Error('INVALID_INPUT');
   const sess=await fetch('/api/session',{cache:'no-store'});if(!sess.ok)throw Error('SESSION_UNAVAILABLE');
   const token=(await sess.json()).session;
   const res=await fetch('/api/acoustic/backend/inspect',{method:'POST',cache:'no-store',
      headers:{'Content-Type':'application/json','X-FREQMED-SESSION':token},
      body:JSON.stringify({channel,hz,level,duration_ms:duration})});
   const val=await res.json();if(!res.ok)throw Error(val.error||'HTTP_'+res.status);
   $('r57-result').dataset.ok=val.route_contract_valid?'true':'false';
   $('r57-result').textContent=(val.route_contract_valid?t(4):t(5)+val.result)+'\n'+
      'DEFAULT ROUTE MATCH: '+val.default_route_matches+'\n'+
      'DIGITAL FRAMES: '+(val.digital_frame_budget??'N/A')+'\n'+
      'BACKEND LINKED: '+val.backend_linked+'\nPHYSICAL OUTPUT: '+val.physical_output;
  }catch(err){$('r57-result').dataset.ok='false';$('r57-result').textContent=t(5)+err.message;}
  finally{btn.disabled=false;}
 }
 $('r57-inspect').addEventListener('click',run);
 ['r55-software-stop','r54-clear','r54-bind','reset','validate','r56-prepare'].forEach(id=>{
    const btn=$(id);if(btn)btn.addEventListener('click',invalidate);
 });
 document.querySelectorAll('#hz,#level,#duration,input[name="channel"]').forEach(el=>el.addEventListener('input',invalidate));
 async function checkStale(){
   if($('r57-result').dataset.ok!=='true')return;
   try{const r=await fetch('/api/acoustic/backend/status',{cache:'no-store'});if(!r.ok)return;
       const s=await r.json();if(!s.checked)invalidate();}catch(_){}
 }
 window.setInterval(checkStale,1700);
 $('lang').addEventListener('change',labels);labels();
})();
