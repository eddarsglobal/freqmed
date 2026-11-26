/* SPDX-License-Identifier: Apache-2.0 */
(()=>{
"use strict";
const $=id=>document.getElementById(id);
const rows={
en:"Qualification & performance|FFT requests|FFT calculations|FFT reused|FFT computation · ms|Result copies · ms|Frame interval p95 · ms|JS heap · MiB|Viewport · CSS px|Refresh metrics|Measure frame intervals|Consolidated checks|Counters cover shared full-window FFT calls, not all CPU/GPU work. Frame intervals are browser observations, not GPU utilization. No physical output.|Instruments|Spectral intelligence|Comparison & archive",
fr:"Qualification et performances|Requêtes FFT|Calculs FFT|FFT réutilisées|Calcul FFT · ms|Copies des résultats · ms|Intervalle d’image p95 · ms|Tas JS · Mio|Zone visible · px CSS|Actualiser|Mesurer les intervalles d’image|Contrôles consolidés|Compteurs des FFT mutualisées sur fenêtres complètes, pas de toute la charge CPU/GPU. Intervalles observés dans le navigateur, pas d’utilisation GPU. Aucune sortie physique.|Instruments|Intelligence spectrale|Comparaison et archive",
de:"Qualifikation und Leistung|FFT-Anfragen|FFT-Berechnungen|FFT wiederverwendet|FFT-Berechnung · ms|Ergebniskopien · ms|Bildintervall p95 · ms|JS-Heap · MiB|Ansichtsbereich · CSS-px|Aktualisieren|Bildintervalle messen|Gesamtprüfungen|Zähler für gemeinsam genutzte FFT vollständiger Fenster, nicht für die gesamte CPU/GPU-Last. Browserintervalle, keine GPU-Auslastung. Keine physische Ausgabe.|Instrumente|Spektralanalyse|Vergleich und Archiv",
ar:"التأهيل والأداء|طلبات FFT|حسابات FFT|إعادة استخدام FFT|حساب FFT · ms|نسخ النتائج · ms|فاصل الإطارات p95 · ms|ذاكرة JS · MiB|مساحة العرض · CSS px|تحديث المقاييس|قياس فواصل الإطارات|فحوص موحدة|عدادات FFT المشتركة للنوافذ الكاملة وليست كامل حمل المعالج. فواصل المتصفح ليست قياس استخدام GPU. لا خرج فيزيائي.|الأدوات|التحليل الطيفي|المقارنة والأرشيف",
es:"Cualificación y rendimiento|Solicitudes FFT|Cálculos FFT|FFT reutilizadas|Cálculo FFT · ms|Copias de resultados · ms|Intervalo de fotograma p95 · ms|Memoria JS · MiB|Vista · px CSS|Actualizar métricas|Medir intervalos de fotogramas|Controles consolidados|Contadores FFT compartidos de ventanas completas, no de toda la carga CPU/GPU. Intervalos del navegador, no utilización GPU. Sin salida física.|Instrumentos|Inteligencia espectral|Comparación y archivo",
pt:"Qualificação e desempenho|Pedidos FFT|Cálculos FFT|FFT reutilizadas|Cálculo FFT · ms|Cópias dos resultados · ms|Intervalo de fotograma p95 · ms|Memória JS · MiB|Vista · px CSS|Atualizar métricas|Medir intervalos de fotogramas|Verificações consolidadas|Contadores FFT partilhados de janelas completas, não de toda a carga CPU/GPU. Intervalos do navegador, não utilização GPU. Sem saída física.|Instrumentos|Inteligência espectral|Comparação e arquivo",
hr:"Kvalifikacija i izvedba|FFT zahtjevi|FFT izračuni|Ponovno korištene FFT|FFT izračun · ms|Kopije rezultata · ms|Interval okvira p95 · ms|JS memorija · MiB|Prikaz · CSS px|Osvježi metrike|Izmjeri intervale okvira|Objedinjene provjere|Brojači zajedničkih FFT cijelih prozora, ne ukupnog CPU/GPU opterećenja. Intervali preglednika nisu iskorištenost GPU-a. Nema fizičkog izlaza.|Instrumenti|Spektralna analiza|Usporedba i arhiva",
it:"Qualificazione e prestazioni|Richieste FFT|Calcoli FFT|FFT riutilizzate|Calcolo FFT · ms|Copie dei risultati · ms|Intervallo fotogrammi p95 · ms|Memoria JS · MiB|Vista · px CSS|Aggiorna metriche|Misura intervalli fotogrammi|Controlli consolidati|Contatori FFT condivisi di finestre complete, non dell’intero carico CPU/GPU. Intervalli del browser, non utilizzo GPU. Nessuna uscita fisica.|Strumenti|Intelligenza spettrale|Confronto e archivio",
zh:"资格验证与性能|FFT 请求|FFT 计算|FFT 复用|FFT 计算 · ms|结果复制 · ms|帧间隔 p95 · ms|JS 堆 · MiB|视口 · CSS px|刷新指标|测量帧间隔|综合检查|完整窗口共享 FFT 计数，不代表全部 CPU/GPU 负载。浏览器帧间隔不代表 GPU 利用率。无物理输出。|仪器|频谱分析|比较与归档",
ko:"검증 및 성능|FFT 요청|FFT 계산|FFT 재사용|FFT 계산 · ms|결과 복사 · ms|프레임 간격 p95 · ms|JS 힙 · MiB|뷰포트 · CSS px|지표 새로고침|프레임 간격 측정|통합 검사|전체 창 공유 FFT 카운터이며 전체 CPU/GPU 부하가 아닙니다. 브라우저 프레임 간격은 GPU 사용률이 아닙니다. 물리 출력 없음.|계측기|스펙트럼 분석|비교 및 보관"
};
function translate(){
 const a=(rows[document.documentElement.lang]||rows.en).split("|");
 for(const e of document.querySelectorAll("[data-perf]"))e.textContent=a[Number(e.dataset.perf)];
 const nav=document.querySelectorAll("[data-workspace-view]");nav.forEach((e,i)=>e.textContent=a[13+i]);
}
function metrics(){
 const m=FIKPerf.report();
 for(const [k,v] of Object.entries({calls:m.calls,misses:m.misses,hits:m.hits,ms:m.computeMs.toFixed(3),copy:m.copyMs.toFixed(3)}))$("perf-"+k).textContent=String(v);
 $("perf-heap").textContent=Number.isFinite(performance.memory?.usedJSHeapSize)?(performance.memory.usedJSHeapSize/1048576).toFixed(2):"—";
 $("perf-viewport").textContent=innerWidth+" × "+innerHeight;
}
$("perf-refresh").onclick=metrics;
let measuring=false;
$("perf-frames").onclick=()=>{
 if(measuring||document.hidden)return;
 measuring=true;$("perf-frames").disabled=true;const intervals=[];let prev=null;
 const done=()=>{measuring=false;$("perf-frames").disabled=false;};
 const start=performance.now();
 function tick(t){
  if(document.hidden||performance.now()-start>10000){$("perf-frame").textContent="—";done();return;}
  if(prev!==null)intervals.push(t-prev);prev=t;
  if(intervals.length<60){requestAnimationFrame(tick);return;}
  intervals.sort((a,b)=>a-b);$("perf-frame").textContent=intervals[Math.ceil(intervals.length*.95)-1].toFixed(2);
  console.log("FIK_UI010_FRAME_REPORT="+JSON.stringify({intervals:60,p95_ms:intervals[56],max_ms:intervals[59],visible:true,scope:"BROWSER_FRAME_INTERVAL_NOT_GPU_UTILIZATION"}));done();
 }
 requestAnimationFrame(tick);
};
$("perf-check").onclick=()=>{
 const checks={};
 for(const [name,api] of Object.entries({science:FIKScience,dashboard:FIKDashboardMath,precision:FIKPrecision,spectral:FIKSpectral,compare:FIKCompare,cache:FIKPerf})){
  try{for(const [k,v] of Object.entries(api.tests()))checks[name+"."+k]=v===true;}
  catch(e){checks[name+".exception"]=false;}
 }
 checks.locale_rows=Object.keys(rows).length===10&&Object.values(rows).every(s=>s.split("|").length===16);
 checks.physical_disabled=document.querySelector(".start").disabled&&document.querySelector(".stop").disabled;
 checks.unique_views=["science-suite","spectral-suite","compare-suite"].filter(n=>!$(n).hidden).length===1;
 checks.counter_consistency=FIKPerf.report().calls===FIKPerf.report().hits+FIKPerf.report().misses;
 checks.stop_exists=!!$("digital-stop");checks.unique_ids=new Set([...document.querySelectorAll("[id]")].map(e=>e.id)).size===document.querySelectorAll("[id]").length;
 const n=Object.values(checks).filter(Boolean).length,total=Object.keys(checks).length;
 $("perf-result").textContent=n+"/"+total+" "+(n===total?"PASS":"FAIL");
 console.log("FIK_UI010_CONSOLIDATED_REPORT="+JSON.stringify({checks,passed:n,total,physical_output:"NONE",scope:"ALGEBRA_AND_DOM_NOT_FULL_INTERACTION"}));metrics();
};
$("language").addEventListener("change",translate);window.addEventListener("resize",metrics);
$("performance-panel").addEventListener("toggle",()=>{if($("performance-panel").open)metrics();});
window.addEventListener("fik-runtime-record",()=>{if($("performance-panel").open)metrics();});
translate();metrics();
})();
