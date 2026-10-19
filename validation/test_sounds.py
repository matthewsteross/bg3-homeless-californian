"""Meme sounds (hc_sounds.py + hc_sound_map.json): every event is a real vanilla event, only HC spells are touched.

File-level checks only; whether each event is audible in game is unverified.
"""
from pathlib import Path
import re
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import hc_sounds

VANILLA = ROOT / 'temp_race' / 'Public'
STATS = ROOT / 'src' / 'HomelessCalifornian' / 'Public' / 'HomelessCalifornian' / 'Stats' / 'Generated' / 'Data'


def vanilla_events():
    events = set()
    for p in VANILLA.glob('*/Stats/Generated/Data/*.txt'):
        text = p.read_text(encoding='utf-8', errors='ignore')
        events.update(re.findall(r'data "(?:CastSound|TargetSound|PrepareSound)" "([^"]+)"', text))
    return events


class SoundMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.map = hc_sounds.load_map()

    def test_map_is_not_empty_and_only_names_hc_spells(self):
        self.assertGreaterEqual(len(self.map), 30)
        own_stats = ''.join(p.read_text(encoding='utf-8') for p in (ROOT / 'src/HomelessCalifornian/Public/HomelessCalifornian/Stats/Generated/Data').glob('*.txt'))
        for spell, sounds in self.map.items():
            self.assertTrue(spell.startswith('HC_') or ('new entry "%s"' % spell) in own_stats, spell)  # class actions keep vanilla-style names but are defined in our own stats
            self.assertTrue(sounds, spell)
            self.assertTrue(set(sounds) <= set(hc_sounds.FIELDS), (spell, sounds))

    def test_every_event_is_a_real_vanilla_event(self):
        known = vanilla_events()
        self.assertGreater(len(known), 1500)
        for spell, sounds in self.map.items():
            for field, event in sounds.items():
                self.assertIn(event, known, (spell, field, event))

    def test_events_are_varied(self):
        counts = {}
        for sounds in self.map.values():
            for event in sounds.values():
                counts[event] = counts.get(event, 0) + 1
        self.assertLessEqual(max(counts.values()), 5, counts)

    def test_every_spell_exists_as_spelldata(self):
        text = ''.join(p.read_text(encoding='utf-8') for p in STATS.glob('HC_*.txt'))
        text += ''.join(p.read_text(encoding='utf-8') for p in STATS.glob('Spell_*.txt'))
        for spell in self.map:
            self.assertRegex(text, r'new entry "%s"\s*\r?\ntype "SpellData"' % re.escape(spell), spell)

    def test_apply_is_idempotent_and_only_touches_mapped_spells(self):
        with tempfile.TemporaryDirectory() as tmp:
            public = Path(tmp) / 'Public'
            data = public / 'Stats' / 'Generated' / 'Data'
            data.mkdir(parents=True)
            for p in STATS.glob('*.txt'):
                shutil.copy(p, data / p.name)
            before = {p.name: p.read_bytes() for p in data.glob('*.txt')}
            changed = hc_sounds.apply_sounds(public, self.map)
            self.assertEqual(changed, len(self.map))
            after = {p.name: p.read_bytes() for p in data.glob('*.txt')}
            again = hc_sounds.apply_sounds(public, self.map)
            self.assertEqual(again, len(self.map))
            self.assertEqual(after, {p.name: p.read_bytes() for p in data.glob('*.txt')})
            joined = ''.join(b.decode('utf-8') for b in after.values())
            for spell, sounds in self.map.items():
                block = joined.split(f'new entry "{spell}"')[1].split('new entry "')[0]
                for field, event in sounds.items():
                    self.assertEqual(block.count(f'data "{field}" '), 1, (spell, field))
                    self.assertIn(f'data "{field}" "{event}"', block)
            # unmapped spells keep their exact bytes: compare the entry text of one unmapped HC spell
            unmapped = next((s for s in re.findall(r'new entry "(HC_[A-Za-z0-9_]+)"\s*\r?\ntype "SpellData"',
                                                 ''.join(b.decode('utf-8') for b in before.values()))
                            if s not in self.map), None)
            if unmapped is None:  # every HC spell is mapped now
                return
            old = ''.join(b.decode('utf-8') for b in before.values()).split(f'new entry "{unmapped}"')[1].split('new entry "')[0]
            new = joined.split(f'new entry "{unmapped}"')[1].split('new entry "')[0]
            self.assertEqual(old, new)


if __name__ == '__main__':
    unittest.main()
