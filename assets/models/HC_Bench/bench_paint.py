"""Texture atlas painter for the Hostile Architecture Bench (1024x1024), AI-generated procedural art (PIL/numpy).

Layout (pixels, origin top-left):
  (   0,   0)-( 512, 200)  pad      concrete pad top (planar over 3.2 x 1.24 m): joints, cracks, oil, gum, butts, yellow curb strip
  ( 512,   0)-( 768, 192)  ad       sponsor ad panel: hot-pink, giant smiley and a 'no lying down' pictogram (shapes only)
  (   0, 200)-( 512, 320)  barcode  neon-yellow municipal asset-tag plate: QR block, barcode bars, fake text dashes, city seal
  (   0, 960)-(1024,1024)  32 x 2 small 32 px palette cells (green, chrome, yellow, concrete, ...)
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
    'green':        ((16, 122, 70), 0.30, 0.25, 0.45),
    'green_hi':     ((46, 170, 100), 0.20, 0.30, 0.40),
    'green_dark':   ((8, 76, 46), 0.40, 0.20, 0.55),
    'chrome':       ((236, 242, 252), 0.0, 0.0, 0.10),     # painted with reflection bands below
    'steel_stud':   ((226, 232, 242), 0.05, 0.25, 0.20),
    'bolt':         ((190, 196, 206), 0.20, 0.30, 0.35),
    'concrete':     ((170, 166, 156), 0.35, 0.10, 0.90),
    'concrete_dk':  ((124, 120, 112), 0.45, 0.10, 0.90),
    'yellow':       ((255, 232, 0), 0.05, 0.10, 0.40),
    'black':        ((16, 16, 18), 0.0, 0.0, 0.50),
    'pink':         ((255, 48, 170), 0.05, 0.05, 0.40),
    'white':        ((250, 250, 246), 0.10, 0.05, 0.40),
    'pigeon':       ((150, 158, 176), 0.20, 0.0, 0.85),
    'pigeon_dark':  ((84, 92, 118), 0.20, 0.0, 0.85),
    'pigeon_neck':  ((140, 60, 200), 0.0, 0.0, 0.40),
    'pigeon_neck2': ((30, 200, 130), 0.0, 0.0, 0.40),
    'orange':       ((255, 140, 10), 0.05, 0.05, 0.50),
    'red':          ((236, 28, 36), 0.10, 0.05, 0.40),
    'leaf':         ((90, 200, 40), 0.0, 0.0, 0.80),
}
ORDER = list(PALETTE)
REGION = {'pad': (0, 0, 512, 200), 'ad': (512, 0, 256, 192), 'barcode': (0, 200, 512, 120)}
ROUGH = {'pad': 0.92, 'ad': 0.35, 'barcode': 0.4}
PAD_W, PAD_D = 3.2, 1.24


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


def _smiley(d, cx, cy, r, bg=(255, 232, 0, 255), face=(30, 30, 30, 255)):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=bg, outline=(60, 40, 0, 255), width=max(2, r // 12))
    e = max(2, r // 5)
    for sx in (-1, 1):
        d.ellipse([cx + sx * r // 2 - e, cy - r // 3 - e * 2, cx + sx * r // 2 + e, cy - r // 3 + e * 2], fill=face)
        d.ellipse([cx + sx * r * 6 // 10 - e, cy + r // 8 - e, cx + sx * r * 6 // 10 + e, cy + r // 8 + e], fill=(255, 110, 130, 190))
    d.arc([cx - r * 6 // 10, cy - r // 4, cx + r * 6 // 10, cy + r * 7 // 10], 10, 170, fill=face, width=max(3, r // 7))


def _pad():
    w, h = REGION['pad'][2:]
    rng = np.random.default_rng(31)
    v = np.linspace(0, 1, h)[:, None] * np.ones((1, w))
    t = np.zeros((h, w, 3), 'float32'); t[:] = (176, 172, 162)
    g = _fbm(rng, (h, w), 4, 5)
    t *= (0.80 + 0.40 * g)[..., None]
    speck = rng.random((h, w, 1))
    t = np.where(speck > 0.985, t * 0.55, np.where(speck < 0.012, np.minimum(t * 1.25, 255), t))
    t += rng.normal(0, 3.5, (h, w, 1))
    img = Image.fromarray(np.clip(t, 0, 255).astype('uint8'))
    d = ImageDraw.Draw(img, 'RGBA')
    # expansion joints (dark grooves with a light edge) at the slab quarters
    for x in (w // 4, w // 2 + 20, w * 3 // 4 + 8):
        d.line([(x, 0), (x, h)], fill=(70, 66, 60, 255), width=3)
        d.line([(x + 2, 0), (x + 2, h)], fill=(215, 211, 200, 160), width=1)
    d.line([(0, h // 2 + 10), (w, h // 2 + 10)], fill=(70, 66, 60, 255), width=3)
    # cracks with a tuft of weeds
    for pts in ([(60, 30), (90, 60), (84, 96), (120, 130), (112, 170)], [(380, 20), (352, 58), (372, 100), (340, 150)]):
        d.line(pts, fill=(52, 48, 44, 255), width=2, joint='curve')
    for tx, ty in ((120, 130), (340, 150)):
        for k in range(5):
            d.line([(tx, ty), (tx + (k - 2) * 5, ty - 14 - (k % 2) * 7)], fill=(70, 170, 40, 255), width=2)
        d.ellipse([tx - 4, ty - 26, tx + 4, ty - 18], fill=(255, 224, 0, 255))
    # oil stain
    layer = Image.new('RGBA', (w, h), (0, 0, 0, 0)); ld = ImageDraw.Draw(layer)
    for (cx, cy, rx, ry) in ((330, 120, 46, 28), (366, 104, 26, 18), (150, 40, 30, 16)):
        ld.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=(36, 30, 22, 120))
    # gum splats (pink and grey) and cigarette butts
    for _ in range(30):
        x, y, r = int(rng.integers(8, w - 8)), int(rng.integers(8, h - 24)), int(rng.integers(2, 5))
        col = (255, 120, 180, 230) if rng.random() < 0.5 else (92, 88, 82, 230)
        ld.ellipse([x - r, y - r, x + r, y + r], fill=col)
    for _ in range(9):
        x, y = int(rng.integers(20, w - 20)), int(rng.integers(20, h - 30)); a = rng.random() * math.pi
        dx, dy = math.cos(a) * 9, math.sin(a) * 9
        ld.line([(x, y), (x + dx, y + dy)], fill=(245, 240, 225, 255), width=3)
        ld.line([(x + dx * 0.8, y + dy * 0.8), (x + dx, y + dy)], fill=(255, 140, 30, 255), width=3)
    layer = layer.filter(ImageFilter.GaussianBlur(0.6))
    img = Image.alpha_composite(img.convert('RGBA'), layer)
    d = ImageDraw.Draw(img, 'RGBA')
    # faded yellow curb strip along the front edge (v = 1 is the front, +Z) and bird droppings
    d.rectangle([0, h - 20, w, h], fill=(255, 214, 0, 255))
    for _ in range(40):
        x = int(rng.integers(0, w)); d.rectangle([x, h - 20, x + int(rng.integers(3, 14)), h], fill=(150, 146, 134, 150))
    for _ in range(14):
        x, y, r = int(rng.integers(8, w - 8)), int(rng.integers(10, h - 30)), int(rng.integers(2, 5))
        d.ellipse([x - r * 2, y - r, x + r * 2, y + r], fill=(252, 252, 250, 255))
        d.ellipse([x - r, y - r // 2, x + r, y + r // 2], fill=(110, 90, 50, 255))
    return img.convert('RGB')


def _ad():
    w, h = REGION['ad'][2:]
    yy = np.linspace(0, 1, h)[:, None, None] * np.ones((1, w, 1))
    t = np.array([255, 36, 168], 'float32') * (1 - yy) + np.array([255, 120, 210], 'float32') * yy
    img = Image.fromarray(np.clip(t * np.ones((h, w, 3)), 0, 255).astype('uint8'))
    d = ImageDraw.Draw(img, 'RGBA')
    d.rounded_rectangle([5, 5, w - 6, h - 6], 14, outline=(255, 255, 255, 255), width=6)
    d.rounded_rectangle([14, 14, w - 15, h - 15], 10, outline=(255, 232, 0, 255), width=3)
    # cheerful giant smiley
    _smiley(d, 66, 80, 52)
    # 'no lying down' pictogram: figure stretched out on a bench inside a red prohibition circle
    cx, cy, r = 190, 82, 56
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255, 255))
    ink = (30, 30, 44, 255)
    d.rectangle([cx - 38, cy + 14, cx + 38, cy + 21], fill=ink)                                         # bench seat
    for lx in (cx - 32, cx + 28):
        d.rectangle([lx, cy + 21, lx + 6, cy + 36], fill=ink)
    d.ellipse([cx - 40, cy - 14, cx - 22, cy + 4], fill=ink)                                              # head
    d.rounded_rectangle([cx - 24, cy - 4, cx + 20, cy + 12], 6, fill=ink)                                 # torso lying flat
    d.rounded_rectangle([cx + 14, cy - 2, cx + 40, cy + 10], 5, fill=ink)                                 # legs
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(230, 20, 30, 255), width=10)
    d.line([(cx - 40, cy - 40), (cx + 40, cy + 40)], fill=(230, 20, 30, 255), width=10)
    # big heart plus little stars, a sky-blue strip of fake fine print
    for hx, hy, hs in ((46, 156, 15), (208, 160, 11)):
        d.ellipse([hx - hs, hy - hs, hx, hy], fill=(255, 255, 255, 255)); d.ellipse([hx, hy - hs, hx + hs, hy], fill=(255, 255, 255, 255))
        d.polygon([(hx - hs, hy - hs // 3), (hx + hs, hy - hs // 3), (hx, hy + hs)], fill=(255, 255, 255, 255))
    d.rounded_rectangle([70, 140, 190, 178], 8, fill=(40, 200, 255, 255))
    for k in range(3):
        d.line([(80, 150 + k * 10), (80 + 80 - k * 18, 150 + k * 10)], fill=(255, 255, 255, 255), width=4)
    return img


def _barcode():
    w, h = REGION['barcode'][2:]
    rng = np.random.default_rng(33)
    t = np.zeros((h, w, 3), 'float32'); t[:] = (255, 240, 0)
    t *= (0.94 + 0.06 * _fbm(rng, (h, w), 4, 3))[..., None]
    img = Image.fromarray(np.clip(t, 0, 255).astype('uint8'))
    d = ImageDraw.Draw(img, 'RGBA')
    d.rectangle([0, 0, w - 1, h - 1], outline=(16, 16, 18, 255), width=6)
    d.rectangle([8, 8, w - 9, 22], fill=(16, 16, 18, 255))                                               # header band
    for k in range(9):
        d.rectangle([20 + k * 54, 11, 20 + k * 54 + 30, 19], fill=(255, 240, 0, 255))                    # fake header text
    # QR-ish block
    q = 74; x0, y0 = 22, 34
    d.rectangle([x0, y0, x0 + q, y0 + q], fill=(255, 255, 255, 255), outline=(16, 16, 18, 255), width=2)
    cell = q // 9
    for i in range(9):
        for j in range(9):
            finder = (i < 3 and j < 3) or (i > 5 and j < 3) or (i < 3 and j > 5)
            on = finder and not (i % 3 == 1 and j % 3 == 1 and False)
            if finder:
                on = (i % 3 != 1 or j % 3 != 1) or True
            elif rng.random() < 0.5:
                on = True
            if on:
                d.rectangle([x0 + i * cell + 2, y0 + j * cell + 2, x0 + (i + 1) * cell + 1, y0 + (j + 1) * cell + 1], fill=(16, 16, 18, 255))
    # barcode bars
    bx = 118
    while bx < 352:
        bw = int(rng.choice([3, 3, 5, 7, 9])); gap = int(rng.choice([3, 5, 7]))
        d.rectangle([bx, 34, bx + bw, 92], fill=(16, 16, 18, 255)); bx += bw + gap
    for k in range(5):                                                                                    # fake digits as blocks
        d.rectangle([124 + k * 46, 98, 124 + k * 46 + 32, 106], fill=(16, 16, 18, 255))
    # city seal: black disc, yellow star, and three text dashes
    sx, sy = 420, 68
    d.ellipse([sx - 40, sy - 40, sx + 40, sy + 40], fill=(16, 16, 18, 255))
    pts = [(sx + (30 if k % 2 == 0 else 13) * math.cos(-math.pi / 2 + k * math.pi / 5),
            sy + (30 if k % 2 == 0 else 13) * math.sin(-math.pi / 2 + k * math.pi / 5)) for k in range(10)]
    d.polygon(pts, fill=(255, 240, 0, 255))
    d.rectangle([22, 108, 70, 112], fill=(16, 16, 18, 255))
    return img


def _tile(name, seed):
    base, grime, scratch, _ = PALETTE[name]
    rng = np.random.default_rng(seed)
    t = np.zeros((CELL, CELL, 3), 'float32'); t[:] = base
    if name == 'chrome':
        # tubes map the cell's v axis around the tube: bright white reflection bands, a dark horizon band, a cool sky tint
        v = np.linspace(0, 1, CELL)[:, None] * np.ones((1, CELL))
        bright = np.exp(-((v - 0.28) / 0.13) ** 2)
        dark = np.exp(-((v - 0.80) / 0.10) ** 2)
        t = np.array([232, 238, 248], 'float32') * np.ones((CELL, CELL, 3))
        t = t * (1 - 0.62 * dark[..., None]) + np.array([255, 255, 255], 'float32') * 0.85 * bright[..., None]
        t = np.clip(t, 0, 255)
        return Image.fromarray(t.astype('uint8'))
    t *= np.linspace(1.08, 0.92, CELL)[:, None, None]
    lf = Image.fromarray((rng.random((5, 5)) * 255).astype('uint8')).resize((CELL, CELL), Image.BICUBIC)
    g = np.asarray(lf).astype('float32') / 255.0
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
    for name, fn in (('pad', _pad), ('ad', _ad), ('barcode', _barcode)):
        x0, y0, w, h = REGION[name]
        img = fn()
        assert img.size == (w, h), (name, img.size, (w, h))
        atlas.paste(img, (x0, y0)); rough[y0:y0 + h, x0:x0 + w] = ROUGH[name]
    cells = {}
    for i, name in enumerate(ORDER):
        col, row = i % 32, i // 32
        atlas.paste(_tile(name, 600 + i), (col * CELL, CELL_Y0 + row * CELL))
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
