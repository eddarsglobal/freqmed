/* SPDX-License-Identifier: Apache-2.0 */
'use strict';
(()=>{
 const $=id=>document.getElementById(id);
 const t={
  fr:['Liaison isolée du backend acoustique','Code historique compilé dans une bibliothèque distincte. Seul un diagnostic est accessible : aucune fonction de lecture audio ne peut être appelée par cette interface.','Contrôler la liaison native isolée','Aucune vérification du binaire candidat.','Source compilée ≠ moteur activé. Aucun pilote EM, aucune mesure, aucune coupure physique certifiée.'],
  en:['Isolated acoustic backend link','Historical CoreAudio source compiled in a separate native library. Only read-only evidence is reachable.','Inspect isolated native link','Candidate binary not inspected.','Compiled source is not active playback. No EM driver, measurement or certified physical interlock.'],
  de:['Isolierte akustische Backend-Bindung','Historischer CoreAudio-Quellcode isoliert kompiliert. Keine Audioausgabe.','Native Bindung prüfen','Nicht geprüft.','Kein Ton oder physischer Sicherheitsschalter.'],
  ar:['ربط محرك الصوت المعزول','تم تجميع المصدر الأصلي في مكتبة مستقلة دون تشغيل الصوت.','فحص الربط','لم يتم الفحص.','لا تشغيل ولا قياس فعلي.'],
  es:['Enlace acústico aislado','Código CoreAudio original compilado de forma aislada, sin reproducción.','Inspeccionar enlace','Sin comprobar.','Sin sonido ni medidas.'],
  pt:['Ligação acústica isolada','Código CoreAudio original isolado, sem reprodução.','Verificar ligação','Não verificado.','Sem som nem medições.'],
  hr:['Izolirani akustički sustav','Izvorni CoreAudio kod zasebno preveden, bez reprodukcije.','Provjeri povezivanje','Nije provjereno.','Bez zvuka ili mjerenja.'],
  it:['Collegamento audio isolato','Codice CoreAudio isolato, senza riproduzione.','Verifica collegamento','Non verificato.','Nessuna emissione o misura.'],
  zh:['隔离的声学后端','原始 CoreAudio 源码独立编译，不可播放。','检查本地链接','尚未检查。','无声音或测量。'],
  ko:['격리된 음향 엔진','원본 CoreAudio 코드를 분리 빌드하며 재생은 불가합니다.','연결 검사','미검사.','소리 및 측정 없음.']};
 const str=i=>(t[$('lang')?.value]||t.fr)[i];
 function refreshLabels(){ $('r58-title').textContent=str(0);$('r58-hint').textContent=str(1);$('r58-label').textContent=str(2);$('r58-note').textContent=str(4); }
 async function inspect(){
   const btn=$('r58-check');btn.disabled=true;
   try{
     const r=await fetch('/api/acoustic/candidate/status',{cache:'no-store'});if(!r.ok)throw Error('HTTP_'+r.status);
     const s=await r.json();$('r58-result').dataset.linked=String(s.candidate_source_linked_isolated);
     $('r58-result').textContent='ISOLATED CANDIDATE SOURCE LINKED: '+s.candidate_source_linked_isolated+'\n'+
      'PINNED GIT BLOBS: '+s.source_git_blobs_verified+'\n'+
      'ORIGINAL CORE AUDIO C COMPILED: '+s.original_acoustic_backend_compiled+'\n'+
      'EMITTER ENTRYPOINT DENIED: '+s.hard_denial_verified_in_candidate+'\n'+
      'EMISSION SYMBOLS EXPORTED: '+s.emission_entrypoints_exported+'\n'+
      'PLAYBACK: '+s.playback+'\nPHYSICAL OUTPUT: '+s.main_application_physical_output+'\n'+
      (s.error==='NONE'?'':('ERROR: '+s.error));
   }catch(e){$('r58-result').dataset.linked='false';$('r58-result').textContent=String(e.message);}
   finally{btn.disabled=false;}
 }
 $('r58-check').addEventListener('click',inspect);
 $('lang').addEventListener('change',refreshLabels);refreshLabels();
})();
