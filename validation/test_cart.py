"""Abandoned Cart prop: assets, visual resource, root template, stat, spell and Venice L3 grant.

Runs on a freshly generated temporary tree. File-level checks only; nothing here proves it works in game.
"""
from pathlib import Path
import contextlib
import io
import re
import sys
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import generate_mod as generator
import hc_cart

RES = 'Generated/Public/HomelessCalifornian/Assets/Props/HC_ShoppingCart/Resources'


def attrs(node):
    return {a.get('id'): a.get('value') for a in node.findall('attribute')}


class CartTests(unittest.TestCase):
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

    def test_binary_assets_are_copied_next_to_the_pak_root(self):
        for name in hc_cart.ASSET_FILES:
            p = self.source / RES / name
            self.assertTrue(p.is_file(), name)
            self.assertGreater(p.stat().st_size, 1000, name)
        for tex in ('BM', 'NM', 'PM'):
            self.assertTrue((self.source / RES / f'HC_ShoppingCart_{tex}.DDS').read_bytes().startswith(b'DDS '))

    def test_visual_resource_matches_grill_pattern(self):
        path = self.public / 'Content/Assets/Props/[PAK]_HC_ShoppingCart/_merged.lsf.lsx'
        tree = ET.parse(path)
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
        self.assertEqual(v['Template'], RES + '/HC_ShoppingCart.Dummy_LTS_GEN_Fire_Basket_A.0')
        self.assertEqual(v['SourceFile'], RES + '/HC_ShoppingCart.GR2')
        objects = [attrs(n) for n in visual.findall('.//node[@id="Objects"]')]
        self.assertEqual([o['ObjectID'] for o in objects], [
            'HC_ShoppingCart.LTS_GEN_Fire_Basket_A_Mesh.0',
            'HC_ShoppingCart.LTS_GEN_Fire_Basket_A_Mesh_LOD1.1',
            'HC_ShoppingCart.LTS_GEN_Fire_Basket_A_Mesh_LOD2.2'])
        self.assertEqual({o['MaterialID'] for o in objects}, {attrs(material)['ID']})

    def test_root_template_is_a_static_prop_pointing_at_the_visual(self):
        tree = ET.parse(self.public / 'RootTemplates/HC_ShoppingCart.lsf.lsx')
        nodes = tree.findall('.//node[@id="GameObjects"]')
        self.assertEqual(len(nodes), 1)
        a = attrs(nodes[0])
        self.assertEqual(a['CanBeMoved'], 'False')
        self.assertEqual(a['CanBePickedUp'], 'False')
        self.assertEqual(a['Stats'], 'HC_OBJ_ShoppingCart')
        self.assertNotIn('PhysicsTemplate', a)
        visual = ET.parse(self.public / 'Content/Assets/Props/[PAK]_HC_ShoppingCart/_merged.lsf.lsx')
        visual_id = attrs(visual.find('.//region[@id="VisualBank"]//node[@id="Resource"]'))['ID']
        self.assertEqual(a['VisualTemplate'], visual_id)
        self.assertEqual(len(nodes[0].findall('.//node[@id="Bound"]')), 3)
        # Every guid it uses must differ from the wardrobe templates and be deterministic.
        self.assertEqual(a['MapKey'], generator.get_guid('HC_ShoppingCart_RootTemplate'))

    def test_object_stat_and_spell(self):
        stat = (self.public / 'Stats/Generated/Data/HC_Object_ShoppingCart.txt').read_text(encoding='utf-8')
        template = generator.get_guid('HC_ShoppingCart_RootTemplate')
        self.assertIn('new entry "HC_OBJ_ShoppingCart"', stat)
        self.assertIn('using "_BaseItem"', stat)
        self.assertIn(f'data "RootTemplate" "{template}"', stat)
        spell = (self.public / 'Stats/Generated/Data/HC_Spells_Cart.txt').read_text(encoding='utf-8')
        self.assertIn('new entry "HC_Target_AbandonedCart"', spell)
        self.assertIn('using "Projectile_GEB_Perform_TossCoin"', spell)
        self.assertIn(f'data "SpellProperties" "GROUND:Spawn({template})"', spell)
        self.assertEqual(spell.count('GROUND:Spawn('), 1)
        self.assertIn('data "UseCosts" "BonusActionPoint:1;HC_Junk:1"', spell)
        self.assertIn('data "Cooldown" "OncePerShortRest"', spell)
        self.assertIn('data "TargetRadius" "6"', spell)

    def test_venice_level_three_grants_cart_beside_shopping_cart_charge(self):
        lists = ET.parse(self.public / 'Lists/SpellLists.lsx')
        venice_lists = [attrs(n)['Spells'].split(';') for n in lists.findall('.//node[@id="SpellList"]')
                        if 'HC_Target_AbandonedCart' in attrs(n)['Spells']]
        self.assertEqual(len(venice_lists), 1)
        uid_node = next(n for n in lists.findall('.//node[@id="SpellList"]') if 'HC_Target_AbandonedCart' in attrs(n)['Spells'])
        uid = attrs(uid_node)['UUID']
        progressions = ET.parse(self.public / 'Progressions/Progressions.lsx')
        hits = [attrs(n) for n in progressions.findall('.//node[@id="Progression"]')
                if attrs(n).get('Name') == 'VeniceBoardwalkBrawler' and attrs(n).get('Level') == '3']
        self.assertTrue(any(f'AddSpells({uid})' in h.get('Selectors', '') for h in hits))
        # Shopping Cart Charge is granted by the subclass level 3 list that was already there.
        base = [attrs(n)['Spells'] for n in lists.findall('.//node[@id="SpellList"]') if 'Rush_ShoppingCartCharge' in attrs(n)['Spells']]
        self.assertEqual(len(base), 1)

    def test_new_loca_handles_exist(self):
        xml = (self.public / 'Localization/English/HomelessCalifornian.loca.xml').read_text(encoding='utf-8')
        for key in ('HC_OBJ_ShoppingCart_Name', 'HC_OBJ_ShoppingCart_Description',
                    'HC_Target_AbandonedCart_Name', 'HC_Target_AbandonedCart_Description'):
            self.assertIn(f'contentuid="{generator.get_handle(key)}"', xml, key)
        self.assertIn('Abandoned Cart', xml)


if __name__ == '__main__':
    unittest.main()
