"""Procedural Hostile Architecture Bench, written into the fire-basket template DAE (all 3 LODs).

AI-generated asset (procedural Python geometry and textures; no vanilla art is reused).
usage: build_bench_model.py <basket_template.dae> <out.dae> <out_dir>
Units metres. Origin at ground, +Z = front (the seat side), +Y up. A 2.0 m long heavy dark-green cast-iron bus-stop bench
(three end/centre frames with scroll armrests, four seat slats, three backrest slats) on a 3.2 m concrete pad. Five oversized
chrome armrest dividers loop across the seat so nobody can lie down, 40-odd jagged steel pyramid studs bristle between them,
a neon-yellow municipal asset-tag plate (QR block, barcode, city seal) is bolted to the backrest, a small hot-pink sponsor
ad panel (giant smiley, 'no lying down' pictogram) stands on a post beside the bench, and one pigeon sits on the backrest,
perfectly comfortable. No lettering anywhere (BG3 mirrors the DAE).
Writes <out_dir>/HC_Bench_BM.png, _NM.png, _PM.png, bench_preview.json (Blender previews) and bench_bounds.json.
Pipeline (see HANDOFF.md / hc_tarp.py): this script -> out.dae; then, with absolute paths,
  Divine.exe -g bg3 -a convert-model -s out.dae -d HC_Bench.GR2 -i dae -o gr2 -e conform --conform-path <vanilla LTS_GEN_Fire_Basket_A.GR2> -l warn
  texconv.exe -nologo -y -f BC3_UNORM -m 0 -o <dir> <png>   (rename the results to .DDS)
Winding convention follows build_tarp_model.py: the right-hand normal of each DAE triangle points opposite to the
vertex normal (BG3 mirrors the DAE); internally triangles are stored outward-CCW.
"""
import sys, re, json, math
import numpy as np
sys.path.insert(0, __file__.replace('\\', '/').rsplit('/', 1)[0])
import bench_paint as paint_mod

TPL, OUT, OD = sys.argv[1:4]
cells, rough = paint_mod.paint(OD + '/HC_Bench_BM.png')
paint_mod.nm_image().save(OD + '/HC_Bench_NM.png')
paint_mod.pm_image(rough).save(OD + '/HC_Bench_PM.png')
rng = np.random.default_rng(20261019)
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


X, Y, Z = V(1, 0, 0), V(0, 1, 0), V(0, 0, 1)


def rx(a):
    c, s = math.cos(a), math.sin(a); return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def ry(a):
    c, s = math.cos(a), math.sin(a); return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


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


def bar(p0, p1, hw, hd, cell, faces=None):
    """Oriented square-section bar from p0 to p1 (hw half width across, hd half depth)."""
    p0, p1 = V(*p0), V(*p1); d = p1 - p0; L = np.linalg.norm(d); ay = d / L
    ax = nrm(X - ay * (X @ ay)); az = np.cross(ax, ay)
    box((p0 + p1) / 2, ax, ay, az, hw, L / 2, hd, cellf(cell), faces)


# ----------------------------------------------------------------------------- generic sweeps
def path_tube(pts, radii, sides, uvf, caps=True):
    """Tube along a polyline with parallel-transport frames. uvf(s, t): s along 0..1, t around 0..1."""
    pts = [V(*p) for p in pts]; n = len(pts)
    radii = [radii] * n if np.isscalar(radii) else radii
    tans = [nrm(pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]) for i in range(n)]
    u, v = frame(tans[0]); rings = []
    for i in range(n):
        if i > 0:
            t = tans[i]; u = nrm(u - t * (u @ t)); v = np.cross(t, u)
        ring = []
        for k in range(sides + 1):
            a = 2 * math.pi * k / sides
            rad = u * math.cos(a) + v * math.sin(a)
            ring.append(vert(pts[i] + rad * radii[i], rad, uvf(i / (n - 1), k / sides)))
        rings.append(ring)
    for i in range(n - 1):
        for k in range(sides):
            a, b, c, e = rings[i][k], rings[i][k + 1], rings[i + 1][k], rings[i + 1][k + 1]
            add_tri(a, b, c); add_tri(b, e, c)
    if caps:
        for idx, sgn in ((0, -1), (n - 1, 1)):
            if radii[idx] < 1e-6:
                continue
            t = tans[idx]
            ctr = vert(pts[idx], t * sgn, uvf(idx / (n - 1), 0.5))
            ids = [vert(P[rings[idx][k]], t * sgn, uvf(idx / (n - 1), 0.5)) for k in range(sides + 1)]
            for k in range(sides):
                add_tri(ctr, ids[k], ids[k + 1])


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
            ring.append(vert(pc + rad * r, n, cuv(cells[cell], f, k / seg)))
        rings.append(ring)
    for k in range(seg):
        a, b, c, e = rings[0][k], rings[0][k + 1], rings[1][k], rings[1][k + 1]
        add_tri(a, b, c); add_tri(b, e, c)
    if caps:
        for pc, r, sg, f in ((p0, r0, -1, 0.0), (p1, r1, 1, 1.0)):
            if r < 1e-6:
                continue
            ctr = vert(pc, d * sg, cuv(cells[cell], f, 0.5))
            ids = []
            for k in range(seg + 1):
                a = 2 * math.pi * k / seg
                ids.append(vert(pc + (u * math.cos(a) + v * math.sin(a)) * r, d * sg, cuv(cells[cell], f, 0.5 + 0.2 * math.sin(a))))
            for k in range(seg):
                add_tri(ctr, ids[k], ids[k + 1])


def lathe_dir(c, d, profile, seg, uvf, cap_top=None, cap_bottom=None):
    """Surface of revolution about the axis through c along d. profile: [(radius, height along d, v)] bottom -> top."""
    c = V(*c); d = nrm(V(*d)); eu, ev = frame(d)
    rings = []; npts = len(profile)
    for idx, (r, h, v) in enumerate(profile):
        p0 = profile[max(idx - 1, 0)]; p1 = profile[min(idx + 1, npts - 1)]
        dr, dh = p1[0] - p0[0], p1[1] - p0[1]
        ring = []
        for k in range(seg + 1):
            th = 2 * math.pi * k / seg
            rad = eu * math.cos(th) + ev * math.sin(th)
            n = nrm(rad * dh - d * dr)
            ring.append(vert(c + d * h + rad * r, n, uvf(k / seg, v)))
        rings.append(ring)
    for i in range(npts - 1):
        for k in range(seg):
            a, b, cc, e = rings[i][k], rings[i][k + 1], rings[i + 1][k], rings[i + 1][k + 1]
            add_tri(a, b, cc); add_tri(b, e, cc)
    for end, cell, sgn in ((profile[-1], cap_top, 1), (profile[0], cap_bottom, -1)):
        if cell is None:
            continue
        r, h, _ = end
        ctr = vert(c + d * h, d * sgn, cuv(cells[cell], 0.5, 0.5))
        ids = [vert(c + d * h + (eu * math.cos(2 * math.pi * k / seg) + ev * math.sin(2 * math.pi * k / seg)) * r, d * sgn,
                    cuv(cells[cell], 0.5, 0.5)) for k in range(seg + 1)]
        for k in range(seg):
            add_tri(ctr, ids[k], ids[k + 1])


def flat_uv(cell):
    return lambda u, v: cuv(cells[cell], u, v)


def catmull(pts, per=6):
    p = [V(*q) for q in pts]
    ext = [p[0] * 2 - p[1]] + p + [p[-1] * 2 - p[-2]]
    out = []
    for i in range(1, len(ext) - 2):
        p0, p1, p2, p3 = ext[i - 1:i + 3]
        for j in range(per):
            t = j / per
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(p[-1])
    return out


def pyramid(c, s, h, lean, cell):
    """Four-sided steel stud, flat shaded, base centre c (no base face: it sits on the slat)."""
    base = [V(c[0] - s, c[1], c[2] - s), V(c[0] + s, c[1], c[2] - s), V(c[0] + s, c[1], c[2] + s), V(c[0] - s, c[1], c[2] + s)]
    apex = V(c[0] + lean[0], c[1] + h, c[2] + lean[1])
    for k in range(4):
        a, b = base[k], base[(k + 1) % 4]
        n = nrm(np.cross(b - a, apex - a))
        ids = [vert(a, n, cuv(cells[cell], 0.15, 0.1 + 0.2 * k)), vert(b, n, cuv(cells[cell], 0.85, 0.1 + 0.2 * k)),
               vert(apex, n, cuv(cells[cell], 0.5, 0.95))]
        add_tri(*ids)


# ----------------------------------------------------------------------------- layout
CX = -0.30                  # bench centre (the ad post stands to the right on the same pad)
PX0, PX1, PZ0, PZ1, PH = -1.60, 1.60, -0.62, 0.62, 0.08       # concrete pad
HALF = 0.96                 # half length between the frame centre lines
SEAT_Y = 0.455


def pad_uv(k, sg, a, b):
    return None


# concrete pad: planar top, dark-concrete sides
def aabb_pad():
    lo, hi = V(PX0, 0, PZ0), V(PX1, PH, PZ1)
    for (k, sg) in ((1, 1), (0, -1), (0, 1), (2, -1), (2, 1)):
        i, j = (k + 1) % 3, (k + 2) % 3
        n = np.zeros(3); n[k] = sg
        base = lo.copy() if sg < 0 else hi.copy()
        corners = []
        for si, sj in ((0, 0), (1, 0), (1, 1), (0, 1)):
            p = base.copy(); p[i] = lo[i] if si == 0 else hi[i]; p[j] = lo[j] if sj == 0 else hi[j]
            if k == 1:
                uv = ruv('pad', (p[0] - PX0) / (PX1 - PX0), (p[2] - PZ0) / (PZ1 - PZ0))
            else:
                uv = cuv(cells['concrete_dk'], 0.5, 0.5)
            corners.append(vert(p, n, uv))
        add_tri(corners[0], corners[1], corners[2]); add_tri(corners[0], corners[2], corners[3])


aabb_pad()

# ----------------------------------------------------------------------------- frames: two ends and one centre support
for fx, with_arm in ((CX - HALF, True), (CX, False), (CX + HALF, True)):
    for zc in (0.20, -0.40):                                                    # foot plates with an anchor bolt each
        box((fx, PH + 0.012, zc), X, Y, Z, 0.085, 0.012, 0.085, cellf('green_dark'))
        tube((fx, PH + 0.024, zc), (fx, PH + 0.060, zc), 0.020, 0.020, 6, 'bolt')
    bar((fx, PH + 0.02, 0.20), (fx, 0.445, 0.20), 0.042, 0.040, 'green')       # front leg
    bar((fx, PH + 0.02, -0.40), (fx, 0.97, -0.355), 0.050, 0.038, 'green')     # rear leg running up into the backrest
    bar((fx, 0.40, -0.30), (fx, 0.40, 0.21), 0.034, 0.030, 'green_dark')       # seat bracket
    if with_arm:                                                                # scroll armrest, then a boss on the outer face
        arm = catmull([(fx, 0.44, 0.22), (fx, 0.58, 0.27), (fx, 0.72, 0.23), (fx, 0.775, 0.08), (fx, 0.765, -0.10), (fx, 0.70, -0.25)], 2)
        path_tube(arm, 0.036, 8, lambda s, t: cuv(cells['green_hi'], s, t))
        sg = 1 if fx > CX else -1
        lathe_dir((fx + sg * 0.045, 0.30, -0.10), (sg, 0, 0), [(0.075, 0.0, 0), (0.075, 0.012, 0.3), (0.050, 0.030, 1)], 10,
                  flat_uv('green_hi'), cap_top='green_hi')
# long under-seat rails and a low stretcher
bar((CX - HALF, 0.40, 0.19), (CX + HALF, 0.40, 0.19), 0.030, 0.026, 'green_dark')
bar((CX - HALF, 0.40, -0.26), (CX + HALF, 0.40, -0.26), 0.030, 0.026, 'green_dark')
bar((CX - HALF, 0.20, -0.40), (CX + HALF, 0.20, -0.40), 0.030, 0.026, 'green_dark')

# ----------------------------------------------------------------------------- seat slats (cast-iron bench slats)
SLATS_Z = (-0.205, -0.075, 0.055, 0.185)
for zc in SLATS_Z:
    box((CX, SEAT_Y, zc), X, Y, Z, HALF, 0.018, 0.057, cellf('green'))
tube((CX - HALF, SEAT_Y, 0.255), (CX + HALF, SEAT_Y, 0.255), 0.028, 0.028, 8, 'green_hi')         # rolled front lip

# ----------------------------------------------------------------------------- backrest (leaning back 10 degrees)
TILT = -0.17
RB = rx(TILT)
BX, BY, BZ = RB @ X, RB @ Y, RB @ Z
B0 = V(CX, 0.50, -0.27)


def Bp(x, y, z=0.0):
    return B0 + RB @ V(x, y, z)


for ly in (0.09, 0.24, 0.39):
    box(Bp(0, ly), BX, BY, BZ, HALF, 0.062, 0.018, cellf('green'))
tube(Bp(-HALF, 0.465), Bp(HALF, 0.465), 0.026, 0.026, 8, 'green_hi')                                 # top rail

# neon-yellow municipal asset tag, bolted to the upper slat
PLATE_C = Bp(0.0, 0.385, 0.030)
PHX, PHY = 0.45, 0.105


def plate_uv(k, sg, a, b):
    if k == 2 and sg == 1:
        return ruv('barcode', a, 1 - b)
    return cuv(cells['black'], a, b)


box(PLATE_C, BX, BY, BZ, PHX, PHY, 0.010, plate_uv)
for sx in (-1, 1):
    for sy in (-1, 1):
        c = PLATE_C + BX * sx * (PHX - 0.03) + BY * sy * (PHY - 0.03) + BZ * 0.010
        tube(c, c + BZ * 0.016, 0.013, 0.013, 6, 'bolt')

# ----------------------------------------------------------------------------- five oversized chrome divider hoops + steel pyramid studs
HOOP_X = [-0.76, -0.38, 0.0, 0.38, 0.76]
for hx in HOOP_X:
    x = CX + hx
    ctrl = [(x, 0.47, -0.19), (x, 0.58, -0.215), (x, 0.68, -0.16), (x, 0.745, -0.05), (x, 0.755, 0.06), (x, 0.70, 0.17), (x, 0.60, 0.245),
            (x, 0.47, 0.26)]
    path_tube(catmull(ctrl, 2), 0.033, 8, lambda s, t: cuv(cells['chrome'], s, t))
    for zc in (-0.19, 0.26):                                                                           # mounting flange on the slats
        box((x, SEAT_Y + 0.026, zc), X, Y, Z, 0.062, 0.010, 0.050, cellf('steel_stud'))
n_studs = 0
for ri, zc in enumerate((-0.15, -0.045, 0.06, 0.165)):
    for sx in np.arange(-0.90 + (0.0375 if ri % 2 else 0.0), 0.901, 0.075):
        if any(abs(sx - hx) < 0.075 for hx in HOOP_X):
            continue
        jitter = (rng.uniform(-0.012, 0.012), rng.uniform(-0.012, 0.012))
        pyramid((CX + sx, SEAT_Y + 0.018, zc), 0.027, rng.uniform(0.080, 0.115), jitter, 'steel_stud')
        n_studs += 1
print('studs', n_studs)

# ----------------------------------------------------------------------------- sponsor ad panel on a post
AX, AZ = CX + 1.46, -0.08
ADR = ry(-0.42)
AXX, AYY, AZZ = ADR @ X, ADR @ Y, ADR @ Z
tube((AX, PH, AZ), (AX, 0.78, AZ), 0.045, 0.038, 8, 'green')
tube((AX, PH, AZ), (AX, PH + 0.04, AZ), 0.075, 0.075, 8, 'green_dark')
ADC = V(AX, 0.98, AZ)
box(ADC, AXX, AYY, AZZ, 0.33, 0.25, 0.022, cellf('green'))                                         # frame
box(ADC + AZZ * 0.020, AXX, AYY, AZZ, 0.29, 0.21, 0.010,
    lambda k, sg, a, b: ruv('ad', a, 1 - b) if (k == 2 and sg == 1) else cuv(cells['green_dark'], a, b))
for sx in (-1, 1):
    for sy in (-1, 1):
        c = ADC + AXX * sx * 0.31 + AYY * sy * 0.23 + AZZ * 0.024
        tube(c, c + AZZ * 0.016, 0.014, 0.014, 6, 'bolt')

# ----------------------------------------------------------------------------- the pigeon: the only creature the bench was built to welcome
PS = 1.55                                       # pigeon scale (chunky enough to read from the game camera)
PG = V(CX - 0.70, 0.985, -0.31)
PD = nrm(V(0.30, 0.0, 0.95))                    # body axis, tail to chest
PUP = Y
PU = nrm(np.cross(PUP, PD))
prof = []
for i in range(7):
    t = i / 6
    prof.append((PS * (0.070 * math.sqrt(max(1 - (2 * t - 1) ** 2, 0.0)) + 0.004), PS * (-0.10 + 0.20 * t), t))
lathe_dir(PG + PUP * PS * 0.070, PD, prof, 10, flat_uv('pigeon'), cap_top='pigeon', cap_bottom='pigeon')           # plump body
head = PG + PUP * PS * 0.135 + PD * PS * 0.085
hp = [(0.0, -0.040, 0), (0.036, -0.026, 0.25), (0.042, 0.0, 0.5), (0.036, 0.026, 0.75), (0.0, 0.040, 1)]
lathe_dir(head, PUP, [(r * PS, h * PS, v) for r, h, v in hp], 10, flat_uv('pigeon_dark'))                          # round head
lathe_dir(PG + PUP * PS * 0.098 + PD * PS * 0.070, PUP, [(0.050 * PS, -0.014 * PS, 0), (0.056 * PS, 0.0, 0.5), (0.044 * PS, 0.016 * PS, 1)], 10,
          flat_uv('pigeon_neck'), cap_top='pigeon_neck2')                                                          # iridescent neck ring
tube(head + PD * PS * 0.030, head + PD * PS * 0.085 - PUP * PS * 0.008, 0.016 * PS, 0.003, 6, 'orange')            # beak
for sg in (-1, 1):
    box(head + PD * PS * 0.020 + PU * sg * PS * 0.034 + PUP * PS * 0.010, PU, PUP, PD, 0.009, 0.009, 0.009, cellf('red'))   # eyes
box(PG + PUP * PS * 0.075 - PD * PS * 0.115, PU, PUP, PD, 0.040 * PS, 0.008 * PS, 0.040 * PS, cellf('pigeon_dark'))   # tail
for sg in (-1, 1):
    box(PG + PUP * 0.006 + PU * sg * 0.032, PU, PUP, PD, 0.008, 0.008, 0.018, cellf('orange'))                       # feet

# ----------------------------------------------------------------------------- finish
pos = np.array(P); nor = np.array(N); uv = np.array(U); tri = np.array(T)
bmin, bmax = pos.min(0), pos.max(0)
print('verts', len(pos), 'tris', len(tri), 'bbox min', bmin.round(3), 'max', bmax.round(3), 'size', (bmax - bmin).round(3))
assert len(tri) < 3500, 'triangle budget exceeded'
json.dump({'pos': pos.tolist(), 'uv': uv.tolist(), 'tri': tri.tolist(), 'nor': nor.tolist()}, open(OD + '/bench_preview.json', 'w'))
json.dump({'min': bmin.tolist(), 'max': bmax.tolist(), 'tris': int(len(tri))}, open(OD + '/bench_bounds.json', 'w'))

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
