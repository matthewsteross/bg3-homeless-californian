"""Broken-Down Robotaxi prop and spell: assets, visual resource, root template, stat, status, spell and grants.

Generates into a temporary tree through hc_robotaxi.generate_robotaxi only (independent of generate_mod.main()).
File-level checks only; nothing here proves it works in game.
The GR2 round-trip needs LSLib Divine (tools/Packed/Tools/Divine.exe) and is skipped when it is absent.
"""
from pathlib import Path
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
import hc_robotaxi as hr
import hc_tarp

DIVINE = ROOT / 'tools' / 'Packed' / 'Tools' / 'Divine.exe'
VANILLA = ROOT / 'temp_race' / 'Public'
RES = 'Generated/Public/HomelessCalifornian/Assets/Props/HC_Robotaxi/Resources'
GUID = re.compile(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}')


def attrs(node):
    return {a.get('id'): a.get('value') for a in node.findall('attribute')}


def stat_fields(text, name):
    block = text.split(f'new entry "{name}"')[1].split('new entry "')[0]
    return dict(re.findall(r'data "([^"]+)" "([^"]*)"', block))


def generator_loca_text():
    """Rendered loca entries as one searchable string (LOCA_ENTRIES is filled by add_loca)."""
    return '\n'.join(f'contentuid="{h}" {t}' for h, t in generator.LOCA_ENTRIES.items())


class RobotaxiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.source = Path(cls._tmp.name)
        cls.public = cls.source / 'Public/HomelessCalifornian'
        cls.grants = hr.generate_robotaxi(cls.public, generator.add_loca, generator.get_guid)
        cls.data = cls.public / 'Stats/Generated/Data'

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def test_binary_assets_are_tracked_and_copied_next_to_the_pak_root(self):
        for name in hr.ASSET_FILES:
            self.assertGreater((hr.ASSET_SRC / name).stat().st_size, 1000, name)
            p = self.source / RES / name
            self.assertTrue(p.is_file(), name)
            self.assertEqual(p.read_bytes(), (hr.ASSET_SRC / name).read_bytes(), name)
        for tex in ('BM', 'NM', 'PM'):
            self.assertTrue((self.source / RES / f'HC_Robotaxi_{tex}.DDS').read_bytes().startswith(b'DDS '))
        for script in ('build_robotaxi_model.py', 'robotaxi_paint.py', 'render_robotaxi.py'):
            self.assertTrue((hr.ASSET_SRC / script).is_file(), script)

    def test_base_colour_texture_is_1024_bc3_and_matches_the_visual_resource(self):
        header = (hr.ASSET_SRC / 'HC_Robotaxi_BM.DDS').read_bytes()[:128]
        height, width = int.from_bytes(header[12:16], 'little'), int.from_bytes(header[16:20], 'little')
        self.assertEqual((width, height), (1024, 1024))
        self.assertEqual(header[84:88], b'DXT5')
        tree = ET.parse(self.public / 'Content/Assets/Props/[PAK]_HC_Robotaxi/_merged.lsf.lsx')
        sizes = {attrs(t)['Name']: (attrs(t)['Width'], attrs(t)['Height'])
                 for t in tree.findall('.//region[@id="TextureBank"]//node[@id="Resource"]')}
        self.assertEqual(sizes['HC_Robotaxi_BM'], ('1024', '1024'))

    @unittest.skipUnless(DIVINE.is_file(), 'Divine.exe not available')
    def test_gr2_round_trips_through_divine_with_three_lods_and_budget(self):
        with tempfile.TemporaryDirectory() as tmp:
            dae = Path(tmp) / 'rt.dae'
            result = subprocess.run([str(DIVINE), '-g', 'bg3', '-a', 'convert-model',
                                     '-s', str(hr.ASSET_SRC / 'HC_Robotaxi.GR2'), '-d', str(dae),
                                     '-i', 'gr2', '-o', 'dae', '-l', 'warn'], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            text = dae.read_text(encoding='utf-8')
        self.assertEqual(re.findall(r'<geometry id="([^"]+)"', text), [
            'LTS_GEN_Fire_Basket_A_Mesh-geom', 'LTS_GEN_Fire_Basket_A_Mesh_LOD1-geom', 'LTS_GEN_Fire_Basket_A_Mesh_LOD2-geom'])
        counts = [int(c) for c in re.findall(r'<triangles count="(\d+)"', text)]
        self.assertEqual(counts, [hr.TRIANGLES] * 3)
        self.assertTrue(all(c < 3800 for c in counts))
        self.assertIn('Dummy_LTS_GEN_Fire_Basket_A', text)
        positions = re.search(r'LTS_GEN_Fire_Basket_A_Mesh-positions-array" count="\d+">([^<]*)<', text).group(1).split()
        xyz = [[float(v) for v in positions[i::3]] for i in range(3)]
        for axis, values in enumerate(xyz):
            self.assertAlmostEqual(min(values), hr.BMIN[axis], delta=0.01, msg=f'min axis {axis}')
            self.assertAlmostEqual(max(values), hr.BMAX[axis], delta=0.01, msg=f'max axis {axis}')
        # a ~3.6 m long, ~1.6 m wide, ~1.5 m tall car on the ground (+Z nose); the mirror decorations and the cone add margins
        self.assertAlmostEqual(hr.BMAX[1], 1.5, delta=0.05)
        self.assertAlmostEqual(hr.BMAX[2] - hr.BMIN[2], 3.9, delta=0.2)
        self.assertEqual(hr.BMIN[1], 0.0)

    def test_visual_resource_matches_cart_pattern(self):
        tree = ET.parse(self.public / 'Content/Assets/Props/[PAK]_HC_Robotaxi/_merged.lsf.lsx')
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
        self.assertEqual(v['Template'], RES + '/HC_Robotaxi.Dummy_LTS_GEN_Fire_Basket_A.0')
        self.assertEqual(v['SourceFile'], RES + '/HC_Robotaxi.GR2')
        objects = [attrs(n) for n in visual.findall('.//node[@id="Objects"]')]
        self.assertEqual([o['ObjectID'] for o in objects], [
            'HC_Robotaxi.LTS_GEN_Fire_Basket_A_Mesh.0',
            'HC_Robotaxi.LTS_GEN_Fire_Basket_A_Mesh_LOD1.1',
            'HC_Robotaxi.LTS_GEN_Fire_Basket_A_Mesh_LOD2.2'])
        self.assertEqual({o['MaterialID'] for o in objects}, {attrs(material)['ID']})
        for key, size in (('BoundsMin', hr.BMIN), ('BoundsMax', hr.BMAX)):
            self.assertEqual([float(x) for x in v[key].split()], [float(f'{x:g}') for x in size])

    def test_root_template_and_object_stat_reference_each_other(self):
        tree = ET.parse(self.public / 'RootTemplates/HC_Robotaxi.lsf.lsx')
        nodes = tree.findall('.//node[@id="GameObjects"]')
        self.assertEqual(len(nodes), 1)
        a = attrs(nodes[0])
        template = generator.get_guid(hr.TEMPLATE_KEY)
        self.assertEqual(hr.TEMPLATE_KEY, 'HC_Robotaxi_RootTemplate')
        self.assertEqual(a['CanBeMoved'], 'False')
        self.assertEqual(a['CanBePickedUp'], 'False')
        self.assertEqual(a['Stats'], 'HC_OBJ_Robotaxi')
        self.assertEqual(a['MapKey'], template)
        self.assertEqual(a['ParentTemplateId'], hc_cart.PARENT_TEMPLATE)
        self.assertNotIn('PhysicsTemplate', a)
        visual = ET.parse(self.public / 'Content/Assets/Props/[PAK]_HC_Robotaxi/_merged.lsf.lsx')
        visual_id = attrs(visual.find('.//region[@id="VisualBank"]//node[@id="Resource"]'))['ID']
        self.assertEqual(a['VisualTemplate'], visual_id)
        bounds = nodes[0].findall('.//node[@id="Bound"]')
        self.assertEqual(len(bounds), 3)
        for b in bounds:
            ba = attrs(b)
            hi = [float(x) for x in ba['Max'].split()]
            lo = [float(x) for x in ba['Min'].split()]
            self.assertTrue(all(l >= m - 1e-6 for l, m in zip(lo, hr.BMIN)))
            self.assertTrue(all(h <= m + 1e-6 for h, m in zip(hi, hr.BMAX)))
            self.assertAlmostEqual(float(ba['Height']), hi[1], places=6)      # each bound's Height is its own max Y
        stat = (self.data / 'HC_Object_Robotaxi.txt').read_text(encoding='utf-8')
        self.assertIn('new entry "HC_OBJ_Robotaxi"', stat)
        self.assertIn('type "Object"', stat)
        self.assertIn('using "_BaseItem"', stat)
        self.assertIn(f'data "RootTemplate" "{template}"', stat)
        self.assertIn('data "Vitality" "-1"', stat)

    def test_spell_spawns_one_robotaxi_with_action_cost_and_no_junk(self):
        text = (self.data / 'HC_Spells_Robotaxi.txt').read_text(encoding='utf-8')
        self.assertEqual(text.count('new entry "'), 1)
        f = stat_fields(text, hr.SPELL)
        template = generator.get_guid(hr.TEMPLATE_KEY)
        self.assertIn('using "Projectile_GEB_Perform_TossCoin"', text)
        self.assertEqual(f['SpellProperties'].count('GROUND:Spawn('), 1)
        self.assertEqual(f['SpellProperties'], f'GROUND:Spawn({template});ApplyStatus(SELF,{hr.STATUS},100,3)')
        self.assertEqual(f['TargetRadius'], '9')
        self.assertEqual(f['UseCosts'], 'ActionPoint:1')
        self.assertNotIn('HC_Junk', f['UseCosts'])
        self.assertEqual(f['Cooldown'], 'OncePerRest')
        self.assertEqual(hr.SPELL, 'HC_Target_RobotaxiBreakdown')
        xml = generator_loca_text()
        for key in (hr.SPELL + '_Name', hr.SPELL + '_Description', hr.STATUS + '_Name', hr.STATUS + '_Description',
                    hr.OBJECT_STAT + '_Name', hr.OBJECT_STAT + '_Description'):
            self.assertIn(generator.get_handle(key), xml, key)
        self.assertEqual(f['DisplayName'], generator.get_handle(hr.SPELL + '_Name') + ';1')
        self.assertEqual(f['Description'], generator.get_handle(hr.SPELL + '_Description') + ';1')
        self.assertEqual(generator.LOCA_ENTRIES[generator.get_handle(hr.SPELL + '_Name')], 'Autonomous Robotaxi Has Seen a Traffic Cone')
        self.assertIn(f['Icon'], (hr.SPELL_ICON_FALLBACK,) + tuple(self._custom_icon_names()))

    def test_spell_description_is_mechanics_first_with_three_to_five_sentences(self):
        text = generator.LOCA_ENTRIES[generator.get_handle(hr.SPELL + '_Description')]
        sentences = [s for s in re.split(r'(?<=[.!?])\s+', text.strip()) if s]
        self.assertTrue(3 <= len(sentences) <= 5, sentences)
        self.assertIn('9 m', text)
        self.assertIn('3 m of extra movement', text)
        self.assertIn('Advantage on Dexterity saving throws', text)
        self.assertIn('3 turns', text)
        self.assertIn('no Junk', text)
        self.assertLess(text.index('no Junk'), text.index('traffic cone'))     # mechanics before the joke
        self.assertTrue(sentences[-1].lower().startswith('the app says'))

    def _custom_icon_names(self):
        from hc_icon_keys import SPELL_ICON_KEYS
        return [SPELL_ICON_KEYS[hr.SPELL]] if hr.SPELL in SPELL_ICON_KEYS else []

    def test_status_gives_movement_and_dexterity_save_advantage(self):
        text = (self.data / 'HC_Status_Robotaxi.txt').read_text(encoding='utf-8')
        f = stat_fields(text, hr.STATUS)
        self.assertIn('type "StatusData"', text)
        self.assertEqual(f['StatusType'], 'BOOST')
        self.assertEqual(f['Boosts'], 'ActionResource(Movement,3,0);Advantage(SavingThrow,Dexterity)')
        self.assertEqual(f['StackId'], hr.STATUS)
        self.assertEqual(hr.STATUS, 'HC_ROBOTAXI_RIDERS_NOTIFIED')
        self.assertTrue(hr.STATUS.startswith('HC_'))
        self.assertEqual(f['DisplayName'], generator.get_handle(hr.STATUS + '_Name') + ';1')
        self.assertEqual(generator.LOCA_ENTRIES[generator.get_handle(hr.STATUS + '_Name')], 'Your Driver Is Arriving In 0 Minutes')
        self.assertEqual(f['Icon'], hr.STATUS_ICON_FALLBACK)

    def test_vanilla_evidence_for_donor_icons_and_functors(self):
        stats = list((VANILLA / 'Shared/Stats/Generated/Data').glob('*.txt'))
        if not stats:
            self.skipTest('temp_race vanilla extract not available')
        corpus = '\n'.join(p.read_text(encoding='utf-8', errors='ignore') for p in stats)
        self.assertRegex(corpus, r'new entry "Projectile_GEB_Perform_TossCoin"\ntype "SpellData"')
        self.assertIn('GROUND:Spawn(', corpus)
        self.assertIn('ApplyStatus(SELF,', corpus)
        # both boost forms exist verbatim in vanilla
        self.assertIn('data "Boosts" "ActionResource(Movement,3,0)"', corpus)
        self.assertIn('Advantage(SavingThrow,Dexterity)', corpus)
        self.assertIn('data "Cooldown" "OncePerRest"', corpus)         # there is no OncePerLongRest token in vanilla
        self.assertNotIn('"OncePerLongRest"', corpus)
        self.assertIn(f'data "Icon" "{hr.SPELL_ICON_FALLBACK}"', corpus)
        self.assertIn(f'data "Icon" "{hr.STATUS_ICON_FALLBACK}"', corpus)
        self.assertEqual(hr.SPELL_ICON_FALLBACK, hc_barricade.SPELL_ICON_FALLBACK)
        self.assertEqual(hr.STATUS_ICON_FALLBACK, hc_barricade.STATUS_ICON_FALLBACK)
        for name in (hr.SPELL, hr.STATUS, hr.OBJECT_STAT):
            self.assertNotIn(f'new entry "{name}"', corpus)

    def test_grants_a_siliconite_level_five_racial_spell_only(self):
        self.assertEqual(self.grants, {'base': {}, 'subclasses': {}, 'existing_list_spells': {'Siliconite_L5': 'HC_Target_RobotaxiBreakdown'}})

    def test_guids_are_unique_and_do_not_collide_with_other_props(self):
        own = {k: generator.get_guid(f'HC_Robotaxi_{k}') for k in ('bm', 'nm', 'pm', 'mat', 'visual')}
        own['template'] = generator.get_guid(hr.TEMPLATE_KEY)
        others = set()
        for prefix in ('HC_ShoppingCart', 'HC_BlueTarp', 'HC_Barricade', 'HC_PopUpTent'):
            others |= {generator.get_guid(f'{prefix}_{k}') for k in ('bm', 'nm', 'pm', 'mat', 'visual', 'RootTemplate')}
        self.assertEqual(len(set(own.values())), 6)
        self.assertFalse(set(own.values()) & others)
        written = set()
        for path in (self.public / 'Content/Assets/Props/[PAK]_HC_Robotaxi/_merged.lsf.lsx',
                     self.public / 'RootTemplates/HC_Robotaxi.lsf.lsx'):
            written |= set(GUID.findall(path.read_text(encoding='utf-8')))
        self.assertEqual(written - set(own.values()), {hr.PARENT_TEMPLATE})
        self.assertEqual(hr.PARENT_TEMPLATE, hc_cart.PARENT_TEMPLATE)
        self.assertEqual(hr.PARENT_TEMPLATE, hc_tarp.PARENT_TEMPLATE)
        self.assertEqual(hr.PARENT_TEMPLATE, hc_barricade.PARENT_TEMPLATE)

    def test_no_foreign_mod_references(self):
        files = [p for p in self.source.rglob('*') if p.is_file() and p.suffix.lower() not in ('.dds', '.gr2')]
        files += [ROOT / 'hc_robotaxi.py', Path(__file__)] + [p for p in hr.ASSET_SRC.glob('*.py')]
        self.assertGreater(len(files), 6)
        needle = 'patr' + 'iot'
        for p in files:
            self.assertNotIn(needle, p.read_text(encoding='utf-8', errors='ignore').lower(), str(p))


if __name__ == '__main__':
    unittest.main()
