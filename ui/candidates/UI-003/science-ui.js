/* SPDX-License-Identifier: Apache-2.0 */
(()=>{
"use strict";
const $=id=>document.getElementById(id), source=JSON.parse($("fik-source").textContent);
const good=source.source==="FREQMED_NATIVE_C_MEMORY_ONLY"&&source.physical_output===false&&source.physical_measurement===false&&
 source.count===4096&&source.samples?.length===4096&&FIKScience.valid(source.samples,source.rate_hz)&&source.samples.every(v=>Math.abs(v)<=.25);
const x=good?source.samples:null,rate=good?source.rate_hz:0;
const spec=good?FIKScience.spectrum(x,rate):null,st=good?FIKScience.spectrogram(x,rate):null,stats=good?FIKScience.stats(x,rate):null;
const times=good?x.map((_,i)=>i*1000/rate):[];
const labels="title notice time fft stft phase samples duration peak inspect band cursor frequency reset empty check".split(" ");
const dict={
en:"Scientific monitors|Digital command snapshot only — not a physical measurement. Independent of the draft controls.|Waveform|FFT spectrum|Spectrogram|Spectral phase|Samples|Duration|Peak bin|Inspector|Frequency range|Cursor|Frequency bin|Reset view|Digital snapshot unavailable|Scientific checks",
fr:"Moniteurs scientifiques|Bloc de commande numérique uniquement — aucune mesure physique. Indépendant des réglages de brouillon.|Signal temporel|Spectre FFT|Spectrogramme|Phase spectrale|Échantillons|Durée|Bin dominant|Inspecteur|Plage fréquentielle|Curseur|Bin fréquentiel|Réinitialiser la vue|Bloc numérique indisponible|Contrôles scientifiques",
de:"Wissenschaftliche Monitore|Nur digitaler Befehlsblock — keine physische Messung. Unabhängig vom Entwurf.|Wellenform|FFT-Spektrum|Spektrogramm|Spektralphase|Abtastwerte|Dauer|Spitzenbin|Inspektor|Frequenzbereich|Cursor|Frequenzbin|Ansicht zurücksetzen|Digitaler Block nicht verfügbar|Wissenschaftliche Prüfungen",
ar:"المراقبات العلمية|كتلة أوامر رقمية فقط — ليست قياسًا فيزيائيًا. مستقلة عن المسودة.|شكل الموجة|طيف FFT|المخطط الطيفي|الطور الطيفي|العينات|المدة|حاوية الذروة|المفتش|نطاق التردد|المؤشر|حاوية التردد|إعادة ضبط العرض|الكتلة الرقمية غير متاحة|الفحوص العلمية",
es:"Monitores científicos|Bloque de comando digital — no es una medición física. Independiente del borrador.|Forma de onda|Espectro FFT|Espectrograma|Fase espectral|Muestras|Duración|Bin dominante|Inspector|Rango de frecuencias|Cursor|Bin de frecuencia|Restablecer vista|Bloque digital no disponible|Controles científicos",
pt:"Monitores científicos|Bloco de comando digital — não é uma medição física. Independente do rascunho.|Forma de onda|Espetro FFT|Espetrograma|Fase espetral|Amostras|Duração|Bin dominante|Inspetor|Intervalo de frequência|Cursor|Bin de frequência|Repor vista|Bloco digital indisponível|Controlos científicos",
hr:"Znanstveni monitori|Samo blok digitalne naredbe — nije fizičko mjerenje. Neovisan o nacrtu.|Valni oblik|FFT spektar|Spektrogram|Spektralna faza|Uzorci|Trajanje|Vršni bin|Inspektor|Frekvencijski raspon|Pokazivač|Frekvencijski bin|Vrati prikaz|Digitalni blok nije dostupan|Znanstvene provjere",
it:"Monitor scientifici|Solo blocco di comando digitale — non è una misura fisica. Indipendente dalla bozza.|Forma d’onda|Spettro FFT|Spettrogramma|Fase spettrale|Campioni|Durata|Bin dominante|Ispettore|Intervallo di frequenza|Cursore|Bin di frequenza|Ripristina vista|Blocco digitale non disponibile|Controlli scientifici",
zh:"科学监视器|仅数字指令数据块，并非物理测量。独立于草稿设置。|波形|FFT 频谱|时频谱|频谱相位|采样数|时长|峰值频点|检查器|频率范围|光标|频点|重置视图|数字数据块不可用|科学检查",
ko:"과학 모니터|디지털 명령 블록 전용 — 물리 측정 아님. 초안 설정과 독립적입니다.|파형|FFT 스펙트럼|스펙트로그램|스펙트럼 위상|샘플|지속 시간|최대 빈|검사기|주파수 범위|커서|주파수 빈|보기 초기화|디지털 블록 없음|과학 검사"
};
let mode="time",plot=null,scheduled=0,stBin=0,stFrame=0;
const css=k=>getComputedStyle(document.documentElement).getPropertyValue(k).trim();
const fmt=(v,d=2)=>v==null?"—":Number(v).toFixed(d);
function translate(){
 const row=(dict[document.documentElement.lang]||dict.en).split("|");
 for(const el of document.querySelectorAll("[data-sc]"))el.textContent=row[labels.indexOf(el.dataset.sc)];
}
function upper(){return Math.min(rate/2,$("sc-band").value==="full"?rate/2:Number($("sc-band").value));}
function binMax(spacing){return Math.max(0,Math.floor(upper()/spacing));}
function cursor(max,value){const el=$("sc-cursor");el.max=String(max);el.value=String(Math.min(max,Math.max(0,value)));}
function setMetrics(){
 $("science-source").textContent=good?"C11 · PLATFORM-09 · "+rate+" Hz · SNAPSHOT":"UNAVAILABLE";
 $("sc-count").textContent=good?String(x.length):"—";
 $("sc-duration").textContent=good?fmt(stats.ms,3)+" ms":"—";
 $("sc-rms").textContent=good?fmt(stats.rms,5):"—";
 $("sc-peak").textContent=good&&spec.peak!==null?fmt(spec.hz[spec.peak],2)+" Hz":"—";
 $("sc-quality").textContent=good?"Hann · FFT "+x.length+" · Δf "+fmt(spec.binHz,3)+" Hz · digital, not SPL":"No source; no trace";
}
function readout(){
 if(!good)return;
 let i=Number($("sc-cursor").value),message="";
 if(mode==="time")message="n = "+i+"\nt = "+fmt(times[i],4)+" ms\nx[n] = "+fmt(x[i],7);
 if(mode==="fft")message="k = "+i+"\nf = "+fmt(spec.hz[i],3)+" Hz\nAmplitude = "+fmt(spec.amp[i],7)+"\n"+fmt(spec.db[i],2)+" dBFS (peak ref.)";
 if(mode==="stft"){stFrame=i;stBin=Number($("sc-second").value);message="t (window center) = "+fmt(st.time[stFrame],3)+" ms\nf = "+fmt(stBin*st.binHz,3)+" Hz\n"+fmt(st.frames[stFrame][stBin],2)+" dBFS (peak ref.)";drawHeat();}
 if(mode==="phase"){message="k = "+i+"\nf = "+fmt(spec.hz[i],3)+" Hz\n∠ = "+(spec.phase[i]===null?"—":fmt(spec.phase[i],2)+"°");drawPhase(i);}
 $("sc-readout").textContent=message;
}
function clearPlot(){if(plot){plot.destroy();plot=null;}$("sc-plot").replaceChildren();}
function chart(){
 clearPlot();const host=$("sc-plot"),width=Math.max(160,host.clientWidth),height=Math.max(180,host.clientHeight);
 const freq=mode==="fft",data=freq?[spec.hz,spec.db]:[times,x];
 plot=new uPlot({width,height,legend:{show:false},cursor:{drag:{x:true,y:false}},scales:{x:{time:false},y:{range:freq?[-120,0]:[-.27,.27]}},
  axes:[{stroke:css("--muted"),grid:{stroke:css("--edge")},ticks:{stroke:css("--edge")},size:42,label:freq?"Hz":"ms"},
   {stroke:css("--muted"),grid:{stroke:css("--edge")},ticks:{stroke:css("--edge")},size:55,label:freq?"dBFS":"digital"}],
  series:[{},{stroke:css("--cyan"),width:1.5,points:{show:false}}],
  hooks:{setCursor:[u=>{if(u.cursor.idx!=null){const el=$("sc-cursor");el.value=String(Math.min(Number(el.max),u.cursor.idx));readout();}}]}},data,host);
 if(freq)plot.setScale("x",{min:0,max:upper()});
}
function palette(db){
 const colors=[[9,19,31],[36,79,157],[125,69,173],[237,123,89],[255,222,135]];
 const v=Math.min(4,Math.max(0,(db+100)/100*4)),i=Math.min(3,Math.floor(v)),f=v-i;
 return "rgb("+colors[i].map((c,j)=>Math.round(c+(colors[i+1][j]-c)*f)).join(",")+")";
}
function canvasSize(c){const scale=Math.min(2,devicePixelRatio||1),w=Math.max(1,Math.min(2048,Math.round(c.clientWidth*scale))),h=Math.max(1,Math.min(1024,Math.round(c.clientHeight*scale)));if(c.width!==w)c.width=w;if(c.height!==h)c.height=h;return [w,h,scale];}
function drawHeat(){
 const c=$("sc-heatmap"),[w,h,scale]=canvasSize(c),ctx=c.getContext("2d");if(!ctx)return false;
 const bins=binMax(st.binHz)+1,n=st.frames.length;
 for(let t=0;t<n;t++)for(let k=0;k<bins;k++){
  const l=Math.floor(t*w/n),r=Math.ceil((t+1)*w/n),top=Math.floor((bins-1-k)*h/bins),bottom=Math.ceil((bins-k)*h/bins);
  ctx.fillStyle=palette(st.frames[t][k]);ctx.fillRect(l,top,r-l,bottom-top);
 }
 const cx=(stFrame+.5)*w/n,cy=(bins-stBin-.5)*h/bins;
 ctx.strokeStyle="#ffffff";ctx.lineWidth=scale;ctx.beginPath();ctx.moveTo(cx,0);ctx.lineTo(cx,h);ctx.moveTo(0,cy);ctx.lineTo(w,cy);ctx.stroke();
 return true;
}
function drawPhase(k){
 const c=$("sc-phase-canvas"),[w,h,scale]=canvasSize(c),ctx=c.getContext("2d");if(!ctx)return false;
 ctx.clearRect(0,0,w,h);const cx=w/2,cy=h/2,r=Math.max(5,Math.min(w,h)*.36);
 ctx.strokeStyle=css("--edge");ctx.lineWidth=scale;
 for(let a=1;a<=3;a++){ctx.beginPath();ctx.arc(cx,cy,r*a/3,0,Math.PI*2);ctx.stroke();}
 ctx.beginPath();ctx.moveTo(cx-r,cy);ctx.lineTo(cx+r,cy);ctx.moveTo(cx,cy-r);ctx.lineTo(cx,cy+r);ctx.stroke();
 ctx.fillStyle=css("--muted");ctx.textAlign="center";ctx.font=11*scale+"px system-ui";
 ctx.fillText("0°",cx+r+14*scale,cy);ctx.fillText("90°",cx,cy-r-7*scale);ctx.fillText("±180°",cx-r-20*scale,cy);ctx.fillText("−90°",cx,cy+r+13*scale);
 const p=spec.phase[k];if(p!==null){const a=p*Math.PI/180;ctx.strokeStyle=css("--cyan");ctx.fillStyle=css("--cyan");ctx.lineWidth=3*scale;
  const dx=cx+r*Math.cos(a),dy=cy-r*Math.sin(a);ctx.beginPath();ctx.moveTo(cx,cy);ctx.lineTo(dx,dy);ctx.stroke();ctx.beginPath();ctx.arc(dx,dy,4*scale,0,Math.PI*2);ctx.fill();
 }
 $("sc-phase-meta").textContent=p===null?"Phase unavailable below amplitude threshold":"Phase of Hann-window FFT coefficient · relative to first sample";
 return true;
}
function render(){
 clearPlot();
 $("sc-plot").hidden=!good||!(mode==="time"||mode==="fft");
 $("sc-heat").hidden=!good||mode!=="stft";$("sc-phase").hidden=!good||mode!=="phase";$("sc-unavailable").hidden=good;
 $("sc-band").disabled=!good||mode==="time";$("sc-cursor").disabled=!good;$("sc-second").disabled=!good;
 $("sc-second").hidden=mode!=="stft";$("sc-second-label").hidden=mode!=="stft";
 for(const b of document.querySelectorAll("[data-sc-mode]"))b.setAttribute("aria-pressed",String(b.dataset.scMode===mode));
 if(!good){$("sc-readout").textContent="—";return;}
 if(mode==="time"){cursor(x.length-1,Number($("sc-cursor").value));$("sc-method").textContent="Normalized digital samples. Drag to zoom; no acoustic units.";chart();}
 if(mode==="fft"||mode==="phase"){cursor(binMax(spec.binHz),Number($("sc-cursor").value));$("sc-method").textContent=mode==="fft"?"Periodic Hann, coherent gain correction. Bin center, not an exact frequency estimate.":"Single coefficient phase, not stereo correlation or physical phase. Below threshold: unavailable.";if(mode==="fft")chart();}
 if(mode==="stft"){cursor(st.frames.length-1,stFrame);$("sc-second").max=String(binMax(st.binHz));$("sc-second").value=String(Math.min(stBin,binMax(st.binHz)));$("sc-method").textContent="Hann STFT: 512 samples, 128 hop. No padding. Color scale clipped below −100 dBFS."; $("sc-first").textContent=fmt(st.time[0],2)+" ms";$("sc-last").textContent=fmt(st.time[st.time.length-1],2)+" ms";$("sc-stft-meta").textContent=st.frames.length+" frames · Δf "+fmt(st.binHz,3)+" Hz · 0–"+fmt(binMax(st.binHz)*st.binHz,1)+" Hz";}
 readout();
}
function select(next){mode=next;stFrame=0;stBin=0;cursor(0,0);if(good&&(mode==="fft"||mode==="phase"))cursor(binMax(spec.binHz),spec.peak??0);render();}
for(const b of document.querySelectorAll("[data-sc-mode]"))b.addEventListener("click",()=>select(b.dataset.scMode));
$("sc-band").addEventListener("change",render);
$("sc-cursor").addEventListener("input",()=>{
 readout();if(plot){const i=Number($("sc-cursor").value),left=plot.valToPos(plot.data[0][i],"x");if(Number.isFinite(left))plot.setCursor({left,top:plot.bbox.height/(devicePixelRatio||1)/2});}
});
$("sc-second").addEventListener("input",readout);
$("sc-heatmap").addEventListener("pointerdown",e=>{
 if(!good||mode!=="stft")return;const rect=e.currentTarget.getBoundingClientRect(),bins=binMax(st.binHz)+1;
 stFrame=Math.max(0,Math.min(st.frames.length-1,Math.floor((e.clientX-rect.left)/rect.width*st.frames.length)));
 stBin=Math.max(0,Math.min(bins-1,Math.floor((1-(e.clientY-rect.top)/rect.height)*bins)));
 $("sc-cursor").value=String(stFrame);$("sc-second").value=String(stBin);readout();
});
$("sc-reset").addEventListener("click",()=>{$("sc-band").value="1000";select(mode);});
function redraw(){if(!scheduled)scheduled=requestAnimationFrame(()=>{scheduled=0;render();});}
$("theme").addEventListener("change",redraw);$("language").addEventListener("change",()=>{translate();redraw();});
if(window.matchMedia){const mq=matchMedia("(prefers-color-scheme: light)");if(mq.addEventListener)mq.addEventListener("change",redraw);}
if(typeof ResizeObserver==="function"){let width=0;new ResizeObserver(entries=>{const next=entries[0].contentRect.width;if(Math.abs(next-width)>1){width=next;redraw();}}).observe(document.querySelector(".science-visual"));}
else window.addEventListener("resize",redraw);
$("science-test").addEventListener("click",()=>{
 const prev=mode,band=$("sc-band").value,oldCursor=Number($("sc-cursor").value),oldSecond=Number($("sc-second").value);
 const checks=FIKScience.tests();let error=null;
 try{
  checks.dictionaries=Object.keys(dict).length===10&&Object.values(dict).every(s=>s.split("|").length===labels.length);
  checks.no_physical_command=document.querySelector(".start").disabled&&document.querySelector(".stop").disabled;
  checks.source_contract=good||source.source==="UNAVAILABLE";
  if(good){
   checks.actual_samples=x.length===4096&&stats.peak<=.25&&Number.isFinite(stats.rms);
   checks.actual_fft=spec.hz.length===2049&&spec.amp.every(Number.isFinite)&&spec.binHz===rate/4096;
   checks.actual_stft=st.frames.length===29&&st.frames.every(f=>f.length===257&&f.every(Number.isFinite));
   select("time");checks.waveform_render=!!plot&&plot.data[1].length===4096;
   select("fft");checks.spectrum_render=!!plot&&plot.data[1].length===2049;
   select("stft");checks.heatmap_render=drawHeat()&&!$("sc-heat").hidden;
   select("phase");checks.phase_render=drawPhase(Number($("sc-cursor").value))&&!$("sc-phase").hidden;
  }else{select("time");checks.no_trace=!plot&&!$("sc-unavailable").hidden;}
 }catch(e){error=String(e);}
 finally{$("sc-band").value=band;select(prev);$("sc-cursor").value=String(oldCursor);$("sc-second").value=String(oldSecond);readout();}
 const vals=Object.values(checks),passed=vals.filter(Boolean).length;
 const report={checks,passed,total:vals.length,error,native_snapshot:good,scope:"DIGITAL_ANALYSIS_AND_BROWSER_ONLY",physical_output:"NONE"};
 $("science-test-result").textContent=passed+"/"+vals.length+" "+(!error&&passed===vals.length?(good?"PASS":"PASS (NO SOURCE)"):"FAIL");
 console.log("FIK_UI003_REPORT="+JSON.stringify(report));
});
translate();setMetrics();render();
})();
