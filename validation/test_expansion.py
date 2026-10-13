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
            self.assertEqual(len(new_lists), 19)
            progressions = ET.parse(public / 'Progressions/Progressions.lsx')
            selectors = ';'.join(a.get('value', '') for a in progressions.findall('.//attribute[@id="Selectors"]'))
            for uid in new_lists:
                self.assertIn(uid, selectors)
            expected = {('HomelessCalifornian', '4'): 'HC_Target_CoatHangerSlimJim',
                        ('TenderloinBiohazard', '6'): 'HC_Target_CurbsideClinic',
                        ('HomelessCalifornian', '5'): 'HC_Target_GuiltTrip',
                        ('HomelessCalifornian', '6'): 'HC_Target_PublicScene',
                        ('HomelessCalifornian', '8'): 'HC_Target_TrappedInTheInvisibleBox',
                        ('HomelessCalifornian', '9'): 'HC_Zone_BucketDrumSolo',
                        ('HomelessCalifornian', '10'): 'HC_Target_CompassionBurnout',
                        ('HomelessCalifornian', '11'): 'HC_Projectile_PuncturedLithiumCell',
                        ('VeniceBoardwalkBrawler', '6'): 'HC_Target_Sublet',
                        ('TenderloinBiohazard', '10'): 'HC_Target_EverybodyKnowsThisGuy'}
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
            self.assertEqual(len(options.find('attribute[@id="Passives"]').get('value').split(',')), 3)
            self.assertEqual(selectors.count(f'SelectPassives({trade_list},1,HCStreetTrade)'), 1)
            doctrine_list = generator.get_guid('HC_JunkDoctrine_List')
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
