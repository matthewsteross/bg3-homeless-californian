"""Round 5 file-level contracts (stereotype & street comedy expansion)."""
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
import hc_round5 as round5
import validate
from hc_icon_keys import SPELL_ICON_KEYS

EXPECTED_SPELLS = {
    round5.LAWNMOWER,
    round5.COPPER_STRIP,
    round5.PROP47_CALC,
    round5.SCOOTER_HIT,
    round5.FOIL_HOTBOX,
    round5.VENICE_BONGOS,
    round5.BART_SEAT,
    round5.PROPANE_BBQ,
    round5.UNHOUSED_LECTURE,
    round5.EREWHON_SMOOTHIE,
}

EXPECTED_STATUSES = {spec[0] for spec in round5.STATUS_SPECS}


class RoundFiveTests(unittest.TestCase):
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
        cls.new = {k: v[0] for k, v in cls.stats.items() if v[0].path.name.endswith('_Round5.txt')}
        cls.loca = {e.get('contentuid'): e.text for e in
                    ET.parse(cls.public / 'Localization/English/HomelessCalifornian.loca.xml').iter('content')}
        cls.progs = [cls.attrs(n) for n in ET.parse(cls.public / 'Progressions/Progressions.lsx')
                     .findall('.//node[@id="Progression"]')]
        cls.lists = {cls.attrs(n)['UUID']: cls.attrs(n)['Spells'].split(';') for n in
                     ET.parse(cls.public / 'Lists/SpellLists.lsx').findall('.//node[@id="SpellList"]')}

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

    def test_all_round5_entries_are_unique_prefixed_and_do_not_override_vanilla(self):
        self.assertEqual(set(self.new), EXPECTED_SPELLS | EXPECTED_STATUSES)
        self.assertEqual(len(self.new), 17)
        for name in self.new:
            self.assertTrue(name.startswith('HC_'))
            self.assertNotIn(name, self.vanilla)
            self.assertEqual(len(self.stats[name]), 1)

    def test_all_donors_exist_in_vanilla_and_none_are_honour_overridden(self):
        honour_names = {name for name, entries in self.vanilla.items()
                        if any('Honour' in e.path.parts for e in entries)}
        for name, entry in self.new.items():
            if entry.using:
                self.assertIn(entry.using, self.vanilla, name)
                self.assertTrue(any(e.type == entry.type for e in self.vanilla[entry.using]), name)
                self.assertNotIn(entry.using, honour_names, name)

    def test_base_subclass_and_racial_progression_grants(self):
        expected_grants = [
            (round5.LAWNMOWER, 'HomelessCalifornian', '6'),
            (round5.COPPER_STRIP, 'HomelessCalifornian', '7'),
            (round5.PROP47_CALC, 'HomelessCalifornian', '9'),
            (round5.SCOOTER_HIT, 'HomelessCalifornian', '10'),
            (round5.FOIL_HOTBOX, 'TenderloinBiohazard', '6'),
            (round5.VENICE_BONGOS, 'VeniceBoardwalkBrawler', '6'),
            (round5.BART_SEAT, 'BARTPlatformMenace', '6'),
            (round5.PROPANE_BBQ, 'OverpassRiverbedDweller', '6'),
            (round5.UNHOUSED_LECTURE, 'Californian', '1'),
            (round5.EREWHON_SMOOTHIE, 'Californian', '1'),
        ]
        for spell, prog_name, prog_level in expected_grants:
            with self.subTest(spell=spell):
                found = [(p['Name'], p['Level']) for p in self.progs if spell in self.grants(p)]
                self.assertEqual(found, [(prog_name, prog_level)])

    def test_spell_mechanics_and_surfaces(self):
        self.assertIn('ApplyStatus(HC_TWEAKER_HYPERFOCUS,100,2)', self.fields(round5.LAWNMOWER)['SpellProperties'])
        self.assertIn('GROUND:CreateSurface(1.5,2,WaterElectrified)', self.fields(round5.COPPER_STRIP)['SpellProperties'])
        self.assertIn('DealDamage(3d8,Lightning,Magical)', self.fields(round5.COPPER_STRIP)['SpellSuccess'])
        self.assertIn('SummonInInventory(' + round5.GOLD_TEMPLATE, self.fields(round5.PROP47_CALC)['SpellProperties'])
        self.assertIn('ApplyStatus(DAZED,100,2)', self.fields(round5.PROP47_CALC)['SpellSuccess'])
        self.assertIn('ApplyStatus(PRONE,100,1)', self.fields(round5.SCOOTER_HIT)['SpellSuccess'])
        self.assertIn('GROUND:CreateSurface(3,2,FogCloud)', self.fields(round5.FOIL_HOTBOX)['SpellProperties'])
        self.assertIn('ApplyStatus(FENT_STUPOR,100,1)', self.fields(round5.FOIL_HOTBOX)['SpellSuccess'])
        self.assertIn('ApplyStatus(PANHANDLING_SHAME,100,2)', self.fields(round5.VENICE_BONGOS)['SpellSuccess'])
        self.assertIn('ApplyStatus(FECAL_STENCH,100,2)', self.fields(round5.BART_SEAT)['SpellSuccess'])
        self.assertIn('GROUND:CreateSurface(2,2,Fire)', self.fields(round5.PROPANE_BBQ)['SpellProperties'])
        self.assertIn('ApplyStatus(HC_CANCELLED_PROBLEMATIC,100,2)', self.fields(round5.UNHOUSED_LECTURE)['SpellSuccess'])
        self.assertIn('ApplyStatus(SELF,HC_EREWHON_GLOW,100,2)', self.fields(round5.EREWHON_SMOOTHIE)['SpellProperties'])

    def test_localization_and_icon_registration(self):
        vanilla_icons = {e.fields.get('Icon') for es in self.vanilla.values() for e in es}
        for name, entry in self.new.items():
            for field in ('DisplayName', 'Description'):
                handle, ver = entry.fields[field].split(';')
                self.assertEqual(ver, '1')
                self.assertTrue(self.loca[handle].strip(), f'{name}.{field}')
            icon = entry.fields['Icon']
            self.assertTrue(icon in vanilla_icons or (ROOT / 'assets/icons' / (icon + '.png')).is_file(), icon)
        for spell in EXPECTED_SPELLS:
            self.assertIn(spell, SPELL_ICON_KEYS)


if __name__ == '__main__':
    unittest.main()
