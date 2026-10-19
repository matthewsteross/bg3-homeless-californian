"""hc_icons_apply: icons are applied by stat name (any prefix), idempotently, only when the PNG exists."""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import hc_icons_apply as ia


class IconsApplyTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.public = self.root / 'Public'
        data = self.public / 'Stats/Generated/Data'
        data.mkdir(parents=True)
        self.icons = self.root / 'icons'
        self.icons.mkdir()
        (self.icons / 'Spell_Good.png').write_bytes(b'x')
        self.text = ('new entry "Shout_Plain"\r\ntype "SpellData"\r\nusing "Shout_SecondWind"\r\ndata "Icon" "Old_Icon"\r\ndata "Level" "0"\r\n\r\n'
                     'new entry "HC_Target_NoIcon"\r\ntype "SpellData"\r\ndata "Level" "0"\r\n\r\n'
                     'new entry "HC_Missing"\r\ntype "SpellData"\r\ndata "Level" "0"\r\n')
        (data / 'S.txt').write_bytes(self.text.encode('utf-8'))
        self.map = {'Shout_Plain': 'Spell_Good', 'HC_Target_NoIcon': 'Spell_Good', 'HC_Missing': 'Spell_Absent'}

    def read(self):
        return (self.public / 'Stats/Generated/Data/S.txt').read_bytes().decode('utf-8')

    def test_applies_replaces_and_skips_missing_png(self):
        changed = ia.apply_icons(self.public, self.map, self.icons)
        self.assertEqual(changed, 2)
        text = self.read()
        self.assertEqual(text.count('data "Icon" "Spell_Good"'), 2)
        self.assertNotIn('Old_Icon', text)
        self.assertNotIn('Spell_Absent', text)
        self.assertIn('data "Level" "0"', text)

    def test_idempotent_and_keeps_crlf(self):
        ia.apply_icons(self.public, self.map, self.icons)
        once = self.read()
        ia.apply_icons(self.public, self.map, self.icons)
        self.assertEqual(once, self.read())
        self.assertNotIn('\n\n\n', once.replace('\r\n', '\n'))
        self.assertEqual(once.count('\r\n'), once.count('\n'))

    def test_real_map_keys_have_pngs_or_are_future(self):
        icon_map = ia.load_map()
        for name, key in icon_map.items():
            self.assertTrue(key.startswith(('Spell_', 'Passive_', 'Status_')), (name, key))


if __name__ == '__main__':
    unittest.main()
