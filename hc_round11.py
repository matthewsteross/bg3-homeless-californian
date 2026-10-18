"""Round 11: eleven spells, one low-HP passive, two inventory items.
File-level candidate only; every mechanic remains UNVERIFIED in game.
Google Maps uses the explicitly authorized single-target fallback, not teleportation.
The snack applies Poisoned when its three-turn buff ends (including early removal).
The shared posture StackId uses Overwrite and no explicit StackPriority, matching
hc_expansion.py and hc_round8.py's default behavior. No shared file is modified.
Vanilla file:line evidence is collected below from all five extracted layers.

- new entry "Target_ViciousMockery": Shared/Stats/Generated/Data/Spell_Target.txt:6164.
- new entry "Zone_Thunderwave": Shared/Stats/Generated/Data/Spell_Zone.txt:283.
- new entry "Shout_FeyPresence": SharedDev/Stats/Generated/Data/Spell_Shout.txt:4747.
- new entry "Projectile_AcidSplash": Shared/Stats/Generated/Data/Spell_Projectile.txt:1808.
- new entry "Shout_SecondWind": Shared/Stats/Generated/Data/Spell_Shout.txt:2458.
- new entry "ARM_Amulet": Shared/Stats/Generated/Data/Armor.txt:1255.
- new entry "OBJ_Potion_Healing": Shared/Stats/Generated/Data/Object.txt:5435.
- ActionResourceMultiplier(Movement,50,0): Shared/Stats/Generated/Data/Status_BOOST.txt:1601.
- ActionResourceBlock(ReactionActionPoint): Shared/Stats/Generated/Data/Status_BOOST.txt:266.
- AC(3): Shared/Stats/Generated/Data/Status_BOOST.txt:221.
- AC(2): Shared/Stats/Generated/Data/Armor.txt:241.
- Advantage(AllSavingThrows): Shared/Stats/Generated/Data/Passive.txt:1056.
- Initiative(2): SharedDev/Stats/Generated/Data/Passive.txt:3800.
- ActionResource(Movement,3,0): Shared/Stats/Generated/Data/Passive.txt:2065.
- Advantage(Skill,Stealth): Shared/Stats/Generated/Data/Passive.txt:326.
- Advantage(SavingThrow,Constitution): Shared/Stats/Generated/Data/Status_POLYMORPHED.txt:567.
- TemporaryHP(5): Shared/Stats/Generated/Data/Status_BOOST.txt:1708.
- RegainHitPoints(4d4+4): Shared/Stats/Generated/Data/Status_BOOST.txt:7044.
- RemoveStatus(FRIGHTENED): SharedDev/Stats/Generated/Data/Spell_Target.txt:1266.
- ApplyStatus(DAZED,100,2): Shared/Stats/Generated/Data/Spell_Projectile.txt:664.
- ApplyStatus(PRONE,100,1): Shared/Stats/Generated/Data/Spell_Projectile.txt:386.
- ApplyStatus(FRIGHTENED,100,2): Shared/Stats/Generated/Data/Spell_Projectile.txt:315.
- ApplyStatus(BURNING,100,2): Shared/Stats/Generated/Data/Spell_Projectile.txt:2299.
- ApplyStatus(POISONED,100,1): Gustav/Stats/Generated/Data/Spell_Projectile.txt:33.
- DealDamage(3d8,Psychic,Magical): SharedDev/Stats/Generated/Data/Spell_Target.txt:4630.
- DealDamage(3d8,Thunder,Magical): Shared/Stats/Generated/Data/Spell_Projectile.txt:871.
- DealDamage(4d6,Psychic,Magical): Shared/Stats/Generated/Data/Spell_Target.txt:4558.
- DealDamage(2d8,Psychic,Magical): GustavDev/Stats/Generated/Data/Spell_Target.txt:6484.
- DealDamage(3d6,Bludgeoning,Magical): SharedDev/Stats/Generated/Data/Status_BOOST.txt:5948.
- DealDamage(2d8,Fire,Magical): Shared/Stats/Generated/Data/Spell_Projectile.txt:820.
- DealDamage(2d6,Fire,Magical): Shared/Stats/Generated/Data/Spell_Projectile.txt:1755.
- HasHPPercentageLessThan(50,context.Target): Gustav/Stats/Generated/Data/Passive.txt:740.
- BoostContext" "OnDamaged;OnHealed: SharedDev/Stats/Generated/Data/Passive.txt:2724.
- GROUND:CreateSurface(: Shared/Stats/Generated/Data/Spell_Projectile.txt:690.
- SummonInInventory(template,-1,1,false,false,false,...): SharedDev/Stats/Generated/Data/Spell_Target.txt:6362 (first six arguments; optional tail omitted as in round 10).
- OnRemoveFunctors" "ApplyStatus(: Shared/Stats/Generated/Data/Status_BOOST.txt:586.
- Shape" "Cone: Shared/Stats/Generated/Data/Spell_Zone.txt:23.
- Angle" "60: Shared/Stats/Generated/Data/Spell_Zone.txt:85.
- Enemy(): Shared/Stats/Generated/Data/Interrupt.txt:459.
- not Combat(): Shared/Stats/Generated/Data/Passive.txt:2073.
- SavingThrow(Ability.Dexterity,SourceSpellDC()): Shared/Stats/Generated/Data/Spell_Projectile.txt:1154.
- SavingThrow(Ability.Wisdom,SourceSpellDC()): Shared/Stats/Generated/Data/Spell_Projectile.txt:1854.
- SavingThrow(Ability.Constitution,SourceSpellDC()): Shared/Stats/Generated/Data/Spell_Shout.txt:3416.
"""
from pathlib import Path
import xml.etree.ElementTree as ET
from hc_icon_keys import icon_for_spell

CEQA='HC_Target_CEQAEnvironmentalInjunction'
BLOWER='HC_Zone_SaturdayGasLeafBlower'
COAST='HC_Target_CoastalCommissionReview'
REPLY='HC_Shout_ReplyAllWholeCompany'
PLEXI='HC_Shout_WalgreensPlexiglassAisle'
THERAPY='HC_Shout_TherapySettingBoundaries'
MAPS='HC_Target_GoogleMapsIntoTraffic'
SANTA='HC_Shout_SantaAnaEmotionally'
GRIDLOCK='HC_Projectile_405ThanksgivingGridlock'
SUBSTACK='HC_Target_SubstackManifestDestiny'
GLOVE='HC_Shout_GloveBoxCleanout'
PTO='HC_UnlimitedPTOGuiltTrip'
PLATE='HC_ARM_ExpiredTemporaryPlate'
SNACK='HC_OBJ_WarmHorchataChurro'
CONSUME='HC_HORCHATA_CONSUME'
RUSH='HC_HORCHATA_CONSTITUTION'
HALF='HC_R11_MOVEMENT_HALVED'
NO_REACTION='HC_R11_COMMENT_PERIOD'
PLEXI_STATUS='HC_R11_PLEXIGLASS_POSTURE'
THERAPY_STATUS='HC_R11_THERAPY_BOUNDARIES'
TEMP_HP='HC_R11_SANTA_ANA_RESOLVE'
ALL_SPELLS=(CEQA,BLOWER,COAST,REPLY,PLEXI,THERAPY,MAPS,SANTA,GRIDLOCK,SUBSTACK,GLOVE)
ICON_KEYS={name:'Spell_'+key for name,key in zip(ALL_SPELLS,('CEQAEnvironmentalInjunction','SaturdayGasLeafBlower','CoastalCommissionReview','ReplyAllWholeCompany','WalgreensPlexiglassAisle','TherapySettingBoundaries','GoogleMapsIntoTraffic','SantaAnaEmotionally','405ThanksgivingGridlock','SubstackManifestDestiny','GloveBoxCleanout'))}
ITEMS=(
 (PLATE,'Armor','ARM_Amulet','51873c0d-f319-45e6-a6a2-79164cd8f3db','Item_LOOT_GEN_Amulet_Necklace_A_Bronze_A',
  '90-Day Expired Temporary Paper License Plate',
  'Uncommon amulet: +2 Initiative and +3 m movement. Grants advantage on Stealth checks while equipped. Taped inside a tinted rear window since 2019, legally invisible to the Highway Patrol.',
  {'Boosts':'Initiative(2);ActionResource(Movement,3,0);Advantage(Skill,Stealth)'}),
 (SNACK,'Object','OBJ_Potion_Healing','d47006e9-8a51-453d-b200-9e0d42e9bbab','Item_CONS_Potion_Healing_A',
  'Warm Gas-Station Horchata & Day-Old Churro',
  'Consume with a bonus action to regain 4d4+4 Hit Points and remove Frightened. Gain advantage on Constitution saving throws for 3 turns, then become Poisoned for 1 turn when the benefit ends. Dispensed from a machine last sanitized under the action-movie administration.',
  {'UseCosts':'BonusActionPoint:1'}),
)
STATUS_SPECS=(
 (HALF,'Movement Under Review','Movement speed is halved. The detour has requested another detour. Nobody has approved the feet.',{'Boosts':'ActionResourceMultiplier(Movement,50,0)','StatusPropertyFlags':'InitiateCombat'}),
 (NO_REACTION,'Comment Period Open','Cannot take reactions. Public comments must be submitted in triplicate. Interruptions will be reviewed next quarter.',{'Boosts':'ActionResourceBlock(ReactionActionPoint)','StatusPropertyFlags':'InitiateCombat'}),
 (PLEXI_STATUS,'Plexiglass Posture','Gain +3 Armour Class. Replaces other shared defensive postures. The employee with the key is on break.',{'Boosts':'AC(3)','StackId':'HC_CHAIR_BRACED'}),
 (THERAPY_STATUS,'Setting Boundaries','Gain +3 Armour Class. Replaces other shared defensive postures. Your sword is violating my calendar.',{'Boosts':'AC(3)','StackId':'HC_CHAIR_BRACED'}),
 (TEMP_HP,'Santa Ana Resolve','Gain 5 temporary Hit Points. They do not stack with other temporary Hit Points. The forecast has chosen violence.',{'Boosts':'TemporaryHP(5)'}),
 (RUSH,'Horchata Constitution','Advantage on Constitution saving throws for 3 turns. Become Poisoned for 1 turn when this benefit ends, including early removal. The churro has filed a counterclaim.',{'Boosts':'Advantage(SavingThrow,Constitution)','OnRemoveFunctors':'ApplyStatus(POISONED,100,1)'}),
 (CONSUME,'Horchata and Churro','Regain 4d4+4 Hit Points and remove Frightened. Gain Horchata Constitution for 3 turns. There was no date on the dispenser.',{'OnApplyFunctors':f'RegainHitPoints(4d4+4);RemoveStatus(FRIGHTENED);ApplyStatus({RUSH},100,3)','StatusPropertyFlags':'DisableOverhead;DisableCombatlog;DisablePortraitIndicator'}),
)
PASSIVE_DESCRIPTION=('While below 30% of your maximum Hit Points, gain +2 Armour Class. You also have advantage on all saving throws while below that threshold. Take as much time off as you want, provided you die answering Jira tickets.')
GRANTS={
 'base':{4:[PLEXI,GLOVE],5:[BLOWER],6:[THERAPY],7:[CEQA],8:[REPLY],9:[COAST]},
 'subclasses':{'OverpassRiverbedDweller':{6:[GRIDLOCK]},'BARTPlatformMenace':{3:[SUBSTACK]}},
 'existing_list_spells':{'Siliconite_L5':MAPS,'InlandEmperor_L5':SANTA},
 'base_passives':{10:[PTO]},
}


def generate_round11(public_dir,add_loca,get_guid):
    public=Path(public_dir);stats=public/'Stats/Generated/Data';roots=public/'RootTemplates'
    stats.mkdir(parents=True,exist_ok=True);roots.mkdir(parents=True,exist_ok=True)
    def loca(name,title,description):
        return {'DisplayName':add_loca(name+'_Name',title)+';1','Description':add_loca(name+'_Description',description)+';1'}
    def emit(name,kind,fields,donor=None):
        if not name.startswith('HC_'):raise ValueError(name)
        lines=[f'new entry "{name}"',f'type "{kind}"']
        if donor:lines.append(f'using "{donor}"')
        for key,value in fields.items():
            if any(x in value for x in ('"','\n','\r')):raise ValueError(f'Unsafe {name}.{key}')
            lines.append(f'data "{key}" "{value}"')
        return '\n'.join(lines)
    passive=loca(PTO,'Unlimited PTO Guilt Trip',PASSIVE_DESCRIPTION)
    passive.update(Icon='PassiveFeature_Resilient',Properties='Highlighted',BoostContext='OnDamaged;OnHealed',
                   BoostConditions='HasHPPercentageLessThan(30, context.Target)',Boosts='AC(2);Advantage(AllSavingThrows)')
    (stats/'HC_Passives_Round11.txt').write_text(emit(PTO,'PassiveData',passive)+'\n',encoding='utf-8')
    save=ET.Element('save');ET.SubElement(save,'version',major='4',minor='0',revision='9',build='0')
    region=ET.SubElement(save,'region',id='Templates');kids=ET.SubElement(ET.SubElement(region,'node',id='Templates'),'children')
    item_blocks={};summons=[]
    for name,kind,donor,parent,icon,title,description,extra in ITEMS:
        guid=get_guid(name+'_RootTemplate');handles=loca(name,title,description)
        obj=ET.SubElement(kids,'node',id='GameObjects')
        for key,typ,value in [('MapKey','FixedString',guid),('Name','LSString',name),('ParentTemplateId','FixedString',parent),('Stats','FixedString',name),('Type','FixedString','item'),('Icon','FixedString',icon)]:
            ET.SubElement(obj,'attribute',id=key,type=typ,value=value)
        for key,value in handles.items():ET.SubElement(obj,'attribute',id=key,type='TranslatedString',handle=value.split(';')[0],version='1')
        if name==SNACK:
            use=ET.SubElement(ET.SubElement(obj,'children'),'node',id='OnUsePeaceActions')
            action=ET.SubElement(ET.SubElement(use,'children'),'node',id='Action')
            ET.SubElement(action,'attribute',id='ActionType',type='int32',value='7')
            attrs=ET.SubElement(ET.SubElement(action,'children'),'node',id='Attributes')
            for key,typ,value in [('Animation','FixedString','895ce382-397d-4b9a-9e8f-6ee3b1ff3a13'),('Conditions','LSString',''),('Consume','bool','True'),('StatsId','FixedString',CONSUME),('StatusDuration','int32','0')]:
                ET.SubElement(attrs,'attribute',id=key,type=typ,value=value)
        fields={'RootTemplate':guid,'Rarity':'Uncommon','ValueOverride':'0',**extra}
        item_blocks.setdefault(kind,[]).append(emit(name,kind,fields,donor));summons.append(f'SummonInInventory({guid},-1,1,false,false,false)')
    ET.indent(save,space='    ');ET.ElementTree(save).write(roots/'HC_Round11Items.lsf.lsx',encoding='utf-8',xml_declaration=True)
    for kind,blocks in item_blocks.items():(stats/f'HC_{kind}_Round11.txt').write_text('\n\n'.join(blocks)+'\n',encoding='utf-8')
    statuses=[]
    for name,title,description,extra in STATUS_SPECS:
        fields={'StatusType':'BOOST','StackId':name,'StackType':'Overwrite','TickType':'EndTurn','Icon':'Spell_Abjuration_MageArmor',**extra,**loca(name,title,description)}
        statuses.append(emit(name,'StatusData',fields))
    (stats/'HC_Status_Round11.txt').write_text('\n\n'.join(statuses)+'\n',encoding='utf-8')
    specs=[]
    def spell(name,donor,title,description,**overrides):
        specs.append((name,donor,title,description,overrides))
    enemy='Enemy() and not Dead()'
    def save_fields(ability,damage,status='',radius='9'):
        return dict(TargetRadius=radius,TargetConditions=enemy,SpellRoll=f'not SavingThrow(Ability.{ability}, SourceSpellDC())',
                    SpellSuccess=damage+(';' if damage and status else '')+status,
                    SpellFail=damage.replace('DealDamage(','DealDamage((').replace(',',')/2,',1) if damage else '',
                    TooltipAttackSave=ability,DamageType=damage.split(',')[1] if damage else '',TooltipDamageList=damage,TooltipStatusApply=status)
    spell(CEQA,'Target_ViciousMockery','CEQA Environmental Impact Injunction',
          'A creature within 9 m makes a Wisdom save, taking 3d8 Psychic damage and becoming Dazed with movement halved for 2 turns on failure, or half damage without statuses on success. Costs an action and 1 Junk; once per short rest. The 4,000 pages concern the Santa Cruz long-toed salamander; the goblin raid is supported in principle.',
          **save_fields('Wisdom','DealDamage(3d8,Psychic,Magical)',f'ApplyStatus(DAZED,100,2);ApplyStatus({HALF},100,2)'))
    spell(BLOWER,'Zone_Thunderwave','Saturday 7:02 AM Gas Leaf Blower',
          'Enemies in a 9 m cone make a Dexterity save, taking 3d8 Thunder damage and falling Prone with movement halved for 1 turn on failure, or half damage without statuses on success. Costs an action and 1 Junk; once per short rest. The HOA banned drum circles and then licensed this.',
          **save_fields('Dexterity','DealDamage(3d8,Thunder,Magical)',f'ApplyStatus(PRONE,100,1);ApplyStatus({HALF},100,1)'),Shape='Cone',Range='9',Base='3',Angle='60')
    coast=save_fields('Wisdom','',f'ApplyStatus(DAZED,100,2);ApplyStatus({NO_REACTION},100,2)');coast['SpellFail']=f'ApplyStatus({HALF},100,1)'
    spell(COAST,'Target_ViciousMockery','Coastal Commission Review (Comment Period Open)',
          'A creature within 9 m makes a Wisdom save: on failure it is Dazed and cannot take reactions for 2 turns, while success halves its movement for 1 turn. Deals no damage and costs an action and 1 Junk; once per short rest. Your Fireball is conceptually approved for fiscal year 2031.',**coast)
    spell(REPLY,'Shout_FeyPresence','Reply-All With the Whole Company',
          'Enemies within 6 m make a Wisdom save, taking 4d6 Psychic damage and becoming Frightened for 2 turns on failure, or half damage without fear on success. Costs an action and 1 Junk; once per long rest. Fourteen people wrote please remove me and none of them left.',
          **save_fields('Wisdom','DealDamage(4d6,Psychic,Magical)','ApplyStatus(FRIGHTENED,100,2)',radius='0'),AreaRadius='6',Cooldown='OncePerRest')
    spell(PLEXI,'Shout_SecondWind','Walgreens Locked-Deodorant Plexiglass Aisle',
          'Gain +3 Armour Class for 2 turns, replacing other shared defensive postures. Costs a bonus action and 1 Junk; once per short rest. Please press the call button for this $4 stick of Old Spice; nobody is coming.',
          UseCosts='BonusActionPoint:1;HC_Junk:1',TargetConditions='Self()',TargetRadius='0',SpellProperties=f'ApplyStatus(SELF,{PLEXI_STATUS},100,2)')
    spell(THERAPY,'Shout_FeyPresence','In Therapy, Setting Boundaries',
          'Gain +3 Armour Class for 2 turns, replacing other shared defensive postures, while enemies within 3 m make a Wisdom save against 2d8 Psychic damage, halved on success. Costs a bonus action and 2 Junk; once per short rest. I do not have the emotional bandwidth to hold space for your greatsword right now.',
          **save_fields('Wisdom','DealDamage(2d8,Psychic,Magical)',radius='0'),AreaRadius='3',UseCosts='BonusActionPoint:1;HC_Junk:2',SpellProperties=f'ApplyStatus(SELF,{THERAPY_STATUS},100,2)')
    spell(MAPS,'Target_ViciousMockery','Google Maps Walks You Into Traffic',
          'A creature within 9 m makes a Dexterity save, taking 3d6 Bludgeoning damage and falling Prone for 1 turn on failure, or half damage without falling on success. Costs an action and no Junk; once per short rest. Recalculating. You have arrived at the bumper.',
          **save_fields('Dexterity','DealDamage(3d6,Bludgeoning,Magical)','ApplyStatus(PRONE,100,1)'),UseCosts='ActionPoint:1')
    spell(SANTA,'Shout_FeyPresence','Santa Ana, Emotionally',
          'Enemies within 4.5 m make a Constitution save, taking 2d8 Fire damage and Burning for 2 turns on failure, or half damage without Burning on success. Gain 5 temporary Hit Points; costs an action and no Junk, once per short rest. The wind is forty miles an hour and somehow knows your name.',
          **save_fields('Constitution','DealDamage(2d8,Fire,Magical)','ApplyStatus(BURNING,100,2)',radius='0'),AreaRadius='4.5',UseCosts='ActionPoint:1',SpellProperties=f'ApplyStatus(SELF,{TEMP_HP},100,-1)')
    spell(GRIDLOCK,'Projectile_AcidSplash','405 Sepulveda Pass Thanksgiving Gridlock',
          'At a point within 9 m, enemies in a 4.5 m radius make a Dexterity save against 2d6 Fire damage, halved on success. The ground becomes Mud difficult terrain for 3 turns; costs an action and 1 Junk, once per short rest. It is 11 miles to the airport and you will arrive in 2029.',
          **save_fields('Dexterity','DealDamage(2d6,Fire,Magical)'),AreaRadius='4.5',ExplodeRadius='4.5',SpellProperties='GROUND:CreateSurface(4.5,3,Mud)')
    spell(SUBSTACK,'Target_ViciousMockery','Substack Manifest Destiny',
          'A creature within 18 m makes a Wisdom save, taking 3d8 Psychic damage and becoming Frightened for 2 turns on failure, or half damage without fear on success. Costs an action and 1 Junk; once per short rest. Free subscribers get the panic attack; paid founding members get the unhinged footnotes.',
          **save_fields('Wisdom','DealDamage(3d8,Psychic,Magical)','ApplyStatus(FRIGHTENED,100,2)',radius='18'))
    spell(GLOVE,'Shout_SecondWind','Glove Box Cleanout',
          'Outside combat, place an Expired Temporary Paper License Plate amulet and Warm Horchata & Day-Old Churro consumable in your inventory. Costs an action and 1 Junk; once per short rest, and equipment must be equipped separately. Three years of registration slips, one ice scraper, and this.',
          TargetRadius='0',TargetConditions='Self()',RequirementConditions='not Combat()',SpellProperties=';'.join(summons))
    defaults=dict(Level='0',MemoryCost='0',UseCosts='ActionPoint:1;HC_Junk:1',Cooldown='OncePerShortRest',
                  SpellProperties='',SpellRoll='',SpellSuccess='',SpellFail='',SpellContainerID='',ContainerSpells='',
                  RechargeValues='',DescriptionParams='',ExtraDescription='',TooltipUpcastDescription='',TooltipUpcastDescriptionParams='',
                  TooltipDamageList='',TooltipStatusApply='',TooltipAttackSave='',TooltipPermanentWarnings='',TooltipOnSave='',CastTextEvent='Cast')
    blocks=[]
    for name,donor,title,description,extra in specs:
        fields={**defaults,**extra,**loca(name,title,description),'Icon':icon_for_spell(name,'Spell_Evocation_Thunderwave')}
        blocks.append(emit(name,'SpellData',fields,donor))
    (stats/'HC_Spells_Round11.txt').write_text('\n\n'.join(blocks)+'\n',encoding='utf-8')
    import copy
    return copy.deepcopy(GRANTS)

