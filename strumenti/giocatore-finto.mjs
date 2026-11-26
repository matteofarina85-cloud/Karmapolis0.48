// 🤖 GIOCATORE FINTO v2 (26/11/2026): gioca partite intere con le regole nuove e fa il riassunto per livello.
// uso: node bot2.mjs "1,2,3,4,10" [partite per livello=3] [bravura=1 | 0.7 principiante]
await import('./run.mjs');
const w=W, S=w.__sim, $=id=>w.document.getElementById(id);
const LVS=(process.argv[2]||'1,2,3,4').split(',').map(Number), RUNS=+process.argv[3]||3, SK=+process.argv[4]||1;
const D=(a,b)=>Math.hypot(a.x-b.x,a.z-b.z);
const out=[]; let first=true;
for(const lv of LVS){ const R=[];
  for(let r=0;r<RUNS;r++){ S.LV.n=lv; if(first){ w.__dbg.goTown(); first=false; } $('restart').click(); S.G.karma=Math.max(S.G.karma,0);
    let busy=0, st={cure:0,wrong:0,candy:0,buy:0,carlo:0,leoHit:0}, maxCarriers=0, k0=S.G.karma;
    for(let f=0;f<9000;f++){ __step(1); if(S.gameOver) break; const P=S.player.pos; busy-=0.05;
      const carriers=S.PEDS.filter(p=>p.good>0).length; if(carriers>maxCarriers) maxCarriers=carriers;
      if(S.LEO.on && S.carloAvail() && S.G.karma>=S.CARLO.price){ if(S.callCarlo()) st.carlo++; }
      if(S.player.listen||busy>0) continue;
      const goTo=(t)=>{ const d=Math.hypot(t.x-P.x,t.z-P.z); if(d<=1.8) return true; const sp=4.6*SK*0.05*0.8; P.x+=(t.x-P.x)/d*Math.min(d-1.5,sp); P.z+=(t.z-P.z)/d*Math.min(d-1.5,sp); return false; };
      // 1) caramella a chi sta già bene, in mezzo alla gente
      if(S.G.candies>0){ let best=null,bs=-1e9; for(const p of S.PEDS){ if(p.kind||p.good>0||p.gone||p.ko>0) continue; const d=D(p,P); if(d>18) continue; let n=0; for(const q of S.PEDS) if(q!==p&&D(p,q)<5) n+=q.kind?2:1; const sc=n*3-d; if(sc>bs){ bs=sc; best=p; } }
        if(best){ if(goTo(best)){ S.player.focusPed=best; const c0=S.G.candies; S.giveCandy(); if(S.G.candies<c0) st.candy++; busy=0.6/SK; } continue; } }
      // 2) compro caramelle se ho karma e la bancarella è vicina
      if(S.G.candies===0 && S.G.karma>=S.CANDY_PRICE+10){ let b=null,bd=1e9; for(const [x,z] of S.CANDY_STALLS){ const d=Math.hypot(x-P.x,z-P.z); if(d<bd){ bd=d; b={x,z}; } } if(b && bd<35){ if(goTo(b)){ const n=Math.min(S.CANDY_MAX,Math.floor((S.G.karma-10)/S.CANDY_PRICE)); S.G.karma-=n*S.CANDY_PRICE; S.G.candies+=n; st.buy+=n; busy=1; } continue; } }
      // 3) curo il malato più vicino (prima il focolaio) con la cura giusta se ho cariche
      let best=null,bd=1e9; const T=S.TGT; for(const p of S.PEDS){ if(!p.kind||p.ko>0||p.fly||p.goto||p.gone) continue; const id=Object.keys(S.CURE).find(k=>S.CURE[k].k===p.kind); if(S.G.ch[id]<=0) continue; let d=D(p,P); if(T&&T.zone&&!(p.x>T.zone.x0&&p.x<T.zone.x1&&p.z>T.zone.z0&&p.z<T.zone.z1)) d+=25; if(d<bd){ bd=d; best=p; } }
      if(!best){ busy=0.5; continue; }
      if(goTo(best)){ S.player.focusPed=best; const id=Object.keys(S.CURE).find(k=>S.CURE[k].k===best.kind); S.cure(id); st.cure++; busy=(S.CURE[id].hold?0:0.6)/SK; } }
    if(S.LEO.victims) st.leoHit=S.LEO.victims.length;
    R.push({stars:($('goStars').textContent.match(/⭐/g)||[]).length, win:/superato/.test($('goTitle').textContent), pct:Math.round(S.colorPct()*100), k:Math.round(S.G.karma-k0), maxCarriers, ...st}); }
  const avg=k=>(R.reduce((a,x)=>a+(+x[k]),0)/R.length);
  const row={liv:lv,partite:R.length,vinte:R.filter(x=>x.win).length,stelle:avg('stars').toFixed(1),colori:Math.round(avg('pct'))+'%',karma:Math.round(avg('k')),cure:Math.round(avg('cure')),caramelle:avg('candy').toFixed(1),comprate:avg('buy').toFixed(1),portatori_max:Math.round(avg('maxCarriers')),carlo:avg('carlo').toFixed(1),leo_vittime:avg('leoHit').toFixed(1)};
  out.push(row); console.log(JSON.stringify(row)); }
console.log('\n| '+Object.keys(out[0]).join(' | ')+' |'); for(const r of out) console.log('| '+Object.values(r).join(' | ')+' |');
process.exit(0);
