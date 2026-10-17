"""Texture atlas painter for the Caltrans 'LANE CLOSED AHEAD' barricade (512x512), AI-generated procedural art.

Layout (pixels, origin top-left):
  (  0,  0)-(512, 80)   rail front sheeting, top rail     (u along the rail, orange/white 45 degree stripes)
  (  0, 80)-(512,160)   rail front sheeting, middle rail
  (  0,160)-(512,240)   rail front sheeting, bottom rail
  (  0,240)-(512,320)   rail back sheeting
  (  0,320)-(192,352)   post / brace stripes (u along the bar)
  (192,320)-(384,352)   foot bar stripes
  (  0,352)-(192,448)   sandbag (planar from above)
  (192,352)-(384,384)   amber lamp lens (u around, v rim -> hot top)
  (384,320)-(512,512)   traffic cone (u around, v tip -> base)
  (  0,448)-(384,512)   12 x 2 small 32px palette cells
paint(out_png) writes the base colour PNG (BM) and returns (cells, rough) where rough is a 512x512 float map used by
paint_pm(). Lettering is deliberately absent (BG3 mirrors the DAE, so text would need an in-game check).
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W = 512
CELL = 32
CELL_Y0 = 448

ORANGE = np.array([255, 112, 0], 'float32')
WHITE = np.array([248, 248, 242], 'float32')

# name: (base RGB, grime 0-1, scratch 0-1, rough 0-1)
PALETTE = {
    'orange':        ((255, 100, 0), 0.30, 0.20, 0.45),
    'orange_dark':   ((214, 78, 0), 0.40, 0.20, 0.50),
    'white':         ((236, 236, 228), 0.30, 0.15, 0.40),
    'rubber':        ((34, 33, 35), 0.35, 0.10, 0.85),
    'rubber_grey':   ((72, 72, 74), 0.45, 0.20, 0.85),
    'housing_yel':   ((250, 196, 20), 0.25, 0.20, 0.40),
    'housing_blk':   ((24, 24, 26), 0.20, 0.10, 0.50),
    'bolt':          ((150, 152, 156), 0.50, 0.40, 0.35),
    'rope':          ((176, 150, 104), 0.45, 0.00, 0.90),
    'rust':          ((130, 76, 44), 0.55, 0.30, 0.80),
}
ORDER = list(PALETTE)
REGION = {
    'front0': (0, 0, 512, 80),
    'front1': (0, 80, 512, 80),
    'front2': (0, 160, 512, 80),
    'back': (0, 240, 512, 80),
    'bar': (0, 320, 192, 32),
    'foot': (192, 320, 192, 32),
    'bag': (0, 352, 192, 96),
    'lens': (192, 352, 192, 32),
    'cone': (384, 320, 128, 192),
}
# world size (metres) each region spans, used to keep stripes at 45 degrees
RAIL_LEN, RAIL_H = 2.20, 0.156


def _lowfreq(rng, n, size):
    a = rng.random((n, n)).astype('float32')
    im = Image.fromarray((a * 255).astype('uint8')).resize((size[1], size[0]), Image.BICUBIC)
    return np.asarray(im).astype('float32') / 255.0


def _stripes(w, h, mx, my, period, phase, down=True):
    """Soft 0..1 mask (1 = orange) of 45 degree stripes. mx, my = metres per pixel along u and v."""
    ii, jj = np.meshgrid(np.arange(w) * mx, np.arange(h) * my)
    s = (ii + (jj if down else -jj)) / period + phase
    t = s - np.floor(s)
    eps = 1.2 * mx / period
    a = np.clip((0.5 - t) / eps + 0.5, 0, 1)        # falling edge at 0.5
    b = np.clip(t / eps, 0, 1)                      # rising edge at 0
    return np.minimum(a, b)


def _prism(w, h, strength, rng):
    """Retro-reflective microprism sparkle: fine staggered diamond pattern."""
    ii, jj = np.meshgrid(np.arange(w), np.arange(h))
    d = 0.5 + 0.5 * np.sin(ii * 1.9) * np.sin(jj * 1.9 + (ii // 2 % 2) * 1.5)
    return (1.0 + strength * (d - 0.5)) + rng.normal(0, strength * 0.35, (h, w))


def _splat(layer_draw, rng, w, h, count, color, rmin, rmax, y_bias=0.0):
    for _ in range(count):
        x = int(rng.integers(0, w)); y = int(h * (rng.random() ** (1.0 + y_bias)))
        r = int(rng.integers(rmin, rmax + 1))
        layer_draw.ellipse([x - r, y - r // 2, x + r, y + r // 2], fill=color)


def _scribble(d, rng, x0, y0, w, h, color, width=2, strokes=5):
    """A marker 'tag': a few looping strokes, no letters."""
    for _ in range(strokes):
        pts = []
        x, y = x0 + rng.random() * w * 0.2, y0 + rng.random() * h
        for _ in range(7):
            pts.append((x, y))
            x += rng.uniform(w * 0.06, w * 0.2)
            y = y0 + rng.random() * h
        d.line(pts, fill=color, width=width, joint='curve')


def _flyer(img, rng, x, y, fw, fh):
    d = ImageDraw.Draw(img, 'RGBA')
    d.rectangle([x + 2, y + 2, x + fw + 2, y + fh + 2], fill=(0, 0, 0, 60))
    d.rectangle([x, y, x + fw, y + fh], fill=(244, 240, 214, 255))
    d.rectangle([x, y, x + fw, y + 4], fill=(212, 40, 40, 255))              # headline bar
    ly = y + 8
    while ly < y + fh - 5:
        ln = int(rng.integers(fw // 3, fw - 8))
        d.line([(x + 4, ly), (x + 4 + ln, ly)], fill=(60, 60, 70, 255), width=1)
        ly += 4
    for tx in (x - 3, x + fw - 8):                                           # tape
        d.rectangle([tx, y - 2, tx + 11, y + 4], fill=(222, 214, 150, 200))


def _smiley(img, cx, cy, r, face=(30, 30, 30, 255), bg=(250, 214, 20, 255), flat=True):
    d = ImageDraw.Draw(img, 'RGBA')
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=bg, outline=(40, 40, 30, 255))
    e = max(1, r // 4)
    d.ellipse([cx - r // 2 - e // 2, cy - r // 3 - e, cx - r // 2 + e // 2 + 1, cy - r // 3 + e], fill=face)
    d.ellipse([cx + r // 2 - e // 2, cy - r // 3 - e, cx + r // 2 + e // 2 + 1, cy - r // 3 + e], fill=face)
    if flat:
        d.line([(cx - r // 2, cy + r // 2), (cx + r // 2, cy + r // 2)], fill=face, width=max(1, r // 6))
    else:
        d.arc([cx - r // 2, cy, cx + r // 2, cy + r // 2 + 2], 20, 160, fill=face, width=max(1, r // 6))


def _rail(seed, variant, back):
    """Reflective sheeting on a plastic rail: 45 degree stripes, border, grime, scuffs and a bit of life."""
    w, h = 512, 80
    rng = np.random.default_rng(seed)
    mx, my = RAIL_LEN / w, RAIL_H / h
    m = _stripes(w, h, mx, my, 0.30, 0.13 * variant + (0.5 if back else 0.0))
    orange = ORANGE * (1.0 - 0.06 * np.linspace(0, 1, h)[:, None, None])
    t = orange * m[..., None] + WHITE * (1 - m[..., None])
    t = t * _prism(w, h, 0.07, rng)[..., None]
    g = _lowfreq(rng, 10, (h, w))
    vv = np.linspace(0, 1, h)[:, None]
    dirt = np.clip(g * (0.35 + 0.9 * vv) * (1.15 if back is False else 0.7), 0, 1)
    t *= (1.0 - 0.27 * dirt)[..., None]
    t += (dirt * 10)[..., None] * np.array([1.0, 0.7, -0.5], 'float32')
    # traffic-film haze (exhaust) as a broad pale-grey veil, a touch heavier on the front
    t = t * (1 - 0.03 * g[..., None]) + np.array([60, 58, 55], 'float32') * 0.03 * g[..., None]
    img = Image.fromarray(np.clip(t, 0, 255).astype('uint8'))
    layer = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    # mud splatter, heaviest at the bottom edge and on the lowest rail
    _splat(d, rng, w, h, 70 if variant == 2 else 28, (92, 64, 36, 150), 1, 4, y_bias=-0.6)
    # long scuffs where traffic grazed it
    for _ in range(9):
        x0 = int(rng.integers(0, w - 60)); y0 = int(rng.integers(4, h - 4)); ln = int(rng.integers(20, 90))
        d.line([(x0, y0), (x0 + ln, y0 + int(rng.integers(-3, 4)))],
               fill=(30, 28, 26, 90) if rng.random() < 0.6 else (250, 250, 245, 110), width=int(rng.integers(1, 3)))
    layer = layer.filter(ImageFilter.GaussianBlur(0.8))
    img = Image.alpha_composite(img.convert('RGBA'), layer).convert('RGB')
    if not back:
        if variant == 0:       # marker tag on the right, silver sticker on the left
            d2 = ImageDraw.Draw(img, 'RGBA')
            _scribble(d2, rng, 330, 12, 120, 54, (12, 12, 16, 235), width=3, strokes=4)
            d2.ellipse([396, 18, 410, 32], outline=(12, 12, 16, 235), width=2)
            _smiley(img, 70, 40, 15, flat=False)
        elif variant == 1:     # taped-up flyer and a bumper sticker
            _flyer(img, rng, 120, 14, 48, 54)
            d2 = ImageDraw.Draw(img, 'RGBA')
            d2.rectangle([360, 26, 440, 52], fill=(34, 90, 170, 255), outline=(240, 240, 240, 255))
            d2.line([(366, 39), (434, 39)], fill=(250, 214, 20, 255), width=3)
            d2.ellipse([396, 31, 408, 47], fill=(232, 40, 40, 255))
        else:                  # boot print, cracked bottom corner
            d2 = ImageDraw.Draw(img, 'RGBA')
            for k in range(4):
                d2.rounded_rectangle([280 + k * 17, 38 + (k % 2) * 3, 292 + k * 17, 56 + (k % 2) * 3], 4, fill=(70, 50, 30, 120))
            d2.line([(470, 70), (484, 54), (480, 44), (498, 30)], fill=(30, 28, 26, 190), width=1)
    else:
        d2 = ImageDraw.Draw(img, 'RGBA')
        _scribble(d2, rng, 60, 20, 100, 40, (20, 20, 24, 150), width=2, strokes=2)
    arr = np.asarray(img).astype('float32')
    # plastic frame: a lighter lip all around with a darker moulded groove just inside it
    fr = np.zeros((h, w), 'float32')
    fr[:3, :] = 1; fr[-3:, :] = 1; fr[:, :3] = 1; fr[:, -3:] = 1
    arr = np.where(fr[..., None] > 0, arr * 0.62 + np.array([88, 34, 0], 'float32'), arr)
    arr[3:5, :, :] *= 0.72; arr[-5:-3, :, :] *= 0.72; arr[:, 3:5, :] *= 0.72; arr[:, -5:-3, :] *= 0.72
    arr += rng.normal(0, 2.5, (h, w, 1))
    return Image.fromarray(np.clip(arr, 0, 255).astype('uint8'))


def _bars(seed, w, h, length_m, width_m, period, phase):
    rng = np.random.default_rng(seed)
    m = _stripes(w, h, length_m / w, width_m / h, period, phase)
    t = ORANGE * m[..., None] + WHITE * (1 - m[..., None])
    g = _lowfreq(rng, 8, (h, w))
    t *= (1 - 0.30 * g * np.linspace(0.3, 1.0, w)[None, :])[..., None]
    t *= _prism(w, h, 0.05, rng)[..., None]
    img = Image.fromarray(np.clip(t, 0, 255).astype('uint8'))
    d = ImageDraw.Draw(img, 'RGBA')
    for _ in range(5):
        x0 = int(rng.integers(0, w - 40)); y0 = int(rng.integers(2, h - 2)); ln = int(rng.integers(12, 40))
        d.line([(x0, y0), (x0 + ln, y0)], fill=(30, 28, 26, 100), width=1)
    arr = np.asarray(img).astype('float32') + rng.normal(0, 2.5, (h, w, 1))
    return Image.fromarray(np.clip(arr, 0, 255).astype('uint8'))


def _bag(seed):
    """Sandbag canvas planar from above (192 x 96): woven tan, water stain, stitched end seams and a marker face."""
    w, h = 192, 96
    rng = np.random.default_rng(seed)
    t = np.zeros((h, w, 3), 'float32'); t[:] = (214, 184, 124)
    g = _lowfreq(rng, 7, (h, w))
    t *= (1.0 - 0.36 * g)[..., None]
    ii, jj = np.meshgrid(np.arange(w), np.arange(h))
    weave = 0.5 + 0.5 * np.sin(ii * 2 * np.pi / 2.6) * np.sin(jj * 2 * np.pi / 2.6)
    t *= (0.88 + 0.12 * weave)[..., None]
    wet = np.clip((_lowfreq(rng, 4, (h, w)) - 0.55) * 4, 0, 1)
    t = t * (1 - 0.35 * wet[..., None]) + np.array([86, 66, 40], 'float32') * 0.35 * wet[..., None]
    img = Image.fromarray(np.clip(t, 0, 255).astype('uint8'))
    d = ImageDraw.Draw(img, 'RGBA')
    for x in (5, w - 6):                      # sewn end seams with cross-stitches
        d.line([(x, 0), (x, h)], fill=(90, 70, 44, 255), width=1)
        for y in range(2, h, 5):
            d.line([(x - 3, y), (x + 3, y + 2)], fill=(70, 54, 34, 255), width=1)
    for _ in range(3):                        # spilled-sand dusting
        cx, cy = int(rng.integers(20, w - 20)), int(rng.integers(8, h - 8))
        d.ellipse([cx - 12, cy - 5, cx + 12, cy + 5], fill=(226, 204, 150, 70))
    _smiley(img, 96, 44, 17, face=(24, 20, 16, 255), bg=(0, 0, 0, 0), flat=True)
    arr = np.asarray(img).astype('float32') + rng.normal(0, 3, (h, w, 1))
    return Image.fromarray(np.clip(arr, 0, 255).astype('uint8'))


def _lens():
    """Amber lamp lens (192 x 32): v runs top -> rim. Glows hot at the crown, deep orange-amber at the rim."""
    w, h = 192, 32
    rng = np.random.default_rng(77)
    vv = np.linspace(0, 1, h)[:, None]          # 0 = crown, 1 = rim
    uu = np.linspace(0, 1, w)[None, :]
    crown = np.array([255, 246, 168], 'float32'); mid = np.array([255, 178, 0], 'float32'); rim = np.array([255, 128, 0], 'float32')
    k = np.clip(vv * 2.2, 0, 1)[..., None]
    t = crown * (1 - k) + mid * k
    k2 = np.clip((vv - 0.8) * 4, 0, 1)[..., None]
    t = t * (1 - k2) + rim * k2
    facets = 0.5 + 0.5 * np.cos(uu * 2 * np.pi * 6)          # moulded lens ribs
    t = t * (0.93 + 0.07 * facets[..., None])
    t = np.broadcast_to(t, (h, w, 3)).copy()
    t += rng.normal(0, 2, (h, w, 1))
    return Image.fromarray(np.clip(t, 0, 255).astype('uint8'))


def _cone(seed):
    """Traffic cone (128 x 192): u around, v tip (0) -> base (1). Orange body, two retro-reflective collars."""
    w, h = 128, 192
    rng = np.random.default_rng(seed)
    hh = 1.0 - np.linspace(0, 1, h)[:, None]    # 0 = base ... 1 = tip
    body = np.array([255, 96, 0], 'float32')
    t = np.zeros((h, w, 3), 'float32'); t[:] = body
    t *= (1.04 - 0.10 * hh)[..., None]
    for lo, hi in ((0.60, 0.80), (0.31, 0.46)):  # collars: top (6 in), lower (4 in)
        m = np.clip((hh - lo) / 0.012, 0, 1) * np.clip((hi - hh) / 0.012, 0, 1)
        collar = WHITE * _prism(w, h, 0.09, rng)[..., None]
        t = t * (1 - m[..., None]) + collar * m[..., None]
    g = _lowfreq(rng, 8, (h, w))
    uu = np.linspace(0, 1, w)[None, :]
    foot = np.clip(1.0 - hh * 3.4, 0, 1)         # road grime rising from the base
    dirt = np.clip(g * 0.6 + foot * 0.9, 0, 1)
    t *= (1.0 - 0.38 * dirt)[..., None]
    t += (dirt * 10)[..., None] * np.array([1.0, 0.6, -0.5], 'float32')
    img = Image.fromarray(np.clip(t, 0, 255).astype('uint8'))
    layer = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    # tyre kiss: two dark parallel curves low on the cone, plus a long scrape
    for off in (0, 6):
        d.arc([10 + off, 120 + off, 110 + off, 220 + off], 200, 300, fill=(18, 18, 20, 150), width=4)
    d.line([(88, 70), (112, 100)], fill=(24, 22, 20, 120), width=3)
    d.line([(20, 90), (52, 96)], fill=(255, 220, 190, 90), width=2)
    layer = layer.filter(ImageFilter.GaussianBlur(0.9))
    img = Image.alpha_composite(img.convert('RGBA'), layer).convert('RGB')
    _smiley(img, 42, 66, 11, flat=True)          # a little yellow sticker on the top collar
    # the very tip is a darker moulded cap
    arr = np.asarray(img).astype('float32')
    tip = np.clip((hh - 0.93) / 0.02, 0, 1)
    arr = arr * (1 - 0.5 * tip[..., None]) + np.array([70, 28, 0], 'float32') * 0.5 * tip[..., None]
    arr += rng.normal(0, 2.5, (h, w, 1))
    return Image.fromarray(np.clip(arr, 0, 255).astype('uint8'))


def _tile(name, seed):
    base, grime, scratch, _ = PALETTE[name]
    rng = np.random.default_rng(seed)
    t = np.zeros((CELL, CELL, 3), 'float32'); t[:] = base
    t *= np.linspace(1.08, 0.92, CELL)[:, None, None]
    g = _lowfreq(rng, 5, (CELL, CELL))
    t *= (1.0 - grime * 0.5 * g)[..., None]
    t += rng.normal(0, 4, (CELL, CELL, 1))
    img = Image.fromarray(np.clip(t, 0, 255).astype('uint8'))
    d = ImageDraw.Draw(img)
    for _ in range(int(8 * scratch) + (1 if scratch > 0 else 0)):
        y = int(rng.integers(0, CELL)); x0 = int(rng.integers(0, CELL)); ln = int(rng.integers(6, 24))
        d.line([(x0, y), (x0 + ln, y)], fill=(235,) * 3 if rng.random() < 0.5 else (22,) * 3, width=1)
    return img


def paint(out_png):
    atlas = Image.new('RGB', (W, W), (110, 110, 110))
    rough = np.full((W, W), 0.55, 'float32')

    def put(name, img, r):
        x0, y0, w, h = REGION[name]
        atlas.paste(img, (x0, y0)); rough[y0:y0 + h, x0:x0 + w] = r

    put('front0', _rail(41, 0, False), 0.28)
    put('front1', _rail(42, 1, False), 0.28)
    put('front2', _rail(43, 2, False), 0.30)
    put('back', _rail(44, 1, True), 0.36)
    put('bar', _bars(45, 192, 32, 0.9, 0.07, 0.20, 0.05), 0.40)
    put('foot', _bars(46, 192, 32, 0.6, 0.10, 0.20, 0.35), 0.45)
    put('bag', _bag(47), 0.97)
    put('lens', _lens(), 0.12)
    put('cone', _cone(48), 0.40)
    cells = {}
    for i, name in enumerate(ORDER):
        col, row = i % 12, i // 12
        atlas.paste(_tile(name, 400 + i), (col * CELL, CELL_Y0 + row * CELL))
        rough[CELL_Y0 + row * CELL:CELL_Y0 + (row + 1) * CELL, col * CELL:(col + 1) * CELL] = PALETTE[name][3]
        cells[name] = (col, row)
    atlas.save(out_png)
    return cells, rough


def pm_image(rough):
    """Physical map: R metal (0), G roughness, B 255, A 255 (same channel order as the cart's flat PM (0,200,255,255))."""
    small = np.asarray(Image.fromarray((np.clip(rough, 0, 1) * 255).astype('uint8')).resize((256, 256), Image.BILINEAR)).astype('float32')
    g = 70 + small * (235 - 70) / 255.0 * 1.0                       # rough 0..1 -> 70..235
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
    return uv_px(x0 + 1.0 + a * (w - 2.0), y0 + 1.0 + b * (h - 2.0))
