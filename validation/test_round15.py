import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

DATA = ROOT / 'src/HomelessCalifornian/Public/HomelessCalifornian'


class RoundFifteenTests(unittest.TestCase):
    def test_passives_defined_with_custom_icons(self):
        text = (DATA / 'Stats/Generated/Data/HC_Passives_Round15.txt').read_text(encoding='utf-8')
        for name, icon in (('HC_SoCalSigAlertSixthSense', 'Spell_Passive_SoCalSigAlert'),
                           ('HC_NorCalPreSeedPitchDeck', 'Spell_Passive_NorCalPreSeed')):
            self.assertIn(f'new entry "{name}"', text)
            self.assertIn(f'data "Icon" "{icon}"', text)
            self.assertTrue((ROOT / 'assets/icons' / f'{icon}.png').is_file())

    def test_granted_at_subrace_level_one(self):
        prog = (DATA / 'Progressions/Progressions.lsx').read_text(encoding='utf-8')
        for subrace, passive in (('Beachborn', 'HC_SoCalSigAlertSixthSense'), ('Siliconite', 'HC_NorCalPreSeedPitchDeck')):
            blocks = [b for b in re.split(r'(?=<node id="Progression">)', prog)
                      if f'value="{subrace}"' in b and 'id="Level" type="uint8" value="1"' in b and 'ProgressionType" type="uint8" value="2"' in b]
            self.assertEqual(len(blocks), 1, subrace)
            self.assertIn(passive, blocks[0])

    def test_only_proven_boost_forms(self):
        import hc_round15
        for _n, _t, _s, _d, boosts in hc_round15.PASSIVES:
            for part in boosts.split(';'):
                self.assertRegex(part, r'^(Initiative\(\d+\)|ActionResource\(Movement,[\d.]+,0\)|RollBonus\(Attack,\d+\)|Advantage\(Skill,Persuasion\))$')


if __name__ == '__main__':
    unittest.main()
