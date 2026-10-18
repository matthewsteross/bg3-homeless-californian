"""Clone the receipt-scroll prop pipeline into a new Meshy prop (lead tool; saves Codex budget).

Usage (from the project folder):
  python make_prop.py --key hotdog --name HotDogCart --src assets/meshy/hotdog --spell HC_Shout_X \
      --height 1.4 --title "Bacon-Wrapped Cart" --desc "One sentence of flavour." [--angle 0] [--run]

It copies hc_receipt.py, validation/test_receipt.py, assets/models/HC_ReceiptScroll/*.py and work/receipt/run.{sh,py}
with the names swapped, sets the target height, rotation, title and description, and with --run executes
`bash work/<key>/run.sh v1` (needs Blender, Divine and texconv as for every other prop). Then wire
`from hc_<key> import generate_<key>` into generate_mod.py main() next to the other props and look at
work/<key>/out/preview_*_v1.png before shipping. Reject models with floating or missing geometry.
The new test patches the real built spell, so the spell must already exist in src (run build.py first).
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SPELL0, TITLE0, NAME0, KEY0 = 'HC_Shout_CVSReceiptScroll', 'Endless Pharmacy Receipt', 'ReceiptScroll', 'receipt'


def swap(text, a):
    text = text.replace(SPELL0, '@@SPELL@@').replace(TITLE0, '@@TITLE@@')
    text = re.sub(r"(item_desc = ')[^']*(')", lambda m: m.group(1) + '@@DESC@@' + m.group(2), text)
    text = text.replace(NAME0, a.name).replace(KEY0, a.key)
    text = text.replace('@@SPELL@@', a.spell).replace('@@TITLE@@', a.title).replace('@@DESC@@', a.desc)
    return text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--key', required=True)
    ap.add_argument('--name', required=True)
    ap.add_argument('--src', required=True, help='assets/meshy/<folder> with model.glb and the four textures')
    ap.add_argument('--spell', required=True)
    ap.add_argument('--height', type=float, required=True)
    ap.add_argument('--angle', type=float, default=0.0)
    ap.add_argument('--title', required=True)
    ap.add_argument('--desc', required=True)
    ap.add_argument('--run', action='store_true')
    a = ap.parse_args()
    for bad in ("'", '"', '\\', '\n'):
        if bad in a.title or bad in a.desc:
            sys.exit('title/description must not contain quotes or backslashes')
    if not (ROOT / a.src / 'model.glb').is_file():
        sys.exit(f'missing {a.src}/model.glb')
    jobs = {
        'hc_receipt.py': f'hc_{a.key}.py',
        'validation/test_receipt.py': f'validation/test_{a.key}.py',
        'assets/models/HC_ReceiptScroll/build_receipt_model.py': f'assets/models/HC_{a.name}/build_{a.key}_model.py',
        'assets/models/HC_ReceiptScroll/render_receipt.py': f'assets/models/HC_{a.name}/render_{a.key}.py',
        'work/receipt/run.sh': f'work/{a.key}/run.sh',
        'work/receipt/run.py': f'work/{a.key}/run.py',
    }
    for old, new in jobs.items():
        text = swap((ROOT / old).read_text(encoding='utf-8'), a)
        if old.endswith('build_receipt_model.py'):
            text = text.replace("parents[2] / 'meshy/" + a.key + "'", "parents[2] / 'meshy/" + Path(a.src).name + "'")
            text, n = re.subn(r'scale = [0-9.]+ / ', f'scale = {a.height} / ', text)
            text = re.sub(r'np\.deg2rad\([-0-9.]+\)', f'np.deg2rad({a.angle})', text)
            assert n == 1, 'height line not found'
        dest = ROOT / new
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding='utf-8', newline='\n')
        print('wrote', new)
    if a.run:
        sys.exit(subprocess.run(['C:/Program Files/Git/bin/bash.exe', f'work/{a.key}/run.sh', 'v1'], cwd=ROOT).returncode)


if __name__ == '__main__':
    main()
