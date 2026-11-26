# Karmapolis: carrozzerie delle auto modellate in Blender (ispirate a forme vere: berlina, utilitaria tonda, station wagon, SUV squadrato, coupé sportiva, furgone)
# Coordinate di gioco: x larghezza, y su, z avanti. Le misure seguono CARTYPES del gioco (fisica invariata).
import bpy, bmesh, math, json, sys, struct
from mathutils import Vector
OUT='/home/claude/bl/auto/'
T={ # L,W,H, belt, nose(h davanti), zw (base parabrezza da davanti), roofF, roofR (da davanti), zc (base lunotto da davanti), trunkH, tumble, ax, wr, round
 'berlina': dict(L=4.4,W=1.78,H=1.42,belt=0.92,nose=0.70,zw=1.30,r0=1.95,r1=3.05,zc=3.70,trunk=0.98,tum=0.24,ax=(0.78,0.75),wr=0.33,rnd=0.55),
 'citycar': dict(L=3.6,W=1.62,H=1.5,belt=0.95,nose=0.74,zw=0.85,r0=1.45,r1=2.95,zc=3.35,trunk=None,tum=0.22,ax=(0.62,0.55),wr=0.31,rnd=0.75),
 'wagon':   dict(L=4.6,W=1.8,H=1.5,belt=0.95,nose=0.70,zw=1.25,r0=1.90,r1=4.05,zc=4.40,trunk=None,tum=0.22,ax=(0.78,0.75),wr=0.33,rnd=0.5),
 'suv':     dict(L=4.6,W=1.92,H=1.78,belt=1.08,nose=0.92,zw=1.15,r0=1.75,r1=4.05,zc=4.38,trunk=None,tum=0.16,ax=(0.85,0.8),wr=0.39,rnd=0.3),
 'sportiva':dict(L=4.35,W=1.9,H=1.16,belt=0.74,nose=0.52,zw=1.55,r0=2.25,r1=2.70,zc=3.75,trunk=0.80,tum=0.26,ax=(0.8,0.82),wr=0.34,rnd=0.6),
 'furgone': dict(L=4.95,W=1.98,H=2.2,belt=1.18,nose=1.00,zw=0.55,r0=1.10,r1=4.85,zc=4.90,trunk=None,tum=0.08,ax=(0.75,0.7),wr=0.36,rnd=0.25)}
MATS=['paint','glass','trim','chrome','head','tail','grille']
def smooth(a,b,t): t=max(0,min(1,t)); return a+(b-a)*t*t*(3-2*t)
def topY(P,d):  # d = distanza dal muso (0 davanti, L dietro)
    L,H,belt=P['L'],P['H'],P['belt']; tr=P['trunk'] if P['trunk'] is not None else None
    if d<0.18: return smooth(P['nose']-0.22,P['nose'],d/0.18)
    if d<P['zw']: return smooth(P['nose'],belt+0.05,(d-0.18)/(P['zw']-0.18))
    if d<P['r0']: return smooth(belt+0.05,H,(d-P['zw'])/(P['r0']-P['zw'])*1.0)
    if d<P['r1']: return H+0.02*math.sin(math.pi*(d-P['r0'])/(P['r1']-P['r0']))
    if tr is None:  # coda tronca (utilitaria, wagon, SUV, furgone)
        if d<L-0.05: return smooth(H,H-0.10,(d-P['r1'])/max(0.05,(L-0.05-P['r1'])))
        return H-0.1-(d-(L-0.05))*4
    if d<P['zc']: return smooth(H,tr,(d-P['r1'])/(P['zc']-P['r1']))
    if d<L-0.12: return tr+0.02
    return smooth(tr+0.02,tr-0.25,(d-(L-0.12))/0.12)
def botY(P,d):
    y=0.28; wr=P['wr']
    for c in (P['ax'][0],P['L']-P['ax'][1]):
        k=abs(d-c)/(wr+0.14)
        if k<1: y=max(y,0.28+(2*wr+0.04-0.28)*math.sqrt(max(0,1-k*k)))
    if d<0.12: y=smooth(0.45,0.30,d/0.12)
    if d>P['L']-0.12: y=smooth(0.30,0.45,(d-(P['L']-0.12))/0.12)
    return y
def ring(P,d,end=1.0):
    W=P['W']; hw=W/2*end; belt=P['belt']; top=min(topY(P,d),belt+0.03); bot=botY(P,d)
    mid=min(belt-0.12,max(bot+0.06,belt-0.3)); bl=top-0.05
    return [(0,bot),(hw-0.14,bot),(hw-0.03,bot+0.05),(hw,mid),(hw-0.012,bl),(hw-0.09*end,top-0.012),(hw*0.45,top),(0.0,top)]
def loft(name,rings,closed_ends=True,sub=1):
    bm=bmesh.new(); V=[[bm.verts.new(p) for p in r] for r in rings]; m=len(V[0])
    for i in range(len(V)-1):
        for j in range(m-1): bm.faces.new((V[i][j],V[i][j+1],V[i+1][j+1],V[i+1][j]))
        bm.faces.new((V[i][m-1],V[i][0],V[i+1][0],V[i+1][m-1]))
    if closed_ends: bm.faces.new(list(reversed(V[0]))); bm.faces.new(V[-1])
    me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); ob=bpy.data.objects.new(name,me); bpy.context.scene.collection.objects.link(ob)
    bpy.ops.object.select_all(action='DESELECT'); bpy.context.view_layer.objects.active=ob; ob.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.mesh.normals_make_consistent(inside=False); bpy.ops.object.mode_set(mode='OBJECT')
    if sub: sd=ob.modifiers.new('sd','SUBSURF'); sd.levels=sub; bpy.ops.object.modifier_apply(modifier='sd')
    return ob
def stations(a,b,step):
    n=max(2,int((b-a)/step)); return [a+(b-a)*i/n for i in range(n+1)]
def build(name,P,lod='hi'):
    HI=lod=='hi'; L=P['L']; ds=[0.0,0.03]+stations(0.0,L,0.12 if HI else 0.14)[1:-1]+[L-0.03,L]
    rings=[]
    for d in ds:
        e=0.9 if d<=0.0 or d>=L else (0.96 if d<0.05 or d>L-0.05 else 1.0)
        pts=ring(P,d,e); z=L/2-d
        full=[(-x,y) for (x,y) in reversed(pts[1:])]+pts
        rings.append([(x,y,z) for (x,y) in full])
    body=loft(name+'_body',rings,True,1 if HI else 0)
    # abitacolo: parabrezza, finestrini, lunotto e tetto (spigoli netti, un po' smussati)
    W=P['W']; belt=P['belt']; wb=W/2-0.07; wt=W/2-P['tum']
    cr=[]
    for d in stations(P['zw']-0.04,P['zc']+0.02,0.1 if HI else 0.16):
        top=max(belt+0.02,topY(P,d)); z=L/2-d
        cr.append([(-wb,belt-0.03,z),(wb,belt-0.03,z),(wt,top,z),(0,top+0.012,z),(-wt,top,z)])
    cab=loft(name+'_cab',cr,True,0)
    bv=cab.modifiers.new('bv','BEVEL'); bv.width=0.025; bv.segments=1; bpy.ops.object.modifier_apply(modifier='bv')
    parts=[(body,'body'),(cab,'cab')]
    # fari, fanali, griglia, paraurti, specchietti (pezzi separati, forme pulite)
    def box(nm,loc,size,bev=0.03,rot=(0,0,0),k='trim'):
        bpy.ops.mesh.primitive_cube_add(size=1,location=loc,rotation=rot); o=bpy.context.object; o.name=nm; o.scale=size; bpy.ops.object.transform_apply(scale=True,rotation=True,location=True)
        if bev: m=o.modifiers.new('b','BEVEL'); m.width=bev; m.segments=2 if HI else 1; bpy.ops.object.modifier_apply(modifier='b')
        parts.append((o,k)); return o
    zf=L/2; zb=-L/2; hy=P['nose']-0.13
    for s in (-1,1):
        box('head',(s*(W/2-0.3),hy,zf-0.06),(0.36,0.14,0.14),0.05,(0.18,0,0),'head')
        box('tail',(s*(W/2-0.22),belt-0.13,zb+0.05),(0.36,0.13,0.1),0.035,(0,0,0),'tail')
        box('mirror',(s*(W/2+0.06),belt+0.12,zf-P['zw']-0.15),(0.1,0.1,0.2),0.03,(0,0,0),'paint')
        box('skirt',(s*(W/2-0.01),0.33,0.0),(0.05,0.1,L-2*max(P['ax'])-0.5),0.02,(0,0,0),'trim')
        box('handle',(s*(W/2+0.005),belt-0.06,zf-P['zw']-0.65),(0.03,0.04,0.18),0.012,(0,0,0),'chrome')
    box('grille',(0,hy-0.06,zf-0.03),(W*0.42,0.16,0.08),0.03,(0.18,0,0),'grille')
    box('bumpF',(0,0.42,zf-0.07),(W-0.06,0.18,0.18),0.06,(0,0,0),'trim')
    box('bumpR',(0,0.44,zb+0.07),(W-0.06,0.18,0.18),0.06,(0,0,0),'trim')
    box('plateR',(0,belt-0.33,zb+0.01),(0.42,0.11,0.03),0.01,(0,0,0),'chrome')
    return parts
def assign_parts(parts,P):
    out=[]
    for ob,kind in parts:
        me=ob.data; res=[]
        for f in me.polygons:
            if kind=='cab':
                k='paint' if f.normal.y>0.8 else 'glass'
                c=f.center; L=P['L']; d=L/2-c.z; bz=(P['r0']+P['r1'])/2+0.1
                if abs(f.normal.x)>0.5:
                    if d<P['zw']+(P['r0']-P['zw'])*0.5 or d>P['r1']+(P['zc']-P['r1'])*0.6: k='paint'   # montanti anteriori e posteriori
                    if abs(d-bz)<0.06 and L>3.8: k='paint'                    # montante centrale
                    if c.y<P['belt']+0.05: k='paint'
            elif kind=='body': k='paint'
            else: k=kind
            res.append(MATS.index(k))
        out.append((ob,res))
    return out
def export(parts,name,P):
    pos=[];nor=[];mat=[];idx=[]
    for ob,mi in parts:
        me=ob.data; me.calc_loop_triangles(); key={}
        sm=ob.name.endswith('_body')
        for t in me.loop_triangles:
            k=mi[t.polygon_index]; fn=me.polygons[t.polygon_index].normal
            for vi in t.vertices:
                kk=(vi,k) if sm else (vi,k,t.polygon_index)
                if kk not in key:
                    key[kk]=len(mat); v=me.vertices[vi].co; nn=me.vertices[vi].normal if sm else fn
                    pos+=[round(v.x,4),round(v.y,4),round(v.z,4)]; nor+=[max(-127,min(127,round(c*127))) for c in nn]; mat.append(k)
                idx.append(key[kk])
    return {'n':len(mat),'pos':pos,'nor':nor,'mat':mat,'ind':idx}
def mirrors(P):  # specchietti: piccoli volumi in cima alla portiera
    out=[]; zf=P['L']/2-P['zw']-0.18; y=P['belt']+0.13
    for s in (-1,1): out.append((s*(P['W']/2+0.07),y,zf))
    return out
bpy.ops.wm.read_factory_settings(use_empty=True)
DATA={'mats':MATS,'cars':{}}; BIN=bytearray()
def push(arr,fmt):
    global BIN
    while len(BIN)%4: BIN+=b'\0'
    o=len(BIN); BIN+=struct.pack('<%d%s'%(len(arr),fmt),*arr); return [o,len(arr)]
for name,P in T.items():
  for lod in ('hi','lo'):
    parts=build(name,P,lod); ap=assign_parts(parts,P); e=export(ap,name,P)
    DATA['cars'][name+('' if lod=='hi' else '_lo')]={'n':e['n'],'pos':push([int(round(v*1000)) for v in e['pos']],'h'),'nor':push(e['nor'],'b'),'mat':push(e['mat'],'B'),'ind':push(e['ind'],'H' if e['n']<65535 else 'I'),'i32':e['n']>=65535,'tris':len(e['ind'])//3}
    print('AUTO',name,lod,e['n'],'vertici',len(e['ind'])//3,'triangoli',flush=True)
    [setattr(o,'name','car_'+name+'_'+lod+'_'+o.name) for o,_ in parts]
json.dump(DATA,open(OUT+'auto.json','w')); open(OUT+'auto.bin','wb').write(BIN); print('BIN',len(BIN))
bpy.ops.wm.save_as_mainfile(filepath=OUT+'auto.blend')
