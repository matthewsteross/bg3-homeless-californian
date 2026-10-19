"""Apply custom icons to any spell, passive or status by stat name (not only the HC_-prefixed ones).

assets/icons/icon_map.json maps a stat name (for example a vanilla-style name such as "Shout_SidewalkScramble") to an icon key
(e.g. "Spell_SidewalkScramble"). The icon PNG assets/icons/<key>.png makes build_icons.py add it to the atlas (hc_icon_keys.py
loads this same map), and this post-step (run at the end of generation, like hc_sounds.apply_sounds) rewrites the entry's
`Icon` field in the generated Stats/Generated/Data/*.txt. A key without a PNG is ignored, so the map can list future icons.
Applying it twice gives the same result.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MAP_FILE = ROOT / "assets" / "icons" / "icon_map.json"
ICON_DIR = ROOT / "assets" / "icons"
_TYPES = ('type "SpellData"', 'type "PassiveData"', 'type "StatusData"')


def load_map(path=MAP_FILE):
    if not Path(path).is_file():
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def apply_icons(public_dir, icon_map=None, icon_dir=ICON_DIR):
    """Set the Icon field of mapped entries whose PNG exists; returns how many entries were changed."""
    icon_map = load_map() if icon_map is None else icon_map
    usable = {n: k for n, k in icon_map.items() if (Path(icon_dir) / f"{k}.png").is_file()}
    if not usable:
        return 0
    data_dir = Path(public_dir) / "Stats" / "Generated" / "Data"
    changed = set()
    for path in sorted(data_dir.glob("*.txt")):
        raw = path.read_bytes().decode("utf-8")
        nl = "\r\n" if "\r\n" in raw else "\n"
        parts = re.split(r'(?m)^(?=new entry ")', raw)
        out = []
        for part in parts:
            m = re.match(r'new entry "([^"]+)"', part)
            if m and m.group(1) in usable and any(t in part for t in _TYPES):
                key = usable[m.group(1)]
                lines = part.split(nl)
                trailing_blank = part.endswith(nl + nl)
                while lines and lines[-1] == "":
                    lines.pop()
                lines = [ln for ln in lines if not ln.startswith('data "Icon" ')]
                lines.append(f'data "Icon" "{key}"')
                part = nl.join(lines) + nl + (nl if trailing_blank else "")
                changed.add(m.group(1))
            out.append(part)
        new = "".join(out)
        if new != raw:
            path.write_bytes(new.encode("utf-8"))
    return len(changed)
