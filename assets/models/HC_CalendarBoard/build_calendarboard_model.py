"""Meshy AI text-to-3D GLB -> fire-basket DAE; Y up, metres, +Z front.
Usage: build_calendarboard_model.py template.dae output.dae output_directory
"""
import sys, struct, json, re
sys.dont_write_bytecode = True
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'HC_PortaPotty'))
import portapotty_paint as paint_mod
TPL, OUT, OD = sys.argv[1:4]
source = Path(__file__).resolve().parents[2] / 'meshy/calendarboard'
raw = (source / 'model.glb').read_bytes()
magic, version, length = struct.unpack_from('<III', raw)
assert magic == 0x46546c67 and version == 2 and length == len(raw)
offset = 12
while offset < len(raw):
    size, kind = struct.unpack_from('<II', raw, offset); offset += 8
    chunk = raw[offset:offset+size]; offset += size
    if kind == 0x4e4f534a: doc = json.loads(chunk)
    elif kind == 0x004e4942: binary = chunk

def accessor(index):
    a = doc['accessors'][index]; v = doc['bufferViews'][a['bufferView']]
    assert 'sparse' not in a and v.get('buffer', 0) == 0
    dtype = np.dtype({5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1'}[a['componentType']])
    width = {'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']]
    start = v.get('byteOffset',0) + a.get('byteOffset',0)
    return np.ndarray((a['count'], width), dtype=dtype, buffer=binary, offset=start,
                      strides=(v.get('byteStride', width*dtype.itemsize), dtype.itemsize)).copy()
assert len(doc['meshes']) == 1
primitive = doc['meshes'][0]['primitives'][0]
assert len(doc['meshes'][0]['primitives']) == 1 and primitive.get('mode',4) == 4
# Meshy exports a single identity mesh node; reject transforms rather than silently dropping them.
for node in doc.get('nodes',[]):
    if 'mesh' in node:
        assert np.allclose(np.array(node.get('matrix', np.eye(4).ravel())).reshape(4,4), np.eye(4)) and node.get('translation',[0,0,0]) == [0,0,0]
        assert node.get('scale',[1,1,1]) == [1,1,1] and node.get('rotation',[0,0,0,1]) == [0,0,0,1]
a = primitive['attributes']
pos = accessor(a['POSITION']).astype(float); nor = accessor(a['NORMAL']).astype(float)
uv = accessor(a['TEXCOORD_0']).astype(float); uv[:,1] = 1 - uv[:,1]
tri = accessor(primitive['indices']).reshape(-1,3).astype(int)
# Uniform scale to 1.6 m high; preserve Meshy's aspect ratio.
original_min, original_max = pos.min(0), pos.max(0)
scale = 1.9 / (original_max[1] - original_min[1])
pos *= scale
# Rotate about Y only if preview review requires it; rotate normals together.
angle = np.deg2rad(0.0)
rotation = np.array([[np.cos(angle),0,np.sin(angle)],[0,1,0],[-np.sin(angle),0,np.cos(angle)]])
pos = pos @ rotation.T
nor = nor @ rotation.T
print('source bounds', original_min, original_max, 'uniform scale', scale)
# Front orientation is verified against Blender front/rear previews.
pos -= np.array([(pos[:,0].min()+pos[:,0].max())/2, pos[:,1].min(), (pos[:,2].min()+pos[:,2].max())/2])
Path(OD).mkdir(parents=True, exist_ok=True)
bm = Image.open(source/'texture0_base_color.png').convert('RGB').resize((1024,1024), Image.Resampling.LANCZOS)
bm.save(OD+'/HC_CalendarBoard_BM.png')
rough = np.asarray(Image.open(source/'texture0_roughness.png').convert('L').resize((1024,1024), Image.Resampling.BILINEAR), dtype=float)/255
paint_mod.nm_image().save(OD+'/HC_CalendarBoard_NM.png')
paint_mod.pm_image(rough).save(OD+'/HC_CalendarBoard_PM.png')
# ----------------------------------------------------------------------------- finish

bmin, bmax = pos.min(0), pos.max(0)
print('verts', len(pos), 'tris', len(tri), 'bbox min', bmin.round(3), 'max', bmax.round(3), 'size', (bmax - bmin).round(3))
assert len(tri) < 8000, 'triangle budget exceeded'
json.dump({'pos': pos.tolist(), 'uv': uv.tolist(), 'tri': tri.tolist(), 'nor': nor.tolist()}, open(OD + '/calendarboard_preview.json', 'w'))
json.dump({'min': bmin.tolist(), 'max': bmax.tolist(), 'tris': int(len(tri))}, open(OD + '/calendarboard_bounds.json', 'w'))

# DAE triangles: right-hand normal opposite to vertex normal (see module doc)
dtri = tri[:, [0, 2, 1]]


def nz(v):
    l = np.linalg.norm(v, axis=-1, keepdims=True); l[l < 1e-12] = 1; return v / l


nor = nz(nor)
p0, p1, p2 = pos[dtri[:, 0]], pos[dtri[:, 1]], pos[dtri[:, 2]]
u0, u1, u2 = uv[dtri[:, 0]], uv[dtri[:, 1]], uv[dtri[:, 2]]
e1, e2 = p1 - p0, p2 - p0; d1, d2 = u1 - u0, u2 - u0
den = d1[:, 0] * d2[:, 1] - d2[:, 0] * d1[:, 1]; den[np.abs(den) < 1e-12] = 1
tang = (e1 * d2[:, 1:2] - e2 * d1[:, 1:2]) / den[:, None]
CP, CN, CT, CB, CU = [], [], [], [], []
for ti in range(len(dtri)):
    for k in range(3):
        v = dtri[ti, k]; n = nor[v]; t = tang[ti] - n * (n @ tang[ti])
        if np.linalg.norm(t) < 1e-7:
            t = np.cross(n, [0, 1, 0]); t = t if np.linalg.norm(t) > 1e-7 else np.array([1., 0, 0])
        t = t / np.linalg.norm(t)
        CP.append(pos[v]); CN.append(n); CT.append(t); CB.append(np.cross(n, t)); CU.append(uv[v])
CP, CN, CT, CB, CU = [np.array(x) for x in (CP, CN, CT, CB, CU)]
key = np.round(np.concatenate([CP, CN, CT, CB, CU], 1), 6)
_, first, inv = np.unique(key, axis=0, return_index=True, return_inverse=True); inv = inv.reshape(-1)
CP, CN, CT, CB, CU = [x[first] for x in (CP, CN, CT, CB, CU)]; count = len(CP)
print('unique DAE corner vertices', count)

s = open(TPL, encoding='utf-8-sig').read()
fmt = lambda a: ' '.join('%.6f' % x for x in a.ravel())
pidx = ' '.join('%d %d %d %d %d' % (i, i, i, i, i) for i in inv)
for name in ['LTS_GEN_Fire_Basket_A_Mesh', 'LTS_GEN_Fire_Basket_A_Mesh_LOD1', 'LTS_GEN_Fire_Basket_A_Mesh_LOD2']:
    a = s.index('<geometry id="%s-geom"' % name); b = s.index('</geometry>', a); g = s[a:b]
    for key_, arr in [('positions', CP), ('normals', CN), ('tangents', CT), ('binormals', CB), ('uvs0', CU)]:
        g, n_ = re.subn(r'(<float_array id="%s-%s-array" count=")\d+(">)[^<]*(</float_array>)' % (name, key_),
                        lambda m: m.group(1) + str(arr.size) + m.group(2) + fmt(arr) + m.group(3), g); assert n_ == 1
        g, n_ = re.subn(r'(<accessor count=")\d+(" source="#%s-%s-array")' % (name, key_),
                        lambda m: m.group(1) + str(count) + m.group(2), g); assert n_ == 1
    g, n_ = re.subn(r'<triangles count="\d+">', '<triangles count="%d">' % len(dtri), g); assert n_ == 1
    g, n_ = re.subn(r'(<triangles[^>]*>.*?<p>)[^<]*(</p>)', lambda m: m.group(1) + pidx + m.group(2), g, flags=re.S); assert n_ == 1
    s = s[:a] + g + s[b:]
open(OUT, 'w', encoding='utf-8').write(s)
print('wrote', OUT)

