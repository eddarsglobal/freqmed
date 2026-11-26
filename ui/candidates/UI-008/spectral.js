/* SPDX-License-Identifier: Apache-2.0 */
const FIKSpectral=(()=>{
"use strict";
const DB=a=>a>0?20*Math.log10(a):null;
function peaks(s,limit=8){
 const p=[],a=s.amp;
 for(let k=2;k<a.length-2;k++){
  if(a[k]<1e-6||a[k]<=a[k-1]||a[k]<a[k+1])continue;
  const l=Math.log(Math.max(a[k-1],1e-15)),m=Math.log(a[k]),r=Math.log(Math.max(a[k+1],1e-15)),den=l-2*m+r;
  const offset=den<0?Math.max(-.5,Math.min(.5,.5*(l-r)/den)):0;
  p.push({bin:k,binHz:s.hz[k],estimateHz:(k+offset)*s.binHz,amplitude:a[k],db:DB(a[k])});
 }
 return p.sort((a,b)=>b.amplitude-a.amplitude||a.bin-b.bin).slice(0,limit);
}
// Fit DC and up to eight sinusoidal harmonics jointly at the native command frequency.
// The model describes only this digital window. It is not an acoustic distortion measurement.
function harmonicFit(x,rate,f){
 if(!FIKScience.valid(x,rate)||!Number.isFinite(f)||f<=0||f>=rate/2||f*x.length/rate<4)return null;
 const count=Math.min(8,Math.ceil(rate/(2*f))-1);
 if(count<1)return null;
 const n=1+2*count,A=Array.from({length:n},()=>new Float64Array(n+1)),row=new Float64Array(n);
 let energy=0;row[0]=1;
 for(let i=0;i<x.length;i++){
  const t=2*Math.PI*f*i/rate;energy+=x[i]*x[i];
  for(let k=1;k<=count;k++){row[2*k-1]=Math.cos(k*t);row[2*k]=Math.sin(k*t);}
  for(let j=0;j<n;j++){for(let k=j;k<n;k++)A[j][k]+=row[j]*row[k];A[j][n]+=row[j]*x[i];}
 }
 for(let j=0;j<n;j++)for(let k=0;k<j;k++)A[j][k]=A[k][j];
 for(let j=0;j<n;j++){
  let p=j;for(let k=j+1;k<n;k++)if(Math.abs(A[k][j])>Math.abs(A[p][j]))p=k;
  if(Math.abs(A[p][j])<x.length*1e-8)return null;
  [A[j],A[p]]=[A[p],A[j]];const v=A[j][j];
  for(let k=j;k<=n;k++)A[j][k]/=v;
  for(let i=0;i<n;i++)if(i!==j){const z=A[i][j];for(let k=j;k<=n;k++)A[i][k]-=z*A[j][k];}
 }
 const c=A.map(a=>a[n]);if(!c.every(Number.isFinite))return null;
 const harmonics=Array.from({length:count},(_,i)=>({order:i+1,hz:f*(i+1),amplitude:Math.hypot(c[2*i+1],c[2*i+2])}));
 if(harmonics[0].amplitude<1e-6)return null;
 let error=0;
 for(let i=0;i<x.length;i++){
  let y=c[0],t=2*Math.PI*f*i/rate;
  for(let k=1;k<=count;k++)y+=c[2*k-1]*Math.cos(k*t)+c[2*k]*Math.sin(k*t);
  error+=(x[i]-y)**2;
 }
 const residual=energy>0?Math.sqrt(error/energy):null;
 return {harmonics,thd:count>=2?Math.sqrt(harmonics.slice(1).reduce((s,h)=>s+h.amplitude*h.amplitude,0))/harmonics[0].amplitude:null,residual,commandHz:f};
}
function comparable(a,b){return !!a&&!!b&&a.rate===b.rate&&a.n===b.n&&a.spectrum.amp.length===b.spectrum.amp.length;}
function compare(a,b){if(!comparable(a,b))return null;return {deltaRms:b.rms-a.rms,deltaPeak:b.peak-a.peak,deltaCommand:b.command-a.command};}
function axis(f,lo,hi,log){return log?Math.log(f/lo)/Math.log(hi/lo):(f-lo)/(hi-lo);}
function tests(){
 const n=4096,r=4096,f=64.3;
 const x=Array.from({length:n},(_,i)=>.4*Math.sin(2*Math.PI*f*i/r)+.04*Math.cos(4*Math.PI*f*i/r));
 const s=FIKScience.spectrum(x,r),p=peaks(s),h=harmonicFit(x,r,f),z=Array(n).fill(0);
 const a={rate:r,n,spectrum:s,rms:.2,peak:.4,command:64},b={...a,rms:.3,peak:.5,command:65},d=compare(a,b);
 return {peak_detected:p.length>0&&p[0].bin===64,subbin_estimate:Math.abs(p[0].estimateHz-f)<.1,
 fundamental_fit:Math.abs(h.harmonics[0].amplitude-.4)<1e-10,harmonic_fit:Math.abs(h.harmonics[1].amplitude-.04)<1e-10,
 thd:Math.abs(h.thd-.1)<1e-10,residual:h.residual<1e-10,silence:peaks(FIKScience.spectrum(z,r)).length===0&&harmonicFit(z,r,f)===null,
 insufficient_cycles:harmonicFit(x,r,2)===null,nyquist:harmonicFit(x,r,r/2)===null,
 no_higher_harmonics:harmonicFit(Array.from({length:n},(_,i)=>.2*Math.cos(2*Math.PI*1500*i/r)),r,1500).thd===null,
 incompatible_comparison:compare(a,{...b,rate:2*r})===null,comparison:Math.abs(d.deltaRms-.1)<1e-12&&d.deltaCommand===1,
 axis_linear:axis(50,0,100,false)===.5,axis_log:Math.abs(axis(100,10,1000,true)-.5)<1e-12};
}
return Object.freeze({peaks,harmonicFit,compare,comparable,axis,tests});
})();
