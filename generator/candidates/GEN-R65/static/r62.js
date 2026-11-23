/* GEN-R62: UID is never returned; only OS identity equality state. No output. */
'use strict';
(()=>{
const $=id=>document.getElementById(id);
const t={
 fr:['Identité CoreAudio réelle','IDENTITÉ OS CONFIRMÉE · SANS ÉMISSION','NON LIÉE','IDENTITÉ INVALIDÉE','ARRÊTÉE','LECTURE OS INDISPONIBLE'],
 en:['Real CoreAudio identity','OS IDENTITY CONFIRMED · NO OUTPUT','UNBOUND','IDENTITY INVALIDATED','STOPPED','OS READ UNAVAILABLE'],
 de:['Echte CoreAudio-Identität','OS-IDENTITÄT BESTÄTIGT · KEINE AUSGABE','NICHT VERKNÜPFT','IDENTITÄT UNGÜLTIG','GESTOPPT','OS-ABFRAGE NICHT VERFÜGBAR'],
 ar:['هوية CoreAudio الحقيقية','تم تأكيد هوية النظام · دون إصدار','غير مرتبطة','الهوية غير صالحة','متوقفة','قراءة النظام غير متاحة'],
 es:['Identidad CoreAudio real','IDENTIDAD DEL SISTEMA CONFIRMADA · SIN EMISIÓN','NO VINCULADA','IDENTIDAD INVALIDADA','DETENIDA','LECTURA DEL SISTEMA NO DISPONIBLE'],
 pt:['Identidade CoreAudio real','IDENTIDADE DO SISTEMA CONFIRMADA · SEM EMISSÃO','NÃO VINCULADA','IDENTIDADE INVALIDADA','PARADA','LEITURA DO SISTEMA INDISPONÍVEL'],
 hr:['Stvarni CoreAudio identitet','IDENTITET SUSTAVA POTVRĐEN · BEZ EMISIJE','NEPOVEZANO','IDENTITET PONIŠTEN','ZAUSTAVLJENO','OS OČITAVANJE NEDOSTUPNO'],
 it:['Identità CoreAudio reale','IDENTITÀ DEL SISTEMA CONFERMATA · SENZA EMISSIONE','NON COLLEGATA','IDENTITÀ INVALIDATA','ARRESTATA','LETTURA DEL SISTEMA NON DISPONIBILE'],
 zh:['真实 CoreAudio 标识','系统标识已确认 · 无输出','未绑定','标识已失效','已停止','系统读取不可用'],
 ko:['실제 CoreAudio 식별','OS 식별 확인 · 출력 없음','연결되지 않음','식별 무효화','중지됨','OS 읽기 불가']};
let data=null,epoch=0;
const L=()=>t[$('lang')?.value]||t.fr;
function draw(){const box=$('r62-identity-panel');if(!box)return;const labels=L();
$('r62-identity-label').textContent=labels[0];
const st=data?.state||'UNBOUND',pinned=st==='PINNED_NO_EMISSION'&&data?.identity_confirmed_now===true;
box.dataset.pinned=String(pinned);box.dataset.fault=String(st==='INVALIDATED');
$('r62-identity-status').textContent=pinned?labels[1]:st==='STOPPED'?labels[4]:st==='INVALIDATED'?labels[3]:data?.unavailable?labels[5]:labels[2];
$('r62-identity-status').title=data?.reason||'';
}
async function poll(){const request=++epoch;try{const resp=await fetch('/api/acoustic/identity/status',{cache:'no-store'});
if(!resp.ok)throw Error('IDENTITY_STATUS_UNAVAILABLE');const obj=await resp.json();if(request!==epoch)return;data=obj;
}catch(_){if(request===epoch)data={unavailable:true,state:'UNBOUND'};}draw();}
document.addEventListener('DOMContentLoaded',()=>{draw();poll();$('lang')?.addEventListener('change',draw);window.setInterval(poll,1700);});
})();
