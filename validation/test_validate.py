"""Intentional corrupt fixtures, never modify generated/game source."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
import sys

spec = importlib.util.spec_from_file_location('hc_validator', Path(__file__).with_name('validate.py'))
v = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = v
spec.loader.exec_module(v)

class ValidatorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.source = Path(self.tmp.name) / 'source'
        self.vanilla = Path(self.tmp.name) / 'vanilla'
        self.source.mkdir(); self.vanilla.mkdir()
        self.write(self.source, 'Public/HC/Stats/Generated/Data/Spell.txt', 'new entry "Test"\ntype "SpellData"\ndata "UseCosts" ""\n')
        self.write(self.vanilla, 'Public/Shared/Stats/Generated/Data/Base.txt', 'new entry "VALID_STATUS"\ntype "StatusData"\ndata "StatusGroups" "SG_Prone"\nnew entry "BaseSpell"\ntype "SpellData"\ndata "SpellProperties" "CreateSurface(1,2,Mud)"\n')
    def write(self, root, path, content):
        p = root / path; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(content, encoding='utf-8')
        return p
    def stat(self, body):
        self.write(self.source, 'Public/HC/Stats/Generated/Data/Spell.txt', 'new entry "Test"\ntype "SpellData"\n' + body)
    def check(self): return v.validate(self.source, self.vanilla, require_vanilla=False)[0]
    def test_valid_fixture(self): self.assertEqual(self.check(), [])
    def test_missing_status_without_custom_prefix(self):
        self.stat('data "SpellSuccess" "ApplyStatus(MISSING,100,1)"\n')
        self.assertTrue(any('MISSING' in x for x in self.check()))
    def test_missing_passive_and_spell(self):
        self.stat('data "Boosts" "UnlockSpell(MissingSpell)"\ndata "Conditions" "HasPassive(\'MissingPassive\')"\n')
        errors = self.check()
        self.assertTrue(any('MissingSpell' in x for x in errors))
        self.assertTrue(any('MissingPassive' in x for x in errors))
    def test_status_groups_are_valid(self):
        self.stat('data "Boosts" "StatusImmunity(SG_Prone)"\ndata "SpellProperties" "RemoveStatus(SG_Prone)"\n')
        self.assertEqual(self.check(), [])
    def test_self_status_removal_still_checks_actual_status(self):
        self.stat('data "SpellProperties" "RemoveStatus(SELF,VALID_STATUS)"\n')
        self.assertEqual(self.check(), [])
        self.stat('data "SpellProperties" "RemoveStatus(SELF,MISSING_STATUS)"\n')
        self.assertTrue(any('MISSING_STATUS' in x for x in self.check()))
    def test_duplicate_stats(self):
        self.write(self.source, 'Public/HC/Stats/Generated/Data/Other.txt', 'new entry "Test"\ntype "StatusData"\n')
        self.assertTrue(any('Duplicate stat' in x for x in self.check()))
    def test_wrong_using_type_and_cycles(self):
        self.stat('using "VALID_STATUS"\ndata "UseCosts" ""\n')
        self.assertTrue(any('using' in x for x in self.check()))
        self.stat('using "Test"\ndata "UseCosts" ""\n')
        self.assertTrue(any('cyclic' in x for x in self.check()))
    def test_missing_icon_and_handle(self):
        self.stat('data "Icon" "MISSING_ICON"\ndata "DisplayName" "h00000000g0000g0000g0000g000000000000;1"\n')
        errors = self.check()
        self.assertTrue(any('undefined icon' in x for x in errors))
        self.assertTrue(any('missing localization' in x for x in errors))
    def test_bad_xml_and_selector(self):
        self.write(self.source, 'Public/HC/Bad.lsx', '<broken>')
        self.write(self.source, 'Public/HC/Progressions.lsx', '<save><attribute id="Selectors" value="AddSpells(00000000-0000-0000-0000-000000000000)"/></save>')
        errors = self.check()
        self.assertTrue(any('XML' in x for x in errors))
        self.assertTrue(any('selector list' in x for x in errors))
    def test_missing_action_resource_and_surface(self):
        self.stat('data "UseCosts" "HC_Missing:1"\ndata "SpellProperties" "CreateSurface(1,2,InventedMud)"\n')
        errors = self.check()
        self.assertTrue(any('UseCosts resource' in x for x in errors))
        self.assertTrue(any('InventedMud' in x for x in errors))
    def test_missing_vanilla_fails_closed(self):
        self.assertTrue(any('reference layer missing' in x for x in v.validate(self.source, self.vanilla)[0]))
    def test_package_mismatch(self):
        pak = self.write(self.source.parent, 'dummy.pak', 'fixture')
        unpacker = self.write(self.source.parent, 'fake_unpacker.py', 'import sys\nfrom pathlib import Path\np=Path(sys.argv[2])/"Public/HC/Stats/Generated/Data/Spell.txt"\np.parent.mkdir(parents=True)\np.write_text("corrupted")\n')
        self.assertTrue(any('mismatch' in x for x in v.compare_pak(self.source, pak, unpacker, self.source.parent/'work')))

if __name__ == '__main__': unittest.main()
