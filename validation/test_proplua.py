"""The Script Extender prop-cleanup files are generated and match the lifetime status name."""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import hc_proplua
import hc_prop_lifetime


class PropLuaTests(unittest.TestCase):
    def test_files_written_and_reference_lifetime_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = hc_proplua.generate_proplua(tmp)
            lua = (base / 'Lua' / 'BootstrapServer.lua').read_text(encoding='utf-8')
            config = (base / 'Config.json').read_text(encoding='utf-8')
        self.assertIn(hc_prop_lifetime.STATUS, lua)
        self.assertIn('RequestDelete', lua)
        self.assertIn('"ModTable": "HomelessCalifornian"', config)

    def test_built_source_contains_script(self):
        built = ROOT / 'src/HomelessCalifornian/Mods/HomelessCalifornian/ScriptExtender/Lua/BootstrapServer.lua'
        if not built.is_file():
            self.skipTest('built tree missing')
        self.assertEqual(built.read_text(encoding='utf-8'), hc_proplua.LUA)


if __name__ == '__main__':
    unittest.main()
