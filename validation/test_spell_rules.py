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

ALLOWED_RESOURCES = {'ActionPoint', 'BonusActionPoint', 'ReactionActionPoint', 'HC_Junk'}


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


if __name__ == '__main__':
    unittest.main()
