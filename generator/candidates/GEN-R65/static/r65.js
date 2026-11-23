/* SPDX-License-Identifier: Apache-2.0 */
'use strict';
/* 256-frame ephemeral digital command segments; NEVER audio output. */
(()=>{
 const $=id=>document.getElementById(id);
 const labels={
  fr:['Préparer par blocs bornés · R65','Aucun bloc R65 préparé.','Préparation numérique par blocs terminée','Préparation par blocs refusée','blocs de 256 trames maximum · effacés'],
  en:['Prepare bounded segments · R65','No R65 segments prepared.','Segmented digital preparation completed','Segment preparation refused','segments of at most 256 frames · erased'],
  de:['Begrenzte Blöcke vorbereiten · R65','Keine R65-Blöcke vorbereitet.','Digitale Blockvorbereitung abgeschlossen','Blockvorbereitung abgelehnt','Blöcke mit höchstens 256 Frames · gelöscht'],
  ar:['تحضير مقاطع محدودة · R65','لم يتم تحضير مقاطع R65.','اكتمل التحضير الرقمي بالمقاطع','رُفض تحضير المقاطع','مقاطع لا تتجاوز 256 إطارًا · مُسحت'],
  es:['Preparar segmentos limitados · R65','Sin segmentos R65 preparados.','Preparación digital por segmentos completada','Preparación rechazada','segmentos de hasta 256 tramas · borrados'],
  pt:['Preparar segmentos limitados · R65','Nenhum segmento R65 preparado.','Preparação digital segmentada concluída','Preparação segmentada recusada','segmentos até 256 quadros · apagados'],
  hr:['Pripremi ograničene segmente · R65','Nema pripremljenih R65 segmenata.','Segmentirana digitalna priprema dovršena','Priprema segmenata odbijena','segmenti do 256 okvira · obrisani'],
  it:['Prepara segmenti limitati · R65','Nessun segmento R65 preparato.','Preparazione digitale segmentata completata','Preparazione rifiutata','segmenti fino a 256 frame · cancellati'],
  zh:['准备有界分段 · R65','尚未准备 R65 分段。','数字分段准备完成','分段准备被拒绝','每段最多 256 帧 · 已擦除'],
  ko:['제한된 조각 준비 · R65','R65 조각이 준비되지 않았습니다.','디지털 조각 준비 완료','조각 준비 거부됨','조각당 최대 256 프레임 · 삭제됨']
 };
 const t=i=>(labels[$('lang')?.value]||labels.fr)[i];
 const result=$('r65-result'), button=$('r65-prepare');
 function reset(){result.dataset.done='no';result.textContent=t(1);}
 function relabel(){button.textContent=t(0);if(result.dataset.done!=='yes')result.textContent=t(1);}
 async function prepare(){button.disabled=true;
  try{
   const sessionRes=await fetch('/api/session',{cache:'no-store'});
   if(!sessionRes.ok)throw Error('SESSION_UNAVAILABLE');
   const token=(await sessionRes.json()).session;
   const res=await fetch('/api/acoustic/pcm/prepare-segmented',{
      method:'POST',cache:'no-store',headers:{'Content-Type':'application/json','X-FREQMED-SESSION':token},body:'{}'});
   const out=await res.json();if(!res.ok)throw Error(out.error||'HTTP_'+res.status);
   if(out.prepared!==true||out.all_segments_zeroized!==true||
      out.stream_integrity_r65!=='CONTIGUOUS_BOUNDED_NUMERIC_NO_PLAYBACK'||
      out.peak_pcm_buffer_samples>512||out.segment_frames_max!==256||
      out.playback!=='NOT_PERFORMED'||out.physical_output!=='HARD_DENIED')throw Error('UNSAFE_RESULT');
   result.dataset.done='yes';
   result.textContent=t(2)+': '+out.digital_frames+' frames · '+out.channels+' ch · '+
     out.segment_count+' '+t(4)+' · PHYSICAL OUTPUT: HARD_DENIED';
  }catch(err){result.dataset.done='no';result.textContent=t(3)+': '+String(err.message)}
  finally{button.disabled=false;}
 }
 button.addEventListener('click',prepare);
 for(const id of ['hz','level','duration','r54-clear','r54-bind','r55-software-stop','reset']){
   $(id)?.addEventListener('input',reset);
   $(id)?.addEventListener('click',reset);
 }
 $('lang').addEventListener('change',relabel);relabel();
})();
