/* SPDX-License-Identifier: Apache-2.0 */
const FIKScience=(()=>{
"use strict";
const FLOOR=-120,EPS=1e-6;
function valid(x,rate){return Array.isArray(x)&&x.length>=16&&x.length<=4096&&
 (x.length&(x.length-1))===0&&Number.isInteger(rate)&&rate>0&&rate<=384000&&
 x.every(v=>Number.isFinite(v)&&Math.abs(v)<=1);}
function fft(re,im){
 const n=re.length;
 for(let i=1,j=0;i<n;i++){
  let bit=n>>1;for(;j&bit;bit>>=1)j^=bit;j^=bit;
  if(i<j){[re[i],re[j]]=[re[j],re[i]];[im[i],im[j]]=[im[j],im[i]];}
 }
 for(let m=2;m<=n;m*=2){
  for(let k=0;k<m/2;k++){
   const a=-2*Math.PI*k/m,c=Math.cos(a),s=Math.sin(a);
   for(let i=k;i<n;i+=m){
    const j=i+m/2,u=c*re[j]-s*im[j],v=s*re[j]+c*im[j];
    re[j]=re[i]-u;im[j]=im[i]-v;re[i]+=u;im[i]+=v;
   }
  }
 }
}
function spectrum(x,rate){
 if(!valid(x,rate))throw Error("Invalid bounded digital samples");
 const n=x.length,re=new Float64Array(n),im=new Float64Array(n);
 let gain=0;
 for(let i=0;i<n;i++){const w=.5-.5*Math.cos(2*Math.PI*i/n);gain+=w;re[i]=x[i]*w;}
 fft(re,im);
 const hz=[],amp=[],db=[],phase=[];
 let peak=0;
 for(let k=0;k<=n/2;k++){
  const a=Math.hypot(re[k],im[k])*(k===0||k===n/2?1:2)/gain;
  hz.push(k*rate/n);amp.push(a);db.push(Math.max(FLOOR,20*Math.log10(Math.max(1e-6,a))));
  phase.push(a>=EPS?Math.atan2(im[k],re[k])*180/Math.PI:null);
  if(k>0&&k<n/2&&(!peak||a>amp[peak]))peak=k;
 }
 if(amp[peak]<EPS)peak=null;
 return {hz,amp,db,phase,peak,binHz:rate/n};
}
function spectrogram(x,rate,size=512,hop=128){
 if(!valid(x,rate)||!Number.isInteger(size)||size<16||size>x.length||(size&(size-1))!==0||
    !Number.isInteger(hop)||hop<1||hop>size||Math.floor((x.length-size)/hop)+1>128)throw Error("Invalid STFT settings");
 const frames=[],time=[];
 for(let i=0;i+size<=x.length;i+=hop){
  frames.push(spectrum(x.slice(i,i+size),rate).db);
  time.push((i+size/2)*1000/rate);
 }
 return {frames,time,binHz:rate/size,size,hop};
}
function stats(x,rate){
 if(!valid(x,rate))throw Error("Invalid source");
 let sum=0,energy=0,peak=0;
 for(const v of x){sum+=v;energy+=v*v;peak=Math.max(peak,Math.abs(v));}
 return {mean:sum/x.length,rms:Math.sqrt(energy/x.length),peak,ms:1000*x.length/rate};
}
function tests(){
 const checks={},close=(a,b,t=1e-9)=>Math.abs(a-b)<t;
 // Algebraic software test vectors, never displayed as acquisition.
 const n=64,rate=6400,k=5,cos=Array.from({length:n},(_,i)=>.25*Math.cos(2*Math.PI*k*i/n+Math.PI/4));
 const s=spectrum(cos,rate),m=stats(cos,rate),z=spectrum(Array(n).fill(0),rate);
 checks.bin_frequency=s.hz[k]===500&&s.binHz===100;
 checks.peak_bin=s.peak===k;
 checks.amplitude=close(s.amp[k],.25);
 checks.phase=close(s.phase[k],45);
 checks.dbfs=close(s.db[k],20*Math.log10(.25));
 checks.rms=close(m.rms,.25/Math.sqrt(2));
 checks.mean=close(m.mean,0);
 checks.duration=m.ms===10;
 checks.silence=z.peak===null&&z.phase.every(v=>v===null)&&z.db.every(v=>v===FLOOR);
 const dc=spectrum(Array(n).fill(.2),rate);
 checks.dc_scaling=close(dc.amp[0],.2);
 const ny=spectrum(Array.from({length:n},(_,i)=>i%2?-.3:.3),rate);
 checks.nyquist_scaling=close(ny.amp[n/2],.3);
 const st=spectrogram(cos,rate,32,16);
 checks.stft_shape=st.frames.length===3&&st.frames.every(f=>f.length===17);
 checks.stft_time=st.time[0]===2.5&&st.time[2]===7.5;
 checks.stft_spacing=st.binHz===200;
 let rejected=0;
 for(const x of [[NaN,...cos.slice(1)],cos.slice(1),Array(n).fill(2)]){try{spectrum(x,rate);}catch(_){rejected++;}}
 checks.invalid_rejected=rejected===3;
 try{spectrogram(cos,rate,32,0);checks.hop_rejected=false;}catch(_){checks.hop_rejected=true;}
 return checks;
}
return Object.freeze({valid,spectrum,spectrogram,stats,tests,FLOOR});
})();
