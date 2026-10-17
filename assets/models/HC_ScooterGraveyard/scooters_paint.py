"""Texture atlas painter for the Dockless Scooter Graveyard (1024x1024), AI-generated procedural art.

Layout (pixels, origin top-left; see REGION and the palette cells at the bottom):
  pave   (  0,   0, 576, 384)  cracked sidewalk seen from above (u = x, v = z, top = back of the prop)
  fence  (576,   0, 448, 224)  chain-link mesh with torn hole, caught plastic bags, rust
  st0-3  (576+112i, 224, 112, 96) die-cut stickers: smiley, lightning bolt, heart, star
  qr     (576, 320,  96,  96)  scan-me plate (pixel pattern, no letters)
  wheel  (672, 320,  96,  96)  wheel face (polar: hub, spokes, sidewall)
  tread  (768, 320, 128,  48)  tyre tread
  dash   (768, 368, 128,  48)  handlebar display with a low-battery glow
  cone   (896, 320, 128, 192)  traffic cone
  grip   (  0, 384, 288,  96)  grip tape
  b_lime / b_cyan / b_white (192 x 96 each at y = 480) scooter body panels
  cells  32 x 32 palette cells from y = 896 (32 per row)
paint(out_png, glows) writes the base colour PNG and returns the roughness map. glows = [(x, z, radius_m, (r, g, b))] are
LED light pools painted onto the pavement (there is no emissive map; the LEDs themselves are bright in the base colour).
Lettering is deliberately absent (BG3 mirrors the DAE, so text would need an in-game check).
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W = 1024
CELL = 32
CELL_Y0 = 896

LIME = (160, 238, 8)
CYAN = (24, 212, 240)
WHITE = (240, 244, 240)

# name: (base RGB, grime 0-1, scratch 0-1, rough 0-1)
PALETTE = {
    'lime':        (LIME, 0.30, 0.30, 0.38),
    'lime_dark':   ((98, 168, 0), 0.40, 0.25, 0.42),
    'cyan':        (CYAN, 0.30, 0.30, 0.38),
    'cyan_dark':   ((0, 150, 190), 0.40, 0.25, 0.42),
    'white':       (WHITE, 0.35, 0.30, 0.40),
    'white_dark':  ((186, 192, 190), 0.45, 0.30, 0.45),
    'rubber':      ((26, 26, 28), 0.35, 0.10, 0.85),
    'rubber_grey': ((70, 70, 74), 0.45, 0.20, 0.85),
    'steel':       ((176, 180, 188), 0.45, 0.45, 0.30),
    'steel_dark':  ((92, 96, 104), 0.50, 0.40, 0.35),
    'led_cyan':    ((70, 255, 240), 0.0, 0.0, 0.10),
    'led_green':   ((110, 255, 50), 0.0, 0.0, 0.10),
    'led_red':     ((255, 40, 50), 0.0, 0.0, 0.10),
    'concrete':    ((150, 146, 138), 0.55, 0.20, 0.90),
    'concrete_dark': ((100, 98, 94), 0.60, 0.15, 0.92),
    'rust':        ((140, 78, 44), 0.55, 0.30, 0.80),
    'zip_black':   ((18, 18, 22), 0.10, 0.10, 0.60),
    'zip_white':   ((232, 232, 220), 0.30, 0.10, 0.60),
    'weed':        ((62, 168, 40), 0.20, 0.00, 0.80),
    'weed_dark':   ((34, 108, 30), 0.20, 0.00, 0.80),
    'orange':      ((255, 100, 0), 0.30, 0.20, 0.45),
    'yellow':      ((250, 214, 20), 0.25, 0.20, 0.40),
    'pink':        ((255, 80, 170), 0.25, 0.10, 0.60),
    'purple':      ((150, 60, 220), 0.25, 0.10, 0.60),
}
ORDER = list(PALETTE)
REGION = {
    'pave': (0, 0, 576, 384),
    'fence': (576, 0, 448, 224),
    'st0': (576, 224, 112, 96), 'st1': (688, 224, 112, 96), 'st2': (800, 224, 112, 96), 'st3': (912, 224, 112, 96),
    'qr': (576, 320, 96, 96),
    'wheel': (672, 320, 96, 96),
    'tread': (768, 320, 128, 48),
    'dash': (768, 368, 128, 48),
    'cone': (896, 320, 128, 192),
    'grip': (0, 384, 288, 96),
    'b_lime': (0, 480, 192, 96),
    'b_cyan': (192, 480, 192, 96),
    'b_white': (384, 480, 192, 96),
}
PAVE_X = (-1.2, 1.2)
PAVE_Z = (-0.8, 0.8)

# ----------------------------------------------------------------------------- uv helpers (also used by the model)


def uv_px(x, y):
    return (x / W, 1.0 - y / W)


COLS = {name: (i % 32, i // 32) for i, name in enumerate(ORDER)}


def uv(cell, f, g):
    """UV inside a 32px palette cell (cell = name or (col, row)); 2px inset."""
    col, row = COLS[cell] if isinstance(cell, str) else cell
    span = CELL - 4.0
    return uv_px(col * CELL + 2.0 + f * span, CELL_Y0 + row * CELL + 2.0 + g * span)


def ruv(name, a, b):
    """UV inside a region. a = 0..1 along the region's u (left -> right), b = 0..1 along v (top -> bottom)."""
    x0, y0, w, h = REGION[name]
    return uv_px(x0 + 1.0 + a * (w - 2.0), y0 + 1.0 + b * (h - 2.0))


def pave_uv(x, z):
    a = (x - PAVE_X[0]) / (PAVE_X[1] - PAVE_X[0])
    b = (z - PAVE_Z[0]) / (PAVE_Z[1] - PAVE_Z[0])
    return ruv('pave', min(max(a, 0.0), 1.0), min(max(b, 0.0), 1.0))


def pave_px(x, z):
    """Pixel position inside the pavement region (0..576, 0..384)."""
    return ((x - PAVE_X[0]) / (PAVE_X[1] - PAVE_X[0]) * 576.0, (z - PAVE_Z[0]) / (PAVE_Z[1] - PAVE_Z[0]) * 384.0)


# ----------------------------------------------------------------------------- generic drawing helpers
SS = 4   # supersampling factor for line art


def _lowfreq(rng, n, size):
    a = rng.random((n, n)).astype('float32')
    im = Image.fromarray((a * 255).astype('uint8')).resize((size[1], size[0]), Image.BICUBIC)
    return np.asarray(im).astype('float32') / 255.0


def _ss(w, h, bg=(0, 0, 0, 0)):
    return Image.new('RGBA', (w * SS, h * SS), bg)


def _down(layer):
    return layer.resize((layer.width // SS, layer.height // SS), Image.LANCZOS)


def _composite(img, layer):
    return Image.alpha_composite(img.convert('RGBA'), layer).convert('RGB')


def _noise(arr, rng, s=2.5):
    arr = arr + rng.normal(0, s, arr.shape[:2] + (1,))
    return Image.fromarray(np.clip(arr, 0, 255).astype('uint8'))


def _glow(img, x, y, r, col, strength=1.0):
    """Soft additive light pool on an RGB image (x, y, r in pixels)."""
    a = np.asarray(img).astype('float32')
    h, w = a.shape[:2]
    ii, jj = np.meshgrid(np.arange(w), np.arange(h))
    d = np.sqrt((ii - x) ** 2 + (jj - y) ** 2) / max(r, 1)
    k = np.clip(1.0 - d, 0, 1) ** 2 * strength
    a = a * (1 - 0.55 * k[..., None]) + np.array(col, 'float32') * 0.75 * k[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype('uint8'))


# ----------------------------------------------------------------------------- pavement
def _crack(d, rng, x, y, ang, length, width, depth=0):
    pts = [(x * SS, y * SS)]
    for _ in range(int(length / 6) + 1):
        ang += rng.normal(0, 0.45)
        x += math.cos(ang) * rng.uniform(4, 9); y += math.sin(ang) * rng.uniform(4, 9)
        pts.append((x * SS, y * SS))
        if depth < 2 and rng.random() < 0.12:
            _crack(d, rng, x, y, ang + rng.choice([-1, 1]) * rng.uniform(0.5, 1.1), length * 0.5, max(width - 1, 1), depth + 1)
    d.line([(px + SS, py + SS) for px, py in pts], fill=(255, 250, 240, 70), width=int(width * SS * 0.6), joint='curve')
    d.line(pts, fill=(22, 20, 20, 235), width=int(width * SS), joint='curve')


def _pavement(glows):
    w, h = 576, 384
    rng = np.random.default_rng(1017)
    base = np.zeros((h, w, 3), 'float32'); base[:] = (176, 170, 160)
    g = _lowfreq(rng, 9, (h, w)); g2 = _lowfreq(rng, 40, (h, w))
    base *= (0.86 + 0.20 * g + 0.08 * g2)[..., None]
    base[..., 2] *= 0.97
    img = Image.fromarray(np.clip(base, 0, 255).astype('uint8'))
    # large stains: oil with a faint rainbow rim, dark wet patch
    layer = _ss(w, h); d = ImageDraw.Draw(layer)
    for cx, cy, rx, ry in ((130, 270, 60, 34), (390, 300, 44, 26), (470, 110, 36, 22), (230, 90, 30, 18)):
        d.ellipse([(cx - rx) * SS, (cy - ry) * SS, (cx + rx) * SS, (cy + ry) * SS], fill=(40, 36, 40, 120))
        d.ellipse([(cx - rx * 0.62) * SS, (cy - ry * 0.62) * SS, (cx + rx * 0.62) * SS, (cy + ry * 0.62) * SS], fill=(60, 30, 90, 70))
        d.arc([(cx - rx) * SS, (cy - ry) * SS, (cx + rx) * SS, (cy + ry) * SS], 200, 330, fill=(80, 200, 160, 110), width=2 * SS)
    layer = _down(layer).filter(ImageFilter.GaussianBlur(3.0))
    img = _composite(img, layer)
    # expansion joints (slab edges about 0.8 m)
    layer = _ss(w, h); d = ImageDraw.Draw(layer)
    for ux in (w / 3, 2 * w / 3):
        d.line([(ux * SS, 0), (ux * SS, h * SS)], fill=(255, 250, 240, 90), width=4 * SS)
        d.line([(ux * SS, 0), (ux * SS, h * SS)], fill=(30, 28, 28, 220), width=2 * SS)
    d.line([(0, h / 2 * SS), (w * SS, h / 2 * SS)], fill=(255, 250, 240, 90), width=4 * SS)
    d.line([(0, h / 2 * SS), (w * SS, h / 2 * SS)], fill=(30, 28, 28, 220), width=2 * SS)
    for x, y, a, ln in ((w / 3, 40, 0.5, 90), (w / 3, 300, -0.6, 110), (2 * w / 3, 150, 2.4, 100), (2 * w / 3, 330, -2.6, 70),
                        (90, h / 2, 1.2, 100), (300, h / 2, -1.0, 80), (480, h / 2, 0.9, 120), (210, 150, 0.2, 60),
                        (430, 190, 2.8, 70), (40, 60, 0.9, 60)):
        _crack(d, rng, x, y, a, ln, 1.8)
    layer = _down(layer).filter(ImageFilter.GaussianBlur(0.5))
    img = _composite(img, layer)
    layer = _ss(w, h); d = ImageDraw.Draw(layer)
    # the ironic 'Parking Corral' (blue box with a scooter pictogram) that the pile is nowhere near
    bx0, by0, bx1, by1 = 28, 262, 190, 362
    d.rectangle([bx0 * SS, by0 * SS, bx1 * SS, by1 * SS], fill=(30, 100, 190, 235))
    d.rectangle([(bx0 + 5) * SS, (by0 + 5) * SS, (bx1 - 5) * SS, (by1 - 5) * SS], outline=(245, 245, 240, 255), width=4 * SS)
    cx, cy = (bx0 + bx1) / 2, (by0 + by1) / 2
    wh = (245, 245, 240, 255)
    for dx in (-44, 40):                                    # wheels
        d.ellipse([(cx + dx - 11) * SS, (cy + 20 - 11) * SS, (cx + dx + 11) * SS, (cy + 20 + 11) * SS], outline=wh, width=5 * SS)
    d.line([((cx - 44) * SS, (cy + 20) * SS), ((cx + 40) * SS, (cy + 20) * SS)], fill=wh, width=5 * SS)      # deck
    d.line([((cx + 40) * SS, (cy + 20) * SS), ((cx + 28) * SS, (cy - 26) * SS)], fill=wh, width=5 * SS)       # stem
    d.line([((cx + 16) * SS, (cy - 26) * SS), ((cx + 40) * SS, (cy - 26) * SS)], fill=wh, width=5 * SS)       # bars
    # chalk: sun with a smiley, hopscotch, a stick figure (pink, yellow, sky blue)
    for (x0, y0), col in (((250, 300), (255, 120, 190, 215)), ((250, 322), (255, 120, 190, 215)), ((250, 344), (255, 120, 190, 215))):
        d.rectangle([x0 * SS, y0 * SS, (x0 + 22) * SS, (y0 + 22) * SS], outline=col, width=2 * SS)
    d.rectangle([272 * SS, 322 * SS, 294 * SS, 344 * SS], outline=(255, 120, 190, 215), width=2 * SS)
    d.rectangle([228 * SS, 322 * SS, 250 * SS, 344 * SS], outline=(255, 120, 190, 215), width=2 * SS)
    sx, sy = 340, 336
    d.ellipse([(sx - 14) * SS, (sy - 14) * SS, (sx + 14) * SS, (sy + 14) * SS], outline=(255, 226, 60, 225), width=3 * SS)
    for k in range(12):
        a = k * math.pi / 6
        d.line([((sx + 19 * math.cos(a)) * SS, (sy + 19 * math.sin(a)) * SS), ((sx + 28 * math.cos(a)) * SS, (sy + 28 * math.sin(a)) * SS)],
               fill=(255, 226, 60, 225), width=3 * SS)
    d.ellipse([(sx - 6) * SS, (sy - 5) * SS, (sx - 3) * SS, (sy - 2) * SS], fill=(255, 226, 60, 225))
    d.ellipse([(sx + 3) * SS, (sy - 5) * SS, (sx + 6) * SS, (sy - 2) * SS], fill=(255, 226, 60, 225))
    d.arc([(sx - 7) * SS, (sy - 4) * SS, (sx + 7) * SS, (sy + 7) * SS], 20, 160, fill=(255, 226, 60, 225), width=2 * SS)
    fx, fy = 440, 346
    sky = (110, 200, 255, 225)
    d.ellipse([(fx - 6) * SS, (fy - 38) * SS, (fx + 6) * SS, (fy - 26) * SS], outline=sky, width=2 * SS)
    d.line([(fx * SS, (fy - 26) * SS), (fx * SS, (fy - 6) * SS)], fill=sky, width=2 * SS)
    d.line([((fx - 12) * SS, (fy - 20) * SS), ((fx + 12) * SS, (fy - 24) * SS)], fill=sky, width=2 * SS)
    d.line([(fx * SS, (fy - 6) * SS), ((fx - 9) * SS, (fy + 12) * SS)], fill=sky, width=2 * SS)
    d.line([(fx * SS, (fy - 6) * SS), ((fx + 9) * SS, (fy + 12) * SS)], fill=sky, width=2 * SS)
    layer = _down(layer)
    arr = np.asarray(layer).astype('float32')
    # weather the paint and chalk: knock back alpha with fine grit
    grit = np.clip(_lowfreq(rng, 70, (h, w)) * 1.5 - 0.15, 0, 1)
    arr[..., 3] *= (0.55 + 0.45 * grit)
    img = _composite(img, Image.fromarray(np.clip(arr, 0, 255).astype('uint8'), 'RGBA'))
    # gum, butts, jacaranda blossoms, leaves, bird mess
    layer = _ss(w, h); d = ImageDraw.Draw(layer)
    for _ in range(60):
        x, y = rng.uniform(0, w), rng.uniform(0, h); r = rng.uniform(1.2, 3.0)
        col = rng.choice([0, 0, 0, 1, 2])
        c = ((70, 66, 64, 225), (255, 130, 190, 235), (240, 240, 232, 235))[col]
        d.ellipse([(x - r) * SS, (y - r * 0.8) * SS, (x + r) * SS, (y + r * 0.8) * SS], fill=c)
    for _ in range(14):
        x, y = rng.uniform(0, w), rng.uniform(0, h); a = rng.uniform(0, 3)
        d.line([(x * SS, y * SS), ((x + 6 * math.cos(a)) * SS, (y + 6 * math.sin(a)) * SS)], fill=(236, 230, 214, 255), width=2 * SS)
        d.line([((x + 6 * math.cos(a)) * SS, (y + 6 * math.sin(a)) * SS), ((x + 8 * math.cos(a)) * SS, (y + 8 * math.sin(a)) * SS)], fill=(240, 130, 30, 255), width=2 * SS)
    for _ in range(150):
        x, y = rng.uniform(0, w), rng.uniform(0, h); r = rng.uniform(1.5, 3.2)
        d.ellipse([(x - r) * SS, (y - r) * SS, (x + r) * SS, (y + r) * SS], fill=(158, 82, 220, 215) if rng.random() < 0.8 else (200, 150, 245, 220))
    for _ in range(22):
        x, y = rng.uniform(0, w), rng.uniform(0, h); r = rng.uniform(3, 6)
        d.ellipse([(x - r) * SS, (y - r * 0.55) * SS, (x + r) * SS, (y + r * 0.55) * SS],
                  fill=((222, 140, 30, 235), (196, 70, 30, 235), (120, 150, 40, 235))[int(rng.integers(0, 3))])
    for _ in range(5):
        x, y = rng.uniform(20, w - 20), rng.uniform(20, h - 20)
        d.ellipse([(x - 6) * SS, (y - 3) * SS, (x + 6) * SS, (y + 3) * SS], fill=(250, 250, 244, 230))
        d.ellipse([(x - 2) * SS, (y - 1) * SS, (x + 2) * SS, (y + 1) * SS], fill=(40, 40, 40, 240))
    img = _composite(img, _down(layer))
    # LED light pools
    for gx, gz, gr, col in glows:
        px, py = pave_px(gx, gz)
        img = _glow(img, px, py, gr / (PAVE_X[1] - PAVE_X[0]) * w, col)
    arr = np.asarray(img).astype('float32')
    # darker edge frame so the slab reads against the ground
    ee = np.zeros((h, w), 'float32'); ee[:5, :] = 1; ee[-5:, :] = 1; ee[:, :5] = 1; ee[:, -5:] = 1
    arr *= (1 - 0.25 * ee[..., None])
    return _noise(arr, rng, 3.0)


# ----------------------------------------------------------------------------- chain-link fence
def _fence():
    w, h = 448, 224
    rng = np.random.default_rng(2)
    t = np.zeros((h, w, 3), 'float32'); t[:] = (30, 34, 40)
    img = Image.fromarray(t.astype('uint8'))
    p = 15.0
    layer = _ss(w, h); d = ImageDraw.Draw(layer)
    n = int(w / p) + int(h / p) + 4
    for k in range(-n, n):
        x = k * p
        d.line([(x * SS, 0), ((x + h) * SS, h * SS)], fill=(120, 124, 132, 255), width=int(4.2 * SS))
        d.line([((x + 90) * SS, 0), ((x + 90 - h) * SS, h * SS)], fill=(120, 124, 132, 255), width=int(4.2 * SS))
    for k in range(-n, n):
        x = k * p
        d.line([(x * SS, 0), ((x + h) * SS, h * SS)], fill=(205, 210, 218, 255), width=int(2.4 * SS))
        d.line([((x + 90) * SS, 0), ((x + 90 - h) * SS, h * SS)], fill=(226, 230, 236, 255), width=int(2.4 * SS))
    img = _composite(img, _down(layer))
    arr = np.asarray(img).astype('float32')
    g = _lowfreq(rng, 12, (h, w))
    rustm = np.clip((_lowfreq(rng, 6, (h, w)) - 0.55) * 5, 0, 1)
    arr = arr * (1 - 0.65 * rustm[..., None]) + np.array([150, 80, 40], 'float32') * 0.65 * rustm[..., None] * (0.6 + 0.6 * g[..., None])
    arr *= (0.78 + 0.35 * g)[..., None]
    img = Image.fromarray(np.clip(arr, 0, 255).astype('uint8'))
    layer = _ss(w, h); d = ImageDraw.Draw(layer)
    # torn hole near the lower right where a handlebar punched through (dark gap with curled cut wires)
    hx, hy = 330, 150
    d.ellipse([(hx - 34) * SS, (hy - 22) * SS, (hx + 34) * SS, (hy + 22) * SS], fill=(18, 20, 24, 255))
    for k in range(14):
        a = k * 2 * math.pi / 14 + rng.normal(0, 0.1)
        rr = rng.uniform(26, 42)
        d.arc([(hx + math.cos(a) * 30 - 7) * SS, (hy + math.sin(a) * 18 - 7) * SS, (hx + math.cos(a) * 30 + 7) * SS, (hy + math.sin(a) * 18 + 7) * SS],
              0, 280, fill=(214, 218, 226, 255), width=int(2.2 * SS))
    # plastic bags caught in the mesh: bright pink, yellow and white, with crinkle lines
    for bx, by, bw, bh, col in ((70, 32, 46, 38, (255, 90, 170, 235)), (205, 120, 36, 44, (250, 220, 40, 235)),
                                 (400, 40, 36, 44, (240, 244, 250, 235)), (40, 150, 42, 34, (80, 220, 255, 225))):
        pts = [(bx + rng.uniform(-3, 3), by), (bx + bw * 0.5, by + rng.uniform(-6, 2)), (bx + bw + rng.uniform(-3, 3), by + 4),
               (bx + bw * 0.9, by + bh * 0.6), (bx + bw * 0.6, by + bh), (bx + bw * 0.2, by + bh * 0.8), (bx, by + bh * 0.4)]
        d.polygon([(px * SS, py * SS) for px, py in pts], fill=col)
        for _ in range(5):
            cx0, cy0 = bx + rng.uniform(0, bw), by + rng.uniform(0, bh)
            d.line([(cx0 * SS, cy0 * SS), ((cx0 + rng.uniform(-9, 9)) * SS, (cy0 + rng.uniform(5, 14)) * SS)], fill=(255, 255, 255, 120), width=SS)
    # a purple scarf and a sock, because of course
    d.line([(150 * SS, 0), (162 * SS, 50 * SS), (150 * SS, 98 * SS)], fill=(150, 60, 220, 240), width=9 * SS, joint='curve')
    for k in range(5):
        d.line([(146 * SS, (8 + k * 20) * SS), (166 * SS, (8 + k * 20) * SS)], fill=(255, 230, 60, 230), width=3 * SS)
    img = _composite(img, _down(layer))
    layer = _ss(w, h); d = ImageDraw.Draw(layer)
    d.rectangle([(1) * SS, 0, (w - 1) * SS, 7 * SS], fill=(150, 154, 162, 255))              # top rail
    d.rectangle([(1) * SS, (h - 8) * SS, (w - 1) * SS, h * SS], fill=(130, 134, 142, 255))   # bottom rail
    d.rectangle([0, 0, 7 * SS, h * SS], fill=(150, 154, 162, 255))                           # post edges
    d.rectangle([(w - 7) * SS, 0, w * SS, h * SS], fill=(150, 154, 162, 255))
    img = _composite(img, _down(layer))
    arr = np.asarray(img).astype('float32')
    return _noise(arr, rng, 2.0)


# ----------------------------------------------------------------------------- stickers, qr, wheel, tread, dash
def _sticker(i):
    w, h = 112, 96
    rng = np.random.default_rng(300 + i)
    layer = _ss(w, h)
    d = ImageDraw.Draw(layer)
    cx, cy = 56, 48
    d.ellipse([(cx - 44) * SS, (cy - 44) * SS, (cx + 44) * SS, (cy + 44) * SS], fill=(250, 250, 244, 255))     # die-cut white border
    if i == 0:                                                                                                    # smiley
        d.ellipse([(cx - 40) * SS, (cy - 40) * SS, (cx + 40) * SS, (cy + 40) * SS], fill=(255, 222, 24, 255), outline=(40, 30, 10, 255), width=3 * SS)
        for ex in (-14, 14):
            d.ellipse([(cx + ex - 5) * SS, (cy - 18) * SS, (cx + ex + 5) * SS, (cy - 2) * SS], fill=(30, 24, 10, 255))
        d.arc([(cx - 24) * SS, (cy - 14) * SS, (cx + 24) * SS, (cy + 26) * SS], 20, 160, fill=(30, 24, 10, 255), width=4 * SS)
    elif i == 1:                                                                                                  # lightning bolt
        d.ellipse([(cx - 40) * SS, (cy - 40) * SS, (cx + 40) * SS, (cy + 40) * SS], fill=(120, 50, 220, 255))
        bolt = [(cx + 6, cy - 36), (cx - 20, cy + 4), (cx - 2, cy + 4), (cx - 10, cy + 36), (cx + 22, cy - 8), (cx + 4, cy - 8)]
        d.polygon([(x * SS, y * SS) for x, y in bolt], fill=(255, 240, 40, 255), outline=(30, 10, 60, 255))
    elif i == 2:                                                                                                  # heart
        d.ellipse([(cx - 40) * SS, (cy - 40) * SS, (cx + 40) * SS, (cy + 40) * SS], fill=(40, 190, 240, 255))
        d.ellipse([(cx - 28) * SS, (cy - 24) * SS, (cx + 2) * SS, (cy + 6) * SS], fill=(255, 60, 110, 255))
        d.ellipse([(cx - 2) * SS, (cy - 24) * SS, (cx + 28) * SS, (cy + 6) * SS], fill=(255, 60, 110, 255))
        d.polygon([((cx - 27) * SS, (cy - 2) * SS), ((cx + 27) * SS, (cy - 2) * SS), (cx * SS, (cy + 30) * SS)], fill=(255, 60, 110, 255))
    else:                                                                                                         # starburst
        d.ellipse([(cx - 40) * SS, (cy - 40) * SS, (cx + 40) * SS, (cy + 40) * SS], fill=(255, 120, 20, 255))
        pts = []
        for k in range(10):
            a = k * math.pi / 5 - math.pi / 2; r = 34 if k % 2 == 0 else 15
            pts.append(((cx + r * math.cos(a)) * SS, (cy + r * math.sin(a)) * SS))
        d.polygon(pts, fill=(255, 250, 120, 255), outline=(120, 40, 0, 255))
    img = Image.new('RGBA', (w * SS, h * SS), (58, 54, 50, 255))
    img = Image.alpha_composite(img, layer)
    img = _down(img).convert('RGB')
    # sticker wear: scratches, grime
    arr = np.asarray(img).astype('float32')
    g = _lowfreq(rng, 6, (h, w))
    arr *= (0.88 + 0.12 * g)[..., None]
    im = _noise(arr, rng, 3.0)
    dd = ImageDraw.Draw(im)
    for _ in range(4):
        x0, y0 = int(rng.integers(10, 80)), int(rng.integers(10, 80)); dd.line([(x0, y0), (x0 + int(rng.integers(8, 30)), y0 + int(rng.integers(-4, 5)))], fill=(235, 235, 230), width=1)
    return im


def _qr():
    w = h = 96
    rng = np.random.default_rng(55)
    t = np.zeros((h, w, 3), 'uint8'); t[:] = (238, 238, 232)
    m = 21; c = 3.6; off = 10
    grid = (rng.random((m, m)) < 0.5)
    for ox, oy in ((0, 0), (m - 7, 0), (0, m - 7)):
        grid[oy:oy + 7, ox:ox + 7] = True; grid[oy + 1:oy + 6, ox + 1:ox + 6] = False; grid[oy + 2:oy + 5, ox + 2:ox + 5] = True
        grid[max(oy - 1, 0):oy + 8, max(ox - 1, 0):ox + 8] |= False
    for j in range(m):
        for i in range(m):
            if grid[j, i]:
                x0, y0 = int(off + i * c), int(off + j * c)
                t[y0:y0 + int(c) + 1, x0:x0 + int(c) + 1] = (14, 14, 18)
    # lime frame: this is where you "scan to unlock"
    t[:4, :] = LIME; t[-4:, :] = LIME; t[:, :4] = LIME; t[:, -4:] = LIME
    img = Image.fromarray(t)
    arr = np.asarray(img).astype('float32') * (0.88 + 0.12 * _lowfreq(rng, 5, (h, w)))[..., None]
    return _noise(arr, rng, 2.5)


def _wheel():
    w = h = 96
    rng = np.random.default_rng(66)
    c = (w - 1) / 2.0
    ii, jj = np.meshgrid(np.arange(w), np.arange(h))
    dx, dy = ii - c, jj - c
    r = np.sqrt(dx ** 2 + dy ** 2) / (0.48 * w)      # 1.0 = outer edge of the fan (0.88 of the wheel radius)
    th = np.arctan2(dy, dx)
    t = np.zeros((h, w, 3), 'float32'); t[:] = (30, 30, 34)
    side = (r > 0.74)
    ribs = 0.5 + 0.5 * np.sin(th * 24)
    t[side] = (30 + 16 * ribs[side])[:, None] * np.array([1, 1, 1.05])
    rim = (r <= 0.74) & (r > 0.26)
    spoke = np.cos(th * 5) > 0.15
    t[rim & spoke] = (186, 192, 200)
    t[rim & ~spoke] = (44, 46, 52)
    t[(r > 0.66) & (r <= 0.74)] = (150, 156, 164)
    hub = r <= 0.26
    t[hub] = (214, 218, 226)
    for k in range(4):
        a = k * math.pi / 2 + 0.4
        bx, by = 0.15 * math.cos(a), 0.15 * math.sin(a)
        d2 = np.sqrt((dx / (0.48 * w) - bx) ** 2 + (dy / (0.48 * w) - by) ** 2)
        t[d2 < 0.035] = (40, 42, 48)
    t[(r < 0.05)] = (60, 62, 68)
    t[r > 1.02] = (24, 24, 26)
    t *= (0.88 + 0.12 * _lowfreq(rng, 6, (h, w)))[..., None]
    # a hint of lime on the spokes: scooters share paint with their wheels
    return _noise(t, rng, 2.5)


def _tread():
    w, h = 128, 48
    rng = np.random.default_rng(77)
    t = np.zeros((h, w, 3), 'float32'); t[:] = (28, 28, 30)
    ii, jj = np.meshgrid(np.arange(w), np.arange(h))
    groove = (np.sin((ii + abs(jj - h / 2) * 1.2) * 2 * math.pi / 8) > 0.55)
    t[groove] = (14, 14, 16)
    dirt = np.clip(_lowfreq(rng, 6, (h, w)) * 1.2, 0, 1)
    t = t * (1 - 0.45 * dirt[..., None]) + np.array([120, 104, 84], 'float32') * 0.45 * dirt[..., None] * 0.6
    t[:3, :] *= 1.4
    return _noise(t, rng, 2.5)


def _dash():
    w, h = 128, 48
    rng = np.random.default_rng(88)
    t = np.zeros((h, w, 3), 'float32'); t[:] = (20, 22, 26)
    img = Image.fromarray(t.astype('uint8'))
    layer = _ss(w, h); d = ImageDraw.Draw(layer)
    d.rounded_rectangle([14 * SS, 8 * SS, 114 * SS, 40 * SS], radius=6 * SS, fill=(8, 12, 14, 255), outline=(70, 74, 82, 255), width=2 * SS)
    # battery icon: nearly empty, one green bar (it still says it has range, it does not)
    d.rectangle([28 * SS, 15 * SS, 84 * SS, 33 * SS], outline=(120, 255, 70, 255), width=2 * SS)
    d.rectangle([84 * SS, 21 * SS, 88 * SS, 27 * SS], fill=(120, 255, 70, 255))
    d.rectangle([32 * SS, 19 * SS, 42 * SS, 29 * SS], fill=(150, 255, 80, 255))
    for k in range(1, 4):
        d.rectangle([(32 + k * 14) * SS, 19 * SS, (42 + k * 14) * SS, 29 * SS], outline=(40, 70, 36, 255), width=1 * SS)
    d.ellipse([(98 - 4) * SS, (24 - 4) * SS, (98 + 4) * SS, (24 + 4) * SS], fill=(150, 255, 80, 255))
    img = _composite(img, _down(layer))
    arr = np.asarray(img).astype('float32')
    return _noise(arr, rng, 1.5)


# ----------------------------------------------------------------------------- cone, grip, body panels
def _cone():
    w, h = 128, 192
    rng = np.random.default_rng(48)
    hh = 1.0 - np.linspace(0, 1, h)[:, None]
    t = np.zeros((h, w, 3), 'float32'); t[:] = (255, 96, 0)
    t *= (1.04 - 0.10 * hh)[..., None]
    for lo, hi in ((0.60, 0.80), (0.31, 0.46)):
        m = np.clip((hh - lo) / 0.012, 0, 1) * np.clip((hi - hh) / 0.012, 0, 1)
        collar = np.array([248, 248, 242], 'float32') * (1 + 0.08 * rng.normal(0, 0.5, (h, w, 1)))
        t = t * (1 - m[..., None]) + collar * m[..., None]
    g = _lowfreq(rng, 8, (h, w))
    foot = np.clip(1.0 - hh * 3.4, 0, 1)
    dirt = np.clip(g * 0.6 + foot * 0.9, 0, 1)
    t *= (1.0 - 0.38 * dirt)[..., None]
    t += (dirt * 10)[..., None] * np.array([1.0, 0.6, -0.5], 'float32')
    img = Image.fromarray(np.clip(t, 0, 255).astype('uint8'))
    layer = _ss(w, h); d = ImageDraw.Draw(layer)
    for off in (0, 6):
        d.arc([(10 + off) * SS, (120 + off) * SS, (110 + off) * SS, (220 + off) * SS], 200, 300, fill=(18, 18, 20, 150), width=4 * SS)
    d.line([(88 * SS, 70 * SS), (112 * SS, 100 * SS)], fill=(24, 22, 20, 120), width=3 * SS)
    # smiley sticker on the top collar
    sx, sy, r = 42, 66, 11
    d.ellipse([(sx - r) * SS, (sy - r) * SS, (sx + r) * SS, (sy + r) * SS], fill=(250, 214, 20, 255), outline=(40, 30, 10, 255), width=SS)
    d.ellipse([(sx - 5) * SS, (sy - 5) * SS, (sx - 2) * SS, (sy - 1) * SS], fill=(30, 24, 10, 255))
    d.ellipse([(sx + 2) * SS, (sy - 5) * SS, (sx + 5) * SS, (sy - 1) * SS], fill=(30, 24, 10, 255))
    d.arc([(sx - 6) * SS, (sy - 3) * SS, (sx + 6) * SS, (sy + 6) * SS], 20, 160, fill=(30, 24, 10, 255), width=SS)
    img = _composite(img, _down(layer))
    arr = np.asarray(img).astype('float32')
    tip = np.clip((hh - 0.93) / 0.02, 0, 1)
    arr = arr * (1 - 0.5 * tip[..., None]) + np.array([70, 28, 0], 'float32') * 0.5 * tip[..., None]
    return _noise(arr, rng, 2.5)


def _grip():
    w, h = 288, 96
    rng = np.random.default_rng(99)
    t = np.zeros((h, w, 3), 'float32'); t[:] = (30, 30, 32)
    grit = rng.random((h, w)) > 0.82
    t[grit] = (96, 96, 100)
    ii, jj = np.meshgrid(np.arange(w), np.arange(h))
    worn = np.clip((_lowfreq(rng, 5, (h, w)) - 0.5) * 3, 0, 1)
    t = t * (1 - 0.35 * worn[..., None]) + np.array([150, 148, 140], 'float32') * 0.35 * worn[..., None] * 0.5
    img = Image.fromarray(np.clip(t, 0, 255).astype('uint8'))
    layer = _ss(w, h); d = ImageDraw.Draw(layer)
    # bootprints: two sole shapes, a gum blob, a peeled corner
    for ox, oy, ang in ((60, 48, 0.0), (160, 40, 0.15)):
        d.rounded_rectangle([(ox - 22) * SS, (oy - 12) * SS, (ox + 22) * SS, (oy + 12) * SS], radius=6 * SS, fill=(170, 160, 140, 90))
        for k in range(5):
            d.line([((ox - 16 + k * 8) * SS, (oy - 10) * SS), ((ox - 16 + k * 8) * SS, (oy + 10) * SS)], fill=(30, 30, 32, 120), width=2 * SS)
    d.ellipse([230 * SS, 56 * SS, 246 * SS, 68 * SS], fill=(255, 140, 200, 235))
    img = _composite(img, _down(layer))
    arr = np.asarray(img).astype('float32')
    return _noise(arr, rng, 3.0)


def _body(name, seed, base):
    w, h = 192, 96
    rng = np.random.default_rng(seed)
    t = np.zeros((h, w, 3), 'float32'); t[:] = base
    vv = np.linspace(0, 1, h)[:, None]
    t *= (1.07 - 0.20 * vv)[..., None]
    g = _lowfreq(rng, 8, (h, w))
    dirt = np.clip(g * (0.25 + 0.9 * vv), 0, 1)
    t *= (1 - 0.40 * dirt)[..., None]
    t += (dirt * 18)[..., None] * np.array([1.0, 0.6, -0.8], 'float32')
    mud = np.clip((_lowfreq(rng, 14, (h, w)) - 0.62) * 6, 0, 1) * vv
    t = t * (1 - 0.5 * mud[..., None]) + np.array([90, 70, 44], 'float32') * 0.5 * mud[..., None]
    img = Image.fromarray(np.clip(t, 0, 255).astype('uint8'))
    layer = _ss(w, h); d = ImageDraw.Draw(layer)
    for _ in range(14):
        x0, y0 = rng.uniform(0, w), rng.uniform(2, h - 2); ln = rng.uniform(8, 36)
        d.line([(x0 * SS, y0 * SS), ((x0 + ln) * SS, (y0 + rng.uniform(-3, 3)) * SS)],
               fill=(36, 34, 30, 110) if rng.random() < 0.55 else (255, 255, 250, 130), width=int(rng.uniform(1, 2.2) * SS))
    for _ in range(3):                           # black rubber scuff marks from other scooters
        x0, y0 = rng.uniform(10, w - 40), rng.uniform(10, h - 10)
        d.line([(x0 * SS, y0 * SS), ((x0 + 28) * SS, (y0 + 6) * SS)], fill=(16, 16, 18, 150), width=5 * SS)
    d.rectangle([0, 0, w * SS, 2 * SS], fill=(255, 255, 255, 60))
    img = _composite(img, _down(layer).filter(ImageFilter.GaussianBlur(0.4)))
    arr = np.asarray(img).astype('float32')
    return _noise(arr, rng, 2.5)


def _tile(name, seed):
    base, grime, scratch, _ = PALETTE[name]
    rng = np.random.default_rng(seed)
    t = np.zeros((CELL, CELL, 3), 'float32'); t[:] = base
    t *= np.linspace(1.08, 0.92, CELL)[:, None, None]
    g = _lowfreq(rng, 5, (CELL, CELL))
    t *= (1.0 - grime * 0.5 * g)[..., None]
    t += rng.normal(0, 4 if grime > 0 else 0, (CELL, CELL, 1))
    img = Image.fromarray(np.clip(t, 0, 255).astype('uint8'))
    d = ImageDraw.Draw(img)
    for _ in range(int(8 * scratch) + (1 if scratch > 0 else 0)):
        y = int(rng.integers(0, CELL)); x0 = int(rng.integers(0, CELL)); ln = int(rng.integers(6, 24))
        d.line([(x0, y), (x0 + ln, y)], fill=(235,) * 3 if rng.random() < 0.5 else (22,) * 3, width=1)
    return img


def paint(out_png, glows=()):
    atlas = Image.new('RGB', (W, W), (110, 110, 110))
    rough = np.full((W, W), 0.55, 'float32')

    def put(name, img, r):
        x0, y0, w, h = REGION[name]
        atlas.paste(img, (x0, y0)); rough[y0:y0 + h, x0:x0 + w] = r

    put('pave', _pavement(glows), 0.92)
    put('fence', _fence(), 0.45)
    for i in range(4):
        put('st%d' % i, _sticker(i), 0.25)
    put('qr', _qr(), 0.30)
    put('wheel', _wheel(), 0.45)
    put('tread', _tread(), 0.88)
    put('dash', _dash(), 0.20)
    put('cone', _cone(), 0.42)
    put('grip', _grip(), 0.95)
    put('b_lime', _body('lime', 11, LIME), 0.38)
    put('b_cyan', _body('cyan', 12, CYAN), 0.38)
    put('b_white', _body('white', 13, WHITE), 0.40)
    for i, name in enumerate(ORDER):
        col, row = COLS[name]
        atlas.paste(_tile(name, 400 + i), (col * CELL, CELL_Y0 + row * CELL))
        rough[CELL_Y0 + row * CELL:CELL_Y0 + (row + 1) * CELL, col * CELL:(col + 1) * CELL] = PALETTE[name][3]
    atlas.save(out_png)
    return rough


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
