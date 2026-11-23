/* SPDX-License-Identifier: Apache-2.0 */
'use strict';
// R56 uses real native C + OS CoreAudio metadata; never starts physical output.
(() => {
  const $ = id => document.getElementById(id);
  const phrases = {
    fr:['Préparation native d’une commande acoustique','Choisis une sortie CoreAudio réelle à droite, puis contrôle les paramètres avec le moteur C. Aucun tampon audio généré.','Vérifier la route et la commande C','Aucune préparation effectuée.','Une commande numérique compatible ne prouve ni émission physique ni sécurité acoustique. Démarrage verrouillé.','Sélectionner une sortie CoreAudio réelle avant la préparation.','Commande numérique compatible avec la sortie OS. Aucune émission autorisée.','Préparation refusée : ','Fréquence numérique','Trames numériques prévues','Aucune trame produite'],
    en:['Native acoustic command preparation','Select a real CoreAudio output, then check the command using native C. No audio buffers generated.','Check route and command using C','No preparation performed.','A compatible digital command does not prove physical output or acoustic safety. Start remains locked.','Select a real CoreAudio output first.','Digital command compatible with OS route. No output authorized.','Preparation refused: ','Digital frequency','Planned digital frames','No frames generated'],
    de:['Native Akustik-Vorbereitung','Echte CoreAudio-Ausgabe wählen, dann C-Befehl prüfen. Kein Audiosignal.','Route und C-Befehl prüfen','Keine Vorbereitung','Digitalprüfung bedeutet keine Emissionsfreigabe.','CoreAudio-Ausgabe auswählen','Digitalprüfung bestanden; Ausgabe gesperrt','Abgelehnt: ','Frequenz','Digitale Frames','Keine Frames erzeugt'],
    ar:['التحضير الصوتي الأصلي','اختر جهاز CoreAudio حقيقيًا للتحقق من الأمر دون إنتاج صوت.','فحص المسار والأمر بلغة C','لا يوجد تحضير','التوافق الرقمي لا يسمح بالإرسال.','اختر مخرجًا حقيقيًا','الأمر الرقمي متوافق دون السماح بالإرسال','رفض التحضير: ','التردد','إطارات رقمية','لم تنتج إطارات'],
    es:['Preparación acústica nativa','Elige una salida CoreAudio real; comprobación C sin emisión.','Verificar ruta y comando C','Sin preparación','La compatibilidad digital no autoriza salida.','Seleccionar salida real','Contrato digital compatible; salida bloqueada','Rechazado: ','Frecuencia','Tramas digitales','No se generaron'],
    pt:['Preparação acústica nativa','Escolha uma saída CoreAudio real; sem emitir sinal.','Verificar rota e comando C','Sem preparação','Compatibilidade digital não autoriza emissão.','Selecione saída real','Comando digital compatível; emissão bloqueada','Recusado: ','Frequência','Quadros digitais','Não gerados'],
    hr:['Izvorna akustična priprema','Odaberite stvarni CoreAudio izlaz; bez emitiranja.','Provjeri izlaz i C naredbu','Nema pripreme','Digitalna kompatibilnost nije odobrenje emisije.','Odaberite stvarni izlaz','Digitalna naredba odgovara; izlaz blokiran','Odbijeno: ','Frekvencija','Digitalni okviri','Nisu proizvedeni'],
    it:['Preparazione acustica nativa','Selezionare una reale uscita CoreAudio; nessuna emissione.','Verifica rotta e comando C','Nessuna preparazione','Compatibilità digitale non autorizza emissione.','Selezionare uscita reale','Comando digitale compatibile; uscita bloccata','Rifiutato: ','Frequenza','Frame digitali','Non generati'],
    zh:['原生声学命令准备','选择真实 CoreAudio 输出并用 C 验证，无音频输出。','验证设备和命令','尚未准备','数字兼容不等于允许发声。','选择真实输出设备','数字参数兼容；输出锁定','拒绝: ','频率','数字帧','未生成'],
    ko:['네이티브 음향 명령 준비','실제 CoreAudio 출력을 선택하고 C로 확인합니다. 출력 없음.','출력 및 명령 확인','준비되지 않음','디지털 호환성이 물리적 출력 허가는 아닙니다.','실제 출력 선택','디지털 명령 확인됨; 출력 잠김','거부: ','주파수','디지털 프레임','생성되지 않음']
  };
  let lastLanguage = '';
  const t=i=>(phrases[$('lang')?.value]||phrases.fr)[i];
  function labels(){
    $('r56-title').textContent=t(0);$('r56-hint').textContent=t(1);
    $('r56-button-label').textContent=t(2);$('r56-disclaimer').textContent=t(4);
    if(lastLanguage!==$('lang').value){ $('r56-result').textContent=t(3); lastLanguage=$('lang').value; }
  }
  async function run(){
    const button=$('r56-prepare');button.disabled=true;
    try {
      const channel=document.querySelector('input[name="channel"]:checked')?.value;
      const hz=$('hz').valueAsNumber, level=$('level').valueAsNumber, duration=$('duration').valueAsNumber;
      if(channel!=='acoustic') throw Error('ONLY_ACOUSTIC_CHANNEL_SUPPORTED');
      if(!Number.isFinite(hz)||!Number.isFinite(level)||!Number.isSafeInteger(duration))throw Error('INVALID_INPUT');
      const session=await fetch('/api/session',{cache:'no-store'});if(!session.ok)throw Error('SESSION_UNAVAILABLE');
      const token=(await session.json()).session;
      const res=await fetch('/api/acoustic/preflight',{method:'POST',cache:'no-store',
        headers:{'Content-Type':'application/json','X-FREQMED-SESSION':token},
        body:JSON.stringify({channel,hz,level,duration_ms:duration})});
      const value=await res.json();if(!res.ok)throw Error(value.error||'HTTP_'+res.status);
      $('r56-result').dataset.ok=value.digital_contract_valid?'true':'false';
      $('r56-result').textContent=(value.digital_contract_valid?t(6):t(7)+value.result)+'\n'+
        t(8)+': '+hz+' Hz'+(value.os_nominal_sample_rate_hz!==null?' / OS '+value.os_nominal_sample_rate_hz+' Hz':'')+'\n'+
        (value.digital_frame_budget===null?t(10):t(9)+': '+value.digital_frame_budget)+'\n'+
        'PHYSICAL OUTPUT: '+value.physical_output;
    }catch(err){$('r56-result').dataset.ok='false';$('r56-result').textContent=t(7)+err.message;}
    finally{button.disabled=false;}
  }
  $('r56-prepare').addEventListener('click',run);
  // As soon as the operator stops, clears or replaces a route, never leave
  // a green result from an earlier command visible in this tab.
  ['r55-software-stop','r54-clear','r54-bind','reset','validate'].forEach(id=>{
    const target=$(id);if(target)target.addEventListener('click',()=>{
      $('r56-result').dataset.ok='false';$('r56-result').textContent=t(3);
    });
  });
  // Detect asynchronous CoreAudio route invalidation by asking the server,
  // never from a pretend local device list.
  async function invalidateOnServerChange(){
    if($('r56-result').dataset.ok!=='true')return;
    try{
      const response=await fetch('/api/acoustic/preflight/status',{cache:'no-store'});
      if(!response.ok)return;
      const state=await response.json();
      if(!state.checked || !state.digital_contract_valid){
        $('r56-result').dataset.ok='false';$('r56-result').textContent=t(3);
      }
    }catch(_ignored){}
  }
  window.setInterval(invalidateOnServerChange,1800);
  $('lang').addEventListener('change',labels);
  document.querySelectorAll('#hz,#level,#duration,input[name="channel"]').forEach(e=>e.addEventListener('input',()=>{$('r56-result').dataset.ok='false';$('r56-result').textContent=t(3);}));
  labels();
})();
