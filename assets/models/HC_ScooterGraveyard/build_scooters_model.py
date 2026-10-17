"""Procedural Dockless Scooter Graveyard, written into the fire-basket template DAE (all 3 LODs).

AI-generated asset (procedural Python geometry and textures; no vanilla art is reused).
usage: build_scooters_model.py <basket_template.dae> <out.dae> <out_dir>
Units metres. Origin at ground centre, +Z = front, +Y up, X = width.
Six abandoned rental e-scooters (lime, cyan and white) heaped against a chain-link fence panel on a cracked slab of
sidewalk: one leaning on the fence, one on its side, one upside-down with a wheel in the air, a bent kickstand, bars at odd
angles, zip ties, stickers, glowing LED strips, a green low-battery light and a stray traffic cone on top.
Writes <out_dir>/HC_ScooterGraveyard_BM.png, _NM.png, _PM.png, scooters_preview.json (Blender previews) and scooters_bounds.json.
Pipeline (see HANDOFF.md / hc_tarp.py): this script -> out.dae; then, with absolute paths,
  Divine.exe -g bg3 -a convert-model -s out.dae -d HC_ScooterGraveyard.GR2 -i dae -o gr2 -e conform --conform-path <vanilla LTS_GEN_Fire_Basket_A.GR2> -l warn
  texconv.exe -nologo -y -f BC3_UNORM -m 0 -o <dir> <png>   (rename the results to .DDS)
Winding convention follows build_tarp_model.py: the right-hand normal of each DAE triangle points opposite to the
vertex normal (BG3 mirrors the DAE); internally triangles are stored outward-CCW.
"""
import sys, re, json, math
import numpy as np
sys.path.insert(0, __file__.replace('\\', '/').rsplit('/', 1)[0])
import scooters_paint as paint_mod

TPL, OUT, OD = sys.argv[1:4]
rng = np.random.default_rng(20261017)
ruv, cuv = paint_mod.ruv, paint_mod.uv

P, N, U, T = [], [], [], []
XF_R, XF_T = np.eye(3), np.zeros(3)


def V(*a):
    return np.array(a, float)


def nrm(v):
    l = np.linalg.norm(v)
    return v / l if l > 1e-12 else v


def Rx(a):
    c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]], float)


def Ry(a):
    c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]], float)


def Rz(a):
    c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]], float)


class push:
    """Compose a local frame: p -> (outer transform)(R p + t)."""
    def __init__(self, R=None, t=(0, 0, 0)):
        self.R = np.eye(3) if R is None else R
        self.t = np.array(t, float)

    def __enter__(self):
        global XF_R, XF_T
        self.saved = (XF_R, XF_T)
        XF_T = XF_R @ self.t + XF_T
        XF_R = XF_R @ self.R
        return self

    def __exit__(self, *a):
        global XF_R, XF_T
        XF_R, XF_T = self.saved


def vert(p, n, uv):
    P.append(XF_R @ np.array(p, float) + XF_T); N.append(nrm(XF_R @ np.array(n, float))); U.append(uv)
    return len(P) - 1


def add_tri(a, b, c):
    """Store the triangle outward-CCW: flip if its right-hand normal disagrees with the vertex normals."""
    gn = np.cross(P[b] - P[a], P[c] - P[a])
    mn = N[a] + N[b] + N[c]
    if np.linalg.norm(gn) < 1e-14:
        return
    T.append((a, b, c) if gn @ mn >= 0 else (a, c, b))


def frame(d):
    ref = V(0, 1, 0) if abs(d[1]) < 0.9 else V(1, 0, 0)
    u = nrm(np.cross(ref, d)); v = np.cross(d, u)
    return u, v


def U_(cell, a, b):
    """UV for a palette cell name or a painted region name."""
    return ruv(cell, a, b) if cell in paint_mod.REGION else cuv(cell, a, b)


def box(c, ax, ay, az, hx, hy, hz, uvf, faces=None):
    """Oriented, flat-shaded box. uvf(k, sg, a, b); a runs along local axis (k+1)%3 and b along (k+2)%3, both 0..1."""
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
    return lambda k, sg, a, b: U_(name, a, b)


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
            ring.append(vert(pc + rad * r, n, U_(cell, f, k / seg)))
        rings.append(ring)
    for k in range(seg):
        a, b, c, e = rings[0][k], rings[0][k + 1], rings[1][k], rings[1][k + 1]
        add_tri(a, b, c); add_tri(b, e, c)
    if caps:
        for pc, r, sg, f in ((p0, r0, -1, 0.0), (p1, r1, 1, 1.0)):
            if r < 1e-6:
                continue
            ctr = vert(pc, d * sg, U_(cell, f, 0.5))
            ids = []
            for k in range(seg + 1):
                a = 2 * math.pi * k / seg
                ids.append(vert(pc + (u * math.cos(a) + v * math.sin(a)) * r, d * sg, U_(cell, f, 0.5 + 0.2 * math.sin(a))))
            for k in range(seg):
                add_tri(ctr, ids[k], ids[k + 1])


def bar(p0, p1, half_w, half_t, cell, wide=X, faces=None):
    """Oriented box from p0 to p1 (length along its local y), width along `wide`."""
    p0, p1 = V(*p0), V(*p1)
    ay = nrm(p1 - p0); az = nrm(np.cross(wide, ay)); ax = nrm(np.cross(ay, az))
    box((p0 + p1) / 2, ax, ay, az, half_w, np.linalg.norm(p1 - p0) / 2, half_t, cellf(cell), faces)


def lathe_y(cx, cz, profile, seg, uvf, cap_top=None):
    """Surface of revolution about a vertical axis at (cx, cz). profile: [(radius, y, v)] bottom -> top."""
    rings = []
    npts = len(profile)
    for idx, (r, y, v) in enumerate(profile):
        p0 = profile[max(idx - 1, 0)]; p1 = profile[min(idx + 1, npts - 1)]
        dr, dy = p1[0] - p0[0], p1[1] - p0[1]
        ring = []
        for k in range(seg + 1):
            th = 2 * math.pi * k / seg
            cs, sn = math.cos(th), math.sin(th)
            ring.append(vert(V(cx + r * cs, y, cz + r * sn), nrm(V(dy * cs, -dr, dy * sn)), uvf(k / seg, v)))
        rings.append(ring)
    for i in range(npts - 1):
        for k in range(seg):
            a, b, c, e = rings[i][k], rings[i][k + 1], rings[i + 1][k], rings[i + 1][k + 1]
            add_tri(a, b, c); add_tri(b, e, c)
    if cap_top:
        r, y, _ = profile[-1]
        ctr = vert(V(cx, y, cz), Y, cuv(cap_top, 0.5, 0.5))
        ids = [vert(V(cx + r * math.cos(2 * math.pi * k / seg), y, cz + r * math.sin(2 * math.pi * k / seg)), Y, cuv(cap_top, 0.5, 0.5))
               for k in range(seg + 1)]
        for k in range(seg):
            add_tri(ctr, ids[k], ids[k + 1])


# ----------------------------------------------------------------------------- the scooter
WR, WW = 0.125, 0.07          # wheel radius and width
WSEG = 12
REAR_Z, FRONT_Z = -0.40, 0.46
STEM_A, STEM_L = 14.0, 0.60
LEDS = []                     # (first vertex, last vertex, rgb) of every glowing strip, for the pavement light pools


def wheel(c, axis, seg=WSEG):
    """Tyre as a short drum: a flat face fan on each side (painted rim) and a rounded tread."""
    c, axis = V(*c), nrm(V(*axis)); u, v = frame(axis)
    h = WW / 2
    prof = [(0.88 * WR, -h, 0.0, 0.5, -1.0), (WR, -0.55 * h, 0.2, 1.0, -0.55), (WR, 0.55 * h, 0.8, 1.0, 0.55), (0.88 * WR, h, 1.0, 0.5, 1.0)]
    rings = []
    for r, s, tv, nr, na in prof:
        ring = []
        for k in range(seg + 1):
            a = 2 * math.pi * k / seg
            rad = u * math.cos(a) + v * math.sin(a)
            ring.append(vert(c + rad * r + axis * s, nrm(rad * nr + axis * na), ruv('tread', k / seg, tv)))
        rings.append(ring)
    for i in range(3):
        for k in range(seg):
            a, b, cc, e = rings[i][k], rings[i][k + 1], rings[i + 1][k], rings[i + 1][k + 1]
            add_tri(a, b, cc); add_tri(b, e, cc)
    for s, sg in ((-h, -1), (h, 1)):
        ctr = vert(c + axis * s, axis * sg, ruv('wheel', 0.5, 0.5))
        ids = []
        for k in range(seg + 1):
            a = 2 * math.pi * k / seg
            ids.append(vert(c + (u * math.cos(a) + v * math.sin(a)) * 0.88 * WR + axis * s, axis * sg,
                            ruv('wheel', 0.5 + 0.5 * math.cos(a), 0.5 + 0.5 * math.sin(a))))
        for k in range(seg):
            add_tri(ctr, ids[k], ids[k + 1])


def led(box_args, color, faces):
    i0 = len(P)
    box(*box_args, faces=faces)
    LEDS.append((i0, len(P), color))


def scooter(body, twist=0.0, tilt=0.0, kick='down', stick=0, batt=True):
    """Local frame: x width, y up, z forward (front wheel at +z). Built at rest on its wheels."""
    dark = body + '_dark'
    reg = 'b_' + body
    deck_uv = lambda k, sg, a, b: ruv(reg, a, b) if (k == 1 and sg == 1) else U_(dark if k == 1 else body, a, b)
    # deck, battery pack, grip tape, sticker
    box((0, 0.17, -0.02), X, Y, Z, 0.095, 0.028, 0.32, deck_uv)
    box((0, 0.124, 0.0), X, Y, Z, 0.062, 0.024, 0.19, cellf('rubber_grey'))
    box((0, 0.1925, -0.14), X, Y, Z, 0.07, 0.001, 0.15, lambda k, sg, a, b: ruv('grip', a, b), faces={(1, 1)})
    box((0, 0.1935, 0.20), X, Y, Z, 0.052, 0.001, 0.046, lambda k, sg, a, b: ruv('st%d' % stick, b, a), faces={(1, 1)})
    # LED strips: along both deck sides and under the battery pack
    for sx in (-1, 1):
        led((V(sx * 0.0875, 0.168, 0.0), X, Y, Z, 0.001, 0.007, 0.26, cellf('led_cyan')), (70, 255, 240), {(0, sx)})
    led((V(0, 0.0995, 0.0), X, Y, Z, 0.03, 0.001, 0.17, cellf('led_cyan')), (70, 255, 240), {(1, -1)})
    # wheels, rear fender, tail light
    wheel((0, WR, REAR_Z), X)
    wheel((0, WR, FRONT_Z), X)
    arc = [(REAR_Z + (WR + 0.022) * math.cos(math.radians(a)), WR + (WR + 0.022) * math.sin(math.radians(a))) for a in (15, 62, 112, 160)]
    for (z0, y0), (z1, y1) in zip(arc, arc[1:]):
        bar((0, y0, z0), (0, y1, z1), 0.034, 0.004, body)
    led((V(0, arc[-1][1] - 0.012, arc[-1][0] - 0.004), X, Y, Z, 0.016, 0.01, 0.003, cellf('led_red')), (255, 40, 50), {(2, -1)})
    # steering head and fork
    for sx in (-1, 1):
        tube((sx * 0.044, WR, FRONT_Z), (sx * 0.034, 0.215, FRONT_Z - 0.06), 0.016, 0.016, 5, 'steel_dark', caps=False)
    sa = math.radians(STEM_A)
    sdir = V(0, math.cos(sa), -math.sin(sa))
    base = V(0, 0.215, FRONT_Z - 0.06)
    top = base + sdir * STEM_L
    box(base + V(0, 0.0, 0.0), X, sdir, nrm(np.cross(X, sdir)), 0.04, 0.045, 0.034, cellf(body))
    tube(base + sdir * 0.04, top, 0.028, 0.024, 8, body, caps=False)
    tube(base + sdir * 0.07, base + sdir * 0.17, 0.034, 0.034, 8, 'steel_dark', caps=True)
    fwd = nrm(np.cross(X, sdir))
    qc = base + sdir * 0.42 + fwd * 0.02
    box(qc, X, sdir, fwd, 0.04, 0.05, 0.003, lambda k, sg, a, b: ruv('qr', a, 1 - b), faces={(2, 1)})
    # handlebar group (can be twisted and dipped for that wrecked look)
    Rs = np.column_stack([X, sdir, nrm(np.cross(X, sdir))])
    with push(Rs @ Ry(twist) @ Rz(tilt), top):
        tube((-0.17, 0, 0), (0.17, 0, 0), 0.017, 0.017, 6, 'steel_dark', caps=False)
        for sx in (-1, 1):
            tube((sx * 0.17, 0, 0), (sx * 0.265, 0, 0), 0.025, 0.025, 5, 'rubber')
            tube((sx * 0.19, -0.012, 0.01), (sx * 0.2, -0.018, 0.1), 0.008, 0.006, 4, 'steel', caps=False)
        box((0, 0.03, 0.0), X, Y, Z, 0.062, 0.026, 0.036,
            lambda k, sg, a, b: ruv('dash', a, b) if (k == 2 and sg == -1) else U_('rubber', a, b))
        if batt:
            led((V(0, 0.0605, -0.01), X, Y, Z, 0.013, 0.0075, 0.013, cellf('led_green')), (110, 255, 50), {(1, 1), (2, -1)})
        led((V(0, 0.032, 0.0375), X, Y, Z, 0.04, 0.016, 0.001, cellf('led_cyan')), (70, 255, 240), {(2, 1)})
    # kickstand
    if kick == 'down':
        tube((0.07, 0.15, -0.12), (0.086, 0.012, -0.2), 0.011, 0.011, 5, 'steel_dark', caps=False)
    elif kick == 'bent':
        tube((0.07, 0.15, -0.12), (0.135, 0.07, -0.16), 0.011, 0.011, 5, 'steel_dark', caps=False)
        tube((0.135, 0.07, -0.16), (0.235, 0.04, -0.07), 0.011, 0.011, 5, 'steel_dark', caps=False)
    else:   # folded up under the deck
        tube((0.07, 0.15, -0.12), (0.07, 0.15, -0.3), 0.011, 0.011, 5, 'steel_dark', caps=False)
    return {'stem_base': base, 'stem_top': top, 'sdir': sdir, 'Rs': Rs}


SCOOTERS = []
SCALE = 1.1


def orient(fwd, up):
    """Rotation taking local +z to `fwd` and local +y as close as possible to `up` (both world directions)."""
    z = nrm(V(*fwd)); y = V(*up); y = nrm(y - (y @ z) * z); x = np.cross(y, z)
    return np.column_stack([x, y, z])




def place(spec):
    """Build one scooter, rotate it (yaw, pitch, roll degrees), put it at (x, z) and drop its lowest point to rest_y."""
    i0 = len(P)
    with push(SCALE * orient(spec['fwd'], spec['up']), (spec['x'], 0, spec['z'])):
        info = scooter(spec['body'], spec.get('twist', 0), spec.get('tilt', 0), spec.get('kick', 'down'), spec.get('stick', 0), spec.get('batt', True))
        Rw, Tw = XF_R.copy(), XF_T.copy()
    lo = min(p[1] for p in P[i0:])
    dy = spec['rest_y'] - lo
    dz = 0.0
    if 'fence' in spec:
        dz = (FZ + 0.012 + spec['fence']) - min(p[2] for p in P[i0:])
    for i in range(i0, len(P)):
        P[i] = P[i] + V(0, dy, dz)
    SCOOTERS.append({'R': Rw, 'T': Tw + V(0, dy, dz), 'range': (i0, len(P)), 'info': info})


def world(i, local):
    s = SCOOTERS[i]
    return s['R'] @ V(*local) + s['T']


# ----------------------------------------------------------------------------- pile layout
G0 = 0.03     # sidewalk top
# yaw: 0 faces +z (front), 90 faces +x. pitch + = nose down. roll + = lean right (deck normal toward -x ... see notes in README of this script)
PILE = [
    # 0: lime, standing on its wheels at the left, leaning on the fence, handlebar twisted
    dict(body='lime', fwd=(1, 0, 0.05), up=(0, 0.95, -0.30), x=-0.55, z=-0.30, rest_y=G0, twist=28, tilt=-6, kick='down', stick=0, fence=0.0),
    # 1: cyan, flat on its side at the front left, bent kickstand
    dict(body='cyan', fwd=(1, 0, -0.35), up=(-0.55, 0.4, -0.7), x=-0.45, z=0.30, rest_y=G0, kick='bent', stick=1, twist=-20, fence=0.0),
    # 2: white, upside-down on top of the heap, front wheel up in the air
    dict(body='white', fwd=(0.25, 0.40, -0.85), up=(0.05, -0.9, 0.3), x=0.10, z=-0.08, rest_y=0.24, kick='up', stick=2, twist=18, tilt=10, fence=0.0),
    # 3: lime, sprawled on its side across the middle, stem pointing at the camera
    dict(body='lime', fwd=(0.8, 0.4, -0.35), up=(-0.5, 0.55, 0.55), x=-0.22, z=0.02, rest_y=0.03, kick='down', stick=3, twist=-30, tilt=8),
    # 4: cyan, still upright at the right, tipping over onto the fence, bent kickstand
    dict(body='cyan', fwd=(-1, 0, 0.1), up=(0.1, 0.93, -0.35), x=0.55, z=-0.30, rest_y=G0, kick='bent', stick=2, twist=14, tilt=-9, fence=0.0),
    # 5: white, lying on its side at the lower right front, stem pointing into the pile
    dict(body='white', fwd=(-1, 0, 0.35), up=(0.3, 0.3, -1), x=0.65, z=0.35, rest_y=G0, kick='down', stick=3, twist=-12, tilt=5),
]

# ----------------------------------------------------------------------------- sidewalk slab with lifted chunks
box((0, G0 / 2, 0), X, Y, Z, 1.2, G0 / 2, 0.8,
    lambda k, sg, a, b: ruv('pave', b, a) if (k == 1 and sg == 1) else U_('concrete_dark', a, b))


def chunk(cx, cz, w, d, yaw_deg, lift_axis, lift):
    """A broken slab lifted along one edge: top face keeps the pavement painting at its true x,z."""
    ca, sa_ = math.cos(math.radians(yaw_deg)), math.sin(math.radians(yaw_deg))
    corners = []
    for sx, sz in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        lx, lz = sx * w / 2, sz * d / 2
        x, z = cx + lx * ca - lz * sa_, cz + lx * sa_ + lz * ca
        t_ = ((lx / (w / 2)) if lift_axis == 'x' else (lz / (d / 2))) * 0.5 + 0.5
        y = G0 + 0.004 + lift * t_
        corners.append(V(x, y, z))
    n = nrm(np.cross(corners[1] - corners[0], corners[2] - corners[1]))
    if n[1] < 0:
        n = -n
    ids = [vert(c, n, paint_mod.pave_uv(c[0], c[2])) for c in corners]
    add_tri(ids[0], ids[1], ids[2]); add_tri(ids[0], ids[2], ids[3])
    for k in range(4):
        a, b = corners[k], corners[(k + 1) % 4]
        out = nrm(np.cross(b - a, Y))
        va = vert(a, out, cuv('concrete_dark', 0.2, 0.2)); vb = vert(b, out, cuv('concrete_dark', 0.8, 0.2))
        vc = vert(V(b[0], G0 - 0.002, b[2]), out, cuv('concrete_dark', 0.8, 0.8)); vd = vert(V(a[0], G0 - 0.002, a[2]), out, cuv('concrete_dark', 0.2, 0.8))
        add_tri(va, vb, vc); add_tri(va, vc, vd)


chunk(1.0, 0.55, 0.34, 0.28, 22, 'x', 0.05)
chunk(-0.96, 0.50, 0.30, 0.30, -15, 'z', 0.04)
chunk(0.15, 0.68, 0.30, 0.20, 5, 'x', 0.035)

# ----------------------------------------------------------------------------- chain-link fence panel
FZ = -0.66
for sg in (1, -1):
    z = FZ + sg * 0.007
    n = V(0, 0, sg)
    corners = [(-1.15, 0.08), (1.15, 0.08), (1.15, 1.25), (-1.15, 1.25)]
    ids = []
    for x, y in corners:
        a = (x + 1.15) / 2.3; b = 1.0 - (y - 0.08) / 1.17
        ids.append(vert(V(x, y, z), n, ruv('fence', a if sg == 1 else 1 - a, b)))
    add_tri(ids[0], ids[1], ids[2]); add_tri(ids[0], ids[2], ids[3])
tube((-1.16, 1.27, FZ), (1.16, 1.27, FZ), 0.016, 0.016, 6, 'steel')
tube((-1.16, 0.065, FZ), (1.16, 0.065, FZ), 0.014, 0.014, 6, 'steel', caps=False)
for sx in (-1, 1):
    box((sx * 1.14, 0.655, FZ), X, Y, Z, 0.026, 0.62, 0.026, cellf('steel'))
    box((sx * 1.0, 0.03 + G0, FZ + 0.04), X, Y, Z, 0.045, 0.03, 0.16, cellf('concrete'))     # fence feet

# ----------------------------------------------------------------------------- scooters
for spec in PILE:
    place(spec)

# ----------------------------------------------------------------------------- zip ties (bright and black), tied from scooter parts to the fence and to each other
ZIPCOL = ['zip_black', 'zip_black', 'orange', 'zip_black', 'pink', 'yellow', 'zip_black', 'zip_white', 'orange', 'zip_black', 'pink', 'zip_black']


def zip_tie(p0, p1, col, droop=0.03):
    p0, p1 = V(*p0), V(*p1)
    mid = (p0 + p1) / 2 + V(rng.normal(0, 0.012), -droop, rng.normal(0, 0.012))
    tube(p0, mid, 0.0065, 0.0065, 4, col, caps=False)
    tube(mid, p1, 0.0065, 0.0065, 4, col, caps=False)


# ----------------------------------------------------------------------------- stray cone on top, plus weeds
def cone(base_pt, up_dir, spin=0.0):
    """Traffic cone standing on base_pt with its axis along up_dir (a world direction)."""
    R = orient((math.sin(spin), 0, math.cos(spin)), up_dir)
    with push(R, base_pt):
        box((0, 0.0125, 0), X, Y, Z, 0.10, 0.0125, 0.10, cellf('rubber'))
        hs = (0.0, 0.31, 0.60, 0.80, 1.0)
        prof = [(0.082 + (0.020 - 0.082) * h, 0.025 + (0.43 - 0.025) * h, h) for h in hs]
        lathe_y(0, 0, prof, 10, lambda u, v: ruv('cone', u, 1 - v), cap_top='rubber')


def blade(px, py, pz, ang, h, lean, w=0.011):
    dx, dz = math.cos(ang), math.sin(ang)
    side = V(-dz, 0, dx)
    base = V(px, py, pz)
    tip = base + V(dx * lean, h, dz * lean)
    n = nrm(np.cross(side, tip - base))
    for sgn in (1, -1):
        nn = n * sgn
        a = vert(base - side * w, nn, cuv('weed', 0.3, 0.3)); b = vert(base + side * w, nn, cuv('weed_dark', 0.5, 0.5)); c = vert(tip, nn, cuv('weed', 0.5, 0.8))
        add_tri(a, b, c)


def tuft(x, z, n=3, h=0.1):
    for k in range(n):
        blade(x + rng.normal(0, 0.01), G0 + 0.003, z + rng.normal(0, 0.01), rng.uniform(0, 6.28), h * rng.uniform(0.6, 1.1), h * rng.uniform(0.2, 0.5))


for x, z in ((-1.02, 0.34), (0.9, 0.7), (-0.5, 0.7), (1.12, -0.5), (-0.1, -0.5)):
    tuft(x, z)

# ----------------------------------------------------------------------------- cone and zip ties (positions tuned against the previews)
def wdir(i, d):
    return SCOOTERS[i]['R'] @ V(*d)


# the stray cone is balanced on the upside-down scooter's battery pack, leaning with it
cone(world(2, (0, 0.099, 0.0)), -wdir(2, (0, 1, 0)) + V(0.06, 0, 0.04), spin=0.5)


def stem_pt(i, f):
    inf = SCOOTERS[i]['info']
    return world(i, inf['stem_base'] + inf['sdir'] * (STEM_L * f))


ties = [
    ((-0.30, 0.99, FZ + 0.01), stem_pt(0, 1.0), 'orange'),
    ((-0.34, 0.80, FZ + 0.01), stem_pt(0, 0.82), 'zip_black'),
    ((0.28, 0.96, FZ + 0.01), stem_pt(4, 1.0), 'pink'),
    ((0.33, 0.78, FZ + 0.01), stem_pt(4, 0.8), 'zip_black'),
    (stem_pt(0, 0.95), stem_pt(4, 0.95), 'yellow'),
    (stem_pt(0, 0.7), stem_pt(4, 0.72), 'zip_black'),
    (stem_pt(2, 0.9), stem_pt(4, 0.5), 'zip_white'),
    (stem_pt(1, 0.9), stem_pt(3, 0.4), 'pink'),
]
for p0_, p1_, col in ties:
    zip_tie(p0_, p1_, col, droop=0.02)
for k in range(9):          # a garland of loose ties hanging off the top rail
    x = -1.0 + 0.24 * k + rng.normal(0, 0.03)
    zip_tie((x, 1.262, FZ + 0.004), (x + rng.normal(0, 0.02), 1.12 - 0.04 * rng.random(), FZ + 0.03), ZIPCOL[k % len(ZIPCOL)], droop=0.01)

# an orphaned pink bike helmet in the front left (nobody wears one)
def helmet(cx, cz, yaw, lean):
    with push(Ry(yaw) @ Rx(lean), (cx, G0 + 0.045, cz)):
        prof = [(0.125, 0.0, 0.0), (0.125, 0.035, 0.2), (0.108, 0.085, 0.5), (0.07, 0.122, 0.8), (0.0, 0.135, 1.0)]
        lathe_y(0, 0, prof, 10, lambda u, v: cuv('pink', u, v))
        for a_ in (0.0, 1.05, 2.1, 3.15, 4.2, 5.25):      # yellow vent stripes
            box((0.082 * math.cos(a_), 0.1, 0.082 * math.sin(a_)), V(-math.sin(a_), 0, math.cos(a_)), Y, V(math.cos(a_), 0, math.sin(a_)),
                0.012, 0.022, 0.006, cellf('yellow'), faces={(2, 1)})
        tube((0.12, 0.03, 0.0), (0.2, 0.0, 0.1), 0.006, 0.006, 4, 'rubber', caps=False)     # chin strap


helmet(-0.88, 0.50, 30, 18)

# ----------------------------------------------------------------------------- finish
pos = np.array(P); nor = np.array(N); uv = np.array(U); tri = np.array(T)
bmin, bmax = pos.min(0), pos.max(0)
print('verts', len(pos), 'tris', len(tri), 'bbox min', bmin.round(3), 'max', bmax.round(3), 'size', (bmax - bmin).round(3))
for i, s in enumerate(SCOOTERS):
    a, b = s['range']
    print('scooter', i, PILE[i]['body'], 'bbox min', pos[a:b].min(0).round(2), 'max', pos[a:b].max(0).round(2),
          '| rear', world(i, (0, WR, REAR_Z)).round(2), 'front', world(i, (0, WR, FRONT_Z)).round(2), 'deck', world(i, (0, 0.17, 0)).round(2),
          'stemtop', world(i, s['info']['stem_top']).round(2))
assert len(tri) < 3500, 'triangle budget exceeded'
for ax_, lim in ((0, 1.22), (2, 0.82)):
    if max(abs(bmin[ax_]), abs(bmax[ax_])) > lim:
        print('WARNING: out of the slab on axis', ax_, bmin[ax_], bmax[ax_])
if bmax[1] > 1.34:
    print('WARNING: taller than 1.34 m', bmax[1])

# glow pools for the LEDs lying close to the ground
glows = []
for i0, i1, col in LEDS:
    c = pos[i0:i1].mean(0)
    if c[1] < 0.32 and abs(c[0]) < 1.15 and abs(c[2]) < 0.78 and col != (255, 40, 50):
        glows.append((float(c[0]), float(c[2]), 0.26, col))
rough = paint_mod.paint(OD + '/HC_ScooterGraveyard_BM.png', glows)
paint_mod.nm_image().save(OD + '/HC_ScooterGraveyard_NM.png')
paint_mod.pm_image(rough).save(OD + '/HC_ScooterGraveyard_PM.png')
json.dump({'pos': pos.tolist(), 'uv': uv.tolist(), 'tri': tri.tolist(), 'nor': nor.tolist()}, open(OD + '/scooters_preview.json', 'w'))
json.dump({'min': bmin.tolist(), 'max': bmax.tolist(), 'tris': int(len(tri))}, open(OD + '/scooters_bounds.json', 'w'))

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
