"""Municipal Hostile Architecture Bench prop and spell: assets, visual resource, root template, stat, status, spell and grants.

Generates into a temporary tree through hc_bench.generate_bench only (independent of generate_mod.main()).
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
import hc_bench as hb
import hc_cart
import hc_portapotty
import hc_robotaxi
import hc_scooters
import hc_tarp
import hc_tent

DIVINE = ROOT / 'tools' / 'Packed' / 'Tools' / 'Divine.exe'
VANILLA = ROOT / 'temp_race' / 'Public'
RES = 'Generated/Public/HomelessCalifornian/Assets/Props/HC_Bench/Resources'
GUID = re.compile(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}')
# Boosts of the other prop statuses (cart-less list, see each hc_*.py): the bench status must be different from all of them.
OTHER_PROP_BOOSTS = ('AC(2)', 'TemporaryHP(8)', 'CharacterWeaponDamage(1d8,Lightning);ActionResource(Movement,3,0)',
                     'ActionResource(Movement,3,0);Advantage(SavingThrow,Dexterity)',
                     'StatusImmunity(SG_Poisoned);RollBonus(SavingThrow,1d4)')


def attrs(node):
    return {a.get('id'): a.get('value') for a in node.findall('attribute')}


def stat_fields(text, name):
    block = text.split(f'new entry "{name}"')[1].split('new entry "')[0]
    return dict(re.findall(r'data "([^"]+)" "([^"]*)"', block))


def generator_loca_text():
    """Rendered loca entries as one searchable string (LOCA_ENTRIES is filled by add_loca)."""
    return '\n'.join(f'contentuid="{h}" {t}' for h, t in generator.LOCA_ENTRIES.items())


class BenchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.source = Path(cls._tmp.name)
        cls.public = cls.source / 'Public/HomelessCalifornian'
        cls.grants = hb.generate_bench(cls.public, generator.add_loca, generator.get_guid)
        cls.data = cls.public / 'Stats/Generated/Data'

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def test_binary_assets_are_tracked_and_copied_next_to_the_pak_root(self):
        for name in hb.ASSET_FILES:
            self.assertGreater((hb.ASSET_SRC / name).stat().st_size, 1000, name)
            p = self.source / RES / name
            self.assertTrue(p.is_file(), name)
            self.assertEqual(p.read_bytes(), (hb.ASSET_SRC / name).read_bytes(), name)
        for tex in ('BM', 'NM', 'PM'):
            self.assertTrue((self.source / RES / f'HC_Bench_{tex}.DDS').read_bytes().startswith(b'DDS '))
        for script in ('build_bench_model.py', 'bench_paint.py', 'render_bench.py'):
            self.assertTrue((hb.ASSET_SRC / script).is_file(), script)

    def test_base_colour_texture_is_1024_bc3_and_matches_the_visual_resource(self):
        header = (hb.ASSET_SRC / 'HC_Bench_BM.DDS').read_bytes()[:128]
        height, width = int.from_bytes(header[12:16], 'little'), int.from_bytes(header[16:20], 'little')
        self.assertEqual((width, height), (1024, 1024))
        self.assertIn(header[84:88], (b'DXT1', b'DXT5'))
        tree = ET.parse(self.public / 'Content/Assets/Props/[PAK]_HC_Bench/_merged.lsf.lsx')
        sizes = {attrs(t)['Name']: (attrs(t)['Width'], attrs(t)['Height'])
                 for t in tree.findall('.//region[@id="TextureBank"]//node[@id="Resource"]')}
        self.assertEqual(sizes['HC_Bench_BM'], ('1024', '1024'))

    @unittest.skipUnless(DIVINE.is_file(), 'Divine.exe not available')
    def test_gr2_round_trips_through_divine_with_three_lods_and_budget(self):
        with tempfile.TemporaryDirectory() as tmp:
            dae = Path(tmp) / 'rt.dae'
            result = subprocess.run([str(DIVINE), '-g', 'bg3', '-a', 'convert-model',
                                     '-s', str(hb.ASSET_SRC / 'HC_Bench.GR2'), '-d', str(dae),
                                     '-i', 'gr2', '-o', 'dae', '-l', 'warn'], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            text = dae.read_text(encoding='utf-8')
        self.assertEqual(re.findall(r'<geometry id="([^"]+)"', text), [
            'LTS_GEN_Fire_Basket_A_Mesh-geom', 'LTS_GEN_Fire_Basket_A_Mesh_LOD1-geom', 'LTS_GEN_Fire_Basket_A_Mesh_LOD2-geom'])
        counts = [int(c) for c in re.findall(r'<triangles count="(\d+)"', text)]
        self.assertEqual(counts, [hb.TRIANGLES] * 3)
        self.assertTrue(all(c < 3500 for c in counts))
        self.assertIn('Dummy_LTS_GEN_Fire_Basket_A', text)
        positions = re.search(r'LTS_GEN_Fire_Basket_A_Mesh-positions-array" count="\d+">([^<]*)<', text).group(1).split()
        xyz = [[float(v) for v in positions[i::3]] for i in range(3)]
        for axis, values in enumerate(xyz):
            self.assertAlmostEqual(min(values), hb.BMIN[axis], delta=0.01, msg=f'min axis {axis}')
            self.assertAlmostEqual(max(values), hb.BMAX[axis], delta=0.01, msg=f'max axis {axis}')
        # the bench itself is about 2.1 m long x 0.76 m deep x 1 m tall on a 3.2 m concrete pad, and the prop stands on the ground
        self.assertAlmostEqual(hb.INNER_MAX[0] - hb.INNER_MIN[0], 2.08, delta=0.1)
        self.assertAlmostEqual(hb.INNER_MAX[1], 1.0, delta=0.05)
        self.assertAlmostEqual(hb.INNER_MAX[2] - hb.INNER_MIN[2], 0.76, delta=0.05)
        self.assertAlmostEqual(hb.BMAX[0] - hb.BMIN[0], 3.2, delta=0.05)
        self.assertEqual(hb.BMIN[1], 0.0)

    def test_visual_resource_matches_cart_pattern(self):
        tree = ET.parse(self.public / 'Content/Assets/Props/[PAK]_HC_Bench/_merged.lsf.lsx')
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
        self.assertEqual(v['Template'], RES + '/HC_Bench.Dummy_LTS_GEN_Fire_Basket_A.0')
        self.assertEqual(v['SourceFile'], RES + '/HC_Bench.GR2')
        objects = [attrs(n) for n in visual.findall('.//node[@id="Objects"]')]
        self.assertEqual([o['ObjectID'] for o in objects], [
            'HC_Bench.LTS_GEN_Fire_Basket_A_Mesh.0',
            'HC_Bench.LTS_GEN_Fire_Basket_A_Mesh_LOD1.1',
            'HC_Bench.LTS_GEN_Fire_Basket_A_Mesh_LOD2.2'])
        self.assertEqual({o['MaterialID'] for o in objects}, {attrs(material)['ID']})
        for key, size in (('BoundsMin', hb.BMIN), ('BoundsMax', hb.BMAX)):
            self.assertEqual([float(x) for x in v[key].split()], [float(f'{x:g}') for x in size])

    def test_root_template_and_object_stat_reference_each_other(self):
        tree = ET.parse(self.public / 'RootTemplates/HC_Bench.lsf.lsx')
        nodes = tree.findall('.//node[@id="GameObjects"]')
        self.assertEqual(len(nodes), 1)
        a = attrs(nodes[0])
        template = generator.get_guid(hb.TEMPLATE_KEY)
        self.assertEqual(a['CanBeMoved'], 'False')
        self.assertEqual(a['CanBePickedUp'], 'False')
        self.assertEqual(a['Stats'], 'HC_OBJ_HostileBench')
        self.assertEqual(a['MapKey'], template)
        self.assertEqual(a['ParentTemplateId'], hc_cart.PARENT_TEMPLATE)
        self.assertNotIn('PhysicsTemplate', a)
        visual = ET.parse(self.public / 'Content/Assets/Props/[PAK]_HC_Bench/_merged.lsf.lsx')
        visual_id = attrs(visual.find('.//region[@id="VisualBank"]//node[@id="Resource"]'))['ID']
        self.assertEqual(a['VisualTemplate'], visual_id)
        bounds = nodes[0].findall('.//node[@id="Bound"]')
        self.assertEqual(len(bounds), 3)
        for b in bounds:
            ba = attrs(b)
            hi = [float(x) for x in ba['Max'].split()]
            lo = [float(x) for x in ba['Min'].split()]
            self.assertTrue(all(l >= m - 1e-6 for l, m in zip(lo, hb.BMIN)))
            self.assertTrue(all(h <= m + 1e-6 for h, m in zip(hi, hb.BMAX)))
            self.assertAlmostEqual(float(ba['Height']), hi[1], places=6)           # Height equals the bound's own max Y
        inner = [attrs(b) for b in bounds if attrs(b)['Type'] == '0'][0]
        self.assertEqual([float(x) for x in inner['Max'].split()], list(hb.INNER_MAX))
        self.assertEqual([float(x) for x in inner['Min'].split()], list(hb.INNER_MIN))
        stat = (self.data / 'HC_Object_Bench.txt').read_text(encoding='utf-8')
        self.assertIn('new entry "HC_OBJ_HostileBench"', stat)
        self.assertIn('type "Object"', stat)
        self.assertIn('using "_BaseItem"', stat)
        self.assertIn(f'data "RootTemplate" "{template}"', stat)
        self.assertIn('data "Vitality" "-1"', stat)

    def test_spell_spawns_one_bench_with_the_requested_costs(self):
        text = (self.data / 'HC_Spells_Bench.txt').read_text(encoding='utf-8')
        self.assertEqual(text.count('new entry "'), 1)
        f = stat_fields(text, hb.SPELL)
        template = generator.get_guid(hb.TEMPLATE_KEY)
        self.assertEqual(hb.SPELL, 'HC_Target_HostileArchitectureBench')
        self.assertIn('using "Projectile_GEB_Perform_TossCoin"', text)
        self.assertEqual(f['SpellProperties'].count('GROUND:Spawn('), 1)
        self.assertEqual(f['SpellProperties'], f'GROUND:Spawn({template});ApplyStatus(SELF,HC_CERTIFIED_BENCH_SLEEPER,100,3)')
        self.assertEqual(f['TargetRadius'], '9')
        self.assertEqual(f['UseCosts'], 'ActionPoint:1')
        self.assertNotIn('HC_Junk', text)
        self.assertEqual(f['Cooldown'], 'OncePerRest')
        xml = generator_loca_text()
        for key in (hb.SPELL + '_Name', hb.SPELL + '_Description', hb.STATUS + '_Name', hb.STATUS + '_Description',
                    hb.OBJECT_STAT + '_Name', hb.OBJECT_STAT + '_Description'):
            self.assertIn(generator.get_handle(key), xml, key)
        self.assertEqual(f['DisplayName'], generator.get_handle(hb.SPELL + '_Name') + ';1')
        self.assertEqual(f['Description'], generator.get_handle(hb.SPELL + '_Description') + ';1')
        self.assertEqual(generator.LOCA_ENTRIES[generator.get_handle(hb.SPELL + '_Name')], 'Municipal Hostile Architecture Installation')
        self.assertIn(f['Icon'], (hb.SPELL_ICON_FALLBACK,) + tuple(self._custom_icon_names()))

    def test_spell_description_is_mechanics_first_with_three_to_five_sentences(self):
        text = generator.LOCA_ENTRIES[generator.get_handle(hb.SPELL + '_Description')]
        sentences = [s for s in re.split(r'(?<=[.!?])\s+', text.strip()) if s]
        self.assertTrue(3 <= len(sentences) <= 5, sentences)
        for fact in ('9 m', 'no Junk', 'long rest', '3 turns', 'Piercing', 'Bludgeoning', 'Prone'):
            self.assertIn(fact, text)
        self.assertLess(text.index('3 turns'), text.index('nap on it'))
        self.assertTrue(sentences[-1].endswith('anyway.'))

    def _custom_icon_names(self):
        from hc_icon_keys import SPELL_ICON_KEYS
        return [SPELL_ICON_KEYS[hb.SPELL]] if hb.SPELL in SPELL_ICON_KEYS else []

    def test_status_grants_piercing_bludgeoning_resistance_and_prone_immunity(self):
        text = (self.data / 'HC_Status_Bench.txt').read_text(encoding='utf-8')
        f = stat_fields(text, hb.STATUS)
        self.assertIn('type "StatusData"', text)
        self.assertEqual(hb.STATUS, 'HC_CERTIFIED_BENCH_SLEEPER')
        self.assertEqual(f['StatusType'], 'BOOST')
        self.assertEqual(f['Boosts'], 'Resistance(Piercing,Resistant);Resistance(Bludgeoning,Resistant);StatusImmunity(SG_Prone)')
        self.assertEqual(f['StackId'], hb.STATUS)
        self.assertEqual(f['StackType'], 'Overwrite')
        self.assertEqual(f['TickType'], 'EndTurn')
        self.assertEqual(f['DisplayName'], generator.get_handle(hb.STATUS + '_Name') + ';1')
        self.assertEqual(generator.LOCA_ENTRIES[generator.get_handle(hb.STATUS + '_Name')], 'Certified Bench Sleeper')
        desc = generator.LOCA_ENTRIES[generator.get_handle(hb.STATUS + '_Description')]
        for fact in ('Resistance to Piercing and Bludgeoning', 'Immune to being knocked Prone'):
            self.assertIn(fact, desc)
        self.assertNotIn(f['Boosts'], OTHER_PROP_BOOSTS)                      # different from every other prop status
        for other in (hc_barricade.STATUS, hc_scooters.STATUS, hc_robotaxi.STATUS, hc_portapotty.STATUS):
            self.assertNotEqual(hb.STATUS, other)

    def test_vanilla_evidence_for_donor_icons_and_functors(self):
        stats = list((VANILLA / 'Shared/Stats/Generated/Data').glob('*.txt'))
        if not stats:
            self.skipTest('temp_race vanilla extract not available')
        corpus = '\n'.join(p.read_text(encoding='utf-8', errors='ignore') for p in stats)
        # the boost tokens also live in the Gustav / GustavDev / SharedDev status files
        wide = corpus + '\n'.join(p.read_text(encoding='utf-8', errors='ignore')
                                  for sub in ('Gustav', 'GustavDev', 'SharedDev')
                                  for p in (VANILLA / sub / 'Stats/Generated/Data').glob('Status_*.txt'))
        self.assertRegex(corpus, r'new entry "Projectile_GEB_Perform_TossCoin"\ntype "SpellData"')
        self.assertIn('GROUND:Spawn(', corpus)
        self.assertIn('ApplyStatus(SELF,', corpus)
        self.assertIn('Resistance(Piercing,Resistant)', wide)
        self.assertIn('Resistance(Bludgeoning,Resistant)', wide)
        self.assertIn('Attribute(Grounded);StatusImmunity(SG_Prone)', wide)   # MAG_UNMOVABLE
        self.assertIn('data "Cooldown" "OncePerRest"', corpus)         # there is no OncePerLongRest token in vanilla
        self.assertNotIn('data "Cooldown" "OncePerLongRest"', corpus)
        every = '\n'.join(p.read_text(encoding='utf-8', errors='ignore')                  # icons also live in the *Dev spell files
                          for sub in ('Shared', 'SharedDev', 'Gustav', 'GustavDev', 'Honour')
                          for p in (VANILLA / sub / 'Stats/Generated/Data').glob('*.txt'))
        self.assertIn(f'data "Icon" "{hb.SPELL_ICON_FALLBACK}"', every)
        self.assertIn(f'data "Icon" "{hb.STATUS_ICON_FALLBACK}"', every)
        for name in (hb.SPELL, hb.STATUS, hb.OBJECT_STAT):              # new names must not collide with vanilla
            self.assertTrue(name.startswith('HC_'))
            self.assertNotIn(f'new entry "{name}"', wide)

    def test_grants_one_base_class_level_10_spell(self):
        self.assertEqual(self.grants, {'base': {10: ['HC_Target_HostileArchitectureBench']}, 'subclasses': {},
                                       'existing_list_spells': {}})

    def test_guids_are_unique_and_do_not_collide_with_other_props(self):
        own = {k: generator.get_guid(f'HC_Bench_{k}') for k in ('bm', 'nm', 'pm', 'mat', 'visual')}
        own['template'] = generator.get_guid(hb.TEMPLATE_KEY)
        others = set()
        for prefix in ('HC_ShoppingCart', 'HC_BlueTarp', 'HC_Barricade', 'HC_PopUpTent', 'HC_PortaPotty', 'HC_Robotaxi',
                       'HC_ScooterGraveyard'):
            others |= {generator.get_guid(f'{prefix}_{k}') for k in ('bm', 'nm', 'pm', 'mat', 'visual', 'RootTemplate')}
        self.assertEqual(len(set(own.values())), 6)
        self.assertFalse(set(own.values()) & others)
        written = set()
        for path in (self.public / 'Content/Assets/Props/[PAK]_HC_Bench/_merged.lsf.lsx',
                     self.public / 'RootTemplates/HC_Bench.lsf.lsx'):
            written |= set(GUID.findall(path.read_text(encoding='utf-8')))
        self.assertEqual(written - set(own.values()), {hb.PARENT_TEMPLATE})
        for module in (hc_cart, hc_tarp, hc_barricade, hc_tent, hc_portapotty, hc_robotaxi, hc_scooters):
            self.assertEqual(hb.PARENT_TEMPLATE, module.PARENT_TEMPLATE)

    def test_names_do_not_collide_with_other_hc_content(self):
        for path in ROOT.glob('hc_*.py'):
            if path.name == 'hc_bench.py':
                continue
            text = path.read_text(encoding='utf-8', errors='ignore')
            for name in (hb.SPELL, hb.STATUS, hb.OBJECT_STAT, hb.TEMPLATE_KEY):
                self.assertNotIn(f'"{name}"', text, f'{name} also appears in {path.name}')

    def test_no_foreign_mod_references(self):
        files = [p for p in self.source.rglob('*') if p.is_file() and p.suffix.lower() not in ('.dds', '.gr2')]
        files += [ROOT / 'hc_bench.py', Path(__file__)] + [p for p in hb.ASSET_SRC.glob('*.py')]
        self.assertGreater(len(files), 6)
        needle = 'patr' + 'iot'
        for p in files:
            self.assertNotIn(needle, p.read_text(encoding='utf-8', errors='ignore').lower(), str(p))


if __name__ == '__main__':
    unittest.main()
