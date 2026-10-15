"""Local junk toolkit. Gemini draft, integrated and vanilla-checked by Codex.

Animations and 3D visuals use shipped game data. No custom mesh is implied by
the flavor text. Progression grants are attached by generate_mod.py.
"""
from pathlib import Path
import xml.etree.ElementTree as ET
from hc_icon_keys import icon_for_spell


def generate_expansion(public_dir, add_loca, get_guid):
    public = Path(public_dir)
    stats = public / 'Stats/Generated/Data'
    resources = public / 'ActionResourceDefinitions'
    stats.mkdir(parents=True, exist_ok=True)
    resources.mkdir(parents=True, exist_ok=True)
    save = ET.Element('save')
    ET.SubElement(save, 'version', major='4', minor='8', revision='0', build='10')
    region = ET.SubElement(save, 'region', id='ActionResourceDefinitions')
    children = ET.SubElement(ET.SubElement(region, 'node', id='root'), 'children')
    node = ET.SubElement(children, 'node', id='ActionResourceDefinition')
    for name, text in [
        ('DisplayName', 'Junk'),
        ('Description', 'A small collection of things you will definitely need. Fuels your junk toolkit; replenished on short rest.'),
        ('Error', 'Not enough Junk. The good rubbish has already been spoken for.'),
    ]:
        ET.SubElement(node, 'attribute', id=name, type='TranslatedString',
                      handle=add_loca('HC_Junk_' + name, text), version='1')
    for name, kind, value in [('MaxLevel', 'uint32', '0'), ('Name', 'FixedString', 'HC_Junk'),
                              ('ReplenishType', 'FixedString', 'ShortRest'),
                              ('ShowOnActionResourcePanel', 'bool', 'true'),
                              ('UUID', 'guid', get_guid('HC_Junk_Resource'))]:
        ET.SubElement(node, 'attribute', id=name, type=kind, value=value)
    ET.indent(save, space='    ')
    ET.ElementTree(save).write(resources / 'ActionResourceDefinitions.lsx', encoding='utf-8', xml_declaration=True)

    def emit(name, kind, fields, donor=None):
        lines = [f'new entry "{name}"', f'type "{kind}"']
        if donor:
            lines.append(f'using "{donor}"')
        for key, value in fields.items():
            if '"' in value or '\n' in value:
                raise ValueError(f'Unsafe stat field {name}.{key}')
            lines.append(f'data "{key}" "{value}"')
        return '\n'.join(lines) + '\n'

    def loca(name, title, description):
        return {'DisplayName': add_loca(name + '_Name', title) + ';1',
                'Description': add_loca(name + '_Description', description) + ';1'}

    status_specs = [
        ('HC_CHAIR_BRACED', 'Chair-Braced', '+2 AC, advantage on Strength saves, and immunity to Prone. The chair has passed its own inspection.',
         'AC(2);Advantage(SavingThrow,Strength);StatusImmunity(SG_Prone)', 'Skill_Fighter_SecondWind'),
        ('HC_MOVING_DAY', 'Moving Day Hustle', '+6 m movement and immunity to difficult terrain. The property line is wherever you stop next.',
         'ActionResource(Movement,6,0);StatusImmunity(DIFFICULT_TERRAIN);StatusImmunity(DIFFICULT_TERRAIN_MUD);StatusImmunity(DIFFICULT_TERRAIN_WEB);StatusImmunity(DIFFICULT_TERRAIN_VINES)', 'Spell_Transmutation_Longstrider'),
        ('HC_CHAIR_LEG_READY', 'Heirloom Splinter', 'Unlocks Chair-Leg Shiv. This chair has been in the family since Tuesday.',
         'UnlockSpell(HC_Target_ChairLegShiv)', 'Spell_Transmutation_MagicWeapon'),
        ('HC_TERRITORY_CLAIMED', 'I Was Here First', '+2 AC, advantage on Constitution saves, and immunity to Prone and difficult terrain. You have established residency on this sidewalk.',
         'AC(2);Advantage(SavingThrow,Constitution);StatusImmunity(SG_Prone);StatusImmunity(DIFFICULT_TERRAIN);StatusImmunity(DIFFICULT_TERRAIN_MUD);StatusImmunity(DIFFICULT_TERRAIN_WEB);StatusImmunity(DIFFICULT_TERRAIN_VINES)', 'Skill_Fighter_SecondWind'),
        ('HC_PIGEON_WITNESS', 'Pigeon Witness Protection', 'Paperwork asserts this is an ordinary municipal pigeon. Unlocks Pigeon Lunch Rush.',
         'UnlockSpell(HC_Shout_PigeonLunchRush)', 'Spell_Conjuration_FindFamiliar_Raven'),
        ('HC_DISTRACTED_BY_PIGEONS', 'Lunch Rush Distraction', 'Mobbed by aggressive pigeons squabbling over sidewalk crumbs. Disadvantage on attack rolls and Dexterity saving throws.',
         'Disadvantage(AttackRoll);Disadvantage(SavingThrow,Dexterity)', 'Spell_EverybodyKnowsThisGuy'),
    ]
    status_blocks = []
    status_icon_spells = {
        'HC_CHAIR_BRACED': 'HC_Shout_LoadBearingChair',
        'HC_MOVING_DAY': 'HC_Shout_MovingDay',
        'HC_CHAIR_LEG_READY': 'HC_Target_ChairLegShiv',
        'HC_TERRITORY_CLAIMED': 'HC_Shout_IWasHereFirst',
        'HC_PIGEON_WITNESS': 'HC_Target_PigeonWitnessProtection',
        'HC_DISTRACTED_BY_PIGEONS': 'HC_Shout_PigeonLunchRush',
    }
    for name, title, description, boosts, icon in status_specs:
        icon = icon_for_spell(status_icon_spells[name], icon)
        fields = dict(StatusType='BOOST', StackId=name, StackType='Overwrite', TickType='EndTurn', Icon=icon, Boosts=boosts)
        fields.update(loca(name, title, description))
        status_blocks.append(emit(name, 'StatusData', fields))
    (stats / 'HC_Status_Expansion.txt').write_text('\n'.join(status_blocks), encoding='utf-8')

    spells = []
    def spell(name, donor, title, description, **fields):
        # Clear inherited tooltip facts rather than letting a donor advertise
        # poison, healing, bleeding, spell slots, or a different save.
        data = dict(Level='0', Cooldown='', DescriptionParams='', ExtraDescription='', MemoryCost='0', RechargeValues='',
                    TooltipUpcastDescription='', TooltipUpcastDescriptionParams='',
                    TooltipDamageList='', TooltipStatusApply='', TooltipAttackSave='',
                    TooltipPermanentWarnings='', SpellProperties='', SpellSuccess='', SpellFail='',
                    CastTextEvent='Cast')
        data.update(fields)
        data['Icon'] = icon_for_spell(name, data.get('Icon', ''))
        data.update(loca(name, title, description))
        spells.append(emit(name, 'SpellData', data, donor))

    brick = 'HC_Projectile_EmotionalSupportBrick'
    spell(brick, 'Projectile_SlingPoop', 'Emotional Support Brick',
          'Hurl a beloved brick: 2d6 + Constitution modifier Bludgeoning on a ranged spell hit. A failed Constitution save causes Dazed for 1 turn. You cannot throw this away. You might need it.',
          UseCosts='ActionPoint:1;HC_Junk:1', Icon='Action_Throw',
          Trajectories='d8717ced-7980-43dd-ad91-2107c37c8122,a2424c9b-3d58-5c9a-2f6c-c49031192a6d',
          SpellSuccess='DealDamage(2d6+ConstitutionModifier,Bludgeoning,Magical);IF(Character() and not SavingThrow(Ability.Constitution,SourceSpellDC())):ApplyStatus(DAZED,100,1)',
          TooltipDamageList='DealDamage(2d6+ConstitutionModifier,Bludgeoning)',
          TooltipAttackSave='RangedSpellAttack;Constitution', TooltipStatusApply='ApplyStatus(DAZED,100,1)')

    bags = 'HC_Target_BagOfOtherBags'
    spell(bags, 'Target_Web', 'Bag of Other Bags',
          'Create a 2.5 m web surface for 3 turns. Requires concentration; can trap allies as well as enemies and can burn. Every bag contains another bag. None contains an exit.',
          UseCosts='ActionPoint:1;HC_Junk:1', Icon='Spell_Conjuration_Web', AreaRadius='2.5',
          SpellProperties='GROUND:CreateSurface(2.5,3,Web,true)', TooltipAttackSave='Dexterity')

    chair = 'HC_Shout_LoadBearingChair'
    spell(chair, 'Shout_SecondWind', 'Load-Bearing Lawn Chair',
          'Gain +2 AC, advantage on Strength saves, and immunity to Prone for 2 turns. This folding chair is the only stable institution left.',
          UseCosts='BonusActionPoint:1;HC_Junk:1', Icon='Skill_Fighter_SecondWind',
          SpellProperties='ApplyStatus(HC_CHAIR_BRACED,100,2)', TooltipStatusApply='ApplyStatus(HC_CHAIR_BRACED,100,2)')

    dive = 'HC_Shout_DumpsterDive'
    spell(dive, 'Shout_SecondWind', 'Dumpster Dive',
          'Outside combat, restore 2 Junk up to your maximum and scavenge discarded edible rations (a piece of cheese and a half-eaten apple). Once per short rest. Ownership is a theory you are willing to discuss later.',
          UseCosts='ActionPoint:1', Icon='Spell_Transmutation_Goodberry', Cooldown='OncePerShortRest',
          RequirementConditions='not Combat()',
          SpellProperties='RestoreResource(HC_Junk,2,0);SummonInInventory(06474f97-0dd0-45e6-8db8-5f75009bf336,-1,1,false,false,false);SummonInInventory(2ca3cb11-2271-461a-9096-c425c0bd3b12,-1,1,false,false,false)')

    moving = 'HC_Shout_MovingDay'
    spell(moving, 'Shout_FentLean_End', 'Moving Day',
          'While in Fent Lean, end it for free, gain +6 m movement and difficult-terrain immunity for 1 turn, and scatter a 2.5 m perimeter of discarded rubbish (difficult terrain) for 2 turns where you stood. Once per short rest. Your forwarding address is already incorrect.',
          UseCosts='', Icon='Spell_Transmutation_Longstrider', Cooldown='OncePerShortRest',
          RequirementConditions="HasStatus('FENT_LEAN')",
          SpellProperties='RemoveStatus(FENT_LEAN);ApplyStatus(HC_MOVING_DAY,100,1);GROUND:CreateSurface(2.5,2,Mud)',
          TooltipStatusApply='ApplyStatus(HC_MOVING_DAY,100,1)')

    first = 'HC_Shout_IWasHereFirst'
    spell(first, 'Shout_SecondWind', 'I Was Here First',
          'Stake your claim on this patch of ground for 2 turns. Costs an action and 1 Junk; once per short rest. Gain +2 AC, advantage on Constitution saves, and immunity to Prone, while scattering a 2.5 m perimeter of protective rubbish (difficult terrain) for 2 turns around you. You have lived here for fifteen minutes. That is legal precedence.',
          UseCosts='ActionPoint:1;HC_Junk:1', Icon='Skill_Fighter_SecondWind', Cooldown='OncePerShortRest',
          SpellProperties='ApplyStatus(HC_TERRITORY_CLAIMED,100,2);GROUND:CreateSurface(2.5,2,Mud)',
          TooltipStatusApply='ApplyStatus(HC_TERRITORY_CLAIMED,100,2)')

    bird = 'HC_Target_PigeonWitnessProtection'
    spell(bird, 'Target_FindFamiliar_Raven', 'Pigeon Witness Protection',
          'Summon a raven familiar that can scout, use its normal familiar abilities, and command a Pigeon Lunch Rush to distract enemies. Replaces your existing familiar. Once per short rest. It is visibly a raven; the pigeon paperwork is airtight.',
          UseCosts='ActionPoint:1;HC_Junk:1', Icon='Spell_Conjuration_FindFamiliar_Raven', Cooldown='OncePerShortRest',
          SpellContainerID='', ContainerSpells='', RitualCosts='ActionPoint:1;HC_Junk:1',
          SpellFlags='IsSpell;HasSomaticComponent;HasVerbalComponent;HasHighGroundRangeExtension;CannotTargetCharacter;CannotTargetItems',
          SpellProperties="GROUND:Summon(ecdffa46-80bd-41d2-8a50-4460a2810672,Permanent,,,'FindFamiliarStack',UNSUMMON_ABLE,SHADOWCURSE_SUMMON_CHECK,HC_PIGEON_WITNESS)")

    rush = 'HC_Shout_PigeonLunchRush'
    spell(rush, 'Shout_ArmsOfHadar', 'Pigeon Lunch Rush',
          'The pigeon creates a chaotic flap of oily wings and dropped French fries in a 4 m radius. Enemies who fail a Dexterity saving throw suffer Disadvantage on attack rolls and Dexterity saves for 1 turn. Once per short rest. Someone dropped half a croissant. It is serious.',
          UseCosts='ActionPoint:1', Icon='Spell_EverybodyKnowsThisGuy', Cooldown='OncePerShortRest',
          AreaRadius='4', TargetConditions='Character() and Enemy() and not Dead()',
          SpellRoll='not SavingThrow(Ability.Dexterity, SourceSpellDC())',
          SpellSuccess='ApplyStatus(HC_DISTRACTED_BY_PIGEONS,100,1)',
          SpellFail='ApplyStatus(SAVED_AGAINST_HOSTILE_SPELL,100,0)',
          TooltipStatusApply='ApplyStatus(HC_DISTRACTED_BY_PIGEONS,100,1)',
          TooltipAttackSave='Dexterity')

    furniture = 'HC_Target_HeirloomFurniture'
    spell(furniture, 'Target_BrokenBottleShank', 'Heirloom Furniture',
          'Melee weapon attack: 3d6 + Constitution modifier Bludgeoning. A failed Strength save knocks Prone for 1 turn. A hit readies Chair-Leg Shiv for 2 turns. This chair has been in the family since Tuesday.',
          UseCosts='ActionPoint:1;HC_Junk:1', Icon='Spell_BottleShank', DamageType='Bludgeoning',
          SpellSuccess='DealDamage(3d6+ConstitutionModifier,Bludgeoning);IF(Character() and not SavingThrow(Ability.Strength,SourceSpellDC())):ApplyStatus(PRONE,100,1);ApplyStatus(SELF,HC_CHAIR_LEG_READY,100,2)',
          TooltipDamageList='DealDamage(3d6+ConstitutionModifier,Bludgeoning)', TooltipAttackSave='MeleeWeaponAttack;Strength',
          TooltipStatusApply='ApplyStatus(PRONE,100,1)')

    shiv = 'HC_Target_ChairLegShiv'
    spell(shiv, 'Target_BrokenBottleShank', 'Chair-Leg Shiv',
          'Bonus-action melee weapon attack: 2d6 + Constitution modifier Piercing. Consumes your prepared chair leg, hit or miss. Some assembly was required. Less is required now.',
          UseCosts='BonusActionPoint:1', Icon='Spell_BottleShank', DamageType='Piercing',
          RequirementConditions="HasStatus('HC_CHAIR_LEG_READY')", SpellProperties='RemoveStatus(SELF,HC_CHAIR_LEG_READY)',
          SpellSuccess='DealDamage(2d6+ConstitutionModifier,Piercing)',
          TooltipDamageList='DealDamage(2d6+ConstitutionModifier,Piercing)', TooltipAttackSave='MeleeWeaponAttack')

    swap = 'HC_Target_WrongPlatform'
    spell(swap, 'Target_BenignTransposition_Teleport', 'Wrong Platform',
          'An enemy within 9 m makes a Wisdom save. On failure, swap positions with it. Once per short rest. You wanted the other platform. Everyone does.',
          UseCosts='ActionPoint:1;HC_Junk:1', Icon='Action_BenignTransposition', Cooldown='OncePerShortRest', TargetRadius='9',
          TargetConditions='Character() and Enemy() and not Self() and not Dead()', RequirementConditions='',
          SpellRoll='not SavingThrow(Ability.Wisdom,SourceSpellDC())', SpellSuccess='SwapPlaces()',
          SpellFail='ApplyStatus(SAVED_AGAINST_HOSTILE_SPELL,100,0)', TooltipAttackSave='Wisdom',
          SpellFlags='HasVerbalComponent;HasHighGroundRangeExtension;RangeIgnoreVerticalThreshold;IsHarmful')

    (stats / 'HC_Spells_Expansion.txt').write_text('\n'.join(spells), encoding='utf-8')
    return {'base': {1: [brick, bags, chair], 2: [dive], 7: [moving, first]},
            'subclasses': {'TenderloinBiohazard': {3: [bird]}, 'VeniceBoardwalkBrawler': {3: [furniture]},
                           'BARTPlatformMenace': {6: [swap]}}, 'resource_increases': {1: 3, 5: 2, 9: 2}}
