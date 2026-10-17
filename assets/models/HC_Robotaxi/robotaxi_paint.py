"""Texture atlas painter and shared car envelope for the Broken-Down Robotaxi (1024x1024), AI-generated procedural art.

Everything is drawn from world coordinates (metres) through planar projections, so the geometry script and this painter
always agree. The body shell is UV-mapped per quad by its normal: side (R / L), top (hood, windshield, roof), front, rear.

Atlas layout (pixels, origin top-left):
  (  0,  0)-(512,224)   side elevation, +X side  (nose on the left as seen from outside)
  (512,  0)-(1024,224)  side elevation, -X side  (nose on the right as seen from outside)
  (  0,224)-(240,756)   plan view: hood, windshield, roof, LiDAR ring decal
  (240,224)-(480,448)   front view: nose fascia
  (480,224)-(720,448)   rear view: tailgate glass, tail lights, smiley sticker
  (720,224)-(896,352)   LiDAR dome (u around, v flange -> tip)
  (896,224)-(1024,416)  traffic cone (u around, v tip -> base)
  (720,352)-(848,480)   rider-rating star sticker (planar)
  (240,448)-(496,512)   tyre (u around, v across)
  (496,448)-(624,576)   wheel face (planar disc)
  (240,512)-(368,576)   amber hazard lens
  (368,512)-(496,640)   deflated balloon (u around, v tip -> knot)
  (496,576)-(624,640)   parking-ticket slip
  (  0,992)-(1024,1024) 32 small 32px palette cells
paint() writes the base colour PNG and returns (cells, rough). Lettering is deliberately absent (BG3 mirrors the DAE).
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W = 1024
SS = 2                      # supersampling of every painted region
S = 142.0                   # pixels per metre of the planar projections
YT, XH, ZT = 1.58, 0.845, 1.87
CELL, CELL_Y0 = 32, 992

REGION = {
    'sideR': (0, 0, 512, 224), 'sideL': (512, 0, 512, 224),
    'top': (0, 224, 240, 532), 'front': (240, 224, 240, 224), 'rear': (480, 224, 240, 224),
    'lidar': (720, 224, 176, 128), 'cone': (896, 224, 128, 192), 'star': (720, 352, 128, 128),
    'tire': (240, 448, 256, 64), 'wheelface': (496, 448, 128, 128), 'lens': (240, 512, 128, 64),
    'balloon': (368, 512, 128, 128), 'ticket': (496, 576, 128, 64),
}

# name: (base RGB, rough)
PALETTE = {
    'white':   ((246, 247, 250), 0.22),
    'black':   ((22, 23, 28), 0.45),
    'glass':   ((12, 15, 22), 0.08),
    'teal':    ((0, 236, 214), 0.20),
    'magenta': ((255, 28, 172), 0.20),
    'amber':   ((255, 168, 0), 0.12),
    'orange':  ((255, 102, 0), 0.45),
    'red':     ((236, 30, 44), 0.30),
    'yellow':  ((255, 214, 24), 0.30),
    'grey':    ((120, 124, 132), 0.50),
    'silver':  ((190, 194, 202), 0.30),
    'rubber':  ((30, 30, 33), 0.85),
}
ORDER = list(PALETTE)

# ----------------------------------------------------------------------------- shared car envelope (metres)
BOT_Z = [-1.8, -1.65, -1.5, 1.5, 1.65, 1.74, 1.8]
BOT_Y = [.27, .21, .19, .19, .21, .24, .28]
BELT_Z = [-1.8, -1.74, -1.6, -1.3, -0.5, 0.3, 0.6, 0.9, 1.3, 1.5, 1.65, 1.74, 1.8]
BELT_Y = [.86, .88, .90, .91, .91, .91, .90, .86, .80, .76, .70, .62, .52]
ROOF_Z = [-1.8, -1.72, -1.62, -1.52, -1.40, -1.25, -0.15, 0.6]
ROOF_Y = [.89, .95, 1.08, 1.20, 1.28, 1.31, 1.31, .93]
WID_Z = [-1.8, -1.77, -1.7, -1.55, -1.45, 1.45, 1.55, 1.65, 1.74, 1.8]
WID_Y = [.58, .67, .74, .79, .80, .80, .79, .76, .69, .58]
WHEEL_Z = (1.12, -1.10)
WHEEL_X, WHEEL_YC, WHEEL_R, WHEEL_HW = 0.72, 0.32, 0.315, 0.10
ARCH_R, WELL_X, ARCH_BLEND = 0.39, 0.60, 0.11
LOW = [(0, 0), (0.66, 0), (0.92, 0.06), (1.0, 0.17), (1.0, 0.31), (1.0, 0.46), (1.0, 0.62), (1.0, 0.77), (0.97, 0.94), (0.93, 1.0)]
CAB = [(0.69, 0.18), (0.62, 0.62), (0.50, 0.96), (0.0, 1.0)]
HOOD_X = [0.75, 0.5, 0.25, 0.0]
HOOD_YN = [0.45, 0.85, 0.98, 1.0]


def env(z):
    """(ybot, ybelt, yroof, half width) at z; yroof is the crowned hood/deck height where there is no cabin."""
    z = np.asarray(z, float)
    yb = np.interp(z, BOT_Z, BOT_Y)
    be = np.interp(z, BELT_Z, BELT_Y)
    ro = np.interp(z, ROOF_Z, ROOF_Y)
    ro = np.where(z > 0.6, be + 0.03, np.maximum(ro, be + 0.03))
    return yb, be, ro, np.interp(z, WID_Z, WID_Y)


def smooth(t):
    t = np.clip(t, 0, 1)
    return t * t * (3 - 2 * t)


def inset(x, y, z):
    g = 0.0
    for zc in WHEEL_Z:
        dy = y - WHEEL_YC
        reff = ARCH_R if dy <= 0 else math.sqrt(max(ARCH_R ** 2 - dy ** 2, 0.0))
        g = max(g, float(smooth((reff - abs(z - zc)) / ARCH_BLEND)))
    return x + (min(x, WELL_X) - x) * g


def arch_field(z, y):
    """Vectorised wheel-arch recess factor g(z, y) (0 = body surface, 1 = fully inset), same as inset()."""
    z = np.asarray(z, float); y = np.asarray(y, float)
    g = np.zeros_like(z + y)
    for zc in WHEEL_Z:
        dy = y - WHEEL_YC
        reff = np.where(dy <= 0, ARCH_R, np.sqrt(np.maximum(ARCH_R ** 2 - dy ** 2, 0.0)))
        g = np.maximum(g, smooth((reff - np.abs(z - zc)) / ARCH_BLEND))
    return g


def half_section(z):
    """Right half of the body cross-section at z, bottom centre -> top centre: len(LOW)+len(CAB) (x, y) points, wheel arches cut in."""
    yb, be, ro, w = (float(v) for v in env(z))
    h = ro - be
    c = float(np.clip((h - 0.03) / 0.36, 0, 1))
    pts = [(f * w, yb + yn * (be - yb)) for f, yn in LOW]
    sx = LOW[-1][0] * w
    for k, (cx, cyn) in enumerate(CAB):
        x = HOOD_X[k] * sx * (1 - c) + cx * c
        yn = HOOD_YN[k] * (1 - c) + cyn * c
        pts.append((x, be + yn * h))
    return [(inset(x, y, z), y) for x, y in pts]


def surface_y(x, z):
    """Height of the top surface (hood/windshield/roof) at (x, z), by interpolating the top part of the section."""
    pts = half_section(z)[len(LOW) - 1:]          # shoulder -> roof centre, x decreasing
    xs = [p[0] for p in pts][::-1]
    ys = [p[1] for p in pts][::-1]
    return float(np.interp(abs(x), xs, ys))


# ----------------------------------------------------------------------------- projections and UVs
def project(name, x, y, z):
    """World -> region pixel coordinates (floats, region-local, 1x)."""
    if name == 'sideR':
        return (1.8 - z) * S, (YT - y) * S
    if name == 'sideL':
        return (z + 1.8) * S, (YT - y) * S
    if name == 'top':
        return (XH - x) * S, (ZT - z) * S
    if name == 'front':
        return (x + XH) * S, (YT - y) * S
    if name == 'rear':
        return (XH - x) * S, (YT - y) * S
    raise KeyError(name)


def uv_px(x, y):
    return (x / W, 1.0 - y / W)


def uv_world(name, x, y, z):
    px, py = project(name, x, y, z)
    x0, y0, w, h = REGION[name]
    return uv_px(x0 + min(max(px, 1.0), w - 1.0), y0 + min(max(py, 1.0), h - 1.0))


def ruv(name, a, b):
    """UV inside a region. a = 0..1 left -> right, b = 0..1 top -> bottom."""
    x0, y0, w, h = REGION[name]
    return uv_px(x0 + 1.0 + a * (w - 2.0), y0 + 1.0 + b * (h - 2.0))


def cuv(cell, f, g):
    col, row = cell
    return uv_px(col * CELL + 2.0 + f * (CELL - 4.0), CELL_Y0 + row * CELL + 2.0 + g * (CELL - 4.0))


# ----------------------------------------------------------------------------- painting helpers
def lowfreq(rng, n, shape):
    a = rng.random((n, n)).astype('float32')
    im = Image.fromarray((a * 255).astype('uint8')).resize((shape[1], shape[0]), Image.BICUBIC)
    return np.asarray(im).astype('float32') / 255.0


class Canvas:
    """A region painted at SS x; shapes are given in world coordinates (or pixel coordinates via .px)."""

    def __init__(self, name, bg=(252, 252, 254), rough=0.22):
        self.name = name
        x0, y0, self.w, self.h = REGION[name]
        self.im = Image.new('RGB', (self.w * SS, self.h * SS), bg)
        self.rm = Image.new('L', (self.w * SS, self.h * SS), int(rough * 255))
        self.glassm = Image.new('L', (self.w * SS, self.h * SS), 0)
        self.d = ImageDraw.Draw(self.im, 'RGBA')
        self.dr = ImageDraw.Draw(self.rm)
        self.dg = ImageDraw.Draw(self.glassm)

    def p(self, x, y, z):
        px, py = project(self.name, x, y, z)
        return (px * SS, py * SS)

    def poly(self, pts, fill, rough=None, outline=None, width=1):
        q = [self.p(*pt) for pt in pts]
        self.d.polygon(q, fill=fill, outline=outline, width=width) if outline else self.d.polygon(q, fill=fill)
        if rough is not None:
            self.dr.polygon(q, fill=int(rough * 255))

    def line(self, pts, fill, width=2, rough=None):
        q = [self.p(*pt) for pt in pts]
        self.d.line(q, fill=fill, width=int(width * SS), joint='curve')
        if rough is not None:
            self.dr.line(q, fill=int(rough * 255), width=int(width * SS))

    def disc(self, c, r, fill, rough=None, outline=None, width=1):
        px, py = self.p(*c)
        rr = r * S * SS
        box = [px - rr, py - rr, px + rr, py + rr]
        self.d.ellipse(box, fill=fill, outline=outline, width=int(width * SS)) if outline else self.d.ellipse(box, fill=fill)
        if rough is not None:
            self.dr.ellipse(box, fill=int(rough * 255))

    def ellipse(self, c, rx, ry, fill, rough=None):
        """Ellipse with radii (rx along image x in metres, ry along image y in metres) around world point c."""
        px, py = self.p(*c)
        a, b = rx * S * SS, ry * S * SS
        self.d.ellipse([px - a, py - b, px + a, py + b], fill=fill)
        if rough is not None:
            self.dr.ellipse([px - a, py - b, px + a, py + b], fill=int(rough * 255))

    def glass(self, pts, tint=(12, 15, 22), rough=0.08):
        self.poly(pts, tint + (255,), rough)
        self.dg.polygon([self.p(*pt) for pt in pts], fill=255)

    def glow(self, c, r, color, strength=200):
        """Soft halo (blurred disc) around a world point, composited over the colour map."""
        px, py = self.p(*c)
        rr = r * S * SS
        layer = Image.new('RGBA', self.im.size, (0, 0, 0, 0))
        ImageDraw.Draw(layer).ellipse([px - rr, py - rr, px + rr, py + rr], fill=color + (strength,))
        layer = layer.filter(ImageFilter.GaussianBlur(rr * 0.45))
        self.im = Image.alpha_composite(self.im.convert('RGBA'), layer).convert('RGB')
        self.d = ImageDraw.Draw(self.im, 'RGBA')

    def blend_gradient(self, mask_pts, c0, c1, axis_pts, rough=0.18):
        """Fill a polygon with a linear gradient c0 -> c1 between two pixel-space points."""
        mask = Image.new('L', self.im.size, 0)
        ImageDraw.Draw(mask).polygon([self.p(*pt) for pt in mask_pts], fill=255)
        (ax, ay), (bx, by) = [self.p(*pt) for pt in axis_pts]
        yy, xx = np.mgrid[0:self.im.size[1], 0:self.im.size[0]]
        t = np.clip(((xx - ax) * (bx - ax) + (yy - ay) * (by - ay)) / ((bx - ax) ** 2 + (by - ay) ** 2 + 1e-9), 0, 1)[..., None]
        grad = (np.array(c0, 'float32') * (1 - t) + np.array(c1, 'float32') * t)
        m = (np.asarray(mask).astype('float32') / 255.0)[..., None]
        base = np.asarray(self.im).astype('float32')
        self.im = Image.fromarray(np.clip(base * (1 - m) + grad * m, 0, 255).astype('uint8'))
        self.d = ImageDraw.Draw(self.im, 'RGBA')
        self.rm.paste(int(rough * 255), mask=mask)

    def mask_blend(self, mask, color, rough=None):
        """Blend a colour over the canvas through a float mask (SS-sized, 0..1)."""
        base = np.asarray(self.im).astype('float32')
        m = mask[..., None]
        self.im = Image.fromarray(np.clip(base * (1 - m) + np.array(color, 'float32') * m, 0, 255).astype('uint8'))
        self.d = ImageDraw.Draw(self.im, 'RGBA')
        if rough is not None:
            r = np.asarray(self.rm).astype('float32') / 255.0
            self.rm = Image.fromarray((np.clip(r * (1 - mask) + rough * mask, 0, 1) * 255).astype('uint8'))
            self.dr = ImageDraw.Draw(self.rm)

    def finish(self, seed, hfun=None, dirt=0.5):
        """Glass sheen, road-film grime and noise; returns (RGB at 1x, rough at 1x)."""
        rng = np.random.default_rng(seed)
        arr = np.asarray(self.im).astype('float32')
        h, w = arr.shape[:2]
        yy, xx = np.mgrid[0:h, 0:w].astype('float32')
        gm = (np.asarray(self.glassm).astype('float32') / 255.0)[..., None]
        s = np.sin((xx * 0.55 + yy * 1.0) / (9.0 * SS)) * 0.5 + 0.5
        bands = np.clip((s - 0.78) * 6.0, 0, 1)[..., None]
        arr = arr + gm * (bands * np.array([40, 70, 100], 'float32') + 14 * np.array([0.3, 0.6, 1.0], 'float32') * (yy / h)[..., None])
        g = lowfreq(rng, 9, (h, w))
        hf = np.zeros((h, w), 'float32') + 0.25
        if hfun is not None:
            hf = np.clip((0.62 - hfun(xx / SS, yy / SS)) / 0.52, 0, 1) * 0.85 + 0.15
        dm = np.clip(g * hf * 1.5, 0, 1) * dirt
        arr *= (1.0 - 0.34 * dm)[..., None]
        arr += (dm * 12)[..., None] * np.array([1.0, 0.6, -0.6], 'float32')
        # fine grain
        arr += rng.normal(0, 2.0, (h, w, 1))
        img = Image.fromarray(np.clip(arr, 0, 255).astype('uint8')).resize((self.w, self.h), Image.LANCZOS)
        rough = np.asarray(self.rm).astype('float32') / 255.0
        rough = np.clip(rough + 0.25 * dm * (1 - gm[..., 0]), 0, 1)
        rimg = Image.fromarray((rough * 255).astype('uint8')).resize((self.w, self.h), Image.BILINEAR)
        return img, np.asarray(rimg).astype('float32') / 255.0


def side_hfun(name):
    return lambda px, py: YT - py / S


def star_pts(cx, cy, ro, ri, rot=-math.pi / 2):
    pts = []
    for k in range(10):
        a = rot + k * math.pi / 5
        r = ro if k % 2 == 0 else ri
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def smiley(d, cx, cy, r, SSf=1.0, face=(30, 28, 20, 255), bg=(255, 214, 24, 255), smile=True):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=bg, outline=(70, 55, 10, 255), width=max(1, int(r / 14)))
    e = r * 0.16
    for sx in (-1, 1):
        d.ellipse([cx + sx * r * 0.36 - e, cy - r * 0.28 - e * 1.4, cx + sx * r * 0.36 + e, cy - r * 0.28 + e * 1.4], fill=face)
    if smile:
        d.arc([cx - r * 0.55, cy - r * 0.35, cx + r * 0.55, cy + r * 0.62], 25, 155, fill=face, width=max(2, int(r / 9)))
    else:
        d.line([(cx - r * 0.4, cy + r * 0.38), (cx + r * 0.4, cy + r * 0.38)], fill=face, width=max(2, int(r / 9)))


# ----------------------------------------------------------------------------- body regions
def cab_band(z0, z1, yn0, yn1, n=24, zend_bot=None):
    """World polygon (x unused, set by caller) of a window on the cabin side between z0 and z1 and cabin fractions yn0..yn1."""
    zs = np.linspace(z0, z1, n)
    bot, top = [], []
    for z in zs:
        yb, be, ro, _ = env(z)
        h = float(ro - be)
        bot.append((z, float(be + yn0 * h)))
        top.append((z, float(be + yn1 * h)))
    return bot + top[::-1]


def paint_side(name, seed, left):
    c = Canvas(name)
    xs = 0.8 if name == 'sideR' else -0.8
    def W3(zy):
        return [(xs, y, z) for z, y in zy]
    # ----- livery swoosh: teal -> magenta tapered band low on the doors
    zs = np.linspace(1.62, -1.62, 40)
    up = [(xs, 0.43 + 0.02 + 0.045 * (1.62 - z) / 3.24 + 0.012 * math.sin(z * 2.2), z) for z in zs]
    dn = [(xs, 0.43 - 0.02 - 0.045 * (1.62 - z) / 3.24 + 0.012 * math.sin(z * 2.2), z) for z in zs]
    c.blend_gradient(up + dn[::-1], (0, 235, 215), (255, 40, 175), [(xs, 0.4, 1.62), (xs, 0.4, -1.62)])
    # thin pinstripe above it
    c.line([(xs, 0.53 + 0.05 * (1.62 - z) / 3.24 + 0.012 * math.sin(z * 2.2), z) for z in zs], (255, 40, 175, 255), width=0.014)
    # ----- cabin glass: blacked-out windows with white pillars
    for z0, z1, y0, y1 in ((0.40, -0.21, 0.14, 0.80), (-0.35, -1.46, 0.14, 0.80)):
        band = cab_band(z0, z1, y0, y1)
        c.glass(W3(band))
    # belt-line trim and shoulder crease
    c.line([(xs, float(env(z)[1]) + 0.002, z) for z in np.linspace(0.6, -1.7, 24)], (40, 42, 50, 255), width=0.014)
    c.line([(xs, 0.71 + 0.2 * (z > 0.9) * (z - 0.9), z) for z in np.linspace(1.5, -1.65, 20)], (200, 205, 214, 255), width=0.008)
    # door seams
    for zv in (0.52, -0.28, -1.02):
        yb, be, ro, _ = env(zv)
        c.line([(xs, float(be) - 0.01, zv), (xs, 0.27, zv)], (120, 126, 134, 255), width=0.008)
    c.line([(xs, 0.27, 0.52), (xs, 0.27, -1.02)], (120, 126, 134, 255), width=0.008)
    # door handles
    for zh in (0.10, -0.62):
        c.poly(W3([(zh + 0.08, 0.82), (zh - 0.08, 0.82), (zh - 0.08, 0.795), (zh + 0.08, 0.795)]), (30, 32, 38, 255), 0.4)
    # ----- wheel arches: dark well exactly where the geometry is recessed, black flare trim at its rim
    h2, w2 = c.im.size[1], c.im.size[0]
    yy, xx = np.mgrid[0:h2, 0:w2].astype('float32')
    zz = (1.8 - xx / SS / S) if name == 'sideR' else (xx / SS / S - 1.8)
    yv = YT - yy / SS / S
    g = arch_field(zz, yv)
    rim = np.clip(1 - np.abs(g - 0.5) * 2.0, 0, 1) ** 0.6
    c.mask_blend(np.clip(g * 1.4, 0, 1), (26, 27, 32), 0.7)
    c.mask_blend(rim * 0.55 * (yv > 0.21), (10, 10, 12), 0.6)
    # rocker panel (black plastic) low on the body, between the wheels
    c.poly(W3([(1.40, 0.255), (-1.40, 0.255), (-1.40, 0.20), (1.40, 0.20)]), (26, 27, 32, 255), 0.55)
    # ----- amber hazard markers glowing at the corners
    for zm, ym in ((1.60, 0.55), (-1.63, 0.60)):
        c.glow((xs, ym, zm), 0.13, (255, 170, 0), 210)
        c.ellipse((xs, ym, zm), 0.045, 0.028, (255, 190, 20, 255), 0.1)
        c.ellipse((xs, ym, zm), 0.022, 0.012, (255, 252, 200, 255), 0.1)
    # ----- sensor ring decal on the front door (magenta / white / magenta)
    if not left:
        cc = (xs, 0.585, 0.17)
        c.disc(cc, 0.125, (255, 28, 172, 255), 0.18)
        c.disc(cc, 0.095, (250, 250, 252, 255), 0.18)
        c.disc(cc, 0.070, (255, 28, 172, 255), 0.18)
        c.disc(cc, 0.040, (22, 24, 34, 255), 0.1)
        c.disc((xs, 0.585, 0.155), 0.012, (200, 255, 255, 255), 0.05)
    else:
        # left side: sensor ring is peeling off, half-ring only
        cc = (xs, 0.585, 0.17)
        c.disc(cc, 0.125, (255, 28, 172, 255), 0.18)
        c.disc(cc, 0.095, (250, 250, 252, 255), 0.18)
        c.disc(cc, 0.070, (255, 28, 172, 255), 0.18)
        c.disc(cc, 0.040, (22, 24, 34, 255), 0.1)
        c.poly(W3([(0.30, 0.55), (0.22, 0.72), (0.05, 0.72), (0.05, 0.55)]), (244, 246, 249, 255))
    # ----- rider rating: five stars on the rear door, one lit, four grey
    for k in range(5):
        zc = -0.46 - 0.17 * k
        pts = [(xs, y, z) for z, y in star_pts(zc, 0.62, 0.062, 0.027, rot=math.pi / 2)]
        c.poly(pts, (255, 196, 28, 255) if k == 0 else (150, 154, 164, 255), 0.2)
    # ----- duct-tape X over a dent on the front fender / door
    zt, yt = (1.02, 0.66) if not left else (-0.80, 0.70)
    c.glow((xs, yt, zt), 0.20, (90, 92, 100), 60)
    for sgn in (1, -1):
        c.line([(xs, yt - 0.075 * sgn, zt - 0.13), (xs, yt + 0.075 * sgn, zt + 0.13)], (178, 184, 192, 255), width=0.042, rough=0.35)
        c.line([(xs, yt - 0.075 * sgn + 0.02, zt - 0.13), (xs, yt + 0.075 * sgn + 0.02, zt + 0.13)], (230, 234, 240, 120), width=0.01)
    # ----- a long scratch and scuff marks
    rng = np.random.default_rng(seed + 5)
    for _ in range(9):
        z0 = float(rng.uniform(-1.5, 1.4)); y0 = float(rng.uniform(0.3, 0.8)); ln = float(rng.uniform(0.1, 0.4))
        c.line([(xs, y0, z0), (xs, y0 + float(rng.uniform(-0.03, 0.03)), z0 - ln)], (110, 108, 104, 120), width=0.006)
    # mud splatter low on the body
    for _ in range(110):
        z0 = float(rng.uniform(-1.75, 1.75)); y0 = 0.2 + 0.45 * float(rng.random() ** 2.2)
        r = float(rng.uniform(0.004, 0.018))
        c.disc((xs, y0, z0), r, (112, 90, 64, 110))
    return c.finish(seed, side_hfun(name), 0.30)


def paint_top(seed):
    c = Canvas('top')
    # teal -> magenta racing stripes down the hood and roof
    for x0 in (-0.09, 0.09):
        c.blend_gradient([(x0 - 0.03, 0, 1.78), (x0 + 0.03, 0, 1.78), (x0 + 0.03, 0, 0.62), (x0 - 0.03, 0, 0.62)],
                         (0, 235, 215), (255, 40, 175), [(0, 0, 1.78), (0, 0, 0.62)])
        c.blend_gradient([(x0 - 0.03, 0, -0.12), (x0 + 0.03, 0, -0.12), (x0 + 0.03, 0, -0.56), (x0 - 0.03, 0, -0.56)],
                         (0, 235, 215), (255, 40, 175), [(0, 0, -0.12), (0, 0, -0.56)])
    # hood panel seams and a vent
    c.line([(0.0, 0.0, 1.78), (0.0, 0.0, 0.62)], (130, 136, 146, 200), width=0.006)
    for sx in (-1, 1):
        c.line([(sx * 0.46, 0, 1.55), (sx * 0.58, 0, 1.0), (sx * 0.62, 0, 0.64)], (130, 136, 146, 220), width=0.007)
        for k in range(4):
            c.line([(sx * (0.15 + 0.03 * k), 0, 1.30 - 0.03 * k), (sx * (0.34 + 0.03 * k), 0, 1.20 - 0.03 * k)], (60, 62, 72, 200), width=0.008)
    # windshield (blacked out) with dark frit band at the top edge, wiper blades, and the parking-ticket spot
    c.glass([(-0.64, 0, 0.56), (0.64, 0, 0.56), (0.58, 0, -0.08), (-0.58, 0, -0.08)])
    for sx in (-1, 1):
        c.line([(sx * 0.05, 0, 0.60), (sx * 0.54, 0, 0.50)], (24, 24, 28, 255), width=0.014)
    # roof: panoramic glass behind the LiDAR, rails white
    c.glass([(-0.40, 0, -0.84), (0.40, 0, -0.84), (0.40, 0, -1.30), (-0.40, 0, -1.30)])
    c.line([(0, 0, -0.84), (0, 0, -1.30)], (240, 242, 246, 255), width=0.016)
    # roof spoiler lip at the back and roof rails
    c.poly([(-0.58, 0, -1.46), (0.58, 0, -1.46), (0.52, 0, -1.58), (-0.52, 0, -1.58)], (240, 242, 246, 255), 0.2)
    c.line([(-0.5, 0, -0.1), (-0.5, 0, -1.45)], (210, 214, 222, 255), width=0.01)
    c.line([(0.5, 0, -0.1), (0.5, 0, -1.45)], (210, 214, 222, 255), width=0.01)
    # LiDAR ring decal on the roof: outer magenta, white, teal, magenta (centre z = -0.40)
    ctr = (0, 0, -0.40)
    c.glow(ctr, 0.42, (0, 235, 215), 140)
    for r, col in ((0.345, (255, 28, 172)), (0.315, (250, 250, 252)), (0.285, (0, 236, 214)), (0.245, (250, 250, 252)), (0.215, (255, 28, 172))):
        c.disc(ctr, r, col + (255,), 0.15)
    c.disc(ctr, 0.19, (22, 24, 34, 255), 0.4)
    # hood sticker bomb: smiley and a lightning bolt, sun-bleached
    px, py = c.p(0.28, 0, 0.95)
    smiley(c.d, px, py, 0.075 * S * SS, smile=False)
    bolt = [(-0.32, 0, 1.15), (-0.40, 0, 1.0), (-0.355, 0, 1.0), (-0.42, 0, 0.84), (-0.30, 0, 0.99), (-0.345, 0, 0.99)]
    c.poly(bolt, (255, 214, 24, 255), 0.3)
    # scorched hood: scorch smudges (broken down!)
    c.glow((0.1, 0, 1.55), 0.22, (60, 56, 54), 45)
    c.glow((-0.2, 0, 1.4), 0.15, (60, 56, 54), 40)
    # bird droppings on the roof, because LA
    for (x, z) in ((0.30, -0.1), (-0.2, 0.0), (0.05, -0.72)):
        c.disc((x, 0, z), 0.018, (250, 250, 244, 255), 0.4)
        c.disc((x, 0, z), 0.008, (160, 150, 120, 255), 0.5)
    return c.finish(seed, None, 0.18)


def paint_front(seed):
    c = Canvas('front')
    # lower bumper intake (black mesh) and splitter
    c.poly([(-0.58, 0.20, 1.8), (0.58, 0.20, 1.8), (0.55, 0.34, 1.8), (-0.55, 0.34, 1.8)], (20, 21, 26, 255), 0.6)
    for k in range(8):
        y = 0.215 + 0.016 * k
        c.line([(-0.55, y, 1.8), (0.55, y, 1.8)], (60, 62, 72, 255), width=0.004)
    # headlight pods with a hot cyan DRL strip
    for sx in (-1, 1):
        c.poly([(sx * 0.24, 0.40, 1.8), (sx * 0.68, 0.40, 1.8), (sx * 0.68, 0.485, 1.8), (sx * 0.24, 0.485, 1.8)], (16, 18, 26, 255), 0.08)
        c.glow((sx * 0.46, 0.44, 1.8), 0.22, (0, 235, 255), 130)
        c.poly([(sx * 0.30, 0.425, 1.8), (sx * 0.64, 0.425, 1.8), (sx * 0.64, 0.445, 1.8), (sx * 0.30, 0.445, 1.8)], (170, 255, 255, 255), 0.05)
    # central sensor band and little camera eyes
    c.poly([(-0.20, 0.40, 1.8), (0.20, 0.40, 1.8), (0.20, 0.485, 1.8), (-0.20, 0.485, 1.8)], (12, 14, 22, 255), 0.06)
    for sx in (-1, 1):
        c.disc((sx * 0.10, 0.442, 1.8), 0.022, (0, 255, 170, 255), 0.05)
        c.disc((sx * 0.10, 0.442, 1.8), 0.009, (240, 255, 250, 255), 0.05)
    # blank licence plate (white slab, blue band, dots only), slightly crooked
    c.poly([(-0.17, 0.355, 1.8), (0.17, 0.35, 1.8), (0.17, 0.30, 1.8), (-0.17, 0.305, 1.8)], (240, 240, 232, 255), 0.5)
    c.poly([(-0.17, 0.355, 1.8), (0.17, 0.35, 1.8), (0.17, 0.337, 1.8), (-0.17, 0.343, 1.8)], (40, 90, 200, 255), 0.4)
    # hood leading-edge shadow + corner hazard glow
    for sx in (-1, 1):
        c.glow((sx * 0.62, 0.43, 1.8), 0.14, (255, 160, 0), 200)
    # clear-coat chips along the nose
    rng = np.random.default_rng(seed)
    for _ in range(60):
        x0 = float(rng.uniform(-0.65, 0.65)); y0 = float(rng.uniform(0.28, 0.55))
        c.disc((x0, y0, 1.8), float(rng.uniform(0.003, 0.008)), (60, 60, 66, 170))
    return c.finish(seed, side_hfun('front'), 0.35)


def paint_rear(seed):
    c = Canvas('rear')
    # rear glass (blacked out) with defroster lines
    c.glass([(-0.56, 0.93, -1.8), (0.56, 0.93, -1.8), (0.50, 1.22, -1.8), (-0.50, 1.22, -1.8)])
    for k in range(7):
        y = 0.96 + 0.035 * k
        c.line([(-0.52, y, -1.8), (0.52, y, -1.8)], (70, 40, 20, 120), width=0.003)
    # yellow smiley sticker in the rear window
    px, py = c.p(0.18, 1.06, -1.8)
    smiley(c.d, px, py, 0.095 * S * SS, smile=True)
    # tail-light bar across the full width, glowing red
    c.glow((0, 0.76, -1.8), 0.40, (255, 20, 40), 120)
    c.poly([(-0.66, 0.775, -1.8), (0.66, 0.775, -1.8), (0.66, 0.725, -1.8), (-0.66, 0.725, -1.8)], (255, 36, 52, 255), 0.1)
    c.poly([(-0.60, 0.755, -1.8), (0.60, 0.755, -1.8), (0.60, 0.742, -1.8), (-0.60, 0.742, -1.8)], (255, 200, 190, 255), 0.1)
    # black lower bumper with reflectors, blank plate
    c.poly([(-0.62, 0.30, -1.8), (0.62, 0.30, -1.8), (0.60, 0.42, -1.8), (-0.60, 0.42, -1.8)], (20, 21, 26, 255), 0.6)
    c.poly([(-0.17, 0.62, -1.8), (0.17, 0.625, -1.8), (0.17, 0.52, -1.8), (-0.17, 0.515, -1.8)], (240, 240, 232, 255), 0.5)
    c.poly([(-0.17, 0.62, -1.8), (0.17, 0.625, -1.8), (0.17, 0.60, -1.8), (-0.17, 0.595, -1.8)], (230, 150, 20, 255), 0.4)
    for sx in (-1, 1):
        c.poly([(sx * 0.45, 0.39, -1.8), (sx * 0.58, 0.39, -1.8), (sx * 0.58, 0.33, -1.8), (sx * 0.45, 0.33, -1.8)], (230, 20, 30, 255), 0.2)
        c.glow((sx * 0.64, 0.50, -1.8), 0.14, (255, 160, 0), 200)
    # sensor ring decal, tailgate camera eye and a bumper sticker (shapes only)
    c.disc((-0.30, 0.545, -1.8), 0.05, (255, 28, 172, 255), 0.18)
    c.disc((-0.30, 0.545, -1.8), 0.03, (250, 250, 252, 255), 0.18)
    c.disc((-0.30, 0.545, -1.8), 0.015, (22, 24, 34, 255), 0.1)
    c.poly([(0.30, 0.60, -1.8), (0.50, 0.60, -1.8), (0.50, 0.50, -1.8), (0.30, 0.50, -1.8)], (40, 200, 90, 255), 0.4)
    c.line([(0.32, 0.55, -1.8), (0.48, 0.55, -1.8)], (250, 250, 250, 255), width=0.014)
    return c.finish(seed, side_hfun('rear'), 0.35)


# ----------------------------------------------------------------------------- small parts
def paint_lidar(seed):
    w, h = 176, 128
    rng = np.random.default_rng(seed)
    vv = np.linspace(1, 0, h)[:, None]           # 1 at the tip (image top) -> 0 at the flange
    uu = np.linspace(0, 1, w)[None, :]
    t = np.zeros((h, w, 3), 'float32')
    body = np.array([10, 255, 226], 'float32'); deep = np.array([20, 200, 255], 'float32'); hot = np.array([235, 255, 255], 'float32')
    k = np.clip((vv - 0.2) / 0.55, 0, 1)
    t[:] = body * (1 - k[..., None] * 0.55) + deep * (k[..., None] * 0.55)
    streak = 0.5 + 0.5 * np.sin(uu * 2 * math.pi * 9 + vv * 6.0)
    t *= (0.78 + 0.34 * streak)[..., None]
    for v0 in (0.30, 0.38, 0.46, 0.54, 0.62):
        m = np.exp(-((vv - v0) / 0.012) ** 2)
        t = t * (1 - m[..., None]) + hot * m[..., None]
    tip = np.clip((vv - 0.78) / 0.22, 0, 1)
    t = t * (1 - tip[..., None]) + hot * tip[..., None]
    flange = np.clip((0.10 - vv) / 0.03, 0, 1)
    t = t * (1 - flange[..., None]) + np.array([255, 30, 175], 'float32') * flange[..., None]
    puck = np.clip((vv - 0.09) / 0.01, 0, 1) * np.clip((0.215 - vv) / 0.01, 0, 1)
    t = t * (1 - puck[..., None]) + np.array([22, 24, 30], 'float32') * puck[..., None]
    t += rng.normal(0, 2, (h, w, 1))
    rough = np.full((h, w), 0.12, 'float32')
    rough[vv[:, 0] < 0.215, :] = 0.4
    return Image.fromarray(np.clip(t, 0, 255).astype('uint8')), rough


def paint_cone(seed):
    w, h = 128, 192
    rng = np.random.default_rng(seed)
    hh = 1.0 - np.linspace(0, 1, h)[:, None]     # 0 = base ... 1 = tip
    t = np.zeros((h, w, 3), 'float32'); t[:] = (255, 100, 0)
    t *= (1.05 - 0.10 * hh)[..., None]
    for lo, hi in ((0.60, 0.80), (0.31, 0.46)):
        m = np.clip((hh - lo) / 0.012, 0, 1) * np.clip((hi - hh) / 0.012, 0, 1)
        prism = 1.0 + 0.07 * (np.sin(np.arange(w) * 1.9)[None, :] * np.sin(np.arange(h) * 1.9)[:, None])
        t = t * (1 - m[..., None]) + (np.array([250, 250, 244], 'float32') * prism[..., None]) * m[..., None]
    g = lowfreq(rng, 8, (h, w))
    foot = np.clip(1.0 - hh * 3.4, 0, 1)
    dirt = np.clip(g * 0.6 + foot * 0.9, 0, 1)
    t *= (1.0 - 0.36 * dirt)[..., None]
    img = Image.fromarray(np.clip(t, 0, 255).astype('uint8'))
    d = ImageDraw.Draw(img, 'RGBA')
    for off in (0, 6):
        d.arc([10 + off, 120 + off, 110 + off, 220 + off], 200, 300, fill=(18, 18, 20, 150), width=4)
    d.line([(88, 70), (112, 100)], fill=(24, 22, 20, 120), width=3)
    smiley(d, 42, 66, 11, smile=False)
    arr = np.asarray(img).astype('float32')
    tip = np.clip((hh - 0.93) / 0.02, 0, 1)
    arr = arr * (1 - 0.5 * tip[..., None]) + np.array([70, 28, 0], 'float32') * 0.5 * tip[..., None]
    arr += rng.normal(0, 2.5, (h, w, 1))
    return Image.fromarray(np.clip(arr, 0, 255).astype('uint8')), np.full((h, w), 0.42, 'float32')


def paint_star(seed):
    w = h = 128
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:h, 0:w].astype('float32')
    gold = np.array([255, 205, 30], 'float32'); orange = np.array([255, 140, 0], 'float32')
    k = np.clip((yy + xx) / (w + h), 0, 1)[..., None]
    t = gold * (1 - k) + orange * k
    left = (xx < w * 0.5)[..., None]
    grey = np.array([156, 160, 172], 'float32') * (1.05 - 0.15 * k)
    t = np.where(left, t, grey)                       # a rating of one and a half stars
    hi = np.exp(-(((xx - 46) ** 2 + (yy - 42) ** 2) / 260.0))[..., None]
    t = t + hi * 60
    t += rng.normal(0, 2, (h, w, 1))
    return Image.fromarray(np.clip(t, 0, 255).astype('uint8')), np.full((h, w), 0.25, 'float32')


def paint_tire(seed):
    w, h = 256, 64
    rng = np.random.default_rng(seed)
    uu = np.arange(w)[None, :]; vv = np.linspace(0, 1, h)[:, None]
    t = np.zeros((h, w, 3), 'float32'); t[:] = (30, 30, 33)
    tread = np.clip((vv - 0.30) / 0.05, 0, 1) * np.clip((0.70 - vv) / 0.05, 0, 1)
    blocks = 0.5 + 0.5 * np.sign(np.sin(uu * 2 * math.pi / 8.0 + vv * 4))
    t = t * (1 - tread[..., None] * 0.45 * blocks[..., None])
    for v0 in (0.12, 0.88):
        m = np.exp(-((vv - v0) / 0.018) ** 2)
        t = t + m[..., None] * np.array([60, 60, 66], 'float32')
    side = np.clip((0.22 - vv) / 0.06, 0, 1) + np.clip((vv - 0.78) / 0.06, 0, 1)
    g = lowfreq(rng, 6, (h, w))
    t = t * (1 + 0.5 * g[..., None] * 0.4) + side[..., None] * np.array([16, 16, 18], 'float32')
    t += rng.normal(0, 3, (h, w, 1))
    return Image.fromarray(np.clip(t, 0, 255).astype('uint8')), np.full((h, w), 0.85, 'float32')


def paint_wheelface(seed):
    w = h = 128
    rng = np.random.default_rng(seed)
    img = Image.new('RGB', (w * 2, h * 2), (30, 30, 34))
    d = ImageDraw.Draw(img, 'RGBA')
    c = w
    d.ellipse([c - 124, c - 124, c + 124, c + 124], fill=(34, 34, 38, 255))                 # tyre shoulder
    d.ellipse([c - 106, c - 106, c + 106, c + 106], fill=(196, 200, 208, 255))              # rim lip
    d.ellipse([c - 98, c - 98, c + 98, c + 98], fill=(0, 236, 214, 255))                    # teal accent ring
    d.ellipse([c - 90, c - 90, c + 90, c + 90], fill=(206, 210, 218, 255))
    for k in range(5):                                                                        # five dark scoops between spokes
        a0 = math.radians(72 * k + 12); a1 = math.radians(72 * k + 60)
        pts = [(c + 30 * math.cos(a0), c + 30 * math.sin(a0))]
        for a in np.linspace(a0, a1, 8):
            pts.append((c + 84 * math.cos(a), c + 84 * math.sin(a)))
        pts.append((c + 30 * math.cos(a1), c + 30 * math.sin(a1)))
        d.polygon(pts, fill=(26, 28, 34, 255))
    d.ellipse([c - 34, c - 34, c + 34, c + 34], fill=(255, 28, 172, 255))                    # magenta hub cap
    d.ellipse([c - 22, c - 22, c + 22, c + 22], fill=(250, 250, 252, 255))
    d.ellipse([c - 9, c - 9, c + 9, c + 9], fill=(26, 28, 34, 255))
    out = img.resize((w, h), Image.LANCZOS)
    arr = np.asarray(out).astype('float32') + rng.normal(0, 2, (h, w, 1))
    return Image.fromarray(np.clip(arr, 0, 255).astype('uint8')), np.full((h, w), 0.28, 'float32')


def paint_lens(seed):
    w, h = 128, 64
    rng = np.random.default_rng(seed)
    vv = np.linspace(1, 0, h)[:, None]; uu = np.linspace(0, 1, w)[None, :]
    crown = np.array([255, 246, 190], 'float32'); mid = np.array([255, 180, 0], 'float32'); rim = np.array([255, 120, 0], 'float32')
    k = np.clip((1 - vv) * 1.8, 0, 1)[..., None]
    t = crown * (1 - k) + mid * k
    k2 = np.clip(((1 - vv) - 0.75) * 4, 0, 1)[..., None]
    t = t * (1 - k2) + rim * k2
    t = t * (0.94 + 0.06 * (0.5 + 0.5 * np.cos(uu * 2 * math.pi * 5)))[..., None]
    t += rng.normal(0, 2, (h, w, 1))
    return Image.fromarray(np.clip(t, 0, 255).astype('uint8')), np.full((h, w), 0.1, 'float32')


def paint_balloon(seed):
    w = h = 128
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:h, 0:w].astype('float32')
    t = np.zeros((h, w, 3), 'float32'); t[:] = (238, 28, 44)
    wr = 0.5 + 0.5 * np.sin(xx * 0.9 + np.sin(yy * 0.3) * 2.0)
    t *= (0.80 + 0.30 * wr)[..., None]
    hi = np.exp(-(((xx - 38) ** 2 + (yy - 50) ** 2) / 500.0))[..., None]
    t = t + hi * 70
    t += rng.normal(0, 2, (h, w, 1))
    return Image.fromarray(np.clip(t, 0, 255).astype('uint8')), np.full((h, w), 0.3, 'float32')


def paint_ticket(seed):
    w, h = 128, 64
    rng = np.random.default_rng(seed)
    img = Image.new('RGB', (w, h), (255, 212, 70))
    d = ImageDraw.Draw(img, 'RGBA')
    d.rectangle([0, 0, w, 14], fill=(226, 34, 40, 255))
    d.rectangle([6, 3, 28, 11], fill=(255, 240, 200, 255))
    y = 20
    while y < h - 18:
        ln = int(rng.integers(40, w - 18))
        d.line([(8, y), (8 + ln, y)], fill=(70, 60, 50, 255), width=2)
        y += 6
    for x in range(10, 74, 4):                                                               # barcode
        d.rectangle([x, h - 14, x + int(rng.integers(1, 3)), h - 4], fill=(30, 28, 26, 255))
    d.ellipse([w - 34, h - 24, w - 8, h - 4], outline=(226, 34, 40, 255), width=3)          # rubber stamp
    arr = np.asarray(img).astype('float32') + rng.normal(0, 3, (h, w, 1))
    return Image.fromarray(np.clip(arr, 0, 255).astype('uint8')), np.full((h, w), 0.8, 'float32')


def _tile(name, seed):
    base, rough = PALETTE[name]
    rng = np.random.default_rng(seed)
    t = np.zeros((CELL, CELL, 3), 'float32'); t[:] = base
    t *= np.linspace(1.06, 0.94, CELL)[:, None, None]
    t += rng.normal(0, 3, (CELL, CELL, 1))
    return Image.fromarray(np.clip(t, 0, 255).astype('uint8'))


def paint(out_png):
    atlas = Image.new('RGB', (W, W), (110, 110, 110))
    rough = np.full((W, W), 0.55, 'float32')

    def put(name, img, r):
        x0, y0, w, h = REGION[name]
        atlas.paste(img, (x0, y0))
        rough[y0:y0 + h, x0:x0 + w] = r

    for name, left, seed in (('sideR', False, 11), ('sideL', True, 12)):
        put(name, *paint_side(name, seed, left))
    put('top', *paint_top(13))
    put('front', *paint_front(14))
    put('rear', *paint_rear(15))
    put('lidar', *paint_lidar(16))
    put('cone', *paint_cone(17))
    put('star', *paint_star(18))
    put('tire', *paint_tire(19))
    put('wheelface', *paint_wheelface(20))
    put('lens', *paint_lens(21))
    put('balloon', *paint_balloon(22))
    put('ticket', *paint_ticket(23))
    cells = {}
    for i, name in enumerate(ORDER):
        col, row = i % 32, i // 32
        atlas.paste(_tile(name, 400 + i), (col * CELL, CELL_Y0 + row * CELL))
        rough[CELL_Y0 + row * CELL:CELL_Y0 + (row + 1) * CELL, col * CELL:(col + 1) * CELL] = PALETTE[name][1]
        cells[name] = (col, row)
    atlas.save(out_png)
    return cells, rough


def pm_image(rough):
    """Physical map: R metal (0), G roughness, B 255, A 255 (same channel order as the cart/tent/barricade)."""
    small = np.asarray(Image.fromarray((np.clip(rough, 0, 1) * 255).astype('uint8')).resize((256, 256), Image.BILINEAR)).astype('float32')
    g = 70 + small * (235 - 70) / 255.0
    out = np.zeros((256, 256, 4), 'uint8')
    out[..., 1] = np.clip(g, 0, 255)
    out[..., 2] = 255; out[..., 3] = 255
    return Image.fromarray(out, 'RGBA')


def nm_image():
    out = np.zeros((256, 256, 4), 'uint8')
    out[..., 1] = 128; out[..., 2] = 255; out[..., 3] = 128
    return Image.fromarray(out, 'RGBA')


if __name__ == '__main__':
    import sys
    paint(sys.argv[1])
