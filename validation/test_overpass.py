"""Overpass Riverbed Dweller (4th subclass) regression checks, run on a freshly generated temp tree.

Spec: work/spec-overpass-subclass.md. No game files needed; vanilla donors are checked against the
local extracted reference in temp_race.
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

SUBCLASS = 'OverpassRiverbedDweller'
NEW_SPELLS = ['HC_Zone_StormDrainFlashFlood', 'HC_Shout_BlueTarpLeanTo', 'HC_Target_CulvertSiphon',
              'HC_Shout_SquattersRights_Overpass', 'HC_Target_DrainageDitchDigIn']
NEW_STATUSES = ['HC_TARP_COVER', 'HC_SPILLWAY_SOVEREIGN']
NEW_PASSIVES = ['HC_ConcreteBankTraction', 'HC_UnderpassClimateControl', 'HC_RebarAnchor']
LEVEL_GRANTS = {'3': (['HC_Zone_StormDrainFlashFlood', 'HC_Shout_BlueTarpLeanTo'], 'HC_ConcreteBankTraction'),
                '6': (['HC_Target_CulvertSiphon'], 'HC_UnderpassClimateControl'),
                # Level 10's spell comes from the hand-written SpellList_Overpass_L10 (BART L10 style), not
                # from an expansion list, so it is asserted in test_level_ten_spell_list_is_wired.
                '10': ([], 'HC_RebarAnchor'),
                '12': (['HC_Shout_SquattersRights_Overpass'], None)}


def attrs_of(node):
    return {a.get('id'): a.get('value', '') for a in node.findall('attribute')}


class OverpassSubclassTests(unittest.TestCase):
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
        cls.spells = parse_entries((data / 'HC_Spells_Overpass.txt').read_text(encoding='utf-8'))
        cls.spells.update(parse_entries((data / 'HC_Spells_Capstone.txt').read_text(encoding='utf-8')))
        cls.statuses = parse_entries((data / 'HC_Status_Overpass.txt').read_text(encoding='utf-8'))
        cls.statuses.update(parse_entries((data / 'HC_Status_Capstone.txt').read_text(encoding='utf-8')))
        cls.passives = parse_entries((data / 'HC_Passives_Overpass.txt').read_text(encoding='utf-8'))
        cls.progressions = ET.parse(cls.public / 'Progressions/Progressions.lsx')
        cls.spell_lists = {}
        for node in ET.parse(cls.public / 'Lists/SpellLists.lsx').findall('.//node[@id="SpellList"]'):
            a = attrs_of(node)
            cls.spell_lists[a['UUID']] = a['Spells'].split(';')
        loca = ET.parse(cls.public / 'Localization/English/HomelessCalifornian.loca.xml')
        cls.loca = {c.get('contentuid'): c.text for c in loca.iter('content')}

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def overpass_progressions(self):
        result = {}
        for node in self.progressions.findall('.//node[@id="Progression"]'):
            a = attrs_of(node)
            if a.get('Name') == SUBCLASS:
                result[a['Level']] = a
        return result

    # ------------------------------------------------------------------ wiring
    def test_guids_are_deterministic_and_distinct(self):
        self.assertEqual(generator.SUBCLASS_OVERPASS_UUID, generator.get_guid('Subclass_Overpass'))
        self.assertEqual(generator.SUBCLASS_OVERPASS_TABLE_UUID, generator.get_guid('Subclass_Overpass_Table'))
        others = {generator.SUBCLASS_TENDERLOIN_UUID, generator.SUBCLASS_VENICE_UUID, generator.SUBCLASS_BART_UUID,
                  generator.SUBCLASS_TENDERLOIN_TABLE_UUID, generator.SUBCLASS_VENICE_TABLE_UUID,
                  generator.SUBCLASS_BART_TABLE_UUID, generator.CLASS_UUID, generator.PROG_TABLE_UUID}
        self.assertNotIn(generator.SUBCLASS_OVERPASS_UUID, others)
        self.assertNotIn(generator.SUBCLASS_OVERPASS_TABLE_UUID, others)

    def test_class_description_node(self):
        tree = ET.parse(self.public / 'ClassDescriptions/ClassDescriptions.lsx')
        nodes = [n for n in tree.findall('.//node[@id="ClassDescription"]')
                 if attrs_of(n).get('Name') == SUBCLASS]
        self.assertEqual(len(nodes), 1)
        a = attrs_of(nodes[0])
        self.assertEqual(a['UUID'], generator.SUBCLASS_OVERPASS_UUID)
        self.assertEqual(a['ParentGuid'], generator.CLASS_UUID)
        self.assertEqual(a['ProgressionTableUUID'], generator.SUBCLASS_OVERPASS_TABLE_UUID)
        name_handle = nodes[0].find('attribute[@id="DisplayName"]').get('handle')
        desc_handle = nodes[0].find('attribute[@id="Description"]').get('handle')
        self.assertEqual(self.loca[name_handle], 'Overpass Riverbed Dweller')
        self.assertEqual(self.loca[desc_handle],
                         'A survivalist who keeps house in concrete flood channels and under freeway overpasses. '
                         'The ground is always doing something. You are used to it.')

    def test_subclass_offered_at_base_level_three(self):
        for node in self.progressions.findall('.//node[@id="Progression"]'):
            a = attrs_of(node)
            if a.get('Name') == 'HomelessCalifornian' and a.get('Level') == '3':
                objects = [n.get('value') for n in node.iter('attribute') if n.get('id') == 'Object']
                self.assertEqual(len(objects), 4)
                self.assertIn(generator.SUBCLASS_OVERPASS_UUID, objects)
                return
        self.fail('No base level 3 progression')

    def test_four_progression_levels_on_the_subclass_table(self):
        progs = self.overpass_progressions()
        self.assertEqual(sorted(progs, key=int), ['3', '6', '10', '12'])
        for level, a in progs.items():
            self.assertEqual(a['ProgressionType'], '1', f'level {level}')
            self.assertEqual(a['TableUUID'], generator.SUBCLASS_OVERPASS_TABLE_UUID, f'level {level}')

    def test_spell_lists_and_passives_attach_at_the_right_levels(self):
        progs = self.overpass_progressions()
        for level, (spells, passive) in LEVEL_GRANTS.items():
            a = progs[level]
            if spells:
                uid = generator.get_guid(f'HC_ExpansionList_{SUBCLASS}_{level}')
                self.assertEqual(self.spell_lists[uid], spells)
                self.assertIn(f'AddSpells({uid})', a['Selectors'])
            elif level != '10':
                self.assertNotIn('AddSpells', a.get('Selectors', ''))
            if passive:
                self.assertEqual(a['PassivesAdded'], passive)
            else:
                self.assertNotIn('PassivesAdded', a)

    def test_level_ten_spell_list_is_wired(self):
        uid = generator.SPELLLIST_OVERPASS_L10
        self.assertEqual(uid, generator.get_guid('SpellList_Overpass_L10'))
        self.assertNotEqual(uid, generator.SPELLLIST_BART_L10)
        self.assertEqual(self.spell_lists[uid], ['HC_Target_DrainageDitchDigIn'])
        a = self.overpass_progressions()['10']
        self.assertEqual(a['Selectors'], f'AddSpells({uid})')
        self.assertEqual(a['PassivesAdded'], 'HC_RebarAnchor')
        # Granted exactly once: not also through an expansion list, and not at any other level.
        for level, other in self.overpass_progressions().items():
            if level == '10':
                continue
            for list_id in re.findall(r'AddSpells\(([^)]+)\)', other.get('Selectors', '')):
                self.assertNotIn('HC_Target_DrainageDitchDigIn', self.spell_lists[list_id], f'level {level}')
        occurrences = sum(spells.count('HC_Target_DrainageDitchDigIn') for spells in self.spell_lists.values())
        self.assertEqual(occurrences, 1)

    def test_every_new_stat_is_defined(self):
        self.assertEqual(sorted(self.spells.keys() & set(NEW_SPELLS)), sorted(NEW_SPELLS))
        self.assertEqual(sorted(self.statuses.keys() & set(NEW_STATUSES)), sorted(NEW_STATUSES))
        self.assertEqual(sorted(self.passives), sorted(NEW_PASSIVES))
        for level, (spells, passive) in LEVEL_GRANTS.items():
            for s in spells:
                self.assertIn(s, self.spells)
            if passive:
                self.assertIn(passive, self.passives)

    def test_no_missing_donors(self):
        vanilla = validator.read_stats(ROOT / 'temp_race')
        own = {**self.spells, **self.statuses, **self.passives}
        for name in NEW_SPELLS + NEW_STATUSES + NEW_PASSIVES:
            donor = own[name]['using']
            if donor is None:
                continue
            self.assertIn(donor, vanilla, f'{name}: donor {donor} not in local vanilla reference')
            self.assertEqual(vanilla[donor][-1].type, 'SpellData', name)

    def test_loca_present_for_every_new_stat(self):
        for entries in (self.spells, self.statuses, self.passives):
            for name, e in entries.items():
                if name not in NEW_SPELLS + NEW_STATUSES + NEW_PASSIVES:
                    continue
                for key in ('DisplayName', 'Description'):
                    handle = e['data'][key].split(';')[0]
                    self.assertIn(handle, self.loca, f'{name}.{key}')
                    self.assertTrue(self.loca[handle].strip(), f'{name}.{key} is empty')

    # ------------------------------------------------------------------ passives / statuses
    def test_passive_boosts(self):
        self.assertEqual(self.passives['HC_ConcreteBankTraction']['data']['Boosts'],
                         'StatusImmunity(DIFFICULT_TERRAIN);StatusImmunity(DIFFICULT_TERRAIN_MUD);StatusImmunity(DIFFICULT_TERRAIN_WEB);StatusImmunity(DIFFICULT_TERRAIN_VINES)')
        self.assertEqual(self.passives['HC_UnderpassClimateControl']['data']['Boosts'],
                         'Resistance(Lightning,Resistant);Resistance(Cold,Resistant)')
        rebar = self.passives['HC_RebarAnchor']['data']['Boosts'].split(';')
        self.assertCountEqual(rebar, ['AC(1)', 'Advantage(SavingThrow,Strength)'])

    def test_status_boosts_and_no_auras(self):
        tarp = self.statuses['HC_TARP_COVER']['data']
        self.assertEqual(tarp['StatusType'], 'BOOST')
        self.assertCountEqual(tarp['Boosts'].split(';'), ['AC(1)', 'Advantage(SavingThrow,Dexterity)'])
        sov = self.statuses['HC_SPILLWAY_SOVEREIGN']['data']
        self.assertCountEqual(sov['Boosts'].split(';'), ['AC(2)', 'ActionResource(Movement,3,0)'])
        for name in NEW_STATUSES:
            self.assertNotIn('AuraStatuses', self.statuses[name]['data'])
            self.assertNotIn('AuraRadius', self.statuses[name]['data'])

    # ------------------------------------------------------------------ spells
    def test_storm_drain_flash_flood(self):
        e = self.spells['HC_Zone_StormDrainFlashFlood']
        d = e['data']
        self.assertEqual(e['using'], 'Zone_Thunderwave')
        self.assertEqual(d['UseCosts'], 'ActionPoint:1;HC_Junk:1')
        self.assertEqual(d['Cooldown'], 'OncePerShortRest')
        self.assertEqual(d['Range'], '9')
        self.assertIn('SavingThrow(Ability.Strength', d['SpellRoll'])
        self.assertIn('DealDamage(2d8+ConstitutionModifier,Bludgeoning', d['SpellSuccess'])
        self.assertIn('ApplyStatus(PRONE,100,1)', d['SpellSuccess'])
        self.assertIn('DealDamage((2d8+ConstitutionModifier)/2,Bludgeoning', d['SpellFail'])
        self.assertNotIn('PRONE', d['SpellFail'])
        self.assertEqual(d['SpellProperties'], '')
        self.assertEqual((d['SurfaceType'], d['SurfaceLifetime']), ('Water', '2'))
        # Inherited Thunderwave facts must be gone.
        self.assertNotIn('Thunder', d['TooltipDamageList'])
        self.assertNotIn('Force(', d['SpellSuccess'])
        self.assertEqual(d['TooltipAttackSave'], 'Strength')

    def test_blue_tarp_lean_to(self):
        e = self.spells['HC_Shout_BlueTarpLeanTo']
        d = e['data']
        self.assertEqual(e['using'], 'Shout_SecondWind')
        self.assertEqual(d['UseCosts'], 'BonusActionPoint:1;HC_Junk:1')
        self.assertEqual(d['Cooldown'], 'OncePerShortRest')
        self.assertEqual(d['AreaRadius'], '3')
        self.assertIn('Ally() or Self()', d['TargetConditions'])
        self.assertNotIn('Enemy', d['TargetConditions'])
        self.assertIn('ApplyStatus(HC_TARP_COVER,100,2)', d['SpellProperties'])
        self.assertIn('GROUND:SurfaceChange(Douse)', d['SpellProperties'])

    def test_culvert_siphon(self):
        e = self.spells['HC_Target_CulvertSiphon']
        d = e['data']
        self.assertEqual(e['using'], 'Target_CureWounds')
        self.assertEqual(d['UseCosts'], 'ActionPoint:1;HC_Junk:1')
        self.assertEqual(d['Cooldown'], 'OncePerShortRest')
        self.assertEqual(d['TargetRadius'], '9')
        self.assertIn('Ally() or Self()', d['TargetConditions'])
        for functor in ('RegainHitPoints(2d6+ConstitutionModifier)', 'RemoveStatus(BURNING)',
                        'GROUND:SurfaceChange(Douse)'):
            self.assertIn(functor, d['SpellProperties'])
        self.assertNotIn('IsMelee', d['SpellFlags'])
        self.assertNotIn('SpellCastingAbilityModifier', d['TooltipDamageList'])

    def test_drainage_ditch_dig_in(self):
        e = self.spells['HC_Target_DrainageDitchDigIn']
        d = e['data']
        self.assertEqual(e['using'], 'Target_CreateWater')
        self.assertEqual(d['UseCosts'], 'ActionPoint:1;HC_Junk:1')
        self.assertEqual(d['Cooldown'], 'OncePerShortRest')
        self.assertEqual(d['TargetRadius'], '9')
        self.assertEqual(d['SpellContainerID'], '')
        self.assertEqual(d['SpellProperties'], 'GROUND:CreateSurface(3,3,Mud)')
        # The surface radius and the targeting area match, and the donor's Wet/Water effects are gone.
        self.assertEqual(d['AreaRadius'], '3')
        self.assertNotIn('WET', d['SpellProperties'])
        self.assertNotIn('Water', d['SpellProperties'])
        self.assertEqual(d['TooltipStatusApply'], '')
        # Icon falls back to a vanilla icon that exists in the extracted vanilla spell data.
        self.assertEqual(d['Icon'], 'Spell_Conjuration_Grease')
        vanilla_targets = (ROOT / 'temp_race/Public/Shared/Stats/Generated/Data/Spell_Target.txt').read_text(encoding='utf-8')
        self.assertIn('data "Icon" "Spell_Conjuration_Grease"', vanilla_targets)
        # Every name the spell leans on exists in the vanilla reference.
        self.assertIn('CreateSurface(2,2,Mud)', vanilla_targets)
        self.assertIn('new entry "DIFFICULT_TERRAIN_MUD"',
                      (ROOT / 'temp_race/Public/Shared/Stats/Generated/Data/Status_BOOST.txt').read_text(encoding='utf-8'))

    def test_drainage_ditch_text_and_immunity_interaction(self):
        text = self.loca[self.spells['HC_Target_DrainageDitchDigIn']['data']['Description'].split(';')[0]]
        for fact in ('an action and 1 Junk', 'once per short rest', '9 m', '3 m radius', 'difficult terrain', '3 turns',
                     'Concrete Bank Traction'):
            self.assertIn(fact, text)
        self.assertTrue(text.endswith('Technically a flood-control project.'))
        self.assertEqual(self.loca[self.spells['HC_Target_DrainageDitchDigIn']['data']['DisplayName'].split(';')[0]],
                         'Drainage Ditch Dig-In')
        # The subclass passive that makes the caster ignore the mud is the one granted at level 3.
        self.assertIn('StatusImmunity(DIFFICULT_TERRAIN_MUD)', self.passives['HC_ConcreteBankTraction']['data']['Boosts'])

    def test_overpass_capstone_matches_the_sibling_capstones(self):
        d = self.spells['HC_Shout_SquattersRights_Overpass']['data']
        self.assertEqual(self.spells['HC_Shout_SquattersRights_Overpass']['using'], 'Shout_SecondWind')
        self.assertEqual(d['UseCosts'], 'BonusActionPoint:1')
        self.assertEqual(d['Cooldown'], 'OncePerRest')
        self.assertIn('ApplyStatus(HC_SPILLWAY_SOVEREIGN,100,3)', d['SpellProperties'])
        self.assertIn('RestoreResource(HC_Junk,100%,0)', d['SpellProperties'])
        self.assertIn('GROUND:CreateSurface(4,3,Mud)', d['SpellProperties'])
        # Same Junk-restore text as the siblings, and the same cooldown.
        sibling = self.spells['HC_Shout_SquattersRights_BART']['data']
        self.assertEqual(d['Cooldown'], sibling['Cooldown'])
        self.assertEqual(d['UseCosts'], sibling['UseCosts'])

    def test_only_the_capstone_restores_junk(self):
        for name in ('HC_Zone_StormDrainFlashFlood', 'HC_Shout_BlueTarpLeanTo', 'HC_Target_CulvertSiphon'):
            self.assertNotIn('RestoreResource', self.spells[name]['data']['SpellProperties'])
            self.assertNotIn('RestoreResource', self.spells[name]['data'].get('SpellSuccess', ''))

    def test_costs_use_existing_resources_and_no_reactions(self):
        for name in NEW_SPELLS:
            cost = self.spells[name]['data']['UseCosts']
            for token in filter(None, cost.split(';')):
                self.assertIn(token.split(':')[0], {'ActionPoint', 'BonusActionPoint', 'HC_Junk'}, f'{name}: {cost}')
            self.assertNotIn('Reaction', cost)
            self.assertNotIn('SpellSlot', cost)

    def test_no_new_action_resource_is_introduced(self):
        resources = ET.parse(self.public / 'ActionResourceDefinitions/ActionResourceDefinitions.lsx')
        self.assertEqual([a.get('value') for a in resources.findall('.//attribute[@id="Name"]')], ['HC_Junk'])

    def test_text_rules_no_em_dashes_or_emojis(self):
        for name in NEW_SPELLS + NEW_STATUSES + NEW_PASSIVES:
            for entries in (self.spells, self.statuses, self.passives):
                if name not in entries:
                    continue
                for key in ('DisplayName', 'Description'):
                    text = self.loca[entries[name]['data'][key].split(';')[0]]
                    self.assertNotIn('—', text, f'{name}.{key}')
                    self.assertTrue(re.fullmatch(r"[\x20-\x7E]+", text), f'{name}.{key} has non-ASCII text')


if __name__ == '__main__':
    unittest.main()
