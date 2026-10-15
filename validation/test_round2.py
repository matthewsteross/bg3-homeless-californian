"""Round 2 additions (run on a freshly generated temp tree).

Spec: work/spec-round2.md.
* Four base-class Junk spells: Catalytic Converter Sawzall, Sprinkler Violation, HOV Lane, One-Star Citation
* Inland Emperor level 3 racial spell: Bakersfield Tule Fog
* Street Trade option Notary, Junk Doctrine option Tinfoil Deflector

Donors, statuses, boosts, surfaces and icons are proved against the local vanilla extraction in temp_race.
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

BASE_GRANTS = {'2': 'HC_Target_SprinklerViolation', '4': 'HC_Target_CatalyticConverterSawzall',
               '8': 'HC_Target_OneStarCitation', '11': 'HC_Target_HOVLane'}
SPELLS = list(BASE_GRANTS.values()) + ['HC_Target_TuleFog']
NOTARY = 'HC_StreetTrade_Notary'
TINFOIL = 'HC_JunkDoctrine_TinfoilDeflector'
DONORS = {'HC_Target_CatalyticConverterSawzall': 'Target_InflictWounds',
          'HC_Target_SprinklerViolation': 'Target_CreateWater',
          'HC_Target_HOVLane': 'Target_MistyStep',
          'HC_Target_OneStarCitation': 'Target_ViciousMockery',
          'HC_Target_TuleFog': 'Target_FogCloud'}
# Every functor / boost snippet the new data relies on, with vanilla proof (whitespace-insensitive).
VANILLA_EVIDENCE = [
    'GROUND:TeleportSource()', 'GROUND:CreateSurface(4.5,10,FogCloud,true)', 'ApplyStatus(WET,100,3)',
    'GROUND:CreateSurface(4,0,Water)', 'Attack(AttackType.MeleeSpellAttack)', 'ApplyStatus(BANE,100,10)',
    'DealDamage(2d8,Psychic,Magical)', 'GROUND:CreateSurface(2,2,DarknessCloud)',
    'AC(-2)', 'ActionResourceBlock(ReactionActionPoint)',
    # Advantage(Skill,Investigation) has no vanilla use; Investigation is proved as a Skill enum value instead,
    # and the shipped Scrounger trade already uses the same boost shape.
    'ProficiencyBonus(Skill,Investigation)', 'Advantage(Skill,Persuasion)', 'Resistance(Psychic,Resistant)',
]


def attrs_of(node):
    return {a.get('id'): a.get('value', '') for a in node.findall('attribute')}


def squash(text):
    return re.sub(r'\s+', '', text)


class RoundTwoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        source = Path(cls._tmp.name)
        cls.public = source / 'Public/HomelessCalifornian'
        with patch.object(generator, 'PUBLIC_DIR', str(cls.public)), \
                patch.object(generator, 'MODS_DIR', str(source / 'Mods/HomelessCalifornian')), \
                contextlib.redirect_stdout(io.StringIO()):
            generator.main()
        data = cls.public / 'Stats/Generated/Data'
        cls.spells = parse_entries((data / 'HC_Spells_Round2.txt').read_text(encoding='utf-8'))
        cls.statuses = parse_entries((data / 'HC_Status_Round2.txt').read_text(encoding='utf-8'))
        cls.passives = {}
        for name in ('HC_Passives_Choices.txt', 'HC_Passives_Doctrines.txt'):
            cls.passives.update(parse_entries((data / name).read_text(encoding='utf-8')))
        cls.progressions = [attrs_of(n) for n in
                            ET.parse(cls.public / 'Progressions/Progressions.lsx').findall('.//node[@id="Progression"]')]
        cls.spell_lists = {}
        for node in ET.parse(cls.public / 'Lists/SpellLists.lsx').findall('.//node[@id="SpellList"]'):
            a = attrs_of(node)
            cls.spell_lists[a['UUID']] = a['Spells'].split(';')
        cls.passive_lists = {}
        for node in ET.parse(cls.public / 'Lists/PassiveLists.lsx').findall('.//node[@id="PassiveList"]'):
            a = attrs_of(node)
            cls.passive_lists[a['UUID']] = a['Passives'].split(',')
        loca = ET.parse(cls.public / 'Localization/English/HomelessCalifornian.loca.xml')
        cls.loca = {c.get('contentuid'): c.text for c in loca.iter('content')}
        cls.vanilla_stats = validator.read_stats(ROOT / 'temp_race')
        cls.vanilla_text = ''
        for path in (ROOT / 'temp_race/Public').rglob('*.txt'):
            if 'Stats' in path.parts:
                cls.vanilla_text += squash(path.read_text(encoding='utf-8-sig', errors='replace')) + '\n'

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def description(self, entry):
        return self.loca[entry['data']['Description'].split(';')[0]]

    def progression(self, name, level):
        found = [a for a in self.progressions if a.get('Name') == name and a.get('Level') == level
                 and a.get('ProgressionType') in ('0', '2')]
        self.assertEqual(len(found), 1, f'{name} level {level}')
        return found[0]

    def granted_spells(self, progression):
        names = []
        for uid in re.findall(r'AddSpells\(([0-9a-f-]{36})', progression.get('Selectors', '')):
            names.extend(self.spell_lists[uid])
        return names

    # ------------------------------------------------------------------ wiring
    def test_all_five_spells_and_status_exist(self):
        for name in SPELLS:
            with self.subTest(name=name):
                self.assertIn(name, self.spells)
                self.assertEqual(self.spells[name]['using'], DONORS[name])
        self.assertIn('HC_DECAT_EXHAUST', self.statuses)

    def test_each_base_spell_is_granted_at_its_level_and_only_there(self):
        for level, spell in BASE_GRANTS.items():
            with self.subTest(level=level):
                self.assertIn(spell, self.granted_spells(self.progression('HomelessCalifornian', level)))
        for a in self.progressions:
            if a.get('ProgressionType') == '1' or a.get('Name') != 'HomelessCalifornian':
                continue
            for spell in self.granted_spells(a):
                if spell in BASE_GRANTS.values():
                    self.assertEqual(BASE_GRANTS[a['Level']], spell, f'{spell} granted at level {a["Level"]}')

    def test_at_most_one_new_spell_per_class_level(self):
        self.assertEqual(len(set(BASE_GRANTS)), len(BASE_GRANTS))
        for a in self.progressions:
            if a.get('Name') == 'HomelessCalifornian':
                new = [s for s in self.granted_spells(a) if s in BASE_GRANTS.values()]
                self.assertLessEqual(len(new), 1, f'level {a["Level"]}')

    def test_tule_fog_is_inland_emperor_level_three_only(self):
        level3 = self.progression('InlandEmperor', '3')
        self.assertIn('AddSpells(' + generator.SPELLLIST_INLANDEMPEROR_L3, level3['Selectors'])
        self.assertEqual(self.spell_lists[generator.SPELLLIST_INLANDEMPEROR_L3], ['Zone_OverpassExhaust', 'HC_Target_TuleFog'])
        for a in self.progressions:
            if a is not level3:
                self.assertNotIn('HC_Target_TuleFog', self.granted_spells(a))

    def test_street_trade_and_doctrine_selector_membership(self):
        trade = self.passive_lists[generator.get_guid('HC_StreetTrade_List')]
        doctrine = self.passive_lists[generator.get_guid('HC_JunkDoctrine_List')]
        self.assertEqual(trade.count(NOTARY), 1)
        self.assertEqual(doctrine.count(TINFOIL), 1)
        self.assertIn(NOTARY, self.passives)
        self.assertIn(TINFOIL, self.passives)

    # ---------------------------------------------------------- spell contents
    def test_junk_costs_and_cooldowns(self):
        expected = {
            'HC_Target_CatalyticConverterSawzall': ('ActionPoint:1;HC_Junk:1', 'OncePerShortRest'),
            'HC_Target_SprinklerViolation': ('BonusActionPoint:1;HC_Junk:1', 'OncePerShortRest'),
            'HC_Target_HOVLane': ('BonusActionPoint:1;HC_Junk:1', 'OncePerShortRest'),
            'HC_Target_OneStarCitation': ('ActionPoint:1;HC_Junk:1', ''),
            'HC_Target_TuleFog': ('ActionPoint:1', 'OncePerShortRest'),
        }
        for name, (cost, cooldown) in expected.items():
            with self.subTest(name=name):
                d = self.spells[name]['data']
                self.assertEqual(d['UseCosts'], cost)
                self.assertEqual(d['Cooldown'], cooldown)
                self.assertEqual(d['Level'], '0')
                self.assertEqual(d['MemoryCost'], '0')
                self.assertEqual(d['TooltipUpcastDescription'], '')

    def test_sawzall_is_a_melee_spell_attack_with_decat_status(self):
        d = self.spells['HC_Target_CatalyticConverterSawzall']['data']
        self.assertEqual(d['TargetRadius'], '1.5')
        self.assertEqual(d['SpellRoll'], 'Attack(AttackType.MeleeSpellAttack)')
        self.assertEqual(d['SpellSuccess'], 'DealDamage(3d8,Slashing,Magical);ApplyStatus(HC_DECAT_EXHAUST,100,2)')
        self.assertEqual(d['DamageType'], 'Slashing')
        self.assertEqual(d['TooltipDamageList'], 'DealDamage(3d8,Slashing)')
        status = self.statuses['HC_DECAT_EXHAUST']['data']
        self.assertEqual(status['Boosts'], 'AC(-2);ActionResourceBlock(ReactionActionPoint)')
        self.assertEqual(status['StatusType'], 'BOOST')

    def test_sprinkler_violation_creates_water_and_applies_wet(self):
        d = self.spells['HC_Target_SprinklerViolation']['data']
        self.assertEqual(d['TargetRadius'], '9')
        self.assertEqual(d['SpellContainerID'], '')
        self.assertEqual(d['SpellProperties'], 'ApplyStatus(WET,100,3);GROUND:CreateSurface(2,2,Water)')
        self.assertIn('WET', self.vanilla_stats)

    def test_hov_lane_teleports_12m_without_a_surface(self):
        d = self.spells['HC_Target_HOVLane']['data']
        self.assertEqual(d['TargetRadius'], '12')
        self.assertEqual(d['SpellProperties'], 'GROUND:TeleportSource()')
        self.assertNotIn('CreateSurface', d['SpellProperties'])
        self.assertTrue(self.vanilla_stats['Target_MistyStep'][-1].fields['SpellProperties'].startswith('GROUND:TeleportSource()'))

    def test_one_star_citation_damage_and_wisdom_save_for_bane(self):
        d = self.spells['HC_Target_OneStarCitation']['data']
        self.assertEqual(d['TargetRadius'], '9')
        self.assertEqual(d['SpellProperties'], 'DealDamage(2d8,Psychic,Magical)')
        self.assertIn('SavingThrow(Ability.Wisdom', d['SpellRoll'])
        self.assertEqual(d['SpellSuccess'], 'ApplyStatus(BANE,100,2)')
        self.assertIn('BANE', self.vanilla_stats)

    def test_tule_fog_is_a_two_turn_four_metre_cloud_without_concentration(self):
        d = self.spells['HC_Target_TuleFog']['data']
        self.assertEqual(d['TargetRadius'], '9')
        self.assertEqual(d['AreaRadius'], '4')
        self.assertEqual(d['SpellProperties'], 'GROUND:CreateSurface(4,2,FogCloud)')
        self.assertNotIn('IsConcentration', d['SpellFlags'].split(';'))

    def test_no_script_model_reaction_or_junk_refund_features(self):
        for name in SPELLS + ['HC_DECAT_EXHAUST', NOTARY, TINFOIL]:
            entry = (self.spells.get(name) or self.statuses.get(name) or self.passives[name])
            body = ' '.join(entry['data'].values())
            for token in ('RestoreResource', 'Reaction:', 'Interrupt', 'Script', 'Mesh'):
                self.assertNotIn(token, body.replace('ActionResourceBlock(ReactionActionPoint)', ''), name)

    # ------------------------------------------------------------ passives
    def test_notary_and_tinfoil_boosts(self):
        self.assertEqual(self.passives[NOTARY]['data']['Boosts'], 'Advantage(Skill,Investigation);Advantage(Skill,Persuasion)')
        self.assertEqual(self.passives[TINFOIL]['data']['Boosts'], 'Resistance(Psychic,Resistant)')
        for key in (NOTARY, TINFOIL):
            self.assertEqual(self.passives[key]['data']['Properties'], 'Highlighted')
            self.assertIsNone(self.passives[key].get('using'))

    def test_tinfoil_does_not_duplicate_nimby_charm_advantage(self):
        self.assertNotIn('Advantage', self.passives[TINFOIL]['data']['Boosts'])
        self.assertNotIn('Charm', self.passives[TINFOIL]['data']['Boosts'])

    # ---------------------------------------------------------------- loca
    def test_names_and_descriptions_have_loca_with_exact_numbers(self):
        titles = {'HC_Target_CatalyticConverterSawzall': 'Catalytic Converter Sawzall',
                  'HC_Target_SprinklerViolation': 'Sprinkler Violation', 'HC_Target_HOVLane': 'HOV Lane',
                  'HC_Target_OneStarCitation': 'One-Star Citation', 'HC_Target_TuleFog': 'Bakersfield Tule Fog',
                  'HC_DECAT_EXHAUST': 'Decatted Exhaust', NOTARY: 'Notary', TINFOIL: 'Tinfoil Deflector'}
        for name, title in titles.items():
            entry = self.spells.get(name) or self.statuses.get(name) or self.passives[name]
            with self.subTest(name=name):
                for field in ('DisplayName', 'Description'):
                    handle, version = entry['data'][field].split(';')
                    self.assertEqual(version, '1')
                    self.assertTrue(self.loca[handle].strip(), f'{name}.{field}')
                self.assertEqual(self.loca[entry['data']['DisplayName'].split(';')[0]], title)
        numbers = {'HC_Target_CatalyticConverterSawzall': ['3d8 Slashing', '1.5 m', '-2 AC', '2 turns', '1 Junk'],
                   'HC_Target_SprinklerViolation': ['9 m', '2 m', '2 turns', '3 turns', '1 Junk'],
                   'HC_Target_HOVLane': ['12 m', '1 Junk'],
                   'HC_Target_OneStarCitation': ['2d8 Psychic', '9 m', '2 turns', '1d4', '1 Junk'],
                   'HC_Target_TuleFog': ['9 m', '4 m', '2 turns']}
        for name, parts in numbers.items():
            text = self.description(self.spells[name])
            for part in parts:
                self.assertIn(part, text, name)

    def test_flavour_sentence_comes_last(self):
        for name in SPELLS:
            text = self.description(self.spells[name])
            self.assertTrue(text.endswith('.'), name)
            self.assertNotRegex(text.split('. ')[-1], r'\d', f'{name}: last sentence should be flavour, not numbers')

    def test_no_new_handle_collides(self):
        keys = SPELLS + ['HC_DECAT_EXHAUST', NOTARY, TINFOIL]
        handles = []
        for key in keys:
            entry = self.spells.get(key) or self.statuses.get(key) or self.passives[key]
            handles += [entry['data'][f].split(';')[0] for f in ('DisplayName', 'Description')]
        self.assertEqual(len(handles), len(set(handles)))

    # ----------------------------------------------------- vanilla evidence
    def test_donors_and_referenced_statuses_exist_in_vanilla(self):
        for donor in DONORS.values():
            self.assertIn(donor, self.vanilla_stats, donor)
            self.assertEqual(self.vanilla_stats[donor][-1].type, 'SpellData')
        for status in ('WET', 'BANE', 'SAVED_AGAINST_HOSTILE_SPELL'):
            self.assertEqual(self.vanilla_stats[status][-1].type, 'StatusData', status)

    def test_functor_and_boost_syntax_has_vanilla_evidence(self):
        for snippet in VANILLA_EVIDENCE:
            with self.subTest(snippet=snippet):
                self.assertTrue(squash(snippet) in self.vanilla_text, f'{snippet} not found in temp_race vanilla stats')

    def test_icons_are_vanilla(self):
        vanilla_icons = {st[-1].fields.get('Icon') for st in self.vanilla_stats.values()}
        for name in SPELLS + ['HC_DECAT_EXHAUST', NOTARY, TINFOIL]:
            entry = self.spells.get(name) or self.statuses.get(name) or self.passives[name]
            icon = entry['data']['Icon']
            with self.subTest(name=name):
                custom = ROOT / 'assets/icons' / (icon + '.png')
                self.assertTrue(icon in vanilla_icons or custom.is_file(), icon)

    def test_vanilla_keys_are_not_redefined(self):
        for name in SPELLS + ['HC_DECAT_EXHAUST', NOTARY, TINFOIL]:
            self.assertNotIn(name, self.vanilla_stats)


if __name__ == '__main__':
    unittest.main()
