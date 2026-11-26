/* SPDX-License-Identifier: Apache-2.0 */
const FIKPerf=(()=>{
"use strict";
function cache(clock){
 const entries=new WeakMap();
 let calls=0,hits=0,misses=0,computeMs=0,copyMs=0;
 const clone=s=>({...s,hz:s.hz.slice(),amp:s.amp.slice(),db:s.db.slice(),phase:s.phase.slice()});
 function spectrum(raw,x,rate){
  // Only immutable, full-sized windows can share results. A mutable input is never cached.
  if(!Array.isArray(x)||x.length!==4096||!Object.isFrozen(x))return raw(x,rate);
  calls++;let e=entries.get(x);
  if(e&&e.rate===rate){hits++;}else{
   misses++;const t=clock();const result=raw(x,rate);computeMs+=clock()-t;
   e={rate,result};entries.set(x,e);
  }
  const t=clock(),v=clone(e.result);copyMs+=clock()-t;return v;
 }
 return {spectrum,report:()=>({calls,hits,misses,computeMs,copyMs})};
}
const shared=cache(()=>performance.now());
function tests(){
 const c=cache(()=>0),x=Object.freeze(Array(4096).fill(.2)),y=Array(4096).fill(.2);
 let n=0;const raw=(a,r)=>{n++;return {hz:[r],amp:[a[0]],db:[-1],phase:[0],peak:0,binHz:r};};
 const a=c.spectrum(raw,x,44100);a.amp[0]=9;
 const b=c.spectrum(raw,x,44100),d=c.spectrum(raw,x,48000);
 c.spectrum(raw,y,44100);y[0]=.5;const e=c.spectrum(raw,y,44100);
 const report=c.report();
 return {cache_hit:report.hits===1,rate_invalidates:d.hz[0]===48000,isolated_result:b.amp[0]===.2,
 mutable_bypass:e.amp[0]===.5,counts:report.calls===3&&report.misses===2&&n===4,
 exact_result:b.binHz===44100&&b.phase[0]===0&&b.peak===0};
}
return Object.freeze({spectrum:shared.spectrum,report:shared.report,tests});
})();
// Capture phase runs before all instrument listeners. No new signal is created.
window.addEventListener("fik-native-snapshot",e=>{
 const d=e.detail;
 if(d&&d.source==="FREQMED_NATIVE_C_MEMORY_ONLY"&&Array.isArray(d.samples)&&d.samples.length===4096)Object.freeze(d.samples);
},true);
