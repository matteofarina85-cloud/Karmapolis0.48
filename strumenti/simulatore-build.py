import re,sys
s=open('/home/claude/karmapolis0.48/index.html',encoding='utf-8').read()
body=s[s.index('<body>')+6:s.index('<script>/* se qualcosa')]
open('body.html','w').write(body)
mod=re.search(r'<script type="module">(.*?)</script>',s,re.S).group(1)
mod=mod.replace("from 'three';","from './"+__import__('os').environ.get('SHIM','three-shim.mjs')+"';").replace("from 'three/addons/","from 'three/examples/jsm/")
mod=mod.replace("qhLoad('teste/')","Promise.resolve()") # nel simulatore le teste vecchie non servono (le persone sono UM) e il loro caricamento resta appeso
open('game.mjs','w').write(mod)
open('game.mjs','a').write("\nwindow.__sim={PEDS,player,cure,giveCandy,G,ACT,gCell,KINDS,KI,CURE,LV,colorPct,get LC(){return LC;},get ACTZ(){return ACTZ;},get TGT(){return TGT;},get gameOver(){return gameOver;},CANDY_STALLS,CANDY_PRICE,CANDY_MAX,LEO,CARLO,callCarlo,carloAvail};\n")
