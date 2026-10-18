"""Build the Nexus playtest ZIP (pak + package_readme.txt) and the Nexus update text (lead tool).

python make_release.py --version 0.5.0 --date 2026-10-18 --tests 848
Run after `python build.py` and the full test suite. Never installs anything into BG3.
"""
import argparse
import hashlib
import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'work/public-playtest'


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def counts():
    spells = statuses = passives = 0
    for p in (ROOT / 'src/HomelessCalifornian/Public/HomelessCalifornian/Stats/Generated/Data').glob('*.txt'):
        for m in re.finditer(r'new entry "(HC_[A-Za-z0-9_]+)"\s*\r?\ntype "(\w+)"', p.read_text(encoding='utf-8')):
            if m.group(2) == 'SpellData':
                spells += 1
            elif m.group(2) == 'StatusData':
                statuses += 1
            elif m.group(2) == 'PassiveData':
                passives += 1
    icons = len(list((ROOT / 'assets/icons').glob('Spell_*.png')))
    props = len(list((ROOT / 'assets/models').glob('HC_*/*_bounds.json')))
    return spells, statuses, passives, icons, props


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--version', required=True)
    ap.add_argument('--date', required=True)
    ap.add_argument('--tests', type=int, required=True)
    a = ap.parse_args()
    pak = ROOT / 'dist/HomelessCalifornian.pak'
    spells, statuses, passives, icons, models = counts()
    pak_sha = sha(pak)
    readme = f"""HOMELESS CALIFORNIAN - PLAYTEST {a.date} (v{a.version})

Intentionally overpowered, with normal actions, saves, Junk costs and rest
cooldowns. Not an attempt at vanilla balance. Windows PC installation is the
only installation tested so far. This is not a mod.io or console release.

INSTALL
Close BG3, extract HomelessCalifornian.pak from the ZIP, import the pak with
your usual PC BG3 mod manager, enable it and export your load order.
Do not install a duplicate copy. Use a separate test save. A new character or
respec is needed for new level grants on an existing character.
Everyone in co-op needs the same package and load order. Keep the mod installed
on saves that use its class/race; don't remove it mid-campaign casually.

WHAT'S IN IT
About {spells} spells, {statuses} statuses and {passives} passives. Four subclasses with something at every level 3-12
(they share a common core of spells and differ mildly). Dozens of custom 3D props
that your spells drop on the ground (about {models} Meshy-generated models plus earlier
hand-built ones), a Caltrans safety vest, new icons, and funnier vanilla sound
effects on every spell.

TEST STATUS
{a.tests} automated file-level tests and the pak validator pass. Only the earlier
v0.4.0 data was checked in game. Everything newer (the props spawning, their size
and facing, the new spells' numbers and targeting, the sounds, the new icons) is
UNTESTED in game. Expect rough edges; please report them.

BUG REPORTS
https://github.com/matthewsteross/bg3-homeless-californian/issues/new/choose
Please include game build/platform, level/subclass/multiclass, numbered steps,
expected versus actual result, mod list/load order, new character/respec and
reload details. Screenshots are welcome.

AI DISCLOSURE
Human-led design with Claude/Gemini/Codex/Grok code and writing assistance.
Spell icons were generated with Gemini and Codex image tools. The 3D props were
generated with Meshy (AI text-to-3D) and converted by our own scripts; earlier
props were built procedurally by AI-written code. Spell sounds reuse existing
vanilla sound events. No custom voice recordings.

PAK SHA256
{pak_sha}
"""
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'package_readme.txt').write_text(readme, encoding='utf-8', newline='\n')
    zip_path = OUT / f'HomelessCalifornian-Playtest-{a.date}-v{a.version}.zip'
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        z.write(pak, 'HomelessCalifornian.pak')
        z.write(OUT / 'package_readme.txt', 'package_readme.txt')
    zsha = sha(zip_path)
    nexus = f"""# Nexus update {a.version} ({a.date}) - what to enter

FILE: `work\\public-playtest\\{zip_path.name}`
- Size {zip_path.stat().st_size:,} bytes; ZIP SHA256 `{zsha}`
- PAK SHA256 `{pak_sha}`
Upload as UPDATE of the existing file (Files tab, "Update" on the previous row); file version `{a.version}`; tick "Update mod version".

## Changelog
{a.version} - {a.date}
- NEW: about {spells} spells now (up from 141): Round 11 and Round 12 base-class spells, four subclasses with a feature at every level 3-12, and a shared core of subclass spells.
- NEW: Round 12: ten "spell drops an object" Shouts at base levels 2-12 (federal mailbox, coin kiosk, burst hydrant, privacy pod, muffler totem, danger-dog cart, cybertruck husk, amber-alert trailer, taco truck, Walk of Fame slab).
- NEW: dozens of custom 3D props made with Meshy and converted by our scripts: dumpster (with a parody "Waste Mismanagement" logo), wardrobe, giant needle (4 m, level 7 Oversized Sharps Disposal), propane BBQ, hot bar, plexiglass aisle, therapy couch, mattress, podium and more; they despawn after about 60 seconds (in-game despawn untested).
- NEW: {icons} custom spell icons; every spell with a title now has a funnier vanilla sound event; Caltrans-themed jokes pass.
- Includes everything from 0.4.5.
- Status: {a.tests} automated tests and the pak validator pass. NOT play-tested beyond v0.4.0: props (spawning, size, facing, despawn), numbers, sounds and icons are untested in game.

## Description edits
- Status line -> "Honest status (v{a.version}, {a.date} build): about {spells} spells, dozens of custom 3D props, four subclasses with something every level. File-level verified; combat numbers, prop spawning, icons and sounds untested in game."
- AI disclosure: mention Meshy (3D props), Gemini and Codex image tools (icons), Claude/Gemini/Codex/Grok (code and writing).
- Post a comment: "v{a.version} is up: a huge pile of new spells, props, icons and silly sounds. None of the new content has been play-tested yet, bug reports welcome."
"""
    (OUT / f'nexus-update-{a.version}.md').write_text(nexus, encoding='utf-8', newline='\n')
    print(zip_path, zip_path.stat().st_size, zsha)
    print('spells', spells, 'statuses', statuses, 'passives', passives, 'icons', icons, 'models', models)


if __name__ == '__main__':
    main()
