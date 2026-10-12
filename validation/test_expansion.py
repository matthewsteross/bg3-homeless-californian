"""Generation regression checks run entirely in temporary source trees."""
from pathlib import Path
import contextlib
import hashlib
import io
import sys
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import generate_mod as generator


class ExpansionGenerationTests(unittest.TestCase):
    def test_repeatable_grants_and_resource(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)
            public = source / 'Public/HomelessCalifornian'
            with patch.object(generator, 'PUBLIC_DIR', str(public)), \
                 patch.object(generator, 'MODS_DIR', str(source / 'Mods/HomelessCalifornian')), \
                 contextlib.redirect_stdout(io.StringIO()):
                generator.main()
                before = {p.relative_to(source): hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in source.rglob('*') if p.is_file()}
                generator.main()
                after = {p.relative_to(source): hashlib.sha256(p.read_bytes()).hexdigest()
                         for p in source.rglob('*') if p.is_file()}
            self.assertEqual(before, after)
            lists = ET.parse(public / 'Lists/SpellLists.lsx')
            new_lists = {}
            for node in lists.findall('.//node[@id="SpellList"]'):
                attrs = {a.get('id'): a.get('value') for a in node.findall('attribute')}
                if 'HC_' in attrs['Spells']:
                    new_lists[attrs['UUID']] = attrs['Spells'].split(';')
            self.assertEqual(len(new_lists), 6)
            progressions = ET.parse(public / 'Progressions/Progressions.lsx')
            selectors = ';'.join(a.get('value', '') for a in progressions.findall('.//attribute[@id="Selectors"]'))
            for uid in new_lists:
                self.assertIn(uid, selectors)
            resources = ET.parse(public / 'ActionResourceDefinitions/ActionResourceDefinitions.lsx')
            resource_names = [a.get('value') for a in resources.findall('.//attribute[@id="Name"]')]
            self.assertEqual(resource_names, ['HC_Junk'])
            roots = ET.parse(public / 'RootTemplates/HC_Wardrobe.lsf.lsx')
            self.assertEqual(len(roots.findall('.//node[@id="GameObjects"]')), 2)

    def test_missing_progression_fails_instead_of_orphaning_spell(self):
        with tempfile.TemporaryDirectory() as directory:
            public = Path(directory)
            (public / 'Lists').mkdir()
            (public / 'Progressions').mkdir()
            (public / 'Lists/SpellLists.lsx').write_text('<save>\n            </children>\n</save>')
            (public / 'Progressions/Progressions.lsx').write_text('<save/>')
            with patch.object(generator, 'PUBLIC_DIR', str(public)):
                with self.assertRaisesRegex(ValueError, 'lack progression nodes'):
                    generator.generate_local_expansion()


if __name__ == '__main__':
    unittest.main()
