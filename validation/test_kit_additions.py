"""Checks for the three small boost-only additions (run on a freshly generated temp tree).

* HC_StreetTrade_SqueegeeTechnician - Street Trade option (level 2 selector)
* HC_JunkDoctrine_CardboardInsulator - Junk Doctrine option (level 4 selector)
* HC_NimbyZoningDefense - base Californian race passive (race level 1)

Boost syntax and icon names are proved against the local vanilla extraction in temp_race.
"""
from pathlib import Path
import contextlib
import io
import re
import sys
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'validation'))
import generate_mod as generator
import validate as validator
from test_spell_rules import parse_entries

TRADE = 'HC_StreetTrade_SqueegeeTechnician'
DOCTRINE = 'HC_JunkDoctrine_CardboardInsulator'
RACIAL = 'HC_NimbyZoningDefense'
ORIGINAL_RACIAL = ['EarthquakeSense', 'Veteran405', 'RunyonCanyonGlutes']
EXPECTED_BOOSTS = {
    TRADE: 'Advantage(Skill,Intimidation);Advantage(Skill,Insight)',
    DOCTRINE: 'Resistance(Cold,Resistant)',
    RACIAL: 'Tag(CHARMED_ADV)',
}
# Every function/argument combination used by the new boosts, with the vanilla files that prove it.
VANILLA_BOOST_EVIDENCE = ['Advantage(Skill,Intimidation)', 'Advantage(Skill,Insight)',
                          'Resistance(Cold,Resistant)', 'Tag(CHARMED_ADV)']
FORBIDDEN_IN_DOCTRINE = ('HC_Junk', 'RestoreResource', 'ActionResource', 'StatsFunctors', 'UnlockSpell')


def attrs_of(node):
    return {a.get('id'): a.get('value', '') for a in node.findall('attribute')}


def squash(text):
    return re.sub(r'\s+', '', text)


class KitAdditionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.source = Path(cls._tmp.name)
        cls.public = cls.source / 'Public/HomelessCalifornian'
        with patch.object(generator, 'PUBLIC_DIR', str(cls.public)), \
                patch.object(generator, 'MODS_DIR', str(cls.source / 'Mods/HomelessCalifornian')), \
                contextlib.redirect_stdout(io.StringIO()):
            generator.main()
        data = cls.public / 'Stats/Generated/Data'
        cls.passives = {}
        for name in ('HC_Passives_Choices.txt', 'HC_Passives_Doctrines.txt', 'Passive.txt'):
            cls.passives.update(parse_entries((data / name).read_text(encoding='utf-8')))
        cls.progressions = [attrs_of(n) for n in
                            ET.parse(cls.public / 'Progressions/Progressions.lsx').findall('.//node[@id="Progression"]')]
        cls.passive_lists = {}
        for node in ET.parse(cls.public / 'Lists/PassiveLists.lsx').findall('.//node[@id="PassiveList"]'):
            a = attrs_of(node)
            cls.passive_lists[a['UUID']] = a['Passives'].split(',')
        loca = ET.parse(cls.public / 'Localization/English/HomelessCalifornian.loca.xml')
        cls.loca = {c.get('contentuid'): c.text for c in loca.iter('content')}
        cls.vanilla_text = ''
        for path in (ROOT / 'temp_race/Public').rglob('*.txt'):
            if 'Stats' in path.parts:
                cls.vanilla_text += squash(path.read_text(encoding='utf-8-sig', errors='replace')) + '\n'
        cls.vanilla_stats = validator.read_stats(ROOT / 'temp_race')

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def level_progression(self, name, level):
        found = [a for a in self.progressions if a.get('Name') == name and a.get('Level') == level
                 and a.get('ProgressionType') in ('0', '2')]
        self.assertEqual(len(found), 1, f'{name} level {level}')
        return found[0]

    # ------------------------------------------------------------ passives exist
    def test_new_passives_exist_and_are_boost_only(self):
        for key, boosts in EXPECTED_BOOSTS.items():
            with self.subTest(key=key):
                self.assertIn(key, self.passives)
                entry = self.passives[key]['data']
                self.assertEqual(entry['Boosts'], boosts)
                self.assertEqual(self.passives[key].get('using'), None)
                for forbidden in ('StatsFunctors', 'StatsFunctorContext', 'Conditions', 'ToggleOnFunctors',
                                  'ToggleOffFunctors', 'ToggleGroup', 'IsToggled'):
                    self.assertNotIn(forbidden, entry, f'{key} must be boost-only')

    def test_doctrine_gives_no_junk_refund_or_loop(self):
        boosts = self.passives[DOCTRINE]['data']['Boosts']
        for token in FORBIDDEN_IN_DOCTRINE:
            self.assertNotIn(token, boosts)
        description = self.loca[self.passives[DOCTRINE]['data']['Description'].split(';')[0]]
        self.assertNotIn('Junk', description)

    # --------------------------------------------------------- selector wiring
    def test_street_trade_selector_wiring(self):
        uid = generator.get_guid('HC_StreetTrade_List')
        options = self.passive_lists[uid]
        self.assertEqual(len(options), 9)
        self.assertEqual(options.count(TRADE), 1)
        self.assertEqual(options[:5], ['HC_StreetTrade_Scrounger', 'HC_StreetTrade_Fixer', 'HC_StreetTrade_Lookout',
                                       'HC_StreetTrade_CanCollector', 'HC_StreetTrade_Busker'])
        level2 = self.level_progression('HomelessCalifornian', '2')
        self.assertEqual(level2['Selectors'].count(f'SelectPassives({uid},1,HCStreetTrade)'), 1)
        for option in options:
            self.assertIn(option, self.passives)

    def test_junk_doctrine_selector_wiring(self):
        uid = generator.get_guid('HC_JunkDoctrine_List')
        options = self.passive_lists[uid]
        self.assertEqual(len(options), 8)
        self.assertEqual(options.count(DOCTRINE), 1)
        self.assertEqual(options[:4], ['HC_JunkDoctrine_Hoarder', 'HC_JunkDoctrine_Fortifier',
                                       'HC_JunkDoctrine_Runner', 'HC_JunkDoctrine_Twitchy'])
        level4 = self.level_progression('HomelessCalifornian', '4')
        self.assertEqual(level4['Selectors'].count(f'SelectPassives({uid},1,HCJunkDoctrine)'), 1)
        for option in options:
            self.assertIn(option, self.passives)

    def test_nimby_is_in_californian_level_one_kit_only(self):
        level1 = self.level_progression('Californian', '1')
        granted = level1['PassivesAdded'].split(';')
        self.assertEqual(granted, ORIGINAL_RACIAL + [RACIAL, 'HC_WeatherComplaint',
                         'HC_WeatherComplaint_WET', 'HC_WeatherComplaint_CHILLED', 'HC_WeatherComplaint_ICE'])
        # Not granted by any other progression, list or selector (no subrace or class double-dip).
        holders = [a for a in self.progressions
                   if RACIAL in re.split(r'[;,]', a.get('PassivesAdded', '')) or RACIAL in a.get('Selectors', '')]
        self.assertEqual(holders, [level1])
        for options in self.passive_lists.values():
            self.assertNotIn(RACIAL, options)

    # ------------------------------------------------------------------- loca
    def test_names_and_descriptions_have_loca(self):
        for key in EXPECTED_BOOSTS:
            entry = self.passives[key]['data']
            for field in ('DisplayName', 'Description'):
                handle, version = entry[field].split(';')
                self.assertEqual(version, '1')
                self.assertIn(handle, self.loca, f'{key}.{field}')
                self.assertTrue(self.loca[handle].strip())
        names = {self.loca[self.passives[k]['data']['DisplayName'].split(';')[0]]: k for k in EXPECTED_BOOSTS}
        self.assertEqual(set(names), {'Squeegee Technician', 'Cardboard Insulator', 'NIMBY Zoning Defense'})

    def test_no_new_handle_collides_with_other_text(self):
        handles = [self.passives[k]['data'][f].split(';')[0] for k in EXPECTED_BOOSTS
                   for f in ('DisplayName', 'Description')]
        self.assertEqual(len(set(handles)), 6)

    # --------------------------------------------------------------- icons
    def test_icons_are_vanilla_or_shipped_custom_art(self):
        # The atlas is built by build_icons.py into the committed source tree, not by generate_mod.py.
        atlas = ET.parse(ROOT / 'src/HomelessCalifornian/Public/HomelessCalifornian/GUI/Icons_Items.lsx')
        shipped = {a.get('value') for a in atlas.iter('attribute') if a.get('id') == 'MapKey'}
        vanilla_icons = {st[-1].fields.get('Icon') for st in self.vanilla_stats.values()}
        for key in EXPECTED_BOOSTS:
            icon = self.passives[key]['data']['Icon']
            with self.subTest(key=key):
                if icon in vanilla_icons:
                    continue
                self.assertIn(icon, shipped, f'{key}: icon {icon} is neither vanilla nor in the shipped atlas')
                self.assertTrue((ROOT / 'assets/icons' / (icon + '.png')).is_file(), icon)

    # ----------------------------------------------------- vanilla evidence
    def test_boost_syntax_has_vanilla_evidence(self):
        for snippet in VANILLA_BOOST_EVIDENCE:
            with self.subTest(snippet=snippet):
                self.assertIn(squash(snippet), self.vanilla_text, f'{snippet} not found in temp_race vanilla stats')

    def test_every_boost_in_new_passives_is_covered_by_evidence(self):
        used = []
        for boosts in EXPECTED_BOOSTS.values():
            used.extend(boosts.split(';'))
        self.assertEqual(sorted(set(used)), sorted(VANILLA_BOOST_EVIDENCE))

    def test_skill_names_are_vanilla_skills(self):
        for skill in re.findall(r'Advantage\(Skill,(\w+)\)', self.passives[TRADE]['data']['Boosts']):
            self.assertIn(f'Advantage(Skill,{skill})', self.vanilla_text)


if __name__ == '__main__':
    unittest.main()
