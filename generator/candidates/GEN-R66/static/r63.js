/* SPDX-License-Identifier: Apache-2.0 */
'use strict';
/* No device or sound output. R63 returns only counts; PCM is erased in C. */
(()=>{
 const $=id=>document.getElementById(id);
 const labels={
 fr:['Préparation PCM numérique · sans émission','Prépare temporairement un bloc numérique dans le moteur C, puis efface la mémoire. Aucune émission.','Préparer le flux numérique','Aucun flux numérique préparé.','Bloc numérique préparé et effacé','Préparation refusée','· enveloppe numérique vérifiée'],
 en:['Digital PCM preparation · no playback','Prepare a temporary digital block in C, then erase memory. No emission.','Prepare digital frame block','No digital block prepared.','Digital block prepared and erased','Preparation refused','· digital envelope verified'],
 de:['Digitale PCM-Vorbereitung · keine Ausgabe','Digitalen Block in C vorbereiten und Speicher löschen. Keine Ausgabe.','Digitalen Block vorbereiten','Kein Digitalblock vorbereitet.','Digitalblock erstellt und gelöscht','Vorbereitung verweigert','· digitale Hüllkurve geprüft'],
 ar:['تحضير PCM رقمي · دون تشغيل','تحضير كتلة رقمية مؤقتة في C ومسحها من الذاكرة. دون بث.','تحضير الكتلة الرقمية','لم يتم تحضير كتلة رقمية.','تم تحضير الكتلة الرقمية ومسحها','تم رفض التحضير','· تم التحقق من الغلاف الرقمي'],
 es:['Preparación PCM digital · sin reproducción','Prepara un bloque digital temporal en C y borra la memoria. Sin emisión.','Preparar bloque digital','Ningún bloque preparado.','Bloque digital preparado y borrado','Preparación rechazada','· envolvente digital verificada'],
 pt:['Preparação PCM digital · sem reprodução','Prepara um bloco digital temporário em C e apaga a memória. Sem emissão.','Preparar bloco digital','Nenhum bloco preparado.','Bloco digital preparado e apagado','Preparação recusada','· envelope digital verificado'],
 hr:['Digitalna PCM priprema · bez reprodukcije','Privremeni digitalni blok u C-u, zatim brisanje memorije. Bez emitiranja.','Pripremi digitalni blok','Nema pripremljenog bloka.','Digitalni blok pripremljen i izbrisan','Priprema odbijena','· digitalna ovojnica potvrđena'],
 it:['Preparazione PCM digitale · senza riproduzione','Prepara un blocco digitale temporaneo in C, poi cancella la memoria. Nessuna emissione.','Prepara blocco digitale','Nessun blocco preparato.','Blocco digitale preparato e cancellato','Preparazione rifiutata','· inviluppo digitale verificato'],
 zh:['数字 PCM 准备 · 无播放','在 C 中暂存数字块，之后清除内存。没有声音输出。','准备数字块','尚未准备数字块。','数字块已准备并清除','准备被拒绝','· 数字包络已验证'],
 ko:['디지털 PCM 준비 · 재생 없음','C에서 디지털 블록을 일시 생성한 후 메모리에서 지웁니다. 소리 출력 없음.','디지털 블록 준비','준비된 블록 없음.','디지털 블록 생성 후 삭제됨','준비 거부','· 디지털 엔벌로프 검증됨']
 };
 const t=i=>(labels[$('lang')?.value]||labels.fr)[i];
 function relabel(){ $('r63-title').textContent=t(0);$('r63-description').textContent=t(1);$('r63-prepare').textContent=t(2);if($('r63-result').dataset.done!=='yes')$('r63-result').textContent=t(3);}
 function reset(){ $('r63-result').dataset.done='no';$('r63-result').textContent=t(3); }
 async function prepare(){
  const button=$('r63-prepare');button.disabled=true;
  try{
    const tok=await fetch('/api/session',{cache:'no-store'});if(!tok.ok)throw Error('SESSION_UNAVAILABLE');
    const token=(await tok.json()).session;
    const res=await fetch('/api/acoustic/pcm/prepare',{method:'POST',cache:'no-store',headers:{'Content-Type':'application/json','X-FREQMED-SESSION':token},body:'{}'});
    const out=await res.json();if(!res.ok)throw Error(out.error||'HTTP_'+res.status);
    if(!out.prepared||!out.transient_pcm_zeroized||out.digital_envelope_verified!==true||out.digital_zero_edges!==true||out.digital_integrity_r64!=='PASS_NUMERIC_ONLY_NO_PLAYBACK'||out.playback!=='NOT_PERFORMED')throw Error('RESULT_NOT_SAFE');
    $('r63-result').dataset.done='yes';$('r63-result').textContent=t(4)+': '+out.digital_frames+' frames · '+out.channels+' ch · '+out.digital_samples+' samples '+t(6)+' · PHYSICAL OUTPUT: HARD_DENIED';
  }catch(e){$('r63-result').dataset.done='no';$('r63-result').textContent=t(5)+': '+String(e.message)}
  finally{button.disabled=false;}
 }
 $('r63-prepare').addEventListener('click',prepare);
 ['hz','level','duration','r54-clear','r54-bind','r55-software-stop','reset'].forEach(id=>$(id)?.addEventListener('input',reset));
 ['r54-clear','r54-bind','r55-software-stop','reset'].forEach(id=>$(id)?.addEventListener('click',reset));
 $('lang').addEventListener('change',relabel);relabel();
})();
