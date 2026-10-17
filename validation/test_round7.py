"""Round 7 file-level contracts (subclasses L3/L10, subrace L1/L5, base L1/L2/L7/L12)."""
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
import hc_round7 as round7
import validate
from hc_icon_keys import SPELL_ICON_KEYS

EXPECTED_SPELLS = {
    round7.FOIL_BLOWBACK,
    round7.ROID_RAGE,
    round7.EMERGENCY_GATE,
    round7.EXTENSION_TAP,
    round7.BOTOX_FREEZE,
    round7.POLYCULE_CALENDAR,
    round7.ALTIMA_REV,
    round7.SQUEEGEE_SMEAR,
    round7.SERVICE_VEST,
    round7.PISS_JUG,
    round7.GOVERNOR_PHOTO_OP,
}

EXPECTED_STATUSES = {spec[0] for spec in round7.STATUS_SPECS}


class RoundSevenTests(unittest.TestCase):
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
        cls.new = {k: v[0] for k, v in cls.stats.items() if v[0].path.name.endswith('_Round7.txt')}
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

    def test_all_round7_entries_are_unique_prefixed_and_do_not_override_vanilla(self):
        self.assertEqual(set(self.new), EXPECTED_SPELLS | EXPECTED_STATUSES)
        self.assertEqual(len(self.new), 19)
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

    def test_progression_grants_for_base_subclasses_and_subraces(self):
        expected_grants = [
            (round7.SQUEEGEE_SMEAR, 'HomelessCalifornian', '1'),
            (round7.SERVICE_VEST, 'HomelessCalifornian', '2'),
            (round7.PISS_JUG, 'HomelessCalifornian', '7'),
            (round7.GOVERNOR_PHOTO_OP, 'HomelessCalifornian', '12'),
            (round7.FOIL_BLOWBACK, 'TenderloinBiohazard', '3'),
            (round7.ROID_RAGE, 'VeniceBoardwalkBrawler', '10'),
            (round7.EMERGENCY_GATE, 'BARTPlatformMenace', '10'),
            (round7.EXTENSION_TAP, 'OverpassRiverbedDweller', '3'),
            (round7.BOTOX_FREEZE, 'Beachborn', '5'),
            (round7.POLYCULE_CALENDAR, 'Siliconite', '5'),
            (round7.ALTIMA_REV, 'InlandEmperor', '1'),
        ]
        for spell, prog_name, prog_level in expected_grants:
            with self.subTest(spell=spell):
                found = {(p['Name'], p['Level']) for p in self.progs if spell in self.grants(p)}
                self.assertEqual(found, {(prog_name, prog_level)})

    def test_spell_mechanics_and_surfaces(self):
        self.assertIn('ApplyStatus(HC_CONTACT_HIGH_NOD,100,2)', self.fields(round7.FOIL_BLOWBACK)['SpellSuccess'])
        self.assertIn('ApplyStatus(HC_TRENBOLONE_MELTDOWN,100,2)', self.fields(round7.ROID_RAGE)['SpellProperties'])
        self.assertIn('ApplyStatus(SELF,HC_SCOOTER_GETAWAY,100,1)', self.fields(round7.EMERGENCY_GATE)['SpellProperties'])
        self.assertIn('GROUND:CreateSurface(2,2,WaterElectrified)', self.fields(round7.EXTENSION_TAP)['SpellProperties'])
        self.assertIn('ApplyStatus(HC_BOTOX_FACE_FREEZE,100,2)', self.fields(round7.BOTOX_FREEZE)['SpellSuccess'])
        self.assertIn('ApplyStatus(HC_POLYCULE_EXHAUSTION,100,2)', self.fields(round7.POLYCULE_CALENDAR)['SpellSuccess'])
        self.assertIn('ApplyStatus(HC_ALTIMA_TINNITUS,100,2)', self.fields(round7.ALTIMA_REV)['SpellSuccess'])
        self.assertIn('ApplyStatus(BLINDED,100,1)', self.fields(round7.SQUEEGEE_SMEAR)['SpellSuccess'])
        self.assertIn('ApplyStatus(HC_ADA_LAWSUIT_SHIELD,100,2)', self.fields(round7.SERVICE_VEST)['SpellProperties'])
        self.assertIn('GROUND:CreateSurface(3,2,Acid)', self.fields(round7.PISS_JUG)['SpellProperties'])
        self.assertIn('ApplyStatus(FECAL_STENCH,100,2)', self.fields(round7.PISS_JUG)['SpellSuccess'])
        self.assertIn('ApplyStatus(SELF,HC_NAPA_FUNDRAISER_BUFF,100,2)', self.fields(round7.GOVERNOR_PHOTO_OP)['SpellProperties'])

    def test_localization_and_icon_registration(self):
        for spell in EXPECTED_SPELLS:
            self.assertIn(spell, SPELL_ICON_KEYS)
        for name, entry in self.new.items():
            for field in ('DisplayName', 'Description'):
                handle = entry.fields[field].split(';')[0]
                self.assertIn(handle, self.loca, f'{name}.{field}')
                self.assertTrue(self.loca[handle].strip())


if __name__ == '__main__':
    unittest.main()
