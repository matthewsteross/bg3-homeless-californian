"""Procedural Broken-Down Robotaxi, written into the fire-basket template DAE (all 3 LODs).

AI-generated asset (procedural Python geometry and textures; no vanilla art is reused).
usage: build_robotaxi_model.py <basket_template.dae> <out.dae> <out_dir>
Units metres. Origin at ground centre, +Z = front (nose), +Y up, X = width. About 3.6 m x 1.6 m x 1.5 m.
Glossy white crossover shell (lofted cross-sections with wheel arches), blacked-out glass painted into the atlas, a neon-teal
LiDAR dome with a magenta flange on the roof, amber hazard lamps on all four corners, four wheels (one flat), side mirrors with
a deflated balloon and a half-lit rider-rating star hanging from them, a parking ticket on the windshield and one orange
traffic cone wedged under the front bumper.
Writes <out_dir>/HC_Robotaxi_BM.png, _NM.png, _PM.png, robotaxi_preview.json (Blender previews) and robotaxi_bounds.json.
Pipeline (see HANDOFF.md / hc_tarp.py): this script -> out.dae; then, with absolute paths,
  Divine.exe -g bg3 -a convert-model -s out.dae -d HC_Robotaxi.GR2 -i dae -o gr2 -e conform --conform-path <vanilla LTS_GEN_Fire_Basket_A.GR2> -l warn
  texconv.exe -nologo -y -f BC3_UNORM -m 0 -o <dir> <png>   (rename the results to .DDS)
Winding convention follows build_barricade_model.py: the right-hand normal of each DAE triangle points opposite to the
vertex normal (BG3 mirrors the DAE); internally triangles are stored outward-CCW.
"""
import sys, re, json, math
import numpy as np
sys.path.insert(0, __file__.replace('\\', '/').rsplit('/', 1)[0])
import robotaxi_paint as pt

TPL, OUT, OD = sys.argv[1:4]
cells, rough = pt.paint(OD + '/HC_Robotaxi_BM.png')
pt.nm_image().save(OD + '/HC_Robotaxi_NM.png')
pt.pm_image(rough).save(OD + '/HC_Robotaxi_PM.png')
rng = np.random.default_rng(20261018)
ruv, cuv, uvw = pt.ruv, pt.cuv, pt.uv_world

P, N, U, T = [], [], [], []
XF = [np.eye(3), np.zeros(3)]


def V(*a):
    return np.array(a, float)


def nrm(v):
    l = np.linalg.norm(v)
    return v / l if l > 1e-12 else v


class xf:
    """Context manager: every vertex created inside is transformed by rotation R then translation t."""
    def __init__(self, R=None, t=(0, 0, 0)):
        self.R = np.eye(3) if R is None else R
        self.t = V(*t)

    def __enter__(self):
        self.old = (XF[0], XF[1])
        XF[0], XF[1] = self.R, self.t

    def __exit__(self, *a):
        XF[0], XF[1] = self.old


def rot_x(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def rot_z(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def frame(d):
    ref = V(0, 1, 0) if abs(d[1]) < 0.9 else V(1, 0, 0)
    u = nrm(np.cross(ref, d)); v = np.cross(d, u)
    return u, v


def rot_to(d):
    """Rotation taking local +Y to direction d."""
    d = nrm(np.array(d, float)); u, v = frame(d)
    R = np.column_stack([u, d, v])
    if np.linalg.det(R) < 0:
        R = np.column_stack([-u, d, v])
    return R


def vert(p, n, uv):
    p = XF[0] @ np.array(p, float) + XF[1]
    n = XF[0] @ np.array(n, float)
    P.append(p); N.append(n); U.append(uv)
    return len(P) - 1


def add_tri(a, b, c):
    """Store the triangle outward-CCW: flip if its right-hand normal disagrees with the vertex normals."""
    gn = np.cross(P[b] - P[a], P[c] - P[a])
    mn = N[a] + N[b] + N[c]
    if np.linalg.norm(gn) < 1e-12:
        return
    T.append((a, b, c) if gn @ mn >= 0 else (a, c, b))


def box(c, ax, ay, az, hx, hy, hz, uvf, faces=None):
    axes = [nrm(np.array(ax, float)), nrm(np.array(ay, float)), nrm(np.array(az, float))]; half = [hx, hy, hz]; c = np.array(c, float)
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
            ids = [vert(pc + (u * math.cos(2 * math.pi * k / seg) + v * math.sin(2 * math.pi * k / seg)) * r, d * sg,
                        cuv(cell, f, 0.5 + 0.2 * math.sin(2 * math.pi * k / seg))) for k in range(seg + 1)]
            for k in range(seg):
                add_tri(ctr, ids[k], ids[k + 1])


def lathe(profile, seg, uvf, cap_top=None, cap_bottom=None, scale=(1.0, 1.0)):
    """Surface of revolution about local +Y at the origin. profile: [(radius, y, v)] bottom -> top.
    uvf(u, v) -> uv. cap_*: function (cos, sin) -> uv for a flat disc closing that end."""
    rings = []
    npts = len(profile)
    for idx, (r, y, v) in enumerate(profile):
        p0 = profile[max(idx - 1, 0)]; p1 = profile[min(idx + 1, npts - 1)]
        dr, dy = p1[0] - p0[0], p1[1] - p0[1]
        ring = []
        for k in range(seg + 1):
            th = 2 * math.pi * k / seg
            cs, sn = math.cos(th), math.sin(th)
            n = nrm(V(dy * cs, -dr, dy * sn))
            ring.append(vert(V(r * cs * scale[0], y, r * sn * scale[1]), n, uvf(k / seg, v)))
        rings.append(ring)
    for i in range(npts - 1):
        for k in range(seg):
            a, b, c, e = rings[i][k], rings[i][k + 1], rings[i + 1][k], rings[i + 1][k + 1]
            add_tri(a, b, c); add_tri(b, e, c)
    for end, capf, sgn in ((profile[-1], cap_top, 1), (profile[0], cap_bottom, -1)):
        if capf is None:
            continue
        r, y, _ = end
        ctr = vert(V(0, y, 0), V(0, sgn, 0), capf(0.0, 0.0))
        ids = [vert(V(r * math.cos(2 * math.pi * k / seg) * scale[0], y, r * math.sin(2 * math.pi * k / seg) * scale[1]),
                    V(0, sgn, 0), capf(math.cos(2 * math.pi * k / seg), math.sin(2 * math.pi * k / seg))) for k in range(seg + 1)]
        for k in range(seg):
            add_tri(ctr, ids[k], ids[k + 1])


# ============================================================================= body shell (loft along Z)
ZS = [1.80, 1.76, 1.70, 1.64, 1.58, 1.52, 1.46, 1.40, 1.30, 1.20, 1.12, 1.04, 0.94, 0.86, 0.78, 0.72, 0.66, 0.60, 0.45, 0.30, 0.15,
      0.0, -0.15, -0.40, -0.62, -0.68, -0.74, -0.82, -0.92, -1.02, -1.10, -1.18, -1.28, -1.38, -1.46, -1.52, -1.58, -1.64, -1.70,
      -1.76, -1.80]
HALF = len(pt.LOW) + len(pt.CAB)
NR = HALF + HALF - 2                        # ring points (right half + mirrored left half)


def ring_points(z):
    h = pt.half_section(z)
    right = [(x, y) for x, y in h]
    left = [(-x, y) for x, y in h[1:-1]][::-1]
    return [(x, y, z) for x, y in right + left]


G = np.array([ring_points(z) for z in ZS])  # [station, ring, xyz]
NS = len(ZS)
GN = np.zeros_like(G)
for i in range(NS):
    cen = V(0, G[i, :, 1].mean(), ZS[i])
    for j in range(NR):
        tr = G[i, (j + 1) % NR] - G[i, (j - 1) % NR]
        ts = G[min(i + 1, NS - 1), j] - G[max(i - 1, 0), j]
        n = np.cross(tr, ts)
        n = nrm(n)
        if n @ (G[i, j] - cen) < 0:
            n = -n
        GN[i, j] = n

ARCH_ZONE = [(zc - pt.ARCH_R - 0.12, zc + pt.ARCH_R + 0.12) for zc in pt.WHEEL_Z]


def pick_region(fn, c):
    """Atlas region for a body quad from its face normal / centre."""
    if fn[1] < -0.55:
        return 'under'
    if abs(c[0]) > 0.5 and c[1] < 0.80 and any(a <= c[2] <= b for a, b in ARCH_ZONE):
        return 'sideR' if c[0] > 0 else 'sideL'
    ax, ay, az = abs(fn[0]), abs(fn[1]), abs(fn[2])
    if ax >= ay and ax >= az:
        return 'sideR' if fn[0] > 0 else 'sideL'
    if ay >= az:
        return 'top'
    return 'front' if fn[2] > 0 else 'rear'


for i in range(NS - 1):
    for j in range(NR):
        j2 = (j + 1) % NR
        ids = [(i, j), (i, j2), (i + 1, j2), (i + 1, j)]
        pos = [G[a, b] for a, b in ids]
        fn = nrm(np.cross(pos[1] - pos[0], pos[3] - pos[0]) + np.cross(pos[2] - pos[1], pos[3] - pos[1]))
        avgn = sum(GN[a, b] for a, b in ids)
        if fn @ avgn < 0:
            fn = -fn
        cen = sum(pos) / 4
        reg = pick_region(fn, cen)
        vs = []
        for (a, b), p in zip(ids, pos):
            uv = cuv(cells['black'], 0.5, 0.5) if reg == 'under' else uvw(reg, p[0], p[1], p[2])
            vs.append(vert(p, GN[a, b], uv))
        add_tri(vs[0], vs[1], vs[2]); add_tri(vs[0], vs[2], vs[3])

# nose and tail caps (flat)
for i, sg, reg in ((0, 1, 'front'), (NS - 1, -1, 'rear')):
    ctr_p = G[i].mean(0)
    ctr = vert(ctr_p, V(0, 0, sg), uvw(reg, ctr_p[0], ctr_p[1], ctr_p[2]))
    ids = [vert(G[i, j], V(0, 0, sg), uvw(reg, *G[i, j])) for j in range(NR)]
    for j in range(NR):
        add_tri(ctr, ids[j], ids[(j + 1) % NR])

# ============================================================================= wheels
def wheel(sx, zc, flat=False):
    """Tyre + rim face. sx = +1 / -1 side. flat: squashed, bulging tyre sunk into the arch (the broken-down corner)."""
    yc = pt.WHEEL_YC
    R = rot_z(-math.pi / 2) if sx > 0 else rot_z(math.pi / 2)
    hw, r = pt.WHEEL_HW, pt.WHEEL_R
    if flat:
        r *= 0.84; hw *= 1.22; yc = r + 0.005
    prof = [(r * 0.57, -hw, 0.0), (r * 0.94, -hw * 0.95, 0.25), (r, 0.0, 0.5), (r * 0.94, hw * 0.95, 0.75), (r * 0.57, hw, 1.0)]
    with xf(R, (sx * pt.WHEEL_X, yc, zc)):
        lathe(prof, 16, lambda u, v: ruv('tire', u, 1 - v), cap_top=lambda c, s: ruv('wheelface', 0.5 + 0.48 * c, 0.5 + 0.48 * s))


for sx in (1, -1):
    for zc in pt.WHEEL_Z:
        wheel(sx, zc, flat=(sx > 0 and zc < 0))

# ============================================================================= lidar dome (neon teal) with magenta flange
LZ = -0.40
roof_top = pt.surface_y(0.0, LZ)
LV = [(0.26, 0.0, 0.00), (0.26, 0.012, 0.07), (0.19, 0.014, 0.10), (0.19, 0.040, 0.20), (0.165, 0.045, 0.22),
      (0.165, 0.135, 0.72), (0.12, 0.168, 0.88), (0.0, 0.190, 1.0)]
with xf(None, (0.0, roof_top - 0.002, LZ)):
    lathe(LV, 18, lambda u, v: ruv('lidar', u, 1 - v))

# ============================================================================= hazard lamps on all four corners (amber domes)
DOME = [(0.085, 0.0, 0.0), (0.078, 0.02, 0.35), (0.055, 0.042, 0.75), (0.0, 0.056, 1.0)]
for sx, sz, y in ((1, 1, 0.42), (-1, 1, 0.42), (1, -1, 0.52), (-1, -1, 0.52)):
    zz = 1.74 if sz > 0 else -1.76
    xx = 0.64 if sz > 0 else 0.64
    d = V(sx * 0.7, 0.05, sz * 0.7)
    with xf(rot_to(d), (sx * xx, y, zz)):
        lathe(DOME, 8, lambda u, v: ruv('lens', u, 1 - v))

# ============================================================================= side mirrors, balloon and star
MZ = 0.34
CAB0 = len(pt.LOW)
MIR_X = 0.88                                    # mirror housing centre, outside the body shell
MIR_Y = pt.surface_y(0.7, MZ) + 0.05
for sx in (1, -1):
    box((sx * MIR_X, MIR_Y, MZ), X, Y, Z, 0.035, 0.035, 0.065, cellf('teal'))
    arm_x = pt.half_section(MZ)[CAB0][0] - 0.02
    tube((sx * arm_x, MIR_Y - 0.01, MZ), (sx * (MIR_X - 0.03), MIR_Y, MZ), 0.012, 0.012, 5, cells['black'], caps=False)

# deflated balloon tied to the +X mirror (red, squashed, with a knot and string up to the mirror)
tie = V(MIR_X + 0.01, MIR_Y - 0.035, MZ + 0.03)
BAL = [(0.0, -0.22, 0.0), (0.040, -0.20, 0.12), (0.082, -0.15, 0.34), (0.086, -0.09, 0.56), (0.050, -0.04, 0.80),
       (0.012, -0.012, 0.93), (0.005, 0.0, 1.0)]
with xf(None, tuple(tie + V(0.02, -0.08, 0.0))):
    lathe(BAL, 10, lambda u, v: ruv('balloon', u, 1 - v), scale=(0.6, 1.5))
tube(tuple(tie + V(0.02, -0.08, 0)), tuple(tie), 0.003, 0.003, 4, cells['black'], caps=False)

# rider-rating star on a string from the -X mirror (a half-lit gold star, shape only)
st_top = V(-MIR_X - 0.01, MIR_Y - 0.035, MZ - 0.02)
SR_O, SR_I = 0.14, 0.060
star = [(SR_O * math.cos(-math.pi / 2 + k * math.pi / 5) * (1 if k % 2 == 0 else SR_I / SR_O),
         SR_O * math.sin(-math.pi / 2 + k * math.pi / 5) * (1 if k % 2 == 0 else SR_I / SR_O)) for k in range(10)]
star_c = st_top + V(-0.03, -0.12 - SR_O, 0.0)
for sg in (1, -1):
    cid = vert(star_c, V(0, 0, sg), ruv('star', 0.5, 0.5))
    ring = [vert(star_c + V(sx_, -sy_, sg * 0.004), V(0, 0, sg), ruv('star', 0.5 + 0.5 * sx_ / SR_O * 0.97, 0.5 - 0.5 * sy_ / SR_O * 0.97))
            for sx_, sy_ in star]
    for k in range(10):
        add_tri(cid, ring[k], ring[(k + 1) % 10])
tube(tuple(st_top), tuple(star_c + V(0, SR_O * 0.97, 0)), 0.003, 0.003, 4, cells['black'], caps=False)

# ============================================================================= parking ticket on the windshield
tz, tx = 0.18, -0.30
ty = pt.surface_y(tx, tz)
dydz = (pt.surface_y(tx, tz + 0.05) - pt.surface_y(tx, tz - 0.05)) / 0.10
dydx = (pt.surface_y(tx + 0.05, tz) - pt.surface_y(tx - 0.05, tz)) / 0.10
az = nrm(V(0, dydz, 1)); ax = nrm(V(1, dydx, 0)); ay = nrm(np.cross(az, ax))
box((tx, ty + 0.006, tz), ax, ay, az, 0.10, 0.003, 0.065, lambda k, sg, a, b: ruv('ticket', a, 1 - b) if k == 1 else cuv(cells['yellow'], a, b),
    faces={(1, 1), (0, 1), (0, -1), (2, 1), (2, -1)})

# ============================================================================= traffic cone wedged under the front bumper
CONE_H0, CONE_H1, CR0, CR1 = 0.035, 0.44, 0.08, 0.017
lean = math.radians(46)
Rlean = rot_x(-lean)                         # tilt the tip towards -Z (into the nose)
cone_pivot = V(0.12, 0.0, 2.04)
cone_local = []


def cone_geom():
    box((0, 0.012, 0), X, Y, Z, 0.095, 0.012, 0.095, cellf('rubber'))
    prof = [(CR0 + (CR1 - CR0) * h, CONE_H0 + (CONE_H1 - CONE_H0) * h, h) for h in (0.0, 0.31, 0.46, 0.60, 0.80, 1.0)]
    lathe(prof, 14, lambda u, v: ruv('cone', u, 1 - v), cap_top=lambda c, s: cuv(cells['rubber'], 0.5, 0.5))


with xf(Rlean, tuple(cone_pivot)):
    n0 = len(P)
    cone_geom()
cp = np.array(P[n0:])
shift = -cp[:, 1].min()
for k in range(n0, len(P)):
    P[k] = P[k] + V(0, shift, 0)

# ============================================================================= finish
pos = np.array(P); nor = np.array(N); uv = np.array(U); tri = np.array(T)
bmin, bmax = pos.min(0), pos.max(0)
print('verts', len(pos), 'tris', len(tri), 'bbox min', bmin.round(3), 'max', bmax.round(3), 'size', (bmax - bmin).round(3))
assert len(tri) < 3800, 'triangle budget exceeded'
json.dump({'pos': pos.tolist(), 'uv': uv.tolist(), 'tri': tri.tolist(), 'nor': nor.tolist()}, open(OD + '/robotaxi_preview.json', 'w'))
json.dump({'min': bmin.tolist(), 'max': bmax.tolist(), 'tris': int(len(tri))}, open(OD + '/robotaxi_bounds.json', 'w'))

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
