// esporta i personaggi "Ultimate Modular Men/Women" (Quaternius, CC0) per Karmapolis: geometria liscia, pesi sulle ossa Mixamo, giunture
import * as THREE from 'three'; import fs from 'fs';
import {GLTFLoader} from 'three/examples/jsm/loaders/GLTFLoader.js';
import {mergeVertices} from 'three/examples/jsm/utils/BufferGeometryUtils.js';
THREE.FileLoader.prototype.load=function(url,onLoad,_,onErr){ try{ const b=fs.readFileSync(decodeURIComponent(url)); onLoad(b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength)); }catch(e){ onErr&&onErr(e); } };
async function loadG(path){ const dir=path.slice(0,path.lastIndexOf('/')+1); const j=JSON.parse(fs.readFileSync(path,'utf8')); for(const b of j.buffers){ if(b.uri.startsWith('data:')){ const f='/tmp/rb_'+(Math.random()*1e9|0)+'.bin'; fs.writeFileSync(f,Buffer.from(b.uri.slice(b.uri.indexOf(',')+1),'base64')); b.uri=f; } else b.uri=dir+b.uri; } return await new Promise((res,rej)=>new GLTFLoader().parse(JSON.stringify(j),'',res,rej)); }
const MIX=['Hips','Spine','Spine1','Spine2','Neck','Head','LeftShoulder','LeftArm','LeftForeArm','LeftHand','RightShoulder','RightArm','RightForeArm','RightHand','LeftUpLeg','LeftLeg','LeftFoot','LeftToeBase','RightUpLeg','RightLeg','RightFoot','RightToeBase'];
for(const s of ['Left','Right']) for(const f of ['Thumb','Index','Middle','Ring','Pinky']) for(let i=1;i<=4;i++) MIX.push(s+'Hand'+f+i);
const QM={Root:'Hips',Body:'Hips',Hips:'Hips',Abdomen:'Spine',Torso:'Spine1',Chest:'Spine2',Neck:'Neck',Head:'Head'};
for(const [q,m] of [['L','Left'],['R','Right']]){ Object.assign(QM,{['Shoulder'+q]:m+'Shoulder',['UpperArm'+q]:m+'Arm',['LowerArm'+q]:m+'ForeArm',['Wrist'+q]:m+'Hand',['UpperLeg'+q]:m+'UpLeg',['LowerLeg'+q]:m+'Leg',['Foot'+q]:m+'Foot',['PT'+q]:m+'ToeBase'});
  for(const f of ['Thumb','Index','Middle','Ring','Pinky']) for(let i=1;i<=4;i++) QM[f+i+q]=m+'Hand'+f+i; }
const MEN='/home/claude/bl/out/m/', WOM='/home/claude/bl/out/f/';
const MODELS={m:['Casual_2','Casual_Hoodie','Suit','Worker','Farmer','Beach','Punk','Adventurer','King','Swat','Spacesuit'],f:['Casual','Formal','Suit','Worker','Punk','Adventurer','Medieval','Soldier','SciFi','Witch']};
const EXCL={m:{Head:['Swat','Spacesuit','King'],Body:['Swat','Spacesuit','King'],Legs:['Swat','Spacesuit','King'],Feet:['Swat','Spacesuit','King']},f:{Head:['Witch','SciFi'],Body:['Medieval','SciFi','Witch','Soldier'],Legs:['SciFi','Witch'],Feet:['SciFi']}};
const META={mix:MIX,rigs:{},parts:[]}; const BIN=[]; let off=0;
const push=(arr)=>{ const pad=(4-(off%4))%4; if(pad){ BIN.push(Buffer.alloc(pad)); off+=pad; } BIN.push(Buffer.from(arr.buffer,arr.byteOffset,arr.byteLength)); const o=off; off+=arr.byteLength; return [o,arr.length]; };
const FINGER=/(Thumb|Index|Middle|Ring|Pinky)\d/;
for(const sex of ['m','f']) for(const name of MODELS[sex]){ const g=await loadG((sex==='m'?MEN:WOM)+name+'.gltf'); g.scene.updateMatrixWorld(true);
  const byKind={}; g.scene.traverse(o=>{ if(!o.isSkinnedMesh) return; const kind=((o.name+' '+(o.parent&&o.parent.name)).match(/_(Head|Body|Legs|Feet)/)||[])[1]; if(!kind||EXCL[sex][kind].includes(name)) return; (byKind[kind]=byKind[kind]||[]).push(o); });
  for(const [kind,list] of Object.entries(byKind)){ const o=list[0];
    // più primitive (un materiale ciascuna) → una geometria sola con i gruppi
    if(list.length>1){ const gs=list.map(x=>x.geometry.index?x.geometry.toNonIndexed():x.geometry.clone()); const mg=(await import('three/examples/jsm/utils/BufferGeometryUtils.js')).mergeGeometries(gs,true); o.geometry=mg; o.material=list.map(x=>x.material); }
    if(!META.rigs[sex]){ const J={}; const sk=o.skeleton; for(let i=0;i<sk.bones.length;i++){ if(/^(Root|Body)$/.test(sk.bones[i].name)) continue; const mn=QM[sk.bones[i].name]; if(!mn||J[mn]) continue; const p=new THREE.Vector3().setFromMatrixPosition(sk.boneInverses[i].clone().invert()).applyMatrix4(o.bindMatrix).applyMatrix4(o.matrixWorld); J[mn]=p.toArray().map(x=>+x.toFixed(4)); } META.rigs[sex]=J; }
    let geo=o.geometry.index?o.geometry.toNonIndexed():o.geometry.clone(); const P=geo.attributes.position, v=new THREE.Vector3(); for(let i=0;i<P.count;i++){ v.fromBufferAttribute(P,i).applyMatrix4(o.bindMatrix).applyMatrix4(o.matrixWorld); P.setXYZ(i,v.x,v.y,v.z); }
    const ml=Array.isArray(o.material)?o.material:[o.material]; const mats=[]; const part=new Float32Array(P.count); const groups=geo.groups.length?geo.groups:[{start:0,count:P.count,materialIndex:0}];
    for(const gr of groups){ const m=ml[gr.materialIndex]; let k=mats.findIndex(x=>x.name===m.name.replace(/\.\d+$/,'')); if(k<0){ k=mats.length; mats.push({name:m.name.replace(/\.\d+$/,''),color:'#'+m.color.getHexString()}); } for(let t=gr.start;t<gr.start+gr.count;t++) part[t]=k; }
    const SI=geo.attributes.skinIndex, SW=geo.attributes.skinWeight; const ni=new Float32Array(P.count*4), nw=new Float32Array(P.count*4);
    for(let i=0;i<P.count;i++){ const acc={}; for(let k=0;k<4;k++){ const w=SW.getComponent(i,k); if(w<=0) continue; const bn=o.skeleton.bones[SI.getComponent(i,k)].name; let mn=QM[bn]||'Hips'; mn=mn.replace(/Hand(Thumb|Index|Middle|Ring|Pinky)\d$/,'Hand'); acc[mn]=(acc[mn]||0)+w; } // dita → mano (rigida: le dita del modello e dello scheletro hanno orientamenti diversi)
      const ent=Object.entries(acc).sort((a,b)=>b[1]-a[1]).slice(0,4); const sum=ent.reduce((a,e)=>a+e[1],0)||1; ent.forEach(([mn,w],k)=>{ ni[i*4+k]=MIX.indexOf(mn); nw[i*4+k]=w/sum; }); }
    let ng=new THREE.BufferGeometry(); ng.setAttribute('position',new THREE.BufferAttribute(P.array.slice(0),3)); ng.setAttribute('part',new THREE.BufferAttribute(part,1)); ng.setAttribute('skinIndex',new THREE.BufferAttribute(ni,4)); ng.setAttribute('skinWeight',new THREE.BufferAttribute(nw,4));
    ng=mergeVertices(ng,1e-4); ng.computeVertexNormals();
    const A=ng.attributes, n=A.position.count; const pos=new Float32Array(A.position.array), nor=new Int8Array(n*3); for(let i=0;i<n*3;i++) nor[i]=Math.round(A.normal.array[i]*127);
    const pa=new Uint8Array(n), si=new Uint8Array(n*4), sw=new Uint8Array(n*4); for(let i=0;i<n;i++){ pa[i]=A.part.array[i]; for(let k=0;k<4;k++){ si[i*4+k]=A.skinIndex.array[i*4+k]; sw[i*4+k]=Math.round(A.skinWeight.array[i*4+k]*255); } }
    META.parts.push({sex,kind,name,mats,n,pos:push(pos),nor:push(nor),part:push(pa),si:push(si),sw:push(sw),ind:push(new Uint16Array(ng.index.array))}); } }
// Anthony (Teo): viso "Avventura" con i capelli lunghi. Copio la testa e allungo verso il basso i capelli di dietro e dei lati (la barba davanti resta com'è)
{ const src=META.parts.find(p=>p.sex==='m'&&p.kind==='Head'&&p.name==='Adventurer'); const all=Buffer.concat(BIN);
  const pos=new Float32Array(all.buffer.slice(all.byteOffset+src.pos[0],all.byteOffset+src.pos[0]+src.pos[1]*4)); const pa=new Uint8Array(all.buffer.slice(all.byteOffset+src.part[0],all.byteOffset+src.part[0]+src.part[1]));
  const hk=src.mats.findIndex(m=>m.name==='Hair'); const Y0=1.80, L=2.6;
  for(let i=0;i<src.n;i++){ if(pa[i]!==hk) continue; const y=pos[i*3+1], z=pos[i*3+2]; if(y>=Y0) continue; const w=Math.min(1,Math.max(0,(0.085-z)/0.06)); if(w<=0) continue;
    const ny=Y0-(Y0-y)*(1+(L-1)*w); const drop=y-ny; pos[i*3+1]=ny; pos[i*3+2]=z-drop*0.25*w; const x=pos[i*3]; pos[i*3]=x*(1+drop*0.9*w); }
  const cp=a=>new a.constructor(a); const g=(o)=>new Uint8Array(all.buffer.slice(all.byteOffset+o[0],all.byteOffset+o[0]+o[1]*({nor:1,part:1,si:1,sw:1})[1]));
  const sub=(o,T,b)=>new T(all.buffer.slice(all.byteOffset+o[0],all.byteOffset+o[0]+o[1]*b));
  META.parts.push({...src,name:'Adventurer_Long',pos:push(pos),nor:push(sub(src.nor,Int8Array,1)),part:push(pa),si:push(sub(src.si,Uint8Array,1)),sw:push(sub(src.sw,Uint8Array,1)),ind:push(sub(src.ind,Uint16Array,2))}); }

// 💈 tagli nuovi per i personaggi di Teo (26/11): "Marines" (lati rasati, spazzola sopra) per Carlo, "Calvo in mezzo" (cozzetta, capelli ai lati) per Leo
function headVariant(srcName,newName,fn){ const src=META.parts.find(p=>p.sex==='m'&&p.kind==='Head'&&p.name===srcName); const all=Buffer.concat(BIN);
  const sub=(o,T,bytes)=>new T(all.buffer.slice(all.byteOffset+o[0],all.byteOffset+o[0]+o[1]*bytes));
  const pos=sub(src.pos,Float32Array,4), pa=sub(src.part,Uint8Array,1), mats=src.mats.map(m=>({...m}));
  fn(pos,pa,mats,src.n);
  META.parts.push({...src,name:newName,mats,pos:push(pos),nor:push(sub(src.nor,Int8Array,1)),part:push(pa),si:push(sub(src.si,Uint8Array,1)),sw:push(sub(src.sw,Uint8Array,1)),ind:push(sub(src.ind,Uint16Array,2))}); }
const C0=[0,1.735,0.0]; // centro della testa (circa)
const pullIn=(pos,i,d)=>{ const x=pos[i*3]-C0[0], y=pos[i*3+1]-C0[1], z=pos[i*3+2]-C0[2], L=Math.hypot(x,y,z)||1; pos[i*3]-=x/L*d; pos[i*3+1]-=y/L*d; pos[i*3+2]-=z/L*d; };
headVariant('Casual_2','Marines',(pos,pa,mats,n)=>{ const hk=mats.findIndex(m=>m.name==='Hair'); let sd=mats.findIndex(m=>m.name==='Skin_Darker'); if(sd<0){ sd=mats.length; mats.push({name:'Skin_Darker',color:'#9a7a64'}); }
  for(let i=0;i<n;i++){ if(pa[i]!==hk) continue; const x=pos[i*3], y=pos[i*3+1], z=pos[i*3+2];
    if(y<1.68 && z>0.02) continue; // barba: resta
    if(y<1.80 || Math.abs(x)>0.075){ pa[i]=sd; pullIn(pos,i,0.012); } // lati e nuca rasati
    else { pos[i*3+1]+=0.012+0.25*(y-1.80); } } }); // sopra: spazzola un po' più alta
headVariant('Suit','Calvo_Lati',(pos,pa,mats,n)=>{ const hk=mats.findIndex(m=>m.name==='Hair'), sk=mats.findIndex(m=>m.name==='Skin');
  for(let i=0;i<n;i++){ if(pa[i]!==hk) continue; const x=pos[i*3], y=pos[i*3+1], z=pos[i*3+2];
    if((y>1.755 && Math.abs(x)<0.088) || (z>0.04 && y>1.725)){ pa[i]=sk; const dx=x-C0[0], dy=y-C0[1], dz=z-C0[2], L=Math.hypot(dx,dy,dz), R=Math.min(L,0.092); pos[i*3]=C0[0]+dx/L*R; pos[i*3+1]=C0[1]+dy/L*R; pos[i*3+2]=C0[2]+dz/L*R; } } }); // la parte senza capelli torna sulla forma della testa // in cima e davanti niente capelli (la "cozzetta"), restano ai lati e dietro
headVariant('Casual_2','Spazzola',(pos,pa,mats,n)=>{ const hk=mats.findIndex(m=>m.name==='Hair'), sk=mats.findIndex(m=>m.name==='Skin'); const sd=mats.length; mats.push({name:'Shaved',color:'#6b5444'});
  const skin=[]; for(let i=0;i<n;i++) if(pa[i]===sk) skin.push(i);
  const snap=(i,out)=>{ const x=pos[i*3], y=pos[i*3+1], z=pos[i*3+2]; let b=-1,bd=1e9; for(const j of skin){ const d=(pos[j*3]-x)**2+(pos[j*3+1]-y)**2+(pos[j*3+2]-z)**2; if(d<bd){ bd=d; b=j; } } if(b<0) return;
    const dx=x-C0[0], dy=y-C0[1], dz=z-C0[2], L=Math.hypot(dx,dy,dz)||1, R=Math.hypot(pos[b*3]-C0[0],pos[b*3+1]-C0[1],pos[b*3+2]-C0[2])+out; pos[i*3]=C0[0]+dx/L*R; pos[i*3+1]=C0[1]+dy/L*R; pos[i*3+2]=C0[2]+dz/L*R; };
  const orig=pos.slice(); const sel=[];
  for(let i=0;i<n;i++){ if(pa[i]!==hk) continue; const x=orig[i*3], y=orig[i*3+1], z=orig[i*3+2];
    const top=y>1.775 && z>-0.075 && Math.abs(x)<0.075;
    if(top) sel.push([i,0.022]); else { pa[i]=sd; sel.push([i,0.006]); } } // sopra: spazzola corta (2 cm), lati, nuca e barba rasati: niente codino
  for(const [i,o] of sel) snap(i,o); });
const cnt={}; for(const p of META.parts){ const k=p.sex+p.kind; cnt[k]=(cnt[k]||0)+1; } console.log(cnt, 'vertici medi', Math.round(META.parts.reduce((a,p)=>a+p.n,0)/META.parts.length));
fs.mkdirSync('/home/claude/umout3',{recursive:true}); fs.writeFileSync('/home/claude/umout3/gente.bin',Buffer.concat(BIN)); fs.writeFileSync('/home/claude/umout3/gente.json',JSON.stringify(META)); console.log('bin',off);
