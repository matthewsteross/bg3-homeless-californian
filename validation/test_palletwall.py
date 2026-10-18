"""PalletWall assets, resource links, bounds, GR2 round trip and existing-spell patch checks.
File-level validation only; does not establish in-game behavior."""
from pathlib import Path
from validation.prop_patch_helper import unpatched
import re
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import uuid
class generator:
    LOCA_ENTRIES = {}
    @staticmethod
    def get_guid(key):
        return str(uuid.uuid5(uuid.UUID('3fa85f64-5717-4562-b3fc-2c963f66afa6'), key))
    @staticmethod
    def add_loca(key, text):
        h = 'h' + uuid.uuid5(uuid.NAMESPACE_URL, key).hex
        generator.LOCA_ENTRIES[h] = text
        return h
import hc_barricade
import hc_cart
import hc_palletwall as hp
from hc_prop_lifetime import prop_lifetime, STATUS as LIFETIME_STATUS
import hc_tarp
import hc_tent

DIVINE = ROOT / 'tools' / 'Packed' / 'Tools' / 'Divine.exe'
VANILLA = ROOT / 'temp_race' / 'Public'
RES = 'Generated/Public/HomelessCalifornian/Assets/Props/HC_PalletWall/Resources'
GUID = re.compile(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}')


def attrs(node):
    return {a.get('id'): a.get('value') for a in node.findall('attribute')}


def stat_fields(text, name):
    block = text.split(f'new entry "{name}"')[1].split('new entry "')[0]
    return dict(re.findall(r'data "([^"]+)" "([^"]*)"', block))


def generator_loca_text():
    """Rendered loca entries as one searchable string (LOCA_ENTRIES is filled by add_loca)."""
    return '\n'.join(f'contentuid="{h}" {t}' for h, t in generator.LOCA_ENTRIES.items())


class PalletWallTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.source = Path(cls._tmp.name)
        cls.public = cls.source / 'Public/HomelessCalifornian'
        data = cls.public / 'Stats/Generated/Data'
        data.mkdir(parents=True)
        cls.original = 'ApplyStatus(HC_TERRITORY_CLAIMED,100,2);GROUND:CreateSurface(2.5,2,Mud)'
        (data / 'Existing.txt').write_text('new entry \"HC_Shout_PalletAndTinArmor\"\ntype \"SpellData\"\ndata \"SpellProperties\" \"' + cls.original + '\"\n\nnew entry \"HC_TestNeighbor\"\ntype \"SpellData\"\n')
        cls.grants = hp.generate_palletwall(cls.public, generator.add_loca, generator.get_guid)
        cls.data = cls.public / 'Stats/Generated/Data'

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def test_binary_assets_are_tracked_and_copied_next_to_the_pak_root(self):
        for name in hp.ASSET_FILES:
            self.assertGreater((hp.ASSET_SRC / name).stat().st_size, 1000, name)
            p = self.source / RES / name
            self.assertTrue(p.is_file(), name)
            self.assertEqual(p.read_bytes(), (hp.ASSET_SRC / name).read_bytes(), name)
        for tex in ('BM', 'NM', 'PM'):
            self.assertTrue((self.source / RES / f'HC_PalletWall_{tex}.DDS').read_bytes().startswith(b'DDS '))
        for script in ('build_palletwall_model.py', 'render_palletwall.py'):
            self.assertTrue((hp.ASSET_SRC / script).is_file(), script)

    def test_base_colour_texture_is_1024_bc3_and_matches_the_visual_resource(self):
        header = (hp.ASSET_SRC / 'HC_PalletWall_BM.DDS').read_bytes()[:128]
        height, width = int.from_bytes(header[12:16], 'little'), int.from_bytes(header[16:20], 'little')
        self.assertEqual((width, height), (1024, 1024))
        self.assertEqual(header[84:88], b'DXT5')
        tree = ET.parse(self.public / 'Content/Assets/Props/[PAK]_HC_PalletWall/_merged.lsf.lsx')
        sizes = {attrs(t)['Name']: (attrs(t)['Width'], attrs(t)['Height'])
                 for t in tree.findall('.//region[@id="TextureBank"]//node[@id="Resource"]')}
        self.assertEqual(sizes['HC_PalletWall_BM'], ('1024', '1024'))

    @unittest.skipUnless(DIVINE.is_file(), 'Divine.exe not available')
    def test_gr2_round_trips_through_divine_with_three_lods_and_budget(self):
        with tempfile.TemporaryDirectory() as tmp:
            dae = Path(tmp) / 'rt.dae'
            result = subprocess.run([str(DIVINE), '-g', 'bg3', '-a', 'convert-model',
                                     '-s', str(hp.ASSET_SRC / 'HC_PalletWall.GR2'), '-d', str(dae),
                                     '-i', 'gr2', '-o', 'dae', '-l', 'warn'], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            text = dae.read_text(encoding='utf-8')
        self.assertEqual(re.findall(r'<geometry id="([^"]+)"', text), [
            'LTS_GEN_Fire_Basket_A_Mesh-geom', 'LTS_GEN_Fire_Basket_A_Mesh_LOD1-geom', 'LTS_GEN_Fire_Basket_A_Mesh_LOD2-geom'])
        counts = [int(c) for c in re.findall(r'<triangles count="(\d+)"', text)]
        self.assertEqual(counts, [hp.TRIANGLES] * 3)
        self.assertTrue(all(c < 8000 for c in counts))
        self.assertIn('Dummy_LTS_GEN_Fire_Basket_A', text)
        positions = re.search(r'LTS_GEN_Fire_Basket_A_Mesh-positions-array" count="\d+">([^<]*)<', text).group(1).split()
        xyz = [[float(v) for v in positions[i::3]] for i in range(3)]
        for axis, values in enumerate(xyz):
            self.assertAlmostEqual(min(values), hp.BMIN[axis], delta=0.01, msg=f'min axis {axis}')
            self.assertAlmostEqual(max(values), hp.BMAX[axis], delta=0.01, msg=f'max axis {axis}')
        self.assertEqual(hp.BMIN[1], 0.0)

    def test_visual_resource_matches_cart_pattern(self):
        tree = ET.parse(self.public / 'Content/Assets/Props/[PAK]_HC_PalletWall/_merged.lsf.lsx')
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
        self.assertEqual(v['Template'], RES + '/HC_PalletWall.Dummy_LTS_GEN_Fire_Basket_A.0')
        self.assertEqual(v['SourceFile'], RES + '/HC_PalletWall.GR2')
        objects = [attrs(n) for n in visual.findall('.//node[@id="Objects"]')]
        self.assertEqual([o['ObjectID'] for o in objects], [
            'HC_PalletWall.LTS_GEN_Fire_Basket_A_Mesh.0',
            'HC_PalletWall.LTS_GEN_Fire_Basket_A_Mesh_LOD1.1',
            'HC_PalletWall.LTS_GEN_Fire_Basket_A_Mesh_LOD2.2'])
        self.assertEqual({o['MaterialID'] for o in objects}, {attrs(material)['ID']})
        for key, size in (('BoundsMin', hp.BMIN), ('BoundsMax', hp.BMAX)):
            self.assertEqual([float(x) for x in v[key].split()], [float(f'{x:g}') for x in size])

    def test_root_template_and_object_stat_reference_each_other(self):
        tree = ET.parse(self.public / 'RootTemplates/HC_PalletWall.lsf.lsx')
        nodes = tree.findall('.//node[@id="GameObjects"]')
        self.assertEqual(len(nodes), 1)
        a = attrs(nodes[0])
        template = generator.get_guid(hp.TEMPLATE_KEY)
        self.assertEqual(a['CanBeMoved'], 'False')
        self.assertEqual(a['CanBePickedUp'], 'False')
        self.assertEqual(a['Stats'], 'HC_PalletWall_Object')
        self.assertEqual(a['MapKey'], template)
        self.assertEqual(a['ParentTemplateId'], hc_cart.PARENT_TEMPLATE)
        self.assertNotIn('PhysicsTemplate', a)
        visual = ET.parse(self.public / 'Content/Assets/Props/[PAK]_HC_PalletWall/_merged.lsf.lsx')
        visual_id = attrs(visual.find('.//region[@id="VisualBank"]//node[@id="Resource"]'))['ID']
        self.assertEqual(a['VisualTemplate'], visual_id)
        bounds = nodes[0].findall('.//node[@id="Bound"]')
        self.assertEqual(len(bounds), 3)
        for b in bounds:
            ba = attrs(b)
            hi = [float(x) for x in ba['Max'].split()]
            lo = [float(x) for x in ba['Min'].split()]
            self.assertTrue(all(l >= m - 1e-6 for l, m in zip(lo, hp.BMIN)))
            self.assertTrue(all(h <= m + 1e-6 for h, m in zip(hi, hp.BMAX)))
            self.assertAlmostEqual(float(ba['Height']), hi[1], places=6)           # Height equals the bound's own max Y
        inner = [attrs(b) for b in bounds if attrs(b)['Type'] == '0'][0]
        for actual, expected in zip(map(float, inner['Max'].split()), hp.INNER_MAX):
            self.assertAlmostEqual(actual, expected, places=7)
        for actual, expected in zip(map(float, inner['Min'].split()), hp.INNER_MIN):
            self.assertAlmostEqual(actual, expected, places=7)
        stat = (self.data / 'HC_Object_PalletWall.txt').read_text(encoding='utf-8')
        self.assertIn('new entry "HC_PalletWall_Object"', stat)
        self.assertIn('type "Object"', stat)
        self.assertIn('using "_BaseItem"', stat)
        self.assertIn(f'data "RootTemplate" "{template}"', stat)
        self.assertIn('data "Vitality" "-1"', stat)

    def test_patch_preserves_properties_and_is_idempotent(self):
        path = self.data / 'Existing.txt'
        before = path.read_text()
        hp.generate_palletwall(self.public, generator.add_loca, generator.get_guid)
        self.assertEqual(path.read_text(), before)
        self.assertTrue(before.endswith('new entry "HC_TestNeighbor"\ntype "SpellData"\n'))
        props = stat_fields(before, 'HC_Shout_PalletAndTinArmor')['SpellProperties']
        self.assertEqual(props, self.original + ';' + prop_lifetime(generator.get_guid(hp.TEMPLATE_KEY))[1])
        self.assertEqual(self.grants, {'base': {}, 'subclasses': {}, 'existing_list_spells': {}})

    def test_vanilla_donor_spawn_and_unique_names(self):
        shared = VANILLA / 'Shared/Stats/Generated/Data'
        self.assertIn('new entry "_BaseItem"\ntype "Object"', (shared / 'Object.txt').read_text(encoding='utf-8'))
        self.assertIn('GROUND:Spawn(', (shared / 'Spell_Projectile.txt').read_text(encoding='utf-8'))
        for path in shared.glob('*.txt'):
            self.assertNotIn('new entry "HC_PalletWall_Object"', path.read_text(encoding='utf-8'))
        for path in ROOT.glob('hc_*.py'):
            if path.name != 'hc_palletwall.py':
                self.assertNotIn('HC_PalletWall_Object', path.read_text(encoding='utf-8'))

    def test_lifetime_status_and_legacy_upgrade(self):
        text = (self.data / 'HC_Status_PropLifetime.txt').read_text()
        self.assertEqual(text, prop_lifetime(generator.get_guid(hp.TEMPLATE_KEY))[0])
        fields = stat_fields(text, LIFETIME_STATUS)
        self.assertEqual(fields['OnApplyFunctors'], f'SetStatusDuration({LIFETIME_STATUS},10,ForceSet)')
        self.assertEqual(fields['OnRemoveFunctors'], 'Kill()')
        self.assertEqual(fields['RemoveEvents'], 'OnRemove')
        self.assertEqual(fields['StatusType'], 'BOOST')
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'Old.txt'
            guid = generator.get_guid(hp.TEMPLATE_KEY)
            path.write_text(f'new entry "{hp.SPELL}"\ndata "SpellProperties" "Keep();GROUND:Spawn({guid})"\n')
            hp.patch_palletwall_spell(tmp, guid)
            expected = 'Keep();' + prop_lifetime(guid)[1]
            self.assertEqual(stat_fields(path.read_text(), hp.SPELL)['SpellProperties'], expected)
            before = path.read_bytes()
            hp.patch_palletwall_spell(tmp, guid)
            self.assertEqual(path.read_bytes(), before)

    def test_missing_spell_has_clear_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, 'HC_Shout_PalletAndTinArmor.*found 0'):
                hp.patch_palletwall_spell(tmp, generator.get_guid(hp.TEMPLATE_KEY))

    def test_guids_are_unique_and_do_not_collide_with_other_props(self):
        own = {k: generator.get_guid(f'HC_PalletWall_{k}') for k in ('bm', 'nm', 'pm', 'mat', 'visual')}
        own['template'] = generator.get_guid(hp.TEMPLATE_KEY)
        others = set()
        for prefix in ('HC_ShoppingCart', 'HC_BlueTarp', 'HC_Barricade', 'HC_PopUpTent'):
            others |= {generator.get_guid(f'{prefix}_{k}') for k in ('bm', 'nm', 'pm', 'mat', 'visual', 'RootTemplate')}
        self.assertEqual(len(set(own.values())), 6)
        self.assertFalse(set(own.values()) & others)
        written = set()
        for path in (self.public / 'Content/Assets/Props/[PAK]_HC_PalletWall/_merged.lsf.lsx',
                     self.public / 'RootTemplates/HC_PalletWall.lsf.lsx'):
            written |= set(GUID.findall(path.read_text(encoding='utf-8')))
        self.assertEqual(written - set(own.values()), {hp.PARENT_TEMPLATE})
        for module in (hc_cart, hc_tarp, hc_barricade, hc_tent):
            self.assertEqual(hp.PARENT_TEMPLATE, module.PARENT_TEMPLATE)

    def test_real_generated_spell_and_crlf_preserve_all_other_bytes(self):
        paths = list((ROOT / 'src/HomelessCalifornian/Public/HomelessCalifornian/Stats/Generated/Data').glob('*.txt'))
        original = unpatched(next(p.read_bytes() for p in paths if f'new entry "{hp.SPELL}"'.encode() in p.read_bytes()))
        for content in (original, original.replace(b'\r\n', b'\n').replace(b'\n', b'\r\n')):
            with tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / 'Existing.txt'
                path.write_bytes(content)
                hp.patch_palletwall_spell(tmp, generator.get_guid(hp.TEMPLATE_KEY))
                spawn = prop_lifetime(generator.get_guid(hp.TEMPLATE_KEY))[1].encode()
                self.assertEqual(path.read_bytes().replace(b';' + spawn, b''), content)
                before = path.read_bytes()
                hp.patch_palletwall_spell(tmp, generator.get_guid(hp.TEMPLATE_KEY))
                self.assertEqual(path.read_bytes(), before)

    def test_duplicate_spell_and_missing_properties_fail_without_modification(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'Bad.txt'
            for content in (f'new entry "{hp.SPELL}"\ndata "SpellProperties" "Keep()"\n' * 2,
                            f'new entry "{hp.SPELL}"\ntype "SpellData"\n'):
                path.write_text(content)
                before = path.read_bytes()
                with self.assertRaises(ValueError):
                    hp.patch_palletwall_spell(tmp, generator.get_guid(hp.TEMPLATE_KEY))
                self.assertEqual(path.read_bytes(), before)

    def test_target_size_and_centering(self):
        self.assertAlmostEqual(hp.BMAX[1], 1.5, places=6)
        self.assertAlmostEqual(hp.BMAX[0] - hp.BMIN[0], 1.8, places=6)
        self.assertAlmostEqual(hp.BMIN[0] + hp.BMAX[0], 0, places=6)
        self.assertAlmostEqual(hp.BMIN[2] + hp.BMAX[2], 0, places=6)

    def test_geometry_is_the_source_pallet_wall(self):
        import json
        import struct
        import numpy as np
        raw = (ROOT / 'assets/meshy/palletwall/model.glb').read_bytes()
        offset = 12
        while offset < len(raw):
            size, kind = struct.unpack_from('<II', raw, offset)
            offset += 8
            chunk = raw[offset:offset + size]
            offset += size
            if kind == 0x4e4f534a:
                doc = json.loads(chunk)
            elif kind == 0x004e4942:
                binary = chunk
        primitive = doc['meshes'][0]['primitives'][0]
        accessor = doc['accessors'][primitive['attributes']['POSITION']]
        view = doc['bufferViews'][accessor['bufferView']]
        positions = np.ndarray((accessor['count'], 3), dtype='<f4', buffer=binary,
                               offset=view.get('byteOffset', 0) + accessor.get('byteOffset', 0),
                               strides=(view.get('byteStride', 12), 4)).astype(float)
        positions *= [1.8 / np.ptp(positions[:, 0]), 1.5 / np.ptp(positions[:, 1]), 1.8 / np.ptp(positions[:, 0])]
        positions -= [(positions[:, 0].min() + positions[:, 0].max()) / 2,
                      positions[:, 1].min(),
                      (positions[:, 2].min() + positions[:, 2].max()) / 2]
        preview = json.loads((hp.ASSET_SRC / 'palletwall_preview.json').read_text())
        np.testing.assert_allclose(preview['pos'], positions, atol=1e-8)
        self.assertEqual(hp.TRIANGLES, doc['accessors'][primitive['indices']]['count'] // 3)
        self.assertEqual(hp.TRIANGLES, 7000)
        self.assertIn("'meshy/palletwall'", (hp.ASSET_SRC / 'build_palletwall_model.py').read_text())

    def test_source_textures_and_flat_normal_encoding(self):
        import numpy as np
        from PIL import Image
        source = ROOT / 'assets/meshy/palletwall'
        for name in ('model.glb', 'texture0_base_color.png', 'texture0_normal.png',
                     'texture0_metallic.png', 'texture0_roughness.png'):
            self.assertTrue((source / name).is_file(), name)
        expected = Image.open(source / 'texture0_base_color.png').convert('RGB').resize((1024, 1024), Image.Resampling.LANCZOS)
        actual = Image.open(hp.ASSET_SRC / 'HC_PalletWall_BM.png').convert('RGB')
        np.testing.assert_array_equal(actual, expected)
        normal = np.asarray(Image.open(hp.ASSET_SRC / 'HC_PalletWall_NM.png'))
        np.testing.assert_array_equal(normal, np.broadcast_to([0, 128, 255, 128], normal.shape))
        rough = np.asarray(Image.open(source / 'texture0_roughness.png').convert('L').resize((1024, 1024), Image.Resampling.BILINEAR), dtype=float) / 255
        small = np.asarray(Image.fromarray((rough * 255).astype('uint8')).resize((256, 256), Image.Resampling.BILINEAR)).astype('float32')
        physical = np.asarray(Image.open(hp.ASSET_SRC / 'HC_PalletWall_PM.png'))
        np.testing.assert_array_equal(physical[:, :, 1], (70 + small * (235 - 70) / 255).astype('uint8'))
        self.assertTrue(np.all(physical[:, :, 0] == 0))
        self.assertTrue(np.all(physical[:, :, 2:] == 255))

    def test_no_foreign_mod_references(self):
        files = [p for p in self.source.rglob('*') if p.is_file() and p.suffix.lower() not in ('.dds', '.gr2')]
        files += [ROOT / 'hc_palletwall.py', Path(__file__)] + [p for p in hp.ASSET_SRC.glob('*.py')]
        self.assertGreater(len(files), 6)
        needle = 'patr' + 'iot'
        for p in files:
            self.assertNotIn(needle, p.read_text(encoding='utf-8', errors='ignore').lower(), str(p))


if __name__ == '__main__':
    unittest.main()
