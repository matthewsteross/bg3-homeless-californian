"""Exercise infrastructure only against an isolated copy of current Public."""
from pathlib import Path
import re
import shutil
import sys
import tempfile
import unittest
import uuid
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from hc_subclass_levels import (NEW_LEVELS, SUBCLASSES, add_empty_subclass_nodes,
                                apply_subclass_passives)
from validation import validate


def guid(key):
    return str(uuid.uuid5(uuid.UUID('3fa85f64-5717-4562-b3fc-2c963f66afa6'), key))


def attrs(node):
    return {a.get('id'): a.get('value') for a in node.findall('attribute')}


class SubclassLevelsTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.source = Path(tmp.name)
        shutil.copytree(ROOT / 'src/HomelessCalifornian/Public', self.source / 'Public')
        self.public = self.source / 'Public/HomelessCalifornian'
        self.path = self.public / 'Progressions/Progressions.lsx'
        # The built tree may already contain the new empty nodes; strip them so the tests start from the old layout.
        import re
        wanted = {guid(f'HC_SubclassLevel_{name}_{level}') for name in SUBCLASSES for level in NEW_LEVELS}
        raw = self.path.read_bytes().decode('utf-8')
        def drop(m):
            return '' if any(u in m.group(0) for u in wanted) else m.group(0)
        pattern = '(?:' + chr(13) + '?' + chr(10) + ')?[ ' + chr(9) + ']*<node id="Progression">(?:(?!<node).)*?</node>'
        raw = re.sub(pattern, drop, raw, flags=re.S)
        self.path.write_bytes(raw.encode('utf-8'))
        self.before = self.path.read_bytes()

    def nodes(self):
        return [attrs(n) for n in ET.parse(self.path).findall('.//node[@id="Progression"]')]

    def test_empty_nodes_structure_bytes_unique_and_idempotent(self):
        add_empty_subclass_nodes(self.public, guid)
        after = self.path.read_bytes()
        # Every original byte is retained, with a single appended insertion.
        end = self.before.rfind(b'            </children>')
        self.assertTrue(after.startswith(self.before[:end]))
        self.assertTrue(after.endswith(self.before[end:]))
        nodes = self.nodes()
        self.assertEqual(len(nodes), len(ET.fromstring(self.before).findall('.//node[@id="Progression"]')) + 24)
        ids = [a.get('value') for a in ET.fromstring(after).iter('attribute') if a.get('id') == 'UUID']
        self.assertEqual(len(ids), len(set(ids)))
        for name in SUBCLASSES:
            donor = next(n for n in nodes if n.get('Name') == name and n['Level'] == '3')
            for level in NEW_LEVELS:
                node = next(n for n in nodes if n.get('Name') == name and n['Level'] == str(level))
                expected = {k: v for k, v in donor.items() if k not in ('Selectors', 'PassivesAdded', 'PassivesRemoved', 'Boosts')}
                expected.update(Level=str(level), UUID=guid(f'HC_SubclassLevel_{name}_{level}'))
                self.assertEqual(node, expected)
        add_empty_subclass_nodes(self.public, guid)
        self.assertEqual(after, self.path.read_bytes())

    def test_passives_merge_and_missing_target_is_atomic(self):
        add_empty_subclass_nodes(self.public, guid)
        grants = {SUBCLASSES[0]: {3: ['BiohazardStench', 'HC_ConcreteBankTraction', 'HC_ConcreteBankTraction'],
                                   4: ['HC_RebarAnchor', 'HC_RebarAnchor']}}
        apply_subclass_passives(self.public, grants)
        nodes = {(n.get('Name'), n.get('Level')): n for n in self.nodes()}
        self.assertEqual(nodes[SUBCLASSES[0], '3']['PassivesAdded'], 'BiohazardStench;HC_ConcreteBankTraction')
        self.assertEqual(nodes[SUBCLASSES[0], '4']['PassivesAdded'], 'HC_RebarAnchor')
        after = self.path.read_bytes()
        apply_subclass_passives(self.public, grants)
        self.assertEqual(after, self.path.read_bytes())
        for grants in ({SUBCLASSES[0]: {4: ['HC_RebarAnchor'], 99: ['Missing']}}, {'Unknown': {4: ['Missing']}}):
            with self.assertRaisesRegex(ValueError, 'Missing subclass progression'):
                apply_subclass_passives(self.public, grants)
            self.assertEqual(after, self.path.read_bytes())

    def test_spell_attachment_and_repo_validator(self):
        add_empty_subclass_nodes(self.public, guid)
        apply_subclass_passives(self.public, {n: {l: ['HC_RebarAnchor'] for l in NEW_LEVELS} for n in SUBCLASSES})
        # Reproduce generate_local_expansion list_ids / consumed / attach logic.
        grants = {'subclasses': {n: {l: ['HC_Target_CulvertSiphon'] for l in NEW_LEVELS} for n in SUBCLASSES}}
        list_ids = {(n, l): guid(f'Test_SubclassList_{n}_{l}') for n, levels in grants['subclasses'].items() for l in levels}
        lists = ET.parse(self.public / 'Lists/SpellLists.lsx')
        parent = lists.find('.//node[@id="root"]/children')
        for key, uid in list_ids.items():
            node = ET.SubElement(parent, 'node', id='SpellList')
            ET.SubElement(node, 'attribute', id='Spells', type='LSString', value=';'.join(grants['subclasses'][key[0]][key[1]]))
            ET.SubElement(node, 'attribute', id='UUID', type='guid', value=uid)
        lists.write(self.public / 'Lists/SpellLists.lsx', encoding='utf-8', xml_declaration=True)
        consumed = set()

        def attach(match):
            block = match.group(0)
            a = attrs(ET.fromstring(block))
            key = (a.get('Name'), int(a.get('Level', '0')))
            uid = list_ids.get(key)
            if uid:
                consumed.add(key)
                old = a.get('Selectors', '')
                value = ';'.join(x for x in [old, f'AddSpells({uid})'] if x)
                line = f'<attribute id="Selectors" type="LSString" value="{value}"/>'
                if 'Selectors' in a:
                    block = re.sub(r'<attribute id="Selectors"[^>]*/>', lambda _: line, block, count=1)
                else:
                    block = block.replace('<attribute id="Level"', line + '\n                    <attribute id="Level"', 1)
            return block

        text = re.sub(r'<node id="Progression">(?:(?!<node).)*?</node>', attach, self.path.read_text(encoding='utf-8'), flags=re.S)
        self.assertEqual(set(list_ids), consumed)
        self.path.write_text(text, encoding='utf-8')
        for n in self.nodes():
            key = (n.get('Name'), int(n.get('Level', '0')))
            if key in list_ids:
                self.assertIn(f'AddSpells({list_ids[key]})', n['Selectors'])
        errors, counts = validate.validate(self.source, ROOT / 'temp_race')
        self.assertEqual(errors, [], '\n'.join(errors))
        self.assertTrue(counts)


if __name__ == '__main__':
    unittest.main()
