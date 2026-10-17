"""Procedural Caltrans 'LANE CLOSED AHEAD' Type III barricade, written into the fire-basket template DAE (all 3 LODs).

AI-generated asset (procedural Python geometry and textures; no vanilla art is reused).
usage: build_barricade_model.py <basket_template.dae> <out.dae> <out_dir>
Units metres. Origin at ground centre, +Z = front (the side the sheeting faces), +Y up, X = width.
Orange/white striped plastic Type III barricade: three slat boards on two posts, rear and front stabiliser braces, foot
bars with a sandbag draped over each, two traffic cones with reflective collars in front, and a flashing amber lamp on top.
Writes <out_dir>/HC_Barricade_BM.png, _NM.png, _PM.png, barricade_preview.json (Blender previews) and barricade_bounds.json.
Pipeline (see HANDOFF.md / hc_tarp.py): this script -> out.dae; then, with absolute paths,
  Divine.exe -g bg3 -a convert-model -s out.dae -d HC_Barricade.GR2 -i dae -o gr2 -e conform --conform-path <vanilla LTS_GEN_Fire_Basket_A.GR2> -l warn
  texconv.exe -nologo -y -f BC3_UNORM -m 0 -o <dir> <png>   (rename the results to .DDS)
Winding convention follows build_tarp_model.py: the right-hand normal of each DAE triangle points opposite to the
vertex normal (BG3 mirrors the DAE); internally triangles are stored outward-CCW.
"""
import sys, re, json, math
import numpy as np
sys.path.insert(0, __file__.replace('\\', '/').rsplit('/', 1)[0])
import barricade_paint as paint_mod

TPL, OUT, OD = sys.argv[1:4]
cells, rough = paint_mod.paint(OD + '/HC_Barricade_BM.png')
paint_mod.nm_image().save(OD + '/HC_Barricade_NM.png')
paint_mod.pm_image(rough).save(OD + '/HC_Barricade_PM.png')
rng = np.random.default_rng(20261017)
ruv, cuv = paint_mod.ruv, paint_mod.uv

P, N, U, T = [], [], [], []


def V(*a):
    return np.array(a, float)


def nrm(v):
    l = np.linalg.norm(v)
    return v / l if l > 1e-12 else v


def vert(p, n, uv):
    P.append(np.array(p, float)); N.append(np.array(n, float)); U.append(uv)
    return len(P) - 1


def add_tri(a, b, c):
    """Store the triangle outward-CCW: flip if its right-hand normal disagrees with the vertex normals."""
    gn = np.cross(P[b] - P[a], P[c] - P[a])
    mn = N[a] + N[b] + N[c]
    if np.linalg.norm(gn) < 1e-12:
        return
    T.append((a, b, c) if gn @ mn >= 0 else (a, c, b))


def frame(d):
    ref = V(0, 1, 0) if abs(d[1]) < 0.9 else V(1, 0, 0)
    u = nrm(np.cross(ref, d)); v = np.cross(d, u)
    return u, v


def box(c, ax, ay, az, hx, hy, hz, uvf, faces=None):
    """Oriented, flat-shaded box. uvf(k, sg, a, b): k = local axis of the face normal (0 x, 1 y, 2 z), sg = side,
    a runs along local axis (k+1)%3 and b along (k+2)%3, both 0..1. faces limits the emitted (k, sg) pairs."""
    axes = [nrm(ax), nrm(ay), nrm(az)]; half = [hx, hy, hz]; c = np.array(c, float)
    for k in range(3):
        i, j = (k + 1) % 3, (k + 2) % 3
        for sg in (-1, 1):
            if faces is not None and (k, sg) not in faces:
                continue
            n = axes[k] * sg
            base = c + n * half[k]
            corners = []
            for si, sj in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
                p = base + axes[i] * si * half[i] + axes[j] * sj * half[j]
                corners.append(vert(p, n, uvf(k, sg, (si + 1) / 2, (sj + 1) / 2)))
            add_tri(corners[0], corners[1], corners[2]); add_tri(corners[0], corners[2], corners[3])


def cellf(name):
    cell = cells[name]
    return lambda k, sg, a, b: cuv(cell, a, b)


X, Y, Z = V(1, 0, 0), V(0, 1, 0), V(0, 0, 1)


def tube(p0, p1, r0, r1, seg, cell, caps=True):
    p0, p1 = V(*p0), V(*p1); d = p1 - p0; L = np.linalg.norm(d)
    d = d / L; u, v = frame(d)
    rings = []
    for pc, r, f in ((p0, r0, 0.0), (p1, r1, 1.0)):
        ring = []
        for k in range(seg + 1):
            a = 2 * math.pi * k / seg
            rad = u * math.cos(a) + v * math.sin(a)
            n = nrm(rad + d * (r0 - r1) / L)
            ring.append(vert(pc + rad * r, n, cuv(cell, f, k / seg)))
        rings.append(ring)
    for k in range(seg):
        a, b, c, e = rings[0][k], rings[0][k + 1], rings[1][k], rings[1][k + 1]
        add_tri(a, b, c); add_tri(b, e, c)
    if caps:
        for pc, r, sg, f in ((p0, r0, -1, 0.0), (p1, r1, 1, 1.0)):
            if r < 1e-6:
                continue
            ctr = vert(pc, d * sg, cuv(cell, f, 0.5))
            ids = []
            for k in range(seg + 1):
                a = 2 * math.pi * k / seg
                ids.append(vert(pc + (u * math.cos(a) + v * math.sin(a)) * r, d * sg, cuv(cell, f, 0.5 + 0.2 * math.sin(a))))
            for k in range(seg):
                add_tri(ctr, ids[k], ids[k + 1])


def lathe(cx, cz, yaw, profile, seg, uvf, cap_top=None, cap_bottom=None):
    """Surface of revolution about a vertical axis at (cx, cz). profile: [(radius, y, v)] bottom -> top.
    uvf(u, v) -> uv, u = 0..1 around. cap_*: palette cell name for a flat disc closing that end."""
    rings = []
    npts = len(profile)
    for idx, (r, y, v) in enumerate(profile):
        p0 = profile[max(idx - 1, 0)]; p1 = profile[min(idx + 1, npts - 1)]
        dr, dy = p1[0] - p0[0], p1[1] - p0[1]
        ring = []
        for k in range(seg + 1):
            th = yaw + 2 * math.pi * k / seg
            cs, sn = math.cos(th), math.sin(th)
            n = nrm(V(dy * cs, -dr, dy * sn))
            ring.append(vert(V(cx + r * cs, y, cz + r * sn), n, uvf(k / seg, v)))
        rings.append(ring)
    for i in range(npts - 1):
        for k in range(seg):
            a, b, c, e = rings[i][k], rings[i][k + 1], rings[i + 1][k], rings[i + 1][k + 1]
            add_tri(a, b, c); add_tri(b, e, c)
    for end, cell, sgn in ((profile[-1], cap_top, 1), (profile[0], cap_bottom, -1)):
        if cell is None:
            continue
        r, y, _ = end
        ctr = vert(V(cx, y, cz), V(0, sgn, 0), cuv(cells[cell], 0.5, 0.5))
        ids = [vert(V(cx + r * math.cos(yaw + 2 * math.pi * k / seg), y, cz + r * math.sin(yaw + 2 * math.pi * k / seg)),
                    V(0, sgn, 0), cuv(cells[cell], 0.5 + 0.3 * math.cos(2 * math.pi * k / seg), 0.5 + 0.3 * math.sin(2 * math.pi * k / seg)))
               for k in range(seg + 1)]
        for k in range(seg):
            add_tri(ctr, ids[k], ids[k + 1])


# ----------------------------------------------------------------------------- dimensions
POST_X = 1.0
RAIL_HX = 1.12
RAIL_HY = 0.085
RAIL_YC = (0.285, 0.565, 0.845)        # bottom, middle, top
FRONT_REGION = ('front2', 'front1', 'front0')
RAIL_Z0, RAIL_Z1 = 0.02, 0.05           # rails sit on the front face of the posts
POST_HZ = 0.02
FOOT_HZ = 0.31

# ----------------------------------------------------------------------------- slat boards
for yc, region in zip(RAIL_YC, FRONT_REGION):
    zc = (RAIL_Z0 + RAIL_Z1) / 2
    # plastic core (frame colour) ...
    box((0, yc, zc), X, Y, Z, RAIL_HX, RAIL_HY, (RAIL_Z1 - RAIL_Z0) / 2, cellf('orange_dark'))
    # ... with the reflective sheeting as a raised panel on each face
    box((0, yc, RAIL_Z1 + 0.0015), X, Y, Z, 1.10, 0.078, 0.0015,
        lambda k, sg, a, b, r=region: ruv(r, a, 1 - b), faces={(2, 1)})
    box((0, yc, RAIL_Z0 - 0.0015), X, Y, Z, 1.10, 0.078, 0.0015,
        lambda k, sg, a, b: ruv('back', 1 - a, 1 - b), faces={(2, -1)})


# ----------------------------------------------------------------------------- posts, braces and feet
def bar_uvf(long_axis):
    """Stripes along a bar: long_axis = local axis index (0, 1 or 2) running along the bar."""
    def f(k, sg, a, b, region='bar'):
        if k == long_axis:
            return cuv(cells['orange'], a, b)
        # the face spans the long axis plus one other axis
        i, j = (k + 1) % 3, (k + 2) % 3
        if i == long_axis:
            return ruv(region, a, b)
        if j == long_axis:
            return ruv(region, b, a)
        return cuv(cells['orange'], a, b)
    return f


def oriented_bar(p0, p1, half_w, half_t, region='bar'):
    p0, p1 = V(*p0), V(*p1)
    ay = nrm(p1 - p0); ax = X; az = nrm(np.cross(ax, ay)); ax = nrm(np.cross(ay, az))
    f = bar_uvf(1)
    box((p0 + p1) / 2, ax, ay, az, half_w, np.linalg.norm(p1 - p0) / 2, half_t, lambda k, sg, a, b: f(k, sg, a, b, region))


FOOT_UV = (lambda k, sg, a, b: ruv('foot', b, a) if k == 0 else (ruv('foot', a, b) if k == 1 else cuv(cells['orange'], a, b)))
for sx in (-1, 1):
    x = sx * POST_X
    # upright post (stripes run up it)
    box((x, 0.495, 0.0), X, Y, Z, 0.035, 0.46, POST_HZ, bar_uvf(1))
    # foot bar along Z with stripes
    box((x, 0.035, 0.0), X, Y, Z, 0.05, 0.035, FOOT_HZ, FOOT_UV)
    # rear stabiliser brace, from near the top of the post back to the end of the foot
    oriented_bar((x, 0.88, -POST_HZ - 0.016), (x, 0.07, -0.285), 0.03, 0.016)
    # front stabiliser brace, from the bottom rail down to the front of the foot
    oriented_bar((x, 0.285, RAIL_Z1 + 0.017), (x, 0.07, 0.285), 0.03, 0.016)
    # bolts through the rails and braces
    for yc in RAIL_YC:
        tube((x, yc, RAIL_Z1 + 0.003), (x, yc, RAIL_Z1 + 0.014), 0.013, 0.011, 6, cells['bolt'])

# ----------------------------------------------------------------------------- sandbags draped over the front of each foot
BAG_A, BAG_B, BAG_C = 0.19, 0.11, 0.098
BAG_Z = 0.13
NT, NP = 14, 10


def sp(v, e):
    return math.copysign(abs(v) ** e, v)


def bag_point(th, ph, jitter):
    x = BAG_A * math.sin(ph)
    r = max(math.cos(ph), 0.0) ** 0.55
    z = BAG_B * r * sp(math.cos(th), 0.78)
    y = BAG_C * r * sp(math.sin(th), 0.78)
    y = max(y, -BAG_C * 0.62)                        # flat-ish bottom
    y -= 0.028 * (x / BAG_A) ** 2                    # ends droop over the foot bar
    r_j = 1.0 + jitter
    return V(x, y * r_j, z * r_j)


def build_bag(cx, flip):
    jit = rng.normal(0, 0.03, (NP + 1, NT + 1)); jit[:, NT] = jit[:, 0]
    pts = np.zeros((NP + 1, NT + 1, 3))
    for i in range(NP + 1):
        ph = -math.pi / 2 + math.pi * i / NP
        for j in range(NT + 1):
            th = 2 * math.pi * (j % NT) / NT
            pts[i, j] = bag_point(th, ph, jit[i, j] if 0 < i < NP else 0.0)
    pts[:, :, 1] -= pts[:, :, 1].min()
    ids = np.zeros((NP + 1, NT + 1), int)
    cen = pts.reshape(-1, 3).mean(0)
    for i in range(NP + 1):
        for j in range(NT + 1):
            if i in (0, NP):
                n = V(-1 if i == 0 else 1, 0, 0)
            else:
                dth = pts[i, (j + 1) % NT] - pts[i, (j - 1) % NT]
                dph = pts[i + 1, j] - pts[i - 1, j]
                n = nrm(np.cross(dth, dph))
                if n @ (pts[i, j] - cen) < 0:
                    n = -n
            p = pts[i, j]
            world = V(cx + p[0] * flip, p[1], BAG_Z + p[2])
            n = V(n[0] * flip, n[1], n[2])
            u = 0.5 + p[0] / (2 * BAG_A) * 0.96
            v = 0.5 - p[2] / (2 * BAG_B) * 0.80
            ids[i, j] = vert(world, n, ruv('bag', min(max(u, 0), 1), min(max(v, 0), 1)))
    for i in range(NP):
        for j in range(NT):
            a, b, c, d = ids[i, j], ids[i, j + 1], ids[i + 1, j + 1], ids[i + 1, j]
            add_tri(a, b, c); add_tri(a, c, d)


build_bag(-POST_X, 1)
build_bag(POST_X, -1)

# ----------------------------------------------------------------------------- amber flashing lamp on top
LAMP_Z = (RAIL_Z0 + RAIL_Z1) / 2 + 0.012
top = RAIL_YC[2] + RAIL_HY                                  # 0.93
box((0, top + 0.01, LAMP_Z), X, Y, Z, 0.115, 0.01, 0.075, cellf('housing_blk'))
for sx in (-1, 1):
    tube((sx * 0.085, top + 0.02, LAMP_Z - 0.04), (sx * 0.085, top + 0.032, LAMP_Z - 0.04), 0.012, 0.010, 6, cells['bolt'])
    tube((sx * 0.085, top + 0.02, LAMP_Z + 0.04), (sx * 0.085, top + 0.032, LAMP_Z + 0.04), 0.012, 0.010, 6, cells['bolt'])
y0 = top + 0.02
lathe(0, LAMP_Z, 0.0, [(0.095, y0, 0), (0.095, y0 + 0.026, 1)], 16,
      lambda u, v: cuv(cells['housing_blk'], u, v), cap_bottom='housing_blk')
# amber lens: a short straight section then a dome, all on the hot 'lens' strip
lathe(0, LAMP_Z, 0.0, [(0.092, y0 + 0.026, 0), (0.092, y0 + 0.066, 1)], 16,
      lambda u, v: ruv('lens', u, 1 - 0.30 * v - 0.05))
dome = [(0.092 * math.cos(math.radians(a)), y0 + 0.066 + 0.084 * math.sin(math.radians(a)), 1.0 - a / 90.0)
        for a in (0, 20, 40, 58, 74, 90)]
lathe(0, LAMP_Z, 0.0, dome, 16, lambda u, v: ruv('lens', u, 1 - v))

# ----------------------------------------------------------------------------- traffic cones with reflective collars
CONE_H0, CONE_H1 = 0.05, 0.70
CONE_R0, CONE_R1 = 0.108, 0.028


def cone(cx, cz, yaw, lean_u):
    ax = V(math.cos(yaw), 0, -math.sin(yaw)); az = V(math.sin(yaw), 0, math.cos(yaw))
    box((cx, 0.0165, cz), ax, Y, az, 0.125, 0.0165, 0.125, cellf('rubber'))
    box((cx, 0.0425, cz), ax, Y, az, 0.108, 0.0105, 0.108, cellf('rubber_grey'))
    hs = (0.0, 0.31, 0.46, 0.60, 0.80, 1.0)
    prof = [(CONE_R0 + (CONE_R1 - CONE_R0) * h, CONE_H0 + (CONE_H1 - CONE_H0) * h, h) for h in hs]
    lathe(cx, cz, yaw + lean_u, prof, 16, lambda u, v: ruv('cone', u, 1 - v), cap_top='rubber')


cone(-0.62, 0.37, math.radians(14), 0.0)
cone(0.55, 0.38, math.radians(-9), 2.2)

# ----------------------------------------------------------------------------- finish
pos = np.array(P); nor = np.array(N); uv = np.array(U); tri = np.array(T)
bmin, bmax = pos.min(0), pos.max(0)
print('verts', len(pos), 'tris', len(tri), 'bbox min', bmin.round(3), 'max', bmax.round(3), 'size', (bmax - bmin).round(3))
assert len(tri) < 3000, 'triangle budget exceeded'
json.dump({'pos': pos.tolist(), 'uv': uv.tolist(), 'tri': tri.tolist(), 'nor': nor.tolist()}, open(OD + '/barricade_preview.json', 'w'))
json.dump({'min': bmin.tolist(), 'max': bmax.tolist(), 'tris': int(len(tri))}, open(OD + '/barricade_bounds.json', 'w'))

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
