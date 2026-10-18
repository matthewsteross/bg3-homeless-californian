"""Isolated BART generation, progression attachment and vanilla contracts."""
from pathlib import Path
import re
import shutil
import sys
import tempfile
import unittest
import uuid
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import hc_sub_bart as bart
from hc_subclass_levels import add_empty_subclass_nodes, apply_subclass_passives
from validation import validate


def guid(key):
    return str(uuid.uuid5(uuid.UUID('3fa85f64-5717-4562-b3fc-2c963f66afa6'), key))


def attributes(node):
    return {a.get('id'): a.get('value') for a in node.findall('attribute')}


class BARTTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.tmp.cleanup)
        cls.source = Path(cls.tmp.name) / 'HomelessCalifornian'
        shutil.copytree(ROOT / 'src/HomelessCalifornian', cls.source)
        cls.public = cls.source / 'Public/HomelessCalifornian'
        cls.original = validate.read_stats(cls.source)
        cls.loca = {}

        def add_loca(key, text):
            raw = uuid.uuid5(uuid.NAMESPACE_URL, key).hex
            handle = f'h{raw[:8]}g{raw[8:12]}g{raw[12:16]}g{raw[16:20]}g{raw[20:]}'
            cls.loca[handle] = text
            return handle

        cls.grants = bart.generate_sub_bart(cls.public, add_loca, guid)
        cls.new = {n: entries[0] for n, entries in validate.read_stats(cls.source).items()
                   if entries[0].path.name in ('HC_Passives_SubBART.txt', 'HC_Status_SubBART.txt', 'HC_Spells_SubBART.txt')}
        cls.generated_bytes = {p.name: p.read_bytes() for p in (cls.public / 'Stats/Generated/Data').glob('*_SubBART.txt')}
        cls.second_grants = bart.generate_sub_bart(cls.public, add_loca, guid)
        cls.second_bytes = {p.name: p.read_bytes() for p in (cls.public / 'Stats/Generated/Data').glob('*_SubBART.txt')}
        loca_path = cls.public / 'Localization/English/HomelessCalifornian.loca.xml'
        text = loca_path.read_text(encoding='utf-8')
        additions = ''.join(f'<content contentuid="{h}" version="1">{escape(t)}</content>\n' for h, t in cls.loca.items())
        loca_path.write_text(text.replace('</contentList>', additions + '</contentList>'), encoding='utf-8')
        add_empty_subclass_nodes(cls.public, guid)
        apply_subclass_passives(cls.public, cls.grants['subclass_passives'])
        passive_bytes = (cls.public / 'Progressions/Progressions.lsx').read_bytes()
        apply_subclass_passives(cls.public, cls.grants['subclass_passives'])
        cls.passives_idempotent = passive_bytes == (cls.public / 'Progressions/Progressions.lsx').read_bytes()
        lists_path = cls.public / 'Lists/SpellLists.lsx'
        lists = ET.parse(lists_path)
        parent = lists.find('.//node[@id="root"]/children')
        cls.list_ids = {}
        for name, levels in cls.grants['subclasses'].items():
            for level, spells in levels.items():
                uid = guid(f'Test_SubBART_{name}_{level}')
                cls.list_ids[name, level] = uid
                node = ET.SubElement(parent, 'node', id='SpellList')
                ET.SubElement(node, 'attribute', id='Spells', type='LSString', value=';'.join(spells))
                ET.SubElement(node, 'attribute', id='UUID', type='guid', value=uid)
        lists.write(lists_path, encoding='utf-8', xml_declaration=True)
        path = cls.public / 'Progressions/Progressions.lsx'
        consumed = set()

        def attach(match):
            block = match.group(0)
            a = attributes(ET.fromstring(block))
            key = (a.get('Name'), int(a.get('Level', '0')))
            uid = cls.list_ids.get(key)
            if uid:
                consumed.add(key)
                value = ';'.join(v for v in (a.get('Selectors', ''), f'AddSpells({uid})') if v)
                line = f'<attribute id="Selectors" type="LSString" value="{value}"/>'
                if 'Selectors' in a:
                    block = re.sub(r'<attribute id="Selectors"[^>]*/>', lambda _: line, block, count=1)
                else:
                    block = block.replace('<attribute id="Level"', line + '\n                    <attribute id="Level"', 1)
            return block

        text = re.sub(r'<node id="Progression">(?:(?!<node).)*?</node>', attach, path.read_text(encoding='utf-8'), flags=re.S)
        path.write_text(text, encoding='utf-8')
        cls.consumed = consumed
        cls.progs = [attributes(n) for n in ET.parse(path).findall('.//node[@id="Progression"]')]
        cls.lists = [attributes(n) for n in lists.findall('.//node[@id="SpellList"]')]
        cls.vanilla = validate.read_stats(ROOT / 'temp_race')
        cls.vanilla_text = '\n'.join(e.body for entries in cls.vanilla.values() for e in entries)

    def fields(self, name):
        return self.new[name].fields

    def test_unique_names_and_deterministic_generation(self):
        self.assertEqual(len(self.new), 16)  # 6 spells + 2 helpers + 6 passives + hidden passive + status
        self.assertEqual(self.generated_bytes, self.second_bytes)
        self.assertEqual(self.grants, self.second_grants)
        self.assertFalse(set(self.new) & set(self.original))
        self.assertFalse(set(self.new) & set(self.vanilla))
        all_generated = validate.read_stats(self.source)
        for name in self.new:
            self.assertTrue(name.startswith('HC_'))
            self.assertEqual(len(all_generated[name]), 1)
        for path in ROOT.glob('hc_*.py'):
            if path.name == 'hc_sub_bart.py':
                continue
            text = path.read_text(encoding='utf-8')
            for name in self.new:
                self.assertNotRegex(text, rf'[\x22\x27]{re.escape(name)}[\x22\x27]', str(path))

    def test_donors_types_icons_and_no_honour_override(self):
        icons = {s.fields.get('Icon') for entries in self.vanilla.values() for s in entries}
        for name, stat in self.new.items():
            self.assertIn(stat.fields['Icon'], icons, name)
            seen = set()
            while stat.using:
                self.assertNotIn(stat.using, seen)
                seen.add(stat.using)
                self.assertIn(stat.using, self.vanilla)
                donors = self.vanilla[stat.using]
                self.assertTrue(all(d.type == stat.type for d in donors))
                self.assertTrue(all('Honour' not in d.path.parts for d in donors), stat.using)
                stat = donors[-1]

    def test_grants_exact_levels_and_once_only(self):
        self.assertEqual(self.grants['base'], {})
        self.assertEqual(self.grants['existing_list_spells'], {})
        self.assertEqual(set(self.grants['subclasses']), {bart.SUBCLASS})
        self.assertEqual(set(self.grants['subclass_passives']), {bart.SUBCLASS})
        self.assertEqual(self.consumed, set(self.list_ids))
        self.assertTrue(self.passives_idempotent)
        self.assertEqual(tuple(self.grants['subclasses'][bart.SUBCLASS]), bart.LEVELS)
        for level, spec, passive in zip(bart.LEVELS, bart.SPELL_SPECS, bart.PASSIVE_SPECS):
            self.assertEqual(self.grants['subclasses'][bart.SUBCLASS][level], [spec[0]])
            node = next(p for p in self.progs if p.get('Name') == bart.SUBCLASS and p['Level'] == str(level))
            uid = self.list_ids[bart.SUBCLASS, level]
            self.assertEqual(node['Selectors'].split(';').count(f'AddSpells({uid})'), 1)
            self.assertEqual(sum(n.get('Spells', '').split(';').count(spec[0]) for n in self.lists), 1)
            for name in self.grants['subclass_passives'][bart.SUBCLASS][level]:
                self.assertEqual(self.new[name].type, 'PassiveData')
                self.assertEqual(node['PassivesAdded'].split(';').count(name), 1)
                self.assertEqual(sum(p.get('PassivesAdded', '').split(';').count(name) for p in self.progs), 1)
            self.assertIn(passive[0], node['PassivesAdded'].split(';'))
        self.assertNotIn(bart.ESCAPE, ';'.join(n.get('Spells', '') for n in self.lists))
        self.assertEqual(self.fields(bart.PASSIVE_SPECS[-1][0])['Boosts'], f'UnlockSpell({bart.ESCAPE})')

    def test_descriptions_jokes_and_titles(self):
        source = (ROOT / 'work/sc-bart-flash.md').read_text(encoding='utf-8') + (ROOT / 'work/sc-venice-bart-grok.md').read_text(encoding='utf-8')
        existing_titles = (ROOT / 'work/existing-spell-titles-2026-10-18.txt').read_text(encoding='utf-8').splitlines()
        for spec in bart.SPELL_SPECS + bart.PASSIVE_SPECS:
            name, title, description = (spec[0], spec[2], spec[3]) if len(spec) == 5 else spec[:3]
            self.assertIn(title, source)
            self.assertNotIn(title, existing_titles)
            # Match the complete original joke, including multi-sentence Grok endings.
            line = next(line for line in source.splitlines() if f'| {title} |' in line)
            joke = line.split('|')[4].strip()
            self.assertTrue(description.endswith(joke), name)
        for name, stat in self.new.items():
            description = self.loca[stat.fields['Description'].split(';')[0]]
            self.assertTrue(3 <= len(re.findall(r'\.(?:\s|$)', description)) <= 5, name)
            self.assertNotIn('"', description)
            for field in ('Description', 'DisplayName'):
                self.assertIn(stat.fields[field].split(';')[0], self.loca)

    def test_costs_cooldowns_and_clear_inheritance(self):
        for level, spec in zip(bart.LEVELS, bart.SPELL_SPECS):
            f = self.fields(spec[0])
            junk = int(re.search(r'HC_Junk:(\d+)', f['UseCosts'])[1])
            allowed = {4: {1}, 5: {1}, 7: {1, 2}, 8: {1, 2}, 9: {2}, 11: {2, 3}}
            self.assertIn(junk, allowed[level])
            self.assertRegex(f['UseCosts'], r'^(?:ActionPoint|BonusActionPoint):1;HC_Junk:\d$')
            self.assertIn(f['Cooldown'], ('OncePerShortRest', 'OncePerRest'))
            self.assertEqual(f['Level'], '0')
            for key in ('TooltipUpcastDescription', 'TooltipUpcastDescriptionParams', 'ExtraDescription', 'RechargeValues'):
                self.assertEqual(f[key], '', f'{spec[0]}.{key}')
        self.assertEqual(self.fields(bart.ESCAPE)['UseCosts'], 'BonusActionPoint:1;HC_Junk:2')
        self.assertEqual(self.fields(bart.ESCAPE)['Cooldown'], 'OncePerShortRest')

    def test_mechanics_and_save_branches(self):
        f = self.fields
        self.assertEqual(f(bart.BETWEEN)['SpellProperties'], f'GROUND:CreateExplosion({bart.IMPACT});GROUND:TeleportSource()')
        self.assertEqual(f(bart.IMPACT)['AreaRadius'], '3')
        self.assertEqual(f(bart.IMPACT)['SurfaceType'], 'Sentinel')
        self.assertEqual(f(bart.SCREECH)['Shape'], 'Cone')
        self.assertEqual(f(bart.SCREECH)['Range'], '9')
        self.assertEqual(f(bart.DOORS)['Boosts'], 'ActionResourceBlock(Movement)')
        self.assertEqual(f(bart.TRACK_JUMP)['OriginSpellProperties'], '')
        self.assertEqual(f(bart.TRACK_JUMP)['OriginSpellSuccess'], 'DealDamage(4d8,Lightning,Magical)')
        self.assertEqual(f(bart.TRACK_JUMP)['TargetRadius'], '3')
        self.assertEqual(f(bart.TRACK_JUMP)['AreaRadius'], '18')
        self.assertIn('not Ally()', f(bart.TRACK_JUMP)['OriginTargetConditions'])
        self.assertNotIn('706802ee', f(bart.TRACK_JUMP)['SpellAnimation'])
        self.assertEqual(f(bart.LOCKDOWN)['AmountOfTargets'], '3')
        self.assertNotIn('IsConcentration', f(bart.LOCKDOWN)['SpellFlags'])
        self.assertIn('IgnorePreviouslyPickedEntities', f(bart.LOCKDOWN)['SpellFlags'])
        self.assertEqual(f(bart.LOCKDOWN)['SpellSuccess'], 'ApplyStatus(STUNNED,100,1)')
        for name in (bart.EAR_POP, bart.IMPACT, bart.SCREECH, bart.BACKPACK):
            self.assertIn('not Ally()', f(name)['TargetConditions'])
            self.assertIn('SourceSpellDC()', f(name)['SpellRoll'])
            self.assertIn('ApplyStatus(', f(name)['SpellSuccess'])
            self.assertNotIn('ApplyStatus(', f(name)['SpellFail'])
            self.assertIn('/2', f(name)['SpellFail'])
        self.assertIn('ApplyStatus(SELF,INVISIBILITY,100,1)', f(bart.ESCAPE)['SpellProperties'])
        self.assertIn('ApplyStatus(SELF,DISENGAGE,100,1)', f(bart.ESCAPE)['SpellProperties'])

    def test_boost_and_functor_tokens_have_vanilla_precedent(self):
        norm = lambda t: re.sub(r',\s+', ',', t)
        vanilla = norm(self.vanilla_text)
        for name, stat in self.new.items():
            for token in stat.fields.get('Boosts', '').split(';'):
                if not token:
                    continue
                if token == f'UnlockSpell({bart.ESCAPE})':
                    self.assertIn('UnlockSpell(', vanilla)
                else:
                    self.assertIn(norm(token), vanilla, f'{name}: {token}')
            for key in ('BoostContext', 'BoostConditions'):
                if key in stat.fields:
                    self.assertIn(stat.fields[key], self.vanilla_text)
            for key in ('SpellProperties', 'SpellSuccess', 'SpellFail', 'OriginSpellSuccess', 'OriginSpellFail'):
                for token in stat.fields.get(key, '').split(';'):
                    token = re.sub(r'^(GROUND|SELF):', '', token)
                    if not token:
                        continue
                    func = token.split('(')[0]
                    self.assertIn(func + '(', vanilla, f'{name}: {func}')
                    if token.startswith('ApplyStatus(') and bart.DOORS not in token:
                        self.assertIn(token.replace('SELF,', ''), vanilla)
        for stat in self.new.values():
            self.assertNotIn('patriot', stat.body.lower())

    def test_combined_repo_validator(self):
        errors, counts = validate.validate(self.source, ROOT / 'temp_race')
        self.assertEqual(errors, [], '\n'.join(errors))
        self.assertGreaterEqual(counts['stats'], len(self.new))


if __name__ == '__main__':
    unittest.main()
