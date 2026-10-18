"""ReceiptScroll assets, resource links, bounds, GR2 round trip and existing-spell patch checks.
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
import generate_mod as generator
import hc_barricade
import hc_cart
import hc_receipt as hp
from hc_prop_lifetime import prop_lifetime, STATUS as LIFETIME_STATUS
import hc_tarp
import hc_tent

DIVINE = ROOT / 'tools' / 'Packed' / 'Tools' / 'Divine.exe'
VANILLA = ROOT / 'temp_race' / 'Public'
RES = 'Generated/Public/HomelessCalifornian/Assets/Props/HC_ReceiptScroll/Resources'
GUID = re.compile(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}')


def attrs(node):
    return {a.get('id'): a.get('value') for a in node.findall('attribute')}


def stat_fields(text, name):
    block = text.split(f'new entry "{name}"')[1].split('new entry "')[0]
    return dict(re.findall(r'data "([^"]+)" "([^"]*)"', block))


def generator_loca_text():
    """Rendered loca entries as one searchable string (LOCA_ENTRIES is filled by add_loca)."""
    return '\n'.join(f'contentuid="{h}" {t}' for h, t in generator.LOCA_ENTRIES.items())


class ReceiptScrollTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.source = Path(cls._tmp.name)
        cls.public = cls.source / 'Public/HomelessCalifornian'
        data = cls.public / 'Stats/Generated/Data'
        data.mkdir(parents=True)
        cls.original = 'ApplyStatus(HC_TERRITORY_CLAIMED,100,2);GROUND:CreateSurface(2.5,2,Mud)'
        (data / 'Existing.txt').write_text('new entry \"HC_Shout_CVSReceiptScroll\"\ntype \"SpellData\"\ndata \"SpellProperties\" \"' + cls.original + '\"\n\nnew entry \"HC_TestNeighbor\"\ntype \"SpellData\"\n')
        cls.grants = hp.generate_receipt(cls.public, generator.add_loca, generator.get_guid)
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
            self.assertTrue((self.source / RES / f'HC_ReceiptScroll_{tex}.DDS').read_bytes().startswith(b'DDS '))
        for script in ('build_receipt_model.py', 'render_receipt.py'):
            self.assertTrue((hp.ASSET_SRC / script).is_file(), script)

    def test_base_colour_texture_is_1024_bc3_and_matches_the_visual_resource(self):
        header = (hp.ASSET_SRC / 'HC_ReceiptScroll_BM.DDS').read_bytes()[:128]
        height, width = int.from_bytes(header[12:16], 'little'), int.from_bytes(header[16:20], 'little')
        self.assertEqual((width, height), (1024, 1024))
        self.assertIn(header[84:88], (b'DXT1', b'DXT5'))
        tree = ET.parse(self.public / 'Content/Assets/Props/[PAK]_HC_ReceiptScroll/_merged.lsf.lsx')
        sizes = {attrs(t)['Name']: (attrs(t)['Width'], attrs(t)['Height'])
                 for t in tree.findall('.//region[@id="TextureBank"]//node[@id="Resource"]')}
        self.assertEqual(sizes['HC_ReceiptScroll_BM'], ('1024', '1024'))

    @unittest.skipUnless(DIVINE.is_file(), 'Divine.exe not available')
    def test_gr2_round_trips_through_divine_with_three_lods_and_budget(self):
        with tempfile.TemporaryDirectory() as tmp:
            dae = Path(tmp) / 'rt.dae'
            result = subprocess.run([str(DIVINE), '-g', 'bg3', '-a', 'convert-model',
                                     '-s', str(hp.ASSET_SRC / 'HC_ReceiptScroll.GR2'), '-d', str(dae),
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
        tree = ET.parse(self.public / 'Content/Assets/Props/[PAK]_HC_ReceiptScroll/_merged.lsf.lsx')
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
        self.assertEqual(v['Template'], RES + '/HC_ReceiptScroll.Dummy_LTS_GEN_Fire_Basket_A.0')
        self.assertEqual(v['SourceFile'], RES + '/HC_ReceiptScroll.GR2')
        objects = [attrs(n) for n in visual.findall('.//node[@id="Objects"]')]
        self.assertEqual([o['ObjectID'] for o in objects], [
            'HC_ReceiptScroll.LTS_GEN_Fire_Basket_A_Mesh.0',
            'HC_ReceiptScroll.LTS_GEN_Fire_Basket_A_Mesh_LOD1.1',
            'HC_ReceiptScroll.LTS_GEN_Fire_Basket_A_Mesh_LOD2.2'])
        self.assertEqual({o['MaterialID'] for o in objects}, {attrs(material)['ID']})
        for key, size in (('BoundsMin', hp.BMIN), ('BoundsMax', hp.BMAX)):
            self.assertEqual([float(x) for x in v[key].split()], [float(f'{x:g}') for x in size])

    def test_root_template_and_object_stat_reference_each_other(self):
        tree = ET.parse(self.public / 'RootTemplates/HC_ReceiptScroll.lsf.lsx')
        nodes = tree.findall('.//node[@id="GameObjects"]')
        self.assertEqual(len(nodes), 1)
        a = attrs(nodes[0])
        template = generator.get_guid(hp.TEMPLATE_KEY)
        self.assertEqual(a['CanBeMoved'], 'False')
        self.assertEqual(a['CanBePickedUp'], 'False')
        self.assertEqual(a['Stats'], 'HC_ReceiptScroll_Object')
        self.assertEqual(a['MapKey'], template)
        self.assertEqual(a['ParentTemplateId'], hc_cart.PARENT_TEMPLATE)
        self.assertNotIn('PhysicsTemplate', a)
        visual = ET.parse(self.public / 'Content/Assets/Props/[PAK]_HC_ReceiptScroll/_merged.lsf.lsx')
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
        self.assertEqual([float(x) for x in inner['Max'].split()], [float(f'{x:.9g}') for x in hp.INNER_MAX])
        self.assertEqual([float(x) for x in inner['Min'].split()], [float(f'{x:.9g}') for x in hp.INNER_MIN])
        stat = (self.data / 'HC_ReceiptScroll_Object.txt').read_text(encoding='utf-8')
        self.assertIn('new entry "HC_ReceiptScroll_Object"', stat)
        self.assertIn('type "Object"', stat)
        self.assertIn('using "_BaseItem"', stat)
        self.assertIn(f'data "RootTemplate" "{template}"', stat)
        self.assertIn('data "Vitality" "-1"', stat)

    def test_patch_preserves_properties_and_is_idempotent(self):
        path = self.data / 'Existing.txt'
        before = path.read_text()
        hp.generate_receipt(self.public, generator.add_loca, generator.get_guid)
        self.assertEqual(path.read_text(), before)
        self.assertTrue(before.endswith('new entry "HC_TestNeighbor"\ntype "SpellData"\n'))
        props = stat_fields(before, 'HC_Shout_CVSReceiptScroll')['SpellProperties']
        self.assertEqual(props, self.original + ';' + prop_lifetime(generator.get_guid(hp.TEMPLATE_KEY))[1])
        self.assertEqual(self.grants, {'base': {}, 'subclasses': {}, 'existing_list_spells': {}})

    def test_vanilla_donor_spawn_and_unique_names(self):
        shared = VANILLA / 'Shared/Stats/Generated/Data'
        self.assertIn('new entry "_BaseItem"\ntype "Object"', (shared / 'Object.txt').read_text(encoding='utf-8'))
        self.assertIn('GROUND:Spawn(', (shared / 'Spell_Projectile.txt').read_text(encoding='utf-8'))
        for path in shared.glob('*.txt'):
            self.assertNotIn('new entry "HC_ReceiptScroll_Object"', path.read_text(encoding='utf-8'))
        for path in ROOT.glob('hc_*.py'):
            if path.name != 'hc_receipt.py':
                self.assertNotIn('HC_ReceiptScroll_Object', path.read_text(encoding='utf-8'))

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
            hp.patch_receipt_spell(tmp, guid)
            expected = 'Keep();' + prop_lifetime(guid)[1]
            self.assertEqual(stat_fields(path.read_text(), hp.SPELL)['SpellProperties'], expected)
            before = path.read_bytes()
            hp.patch_receipt_spell(tmp, guid)
            self.assertEqual(path.read_bytes(), before)

    def test_missing_spell_has_clear_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, 'HC_Shout_CVSReceiptScroll.*found 0'):
                hp.patch_receipt_spell(tmp, generator.get_guid(hp.TEMPLATE_KEY))

    def test_guids_are_unique_and_do_not_collide_with_other_props(self):
        own = {k: generator.get_guid(f'HC_ReceiptScroll_{k}') for k in ('bm', 'nm', 'pm', 'mat', 'visual')}
        own['template'] = generator.get_guid(hp.TEMPLATE_KEY)
        others = set()
        for prefix in ('HC_ShoppingCart', 'HC_BlueTarp', 'HC_Barricade', 'HC_PopUpTent', 'HC_PlexiAisle', 'HC_AnimalStyleTray', 'HC_CouncilPodium'):
            others |= {generator.get_guid(f'{prefix}_{k}') for k in ('bm', 'nm', 'pm', 'mat', 'visual', 'RootTemplate')}
        self.assertEqual(len(set(own.values())), 6)
        self.assertFalse(set(own.values()) & others)
        written = set()
        for path in (self.public / 'Content/Assets/Props/[PAK]_HC_ReceiptScroll/_merged.lsf.lsx',
                     self.public / 'RootTemplates/HC_ReceiptScroll.lsf.lsx'):
            written |= set(GUID.findall(path.read_text(encoding='utf-8')))
        self.assertEqual(written - set(own.values()), {hp.PARENT_TEMPLATE})
        for module in (hc_cart, hc_tarp, hc_barricade, hc_tent):
            self.assertEqual(hp.PARENT_TEMPLATE, module.PARENT_TEMPLATE)

    def test_no_foreign_mod_references(self):
        files = [p for p in self.source.rglob('*') if p.is_file() and p.suffix.lower() not in ('.dds', '.gr2')]
        files += [ROOT / 'hc_receipt.py', Path(__file__)] + [p for p in hp.ASSET_SRC.glob('*.py')]
        self.assertGreater(len(files), 6)
        needle = 'patr' + 'iot'
        for p in files:
            self.assertNotIn(needle, p.read_text(encoding='utf-8', errors='ignore').lower(), str(p))



    def test_actual_generated_spell_patch_is_non_destructive(self):
        source = ROOT/'src/HomelessCalifornian/Public/HomelessCalifornian/Stats/Generated/Data'
        candidates = [p for p in source.glob('*.txt') if f'new entry "{hp.SPELL}"' in p.read_text(encoding='utf-8')]
        self.assertEqual(len(candidates),1)
        before = unpatched(candidates[0].read_bytes())
        old = stat_fields(before.decode('utf-8'),hp.SPELL)['SpellProperties']
        guid = generator.get_guid(hp.TEMPLATE_KEY)
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'Source.txt'
            path.write_bytes(before)
            hp.patch_receipt_spell(tmp,guid)
            after=path.read_bytes()
            new=stat_fields(after.decode('utf-8'),hp.SPELL)['SpellProperties']
            self.assertEqual(new,old+';'+prop_lifetime(guid)[1])
            self.assertEqual(after.replace(new.encode(),old.encode(),1),before)
            hp.patch_receipt_spell(tmp,guid)
            self.assertEqual(path.read_bytes(),after)

    def test_duplicate_spell_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            for name in ('A.txt','B.txt'):
                (Path(tmp)/name).write_text(f'new entry "{hp.SPELL}"\ndata "SpellProperties" "Keep()"\n')
            with self.assertRaisesRegex(ValueError,'found 2'):
                hp.patch_receipt_spell(tmp,generator.get_guid(hp.TEMPLATE_KEY))

    def test_patch_preserves_crlf_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'Windows.txt'
            before=f'new entry "{hp.SPELL}"\r\ndata "SpellProperties" "Keep()"\r\n# neighbor\r\n'.encode()
            path.write_bytes(before)
            guid=generator.get_guid(hp.TEMPLATE_KEY)
            hp.patch_receipt_spell(tmp,guid)
            spawn=prop_lifetime(guid)[1].encode()
            self.assertEqual(path.read_bytes(),before.replace(b'Keep()',b'Keep();'+spawn))

if __name__ == '__main__':
    unittest.main()
