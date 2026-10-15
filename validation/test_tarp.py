"""Blue Tarp Lean-To prop: assets, visual resource, root template, stat, spawn functor and uniqueness of GUIDs.

Runs on a freshly generated temporary tree. File-level checks only; nothing here proves it works in game.
The GR2 round-trip needs LSLib Divine (tools/Packed/Tools/Divine.exe) and is skipped when it is absent.
"""
from pathlib import Path
import contextlib
import io
import re
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import generate_mod as generator
import hc_cart
import hc_tarp

ROOT = Path(__file__).resolve().parents[1]
DIVINE = ROOT / 'tools' / 'Packed' / 'Tools' / 'Divine.exe'
RES = 'Generated/Public/HomelessCalifornian/Assets/Props/HC_BlueTarp/Resources'
GUID = re.compile(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}')


def attrs(node):
    return {a.get('id'): a.get('value') for a in node.findall('attribute')}


class TarpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.source = Path(cls._tmp.name)
        cls.public = cls.source / 'Public/HomelessCalifornian'
        with patch.object(generator, 'PUBLIC_DIR', str(cls.public)), \
                patch.object(generator, 'MODS_DIR', str(cls.source / 'Mods/HomelessCalifornian')), \
                contextlib.redirect_stdout(io.StringIO()):
            generator.main()

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def test_binary_assets_are_tracked_and_copied_next_to_the_pak_root(self):
        for name in hc_tarp.ASSET_FILES:
            self.assertGreater((hc_tarp.ASSET_SRC / name).stat().st_size, 1000, name)
            p = self.source / RES / name
            self.assertTrue(p.is_file(), name)
            self.assertEqual(p.read_bytes(), (hc_tarp.ASSET_SRC / name).read_bytes(), name)
        for tex in ('BM', 'NM', 'PM'):
            self.assertTrue((self.source / RES / f'HC_BlueTarp_{tex}.DDS').read_bytes().startswith(b'DDS '))
        for script in ('build_tarp_model.py', 'tarp_paint.py', 'render_tarp.py'):
            self.assertTrue((hc_tarp.ASSET_SRC / script).is_file(), script)

    @unittest.skipUnless(DIVINE.is_file(), 'Divine.exe not available')
    def test_gr2_round_trips_through_divine_with_three_lods_and_budget(self):
        with tempfile.TemporaryDirectory() as tmp:
            dae = Path(tmp) / 'rt.dae'
            result = subprocess.run([str(DIVINE), '-g', 'bg3', '-a', 'convert-model',
                                     '-s', str(hc_tarp.ASSET_SRC / 'HC_BlueTarp.GR2'), '-d', str(dae),
                                     '-i', 'gr2', '-o', 'dae', '-l', 'warn'], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            text = dae.read_text(encoding='utf-8')
        self.assertEqual(re.findall(r'<geometry id="([^"]+)"', text), [
            'LTS_GEN_Fire_Basket_A_Mesh-geom', 'LTS_GEN_Fire_Basket_A_Mesh_LOD1-geom', 'LTS_GEN_Fire_Basket_A_Mesh_LOD2-geom'])
        counts = [int(c) for c in re.findall(r'<triangles count="(\d+)"', text)]
        self.assertEqual(counts, [hc_tarp.TRIANGLES] * 3)
        self.assertTrue(all(c < 3000 for c in counts))
        self.assertIn('Dummy_LTS_GEN_Fire_Basket_A', text)
        positions = re.search(r'LTS_GEN_Fire_Basket_A_Mesh-positions-array" count="\d+">([^<]*)<', text).group(1).split()
        xyz = [[float(v) for v in positions[i::3]] for i in range(3)]
        for axis, values in enumerate(xyz):
            self.assertAlmostEqual(min(values), hc_tarp.BMIN[axis], delta=0.01, msg=f'min axis {axis}')
            self.assertAlmostEqual(max(values), hc_tarp.BMAX[axis], delta=0.01, msg=f'max axis {axis}')
        # roughly 1.4 m at the ridge
        self.assertAlmostEqual(hc_tarp.BMAX[1], 1.4, delta=0.05)

    def test_visual_resource_matches_cart_pattern(self):
        tree = ET.parse(self.public / 'Content/Assets/Props/[PAK]_HC_BlueTarp/_merged.lsf.lsx')
        textures = tree.findall('.//region[@id="TextureBank"]//node[@id="Resource"]')
        self.assertEqual(len(textures), 3)
        for t in textures:
            self.assertTrue(attrs(t)['SourceFile'].startswith(RES + '/'))
            self.assertTrue(attrs(t)['SourceFile'].endswith('.DDS'))
        self.assertEqual(sorted(attrs(t)['SRGB'] for t in textures), ['False', 'False', 'True'])
        material = tree.find('.//region[@id="MaterialBank"]//node[@id="Resource"]')
        self.assertEqual(attrs(material)['SourceFile'], 'Public/Shared/Assets/Materials/Base/Base.lsf')
        params = {attrs(n)['ParameterName']: attrs(n)['ID'] for n in material.findall('.//node[@id="Texture2DParameters"]')}
        self.assertEqual(set(params), {'normalmap', 'basecolor', 'physicalmap'})
        self.assertEqual(set(params.values()), {attrs(t)['ID'] for t in textures})
        visual = tree.find('.//region[@id="VisualBank"]//node[@id="Resource"]')
        v = attrs(visual)
        self.assertEqual(v['Template'], RES + '/HC_BlueTarp.Dummy_LTS_GEN_Fire_Basket_A.0')
        self.assertEqual(v['SourceFile'], RES + '/HC_BlueTarp.GR2')
        objects = [attrs(n) for n in visual.findall('.//node[@id="Objects"]')]
        self.assertEqual([o['ObjectID'] for o in objects], [
            'HC_BlueTarp.LTS_GEN_Fire_Basket_A_Mesh.0',
            'HC_BlueTarp.LTS_GEN_Fire_Basket_A_Mesh_LOD1.1',
            'HC_BlueTarp.LTS_GEN_Fire_Basket_A_Mesh_LOD2.2'])
        self.assertEqual({o['MaterialID'] for o in objects}, {attrs(material)['ID']})

    def test_root_template_is_a_static_prop_in_its_own_file(self):
        folder = self.public / 'RootTemplates'
        tree = ET.parse(folder / 'HC_BlueTarp.lsf.lsx')
        nodes = tree.findall('.//node[@id="GameObjects"]')
        self.assertEqual(len(nodes), 1)
        a = attrs(nodes[0])
        self.assertEqual(a['CanBeMoved'], 'False')
        self.assertEqual(a['CanBePickedUp'], 'False')
        self.assertEqual(a['Stats'], 'HC_OBJ_BlueTarp')
        self.assertEqual(a['MapKey'], generator.get_guid('HC_BlueTarp_RootTemplate'))
        self.assertNotIn('PhysicsTemplate', a)
        visual = ET.parse(self.public / 'Content/Assets/Props/[PAK]_HC_BlueTarp/_merged.lsf.lsx')
        visual_id = attrs(visual.find('.//region[@id="VisualBank"]//node[@id="Resource"]'))['ID']
        self.assertEqual(a['VisualTemplate'], visual_id)
        self.assertEqual(len(nodes[0].findall('.//node[@id="Bound"]')), 3)
        # Each prop owns exactly one root template file.
        self.assertTrue((folder / 'HC_ShoppingCart.lsf.lsx').is_file())

    def test_object_stat(self):
        stat = (self.public / 'Stats/Generated/Data/HC_Object_BlueTarp.txt').read_text(encoding='utf-8')
        template = generator.get_guid('HC_BlueTarp_RootTemplate')
        self.assertIn('new entry "HC_OBJ_BlueTarp"', stat)
        self.assertIn('type "Object"', stat)
        self.assertIn('using "_BaseItem"', stat)
        self.assertIn(f'data "RootTemplate" "{template}"', stat)

    def test_blue_tarp_shout_spawns_the_prop_once_and_keeps_its_old_effects(self):
        spells = (self.public / 'Stats/Generated/Data/HC_Spells_Overpass.txt').read_text(encoding='utf-8')
        block = spells.split('new entry "HC_Shout_BlueTarpLeanTo"')[1].split('new entry "')[0]
        template = generator.get_guid('HC_BlueTarp_RootTemplate')
        props = re.search(r'data "SpellProperties" "([^"]*)"', block).group(1)
        self.assertEqual(props.count('GROUND:Spawn('), 1)
        self.assertIn(f'GROUND:Spawn({template})', props)
        self.assertIn('ApplyStatus(HC_TARP_COVER,100,2)', props)
        self.assertIn('GROUND:SurfaceChange(Douse)', props)
        self.assertEqual(spells.count('GROUND:Spawn('), 1)
        # Same functor syntax as the verified cart spell.
        cart_spell = (self.public / 'Stats/Generated/Data/HC_Spells_Cart.txt').read_text(encoding='utf-8')
        self.assertIn('GROUND:Spawn(' + generator.get_guid('HC_ShoppingCart_RootTemplate') + ')', cart_spell)

    def test_guids_are_unique_and_do_not_collide_with_the_cart(self):
        tarp_ids = {k: generator.get_guid(f'HC_BlueTarp_{k}') for k in ('bm', 'nm', 'pm', 'mat', 'visual')}
        tarp_ids['template'] = generator.get_guid(hc_tarp.TEMPLATE_KEY)
        cart_ids = {k: generator.get_guid(f'HC_ShoppingCart_{k}') for k in ('bm', 'nm', 'pm', 'mat', 'visual')}
        cart_ids['template'] = generator.get_guid('HC_ShoppingCart_RootTemplate')
        self.assertEqual(len(set(tarp_ids.values())), 6)
        self.assertFalse(set(tarp_ids.values()) & set(cart_ids.values()))
        # Every id written into the new resource and template files is one of ours (or the vanilla parent).
        written = set()
        for path in (self.public / 'Content/Assets/Props/[PAK]_HC_BlueTarp/_merged.lsf.lsx',
                     self.public / 'RootTemplates/HC_BlueTarp.lsf.lsx'):
            written |= set(GUID.findall(path.read_text(encoding='utf-8')))
        self.assertEqual(written - set(tarp_ids.values()), {hc_tarp.PARENT_TEMPLATE})
        self.assertEqual(hc_tarp.PARENT_TEMPLATE, hc_cart.PARENT_TEMPLATE)
        # No other root template file in the tree reuses the tarp template id.
        for path in (self.public / 'RootTemplates').glob('*.lsx'):
            if path.name != 'HC_BlueTarp.lsf.lsx':
                self.assertNotIn(tarp_ids['template'], path.read_text(encoding='utf-8'), path.name)

    def test_new_loca_handles_exist(self):
        xml = (self.public / 'Localization/English/HomelessCalifornian.loca.xml').read_text(encoding='utf-8')
        for key in ('HC_OBJ_BlueTarp_Name', 'HC_OBJ_BlueTarp_Description'):
            self.assertIn(f'contentuid="{generator.get_handle(key)}"', xml, key)
        self.assertIn('Blue Tarp Lean-To', xml)


if __name__ == '__main__':
    unittest.main()
