"""Procedural Abandoned Cart prop, written into the fire-basket template DAE (all 3 LOD meshes).

usage: build_cart_model.py <basket_template.dae> <out.dae> <out_dir>
Units metres. Origin at ground centre, +Z = cart front, +Y up, X = width.
Writes <out_dir>/HC_ShoppingCart_BM.png and <out_dir>/cart_preview.json (for Blender previews).
Winding convention follows build_own_bullet.py: the right-hand normal of each DAE triangle points
opposite to the vertex normal (BG3 mirrors the DAE); internally triangles are stored outward-CCW.
"""
import sys, re, json, math
import numpy as np
sys.path.insert(0, __file__.replace('\\', '/').rsplit('/', 1)[0])
import cart_paint

TPL, OUT, OD = sys.argv[1:4]
cells = cart_paint.paint(OD + '/HC_ShoppingCart_BM.png')
rng = np.random.default_rng(20261014)

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


def obox(c, ax, ay, az, hx, hy, hz, cell):
    """Oriented box, flat-shaded. UV: U runs along the longer in-plane half extent."""
    axes = [nrm(ax), nrm(ay), nrm(az)]; half = [hx, hy, hz]; c = np.array(c, float)
    for k in range(3):
        i, j = (k + 1) % 3, (k + 2) % 3
        for sg in (-1, 1):
            n = axes[k] * sg
            base = c + n * half[k]
            fi = half[i] >= half[j]
            corners = []
            for si, sj in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
                p = base + axes[i] * si * half[i] + axes[j] * sj * half[j]
                a, b = (si, sj) if fi else (sj, si)
                corners.append(vert(p, n, cart_paint.uv(cell, (a + 1) / 2, (b + 1) / 2)))
            add_tri(corners[0], corners[1], corners[2]); add_tri(corners[0], corners[2], corners[3])


def bar(p0, p1, w, h, cell):
    p0, p1 = V(*p0), V(*p1); d = p1 - p0; L = np.linalg.norm(d)
    if L < 1e-6:
        return
    d = d / L; u, v = frame(d)
    obox((p0 + p1) / 2, d, u, v, L / 2, w / 2, h / 2, cell)


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
            ring.append(vert(pc + rad * r, n, cart_paint.uv(cell, f, k / seg)))
        rings.append(ring)
    for k in range(seg):
        a, b, c, e = rings[0][k], rings[0][k + 1], rings[1][k], rings[1][k + 1]
        add_tri(a, b, c); add_tri(b, e, c)
    if caps:
        for pc, r, sg, f in ((p0, r0, -1, 0.0), (p1, r1, 1, 1.0)):
            if r < 1e-6:
                continue
            ctr = vert(pc, d * sg, cart_paint.uv(cell, f, 0.5))
            ids = []
            for k in range(seg + 1):
                a = 2 * math.pi * k / seg
                ids.append(vert(pc + (u * math.cos(a) + v * math.sin(a)) * r, d * sg,
                                cart_paint.uv(cell, f, 0.5 + 0.2 * math.sin(a))))
            for k in range(seg):
                add_tri(ctr, ids[k], ids[k + 1])


# ----------------------------------------------------------------------------- dimensions
Y0, Y1 = 0.30, 0.80            # basket floor / rim height
HW0, HW1 = 0.190, 0.260        # half width at floor / rim
ZR0, ZR1 = -0.300, -0.410      # rear wall z at floor / rim
ZF0, ZF1 = 0.330, 0.455        # front wall z at floor / rim (slants forward)
lerp = lambda a, b, t: a + (b - a) * t


def BP(t, xs, s):
    """Point on the tapered basket: height param t, width fraction xs in [-1,1], length fraction s in [0,1]."""
    return (xs * lerp(HW0, HW1, t), lerp(Y0, Y1, t), lerp(lerp(ZR0, ZR1, t), lerp(ZF0, ZF1, t), s))


CHROME = ['chrome_clean', 'chrome_dirty', 'chrome_rusty', 'zinc']


def pick(rust_bias=0.0):
    w = np.array([0.34, 0.32, 0.22 + rust_bias, 0.12]); w = w / w.sum()
    return CHROME[int(rng.choice(4, p=w))]


def wire(a, b, bias=0.0, size=0.0075):
    bar(a, b, size, size, cells[pick(bias)])


# ----------------------------------------------------------------------------- basket
# rims
for a, b in (((-1, 1, 0), (-1, 1, 1)), ((1, 1, 0), (1, 1, 1)), ((-1, 1, 1), (1, 1, 1)), ((-1, 1, 0), (1, 1, 0))):
    tube(BP(1, a[0], a[2]), BP(1, b[0], b[2]), 0.0085, 0.0085, 8, cells[pick()])
for a, b in (((-1, 0, 0), (-1, 0, 1)), ((1, 0, 0), (1, 0, 1)), ((-1, 0, 1), (1, 0, 1)), ((-1, 0, 0), (1, 0, 0))):
    tube(BP(0, a[0], a[2]), BP(0, b[0], b[2]), 0.0065, 0.0065, 6, cells[pick(0.2)])
# corner posts
for xs in (-1, 1):
    for s in (0, 1):
        tube(BP(0, xs, s), BP(1, xs, s), 0.0075, 0.0075, 6, cells[pick(0.1)])
# side walls
for xs in (-1, 1):
    for t in (0.22, 0.44, 0.66):
        wire(BP(t, xs, 0), BP(t, xs, 1), 0.15 * (1 - t))
    for s in np.linspace(0, 1, 11)[1:-1]:
        wire(BP(0, xs, s), BP(1, xs, s), 0.1)
# front wall (s = 1)
for t in (0.22, 0.44, 0.66):
    wire(BP(t, -1, 1), BP(t, 1, 1), 0.15 * (1 - t))
for xs in np.linspace(-1, 1, 8)[1:-1]:
    wire(BP(0, xs, 1), BP(1, xs, 1), 0.1)
# rear wall (s = 0), fewer bars: it is the loading gate
for t in (0.22, 0.44):
    wire(BP(t, -1, 0), BP(t, 1, 0), 0.2)
for xs in np.linspace(-1, 1, 6)[1:-1]:
    wire(BP(0, xs, 0), BP(1, xs, 0), 0.1)
# floor
for xs in np.linspace(-1, 1, 11)[1:-1]:
    wire((xs * HW0, Y0, ZR0), (xs * HW0, Y0, ZF0), 0.3, 0.008)
for s in np.linspace(0, 1, 15)[1:-1]:
    z = lerp(ZR0, ZF0, s)
    wire((-HW0, Y0 - 0.008, z), (HW0, Y0 - 0.008, z), 0.3, 0.008)

# ----------------------------------------------------------------------------- child seat flap (folded down)
tilt = math.radians(8)
fwd = V(0, -math.sin(tilt), math.cos(tilt)); up = V(0, math.cos(tilt), math.sin(tilt)); xaxis = V(1, 0, 0)
hinge = V(0, lerp(Y0, Y1, 0.54), lerp(ZR0, ZR1, 0.54) + 0.014)
sw, sl, st = 0.212, 0.27, 0.011
blue = cells['plastic_blue']


def seat_strip(a0, a1, b0, b1):
    ca, cb = (a0 + a1) / 2, (b0 + b1) / 2
    obox(hinge + xaxis * ca + fwd * cb, xaxis, fwd, up, (a1 - a0) / 2, (b1 - b0) / 2, st / 2, blue)


seat_strip(-sw, sw, 0.0, 0.045)           # rear strip
seat_strip(-sw, sw, sl - 0.045, sl)       # front strip
seat_strip(-sw, -sw + 0.045, 0.0, sl)     # left
seat_strip(sw - 0.045, sw, 0.0, sl)       # right
seat_strip(-0.022, 0.022, 0.0, sl)        # centre divider -> two leg holes
tube(tuple(hinge + xaxis * -sw), tuple(hinge + xaxis * sw), 0.0065, 0.0065, 6, cells['chrome_dirty'])

# ----------------------------------------------------------------------------- chassis, tray, risers
CX = 0.205
CY = 0.175
ZREAR_W, ZFRONT_W = -0.36, 0.34
for sx in (-1, 1):
    tube((sx * CX, CY, -0.375), (sx * CX, CY, 0.42), 0.009, 0.009, 8, cells[pick(0.25)])
for z in (ZREAR_W, 0.0, ZFRONT_W):
    tube((-CX, CY, z), (CX, CY, z), 0.008, 0.008, 8, cells[pick(0.25)])
for x in (-0.15, -0.075, 0.0, 0.075, 0.15):
    wire((x, CY + 0.012, -0.36), (x, CY + 0.012, 0.34), 0.35, 0.0075)
for z in np.linspace(-0.30, 0.30, 7):
    wire((-CX, CY + 0.016, z), (CX, CY + 0.016, z), 0.35, 0.0075)
for sx in (-1, 1):
    tube((sx * CX, CY, ZREAR_W), (sx * HW0, Y0, ZR0), 0.008, 0.008, 6, cells[pick(0.2)])
    tube((sx * CX, CY, 0.0), (sx * HW0, Y0, lerp(ZR0, ZF0, 0.5)), 0.008, 0.008, 6, cells[pick(0.2)])
    tube((sx * CX, CY, ZFRONT_W), (sx * HW0, Y0, ZF0), 0.008, 0.008, 6, cells[pick(0.2)])

# ----------------------------------------------------------------------------- wheels
WR, WW = 0.055, 0.032
for wz in (0.34, -0.36):
    for sx in (-1, 1):
        wx = sx * CX
        tube((wx - WW / 2, WR, wz), (wx + WW / 2, WR, wz), WR, WR, 20, cells['rubber'])
        tube((wx - 0.019, WR, wz), (wx + 0.019, WR, wz), 0.027, 0.027, 12, cells['zinc'])
        for fx in (-0.0225, 0.0225):                       # fork plates
            obox((wx + fx, 0.098, wz), V(1, 0, 0), V(0, 1, 0), V(0, 0, 1), 0.003, 0.058, 0.016, cells['zinc'])
        obox((wx, 0.165, wz), V(1, 0, 0), V(0, 1, 0), V(0, 0, 1), 0.032, 0.004, 0.032, cells['zinc'])

# ----------------------------------------------------------------------------- handle
HY, HZ, HX = 0.975, -0.485, 0.245
for sx in (-1, 1):
    tube(BP(1, sx, 0), (sx * HX, HY, HZ), 0.0095, 0.0095, 8, cells['chrome_clean'])
tube(BP(1, 0, 0), (0, HY, HZ), 0.007, 0.007, 6, cells['chrome_dirty'])
tube((-HX, HY, HZ), (HX, HY, HZ), 0.0095, 0.0095, 8, cells['chrome_clean'])
tube((-0.17, HY, HZ), (0.17, HY, HZ), 0.0165, 0.0165, 14, cells['grip_red'])
for sx in (-1, 1):
    tube((sx * 0.17, HY, HZ), (sx * 0.178, HY, HZ), 0.0185, 0.0185, 14, cells['zinc'])

# ----------------------------------------------------------------------------- finish
pos = np.array(P); nor = np.array(N); uv = np.array(U); tri = np.array(T)
bmin, bmax = pos.min(0), pos.max(0)
print('verts', len(pos), 'tris', len(tri), 'bbox min', bmin.round(3), 'max', bmax.round(3),
      'size', (bmax - bmin).round(3))
assert len(tri) < 7500, 'triangle budget exceeded'
json.dump({'pos': pos.tolist(), 'uv': uv.tolist(), 'tri': tri.tolist(), 'nor': nor.tolist()}, open(OD + '/cart_preview.json', 'w'))
BOUNDS = (bmin.tolist(), bmax.tolist())
json.dump({'min': bmin.tolist(), 'max': bmax.tolist(), 'tris': int(len(tri))}, open(OD + '/cart_bounds.json', 'w'))

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
