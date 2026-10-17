"""Texture atlas painter for the Evicted Studio Spin Bike (1024x1024), AI-generated procedural art (PIL/numpy).

The bike is the invented boutique brand "SoulCyclone" (no real brand name is used anywhere).

Layout (pixels, origin top-left):
  (   0,   0)-( 512, 320)  screen    tablet screen: neon SOULCYCLONE console, big 98%, RIDE OR DIE, leaderboard, heart rate
  ( 512,   0)-( 768, 336)  notice    laminated EVICTION NOTICE (red banner, house with a red X, text bars, PAY OR QUIT)
  ( 768,   0)-(1024,  96)  towel     sweaty aqua-and-white striped gym towel (u along the drape, v across)
  ( 768,  96)-(1024, 256)  tback     tablet back: silver case with a magenta-cyan swirl logo
  (   0, 320)-( 256, 576)  cover     polished chrome flywheel guard (polar disc map, swirl logo)
  ( 256, 320)-( 512, 576)  puddle    sweat puddle polar map (u = angle, v = centre -> rim)
  (   0, 576)-( 512, 768)  mat       violet yoga mat 2.1 m x 0.9 m (u along z, v across x)
  ( 512, 336)-( 640, 464)  label     water bottle label (lightning bolt)
  (   0, 960)-(1024,1024)  32 x 2 small 32 px palette cells
paint(out_png) writes the base colour PNG and returns (cells, rough).
TEXT: the screen and the notice carry real lettering (SOULCYCLONE, 98%, RIDE OR DIE, EVICTION NOTICE, PAY OR QUIT). The earlier
props avoided lettering because BG3 may mirror the converted DAE; that is UNVERIFIED. If the in-game check shows mirrored text,
set MIRROR_TEXT = True below (it paints every lettered region flipped left to right) and rebuild.
"""
import math
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

W = 1024
CELL = 32
CELL_Y0 = 960
MIRROR_TEXT = False

FONT_BLACK = 'C:/Windows/Fonts/ariblk.ttf'
FONT_BOLD = 'C:/Windows/Fonts/arialbd.ttf'
FONT_IMPACT = 'C:/Windows/Fonts/impact.ttf'

PINK = (255, 134, 178)            # matte millennial pink frame
MAGENTA = (255, 20, 170)
CYAN = (0, 230, 255)
LIME = (190, 255, 0)

# name: (base RGB, grime 0-1, scratch 0-1, rough 0-1)
PALETTE = {
    'pink':        (PINK, 0.30, 0.30, 0.85),
    'pink_dark':   ((214, 112, 148), 0.35, 0.25, 0.85),
    'pink_light':  ((255, 200, 218), 0.20, 0.15, 0.80),
    'chrome':      ((220, 226, 236), 0.0, 0.0, 0.05),       # replaced by a banded gradient in _tile
    'chrome_dark': ((120, 128, 146), 0.20, 0.20, 0.20),
    'black':       ((18, 18, 22), 0.10, 0.10, 0.55),
    'rubber':      ((36, 34, 38), 0.35, 0.10, 0.85),
    'grip':        ((255, 70, 150), 0.25, 0.20, 0.75),
    'knob':        ((255, 20, 90), 0.05, 0.10, 0.30),
    'saddle':      ((70, 20, 120), 0.30, 0.20, 0.55),
    'saddle_pipe': ((255, 60, 190), 0.10, 0.10, 0.50),
    'lime':        (LIME, 0.20, 0.20, 0.45),
    'lime_dark':   ((120, 190, 0), 0.30, 0.25, 0.50),
    'sole':        ((24, 24, 28), 0.40, 0.20, 0.70),
    'cleat':       ((255, 220, 0), 0.30, 0.30, 0.40),
    'strap':       ((0, 190, 255), 0.15, 0.20, 0.60),
    'white':       ((250, 250, 248), 0.25, 0.10, 0.60),
    'bottle':      ((140, 50, 255), 0.05, 0.10, 0.20),
    'cap':         ((190, 255, 0), 0.05, 0.10, 0.35),
    'tape':        ((255, 214, 0), 0.20, 0.15, 0.55),
    'red':         ((235, 28, 40), 0.15, 0.10, 0.40),
    'drop':        ((120, 235, 255), 0.0, 0.0, 0.05),
    'crystal':     ((190, 90, 255), 0.0, 0.0, 0.10),
    'wheel':       ((60, 60, 66), 0.40, 0.20, 0.80),
    'mat_edge':    ((92, 28, 200), 0.20, 0.15, 0.85),
    'paper_edge':  ((222, 232, 238), 0.20, 0.10, 0.20),
}
ORDER = list(PALETTE)
REGION = {
    'screen': (0, 0, 512, 320), 'notice': (512, 0, 256, 336), 'towel': (768, 0, 256, 96), 'tback': (768, 96, 256, 160),
    'cover': (0, 320, 256, 256), 'puddle': (256, 320, 256, 256), 'mat': (0, 576, 512, 192), 'label': (512, 336, 128, 128),
}
ROUGH = {'screen': 0.05, 'notice': 0.10, 'towel': 0.95, 'tback': 0.25, 'cover': 0.05, 'puddle': 0.04, 'mat': 0.85, 'label': 0.4}


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


def _font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def _text_center(d, cx, cy, text, font, fill, stroke=0, stroke_fill=None):
    bbox = d.textbbox((0, 0), text, font=font, stroke_width=stroke)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.text((cx - w / 2 - bbox[0], cy - h / 2 - bbox[1]), text, font=font, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)


def _flip_if_needed(img):
    return ImageOps.mirror(img) if MIRROR_TEXT else img


def _glow(img, layer_fn, blur, strength=1.0):
    """Paint layer_fn(draw) on a black RGBA layer, blur it and add it on top (neon glow), then draw it sharp."""
    glow = Image.new('RGBA', img.size, (0, 0, 0, 0))
    layer_fn(ImageDraw.Draw(glow))
    soft = glow.filter(ImageFilter.GaussianBlur(blur))
    base = img.convert('RGBA')
    for _ in range(int(max(1, strength * 2))):
        base = Image.alpha_composite(base, soft)
    return Image.alpha_composite(base, glow).convert('RGB')


def _swirl(d, cx, cy, r, c0, c1, width, turns=2.3, steps=70):
    """Logo spiral: a thick two-colour arm winding out from the centre."""
    pts = []
    for i in range(steps + 1):
        t = i / steps
        a = turns * 2 * math.pi * t - math.pi / 2
        pts.append((cx + r * t * math.cos(a), cy + r * t * math.sin(a), t))
    for i in range(steps):
        t = pts[i][2]
        col = tuple(int(c0[k] * (1 - t) + c1[k] * t) for k in range(3)) + (255,)
        d.line([pts[i][:2], pts[i + 1][:2]], fill=col, width=max(2, int(width * (0.45 + 0.8 * t))))


def _screen():
    w, h = 512, 320
    rng = np.random.default_rng(31)
    yy = np.linspace(0, 1, h)[:, None] * np.ones((1, w))
    t = np.zeros((h, w, 3), 'float32')
    t[...] = np.array([18, 0, 44]) * (1 - yy[..., None]) + np.array([86, 0, 110]) * yy[..., None]
    img = Image.fromarray(np.clip(t, 0, 255).astype('uint8'))
    d = ImageDraw.Draw(img, 'RGBA')
    for k in range(-6, 22):                                           # retro perspective grid on the lower half
        d.line([(w / 2 + (k - 8) * 8, 150), (w / 2 + (k - 8) * 70, h)], fill=(255, 40, 200, 90), width=1)
    for k in range(7):
        y = 150 + (k / 6.0) ** 1.8 * (h - 150)
        d.line([(0, y), (w, y)], fill=(255, 40, 200, 90), width=1)
    f_head, f_big, f_mid, f_small = _font(FONT_BLACK, 26), _font(FONT_BLACK, 118), _font(FONT_BLACK, 44), _font(FONT_BOLD, 22)

    def header(g):
        g.rounded_rectangle([22, 18, w - 22, 56], 8, outline=CYAN + (255,), width=3)
        _swirl(g, 52, 37, 14, (255, 20, 170), (0, 230, 255), 4, turns=1.6)
        _text_center(g, 290, 37, 'SOULCYCLONE', f_head, CYAN + (255,))
    img = _glow(img, header, 5, 1.0)
    d = ImageDraw.Draw(img, 'RGBA')

    def big(g):
        _text_center(g, 178, 150, '98%', f_big, MAGENTA + (255,), stroke=3, stroke_fill=(255, 190, 240, 255))
    img = _glow(img, big, 9, 1.5)
    d = ImageDraw.Draw(img, 'RGBA')
    d.polygon([(36, 226), (50, 244), (64, 226), (70, 216), (62, 206), (50, 210), (38, 206), (30, 216)], fill=(255, 50, 80, 255))
    d.text((78, 222), '187 BPM', font=f_small, fill=(255, 255, 255, 235))
    d.text((206, 222), 'PR! 9001', font=f_small, fill=(255, 235, 60, 255))
    # leaderboard on the right: bars with ranks, the top one is YOU, glowing lime
    for i, (bw, col) in enumerate(((150, LIME), (136, CYAN), (122, CYAN), (104, CYAN), (84, CYAN))):
        y = 76 + i * 30
        d.rounded_rectangle([356, y, 356 + bw * 0.9, y + 20], 6, fill=col + (255,), outline=(255, 255, 255, 220), width=2)
        d.text((330, y - 1), str(i + 1), font=f_small, fill=(255, 255, 255, 255))
    d.polygon([(352, 62), (366, 52), (380, 62)], fill=(255, 220, 0, 255))      # crown over the top rank
    # RIDE OR DIE banner
    d.rounded_rectangle([34, 258, w - 34, 304], 12, fill=(255, 30, 30, 255), outline=(255, 235, 60, 255), width=4)

    def banner(g):
        _text_center(g, w / 2, 281, 'RIDE OR DIE', f_mid, (255, 255, 255, 255), stroke=2, stroke_fill=(120, 0, 0, 255))
    img = _glow(img, banner, 2, 0.5)
    d = ImageDraw.Draw(img, 'RGBA')
    # heart-rate heart and flame
    d.polygon([(450, 226), (438, 242), (446, 254), (456, 242), (464, 254), (474, 240), (462, 216)], fill=(255, 150, 0, 255))
    # dark bezel margin
    bez = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bez)
    bd.rectangle([0, 0, w, h], outline=(10, 10, 14, 255), width=14)
    bd.rounded_rectangle([0, 0, w - 1, h - 1], 16, outline=(40, 40, 50, 255), width=4)
    img = Image.alpha_composite(img.convert('RGBA'), bez).convert('RGB')
    return _flip_if_needed(img)


def _notice():
    w, h = 256, 336
    rng = np.random.default_rng(32)
    t = np.zeros((h, w, 3), 'float32'); t[:] = (250, 250, 246)
    t *= (0.96 + 0.06 * _fbm(rng, (h, w), 4, 3))[..., None]
    img = Image.fromarray(np.clip(t, 0, 255).astype('uint8'))
    d = ImageDraw.Draw(img, 'RGBA')
    d.rectangle([0, 0, w - 1, h - 1], outline=(200, 214, 224, 255), width=6)            # laminate seal border
    d.rectangle([14, 14, w - 15, 92], fill=(220, 24, 30, 255))                          # red banner
    f1, f2 = _font(FONT_IMPACT, 46), _font(FONT_IMPACT, 36)
    _text_center(d, w / 2, 40, 'EVICTION', f1, (255, 255, 255, 255))
    _text_center(d, w / 2, 76, 'NOTICE', f2, (255, 235, 60, 255))
    # house with a big red X
    d.polygon([(128, 104), (176, 140), (80, 140)], fill=(70, 70, 80, 255))
    d.rectangle([90, 140, 166, 190], fill=(120, 120, 134, 255))
    d.rectangle([118, 158, 140, 190], fill=(60, 40, 30, 255))
    d.rectangle([98, 150, 112, 164], fill=(150, 220, 255, 255))
    d.line([(76, 100), (180, 196)], fill=(220, 24, 30, 255), width=14)
    d.line([(180, 100), (76, 196)], fill=(220, 24, 30, 255), width=14)
    for i in range(6):                                                                  # text bars
        bw = (210, 196, 210, 180, 206, 120)[i]
        d.rectangle([22, 206 + i * 12, 22 + bw * 0.96, 212 + i * 12], fill=(120, 126, 136, 255))
    d.rectangle([22, 284, w - 22, 322], fill=(255, 235, 60, 255), outline=(30, 30, 30, 255), width=3)
    _text_center(d, w / 2, 303, 'PAY OR QUIT', _font(FONT_IMPACT, 30), (200, 10, 20, 255))
    d.ellipse([26, 100, 54, 128], fill=(255, 60, 190, 255))                              # a sticker: the studio has moved on
    d.line([(32, 114), (48, 114)], fill=(255, 255, 255, 255), width=3)
    sheen = Image.new('RGBA', (w, h), (0, 0, 0, 0))                                     # lamination glare
    sd = ImageDraw.Draw(sheen)
    sd.polygon([(150, 0), (210, 0), (60, h), (0, h), (0, h - 70)], fill=(255, 255, 255, 38))
    img = Image.alpha_composite(img.convert('RGBA'), sheen).convert('RGB')
    return _flip_if_needed(img)


def _towel():
    w, h = 256, 96
    rng = np.random.default_rng(33)
    t = np.zeros((h, w, 3), 'float32'); t[:] = (0, 205, 222)
    ii = np.arange(w)[None, :] * np.ones((h, 1))
    jj = np.arange(h)[:, None] * np.ones((1, w))
    t *= (0.9 + 0.1 * np.cos(ii * 2 * np.pi / 3.0) * np.cos(jj * 2 * np.pi / 3.0))[..., None]
    for x0, x1 in ((18, 34), (40, 46), (w - 46, w - 40), (w - 34, w - 18)):          # white end stripes
        t[:, x0:x1] = t[:, x0:x1] * 0.1 + np.array([255, 255, 255], 'float32') * 0.9
    damp = _smooth(_fbm(rng, (h, w), 3, 4), 0.50, 0.72)
    t = t * (1 - 0.46 * damp[..., None]) + np.array([90, 120, 150], 'float32') * 0.46 * damp[..., None]
    t += rng.normal(0, 4, (h, w, 1))
    return Image.fromarray(np.clip(t, 0, 255).astype('uint8'))


def _tback():
    w, h = 256, 160
    rng = np.random.default_rng(34)
    yy = np.linspace(0, 1, h)[:, None] * np.ones((1, w))
    t = np.zeros((h, w, 3), 'float32')
    t[:] = np.array([226, 230, 238]) * (1 - yy[..., None] * 0.18)
    t += rng.normal(0, 2, (h, w, 1))
    img = Image.fromarray(np.clip(t, 0, 255).astype('uint8'))
    d = ImageDraw.Draw(img, 'RGBA')
    _swirl(d, 128, 78, 56, (255, 20, 170), (0, 220, 255), 14, turns=2.0, steps=90)
    d.ellipse([112, 62, 144, 94], fill=(255, 255, 255, 255))
    d.ellipse([120, 70, 136, 86], fill=(255, 20, 170, 255))
    d.rectangle([0, 0, w - 1, h - 1], outline=(150, 156, 170, 255), width=4)
    return img


def _cover():
    w = h = 256
    rng = np.random.default_rng(35)
    yy, xx = np.mgrid[0:h, 0:w].astype('float32')
    dx, dy = (xx - 127.5) / 127.5, (yy - 127.5) / 127.5
    r = np.sqrt(dx * dx + dy * dy)
    th = np.arctan2(dy, dx)
    # polished-chrome look: banded radial reflections plus a bright wedge, like a reflection of a studio window
    band = 0.5 + 0.5 * np.cos(r * 16.0 + 0.7 * np.sin(th * 2))
    base = 185 + 70 * band
    wedge = _smooth(np.cos(th - 0.9), 0.55, 0.95)
    dark = _smooth(np.cos(th + 2.3), 0.4, 0.9)
    v = base * (1 - 0.22 * dark) + 70 * wedge
    t = np.stack([v * 0.96, v * 0.99, v * 1.04], -1)
    t[r > 0.97] = (70, 76, 92)
    img = Image.fromarray(np.clip(t, 0, 255).astype('uint8'))
    d = ImageDraw.Draw(img, 'RGBA')
    for rr in (0.30, 0.62, 0.84):                                                       # moulded ring grooves
        d.ellipse([127.5 - rr * 127.5, 127.5 - rr * 127.5, 127.5 + rr * 127.5, 127.5 + rr * 127.5],
                  outline=(60, 66, 84, 200), width=3)
        d.ellipse([127.5 - rr * 127.5 + 3, 127.5 - rr * 127.5 + 3, 127.5 + rr * 127.5 - 3, 127.5 + rr * 127.5 - 3],
                  outline=(255, 255, 255, 180), width=1)
    _swirl(d, 127, 127, 70, (255, 20, 170), (0, 220, 255), 16, turns=2.1, steps=100)    # the brand swirl
    d.ellipse([110, 110, 146, 146], fill=(255, 255, 255, 255), outline=(60, 66, 84, 255), width=3)
    d.ellipse([120, 120, 136, 136], fill=(255, 20, 170, 255))
    for _ in range(26):                                                                 # fingerprints and scuffs
        a = rng.random() * 6.28; rr = 0.25 + 0.7 * rng.random()
        x, y = 127.5 + 127.5 * rr * math.cos(a), 127.5 + 127.5 * rr * math.sin(a)
        d.line([(x, y), (x + rng.integers(-12, 12), y + rng.integers(-6, 6))], fill=(255, 255, 255, 120), width=1)
    return img


def _puddle():
    w = h = 256
    rng = np.random.default_rng(36)
    uu = np.linspace(0, 1, w)[None, :] * np.ones((h, 1))
    rr = np.linspace(0, 1, h)[:, None] * np.ones((1, w))
    th = uu * 2 * np.pi
    s = np.sin(3 * th + 6 * rr) * 0.5 + np.sin(5 * th - 8 * rr + 1.0) * 0.3
    mix = np.clip(0.5 + 0.4 * s, 0, 1)[..., None]
    t = np.array([60, 215, 255], 'float32') * (1 - mix) + np.array([170, 245, 255], 'float32') * mix
    k = (np.clip(1 - rr / 0.45, 0, 1) ** 1.3)[..., None]
    t = t * (1 - 0.6 * k) + np.array([230, 255, 255], 'float32') * 0.6 * k
    k2 = _smooth(rr, 0.8, 0.96)[..., None]
    t = t * (1 - 0.7 * k2) + np.array([255, 255, 255], 'float32') * 0.7 * k2
    k3 = _smooth(rr, 0.965, 1.0)[..., None]
    t = t * (1 - k3) + np.array([255, 255, 215], 'float32') * k3
    t *= (0.92 + 0.14 * _fbm(rng, (h, w), 5, 3))[..., None]
    img = Image.fromarray(np.clip(t, 0, 255).astype('uint8'))
    d = ImageDraw.Draw(img, 'RGBA')
    for _ in range(22):
        cx, cy, r = int(rng.integers(0, w)), int(rng.integers(30, h - 10)), int(rng.integers(3, 8))
        d.ellipse([cx - r * 2, cy - r, cx + r * 2, cy + r], outline=(255, 255, 255, 220), width=1)
    return img


def _mat():
    w, h = 512, 192
    rng = np.random.default_rng(37)
    ii = np.arange(w)[None, :] * np.ones((h, 1)); jj = np.arange(h)[:, None] * np.ones((1, w))
    t = np.zeros((h, w, 3), 'float32'); t[:] = (128, 40, 245)
    g = _fbm(rng, (h, w), 4, 4)
    t *= (0.86 + 0.24 * g)[..., None]
    t *= (0.95 + 0.05 * np.cos(jj * 2 * np.pi / 3.0))[..., None]                       # foam texture
    img = Image.fromarray(np.clip(t, 0, 255).astype('uint8'))
    d = ImageDraw.Draw(img, 'RGBA')
    d.rectangle([4, 4, w - 5, h - 5], outline=LIME + (255,), width=6)                  # lime border
    d.line([(w // 2, 10), (w // 2, h - 10)], fill=(255, 255, 255, 170), width=3)       # alignment lines
    for x in (w // 4, 3 * w // 4):
        d.line([(x, 70), (x, h - 70)], fill=(255, 255, 255, 120), width=2)
    d.line([(10, h // 2), (w - 10, h // 2)], fill=(255, 255, 255, 120), width=2)
    for cx in (60, w - 60):                                                            # lotus petal ring
        for k in range(8):
            a = k * math.pi / 4
            d.ellipse([cx + 26 * math.cos(a) - 14, h / 2 + 26 * math.sin(a) - 14, cx + 26 * math.cos(a) + 14, h / 2 + 26 * math.sin(a) + 14],
                      outline=(255, 120, 220, 230), width=3)
    for _ in range(16):                                                                # footprints worn into the foam
        cx, cy = int(rng.integers(120, w - 120)), int(rng.integers(30, h - 30))
        d.ellipse([cx - 6, cy - 10, cx + 6, cy + 10], fill=(70, 10, 150, 90))
    return img


def _label():
    w = h = 128
    t = np.zeros((h, w, 3), 'float32'); t[:] = (250, 250, 246)
    img = Image.fromarray(t.astype('uint8'))
    d = ImageDraw.Draw(img, 'RGBA')
    d.rectangle([0, 0, w - 1, 6], fill=(255, 20, 170, 255)); d.rectangle([0, h - 7, w - 1, h - 1], fill=(255, 20, 170, 255))
    d.polygon([(76, 12), (46, 70), (64, 70), (52, 116), (92, 52), (72, 52), (88, 12)], fill=(255, 200, 0, 255), outline=(40, 40, 40, 255))
    return img


def _tile(name, seed):
    base, grime, scratch, _ = PALETTE[name]
    rng = np.random.default_rng(seed)
    t = np.zeros((CELL, CELL, 3), 'float32'); t[:] = base
    if name == 'chrome':
        g = np.linspace(0, 1, CELL)[:, None] * np.ones((1, CELL))       # v (the around-the-tube coordinate) runs along image y
        band = 0.5 + 0.5 * np.cos(g * 2 * np.pi + 0.4)
        v = 150 + 105 * band ** 1.2
        t = np.stack([v * 0.95, v * 0.99, v * 1.06], -1)
        return Image.fromarray(np.clip(t, 0, 255).astype('uint8'))
    t *= np.linspace(1.06, 0.94, CELL)[:, None, None]
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
    makers = {'screen': _screen, 'notice': _notice, 'towel': _towel, 'tback': _tback, 'cover': _cover, 'puddle': _puddle,
              'mat': _mat, 'label': _label}
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
