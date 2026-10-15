"""Procedural Blue Tarp Lean-To prop, written into the fire-basket template DAE (all 3 LOD meshes).

AI-generated asset (procedural Python geometry and textures; no vanilla art is reused).
usage: build_tarp_model.py <basket_template.dae> <out.dae> <out_dir>
Units metres. Origin at ground centre, +Z = open front of the shelter, +Y up, X = width (ridge runs along X).
A blue tarp is draped over a ridge pole on two rebar uprights as an A-frame, with a short rebar prop under the
front lip, six grommets, rope guy lines to rebar stakes, and bricks on the rear flap.
Writes <out_dir>/HC_BlueTarp_BM.png, tarp_preview.json (for Blender previews) and tarp_bounds.json.
Winding convention follows build_cart_model.py: the right-hand normal of each DAE triangle points opposite to the
vertex normal (BG3 mirrors the DAE); internally triangles are stored outward-CCW.
"""
import sys, re, json, math
import numpy as np
sys.path.insert(0, __file__.replace('\\', '/').rsplit('/', 1)[0])
import tarp_paint as paint_mod

TPL, OUT, OD = sys.argv[1:4]
cells = paint_mod.paint(OD + '/HC_BlueTarp_BM.png')
rng = np.random.default_rng(20261015)

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
                corners.append(vert(p, n, paint_mod.uv(cell, (a + 1) / 2, (b + 1) / 2)))
            add_tri(corners[0], corners[1], corners[2]); add_tri(corners[0], corners[2], corners[3])


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
            ring.append(vert(pc + rad * r, n, paint_mod.uv(cell, f, k / seg)))
        rings.append(ring)
    for k in range(seg):
        a, b, c, e = rings[0][k], rings[0][k + 1], rings[1][k], rings[1][k + 1]
        add_tri(a, b, c); add_tri(b, e, c)
    if caps:
        for pc, r, sg, f in ((p0, r0, -1, 0.0), (p1, r1, 1, 1.0)):
            if r < 1e-6:
                continue
            ctr = vert(pc, d * sg, paint_mod.uv(cell, f, 0.5))
            ids = []
            for k in range(seg + 1):
                a = 2 * math.pi * k / seg
                ids.append(vert(pc + (u * math.cos(a) + v * math.sin(a)) * r, d * sg,
                                paint_mod.uv(cell, f, 0.5 + 0.2 * math.sin(a))))
            for k in range(seg):
                add_tri(ctr, ids[k], ids[k + 1])


def washer(c, n, ro, ri, h, cell, hole_cell, seg=8):
    """Grommet: flat ring of outer radius ro, hole radius ri, standing h above its base plane (normal n)."""
    n = nrm(V(*n)); u, v = frame(n); c = V(*c)

    def ring(r, hh):
        return [c + n * hh + (u * math.cos(2 * math.pi * k / seg) + v * math.sin(2 * math.pi * k / seg)) * r
                for k in range(seg + 1)]

    def radial(k):
        a = 2 * math.pi * k / seg
        return u * math.cos(a) + v * math.sin(a)

    ot, it, ob = ring(ro, h), ring(ri, h), ring(ro, 0.0)
    for k in range(seg):
        # top annulus
        q = [vert(p, n, paint_mod.uv(cell, 0.5 + 0.35 * math.cos(a), 0.5 + 0.35 * math.sin(a)))
             for p, a in ((ot[k], 2 * math.pi * k / seg), (ot[k + 1], 2 * math.pi * (k + 1) / seg),
                          (it[k + 1], 2 * math.pi * (k + 1) / seg), (it[k], 2 * math.pi * k / seg))]
        add_tri(q[0], q[1], q[2]); add_tri(q[0], q[2], q[3])
        # outer wall
        w = [vert(ob[k], radial(k), paint_mod.uv(cell, 0.1, 0.1)), vert(ob[k + 1], radial(k + 1), paint_mod.uv(cell, 0.9, 0.1)),
             vert(ot[k + 1], radial(k + 1), paint_mod.uv(cell, 0.9, 0.9)), vert(ot[k], radial(k), paint_mod.uv(cell, 0.1, 0.9))]
        add_tri(w[0], w[1], w[2]); add_tri(w[0], w[2], w[3])
        # inner wall (the dark hole)
        iw = [vert(it[k], -radial(k), paint_mod.uv(hole_cell, 0.5, 0.5)), vert(it[k + 1], -radial(k + 1), paint_mod.uv(hole_cell, 0.5, 0.5)),
              vert(c + (it[k + 1] - c) - n * h, -radial(k + 1), paint_mod.uv(hole_cell, 0.5, 0.5)),
              vert(c + (it[k] - c) - n * h, -radial(k), paint_mod.uv(hole_cell, 0.5, 0.5))]
        add_tri(iw[0], iw[1], iw[2]); add_tri(iw[0], iw[2], iw[3])


# ----------------------------------------------------------------------------- tarp surface
XH = 1.10                 # half width of the tarp
THK = 0.004               # half thickness
NA, NR = 16, 9            # quads along the ridge, rows per slope
GROM_A = (0.0455, 0.5, 0.9545)   # grommet positions along the hem (fraction of width)
# (p, z, y) knots: p = -1 rear edge, 0 ridge, +1 front edge. The rear flap lies flat on the ground at the end.
PROFILE_P = np.array([-1.0, -0.667, 0.0, 0.778, 1.0])
PROFILE_Z = np.array([-0.92, -0.60, 0.0, 0.66, 0.85])
PROFILE_Y = np.array([0.026, 0.100, 1.40, 0.50, 0.30])


def sag_profile(a):
    for i in range(len(GROM_A) - 1):
        lo, hi = GROM_A[i], GROM_A[i + 1]
        if lo <= a <= hi:
            return math.sin(math.pi * (a - lo) / (hi - lo))
    return 0.0


def wrinkle(a, p):
    return (0.55 * math.sin(a * 2 * math.pi * 3.3 + 1.1 + p * 1.7)
            + 0.30 * math.sin(a * 2 * math.pi * 5.7 - 0.8 - p * 2.9)
            + 0.15 * math.sin(p * 9.0 + a * 6.0 + 0.4))


def S(a, p):
    r = abs(p)
    s = 1.0 if p >= 0 else -1.0
    z = float(np.interp(p, PROFILE_P, PROFILE_Z))
    y = float(np.interp(p, PROFILE_P, PROFILE_Y))
    sg = sag_profile(a) * r ** 3
    y += wrinkle(a, p) * 0.014 * min(r * 4, 1.0) * (0.35 if p < -0.6 else 1.0)
    if p > 0:
        y -= 0.050 * sg            # the front hem droops between grommets
    z -= s * 0.045 * sg             # and is pulled in toward the ridge
    y = max(y, 0.012)
    return V(-XH + 2 * XH * a, y, z)


def surf_normal(a, p):
    e = 0.02
    da = (S(min(a + e, 1.0), p) - S(max(a - e, 0.0), p)) / (min(a + e, 1.0) - max(a - e, 0.0))
    p0, p1 = max(p - e, -1.0), min(p + e, 1.0)
    dp = (S(a, p1) - S(a, p0)) / (p1 - p0)
    n = nrm(np.cross(dp, da))
    assert n[1] > 0, (a, p, n)
    return n, nrm(da), nrm(dp)


def build_slope(sign):
    region_top = 'top_front' if sign > 0 else 'top_rear'
    region_under = 'under_front' if sign > 0 else 'under_rear'
    top = [[None] * (NA + 1) for _ in range(NR + 1)]
    bot = [[None] * (NA + 1) for _ in range(NR + 1)]
    for i in range(NR + 1):
        r = i / NR
        p = sign * r
        for j in range(NA + 1):
            a = j / NA
            c = S(a, p); n, _, _ = surf_normal(a, p)
            top[i][j] = vert(c + n * THK, n, paint_mod.uv_region(region_top, a, r))
            bot[i][j] = vert(c - n * THK, -n, paint_mod.uv_region(region_under, a, r))
    for i in range(NR):
        for j in range(NA):
            for g, flip in ((top, False), (bot, True)):
                a, b, c_, d = g[i][j], g[i][j + 1], g[i + 1][j + 1], g[i + 1][j]
                add_tri(a, b, c_); add_tri(a, c_, d)
    # hem strips on the left, right and low edge
    def strip(points):
        """points: list of (a, r, outward_normal); joins the top and bottom surface along the border."""
        ids = []
        for a, r, n_out, in points:
            c = S(a, sign * r); n, _, _ = surf_normal(a, sign * r)
            uvh = paint_mod.uv_region(region_top, a, r)
            ids.append((vert(c + n * THK, n_out, uvh), vert(c - n * THK, n_out, uvh)))
        for k in range(len(ids) - 1):
            (t0, b0), (t1, b1) = ids[k], ids[k + 1]
            add_tri(t0, t1, b1); add_tri(t0, b1, b0)

    for a_edge, nx in ((0.0, -1.0), (1.0, 1.0)):
        strip([(a_edge, i / NR, V(nx, 0, 0)) for i in range(NR + 1)])
    row = []
    for j in range(NA + 1):
        a = j / NA
        _, _, dp = surf_normal(a, sign)
        row.append((a, 1.0, dp * sign))
    strip(row)


build_slope(+1)
build_slope(-1)
tarp_tris = len(T)

# ----------------------------------------------------------------------------- grommets
GROMMET_R = 0.95
grommets = []
for sign in (+1, -1):
    for a in GROM_A:
        p = sign * GROMMET_R
        c = S(a, p); n, _, _ = surf_normal(a, p)
        base = c + n * (THK + 0.0004)
        washer(base, n, 0.020, 0.0085, 0.0045, cells['brass'], cells['grommet_dark'])
        grommets.append((sign, a, base + n * 0.003))

# ----------------------------------------------------------------------------- poles
RIDGE_Y = 1.378
tube((-1.20, RIDGE_Y, 0.0), (1.20, RIDGE_Y, 0.0), 0.0140, 0.0140, 8, cells['rebar_dull'])
for sx in (-1, 1):
    tube((sx * 1.0, 0.0, 0.0), (sx * 1.0, RIDGE_Y, 0.0), 0.0125, 0.0125, 8, cells['rebar_rust'])
# front prop under the lip, leaning back a few degrees onto the middle of the front hem
edge_c = S(0.5, 1.0)
tube((0.0, 0.0, edge_c[2] + 0.05), (0.0, edge_c[1] - THK - 0.004, edge_c[2]), 0.0120, 0.0120, 8, cells['rebar_rust'])

# bricks: two flanking the base of each upright, two holding down the rear flap
for sx in (-1, 1):
    for sz in (-1, 1):
        ang = math.radians(rng.uniform(-12, 12))
        ax = V(math.cos(ang), 0, math.sin(ang)); az = V(-math.sin(ang), 0, math.cos(ang))
        obox((sx * 1.0 + sx * 0.02, 0.0325, sz * 0.14), ax, V(0, 1, 0), az, 0.055, 0.0325, 0.110, cells['brick'])
for a in (0.22, 0.78):
    p = -0.93
    c = S(a, p); n, _, _ = surf_normal(a, p)
    ang = math.radians(rng.uniform(-14, 14))
    ax = V(math.cos(ang), 0, math.sin(ang)); az = nrm(np.cross(ax, n)); ax = nrm(np.cross(n, az))
    obox(c + n * (THK + 0.0325), ax, n, az, 0.110, 0.0325, 0.055, cells['concrete'])

# ----------------------------------------------------------------------------- stakes and guy ropes
stakes = {(+1, 0): (0.0, 1.12), (+1, 1): (-1.18, 1.05), (+1, 2): (1.18, 1.05),
          (-1, 0): (0.0, -1.10), (-1, 1): (-1.18, -1.05), (-1, 2): (1.18, -1.05)}
a_for = {0: 0.5, 1: GROM_A[0], 2: GROM_A[2]}
for (sign, a, gpos) in grommets:
    k = 0 if a == 0.5 else (1 if a == GROM_A[0] else 2)
    sx, sz = stakes[(sign, k)]
    out = nrm(V(sx, 0, sz) - V(0, 0, 0))
    base = V(sx, 0.0, sz)
    top = V(sx + out[0] * 0.05, 0.27, sz + out[2] * 0.05)
    tube(tuple(base), tuple(top), 0.0075, 0.0075, 6, cells['rebar_rust'])
    # rope: from the grommet, sagging slightly, to the stake head
    start = gpos; end = top + V(0, -0.025, 0)
    nseg = 6
    pts = []
    for q in range(nseg + 1):
        t = q / nseg
        pt = start + (end - start) * t + V(0, -0.045 * 4 * t * (1 - t), 0)
        pts.append(pt)
    for q in range(nseg):
        tube(tuple(pts[q]), tuple(pts[q + 1]), 0.0075, 0.0075, 5, cells['rope'], caps=(q == 0 or q == nseg - 1))
    # knot at the stake
    tube(tuple(end + V(0, 0.012, 0)), tuple(end - V(0, 0.012, 0)), 0.013, 0.013, 6, cells['rope_dark'])

# ----------------------------------------------------------------------------- finish
pos = np.array(P); nor = np.array(N); uv = np.array(U); tri = np.array(T)
bmin, bmax = pos.min(0), pos.max(0)
print('verts', len(pos), 'tris', len(tri), '(tarp', tarp_tris, ') bbox min', bmin.round(3), 'max', bmax.round(3),
      'size', (bmax - bmin).round(3))
assert len(tri) < 3000, 'triangle budget exceeded'
json.dump({'pos': pos.tolist(), 'uv': uv.tolist(), 'tri': tri.tolist(), 'nor': nor.tolist()}, open(OD + '/tarp_preview.json', 'w'))
json.dump({'min': bmin.tolist(), 'max': bmax.tolist(), 'tris': int(len(tri))}, open(OD + '/tarp_bounds.json', 'w'))

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
