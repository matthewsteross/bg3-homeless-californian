from pathlib import Path
import re
import tempfile
import unittest
import xml.etree.ElementTree as ET
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'validation'))
import generate_mod as generator
import hc_round13_items as r
import validate

LAYERS = ('Shared', 'SharedDev', 'Gustav', 'GustavDev', 'Honour')


class RoundThirteenItemTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.public = Path(cls.tmp.name) / 'Public/HomelessCalifornian'
        fixture_spell = cls.public / 'Stats/Generated/Data/FixtureSpell.txt'
        fixture_spell.parent.mkdir(parents=True, exist_ok=True)
        fixture_spell.write_text('new entry "HC_Shout_GloveBoxCleanout"\ntype "SpellData"\ndata "SpellProperties" ""\n', encoding='utf-8')
        with patch.dict(generator.LOCA_ENTRIES, {}, clear=True):
            cls.grants = r.generate_round13_items(cls.public, generator.add_loca, generator.get_guid)
            cls.loca = dict(generator.LOCA_ENTRIES)
        cls.stats = validate.read_stats(cls.public)
        cls.entries = {name: entries[0] for name, entries in cls.stats.items() if name != 'HC_Shout_GloveBoxCleanout'}
        cls.vanilla = validate.read_stats(ROOT / 'temp_race')
        cls.vanilla_text = '\n'.join(p.read_text(encoding='utf-8-sig') for layer in LAYERS for p in (ROOT / 'temp_race/Public' / layer / 'Stats/Generated/Data').glob('*.txt'))
        cls.norm = staticmethod(lambda s: re.sub(r'\s+', '', s))
        cls.corpus = cls.norm(cls.vanilla_text)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def f(self, name):
        return self.entries[name].fields

    def test_unique_names_descriptions_and_return_contract(self):
        expected = {i[0] for i in r.ITEMS} | {s[0] for s in r.STATUS_SPECS} | {r.BATTERY_PROJECTILE}
        self.assertEqual(set(self.entries), expected)
        self.assertEqual(self.grants, {'base': {}, 'subclasses': {}, 'existing_list_spells': {}})
        for name in expected:
            self.assertTrue(name.startswith('HC_'))
            self.assertEqual(len(self.stats[name]), 1)
            self.assertNotIn(name, self.vanilla)
            if name in {item[0] for item in r.ITEMS}:
                desc = self.loca[generator.get_handle(name + '_Description')]
                self.assertTrue(3 <= len(re.findall(r'\.(?:\s|$)', desc)) <= 5, (name, desc))
                self.assertNotIn('"', desc)

    def test_item_donors_roots_actions_and_effects(self):
        nodes = ET.parse(self.public / 'RootTemplates/HC_Round13Items.lsf.lsx').findall('.//node[@id="GameObjects"]')
        self.assertEqual(len(nodes), 3)
        for name, kind, donor, parent, icon, title, description, rarity in r.ITEMS:
            entry = self.f(name)
            self.assertEqual(entry['Rarity'], rarity)
            self.assertEqual(entry['ValueOverride'], '0')
            self.assertTrue(any(e.type == self.entries[name].type for e in self.vanilla[donor]))
            obj = next(n for n in nodes if any(a.get('id') == 'Stats' and a.get('value') == name for a in n.findall('attribute')))
            attrs = {a.get('id'): a.get('value') for a in obj.findall('attribute')}
            self.assertEqual(attrs['ParentTemplateId'], parent)
            self.assertEqual(entry['RootTemplate'], attrs['MapKey'])
            if name in (r.GUMMY, r.BROTH):
                action = {a.get('id'): a.get('value') for a in obj.findall('.//node[@id="Attributes"]/attribute')}
                self.assertEqual(action['Consume'], 'True')
                self.assertEqual(action['StatsId'], r.GUMMY_USE if name == r.GUMMY else r.BROTH_USE)
                self.assertEqual(entry['UseCosts'], 'BonusActionPoint:1')
        self.assertIn('TemporaryHP(20)', self.f(r.GUMMY_STATUS)['Boosts'])
        self.assertIn('Resistance(Psychic, Resistant)', self.f(r.GUMMY_STATUS)['Boosts'])
        self.assertIn('Disadvantage(SavingThrow,Dexterity)', self.f(r.GUMMY_STATUS)['Boosts'])
        self.assertEqual(self.f(r.GUMMY_USE)['OnApplyFunctors'], f'ApplyStatus({r.GUMMY_STATUS},100,3)')
        self.assertEqual(self.f(r.BROTH_USE)['OnApplyFunctors'], 'RemoveStatus(SG_Poisoned);RegainHitPoints(3d8+4)')

    def test_grenade_projectile_pattern_and_vanilla_functor_precedent(self):
        f = self.f(r.BATTERY_PROJECTILE)
        self.assertEqual(f['TargetRadius'], '18')
        self.assertEqual(f['AreaRadius'], '3')
        self.assertEqual(f['SpellRoll'], 'not SavingThrow(Ability.Dexterity, SourceSpellDC())')
        self.assertEqual(f['SpellSuccess'], 'DealDamage(3d10,Lightning,Magical);DealDamage(2d6,Fire,Magical)')
        self.assertEqual(f['SpellFail'], 'DealDamage((3d10)/2,Lightning,Magical);DealDamage((2d6)/2,Fire,Magical)')
        self.assertEqual(self.f(r.BATTERY)['ItemUseType'], 'Grenade')
        for token in ('TemporaryHP(20)', 'Resistance(Psychic,Resistant)', 'Disadvantage(SavingThrow,Dexterity)', 'RegainHitPoints(', 'RemoveStatus(SG_Poisoned)', 'SavingThrow(Ability.Dexterity,SourceSpellDC())', 'Projectile_AcidSplash'):
            self.assertIn(self.norm(token), self.corpus)
        self.assertIn('new entry "_Grenade"', self.vanilla_text)

    def test_glovebox_patch_preserves_existing_and_is_idempotent(self):
        isolated = tempfile.TemporaryDirectory()
        self.addCleanup(isolated.cleanup)
        path = Path(isolated.name) / 'Fixture.txt'
        old = 'new entry "HC_Shout_GloveBoxCleanout"\ntype "SpellData"\ndata "SpellProperties" "KeepThis();SummonInInventory(legacy,-1,1,false,false,false)"\ndata "Other" "keep"\n'
        path.write_text(old, encoding='utf-8')
        guids = {name: 'guid_' + name for name in (r.GUMMY, r.BROTH, r.BATTERY)}
        r.patch_round13_glovebox_spell(path.parent, guids)
        first = path.read_text(encoding='utf-8')
        r.patch_round13_glovebox_spell(path.parent, guids)
        self.assertEqual(path.read_text(encoding='utf-8'), first)
        self.assertIn('KeepThis()', first)
        self.assertIn('SummonInInventory(legacy,-1,1,false,false,false)', first)
        self.assertIn('data "Other" "keep"', first)
        for guid in guids.values():
            self.assertEqual(first.count(f'SummonInInventory({guid},-1,1,false,false,false)'), 1)

    def test_validator_passes_with_resource_and_localization_fixture(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp)
            public = source / 'Public/HomelessCalifornian'
            spell_file = public / 'Stats/Generated/Data/FixtureSpell.txt'
            spell_file.parent.mkdir(parents=True, exist_ok=True)
            spell_file.write_text('new entry "HC_Shout_GloveBoxCleanout"\ntype "SpellData"\ndata "SpellProperties" ""\n', encoding='utf-8')
            with patch.dict(generator.LOCA_ENTRIES, {}, clear=True):
                r.generate_round13_items(public, generator.add_loca, generator.get_guid)
                loca = ET.Element('contentList')
                for handle, value in generator.LOCA_ENTRIES.items():
                    ET.SubElement(loca, 'content', contentuid=handle, version='1').text = value
            ET.ElementTree(loca).write(public / 'TestLocalization.lsx', encoding='utf-8')
            icons = ET.Element('save')
            for icon_key in set(__import__('hc_icon_keys').SPELL_ICON_KEYS.values()):
                ET.SubElement(ET.SubElement(icons, 'node', id='IconFixture'), 'attribute', id='MapKey', value=icon_key)
            ET.ElementTree(icons).write(public / 'TestIcons.lsx', encoding='utf-8')
            errors, counts = validate.validate(source, ROOT / 'temp_race')
            self.assertEqual(errors, [])
            self.assertEqual(counts['stats'], len(self.entries) + 1)


if __name__ == '__main__':
    unittest.main()
