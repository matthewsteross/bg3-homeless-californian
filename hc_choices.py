"""Level-two exploration trade choice, using vanilla passive selectors."""
from pathlib import Path
import xml.etree.ElementTree as ET
import re


def generate_choices(public_dir, add_loca, get_guid):
    public = Path(public_dir)
    options = [
        ('HC_StreetTrade_Scrounger', 'Scrounger', 'Investigation', 'Survival', 'You know what is useful, what is edible, and which one matters today.'),
        ('HC_StreetTrade_Fixer', 'Fixer', 'Persuasion', 'Deception', 'The paperwork is missing. The confidence is not.'),
        ('HC_StreetTrade_Lookout', 'Lookout', 'Perception', 'Stealth', 'Notice the trouble before it notices your address.'),
    ]
    blocks = []
    for key, name, first, second, flavor in options:
        title = add_loca(key + '_Name', name)
        description = add_loca(key + '_Description', f'Advantage on {first} and {second} ability checks. {flavor}')
        blocks.append(f'''new entry "{key}"
type "PassiveData"
data "DisplayName" "{title};1"
data "Description" "{description};1"
data "Icon" "PassiveFeature_ReliableTalent"
data "Properties" "Highlighted"
data "Boosts" "Advantage(Skill,{first});Advantage(Skill,{second})"
''')
    (public / 'Stats/Generated/Data/HC_Passives_Choices.txt').write_text('\n'.join(blocks), encoding='utf-8')
    uid = get_guid('HC_StreetTrade_List')
    path = public / 'Lists/PassiveLists.lsx'
    tree = ET.parse(path)
    parent = tree.find('.//node[@id="root"]/children')
    node = ET.SubElement(parent, 'node', id='PassiveList')
    for key, kind, value in [('Name', 'FixedString', 'Street Trade'),
                             ('Passives', 'LSString', ','.join(x[0] for x in options)),
                             ('UUID', 'guid', uid)]:
        ET.SubElement(node, 'attribute', id=key, type=kind, value=value)
    original = path.read_text(encoding='utf-8')
    snippet = ET.tostring(node, encoding='unicode')
    path.write_text(original.replace('            </children>', '                ' + snippet + '\n            </children>', 1), encoding='utf-8')
    path = public / 'Progressions/Progressions.lsx'
    original = path.read_text(encoding='utf-8')
    attached = 0
    def attach(match):
        nonlocal attached
        block = match.group(0)
        attrs = {a.get('id'): a.get('value') for a in ET.fromstring(block).findall('attribute')}
        if attrs.get('Name') == 'HomelessCalifornian' and attrs.get('Level') == '2':
            addition = f';SelectPassives({uid},1,HCStreetTrade)'
            block = re.sub(r'(<attribute id="Selectors"[^>]*value=")([^"]*)("/>)',
                           lambda m: m[1] + m[2] + addition + m[3], block, count=1)
            attached += 1
        return block
    updated = re.sub(r'<node id="Progression">(?:(?!<node).)*?</node>', attach, original, flags=re.S)
    if attached != 1:
        raise ValueError('Street Trade must attach to exactly one HC level-two progression')
    path.write_text(updated, encoding='utf-8')
    path = public / 'Progressions/ProgressionDescriptions.lsx'
    tree = ET.parse(path)
    node = ET.SubElement(tree.find('.//node[@id="root"]/children'), 'node', id='ProgressionDescription')
    for key, text in [('DisplayName', 'Street Trade'), ('Description', 'Choose one exploration trade. Each grants advantage on two ability checks. Respec to change your choice.')]:
        ET.SubElement(node, 'attribute', id=key, type='TranslatedString', handle=add_loca('HCStreetTrade_' + key, text), version='1')
    ET.SubElement(node, 'attribute', id='SelectorId', type='FixedString', value='HCStreetTrade')
    ET.SubElement(node, 'attribute', id='UUID', type='guid', value=get_guid('HCStreetTrade_Description'))
    original = path.read_text(encoding='utf-8')
    snippet = ET.tostring(node, encoding='unicode')
    path.write_text(original.replace('            </children>', '                ' + snippet + '\n            </children>', 1), encoding='utf-8')
