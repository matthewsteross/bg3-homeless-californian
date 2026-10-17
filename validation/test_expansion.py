"""Generation regression checks run entirely in temporary source trees."""
from pathlib import Path
import contextlib
import hashlib
import io
import sys
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import generate_mod as generator


class ExpansionGenerationTests(unittest.TestCase):
    def test_repeatable_grants_and_resource(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)
            public = source / 'Public/HomelessCalifornian'
            with patch.object(generator, 'PUBLIC_DIR', str(public)), \
                 patch.object(generator, 'MODS_DIR', str(source / 'Mods/HomelessCalifornian')), \
                 contextlib.redirect_stdout(io.StringIO()):
                generator.main()
                before = {p.relative_to(source): hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in source.rglob('*') if p.is_file()}
                generator.main()
                after = {p.relative_to(source): hashlib.sha256(p.read_bytes()).hexdigest()
                         for p in source.rglob('*') if p.is_file()}
            self.assertEqual(before, after)
            lists = ET.parse(public / 'Lists/SpellLists.lsx')
            new_lists = {}
            for node in lists.findall('.//node[@id="SpellList"]'):
                attrs = {a.get('id'): a.get('value') for a in node.findall('attribute')}
                if 'HC_' in attrs['Spells']:
                    new_lists[attrs['UUID']] = attrs['Spells'].split(';')
            # 24 expansion lists, Overpass L10, and the base racial list (round 4).
            self.assertEqual(len(new_lists), 26)
            progressions = ET.parse(public / 'Progressions/Progressions.lsx')
            selectors = ';'.join(a.get('value', '') for a in progressions.findall('.//attribute[@id="Selectors"]'))
            for uid in new_lists:
                self.assertIn(uid, selectors)
            expected = {('HomelessCalifornian', '4'): 'HC_Target_CoatHangerSlimJim',
                        ('TenderloinBiohazard', '6'): 'HC_Target_CurbsideClinic',
                        ('HomelessCalifornian', '5'): 'HC_Target_GuiltTrip',
                        ('HomelessCalifornian', '6'): 'HC_Target_PublicScene',
                        ('HomelessCalifornian', '7'): 'HC_Shout_IWasHereFirst',
                        ('HomelessCalifornian', '8'): 'HC_Target_TrappedInTheInvisibleBox',
                        ('HomelessCalifornian', '9'): 'HC_Zone_BucketDrumSolo',
                        ('HomelessCalifornian', '10'): 'HC_Target_CompassionBurnout',
                        ('HomelessCalifornian', '11'): 'HC_Projectile_PuncturedLithiumCell',
                        ('VeniceBoardwalkBrawler', '6'): 'HC_Target_Sublet',
                        ('VeniceBoardwalkBrawler', '10'): 'HC_Target_ChairCheck',
                        ('TenderloinBiohazard', '10'): 'HC_Target_EverybodyKnowsThisGuy',
                        ('BARTPlatformMenace', '6'): 'HC_Target_FareInspection'}
            for node in progressions.findall('.//node[@id="Progression"]'):
                attrs = {a.get('id'): a.get('value') for a in node.findall('attribute')}
                spell = expected.get((attrs.get('Name'), attrs.get('Level')))
                if spell:
                    uid = next(uid for uid, spells in new_lists.items() if spell in spells)
                    self.assertIn(f'AddSpells({uid})', attrs.get('Selectors', ''))
                    del expected[(attrs['Name'], attrs['Level'])]
            self.assertFalse(expected, 'Utility spells must attach at the intended class/subclass levels')
            trade_list = generator.get_guid('HC_StreetTrade_List')
            trade_nodes = lists = ET.parse(public / 'Lists/PassiveLists.lsx')
            options = next(n for n in trade_nodes.findall('.//node[@id="PassiveList"]')
                           if n.find('attribute[@id="UUID"]').get('value') == trade_list)
            self.assertEqual(len(options.find('attribute[@id="Passives"]').get('value').split(',')), 7)
            self.assertEqual(selectors.count(f'SelectPassives({trade_list},1,HCStreetTrade)'), 1)
            doctrine_list = generator.get_guid('HC_JunkDoctrine_List')
            doctrine_options = next(n for n in trade_nodes.findall('.//node[@id="PassiveList"]')
                                    if n.find('attribute[@id="UUID"]').get('value') == doctrine_list)
            self.assertEqual(len(doctrine_options.find('attribute[@id="Passives"]').get('value').split(',')), 6)
            self.assertEqual(selectors.count(f'SelectPassives({doctrine_list},1,HCJunkDoctrine)'), 1)
            for node in progressions.findall('.//node[@id="Progression"]'):
                attrs = {a.get('id'): a.get('value') for a in node.findall('attribute')}
                if attrs.get('Name') == 'HomelessCalifornian' and attrs.get('Level') == '4':
                    self.assertEqual(attrs.get('AllowImprovement'), 'true')
                    self.assertIn(f'SelectPassives({doctrine_list},1,HCJunkDoctrine)', attrs['Selectors'])
            capstones = {'TenderloinBiohazard': 'Tenderloin', 'VeniceBoardwalkBrawler': 'Venice', 'BARTPlatformMenace': 'BART'}
            for node in progressions.findall('.//node[@id="Progression"]'):
                attrs = {a.get('id'): a.get('value') for a in node.findall('attribute')}
                if attrs.get('Name') == 'HomelessCalifornian' and attrs.get('Level') == '12':
                    self.assertEqual(attrs.get('AllowImprovement'), 'true')
                    self.assertIn(f'AddSpells({generator.SPELLLIST_LVL12})', attrs['Selectors'])
                variant = capstones.get(attrs.get('Name'))
                if variant and attrs.get('Level') == '12':
                    self.assertEqual(attrs['ProgressionType'], '1')
                    spell = 'HC_Shout_SquattersRights_' + variant
                    uid = next(uid for uid, spells in new_lists.items() if spell in spells)
                    self.assertIn(f'AddSpells({uid})', attrs['Selectors'])
                    del capstones[attrs['Name']]
            self.assertFalse(capstones)
            resources = ET.parse(public / 'ActionResourceDefinitions/ActionResourceDefinitions.lsx')
            resource_names = [a.get('value') for a in resources.findall('.//attribute[@id="Name"]')]
            self.assertEqual(resource_names, ['HC_Junk'])
            roots = ET.parse(public / 'RootTemplates/HC_Wardrobe.lsf.lsx')
            self.assertEqual(len(roots.findall('.//node[@id="GameObjects"]')), 2)

    def test_californian_racial_progression_wiring(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)
            public = source / 'Public/HomelessCalifornian'
            with patch.object(generator, 'PUBLIC_DIR', str(public)), \
                 patch.object(generator, 'MODS_DIR', str(source / 'Mods/HomelessCalifornian')), \
                 contextlib.redirect_stdout(io.StringIO()):
                generator.main()

            lists = ET.parse(public / 'Lists/SpellLists.lsx')
            spell_lists = {}
            for node in lists.findall('.//node[@id="SpellList"]'):
                attrs = {a.get('id'): a.get('value') for a in node.findall('attribute')}
                spell_lists[attrs['UUID']] = attrs['Spells'].split(';')

            self.assertIn('Target_RipCurrent', spell_lists[generator.SPELLLIST_BEACHBORN_L3])
            self.assertIn('Shout_GoldenHour', spell_lists[generator.SPELLLIST_BEACHBORN_L5])
            self.assertIn('Target_DisruptivePivot', spell_lists[generator.SPELLLIST_SILICONITE_L3])
            self.assertIn('Target_NonDisclosureAgreement', spell_lists[generator.SPELLLIST_SILICONITE_L5])
            self.assertIn('Shout_DustDevil', spell_lists[generator.SPELLLIST_INLANDEMPEROR_L1])
            self.assertIn('Zone_OverpassExhaust', spell_lists[generator.SPELLLIST_INLANDEMPEROR_L3])
            self.assertIn('Target_Heatstroke', spell_lists[generator.SPELLLIST_INLANDEMPEROR_L5])

            progressions = ET.parse(public / 'Progressions/Progressions.lsx')
            prog_map = {}
            for node in progressions.findall('.//node[@id="Progression"]'):
                attrs = {a.get('id'): a.get('value', '') for a in node.findall('attribute')}
                key = (attrs.get('Name'), attrs.get('Level'))
                prog_map[key] = attrs

            calif_l1 = prog_map[('Californian', '1')]
            self.assertIn('RunyonCanyonGlutes', calif_l1['PassivesAdded'])
            self.assertIn('EarthquakeSense', calif_l1['PassivesAdded'])
            self.assertIn('Veteran405', calif_l1['PassivesAdded'])
            self.assertIn(f'AddSpells({generator.SPELLLIST_CALIFORNIAN_L1}', calif_l1['Selectors'])

            beach_l3 = prog_map[('Beachborn', '3')]
            self.assertIn(f'AddSpells({generator.SPELLLIST_BEACHBORN_L3}', beach_l3['Selectors'])
            beach_l5 = prog_map[('Beachborn', '5')]
            self.assertIn(f'AddSpells({generator.SPELLLIST_BEACHBORN_L5}', beach_l5['Selectors'])

            silicon_l3 = prog_map[('Siliconite', '3')]
            self.assertIn(f'AddSpells({generator.SPELLLIST_SILICONITE_L3}', silicon_l3['Selectors'])
            silicon_l5 = prog_map[('Siliconite', '5')]
            self.assertIn(f'AddSpells({generator.SPELLLIST_SILICONITE_L5}', silicon_l5['Selectors'])

            inland_l1 = prog_map[('InlandEmperor', '1')]
            self.assertIn('Passive_SmogLungs', inland_l1['PassivesAdded'])
            self.assertIn(f'AddSpells({generator.SPELLLIST_INLANDEMPEROR_L1}', inland_l1['Selectors'])
            inland_l3 = prog_map[('InlandEmperor', '3')]
            self.assertIn(f'AddSpells({generator.SPELLLIST_INLANDEMPEROR_L3}', inland_l3['Selectors'])
            inland_l5 = prog_map[('InlandEmperor', '5')]
            self.assertIn(f'AddSpells({generator.SPELLLIST_INLANDEMPEROR_L5}', inland_l5['Selectors'])

    def test_missing_progression_fails_instead_of_orphaning_spell(self):
        with tempfile.TemporaryDirectory() as directory:
            public = Path(directory)
            (public / 'Lists').mkdir()
            (public / 'Progressions').mkdir()
            (public / 'Lists/SpellLists.lsx').write_text('<save>\n            </children>\n</save>')
            (public / 'Progressions/Progressions.lsx').write_text('<save/>')
            with patch.object(generator, 'PUBLIC_DIR', str(public)):
                with self.assertRaisesRegex(ValueError, 'lack progression nodes'):
                    generator.generate_local_expansion()


if __name__ == '__main__':
    unittest.main()
