"""Round 4 file-level contracts, generated in isolation; not engine validation."""
import contextlib
import io
from pathlib import Path
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
import hc_round4 as round4
import validate
from hc_icon_keys import SPELL_ICON_KEYS


class RoundFourTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.tmp.name)
        cls.public = cls.root / 'Public/HomelessCalifornian'
        with patch.object(generator, 'PUBLIC_DIR', str(cls.public)), \
                patch.object(generator, 'MODS_DIR', str(cls.root / 'Mods/HomelessCalifornian')), \
                patch.dict(generator.LOCA_ENTRIES, {}, clear=True), \
                contextlib.redirect_stdout(io.StringIO()):
            generator.main()
        cls.stats = validate.read_stats(cls.public)
        cls.vanilla = validate.read_stats(ROOT / 'temp_race')
        cls.new = {k: v[0] for k, v in cls.stats.items() if v[0].path.name.endswith('_Round4.txt')}
        cls.loca = {e.get('contentuid'): e.text for e in
                    ET.parse(cls.public / 'Localization/English/HomelessCalifornian.loca.xml').iter('content')}
        cls.progs = [cls.attrs(n) for n in ET.parse(cls.public / 'Progressions/Progressions.lsx')
                     .findall('.//node[@id="Progression"]')]
        cls.lists = {cls.attrs(n)['UUID']: cls.attrs(n)['Spells'].split(';') for n in
                     ET.parse(cls.public / 'Lists/SpellLists.lsx').findall('.//node[@id="SpellList"]')}

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    @staticmethod
    def attrs(node):
        return {a.get('id'): a.get('value') for a in node.findall('attribute')}

    def fields(self, name):
        return self.new[name].fields

    def grants(self, prog):
        return [s for uid in re.findall(r'AddSpells\(([0-9a-f-]+)', prog.get('Selectors', ''))
                for s in self.lists[uid]]

    def test_all_entries_are_unique_prefixed_and_do_not_override_vanilla(self):
        self.assertEqual(len(self.new), 17)
        for name in self.new:
            self.assertTrue(name.startswith('HC_'))
            self.assertNotIn(name, self.vanilla)
            self.assertEqual(len(self.stats[name]), 1)

    def test_all_donors_exist_in_extraction(self):
        for entry in self.new.values():
            if entry.using:
                self.assertIn(entry.using, self.vanilla)
                self.assertTrue(any(e.type == entry.type for e in self.vanilla[entry.using]))
        self.assertNotIn('TASHAS_HIDEOUS_LAUGHTER', self.vanilla)
        self.assertNotIn('SLOWED', self.vanilla)

    def test_supported_syntax_has_evidence_across_all_five_layers(self):
        layers = {p.parent.parent.parent.parent.name for p in
                  (ROOT / 'temp_race/Public').glob('*/Stats/Generated/Data/*.txt')}
        self.assertEqual(layers, set(validate.LAYERS))
        corpus = '\n'.join(e.body for es in self.vanilla.values() for e in es)
        compact = re.sub(r'\s+', '', corpus)
        for snippet in ('StatusId(\'EXTRA_ATTACK_Q\')', 'OnStatusApplied', 'OnSurfaceEnter',
                        'OnShortRest;OnLongRest', "InSurface('SurfaceWaterFrozen')",
                        "InSurface('SurfaceBloodFrozen')", 'HasHPMoreThan(48)',
                        'ActionResourceBlock(BonusActionPoint)', 'ActionResource(Movement,-3,0)',
                        'RemoveCause(StatusRemoveCause.Condition)',
                        'SavingThrow(Ability.Wisdom,SourceSpellDC())', 'BreakConcentration()'):
            self.assertIn(re.sub(r'\s+', '', snippet), compact)
        self.assertIn("SavingThrow(Ability.Wisdom, 16, AdvantageOnFrightened(), DisadvantageOnFrightened())",
                      self.vanilla['Target_HAG_MaskOfTerror'][0].fields['SpellRoll'])

    def test_freeway_is_base_racial_only(self):
        self.assertIn(round4.FREEWAY, self.lists[generator.SPELLLIST_CALIFORNIAN_L1])
        found = [p for p in self.progs if round4.FREEWAY in self.grants(p)]
        self.assertEqual([(p['Name'], p['Level']) for p in found], [('Californian', '1')])

    def test_weather_passives_are_base_racial_only(self):
        names = {round4.WEATHER, *(round4.WEATHER + '_' + k for k in round4.WEATHER_LINES)}
        for name in names:
            found = [p for p in self.progs if name in p.get('PassivesAdded', '').split(';')]
            self.assertEqual([(p['Name'], p['Level']) for p in found], [('Californian', '1')])

    def test_permit_uses_free_round2_level_and_class_only(self):
        self.assertNotIn(round4.PERMIT_LEVEL, {2, 4, 8, 11})
        found = [p for p in self.progs if round4.PERMIT in self.grants(p)]
        self.assertEqual([(p['Name'], p['Level']) for p in found], [('HomelessCalifornian', '5')])

    def test_spell_costs_saves_range_and_single_target(self):
        for name, radius, cost in [(round4.FREEWAY, '9', 'ActionPoint:1'),
                                  (round4.PERMIT, '18', 'ActionPoint:1;HC_Junk:1')]:
            f = self.fields(name)
            self.assertEqual(f['TargetRadius'], radius)
            self.assertEqual(f['UseCosts'], cost)
            self.assertEqual(f['Cooldown'], 'OncePerShortRest')
            self.assertIn('SavingThrow(Ability.Wisdom, SourceSpellDC()', f['SpellRoll'])
            self.assertEqual(f['AmountOfTargets'], '1')
            self.assertNotIn('IsConcentration', f['SpellFlags'])
            self.assertEqual(f['MemoryCost'], '0')
            self.assertEqual(f['CombatAIOverrideSpell'], '')

    def test_freeway_removes_mechanical_prone(self):
        f = self.fields('HC_FREEWAY_DIRECTIONS')
        self.assertIsNone(self.new['HC_FREEWAY_DIRECTIONS'].using)
        self.assertEqual(f['StatusType'], 'INCAPACITATED')
        self.assertNotIn('SG_Prone', f['StatusGroups'])
        self.assertEqual(f['Boosts'], 'DetectDisturbancesBlock(true);')
        self.assertEqual(f['OnRemoveFunctors'], '')
        self.assertNotIn('AnimationStart', f)
        self.assertNotIn('UseLyingPickingState', f)
        self.assertIn('IntelligenceGreaterThan(4)', self.fields(round4.FREEWAY)['TargetConditions'])
        self.assertNotIn('IntelligenceGreaterThan(4)', self.fields(round4.PERMIT)['TargetConditions'])
        self.assertEqual(self.fields(round4.FREEWAY)['SpellSuccess'], 'ApplyStatus(HC_FREEWAY_DIRECTIONS,100,1)')

    def test_laughter_audio_and_animation_are_copied_explicitly(self):
        status = self.vanilla['HIDEOUS_LAUGHTER'][0]
        self.assertEqual(status.fields['SoundVocalLoop'], 'LAUGHTERMANIACAL')
        for field in ('SoundVocalLoop', 'SoundVocalStart', 'SoundVocalEnd', 'SoundStart',
                      'SoundStop', 'StillAnimationType', 'StillAnimationPriority'):
            self.assertEqual(self.fields('HC_FREEWAY_DIRECTIONS')[field], status.fields[field])

    def test_freeway_status_initiates_combat_and_keeps_overhead_flag(self):
        self.assertEqual(self.fields('HC_FREEWAY_DIRECTIONS')['StatusPropertyFlags'],
                         'OverheadOnTurn;InitiateCombat')

    def test_weather_is_display_only_with_exact_lines(self):
        for key, title in round4.WEATHER_LINES.items():
            f = self.fields('HC_WEATHER_' + key)
            self.assertEqual(self.loca[f['DisplayName'].split(';')[0]], title)
            self.assertEqual(f['Boosts'], '')
            self.assertNotIn('DisableOverhead', f['StatusPropertyFlags'])
            for field in ('Passives', 'StatusEffect', 'TickFunctors', 'OnApplyFunctors'):
                self.assertNotIn(field, f)
            donor = self.vanilla[self.new['HC_WEATHER_' + key].using][0]
            self.assertEqual(set(donor.fields), {'StatusType', 'DisplayName'})

    def test_weather_triggers_and_lock_precede_display(self):
        for key in round4.WEATHER_LINES:
            f = self.fields(round4.WEATHER + '_' + key)
            if key != 'ICE':
                self.assertEqual(f['StatsFunctorContext'], 'OnStatusApplied')
                self.assertIn(f"StatusId('{key}')", f['Conditions'])
            else:
                self.assertEqual(f['StatsFunctorContext'], 'OnSurfaceEnter')
                self.assertIn("InSurface('SurfaceWaterFrozen',context.Source)", f['Conditions'])
                self.assertIn("InSurface('SurfaceBloodFrozen',context.Source)", f['Conditions'])
            self.assertIn(f"not HasStatus('HC_WEATHER_{key}_USED',context.Source)", f['Conditions'])
            self.assertEqual(f['StatsFunctors'], f'ApplyStatus(SELF,HC_WEATHER_{key}_USED,100,-1);ApplyStatus(SELF,HC_WEATHER_{key},100,1)')

    def test_weather_reset_has_no_recursive_status_hook(self):
        f = self.fields(round4.WEATHER)
        self.assertEqual(f['StatsFunctorContext'], 'OnShortRest;OnLongRest')
        self.assertEqual(set(f['StatsFunctors'].split(';')),
                         {f'RemoveStatus(SELF,HC_WEATHER_{k}_USED)' for k in round4.WEATHER_LINES})

    def test_permit_stages_do_not_stack_penalties_or_retain_bane_roll_penalties(self):
        for stage in (3, 2, 1):
            f = self.fields(f'HC_PERMIT_PENDING_{stage}')
            self.assertEqual(self.new[f'HC_PERMIT_PENDING_{stage}'].using, 'BANE')
            self.assertEqual(f['StackId'], 'HC_PERMIT_PENDING')
            self.assertEqual(f['StackType'], 'Overwrite')
            self.assertEqual(f['Boosts'], 'ActionResourceBlock(BonusActionPoint);ActionResource(Movement,-3,0)')
            self.assertEqual(f['TickType'], 'EndTurn')
            self.assertEqual(f['RemoveEvents'], 'OnTurn')
            self.assertEqual(f['RemoveConditions'], round4.PERMIT_SAVE)

    def test_declared_transition_chain_smoke_only_not_engine_execution(self):
        current = 'HC_PERMIT_PENDING_3'
        visited = [current]
        # Interpret emitted transition declarations independently of generator loop.
        for success in (False, True, False, True, False, True):
            if not success:
                self.assertEqual(current, visited[-1])
                continue
            follow = self.fields(current)['OnRemoveFunctors']
            self.assertTrue(follow.startswith('IF(RemoveCause(StatusRemoveCause.Condition)):'))
            current = re.search(r'ApplyStatus\(SELF,(HC_[A-Z0-9_]+),100,(-?\d+)\)', follow)[1]
            visited.append(current)
        self.assertEqual(visited, ['HC_PERMIT_PENDING_3', 'HC_PERMIT_PENDING_2',
                                   'HC_PERMIT_PENDING_1', 'HC_PERMIT_APPROVED'])

    def test_cleansing_and_overwrite_do_not_trigger_approval(self):
        for stage in (3, 2, 1):
            f = self.fields(f'HC_PERMIT_PENDING_{stage}')
            self.assertIn('IF(RemoveCause(StatusRemoveCause.Condition)):', f['OnRemoveFunctors'])
            self.assertEqual(f['OnRemoveFunctors'].count('ApplyStatus('), 1)

    def test_approval_clones_slow_for_one_turn_without_new_save(self):
        f = self.fields('HC_PERMIT_APPROVED')
        self.assertIsNone(self.new['HC_PERMIT_APPROVED'].using)
        self.assertEqual(f['RemoveConditions'], '')
        self.assertEqual(f['RemoveEvents'], '')
        shared = next(e for e in self.vanilla['SLOW'] if 'Shared' in e.path.parts)
        for field in ('StatusType', 'Icon', 'SoundVocalStart', 'SoundLoop', 'SoundStop',
                      'TickType', 'Boosts', 'Passives', 'OnApplyFunctors', 'StatusEffect',
                      'ManagedStatusEffectType', 'ManagedStatusEffectGroup'):
            if field != 'Icon': self.assertEqual(f[field], shared.fields[field], field)
        self.assertEqual(f['StackId'], 'HC_PERMIT_APPROVED')
        self.assertNotIn('StackPriority', f)
        self.assertIn('ApplyStatus(SELF,HC_PERMIT_APPROVED,100,1)', self.fields('HC_PERMIT_PENDING_1')['OnRemoveFunctors'])
        self.assertEqual(self.loca[f['DisplayName'].split(';')[0]], 'Approved, pending review.')

    def test_initial_and_repeat_saves_use_only_current_hp_threshold(self):
        self.assertEqual(self.fields(round4.PERMIT)['SpellRoll'], 'not ' + round4.PERMIT_SAVE)
        for stage in (3, 2, 1):
            self.assertEqual(self.fields(f'HC_PERMIT_PENDING_{stage}')['RemoveConditions'], round4.PERMIT_SAVE)
        self.assertEqual(round4.BOSS_CHECK, 'HasHPMoreThan(100)')
        self.assertEqual(round4.PERMIT_SAVE, 'SavingThrow(Ability.Wisdom, SourceSpellDC(), HasHPMoreThan(100), false)')
        self.assertIn('CURRENT HP', round4.__doc__)
        description = self.loca[self.fields(round4.PERMIT)['Description'].split(';')[0]]
        self.assertIn('above 100 current HP', description)
        self.assertNotIn('Bosses', description)

    def test_no_round4_entry_inherits_prohibited_or_honour_overridden_names(self):
        honour_names = {name for name, entries in self.vanilla.items()
                        if any('Honour' in e.path.parts for e in entries)}
        prohibited = honour_names | {'SLOW', 'HIDEOUS_LAUGHTER'}
        for name, entry in self.new.items():
            self.assertNotIn(entry.using, prohibited, name)
        # Build the forbidden token from parts so it never appears in round-four source/output.
        forbidden = 'Is' + 'Boss'
        self.assertNotIn(forbidden, (ROOT / 'hc_round4.py').read_text(encoding='utf-8'))
        for entry in self.new.values():
            self.assertNotIn(forbidden, entry.body)

    def test_freeway_icon_and_copied_hold_person_save_fields(self):
        f = self.fields('HC_FREEWAY_DIRECTIONS')
        self.assertIn(f['Icon'], ("Spell_Enchantment_Tasha'sHideousLaughter", 'Spell_Status_FREEWAY_DIRECTIONS'))
        self.assertNotIn('DescriptionParams', f)
        self.assertNotIn('StatusEffect', f)
        hold = next(e for e in self.vanilla['HOLD_PERSON'] if 'Shared' in e.path.parts)
        for field in ('StatusType', 'TickType', 'RemoveConditions', 'RemoveEvents',
                      'TooltipSave', 'OnApplyFunctors'):
            self.assertEqual(f[field], hold.fields[field])
        self.assertEqual(f['StatusGroups'], 'SG_Incapacitated;SG_Condition')

    def test_empty_or_missing_racial_passives_do_not_replace_other_empty_attributes(self):
        original = generator.generate_progressions_lsx
        for mode in ('empty', 'missing'):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                public = root / 'Public/HomelessCalifornian'

                def altered_progressions():
                    original()
                    path = public / 'Progressions/Progressions.lsx'
                    tree = ET.parse(path)
                    for node in tree.findall('.//node[@id="Progression"]'):
                        attrs = self.attrs(node)
                        if attrs.get('Name') == 'Californian' and attrs.get('Level') == '1':
                            ET.SubElement(node, 'attribute', id='GuardEmpty', type='LSString', value='')
                            attr = node.find('attribute[@id="PassivesAdded"]')
                            if mode == 'empty':
                                attr.set('value', '')
                            else:
                                node.remove(attr)
                    tree.write(path, encoding='utf-8', xml_declaration=True)

                with patch.object(generator, 'PUBLIC_DIR', str(public)), \
                        patch.object(generator, 'MODS_DIR', str(root / 'Mods/HomelessCalifornian')), \
                        patch.object(generator, 'generate_progressions_lsx', altered_progressions), \
                        patch.dict(generator.LOCA_ENTRIES, {}, clear=True), \
                        contextlib.redirect_stdout(io.StringIO()):
                    generator.main()
                progs = [self.attrs(n) for n in ET.parse(public / 'Progressions/Progressions.lsx')
                         .findall('.//node[@id="Progression"]')]
                race = next(p for p in progs if p.get('Name') == 'Californian' and p.get('Level') == '1')
                self.assertEqual(race['GuardEmpty'], '')
                self.assertEqual(race['PassivesAdded'].split(';'), [round4.WEATHER,
                                 *(round4.WEATHER + '_' + k for k in round4.WEATHER_LINES)])

    def test_localization_and_icon_fallbacks_resolve(self):
        for e in self.new.values():
            for field in ('DisplayName', 'Description'):
                self.assertTrue(self.loca[e.fields[field].split(';')[0]])
        icons = {e.fields.get('Icon') for es in self.vanilla.values() for e in es}
        for name in (round4.FREEWAY, round4.PERMIT):
            self.assertIn(name, SPELL_ICON_KEYS)
            icon = self.fields(name)['Icon']
            self.assertTrue(icon in icons or (ROOT / 'assets/icons' / (icon + '.png')).is_file())

    def test_exact_requested_flavour(self):
        for name, line in [(round4.FREEWAY, 'You will want to take the 101. Trust the 101. There is no 101 at this hour.'),
                           (round4.PERMIT, 'Your form was received. Please allow 6-8 business turns.')]:
            self.assertTrue(self.loca[self.fields(name)['Description'].split(';')[0]].endswith(line))


if __name__ == '__main__':
    unittest.main()
