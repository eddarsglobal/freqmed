/* SPDX-License-Identifier: Apache-2.0 */
const FIKDashboardMath=(()=>{
"use strict";
function metrics(x){
 if(!Array.isArray(x)||x.length<1||x.length>4096)return null;
 let peak=0,sum=0;
 for(const v of x){if(typeof v!=="number"||!Number.isFinite(v)||Math.abs(v)>1)return null;peak=Math.max(peak,Math.abs(v));sum+=v*v;}
 const rms=Math.sqrt(sum/x.length),db=v=>v===0?null:20*Math.log10(v);
 return {peak,rms,peakDb:db(peak),rmsDb:db(rms)};
}
function segments(db){return db===null||!Number.isFinite(db)?0:Math.max(0,Math.min(24,Math.ceil((db+60)/60*24)));}
function progress(done,expected){return Number.isSafeInteger(done)&&Number.isSafeInteger(expected)&&expected>0&&done>=0&&done<=expected?done/expected:null;}
function tests(){
 const a=metrics([.5,-.5,.5,-.5]),z=metrics([0,0]),b=metrics([1,0]);
 return {peak:a.peak===.5,rms:a.rms===.5,db:Math.abs(a.peakDb+6.020599913279624)<1e-10,
  silent:z.peakDb===null&&segments(z.peakDb)===0,rms_mixed:Math.abs(b.rms-Math.SQRT1_2)<1e-12,
  segments:segments(0)===24&&segments(-30)===12&&segments(-61)===0,
  bounds:metrics([NaN])===null&&metrics([1.01])===null&&metrics([])===null,
  progress:progress(441000,441000)===1&&progress(1,2)===.5&&progress(3,2)===null};
}
return Object.freeze({metrics,segments,progress,tests});
})();
