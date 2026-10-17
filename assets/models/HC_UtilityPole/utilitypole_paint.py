"""Texture atlas painter for the Sparking Utility Pole (1024x1024), AI-generated procedural art (PIL/numpy).

Layout (pixels, origin top-left):
  (   0,   0)-( 256, 512)  bark      weathered dark-brown pole wood (u around, v top -> base), woodpecker holes, droppings, staples
  ( 256,   0)-( 512, 128)  arm       crossarm wood, grain along u
  ( 512,   0)-( 768, 256)  balloon   shredded gold Mylar smiley with a party hat and confetti (polar map, centre = middle of the face)
  ( 768,   0)-(1024,  64)  spark     spark ribbon: white core, cyan body, gold rim (u along, v across). Painted, NOT emissive.
  ( 256, 128)-( 384, 256)  placard   red HIGH VOLTAGE placard: white border, big bolt, text-stand-in bars (no lettering)
  ( 768, 128)-(1024, 256)  flyers    three stapled flyers, 85 px each: lost cat, free couch, psychic eye
  ( 256, 256)-( 512, 384)  can       grey transformer can (u around, v top -> bottom), hazard sticker, rust, dents
  ( 512, 256)-( 768, 384)  canburnt  the cooked can: soot, scorch fringe, painted flames
  (   0, 960)-(1024,1024)  32 x 2 small 32 px palette cells
paint(out_png) writes the base colour PNG and returns (cells, rough). Lettering is deliberately absent (BG3 mirrors the DAE).
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W = 1024
CELL = 32
CELL_Y0 = 960

# name: (base RGB, grime 0-1, scratch 0-1, rough 0-1)
PALETTE = {
    'copper':       ((226, 112, 40), 0.15, 0.20, 0.30),
    'copper_light': ((255, 170, 90), 0.05, 0.25, 0.25),
    'glass':        ((20, 206, 220), 0.05, 0.10, 0.05),
    'glass_dark':   ((0, 130, 170), 0.10, 0.10, 0.08),
    'porcelain':    ((240, 226, 190), 0.25, 0.10, 0.20),
    'steel':        ((178, 184, 194), 0.30, 0.30, 0.30),
    'steel_dark':   ((86, 94, 106), 0.35, 0.30, 0.40),
    'black':        ((14, 14, 18), 0.0, 0.0, 0.50),
    'wire_black':   ((58, 60, 74), 0.20, 0.10, 0.55),
    'wood_mid':     ((112, 74, 46), 0.45, 0.25, 0.90),
    'wood_dark':    ((72, 46, 30), 0.45, 0.25, 0.90),
    'wood_grey':    ((136, 120, 102), 0.40, 0.25, 0.92),
    'rust':         ((160, 82, 36), 0.55, 0.30, 0.80),
    'dirt':         ((118, 82, 50), 0.40, 0.15, 0.95),
    'gravel':       ((146, 134, 118), 0.35, 0.25, 0.95),
    'asphalt':      ((96, 98, 110), 0.40, 0.30, 0.85),
    'soot':         ((18, 16, 16), 0.0, 0.0, 0.90),
    'gold':         ((255, 204, 20), 0.0, 0.0, 0.10),
    'cyan':         ((0, 226, 255), 0.0, 0.0, 0.10),
    'white':        ((250, 250, 250), 0.0, 0.0, 0.30),
    'red':          ((236, 28, 36), 0.20, 0.10, 0.40),
    'pink':         ((255, 36, 160), 0.10, 0.10, 0.40),
    'shoe_white':   ((246, 244, 238), 0.45, 0.20, 0.60),
    'shoe_pink':    ((255, 52, 170), 0.35, 0.15, 0.55),
    'sole':         ((226, 222, 210), 0.50, 0.20, 0.70),
    'lace':         ((250, 250, 60), 0.10, 0.05, 0.70),
    'mylar_gold':   ((255, 196, 24), 0.0, 0.0, 0.05),
    'mylar_pink':   ((255, 60, 190), 0.0, 0.0, 0.05),
    'ribbon_cyan':  ((0, 206, 255), 0.0, 0.0, 0.20),
    'ribbon_violet': ((150, 60, 255), 0.0, 0.0, 0.20),
    'hazard':       ((255, 214, 0), 0.20, 0.10, 0.40),
    'orange':       ((255, 120, 20), 0.05, 0.05, 0.40),
    'box_grey':     ((120, 126, 136), 0.45, 0.30, 0.50),
}
ORDER = list(PALETTE)
REGION = {
    'bark': (0, 0, 256, 512), 'arm': (256, 0, 256, 128), 'balloon': (512, 0, 256, 256), 'spark': (768, 0, 256, 64),
    'placard': (256, 128, 128, 128), 'flyers': (768, 128, 256, 128),
    'can': (256, 256, 256, 128), 'canburnt': (512, 256, 256, 128),
}
ROUGH = {'bark': 0.92, 'arm': 0.9, 'balloon': 0.06, 'spark': 0.2, 'placard': 0.35, 'flyers': 0.8,
         'can': 0.45, 'canburnt': 0.75}


def _lowfreq(rng, n, size):
    a = rng.random((n, n)).astype('float32')
    im = Image.fromarray((a * 255).astype('uint8')).resize((size[1], size[0]), Image.BICUBIC)
    return np.asarray(im).astype('float32') / 255.0


def _fbm(rng, size, base=3, octaves=4):
    out = np.zeros(size, 'float32'); amp = 1.0; tot = 0.0
    for k in range(octaves):
        out += amp * _lowfreq(rng, base * 2 ** k, size); tot += amp; amp *= 0.55
    return out / tot


def _streak(rng, h, w, nx, ny):
    """Anisotropic noise: nx columns, ny rows (nx >> ny gives long vertical streaks)."""
    a = rng.random((ny, nx)).astype('float32')
    im = Image.fromarray((a * 255).astype('uint8')).resize((w, h), Image.BICUBIC)
    return np.asarray(im).astype('float32') / 255.0


def _smooth(x, a, b):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def _bark():
    w, h = 256, 512
    rng = np.random.default_rng(31)
    v = np.linspace(0, 1, h)[:, None] * np.ones((1, w))          # 0 = top of the pole, 1 = base
    t = np.zeros((h, w, 3), 'float32'); t[:] = (82, 52, 32)
    st = 0.55 * _streak(rng, h, w, 48, 7) + 0.30 * _streak(rng, h, w, 18, 3) + 0.15 * _fbm(rng, (h, w), 3, 4)
    t *= (0.62 + 0.75 * st)[..., None]
    # sun-bleached grey cap at the top, creosote-black lower half, wet wick at the very base
    grey = _smooth(1 - v, 0.74, 1.0) * (0.55 + 0.45 * _streak(rng, h, w, 30, 5))
    t = t * (1 - 0.65 * grey[..., None]) + np.array([150, 136, 118], 'float32') * 0.65 * grey[..., None]
    low = _smooth(v, 0.42, 0.95)
    t *= (1 - 0.45 * low)[..., None]
    t = t + np.array([0, 0, 0], 'float32')
    img = Image.fromarray(np.clip(t, 0, 255).astype('uint8'))
    layer = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for _ in range(46):                                          # long checking cracks
        x = int(rng.integers(0, w)); y = int(rng.integers(0, h - 80)); ln = int(rng.integers(40, 200))
        pts = []
        for k in range(8):
            pts.append((x + int(rng.integers(-2, 3)), y + ln * k // 7)); x += int(rng.integers(-3, 4))
        d.line(pts, fill=(14, 8, 4, 235), width=int(rng.integers(2, 5)), joint='curve')
        d.line([(px + 3, py) for px, py in pts], fill=(176, 140, 104, 90), width=1)
    for _ in range(5):                                           # woodpecker holes with a shadow
        cx, cy = int(rng.integers(20, w - 20)), int(rng.integers(40, h - 40))
        d.ellipse([cx - 9, cy - 12, cx + 9, cy + 12], fill=(12, 6, 2, 255), outline=(150, 112, 80, 200))
        d.ellipse([cx - 5, cy - 4, cx + 6, cy + 9], fill=(0, 0, 0, 255))
    for _ in range(260):                                         # rusty staples and nails from decades of flyers
        cx, cy = int(rng.integers(0, w)), int(rng.integers(0, h))
        d.rectangle([cx, cy, cx + int(rng.integers(2, 5)), cy + 1], fill=(190, 194, 200, 255))
    for _ in range(40):                                          # torn flyer scraps
        cx, cy = int(rng.integers(0, w - 14)), int(rng.integers(0, h - 14))
        col = ((250, 250, 244), (255, 244, 70), (255, 120, 190))[int(rng.integers(0, 3))]
        d.rectangle([cx, cy, cx + int(rng.integers(3, 12)), cy + int(rng.integers(3, 14))], fill=col + (255,))
    for _ in range(14):                                          # bird droppings on the upper third
        cx, cy = int(rng.integers(0, w)), int(rng.integers(0, h // 3)); r = int(rng.integers(3, 8))
        d.ellipse([cx - r, cy - r, cx + r, cy + r * 3], fill=(250, 250, 250, 255))
        d.ellipse([cx - r // 2, cy - r // 2, cx + r // 2, cy + r], fill=(130, 126, 90, 255))
    layer = layer.filter(ImageFilter.GaussianBlur(0.6))
    return Image.alpha_composite(img.convert('RGBA'), layer).convert('RGB')


def _arm():
    w, h = 256, 128
    rng = np.random.default_rng(32)
    t = np.zeros((h, w, 3), 'float32'); t[:] = (122, 90, 62)
    st = 0.6 * _streak(rng, h, w, 6, 24) + 0.4 * _fbm(rng, (h, w), 3, 4)
    t *= (0.65 + 0.7 * st)[..., None]
    grey = _smooth(_fbm(rng, (h, w), 4, 3), 0.45, 0.8)
    t = t * (1 - 0.5 * grey[..., None]) + np.array([150, 140, 126], 'float32') * 0.5 * grey[..., None]
    img = Image.fromarray(np.clip(t, 0, 255).astype('uint8'))
    d = ImageDraw.Draw(img, 'RGBA')
    for _ in range(14):
        x = int(rng.integers(0, w - 60)); y = int(rng.integers(4, h - 4)); ln = int(rng.integers(30, 120))
        d.line([(x, y), (x + ln, y + int(rng.integers(-2, 3)))], fill=(18, 10, 6, 220), width=int(rng.integers(1, 3)))
    for bx in (36, 128, 220):                                    # bolt heads with rust streaks
        d.ellipse([bx - 7, 60, bx + 7, 74], fill=(170, 176, 186, 255), outline=(70, 70, 76, 255))
        d.line([(bx, 74), (bx + 2, 120)], fill=(160, 80, 36, 170), width=4)
    return img


def _balloon():
    """Polar-mapped smiley foil balloon: the geometry maps (cos, sin) of the disc into this square."""
    w = h = 256
    rng = np.random.default_rng(33)
    yy, xx = np.mgrid[0:h, 0:w].astype('float32')
    rr = np.hypot(xx - 128, yy - 128) / 128.0
    t = np.zeros((h, w, 3), 'float32')
    gold = np.array([255, 198, 20], 'float32'); pink = np.array([255, 56, 186], 'float32')
    mix = _smooth(rr, 0.78, 0.9)[..., None]
    t[:] = gold * (1 - mix) + pink * mix                        # gold face, magenta border
    t *= (0.9 + 0.2 * np.sin((xx + yy) * 0.35))[..., None]      # foil crinkle
    t *= (0.88 + 0.16 * _fbm(rng, (h, w), 5, 3))[..., None]
    img = Image.fromarray(np.clip(t, 0, 255).astype('uint8'))
    d = ImageDraw.Draw(img, 'RGBA')
    for _ in range(46):                                          # confetti dots and slivers
        cx, cy = int(rng.integers(30, w - 30)), int(rng.integers(30, h - 30))
        if math.hypot(cx - 128, cy - 128) > 108:
            continue
        col = ((255, 255, 255), (30, 200, 255), (160, 70, 255), (255, 40, 40))[int(rng.integers(0, 4))]
        d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=col + (255,))
    d.ellipse([84, 84, 108, 120], fill=(40, 20, 20, 255))        # eyes
    d.ellipse([148, 84, 172, 120], fill=(40, 20, 20, 255))
    d.arc([68, 96, 188, 196], 15, 165, fill=(40, 20, 20, 255), width=9)   # smile
    d.polygon([(128, 8), (176, 70), (80, 70)], fill=(30, 200, 255, 255), outline=(255, 255, 255, 255))   # party hat
    for k in range(4):
        d.line([(100 + k * 4, 60 - k * 12), (156 - k * 4, 60 - k * 12)], fill=(255, 255, 255, 255), width=3)
    d.ellipse([118, 0, 138, 14], fill=(255, 40, 40, 255))        # pompom
    d.arc([6, 6, 250, 250], 205, 250, fill=(255, 255, 255, 190), width=8)   # foil sheen
    return img


def _spark():
    w, h = 256, 64
    rng = np.random.default_rng(34)
    u = np.linspace(0, 1, w)[None, :] * np.ones((h, 1))
    v = np.abs(np.linspace(-1, 1, h))[:, None] * np.ones((1, w))
    flick = 0.08 * np.sin(u * 2 * np.pi * 7)
    d = v + flick
    t = np.zeros((h, w, 3), 'float32')
    white = np.array([255, 255, 255], 'float32'); cyan = np.array([0, 226, 255], 'float32'); gold = np.array([255, 196, 0], 'float32')
    k1 = _smooth(d, 0.06, 0.20)[..., None]
    k2 = _smooth(d, 0.50, 0.66)[..., None]
    t[:] = white * (1 - k1) + cyan * k1
    t = t * (1 - k2) + gold * k2
    return Image.fromarray(np.clip(t, 0, 255).astype('uint8'))


def _bolt(d, cx, cy, s, fill, outline=None):
    pts = [(cx + 0.10 * s, cy - 0.50 * s), (cx - 0.34 * s, cy + 0.06 * s), (cx - 0.04 * s, cy + 0.06 * s),
           (cx - 0.14 * s, cy + 0.52 * s), (cx + 0.34 * s, cy - 0.10 * s), (cx + 0.04 * s, cy - 0.10 * s)]
    d.polygon(pts, fill=fill, outline=outline)


def _placard():
    w = h = 128
    rng = np.random.default_rng(36)
    t = np.zeros((h, w, 3), 'float32'); t[:] = (226, 24, 32)
    t *= (0.92 + 0.14 * _fbm(rng, (h, w), 4, 3))[..., None]
    img = Image.fromarray(np.clip(t, 0, 255).astype('uint8'))
    d = ImageDraw.Draw(img, 'RGBA')
    d.rectangle([4, 4, w - 5, h - 5], outline=(255, 255, 255, 255), width=5)
    d.rectangle([14, 14, w - 15, 74], fill=(255, 255, 255, 255))
    _bolt(d, 64, 44, 66, (230, 24, 32, 255), (20, 10, 10, 255))                 # red bolt on the white panel
    for k, ln in enumerate((78, 92, 60)):                                      # stand-ins for the lettering lines
        y = 84 + k * 13
        d.rectangle([64 - ln // 2, y, 64 + ln // 2, y + 7], fill=(255, 255, 255, 255))
    for nx, ny in ((10, 10), (w - 11, 10), (10, h - 11), (w - 11, h - 11)):
        d.ellipse([nx - 3, ny - 3, nx + 3, ny + 3], fill=(176, 180, 186, 255), outline=(60, 60, 66, 255))
    for _ in range(40):                                                         # chipped paint, rust bloom
        x, y = int(rng.integers(0, w)), int(rng.integers(0, h)); r = int(rng.integers(1, 4))
        d.ellipse([x - r, y - r, x + r, y + r], fill=(120, 50, 24, 170))
    return img


def _flyers():
    w, h = 256, 128
    rng = np.random.default_rng(37)
    img = Image.new('RGB', (w, h), (90, 90, 90))
    d = ImageDraw.Draw(img, 'RGBA')
    # 1. neon yellow LOST CAT: head silhouette with ears, big eyes, text bars, torn-off tabs
    x0 = 0; fw = 85
    d.rectangle([x0, 0, x0 + fw - 1, h - 1], fill=(255, 244, 60, 255))
    d.polygon([(x0 + 18, 50), (x0 + 22, 18), (x0 + 36, 34), (x0 + 50, 34), (x0 + 64, 18), (x0 + 68, 50), (x0 + 60, 66), (x0 + 26, 66)],
              fill=(20, 18, 22, 255))
    d.ellipse([x0 + 28, 42, x0 + 38, 54], fill=(255, 255, 80, 255)); d.ellipse([x0 + 48, 42, x0 + 58, 54], fill=(255, 255, 80, 255))
    for k in range(3):
        d.rectangle([x0 + 10, 74 + k * 7, x0 + fw - 12 - (k % 2) * 14, 77 + k * 7], fill=(20, 18, 22, 255))
    for k in range(7):
        if k not in (1, 4):
            d.rectangle([x0 + 3 + k * 11, 100, x0 + 11 + k * 11, 127], fill=(255, 236, 40, 255), outline=(20, 18, 22, 255))
    # 2. hot pink FREE COUCH: couch silhouette
    x0 = 85
    d.rectangle([x0, 0, x0 + fw - 1, h - 1], fill=(255, 52, 170, 255))
    d.rectangle([x0 + 14, 30, x0 + 70, 52], fill=(255, 255, 255, 255))
    d.rectangle([x0 + 8, 48, x0 + 76, 72], fill=(255, 255, 255, 255))
    d.rectangle([x0 + 8, 40, x0 + 18, 76], fill=(255, 255, 255, 255)); d.rectangle([x0 + 66, 40, x0 + 76, 76], fill=(255, 255, 255, 255))
    d.rectangle([x0 + 12, 72, x0 + 18, 82], fill=(255, 255, 255, 255)); d.rectangle([x0 + 66, 72, x0 + 72, 82], fill=(255, 255, 255, 255))
    d.line([(x0 + 14, 62), (x0 + 70, 62)], fill=(255, 52, 170, 255), width=2)
    d.ellipse([x0 + 30, 53, x0 + 42, 62], fill=(120, 70, 30, 255))            # a suspicious stain
    for k in range(2):
        d.rectangle([x0 + 10, 90 + k * 8, x0 + fw - 12, 93 + k * 8], fill=(255, 255, 255, 255))
    for k in range(7):
        if k not in (0, 5):
            d.rectangle([x0 + 3 + k * 11, 108, x0 + 11 + k * 11, 127], fill=(255, 52, 170, 255), outline=(255, 255, 255, 255))
    # 3. violet psychic flyer: eye in a hand
    x0 = 170
    d.rectangle([x0, 0, x0 + fw - 1, h - 1], fill=(250, 250, 250, 255))
    d.ellipse([x0 + 10, 26, x0 + 75, 78], fill=(120, 40, 230, 255))
    d.ellipse([x0 + 22, 38, x0 + 62, 66], fill=(255, 255, 255, 255)); d.ellipse([x0 + 34, 40, x0 + 50, 64], fill=(30, 200, 255, 255))
    d.ellipse([x0 + 38, 46, x0 + 46, 58], fill=(10, 10, 20, 255))
    for k in range(5):
        a = math.radians(200 + k * 35)
        d.line([(x0 + 42, 52), (x0 + 42 + 44 * math.cos(a), 52 + 44 * math.sin(a))], fill=(255, 190, 0, 255), width=3)
    for k in range(3):
        d.rectangle([x0 + 10, 86 + k * 7, x0 + fw - 12 - (k % 2) * 10, 89 + k * 7], fill=(120, 40, 230, 255))
    for k in range(7):
        if k not in (2,):
            d.rectangle([x0 + 3 + k * 11, 108, x0 + 11 + k * 11, 127], fill=(250, 250, 250, 255), outline=(120, 40, 230, 255))
    arr = np.asarray(img).astype('float32')
    arr *= (0.9 + 0.2 * _fbm(rng, (h, w), 5, 3))[..., None]
    return Image.fromarray(np.clip(arr, 0, 255).astype('uint8'))


def _can_base(seed, soot):
    w, h = 256, 128
    rng = np.random.default_rng(seed)
    v = np.linspace(0, 1, h)[:, None] * np.ones((1, w))
    u = np.linspace(0, 1, w)[None, :] * np.ones((h, 1))
    t = np.zeros((h, w, 3), 'float32'); t[:] = (166, 176, 190)
    t *= (0.9 + 0.14 * np.cos(u * 2 * np.pi * 2))[..., None]                   # soft shading round the can
    t *= (0.84 + 0.3 * _fbm(rng, (h, w), 4, 4))[..., None]
    for yb in (0.10, 0.90):                                                    # weld bands
        t *= np.where(np.abs(v - yb) < 0.025, 0.62, 1.0)[..., None]
    rust = _smooth(_streak(rng, h, w, 40, 4) * (1 - v) + 0.2 * _fbm(rng, (h, w), 5, 3), 0.55, 0.85)
    t = t * (1 - 0.7 * rust[..., None]) + np.array([170, 84, 34], 'float32') * 0.7 * rust[..., None]
    if soot:
        s = np.clip(_smooth(1 - v, 0.15, 0.6) * (0.55 + 0.45 * _fbm(rng, (h, w), 4, 3)), 0, 1)
        t = t * (1 - 0.92 * s[..., None]) + np.array([16, 14, 14], 'float32') * 0.92 * s[..., None]
        fringe = _smooth(v, 0.35, 0.6) * (1 - _smooth(v, 0.6, 0.85)) * s
        t = t * (1 - 0.5 * fringe[..., None]) + np.array([176, 96, 30], 'float32') * 0.5 * fringe[..., None]
    return Image.fromarray(np.clip(t, 0, 255).astype('uint8')), rng


def _can():
    img, rng = _can_base(38, False)
    d = ImageDraw.Draw(img, 'RGBA')
    cx = 128                                                                    # front of the can is u = 0.5
    d.polygon([(cx, 26), (cx + 26, 78), (cx - 26, 78)], fill=(255, 214, 0, 255), outline=(20, 20, 20, 255))
    _bolt(d, cx, 56, 30, (20, 20, 22, 255))
    d.rectangle([cx - 22, 88, cx + 22, 108], fill=(238, 232, 212, 255), outline=(60, 60, 60, 255))   # data plate
    for k in range(3):
        d.line([(cx - 17, 93 + k * 5), (cx + 17 - k * 6, 93 + k * 5)], fill=(60, 60, 60, 255), width=1)
    for k in range(3):
        x = 30 + k * 30
        d.ellipse([x, 44, x + 10, 54], fill=(120, 126, 136, 255))             # dents
        d.arc([x, 44, x + 10, 54], 200, 340, fill=(240, 244, 250, 200), width=2)
    return img


def _can_burnt():
    img, rng = _can_base(39, True)
    d = ImageDraw.Draw(img, 'RGBA')
    cx = 128
    # painted flames licking up the front: three tongues, orange outside, yellow core
    for dx, hh, wd in ((-26, 74, 20), (0, 96, 26), (26, 66, 18)):
        d.polygon([(cx + dx - wd, 116), (cx + dx - wd // 2, 116 - hh * 0.55), (cx + dx - wd // 3, 116 - hh * 0.7),
                   (cx + dx, 116 - hh), (cx + dx + wd // 3, 116 - hh * 0.62), (cx + dx + wd // 2, 116 - hh * 0.5),
                   (cx + dx + wd, 116)], fill=(255, 110, 10, 255))
        d.polygon([(cx + dx - wd // 2, 116), (cx + dx, 116 - hh * 0.55), (cx + dx + wd // 2, 116)], fill=(255, 226, 40, 255))
    return img


def _tile(name, seed):
    base, grime, scratch, _ = PALETTE[name]
    rng = np.random.default_rng(seed)
    t = np.zeros((CELL, CELL, 3), 'float32'); t[:] = base
    t *= np.linspace(1.08, 0.92, CELL)[:, None, None]
    g = _lowfreq(rng, 5, (CELL, CELL))
    t *= (1.0 - grime * 0.5 * g)[..., None]
    t += rng.normal(0, 3, (CELL, CELL, 1))
    img = Image.fromarray(np.clip(t, 0, 255).astype('uint8'))
    d = ImageDraw.Draw(img)
    for _ in range(int(8 * scratch) + (1 if scratch > 0 else 0)):
        y = int(rng.integers(0, CELL)); x0 = int(rng.integers(0, CELL)); ln = int(rng.integers(6, 24))
        d.line([(x0, y), (x0 + ln, y)], fill=(235,) * 3 if rng.random() < 0.5 else (22,) * 3, width=1)
    return img


def paint(out_png):
    atlas = Image.new('RGB', (W, W), (110, 110, 110))
    rough = np.full((W, W), 0.55, 'float32')
    makers = {'bark': _bark, 'arm': _arm, 'balloon': _balloon, 'spark': _spark, 'placard': _placard,
              'flyers': _flyers, 'can': _can, 'canburnt': _can_burnt}
    for name, fn in makers.items():
        x0, y0, w, h = REGION[name]
        img = fn()
        assert img.size == (w, h), (name, img.size, (w, h))
        atlas.paste(img, (x0, y0)); rough[y0:y0 + h, x0:x0 + w] = ROUGH[name]
    cells = {}
    for i, name in enumerate(ORDER):
        col, row = i % 32, i // 32
        atlas.paste(_tile(name, 500 + i), (col * CELL, CELL_Y0 + row * CELL))
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
    inset = 2.0
    span = CELL - 2 * inset
    return uv_px(col * CELL + inset + f * span, CELL_Y0 + row * CELL + inset + g * span)


def ruv(name, a, b):
    """UV inside a region. a = 0..1 along the region's u (left -> right), b = 0..1 along v (top -> bottom)."""
    x0, y0, w, h = REGION[name]
    a = min(max(a, 0.0), 1.0); b = min(max(b, 0.0), 1.0)
    return uv_px(x0 + 1.0 + a * (w - 2.0), y0 + 1.0 + b * (h - 2.0))
