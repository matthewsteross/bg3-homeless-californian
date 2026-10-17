"""Procedural Evicted Studio Spin Bike, written into the fire-basket template DAE (all 3 LODs).

AI-generated asset (procedural Python geometry and textures; no vanilla art is reused; the brand "SoulCyclone" is invented).
usage: build_spinbike_model.py <basket_template.dae> <out.dae> <out_dir>
Units metres. Origin at ground, +Z = front (the rider/saddle side, so the tablet screen and the eviction notice face +Z), +Y up.
The bike (about 1.2 m long, 1.65 m tall with the tablet) stands on a violet yoga mat that has been dragged to the curb:
matte millennial-pink angular frame, polished chrome flywheel guards, handlebars and seat post, a tilted tablet console with the
neon "RIDE OR DIE 98%" screen, a water bottle in a cage on the seat tube, clip-in cycling shoes dangling by their laces from the
left pedal, a sweaty towel over the handlebar, a healing crystal on the right grip, a sweat puddle and a laminated EVICTION
NOTICE taped to the saddle.
Writes <out_dir>/HC_SpinBike_BM.png, _NM.png, _PM.png, spinbike_preview.json (Blender previews) and spinbike_bounds.json.
Pipeline (see HANDOFF.md / hc_tarp.py): this script -> out.dae; then, with absolute paths,
  Divine.exe -g bg3 -a convert-model -s out.dae -d HC_SpinBike.GR2 -i dae -o gr2 -e conform --conform-path <vanilla LTS_GEN_Fire_Basket_A.GR2> -l warn
  texconv.exe -nologo -y -f BC3_UNORM -m 0 -o <dir> <png>   (rename the results to .DDS)
Winding convention follows build_tarp_model.py: the right-hand normal of each DAE triangle points opposite to the
vertex normal (BG3 mirrors the DAE); internally triangles are stored outward-CCW.
"""
import sys, re, json, math
import numpy as np
sys.path.insert(0, __file__.replace('\\', '/').rsplit('/', 1)[0])
import spinbike_paint as paint_mod

TPL, OUT, OD = sys.argv[1:4]
cells, rough = paint_mod.paint(OD + '/HC_SpinBike_BM.png')
paint_mod.nm_image().save(OD + '/HC_SpinBike_NM.png')
paint_mod.pm_image(rough).save(OD + '/HC_SpinBike_PM.png')
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


def abox(c, h, cell):
    """Axis-aligned box from centre and half sizes, one palette cell."""
    box(c, X, Y, Z, h[0], h[1], h[2], cellf(cell))


def beam(p0, p1, hw, hh, cell):
    """Rectangular beam between two points (width hw across, height hh), one palette cell."""
    hw, hh = hw * 1.3, hh * 1.3                                                                # a chunkier frame reads better from far away
    p0, p1 = V(*p0), V(*p1); d = p1 - p0; L = np.linalg.norm(d); d = d / L
    up = Y if abs(d @ Y) < 0.95 else X
    side = nrm(np.cross(d, up)); ay = np.cross(side, d)
    box((p0 + p1) / 2, d, ay, side, L / 2, hh, hw, cellf(cell))


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


def disc(c, d, r, region, dome=(0.016, 0.011, 0.005, 0.0), fr=(0.0, 0.5, 0.85, 1.0), seg=32):
    """Slightly domed disc facing d, planar-polar mapped onto a square region (the chrome flywheel guard)."""
    c = V(*c); d = nrm(V(*d)); eu, ev = frame(d); rings = []
    for f, h in zip(fr, dome):
        ring = []
        for k in range(seg + 1):
            th = 2 * math.pi * k / seg
            cu, cv = math.cos(th) * f, math.sin(th) * f
            ring.append(vert(c + d * h + (eu * cu + ev * cv) * r, d, ruv(region, 0.5 + 0.5 * cu, 0.5 - 0.5 * cv)))
        rings.append(ring)
    for i in range(len(fr) - 1):
        for k in range(seg):
            a, b, cc, e = rings[i][k], rings[i][k + 1], rings[i + 1][k], rings[i + 1][k + 1]
            if i == 0:
                add_tri(a, cc, e)
            else:
                add_tri(a, cc, b); add_tri(b, cc, e)


def loft(secs, R, origin, top, side, bot):
    """Box loft. secs = [(s, half_width, y0, y1)] along local x; local y up, local z across. Caps both ends."""
    R = np.array(R, float); origin = V(*origin)
    W = lambda s, y, z: origin + R @ V(s, y, z)
    for i in range(len(secs) - 1):
        (s0, w0, a0, b0), (s1, w1, a1, b1) = secs[i], secs[i + 1]
        mid = W((s0 + s1) / 2, (a0 + b0 + a1 + b1) / 4, 0)
        quads = (
            (top, [W(s0, b0, -w0), W(s0, b0, w0), W(s1, b1, w1), W(s1, b1, -w1)]),
            (bot, [W(s0, a0, -w0), W(s0, a0, w0), W(s1, a1, w1), W(s1, a1, -w1)]),
            (side, [W(s0, a0, w0), W(s0, b0, w0), W(s1, b1, w1), W(s1, a1, w1)]),
            (side, [W(s0, a0, -w0), W(s0, b0, -w0), W(s1, b1, -w1), W(s1, a1, -w1)]),
        )
        for cell, q in quads:
            n = nrm(np.cross(q[1] - q[0], q[2] - q[0]))
            if n @ (sum(q) / 4 - mid) < 0:
                n = -n
            ids = [vert(p, n, cuv(cells[cell], (0, 1, 1, 0)[j], (0, 0, 1, 1)[j])) for j, p in enumerate(q)]
            add_tri(ids[0], ids[1], ids[2]); add_tri(ids[0], ids[2], ids[3])
    for idx, sgn in ((0, -1), (len(secs) - 1, 1)):
        s, w, a, b = secs[idx]
        q = [W(s, a, -w), W(s, a, w), W(s, b, w), W(s, b, -w)]
        n = nrm(R @ V(sgn, 0, 0))
        ids = [vert(p, n, cuv(cells[side], 0.5, 0.5)) for p in q]
        add_tri(ids[0], ids[1], ids[2]); add_tri(ids[0], ids[2], ids[3])


# ============================================================================= yoga mat the bike was dragged across
MX0, MX1, MZ0, MZ1, MY = -0.45, 0.45, -1.18, 0.98, 0.016
mat_corners = [(MX0, MZ0), (MX1, MZ0), (MX1, MZ1), (MX0, MZ1)]


def mat_uv(x, z):
    return ruv('mat', (z - MZ0) / (MZ1 - MZ0), (x - MX0) / (MX1 - MX0))


quad = [vert((x, MY, z), Y, mat_uv(x, z)) for x, z in mat_corners]
add_tri(quad[0], quad[3], quad[2]); add_tri(quad[0], quad[2], quad[1])
for (x0, z0), (x1, z1), n in (((MX0, MZ0), (MX1, MZ0), -Z), ((MX1, MZ0), (MX1, MZ1), X), ((MX1, MZ1), (MX0, MZ1), Z), ((MX0, MZ1), (MX0, MZ0), -X)):
    ids = [vert(p, n, cuv(cells['mat_edge'], 0.5, 0.5)) for p in ((x0, 0, z0), (x1, 0, z1), (x1, MY, z1), (x0, MY, z0))]
    add_tri(ids[0], ids[1], ids[2]); add_tri(ids[0], ids[2], ids[3])
# the far end of the mat has curled itself into a roll
tube((MX0, 0.052, MZ0 - 0.04), (MX1, 0.052, MZ0 - 0.04), 0.052, 0.052, 12, 'mat_edge')

# ============================================================================= frame: stabiliser feet, beam, uprights
beam((0, 0.14, -0.57), (0, 0.14, 0.65), 0.05, 0.05, 'pink')                                       # main beam
abox((0, 0.055, 0.62), (0.31, 0.045, 0.055), 'pink')                                              # rear foot (saddle end)
abox((0, 0.055, -0.55), (0.32, 0.045, 0.055), 'pink')                                             # front foot
for sx in (-1, 1):
    abox((sx * 0.325, 0.055, 0.62), (0.025, 0.05, 0.06), 'rubber')                                # levelling feet
    abox((sx * 0.335, 0.055, -0.55), (0.025, 0.05, 0.06), 'rubber')
    tube((sx * 0.31, 0.062, -0.63), (sx * 0.37, 0.062, -0.63), 0.052, 0.052, 12, 'wheel')       # transport wheels
beam((0, 0.16, 0.37), (0, 1.02, 0.31), 0.052, 0.058, 'pink')                                      # seat tube
beam((0, 0.66, 0.34), (0, 0.84, -0.375), 0.04, 0.045, 'pink')                                     # sloping top tube
beam((0, 0.62, -0.40), (0, 1.04, -0.37), 0.052, 0.058, 'pink')                                    # front mast
beam((0, 0.16, -0.02), (0, 0.38, -0.02), 0.045, 0.05, 'pink_dark')                                # bottom-bracket strut
lathe_dir((-0.09, 0.40, -0.02), X, [(0.052, 0.0, 0), (0.052, 0.18, 1)], 14, flat_uv('pink_dark'), cap_top='pink_dark', cap_bottom='pink_dark')

# ============================================================================= flywheel: pink shell with polished chrome guards
FC = V(0, 0.47, -0.40)
lathe_dir(FC - X * 0.078, X, [(0.30, 0.0, 0), (0.34, 0.012, 0.2), (0.34, 0.144, 0.8), (0.30, 0.156, 1)], 28,
          flat_uv('pink'), cap_top='pink', cap_bottom='pink')
disc(FC + X * 0.081, X, 0.295, 'cover')
disc(FC - X * 0.081, -X, 0.295, 'cover')
lathe_dir((0, 0.808, -0.40), Y, [(0.036, 0.0, 0), (0.046, 0.012, 0.3), (0.046, 0.055, 0.7), (0.034, 0.066, 1)], 12,
          flat_uv('knob'), cap_top='knob')                                                          # resistance knob
tube((0, 0.80, -0.40), (0, 0.815, -0.40), 0.06, 0.06, 10, 'chrome_dark')

# ============================================================================= crank, pedals
tube((-0.14, 0.40, -0.02), (0.14, 0.40, -0.02), 0.022, 0.022, 8, 'chrome')
tube((0.11, 0.40, -0.02), (0.11, 0.25, -0.12), 0.026, 0.022, 8, 'chrome')                       # right crank, pointing down-forward
tube((-0.11, 0.40, -0.02), (-0.11, 0.55, 0.08), 0.026, 0.022, 8, 'chrome')                      # left crank, pointing up-back
for px, py, pz in ((0.19, 0.25, -0.12), (-0.19, 0.55, 0.08)):
    abox((px, py, pz), (0.058, 0.014, 0.05), 'black')                                              # pedal body
    abox((px, py - 0.02, pz), (0.016, 0.014, 0.022), 'cleat')                                      # clip-in cleat catch (bright)
    tube((px - 0.07 * np.sign(px), py, pz), (px + 0.07 * np.sign(px), py, pz), 0.018, 0.018, 8, 'chrome_dark')
    abox((px, py + 0.016, pz), (0.058, 0.004, 0.012), 'chrome')

# ============================================================================= chrome seat post, clamp, saddle with the notice
tube((0, 0.98, 0.31), (0, 1.335, 0.31), 0.03, 0.03, 12, 'chrome')
abox((0, 1.03, 0.31), (0.052, 0.025, 0.055), 'pink_dark')                                          # collar
tube((0.062, 1.03, 0.31), (0.092, 1.03, 0.31), 0.016, 0.022, 8, 'knob')                           # quick-release knob
abox((0, 1.31, 0.31), (0.062, 0.022, 0.05), 'chrome_dark')                                         # rail clamp
for sx in (-0.045, 0.045):
    tube((sx, 1.335, 0.12), (sx, 1.335, 0.50), 0.007, 0.007, 6, 'chrome')                         # saddle rails
RS = ry(math.radians(90))                                                                         # local +x -> world -z (the nose)
loft([(-0.21, 0.115, 1.335, 1.395), (-0.12, 0.140, 1.330, 1.405), (0.0, 0.105, 1.335, 1.400),
      (0.12, 0.062, 1.340, 1.390), (0.21, 0.036, 1.350, 1.380)], RS, (0, 0, 0.31), 'saddle', 'saddle', 'saddle')
loft([(-0.215, 0.103, 1.372, 1.376), (0.215, 0.034, 1.360, 1.364)], RS, (0, 0, 0.31), 'saddle_pipe', 'saddle_pipe', 'saddle_pipe')

# laminated EVICTION NOTICE taped to the saddle: slightly yawed and rolled, glossy border, four fat strips of yellow tape
YAW, ROLL = math.radians(14), math.radians(5)
RN = ry(YAW) @ rz(ROLL)
NC = V(0.0, 1.412, 0.30)
NX, NY, NZ = RN @ X, RN @ Y, RN @ Z


def notice_uv(k, sg, a, b):
    if k == 1 and sg == 1:
        return ruv('notice', b, a)                                                                # image right = +X, image down = +Z
    return cuv(cells['paper_edge'], a, b)


box(NC, NX, NY, NZ, 0.145, 0.004, 0.18, notice_uv)
for sx, sz in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
    tp = NC + RN @ V(sx * 0.125, 0.005, sz * 0.165)
    box(tp, RN @ rz(0) @ ry(sx * sz * math.radians(40)) @ X, NY, NZ, 0.040, 0.0025, 0.016, cellf('tape'))

# ============================================================================= front: chrome handlebar post, T-bar, grips, tablet
tube((0, 0.98, -0.375), (0, 1.25, -0.415), 0.03, 0.03, 12, 'chrome')
BAR = [(-0.26, 1.22, -0.66), (-0.26, 1.24, -0.52), (-0.22, 1.25, -0.44), (0, 1.25, -0.42), (0.22, 1.25, -0.44), (0.26, 1.24, -0.52), (0.26, 1.22, -0.66)]
path_tube(BAR, 0.022, 10, lambda s, t: cuv(cells['chrome'], s, t))
for sx in (-1, 1):
    tube((sx * 0.26, 1.237, -0.545), (sx * 0.26, 1.218, -0.69), 0.034, 0.034, 10, 'grip')       # rubber grips
    abox((sx * 0.26, 1.218, -0.695), (0.034, 0.034, 0.004), 'rubber')
# tilted tablet: screen faces the rider (+Z) and up so that the top-down camera sees it
TH = math.radians(50)
n_t = V(0, math.sin(TH), math.cos(TH)); t_t = V(0, math.cos(TH), -math.sin(TH))
TC = V(0.0, 1.56, -0.43)
tube((0, 1.25, -0.42), tuple(TC - n_t * 0.03), 0.021, 0.021, 10, 'chrome')                       # arm
abox((0, 1.268, -0.42), (0.05, 0.026, 0.03), 'chrome_dark')                                       # bar clamp


def tablet_uv(k, sg, a, b):
    if k == 2 and sg == 1:
        return ruv('screen', a, 1 - b)
    if k == 2 and sg == -1:
        return ruv('tback', a, 1 - b)
    return cuv(cells['black'], a, b)


box(TC, X, t_t, n_t, 0.25, 0.156, 0.016, tablet_uv)

# healing crystal on a cord from the right grip
path_tube([(0.26, 1.20, -0.66), (0.275, 1.12, -0.655), (0.265, 1.05, -0.65)], 0.004, 5, lambda s, t: cuv(cells['white'], s, t))
lathe_dir((0.265, 0.98, -0.65), Y, [(0.0, -0.045, 0), (0.026, 0.0, 0.5), (0.026, 0.03, 0.7), (0.0, 0.085, 1)], 6, flat_uv('crystal'),
          cap_top=None)

# ============================================================================= sweaty towel over the handlebar
xc = -0.115
tw_pts = catmull([(xc, 0.92, 0.33 - 0.64), (xc, 1.04, -0.34), (xc, 1.16, -0.365), (xc, 1.24, -0.395), (xc, 1.285, -0.425), (xc, 1.255, -0.46),
                  (xc, 1.18, -0.478), (xc, 1.12, -0.485)], 5)
tw_pts = [V(*p) for p in tw_pts]
strip(tw_pts, 0.27, [0.05 * math.sin(i * 0.8) for i in range(len(tw_pts))], lambda s, t: ruv('towel', s, t), fixed_side=X)
for dx, dy, dz, r in ((-0.20, 0.80, -0.335, 0.016), (-0.08, 0.66, -0.34, 0.013), (-0.14, 0.50, -0.33, 0.01)):    # sweat drops falling
    lathe_dir((xc + (dx + 0.13), dy, dz), Y, [(0.0, -r * 1.2, 0), (r * 0.8, -r * 0.3, 0.3), (r, 0.0, 0.6), (r * 0.5, r * 1.1, 0.85), (0.0, r * 2.4, 1)], 8,
              flat_uv('drop'))

# ============================================================================= water bottle in a cage on the seat tube
BC = V(0.125, 0.0, 0.335)
BOT = 0.46
for yy in (BOT + 0.07, BOT + 0.20):
    lathe_dir((BC[0], yy, BC[2]), Y, [(0.064, 0.0, 0), (0.064, 0.018, 1)], 14, flat_uv('chrome'), cap_top=None)
beam((0.065, BOT + 0.07, BC[2] - 0.02), (0.065, BOT + 0.20, BC[2] - 0.02), 0.014, 0.012, 'chrome')
abox((0.075, BOT + 0.135, 0.35), (0.04, 0.085, 0.01), 'chrome')                                    # cage back plate
lathe_dir((BC[0], BOT, BC[2]), Y, [(0.046, 0.0, 0), (0.056, 0.012, 0.2), (0.058, 0.07, 1)], 16, flat_uv('bottle'), cap_bottom='bottle')
lathe_dir((BC[0], BOT, BC[2]), Y, [(0.058, 0.07, 1.0), (0.058, 0.20, 0.0)], 16, lambda u, v: ruv('label', u, v))
lathe_dir((BC[0], BOT, BC[2]), Y, [(0.058, 0.20, 0), (0.054, 0.245, 0.4), (0.03, 0.285, 0.8), (0.026, 0.295, 1)], 16, flat_uv('bottle'))
lathe_dir((BC[0], BOT, BC[2]), Y, [(0.030, 0.295, 0), (0.030, 0.325, 0.5), (0.020, 0.335, 1)], 12, flat_uv('cap'), cap_top='cap', cap_bottom='cap')

# ============================================================================= clip-in cycling shoes hanging by their laces from the left pedal
PEDAL = V(-0.19, 0.55, 0.08)
SH = 1.35                                                                                       # shoes are exaggerated so they read from above
SOLE = [(s_ * SH, w_ * SH, y0 * SH, y1 * SH) for s_, w_, y0, y1 in ((-0.18, 0.050, 0.0, 0.016), (0.0, 0.060, 0.0, 0.016), (0.20, 0.050, 0.0, 0.016), (0.215, 0.030, 0.0, 0.016))]
UPPER = [(s_ * SH, w_ * SH, y0 * SH, y1 * SH) for s_, w_, y0, y1 in
         ((-0.17, 0.050, 0.016, 0.095), (-0.10, 0.058, 0.016, 0.125), (-0.02, 0.062, 0.016, 0.105), (0.06, 0.064, 0.016, 0.095),
          (0.14, 0.060, 0.016, 0.078), (0.19, 0.046, 0.016, 0.056), (0.212, 0.024, 0.018, 0.034))]


def shoe(heel_world, axis, up_hint):
    a = nrm(V(*axis)); u = nrm(V(*up_hint) - a * (V(*up_hint) @ a)); w = np.cross(a, u)
    R = np.column_stack([a, u, w])
    attach = V(-0.15, 0.11, 0.0) * SH
    origin = V(*heel_world) - R @ attach
    loft(SOLE, R, origin, 'sole', 'sole', 'sole')
    loft(UPPER, R, origin, 'lime', 'lime', 'lime_dark')
    for s in (0.01, 0.075):                                                                     # velcro straps over the instep
        box(origin + R @ (V(s, 0.098 if s < 0.05 else 0.092, 0) * SH), R @ X, R @ Y, R @ Z, 0.016 * SH, 0.009 * SH, 0.066 * SH, cellf('strap'))
    box(origin + R @ (V(-0.04, 0.125, 0.0) * SH), R @ X, R @ Y, R @ Z, 0.026 * SH, 0.012 * SH, 0.060 * SH, cellf('white'))   # padded collar flash
    box(origin + R @ (V(-0.02, 0.118, 0.035) * SH), R @ X, R @ Y, R @ Z, 0.020 * SH, 0.012 * SH, 0.020 * SH, cellf('chrome'))   # boa dial
    box(origin + R @ (V(0.02, -0.009, 0) * SH), R @ X, R @ Y, R @ Z, 0.034 * SH, 0.009 * SH, 0.022 * SH, cellf('cleat'))        # SPD cleat under the sole
    return origin + R @ attach


for hz, ax_, uh, dx in ((-0.07, (-0.16, -0.92, -0.34), (-1, 0, 0), -0.05), (0.21, (0.10, -0.92, 0.36), (-1, 0, 0.1), 0.0)):
    hp = shoe(PEDAL + V(dx - 0.06, -0.012, hz - 0.08), ax_, uh)
    path_tube([PEDAL + V(0, -0.012, 0), PEDAL + V(dx * 0.4, -0.07, hz * 0.5 - 0.04), tuple(hp + V(0, 0.01, 0))], 0.0065, 5,
              lambda s, t: cuv(cells['white'], s, t))

# ============================================================================= sweat puddle on the mat under the handlebars
PCX, PCZ, PRX, PRZ = 0.0, -0.87, 0.34, 0.27
NA = 24
RINGS = (0.0, 0.5, 1.0)


def blob_r(th):
    return 1 + 0.16 * math.sin(3 * th + 0.6) + 0.10 * math.sin(5 * th + 1.9)


def pud_pos(th, f):
    r = blob_r(th) * f
    return V(PCX + PRX * r * math.cos(th), MY + 0.003 + 0.004 * (1 - f), PCZ + PRZ * r * math.sin(th))


grid = [[None] * (NA + 1) for _ in RINGS]
for ri, f in enumerate(RINGS):
    for k in range(NA + 1):
        th = 2 * math.pi * (k % NA) / NA
        if ri == 0:
            grid[ri][k] = vert(pud_pos(2 * math.pi * (k + 0.5) / NA, 0.0), Y, ruv('puddle', (k + 0.5) / NA, 0.0))
        else:
            grid[ri][k] = vert(pud_pos(th, f), Y, ruv('puddle', k / NA, f))
for ri in range(len(RINGS) - 1):
    for k in range(NA):
        a, b, c, e = grid[ri][k], grid[ri][k + 1], grid[ri + 1][k], grid[ri + 1][k + 1]
        if ri == 0:
            add_tri(a, c, e)
        else:
            add_tri(a, c, b); add_tri(b, c, e)

# ============================================================================= finish
pos = np.array(P); nor = np.array(N); uv = np.array(U); tri = np.array(T)
bmin, bmax = pos.min(0), pos.max(0)
print('verts', len(pos), 'tris', len(tri), 'bbox min', bmin.round(3), 'max', bmax.round(3), 'size', (bmax - bmin).round(3))
assert len(tri) < 3500, 'triangle budget exceeded'
json.dump({'pos': pos.tolist(), 'uv': uv.tolist(), 'tri': tri.tolist(), 'nor': nor.tolist()}, open(OD + '/spinbike_preview.json', 'w'))
json.dump({'min': bmin.tolist(), 'max': bmax.tolist(), 'tris': int(len(tri))}, open(OD + '/spinbike_bounds.json', 'w'))

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
