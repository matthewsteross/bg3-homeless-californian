"""Round 3 junk items (run on a freshly generated temp tree).

Spec: work/spec-items.md. Four items granted by the HC_Shout_CurbAlert shout:
Caltrans Detour Sign, Duct-Taped High-Tops, Lukewarm Gas Station Kombucha, Tin-Foil Sun Visor.

Vanilla stat names and parent template ids are proved here against the local
extraction in temp_race: the stat entry must name the template id, and the id
must occur in the extracted RootTemplates/_merged.lsf.
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

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'validation'))
import generate_mod as generator
from test_spell_rules import parse_entries

VANILLA_DATA = ROOT / 'temp_race/Public/Shared/Stats/Generated/Data'
VANILLA_TEMPLATES = ROOT / 'temp_race/Public/Shared/RootTemplates/_merged.lsf'
SPELL = 'HC_Shout_CurbAlert'
GRANT_LEVEL = '6'

# item -> (stat file, stat type, vanilla donor stat, vanilla donor template id)
ITEMS = {
    'HC_WPN_CaltransDetourSign': ('Weapon.txt', 'Weapon', 'WPN_Greatclub', '19ce6720-03b6-4d22-bf35-4963b510d1da'),
    'HC_ARM_DuctTapedHighTops': ('Armor.txt', 'Armor', 'ARM_Boots_Leather', '969bab00-b269-46a5-a7e9-dd4887814719'),
    'HC_OBJ_LukewarmKombucha': ('Object.txt', 'Object', 'OBJ_Potion_Healing', 'd47006e9-8a51-453d-b200-9e0d42e9bbab'),
    'HC_ARM_TinfoilSunVisor': ('Armor.txt', 'Armor', 'ARM_Helmet_Leather', 'c58a1f91-ec1b-49c8-96ab-d94d4be4b584'),
}


def attrs_of(node):
    return {a.get('id'): a.get('value', '') for a in node.findall('attribute')}


class JunkItemTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        source = Path(cls._tmp.name)
        cls.public = source / 'Public/HomelessCalifornian'
        with patch.object(generator, 'PUBLIC_DIR', str(cls.public)), \
                patch.object(generator, 'MODS_DIR', str(source / 'Mods/HomelessCalifornian')), \
                contextlib.redirect_stdout(io.StringIO()):
            generator.main()
        data = cls.public / 'Stats/Generated/Data'
        cls.stats = {}
        cls.stat_text = ''
        for name in ('HC_Weapon_JunkItems.txt', 'HC_Armor_JunkItems.txt', 'HC_Object_JunkItems.txt'):
            text = (data / name).read_text(encoding='utf-8')
            cls.stat_text += text + '\n'
            cls.stats.update(parse_entries(text))
        cls.statuses = parse_entries((data / 'HC_Status_JunkItems.txt').read_text(encoding='utf-8'))
        cls.spells = parse_entries((data / 'HC_Spell_Shout_CurbAlert.txt').read_text(encoding='utf-8'))
        templates = ET.parse(cls.public / 'RootTemplates/HC_JunkItems.lsf.lsx')
        cls.templates = {attrs_of(n)['Stats']: n for n in templates.findall('.//node[@id="GameObjects"]')}
        loca = ET.parse(cls.public / 'Localization/English/HomelessCalifornian.loca.xml')
        cls.loca = {c.get('contentuid'): c.text for c in loca.iter('content')}
        cls.progressions = [attrs_of(n) for n in
                            ET.parse(cls.public / 'Progressions/Progressions.lsx').findall('.//node[@id="Progression"]')]
        cls.spell_lists = {}
        for node in ET.parse(cls.public / 'Lists/SpellLists.lsx').findall('.//node[@id="SpellList"]'):
            a = attrs_of(node)
            cls.spell_lists[a['UUID']] = a['Spells'].split(';')

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    # --------------------------------------------------------- vanilla proof
    def test_donor_stats_and_template_ids_exist_in_vanilla(self):
        template_bytes = VANILLA_TEMPLATES.read_bytes()
        for item, (filename, kind, donor, template_id) in ITEMS.items():
            with self.subTest(item=item):
                text = (VANILLA_DATA / filename).read_text(encoding='utf-8-sig')
                entry = parse_entries(text)[donor]
                self.assertRegex(text, rf'new entry "{donor}"\s+type "{kind}"')
                self.assertEqual(entry['data']['RootTemplate'], template_id)
                # The template id and the donor stat name both occur in the extracted template table.
                self.assertIn(template_id.encode(), template_bytes)
                self.assertIn(donor.encode(), template_bytes)

    def test_boost_and_functor_syntax_exists_in_vanilla(self):
        text = ''.join(re.sub(r'\s+', '', p.read_text(encoding='utf-8-sig', errors='replace'))
                       for p in VANILLA_DATA.glob('*.txt'))
        for snippet in ('ActionResource(Movement,3,0)', 'Advantage(SavingThrow,Wisdom)',
                        'RegainHitPoints(2d4+2)', 'ApplyStatus(RAGE_STOP_REMOVE,100,1)'):
            with self.subTest(snippet=snippet):
                self.assertIn(re.sub(r'\s+', '', snippet), text)
        # The potion template consumes a BOOST status, and the status holds the heal.
        statuses = parse_entries((VANILLA_DATA / 'Status_BOOST.txt').read_text(encoding='utf-8-sig'))
        self.assertIn('RegainHitPoints(2d4+2)', statuses['POTION_OF_HEALING']['data']['OnApplyFunctors'])
        self.assertIn(b'POTION_OF_HEALING', VANILLA_TEMPLATES.read_bytes())

    # ------------------------------------------------------------- wiring
    def test_stats_use_donors_and_point_at_hc_templates(self):
        self.assertEqual(set(self.stats), set(ITEMS))
        for item, (_, kind, donor, template_id) in ITEMS.items():
            with self.subTest(item=item):
                entry = self.stats[item]
                self.assertIn(f'new entry "{item}"\ntype "{kind}"\nusing "{donor}"', self.stat_text)
                self.assertEqual(entry['using'], donor)
                template = attrs_of(self.templates[item])
                self.assertEqual(entry['data']['RootTemplate'], template['MapKey'])
                self.assertNotEqual(template['MapKey'], template_id)
                self.assertEqual(template['ParentTemplateId'], template_id)
                self.assertEqual(template['Type'], 'item')
                self.assertEqual(entry['data']['Rarity'] in ('Common', 'Uncommon'), True)

    def test_template_keys_unique_and_no_equipment_child(self):
        keys = [attrs_of(n)['MapKey'] for n in self.templates.values()]
        self.assertEqual(len(keys), len(set(keys)))
        for item, node in self.templates.items():
            self.assertIsNone(node.find('.//node[@id="Equipment"]'), item)

    def test_localization_present(self):
        for item, node in self.templates.items():
            attrs = {a.get('id'): a.get('handle') for a in node.findall('attribute')}
            for key in ('DisplayName', 'Description'):
                with self.subTest(item=item, key=key):
                    self.assertTrue(self.loca.get(attrs[key]))
        for name in ('HC_POTION_KOMBUCHA', 'HC_KOMBUCHA_BUZZ', SPELL):
            for key in ('DisplayName', 'Description'):
                entry = (self.statuses.get(name) or self.spells.get(name))
                if name == 'HC_POTION_KOMBUCHA' and key == 'Description':
                    continue
                with self.subTest(name=name, key=key):
                    self.assertTrue(self.loca.get(entry['data'][key].split(';')[0]))

    # --------------------------------------------------------- item effects
    def test_item_effects(self):
        weapon = self.stats['HC_WPN_CaltransDetourSign']
        self.assertEqual(weapon['data']['Rarity'], 'Common')
        # Plain renamed Greatclub: no damage or property override, nothing added to the donor.
        for key in ('Damage', 'Damage Type', 'Weapon Properties', 'BoostsOnEquipMainHand', 'PassivesMainHand'):
            self.assertNotIn(key, weapon['data'])
        self.assertEqual(self.stats['HC_ARM_DuctTapedHighTops']['data']['Boosts'], 'ActionResource(Movement,1.5,0)')
        self.assertEqual(self.stats['HC_ARM_TinfoilSunVisor']['data']['Boosts'], 'Advantage(SavingThrow,Wisdom)')
        self.assertNotIn('Resistance', self.stats['HC_ARM_TinfoilSunVisor']['data']['Boosts'])

    def test_kombucha_heals_and_applies_buzz(self):
        # The consumed status is restated in the HC template and defined here.
        use = self.templates['HC_OBJ_LukewarmKombucha'].find('.//node[@id="OnUsePeaceActions"]')
        attrs = attrs_of(use.find('.//node[@id="Attributes"]'))
        self.assertEqual(attrs['StatsId'], 'HC_POTION_KOMBUCHA')
        self.assertEqual(attrs['Consume'], 'True')
        drink = self.statuses['HC_POTION_KOMBUCHA']['data']
        self.assertEqual(drink['StatusType'], 'BOOST')
        self.assertEqual(drink['OnApplyFunctors'], 'RegainHitPoints(2d4+2);ApplyStatus(HC_KOMBUCHA_BUZZ,100,2)')
        buzz = self.statuses['HC_KOMBUCHA_BUZZ']['data']
        self.assertEqual(buzz['StatusType'], 'BOOST')
        self.assertEqual(buzz['Boosts'], 'ActionResource(Movement,3,0)')
        self.assertEqual(buzz['TickType'], 'EndTurn')
        for forbidden in ('SavingThrow', 'FECAL', 'Stench'):
            self.assertNotIn(forbidden, drink['OnApplyFunctors'])

    # ---------------------------------------------------------------- spell
    def test_curb_alert_summons_all_four_and_recharges_per_rest(self):
        spell = self.spells[SPELL]
        self.assertEqual(spell['using'], 'Shout_SecondWind')
        data = spell['data']
        self.assertEqual(data['SpellType'], 'Shout')
        self.assertEqual(data['Cooldown'], 'OncePerRest')
        self.assertEqual(data['UseCosts'], 'ActionPoint:1')
        self.assertEqual(data['TargetRadius'], '0')
        self.assertIn('IgnoreSilence', data['SpellFlags'])
        self.assertIn('UnavailableInDialogs', data['SpellFlags'])
        for item in ITEMS:
            template_id = attrs_of(self.templates[item])['MapKey']
            self.assertIn(f'SummonInInventory({template_id},-1,1,false,false,false)', data['SpellProperties'])
        self.assertEqual(data['SpellProperties'].count('SummonInInventory('), 4)

    def test_curb_alert_granted_once_at_level_six(self):
        grants = []
        for a in self.progressions:
            if a.get('Name') != 'HomelessCalifornian' or a.get('ProgressionType') == '1':
                continue
            for uid in re.findall(r'AddSpells\(([0-9a-f-]{36})', a.get('Selectors', '')):
                if SPELL in self.spell_lists[uid]:
                    grants.append(a['Level'])
        self.assertEqual(grants, [GRANT_LEVEL])
        # Only one new spell was added at that level.
        new_at_level = [s for a in self.progressions
                        if a.get('Name') == 'HomelessCalifornian' and a.get('Level') == GRANT_LEVEL
                        for uid in re.findall(r'AddSpells\(([0-9a-f-]{36})', a.get('Selectors', ''))
                        for s in self.spell_lists[uid] if s.startswith('HC_')]
        # Public Scene, Curb Alert, 3 AM Sidewalk Lawnmower Disassembly, NIMBY Public Comment Period (round 8), the Spin Bike (round 10), and Therapy, Setting Boundaries (round 11)
        self.assertEqual(len(new_at_level), 7)  # +Acoustic Privacy Pod (round 12)

    def test_icons_exist_in_vanilla_or_hc_assets(self):
        vanilla_icons = (VANILLA_TEMPLATES.read_bytes() + b''.join(
            p.read_bytes() for p in VANILLA_DATA.glob('*.txt')))
        for item, node in self.templates.items():
            icon = attrs_of(node)['Icon']
            with self.subTest(item=item):
                self.assertIn(icon.encode(), vanilla_icons)
        self.assertIn(self.statuses['HC_KOMBUCHA_BUZZ']['data']['Icon'].encode(), vanilla_icons)
        spell_icon = self.spells[SPELL]['data']['Icon']
        self.assertTrue(spell_icon.encode() in vanilla_icons or
                        (ROOT / 'assets/icons' / (spell_icon + '.png')).is_file())


if __name__ == '__main__':
    unittest.main()
