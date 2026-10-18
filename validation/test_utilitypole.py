"""Sparking Utility Pole prop and spell: assets, visual resource, root template, stat, status, spell and grants.

Generates into a temporary tree through hc_utilitypole.generate_utilitypole only (independent of generate_mod.main()).
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
import hc_utilitypole as hu

DIVINE = ROOT / 'tools' / 'Packed' / 'Tools' / 'Divine.exe'
VANILLA = ROOT / 'temp_race' / 'Public'
RES = 'Generated/Public/HomelessCalifornian/Assets/Props/HC_UtilityPole/Resources'
GUID = re.compile(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}')


def attrs(node):
    return {a.get('id'): a.get('value') for a in node.findall('attribute')}


def stat_fields(text, name):
    block = text.split(f'new entry "{name}"')[1].split('new entry "')[0]
    return dict(re.findall(r'data "([^"]+)" "([^"]*)"', block))


def generator_loca_text():
    """Rendered loca entries as one searchable string (LOCA_ENTRIES is filled by add_loca)."""
    return '\n'.join(f'contentuid="{h}" {t}' for h, t in generator.LOCA_ENTRIES.items())


class UtilityPoleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.source = Path(cls._tmp.name)
        cls.public = cls.source / 'Public/HomelessCalifornian'
        cls.grants = hu.generate_utilitypole(cls.public, generator.add_loca, generator.get_guid)
        cls.data = cls.public / 'Stats/Generated/Data'

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def test_binary_assets_are_tracked_and_copied_next_to_the_pak_root(self):
        for name in hu.ASSET_FILES:
            self.assertGreater((hu.ASSET_SRC / name).stat().st_size, 1000, name)
            p = self.source / RES / name
            self.assertTrue(p.is_file(), name)
            self.assertEqual(p.read_bytes(), (hu.ASSET_SRC / name).read_bytes(), name)
        for tex in ('BM', 'NM', 'PM'):
            self.assertTrue((self.source / RES / f'HC_UtilityPole_{tex}.DDS').read_bytes().startswith(b'DDS '))
        for script in ('build_utilitypole_model.py', 'utilitypole_paint.py', 'render_utilitypole.py'):
            self.assertTrue((hu.ASSET_SRC / script).is_file(), script)

    def test_base_colour_texture_is_1024_bc3_and_matches_the_visual_resource(self):
        header = (hu.ASSET_SRC / 'HC_UtilityPole_BM.DDS').read_bytes()[:128]
        height, width = int.from_bytes(header[12:16], 'little'), int.from_bytes(header[16:20], 'little')
        self.assertEqual((width, height), (1024, 1024))
        self.assertIn(header[84:88], (b'DXT1', b'DXT5'))
        tree = ET.parse(self.public / 'Content/Assets/Props/[PAK]_HC_UtilityPole/_merged.lsf.lsx')
        sizes = {attrs(t)['Name']: (attrs(t)['Width'], attrs(t)['Height'])
                 for t in tree.findall('.//region[@id="TextureBank"]//node[@id="Resource"]')}
        self.assertEqual(sizes['HC_UtilityPole_BM'], ('1024', '1024'))

    @unittest.skipUnless(DIVINE.is_file(), 'Divine.exe not available')
    def test_gr2_round_trips_through_divine_with_three_lods_and_honest_bounds(self):
        with tempfile.TemporaryDirectory() as tmp:
            dae = Path(tmp) / 'rt.dae'
            result = subprocess.run([str(DIVINE), '-g', 'bg3', '-a', 'convert-model',
                                     '-s', str(hu.ASSET_SRC / 'HC_UtilityPole.GR2'), '-d', str(dae),
                                     '-i', 'gr2', '-o', 'dae', '-l', 'warn'], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            text = dae.read_text(encoding='utf-8')
        self.assertEqual(re.findall(r'<geometry id="([^"]+)"', text), [
            'LTS_GEN_Fire_Basket_A_Mesh-geom', 'LTS_GEN_Fire_Basket_A_Mesh_LOD1-geom', 'LTS_GEN_Fire_Basket_A_Mesh_LOD2-geom'])
        counts = [int(c) for c in re.findall(r'<triangles count="(\d+)"', text)]
        self.assertEqual(counts, [hu.TRIANGLES] * 3)
        self.assertTrue(all(c < 3500 for c in counts))
        self.assertIn('Dummy_LTS_GEN_Fire_Basket_A', text)
        positions = re.search(r'LTS_GEN_Fire_Basket_A_Mesh-positions-array" count="\d+">([^<]*)<', text).group(1).split()
        xyz = [[float(v) for v in positions[i::3]] for i in range(3)]
        for axis, values in enumerate(xyz):
            self.assertAlmostEqual(min(values), hu.BMIN[axis], delta=0.01, msg=f'min axis {axis}')
            self.assertAlmostEqual(max(values), hu.BMAX[axis], delta=0.01, msg=f'max axis {axis}')
        # tall but honest: about 5 m high, standing on the ground, and a footprint of roughly 3 x 2.4 m
        self.assertEqual(hu.BMIN[1], 0.0)
        self.assertAlmostEqual(hu.BMAX[1], 5.1, delta=0.2)
        self.assertLess(hu.BMAX[0] - hu.BMIN[0], 3.5)
        self.assertLess(hu.BMAX[2] - hu.BMIN[2], 2.8)

    def test_visual_resource_matches_cart_pattern(self):
        tree = ET.parse(self.public / 'Content/Assets/Props/[PAK]_HC_UtilityPole/_merged.lsf.lsx')
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
        self.assertEqual(v['Template'], RES + '/HC_UtilityPole.Dummy_LTS_GEN_Fire_Basket_A.0')
        self.assertEqual(v['SourceFile'], RES + '/HC_UtilityPole.GR2')
        objects = [attrs(n) for n in visual.findall('.//node[@id="Objects"]')]
        self.assertEqual([o['ObjectID'] for o in objects], [
            'HC_UtilityPole.LTS_GEN_Fire_Basket_A_Mesh.0',
            'HC_UtilityPole.LTS_GEN_Fire_Basket_A_Mesh_LOD1.1',
            'HC_UtilityPole.LTS_GEN_Fire_Basket_A_Mesh_LOD2.2'])
        self.assertEqual({o['MaterialID'] for o in objects}, {attrs(material)['ID']})
        for key, size in (('BoundsMin', hu.BMIN), ('BoundsMax', hu.BMAX)):
            self.assertEqual([float(x) for x in v[key].split()], [float(f'{x:g}') for x in size])

    def test_root_template_and_object_stat_reference_each_other(self):
        tree = ET.parse(self.public / 'RootTemplates/HC_UtilityPole.lsf.lsx')
        nodes = tree.findall('.//node[@id="GameObjects"]')
        self.assertEqual(len(nodes), 1)
        a = attrs(nodes[0])
        template = generator.get_guid(hu.TEMPLATE_KEY)
        self.assertEqual(a['CanBeMoved'], 'False')
        self.assertEqual(a['CanBePickedUp'], 'False')
        self.assertEqual(a['Stats'], 'HC_OBJ_UtilityPole')
        self.assertEqual(a['MapKey'], template)
        self.assertEqual(a['ParentTemplateId'], hc_cart.PARENT_TEMPLATE)
        self.assertNotIn('PhysicsTemplate', a)
        visual = ET.parse(self.public / 'Content/Assets/Props/[PAK]_HC_UtilityPole/_merged.lsf.lsx')
        visual_id = attrs(visual.find('.//region[@id="VisualBank"]//node[@id="Resource"]'))['ID']
        self.assertEqual(a['VisualTemplate'], visual_id)
        bounds = nodes[0].findall('.//node[@id="Bound"]')
        self.assertEqual(len(bounds), 3)
        for b in bounds:
            ba = attrs(b)
            hi = [float(x) for x in ba['Max'].split()]
            lo = [float(x) for x in ba['Min'].split()]
            self.assertTrue(all(l >= m - 1e-6 for l, m in zip(lo, hu.BMIN)))
            self.assertTrue(all(h <= m + 1e-6 for h, m in zip(hi, hu.BMAX)))
            self.assertAlmostEqual(float(ba['Height']), hi[1], places=6)           # Height equals the bound's own max Y
        inner = [attrs(b) for b in bounds if attrs(b)['Type'] == '0'][0]
        self.assertEqual([float(x) for x in inner['Max'].split()], list(hu.INNER_MAX))
        self.assertEqual([float(x) for x in inner['Min'].split()], list(hu.INNER_MIN))
        # the collision box is only the foot of the pole: small footprint, nowhere near the full 5 m
        self.assertLessEqual(hu.INNER_MAX[1], 2.0)
        self.assertLess(hu.INNER_MAX[0] - hu.INNER_MIN[0], 1.0)
        stat = (self.data / 'HC_Object_UtilityPole.txt').read_text(encoding='utf-8')
        self.assertIn('new entry "HC_OBJ_UtilityPole"', stat)
        self.assertIn('type "Object"', stat)
        self.assertIn('using "_BaseItem"', stat)
        self.assertIn(f'data "RootTemplate" "{template}"', stat)
        self.assertIn('data "Vitality" "-1"', stat)

    def test_spell_spawns_one_pole_with_the_requested_costs(self):
        text = (self.data / 'HC_Spells_UtilityPole.txt').read_text(encoding='utf-8')
        self.assertEqual(text.count('new entry "'), 1)
        f = stat_fields(text, hu.SPELL)
        template = generator.get_guid(hu.TEMPLATE_KEY)
        self.assertEqual(hu.SPELL, 'HC_Target_SparkingUtilityPole')
        self.assertIn('using "Projectile_GEB_Perform_TossCoin"', text)
        self.assertEqual(f['SpellProperties'].count('GROUND:Spawn('), 1)
        self.assertEqual(f['SpellProperties'], f'GROUND:Spawn({template});ApplyStatus(SELF,HC_GRID_SAFETY_FEE,100,3)')
        self.assertEqual(f['TargetRadius'], '9')
        self.assertEqual(f['UseCosts'], 'ActionPoint:1;HC_Junk:2')
        self.assertEqual(f['Cooldown'], 'OncePerRest')
        xml = generator_loca_text()
        for key in (hu.SPELL + '_Name', hu.SPELL + '_Description', hu.STATUS + '_Name', hu.STATUS + '_Description',
                    hu.OBJECT_STAT + '_Name', hu.OBJECT_STAT + '_Description'):
            self.assertIn(generator.get_handle(key), xml, key)
        self.assertEqual(f['DisplayName'], generator.get_handle(hu.SPELL + '_Name') + ';1')
        self.assertEqual(f['Description'], generator.get_handle(hu.SPELL + '_Description') + ';1')
        self.assertEqual(generator.LOCA_ENTRIES[generator.get_handle(hu.SPELL + '_Name')], 'Deferred Maintenance Pole Drop')
        self.assertIn(f['Icon'], (hu.SPELL_ICON_FALLBACK,) + tuple(self._custom_icon_names()))

    def test_spell_description_is_mechanics_first_with_three_to_five_sentences(self):
        text = generator.LOCA_ENTRIES[generator.get_handle(hu.SPELL + '_Description')]
        sentences = [s for s in re.split(r'(?<=[.!?])\s+', text.strip()) if s]
        self.assertTrue(3 <= len(sentences) <= 5, sentences)
        for fact in ('9 m', '2 Junk', 'long rest', '3 turns', 'lightning', '+1 to attack rolls', 'spell save DC'):
            self.assertIn(fact, text)
        self.assertLess(text.index('3 turns'), text.index('decorative'))
        self.assertTrue(sentences[-1].endswith('before.'))

    def _custom_icon_names(self):
        from hc_icon_keys import SPELL_ICON_KEYS
        return [SPELL_ICON_KEYS[hu.SPELL]] if hu.SPELL in SPELL_ICON_KEYS else []

    def test_status_grants_lightning_resistance_and_small_flat_bonuses(self):
        text = (self.data / 'HC_Status_UtilityPole.txt').read_text(encoding='utf-8')
        f = stat_fields(text, hu.STATUS)
        self.assertIn('type "StatusData"', text)
        self.assertEqual(hu.STATUS, 'HC_GRID_SAFETY_FEE')
        self.assertEqual(f['StatusType'], 'BOOST')
        self.assertEqual(f['Boosts'], 'Resistance(Lightning,Resistant);RollBonus(Attack,1);SpellSaveDC(1)')
        self.assertEqual(f['StackId'], hu.STATUS)
        self.assertEqual(f['StackType'], 'Overwrite')
        self.assertEqual(f['TickType'], 'EndTurn')
        self.assertEqual(f['DisplayName'], generator.get_handle(hu.STATUS + '_Name') + ';1')
        self.assertEqual(generator.LOCA_ENTRIES[generator.get_handle(hu.STATUS + '_Name')], 'Grid Safety Fee')
        desc = generator.LOCA_ENTRIES[generator.get_handle(hu.STATUS + '_Description')]
        for fact in ('lightning', '+1 to attack rolls', '+1 to your spell save DC'):
            self.assertIn(fact, desc)

    def test_status_differs_from_the_other_prop_statuses(self):
        import hc_robotaxi, hc_scooters, hc_tent
        others = [hc_barricade.STATUS, hc_robotaxi.STATUS, hc_scooters.STATUS, hc_tent.STATUS, 'HC_HONEY_BUCKET_CONFIDENCE']
        self.assertNotIn(hu.STATUS, others)
        # the other prop statuses grant AC, movement and advantage, temporary HP, a lightning rider and poison immunity
        self.assertEqual(hu.BOOSTS.count('Resistance(Lightning,Resistant)'), 1)
        for name in others:
            sources = [p.read_text(encoding='utf-8') for p in ROOT.glob('hc_*.py') if p.name != 'hc_utilitypole.py']
            self.assertFalse(any(f'new entry "{hu.STATUS}"' in t for t in sources))
            self.assertNotEqual(name, hu.STATUS)

    def test_vanilla_evidence_for_donor_icons_and_boost_tokens(self):
        stats = list((VANILLA / 'Shared/Stats/Generated/Data').glob('*.txt'))
        if not stats:
            self.skipTest('temp_race vanilla extract not available')
        corpus = '\n'.join(p.read_text(encoding='utf-8', errors='ignore') for p in stats)
        # the boost tokens also live in the Gustav / GustavDev / SharedDev status, passive and armor files
        wide = corpus + '\n'.join(p.read_text(encoding='utf-8', errors='ignore')
                                  for sub in ('Gustav', 'GustavDev', 'SharedDev')
                                  for name in ('Status_BOOST.txt', 'Passive.txt', 'Armor.txt')
                                  for p in (VANILLA / sub / 'Stats/Generated/Data').glob(name))
        self.assertRegex(corpus, r'new entry "Projectile_GEB_Perform_TossCoin"\ntype "SpellData"')
        self.assertIn('GROUND:Spawn(', corpus)
        self.assertIn('ApplyStatus(SELF,', corpus)
        for token in hu.BOOSTS.split(';'):
            self.assertIn(token, wide, token)
        self.assertRegex(wide, r'data "Boosts" "[^"]*SpellSaveDC\(1\)')
        self.assertRegex(wide, r'data "Boosts" "[^"]*Resistance\(Lightning,Resistant\)')
        self.assertRegex(wide, r'data "Boosts" "RollBonus\(Attack,1\)"')
        self.assertIn('data "Cooldown" "OncePerRest"', corpus)         # there is no OncePerLongRest token in vanilla
        self.assertNotIn('data "Cooldown" "OncePerLongRest"', corpus)
        self.assertIn(f'data "Icon" "{hu.SPELL_ICON_FALLBACK}"', wide)
        self.assertIn(f'data "Icon" "{hu.STATUS_ICON_FALLBACK}"', wide)
        self.assertIn('HC_Junk', (ROOT / 'hc_barricade.py').read_text(encoding='utf-8'))
        for name in (hu.SPELL, hu.STATUS, hu.OBJECT_STAT):              # new names must not collide with vanilla
            self.assertTrue(name.startswith('HC_'))
            self.assertNotIn(f'new entry "{name}"', wide)

    def test_grants_one_base_class_level_11_spell(self):
        self.assertEqual(self.grants, {'base': {11: ['HC_Target_SparkingUtilityPole']}, 'subclasses': {},
                                       'existing_list_spells': {}})

    def test_guids_are_unique_and_do_not_collide_with_other_props(self):
        own = {k: generator.get_guid(f'HC_UtilityPole_{k}') for k in ('bm', 'nm', 'pm', 'mat', 'visual')}
        own['template'] = generator.get_guid(hu.TEMPLATE_KEY)
        others = set()
        for prefix in ('HC_ShoppingCart', 'HC_BlueTarp', 'HC_Barricade', 'HC_PopUpTent', 'HC_PortaPotty'):
            others |= {generator.get_guid(f'{prefix}_{k}') for k in ('bm', 'nm', 'pm', 'mat', 'visual', 'RootTemplate')}
        self.assertEqual(len(set(own.values())), 6)
        self.assertFalse(set(own.values()) & others)
        written = set()
        for path in (self.public / 'Content/Assets/Props/[PAK]_HC_UtilityPole/_merged.lsf.lsx',
                     self.public / 'RootTemplates/HC_UtilityPole.lsf.lsx'):
            written |= set(GUID.findall(path.read_text(encoding='utf-8')))
        self.assertEqual(written - set(own.values()), {hu.PARENT_TEMPLATE})
        self.assertEqual(hu.PARENT_TEMPLATE, hc_cart.PARENT_TEMPLATE)
        self.assertEqual(hu.PARENT_TEMPLATE, hc_barricade.PARENT_TEMPLATE)

    def test_no_real_company_or_foreign_mod_references(self):
        files = [p for p in self.source.rglob('*') if p.is_file() and p.suffix.lower() not in ('.dds', '.gr2')]
        files += [ROOT / 'hc_utilitypole.py', Path(__file__)] + [p for p in hu.ASSET_SRC.glob('*.py')]
        self.assertGreater(len(files), 6)
        needles = ('patr' + 'iot', 'pg' + '&e', 'pacific ' + 'gas')
        for p in files:
            text = p.read_text(encoding='utf-8', errors='ignore').lower()
            for needle in needles:
                self.assertNotIn(needle, text, f'{needle} in {p}')
        # the fictional operator is named in the visible text
        loca = generator_loca_text()
        self.assertRegex(loca, r'Pacific Grid (&|&amp;) Excuse')


if __name__ == '__main__':
    unittest.main()
