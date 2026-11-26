/* SPDX-License-Identifier: Apache-2.0 */
const FIKPrecision=(()=>{
"use strict";
const clamp=(v,a,b)=>Math.min(b,Math.max(a,v));
function ratio(v,min,max,scale){if(!Number.isFinite(v)||min>=max||min<=0&&scale==="log")return 0;v=clamp(v,min,max);return scale==="log"?Math.log(v/min)/Math.log(max/min):(v-min)/(max-min);}
function position(p,min,max,scale){p=clamp(p,0,1);return Math.round(scale==="log"?min*Math.pow(max/min,p):min+(max-min)*p);}
function drag(v,dy,min,max,scale,precision,shift){
 if(precision==="fine"||shift)return clamp(Math.round(v+dy),min,max);
 return position(ratio(v,min,max,scale)+dy/240,min,max,scale);
}
function step(id,precision,shift){return shift||precision==="fine"?1:id==="freq"?100:id==="duration"?100:10;}
function differential(a,b,x,y){
 if(!Array.isArray(x)||!Array.isArray(y)||x.length!==y.length||!Number.isInteger(a)||!Number.isInteger(b)||a<0||b<0||a>=x.length||b>=x.length)return null;
 if(![x[a],x[b],y[a],y[b]].every(Number.isFinite))return null;
 return {ax:x[a],bx:x[b],ay:y[a],by:y[b],dx:x[b]-x[a],dy:y[b]-y[a]};
}
function tests(){
 const d=differential(0,2,[0,1,2],[.1,.3,.4]);
 const reverse=differential(2,0,[0,1,2],[.1,.3,.4]);
 return {linear_bounds:position(0,1,22049,"linear")===1&&position(1,1,22049,"linear")===22049,
 log_bounds:position(0,1,22049,"log")===1&&position(1,1,22049,"log")===22049,
 log_mid:position(.5,1,10000,"log")===100,
 round_trip:[1,440,828,10000,22049].every(v=>position(ratio(v,1,22049,"log"),1,22049,"log")===v),
 fine:drag(828,1,1,22049,"log","fine",false)===829,
 shift:drag(828,-1,1,22049,"log","coarse",true)===827,
 clamp:drag(1,-10,1,22049,"linear","fine",false)===1,
 coarse_log:drag(100,120,1,10000,"log","coarse",false)===10000,
 keyboard:step("freq","fine",false)===1&&step("freq","coarse",false)===100&&step("level","coarse",true)===1,
 differential:!!d&&d.dx===2&&Math.abs(d.dy-.3)<1e-12,
 signed:!!reverse&&reverse.dx===-2&&Math.abs(reverse.dy+.3)<1e-12,
 invalid:differential(-1,0,[1],[2])===null&&differential(0,1,[1,2],[2,NaN])===null};
}
return Object.freeze({ratio,position,drag,step,differential,tests});
})();
