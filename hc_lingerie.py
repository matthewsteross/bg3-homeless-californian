"""Lingerie test sets (ten female-oriented colourways), 2026-10-18. FIRST TEST ONLY, NOT PLAY-TESTED.

What this really is: ten new Underwear-slot items. Each one clones the root template of a vanilla underwear item
(assets/lingerie/vanilla_underwear_templates.json: the Equipment/Visuals map that sends all 20 vanilla body-type keys to
vanilla visual resources, so the pieces fit every body type) and changes only the item's own colour overrides
(Color_01/02/03 ...) and its text. No vanilla mesh or texture is copied; the vanilla visual ids are only referenced.
Brand-new geometry and a custom lace texture are a later step (see HANDOFF-2026-10-18-evening.md).

DELIVERY (TEMPORARY, MATTHEW ASKED FOR THIS TO BE REMOVED LATER): the ten items are summoned into the inventory by the
existing spell HC_Shout_ClaimUnclaimedWardrobe (Unclaimed Wardrobe, base level 1). To remove: set DELIVER_VIA_WARDROBE = False
(or delete the patch_delivery call in generate_mod.py) and rebuild; the spell then goes back to giving only the two scavenged
garments and the wardrobe prop.
UNVERIFIED in game: that the clone renders, tints, equips and fits.
"""
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

DELIVER_VIA_WARDROBE = False  # switched off 2026-10-18 after the proof of concept passed; see docs/LINGERIE-NOTES.md
WARDROBE_SPELL = 'HC_Shout_ClaimUnclaimedWardrobe'
DATA = Path(__file__).resolve().parent / 'assets' / 'lingerie' / 'vanilla_underwear_templates.json'

# key, vanilla base, display name, description, {parameter: (r, g, b)}
SETS = [
    ('CaltransOrange', 'ARM_Underwear_Humans_C', 'Caltrans Orange Lace Set',
     'Hi-vis orange lace, reflective in all the places the safety officer will not discuss. Lane closed ahead.',
     {'Color_01': (1.0, 0.30, 0.02)}),
    ('TenderloinBlack', 'ARM_Underwear_Humans_B', 'Tenderloin Midnight Black Set',
     'Black lace with a faint chemical shimmer. It does not show the dirt; neither do you.',
     {'Color_01': (0.03, 0.03, 0.04)}),
    ('VenicePink', 'ARM_Underwear_Tieflings', 'Venice Boardwalk Neon Pink Set',
     'Neon pink, sold by a man with a parrot and a laminated permit that is clearly a coupon.',
     {'Color_01': (1.0, 0.12, 0.45)}),
    ('MalibuCoral', 'ARM_Underwear_Humans', 'Malibu Sunset Coral Set',
     'Coral lace in a shade the listing called Private Beach Access. The beach is not private.',
     {'Color_01': (1.0, 0.38, 0.30)}),
    ('BartBlue', 'ARM_Underwear_Elves_Blue', 'BART Seat-Cushion Blue Set',
     'Indigo with a lighter trim, in a pattern last seen on a train seat you chose not to ask about.',
     {'Color_01': (0.10, 0.25, 0.90), 'Color_02': (0.70, 0.80, 1.00)}),
    ('SeriesBWhite', 'ARM_Underwear_Incubus', 'Series-B Unicorn White Set',
     'Crisp white lace, disrupting the intimate-apparel space with a pre-revenue valuation.',
     {'Color_01': (0.95, 0.95, 0.97)}),
    ('WalkOfFameGold', 'ARM_Underwear_Githyanki_Black', 'Walk of Fame Gold Set',
     'Gold trim over black, brass-star style. A pigeon has already claimed one of the stars.',
     {'Color_01': (1.0, 0.70, 0.10), 'Color_02': (0.05, 0.05, 0.05), 'Color_03': (1.0, 0.85, 0.35)}),
    ('HaightPurple', 'ARM_Underwear_Gnomes_Blue', 'Haight-Ashbury Violet Set',
     'Violet and magenta, tie-dyed in a bathtub by someone who promised it would hold.',
     {'Color_01': (0.50, 0.10, 0.80), 'Color_02': (0.90, 0.20, 0.70), 'Color_03': (0.30, 0.10, 0.60)}),
    ('FireSeasonRed', 'ARM_Underwear_HalfOrcs', 'Fire Season Red Set',
     'Deep red. The air quality index is 312 and you have never looked better.',
     {'Color_01': (0.80, 0.02, 0.02)}),
    ('RedwoodGreen', 'ARM_Underwear_Dwarves_Green', 'Redwood Emerald Set',
     'Forest green with cream trim, sustainably sourced from a tree-sit that is still ongoing.',
     {'Color_01': (0.05, 0.45, 0.15), 'Color_02': (0.30, 0.70, 0.30), 'Color_03': (0.90, 0.85, 0.50)}),
]
ARMOR_NAMES = {key: f'HC_ARM_Lingerie_{key}' for key, *_ in SETS}


def _template_xml(base, new_key, guid, title_handle, desc_handle, colours):
    data = json.loads(DATA.read_text(encoding='utf-8'))[base]
    node = ET.fromstring(data['xml'])
    attrs = {a.get('id'): a for a in node.findall('attribute')}
    attrs['MapKey'].set('value', guid)
    attrs['Name'].set('value', f'HC_Lingerie_{new_key}')
    for tag, handle in (('DisplayName', title_handle), ('Description', desc_handle)):
        old = attrs.get(tag)
        if old is not None:
            node.remove(old)
        el = ET.Element('attribute', id=tag, type='TranslatedString', handle=handle, version='1')
        node.insert(0, el)
    # colour overrides: only touch parameters that exist in the vanilla override list, and enable them
    used = set()
    for param in node.iter('node'):
        if param.get('id') != 'Vector3Parameters':
            continue
        pattr = {a.get('id'): a for a in param.findall('attribute')}
        name = pattr['Parameter'].get('value')
        if name in colours:
            pattr['Value'].set('value', ' '.join(f'{c:g}' for c in colours[name]))
            pattr['Enabled'].set('value', 'True')
            pattr['Custom'].set('value', 'True')
            used.add(name)
    missing = set(colours) - used
    if missing:
        raise ValueError(f'{base} has no override slot for {sorted(missing)}')
    return node


def generate_lingerie(public_dir, add_loca, get_guid):
    public = Path(public_dir)
    stats = public / 'Stats' / 'Generated' / 'Data'
    roots = public / 'RootTemplates'
    stats.mkdir(parents=True, exist_ok=True)
    roots.mkdir(parents=True, exist_ok=True)
    save = ET.Element('save')
    ET.SubElement(save, 'version', major='4', minor='0', revision='9', build='0')
    region = ET.SubElement(save, 'region', id='Templates')
    children = ET.SubElement(ET.SubElement(region, 'node', id='Templates'), 'children')
    blocks, summons = [], []
    for key, base, title, desc, colours in SETS:
        stat = ARMOR_NAMES[key]
        guid = get_guid(stat + '_RootTemplate')
        handle_t = add_loca(stat + '_Name', title)
        handle_d = add_loca(stat + '_Description', desc)
        children.append(_template_xml(base, key, guid, handle_t, handle_d, colours))
        blocks.append(f'''new entry "{stat}"
type "Armor"
using "ARM_Underwear"
data "RootTemplate" "{guid}"
data "Rarity" "Common"
data "ValueOverride" "0"
''')
        summons.append(f'SummonInInventory({guid},-1,1,false,false,false)')
    ET.indent(save, space='    ')
    ET.ElementTree(save).write(roots / 'HC_Lingerie.lsf.lsx', encoding='utf-8', xml_declaration=True)
    (stats / 'HC_Armor_Lingerie.txt').write_text('\n'.join(blocks), encoding='utf-8', newline='\n')
    if DELIVER_VIA_WARDROBE:
        patch_delivery(stats, summons)
    return {'base': {}, 'subclasses': {}, 'existing_list_spells': {}}


def patch_delivery(stats, summons):
    """TEMPORARY: append the ten SummonInInventory functors to the Unclaimed Wardrobe spell (idempotent)."""
    matches = []
    pattern = re.compile(r'(new entry "%s"[^\S\r\n]*\r?\n)(.*?)(?=^new entry |\Z)' % WARDROBE_SPELL, re.M | re.S)
    for path in sorted(Path(stats).glob('*.txt')):
        text = path.read_bytes().decode('utf-8')
        for match in pattern.finditer(text):
            matches.append((path, text, match))
    if len(matches) != 1:
        raise ValueError(f'Expected exactly one {WARDROBE_SPELL} spell; found {len(matches)} in {stats}')
    path, text, match = matches[0]
    block = match.group(0)
    prop = re.search(r'(data "SpellProperties" ")([^"]*)(")', block)
    if prop is None:
        raise ValueError(f'{WARDROBE_SPELL} has no SpellProperties value')
    terms = [t for t in prop.group(2).split(';') if t]
    new_terms = terms + [s for s in summons if s not in terms]
    if new_terms == terms:
        return
    block = block[:prop.start(2)] + ';'.join(new_terms) + block[prop.end(2):]
    path.write_bytes((text[:match.start()] + block + text[match.end():]).encode('utf-8'))
