"""Build labelled contact sheets of icon candidates for cheap visual review.

python tools_comfy_sheets.py --dir work/comfy-icons --per-sheet 16 [--glob "Spell_*_[ab].png"] [--cell 256]
Writes <dir>/sheet_01.png ... and <dir>/sheets.json (list of the file names on each sheet, row-major, 4 columns).
"""
import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dir', required=True)
    ap.add_argument('--per-sheet', type=int, default=16)
    ap.add_argument('--glob', default='Spell_*_[a-z].png')
    ap.add_argument('--cell', type=int, default=256)
    a = ap.parse_args()
    d = Path(a.dir)
    files = sorted(p for p in d.glob(a.glob) if not p.name.startswith('scene_'))
    sheets = []
    cols = 4
    for s in range(0, len(files), a.per_sheet):
        chunk = files[s:s + a.per_sheet]
        rows = (len(chunk) + cols - 1) // cols
        sheet = Image.new('RGB', (cols * a.cell, rows * (a.cell + 18)), (20, 20, 20))
        draw = ImageDraw.Draw(sheet)
        for i, p in enumerate(chunk):
            x, y = (i % cols) * a.cell, (i // cols) * (a.cell + 18)
            sheet.paste(Image.open(p).convert('RGB').resize((a.cell, a.cell), Image.Resampling.LANCZOS), (x, y + 18))
            draw.text((x + 3, y + 3), p.stem.replace('Spell_', ''), fill=(255, 255, 0))
        name = f'sheet_{s // a.per_sheet + 1:02d}.png'
        sheet.save(d / name)
        sheets.append({'sheet': name, 'files': [p.name for p in chunk]})
    (d / 'sheets.json').write_text(json.dumps(sheets, indent=1), encoding='utf-8')
    print(len(files), 'images,', len(sheets), 'sheets')


if __name__ == '__main__':
    main()
