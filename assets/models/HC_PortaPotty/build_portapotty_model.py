"""Procedural Tipped-Over Festival Porta-Potty, written into the fire-basket template DAE (all 3 LODs).

AI-generated asset (procedural Python geometry and textures; no vanilla art is reused).
usage: build_portapotty_model.py <basket_template.dae> <out.dae> <out_dir>
Units metres. Origin at ground, +Z = front (the open-door side), +Y up. The 2.3 m long turquoise cabin lies on its side along X
(roof end at -X, floor end at +X, ground wall on the floor, door on the +Z face): bent white roof vent pipe, door burst half
open and hanging off one hinge (the other hinges snapped), toilet seat tipped inside, toilet paper unspooling out of the
doorway in a long ribbon to a roll lying in the yard, neon blue / acid green puddle with bubbles and a red cup, stink lines
with flies, a smiley sticker on the upper wall, a hand-sanitizer pump on the door-frame wall, an 'out of order' board (crossed
circle, no lettering) and a festival wristband on the door handle.
Writes <out_dir>/HC_PortaPotty_BM.png, _NM.png, _PM.png, portapotty_preview.json (Blender previews) and portapotty_bounds.json.
Pipeline (see HANDOFF.md / hc_tarp.py): this script -> out.dae; then, with absolute paths,
  Divine.exe -g bg3 -a convert-model -s out.dae -d HC_PortaPotty.GR2 -i dae -o gr2 -e conform --conform-path <vanilla LTS_GEN_Fire_Basket_A.GR2> -l warn
  texconv.exe -nologo -y -f BC3_UNORM -m 0 -o <dir> <png>   (rename the results to .DDS)
Winding convention follows build_tarp_model.py: the right-hand normal of each DAE triangle points opposite to the
vertex normal (BG3 mirrors the DAE); internally triangles are stored outward-CCW.
"""
import sys, re, json, math
import numpy as np
sys.path.insert(0, __file__.replace('\\', '/').rsplit('/', 1)[0])
import portapotty_paint as paint_mod

TPL, OUT, OD = sys.argv[1:4]
cells, rough = paint_mod.paint(OD + '/HC_PortaPotty_BM.png')
paint_mod.nm_image().save(OD + '/HC_PortaPotty_NM.png')
paint_mod.pm_image(rough).save(OD + '/HC_PortaPotty_PM.png')
rng = np.random.default_rng(20261018)
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


def rz(a):
    c, s = math.cos(a), math.sin(a); return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


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


# ----------------------------------------------------------------------------- world-planar mapping for the cabin plastic
XMIN, XLEN, YMAX, YLEN, ZMIN, ZLEN = -1.18, 2.36, 1.2, 1.2, -0.62, 1.24


def planar(region, k, sg, p):
    x, y, z = p
    if k == 2:
        a = (x - XMIN) / XLEN; b = (YMAX - y) / YLEN
        if sg < 0:
            a = 1 - a
    elif k == 1:
        a = (x - XMIN) / XLEN; b = (z - ZMIN) / ZLEN
        if sg < 0:
            b = 1 - b
    else:
        a = ((ZMAX_ - z) if sg > 0 else (z - ZMIN)) / XLEN; b = (YMAX - y) / YLEN
    return ruv(region, a, b)


ZMAX_ = 0.62


def aabb(lo, hi, faces):
    """Axis-aligned flat box. faces: {(axis, sign): region or cell name}; regions map world-planar, cells map flat."""
    lo, hi = V(*lo), V(*hi)
    for (k, sg), name in faces.items():
        i, j = (k + 1) % 3, (k + 2) % 3
        n = np.zeros(3); n[k] = sg
        base = lo.copy() if sg < 0 else hi.copy()
        corners = []
        for si, sj in ((0, 0), (1, 0), (1, 1), (0, 1)):
            p = base.copy(); p[i] = lo[i] if si == 0 else hi[i]; p[j] = lo[j] if sj == 0 else hi[j]
            uv = cuv(cells[name], 0.5, 0.5) if name in cells else planar(name, k, sg, p)
            corners.append(vert(p, n, uv))
        add_tri(corners[0], corners[1], corners[2]); add_tri(corners[0], corners[2], corners[3])


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
        if i == 0:
            first = (u.copy(), v.copy())
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


def strip(pts, width, twists, uvf, ref=None, fixed_side=None):
    """Flat double-sided ribbon along a polyline; twists[i] rotates it about the path tangent (radians)."""
    n = len(pts); sides = []
    for i in range(n):
        t = nrm(pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)])
        s0 = np.cross(t, Y if ref is None else ref) if fixed_side is None else np.array(fixed_side, float)
        s0 = nrm(s0) if np.linalg.norm(s0) > 1e-6 else X
        al = twists[i]
        s = s0 * math.cos(al) + np.cross(t, s0) * math.sin(al)
        sides.append((nrm(s), nrm(np.cross(s, t))))
    for sign in (1, -1):
        ids = []
        for i in range(n):
            s, nn = sides[i]; w = width[i] if not np.isscalar(width) else width
            ids.append((vert(pts[i] - s * w / 2, nn * sign, uvf(i / (n - 1), 0.0)),
                        vert(pts[i] + s * w / 2, nn * sign, uvf(i / (n - 1), 1.0))))
        for i in range(n - 1):
            a, b = ids[i]; c, e = ids[i + 1]
            add_tri(a, b, c); add_tri(b, e, c)


# ----------------------------------------------------------------------------- cabin shell
X0, X1 = -1.12, 1.15
T_ = 0.045
YT = 1.2
ZB, ZF = -0.6, 0.6
OPEN_X0, OPEN_X1, OPEN_Y0, OPEN_Y1 = -0.72, 0.95, 0.30, 1.05

aabb((X0, 0, ZB), (X1, T_, ZF), {(1, 1): 'inner'})                                         # ground wall (floor of the tipped cabin)
aabb((X0, YT - T_, ZB), (X1, YT, ZF), {(1, 1): 'top', (1, -1): 'inner'})                  # upper wall: smiley sticker outside
aabb((X0, 0, ZB), (X1, YT, ZB + T_), {(2, -1): 'wall', (2, 1): 'inner'})                  # back wall
aabb((X1 - T_, 0, ZB), (X1, YT, ZF), {(0, 1): 'wall', (0, -1): 'inner'})                  # floor end
aabb((-1.18, 0, -0.62), (X0, 1.23, 0.62), {(0, -1): 'roof', (0, 1): 'inner', (1, 1): 'roof', (2, 1): 'roof', (2, -1): 'roof'})   # roof cap
aabb((-1.20, 0.30, -0.45), (-1.18, 0.34, 0.45), {(0, -1): 'white_pipe', (1, 1): 'white_pipe'})   # roof ribs
aabb((-1.20, 0.86, -0.45), (-1.18, 0.90, 0.45), {(0, -1): 'white_pipe', (1, 1): 'white_pipe'})
aabb((X0, 0, ZF - T_), (X1, OPEN_Y0, ZF), {(2, 1): 'front', (1, 1): 'wall'})                # door-frame wall pieces
aabb((X0, OPEN_Y1, ZF - T_), (X1, YT, ZF), {(2, 1): 'front', (1, -1): 'wall'})
aabb((X0, OPEN_Y0, ZF - T_), (OPEN_X0, OPEN_Y1, ZF), {(2, 1): 'front', (0, 1): 'wall'})
aabb((OPEN_X1, OPEN_Y0, ZF - T_), (X1, OPEN_Y1, ZF), {(2, 1): 'front', (0, -1): 'wall'})
# door stop / frame lip, a darker proud rim just inside the opening
aabb((OPEN_X0, OPEN_Y0, ZF), (OPEN_X1, OPEN_Y0 + 0.035, ZF + 0.022), {(2, 1): 'turq_dark', (1, 1): 'turq_dark'})
aabb((OPEN_X0, OPEN_Y1 - 0.035, ZF), (OPEN_X1, OPEN_Y1, ZF + 0.022), {(2, 1): 'turq_dark', (1, -1): 'turq_dark'})
aabb((OPEN_X0, OPEN_Y0 + 0.035, ZF), (OPEN_X0 + 0.035, OPEN_Y1 - 0.035, ZF + 0.022), {(2, 1): 'turq_dark', (0, 1): 'turq_dark'})
aabb((OPEN_X1 - 0.035, OPEN_Y0 + 0.035, ZF), (OPEN_X1, OPEN_Y1 - 0.035, ZF + 0.022), {(2, 1): 'turq_dark', (0, -1): 'turq_dark'})

# ----------------------------------------------------------------------------- interior: tipped toilet, seat and a roll on the wall
aabb((0.55, 0.05, -0.58), (1.10, 1.15, -0.10), {(0, -1): 'white_pipe', (2, 1): 'white_pipe', (1, 1): 'white_pipe', (1, -1): 'white_pipe'})
SEAT_C = (0.55, 0.60, -0.34)
lathe_dir(SEAT_C, (-1, 0, 0), [(0.21, 0.0, 0), (0.21, 0.035, 0.3), (0.14, 0.04, 0.6), (0.13, 0.0, 1)], 14,
          flat_uv('seat_white'), cap_bottom=None)
lathe_dir(SEAT_C, (-1, 0, 0), [(0.0, -0.17, 0), (0.06, -0.15, 0.3), (0.11, -0.08, 0.6), (0.13, 0.0, 1)], 14, flat_uv('seat_dark'))
lathe_dir(SEAT_C, (-1, 0, 0), [(0.0, -0.10, 0), (0.095, -0.10, 1)], 14, flat_uv('bowl_blue'), cap_top='bowl_blue')
aabb((0.20, 0.55, -0.585), (0.40, 0.85, -0.56), {(2, 1): 'pipe_grey'})                         # tissue holder plate
lathe_dir((0.30, 0.55, -0.50), (0, 1, 0), [(0.075, 0.0, 0), (0.075, 0.17, 1)], 12,
          lambda u, v: ruv('tproll', u, v), cap_top='tp_core', cap_bottom='tp_core')

# ----------------------------------------------------------------------------- the door leaf, burst half open off one hinge
H = V(0.95, 1.05, 0.60)
TH, PH, PS = math.radians(50), math.radians(18), math.radians(10)
R = rz(PS) @ ry(PH) @ rx(-TH)


def L(d):
    return H + R @ V(*d)


LAX, LAY, LAZ = R @ X, R @ Y, R @ Z
LEAF_C = (-0.835, -0.375, 0.0)


def leaf_uv(k, sg, a, b):
    if k == 2 and sg == 1:
        return ruv('door_out', a, 1 - b)
    if k == 2 and sg == -1:
        return ruv('door_in', 1 - a, 1 - b)
    return cuv(cells['turq_dark'], a, b)


box(L(LEAF_C), LAX, LAY, LAZ, 0.835, 0.375, 0.02, leaf_uv)
# handle: two posts and a bar on the outside, near the free edge, with a neon festival wristband around it
for dx in (-1.00, -0.70):
    box(L((dx, -0.60, 0.045)), LAX, LAY, LAZ, 0.012, 0.012, 0.025, cellf('handle_black'))
box(L((-0.85, -0.60, 0.075)), LAX, LAY, LAZ, 0.17, 0.014, 0.014, cellf('handle_black'))
band = []
for k in range(11):
    a = 2 * math.pi * k / 10
    band.append(L((-0.85 + 0.01 * math.cos(a * 2) * 0.0, -0.60 + 0.052 * math.cos(a), 0.075 + 0.052 * math.sin(a))))
path_tube(band, 0.013, 4, lambda s, t: cuv(cells['band_pink'], s, t), caps=False)
# hinges: the cabin side has two knuckles around the one live leaf knuckle; the two others snapped off
HL = V(0.0, 1.05, 0.62)
for x0, x1 in ((0.80, 0.945), (0.40, 0.55)):
    tube((x0, 1.05, 0.625), (x1, 1.05, 0.625), 0.028, 0.028, 8, 'hinge_steel')
    box((x0 / 2 + x1 / 2, 1.0, 0.608), X, Y, Z, (x1 - x0) / 2, 0.035, 0.012, cellf('hinge_steel'))
p0, p1 = L((-0.38, 0.0, 0.025)), L((-0.17, 0.0, 0.025))
tube(p0, p1, 0.028, 0.028, 8, 'hinge_steel')
box(L((-0.275, -0.05, 0.03)), LAX, LAY, LAZ, 0.105, 0.04, 0.008, cellf('hinge_steel'))
tube((-0.05, 1.05, 0.625), (-0.12, 1.07, 0.625), 0.026, 0.020, 8, 'hinge_steel')            # snapped knuckle stub on the frame
path_tube([L((-1.05, -0.04, 0.03)), L((-1.12, -0.12, 0.10)), L((-1.10, -0.20, 0.17))], [0.026, 0.022, 0.015], 7,
          lambda s, t: cuv(cells['hinge_steel'], s, t))                                      # bent strap hanging off the leaf
box(L((-1.40, -0.04, 0.0)), LAX, LAY, LAZ, 0.045, 0.045, 0.021, cellf('rust'))               # torn plastic where the hinge ripped

# ----------------------------------------------------------------------------- roof vent pipe, kinked
VENT = [(-1.20, 0.95, -0.40), (-1.40, 0.96, -0.40), (-1.55, 1.01, -0.39), (-1.62, 1.13, -0.34), (-1.70, 1.30, -0.26), (-1.78, 1.50, -0.16)]
path_tube(VENT, [0.050, 0.050, 0.050, 0.050, 0.050, 0.050], 10, lambda s, t: cuv(cells['white_pipe'], s, t))
tube((-1.545, 1.0, -0.392), (-1.585, 1.045, -0.382), 0.068, 0.068, 10, 'pipe_grey')         # crumple collar at the kink
tube((-1.76, 1.47, -0.17), (-1.80, 1.54, -0.15), 0.075, 0.070, 10, 'pipe_grey')             # vent hood
box((-1.20, 0.95, -0.40), X, Y, Z, 0.035, 0.09, 0.09, cellf('white_pipe'))

# ----------------------------------------------------------------------------- hand-sanitizer pump on the door-frame wall
SZ = ZF + 0.012
box((-0.92, 0.65, SZ), X, Y, Z, 0.17, 0.10, 0.012, cellf('pipe_grey'))
box((-0.90, 0.65, SZ + 0.05), X, Y, Z, 0.115, 0.05, 0.038,
    lambda k, sg, a, b: ruv('label', a, 1 - b) if (k == 2 and sg == 1) else cuv(cells['sani_bottle'], a, b))
tube((-1.015, 0.65, SZ + 0.05), (-1.07, 0.65, SZ + 0.05), 0.02, 0.016, 8, 'sani_cap')
tube((-1.07, 0.65, SZ + 0.05), (-1.07, 0.65, SZ + 0.115), 0.011, 0.011, 6, 'sani_cap')
tube((-1.07, 0.65, SZ + 0.115), (-1.085, 0.65, SZ + 0.15), 0.014, 0.010, 6, 'sani_cap')
path_tube([(-1.085, 0.645, SZ + 0.15), (-1.085, 0.60, SZ + 0.15), (-1.085, 0.56, SZ + 0.15)], [0.008, 0.007, 0.011], 6,
          lambda s, t: cuv(cells['sani_gel'], s, t))                                           # gel dripping down

# ----------------------------------------------------------------------------- toxic puddle with a polar map
PCX, PCZ, PRX, PRZ = 0.05, 1.30, 1.10, 0.85
NA = 30
RINGS = (0.0, 0.34, 0.68, 1.0)


def blob_r(th):
    r = 1 + 0.20 * math.sin(3 * th + 0.7) + 0.12 * math.sin(5 * th + 2.1) + 0.08 * math.sin(2 * th)
    r += 0.34 * math.exp(-((th - math.pi / 2 + 0.25) / 0.38) ** 2) + 0.25 * math.exp(-((th - math.pi + 0.2) / 0.3) ** 2)
    return r


def pud_pos(th, f):
    r = blob_r(th) * f
    return V(PCX + PRX * r * math.cos(th), 0.006 + 0.012 * (1 - f), PCZ + PRZ * r * math.sin(th))


grid = [[None] * (NA + 1) for _ in RINGS]
for ri, f in enumerate(RINGS):
    for k in range(NA + 1):
        th = 2 * math.pi * (k % NA) / NA
        if ri == 0:
            th_c = 2 * math.pi * (k + 0.5) / NA
            grid[ri][k] = vert(pud_pos(th_c, 0.0), Y, ruv('puddle', (k + 0.5) / NA, 0.0))
        else:
            grid[ri][k] = vert(pud_pos(th, f), Y, ruv('puddle', k / NA, f))
for ri in range(len(RINGS) - 1):
    for k in range(NA):
        a, b, c, e = grid[ri][k], grid[ri][k + 1], grid[ri + 1][k], grid[ri + 1][k + 1]
        if ri == 0:
            add_tri(a, c, e)
        else:
            add_tri(a, c, b); add_tri(b, c, e)

# bubbles (bright toxic spheres) and a red solo cup lying in the puddle
BUBBLES = [(0.52, 1.02, 0.10), (-0.42, 1.52, 0.13), (0.88, 1.50, 0.07), (-0.78, 1.14, 0.08), (0.22, 1.78, 0.06),
           (-0.15, 1.02, 0.05), (0.66, 1.80, 0.11)]
for bx, bz, br in BUBBLES:
    prof = [(br * math.cos(math.radians(a)), 0.006 + br * 0.85 * (1 + math.sin(math.radians(a))), (90 - a) / 180.0)
            for a in (-90, -45, 0, 45, 90)]
    lathe_dir((bx, 0.0, bz), (0, 1, 0), prof, 8, lambda u, v: ruv('bubble', u, v))
CUP_C = V(0.72, 0.085, 1.25); CUP_D = nrm(V(0.9, 0.28, 0.32))
lathe_dir(CUP_C - CUP_D * 0.06, CUP_D, [(0.030, 0.0, 0), (0.034, 0.045, 0.5), (0.046, 0.118, 1)], 12, flat_uv('red'),
          cap_bottom='red')
lathe_dir(CUP_C - CUP_D * 0.06, CUP_D, [(0.0, 0.112, 0), (0.040, 0.112, 1)], 12, flat_uv('cup_white'))
lathe_dir(CUP_C - CUP_D * 0.06, CUP_D, [(0.0305, 0.012, 0), (0.0335, 0.020, 1)], 12, flat_uv('cup_white'))

# ----------------------------------------------------------------------------- toilet paper: ribbon from the doorway to a roll in the yard
TP = [(0.30, 0.60, -0.42), (0.28, 0.54, -0.05), (0.20, 0.46, 0.34), (0.12, 0.372, 0.60), (0.08, 0.30, 0.69),
      (0.03, 0.12, 0.78), (-0.02, 0.045, 0.92), (-0.14, 0.04, 1.14), (-0.34, 0.06, 1.36), (-0.42, 0.26, 1.56),
      (-0.24, 0.36, 1.74), (0.06, 0.16, 1.86), (0.34, 0.04, 1.98), (0.52, 0.045, 2.20), (0.36, 0.04, 2.44), (0.08, 0.04, 2.62)]
TP_TW = [0.0, 0.0, 0.0, 0.0, 0.0, 0.3, 0.0, 0.0, 0.7, 1.5, 2.4, 1.2, 0.0, 0.0, 0.0, 0.0]
pts = catmull(TP, 6)
per = 6
tw = []
for i in range(len(TP) - 1):
    for j in range(per):
        tw.append(TP_TW[i] + (TP_TW[i + 1] - TP_TW[i]) * j / per)
tw.append(TP_TW[-1])
dl = sum(np.linalg.norm(pts[i + 1] - pts[i]) for i in range(len(pts) - 1))
print('tp ribbon length', round(dl, 2))
strip(pts, 0.15, tw, lambda s, t: ruv('tp', s, t))
lathe_dir((-0.10, 0.135, 2.64), (1, 0, 0), [(0.125, 0.0, 0), (0.125, 0.13, 1)], 14, lambda u, v: ruv('tproll', u, v),
          cap_top='tp_core', cap_bottom='tp_core')
tube((-0.10, 0.135, 2.64), (0.03, 0.135, 2.64), 0.04, 0.04, 8, 'tp_core')

# ----------------------------------------------------------------------------- stink lines and flies
# three thin S-curved wisps rising from the puddle and one above the vent: one sine wave each, no twist. Each wisp is two flat
# ribbons crossed at 90 degrees along the same centreline, so it reads as a wavy line from every preview angle.
STINK = [((-0.40, 1.12), 0.30, 1.50, 0.0, 0.0), ((0.28, 1.42), 0.30, 1.60, 0.7, math.pi), ((0.72, 1.05), 0.30, 1.45, -0.6, 0.0),
         ((-1.78, -0.16), 1.58, 2.10, 0.3, math.pi)]
for (bx, bz), y0, y1, yw, ph in STINK:
    dirx = V(math.cos(yw), 0, math.sin(yw)); plane_n = V(-math.sin(yw), 0, math.cos(yw))
    pts_s, wid = [], []
    for i in range(17):
        s_ = i / 16
        pts_s.append(V(bx, y0 + (y1 - y0) * s_, bz) + dirx * (0.11 * math.sin(2 * math.pi * s_ + ph)))
        wid.append(0.05 * (1 - 0.55 * s_) + 0.01)
    strip(pts_s, wid, [0.0] * 17, lambda s, t: ruv('stink', s, t), ref=plane_n)
    strip(pts_s, wid, [0.0] * 17, lambda s, t: ruv('stink', s, t), fixed_side=plane_n)
for _ in range(9):
    c = V(rng.uniform(-0.6, 0.9), rng.uniform(0.5, 1.7), rng.uniform(0.8, 1.6)); r = 0.016
    ids = [V(r, 0, 0), V(-r, 0, 0), V(0, r * 0.8, 0), V(0, -r * 0.8, 0), V(0, 0, r), V(0, 0, -r)]
    for ia, ib, ic in ((0, 2, 4), (2, 1, 4), (1, 3, 4), (3, 0, 4), (2, 0, 5), (1, 2, 5), (3, 1, 5), (0, 3, 5)):
        vs = [c + ids[ia], c + ids[ib], c + ids[ic]]
        n = nrm(np.cross(vs[1] - vs[0], vs[2] - vs[0]))
        a_, b_, c_ = [vert(v_, n, cuv(cells['black'], 0.5, 0.5)) for v_ in vs]
        add_tri(a_, b_, c_)

# ----------------------------------------------------------------------------- 'out of order' board: a plank on a stake, crossed-circle symbol
S = V(-1.38, 0.012, 0.98)
RG = ry(math.radians(28)) @ rx(math.radians(-11))


def G(d):
    return S + RG @ V(*d)


GX, GY, GZ = RG @ X, RG @ Y, RG @ Z
box(G((0, 0.52, -0.01)), GX, GY, GZ, 0.022, 0.52, 0.014, cellf('wood_dark'))
box(G((0, 0.80, 0.022)), GX, GY, GZ, 0.27, 0.21, 0.014,
    lambda k, sg, a, b: ruv('sign', a, 1 - b) if (k == 2 and sg == 1) else cuv(cells['wood'], a, b))
for nx, ny in ((-0.22, 0.97), (0.22, 0.97), (-0.22, 0.63), (0.22, 0.63)):
    tube(G((nx, ny, 0.036)), G((nx, ny, 0.046)), 0.012, 0.010, 6, 'nail')

# caution tape (diagonal yellow and black stripes, no lettering) sagging from the sign to the roof end of the cabin
tape_pts = catmull([G((0.27, 0.95, 0.04)), V(-1.30, 0.78, 0.84), V(-1.24, 0.90, 0.70), V(-1.19, 0.99, 0.60)], 5)
strip(tape_pts, 0.09, [0.5 * math.sin(i * 0.9) for i in range(len(tape_pts))],
      lambda s, t: ruv('tape', s, t))

# ----------------------------------------------------------------------------- finish
pos = np.array(P); nor = np.array(N); uv = np.array(U); tri = np.array(T)
bmin, bmax = pos.min(0), pos.max(0)
print('verts', len(pos), 'tris', len(tri), 'bbox min', bmin.round(3), 'max', bmax.round(3), 'size', (bmax - bmin).round(3))
assert len(tri) < 3500, 'triangle budget exceeded'
json.dump({'pos': pos.tolist(), 'uv': uv.tolist(), 'tri': tri.tolist(), 'nor': nor.tolist()}, open(OD + '/portapotty_preview.json', 'w'))
json.dump({'min': bmin.tolist(), 'max': bmax.tolist(), 'tris': int(len(tri))}, open(OD + '/portapotty_bounds.json', 'w'))

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
