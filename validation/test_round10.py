"""Round 10 file-level contracts: 8 spells + Caltrans Safety Vest (armour, requisition shout, equip passive)
+ Rent-Stabilized Grit passive.

The generator is not wired into generate_mod.py by this module's author, so these tests run
generate_round10() against a temporary copy of the built src/ tree, attach the grants the lead would
attach (base passive, shared spell lists excluded) and validate the combined result.
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
import hc_round10 as r10
import validate

SRC = ROOT / 'src/HomelessCalifornian'
VANILLA_LAYERS = ('Shared', 'SharedDev', 'Gustav', 'GustavDev')

SAVE_SPELLS = {r10.CONE_LABYRINTH, r10.CALTRAIN_HORN, r10.RENT_INCREASE, r10.POOL_HOURS,
               r10.PEACH_DENIAL, r10.OAT_MILK}
EIGHT_SPELLS = SAVE_SPELLS | {r10.IN_N_OUT, r10.STREET_SWEEP}
ALL_SPELLS = EIGHT_SPELLS | {r10.VEST_SHOUT}
RACIAL_SPELLS = {r10.PEACH_DENIAL, r10.OAT_MILK}
LONG_REST_SPELLS = {r10.CALTRAIN_HORN, r10.RENT_INCREASE, r10.VEST_SHOUT}
EXPECTED_STATUSES = {spec[0] for spec in r10.STATUS_SPECS}
EXPECTED_PASSIVES = {r10.GRIT_PASSIVE, r10.VEST_PASSIVE}
ALLOWED_RESOURCES = {'ActionPoint', 'BonusActionPoint', 'HC_Junk'}


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


class RoundTenTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not SRC.is_dir():
            raise unittest.SkipTest('built src/HomelessCalifornian tree is missing')
        cls.tmp = tempfile.TemporaryDirectory()
        cls.source = Path(cls.tmp.name) / 'HomelessCalifornian'
        shutil.copytree(SRC, cls.source)
        cls.public = cls.source / 'Public/HomelessCalifornian'
        with patch.dict(generator.LOCA_ENTRIES, {}, clear=True):
            cls.grants = r10.generate_round10(cls.public, generator.add_loca, generator.get_guid)
            entries = dict(generator.LOCA_ENTRIES)
        loca_path = cls.public / 'Localization/English/HomelessCalifornian.loca.xml'
        loca = loca_path.read_text(encoding='utf-8')
        extra = ''.join(f'    <content contentuid="{h}" version="1">{escape(t)}</content>\n'
                        for h, t in entries.items() if f'contentuid="{h}"' not in loca)
        loca_path.write_text(loca.replace('</contentList>', extra + '</contentList>'), encoding='utf-8')
        # Attach the base passive to the L9 progression exactly as the lead would, so the
        # repo validator checks that the passive reference resolves.
        prog_path = cls.public / 'Progressions/Progressions.lsx'
        prog = prog_path.read_text(encoding='utf-8')
        cls.prog_patched = False

        def attach(match):
            block = match.group(0)
            attrs = {a.get('id'): a.get('value') for a in ET.fromstring(block).findall('attribute')}
            if attrs.get('Name') == 'HomelessCalifornian' and attrs.get('Level') == '9':
                cls.prog_patched = True
                old = attrs.get('PassivesAdded', '')
                value = ';'.join(x for x in [old, *cls.grants['base_passives'][9]] if x)
                line = f'<attribute id="PassivesAdded" type="LSString" value="{value}"/>'
                if 'PassivesAdded' in attrs:
                    block = re.sub(r'<attribute id="PassivesAdded"[^>]*/>', lambda _: line, block, count=1)
                else:
                    block = block.replace('<attribute id="Level"', line + '\n<attribute id="Level"', 1)
            return block
        prog = re.sub(r'<node id="Progression">(?:(?!<node).)*?</node>', attach, prog, flags=re.S)
        prog_path.write_text(prog, encoding='utf-8')
        cls.entries = entries
        cls.stats = validate.read_stats(cls.public)
        cls.vanilla = validate.read_stats(ROOT / 'temp_race')
        cls.new = {k: v[0] for k, v in cls.stats.items() if v[0].path.name.endswith('_Round10.txt')}
        cls.loca = {e.get('contentuid'): e.text for e in ET.parse(loca_path).iter('content')}
        cls.progs = [cls.attrs(n) for n in ET.parse(cls.public / 'Progressions/Progressions.lsx')
                     .findall('.//node[@id="Progression"]')]
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
    def test_all_round10_entries_are_unique_prefixed_and_do_not_override_vanilla(self):
        expected = ALL_SPELLS | EXPECTED_STATUSES | EXPECTED_PASSIVES | {r10.VEST_ARMOR}
        self.assertEqual(set(self.new), expected)
        self.assertEqual(len(EIGHT_SPELLS), 8)
        self.assertEqual(len(ALL_SPELLS), 9)
        self.assertEqual(len(EXPECTED_STATUSES), 5)
        for name in self.new:
            self.assertTrue(name.startswith('HC_'))
            self.assertNotIn(name, self.vanilla)
            self.assertEqual(len(self.stats[name]), 1)

    def test_names_and_stack_ids_do_not_collide_with_other_hc_content(self):
        others = set()
        stack_ids = set()
        for name, entries in self.stats.items():
            entry = entries[0]
            if not entry.path.name.endswith('_Round10.txt'):
                others.add(name)
                if entry.fields.get('StackId'):
                    stack_ids.add(entry.fields['StackId'])
        self.assertFalse(set(self.new) & others)
        for status in EXPECTED_STATUSES:
            stack = self.fields(status)['StackId']
            self.assertEqual(stack, status)
            self.assertNotIn(stack, stack_ids)
            self.assertNotIn(stack, self.vanilla)

    def test_all_donors_exist_in_vanilla_and_none_are_honour_overridden(self):
        honour_names = {name for name, entries in self.vanilla.items()
                        if any('Honour' in e.path.parts for e in entries)}
        for name, entry in self.new.items():
            if entry.using:
                self.assertIn(entry.using, self.vanilla, name)
                self.assertTrue(any(e.type == entry.type for e in self.vanilla[entry.using]), name)
                self.assertNotIn(entry.using, honour_names, name)

    def test_repo_validator_passes_on_combined_tree(self):
        self.assertTrue(self.prog_patched, 'Base L9 progression node not found')
        errors, counts = validate.validate(self.source, ROOT / 'temp_race')
        self.assertEqual(errors, [])
        self.assertGreaterEqual(counts['stats'], 240 + 17)

    def test_return_dict_contract(self):
        self.assertEqual(set(self.grants), {'base', 'subclasses', 'existing_list_spells', 'base_passives'})
        self.assertEqual(self.grants['base'], {
            5: [r10.IN_N_OUT], 9: [r10.CONE_LABYRINTH], 10: [r10.CALTRAIN_HORN],
            11: [r10.VEST_SHOUT], 12: [r10.RENT_INCREASE]})
        self.assertEqual(self.grants['subclasses'], {
            'VeniceBoardwalkBrawler': {6: [r10.POOL_HOURS]},
            'BARTPlatformMenace': {10: [r10.STREET_SWEEP]}})
        self.assertEqual(self.grants['existing_list_spells'], {
            'Beachborn_L3': r10.PEACH_DENIAL, 'Siliconite_L1': r10.OAT_MILK})
        self.assertEqual(self.grants['base_passives'], {9: [r10.GRIT_PASSIVE]})
        granted = [s for lv in self.grants['base'].values() for s in lv]
        granted += [s for cat in self.grants['subclasses'].values() for lv in cat.values() for s in lv]
        granted += list(self.grants['existing_list_spells'].values())
        self.assertEqual(sorted(granted), sorted(ALL_SPELLS))
        self.assertNotIn(3, self.grants['base'])  # base level 3 is reserved

    def test_target_progression_levels_exist(self):
        names_levels = {(p['Name'], int(p['Level'])) for p in self.progs}
        for level in self.grants['base']:
            self.assertIn(('HomelessCalifornian', level), names_levels)
        for level in self.grants['base_passives']:
            self.assertIn(('HomelessCalifornian', level), names_levels)
        for category, levels in self.grants['subclasses'].items():
            for level in levels:
                self.assertIn((category, level), names_levels)
        self.assertIn(('Beachborn', 3), names_levels)
        self.assertIn(('Siliconite', 1), names_levels)

    # ------------------------------------------------------------------ rules
    def test_costs_use_owned_resources_and_at_most_one_junk(self):
        for name in ALL_SPELLS:
            f = self.fields(name)
            tokens = [t.split(':') for t in f['UseCosts'].split(';') if t]
            self.assertTrue({t[0] for t in tokens} <= ALLOWED_RESOURCES, name)
            for resource, *amount in tokens:
                if resource == 'HC_Junk':
                    self.assertEqual(amount, ['1'], name)
            self.assertNotIn('Reaction', f['UseCosts'], name)

    def test_racial_spells_cost_no_class_resource_and_class_spells_cost_one_junk_unless_free(self):
        for name in RACIAL_SPELLS:
            self.assertNotIn('HC_Junk', self.fields(name)['UseCosts'], name)
        for name in EIGHT_SPELLS - RACIAL_SPELLS:
            self.assertIn('HC_Junk:1', self.fields(name)['UseCosts'], name)
        self.assertNotIn('HC_Junk', self.fields(r10.VEST_SHOUT)['UseCosts'])

    def test_cooldowns_match_the_design(self):
        for name in ALL_SPELLS:
            expected = 'OncePerRest' if name in LONG_REST_SPELLS else 'OncePerShortRest'
            self.assertEqual(self.fields(name)['Cooldown'], expected, name)

    def test_no_junk_or_gold_generation_and_no_unsafe_functors(self):
        for name in ALL_SPELLS - {r10.VEST_SHOUT}:
            f = self.fields(name)
            blob = ';'.join(f.get(k, '') for k in ('SpellProperties', 'SpellSuccess', 'SpellFail'))
            self.assertNotIn('RestoreResource', blob, name)
            self.assertNotIn('SummonInInventory', blob, name)
            self.assertNotIn('IF(', blob, name)

    def test_no_self_effects_inside_victim_filtered_results(self):
        for name in ALL_SPELLS:
            f = self.fields(name)
            for field in ('SpellSuccess', 'SpellFail'):
                self.assertNotIn('SELF', f.get(field, ''), f'{name}.{field}')

    def test_no_target_filter_requires_a_status_on_the_target(self):
        for name in ALL_SPELLS:
            cond = self.fields(name).get('TargetConditions', '')
            self.assertIsNone(re.search(r"(?<!not )HasStatus\(\s*'[^']+'\s*\)", cond), name)

    def test_hostile_spells_never_target_allies(self):
        for name in SAVE_SPELLS | {r10.STREET_SWEEP}:
            cond = self.fields(name)['TargetConditions']
            self.assertTrue(cond == 'Enemy()' or 'not Ally()' in cond, name)

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
            r10.CONE_LABYRINTH: ('Dexterity', '9', 'DealDamage(2d8,Bludgeoning,Magical)', 'ApplyStatus(PRONE,100,1)'),
            r10.CALTRAIN_HORN: ('Constitution', '12', 'DealDamage(3d8,Thunder,Magical)', 'ApplyStatus(DAZED,100,1)'),
            r10.RENT_INCREASE: ('Wisdom', '9', 'DealDamage(3d8,Psychic,Magical)', 'ApplyStatus(FRIGHTENED,100,2)'),
            r10.POOL_HOURS: ('Wisdom', '9', 'DealDamage(2d6,Psychic,Magical)', 'ApplyStatus(DAZED,100,1)'),
            r10.PEACH_DENIAL: ('Dexterity', '9', 'DealDamage(2d6,Bludgeoning,Magical)', 'ApplyStatus(PRONE,100,1)'),
            r10.OAT_MILK: ('Wisdom', '6', 'DealDamage(2d8,Psychic,Magical)', 'ApplyStatus(HC_OATMILK_LINE_STUCK,100,2)'),
        }
        for name, (ability, radius, damage, status) in want.items():
            self.assertIn(f'Ability.{ability}', f(name)['SpellRoll'], name)
            self.assertEqual(f(name)['TargetRadius'], radius, name)
            self.assertIn(damage, f(name)['SpellSuccess'], name)
            self.assertIn(status, f(name)['SpellSuccess'], name)
        # self movement buffs sit in SpellProperties, outside the victim branches
        self.assertIn('ApplyStatus(SELF,HC_DETOUR_DASH,100,1)', f(r10.CONE_LABYRINTH)['SpellProperties'])
        self.assertIn('ApplyStatus(SELF,HC_VALIDATION_SPRINT,100,1)', f(r10.PEACH_DENIAL)['SpellProperties'])
        self.assertEqual(f('HC_DETOUR_DASH')['Boosts'], 'ActionResource(Movement,3,0)')
        self.assertEqual(f('HC_VALIDATION_SPRINT')['Boosts'], 'ActionResource(Movement,3,0)')
        # Peach Denial is a bonus action
        self.assertEqual(f(r10.PEACH_DENIAL)['UseCosts'], 'BonusActionPoint:1')
        # In-N-Out: bonus action self heal and advantage
        inout = f(r10.IN_N_OUT)
        self.assertEqual(self.new[r10.IN_N_OUT].using, 'Shout_SecondWind')
        self.assertEqual(inout['TargetConditions'], 'Self()')
        self.assertIn('BonusActionPoint:1', inout['UseCosts'])
        self.assertIn('RegainHitPoints(1d8+ConstitutionModifier)', inout['SpellProperties'])
        self.assertIn('ApplyStatus(SELF,HC_ANIMAL_STYLE_ENERGY,100,2)', inout['SpellProperties'])
        self.assertEqual(f('HC_ANIMAL_STYLE_ENERGY')['Boosts'], 'Advantage(AttackRoll)')
        # Street-Sweep: melee spell attack
        sweep = f(r10.STREET_SWEEP)
        self.assertEqual(self.new[r10.STREET_SWEEP].using, 'Target_ShockingGrasp')
        self.assertEqual(sweep['SpellRoll'], 'Attack(AttackType.MeleeSpellAttack)')
        self.assertEqual(sweep['TargetRadius'], '1.5')
        self.assertIn('DealDamage(1d6,Slashing,Magical)', sweep['SpellSuccess'])
        self.assertIn('DealDamage(2d8,Psychic,Magical)', sweep['SpellSuccess'])
        self.assertIn('ApplyStatus(HC_CITATION_FILED,100,2)', sweep['SpellSuccess'])
        self.assertEqual(f('HC_CITATION_FILED')['Boosts'], 'Disadvantage(SavingThrow,Dexterity)')
        self.assertEqual(f('HC_OATMILK_LINE_STUCK')['Boosts'], 'Disadvantage(AttackRoll)')

    def test_every_custom_status_is_applied_by_a_round10_spell(self):
        applied = set()
        for name in ALL_SPELLS:
            f = self.fields(name)
            for field in ('SpellProperties', 'SpellSuccess', 'SpellFail'):
                applied.update(re.findall(r'ApplyStatus\((?:SELF,)?(HC_[A-Z0-9_]+)', f.get(field, '')))
        self.assertEqual(applied, EXPECTED_STATUSES)

    # ------------------------------------------------------- item and passives
    def test_vest_is_rare_light_armour_with_inherited_ac12_and_dex(self):
        vest = self.new[r10.VEST_ARMOR]
        self.assertEqual(vest.type, 'Armor')
        self.assertEqual(vest.using, 'ARM_StuddedLeather_Body')
        donor = self.vanilla['ARM_StuddedLeather_Body'][0].fields
        self.assertEqual(donor['ArmorClass'], '12')
        self.assertEqual(donor['Armor Class Ability'], 'Dexterity')
        self.assertEqual(donor['Proficiency Group'], 'LightArmor')
        self.assertEqual(vest.fields['Rarity'], 'Rare')
        self.assertNotIn('ArmorClass', vest.fields)  # AC comes from the vanilla donor
        self.assertEqual(vest.fields['Boosts'], 'Skill(Deception,1)')
        self.assertEqual(vest.fields['PassivesOnEquip'], r10.VEST_PASSIVE)
        self.assertEqual(self.fields(r10.VEST_PASSIVE)['Boosts'],
                         'Advantage(Skill,Intimidation);Disadvantage(Skill,Stealth)')

    def test_vest_root_template_inherits_the_vanilla_studded_leather_template(self):
        tree = ET.parse(self.public / 'RootTemplates/HC_Round10Items.lsf.lsx')
        nodes = tree.findall('.//node[@id="GameObjects"]')
        self.assertEqual(len(nodes), 1)
        a = self.attrs(nodes[0])
        self.assertEqual(a['ParentTemplateId'], r10.VEST_PARENT_TEMPLATE)
        self.assertEqual(a['Stats'], r10.VEST_ARMOR)
        self.assertEqual(a['Type'], 'item')
        self.assertEqual(a['MapKey'], generator.get_guid(r10.VEST_ARMOR + '_RootTemplate'))
        merged = (ROOT / 'temp_race/Public/Shared/RootTemplates/_merged.lsf').read_bytes()
        self.assertIn(r10.VEST_PARENT_TEMPLATE.encode(), merged)
        self.assertIn(r10.VEST_ICON, (ROOT / 'temp_race/Public/Shared/GUI/Icons_Items.lsx').read_text(encoding='utf-8'))
        spell = self.fields(r10.VEST_SHOUT)
        self.assertEqual(spell['SpellProperties'],
                         f"SummonInInventory({a['MapKey']},-1,1,false,false,false)")
        self.assertEqual(spell['TargetConditions'], 'Self()')
        self.assertEqual(self.new[r10.VEST_SHOUT].using, 'Shout_SecondWind')

    def test_grit_passive_is_a_hp_gated_boost_passive_with_exact_vanilla_shape(self):
        grit = self.fields(r10.GRIT_PASSIVE)
        self.assertEqual(self.new[r10.GRIT_PASSIVE].type, 'PassiveData')
        self.assertEqual(grit['BoostContext'], 'OnDamaged;OnHealed')
        self.assertEqual(grit['BoostConditions'], 'HasHPPercentageLessThan(50, context.Target)')
        self.assertEqual(split_top(grit['Boosts']),
                         ['AC(2)', 'StatusImmunity(SG_Prone)', 'Advantage(SavingThrow,Strength)'])
        # whole-shape precedent: vanilla passive with the same context + condition pair
        lowhp = self.vanilla['MAG_LowHP_IncreaseSpeed_Passive'][0].fields
        self.assertEqual(lowhp['BoostContext'], grit['BoostContext'])
        self.assertEqual(lowhp['BoostConditions'], grit['BoostConditions'])
        self.assertNotIn('Proximity', ';'.join(grit.values()))
        description = self.loca[grit['Description'].split(';')[0]]
        self.assertIn('50%', description)
        self.assertIn('Prone', description)

    def test_grit_is_attached_at_base_level_nine(self):
        l9 = [p for p in self.progs if p['Name'] == 'HomelessCalifornian' and p['Level'] == '9']
        self.assertTrue(any(r10.GRIT_PASSIVE in p.get('PassivesAdded', '').split(';') for p in l9))

    # --------------------------------------------------------- vanilla precedent
    def test_every_boost_functor_and_damage_form_has_exact_vanilla_precedent(self):
        text = self.vanilla_text
        norm = lambda s: re.sub(r',\s+', ',', s)
        boosts = [(n, self.fields(n)['Boosts']) for n in EXPECTED_STATUSES | EXPECTED_PASSIVES | {r10.VEST_ARMOR}]
        for name, value in boosts:
            for token in split_top(value):
                self.assertIn(norm(token), text, f'{name}: boost {token} has no vanilla precedent')
        self.assertIn(norm(self.fields(r10.GRIT_PASSIVE)['BoostConditions']), text)
        for name in ALL_SPELLS:
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
        for name in EIGHT_SPELLS:
            damage = self.fields(name).get('DamageType', '')
            if damage:
                self.assertIn(f',{damage},Magical)', text, name)
            roll = re.sub(r',\s+', ',', self.fields(name).get('SpellRoll', ''))
            for save in re.findall(r'SavingThrow\(Ability\.\w+,SourceSpellDC\(\)\)', roll):
                self.assertIn(save, text, f'{name}: {save}')
            if roll.startswith('Attack('):
                self.assertIn(roll, text, name)

    # ------------------------------------------------------------ localisation
    def test_localization_and_descriptions(self):
        for name, entry in self.new.items():
            for field in ('DisplayName', 'Description'):
                if field not in entry.fields:
                    self.assertEqual(entry.type, 'Armor', f'{name} missing {field}')
                    continue
                handle = entry.fields[field].split(';')[0]
                self.assertIn(handle, self.loca, f'{name}.{field}')
                self.assertTrue(self.loca[handle].strip())
        for spell in ALL_SPELLS:
            description = self.loca[self.fields(spell)['Description'].split(';')[0]]
            sentences = len(re.findall(r'\.(?:\s|$)', description))
            self.assertTrue(3 <= sentences <= 5, f'{spell}: {sentences} sentences')
            self.assertNotIn('"', description)
        vest = r10.VEST_DESCRIPTION
        self.assertIn(vest, self.entries.values())
        self.assertTrue(3 <= len(re.findall(r'\.(?:\s|$)', vest)) <= 5)
        self.assertIn('Armour Class 12', vest)

    def test_titles_are_short_in_game_names(self):
        for spell in ALL_SPELLS:
            title = self.loca[self.fields(spell)['DisplayName'].split(';')[0]]
            self.assertLessEqual(len(title), 40, title)

    def test_no_patriot_paths_in_generated_text(self):
        for name, entry in self.new.items():
            self.assertNotIn('patriot', entry.body.lower(), name)


if __name__ == '__main__':
    unittest.main()
