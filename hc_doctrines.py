"""A level-four resource/protection/mobility choice; no baseline nerfs."""
from pathlib import Path
import re
import xml.etree.ElementTree as ET


def generate_doctrines(public_dir, add_loca, get_guid):
    public = Path(public_dir)
    options = [
        ('HC_JunkDoctrine_Hoarder', 'Hoarder', 'Maximum Junk increased by 2. Your pockets have annexed the neighbouring pockets.', 'ActionResource(HC_Junk,2,0)'),
        ('HC_JunkDoctrine_Fortifier', 'Fortifier', '+1 Armour Class. Every layer of rubbish is another layer of plausible protection.', 'AC(1)'),
        ('HC_JunkDoctrine_Runner', 'Runner', '+3 m movement speed. You have never missed a train you were already chasing.', 'ActionResource(Movement,3,0)'),
    ]
    blocks = []
    for key, name, description, boost in options:
        blocks.append(f'''new entry "{key}"
type "PassiveData"
data "DisplayName" "{add_loca(key + '_Name', name)};1"
data "Description" "{add_loca(key + '_Description', description)};1"
data "Icon" "PassiveFeature_ReliableTalent"
data "Properties" "Highlighted"
data "Boosts" "{boost}"
''')
    (public / 'Stats/Generated/Data/HC_Passives_Doctrines.txt').write_text('\n'.join(blocks), encoding='utf-8')
    uid = get_guid('HC_JunkDoctrine_List')
    node = ET.Element('node', id='PassiveList')
    for key, kind, value in [('Name', 'FixedString', 'Junk Doctrine'), ('Passives', 'LSString', ','.join(x[0] for x in options)), ('UUID', 'guid', uid)]:
        ET.SubElement(node, 'attribute', id=key, type=kind, value=value)
    def insert(path, snippet):
        old = path.read_text(encoding='utf-8')
        if '            </children>' not in old:
            raise ValueError(f'Missing list root in {path}')
        path.write_text(old.replace('            </children>', '                ' + snippet + '\n            </children>', 1), encoding='utf-8')
    insert(public / 'Lists/PassiveLists.lsx', ET.tostring(node, encoding='unicode'))
    path = public / 'Progressions/Progressions.lsx'
    attached = 0
    def attach(match):
        nonlocal attached
        block = match.group(0)
        attrs = {a.get('id'): a.get('value') for a in ET.fromstring(block).findall('attribute')}
        if attrs.get('Name') == 'HomelessCalifornian' and attrs.get('Level') == '4':
            addition = f';SelectPassives({uid},1,HCJunkDoctrine)'
            block = re.sub(r'(<attribute id="Selectors"[^>]*value=")([^"]*)("\s*/>)', lambda m: m[1] + m[2] + addition + m[3], block, count=1)
            attached += 1
        return block
    updated = re.sub(r'<node id="Progression">(?:(?!<node).)*?</node>', attach, path.read_text(encoding='utf-8'), flags=re.S)
    if attached != 1:
        raise ValueError('Junk Doctrine needs exactly one level-four HC progression')
    path.write_text(updated, encoding='utf-8')
    node = ET.Element('node', id='ProgressionDescription')
    for key, value in [('DisplayName', 'Junk Doctrine'), ('Description', 'Choose more Junk, better protection or faster movement. Respec to change your doctrine.')]:
        ET.SubElement(node, 'attribute', id=key, type='TranslatedString', handle=add_loca('HCJunkDoctrine_' + key, value), version='1')
    ET.SubElement(node, 'attribute', id='SelectorId', type='FixedString', value='HCJunkDoctrine')
    ET.SubElement(node, 'attribute', id='UUID', type='guid', value=get_guid('HCJunkDoctrine_Description'))
    insert(public / 'Progressions/ProgressionDescriptions.lsx', ET.tostring(node, encoding='unicode'))
