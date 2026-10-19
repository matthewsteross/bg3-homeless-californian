"""Generate BG3 spell icons with the local ComfyUI Desktop server (Z-Image-Turbo workflow).

python tools_comfy_icon.py --tsv work/icons-missing-2026-10-18.tsv --rows 2 5 9 --out work/comfy-tests
Images are saved by ComfyUI into its output/bg3icons/ subfolder and copied here via the HTTP API.
No icon is installed automatically: look at the results, then use work/save_icon.py to add good ones.
"""
import argparse
import json
import random
import time
import urllib.parse
import urllib.request
from pathlib import Path

SERVER = 'http://127.0.0.1:8188'
STYLE = ('square game spell icon, ornate embossed dark steel gothic fantasy frame with corner filigree and carved runes, '
         'dark painterly Baldur\'s Gate 3 style, dramatic colourful magical lighting, ONE clear central subject that shows the joke, '
         'highly detailed, legible at small size, no text, no letters, no watermark')


def workflow(prompt, seed, prefix):
    return {
        '1': {'class_type': 'UNETLoader', 'inputs': {'unet_name': 'z_image_turbo_bf16.safetensors', 'weight_dtype': 'default'}},
        '2': {'class_type': 'CLIPLoader', 'inputs': {'clip_name': 'qwen_3_4b.safetensors', 'type': 'lumina2', 'device': 'default'}},
        '3': {'class_type': 'VAELoader', 'inputs': {'vae_name': 'ae.safetensors'}},
        '4': {'class_type': 'ModelSamplingAuraFlow', 'inputs': {'model': ['1', 0], 'shift': 3}},
        '5': {'class_type': 'CLIPTextEncode', 'inputs': {'text': prompt, 'clip': ['2', 0]}},
        '6': {'class_type': 'ConditioningZeroOut', 'inputs': {'conditioning': ['5', 0]}},
        '7': {'class_type': 'EmptySD3LatentImage', 'inputs': {'width': 1024, 'height': 1024, 'batch_size': 1}},
        '8': {'class_type': 'KSampler', 'inputs': {'model': ['4', 0], 'seed': seed, 'steps': 8, 'cfg': 1, 'sampler_name': 'euler',
                                                   'scheduler': 'simple', 'positive': ['5', 0], 'negative': ['6', 0],
                                                   'latent_image': ['7', 0], 'denoise': 1}},
        '9': {'class_type': 'VAEDecode', 'inputs': {'samples': ['8', 0], 'vae': ['3', 0]}},
        '10': {'class_type': 'SaveImage', 'inputs': {'images': ['9', 0], 'filename_prefix': prefix}},
    }


def post(path, body):
    req = urllib.request.Request(SERVER + path, data=json.dumps(body).encode(), headers={'Content-Type': 'application/json'})
    return json.loads(urllib.request.urlopen(req, timeout=60).read())


def get(path):
    return urllib.request.urlopen(SERVER + path, timeout=60).read()


def generate(prompt, name, out_dir, seed=None):
    seed = seed if seed is not None else random.randint(1, 2**31)
    resp = post('/prompt', {'prompt': workflow(f'{prompt}. {STYLE}', seed, f'bg3icons/{name}')})
    pid = resp['prompt_id']
    for _ in range(300):
        hist = json.loads(get(f'/history/{pid}'))
        if pid in hist and hist[pid].get('outputs'):
            for node in hist[pid]['outputs'].values():
                for img in node.get('images', []):
                    q = urllib.parse.urlencode({'filename': img['filename'], 'subfolder': img['subfolder'], 'type': img['type']})
                    dest = Path(out_dir) / f'{name}.png'
                    dest.write_bytes(get('/view?' + q))
                    return dest, seed
        time.sleep(2)
    raise TimeoutError(name)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tsv', required=True)
    ap.add_argument('--rows', type=int, nargs='+', required=True, help='1-based data row numbers')
    ap.add_argument('--out', required=True)
    ap.add_argument('--scenes', help='JSON file {IconName: visual scene description}; overrides the TSV text (recommended)')
    a = ap.parse_args()
    Path(a.out).mkdir(parents=True, exist_ok=True)
    scenes = json.loads(Path(a.scenes).read_text(encoding='utf-8')) if a.scenes else {}
    lines = Path(a.tsv).read_text(encoding='utf-8').splitlines()[1:]
    for r in a.rows:
        icon, spell, title, desc = (lines[r - 1].split('\t') + ['', '', '', ''])[:4]
        scene = scenes.get(icon) or desc.split('. ')[0][:220]
        t0 = time.time()
        dest, seed = generate(scene, icon, a.out)
        print(f'{icon}: {dest} seed {seed} in {time.time()-t0:.0f}s')


if __name__ == '__main__':
    main()
