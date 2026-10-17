"""Round 8 file-level contracts (base L4/L6/L10/L11, subclass L10/L12, Californian L1, Siliconite L1).

The generator is not wired into generate_mod.py by this module's author, so these tests run
generate_round8() against a temporary copy of the built src/ tree and validate the combined result.
"""
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from xml.sax.saxutils import escape
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'validation'))
import generate_mod as generator
import hc_round8 as round8
import validate

SRC = ROOT / 'src/HomelessCalifornian'
VANILLA_LAYERS = ('Shared', 'SharedDev', 'Gustav', 'GustavDev')

EXPECTED_SPELLS = {
    round8.POTHOLE, round8.NIMBY_COMMENT, round8.UNFINISHED_BUSINESS, round8.BUDGET_HEARING,
    round8.CHIROPRACTIC, round8.BLACKOUT, round8.SUNGLASSES, round8.SEISMIC_RETROFIT,
    round8.HOT_BAR, round8.SCROLL_MEETING,
}
EXPECTED_STATUSES = {spec[0] for spec in round8.STATUS_SPECS}
ALLOWED_RESOURCES = {'ActionPoint', 'BonusActionPoint', 'ReactionActionPoint', 'HC_Junk'}


def split_top(text):
    depth, cur, parts = 0, '', []
    for ch in text:
        depth += ch in '(['
        depth -= ch in ')]'
        if ch == ';' and depth == 0:
            parts.append(cur.strip())
            cur = ''
        else:
            cur += ch
    if cur.strip():
        parts.append(cur.strip())
    return parts


class RoundEightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not SRC.is_dir():
            raise unittest.SkipTest('built src/HomelessCalifornian tree is missing')
        cls.tmp = tempfile.TemporaryDirectory()
        cls.source = Path(cls.tmp.name) / 'HomelessCalifornian'
        shutil.copytree(SRC, cls.source)
        cls.public = cls.source / 'Public/HomelessCalifornian'
        with patch.dict(generator.LOCA_ENTRIES, {}, clear=True):
            cls.grants = round8.generate_round8(cls.public, generator.add_loca, generator.get_guid)
            entries = dict(generator.LOCA_ENTRIES)
        loca_path = cls.public / 'Localization/English/HomelessCalifornian.loca.xml'
        loca = loca_path.read_text(encoding='utf-8')
        extra = ''.join(f'    <content contentuid="{h}" version="1">{escape(t)}</content>\n'
                        for h, t in entries.items() if f'contentuid="{h}"' not in loca)
        loca_path.write_text(loca.replace('</contentList>', extra + '</contentList>'), encoding='utf-8')
        cls.entries = entries
        cls.stats = validate.read_stats(cls.public)
        cls.vanilla = validate.read_stats(ROOT / 'temp_race')
        cls.new = {k: v[0] for k, v in cls.stats.items() if v[0].path.name.endswith('_Round8.txt')}
        cls.loca = {e.get('contentuid'): e.text for e in
                    ET.parse(loca_path).iter('content')}
        cls.progs = [cls.attrs(n) for n in ET.parse(cls.public / 'Progressions/Progressions.lsx')
                     .findall('.//node[@id="Progression"]')]
        cls.lists = {cls.attrs(n)['UUID']: cls.attrs(n)['Spells'].split(';') for n in
                     ET.parse(cls.public / 'Lists/SpellLists.lsx').findall('.//node[@id="SpellList"]')}
        corpus = []
        for layer in VANILLA_LAYERS:
            for p in (ROOT / 'temp_race/Public' / layer).rglob('*.txt'):
                corpus.append(p.read_text(encoding='utf-8-sig', errors='ignore'))
        cls.vanilla_text = re.sub(r',\s+', ',', '\n'.join(corpus))

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    @staticmethod
    def attrs(node):
        return {a.get('id'): a.get('value') for a in node.findall('attribute')}

    def fields(self, name):
        return self.new[name].fields

    # ---------------------------------------------------------------- structure
    def test_all_round8_entries_are_unique_prefixed_and_do_not_override_vanilla(self):
        self.assertEqual(set(self.new), EXPECTED_SPELLS | EXPECTED_STATUSES)
        self.assertEqual(len(EXPECTED_SPELLS), 10)
        self.assertEqual(len(self.new), 19)
        for name in self.new:
            self.assertTrue(name.startswith('HC_'))
            self.assertNotIn(name, self.vanilla)
            self.assertEqual(len(self.stats[name]), 1)

    def test_all_donors_exist_in_vanilla_and_none_are_honour_overridden(self):
        honour_names = {name for name, entries in self.vanilla.items()
                        if any('Honour' in e.path.parts for e in entries)}
        for name, entry in self.new.items():
            if entry.using:
                self.assertIn(entry.using, self.vanilla, name)
                self.assertTrue(any(e.type == entry.type for e in self.vanilla[entry.using]), name)
                self.assertNotIn(entry.using, honour_names, name)

    def test_repo_validator_passes_on_combined_tree(self):
        errors, counts = validate.validate(self.source, ROOT / 'temp_race')
        self.assertEqual(errors, [])
        self.assertGreaterEqual(counts['stats'], 240 + 19)

    def test_return_dict_contract(self):
        self.assertEqual(set(self.grants), {'base', 'subclasses', 'existing_list_spells'})
        self.assertEqual(self.grants['base'], {
            4: [round8.POTHOLE], 6: [round8.NIMBY_COMMENT],
            10: [round8.UNFINISHED_BUSINESS], 11: [round8.BUDGET_HEARING]})
        self.assertEqual(self.grants['subclasses'], {
            'TenderloinBiohazard': {10: [round8.CHIROPRACTIC]},
            'VeniceBoardwalkBrawler': {12: [round8.SUNGLASSES]},
            'BARTPlatformMenace': {12: [round8.SEISMIC_RETROFIT]},
            'OverpassRiverbedDweller': {10: [round8.BLACKOUT]},
        })
        self.assertEqual(self.grants['existing_list_spells'], {
            'Californian_L1': round8.HOT_BAR, 'Siliconite_L1': round8.SCROLL_MEETING})
        granted = [s for lv in self.grants['base'].values() for s in lv]
        granted += [s for cat in self.grants['subclasses'].values() for lv in cat.values() for s in lv]
        granted += list(self.grants['existing_list_spells'].values())
        self.assertEqual(sorted(granted), sorted(EXPECTED_SPELLS))
        self.assertNotIn(3, self.grants['base'])  # base level 3 is reserved

    def test_target_progression_levels_exist(self):
        names_levels = {(p['Name'], int(p['Level'])) for p in self.progs}
        for level in self.grants['base']:
            self.assertIn(('HomelessCalifornian', level), names_levels)
        for category, levels in self.grants['subclasses'].items():
            for level in levels:
                self.assertIn((category, level), names_levels)
        key_to_prog = {'Californian_L1': ('Californian', 1), 'Siliconite_L1': ('Siliconite', 1)}
        for key, target in key_to_prog.items():
            self.assertIn(target, names_levels, key)
            uid = generator.get_guid('SpellList_' + key)
            self.assertIn(uid, self.lists, key)
            self.assertTrue(any(uid in p.get('Selectors', '') for p in self.progs
                                if (p['Name'], int(p['Level'])) == target), key)

    # ------------------------------------------------------------------ rules
    def test_costs_use_owned_resources_and_at_most_one_junk(self):
        for name in EXPECTED_SPELLS:
            f = self.fields(name)
            tokens = [t.split(':') for t in f['UseCosts'].split(';') if t]
            self.assertTrue({t[0] for t in tokens} <= ALLOWED_RESOURCES, name)
            for resource, *amount in tokens:
                if resource == 'HC_Junk':
                    self.assertEqual(amount, ['2'] if name == round8.NIMBY_COMMENT else ['1'], name)
            if 'HC_Junk' in f['UseCosts'] and f.get('RitualCosts'):
                self.assertIn('HC_Junk', f['RitualCosts'], name)

    def test_no_junk_or_gold_generation_and_no_unsafe_functors(self):
        for name in EXPECTED_SPELLS:
            f = self.fields(name)
            blob = ';'.join(f.get(k, '') for k in ('SpellProperties', 'SpellSuccess', 'SpellFail'))
            self.assertNotIn('RestoreResource', blob, name)
            self.assertNotIn('SummonInInventory', blob, name)
            self.assertNotIn('IF(', blob, name)
            self.assertNotIn('Reaction', f['UseCosts'], name)

    def test_racial_spells_cost_no_class_resource(self):
        for name in (round8.HOT_BAR, round8.SCROLL_MEETING):
            self.assertNotIn('HC_Junk', self.fields(name)['UseCosts'])

    def test_no_target_filter_requires_a_status_on_the_target(self):
        for name in EXPECTED_SPELLS:
            cond = self.fields(name).get('TargetConditions', '')
            self.assertIsNone(re.search(r"(?<!not )HasStatus\(\s*'[^']+'\s*\)", cond), name)

    def test_save_spells_apply_enemy_effects_only_on_the_failed_save_branch(self):
        for name in (round8.POTHOLE, round8.NIMBY_COMMENT, round8.UNFINISHED_BUSINESS,
                     round8.BLACKOUT, round8.SEISMIC_RETROFIT):
            f = self.fields(name)
            self.assertIn('SavingThrow(Ability.', f['SpellRoll'], name)
            self.assertIn('SourceSpellDC()', f['SpellRoll'], name)
            self.assertNotIn('ApplyStatus', f['SpellFail'], name)
            self.assertIn('/2', f['SpellFail'], name)

    # ---------------------------------------------------------------- mechanics
    def test_spell_mechanics_and_surfaces(self):
        f = self.fields
        self.assertIn('ApplyStatus(PRONE,100,1)', f(round8.POTHOLE)['SpellSuccess'])
        self.assertIn('ApplyStatus(HC_BROKEN_ANKLE,100,2)', f(round8.POTHOLE)['SpellSuccess'])
        self.assertIn('ApplyStatus(HC_PUBLIC_COMMENT_TRANCE,100,1)', f(round8.NIMBY_COMMENT)['SpellSuccess'])
        self.assertEqual(f(round8.NIMBY_COMMENT)['AreaRadius'], '6')
        self.assertEqual(f(round8.NIMBY_COMMENT)['Cooldown'], 'OncePerRest')
        self.assertIn('DealDamage(3d10,Force,Magical)', f(round8.UNFINISHED_BUSINESS)['SpellSuccess'])
        self.assertIn('ApplyStatus(HC_RED_TAGGED,100,2)', f(round8.UNFINISHED_BUSINESS)['SpellSuccess'])
        self.assertIn('ApplyStatus(SELF,HC_LINE_ITEM_APPROVED,100,3)', f(round8.BUDGET_HEARING)['SpellProperties'])
        props = f(round8.CHIROPRACTIC)['SpellProperties']
        self.assertIn('RegainHitPoints(4d8)', props)
        self.assertIn('ApplyStatus(PRONE,100,1)', props)
        self.assertIn('ApplyStatus(HC_CERVICAL_REALIGNMENT,100,3)', props)
        self.assertNotIn('Self()', f(round8.CHIROPRACTIC)['TargetConditions'].replace('not Self()', ''))
        self.assertIn('GROUND:CreateSurface(4,3,DarknessCloud)', f(round8.BLACKOUT)['SpellProperties'])
        self.assertIn('ApplyStatus(BLINDED,100,1)', f(round8.BLACKOUT)['SpellSuccess'])
        self.assertIn('ApplyStatus(SELF,HC_TEN_DOLLAR_SHADES,100,3)', f(round8.SUNGLASSES)['SpellProperties'])
        self.assertIn('ApplyStatus(SELF,HC_RETROFIT_PENDING,100,2)', f(round8.SEISMIC_RETROFIT)['SpellProperties'])
        self.assertIn('ApplyStatus(PRONE,100,1)', f(round8.SEISMIC_RETROFIT)['SpellSuccess'])
        self.assertIn('RegainHitPoints(1d8+ConstitutionModifier)', f(round8.HOT_BAR)['SpellProperties'])
        self.assertIn('ApplyStatus(SELF,HC_HOT_BAR_FOOD_COMA,100,2)', f(round8.HOT_BAR)['SpellProperties'])
        self.assertIn('ApplyStatus(HC_SYNERGY_ALIGNED,100,2)', f(round8.SCROLL_MEETING)['SpellProperties'])
        self.assertEqual(f(round8.SCROLL_MEETING)['RitualCosts'], '')

    def test_every_custom_status_is_applied_by_a_round8_spell(self):
        applied = set()
        for name in EXPECTED_SPELLS:
            f = self.fields(name)
            for field in ('SpellProperties', 'SpellSuccess', 'SpellFail'):
                applied.update(re.findall(r'ApplyStatus\((?:SELF,)?(HC_[A-Z0-9_]+)', f.get(field, '')))
        self.assertEqual(applied, EXPECTED_STATUSES)

    # --------------------------------------------------------- vanilla precedent
    def test_every_boost_functor_surface_and_damage_form_has_vanilla_precedent(self):
        text = self.vanilla_text
        norm = lambda s: re.sub(r',\s+', ',', s)
        for name in EXPECTED_STATUSES:
            for token in split_top(self.fields(name)['Boosts']):
                self.assertIn(norm(token), text, f'{name}: boost {token} has no vanilla precedent')
        for name in EXPECTED_SPELLS:
            f = self.fields(name)
            for field in ('SpellProperties', 'SpellSuccess', 'SpellFail'):
                for token in split_top(f.get(field, '')):
                    token = token.split(':', 1)[1] if re.match(r'(GROUND|SELF|TARGET):', token) else token
                    token = re.sub(r'^(ApplyStatus)\(SELF,', r'\1(', token)
                    func = token.split('(', 1)[0]
                    self.assertIn(func + '(', text, f'{name}: {func}')
                    if func == 'DealDamage':
                        match = re.match(r'DealDamage\(\(?(\d+d\d+)\)?(?:/2)?,(\w+),Magical\)', token)
                        self.assertTrue(match, f'{name}: unparsed {token}')
                        self.assertRegex(text, rf'DealDamage\({match.group(1)},{match.group(2)},Magical\)', f'{name}: {token}')
                    elif func == 'RegainHitPoints':
                        self.assertIn(token, text, f'{name}: {token}')
                    elif func == 'CreateSurface':
                        surface = token.rstrip(')').split(',')[2]
                        self.assertRegex(text, rf'CreateSurface\([^()]*,{surface}\b', f'{name}: {surface}')
                    elif func == 'ApplyStatus':
                        status = token[len('ApplyStatus('):].split(',')[0]
                        self.assertTrue(status.startswith('HC_') or status in self.vanilla, f'{name}: {status}')
        for name in EXPECTED_SPELLS:
            damage = self.fields(name).get('DamageType', '')
            if damage:
                self.assertIn(f',{damage},Magical)', text, name)

    # ------------------------------------------------------------ localisation
    def test_localization_and_descriptions(self):
        for name, entry in self.new.items():
            for field in ('DisplayName', 'Description'):
                handle = entry.fields[field].split(';')[0]
                self.assertIn(handle, self.loca, f'{name}.{field}')
                self.assertTrue(self.loca[handle].strip())
        for spell in EXPECTED_SPELLS:
            description = self.loca[self.fields(spell)['Description'].split(';')[0]]
            sentences = len(re.findall(r'\.(?:\s|$)', description))
            self.assertTrue(3 <= sentences <= 5, f'{spell}: {sentences} sentences')
            self.assertNotIn('"', description)

    def test_no_patriot_paths_in_generated_text(self):
        for name, entry in self.new.items():
            self.assertNotIn('patriot', entry.body.lower(), name)


if __name__ == '__main__':
    unittest.main()
