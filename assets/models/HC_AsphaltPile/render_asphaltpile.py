"""Blender preview: blender -b -P render_asphaltpile.py -- <out_dir> <tag>
File space (x right, y up, z asphaltpile front) -> Blender (x, -z, y): a pure rotation, so the front = -Y (Blender 'front view' side)."""
import bpy, sys, json, math
from mathutils import Vector
OD, TAG = sys.argv[sys.argv.index('--') + 1:][:2]
d = json.load(open(OD + '/asphaltpile_preview.json'))
bpy.ops.wm.read_factory_settings(use_empty=True)
verts = [(p[0], -p[2], p[1]) for p in d['pos']]
faces = [tuple(t) for t in d['tri']]
me = bpy.data.meshes.new('asphaltpile'); me.from_pydata(verts, [], faces); me.update()
uvl = me.uv_layers.new(name='uv')
for poly in me.polygons:
    for li in poly.loop_indices:
        uvl.data[li].uv = d['uv'][me.loops[li].vertex_index]
ob = bpy.data.objects.new('asphaltpile', me); bpy.context.scene.collection.objects.link(ob)
for p in me.polygons: p.use_smooth = True
m = bpy.data.materials.new('v'); m.use_nodes = True
t = m.node_tree.nodes.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(OD + '/HC_AsphaltPile_BM.png')
t.interpolation = 'Linear'
m.node_tree.links.new(t.outputs['Color'], m.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
me.materials.append(m)
# asphalt ground so the prop reads against something
gm = bpy.data.meshes.new('ground')
gm.from_pydata([(-5, -5, -0.002), (5, -5, -0.002), (5, 5, -0.002), (-5, 5, -0.002)], [], [(0, 1, 2, 3)])
go = bpy.data.objects.new('ground', gm); bpy.context.scene.collection.objects.link(go)
mat = bpy.data.materials.new('g'); mat.diffuse_color = (0.42, 0.36, 0.27, 1); gm.materials.append(mat)
sc = bpy.context.scene
sc.render.engine = 'BLENDER_WORKBENCH'
sc.display.shading.light = 'STUDIO'; sc.display.shading.color_type = 'TEXTURE'
sc.display.shading.show_cavity = False
sc.render.resolution_x = 1100; sc.render.resolution_y = 800
sc.world = bpy.data.worlds.new('w'); sc.world.color = (0.55, 0.62, 0.72)
sc.view_settings.view_transform = 'Standard'
ctr = Vector((0, 0, 0.8))


def shot(name, direction, ortho, scale):
    direction = Vector(direction).normalized()
    cam_data = bpy.data.cameras.new(name); cam = bpy.data.objects.new(name, cam_data)
    sc.collection.objects.link(cam)
    cam.location = ctr + direction * 8
    cam.rotation_euler = (ctr - cam.location).to_track_quat('-Z', 'Y').to_euler()
    if ortho:
        cam_data.type = 'ORTHO'; cam_data.ortho_scale = scale
    else:
        cam_data.type = 'PERSP'; cam_data.lens = 50; cam.location = ctr + direction * scale
        cam.rotation_euler = (ctr - cam.location).to_track_quat('-Z', 'Y').to_euler()
    sc.camera = cam
    sc.render.filepath = '%s/preview_%s_%s.png' % (OD, name, TAG)
    bpy.ops.render.render(write_still=True)


# Blender dirs: front = -Y, right (+x) = +X, up = +Z
shot('front', (0, -1, 0.05), True, 5.2)
shot('side', (1, 0, 0.05), True, 5.2)
shot('threeq', (0.9, -1.0, 0.62), False, 7.6)
shot('threeq_left', (-0.9, -1.0, 0.55), False, 7.6)
shot('threeq_rear', (-0.8, 1.0, 0.5), False, 7.0)
shot('bg3', (0.8, -1, 1.65), True, 3.6)
shot('top', (0, 0, 1), True, 5.4)
