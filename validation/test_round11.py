"""Round 11 contracts; generates only into a temporary tree, never calls the shared build."""
from pathlib import Path
import re
import tempfile
import unittest
import xml.etree.ElementTree as ET
from unittest.mock import patch
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'validation'))
import generate_mod as generator
import hc_round11 as r
import validate
from validation.test_round10 import split_top

LAYERS=('Shared','SharedDev','Gustav','GustavDev','Honour')


class RoundElevenTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory();cls.public=Path(cls.tmp.name)/'Public/HomelessCalifornian'
        with patch.dict(generator.LOCA_ENTRIES,{},clear=True):
            cls.grants=r.generate_round11(cls.public,generator.add_loca,generator.get_guid);cls.loca=dict(generator.LOCA_ENTRIES)
        cls.stats=validate.read_stats(cls.public);cls.entries={name:entries[0] for name,entries in cls.stats.items()}
        cls.vanilla=validate.read_stats(ROOT/'temp_race')
        cls.text='\n'.join(p.read_text(encoding='utf-8-sig') for layer in LAYERS for p in (ROOT/'temp_race/Public'/layer/'Stats/Generated/Data').glob('*.txt'))
        cls.norm=lambda s:re.sub(r'\s+','',s)
        cls.corpus=re.sub(r'\s+','',cls.text)
    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()
    def f(self,name):return self.entries[name].fields
    def description(self,name):return self.loca[generator.get_handle(name+'_Description')]

    def test_exact_content_unique_and_no_existing_name_collisions(self):
        expected=set(r.ALL_SPELLS)|{r.PTO,r.PLATE,r.SNACK}|{s[0] for s in r.STATUS_SPECS}
        self.assertEqual(set(self.entries),expected);self.assertEqual(len(r.ALL_SPELLS),11)
        for name in expected:
            self.assertTrue(name.startswith('HC_'));self.assertEqual(len(self.stats[name]),1);self.assertNotIn(name,self.vanilla)
            for path in ROOT.glob('hc_*.py'):
                if path.name!='hc_round11.py':self.assertNotIn(name,path.read_text(encoding='utf-8'),str(path))

    def test_donors_exist_with_right_type_and_no_honour_override(self):
        for name,entry in self.entries.items():
            if entry.using:
                donors=self.vanilla[entry.using]
                self.assertTrue(any(e.type==entry.type for e in donors),name)
                self.assertFalse(any('Honour' in e.path.parts for e in donors),name)

    def test_grants_exact_and_each_spell_once(self):
        self.assertEqual(self.grants,{'base':{4:[r.PLEXI,r.GLOVE],5:[r.BLOWER],6:[r.THERAPY],7:[r.CEQA],8:[r.REPLY],9:[r.COAST]},
            'subclasses':{'OverpassRiverbedDweller':{6:[r.GRIDLOCK]},'BARTPlatformMenace':{3:[r.SUBSTACK]}},
            'existing_list_spells':{'Siliconite_L5':r.MAPS,'InlandEmperor_L5':r.SANTA},'base_passives':{10:[r.PTO]}})
        all_grants=[s for v in self.grants['base'].values() for s in v]+[s for levels in self.grants['subclasses'].values() for spells in levels.values() for s in spells]+list(self.grants['existing_list_spells'].values())
        self.assertEqual(sorted(all_grants),sorted(r.ALL_SPELLS))
        self.grants['base'][4].append('sentinel');self.assertNotIn('sentinel',r.GRANTS['base'][4]);self.grants['base'][4].pop()

    def test_costs_levels_and_cooldowns(self):
        for name in r.ALL_SPELLS:
            self.assertEqual(self.f(name)['Level'],'0')
            expected='BonusActionPoint:1;HC_Junk:2' if name==r.THERAPY else 'BonusActionPoint:1;HC_Junk:1' if name==r.PLEXI else 'ActionPoint:1' if name in (r.MAPS,r.SANTA) else 'ActionPoint:1;HC_Junk:1'
            self.assertEqual(self.f(name)['UseCosts'],expected,name)
            self.assertEqual(self.f(name)['Cooldown'],'OncePerRest' if name==r.REPLY else 'OncePerShortRest')
        self.assertEqual(self.f(r.GLOVE)['RequirementConditions'],'not Combat()')

    def test_save_branches_and_enemy_filters(self):
        for name in set(r.ALL_SPELLS)-{r.PLEXI,r.GLOVE}:
            f=self.f(name);self.assertIn('not SavingThrow(',f['SpellRoll']);self.assertIn('SourceSpellDC()',f['SpellRoll'])
            self.assertIn('Enemy()',f['TargetConditions'])
            for key in ('SpellSuccess','SpellFail'):self.assertNotIn('SELF',f[key])
            if name!=r.COAST:
                self.assertIn('/2',f['SpellFail']);self.assertNotIn('ApplyStatus',f['SpellFail'])
        self.assertEqual(self.f(r.COAST)['SpellFail'],f'ApplyStatus({r.HALF},100,1)')
        self.assertNotIn('DealDamage',';'.join(self.f(r.COAST).values()))

    def test_damage_status_duration_and_ranges(self):
        cases={r.CEQA:('Wisdom','3d8,Psychic','ApplyStatus(DAZED,100,2)'),r.BLOWER:('Dexterity','3d8,Thunder','ApplyStatus(PRONE,100,1)'),r.REPLY:('Wisdom','4d6,Psychic','ApplyStatus(FRIGHTENED,100,2)'),r.THERAPY:('Wisdom','2d8,Psychic',''),r.MAPS:('Dexterity','3d6,Bludgeoning','ApplyStatus(PRONE,100,1)'),r.SANTA:('Constitution','2d8,Fire','ApplyStatus(BURNING,100,2)'),r.GRIDLOCK:('Dexterity','2d6,Fire',''),r.SUBSTACK:('Wisdom','3d8,Psychic','ApplyStatus(FRIGHTENED,100,2)')}
        for name,(ability,damage,status) in cases.items():
            self.assertIn('Ability.'+ability,self.f(name)['SpellRoll']);self.assertIn('DealDamage('+damage+',Magical)',self.f(name)['SpellSuccess']);self.assertIn(status,self.f(name)['SpellSuccess'])
        self.assertEqual(self.f(r.HALF)['Boosts'],'ActionResourceMultiplier(Movement,50,0)')
        self.assertEqual(self.f(r.NO_REACTION)['Boosts'],'ActionResourceBlock(ReactionActionPoint)')
        self.assertEqual(self.f(r.BLOWER)['Shape'],'Cone');self.assertEqual(self.f(r.BLOWER)['Range'],'9');self.assertEqual(self.f(r.BLOWER)['Angle'],'60')
        for name,radius in [(r.REPLY,'6'),(r.THERAPY,'3'),(r.SANTA,'4.5'),(r.GRIDLOCK,'4.5')]:self.assertEqual(self.f(name)['AreaRadius'],radius)
        self.assertEqual(self.f(r.GRIDLOCK)['SpellProperties'],'GROUND:CreateSurface(4.5,3,Mud)')
        self.assertEqual(self.f(r.SUBSTACK)['TargetRadius'],'18')
        self.assertEqual(self.f(r.MAPS)['TargetRadius'],'9');self.assertNotIn('Teleport',';'.join(self.f(r.MAPS).values()))
        self.assertIn('SELF,'+r.TEMP_HP,self.f(r.SANTA)['SpellProperties']);self.assertEqual(self.f(r.TEMP_HP)['Boosts'],'TemporaryHP(5)')

    def test_shared_postures_and_hp_passive(self):
        for status in (r.PLEXI_STATUS,r.THERAPY_STATUS):
            f=self.f(status);self.assertEqual(f['Boosts'],'AC(3)');self.assertEqual(f['StackId'],'HC_CHAIR_BRACED');self.assertEqual(f['StackType'],'Overwrite');self.assertNotIn('StackPriority',f)
        p=self.f(r.PTO);self.assertEqual(p['BoostContext'],'OnDamaged;OnHealed');self.assertEqual(p['BoostConditions'],'HasHPPercentageLessThan(30, context.Target)');self.assertEqual(p['Boosts'],'AC(2);Advantage(AllSavingThrows)')

    def test_item_roots_inventory_summons_and_consumable_action(self):
        nodes=ET.parse(self.public/'RootTemplates/HC_Round11Items.lsf.lsx').findall('.//node[@id="GameObjects"]');self.assertEqual(len(nodes),2)
        for item in r.ITEMS:
            name,kind,donor,parent,icon,*_=item
            obj=next(n for n in nodes if any(a.get('id')=='Stats' and a.get('value')==name for a in n.findall('attribute')))
            a={a.get('id'):a.get('value') for a in obj.findall('attribute')};self.assertEqual(a['ParentTemplateId'],parent)
            self.assertEqual(self.f(name)['RootTemplate'],a['MapKey']);self.assertEqual(self.f(name)['ValueOverride'],'0');self.assertEqual(self.f(name)['Rarity'],'Uncommon')
            self.assertIn(f'SummonInInventory({a["MapKey"]},-1,1,false,false,false)',self.f(r.GLOVE)['SpellProperties'])
            self.assertTrue(any(parent.encode() in (ROOT/'temp_race/Public'/layer/'RootTemplates/_merged.lsf').read_bytes() for layer in ('Shared','SharedDev')))
            if name==r.SNACK:
                attrs={a.get('id'):a.get('value') for a in obj.findall('.//node[@id="Attributes"]/attribute')}
                self.assertEqual(attrs['Consume'],'True');self.assertEqual(attrs['StatsId'],r.CONSUME);self.assertEqual(attrs['StatusDuration'],'0')
        self.assertEqual(self.f(r.SNACK)['UseCosts'],'BonusActionPoint:1')
        self.assertEqual(self.f(r.PLATE)['Boosts'],'Initiative(2);ActionResource(Movement,3,0);Advantage(Skill,Stealth)')
        self.assertEqual(self.f(r.CONSUME)['OnApplyFunctors'],f'RegainHitPoints(4d4+4);RemoveStatus(FRIGHTENED);ApplyStatus({r.RUSH},100,3)')
        self.assertEqual(self.f(r.RUSH)['OnRemoveFunctors'],'ApplyStatus(POISONED,100,1)')

    def test_every_boost_damage_and_external_status_has_precedent(self):
        norm=lambda s:re.sub(r'\s+','',s)
        for name,entry in self.entries.items():
            for boost in split_top(entry.fields.get('Boosts','')):self.assertIn(norm(boost),self.corpus,name+': '+boost)
            for key in ('SpellProperties','SpellSuccess','SpellFail','OnApplyFunctors','OnRemoveFunctors'):
                value=entry.fields.get(key,'')
                for dice,kind in re.findall(r'DealDamage\((?:\()?([0-9]+d[0-9]+)(?:\)/2)?,(\w+),Magical\)',value):self.assertIn(f'DealDamage({dice},{kind},Magical)',self.corpus,name)
                for status,chance,turns in re.findall(r'ApplyStatus\((?:SELF,)?(\w+),(\d+),(-?\d+)\)',value):
                    if not status.startswith('HC_'):self.assertIn(f'ApplyStatus({status},{chance},{turns})',self.corpus,name)
                for function in ('RegainHitPoints','RemoveStatus'):
                    for token in re.findall(function+r'\([^)]*\)',value):self.assertIn(norm(token),self.corpus,name)
        for token in ('CreateSurface(','SummonInInventory(','SavingThrow(Ability.Wisdom,SourceSpellDC())','Enemy()','notCombat()'):
            self.assertIn(token,self.corpus)

    def test_localization_descriptions_icons_and_no_foreign_references(self):
        icon_text='\n'.join(p.read_text(encoding='utf-8-sig') for layer in LAYERS for p in (ROOT/'temp_race/Public'/layer/'GUI').glob('Icons*.lsx'))
        for name,entry in self.entries.items():
            if name in (r.PLATE,r.SNACK):continue
            for key in ('DisplayName','Description'):self.assertIn(entry.fields[key].split(';')[0],self.loca)
        for name in self.entries:
            desc=self.description(name);sentences=re.findall(r'\.(?:\s|$)',desc);self.assertTrue(3<=len(sentences)<=5,(name,desc))
            self.assertNotIn('"',desc)
            self.assertNotIn('patr'+'iot',self.entries[name].body.lower())
        for item in r.ITEMS:self.assertIn(item[4],icon_text)
        for name in r.ALL_SPELLS:self.assertEqual(self.f(name)['Icon'],'Spell_Evocation_Thunderwave')

    def test_repo_validator_on_round11_with_explicit_resource_and_localization_fixture(self):
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp);public=source/'Public/HomelessCalifornian'
            with patch.dict(generator.LOCA_ENTRIES,{},clear=True):
                r.generate_round11(public,generator.add_loca,generator.get_guid)
                loca=ET.Element('contentList')
                for handle,text in generator.LOCA_ENTRIES.items():ET.SubElement(loca,'content',contentuid=handle,version='1').text=text
            ET.ElementTree(loca).write(public/'TestLocalization.lsx',encoding='utf-8')
            fixture=ET.Element('save');node=ET.SubElement(fixture,'node',id='ActionResourceDefinition')
            ET.SubElement(node,'attribute',id='Name',value='HC_Junk')
            ET.SubElement(node,'attribute',id='UUID',value=generator.get_guid('HC_Junk_Resource'))
            passive=ET.SubElement(fixture,'node',id='Progression')
            ET.SubElement(passive,'attribute',id='PassivesAdded',value=r.PTO)
            ET.ElementTree(fixture).write(public/'TestResourceAndPassive.lsx',encoding='utf-8')
            errors,counts=validate.validate(source,ROOT/'temp_race')
            self.assertEqual(errors,[]);self.assertEqual(counts['stats'],len(self.entries))

    def test_generation_is_idempotent_and_does_not_replace_existing_lists(self):
        marker=self.public/'Lists/SpellLists.lsx';marker.parent.mkdir();marker.write_text('existing lists stay here')
        before={p.relative_to(self.public):p.read_bytes() for p in self.public.rglob('*') if p.is_file()}
        with patch.dict(generator.LOCA_ENTRIES,{},clear=True):r.generate_round11(self.public,generator.add_loca,generator.get_guid)
        after={p.relative_to(self.public):p.read_bytes() for p in self.public.rglob('*') if p.is_file()};self.assertEqual(before,after)


if __name__=='__main__':unittest.main()
