"""Lingerie test sets: ten colourway clones of vanilla underwear templates (file-level checks only)."""
import re
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import generate_mod as generator
import hc_lingerie as hl

SRC_STATS = ROOT / 'src/HomelessCalifornian/Public/HomelessCalifornian/Stats/Generated/Data'


class LingerieTests(unittest.TestCase):
    def test_ten_unique_sets(self):
        self.assertEqual(len(hl.SETS), 10)
        self.assertEqual(len({s[0] for s in hl.SETS}), 10)
        for key, base, title, desc, colours in hl.SETS:
            self.assertNotIn('"', title + desc)
            self.assertTrue(colours)

    def test_generated_templates_stats_and_colours(self):
        with tempfile.TemporaryDirectory() as tmp:
            public = Path(tmp) / 'Public/HomelessCalifornian'
            (public / 'Stats/Generated/Data').mkdir(parents=True)
            hl.DELIVER_VIA_WARDROBE = False
            try:
                hl.generate_lingerie(public, generator.add_loca, generator.get_guid)
            finally:
                hl.DELIVER_VIA_WARDROBE = True
            tree = ET.parse(public / 'RootTemplates/HC_Lingerie.lsf.lsx')
            nodes = tree.findall('.//node[@id="GameObjects"]')
            self.assertEqual(len(nodes), 10)
            keys = []
            for node in nodes:
                a = {x.get('id'): x for x in node.findall('attribute')}
                keys.append(a['MapKey'].get('value'))
                self.assertTrue(a['Name'].get('value').startswith('HC_Lingerie_'))
                self.assertEqual(a['DisplayName'].get('type'), 'TranslatedString')
                slot = [n for n in node.iter('node') if n.get('id') == 'Slot'][0]
                self.assertEqual(slot.find('attribute').get('value'), 'Underwear')
            self.assertEqual(len(set(keys)), 10)
            stats = (public / 'Stats/Generated/Data/HC_Armor_Lingerie.txt').read_text(encoding='utf-8')
            for key in keys:
                self.assertIn(f'data "RootTemplate" "{key}"', stats)
            first = nodes[0]
            colours = {p.find('attribute[@id="Parameter"]').get('value'): p for p in first.iter('node') if p.get('id') == 'Vector3Parameters'}
            self.assertEqual(colours['Color_01'].find('attribute[@id="Enabled"]').get('value'), 'True')
            self.assertEqual(colours['Color_01'].find('attribute[@id="Value"]').get('value'), '1 0.3 0.02')

    def test_delivery_patch_is_idempotent_and_removable(self):
        with tempfile.TemporaryDirectory() as tmp:
            stats = Path(tmp)
            (stats / 'S.txt').write_text('new entry "HC_Shout_ClaimUnclaimedWardrobe"\ntype "SpellData"\n'
                                         'data "SpellProperties" "SummonInInventory(a,-1,1,false,false,false)"\n', encoding='utf-8')
            sums = [f'SummonInInventory(g{i},-1,1,false,false,false)' for i in range(3)]
            hl.patch_delivery(stats, sums)
            once = (stats / 'S.txt').read_text(encoding='utf-8')
            hl.patch_delivery(stats, sums)
            self.assertEqual(once, (stats / 'S.txt').read_text(encoding='utf-8'))
            self.assertEqual(once.count('SummonInInventory'), 4)
            with self.assertRaises(ValueError):
                hl.patch_delivery(tmp + '/nothing', sums)

    def test_built_wardrobe_spell_delivers_all_sets_while_flag_on(self):
        text = ''.join(p.read_text(encoding='utf-8') for p in SRC_STATS.glob('*.txt'))
        block = text.split('new entry "HC_Shout_ClaimUnclaimedWardrobe"')[1].split('new entry "')[0]
        props = re.search(r'data "SpellProperties" "([^"]*)"', block).group(1)
        expected = 12 if hl.DELIVER_VIA_WARDROBE else 2
        self.assertEqual(props.count('SummonInInventory'), expected)


if __name__ == '__main__':
    unittest.main()
