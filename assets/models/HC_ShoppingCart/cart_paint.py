"""Palette atlas painter for the Abandoned Cart (512x512, 8x8 grid of 64px cells).

Each cell is a flat palette colour with grime blotches, rust bloom and scratch streaks that run
along the U axis (the model maps U along each bar's length, so scratches follow the wire).
paint(out_png) writes the PNG and returns {cell_name: (col, row)}.
"""
import numpy as np
from PIL import Image, ImageDraw

W = 512
CELL = 64

# name: (base RGB, grime 0-1, rust 0-1, scratch 0-1)
PALETTE = {
    'chrome_clean': ((178, 184, 190), 0.25, 0.00, 0.55),
    'chrome_dirty': ((140, 144, 146), 0.60, 0.10, 0.45),
    'chrome_rusty': ((152, 134, 120), 0.60, 0.45, 0.35),
    'rust':         ((128, 72, 42), 0.50, 1.00, 0.20),
    'grip_red':     ((178, 30, 32), 0.40, 0.00, 0.30),
    'rubber':       ((38, 38, 40), 0.30, 0.00, 0.10),
    'plastic_grey': ((122, 126, 124), 0.55, 0.00, 0.25),
    'plastic_blue': ((62, 94, 144), 0.65, 0.00, 0.30),
    'zinc':         ((120, 126, 132), 0.40, 0.15, 0.40),
}
ORDER = list(PALETTE)


def _lowfreq(rng, n):
    a = rng.random((n, n)).astype('float32')
    im = Image.fromarray((a * 255).astype('uint8')).resize((CELL, CELL), Image.BICUBIC)
    return np.asarray(im).astype('float32') / 255.0


def _tile(name, seed):
    base, grime, rust, scratch = PALETTE[name]
    rng = np.random.default_rng(seed)
    t = np.zeros((CELL, CELL, 3), 'float32')
    t[:] = base
    # soft top-to-bottom shading so the cell is not dead flat
    t *= np.linspace(1.12, 0.88, CELL)[:, None, None]
    g = _lowfreq(rng, 6)
    t *= (1.0 - grime * 0.55 * g)[..., None]
    t += (grime * g)[..., None] * np.array([6.0, 2.0, -8.0])   # brown-ish dirt tint
    if rust > 0:
        r = _lowfreq(rng, 7)
        m = np.clip((r - (0.95 - rust * 0.5)) * 6.0, 0, 1)[..., None]
        rust_col = np.array([140.0, 70.0, 28.0]) * (0.7 + 0.3 * _lowfreq(rng, 12))[..., None]
        t = t * (1 - m) + rust_col * m
    t += rng.normal(0, 5.0, (CELL, CELL, 1))                      # fine grain
    img = Image.fromarray(np.clip(t, 0, 255).astype('uint8'))
    d = ImageDraw.Draw(img)
    for _ in range(int(14 * scratch) + 1):
        y = int(rng.integers(0, CELL)); x0 = int(rng.integers(0, CELL)); ln = int(rng.integers(10, 50))
        shade = 215 if rng.random() < 0.6 else 25
        d.line([(x0, y), (x0 + ln, y + int(rng.integers(-1, 2)))], fill=(shade,) * 3, width=1)
    arr = np.asarray(img).astype('float32')
    a2 = np.asarray(Image.fromarray(arr.astype('uint8')))
    # blend scratches back at partial strength so they read as light wear, not drawn lines
    out = np.clip(0.55 * a2 + 0.45 * np.clip(t, 0, 255), 0, 255).astype('uint8')
    return Image.fromarray(out)


def paint(out_png):
    atlas = Image.new('RGB', (W, W), (110, 110, 110))
    cells = {}
    for i, name in enumerate(ORDER):
        col, row = i % 8, i // 8
        atlas.paste(_tile(name, 100 + i), (col * CELL, row * CELL))
        cells[name] = (col, row)
    atlas.save(out_png)
    return cells


def uv(cell, f, g):
    """UV inside a cell. f runs along U (bar length), g along V; both 0..1; 4px inset."""
    col, row = cell
    inset = 4.0
    span = CELL - 2 * inset
    u = (col * CELL + inset + f * span) / W
    v = 1.0 - (row * CELL + inset + g * span) / W
    return (u, v)
