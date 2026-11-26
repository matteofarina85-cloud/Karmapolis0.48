import bpy, bmesh, math, json, sys
from mathutils import Vector, Euler
from bpy_extras.object_utils import world_to_camera_view
MODE=sys.argv[-1]  # 'base' o 'mask'
bpy.ops.wm.read_factory_settings(use_empty=True)
sc=bpy.context.scene; C=sc.collection
W,H,D=0.075,0.155,0.0085
def mat(name,col,emit=False,rough=0.6):
    m=bpy.data.materials.new(name); m.use_nodes=True; nt=m.node_tree; nt.nodes.clear(); out=nt.nodes.new('ShaderNodeOutputMaterial')
    if emit: s=nt.nodes.new('ShaderNodeEmission'); s.inputs[0].default_value=(*col,1); s.inputs[1].default_value=1
    else: s=nt.nodes.new('ShaderNodeBsdfPrincipled'); s.inputs['Base Color'].default_value=(*col,1); s.inputs['Roughness'].default_value=rough
    nt.links.new(s.outputs[0],out.inputs[0]); return m
if MODE=='base': mBody,mScr,mDark,mSkin=mat('body',(0.86,0.88,0.9),rough=0.35),mat('scr',(0.02,0.02,0.03),rough=0.2),mat('dark',(0.05,0.05,0.06)),mat('skin',(0.85,0.85,0.85),rough=0.8)
else: k=mat('k',(0,0,0),True); mBody=mScr=mDark=k; mSkin=mat('w',(1,1,1),True)
# telefono
root=bpy.data.objects.new('phoneRoot',None); C.objects.link(root)
bpy.ops.mesh.primitive_cube_add(size=1); ph=bpy.context.object; ph.scale=(W,D,H); bpy.ops.object.transform_apply(scale=True)
bv=ph.modifiers.new('b','BEVEL'); bv.width=0.009; bv.segments=8; ph.data.materials.append(mBody); bpy.ops.object.shade_smooth(); ph.parent=root
bpy.ops.mesh.primitive_plane_add(size=1); sc_=bpy.context.object; sc_.name='Screen'; sc_.scale=(W-0.008,H-0.03,1); sc_.rotation_euler=(math.pi/2,0,0); sc_.location=(0,-D/2-0.0004,-0.001); sc_.data.materials.append(mScr); sc_.parent=root
for (x,z,sx,sz) in [(0,H/2-0.0085,0.016,0.0022),(0.0,-H/2+0.008,0.012,0.0022)]:
    bpy.ops.mesh.primitive_cube_add(size=1); o=bpy.context.object; o.scale=(sx,0.001,sz); o.location=(x,-D/2-0.0003,z); o.data.materials.append(mDark); o.parent=root
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.0018); o=bpy.context.object; o.location=(0.013,-D/2-0.0003,H/2-0.0085); o.data.materials.append(mDark); o.parent=root
# mano destra: tubi (curve) uniti e rifusi
parts=[]
def tube(pts,r,taper=1.0):
    cu=bpy.data.curves.new('c','CURVE'); cu.dimensions='3D'; cu.bevel_depth=r; cu.bevel_resolution=6; cu.use_fill_caps=True
    sp=cu.splines.new('NURBS'); sp.points.add(len(pts)-1)
    for i,p in enumerate(pts): sp.points[i].co=(*p,1); sp.points[i].radius=1.0+(taper-1.0)*i/(len(pts)-1)
    sp.use_endpoint_u=True; sp.order_u=min(4,len(pts))
    o=bpy.data.objects.new('t',cu); C.objects.link(o); parts.append(o); return o
def blob(loc,scale,rot=(0,0,0)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1,location=loc,rotation=rot); o=bpy.context.object; o.scale=scale; parts.append(o); return o
X=W/2
# palmo dietro, in basso a destra, che esce in basso
blob((0.030,0.028,-0.070),(0.042,0.020,0.055),(0.0,-0.35,0))
blob((0.050,0.030,-0.125),(0.034,0.026,0.06),(0.0,-0.4,0))   # verso il polso
tube([(0.060,0.032,-0.12),(0.075,0.035,-0.20),(0.09,0.04,-0.30)],0.030)  # polso, fuori inquadratura
# pollice: dal palmo sale davanti sul bordo destro
tube([(0.060,0.020,-0.115),(0.050,0.004,-0.085),(0.0435,-0.0035,-0.050),(0.0415,-0.0055,-0.018),(0.0395,-0.0060,0.004)],0.0105,0.8)
# dita dietro che girano attorno al bordo sinistro (si vedono le punte)
for z,r in [(-0.006,0.0092),(-0.028,0.0096),(-0.050,0.0092),(-0.071,0.0082)]:
    tube([(0.022,0.026,z-0.012),(-0.012,0.019,z-0.005),(-X-0.007,0.009,z),(-X-0.006,-0.004,z+0.002),(-X+0.004,-0.0095,z+0.004)],r,0.88)
    blob((-X+0.004,-0.0095,z+0.004),(r*0.86,r*0.86,r*0.86))
blob((0.0395,-0.0060,0.004),(0.0084,0.0084,0.0084))
# converto e unisco
bpy.ops.object.select_all(action='DESELECT')
for o in parts:
    o.select_set(True)
bpy.context.view_layer.objects.active=parts[0]
bpy.ops.object.convert(target='MESH')
bpy.ops.object.join(); hand=bpy.context.object; hand.name='Hand'; bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
rm=hand.modifiers.new('r','REMESH'); rm.mode='VOXEL'; rm.voxel_size=0.002
sm=hand.modifiers.new('s','SMOOTH'); sm.iterations=6; sm.factor=0.8
dc=hand.modifiers.new('d','DECIMATE'); dc.ratio=0.25
hand.data.materials.clear(); hand.data.materials.append(mSkin); bpy.ops.object.shade_smooth(); hand.parent=root
# posa del telefono: inclinato come nella foto di GTA
root.rotation_euler=(math.radians(-14),math.radians(9),math.radians(-7))
# camera
cam=bpy.data.objects.new('cam',bpy.data.cameras.new('cam')); C.objects.link(cam); sc.camera=cam; cam.data.lens=38
cam.location=(0.012,-0.30,-0.005); cam.rotation_euler=(math.radians(84),0,0)
sc.render.resolution_x=900; sc.render.resolution_y=1150; sc.render.film_transparent=True
sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=32 if MODE=='base' else 4; sc.cycles.use_denoising=False
w=bpy.data.worlds.new('w'); sc.world=w; w.use_nodes=True; bg=w.node_tree.nodes['Background']; bg.inputs[0].default_value=(1,1,1,1); bg.inputs[1].default_value=0.55 if MODE=='base' else 0
if MODE=='base':
    L=bpy.data.objects.new('sun',bpy.data.lights.new('sun','SUN')); L.data.energy=3.2; L.data.angle=0.2; L.rotation_euler=(math.radians(55),math.radians(-25),math.radians(-30)); C.objects.link(L)
    pass # sc.render.line_thickness_mode='ABSOLUTE'; sc.render.line_thickness=3.2
    #ls=sc.view_layers[0].freestyle_settings.linesets[0] if sc.view_layers[0].freestyle_settings.linesets else sc.view_layers[0].freestyle_settings.linesets.new('ls')
    #ls.linestyle.color=(0.165,0.133,0.2); ls.select_by_visibility=True; ls.select_crease=False; ls.select_border=True; ls.select_silhouette=True
sc.view_settings.view_transform='Standard'
dg=bpy.context.evaluated_depsgraph_get(); print('VERTS',len(hand.evaluated_get(dg).data.vertices),flush=True)
if MODE=='dry': raise SystemExit
sc.render.filepath=f'/home/claude/bl/hand/{MODE}.png'; bpy.ops.render.render(write_still=True)
# angoli dello schermo in pixel
bpy.context.view_layer.update(); mw=sc_.matrix_world; cs=[]
for lx,ly in [(-0.5,0.5),(0.5,0.5),(0.5,-0.5),(-0.5,-0.5)]:
    v=world_to_camera_view(sc,cam,mw@Vector((lx,ly,0)))
    cs.append([round(v.x*sc.render.resolution_x,1),round((1-v.y)*sc.render.resolution_y,1)])
json.dump({'w':sc.render.resolution_x,'h':sc.render.resolution_y,'corners':cs},open('/home/claude/bl/hand/corners.json','w')); print('CORNERS',cs)
