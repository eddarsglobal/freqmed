/* SPDX-License-Identifier: Apache-2.0 */
'use strict';
/* R59: purely read-only / native contract state; no emission or fake hardware. */
(()=>{
const $=id=>document.getElementById(id);
const tr={
fr:['Session acoustique native sans émission','Associer la sortie CoreAudio sélectionnée à la commande exacte dans le moteur C. STOP et changements de route invalident cette session. Aucun signal émis.','Associer route et commande dans le moteur C','Session non liée.','Contrat numérique, aucun AudioQueue et aucun coupe-circuit matériel certifié.'],
en:['Native acoustic route session, no emission','Bind the selected CoreAudio route to the exact command in native C. STOP and route changes invalidate it. No output.','Bind route and command in native C','Session unbound.','Digital contract only; no AudioQueue and no certified hardware cutoff.'],
de:['Native Akustik-Sitzung ohne Ausgabe','Ausgewählte CoreAudio-Route an C-Befehl binden. Stopp löscht die Bindung.','Route und Befehl binden','Nicht verbunden.','Kein AudioQueue oder Hardware-Not-Aus.'],
ar:['جلسة صوتية أصلية دون بث','ربط مسار CoreAudio بالأمر في محرك C. يؤدي الإيقاف إلى إلغاء الربط.','ربط المسار بالأمر','غير مربوط.','لا إخراج صوتي أو قاطع مستقل معتمد.'],
es:['Sesión acústica nativa sin emisión','Asociar la salida CoreAudio al comando C. Detener invalida la sesión.','Asociar ruta y comando','Sin vincular.','Sin audio ni corte físico certificado.'],
pt:['Sessão acústica nativa sem emissão','Ligar a rota CoreAudio ao comando C. Parar invalida a sessão.','Associar rota e comando','Sem ligação.','Sem saída ou corte físico certificado.'],
hr:['Izvorna akustička sesija bez emitiranja','Poveži CoreAudio izlaz s C naredbom; STOP prekida vezu.','Poveži izlaz i naredbu','Nije povezano.','Bez zvuka i sigurnosnog hardverskog prekida.'],
it:['Sessione acustica nativa senza emissione','Associa la rotta CoreAudio al comando C; STOP annulla la sessione.','Associa rotta e comando','Non associata.','Nessuna emissione o interruttore certificato.'],
zh:['无输出的原生声学会话','将 CoreAudio 路由与 C 命令绑定；停止将清除会话。','绑定路由与命令','尚未绑定。','无播放及独立硬件断路。'],
ko:['출력 없는 네이티브 음향 세션','CoreAudio 경로와 C 명령을 연결합니다. 중지하면 연결 해제됩니다.','경로와 명령 연결','연결되지 않음.','출력이나 인증된 물리 차단 없음.']};
const L=i=>(tr[$('lang')?.value]||tr.fr)[i];
function labels(){ $('r59-title').textContent=L(0);$('r59-hint').textContent=L(1);$('r59-label').textContent=L(2);$('r59-note').textContent=L(4);}
function draw(s){$('r59-result').dataset.bound=String(!!s.route_bound);
 $('r59-result').textContent='NATIVE SESSION: '+s.phase+'\nREASON: '+s.reason+'\nROUTE BOUND: '+s.route_bound+'\nCANDIDATE ISOLATED: '+s.candidate_isolated+'\nDIGITAL FRAME BUDGET: '+(s.digital_frame_budget??'N/A')+'\nPHYSICAL OUTPUT: '+s.physical_output+'\nPLAYBACK: '+s.playback;
}
let dirty=false;
let editRequest=Promise.resolve();
function invalidate(){ $('r59-result').dataset.bound='false';$('r59-result').textContent=L(3); dirty=true; }
function reportCommandEdit(){
 invalidate();
 // Serialize edit invalidations; no stale session stays accepted after an edit.
 editRequest=editRequest.catch(()=>{}).then(async()=>{
   const session=await fetch('/api/session',{cache:'no-store'});
   if(!session.ok)throw Error('SESSION_UNAVAILABLE');
   const token=(await session.json()).session;
   const result=await fetch('/api/acoustic/session/invalidate',{
     method:'POST',cache:'no-store',headers:{'Content-Type':'application/json','X-FREQMED-SESSION':token},body:'{}'});
   if(!result.ok)throw Error('R59_INVALIDATION_REQUEST_FAILED');
 });
}
async function check(){const btn=$('r59-bind');btn.disabled=true;
 try{ await editRequest; }catch(_){ $('r59-result').textContent='R59 REFUSED: COMMAND_INVALIDATION_UNCONFIRMED';btn.disabled=false;return; }
 try{
 const channel=document.querySelector('input[name="channel"]:checked')?.value;
 const hz=$('hz').valueAsNumber,level=$('level').valueAsNumber,duration=$('duration').valueAsNumber;
 if(channel!=='acoustic'||!Number.isFinite(hz)||!Number.isFinite(level)||!Number.isSafeInteger(duration))throw Error('R59_INVALID_INPUT');
 const sess=await fetch('/api/session',{cache:'no-store'});if(!sess.ok)throw Error('SESSION_UNAVAILABLE');
 const token=(await sess.json()).session;
 const res=await fetch('/api/acoustic/session/bind',{method:'POST',cache:'no-store',headers:{'Content-Type':'application/json','X-FREQMED-SESSION':token},body:JSON.stringify({channel,hz,level,duration_ms:duration})});
 const ans=await res.json();if(!res.ok)throw Error(ans.error||'HTTP_'+res.status);
 dirty=false;draw(ans);
 }catch(e){$('r59-result').dataset.bound='false';$('r59-result').textContent='R59 REFUSED: '+String(e.message);}
 finally{btn.disabled=false;}
}
$('r59-bind').addEventListener('click',check);
['r55-software-stop','r54-clear','r54-bind','reset','validate','r56-prepare','r57-inspect'].forEach(id=>$(id)?.addEventListener('click',invalidate));
document.querySelectorAll('#hz,#level,#duration,input[name="channel"]').forEach(el=>el.addEventListener('input',reportCommandEdit));
let pending=false;
async function poll(){if(pending)return;pending=true;try{const r=await fetch('/api/acoustic/session/status',{cache:'no-store'});if(!r.ok)return;
 const state=await r.json();if(!dirty)draw(state);
 }catch(_){$('r59-result').dataset.bound='false';$('r59-result').textContent='R59 STATUS UNAVAILABLE';}finally{pending=false;}}
window.setInterval(poll,1800);$('lang').addEventListener('change',()=>{labels();poll();});labels();poll();
})();
