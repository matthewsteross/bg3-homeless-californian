"""Fail-closed HC file validator. No game, source, or Git mutations.

Run: py -3 validation/validate.py [--pak dist/HomelessCalifornian.pak]
Vanilla data is a local extracted reference, never an output of this tool.
"""
from __future__ import annotations
import argparse
import collections
from dataclasses import dataclass
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SHARED = ROOT.parent / 'bg3-meme-mods'
HANDLE = re.compile(r'h[0-9a-f]{8}g[0-9a-f]{4}g[0-9a-f]{4}g[0-9a-f]{4}g[0-9a-f]{12}')
ENTRY = re.compile(r'^new entry "([^"]+)"(.*?)(?=^new entry |\Z)', re.M | re.S)
FIELD = re.compile(r'^data "([^"]+)" "([^"\n]*)"', re.M)
UUID = r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}'
LAYERS = ('Shared', 'SharedDev', 'Gustav', 'GustavDev', 'Honour')

@dataclass
class Stat:
    name: str
    type: str
    body: str
    path: Path
    fields: dict
    using: str | None

def read_stats(root):
    result = collections.defaultdict(list)
    for path in sorted(root.rglob('*.txt')):
        if 'Stats' not in path.parts:
            continue
        content = path.read_text(encoding='utf-8-sig')
        for match in ENTRY.finditer(content):
            name, body = match.groups()
            typ = re.search(r'^type "([^"]+)"', body, re.M)
            donor = re.search(r'^using "([^"]+)"', body, re.M)
            result[name].append(Stat(name, typ[1] if typ else '', body, path,
                                     dict(FIELD.findall(body)), donor[1] if donor else None))
    return result

def xml_data(root, errors=None):
    trees = []
    for path in sorted(root.rglob('*')):
        if path.suffix.lower() not in ('.lsx', '.xml'):
            continue
        try:
            trees.append((path, ET.parse(path)))
        except ET.ParseError as exc:
            if errors is not None:
                errors.append(f'XML {path.relative_to(root)}: {exc}')
    return trees

def index_xml(trees):
    icons, handles, lists, groups = set(), set(), set(), set()
    for path, tree in trees:
        handles.update(e.get('contentuid') for e in tree.iter('content') if e.get('contentuid'))
        for attr in tree.iter('attribute'):
            key, val = attr.get('id'), attr.get('value', '')
            if key == 'MapKey': icons.add(val)
            if key == 'UUID' and 'Lists' in path.parts: lists.add(val.lower())
            if key in ('StatusGroup', 'Name') and val.startswith('SG_'): groups.add(val)
    return icons, handles, lists, groups

def validate(source, vanilla, require_vanilla=True):
    errors = []
    if not source.is_dir():
        return [f'Source directory missing: {source}'], {}
    if require_vanilla:
        for layer in LAYERS:
            if not (vanilla / 'Public' / layer / 'Stats' / 'Generated' / 'Data').is_dir():
                errors.append(f'Vanilla reference layer missing: {layer}')
    own_multi = read_stats(source)
    base_multi = read_stats(vanilla) if vanilla.is_dir() else {}
    base = {name: entries[-1] for name, entries in base_multi.items()}
    own = {name: entries[0] for name, entries in own_multi.items()}
    if not own: errors.append('No source stats found')
    for name, entries in own_multi.items():
        if len(entries) != 1: errors.append(f'Duplicate stat: {name}')
        if not entries[0].type: errors.append(f'Missing stat type: {name}')
    all_stats = base | own
    trees = xml_data(source, errors)
    base_trees = xml_data(vanilla) if vanilla.is_dir() else []
    icons, handles, lists, groups = index_xml(trees)
    bi, bh, bl, bg = index_xml(base_trees)
    # Vanilla localization is not extracted, but copied appearance handles can be
    # proved vanilla by their occurrence in the original vanilla resource XML.
    for _, tree in base_trees:
        for attr in tree.iter('attribute'):
            handle = attr.get('handle')
            if handle: bh.add(handle)
    for st in base.values(): bh.update(HANDLE.findall(st.body))
    # Vanilla groups are not StatusData entries. Their declaration is in stats fields.
    for st in all_stats.values():
        groups.update(re.findall(r'\bSG_[A-Za-z0-9_]+\b', st.fields.get('StatusGroups', '')))
    groups |= bg
    all_icons = icons | bi
    # Extracted vanilla references often exclude textures/atlas registrations. Explicit
    # icon names in vanilla stats are authoritative fallback evidence.
    all_icons.update(st.fields.get('Icon', '') for st in base.values())
    all_handles = handles | bh
    all_lists = lists | bl
    resources = set()
    resource_names, resource_ids = [], []
    for path, tree in trees + base_trees:
        for node in tree.findall('.//node[@id="ActionResourceDefinition"]'):
            attrs = {a.get('id'): a.get('value', '') for a in node.findall('attribute')}
            resource_name, resource_id = attrs.get('Name', ''), attrs.get('UUID', '')
            if resource_name: resources.add(resource_name)
            if (path, tree) in trees:
                resource_names.append(resource_name); resource_ids.append(resource_id)
                if not resource_name or not re.fullmatch(UUID, resource_id):
                    errors.append(f'{path.name}: action resource requires Name and UUID')
    for values, label in ((resource_names, 'name'), (resource_ids, 'UUID')):
        for value, count in collections.Counter(values).items():
            if count > 1: errors.append(f'Duplicate custom action resource {label}: {value}')
    # SurfaceType is an engine enum; derive supported names from vanilla spell
    # functors instead of inventing names or treating them as stats.
    surfaces = set()
    for st in base.values():
        for args in re.findall(r'\bCreateSurface\(([^()]*)\)', st.body):
            parts = [v.strip() for v in args.split(',')]
            if len(parts) >= 3: surfaces.add(parts[2])

    def ref(name, kind, context, allow_group=False):
        if not name: return
        if allow_group and name in groups: return
        target = all_stats.get(name)
        if not target or target.type != kind:
            errors.append(f'{context}: {name} is not defined as {kind}')

    for name, st in own.items():
        if st.using:
            ref(st.using, st.type, f'{name} using')
            seen, cursor = {name}, st
            while cursor.using and cursor.using in all_stats:
                if cursor.using in seen:
                    errors.append(f'{name}: cyclic using chain'); break
                seen.add(cursor.using); cursor = all_stats[cursor.using]
        for func, args in re.findall(r'\b(ApplyStatus|RemoveStatus|HasStatus|StatusImmunity|HasPassive|UnlockSpell|UnlockInterrupt)\(([^()]*)\)', st.body):
            parts = [v.strip().strip("'\"") for v in args.split(',')]
            if func in ('ApplyStatus', 'RemoveStatus') and parts and parts[0] in ('SELF', 'OBSERVER_OBSERVING', 'TARGET', 'SOURCE'):
                parts = parts[1:]
            if not parts: continue
            kind = 'PassiveData' if func == 'HasPassive' else 'SpellData' if func == 'UnlockSpell' else 'InterruptData' if func == 'UnlockInterrupt' else 'StatusData'
            ref(parts[0], kind, f'{name} {func}', allow_group=func in ('RemoveStatus', 'HasStatus', 'StatusImmunity'))
        for field, kind in (('Passives', 'PassiveData'), ('PassivesOnEquip', 'PassiveData'), ('StatusOnEquip', 'StatusData'), ('SpellContainerID', 'SpellData')):
            for value in st.fields.get(field, '').split(';'):
                ref(value, kind, f'{name} {field}')
        for value in st.fields.get('ContainerSpells', '').split(';'):
            ref(value, 'SpellData', f'{name} ContainerSpells')
        for resource in re.findall(r'(?:^|;)\s*([A-Za-z0-9_]+)\s*:', st.fields.get('UseCosts', '')):
            if resource not in resources: errors.append(f'{name}: undefined UseCosts resource {resource}')
        for resource in re.findall(r'\bActionResource(?:Multiplier)?\(\s*([A-Za-z0-9_]+)', st.body):
            if resource not in resources: errors.append(f'{name}: undefined ActionResource {resource}')
        for args in re.findall(r'\bCreateSurface\(([^()]*)\)', st.body):
            parts = [v.strip() for v in args.split(',')]
            if len(parts) >= 3 and parts[2] not in surfaces:
                errors.append(f'{name}: surface {parts[2]} has no vanilla CreateSurface evidence')
        icon = st.fields.get('Icon', '')
        if icon and icon not in all_icons: errors.append(f'{name}: undefined icon {icon}')
        cd = st.fields.get('Cooldown', '')
        if cd not in ('', 'OncePerTurn', 'OncePerShortRest', 'OncePerCombat', 'OncePerRest', 'OncePerTurnNoRealtime'):
            errors.append(f'{name}: invalid Cooldown {cd}')
        if st.type == 'SpellData' and st.using and 'UseCosts' not in st.fields:
            # Inheriting another custom spell with explicit costs is safe; vanilla donors
            # must be overridden to avoid accidentally requiring spell slots.
            cursor, seen = st, set()
            while cursor.using in own and cursor.using not in seen:
                seen.add(cursor.using); cursor = own[cursor.using]
                if 'UseCosts' in cursor.fields: break
            if 'UseCosts' not in cursor.fields:
                errors.append(f'{name}: inherited costs require explicit UseCosts')
        for handle in HANDLE.findall(st.body):
            if handle not in all_handles: errors.append(f'{name}: missing localization {handle}')

    for path, tree in trees:
        for attr in tree.iter('attribute'):
            key, val = attr.get('id'), attr.get('value', '')
            if key in ('PassivesAdded', 'Passives'):
                for value in re.split(r'[;,]', val): ref(value, 'PassiveData', f'{path.name} {key}')
            if key == 'Spells' and 'Lists' in path.parts:
                for value in re.split(r'[;,]', val): ref(value, 'SpellData', path.name)
            if key == 'Selectors':
                for uid in re.findall(r'(?:AddSpells|SelectSpells|SelectSkills|SelectPassives)\((' + UUID + ')', val):
                    if uid.lower() not in all_lists: errors.append(f'{path.name}: undefined selector list {uid}')
            handle = attr.get('handle')
            if handle and HANDLE.fullmatch(handle) and handle not in all_handles:
                errors.append(f'{path.name}: missing localization {handle}')
        # Atlas keys must have game-facing tooltip and controller assets.
        if path.name == 'Icons_Items.lsx':
            for attr in tree.findall('.//attribute[@id="MapKey"]'):
                key = attr.get('value')
                for directory in ('Tooltips/Icons', 'ControllerUIIcons/skills_png'):
                    p = source / 'Public/Game/GUI/Assets' / directory / (key + '.DDS')
                    if not p.is_file(): errors.append(f'Missing icon asset: {p.relative_to(source)}')
        if path.name == 'metadata.lsx':
            for attr in tree.findall('.//node[@id="Object"]/attribute[@id="MapKey"]'):
                asset = path.parent / attr.get('value', '').replace('\\', '/')
                # GUI metadata addresses PNG logical keys; actual shipped BG3
                # textures are DDS files with the same basename.
                if not asset.is_file() and not asset.with_suffix('.DDS').is_file():
                    errors.append(f'Missing GUI metadata asset: {asset}')
    for directory in source.glob('**/Localization/English'):
        for xml in directory.glob('*.loca.xml'):
            if not xml.with_suffix('').is_file(): errors.append(f'Missing compiled localization: {xml.with_suffix("").relative_to(source)}')
    return sorted(set(errors)), {'stats': len(own), 'icons': len(icons), 'localization': len(handles), 'vanilla_stats': len(base)}

def compare_pak(source, pak, unpacker, scratch):
    if not pak.is_file(): return [f'PAK missing: {pak}']
    if not unpacker.is_file(): return [f'Independent unpacker missing: {unpacker}']
    scratch.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='hc-pak-check-', dir=scratch) as tmp:
        result = subprocess.run([sys.executable, str(unpacker), str(pak), tmp], capture_output=True, text=True)
        if result.returncode: return [f'PAK extraction failed: {result.stderr[-1500:]}']
        extracted = Path(tmp)
        errors = []
        source_files = {p.relative_to(source).as_posix(): p for p in source.rglob('*') if p.is_file()}
        pak_files = {p.relative_to(extracted).as_posix(): p for p in extracted.rglob('*') if p.is_file()}
        # Builders may compile .lsf.lsx and omit the authoring form. Require the
        # binary counterpart then; do not pretend binary equals authoring XML.
        for rel, path in source_files.items():
            if rel.endswith('.lsf.lsx') and rel not in pak_files and rel[:-4] in pak_files:
                continue
            if rel not in pak_files: errors.append(f'PAK missing source file: {rel}')
            elif path.read_bytes() != pak_files[rel].read_bytes(): errors.append(f'PAK/source mismatch: {rel}')
        for rel in pak_files:
            if rel not in source_files and rel + '.lsx' not in source_files:
                errors.append(f'Unexpected PAK file: {rel}')
        return errors

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=ROOT / 'src/HomelessCalifornian')
    parser.add_argument('--vanilla', type=Path, default=ROOT / 'temp_race')
    parser.add_argument('--pak', type=Path)
    parser.add_argument('--unpacker', type=Path, default=SHARED / 'tools/lspk_list.py')
    args = parser.parse_args()
    errors, counts = validate(args.source.resolve(), args.vanilla.resolve())
    if args.pak:
        errors += compare_pak(args.source.resolve(), args.pak.resolve(), args.unpacker.resolve(), ROOT / 'work/local_validation')
    print('HC file validation:', counts)
    for error in errors: print('ERROR:', error)
    print('FAIL' if errors else 'PASS (file-level only; gameplay requires human playtest)')
    return 1 if errors else 0

if __name__ == '__main__':
    sys.exit(main())
