"""Round 9 file-level contracts (base L8/L12, subclass BART L3 / Tenderloin L12 / Overpass L12,
Siliconite L3, Inland Emperor L3 and Beachborn L1 racial lists).

The generator is not wired into generate_mod.py by this module's author, so these tests run
generate_round9() against a temporary copy of the built src/ tree and validate the combined result.
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
import hc_round9 as round9
import validate

SRC = ROOT / 'src/HomelessCalifornian'
VANILLA_LAYERS = ('Shared', 'SharedDev', 'Gustav', 'GustavDev')

EXPECTED_SPELLS = {
    round9.COSTCO_CART, round9.DMV_TICKET, round9.SELF_CHECKOUT, round9.PROP13,
    round9.TECH_SHUTTLE, round9.RACCOON_TRIBUNAL, round9.PURPLEAIR,
    round9.TRUST_FALL, round9.HOA_BEIGE, round9.NEXTDOOR_COYOTE,
}
RACIAL_SPELLS = {round9.TRUST_FALL, round9.HOA_BEIGE, round9.NEXTDOOR_COYOTE}
SAVE_SPELLS = EXPECTED_SPELLS - {round9.PROP13, round9.TRUST_FALL}
LONG_REST_SPELLS = {round9.PROP13, round9.RACCOON_TRIBUNAL, round9.PURPLEAIR}
EXPECTED_STATUSES = {spec[0] for spec in round9.STATUS_SPECS}
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


class RoundNineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not SRC.is_dir():
            raise unittest.SkipTest('built src/HomelessCalifornian tree is missing')
        cls.tmp = tempfile.TemporaryDirectory()
        cls.source = Path(cls.tmp.name) / 'HomelessCalifornian'
        shutil.copytree(SRC, cls.source)
        cls.public = cls.source / 'Public/HomelessCalifornian'
        with patch.dict(generator.LOCA_ENTRIES, {}, clear=True):
            cls.grants = round9.generate_round9(cls.public, generator.add_loca, generator.get_guid)
            entries = dict(generator.LOCA_ENTRIES)
        loca_path = cls.public / 'Localization/English/HomelessCalifornian.loca.xml'
        loca = loca_path.read_text(encoding='utf-8')
        extra = ''.join(f'    <content contentuid="{h}" version="1">{escape(t)}</content>\n'
                        for h, t in entries.items() if f'contentuid="{h}"' not in loca)
        loca_path.write_text(loca.replace('</contentList>', extra + '</contentList>'), encoding='utf-8')
        cls.entries = entries
        cls.stats = validate.read_stats(cls.public)
        cls.vanilla = validate.read_stats(ROOT / 'temp_race')
        cls.new = {k: v[0] for k, v in cls.stats.items() if v[0].path.name.endswith('_Round9.txt')}
        cls.loca = {e.get('contentuid'): e.text for e in ET.parse(loca_path).iter('content')}
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
    def test_all_round9_entries_are_unique_prefixed_and_do_not_override_vanilla(self):
        self.assertEqual(set(self.new), EXPECTED_SPELLS | EXPECTED_STATUSES)
        self.assertEqual(len(EXPECTED_SPELLS), 10)
        self.assertEqual(len(EXPECTED_STATUSES), 3)
        self.assertEqual(len(self.new), 13)
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
        self.assertGreaterEqual(counts['stats'], 240 + 13)

    def test_return_dict_contract(self):
        self.assertEqual(set(self.grants), {'base', 'subclasses', 'existing_list_spells'})
        self.assertEqual(self.grants['base'], {
            8: [round9.COSTCO_CART, round9.DMV_TICKET, round9.SELF_CHECKOUT],
            12: [round9.PROP13]})
        self.assertEqual(self.grants['subclasses'], {
            'BARTPlatformMenace': {3: [round9.TECH_SHUTTLE]},
            'TenderloinBiohazard': {12: [round9.RACCOON_TRIBUNAL]},
            'OverpassRiverbedDweller': {12: [round9.PURPLEAIR]},
        })
        self.assertEqual(self.grants['existing_list_spells'], {
            'Siliconite_L3': round9.TRUST_FALL,
            'InlandEmperor_L3': round9.HOA_BEIGE,
            'Beachborn_L1': round9.NEXTDOOR_COYOTE})
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
        key_to_prog = {'Siliconite_L3': ('Siliconite', 3), 'InlandEmperor_L3': ('InlandEmperor', 3),
                       'Beachborn_L1': ('Beachborn', 1)}
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
                    self.assertEqual(amount, ['1'], name)
            if 'HC_Junk' in f['UseCosts'] and f.get('RitualCosts'):
                self.assertIn('HC_Junk', f['RitualCosts'], name)

    def test_racial_spells_cost_no_class_resource_and_class_spells_cost_one_junk(self):
        for name in RACIAL_SPELLS:
            self.assertNotIn('HC_Junk', self.fields(name)['UseCosts'], name)
        for name in EXPECTED_SPELLS - RACIAL_SPELLS:
            self.assertIn('HC_Junk:1', self.fields(name)['UseCosts'], name)

    def test_cooldowns_match_the_design(self):
        for name in EXPECTED_SPELLS:
            expected = 'OncePerRest' if name in LONG_REST_SPELLS else 'OncePerShortRest'
            self.assertEqual(self.fields(name)['Cooldown'], expected, name)

    def test_no_junk_or_gold_generation_and_no_unsafe_functors(self):
        for name in EXPECTED_SPELLS:
            f = self.fields(name)
            blob = ';'.join(f.get(k, '') for k in ('SpellProperties', 'SpellSuccess', 'SpellFail'))
            self.assertNotIn('RestoreResource', blob, name)
            self.assertNotIn('SummonInInventory', blob, name)
            self.assertNotIn('IF(', blob, name)
            self.assertNotIn('Reaction', f['UseCosts'], name)

    def test_no_self_effects_inside_victim_filtered_results(self):
        for name in EXPECTED_SPELLS:
            f = self.fields(name)
            for field in ('SpellSuccess', 'SpellFail'):
                self.assertNotIn('SELF', f.get(field, ''), f'{name}.{field}')

    def test_no_target_filter_requires_a_status_on_the_target(self):
        for name in EXPECTED_SPELLS:
            cond = self.fields(name).get('TargetConditions', '')
            self.assertIsNone(re.search(r"(?<!not )HasStatus\(\s*'[^']+'\s*\)", cond), name)

    def test_hostile_spells_never_target_allies_and_the_shout_uses_enemy_filter(self):
        for name in SAVE_SPELLS | {round9.TRUST_FALL}:
            cond = self.fields(name)['TargetConditions']
            self.assertTrue(cond == 'Enemy()' or 'not Ally()' in cond, name)
        coyote = self.fields(round9.NEXTDOOR_COYOTE)
        self.assertEqual(coyote['TargetConditions'], 'Enemy()')
        self.assertEqual(coyote['AreaRadius'], '6')
        self.assertEqual(self.new[round9.NEXTDOOR_COYOTE].using, 'Shout_FeyPresence')
        description = self.loca[coyote['Description'].split(';')[0]]
        self.assertIn('Enemies', description)

    def test_save_spells_apply_enemy_effects_only_on_the_failed_save_branch(self):
        for name in SAVE_SPELLS:
            f = self.fields(name)
            self.assertIn('SavingThrow(Ability.', f['SpellRoll'], name)
            self.assertIn('SourceSpellDC()', f['SpellRoll'], name)
            self.assertIn('ApplyStatus', f['SpellSuccess'], name)
            self.assertNotIn('ApplyStatus', f['SpellFail'], name)
            self.assertIn('/2', f['SpellFail'], name)

    # ---------------------------------------------------------------- mechanics
    def test_spell_mechanics(self):
        f = self.fields
        want = {
            round9.COSTCO_CART: ('Strength', '6', 'DealDamage(2d6,Bludgeoning,Magical)', 'ApplyStatus(HC_CUBE_DENIED,100,2)'),
            round9.DMV_TICKET: ('Wisdom', '12', 'DealDamage(2d8,Psychic,Magical)', 'ApplyStatus(DAZED,100,1)'),
            round9.SELF_CHECKOUT: ('Wisdom', '9', 'DealDamage(2d8,Psychic,Magical)', 'ApplyStatus(DAZED,100,2)'),
            round9.TECH_SHUTTLE: ('Dexterity', None, 'DealDamage(3d8,Bludgeoning,Magical)', 'ApplyStatus(PRONE,100,1)'),
            round9.RACCOON_TRIBUNAL: ('Constitution', '3', 'DealDamage(2d6,Piercing,Magical)', 'ApplyStatus(FRIGHTENED,100,1)'),
            round9.PURPLEAIR: ('Constitution', '6', 'DealDamage(2d6,Poison,Magical)', 'ApplyStatus(BLINDED,100,1)'),
            round9.HOA_BEIGE: ('Wisdom', '9', 'DealDamage(2d8,Psychic,Magical)', 'ApplyStatus(FRIGHTENED,100,2)'),
            round9.NEXTDOOR_COYOTE: ('Wisdom', None, 'DealDamage(2d8,Psychic,Magical)', 'ApplyStatus(FRIGHTENED,100,1)'),
        }
        for name, (ability, radius, damage, status) in want.items():
            self.assertIn(f'Ability.{ability}', f(name)['SpellRoll'], name)
            if radius:
                self.assertEqual(f(name)['TargetRadius'], radius, name)
            self.assertIn(damage, f(name)['SpellSuccess'], name)
            self.assertIn(status, f(name)['SpellSuccess'], name)
        self.assertIn('DealDamage(1d8,Poison,Magical)', f(round9.RACCOON_TRIBUNAL)['SpellSuccess'])
        self.assertEqual((f(round9.TECH_SHUTTLE)['Range'], f(round9.TECH_SHUTTLE)['Base']), ('9', '3'))
        self.assertEqual(self.new[round9.TECH_SHUTTLE].using, 'Zone_Thunderwave')
        # Prop 13: bonus action self heal plus the shared +2 AC posture stack
        prop = f(round9.PROP13)
        self.assertEqual(prop['TargetConditions'], 'Self()')
        self.assertIn('BonusActionPoint:1', prop['UseCosts'])
        self.assertIn('RegainHitPoints(1d8+ConstitutionModifier)', prop['SpellProperties'])
        self.assertIn('ApplyStatus(SELF,HC_GRANDFATHERED_IN,100,2)', prop['SpellProperties'])
        grandfathered = self.fields('HC_GRANDFATHERED_IN')
        self.assertEqual(grandfathered['StackId'], 'HC_CHAIR_BRACED')
        self.assertEqual(grandfathered['Boosts'], 'AC(2)')
        # Trust Fall: melee spell attack, no save, self buff outside the victim branch
        fall = f(round9.TRUST_FALL)
        self.assertEqual(fall['SpellRoll'], 'Attack(AttackType.MeleeSpellAttack)')
        self.assertEqual(fall['TargetRadius'], '1.5')
        self.assertIn('DealDamage(2d8,Bludgeoning,Magical)', fall['SpellSuccess'])
        self.assertIn('ApplyStatus(PRONE,100,1)', fall['SpellSuccess'])
        self.assertIn('ApplyStatus(SELF,HC_OFFSITE_BOUNCE_BACK,100,2)', fall['SpellProperties'])
        self.assertEqual(self.fields('HC_OFFSITE_BOUNCE_BACK')['Boosts'], 'Advantage(AttackRoll)')
        self.assertEqual(self.fields('HC_CUBE_DENIED')['Boosts'], 'ActionResource(Movement,-3,0)')

    def test_every_custom_status_is_applied_by_a_round9_spell(self):
        applied = set()
        for name in EXPECTED_SPELLS:
            f = self.fields(name)
            for field in ('SpellProperties', 'SpellSuccess', 'SpellFail'):
                applied.update(re.findall(r'ApplyStatus\((?:SELF,)?(HC_[A-Z0-9_]+)', f.get(field, '')))
        self.assertEqual(applied, EXPECTED_STATUSES)

    # --------------------------------------------------------- vanilla precedent
    def test_every_boost_functor_and_damage_form_has_exact_vanilla_precedent(self):
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
                        self.assertIn(f'DealDamage({match.group(1)},{match.group(2)},Magical)', text,
                                      f'{name}: {token} has no exact vanilla form')
                    elif func == 'RegainHitPoints':
                        self.assertIn(token, text, f'{name}: {token}')
                    elif func == 'ApplyStatus':
                        status, chance, turns = token[len('ApplyStatus('):].rstrip(')').split(',')
                        if status.startswith('HC_'):
                            continue
                        self.assertIn(status, self.vanilla, f'{name}: {status}')
                        self.assertIn(f'ApplyStatus({status},{chance},{turns})', text,
                                      f'{name}: {token} has no exact vanilla form')
        for name in EXPECTED_SPELLS:
            damage = self.fields(name).get('DamageType', '')
            if damage:
                self.assertIn(f',{damage},Magical)', text, name)
            roll = re.sub(r',\s+', ',', self.fields(name)['SpellRoll'])
            for save in re.findall(r'SavingThrow\(Ability\.\w+,SourceSpellDC\(\)\)', roll):
                self.assertIn(save, text, f'{name}: {save}')
            if roll.startswith('Attack('):
                self.assertIn(roll, text, name)

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
