"""Texture atlas painter for the Pop-Up Encampment Tent (1024x1024), AI-generated procedural art (PIL/numpy).

Layout (pixels, origin top-left):
  (   0,  0)-( 256,384)   front panel  (orange, door side)   u left->right seen from outside, v apex (top) -> base
  ( 256,  0)-( 512,384)   right panel  (teal)
  ( 512,  0)-( 768,384)   back panel   (faded orange)
  ( 768,  0)-(1024,384)   left panel   (turquoise)
  (   0,384)-( 256,640)   blue tarp corner
  ( 256,384)-( 768,432)   yellow rain-fly stripe (u along the arch)
  ( 256,432)-( 768,464)   door zipper tape
  ( 256,464)-( 448,640)   tent interior seen through the open door
  ( 448,464)-( 576,592)   sleeping bag (planar, from above)
  ( 576,464)-( 704,592)   gingham tablecloth
  ( 768,384)-( 896,512)   cardboard sign, sun-and-heart doodle (shapes only, no lettering)
  ( 896,384)-(1024,512)   sign back
  ( 768,512)-( 896,576)   fuel can label
  ( 896,512)-( 960,576)   stove flame (v: base blue -> tip yellow)
  ( 960,512)-(1024,576)   pennant flag
  (   0,960)-(1024,1024)  32 x 2 small 32px palette cells
paint() writes the base colour PNG and returns (cells, rough). Lettering is deliberately absent (BG3 mirrors the DAE).
The warm string-light bulbs are also painted as soft glows onto the panels under the strand (see string_path()).
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W = 1024
CELL = 32
CELL_Y0 = 960
HALF_PI = math.pi / 2

# name: (base RGB, grime 0-1, scratch 0-1, rough 0-1)
PALETTE = {
    'pole_black':   ((34, 34, 40), 0.20, 0.10, 0.45),
    'tape':         ((178, 184, 192), 0.35, 0.30, 0.35),
    'peg_orange':   ((255, 112, 12), 0.30, 0.20, 0.50),
    'guy':          ((208, 255, 36), 0.30, 0.05, 0.70),
    'wire':         ((16, 16, 18), 0.10, 0.00, 0.60),
    'bulb':         ((255, 238, 120), 0.0, 0.0, 0.10),
    'bulb_hot':     ((255, 204, 64), 0.0, 0.0, 0.10),
    'crate':        ((126, 70, 196), 0.35, 0.30, 0.55),
    'crate_dark':   ((86, 44, 142), 0.45, 0.30, 0.55),
    'steel':        ((164, 168, 176), 0.40, 0.40, 0.35),
    'pot':          ((34, 112, 214), 0.35, 0.30, 0.30),
    'pot_dark':     ((18, 62, 138), 0.40, 0.30, 0.35),
    'cardboard':    ((196, 152, 100), 0.45, 0.15, 0.90),
    'cardboard_dk': ((140, 104, 64), 0.50, 0.15, 0.90),
    'sneaker_red':  ((226, 40, 54), 0.40, 0.25, 0.70),
    'sneaker_white': ((240, 238, 230), 0.50, 0.25, 0.70),
    'rubber':       ((36, 35, 38), 0.35, 0.10, 0.85),
    'strap':        ((252, 208, 32), 0.30, 0.10, 0.60),
    'tarp_blue':    ((28, 112, 232), 0.30, 0.10, 0.35),
    'skirt':        ((44, 46, 52), 0.50, 0.10, 0.80),
    'hem_orange':   ((214, 74, 8), 0.40, 0.20, 0.55),
    'hem_teal':     ((0, 112, 122), 0.40, 0.20, 0.55),
    'wood':         ((156, 114, 72), 0.40, 0.25, 0.85),
    'cloth_edge':   ((228, 40, 52), 0.30, 0.10, 0.90),
    'flame_core':   ((255, 244, 190), 0.0, 0.0, 0.20),
    'pigeon_grey':  ((132, 136, 150), 0.30, 0.10, 0.80),
    'pigeon_neck':  ((70, 150, 132), 0.10, 0.10, 0.55),
    'pigeon_dark':  ((72, 74, 88), 0.30, 0.10, 0.80),
    'pigeon_beak':  ((244, 170, 90), 0.10, 0.00, 0.60),
}
ORDER = list(PALETTE)
REGION = {
    'front': (0, 0, 256, 384), 'right': (256, 0, 256, 384), 'back': (512, 0, 256, 384), 'left': (768, 0, 256, 384),
    'tarp': (0, 384, 256, 256), 'fly': (256, 384, 512, 48), 'zip': (256, 432, 512, 32), 'interior': (256, 464, 192, 176),
    'bag': (448, 464, 128, 128), 'gingham': (576, 464, 128, 128), 'sign': (768, 384, 128, 128),
    'signback': (896, 384, 128, 128), 'can': (768, 512, 128, 64), 'flame': (896, 512, 64, 64), 'flag': (960, 512, 64, 64),
}
# Dome panels: azimuth range in degrees (x = cos psi, z = sin psi, +Z = front). Seen from outside u runs with falling psi.
PANELS = {'right': (-45.0, 45.0), 'front': (45.0, 135.0), 'left': (135.0, 225.0), 'back': (225.0, 315.0)}
PANEL_H = 384
PANEL_W = 256

# ----------------------------------------------------------------------------- shared string-light path
# anchors (psi in degrees, phi in radians above the ground, 0 = base, pi/2 = apex) and the sag of each swag in phi
STRING_ANCHORS = [(168.0, 0.60), (128.0, 1.04), (52.0, 1.04), (12.0, 0.60)]
STRING_SAGS = [0.13, 0.19, 0.13]
STRING_SEGS = 8


def string_path():
    """Dense (psi_deg, phi) points of the whole strand, plus the indices that carry a bulb."""
    pts, bulbs = [], []
    for k in range(len(STRING_ANCHORS) - 1):
        (p0, f0), (p1, f1) = STRING_ANCHORS[k], STRING_ANCHORS[k + 1]
        for i in range(STRING_SEGS + (1 if k == len(STRING_ANCHORS) - 2 else 0)):
            t = i / STRING_SEGS
            pts.append((p0 + (p1 - p0) * t, f0 + (f1 - f0) * t - STRING_SAGS[k] * 4 * t * (1 - t)))
            if 0 < i < STRING_SEGS:
                bulbs.append(len(pts) - 1)
    return pts, bulbs


def panel_ab(psi_deg, phi):
    """Panel name and (a, b) 0..1 texture coordinates of a dome point (a: left -> right, b: apex -> base)."""
    p = psi_deg % 360.0
    if p >= 315.0:
        p -= 360.0
    for name, (lo, hi) in PANELS.items():
        if lo <= p < hi:
            return name, ((hi - p) / (hi - lo), 1.0 - phi / HALF_PI)
    return 'front', (0.5, 0.5)


# ----------------------------------------------------------------------------- small helpers
def _lowfreq(rng, n, size):
    a = rng.random((n, n)).astype('float32')
    im = Image.fromarray((a * 255).astype('uint8')).resize((size[1], size[0]), Image.BICUBIC)
    return np.asarray(im).astype('float32') / 255.0


def _layer(w, h, ss=2):
    return Image.new('RGBA', (w * ss, h * ss), (0, 0, 0, 0))


def _flatten(img, layer, blur=0.0):
    """Down-sample a supersampled RGBA layer and composite it onto an RGB image."""
    w, h = img.size
    small = layer.resize((w, h), Image.LANCZOS)
    if blur:
        small = small.filter(ImageFilter.GaussianBlur(blur))
    return Image.alpha_composite(img.convert('RGBA'), small).convert('RGB')


def _wobble(pts, rng, amp):
    return [(x + rng.normal(0, amp), y + rng.normal(0, amp)) for x, y in pts]


def _marker(d, pts, color, width, rng, wob=1.0, ss=2, closed=False):
    pts = _wobble([(x * ss, y * ss) for x, y in pts], rng, wob * ss)
    if closed:
        pts = pts + [pts[0]]
    d.line(pts, fill=color, width=int(width * ss), joint='curve')
    for x, y in (pts[0], pts[-1]):
        r = width * ss / 2
        d.ellipse([x - r, y - r, x + r, y + r], fill=color)


def _heart_pts(cx, cy, s, n=28):
    out = []
    for k in range(n + 1):
        t = 2 * math.pi * k / n
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        out.append((cx + x * s / 16.0, cy - y * s / 16.0))
    return out


def _smiley(layer, cx, cy, r, ss=2, bg=(252, 214, 24, 255), face=(36, 30, 20, 255)):
    d = ImageDraw.Draw(layer)
    cx, cy, r = cx * ss, cy * ss, r * ss
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=bg, outline=(60, 44, 20, 255), width=max(1, int(r / 8)))
    e = r / 6
    for sx in (-1, 1):
        d.ellipse([cx + sx * r * 0.38 - e, cy - r * 0.28 - e * 1.3, cx + sx * r * 0.38 + e, cy - r * 0.28 + e * 1.3], fill=face)
    d.arc([cx - r * 0.55, cy - r * 0.35, cx + r * 0.55, cy + r * 0.62], 25, 155, fill=face, width=max(1, int(r / 7)))


def _tape(img, cx, cy, w, h, ang, rng, col=(178, 184, 192), ss=2, torn=True):
    """A strip of duct tape: sheen, fibre lines, crinkles, torn ends, drop shadow."""
    tw, th = int(w * ss), int(h * ss)
    t = np.zeros((th, tw, 3), 'float32'); t[:] = col
    xs = np.linspace(0, 1, tw)[None, :]
    ys = np.linspace(0, 1, th)[:, None]
    sheen = 0.5 + 0.5 * np.sin(xs * 9 + rng.random() * 6 + ys * 2.0)
    t *= (0.86 + 0.20 * sheen)[..., None]
    t *= (0.92 + 0.10 * np.sin(ys * th * 0.9))[..., None]            # cloth weave bands across the tape
    t += rng.normal(0, 3, (th, tw, 1))
    im = Image.fromarray(np.clip(t, 0, 255).astype('uint8')).convert('RGBA')
    d = ImageDraw.Draw(im)
    for _ in range(max(3, int(w / 9))):                              # crinkle lines
        x0 = rng.integers(0, tw); y0 = rng.integers(0, th); ln = rng.integers(8, 30) * ss
        d.line([(x0, y0), (x0 + ln * rng.uniform(-0.3, 0.3), y0 + ln)], fill=(250, 252, 255, 120) if rng.random() < 0.5 else (70, 72, 80, 110), width=1)
    d.rectangle([0, 0, tw, 2 * ss], fill=(120, 124, 132, 120)); d.rectangle([0, th - 2 * ss, tw, th], fill=(110, 114, 122, 120))
    mask = Image.new('L', (tw, th), 255)
    if torn:
        md = ImageDraw.Draw(mask)
        for end in (0, 1):
            xe = 0 if end == 0 else tw
            poly = [(xe, 0)]
            for k in range(1, 8):
                poly.append((xe + (rng.uniform(1, 4) * ss) * (1 if end == 0 else -1), th * k / 8))
            poly.append((xe, th))
            md.polygon(poly, fill=0)
    im.putalpha(mask)
    big = Image.new('RGBA', (int(max(tw, th) * 1.5) + 8, int(max(tw, th) * 1.5) + 8), (0, 0, 0, 0))
    big.paste(im, ((big.width - tw) // 2, (big.height - th) // 2), im)
    big = big.rotate(ang, resample=Image.BICUBIC)
    shadow = Image.new('RGBA', big.size, (0, 0, 0, 0))
    shadow.putalpha(big.getchannel('A').point(lambda v: int(v * 0.35)))
    shadow = shadow.filter(ImageFilter.GaussianBlur(1.6 * ss))
    for layer, off in ((shadow, 1.8), (big, 0)):
        small = layer.resize((layer.width // ss, layer.height // ss), Image.LANCZOS)
        px, py = int(cx - small.width / 2 + off), int(cy - small.height / 2 + off)
        base = img.convert('RGBA')
        base.paste(small, (px, py), small)
        img = base.convert('RGB')
    return img


def _gingham_tile(w, h, c1, c2, cell=12):
    ii, jj = np.meshgrid(np.arange(w), np.arange(h))
    a = ((ii // cell) % 2 == 0); b = ((jj // cell) % 2 == 0)
    k = np.where(a & b, 1.0, np.where(a ^ b, 0.62, 0.0))
    t = np.array(c2, 'float32') * (1 - k[..., None]) + np.array(c1, 'float32') * k[..., None]
    return Image.fromarray(np.clip(t, 0, 255).astype('uint8'))


def _mud(layer_draw, rng, w, h, count, color, rmin, rmax, ss=2):
    for _ in range(count):
        x = int(rng.integers(0, w)); y = int(h * (1 - rng.random() ** 2.6))
        r = int(rng.integers(rmin, rmax + 1))
        layer_draw.ellipse([(x - r) * ss, (y - r // 2) * ss, (x + r) * ss, (y + r // 2) * ss], fill=color)


def _glow(arr, lights, w, h, strength=0.6, radius=15.0):
    """Additive warm halo under each bulb."""
    ii, jj = np.meshgrid(np.arange(w, dtype='float32'), np.arange(h, dtype='float32'))
    halo = np.zeros((h, w), 'float32')
    for a, b in lights:
        cx, cy = a * w, b * h
        halo += np.exp(-(((ii - cx) ** 2 + (jj - cy) ** 2) / (2 * radius ** 2)))
    halo = np.clip(halo, 0, 1.0) * strength
    warm = np.array([255, 214, 96], 'float32')
    return arr * (1 - halo[..., None] * 0.55) + warm * halo[..., None] * 0.85


# ----------------------------------------------------------------------------- tent panels
PANEL_STYLE = {
    'front': dict(base=(255, 100, 18), hem='hem_orange', seed=11),
    'right': dict(base=(0, 158, 168), hem='hem_teal', seed=12),
    'back': dict(base=(242, 134, 20), hem='hem_orange', seed=13),
    'left': dict(base=(38, 198, 190), hem='hem_teal', seed=14),
}


def _panel(kind, lights):
    st = PANEL_STYLE[kind]
    w, h = PANEL_W, PANEL_H
    rng = np.random.default_rng(st['seed'] * 101)
    base = np.array(st['base'], 'float32')
    vv = np.linspace(0, 1, h)[:, None]                         # 0 = apex .. 1 = base
    uu = np.linspace(0, 1, w)[None, :]
    t = np.zeros((h, w, 3), 'float32'); t[:] = base
    t *= (1.13 - 0.22 * vv)[..., None]                          # sun-faded crown, richer low down
    # ripstop grid and fabric tension folds
    ii, jj = np.meshgrid(np.arange(w), np.arange(h))
    rip = 0.93 + 0.07 * ((ii % 7 == 0) | (jj % 7 == 0))
    t *= rip[..., None]
    fold = _lowfreq(rng, 6, (h, w))
    folds = 0.5 + 0.5 * np.sin(uu * 17 + fold * 7 + vv * 4)
    t *= (0.93 + 0.12 * folds)[..., None]
    g = _lowfreq(rng, 9, (h, w))
    # water streaks running down from the top
    streak = np.clip(_lowfreq(rng, 24, (h, w // 8)), 0, 1)
    streak = np.asarray(Image.fromarray((streak * 255).astype('uint8')).resize((w, h), Image.BICUBIC)).astype('float32') / 255
    t *= (1 - 0.13 * np.clip((streak - 0.55) * 3, 0, 1) * (1 - vv))[..., None]
    dirt = np.clip(g * 0.35 + np.clip((vv - 0.62) * 2.4, 0, 1) * (0.55 + g * 0.5), 0, 1)
    t *= (1.0 - 0.38 * dirt)[..., None]
    t += (dirt * 12)[..., None] * np.array([1.0, 0.7, -0.5], 'float32')
    # dark bathtub skirt along the base
    skirt = np.clip((vv - 0.935) / 0.012, 0, 1)
    sk = np.array(PALETTE['skirt'][0], 'float32') * (0.8 + 0.5 * g[..., None])
    t = t * (1 - skirt[..., None]) + sk * skirt[..., None]
    img = Image.fromarray(np.clip(t, 0, 255).astype('uint8'))
    ss = 2
    lay = _layer(w, h, ss); d = ImageDraw.Draw(lay)
    _mud(d, rng, w, h, 90, (84, 60, 34, 140), 1, 5)
    for x in (4, w - 5):                                        # stitched seams down both edges
        for y in range(2, int(h * 0.93), 7):
            d.line([(x * ss, y * ss), (x * ss, (y + 4) * ss)], fill=(30, 26, 22, 170), width=ss)
    d.line([(0, int(h * 0.935) * ss), (w * ss, int(h * 0.935) * ss)], fill=(24, 22, 24, 170), width=2 * ss)
    img = _flatten(img, lay, 0.4)

    def tape(*a, **k):
        nonlocal img
        img = _tape(img, *a, rng=rng, **k)

    if kind == 'front':
        # a gingham patch sewn on, an X of duct tape over a rip, a smiley sticker
        patch = _gingham_tile(54, 46, (214, 36, 44), (255, 250, 244))
        pl = Image.new('RGBA', (54, 46), (0, 0, 0, 0)); pl.paste(patch, (0, 0))
        pd = ImageDraw.Draw(pl)
        for k in range(0, 54, 5):
            pd.line([(k, 0), (k + 2, 0)], fill=(60, 40, 30, 255)); pd.line([(k, 45), (k + 2, 45)], fill=(60, 40, 30, 255))
        pl = pl.rotate(7, resample=Image.BICUBIC, expand=True)
        img = img.convert('RGBA'); img.alpha_composite(pl, (28, 122)); img = img.convert('RGB')
        lay = _layer(w, h, ss); dd = ImageDraw.Draw(lay)
        dd.line([(150 * ss, 244 * ss), (178 * ss, 276 * ss)], fill=(50, 22, 6, 230), width=3 * ss)    # the rip
        img = _flatten(img, lay, 0.5)
        tape(164, 262, 58, 14, 52); tape(164, 262, 58, 14, -52)
        lay = _layer(w, h, ss); _smiley(lay, 212, 96, 15); img = _flatten(img, lay, 0.4)
    elif kind == 'right':
        # big marker rainbow with a sun, plus a taped-up mend
        lay = _layer(w, h, ss); dd = ImageDraw.Draw(lay)
        cols = [(228, 36, 44), (255, 150, 20), (255, 224, 30), (60, 190, 80), (40, 120, 240), (140, 70, 200)]
        for k, c in enumerate(cols):
            r = 66 - k * 8
            _marker(dd, [(128 + r * math.cos(math.radians(a)), 292 - r * math.sin(math.radians(a))) for a in range(180, -1, -12)], c + (245,), 6, rng, 0.9)
        _marker(dd, [(40, 292), (36, 300)], (255, 255, 255, 0), 1, rng)
        for cx, cy in ((46, 296), (210, 296)):                               # cloud puffs
            for ox in (-10, 0, 10):
                dd.ellipse([(cx + ox - 11) * ss, (cy - 11 + abs(ox) * 0.3) * ss, (cx + ox + 11) * ss, (cy + 7) * ss], fill=(250, 250, 255, 235))
        img = _flatten(img, lay, 0.4)
        tape(70, 150, 70, 15, 20); tape(78, 168, 60, 15, -8); tape(190, 210, 70, 14, 74)
    elif kind == 'back':
        # long mend strips and a taped-up flyer (a lost cat, drawn as shapes) plus a warning triangle sticker
        tape(118, 100, 120, 14, 4); tape(130, 116, 100, 14, -3); tape(60, 240, 84, 14, 62)
        lay = _layer(w, h, ss); dd = ImageDraw.Draw(lay)
        fx, fy, fw, fh = 150, 190, 66, 84
        dd.rectangle([(fx + 3) * ss, (fy + 3) * ss, (fx + fw + 3) * ss, (fy + fh + 3) * ss], fill=(0, 0, 0, 70))
        dd.rectangle([fx * ss, fy * ss, (fx + fw) * ss, (fy + fh) * ss], fill=(246, 242, 218, 255))
        dd.rectangle([fx * ss, fy * ss, (fx + fw) * ss, (fy + 7) * ss], fill=(214, 40, 40, 255))
        cx, cy = fx + fw / 2, fy + 34                                       # a cat silhouette
        dd.ellipse([(cx - 11) * ss, (cy - 9) * ss, (cx + 11) * ss, (cy + 11) * ss], fill=(50, 46, 50, 255))
        dd.polygon([((cx - 11) * ss, (cy - 5) * ss), ((cx - 8) * ss, (cy - 18) * ss), ((cx - 1) * ss, (cy - 8) * ss)], fill=(50, 46, 50, 255))
        dd.polygon([((cx + 11) * ss, (cy - 5) * ss), ((cx + 8) * ss, (cy - 18) * ss), ((cx + 1) * ss, (cy - 8) * ss)], fill=(50, 46, 50, 255))
        for sx in (-4, 4):
            dd.ellipse([(cx + sx - 2) * ss, (cy - 4) * ss, (cx + sx + 2) * ss, (cy) * ss], fill=(250, 220, 40, 255))
        ly = fy + 56
        while ly < fy + fh - 12:
            dd.line([((fx + 5) * ss, ly * ss), ((fx + 5 + int(rng.integers(30, fw - 10))) * ss, ly * ss)], fill=(64, 64, 74, 255), width=ss)
            ly += 5
        for k in range(6):                                                  # tear-off tabs
            x0 = fx + 4 + k * 10
            dd.line([(x0 * ss, (fy + fh - 10) * ss), (x0 * ss, (fy + fh) * ss)], fill=(100, 100, 100, 255), width=ss)
        img = _flatten(img, lay, 0.4)
        tape(fx + 8, fy - 1, 22, 9, 8, torn=False); tape(fx + fw - 6, fy - 1, 22, 9, -10, torn=False)
        lay = _layer(w, h, ss); dd = ImageDraw.Draw(lay)
        tx, ty = 70, 150
        dd.polygon([(tx * ss, (ty - 18) * ss), ((tx + 17) * ss, (ty + 12) * ss), ((tx - 17) * ss, (ty + 12) * ss)], fill=(252, 214, 24, 255), outline=(30, 26, 20, 255))
        dd.rectangle([(tx - 1.5) * ss, (ty - 8) * ss, (tx + 1.5) * ss, (ty + 3) * ss], fill=(30, 26, 20, 255))
        dd.ellipse([(tx - 2) * ss, (ty + 5) * ss, (tx + 2) * ss, (ty + 9) * ss], fill=(30, 26, 20, 255))
        img = _flatten(img, lay, 0.4)
    else:  # left
        # a sewn felt heart, a crooked tape stripe and a polka-dot patch
        lay = _layer(w, h, ss); dd = ImageDraw.Draw(lay)
        hp = [(x * ss, y * ss) for x, y in _heart_pts(80, 184, 34)]
        dd.polygon(hp, fill=(226, 36, 74, 255))
        for k in range(len(hp) - 1):                                        # blanket stitching
            if k % 2 == 0:
                dd.line([hp[k], hp[k + 1]], fill=(255, 238, 220, 255), width=int(1.6 * ss))
        pp = _layer(60, 60, ss); pd = ImageDraw.Draw(pp)
        pd.rectangle([0, 0, 60 * ss, 60 * ss], fill=(255, 214, 40, 255))
        for ox in range(6, 60, 14):
            for oy in range(6, 60, 14):
                pd.ellipse([(ox - 3) * ss, (oy - 3) * ss, (ox + 3) * ss, (oy + 3) * ss], fill=(214, 40, 60, 255))
        pp = pp.rotate(-9, resample=Image.BICUBIC, expand=True)
        lay.alpha_composite(pp, (150 * ss, 220 * ss))
        img = _flatten(img, lay, 0.4)
        tape(150, 120, 96, 14, -22); tape(60, 270, 70, 14, 12)
    arr = np.asarray(img).astype('float32')
    arr = _glow(arr, lights, w, h)
    arr += rng.normal(0, 2.2, (h, w, 1))
    return Image.fromarray(np.clip(arr, 0, 255).astype('uint8'))


# ----------------------------------------------------------------------------- other regions
def _tarp():
    w, h = 256, 256
    rng = np.random.default_rng(31)
    vv = np.linspace(0, 1, h)[:, None]; uu = np.linspace(0, 1, w)[None, :]
    t = np.zeros((h, w, 3), 'float32'); t[:] = (26, 108, 232)
    f = _lowfreq(rng, 5, (h, w))
    diag = 0.5 + 0.5 * np.sin((uu * 1.2 + vv) * 38 + f * 5)                  # crinkly sheen bands
    t *= (0.80 + 0.30 * diag)[..., None]
    g = _lowfreq(rng, 8, (h, w))
    t *= (1 - 0.26 * g)[..., None]
    dirt = np.clip(g * 0.4 + np.clip(vv * 1.5 - 0.5, 0, 1) * 0.7, 0, 1)
    t *= (1 - 0.30 * dirt)[..., None]
    t += (dirt * 12)[..., None] * np.array([1.0, 0.8, -0.5], 'float32')
    img = Image.fromarray(np.clip(t, 0, 255).astype('uint8'))
    ss = 2
    lay = _layer(w, h, ss); d = ImageDraw.Draw(lay)
    _mud(d, rng, w, h, 50, (74, 60, 40, 130), 1, 4)
    for _ in range(14):                                                      # fold creases
        x0 = int(rng.integers(0, w)); y0 = int(rng.integers(0, h))
        d.line([(x0 * ss, y0 * ss), ((x0 + int(rng.integers(-40, 40))) * ss, (y0 + int(rng.integers(30, 80))) * ss)], fill=(10, 40, 120, 90), width=ss)
        d.line([((x0 + 2) * ss, y0 * ss), ((x0 + 2 + int(rng.integers(-40, 40))) * ss, (y0 + int(rng.integers(30, 80))) * ss)], fill=(150, 200, 255, 80), width=ss)
    for x in range(8, w - 6, 40):                                            # grommets along the bottom hem
        for y in (h - 10, ):
            d.ellipse([(x - 5) * ss, (y - 5) * ss, (x + 5) * ss, (y + 5) * ss], fill=(176, 180, 188, 255), outline=(60, 62, 68, 255), width=ss)
            d.ellipse([(x - 2.5) * ss, (y - 2.5) * ss, (x + 2.5) * ss, (y + 2.5) * ss], fill=(14, 40, 100, 255))
    for y in range(40, h - 20, 52):
        d.ellipse([(6 - 5) * ss, (y - 5) * ss, (6 + 5) * ss, (y + 5) * ss], fill=(176, 180, 188, 255), outline=(60, 62, 68, 255), width=ss)
    d.line([(0, (h - 20) * ss), (w * ss, (h - 20) * ss)], fill=(220, 240, 255, 90), width=2 * ss)      # hem seam
    for x in (3, w - 4):
        d.line([(x * ss, 0), (x * ss, h * ss)], fill=(220, 240, 255, 70), width=2 * ss)
    img = _flatten(img, lay, 0.4)
    lay = _layer(w, h, ss); _smiley(lay, 60, 100, 14); img = _flatten(img, lay, 0.3)      # a sticker wherever it sticks
    arr = np.asarray(img).astype('float32') + rng.normal(0, 2.5, (h, w, 1))
    return Image.fromarray(np.clip(arr, 0, 255).astype('uint8'))


def _fly():
    w, h = 512, 48
    rng = np.random.default_rng(32)
    t = np.zeros((h, w, 3), 'float32'); t[:] = (255, 220, 24)
    g = _lowfreq(rng, 8, (h, w))
    t *= (1 - 0.14 * g)[..., None]
    ii, jj = np.meshgrid(np.arange(w), np.arange(h))
    t *= (0.93 + 0.07 * ((ii % 7 == 0) | (jj % 7 == 0)))[..., None]
    img = Image.fromarray(np.clip(t, 0, 255).astype('uint8'))
    d = ImageDraw.Draw(img, 'RGBA')
    for y in (3, h - 4):
        d.line([(0, y), (w, y)], fill=(255, 250, 240, 255), width=3)          # white piping
        d.line([(0, y + (3 if y < 10 else -3)), (w, y + (3 if y < 10 else -3))], fill=(120, 90, 10, 140), width=1)
    for x in range(10, w, 14):
        d.line([(x, h // 2 - 1), (x + 7, h // 2 - 1)], fill=(110, 80, 8, 180), width=1)   # centre stitching
    for _ in range(40):
        x = int(rng.integers(0, w)); y = int(rng.integers(0, h)); r = int(rng.integers(1, 4))
        d.ellipse([x - r, y - r // 2, x + r, y + r // 2], fill=(86, 62, 30, 120))
    arr = np.asarray(img).astype('float32') + rng.normal(0, 2.5, (h, w, 1))
    return Image.fromarray(np.clip(arr, 0, 255).astype('uint8'))


def _zip():
    w, h = 512, 32
    t = np.zeros((h, w, 3), 'float32'); t[:] = (22, 22, 26)
    img = Image.fromarray(t.astype('uint8'))
    d = ImageDraw.Draw(img)
    for x in range(0, w, 4):
        d.rectangle([x, 9, x + 1, 22], fill=(196, 198, 204))
    d.line([(0, 15), (w, 15)], fill=(120, 124, 130), width=2)
    return img


def _interior():
    w, h = 192, 176
    rng = np.random.default_rng(33)
    vv = np.linspace(0, 1, h)[:, None]; uu = np.linspace(0, 1, w)[None, :]
    t = np.zeros((h, w, 3), 'float32'); t[:] = (14, 18, 26)
    glow = np.exp(-(((uu - 0.35) / 0.40) ** 2 + ((vv - 0.82) / 0.30) ** 2))     # a lantern burning somewhere in there
    t = t + glow[..., None] * np.array([186, 120, 44], 'float32') * 0.40
    t += rng.normal(0, 2, (h, w, 1))
    img = Image.fromarray(np.clip(t, 0, 255).astype('uint8'))
    d = ImageDraw.Draw(img, 'RGBA')
    d.ellipse([20, 120, 90, 176], fill=(110, 30, 44, 220))                         # a heap of blanket
    d.ellipse([46, 112, 86, 140], fill=(150, 136, 118, 200))                       # pillow
    d.ellipse([112, 126, 168, 170], fill=(60, 80, 110, 220))
    img = img.filter(ImageFilter.GaussianBlur(2.0))
    return img


def _bag():
    w, h = 128, 128
    rng = np.random.default_rng(34)
    t = np.zeros((h, w, 3), 'float32'); t[:] = (196, 30, 44)
    g = _lowfreq(rng, 6, (h, w))
    t *= (1 - 0.30 * g)[..., None]
    img = Image.fromarray(np.clip(t, 0, 255).astype('uint8'))
    d = ImageDraw.Draw(img, 'RGBA')
    for x in range(0, w, 16):                                                       # quilting channels
        d.line([(x, 0), (x, h)], fill=(70, 8, 18, 150), width=2)
        d.line([(x + 2, 0), (x + 2, h)], fill=(255, 140, 150, 70), width=1)
    for y in range(8, h, 32):
        d.line([(0, y), (w, y)], fill=(250, 214, 30, 200), width=3)                  # yellow stripes
    d.rectangle([w - 22, 0, w, h], fill=(140, 18, 32, 255))                          # gathered foot end
    for y in range(4, h, 8):
        d.line([(w - 22, y), (w, y)], fill=(80, 8, 18, 160), width=1)
    for _ in range(12):
        x = int(rng.integers(0, w)); y = int(rng.integers(0, h)); r = int(rng.integers(2, 6))
        d.ellipse([x - r, y - r, x + r, y + r], fill=(60, 40, 30, 70))
    arr = np.asarray(img).astype('float32') + rng.normal(0, 3, (h, w, 1))
    return Image.fromarray(np.clip(arr, 0, 255).astype('uint8'))


def _gingham():
    img = _gingham_tile(128, 128, (216, 36, 48), (255, 250, 242), cell=16)
    arr = np.asarray(img).astype('float32')
    rng = np.random.default_rng(35)
    g = _lowfreq(rng, 6, (128, 128))
    arr *= (1 - 0.22 * g)[..., None]
    arr += rng.normal(0, 3, (128, 128, 1))
    img = Image.fromarray(np.clip(arr, 0, 255).astype('uint8'))
    d = ImageDraw.Draw(img, 'RGBA')
    d.ellipse([70, 60, 100, 82], fill=(70, 40, 20, 110))                             # coffee ring
    d.ellipse([74, 63, 96, 79], outline=(70, 40, 20, 150), width=2)
    return img


def _cardboard(w, h, rng, with_art):
    t = np.zeros((h, w, 3), 'float32'); t[:] = (204, 158, 104)
    g = _lowfreq(rng, 6, (h, w))
    t *= (1 - 0.26 * g)[..., None]
    ii, jj = np.meshgrid(np.arange(w), np.arange(h))
    t *= (0.94 + 0.06 * np.sin(jj * 1.6))[..., None]                                 # corrugation
    img = Image.fromarray(np.clip(t, 0, 255).astype('uint8'))
    ss = 2
    lay = _layer(w, h, ss); d = ImageDraw.Draw(lay)
    if with_art:
        # heart (below), marker outlined, then a big smiling sun (above) with rays: shapes only, no lettering
        hp = _heart_pts(64, 96, 30)
        d.polygon(_wobble([(x * ss, y * ss) for x, y in hp], rng, 1.0 * ss), fill=(226, 36, 56, 255))
        _marker(d, hp, (120, 12, 28, 255), 2.4, rng, 0.8, closed=True)
        sx, sy, sr = 64, 44, 18
        for k in range(12):
            a = 2 * math.pi * k / 12 + 0.1
            _marker(d, [(sx + math.cos(a) * (sr + 4), sy + math.sin(a) * (sr + 4)), (sx + math.cos(a) * (sr + 15), sy + math.sin(a) * (sr + 15))],
                    (252, 160, 0, 255), 3.4, rng, 0.7)
        ring = [(sx + math.cos(a / 14 * 2 * math.pi) * sr, sy + math.sin(a / 14 * 2 * math.pi) * sr) for a in range(15)]
        d.polygon(_wobble([(x * ss, y * ss) for x, y in ring], rng, 0.8 * ss), fill=(255, 224, 30, 255))
        _marker(d, ring, (200, 100, 0, 255), 2.4, rng, 0.7, closed=True)
        for ex in (-6, 6):
            d.ellipse([(sx + ex - 2) * ss, (sy - 6) * ss, (sx + ex + 2) * ss, (sy - 1) * ss], fill=(40, 24, 10, 255))
        d.arc([(sx - 9) * ss, (sy - 4) * ss, (sx + 9) * ss, (sy + 11) * ss], 20, 160, fill=(40, 24, 10, 255), width=int(2.2 * ss))
        for sxx, syy in ((16, 20), (108, 18), (14, 100), (112, 104)):               # tiny sparkles
            _marker(d, [(sxx - 4, syy), (sxx + 4, syy)], (255, 255, 255, 255), 1.8, rng, 0.3)
            _marker(d, [(sxx, syy - 4), (sxx, syy + 4)], (255, 255, 255, 255), 1.8, rng, 0.3)
        _marker(d, [(4, 4), (w - 4, 5), (w - 5, h - 4), (5, h - 5)], (60, 40, 20, 255), 2.2, rng, 1.2, closed=True)   # wobbly border
    else:
        for _ in range(7):
            x0 = int(rng.integers(8, w - 40)); y0 = int(rng.integers(8, h - 10))
            d.line([(x0 * ss, y0 * ss), ((x0 + int(rng.integers(20, 50))) * ss, (y0 + int(rng.integers(-3, 4))) * ss)], fill=(90, 62, 36, 150), width=ss)
    _mud(d, rng, w, h, 20, (86, 60, 34, 90), 1, 4)
    img = _flatten(img, lay, 0.4)
    arr = np.asarray(img).astype('float32') + rng.normal(0, 3, (h, w, 1))
    return Image.fromarray(np.clip(arr, 0, 255).astype('uint8'))


def _can():
    w, h = 128, 64
    t = np.zeros((h, w, 3), 'float32'); t[:] = (96, 176, 64)
    img = Image.fromarray(t.astype('uint8'))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, w, 10], fill=(60, 120, 40)); d.rectangle([0, h - 10, w, h], fill=(60, 120, 40))
    d.rectangle([w // 2 - 36, 14, w // 2 + 36, h - 14], fill=(252, 206, 24))
    d.polygon([(w // 2, 18), (w // 2 + 14, h - 18), (w // 2 - 14, h - 18)], fill=(224, 60, 20))
    return img


def _flame():
    w, h = 64, 64
    vv = np.linspace(0, 1, h)[:, None]
    base = np.array([60, 120, 255], 'float32'); mid = np.array([255, 150, 20], 'float32'); tip = np.array([255, 244, 170], 'float32')
    k = np.clip(vv * 2, 0, 1)[..., None]
    t = base * (1 - k) + mid * k
    k2 = np.clip(vv * 2 - 1, 0, 1)[..., None]
    t = t * (1 - k2) + tip * k2
    t = np.broadcast_to(t, (h, w, 3)).copy()
    return Image.fromarray(t.astype('uint8'))


def _flag():
    w, h = 64, 64
    img = Image.new('RGB', (w, h), (232, 40, 60))
    d = ImageDraw.Draw(img, 'RGBA')
    d.rectangle([0, 0, w, 6], fill=(250, 206, 30))
    d.rectangle([0, h - 6, w, h], fill=(250, 206, 30))
    hp = _heart_pts(32, 32, 14)
    d.polygon(hp, fill=(255, 250, 244, 255))
    return img


def _tile(name, seed):
    base, grime, scratch, _ = PALETTE[name]
    rng = np.random.default_rng(seed)
    t = np.zeros((CELL, CELL, 3), 'float32'); t[:] = base
    t *= np.linspace(1.08, 0.94, CELL)[:, None, None]
    g = _lowfreq(rng, 5, (CELL, CELL))
    t *= (1.0 - grime * 0.5 * g)[..., None]
    t += rng.normal(0, 3.5, (CELL, CELL, 1))
    img = Image.fromarray(np.clip(t, 0, 255).astype('uint8'))
    d = ImageDraw.Draw(img)
    for _ in range(int(8 * scratch) + (1 if scratch > 0 else 0)):
        y = int(rng.integers(0, CELL)); x0 = int(rng.integers(0, CELL)); ln = int(rng.integers(6, 24))
        d.line([(x0, y), (x0 + ln, y)], fill=(235,) * 3 if rng.random() < 0.5 else (22,) * 3, width=1)
    return img


def paint(out_png):
    atlas = Image.new('RGB', (W, W), (110, 110, 110))
    rough = np.full((W, W), 0.6, 'float32')

    def put(name, img, r):
        x0, y0, w, h = REGION[name]
        atlas.paste(img, (x0, y0)); rough[y0:y0 + h, x0:x0 + w] = r

    # lights per panel (a, b) for the bulb halos
    pts, bulbs = string_path()
    lights = {k: [] for k in PANELS}
    for i in bulbs:
        name, ab = panel_ab(*pts[i])
        lights[name].append(ab)
    for name, r in (('front', 0.55), ('right', 0.55), ('back', 0.62), ('left', 0.55)):
        put(name, _panel(name, lights[name]), r)
    put('tarp', _tarp(), 0.30)
    put('fly', _fly(), 0.50)
    put('zip', _zip(), 0.40)
    put('interior', _interior(), 0.95)
    put('bag', _bag(), 0.65)
    put('gingham', _gingham(), 0.90)
    put('sign', _cardboard(128, 128, np.random.default_rng(36), True), 0.90)
    put('signback', _cardboard(128, 128, np.random.default_rng(37), False), 0.90)
    put('can', _can(), 0.35)
    put('flame', _flame(), 0.20)
    put('flag', _flag(), 0.70)
    cells = {}
    for i, name in enumerate(ORDER):
        col, row = i % 32, i // 32
        atlas.paste(_tile(name, 400 + i), (col * CELL, CELL_Y0 + row * CELL))
        rough[CELL_Y0 + row * CELL:CELL_Y0 + (row + 1) * CELL, col * CELL:(col + 1) * CELL] = PALETTE[name][3]
        cells[name] = (col, row)
    atlas.save(out_png)
    return cells, rough


def pm_image(rough):
    """Physical map: R metal (0), G roughness, B 255, A 255 (same channel order as the cart's flat PM (0,200,255,255))."""
    small = np.asarray(Image.fromarray((np.clip(rough, 0, 1) * 255).astype('uint8')).resize((256, 256), Image.BILINEAR)).astype('float32')
    g = 70 + small * (235 - 70) / 255.0
    out = np.zeros((256, 256, 4), 'uint8')
    out[..., 1] = np.clip(g, 0, 255)
    out[..., 2] = 255; out[..., 3] = 255
    return Image.fromarray(out, 'RGBA')


def nm_image():
    """Flat tangent-space normal map in the cart's proven encoding (0,128,255,128)."""
    out = np.zeros((256, 256, 4), 'uint8')
    out[..., 1] = 128; out[..., 2] = 255; out[..., 3] = 128
    return Image.fromarray(out, 'RGBA')


def uv_px(x, y):
    return (x / W, 1.0 - y / W)


def uv(cell, f, g):
    """UV inside a 32px palette cell; 2px inset."""
    col, row = cell
    span = CELL - 4.0
    return uv_px(col * CELL + 2.0 + f * span, CELL_Y0 + row * CELL + 2.0 + g * span)


def ruv(name, a, b):
    """UV inside a region. a = 0..1 along the region's u (left -> right), b = 0..1 along v (top -> bottom)."""
    x0, y0, w, h = REGION[name]
    return uv_px(x0 + 1.0 + a * (w - 2.0), y0 + 1.0 + b * (h - 2.0))
