"""Procedural Sparking Utility Pole, written into the fire-basket template DAE (all 3 LODs).

AI-generated asset (procedural Python geometry and textures; no vanilla art is reused; no real company logo or lettering).
usage: build_utilitypole_model.py <basket_template.dae> <out.dae> <out_dir>
Units metres. Origin at the ground at the pole's foot, +Z = front (the placard and flyer side), +Y up.
A weathered dark-brown wooden pole leans about 15 degrees towards +X: pin insulators of blue-green glass on a crossarm with two
braces, a bracket carrying three grey transformer cans (the middle one cooked and smoking), copper cables snapped and dangling (one
trailing across the ground), a red HIGH VOLTAGE placard (bolt symbol, no lettering), stapled flyers, a nest of dead phone wires with
a pair of sneakers and a junction box, a shredded gold Mylar birthday smiley snagged on the crossarm, and painted (not emissive)
cyan-and-gold spark arcs with gold bursts at the cable tips. A dirt mound, asphalt chunks and a scorch mark sit at the foot. (No smoke geometry: the cooked can is painted soot and flames.)
Writes <out_dir>/HC_UtilityPole_BM.png, _NM.png, _PM.png, utilitypole_preview.json (Blender previews) and utilitypole_bounds.json.
Pipeline (see HANDOFF.md / hc_tarp.py): this script -> out.dae; then, with absolute paths,
  Divine.exe -g bg3 -a convert-model -s out.dae -d HC_UtilityPole.GR2 -i dae -o gr2 -e conform --conform-path <vanilla LTS_GEN_Fire_Basket_A.GR2> -l warn
  texconv.exe -nologo -y -f BC3_UNORM -m 0 -o <dir> <png>   (rename the results to .DDS)
Winding convention follows build_tarp_model.py: the right-hand normal of each DAE triangle points opposite to the
vertex normal (BG3 mirrors the DAE); internally triangles are stored outward-CCW.
"""
import sys, re, json, math
import numpy as np
sys.path.insert(0, __file__.replace('\\', '/').rsplit('/', 1)[0])
import utilitypole_paint as paint_mod

TPL, OUT, OD = sys.argv[1:4]
cells, rough = paint_mod.paint(OD + '/HC_UtilityPole_BM.png')
paint_mod.nm_image().save(OD + '/HC_UtilityPole_NM.png')
paint_mod.pm_image(rough).save(OD + '/HC_UtilityPole_PM.png')
rng = np.random.default_rng(20261019)
ruv, cuv = paint_mod.ruv, paint_mod.uv

P, N, U, T = [], [], [], []
XF = {'R': np.eye(3), 'o': np.zeros(3)}          # current placement transform applied to every vertex


def V(*a):
    return np.array(a, float)


def nrm(v):
    l = np.linalg.norm(v)
    return v / l if l > 1e-12 else v


def vert(p, n, uv):
    P.append(XF['R'] @ np.array(p, float) + XF['o']); N.append(XF['R'] @ np.array(n, float)); U.append(uv)
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


LEAN = rz(math.radians(-14.4)) @ rx(math.radians(4.0))      # pole frame -> world; the pole top leans towards +X (and a little +Z)
print('pole tilt from vertical (deg):', round(math.degrees(math.acos((LEAN @ Y)[1])), 2))


def L(p):
    """World position of a point given in the pole frame."""
    return LEAN @ V(*p)


def in_pole():
    XF['R'] = LEAN; XF['o'] = np.zeros(3)


def in_world():
    XF['R'] = np.eye(3); XF['o'] = np.zeros(3)


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
            ids = [vert(P_local(rings[idx][k]), t * sgn, uvf(idx / (n - 1), 0.5)) for k in range(sides + 1)]
            for k in range(sides):
                add_tri(ctr, ids[k], ids[k + 1])


def P_local(index):
    """Inverse of the current placement for an already stored vertex (so a cap can re-use a ring position)."""
    return XF['R'].T @ (P[index] - XF['o'])


def tube(p0, p1, r0, r1, seg, cell, caps=True):
    p0, p1 = V(*p0), V(*p1); d = p1 - p0; Ln = np.linalg.norm(d)
    d = d / Ln; u, v = frame(d)
    rings = []
    for pc, r, f in ((p0, r0, 0.0), (p1, r1, 1.0)):
        ring = []
        for k in range(seg + 1):
            a = 2 * math.pi * k / seg
            rad = u * math.cos(a) + v * math.sin(a)
            n = nrm(rad + d * (r0 - r1) / Ln)
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


def lathe_dir(c, d, profile, seg, uvf, cap_top=None, cap_bottom=None, phase=0.0):
    """Surface of revolution about the axis through c along d. profile: [(radius, height along d, v)] bottom -> top.
    phase rotates the seam (phase = pi puts u = 0.5 on the +frame-u side, i.e. at the front for an upright pole)."""
    c = V(*c); d = nrm(V(*d)); eu, ev = frame(d)
    rings = []; npts = len(profile)
    for idx, (r, h, v) in enumerate(profile):
        p0 = profile[max(idx - 1, 0)]; p1 = profile[min(idx + 1, npts - 1)]
        dr, dh = p1[0] - p0[0], p1[1] - p0[1]
        ring = []
        for k in range(seg + 1):
            th = 2 * math.pi * k / seg + phase
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
        ids = [vert(c + d * h + (eu * math.cos(2 * math.pi * k / seg + phase) + ev * math.sin(2 * math.pi * k / seg + phase)) * r,
                    d * sgn, cuv(cells[cell], 0.5, 0.5)) for k in range(seg + 1)]
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
    pts = [V(*p) for p in pts]
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


def beam(p0, p1, w, h, uvf):
    """Box between two points in the XY plane of the current frame (w along Z, h across the beam)."""
    p0, p1 = V(p0[0], p0[1], 0.0), V(p1[0], p1[1], 0.0); d = p1 - p0; Ln = np.linalg.norm(d); d = d / Ln
    box((p0 + p1) / 2, d, np.cross(Z, d), Z, Ln / 2, h / 2, w / 2, uvf)


def arm_uv(k, sg, a, b):
    return ruv('arm', a, b)


def count(label, start=[0]):
    print('  %-34s %5d tris' % (label, len(T) - start[0])); start[0] = len(T)


# ----------------------------------------------------------------------------- the pole
POLE_LEN = 4.4
Y0 = 0.06


def pole_r(y):
    return 0.195 - 0.070 * (y / POLE_LEN) + (0.030 * max(0.0, 1 - y / 0.55))        # butt swell at the foot


in_pole()
prof = []
for y in (Y0, 0.45, 1.2, 2.0, 2.8, 3.6, 4.1, POLE_LEN):
    prof.append((pole_r(y) * (1 + 0.03 * math.sin(y * 3.1)), y, 1 - y / POLE_LEN))
prof += [(pole_r(POLE_LEN) * 0.82, POLE_LEN + 0.05, 0.0), (0.0, POLE_LEN + 0.10, 0.0)]
lathe_dir((0, 0, 0), (0, 1, 0), prof, 12, lambda u, v: ruv('bark', u, v), phase=math.pi)
count('pole')

# ----------------------------------------------------------------------------- crossarm, braces, bolts
ARM_Y = 4.0
box((0, ARM_Y, 0), X, Y, Z, 1.12, 0.065, 0.075, arm_uv)
for sx in (-1, 1):
    beam((sx * 0.08, ARM_Y - 0.72), (sx * 0.62, ARM_Y - 0.06), 0.05, 0.06, arm_uv)
for bx in (-0.42, 0.42):
    tube((bx, ARM_Y - 0.075, 0.08), (bx, ARM_Y + 0.075, 0.08), 0.03, 0.03, 6, 'steel')
tube((0, ARM_Y - 0.085, 0.0), (0, ARM_Y + 0.085, 0.0), 0.035, 0.035, 6, 'steel')
count('crossarm and braces')

# ----------------------------------------------------------------------------- glass pin insulators
INS = [(-0.95, ARM_Y + 0.065), (-0.50, ARM_Y + 0.065), (0.50, ARM_Y + 0.065), (0.95, ARM_Y + 0.065), (0.0, POLE_LEN + 0.10)]
INS_PROFILE = [(0.030, 0.0, 0.0), (0.085, 0.05, 0.15), (0.090, 0.075, 0.3), (0.045, 0.095, 0.4), (0.070, 0.125, 0.55),
               (0.040, 0.15, 0.7), (0.048, 0.205, 0.85), (0.0, 0.235, 1.0)]
for ix, iy in INS:
    lathe_dir((ix, iy, 0), (0, 1, 0), [(r * 1.35, h * 1.35, v) for r, h, v in INS_PROFILE], 7, lambda u, v: cuv(cells['glass'], u, 0.2 + 0.6 * v))
count('insulators (5)')

# ----------------------------------------------------------------------------- transformer bracket and three cans
CAN_Y = 3.22
box((0, CAN_Y, 0.17), X, Y, Z, 0.86, 0.045, 0.04, arm_uv)
box((0, CAN_Y - 0.0, 0.10), X, Y, Z, 0.05, 0.05, 0.05, arm_uv)
CAN_X = (-0.58, 0.0, 0.58)
for k, cx in enumerate(CAN_X):
    region = 'canburnt' if k == 1 else 'can'
    cprof = [(0.0, 0.0, 1.0), (0.135, 0.0, 1.0), (0.172, 0.05, 0.92), (0.172, 0.55, 0.12), (0.135, 0.60, 0.04), (0.0, 0.62, 0.0)]
    lathe_dir((cx, CAN_Y - 0.66, 0.34), (0, 1, 0), cprof, 10, lambda u, v, r=region: ruv(r, u, v), phase=math.pi)
    box((cx, CAN_Y - 0.03, 0.30), X, Y, Z, 0.045, 0.05, 0.13, cellf('steel_dark'))            # hanger lug to the bracket
    lathe_dir((cx, CAN_Y - 0.04, 0.34), (0, 1, 0), [(0.05, 0.0, 0), (0.042, 0.04, 0.4), (0.032, 0.08, 0.7), (0.0, 0.10, 1)], 6,
              flat_uv('porcelain'))
count('bracket and cans (3)')

# ----------------------------------------------------------------------------- red HIGH VOLTAGE placard, stapled flyers
PY = 2.1
pr = pole_r(PY)
box((0, PY, pr + 0.015), X, Y, Z, 0.09, 0.09, 0.03, cellf('steel_dark'))
box((0, PY, pr + 0.04), X, Y, Z, 0.30, 0.26, 0.014,
    lambda k, sg, a, b: ruv('placard', a, 1 - b) if (k == 2 and sg == 1) else cuv(cells['red'], a, b))
count('placard')


def flyer(idx, y, ang, w=0.22, h=0.34, roll=0.0, curl=0.0):
    """A flyer stapled round the pole's front: a 4-column patch following the pole radius."""
    r = pole_r(y) + 0.008
    cols = 4
    grid = []
    for j in range(cols + 1):
        fj = j / cols
        phi = ang + (fj - 0.5) * w / r
        yc = y + (fj - 0.5) * roll
        out = r + curl * max(0.0, fj - 0.6)
        n = V(math.sin(phi), 0.0, math.cos(phi))
        a = (idx + fj) / 3.0
        grid.append((vert((out * math.sin(phi), yc + h / 2, out * math.cos(phi)), n, ruv('flyers', a, 0.0)),
                     vert((out * math.sin(phi), yc - h / 2, out * math.cos(phi)), n, ruv('flyers', a, 1.0))))
    for j in range(cols):
        t0, b0 = grid[j]; t1, b1 = grid[j + 1]
        add_tri(t0, b0, t1); add_tri(t1, b0, b1)


flyer(0, 1.18, -0.50, roll=0.04)
flyer(1, 1.34, 0.42, roll=-0.05, curl=0.05)
flyer(2, 0.80, 0.0, roll=0.03)
count('flyers (3)')

# ----------------------------------------------------------------------------- ground: dirt mound, asphalt chunks, scorch
in_world()
mound = [(0.55, 0.0, 0), (0.49, 0.05, 0.3), (0.36, 0.12, 0.6), (0.22, 0.20, 0.85), (0.0, 0.22, 1.0)]
lathe_dir((-0.04, 0.0, 0.0), (0, 1, 0), mound, 10, flat_uv('dirt'))
for cx, cz, ang, s in ((-0.55, 0.30, 0.5, 1.0), (0.62, 0.38, -0.7, 0.8), (0.18, 0.62, 0.2, 0.9)):
    box((cx, 0.05 * s, cz), ry(ang) @ X, ry(ang) @ Y, ry(ang) @ Z, 0.16 * s, 0.05 * s, 0.11 * s, cellf('asphalt'))
count('mound and asphalt chunks')


# ----------------------------------------------------------------------------- cables (copper), frayed ends, spark arcs
def ins_tip(i):
    ix, iy = INS[i]
    return L((ix, iy + 0.215 * 1.35, 0.0))


TIPS = []


def cable(pts, r=0.024, per=2):
    c = [V(q[0], max(q[1], r + 0.003), q[2]) for q in catmull(pts, per)]       # never dip into the ground
    path_tube(c, r, 5, lambda s, t: cuv(cells['copper'], s, t))
    end = c[-1]; back = nrm(c[-1] - c[-3])
    for k in range(3):                                                                 # frayed copper strands
        a = 2 * math.pi * k / 3 + 0.4
        splay = back + V(math.cos(a), 0.2 * math.sin(a * 2), math.sin(a)) * 0.55
        stub = end + nrm(splay) * 0.11
        stub[1] = max(stub[1], 0.012)
        tube(end, stub, 0.009, 0.004, 3, 'copper_light', caps=False)
    TIPS.append((end, back))


in_world()
sA, sB, sC, sD, sE = (ins_tip(i) for i in (3, 0, 1, 2, 4))
# A: right outer, snapped, falls to the ground and slithers across it, its end curling up off the floor (the trailing cable)
cable([sA, sA + V(0.14, -0.04, 0.02), sA + V(0.26, -0.32, 0.06), sA + V(0.30, -0.95, 0.12), sA + V(0.20, -1.70, 0.24),
       V(sA[0] + 0.02, 0.55, 0.52), V(sA[0] - 0.20, 0.05, 0.74), V(sA[0] - 0.52, 0.035, 0.98), V(sA[0] - 0.36, 0.035, 1.26),
       V(sA[0] - 0.60, 0.09, 1.44), V(sA[0] - 0.70, 0.24, 1.52)], r=0.032, per=2)
# B: left outer, hangs in a long drooping loop out in front of the left can
cable([sB, sB + V(-0.14, -0.04, 0.04), sB + V(-0.30, -0.30, 0.14), sB + V(-0.38, -0.80, 0.32), sB + V(-0.34, -1.40, 0.52),
       sB + V(-0.22, -1.85, 0.66)], r=0.032, per=2)
# C: left inner, flops forward over the front
cable([sC, sC + V(0.10, -0.04, 0.12), sC + V(0.20, -0.25, 0.35), sC + V(0.28, -0.65, 0.58), sC + V(0.26, -1.10, 0.70)],
      r=0.032, per=2)
# D: right inner, snapped after a short span, swinging out to the right
cable([sD, sD + V(0.20, -0.04, 0.02), sD + V(0.42, -0.22, 0.05), sD + V(0.55, -0.70, 0.08), sD + V(0.55, -1.30, 0.14),
       sD + V(0.45, -1.80, 0.22)], r=0.032, per=2)
# E: top insulator, a stub whipping up and over
cable([sE, sE + V(0.10, 0.06, 0.02), sE + V(0.24, 0.14, 0.04), sE + V(0.40, 0.12, 0.06)], r=0.032, per=2)
count('copper cables (5)')

# ----------------------------------------------------------------------------- spark arcs, painted not emissive
def spark(tip, d, length, hint, amp=0.17, big=1.0):
    d = nrm(V(*d)); n = nrm(np.cross(d, hint)); u = nrm(np.cross(n, d))
    pts = [tip + d * length * i / 6 + u * amp * ((-1) ** i) * (0 if i == 0 else 1) * (1 - 0.08 * i) for i in range(7)]
    wid = [(0.15 - 0.014 * i) * big for i in range(7)]
    uvf = lambda s, t: ruv('spark', s, t)
    strip(pts, wid, [0.0] * 7, uvf, ref=n)
    strip(pts, wid, [0.0] * 7, uvf, fixed_side=n)
    b0 = pts[3]; bd = nrm(d * 0.5 + u * 0.8 + n * 0.1)
    bu = nrm(np.cross(n, bd))
    bp = [b0 + bd * 0.50 * i / 3 + bu * 0.10 * ((-1) ** i) * (0 if i == 0 else 1) for i in range(4)]
    strip(bp, [0.10 * big, 0.08 * big, 0.06 * big, 0.04 * big], [0.0] * 4, uvf, ref=n)
    # gold burst at the cable tip: two crossed 8-point stars
    for nn in (n, nrm(np.cross(n, d))):
        a1 = nrm(np.cross(nn, d)); a2 = nrm(np.cross(nn, a1))
        pts_ring = [tip + (a1 * math.cos(2 * math.pi * k / 8) + a2 * math.sin(2 * math.pi * k / 8)) * (0.21 if k % 2 == 0 else 0.09) * big
                    for k in range(8)]
        for sg in (1, -1):
            ctr = vert(tip, nn * sg, cuv(cells['gold'], 0.5, 0.5))
            ring = [vert(q, nn * sg, cuv(cells['gold'], 0.5, 0.5)) for q in pts_ring + [pts_ring[0]]]
            for k in range(8):
                add_tri(ctr, ring[k], ring[k + 1])


hints = [V(1, 0, 0), V(1, 0, 0), V(0, 0, 1), V(0, 0, 1), V(0, 0, 1)]
dirs = [V(0.15, 0.85, 0.2), V(-0.55, -0.45, 0.6), V(0.7, -0.5, 0.5), V(0.5, -0.7, 0.45), V(0.8, 0.5, 0.3)]
lens = [0.95, 0.8, 0.8, 0.75, 0.65]
for (tip, back), h, dd, ln_ in zip(TIPS, hints, dirs, lens):
    spark(tip, dd, ln_, h, big=1.0 if ln_ > 0.7 else 0.85)
count('spark arcs and bursts (5)')

# scorch mark under the trailing cable's tip
tipA = TIPS[0][0]
lathe_dir((tipA[0], 0.0, tipA[2]), (0, 1, 0), [(0.32, 0.006, 0.5), (0.0, 0.009, 0.5)], 10, flat_uv('soot'))
count('scorch')

# ----------------------------------------------------------------------------- dead phone wires: nest, tails, sneakers, junction box
in_world()
NC = L((0.10, 2.55, 0.26))
for i in range(4):
    e1 = nrm(V(*rng.normal(0, 1, 3))); e2 = nrm(np.cross(e1, V(*rng.normal(0, 1, 3)))); e3 = np.cross(e1, e2)
    ph = rng.uniform(0, 6)
    pts = []
    for k in range(15):
        a = ph + k * 0.95
        pts.append(NC + (e1 * math.cos(a) + e2 * math.sin(a)) * (0.27 - 0.009 * k) + e3 * 0.07 * math.sin(a * 1.7))
    path_tube(pts, 0.017, 3, lambda s, t: cuv(cells['wire_black'], s, t), caps=False)
# tails: one droops, one reaches the ground
path_tube([NC + V(0.18, 0.0, 0.05), NC + V(0.40, -0.05, 0.18), NC + V(0.60, -0.14, 0.28), NC + V(0.82, -0.50, 0.34),
           NC + V(0.90, -1.10, 0.40)], 0.016, 3, lambda s, t: cuv(cells['wire_black'], s, t), caps=False)
path_tube([NC + V(-0.15, -0.05, 0.10), NC + V(-0.30, -0.40, 0.25), NC + V(-0.50, -0.95, 0.45), NC + V(-0.62, -1.55, 0.70),
           V(NC[0] - 0.50, 0.03, 1.02), V(NC[0] - 0.12, 0.03, 1.22), V(NC[0] - 0.36, 0.03, 1.45)], 0.016, 3,
          lambda s, t: cuv(cells['wire_black'], s, t), caps=False)
# a line of staples tying the nest to the pole
path_tube([L((0.0, 2.62, pole_r(2.62) + 0.01)), NC + V(0.0, 0.05, 0.0)], 0.016, 3, lambda s, t: cuv(cells['wire_black'], s, t), caps=False)
path_tube([L((0.0, 2.48, pole_r(2.48) + 0.01)), NC + V(-0.05, -0.05, 0.0)], 0.016, 3, lambda s, t: cuv(cells['wire_black'], s, t), caps=False)
# pair of sneakers knotted together and slung over the nest (laces yellow), hanging toe-down
SS = 1.9
SH = NC + V(0.60, -0.42, 0.30)
path_tube([NC + V(0.60, -0.14, 0.28), SH + V(0.0, 0.10, 0.0)], 0.011, 3, lambda s, t: cuv(cells['lace'], s, t), caps=False)
for side, col, tcol in ((-1, 'shoe_white', 'shoe_pink'), (1, 'shoe_pink', 'shoe_white')):
    fw = nrm(V(0.25 * side, -0.55, 0.30)); up = nrm(np.cross(np.cross(fw, Y), fw)); wd = np.cross(fw, up)
    sc = SH + V(0.07 * side * SS, -0.12 * SS, 0.0)
    box(sc, fw, up, wd, 0.085 * SS, 0.040 * SS, 0.034 * SS, cellf(col))
    box(sc + fw * 0.085 * SS + up * -0.005, fw, up, wd, 0.045 * SS, 0.034 * SS, 0.034 * SS, cellf(tcol))
    box(sc - up * 0.048 * SS, fw, up, wd, 0.115 * SS, 0.010 * SS, 0.038 * SS, cellf('sole'))
    box(sc - fw * 0.085 * SS + up * 0.050 * SS, fw, up, wd, 0.030 * SS, 0.034 * SS, 0.030 * SS, cellf(col))
    path_tube([SH, sc + up * 0.07 * SS - fw * 0.05 * SS], 0.008, 3, lambda s, t: cuv(cells['lace'], s, t), caps=False)
# junction box with a flapping lid, swinging from the other tail
JB = NC + V(-0.58, -1.40, 0.66)
box(JB, X, Y, Z, 0.10, 0.13, 0.055, cellf('box_grey'))
box(JB + V(0.10, 0.12, 0.06), nrm(V(1, 0.3, 0)), nrm(V(-0.3, 1, 0)), Z, 0.09, 0.012, 0.05, cellf('steel_dark'))
count('phone wires, sneakers, box')

# ----------------------------------------------------------------------------- shredded Mylar birthday balloon on the crossarm
in_pole()
BC = V(-0.72, 3.70, 0.17)
BR = 0.34
NS = 16
A0, A1 = math.radians(35), math.radians(325)        # the missing wedge (the bite) is on the right


def bpos(rr, th, z0):
    wob = 1.0 + (0.07 * math.sin(5 * th + 1.0) if rr > 0.9 * BR else 0.0)       # ragged edge
    return V(BC[0] + rr * wob * math.cos(th), BC[1] + rr * wob * math.sin(th) - 0.02 * (1 - math.cos(th)) * (rr / BR),
             BC[2] + z0 * (1 - (rr / BR) ** 2) + 0.012 * math.sin(4 * th) * rr / BR)


rings_r = [0.0, 0.5 * BR, BR]
for face in (1, -1):
    grid = []
    for ri, rr in enumerate(rings_r):
        row = []
        for k in range(NS + 1):
            th = A0 + (A1 - A0) * k / NS
            p = bpos(rr, th, 0.045)
            if face < 0:
                p = p + V(0, 0, -0.01)
            uvp = ruv('balloon', 0.5 + 0.5 * (rr / BR) * math.cos(th), 0.5 - 0.5 * (rr / BR) * math.sin(th))
            row.append(vert(p, V(0, 0, 1.0 * face), uvp))
        grid.append(row)
    for ri in range(2):
        for k in range(NS):
            a, b, c, e = grid[ri][k], grid[ri][k + 1], grid[ri + 1][k], grid[ri + 1][k + 1]
            add_tri(a, b, c); add_tri(b, e, c)
# shreds hanging from the bottom edge
for th_deg, wid, texa, texb, tw in ((236, 0.10, 0.30, 0.55, 2.4), (262, 0.08, 0.45, 0.30, -2.0), (290, 0.09, 0.15, 0.97, 1.8)):
    th = math.radians(th_deg)
    st = bpos(BR, th, 0.045) + V(0, 0, 0.0)
    pts = [st + V(0.03 * math.sin(i * 1.1), -0.11 * i, 0.012 * i + 0.012 * math.sin(i * 1.7)) for i in range(6)]
    strip(pts, [wid * (1 - 0.13 * i) for i in range(6)], [tw * i / 5 for i in range(6)],
          lambda s, t, a=texa, b=texb: ruv('balloon', a + 0.25 * t, b + 0.10 * s), ref=Z)
# curly cyan ribbon from the knot, spiralling down
pts = []
for i in range(20):
    s = i / 19
    pts.append(V(BC[0] + 0.02 + 0.045 * math.cos(s * 14), BC[1] - BR * 0.85 - 0.70 * s, BC[2] + 0.04 + 0.045 * math.sin(s * 14)))
strip(pts, 0.026, [s * 6 for s in np.linspace(0, 1, 20)], lambda s, t: cuv(cells['ribbon_cyan'], s, t), ref=Y)
# a second ribbon end tied round the crossarm
pts = [V(BC[0] + 0.10, ARM_Y + 0.07, 0.08), V(BC[0] + 0.14, ARM_Y + 0.00, 0.12), V(BC[0] + 0.10, ARM_Y - 0.07, 0.09),
       V(BC[0] + 0.02, ARM_Y - 0.03, 0.14), V(BC[0] - 0.02, BC[1] + BR * 0.9, 0.16)]
strip(pts, 0.024, [0.0, 0.4, 0.8, 1.2, 1.6], lambda s, t: cuv(cells['ribbon_violet'], s, t), ref=Z)
count('shredded Mylar balloon')

# ----------------------------------------------------------------------------- finish
pos = np.array(P); nor = np.array(N); uv = np.array(U); tri = np.array(T)
bmin, bmax = pos.min(0), pos.max(0)
print('verts', len(pos), 'tris', len(tri), 'bbox min', bmin.round(3), 'max', bmax.round(3), 'size', (bmax - bmin).round(3))
assert len(tri) < 3500, 'triangle budget exceeded'
assert bmin[1] >= -0.001, ("model dips below the ground", pos[pos[:,1] < -0.01].round(2)[:6].tolist(), np.where(pos[:,1] < -0.01)[0][:4])
json.dump({'pos': pos.tolist(), 'uv': uv.tolist(), 'tri': tri.tolist(), 'nor': nor.tolist()}, open(OD + '/utilitypole_preview.json', 'w'))
json.dump({'min': bmin.tolist(), 'max': bmax.tolist(), 'tris': int(len(tri))}, open(OD + '/utilitypole_bounds.json', 'w'))

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
CP, CN, CT, CB, CU = [x[first] for x in (CP, CN, CT, CB, CU)]; count_ = len(CP)
print('unique DAE corner vertices', count_)

s = open(TPL, encoding='utf-8-sig').read()
fmt = lambda a: ' '.join('%.6f' % x for x in a.ravel())
pidx = ' '.join('%d %d %d %d %d' % (i, i, i, i, i) for i in inv)
for name in ['LTS_GEN_Fire_Basket_A_Mesh', 'LTS_GEN_Fire_Basket_A_Mesh_LOD1', 'LTS_GEN_Fire_Basket_A_Mesh_LOD2']:
    a = s.index('<geometry id="%s-geom"' % name); b = s.index('</geometry>', a); g = s[a:b]
    for key_, arr in [('positions', CP), ('normals', CN), ('tangents', CT), ('binormals', CB), ('uvs0', CU)]:
        g, n_ = re.subn(r'(<float_array id="%s-%s-array" count=")\d+(">)[^<]*(</float_array>)' % (name, key_),
                        lambda m: m.group(1) + str(arr.size) + m.group(2) + fmt(arr) + m.group(3), g); assert n_ == 1
        g, n_ = re.subn(r'(<accessor count=")\d+(" source="#%s-%s-array")' % (name, key_),
                        lambda m: m.group(1) + str(count_) + m.group(2), g); assert n_ == 1
    g, n_ = re.subn(r'<triangles count="\d+">', '<triangles count="%d">' % len(dtri), g); assert n_ == 1
    g, n_ = re.subn(r'(<triangles[^>]*>.*?<p>)[^<]*(</p>)', lambda m: m.group(1) + pidx + m.group(2), g, flags=re.S); assert n_ == 1
    s = s[:a] + g + s[b:]
open(OUT, 'w', encoding='utf-8').write(s)
print('wrote', OUT)
