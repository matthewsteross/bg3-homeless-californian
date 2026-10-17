"""Original procedural 1024px colour atlas; flat NM and rough physical map.

No logos, lettering, particles or emissive lighting. All apparent soot/flame colour
is painted base colour. Usage is through build_coolerfire_model.py.
"""
from PIL import Image, ImageDraw
import numpy as np

PALETTE = {
    'foam': (238, 235, 213), 'inside': (37, 31, 39),
    'red': (215, 22, 40), 'steel': (156, 165, 177),
    'orange': (255, 82, 3), 'yellow': (255, 220, 22),
    'violet': (170, 28, 247), 'coal': (30, 34, 43),
    'bag': (218, 108, 28), 'fluid': (255, 196, 24),
    'sausage': (190, 66, 29), 'teal': (4, 159, 142),
    'strap': (27, 41, 53), 'lid': (240, 237, 220),
    'ember': (246, 52, 11), 'chip': (188, 182, 164),
}
NAMES = list(PALETTE)


def uv(name, u, v):
    i = NAMES.index(name)
    return ((i % 4 * 256 + 5 + u * 246) / 1024,
            1 - (i // 4 * 256 + 5 + (1 - v) * 246) / 1024)


def paint(directory):
    rng = np.random.default_rng(10172026)
    atlas = Image.new('RGB', (1024, 1024))
    for name, colour in PALETTE.items():
        i = NAMES.index(name)
        noise = rng.normal(0, 3 if name in ('orange', 'yellow', 'violet') else 7, (256, 256, 1))
        tile = Image.fromarray(np.uint8(np.clip(np.array(colour)[None, None, :] + noise, 0, 255)))
        d = ImageDraw.Draw(tile)
        if name in ('foam', 'lid'):
            for _ in range(380):
                x, y = map(int, rng.integers(0, 256, 2))
                r = int(rng.integers(1, 4))
                d.ellipse((x-r, y-r, x+r, y+r), outline=(210, 206, 188), width=1)
            for j in range(9):
                x = int(rng.integers(0, 256))
                d.line([(x, 0), (x+10, 25), (x-3, 48), (x+7, 63)], fill=(65, 51, 49), width=3)
            # Charred rim and blackened lower corners still leave most foam white.
            d.polygon([(0,0),(256,0),(256,10),(227,5),(201,24),(181,7),(143,15),(109,6),(62,25),(35,6),(0,17)], fill=(54,41,43))
            d.polygon([(0,256),(0,216),(17,232),(29,225),(40,256)], fill=(67,49,43))
        elif name == 'bag':
            d.rectangle((27, 45, 228, 209), fill=(28, 32, 38), outline=(248, 185, 67), width=7)
            for x, y in [(65,90),(118,75),(166,100),(86,151),(153,161)]:
                d.rounded_rectangle((x-23,y-17,x+23,y+17), radius=9, fill=(75,76,80), outline=(120,116,112), width=3)
        elif name == 'fluid':
            d.rectangle((18, 43, 238, 215), fill=(203, 29, 29), outline=(255,236,144), width=6)
            d.polygon([(126,65),(104,109),(107,134),(81,118),(75,160),(104,188),(145,193),(177,162),(164,128),(139,148),(147,103)], fill=(28,26,33))
        elif name == 'coal':
            for _ in range(9):
                x,y=map(int,rng.integers(0,256,2))
                d.line([(x,y),(x+36,y+16),(x+13,y+31)], fill=(74,72,79), width=3)
        elif name == 'teal':
            for y in range(20,256,40):
                d.line((0,y,256,y), fill=(7,109,107), width=3)
        elif name == 'sausage':
            for y in range(35,256,58):
                d.line((0,y,256,y+40), fill=(69,35,30), width=13)
        atlas.paste(tile, ((i % 4)*256,(i//4)*256))
    atlas.save(directory / 'HC_CoolerFire_BM.png')
    Image.new('RGB',(256,256),(128,128,255)).save(directory / 'HC_CoolerFire_NM.png')
    # Physical map convention matches the existing prop painters: metal=R,
    # roughness=G, ambient occlusion=B; deliberately rough styrofoam/fire shards.
    Image.new('RGB',(256,256),(0,210,255)).save(directory / 'HC_CoolerFire_PM.png')
