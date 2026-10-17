"""Meme sounds: swap the cast/hit sound events of chosen HC spells for funny vanilla ones.

Spells inherit their sounds from the vanilla donor they `using`. This post-step (called at the end of
generate_local_expansion in generate_mod.py) rewrites the `CastSound` / `TargetSound` / `PrepareSound` lines of the
spells named in hc_sound_map.json inside the generated Stats/Generated/Data/*.txt files. It never adds new audio:
every event name in the map must already be used as a sound field value in vanilla stats (validation/test_sounds.py
checks that against temp_race, all five layers), so the game already has the Wwise event.

Applying it twice gives the same result (existing lines for those fields are replaced, not duplicated).
UNVERIFIED in game: that each vanilla event is audible from this spell's cast animation without the donor's own
animation/VFX (events are plain Wwise event names, the same kind vanilla spells put in the same fields).
"""
import json
import re
from pathlib import Path

MAP_FILE = Path(__file__).with_name("hc_sound_map.json")
FIELDS = ("CastSound", "TargetSound", "PrepareSound")
_FIELD_LINE = re.compile(r'^data "(%s)" ' % "|".join(FIELDS))


def load_map(path=MAP_FILE):
    if not Path(path).is_file():
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def apply_sounds(public_dir, sound_map=None):
    """Rewrite sound fields for mapped spells; returns the number of spells changed."""
    sound_map = load_map() if sound_map is None else sound_map
    if not sound_map:
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
            if m and m.group(1) in sound_map and 'type "SpellData"' in part:
                sounds = sound_map[m.group(1)]
                blank_after = part.endswith(nl + nl)
                lines = part.split(nl)
                # drop existing lines for the fields we set, keep every other line
                lines = [ln for ln in lines if not (_FIELD_LINE.match(ln) and _FIELD_LINE.match(ln).group(1) in sounds)]
                while lines and lines[-1] == "":
                    lines.pop()
                for field in FIELDS:
                    if field in sounds:
                        lines.append(f'data "{field}" "{sounds[field]}"')
                part = nl.join(lines) + nl + (nl if blank_after else "")
                changed.add(m.group(1))
            out.append(part)
        new = "".join(out)
        if new != raw:
            path.write_bytes(new.encode("utf-8"))
    return len(changed)
