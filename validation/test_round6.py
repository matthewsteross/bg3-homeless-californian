"""Round 6 file-level contracts (Oakland Flea Market items, subrace stereotype spells, street tactics, and new trade/doctrine options)."""
import contextlib
import io
from pathlib import Path
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
import hc_round6 as round6
import validate
from hc_icon_keys import SPELL_ICON_KEYS

VANILLA_TEMPLATES = ROOT / 'temp_race/Public/Shared/RootTemplates/_merged.lsf'

EXPECTED_SPELLS = {
    round6.FLEA_MARKET_SHOUT,
    round6.SURFBOARD_CHECK,
    round6.ZOOM_LAYOFF,
    round6.SHAKE_AND_BAKE,
    round6.SQUATTER_LIEN,
    round6.CVS_RECEIPT,
    round6.SIDESHOW_DONUT,
}

EXPECTED_ITEMS = {spec[0] for spec in round6.ITEMS}
EXPECTED_STATUSES = {round6.RHINO_CONSUME_STATUS} | {spec[0] for spec in round6.STATUS_SPECS}


class RoundSixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.tmp.name)
        cls.public = cls.root / 'Public/HomelessCalifornian'
        with patch.object(generator, 'PUBLIC_DIR', str(cls.public)), \
                patch.object(generator, 'MODS_DIR', str(cls.root / 'Mods/HomelessCalifornian')), \
                patch.dict(generator.LOCA_ENTRIES, {}, clear=True), \
                contextlib.redirect_stdout(io.StringIO()):
            generator.main()
        cls.stats = validate.read_stats(cls.public)
        cls.vanilla = validate.read_stats(ROOT / 'temp_race')
        cls.new = {k: v[0] for k, v in cls.stats.items() if v[0].path.name.endswith('_Round6.txt')}
        cls.loca = {e.get('contentuid'): e.text for e in
                    ET.parse(cls.public / 'Localization/English/HomelessCalifornian.loca.xml').iter('content')}
        cls.progs = [cls.attrs(n) for n in ET.parse(cls.public / 'Progressions/Progressions.lsx')
                     .findall('.//node[@id="Progression"]')]
        cls.lists = {cls.attrs(n)['UUID']: cls.attrs(n)['Spells'].split(';') for n in
                     ET.parse(cls.public / 'Lists/SpellLists.lsx').findall('.//node[@id="SpellList"]')}
        cls.passive_lists = {cls.attrs(n)['UUID']: cls.attrs(n)['Passives'].split(',') for n in
                             ET.parse(cls.public / 'Lists/PassiveLists.lsx').findall('.//node[@id="PassiveList"]')}
        templates = ET.parse(cls.public / 'RootTemplates/HC_Round6Items.lsf.lsx')
        cls.templates = {cls.attrs(n)['Stats']: n for n in templates.findall('.//node[@id="GameObjects"]')}

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    @staticmethod
    def attrs(node):
        return {a.get('id'): a.get('value') for a in node.findall('attribute')}

    def fields(self, name):
        return self.new[name].fields

    def grants(self, prog):
        return [s for uid in re.findall(r'AddSpells\(([0-9a-f-]+)', prog.get('Selectors', ''))
                for s in self.lists[uid]]

    def test_all_round6_entries_are_unique_prefixed_and_do_not_override_vanilla(self):
        self.assertEqual(set(self.new), EXPECTED_SPELLS | EXPECTED_ITEMS | EXPECTED_STATUSES)
        self.assertEqual(len(self.new), 18)
        for name in self.new:
            self.assertTrue(name.startswith('HC_'))
            self.assertNotIn(name, self.vanilla)
            self.assertEqual(len(self.stats[name]), 1)

    def test_all_donors_and_item_templates_exist_in_vanilla_and_none_are_honour_overridden(self):
        honour_names = {name for name, entries in self.vanilla.items()
                        if any('Honour' in e.path.parts for e in entries)}
        for name, entry in self.new.items():
            if entry.using:
                self.assertIn(entry.using, self.vanilla, name)
                self.assertTrue(any(e.type == entry.type for e in self.vanilla[entry.using]), name)
                self.assertNotIn(entry.using, honour_names, name)
        template_bytes = VANILLA_TEMPLATES.read_bytes()
        for name, kind, base_stat, parent, icon, *_ in round6.ITEMS:
            self.assertIn(parent.encode(), template_bytes, name)
            self.assertIn(icon.encode(), template_bytes, name)
            self.assertIn(name, self.templates)
            node_attrs = self.attrs(self.templates[name])
            self.assertEqual(node_attrs['ParentTemplateId'], parent)
            self.assertEqual(node_attrs['MapKey'], self.fields(name)['RootTemplate'])

    def test_flea_market_summons_all_four_items_and_rhino_shot_consumes_custom_status(self):
        props = self.fields(round6.FLEA_MARKET_SHOUT)['SpellProperties']
        for name, *_ in round6.ITEMS:
            tid = self.fields(name)['RootTemplate']
            self.assertIn(f'SummonInInventory({tid},-1,1,false,false,false)', props)
        rhino_node = self.templates[round6.RHINO_DRINK]
        action_attrs = self.attrs(rhino_node.find('.//node[@id="Attributes"]'))
        self.assertEqual(action_attrs['StatsId'], round6.RHINO_CONSUME_STATUS)
        self.assertEqual(action_attrs['Consume'], 'True')
        self.assertIn(f'ApplyStatus({round6.RHINO_BUFF_STATUS},100,2)',
                      self.fields(round6.RHINO_CONSUME_STATUS)['OnApplyFunctors'])

    def test_progression_grants_for_base_subclass_and_subraces(self):
        expected_grants = [
            (round6.SQUATTER_LIEN, 'HomelessCalifornian', '5'),
            (round6.FLEA_MARKET_SHOUT, 'HomelessCalifornian', '8'),
            (round6.CVS_RECEIPT, 'HomelessCalifornian', '11'),
            (round6.SIDESHOW_DONUT, 'BARTPlatformMenace', '6'),
            (round6.SURFBOARD_CHECK, 'Beachborn', '3'),
            (round6.ZOOM_LAYOFF, 'Siliconite', '3'),
            (round6.SHAKE_AND_BAKE, 'InlandEmperor', '5'),
        ]
        for spell, prog_name, prog_level in expected_grants:
            with self.subTest(spell=spell):
                found = [(p['Name'], p['Level']) for p in self.progs if spell in self.grants(p)]
                self.assertEqual(found, [(prog_name, prog_level)])

    def test_new_street_trades_and_junk_doctrines_are_wired(self):
        trades = self.passive_lists[generator.get_guid('HC_StreetTrade_List')]
        doctrines = self.passive_lists[generator.get_guid('HC_JunkDoctrine_List')]
        for trade in ('HC_StreetTrade_SignSpinner', 'HC_StreetTrade_ServicePitbull'):
            self.assertIn(trade, trades)
            self.assertIn(trade, self.stats)
        for doc in ('HC_JunkDoctrine_Prop65Immunity', 'HC_JunkDoctrine_ShoppingCartDrift'):
            self.assertIn(doc, doctrines)
            self.assertIn(doc, self.stats)

    def test_localization_and_icon_registration(self):
        for spell in EXPECTED_SPELLS:
            self.assertIn(spell, SPELL_ICON_KEYS)
            for field in ('DisplayName', 'Description'):
                handle, ver = self.fields(spell)[field].split(';')
                self.assertEqual(ver, '1')
                self.assertTrue(self.loca[handle].strip(), f'{spell}.{field}')


if __name__ == '__main__':
    unittest.main()
