"""Round 13: four base-class passives, granted at levels 4/6/8/10 through the Progressions."""
import re
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import hc_round13 as r13

SRC = ROOT / 'src/HomelessCalifornian/Public/HomelessCalifornian'


class RoundThirteenTests(unittest.TestCase):
    def test_passives_defined_with_text_icons_and_boosts(self):
        text = (SRC / 'Stats/Generated/Data/HC_Passives_Round13.txt').read_text(encoding='utf-8')
        for name, title, level, icon, description, boosts in r13.PASSIVES:
            block = text.split(f'new entry "{name}"')[1].split('new entry "')[0]
            self.assertIn('type "PassiveData"', block)
            self.assertIn(f'data "Boosts" "{boosts}"', block)
            self.assertIn('data "DisplayName"', block)
            self.assertNotIn('"', description)

    def test_each_passive_attached_once_at_its_level(self):
        found = {}
        for node in ET.parse(SRC / 'Progressions/Progressions.lsx').iter('node'):
            if node.get('id') != 'Progression':
                continue
            a = {x.get('id'): x.get('value') for x in node.findall('attribute')}
            if a.get('Name') != 'HomelessCalifornian' or a.get('ProgressionType') == '1':
                continue
            for p in (a.get('PassivesAdded') or '').split(';'):
                if p.startswith('HC_') and p in {x[0] for x in r13.PASSIVES}:
                    found.setdefault(p, []).append(int(a['Level']))
        for name, _t, level, *_ in r13.PASSIVES:
            self.assertEqual(found.get(name), [level], name)

    def test_grants_shape(self):
        self.assertEqual(set(r13.GRANTS), {'base', 'subclasses', 'existing_list_spells', 'base_passives'})
        self.assertEqual(sorted(r13.GRANTS['base_passives']), [4, 6, 8, 10])


if __name__ == '__main__':
    unittest.main()
