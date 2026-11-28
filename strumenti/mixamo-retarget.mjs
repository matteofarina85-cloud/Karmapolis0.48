// 🎬 Converte un FBX di Mixamo (X Bot, Without Skin) in una clip per anims.json, riportando le rotazioni sullo scheletro del gioco (28/11/2026). Uso: node mixamo-retarget.mjs file.fbx uscita.json
import fs from 'fs'; globalThis.self=globalThis; globalThis.window=globalThis;
const THREE=await import('/home/claude/sim/node_modules/three/build/three.module.js');
const {FBXLoader}=await import('/home/claude/sim/node_modules/three/examples/jsm/loaders/FBXLoader.js');
const nm=s=>s.replace(/^mixamorig:?/,'');
let buf=fs.readFileSync(process.argv[2]); const src=new FBXLoader().parse(buf.buffer.slice(buf.byteOffset,buf.byteOffset+buf.byteLength),'');
const bones={}; src.traverse(o=>{ if(o.isBone) bones[nm(o.name)]=o; });
const names=Object.keys(bones); const par={}; for(const n of names){ let p=bones[n].parent; par[n]=(p&&p.isBone)?nm(p.name):null; }
src.updateMatrixWorld(true); const Wrest={}; for(const n of names) Wrest[n]=bones[n].getWorldQuaternion(new THREE.Quaternion());
const clip=src.animations[0]; const mixer=new THREE.AnimationMixer(src); const act=mixer.clipAction(clip); act.setLoop(THREE.LoopOnce); act.clampWhenFinished=true; act.play();
const times=clip.tracks.find(t=>/Hips\.quaternion$/.test(t.name)).times; const out={}; for(const n of names) out[n]=[]; const hipsPos=[];
const rootW=new THREE.Quaternion(); if(bones.Hips.parent) bones.Hips.parent.getWorldQuaternion(rootW);
let dbgN=0; for(const t of times){ mixer.setTime(t); if(dbgN++%20===0) console.log("t",t.toFixed(2),bones.Hips.position.y.toFixed(1)); src.updateMatrixWorld(true); const D={};
  for(const n of names){ const W=bones[n].getWorldQuaternion(new THREE.Quaternion()); D[n]=W.multiply(Wrest[n].clone().invert()); }
  for(const n of names){ const p=par[n]; const loc=p?D[p].clone().invert().multiply(D[n]):rootW.clone().invert().multiply(D[n]).multiply(rootW); out[n].push(...loc.toArray()); }
  hipsPos.push(...bones.Hips.position.toArray()); }
const tracks=[]; tracks.push({name:'mixamorigHips.position',type:'vector',times:Array.from(times),values:hipsPos});
for(const n of names) tracks.push({name:'mixamorig'+n+'.quaternion',type:'quaternion',times:Array.from(times),values:out[n]});
const q=(b,i)=>out[b].slice(i*4,i*4+4).map(x=>+x.toFixed(3)); const L=times.length-1; for(const b of ['Hips','Spine','LeftUpLeg','LeftArm','Head']) console.log(b,q(b,L), 'start',q(b,0));
console.log('hips pos start',hipsPos.slice(0,3).map(x=>+x.toFixed(1)),'end',hipsPos.slice(-3).map(x=>+x.toFixed(1)));
fs.writeFileSync(process.argv[3],JSON.stringify({name:'Getting Up',duration:clip.duration,tracks}));
