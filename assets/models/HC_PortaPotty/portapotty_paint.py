"""Texture atlas painter for the Tipped-Over Festival Porta-Potty (1024x1024), AI-generated procedural art (PIL/numpy).

Layout (pixels, origin top-left):
  (   0,   0)-( 512, 256)  wall      turquoise ribbed plastic, planar over the 2.36 x 1.2 m cabin side (ground, back, floor end)
  ( 512,   0)-(1024, 256)  top       same plastic with a smiley sticker, a bumper sticker and scuffs (the upper cabin wall)
  (   0, 256)-( 512, 512)  front     same plastic, door-frame wall
  ( 512, 256)-( 768, 384)  inner     dark teal cabin interior
  ( 768, 256)-(1024, 372)  door_out  door leaf, outside (louvers, slider lock, pictogram, boot dent)
  ( 768, 372)-(1024, 488)  door_in   door leaf, inside
  ( 512, 384)-( 640, 512)  roof      white roof / vent hood plastic
  ( 640, 384)-( 768, 512)  sign      wooden plank with a red crossed circle (shapes only)
  (   0, 512)-( 256, 768)  puddle    polar map: u = angle, v = centre -> rim (neon blue / acid green, foam rim)
  ( 256, 512)-( 768, 576)  tp        toilet-paper ribbon, 4 m x 12 cm (u along the ribbon), tail soaked in neon
  ( 256, 576)-( 512, 640)  tproll    paper wound on a roll (u around, v along the axis)
  ( 256, 640)-( 512, 704)  stink     green stink-line ribbon
  ( 512, 576)-( 640, 704)  bubble    toxic bubble (u around, v top -> bottom)
  ( 640, 576)-( 768, 640)  label     hand-sanitizer bottle label
  ( 768, 576)-(1024, 608)  tape      yellow-and-black diagonal caution tape (no lettering)
  (   0, 960)-(1024,1024)  32 x 2 small 32 px palette cells
paint(out_png) writes the base colour PNG and returns (cells, rough). Lettering is deliberately absent (BG3 mirrors the DAE).
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W = 1024
CELL = 32
CELL_Y0 = 960

TURQ = np.array([0, 212, 206], 'float32')
ACID = np.array([160, 255, 10], 'float32')
NEON_BLUE = np.array([0, 128, 255], 'float32')

# name: (base RGB, grime 0-1, scratch 0-1, rough 0-1)
PALETTE = {
    'turq':         ((0, 206, 202), 0.30, 0.20, 0.35),
    'turq_dark':    ((0, 142, 152), 0.40, 0.25, 0.40),
    'turq_light':   ((96, 240, 232), 0.25, 0.15, 0.30),
    'white_pipe':   ((236, 240, 244), 0.35, 0.20, 0.35),
    'pipe_grey':    ((150, 158, 166), 0.40, 0.30, 0.45),
    'seat_white':   ((244, 244, 238), 0.45, 0.25, 0.30),
    'seat_dark':    ((24, 40, 48), 0.30, 0.10, 0.30),
    'bowl_blue':    ((20, 150, 255), 0.0, 0.0, 0.05),
    'hinge_steel':  ((176, 180, 188), 0.45, 0.40, 0.30),
    'handle_black': ((26, 26, 30), 0.20, 0.10, 0.50),
    'rubber':       ((34, 33, 35), 0.35, 0.10, 0.85),
    'sani_bottle':  ((20, 190, 255), 0.05, 0.10, 0.20),
    'sani_cap':     ((255, 52, 168), 0.10, 0.10, 0.35),
    'sani_gel':     ((170, 255, 30), 0.0, 0.0, 0.05),
    'wood':         ((180, 128, 76), 0.40, 0.25, 0.90),
    'wood_dark':    ((112, 72, 40), 0.45, 0.25, 0.90),
    'nail':         ((170, 172, 176), 0.40, 0.30, 0.40),
    'tp_core':      ((196, 150, 98), 0.40, 0.10, 0.90),
    'tp_white':     ((250, 250, 244), 0.35, 0.05, 0.90),
    'red':          ((236, 28, 36), 0.30, 0.10, 0.40),
    'cup_white':    ((248, 246, 240), 0.30, 0.10, 0.40),
    'black':        ((14, 14, 16), 0.0, 0.0, 0.50),
    'band_pink':    ((255, 40, 190), 0.10, 0.10, 0.50),
    'rust':         ((150, 80, 40), 0.55, 0.30, 0.80),
    'toxic_green':  ((170, 255, 20), 0.0, 0.0, 0.10),
    'toxic_blue':   ((0, 150, 255), 0.0, 0.0, 0.10),
    'gum_yellow':   ((252, 214, 20), 0.20, 0.10, 0.40),
}
ORDER = list(PALETTE)
REGION = {
    'wall': (0, 0, 512, 256), 'top': (512, 0, 512, 256), 'front': (0, 256, 512, 256),
    'inner': (512, 256, 256, 128), 'door_out': (768, 256, 256, 116), 'door_in': (768, 372, 256, 116),
    'roof': (512, 384, 128, 128), 'sign': (640, 384, 128, 128),
    'puddle': (0, 512, 256, 256), 'tp': (256, 512, 512, 64), 'tproll': (256, 576, 256, 64),
    'stink': (256, 640, 256, 64), 'bubble': (512, 576, 128, 128), 'label': (640, 576, 128, 64), 'tape': (768, 576, 256, 32),
}
ROUGH = {'wall': 0.32, 'top': 0.32, 'front': 0.32, 'inner': 0.5, 'door_out': 0.3, 'door_in': 0.45, 'roof': 0.4,
         'sign': 0.9, 'puddle': 0.04, 'tp': 0.88, 'tproll': 0.88, 'stink': 0.6, 'bubble': 0.04, 'label': 0.3, 'tape': 0.7}
# world extents (metres) the wall-type regions cover: 2.36 m (x) x 1.2 m (y) / 1.24 m (z)
CABIN_W, CABIN_H = 2.36, 1.2
TP_LEN, TP_WID = 4.0, 0.12


def _lowfreq(rng, n, size):
    a = rng.random((n, n)).astype('float32')
    im = Image.fromarray((a * 255).astype('uint8')).resize((size[1], size[0]), Image.BICUBIC)
    return np.asarray(im).astype('float32') / 255.0


def _fbm(rng, size, base=3, octaves=4):
    out = np.zeros(size, 'float32'); amp = 1.0; tot = 0.0
    for k in range(octaves):
        out += amp * _lowfreq(rng, base * 2 ** k, size); tot += amp; amp *= 0.55
    return out / tot


def _smooth(x, a, b):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def _smiley(img, cx, cy, r, face=(30, 30, 30, 255), bg=(255, 224, 0, 255), flat=False):
    d = ImageDraw.Draw(img, 'RGBA')
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=bg, outline=(40, 40, 30, 255), width=max(1, r // 12))
    e = max(1, r // 4)
    d.ellipse([cx - r // 2 - e // 2, cy - r // 3 - e, cx - r // 2 + e // 2 + 1, cy - r // 3 + e], fill=face)
    d.ellipse([cx + r // 2 - e // 2, cy - r // 3 - e, cx + r // 2 + e // 2 + 1, cy - r // 3 + e], fill=face)
    if flat:
        d.line([(cx - r // 2, cy + r // 2), (cx + r // 2, cy + r // 2)], fill=face, width=max(1, r // 6))
    else:
        d.arc([cx - r // 2, cy - r // 6, cx + r // 2, cy + r // 2 + 2], 15, 165, fill=face, width=max(2, r // 7))


def _scribble(d, rng, x0, y0, w, h, color, width=2, strokes=5):
    for _ in range(strokes):
        pts = []
        x, y = x0 + rng.random() * w * 0.2, y0 + rng.random() * h
        for _ in range(7):
            pts.append((x, y))
            x += rng.uniform(w * 0.06, w * 0.2)
            y = y0 + rng.random() * h
        d.line(pts, fill=color, width=width, joint='curve')


def _plastic(seed, w, h, mx, my, rib=0.14, vertical_ribs=False):
    """Turquoise moulded plastic: ribs, panel seams, sun fade, road grime from the bottom and a toxic-green splash."""
    rng = np.random.default_rng(seed)
    jj = (np.arange(h)[:, None] * my) * np.ones((1, w))
    ii = (np.arange(w)[None, :] * mx) * np.ones((h, 1))
    v = np.linspace(0, 1, h)[:, None] * np.ones((1, w))
    t = np.zeros((h, w, 3), 'float32'); t[:] = TURQ
    ph = ((ii if vertical_ribs else jj) / rib) % 1.0
    shade = 0.92 + 0.12 * (0.5 + 0.5 * np.cos(2 * np.pi * ph))
    shade = np.where((ph < 0.05) | (ph > 0.95), 0.70, shade)
    t *= shade[..., None]
    for xs in (0.58, 1.18, 1.78):                               # moulded vertical panel seams
        t *= np.where(np.abs(ii - xs) < 0.007, 0.62, 1.0)[..., None]
    g = _fbm(rng, (h, w), 3, 4)
    t *= (0.88 + 0.26 * g)[..., None]
    t *= (1.07 - 0.18 * v)[..., None]
    dirt = np.clip(_fbm(rng, (h, w), 4, 4) * (0.10 + 1.25 * v ** 2.4), 0, 1)
    t = t * (1 - 0.55 * dirt[..., None]) + np.array([76, 56, 22], 'float32') * 0.32 * dirt[..., None]
    sp = _smooth(v + 0.18 * (_fbm(rng, (h, w), 5, 3) - 0.5), 0.80, 0.97) * (_fbm(rng, (h, w), 6, 3) > 0.40)
    t = t * (1 - 0.82 * sp[..., None]) + ACID * 0.82 * sp[..., None]
    img = Image.fromarray(np.clip(t, 0, 255).astype('uint8'))
    layer = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for _ in range(int(w * h / 3400)):                              # mud splatter low on the wall
        x = int(rng.integers(0, w)); y = int(h * (1 - rng.random() ** 2.2)); r = int(rng.integers(1, 5))
        d.ellipse([x - r, y - r // 2, x + r, y + r // 2], fill=(86, 62, 30, 150))
    for _ in range(int(w / 28)):                                    # long scuffs
        x0 = int(rng.integers(0, w - 40)); y0 = int(rng.integers(6, h - 6)); ln = int(rng.integers(16, 80))
        d.line([(x0, y0), (x0 + ln, y0 + int(rng.integers(-3, 4)))],
               fill=(18, 40, 44, 110) if rng.random() < 0.5 else (214, 255, 250, 120), width=int(rng.integers(1, 3)))
    for _ in range(int(w / 70)):                                    # vertical drip stains
        x = int(rng.integers(8, w - 8)); y0 = int(rng.integers(0, h // 2)); ln = int(rng.integers(20, h // 2))
        d.line([(x, y0), (x + int(rng.integers(-2, 3)), y0 + ln)], fill=(150, 130, 40, 70), width=int(rng.integers(2, 5)))
    for _ in range(max(2, w // 130)):                               # dents: a dark crescent and a bright one
        cx, cy, r = int(rng.integers(30, w - 30)), int(rng.integers(30, h - 30)), int(rng.integers(10, 22))
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(0, 60, 66, 50))
        d.ellipse([cx - r + 4, cy - r + 3, cx + r - 2, cy + r - 3], fill=(150, 255, 245, 35))
    layer = layer.filter(ImageFilter.GaussianBlur(0.7))
    return Image.alpha_composite(img.convert('RGBA'), layer).convert('RGB'), rng


def _wall():
    img, rng = _plastic(11, 512, 256, CABIN_W / 512, CABIN_H / 256)
    d = ImageDraw.Draw(img, 'RGBA')
    _scribble(d, rng, 90, 70, 110, 60, (12, 12, 18, 220), width=3, strokes=4)       # marker tag
    d.ellipse([160, 60, 182, 82], outline=(12, 12, 18, 220), width=2)
    for k in range(5):                                                               # tally marks
        d.line([(330 + k * 9, 90), (330 + k * 9, 118)], fill=(230, 30, 140, 230), width=3)
    d.line([(326, 112), (378, 94)], fill=(230, 30, 140, 230), width=3)
    return img


def _top():
    img, rng = _plastic(12, 512, 256, CABIN_W / 512, CABIN_H / 256)
    d = ImageDraw.Draw(img, 'RGBA')
    _smiley(img, 146, 118, 50, flat=False)                                           # the smiley sticker
    d.arc([96, 68, 196, 168], 200, 330, fill=(255, 255, 255, 140), width=3)
    d.rectangle([300, 80, 440, 128], fill=(40, 70, 220, 255), outline=(250, 250, 250, 255), width=3)   # bumper sticker
    for k, col in enumerate(((255, 40, 40), (255, 200, 0), (30, 220, 80), (255, 255, 255))):
        d.rectangle([306 + k * 33, 90, 336 + k * 33, 118], fill=col + (255,))
    d.ellipse([360, 96, 386, 122], fill=(255, 60, 150, 255))
    _scribble(d, rng, 250, 160, 200, 60, (12, 12, 18, 200), width=3, strokes=3)
    return img


def _front():
    img, rng = _plastic(13, 512, 256, CABIN_W / 512, CABIN_H / 256)
    d = ImageDraw.Draw(img, 'RGBA')
    for x, y, col in ((110, 30, (255, 60, 160)), (210, 44, (255, 226, 0)), (440, 36, (120, 60, 220))):
        d.polygon([(x + (13 if k % 2 == 0 else 5) * math.cos(math.pi / 2 + k * math.pi / 5), y - (13 if k % 2 == 0 else 5) * math.sin(math.pi / 2 + k * math.pi / 5)) for k in range(10)], fill=col + (255,))
    return img


def _inner():
    w, h = 256, 128
    rng = np.random.default_rng(14)
    v = np.linspace(0, 1, h)[:, None] * np.ones((1, w))
    t = np.zeros((h, w, 3), 'float32'); t[:] = (6, 112, 122)
    g = _fbm(rng, (h, w), 3, 4)
    t *= (0.7 + 0.5 * g)[..., None]
    t *= (1.15 - 0.45 * v)[..., None]
    stain = _smooth(_fbm(rng, (h, w), 5, 3), 0.55, 0.75)
    t = t * (1 - 0.6 * stain[..., None]) + np.array([86, 64, 24], 'float32') * 0.45 * stain[..., None]
    t += rng.normal(0, 3, (h, w, 1))
    return Image.fromarray(np.clip(t, 0, 255).astype('uint8'))


def _door_out():
    w, h = 256, 116
    img, rng = _plastic(15, w, h, 1.67 / w, 0.75 / h, rib=0.12)
    d = ImageDraw.Draw(img, 'RGBA')
    for k in range(6):                                                               # vent louvers near the hinge edge
        d.rectangle([40 + k * 28, 8, 62 + k * 28, 13], fill=(0, 70, 76, 255))
        d.line([(40 + k * 28, 14), (62 + k * 28, 14)], fill=(160, 255, 250, 140), width=1)
    d.rounded_rectangle([108, 78, 148, 108], 5, fill=(236, 240, 244, 255), outline=(30, 40, 44, 255), width=2)   # lock plate
    d.ellipse([114, 84, 128, 98], fill=(236, 24, 30, 255), outline=(60, 0, 0, 255))
    d.ellipse([130, 84, 144, 98], fill=(40, 90, 50, 255), outline=(10, 40, 10, 255))
    d.ellipse([30, 38, 44, 52], fill=(30, 30, 40, 255))                                # pictogram: head ...
    d.polygon([(25, 82), (49, 82), (37, 54)], fill=(30, 30, 40, 255))                   # ... and body
    for k in range(3):                                                               # boot print dent
        d.rounded_rectangle([196 + k * 11, 52 + (k % 2) * 3, 204 + k * 11, 70 + (k % 2) * 3], 3, fill=(0, 70, 76, 120))
    d.line([(236, 100), (246, 84), (240, 72), (252, 60)], fill=(10, 30, 34, 200), width=1)   # crack
    return img


def _door_in():
    w, h = 256, 116
    rng = np.random.default_rng(16)
    v = np.linspace(0, 1, h)[:, None] * np.ones((1, w))
    t = np.zeros((h, w, 3), 'float32'); t[:] = (88, 190, 190)
    g = _fbm(rng, (h, w), 3, 4)
    t *= (0.78 + 0.34 * g)[..., None]
    t *= (1.05 - 0.2 * v)[..., None]
    dirt = _smooth(_fbm(rng, (h, w), 5, 3), 0.55, 0.8)
    t = t * (1 - 0.5 * dirt[..., None]) + np.array([70, 54, 22], 'float32') * 0.35 * dirt[..., None]
    img = Image.fromarray(np.clip(t, 0, 255).astype('uint8'))
    d = ImageDraw.Draw(img, 'RGBA')
    for _ in range(14):
        x0 = int(rng.integers(0, w - 30)); y0 = int(rng.integers(2, h - 2)); ln = int(rng.integers(10, 50))
        d.line([(x0, y0), (x0 + ln, y0)], fill=(20, 50, 56, 90), width=1)
    return img


def _roof():
    w = h = 128
    rng = np.random.default_rng(17)
    v = np.linspace(0, 1, h)[:, None] * np.ones((1, w))
    t = np.zeros((h, w, 3), 'float32'); t[:] = (250, 252, 255)
    g = _fbm(rng, (h, w), 3, 4)
    t *= (0.9 + 0.12 * g)[..., None]
    ii = np.arange(w)[None, :] * np.ones((h, 1))
    t *= (0.93 + 0.07 * np.cos(ii * 2 * np.pi / 16))[..., None]
    yel = _smooth(_fbm(rng, (h, w), 4, 3), 0.58, 0.8)
    t = t * (1 - 0.5 * yel[..., None]) + np.array([210, 190, 90], 'float32') * 0.5 * yel[..., None]
    img = Image.fromarray(np.clip(t, 0, 255).astype('uint8'))
    d = ImageDraw.Draw(img, 'RGBA')
    for _ in range(7):                                                               # bird droppings with a toxic tint
        cx, cy, r = int(rng.integers(10, w - 10)), int(rng.integers(10, h - 10)), int(rng.integers(3, 7))
        d.ellipse([cx - r, cy - r // 2, cx + r, cy + r // 2], fill=(255, 255, 255, 255))
        d.ellipse([cx - r // 2, cy - r // 3, cx + r // 3, cy + r // 3], fill=(120, 190, 60, 255))
    d.line([(20, 110), (40, 90), (36, 76), (56, 60)], fill=(40, 50, 60, 200), width=1)
    return img


def _sign():
    w = h = 128
    rng = np.random.default_rng(18)
    yy, xx = np.mgrid[0:h, 0:w].astype('float32')
    t = np.zeros((h, w, 3), 'float32'); t[:] = (214, 168, 108)
    grain = 0.5 + 0.5 * np.sin(yy * 0.55 + 3.0 * _fbm(rng, (h, w), 3, 3))
    t *= (0.84 + 0.16 * grain)[..., None]
    g = _fbm(rng, (h, w), 4, 3)
    t *= (0.8 + 0.3 * g)[..., None]
    img = Image.fromarray(np.clip(t, 0, 255).astype('uint8'))
    d = ImageDraw.Draw(img, 'RGBA')
    d.rectangle([2, 2, w - 3, h - 3], outline=(110, 74, 40, 255), width=3)
    cx, cy = 64, 64
    d.ellipse([cx - 46, cy - 46, cx + 46, cy + 46], outline=(220, 24, 28, 255), width=11)   # crossed-circle prohibition symbol
    d.line([(cx - 33, cy - 33), (cx + 33, cy + 33)], fill=(220, 24, 28, 255), width=11)
    for nx, ny in ((9, 9), (w - 10, 9), (9, h - 10), (w - 10, h - 10)):
        d.ellipse([nx - 3, ny - 3, nx + 3, ny + 3], fill=(150, 152, 156, 255), outline=(60, 60, 64, 255))
    for _ in range(14):                                                              # neon splatter from the puddle
        x = int(rng.integers(0, w)); y = int(h * (1 - rng.random() ** 2.0)); r = int(rng.integers(1, 5))
        d.ellipse([x - r, y - r, x + r, y + r], fill=(170, 255, 20, 210))
    return img


def _puddle():
    w = h = 256
    rng = np.random.default_rng(19)
    uu = np.linspace(0, 1, w)[None, :] * np.ones((h, 1))
    rr = np.linspace(0, 1, h)[:, None] * np.ones((1, w))
    th = uu * 2 * np.pi
    s = np.sin(3 * th + 7 * rr + 2.4 * np.sin(2 * th - 4 * rr)) + 0.6 * np.sin(5 * th - 9 * rr + 1.0) + 0.35 * np.sin(8 * th + 14 * rr)
    s = s * _smooth(rr, 0.0, 0.3)
    mix = np.clip(0.5 + 0.38 * s, 0, 1)[..., None]
    t = NEON_BLUE * (1 - mix) + ACID * mix
    k = (np.clip(1 - rr / 0.42, 0, 1) ** 1.4)[..., None]
    t = t * (1 - k) + np.array([210, 255, 255], 'float32') * k
    k2 = _smooth(rr, 0.78, 0.96)[..., None]
    t = t * (1 - 0.78 * k2) + np.array([196, 255, 40], 'float32') * 0.78 * k2
    k3 = _smooth(rr, 0.965, 1.0)[..., None]
    t = t * (1 - k3) + np.array([240, 255, 150], 'float32') * k3
    t *= (0.9 + 0.2 * _fbm(rng, (h, w), 5, 3))[..., None]
    img = Image.fromarray(np.clip(t, 0, 255).astype('uint8'))
    d = ImageDraw.Draw(img, 'RGBA')
    for _ in range(26):                                                              # small bright bubble rings
        cx, cy, r = int(rng.integers(0, w)), int(rng.integers(30, h - 10)), int(rng.integers(3, 8))
        d.ellipse([cx - r * 2, cy - r, cx + r * 2, cy + r], outline=(235, 255, 255, 200), width=1)
    return img


def _tp():
    w, h = 512, 64
    rng = np.random.default_rng(20)
    x = (np.arange(w)[None, :] * TP_LEN / w) * np.ones((h, 1))
    y = (np.arange(h)[:, None] * TP_WID / h) * np.ones((1, w))
    t = np.zeros((h, w, 3), 'float32'); t[:] = (252, 252, 247)
    emb = np.cos(2 * np.pi * (x / 0.04 + y / 0.03)) * np.cos(2 * np.pi * (x / 0.04 - y / 0.03))
    t *= (0.95 + 0.05 * emb)[..., None]
    perf = (x % 0.115) < 0.0035
    dash = (np.arange(h)[:, None] % 6) < 3
    t *= np.where(perf & dash, 0.62, 1.0)[..., None]
    t *= np.where((np.arange(h)[:, None] < 2) | (np.arange(h)[:, None] > h - 3), 0.86, 1.0)[..., None] * np.ones((1, w, 1))
    img = Image.fromarray(np.clip(t, 0, 255).astype('uint8'))
    layer = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for cx in (120, 205, 290):                                                       # boot prints
        d.ellipse([cx - 14, 10, cx + 14, 54], fill=(90, 72, 44, 120))
    for _ in range(26):
        cx = int(rng.integers(0, w)); cy = int(rng.integers(4, h - 4)); r = int(rng.integers(2, 6))
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(110, 90, 50, 70))
    layer = layer.filter(ImageFilter.GaussianBlur(1.2))
    img = Image.alpha_composite(img.convert('RGBA'), layer).convert('RGB')
    a = np.asarray(img).astype('float32')
    u = np.linspace(0, 1, w)[None, :] * np.ones((h, 1))
    wick = _smooth(u, 0.58, 0.95) * (0.6 + 0.4 * _fbm(rng, (h, w), 4, 3))
    toxic = np.where((_fbm(rng, (h, w), 5, 3) > 0.5)[..., None], NEON_BLUE, ACID)
    a = a * (1 - 0.85 * wick[..., None]) + toxic * 0.85 * wick[..., None]
    a += rng.normal(0, 2, (h, w, 1))
    return Image.fromarray(np.clip(a, 0, 255).astype('uint8'))


def _tproll():
    w, h = 256, 64
    rng = np.random.default_rng(21)
    x = np.arange(w)[None, :] * np.ones((h, 1))
    t = np.zeros((h, w, 3), 'float32'); t[:] = (250, 250, 244)
    t *= (0.9 + 0.1 * np.cos(x * 2 * np.pi / 6.0))[..., None]
    t *= (0.9 + 0.2 * _fbm(rng, (h, w), 4, 3))[..., None]
    k = _smooth(np.arange(h)[:, None] * np.ones((1, w)), 0.55 * h, h) * (_fbm(rng, (h, w), 5, 3) > 0.45)
    t = t * (1 - 0.8 * k[..., None]) + ACID * 0.8 * k[..., None]
    return Image.fromarray(np.clip(t, 0, 255).astype('uint8'))


def _stink():
    w, h = 256, 64
    rng = np.random.default_rng(22)
    u = np.linspace(0, 1, w)[None, :] * np.ones((h, 1))
    v = np.linspace(-1, 1, h)[:, None] * np.ones((1, w))
    core = (1 - np.abs(v) ** 1.5)[..., None]
    t = np.array([150, 246, 120], 'float32') * (1 - core * 0.6) + np.array([228, 255, 205], 'float32') * core * 0.6
    t *= (0.88 + 0.12 * np.sin(u * 2 * np.pi * 9))[..., None]
    t += rng.normal(0, 3, (h, w, 1))
    return Image.fromarray(np.clip(t, 0, 255).astype('uint8'))


def _bubble():
    w = h = 128
    rng = np.random.default_rng(23)
    uu = np.linspace(0, 1, w)[None, :] * np.ones((h, 1))
    vv = np.linspace(0, 1, h)[:, None] * np.ones((1, w))                 # 0 = crown, 1 = bottom
    t = np.array([150, 255, 255], 'float32') * (1 - vv[..., None]) + np.array([200, 255, 70], 'float32') * vv[..., None]
    t = t * (0.86 + 0.14 * np.sin(uu * 2 * np.pi * 3 + vv * 6)[..., None])
    rim = np.exp(-((vv - 0.5) / 0.1) ** 2)[..., None]
    t = t * (1 - 0.25 * rim) + np.array([0, 90, 200], 'float32') * 0.25 * rim
    img = Image.fromarray(np.clip(t, 0, 255).astype('uint8'))
    d = ImageDraw.Draw(img, 'RGBA')
    d.ellipse([14, 20, 34, 42], fill=(255, 255, 255, 235))
    d.ellipse([40, 34, 48, 40], fill=(255, 255, 255, 190))
    d.ellipse([80, 12, 92, 22], fill=(255, 255, 255, 200))
    return img


def _label():
    w, h = 128, 64
    t = np.zeros((h, w, 3), 'float32'); t[:] = (176, 255, 40)
    img = Image.fromarray(t.astype('uint8'))
    d = ImageDraw.Draw(img, 'RGBA')
    d.rectangle([2, 2, w - 3, h - 3], outline=(255, 255, 255, 255), width=3)
    d.polygon([(64, 8), (80, 36), (48, 36)], fill=(0, 120, 255, 255))                 # droplet
    d.ellipse([48, 26, 80, 54], fill=(0, 120, 255, 255))
    d.ellipse([56, 32, 62, 40], fill=(255, 255, 255, 220))
    return img


def _tape():
    w, h = 256, 32
    rng = np.random.default_rng(24)
    x = (np.arange(w)[None, :] * 3.0 / w) * np.ones((h, 1))
    y = (np.arange(h)[:, None] * 0.05 / h) * np.ones((1, w))
    m = (((x + y) / 0.07) % 1.0) < 0.5
    t = np.where(m[..., None], np.array([255, 214, 0], 'float32'), np.array([22, 22, 24], 'float32'))
    t = t * (0.9 + 0.1 * _fbm(rng, (h, w), 4, 3))[..., None]
    t[:2] *= 0.8; t[-2:] *= 0.8
    return Image.fromarray(np.clip(t, 0, 255).astype('uint8'))


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
    makers = {'wall': _wall, 'top': _top, 'front': _front, 'inner': _inner, 'door_out': _door_out, 'door_in': _door_in,
              'roof': _roof, 'sign': _sign, 'puddle': _puddle, 'tp': _tp, 'tproll': _tproll, 'stink': _stink,
              'bubble': _bubble, 'label': _label, 'tape': _tape}
    for name, fn in makers.items():
        x0, y0, w, h = REGION[name]
        img = fn()
        assert img.size == (w, h), (name, img.size, (w, h))
        atlas.paste(img, (x0, y0)); rough[y0:y0 + h, x0:x0 + w] = ROUGH[name]
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
    inset = 2.0
    span = CELL - 2 * inset
    return uv_px(col * CELL + inset + f * span, CELL_Y0 + row * CELL + inset + g * span)


def ruv(name, a, b):
    """UV inside a region. a = 0..1 along the region's u (left -> right), b = 0..1 along v (top -> bottom)."""
    x0, y0, w, h = REGION[name]
    a = min(max(a, 0.0), 1.0); b = min(max(b, 0.0), 1.0)
    return uv_px(x0 + 1.0 + a * (w - 2.0), y0 + 1.0 + b * (h - 2.0))
