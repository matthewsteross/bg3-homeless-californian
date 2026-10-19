"""Isolated file-level checks; never run the shared generator or build."""
import re
import sys
import tempfile
import unittest
import uuid
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import hc_sub_others as content
from hc_subclass_levels import add_empty_subclass_nodes, apply_subclass_passives

LAYERS = ('Shared', 'SharedDev', 'Gustav', 'GustavDev', 'Honour')


def parse(text):
    entries = {}
    for body in re.split(r'(?=new entry ")', text):
        match = re.match(r'new entry "([^"]+)"\s+type "([^"]+)"', body)
        if match:
            name, kind = match.groups()
            donor = re.search(r'^using "([^"]+)"', body, re.M)
            entries[name] = (kind, donor[1] if donor else None,
                             dict(re.findall(r'^data "([^"]+)" "([^"]*)"', body, re.M)))
    return entries


class SubOthersTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.public = Path(cls.tmp.name)/'Public/HC'
        cls.loca = {}
        def loca(key, text):
            handle = 'h'+uuid.uuid5(uuid.NAMESPACE_URL, key).hex
            cls.loca[handle] = text
            return handle
        cls.grants = content.generate_sub_others(cls.public, loca,
                                                lambda key: str(uuid.uuid5(uuid.NAMESPACE_URL, key)))
        cls.new = {}
        for path in cls.public.rglob('*.txt'):
            cls.new.update(parse(path.read_text(encoding='utf-8')))
        cls.vanilla = {}
        cls.corpus = ''
        cls.honour = set()
        for layer in LAYERS:
            for path in (ROOT/'temp_race/Public'/layer/'Stats/Generated/Data').glob('*.txt'):
                text = path.read_text(encoding='utf-8-sig')
                entries = parse(text)
                if layer == 'Honour':
                    cls.honour.update(entries)
                cls.vanilla.update(entries)
                cls.corpus += text+'\n'
        cls.normal = re.sub(r',\s+', ',', cls.corpus)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_exact_slots_and_unique_names(self):
        expected_spells = {content.VENICE: (4,7,9), content.TENDERLOIN: (5,8,9), content.OVERPASS: (5,8,9)}
        all_names = []
        self.assertEqual(set(self.grants), {'base','subclasses','existing_list_spells','subclass_passives'})
        self.assertEqual(self.grants['base'], {})
        self.assertEqual(self.grants['existing_list_spells'], {})
        for sub, levels in expected_spells.items():
            self.assertEqual(set(self.grants['subclasses'][sub]), set(levels))
            self.assertEqual(set(self.grants['subclass_passives'][sub]), {4,5,7,8,9,11}-set(levels))
        for category, kind in [('subclasses','SpellData'), ('subclass_passives','PassiveData')]:
            for sub, levels in self.grants[category].items():
                for level, names in levels.items():
                    self.assertEqual(len(names), 1)
                    for name in names:
                        all_names.append(name)
                        self.assertEqual(self.new[name][0], kind)
        self.assertEqual(len(all_names), 18)
        self.assertEqual(len(set(all_names)), 18)
        self.assertEqual(set(all_names), set(self.new))
        for name in all_names:
            self.assertTrue(name.startswith('HC_'))
            self.assertNotIn(name, self.vanilla)
            for path in ROOT.glob('hc_*.py'):
                if path.name != 'hc_sub_others.py' and 'patriot' not in str(path).lower():
                    self.assertNotIn(name, path.read_text(encoding='utf-8-sig'), str(path))

    def test_donors_and_inherited_fields(self):
        for name, (kind, donor, fields) in self.new.items():
            self.assertTrue(fields['Icon'] in self.corpus or fields['Icon'] in __import__('hc_icons_apply').load_map().values(), name)
            if donor:
                self.assertEqual(self.vanilla[donor][0], kind)
                self.assertNotIn(donor, self.honour)
                for field in ('SpellProperties','SpellRoll','SpellSuccess','SpellFail',
                              'TooltipUpcastDescription','RechargeValues','RootSpellID','SpellContainerID'):
                    self.assertIn(field, fields, name)

    def test_boosts_damage_statuses_and_save_tokens(self):
        for name, (kind, donor, fields) in self.new.items():
            for token in fields.get('Boosts', '').split(';'):
                if token:
                    self.assertIn(token, self.normal, name)
            for field in ('SpellSuccess','SpellFail','SpellProperties','SpellRoll'):
                value = re.sub(r',\s+', ',', fields.get(field,''))
                for dice, damage in re.findall(r'DealDamage\(\(?(\d+d\d+)\)?(?:/2)?,(\w+),Magical\)',value):
                    self.assertIn(f'DealDamage({dice},{damage},Magical)',self.normal,name)
                for token in re.findall(r'ApplyStatus\([^()]+\)|Force\([^()]+\)|Attack\([^()]+\)|SavingThrow\(Ability\.\w+,SourceSpellDC\(\)\)', value):
                    self.assertIn(token, self.normal, name)
                for surface in re.findall(r'CreateSurface\([^,]+,[^,]+,(\w+)',value):
                    self.assertRegex(self.normal, r'CreateSurface\([^,]+,[^,]+,'+surface+r'[,)]')
            if fields.get('SurfaceType'):
                self.assertIn('"SurfaceType" "'+fields['SurfaceType']+'"', self.corpus)

    def test_costs_and_signature_mechanics(self):
        for sub, level, name, *rest in content.SPELL_SPECS:
            fields = self.new[name][2]
            self.assertRegex(fields['UseCosts'], r'^(BonusActionPoint|ActionPoint):1;HC_Junk:[12]$')
            self.assertIn('HC_Junk:'+('1' if level <= 5 else '2'),fields['UseCosts'])
            self.assertEqual(fields['Cooldown'], 'OncePerRest' if level == 9 else 'OncePerShortRest')
        miasma = self.new['HC_Target_SteamGrateMiasma'][2]
        self.assertEqual(miasma['AreaRadius'],'6')
        self.assertEqual(miasma['SpellProperties'],'GROUND:CreateSurface(6,3,StinkingCloud,true)')
        self.assertIn('IsConcentration',self.vanilla['Target_StinkingCloud'][2]['SpellFlags'])
        breach = self.new['HC_Zone_SandbagBreach'][2]
        self.assertEqual((breach['Range'],breach['Base'],breach['SurfaceType']),('12','2','Water'))
        self.assertEqual(self.vanilla['Zone_GustOfWind'][2]['Shape'],'Square')

    def test_localization_jokes_and_descriptions(self):
        venice = (ROOT/'work/sc-venice-bart-grok.md').read_text(encoding='utf-8')
        argon = (ROOT/'work/sc-tenderloin-overpass-argon.md').read_text(encoding='utf-8')
        jokes = [line.split(' | ')[4] for line in venice.splitlines() if line.startswith('L')][:6]
        jokes += re.findall(r'\*\*Joke:\*\* \*"(.*?)"\*',argon)
        titles = (ROOT/'work/existing-spell-titles-2026-10-18.txt').read_text(encoding='utf-8').splitlines()
        for name, (kind, donor, fields) in self.new.items():
            title = self.loca[fields['DisplayName'].split(';')[0]]
            desc = self.loca[fields['Description'].split(';')[0]]
            self.assertNotIn(title,titles)
            self.assertTrue(3 <= len(re.findall(r'\.(?:\s|$)',desc)) <= 5,(name,desc))
            self.assertTrue(any(desc.endswith(joke) for joke in jokes),(name,desc))
            self.assertNotIn('patriot',repr((name,fields,desc)).lower())
            self.assertNotIn('"',desc)

    def test_passive_progression_attachment_is_idempotent(self):
        path = self.public/'Progressions/Progressions.lsx'
        path.parent.mkdir(parents=True,exist_ok=True)
        source = ROOT/'src/HomelessCalifornian/Public/HomelessCalifornian/Progressions/Progressions.lsx'
        path.write_bytes(source.read_bytes())
        add_empty_subclass_nodes(self.public,lambda key: str(uuid.uuid5(uuid.NAMESPACE_URL,key)))
        apply_subclass_passives(self.public,self.grants['subclass_passives'])
        first = path.read_bytes()
        apply_subclass_passives(self.public,self.grants['subclass_passives'])
        self.assertEqual(first,path.read_bytes())
        nodes = [{a.get('id'):a.get('value') for a in n.findall('attribute')}
                 for n in ET.fromstring(first).findall('.//node[@id="Progression"]')]
        for sub, levels in self.grants['subclass_passives'].items():
            for level,names in levels.items():
                for name in names:
                    attached = [(n['Name'],int(n['Level'])) for n in nodes
                                for p in n.get('PassivesAdded','').split(';') if p==name]
                    self.assertEqual(attached,[(sub,level)])

    def test_spell_lists_attach_once_at_requested_levels(self):
        # Reproduce the lead's AddSpells list/selector contract in an isolated tree.
        with tempfile.TemporaryDirectory() as tmp:
            public = Path(tmp)
            path = public/'Progressions/Progressions.lsx'
            path.parent.mkdir()
            source = ROOT/'src/HomelessCalifornian/Public/HomelessCalifornian/Progressions/Progressions.lsx'
            path.write_bytes(source.read_bytes())
            add_empty_subclass_nodes(public,lambda key: str(uuid.uuid5(uuid.NAMESPACE_URL,key)))
            tree = ET.parse(path)
            lists = ET.Element('SpellLists')
            expected = {}
            for sub, levels in self.grants['subclasses'].items():
                for level,names in levels.items():
                    uid = str(uuid.uuid5(uuid.NAMESPACE_URL,f'{sub}_{level}_SubOthers'))
                    node = ET.SubElement(lists,'node',id='SpellList')
                    ET.SubElement(node,'attribute',id='UUID',value=uid)
                    ET.SubElement(node,'attribute',id='Spells',value=';'.join(names))
                    expected[uid] = (sub,level,names)
            for node in tree.findall('.//node[@id="Progression"]'):
                attrs = {a.get('id'):a.get('value') for a in node.findall('attribute')}
                for uid,(sub,level,names) in expected.items():
                    if (attrs.get('Name'),attrs.get('Level')) == (sub,str(level)):
                        selector = node.find('attribute[@id="Selectors"]')
                        if selector is None:
                            selector = ET.SubElement(node,'attribute',id='Selectors',type='LSString',value='')
                        selector.set('value',';'.join(filter(None,[selector.get('value'),f'AddSpells({uid})'])))
            for uid,(sub,level,names) in expected.items():
                attached = []
                for node in tree.findall('.//node[@id="Progression"]'):
                    attrs = {a.get('id'):a.get('value') for a in node.findall('attribute')}
                    attached.extend([(attrs['Name'],int(attrs['Level']))]*attrs.get('Selectors','').count(f'AddSpells({uid})'))
                self.assertEqual(attached,[(sub,level)])
                for name in names:
                    self.assertEqual(sum(a.get('value','').split(';').count(name)
                                         for a in lists.findall('.//attribute[@id="Spells"]')),1)
                    self.assertEqual(self.new[name][0],'SpellData')

    def test_vanilla_citations_resolve(self):
        for token, relative, lineno in re.findall(r'^- (.+): (\S+\.txt):(\d+)$',content.__doc__,re.M):
            path = ROOT/'temp_race/Public'/relative
            line = path.read_text(encoding='utf-8-sig').splitlines()[int(lineno)-1]
            self.assertIn(re.sub(r',\s+',',',token),re.sub(r',\s+',',',line))


if __name__ == '__main__':
    unittest.main()
