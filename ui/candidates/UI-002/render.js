/* SPDX-License-Identifier: Apache-2.0 */
(()=>{
"use strict";
const id=x=>document.getElementById(x);
const source=JSON.parse(id("fik-source").textContent);
const good=source.source==="FREQMED_NATIVE_C_MEMORY_ONLY"&&source.physical_output===false&&source.physical_measurement===false&&
 Number.isInteger(source.rate_hz)&&source.rate_hz>0&&source.rate_hz<=384000&&source.count===4096&&
 Array.isArray(source.samples)&&source.samples.length===source.count&&source.samples.every(v=>Number.isFinite(v)&&Math.abs(v)<=.25);
const screen=id("screen"),grid=id("gpu-grid"),fallback=id("cpu-grid"),plotHost=id("digital-plot");
const tab=id("digital-tab"),label=id("renderer-status");
let gl=null,program=null,buf=null,position=-1,shade=null,gridBackend="CSS",digital=false,plot=null,frame=0;
const color=k=>getComputedStyle(document.documentElement).getPropertyValue(k).trim();
function rgb(hex){const m=/^#([0-9a-f]{6})$/i.exec(hex);return m?[0,2,4].map(i=>parseInt(m[1].slice(i,i+2),16)/255):[.2,.25,.3];}
function shader(kind,src){const s=gl.createShader(kind);gl.shaderSource(s,src);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS)){gl.deleteShader(s);throw Error("shader compile");}return s;}
function setup(){
 try{
  gl=grid.getContext("webgl2",{alpha:true,antialias:false,preserveDrawingBuffer:false,powerPreference:"low-power"});
  if(!gl)return false;
  const v=shader(gl.VERTEX_SHADER,"#version 300 es\nin vec2 p;void main(){gl_Position=vec4(p,0.,1.);}");
  const f=shader(gl.FRAGMENT_SHADER,"#version 300 es\nprecision mediump float;uniform vec3 ink;out vec4 c;void main(){c=vec4(ink,1.);}");
  program=gl.createProgram();gl.attachShader(program,v);gl.attachShader(program,f);gl.linkProgram(program);
  gl.deleteShader(v);gl.deleteShader(f);
  if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw Error("link");
  position=gl.getAttribLocation(program,"p");shade=gl.getUniformLocation(program,"ink");buf=gl.createBuffer();
  if(position<0||!shade||!buf)throw Error("bindings");
  return true;
 }catch(_){return false;}
}
function dimensions(canvas){const ratio=Math.min(2,window.devicePixelRatio||1),w=Math.max(1,Math.min(4096,Math.round(screen.clientWidth*ratio))),h=Math.max(1,Math.min(2048,Math.round(screen.clientHeight*ratio)));if(canvas.width!==w)canvas.width=w;if(canvas.height!==h)canvas.height=h;return [w,h,ratio];}
function paintGrid(forceCPU=false){
 if(digital)return;
 const [w,h,r]=dimensions(grid),spacing=Math.max(10,40*zoom*r),ink=rgb(color("--edge"));
 let ok=false;
 if(!forceCPU&&gl&&program&&!gl.isContextLost()){
  try{
   const vertices=[];
   for(let x=w/2%spacing;x<w;x+=spacing)vertices.push(x/w*2-1,-1,x/w*2-1,1);
   for(let y=h/2%spacing;y<h;y+=spacing)vertices.push(-1,y/h*2-1,1,y/h*2-1);
   gl.viewport(0,0,w,h);gl.clearColor(0,0,0,0);gl.clear(gl.COLOR_BUFFER_BIT);
   gl.useProgram(program);gl.bindBuffer(gl.ARRAY_BUFFER,buf);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(vertices),gl.DYNAMIC_DRAW);
   gl.enableVertexAttribArray(position);gl.vertexAttribPointer(position,2,gl.FLOAT,false,0,0);gl.uniform3fv(shade,ink);
   gl.drawArrays(gl.LINES,0,vertices.length/2);ok=gl.getError()===gl.NO_ERROR;
  }catch(_){ok=false;}
 }
 if(ok){gridBackend="WebGL 2";grid.hidden=false;fallback.hidden=true;}
 else{
  grid.hidden=true;const [cw,ch,cr]=dimensions(fallback),ctx=fallback.getContext("2d");
  if(ctx){ctx.clearRect(0,0,cw,ch);ctx.strokeStyle=color("--edge");ctx.lineWidth=cr;const s=40*zoom*cr;
   ctx.beginPath();for(let x=cw/2%s;x<cw;x+=s){ctx.moveTo(x,0);ctx.lineTo(x,ch);}
   for(let y=ch/2%s;y<ch;y+=s){ctx.moveTo(0,y);ctx.lineTo(cw,y);}ctx.stroke();fallback.hidden=false;gridBackend="Canvas 2D";
  }else{fallback.hidden=true;gridBackend="CSS";}
 }
 screen.classList.toggle("native-grid",gridBackend!=="CSS");
 label.textContent=gridBackend+" · "+(good?"C snapshot available":"No C snapshot");
}
function plotData(){
 if(!good||typeof uPlot!=="function")return false;
 try{
  if(plot){plot.destroy();plot=null;}
  plotHost.replaceChildren();
  const width=Math.max(180,plotHost.clientWidth),height=Math.max(150,plotHost.clientHeight);
  const x=source.samples.map((_,i)=>i*1000/source.rate_hz);
  plot=new uPlot({width,height,legend:{show:false},cursor:{drag:{x:true,y:false}},scales:{x:{time:false},y:{range:[-.27,.27]}},
   axes:[{stroke:color("--muted"),grid:{stroke:color("--edge")},ticks:{stroke:color("--edge")},size:36,label:"ms"},
    {stroke:color("--muted"),grid:{stroke:color("--edge")},ticks:{stroke:color("--edge")},size:53}],
   series:[{}, {label:"Digital command",stroke:color("--cyan"),width:1.5,points:{show:false}}]},[x,source.samples],plotHost);
  const end=x[x.length-1];plot.setScale("x",{min:0,max:Math.min(end,end/zoom)});
  return !!plot.root.querySelector("canvas");
 }catch(_){if(plot){plot.destroy();plot=null;}plotHost.textContent="Plot unavailable";return false;}
}
function showDigital(){
 digital=true;tab.setAttribute("aria-pressed","true");
 for(const b of document.querySelectorAll("[data-mode]"))b.setAttribute("aria-pressed","false");
 screen.hidden=true;plotHost.hidden=false;id("digital-info").hidden=false;
 label.textContent="uPlot · Canvas 2D";
 const ok=plotData();if(!ok)plotHost.textContent="Digital source / renderer unavailable";
 return ok;
}
function showAcquisition(){
 digital=false;tab.setAttribute("aria-pressed","false");plotHost.hidden=true;id("digital-info").hidden=true;
 if(plot){plot.destroy();plot=null;}screen.hidden=false;paintGrid();
}
const oldZoom=setZoom;
setZoom=function(v){oldZoom(v);if(digital){if(plot&&good){const end=(source.count-1)*1000/source.rate_hz;plot.setScale("x",{min:0,max:Math.min(end,end/zoom)});}}else paintGrid();};
function redraw(){if(frame)return;frame=requestAnimationFrame(()=>{frame=0;if(digital)plotData();else paintGrid();});}
grid.addEventListener("webglcontextlost",e=>{e.preventDefault();paintGrid(true);});
grid.addEventListener("webglcontextrestored",()=>{setup();redraw();});
tab.addEventListener("click",()=>{oldZoom(1);showDigital();});
for(const b of document.querySelectorAll("[data-mode]"))b.addEventListener("click",showAcquisition);
id("theme").addEventListener("change",redraw);
if(window.matchMedia){const mq=matchMedia("(prefers-color-scheme: light)");if(mq.addEventListener)mq.addEventListener("change",redraw);}
if(typeof ResizeObserver==="function")new ResizeObserver(redraw).observe(screen.parentElement);
else window.addEventListener("resize",redraw);
id("digital-info").textContent=good?
 "C11 · PLATFORM-09 · "+source.count+" samples · "+source.rate_hz+" Hz sample rate · "+source.command_hz+" Hz command · "+(source.digital_level*100)+"% digital · immutable snapshot · NOT MEASURED":
 "No native digital snapshot available";
tab.disabled=!good;
setup();paintGrid();
if(good)showDigital();
const original=runChecks;
id("selftest").onclick=()=>{
 const wasDigital=digital,previousMode=monitorMode;
 const base=original(),checks={};
 // Browser/graphics checks, never physical data. Real Canvas pixel readback.
 const c=document.createElement("canvas");c.width=c.height=2;const ctx=c.getContext("2d");
 if(ctx){ctx.fillStyle="#ff0000";ctx.fillRect(0,0,2,2);}
 checks.canvas2d=!!ctx&&ctx.getImageData(0,0,1,1).data[0]===255;
 checks.uplot=typeof uPlot==="function";
 checks.source=good||source.source==="UNAVAILABLE";
 showAcquisition();paintGrid(true);checks.fallback=gridBackend==="Canvas 2D";
 paintGrid();checks.grid=gridBackend==="WebGL 2"||gridBackend==="Canvas 2D";
 const actualBackend=gridBackend;checks.no_physical_commands=document.querySelector(".start").disabled&&document.querySelector(".stop").disabled;
 if(good){checks.native_plot=showDigital()&&!!plot&&plot.data[1].length===source.count;}
 if(wasDigital&&good)showDigital();else{document.querySelector('[data-mode="'+previousMode+'"]').click();}
 const values=Object.values(checks),passed=values.filter(Boolean).length;
 const report={base,checks,renderer:actualBackend,pixi:"NOT_INTEGRATED",native_snapshot:good,physical_output:"NONE"};
 id("test-result").textContent=(base.passed+passed)+"/"+(23+values.length)+" "+(!base.failed&&passed===values.length?"PASS":"FAIL");
 console.log("FIK_UI002_REPORT="+JSON.stringify(report));return report;
};
})();
