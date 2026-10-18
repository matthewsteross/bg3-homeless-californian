"""Regression tests for spell-data bugs found in the 2026-10-13 audit.

These run entirely on freshly generated data in a temporary tree (no game files needed).
"""
from pathlib import Path
import contextlib
import io
import re
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import generate_mod as generator

ALLOWED_RESOURCES = {'ActionPoint', 'BonusActionPoint', 'ReactionActionPoint', 'HC_Junk', 'HC_DiveCharge'}


def parse_entries(text):
    entries = {}
    cur = None
    for raw in text.splitlines():
        line = raw.strip()
        m = re.match(r'new entry "(.+)"', line)
        if m:
            cur = {'name': m.group(1), 'data': {}, 'using': None}
            entries[cur['name']] = cur
            continue
        if cur is None:
            continue
        m = re.match(r'using "(.+)"', line)
        if m:
            cur['using'] = m.group(1)
            continue
        m = re.match(r'data "(.+?)" "(.*)"$', line)
        if m:
            cur['data'][m.group(1)] = m.group(2)
    return entries


class SpellRuleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        source = Path(cls._tmp.name)
        public = source / 'Public/HomelessCalifornian'
        with patch.object(generator, 'PUBLIC_DIR', str(public)), \
                patch.object(generator, 'MODS_DIR', str(source / 'Mods/HomelessCalifornian')), \
                contextlib.redirect_stdout(io.StringIO()):
            generator.main()
        data = public / 'Stats/Generated/Data'
        cls.spells = {}
        for p in sorted(data.glob('HC_Spells_*.txt')):
            cls.spells.update(parse_entries(p.read_text(encoding='utf-8')))
        cls.statuses = {}
        for p in sorted(data.glob('*.txt')):
            cls.statuses.update(parse_entries(p.read_text(encoding='utf-8')))

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def test_beg_places_gold_in_caster_inventory(self):
        success = self.spells['HC_Target_Beg']['data']['SpellSuccess']
        self.assertIn('SELF:SummonInInventory(', success)

    def test_capstones_restore_all_junk(self):
        for name in ('HC_Shout_SquattersRights_Tenderloin', 'HC_Shout_SquattersRights_Venice', 'HC_Shout_SquattersRights_BART'):
            props = self.spells[name]['data']['SpellProperties']
            self.assertIn('RestoreResource(HC_Junk,100%,0)', props)

    def test_temp_hp_statuses_clear_on_damage(self):
        for name in ('POCKET_LINT_SNACK', 'SWEEP_SHELTER', 'AVOCADO_BLISS', 'SELF_ACTUALIZED'):
            entry = self.statuses[name]
            remove_events = entry['data'].get('RemoveEvents', '').split(';')
            self.assertIn('OnDamage', remove_events, f'{name} must evaluate RemoveConditions OnDamage')

    def test_no_target_filter_requires_a_status_on_the_target(self):
        """Regression: Guilt Trip / Public Scene / Compassion Burnout said 'Invalid Target' on everyone because
        TargetConditions demanded a status normal enemies never have. Statuses may only be *excluded* there."""
        for name, e in self.spells.items():
            cond = e['data'].get('TargetConditions', '')
            for m in re.finditer(r'(?<!not )HasStatus\(\s*\'[^\']+\'\s*\)', cond):
                self.fail(f'{name}: TargetConditions requires a target status ({m.group(0)}): {cond}')

    def test_every_cost_uses_a_resource_the_class_owns(self):
        for name, e in self.spells.items():
            for field in ('UseCosts', 'HitCosts', 'RitualCosts'):
                for token in filter(None, e['data'].get(field, '').split(';')):
                    self.assertIn(token.split(':')[0], ALLOWED_RESOURCES, f'{name}.{field}={e["data"][field]}')

    def test_junk_spells_charge_junk_when_cast_as_rituals(self):
        for name, e in self.spells.items():
            d = e['data']
            if 'HC_Junk' in d.get('UseCosts', '') and d.get('RitualCosts'):
                self.assertIn('HC_Junk', d['RitualCosts'], f'{name} skips its Junk cost when cast out of combat')

    def test_bucket_drum_solo_keeps_its_constitution_save(self):
        d = self.spells['HC_Zone_BucketDrumSolo']['data']
        self.assertIn('SavingThrow(Ability.Constitution', d['SpellRoll'])
        self.assertIn('DealDamage((2d6)/2', d['SpellFail'])

    def test_lithium_cell_rolls_to_hit_and_creates_fire(self):
        d = self.spells['HC_Projectile_PuncturedLithiumCell']['data']
        self.assertEqual(d['SpellRoll'], 'Attack(AttackType.RangedSpellAttack)')
        self.assertIn('CreateSurface(1.5,2,Fire)', d['SpellProperties'])

    def test_chair_check_has_attack_roll_no_superiority_cost_and_gated_prone(self):
        d = self.spells['HC_Target_ChairCheck']['data']
        self.assertEqual(d['SpellRoll'], 'Attack(AttackType.MeleeWeaponAttack)')
        self.assertEqual(d['HitCosts'], '')
        success = d['SpellSuccess']
        self.assertEqual(success.count('PRONE'), 1)
        self.assertRegex(success, r'IF\([^;]*SavingThrow\(Ability\.Strength[^;]*\):ApplyStatus\(PRONE,100,1\)$')
        self.assertNotIn('Force(', success)

    def test_beg_is_not_flagged_as_a_hostile_spell(self):
        flags = self.spells['HC_Target_Beg']['data']['SpellFlags'].split(';')
        self.assertNotIn('IsHarmful', flags)

    def test_save_gated_if_never_leaves_a_following_enemy_effect_ungated(self):
        """An IF(...) guards only the single functor after its colon."""
        for name, e in self.spells.items():
            for field in ('SpellSuccess', 'SpellProperties'):
                text = e['data'].get(field, '')
                depth, cur, segs = 0, '', []
                for ch in text:
                    depth += ch in '(['
                    depth -= ch in ')]'
                    if ch == ';' and depth == 0:
                        segs.append(cur.strip())
                        cur = ''
                    else:
                        cur += ch
                if cur.strip():
                    segs.append(cur.strip())
                for seg, nxt in zip(segs, segs[1:]):
                    if seg.startswith('IF(') and 'SavingThrow' in seg and re.match(r'(ApplyStatus|Force)\((?!SELF)', nxt):
                        self.fail(f'{name}.{field}: ungated functor after a save-gated IF: {nxt}')

    def test_dumpster_dive_yields_cheese_and_eaten_apple(self):
        props = self.spells['HC_Shout_DumpsterDive']['data']['SpellProperties']
        self.assertIn('SummonInInventory(06474f97-0dd0-45e6-8db8-5f75009bf336', props)
        self.assertIn('SummonInInventory(2ca3cb11-2271-461a-9096-c425c0bd3b12', props)

    def test_moving_day_and_i_was_here_first_create_rubbish_hazard(self):
        for name in ('HC_Shout_MovingDay', 'HC_Shout_IWasHereFirst'):
            props = self.spells[name]['data']['SpellProperties']
            self.assertIn('CreateSurface(2.5,2,Mud)', props)
        self.assertEqual(self.spells['HC_Shout_IWasHereFirst']['data']['UseCosts'], 'ActionPoint:1;HC_Junk:1')

    def test_pigeon_witness_protection_wires_lunch_rush(self):
        summon_props = self.spells['HC_Target_PigeonWitnessProtection']['data']['SpellProperties']
        self.assertIn('HC_PIGEON_WITNESS', summon_props)
        self.assertIn('UnlockSpell(HC_Shout_PigeonLunchRush)', self.statuses['HC_PIGEON_WITNESS']['data']['Boosts'])
        rush = self.spells['HC_Shout_PigeonLunchRush']['data']
        self.assertEqual(rush['AreaRadius'], '4')
        self.assertIn('SavingThrow(Ability.Dexterity', rush['SpellRoll'])
        self.assertIn('ApplyStatus(HC_DISTRACTED_BY_PIGEONS,100,1)', rush['SpellSuccess'])

    def test_californian_racial_glutes_and_hydroflask(self):
        glutes = self.statuses['RunyonCanyonGlutes']['data']['Boosts']
        self.assertIn('JumpMaxDistanceMultiplier(1.5)', glutes)
        self.assertIn('CarryCapacityMultiplier(1.25)', glutes)

        flask = self.statuses['Shout_EmotionalSupportHydroflask']['data']
        self.assertEqual(flask['Cooldown'], 'OncePerShortRest')
        self.assertEqual(flask['UseCosts'], 'BonusActionPoint:1')
        props = flask['SpellProperties']
        self.assertIn('RegainHitPoints(1d8+ConstitutionModifier)', props)
        self.assertIn('RemoveStatus(SG_Poisoned)', props)
        self.assertIn('GROUND:CreateSurface(1.5,1,Water)', props)

    def test_beachborn_racial_spells(self):
        rip = self.statuses['Target_RipCurrent']['data']
        self.assertEqual(rip['Cooldown'], 'OncePerShortRest')
        self.assertIn('DealDamage(2d6,Cold', rip['SpellSuccess'])
        self.assertIn('Force(-4.5, OriginToEntity', rip['SpellSuccess'])
        self.assertIn('ApplyStatus(PRONE,100,1)', rip['SpellSuccess'])
        self.assertIn('CreateSurface(1.5,1,Water)', rip['SpellSuccess'])

        golden = self.statuses['Shout_GoldenHour']['data']
        self.assertEqual(golden['Cooldown'], 'OncePerRest')
        self.assertEqual(golden['AreaRadius'], '6')
        self.assertIn('SavingThrow(Ability.Constitution', golden['SpellRoll'])
        self.assertIn('ApplyStatus(BLINDED,100,2)', golden['SpellSuccess'])
        self.assertIn('ApplyStatus(SELF,GOLDEN_HOUR_GLOW,100,2)', golden['SpellProperties'])

        glow = self.statuses['GOLDEN_HOUR_GLOW']['data']['Boosts']
        self.assertIn('ActionResource(Movement,3,0)', glow)
        self.assertIn('CharacterWeaponDamage(1d4,Radiant)', glow)

    def test_siliconite_racial_spells(self):
        pivot_entry = self.statuses['Target_DisruptivePivot']
        pivot = pivot_entry['data']
        self.assertEqual(pivot_entry['using'], 'Target_MistyStep')
        self.assertEqual(pivot['Cooldown'], 'OncePerRest')
        self.assertEqual(pivot['TargetRadius'], '9')
        self.assertEqual(pivot['UseCosts'], 'BonusActionPoint:1')
        self.assertIn('GROUND:ApplyStatus(SELF,DISRUPTIVE_PIVOT_ADV,100,1)', pivot['SpellProperties'])

        adv = self.statuses['DISRUPTIVE_PIVOT_ADV']['data']
        self.assertIn('Advantage(AttackRoll)', adv['Boosts'])
        self.assertIn('OnAttack', adv['RemoveEvents'])

        nda = self.statuses['Target_NonDisclosureAgreement']['data']
        self.assertEqual(nda['Cooldown'], 'OncePerRest')
        self.assertIn('SavingThrow(Ability.Wisdom', nda['SpellRoll'])
        self.assertIn('DealDamage(2d8,Psychic', nda['SpellSuccess'])
        self.assertIn('ApplyStatus(SILENCED,100,2)', nda['SpellSuccess'])

    def test_inland_emperor_racial_spells(self):
        dust = self.statuses['Shout_DustDevil']['data']
        self.assertEqual(dust['Cooldown'], 'OncePerShortRest')
        self.assertEqual(dust['AreaRadius'], '3')
        self.assertEqual(dust['UseCosts'], 'BonusActionPoint:1')
        self.assertIn('ApplyStatus(SELF,BLUR,100,1)', dust['SpellProperties'])
        self.assertIn('ApplyStatus(BLINDED,100,1)', dust['SpellSuccess'])

        exhaust_entry = self.statuses['Zone_OverpassExhaust']
        exhaust = exhaust_entry['data']
        self.assertEqual(exhaust_entry['using'], 'Zone_BurningHands')
        self.assertEqual(exhaust['Cooldown'], 'OncePerRest')
        self.assertEqual(exhaust['Range'], '6')
        self.assertIn('DealDamage(2d8,Poison', exhaust['SpellSuccess'])
        self.assertIn('DealDamage(1d8,Fire', exhaust['SpellSuccess'])

        heat = self.statuses['Target_Heatstroke']['data']
        self.assertEqual(heat['Cooldown'], 'OncePerRest')
        self.assertIn('SavingThrow(Ability.Constitution', heat['SpellRoll'])
        self.assertIn('DealDamage(3d8,Fire', heat['SpellSuccess'])
        self.assertIn('ApplyStatus(HEATSTROKE,100,2)', heat['SpellSuccess'])

        stroke = self.statuses['HEATSTROKE']['data']['Boosts']
        self.assertIn('ActionResourceMultiplier(Movement,50,0)', stroke)
        self.assertIn('Disadvantage(AttackRoll)', stroke)
        self.assertIn('Disadvantage(SavingThrow,Strength)', stroke)
        self.assertIn('Disadvantage(SavingThrow,Dexterity)', stroke)


if __name__ == '__main__':
    unittest.main()

