"""Texture atlas painter for the Blue Tarp Lean-To (512x512), AI-generated procedural art.

Layout (pixels, origin top-left):
  (  0,  0)-(256,256)  front tarp top      (u = along the ridge, v = ridge -> front edge)
  (256,  0)-(512,256)  rear  tarp top      (u = along the ridge, v = ridge -> rear edge)
  (  0,256)-(256,384)  front tarp underside
  (256,256)-(512,384)  rear  tarp underside
  (  0,384)-(512,512)  8 x 2 small 64px palette cells (rebar, rope, brass, brick, ...)
paint(out_png) writes the PNG and returns {cell_name: (col, row)} for the small cells.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W = 512
CELL = 64
CELL_Y0 = 384

# name: (base RGB, grime 0-1, rust 0-1, scratch 0-1)
PALETTE = {
    'rebar_rust':  ((118, 70, 44), 0.55, 1.00, 0.20),
    'rebar_dull':  ((96, 90, 84), 0.60, 0.35, 0.35),
    'brass':       ((176, 140, 62), 0.35, 0.00, 0.30),
    'grommet_dark': ((24, 22, 22), 0.20, 0.00, 0.00),
    'brick':       ((142, 68, 52), 0.55, 0.00, 0.10),
    'concrete':    ((132, 130, 124), 0.65, 0.00, 0.20),
    'zinc':        ((118, 124, 130), 0.40, 0.15, 0.40),
    'rope':        ((176, 150, 104), 0.45, 0.00, 0.00),
    'rope_dark':   ((120, 100, 70), 0.55, 0.00, 0.00),
}
ORDER = list(PALETTE)
REGION = {
    'top_front': (0, 0, 256, 256),
    'top_rear': (256, 0, 256, 256),
    'under_front': (0, 256, 256, 128),
    'under_rear': (256, 256, 256, 128),
}


def _lowfreq(rng, n, size):
    a = rng.random((n, n)).astype('float32')
    im = Image.fromarray((a * 255).astype('uint8')).resize((size[1], size[0]), Image.BICUBIC)
    return np.asarray(im).astype('float32') / 255.0


def _tile(name, seed):
    base, grime, rust, scratch = PALETTE[name]
    rng = np.random.default_rng(seed)
    t = np.zeros((CELL, CELL, 3), 'float32')
    t[:] = base
    t *= np.linspace(1.10, 0.90, CELL)[:, None, None]
    g = _lowfreq(rng, 6, (CELL, CELL))
    t *= (1.0 - grime * 0.55 * g)[..., None]
    t += (grime * g)[..., None] * np.array([6.0, 2.0, -8.0])
    if rust > 0:
        r = _lowfreq(rng, 7, (CELL, CELL))
        m = np.clip((r - (0.95 - rust * 0.5)) * 6.0, 0, 1)[..., None]
        rust_col = np.array([140.0, 70.0, 28.0]) * (0.7 + 0.3 * _lowfreq(rng, 12, (CELL, CELL)))[..., None]
        t = t * (1 - m) + rust_col * m
    t += rng.normal(0, 5.0, (CELL, CELL, 1))
    if name.startswith('rope'):
        # twisted strand: diagonal bands. U (rope length) runs across the cell, V around it.
        ii, jj = np.meshgrid(np.arange(CELL), np.arange(CELL))
        band = 0.5 + 0.5 * np.sin(2 * np.pi * (ii / 10.0 + jj / 21.3))
        t *= (0.62 + 0.38 * band)[..., None]
    img = Image.fromarray(np.clip(t, 0, 255).astype('uint8'))
    d = ImageDraw.Draw(img)
    for _ in range(int(14 * scratch) + (1 if scratch > 0 else 0)):
        y = int(rng.integers(0, CELL)); x0 = int(rng.integers(0, CELL)); ln = int(rng.integers(10, 50))
        shade = 215 if rng.random() < 0.6 else 25
        d.line([(x0, y), (x0 + ln, y + int(rng.integers(-1, 2)))], fill=(shade,) * 3, width=1)
    a2 = np.asarray(img).astype('float32')
    return Image.fromarray(np.clip(0.55 * a2 + 0.45 * np.clip(t, 0, 255), 0, 255).astype('uint8'))


def _tarp(seed, w, h, underside, patch):
    """Woven plastic tarp: faded blue, weave, creases, grime pooling toward the low edge (v = 1)."""
    rng = np.random.default_rng(seed)
    base = np.array([34, 74, 132] if underside else [42, 108, 190], 'float32')
    t = np.zeros((h, w, 3), 'float32'); t[:] = base
    vv = np.linspace(0, 1, h)[:, None]
    uu = np.linspace(0, 1, w)[None, :]
    # sun fade near the ridge, grime toward the low edge
    fade = np.clip(1.0 - vv * 1.6, 0, 1) * (0.10 if underside else 0.28)
    t = t * (1 - fade[..., None]) + np.array([150, 190, 230], 'float32') * fade[..., None]
    g = _lowfreq(rng, 9, (h, w))
    t *= (1.0 - 0.38 * g * (0.4 + 0.9 * vv))[..., None]
    t += (g * vv * 22)[..., None] * np.array([1.0, 0.7, -0.6], 'float32')
    # woven grid
    ii, jj = np.meshgrid(np.arange(w), np.arange(h))
    weave = 0.5 + 0.5 * np.sin(ii * 2 * np.pi / 3.0) * np.sin(jj * 2 * np.pi / 3.0)
    t *= (0.93 + 0.07 * weave)[..., None]
    img = Image.fromarray(np.clip(t, 0, 255).astype('uint8'))
    # creases and stains go on a separate RGBA layer that is blurred before compositing, so they read as soft folds
    layer = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for _ in range(14 if not underside else 8):
        x0 = int(rng.integers(0, w)); y0 = int(rng.integers(0, h)); ln = int(rng.integers(h // 4, h // 2))
        dx = int(rng.integers(-ln // 5, ln // 5 + 1))
        d.line([(x0, y0), (x0 + dx, y0 + ln)], fill=(215, 232, 248, 80), width=2)
        d.line([(x0 + 2, y0), (x0 + 2 + dx, y0 + ln)], fill=(8, 26, 64, 70), width=2)
    if not underside:
        for _ in range(7):   # rain streaks running to the low edge
            x0 = int(rng.integers(0, w)); y0 = int(rng.integers(0, h // 2)); ln = int(rng.integers(h // 4, h // 2))
            d.line([(x0, y0), (x0 + int(rng.integers(-3, 4)), y0 + ln)], fill=(80, 70, 48, 60), width=int(rng.integers(2, 5)))
        for _ in range(4):   # old puddle rings and bleach-spots
            cx, cy = int(rng.integers(20, w - 20)), int(rng.integers(h // 3, h - 20)); r = int(rng.integers(10, 26))
            d.ellipse([cx - r, cy - r // 2, cx + r, cy + r // 2], outline=(190, 205, 215, 75), width=2)
    layer = layer.filter(ImageFilter.GaussianBlur(1.3))
    img = Image.alpha_composite(img.convert('RGBA'), layer).convert('RGB')
    d = ImageDraw.Draw(img, 'RGBA')
    if not underside:
        if patch:  # duct-tape repair
            px, py = int(w * 0.30), int(h * 0.38)
            d.rectangle([px, py, px + 54, py + 22], fill=(150, 154, 156, 255))
            d.rectangle([px, py + 10, px + 54, py + 12], fill=(124, 128, 130, 255))
            d.line([(px + 2, py + 3), (px + 50, py + 4)], fill=(196, 199, 201, 255), width=1)
        else:    # a mended tear: dark slit with a few rope stitches
            sx, sy = int(w * 0.68), int(h * 0.50)
            d.line([(sx, sy), (sx + 8, sy + 26)], fill=(22, 44, 84, 255), width=2)
            for k in range(5):
                d.line([(sx - 3 + k, sy + 3 + k * 5), (sx + 7 + k, sy + 3 + k * 5)], fill=(176, 154, 110, 255), width=1)
    arr = np.asarray(img).astype('float32')
    arr += rng.normal(0, 3.5, (h, w, 1))
    # reinforced hem band (lighter, tighter weave) on the left, right and low edge of the region
    band = 7
    m = np.zeros((h, w), bool)
    m[:, :band] = True; m[:, -band:] = True; m[-band:, :] = True
    hem = arr * 0.78 + np.array([14, 18, 26], 'float32')
    arr = np.where(m[..., None], hem, arr)
    arr[-band - 1, :, :] *= 0.8
    return Image.fromarray(np.clip(arr, 0, 255).astype('uint8'))


def paint(out_png):
    atlas = Image.new('RGB', (W, W), (110, 110, 110))
    atlas.paste(_tarp(11, 256, 256, False, True), (0, 0))
    atlas.paste(_tarp(12, 256, 256, False, False), (256, 0))
    atlas.paste(_tarp(13, 256, 128, True, False), (0, 256))
    atlas.paste(_tarp(14, 256, 128, True, False), (256, 256))
    cells = {}
    for i, name in enumerate(ORDER):
        col, row = i % 8, i // 8
        atlas.paste(_tile(name, 300 + i), (col * CELL, CELL_Y0 + row * CELL))
        cells[name] = (col, row)
    atlas.save(out_png)
    return cells


def uv_px(x, y):
    return (x / W, 1.0 - y / W)


def uv(cell, f, g):
    """UV inside a small cell. f runs along U (bar length), g along V; both 0..1; 4px inset."""
    col, row = cell
    inset = 4.0
    span = CELL - 2 * inset
    return uv_px(col * CELL + inset + f * span, CELL_Y0 + row * CELL + inset + g * span)


def uv_region(name, a, r):
    """UV inside a tarp region. a = fraction along the ridge (0..1), r = fraction down the slope (0..1)."""
    x0, y0, w, h = REGION[name]
    return uv_px(x0 + a * (w - 1) + 0.5, y0 + r * (h - 1) + 0.5)
