"""Batch BG3 spell icons: scene via ComfyUI (Z-Image-Turbo), then composite our own frame (assets/icon_frame/frame_1024.png).

python tools_comfy_batch.py --scenes work/comfy-icons-scenes.json --variants 2 --out work/comfy-icons [--only Name Name]
Writes <out>/<IconName>_a.png, _b.png ... (final 1024 icons with frame) and <out>/scene_<IconName>_<k>.png (scene only).
Pick the best with `python work/save_icon.py <png> <IconName> "ComfyUI Z-Image-Turbo"` (that is what adds it to assets/icons).
"""
import argparse
import json
import random
import time
import urllib.parse
from pathlib import Path

from PIL import Image

import tools_comfy_icon as t

SCENE_STYLE = ("oil-painted dark fantasy illustration, dramatic colourful magical lighting, one clear central subject filling the scene, "
               "highly detailed, bold readable shapes")
# Same scene text gives near-identical images for every seed with Z-Image-Turbo, so each variant gets a different composition/lighting.
VARIANT_MODS = [
    'dramatic low-angle view, close to the subject',
    'wide establishing view showing the whole surroundings',
    'tight close-up on the key detail, shallow depth of field',
    'high overhead view looking down',
    'strong backlit silhouette against a glowing background',
    'neon-lit night scene with saturated purple and teal light',
    'warm golden-hour light with long shadows',
    'moody fog and rain with a single bright light source',
]
FRAME = Path(__file__).resolve().parent / 'assets' / 'icon_frame' / 'frame_1024.png'


def scene_image(scene, seed, name, mod=''):
    resp = t.post('/prompt', {'prompt': t.workflow(f'{scene}, {mod}. {SCENE_STYLE}' if mod else f'{scene}. {SCENE_STYLE}', seed, f'bg3icons/{name}')})
    pid = resp['prompt_id']
    for _ in range(300):
        hist = json.loads(t.get(f'/history/{pid}'))
        if pid in hist and hist[pid].get('outputs'):
            img = [i for n in hist[pid]['outputs'].values() for i in n.get('images', [])][0]
            q = urllib.parse.urlencode({'filename': img['filename'], 'subfolder': img['subfolder'], 'type': img['type']})
            from io import BytesIO
            return Image.open(BytesIO(t.get('/view?' + q))).convert('RGBA').resize((1024, 1024), Image.Resampling.LANCZOS)
        time.sleep(1.5)
    raise TimeoutError(name)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--scenes', required=True)
    ap.add_argument('--variants', type=int, default=2)
    ap.add_argument('--out', required=True)
    ap.add_argument('--only', nargs='*')
    ap.add_argument('--seed-offset', type=int, default=0)
    ap.add_argument('--diverse', action='store_true', help='give every variant a different composition/lighting modifier (recommended)')
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    scenes = json.loads(Path(a.scenes).read_text(encoding='utf-8'))
    frame = Image.open(FRAME).convert('RGBA')
    for icon, scene in scenes.items():
        if a.only and icon not in a.only:
            continue
        for k in range(a.variants):
            letter = chr(ord('a') + k + a.seed_offset)
            seed = random.randint(1, 2**31)
            img = scene_image(scene, seed, f'{icon}_{letter}', VARIANT_MODS[(k + a.seed_offset) % len(VARIANT_MODS)] if a.diverse else '')
            img.save(out / f'scene_{icon}_{letter}.png')
            img.alpha_composite(frame)
            img.convert('RGB').save(out / f'{icon}_{letter}.png')
            print(icon, letter, seed, flush=True)


if __name__ == '__main__':
    main()
