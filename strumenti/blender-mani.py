# Karmapolis: mani dei personaggi Quaternius sistemate in Blender (più piccole, socchiuse) e "cotte" nel modello
import bpy, sys, math, os
from mathutils import Matrix, Vector
src, dst = sys.argv[-2], sys.argv[-1]
HANDK=0.72; CURL={'Index':(0.5,0.85,0.6),'Middle':(0.55,0.9,0.6),'Ring':(0.6,0.95,0.65),'Pinky':(0.65,1.0,0.7),'Thumb':(0.45,0.35,0.3)}
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
arm=[o for o in bpy.data.objects if o.type=='ARMATURE'][0]; arm.animation_data_clear()
for pb in arm.pose.bones: pb.location=(0,0,0); pb.rotation_quaternion=(1,0,0,0); pb.rotation_euler=(0,0,0); pb.scale=(1,1,1)
bpy.context.view_layer.update()
bpy.context.view_layer.objects.active=arm; bpy.ops.object.mode_set(mode='POSE')
P=arm.pose.bones
def rot_world(pb,ang,axis):
    h=pb.head.copy(); R=Matrix.Translation(h)@Matrix.Rotation(ang,4,axis)@Matrix.Translation(-h)
    pb.matrix=R@pb.matrix; bpy.context.view_layer.update()
for s,sg in (('L',1),('R',-1)):
    w=P.get('Wrist.'+s)
    if not w: continue
    w.scale=(HANDK,HANDK,HANDK); bpy.context.view_layer.update()
    for f,angs in CURL.items():
        for i,a in enumerate(angs):
            pb=P.get(f'{f}{i+2}.{s}')
            if pb and a: rot_world(pb, a*sg, Vector((0,1,0)) if f!='Thumb' else Vector((sg,0.35,0)).normalized())
bpy.ops.object.mode_set(mode='OBJECT')
# applico la posa ai modelli e la rendo la nuova posa di riposo
for o in [o for o in bpy.data.objects if o.type=='MESH']:
    mods=[m for m in o.modifiers if m.type=='ARMATURE']
    if not mods: continue
    m=mods[0]; keep=o.modifiers.new('ArmKeep','ARMATURE'); keep.object=m.object; keep.use_vertex_groups=True
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active=o
    bpy.ops.object.modifier_apply(modifier=m.name); keep.name='Armature'
bpy.ops.object.select_all(action='DESELECT'); arm.select_set(True); bpy.context.view_layer.objects.active=arm
bpy.ops.object.mode_set(mode='POSE'); bpy.ops.pose.select_all(action='SELECT'); bpy.ops.pose.armature_apply(selected=False); bpy.ops.object.mode_set(mode='OBJECT')
os.makedirs(os.path.dirname(dst),exist_ok=True)
bpy.ops.export_scene.gltf(filepath=dst, export_format='GLTF_SEPARATE', export_animations=False, export_yup=True, export_apply=False)
print('OK',dst)
