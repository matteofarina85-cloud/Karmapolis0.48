from PIL import Image, ImageFilter, ImageChops
import numpy as np, json, os
a=Image.open('hand/base.png').convert('RGBA'); m=Image.open('hand/mask.png').convert('L')
A=np.array(a).astype(np.float32); M=np.array(m)>127; alpha=A[...,3]>8
L=(A[...,0]*0.3+A[...,1]*0.59+A[...,2]*0.11)/255
band=np.where(L>0.78,1.0,np.where(L>0.56,0.84,0.68))
for c in range(3): A[...,c]=np.where(M,band*255,A[...,c])
def edge(mask,r):
    im=Image.fromarray((mask*255).astype(np.uint8)); d=np.array(im.filter(ImageFilter.MaxFilter(r)))>127; e=np.array(im.filter(ImageFilter.MinFilter(r)))>127; return d&~e
ink=np.array([42,34,51],np.float32); E=edge(alpha,7)|edge(M,5)
Ef=np.array(Image.fromarray((E*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.9))).astype(np.float32)/255
for c in range(3): A[...,c]=A[...,c]*(1-Ef)+ink[c]*Ef
A[...,3]=np.maximum(A[...,3],Ef*255)
out=Image.fromarray(A.clip(0,255).astype(np.uint8),'RGBA')
Mi=Image.fromarray(((M&~E)*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8))
W=720; H=round(1150*W/900); out=out.resize((W,H),Image.LANCZOS); Mi=Mi.resize((W,H),Image.LANCZOS)
out.save('hand/telefono-mano.webp',quality=88,method=6); mk=Image.new('LA',(W,H)); mk.putalpha(Mi); mk.save('hand/mano-maschera.png',optimize=True)
c=json.load(open('hand/corners.json')); print([[round(x*W/900,2),round(y*W/900,2)] for x,y in c['corners']])
prev=Image.new('RGB',(W,H),(120,140,170)); prev.paste(out,(0,0),out); sk=Image.new('RGB',(W,H),(217,162,122)); mul=ImageChops.multiply(prev,sk); prev.paste(mul,(0,0),Mi); prev.resize((360,round(H/2))).save('/tmp/hand_cel.png')
