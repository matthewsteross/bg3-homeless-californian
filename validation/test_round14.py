"""Round 14: three Caltrans spells granted at base levels 5, 9 and 11."""
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import hc_round14 as r14

SRC = ROOT / 'src/HomelessCalifornian/Public/HomelessCalifornian'


class RoundFourteenTests(unittest.TestCase):
    def test_spells_defined_with_donor_icon_and_no_quotes(self):
        text = (SRC / 'Stats/Generated/Data/HC_Spells_Round14.txt').read_text(encoding='utf-8')
        for level, name, title, donor, icon, description, fields in r14.SPELLS:
            block = text.split(f'new entry "{name}"')[1].split('new entry "')[0]
            self.assertIn(f'using "{donor}"', block)
            self.assertIn('data "Icon" "Spell_', block)
            self.assertNotIn('"', description)
            self.assertIn('HC_Junk', block)

    def test_each_spell_granted_once_at_its_level(self):
        sl = {}
        for n in ET.parse(SRC / 'Lists/SpellLists.lsx').iter('node'):
            a = {x.get('id'): x.get('value') for x in n.findall('attribute')}
            if n.get('id') == 'SpellList':
                sl[a['UUID']] = (a.get('Spells') or '').split(';')
        found = {}
        for n in ET.parse(SRC / 'Progressions/Progressions.lsx').iter('node'):
            if n.get('id') != 'Progression':
                continue
            a = {x.get('id'): x.get('value') for x in n.findall('attribute')}
            if a.get('Name') != 'HomelessCalifornian' or a.get('ProgressionType') == '1':
                continue
            import re
            for uid in re.findall(r'AddSpells\(([0-9a-f-]{36})', a.get('Selectors', '')):
                for s in sl.get(uid, []):
                    found.setdefault(s, []).append(int(a['Level']))
        for level, name, *_ in r14.SPELLS:
            self.assertEqual(found.get(name), [level], name)


if __name__ == '__main__':
    unittest.main()
