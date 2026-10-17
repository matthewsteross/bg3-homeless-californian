"""Procedural Pop-Up Encampment Tent, written into the fire-basket template DAE (all 3 LODs).

AI-generated asset (procedural Python geometry and textures; no vanilla art is reused).
usage: build_tent_model.py <basket_template.dae> <out.dae> <out_dir>
Units metres. Origin at ground centre, +Z = front (the door side), +Y up, X = width.
A two-person dome tent built from four curved fabric panels (front hot orange, right teal, back faded orange, left
turquoise) over two crossing pole arches, with a yellow rain-fly stripe over the crown, a blue tarp corner draped over the
front-left roof, a half-open door (zipper, flap, sleeping bag spilling out, mismatched sneakers), a swag of warm string
lights across the front, neon guy lines and pegs, a purple milk-crate side table with gingham cloth and a tiny camp stove
and pot, a cardboard sign with a sun-and-heart doodle (shapes only, no lettering) and a pennant on the pole tip.
Writes <out_dir>/HC_PopUpTent_BM.png, _NM.png, _PM.png, tent_preview.json (Blender previews) and tent_bounds.json.
Pipeline (see HANDOFF.md / hc_tarp.py): this script -> out.dae; then, with absolute paths,
  Divine.exe -g bg3 -a convert-model -s out.dae -d HC_PopUpTent.GR2 -i dae -o gr2 -e conform --conform-path <vanilla LTS_GEN_Fire_Basket_A.GR2> -l warn
  texconv.exe -nologo -y -f BC3_UNORM -m 0 -o <dir> <png>   (rename the results to .DDS)
Winding convention follows build_barricade_model.py: the right-hand normal of each DAE triangle points opposite to the
vertex normal (BG3 mirrors the DAE); internally triangles are stored outward-CCW.
"""
import sys, re, json, math
import numpy as np
sys.path.insert(0, __file__.replace('\\', '/').rsplit('/', 1)[0])
import tent_paint as paint_mod

TPL, OUT, OD = sys.argv[1:4]
cells, rough = paint_mod.paint(OD + '/HC_PopUpTent_BM.png')
paint_mod.nm_image().save(OD + '/HC_PopUpTent_NM.png')
paint_mod.pm_image(rough).save(OD + '/HC_PopUpTent_PM.png')
rng = np.random.default_rng(20261018)
ruv, cuv, panel_ab = paint_mod.ruv, paint_mod.uv, paint_mod.panel_ab
HALF_PI = math.pi / 2

P, N, U, T = [], [], [], []
_last = [0]


def sec(name):
    print('  %-28s %5d tris' % (name, len(T) - _last[0])); _last[0] = len(T)



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


def quad(a, b, c, d):
    add_tri(a, b, c); add_tri(a, c, d)


def frame(d):
    ref = V(0, 1, 0) if abs(d[1]) < 0.9 else V(1, 0, 0)
    u = nrm(np.cross(ref, d)); v = np.cross(d, u)
    return u, v


X, Y, Z = V(1, 0, 0), V(0, 1, 0), V(0, 0, 1)


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
            quad(*corners)


def cellf(name):
    cell = cells[name]
    return lambda k, sg, a, b: cuv(cell, a, b)


def yaw_axes(yaw_deg):
    y = math.radians(yaw_deg)
    return V(math.cos(y), 0, -math.sin(y)), V(math.sin(y), 0, math.cos(y))


def tube_path(pts, r, seg, cell, caps=True, normals_up=None):
    """Round tube through a polyline; frames come from a fixed reference so they do not twist."""
    pts = [V(*p) for p in pts]
    rings = []
    for k, p in enumerate(pts):
        d = nrm(pts[min(k + 1, len(pts) - 1)] - pts[max(k - 1, 0)])
        u, v = frame(d)
        rr = r[k] if isinstance(r, (list, tuple)) else r
        ring = []
        for s in range(seg + 1):
            a = 2 * math.pi * s / seg
            rad = u * math.cos(a) + v * math.sin(a)
            ring.append(vert(p + rad * rr, rad, cuv(cell, k / max(len(pts) - 1, 1), s / seg)))
        rings.append(ring)
    for k in range(len(pts) - 1):
        for s in range(seg):
            a, b, c, e = rings[k][s], rings[k][s + 1], rings[k + 1][s], rings[k + 1][s + 1]
            add_tri(a, b, c); add_tri(b, e, c)
    if caps:
        for end, sg in ((0, -1), (len(pts) - 1, 1)):
            p = pts[end]; d = nrm(pts[min(end + 1, len(pts) - 1)] - pts[max(end - 1, 0)]) * sg
            u, v = frame(d)
            rr = r[end] if isinstance(r, (list, tuple)) else r
            ctr = vert(p, d, cuv(cell, 0.5, 0.5))
            ids = [vert(p + (u * math.cos(2 * math.pi * s / seg) + v * math.sin(2 * math.pi * s / seg)) * rr, d, cuv(cell, 0.5, 0.5)) for s in range(seg + 1)]
            for s in range(seg):
                add_tri(ctr, ids[s], ids[s + 1])


def lathe(cx, cz, yaw, profile, seg, uvf, cap_top=None, cap_bottom=None, cy=0.0):
    """Surface of revolution about a vertical axis at (cx, cz). profile: [(radius, y, v)] bottom -> top."""
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
            ring.append(vert(V(cx + r * cs, cy + y, cz + r * sn), n, uvf(k / seg, v)))
        rings.append(ring)
    for i in range(npts - 1):
        for k in range(seg):
            a, b, c, e = rings[i][k], rings[i][k + 1], rings[i + 1][k], rings[i + 1][k + 1]
            add_tri(a, b, c); add_tri(b, e, c)
    for end, cell, sgn in ((profile[-1], cap_top, 1), (profile[0], cap_bottom, -1)):
        if cell is None:
            continue
        r, y, _ = end
        ctr = vert(V(cx, cy + y, cz), V(0, sgn, 0), cuv(cells[cell], 0.5, 0.5))
        ids = [vert(V(cx + r * math.cos(yaw + 2 * math.pi * k / seg), cy + y, cz + r * math.sin(yaw + 2 * math.pi * k / seg)),
                    V(0, sgn, 0), cuv(cells[cell], 0.5, 0.5)) for k in range(seg + 1)]
        for k in range(seg):
            add_tri(ctr, ids[k], ids[k + 1])


def ellipsoid(c, yaw_deg, radii, nlon, nlat, uvf, flat=None):
    """Ellipsoid (local z = long axis, rotated about Y). flat: clip the bottom at -flat*ry. uvf(a, b) planar 0..1."""
    rx, ry, rz = radii
    cs, sn = math.cos(math.radians(yaw_deg)), math.sin(math.radians(yaw_deg))

    def rot(v):
        return V(v[0] * cs + v[2] * sn, v[1], -v[0] * sn + v[2] * cs)
    ids = []
    for j in range(nlat + 1):
        ph = -HALF_PI + math.pi * j / nlat
        row = []
        for i in range(nlon + 1):
            th = 2 * math.pi * i / nlon
            lp = V(rx * math.cos(ph) * math.cos(th), ry * math.sin(ph), rz * math.cos(ph) * math.sin(th))
            ln = nrm(V(lp[0] / rx ** 2, lp[1] / ry ** 2, lp[2] / rz ** 2))
            if flat is not None:
                lp[1] = max(lp[1], -flat * ry)
            row.append(vert(V(*c) + rot(lp), rot(ln), uvf(0.5 + lp[2] / (2 * rz) * 0.96, 0.5 - lp[0] / (2 * rx) * 0.96)))
        ids.append(row)
    for j in range(nlat):
        for i in range(nlon):
            quad(ids[j][i], ids[j][i + 1], ids[j + 1][i + 1], ids[j + 1][i])


sec('dome surface')
# ============================================================================= dome surface
A, C, H, SE = 0.95, 0.90, 1.34, 2.0 / 2.6
QE = 0.80                                          # profile exponent: <1 gives steeper walls and a fuller, flatter crown          # half width (x), half depth (z), apex height, superellipse exponent
DOOR_PHI = 0.68
DOOR_HALF = math.radians(24.0)


def sgn(v):
    return 1.0 if v >= 0 else -1.0


def dome_raw(psi, phi):
    rho = math.cos(phi) ** QE
    cx, sz = math.cos(psi), math.sin(psi)
    return V(A * rho * sgn(cx) * abs(cx) ** SE, H * math.sin(phi) ** QE, C * rho * sgn(sz) * abs(sz) ** SE)


def dome_normal(psi, phi):
    e = 1e-3
    p_phi = dome_raw(psi, min(phi + e, HALF_PI)) - dome_raw(psi, max(phi - e, 0.0))
    p_psi = dome_raw(psi + e, phi) - dome_raw(psi - e, phi)
    n = np.cross(p_psi, p_phi) if np.linalg.norm(np.cross(p_psi, p_phi)) > 1e-10 else Y
    n = nrm(n)
    p = dome_raw(psi, phi)
    if n @ (V(p[0], p[1] - 0.25, p[2])) < 0:
        n = -n
    if phi > 1.5:                                  # near the pinch the azimuth tangent vanishes: blend to straight up
        k = min((phi - 1.5) / (HALF_PI - 1.5), 1.0)
        n = nrm(n * (1 - k) + Y * k)
    return n


def dpt(psi_deg, phi, off=0.0):
    psi = math.radians(psi_deg)
    return dome_raw(psi, phi) + dome_normal(psi, phi) * off


def dnrm(psi_deg, phi):
    return dome_normal(math.radians(psi_deg), phi)


PHI_ROWS = [0.0, 0.14, 0.30, 0.48, 0.66, 0.84, 1.02, 1.20, 1.36, 1.49, HALF_PI]


def build_panel(kind):
    lo, hi = paint_mod.PANELS[kind]
    nc = 8
    ids = []
    for phi in PHI_ROWS:
        row = []
        for i in range(nc + 1):
            psi_deg = hi - (hi - lo) * i / nc
            row.append(vert(dpt(psi_deg, phi), dnrm(psi_deg, phi), ruv(kind, i / nc, 1 - phi / HALF_PI)))
        ids.append(row)
    for j in range(len(PHI_ROWS) - 1):
        for i in range(nc):
            quad(ids[j][i], ids[j][i + 1], ids[j + 1][i + 1], ids[j + 1][i])


for kind in paint_mod.PANELS:
    build_panel(kind)

sec('pole sleeves along the four ')
# ----------------------------------------------------------------------------- pole sleeves along the four diagonals
for psi_deg in (45.0, 135.0, 225.0, 315.0):
    phis = [0.0 + k * 0.152 for k in range(11)]
    rings = []
    for k, phi in enumerate(phis):
        p = dpt(psi_deg, phi, 0.0); n = dnrm(psi_deg, phi)
        t = nrm(dpt(psi_deg, min(phi + 0.02, HALF_PI)) - dpt(psi_deg, max(phi - 0.02, 0.0)))
        b = nrm(np.cross(t, n))
        ring = []
        for s in range(5):
            th = math.pi * s / 4
            pos = p + b * math.cos(th) * 0.024 + n * (math.sin(th) * 0.017 - 0.003)
            nn = nrm(b * math.cos(th) * 0.017 + n * math.sin(th) * 0.024)
            ring.append(vert(pos, nn, cuv(cells['pole_black'], k / 10, s / 4)))
        rings.append(ring)
    for k in range(len(phis) - 1):
        for s in range(4):
            quad(rings[k][s], rings[k][s + 1], rings[k + 1][s + 1], rings[k + 1][s])
    # pole-end tab where the sleeve meets the ground: a piece of duct tape with a grommet
    p0 = dpt(psi_deg, 0.0, 0.0)
    out = nrm(V(p0[0], 0, p0[2]))
    box(p0 + out * 0.012 + Y * 0.035, np.cross(Y, out), Y, out, 0.04, 0.035, 0.007, cellf('tape'))

sec('yellow rain-fly stripe over ')
# ----------------------------------------------------------------------------- yellow rain-fly stripe over the crown
fly_phis = [0.12, 0.30, 0.50, 0.70, 0.90, 1.10, 1.30, 1.45, HALF_PI]
path = [dpt(180.0, f, 0.026) for f in fly_phis] + [dpt(0.0, f, 0.026) for f in reversed(fly_phis[:-1])]
pn = [dnrm(180.0, f) for f in fly_phis] + [dnrm(0.0, f) for f in reversed(fly_phis[:-1])]
lens = np.cumsum([0] + [np.linalg.norm(path[k + 1] - path[k]) for k in range(len(path) - 1)])
fly_ids = []
for k, (p, n) in enumerate(zip(path, pn)):
    a = lens[k] / lens[-1]
    fly_ids.append([vert(p + Z * 0.072, n, ruv('fly', a, 0.0)), vert(p - Z * 0.072, n, ruv('fly', a, 1.0))])
for k in range(len(path) - 1):
    quad(fly_ids[k][0], fly_ids[k][1], fly_ids[k + 1][1], fly_ids[k + 1][0])

sec('pole hub and pennant at the ')
# ----------------------------------------------------------------------------- pole hub and pennant at the crown
lathe(0, 0, 0.0, [(0.055, 0.0, 0), (0.055, 0.025, 1)], 12, lambda u, v: cuv(cells['pole_black'], u, v),
      cap_top='pole_black', cy=H - 0.012)
FLAG_BASE = H + 0.012
tube_path([(0, FLAG_BASE, 0), (0, FLAG_BASE + 0.25, 0)], 0.006, 6, cells['steel'])
ft = FLAG_BASE + 0.25
for sg in (1, -1):
    nvec = V(0, 0, sg)
    a_ = vert(V(0, ft, 0), nvec, ruv('flag', 0.0 if sg > 0 else 1.0, 0.04))
    b_ = vert(V(0, ft - 0.085, 0), nvec, ruv('flag', 0.0 if sg > 0 else 1.0, 0.96))
    c_ = vert(V(0.17, ft - 0.042, 0), nvec, ruv('flag', 1.0 if sg > 0 else 0.0, 0.5))
    add_tri(a_, b_, c_)

sec('door')
# ============================================================================= door
def alpha(v):
    return DOOR_HALF * max(1 - v ** 2.4, 0.0) ** 0.5


def door_pt(s, v, off=0.0):
    return dpt(90.0 - s * math.degrees(alpha(v)), DOOR_PHI * v, off)


def door_n(s, v):
    return dnrm(90.0 - s * math.degrees(alpha(v)), DOOR_PHI * v)


# dark interior seen through the opening
DV = [0.0, 0.15, 0.30, 0.50, 0.70, 0.85, 1.0]
ids = []
for v in DV:
    ids.append([vert(door_pt(s, v, 0.006), door_n(s, v), ruv('interior', (s + 1) / 2, 1 - v)) for s in np.linspace(-1, 1, 7)])
for j in range(len(DV) - 1):
    for i in range(6):
        quad(ids[j][i], ids[j][i + 1], ids[j + 1][i + 1], ids[j + 1][i])

# zipper tape around the opening
zv = [0.0, 0.15, 0.30, 0.50, 0.70, 0.85, 0.95, 1.0]
zpath = [(-1.0, v) for v in zv] + [(1.0, v) for v in reversed(zv[:-1])]
zp = [door_pt(s, v, 0.012) for s, v in zpath]
zn = [door_n(s, v) for s, v in zpath]
zl = np.cumsum([0] + [np.linalg.norm(zp[k + 1] - zp[k]) for k in range(len(zp) - 1)])
zids = []
for k in range(len(zp)):
    t = nrm(zp[min(k + 1, len(zp) - 1)] - zp[max(k - 1, 0)])
    b = nrm(np.cross(t, zn[k]))
    a = zl[k] / zl[-1]
    zids.append([vert(zp[k] + b * 0.016, zn[k], ruv('zip', a, 0.0)), vert(zp[k] - b * 0.016, zn[k], ruv('zip', a, 1.0))])
for k in range(len(zp) - 1):
    quad(zids[k][0], zids[k][1], zids[k + 1][1], zids[k + 1][0])

# door flap, unzipped from the bottom left and hanging off the right side
FV = [0.0, 0.18, 0.36, 0.54, 0.72, 0.88]
FC = 4


def flap_edge(v):
    return 0.55 - 0.9 * v


fl_ids = []
free_edge = []
for v in FV:
    e = flap_edge(v)
    row = []
    for i in range(FC + 1):
        s = e + (1.0 - e) * i / FC
        f = (1 - s) / max(1 - e, 1e-6)
        off = 0.020 + 0.030 * f ** 1.4 + 0.012 * math.sin(v * 5 + 1)
        psi = 90.0 - s * math.degrees(alpha(v)); phi = DOOR_PHI * v
        _, (a, b) = panel_ab(psi, phi)
        row.append(vert(dpt(psi, phi, off), dnrm(psi, phi), ruv('front', a, b)))
        if i == 0:
            free_edge.append(dpt(psi, phi, off))
    fl_ids.append(row)
for j in range(len(FV) - 1):
    for i in range(FC):
        quad(fl_ids[j][i], fl_ids[j][i + 1], fl_ids[j + 1][i + 1], fl_ids[j + 1][i])
tube_path(free_edge, 0.012, 5, cells['hem_orange'])

sec('blue tarp corner draped over')
# ============================================================================= blue tarp corner draped over the front-left roof
TARP_PSI = (118.0, 172.0)
TARP_LO = [0.52, 0.48, 0.56, 0.50, 0.42, 0.34, 0.24, 0.12, 0.10]
TARP_HI = 1.38
NTC, NTR = 8, 5
tids = []
for i in range(NTC + 1):
    psi_deg = TARP_PSI[1] - (TARP_PSI[1] - TARP_PSI[0]) * i / NTC
    col = []
    for j in range(NTR + 1):
        phi = TARP_LO[i] + (TARP_HI - TARP_LO[i]) * j / NTR
        off = 0.048 + 0.075 * max(0.0, 0.6 - phi) + 0.014 * math.sin(7 * math.radians(psi_deg) + 5 * phi)
        col.append(vert(dpt(psi_deg, phi, off), dnrm(psi_deg, phi), ruv('tarp', i / NTC, 1 - j / NTR)))
    tids.append(col)
for i in range(NTC):
    for j in range(NTR):
        quad(tids[i][j], tids[i + 1][j], tids[i + 1][j + 1], tids[i][j + 1])
tarp_corner = dpt(TARP_PSI[1] - 3.0, TARP_LO[7], 0.10)

sec('guy lines and pegs')
# ============================================================================= guy lines and pegs
GUY = cells['guy']


def guy_line(p0, p1, sag=0.012):
    mid = (V(*p0) + V(*p1)) / 2 - Y * sag
    tube_path([p0, mid, p1], 0.0055, 3, GUY, caps=False)


def peg(base, out, lean=0.035):
    top = V(base[0], 0.085, base[2]) + out * lean
    bot = V(base[0], 0.0, base[2]) - out * lean
    tube_path([bot, top], 0.010, 4, cells['steel'], caps=False)
    d_ = nrm(top - bot); u_, v_ = frame(d_)
    box(top + d_ * 0.012, u_, d_, v_, 0.018, 0.012, 0.018, cellf('peg_orange'), faces={(0, 1), (0, -1), (2, 1), (2, -1), (1, 1)})
    return top + d_ * 0.02


for psi_deg, length in ((45.0, 0.50), (225.0, 0.40), (315.0, 0.46)):
    pb = dpt(psi_deg, 0.0, 0.0)
    out = nrm(V(pb[0], 0, pb[2]))
    base = pb + out * length
    head = peg(base, out)
    guy_line(dpt(psi_deg, 0.40, 0.030), head)
# the front-left guy ties the tarp corner down to its own peg
pb = dpt(160.0, 0.0, 0.0)
out = nrm(V(pb[0], 0, pb[2]))
base = pb + out * 0.27 + V(0, 0, 0.12)
head = peg(base, out)
guy_line(tarp_corner, head, 0.02)
# and the pole end at 135 degrees (the door side) gets a long neon line pegged beside the sign
pb = dpt(135.0, 0.0, 0.0)
out = nrm(V(pb[0], 0, pb[2]))
head = peg(pb + out * 0.40, out)
guy_line(dpt(135.0, 0.40, 0.030), head)

sec('string lights')
# ============================================================================= string lights
spts, sbulbs = paint_mod.string_path()
wire = [dpt(psi, phi, 0.092) for psi, phi in spts]
tube_path(wire, 0.0042, 3, cells['wire'], caps=False)
for k, idx in enumerate(sbulbs):
    p = wire[idx]
    warm = 'bulb' if k % 3 else 'bulb_hot'
    lathe(p[0], p[2], 0.0, [(0.0, -0.062, 0.0), (0.028, -0.034, 0.4), (0.014, -0.006, 0.9)],
          5, lambda u, v, w=warm: cuv(cells[w], u, v * 0.9), cy=p[1])
# battery pack hanging at the right-hand end
pe = wire[-1]
tube_path([pe, pe - Y * 0.04], 0.0042, 3, cells['wire'], caps=False)
box(pe - Y * 0.075, X, Y, Z, 0.03, 0.035, 0.016, cellf('rubber'))
box(pe - Y * 0.075 + Z * 0.0165, X, Y, Z, 0.012, 0.012, 0.0008, cellf('strap'), faces={(2, 1)})

sec('sleeping bag, cardboard mat ')
# ============================================================================= sleeping bag, cardboard mat and sneakers at the door
box((-0.05, 0.006, 0.95), X, Y, Z, 0.42, 0.006, 0.20, lambda k, sg, a, b: ruv('signback', a, b) if (k == 1 and sg == 1) else cuv(cells['cardboard_dk'], a, b))
ellipsoid((-0.06, 0.012 + 0.6 * 0.075, 0.93), 0.0, (0.13, 0.075, 0.21), 10, 7, lambda a, b: ruv('bag', a, b), flat=0.6)
for sx, yaw, zz in ((-0.50, -14.0, 1.00), (-0.34, 9.0, 1.01)):
    c, a_z = yaw_axes(yaw)
    box((sx, 0.014, zz), c, Y, a_z, 0.05, 0.014, 0.115, cellf('sneaker_white'))
    ellipsoid((sx, 0.028 + 0.025, zz - 0.01), yaw, (0.048, 0.040, 0.100), 6, 4,
              lambda a, b: cuv(cells['sneaker_red'], a, b), flat=0.8)
    ellipsoid((sx, 0.036, zz + 0.074), yaw, (0.046, 0.026, 0.044), 5, 3, lambda a, b: cuv(cells['sneaker_white'], a, b), flat=0.4)

sec('milk-crate side table, gingh')
# ============================================================================= milk-crate side table, gingham cloth and camp stove
CRATE_C = (0.99, 0.58)
CY = 12.0
cx_, cz_ = CRATE_C
cax, caz = yaw_axes(CY)


def cr(dx, dy, dz):
    return V(cx_, 0, cz_) + cax * dx + caz * dz + Y * dy


HW, CH = 0.165, 0.28
PUR, PURD = cellf('crate'), cellf('crate_dark')
box(cr(0, 0.008, 0), cax, Y, caz, HW, 0.008, HW, PURD)
for sx in (-1, 1):
    for sz in (-1, 1):
        box(cr(sx * (HW - 0.010), CH / 2, sz * (HW - 0.010)), cax, Y, caz, 0.012, CH / 2, 0.012, PUR, faces={(0, 1), (0, -1), (2, 1), (2, -1)})
for yy, hh in ((CH - 0.012, 0.012), (0.12, 0.007), (0.034, 0.012)):
    for sg in (-1, 1):
        box(cr(0, yy, sg * (HW - 0.004)), cax, Y, caz, HW - 0.02, hh, 0.006, PUR, faces={(1, 1), (1, -1), (2, 1), (2, -1)})
        box(cr(sg * (HW - 0.004), yy, 0), cax, Y, caz, 0.006, hh, HW - 0.02, PUR, faces={(1, 1), (1, -1), (0, 1), (0, -1)})
for sg in (-1, 1):
    for t in (-0.07, 0.07):
        box(cr(t, 0.19, sg * (HW - 0.004)), cax, Y, caz, 0.010, 0.07, 0.005, PUR, faces={(0, 1), (0, -1), (2, 1), (2, -1)})
        box(cr(sg * (HW - 0.004), 0.19, t), cax, Y, caz, 0.005, 0.07, 0.010, PUR, faces={(0, 1), (0, -1), (2, 1), (2, -1)})
# gingham cloth: flat top plus four hanging flaps (a crooked drape)
cloth = lambda k, sg, a, b: ruv('gingham', a, b)
box(cr(0, CH + 0.006, 0), cax, Y, caz, 0.20, 0.004, 0.20, cloth, faces={(1, 1)})
for sg in (-1, 1):
    for k_ in (0, 1):
        sag_ = 0.06 + 0.04 * rng.random()
        if k_ == 0:
            p0, p1 = cr(-0.20, CH + 0.010, sg * 0.20), cr(0.20, CH + 0.010, sg * 0.20)
            n_out = caz * sg
            p2, p3 = cr(0.20, CH + 0.010 - sag_, sg * 0.215), cr(-0.20, CH + 0.010 - sag_ * 0.6, sg * 0.215)
        else:
            p0, p1 = cr(sg * 0.20, CH + 0.010, -0.20), cr(sg * 0.20, CH + 0.010, 0.20)
            n_out = cax * sg
            p2, p3 = cr(sg * 0.215, CH + 0.010 - sag_ * 0.7, 0.20), cr(sg * 0.215, CH + 0.010 - sag_, -0.20)
        ii = [vert(p, nrm(n_out + Y * 0.3), ruv('gingham', ua, vb)) for p, (ua, vb) in zip((p0, p1, p2, p3), ((0, 0), (1, 0), (1, 0.6), (0, 0.6)))]
        quad(*ii)
ST_Y = CH + 0.012
sx_, sz_ = cr(0, 0, 0)[0], cr(0, 0, 0)[2]
lathe(sx_, sz_, 0.0, [(0.045, 0.0, 0), (0.045, 0.085, 1)], 10, lambda u, v: ruv('can', u, 0.1 + 0.8 * (1 - v)), cap_top='steel', cy=ST_Y)
lathe(sx_, sz_, 0.0, [(0.034, 0.0, 0), (0.060, 0.026, 0.5), (0.062, 0.034, 1)], 10, lambda u, v: cuv(cells['steel'], u, v), cap_top='pole_black', cy=ST_Y + 0.085)
for k in range(3):
    ang = 2 * math.pi * k / 3 + 0.5
    px_, pz_ = sx_ + 0.055 * math.cos(ang), sz_ + 0.055 * math.sin(ang)
    tube_path([(px_, ST_Y + 0.115, pz_), (px_, ST_Y + 0.175, pz_)], 0.0045, 4, cells['steel'])
lathe(sx_, sz_, 0.0, [(0.028, 0.0, 0.0), (0.020, 0.012, 0.35), (0.008, 0.032, 0.75), (0.0, 0.050, 1.0)], 8,
      lambda u, v: ruv('flame', 0.1 + 0.8 * u, 1 - v), cy=ST_Y + 0.118)
potc = ST_Y + 0.176
lathe(sx_, sz_, 0.0, [(0.0, 0.0, 0), (0.052, 0.0, 0.0), (0.074, 0.012, 0.2), (0.077, 0.075, 0.9), (0.080, 0.080, 1.0)], 12,
      lambda u, v: cuv(cells['pot'], u, 0.3 + 0.5 * v), cy=potc)
lathe(sx_, sz_, 0.0, [(0.081, 0.078, 0), (0.066, 0.092, 0.4), (0.014, 0.100, 0.8), (0.016, 0.115, 1.0)], 12,
      lambda u, v: cuv(cells['pot_dark'], u, v), cap_top='pot_dark', cy=potc)
tube_path([(sx_ - 0.080, potc + 0.07, sz_), (sx_ - 0.075, potc + 0.13, sz_), (sx_, potc + 0.155, sz_), (sx_ + 0.075, potc + 0.13, sz_), (sx_ + 0.080, potc + 0.07, sz_)],
          0.0042, 4, cells['steel'], caps=False)

sec('cardboard sign: sun-and-hear')
# ============================================================================= cardboard sign: sun-and-heart doodle
SIGN_X, SIGN_Z, SIGN_YAW = -1.00, 0.72, 20.0
sa, sn_ = yaw_axes(SIGN_YAW)
spos = V(SIGN_X, 0.0, SIGN_Z)
box(spos + Y * 0.25 - sn_ * 0.016, sa, Y, sn_, 0.014, 0.25, 0.007, cellf('wood'))
box(spos + Y * 0.66, sa, Y, sn_, 0.17, 0.135, 0.006,
    lambda k, sg, a, b: (ruv('sign', a, 1 - b) if (k == 2 and sg == 1) else
                         ruv('signback', 1 - a, 1 - b) if (k == 2 and sg == -1) else cuv(cells['cardboard_dk'], a, b)))
box(spos + Y * 0.545 + sn_ * 0.0075, sa, Y, sn_, 0.05, 0.016, 0.0008, cellf('tape'), faces={(2, 1)})   # a tape tab at the bottom edge

sec('finish')
# ============================================================================= pigeon with sunglasses perched on the sign (witness protection)
PY_ = 20.0 + 18.0
pc, pf = yaw_axes(PY_)
ptop = V(SIGN_X, 0.66 + 0.135 + 0.006, SIGN_Z)
PG = lambda name: (lambda a, b: cuv(cells[name], a, b))
ellipsoid(ptop + Y * 0.036, PY_, (0.034, 0.030, 0.058), 7, 4, PG('pigeon_grey'), flat=0.8)
ellipsoid(ptop + Y * 0.044 + pf * 0.052, PY_, (0.034, 0.030, 0.030), 6, 3, PG('pigeon_neck'))
ellipsoid(ptop + Y * 0.078 + pf * 0.070, PY_, (0.020, 0.020, 0.022), 6, 3, PG('pigeon_grey'))
box(ptop + Y * 0.078 + pf * 0.093, pc, Y, pf, 0.004, 0.004, 0.011, cellf('pigeon_beak'))
box(ptop + Y * 0.085 + pf * 0.080, pc, Y, pf, 0.022, 0.0045, 0.0045, cellf('rubber'))          # tiny sunglasses
box(ptop + Y * 0.040 - pf * 0.066 + Y * 0.004, pc, Y, pf, 0.018, 0.004, 0.030, cellf('pigeon_dark'))   # tail
for sg in (-1, 1):
    box(ptop + Y * 0.008 + pc * 0.014 * sg, pc, Y, pf, 0.004, 0.008, 0.006, cellf('pigeon_beak'))
sec('pigeon')

# ============================================================================= finish
pos = np.array(P); pos[:, 1] = np.maximum(pos[:, 1], 0.0); nor = np.array(N); uv = np.array(U); tri = np.array(T)
bmin, bmax = pos.min(0), pos.max(0)
print('verts', len(pos), 'tris', len(tri), 'bbox min', bmin.round(3), 'max', bmax.round(3), 'size', (bmax - bmin).round(3))
assert len(tri) < 3500, 'triangle budget exceeded'
json.dump({'pos': pos.tolist(), 'uv': uv.tolist(), 'tri': tri.tolist(), 'nor': nor.tolist()}, open(OD + '/tent_preview.json', 'w'))
json.dump({'min': bmin.tolist(), 'max': bmax.tolist(), 'tris': int(len(tri))}, open(OD + '/tent_bounds.json', 'w'))

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
