"""Round 10 additions: 8 Caltrans/Caltrain/rent/farmers-market comedy spells, the Caltrans Safety
Vest (rare light armour + requisition shout + equip passive) and the Rent-Stabilized Grit passive.

Base class: In-N-Out Animal-Style L5, Cone Labyrinth L9, Caltrain Horn L10, Safety Vest requisition L11,
Rent Increase L12, passive Rent-Stabilized Grit L9 (key 'base_passives').
Subclasses: Venice L6 (Pool-Hours Sign), BART L10 (Street-Sweep Citation).
Subrace lists: Beachborn L3 (Farmers' Market Peach Denial), Siliconite L1 (Oat-Milk Line).

Local development candidate; NOT gameplay-tested.

Vanilla evidence (extracted data under temp_race/Public; none of the donors is overridden in Honour):
- Spell donors: Target_ViciousMockery (Cone Labyrinth, Caltrain, Rent Increase, Pool Hours, Peach Denial, Oat-Milk),
  Target_ShockingGrasp (Street-Sweep melee spell attack, exactly like round 9's Trust Fall), Shout_SecondWind
  (In-N-Out heal; Safety Vest requisition, the Goodberry-style SummonInInventory shout of hc_outfit / hc_round6).
- Item donor: ARM_StuddedLeather_Body (Shared/Stats/Generated/Data/Armor.txt:46-58): ArmorClass 12, ArmorType
  StuddedLeather, "Armor Class Ability" Dexterity, "Proficiency Group" LightArmor, RootTemplate
  19451420-13f6-444c-a15b-7abb6dde3f91 (present in Shared/RootTemplates/_merged.lsf). Rare light armour that adds
  a small Boosts line on top of the donor: ARM_StuddedLeather_Body_Drow (Armor.txt:~505, Rarity Rare,
  Boosts "Skill(Stealth,1)"). Skill(Deception,1): GustavDev/Stats/Generated/Data/Armor.txt:101.
  Equip passives are plain PassiveData with DisplayName/Description/Boosts: ARM_SuperiorPadding_1_Passive
  (SharedDev/.../Passive.txt:3750), ARM_Ambusher_1_Passive (3789). Icon Item_ARM_StuddedLeather is in
  Shared/GUI/Icons_Items.lsx:533.
- Passive Rent-Stabilized Grit: the HP-gated passive shape is MAG_LowHP_IncreaseSpeed_Passive
  (Gustav/Stats/Generated/Data/Passive.txt:734-741): BoostContext "OnDamaged;OnHealed", BoostConditions
  "HasHPPercentageLessThan(50, context.Target)". Boost tokens: AC(2) (Gustav/Stats/Generated/Data/Status_BOOST.txt:259),
  StatusImmunity(SG_Prone) (Gustav/.../Status_INCAPACITATED.txt:189 and 17 other hits), Advantage(SavingThrow,Strength)
  (GustavDev/Stats/Generated/Data/Passive.txt:515). Vanilla has NO token for "advantage on saves
  against being moved", so the passive grants advantage on Strength saving throws, the save most shoves use.
- Functors: DealDamage(2d8,Bludgeoning,Magical), DealDamage(3d8,Thunder,Magical), DealDamage(3d8,Psychic,Magical),
  DealDamage(2d8,Psychic,Magical), DealDamage(2d6,Psychic,Magical), DealDamage(2d6,Bludgeoning,Magical),
  DealDamage(1d6,Slashing,Magical), RegainHitPoints(1d8+ConstitutionModifier) (also used verbatim by round 9).
  DealDamage(1d8,Slashing,Magical) does NOT occur in vanilla, so Street-Sweep deals 1d6 Slashing.
- Statuses applied: DAZED 1 turn, FRIGHTENED 2 turns, PRONE 1 turn (all verbatim vanilla ApplyStatus forms).
- Custom status boosts: ActionResource(Movement,3,0), Advantage(AttackRoll), Disadvantage(AttackRoll),
  Disadvantage(SavingThrow,Dexterity) (27 hits).
- Saves: SavingThrow(Ability.X, SourceSpellDC()); melee spell attack via Attack(AttackType.MeleeSpellAttack).
"""
from pathlib import Path
import xml.etree.ElementTree as ET
from hc_icon_keys import icon_for_spell

# Spells
CONE_LABYRINTH = 'HC_Target_CaltransConeLabyrinth'            # Base L9
IN_N_OUT = 'HC_Shout_InNOutAnimalStyleArgument'               # Base L5
CALTRAIN_HORN = 'HC_Target_CaltrainHornGradeCrossing'         # Base L10
RENT_INCREASE = 'HC_Target_SixtyDayRentIncrease'              # Base L12
VEST_SHOUT = 'HC_Shout_CaltransVestRequisition'               # Base L11
STREET_SWEEP = 'HC_Target_StreetSweepCitation'                # BART L10
POOL_HOURS = 'HC_Target_LaminatedPoolHoursSign'               # Venice L6
PEACH_DENIAL = 'HC_Target_FarmersMarketPeachDenial'           # Beachborn L3
OAT_MILK = 'HC_Target_OatMilkLineTaqueria'                    # Siliconite L1

# Item and passives
VEST_ARMOR = 'HC_ARM_CaltransSafetyVest'
VEST_PASSIVE = 'HC_HiVisAuthority'
GRIT_PASSIVE = 'HC_RentStabilizedGrit'

VEST_PARENT_STAT = 'ARM_StuddedLeather_Body'
VEST_PARENT_TEMPLATE = '19451420-13f6-444c-a15b-7abb6dde3f91'
VEST_ICON = 'Item_ARM_StuddedLeather'
VEST_TITLE = 'Caltrans Safety Vest'
VEST_DESCRIPTION = (
    'Rare light armour: Armour Class 12 plus your Dexterity modifier, and +1 to Deception checks. '
    'Equipping it grants Hi-Vis Authority: advantage on Intimidation checks and disadvantage on Stealth checks. '
    'It is plain studded leather that has been called a safety vest in front of every clipboard in range. '
    'Nobody questions the person in the vest, and nobody can miss them either.')

STATUS_SPECS = [
    ('HC_DETOUR_DASH', CONE_LABYRINTH, 'Spell_Evocation_Thunderwave',
     'Detour Dash',
     '+3 m movement speed. You know the way out of the cones, because you built them.',
     dict(Boosts='ActionResource(Movement,3,0)')),
    ('HC_ANIMAL_STYLE_ENERGY', IN_N_OUT, 'Spell_Abjuration_MageArmor',
     'Animal-Style Energy',
     'Advantage on attack rolls. Grilled onions, extra spread and a belief that the cashier is wrong.',
     dict(Boosts='Advantage(AttackRoll)')),
    ('HC_CITATION_FILED', STREET_SWEEP, 'Spell_Enchantment_Bane',
     'Citation Filed at 2:01',
     'Disadvantage on Dexterity saving throws. The ticket is $97, the appeal is $40 and the form is in a drawer.',
     dict(Boosts='Disadvantage(SavingThrow,Dexterity)', StatusPropertyFlags='InitiateCombat')),
    ('HC_VALIDATION_SPRINT', PEACH_DENIAL, 'Action_PushingAttack_Melee',
     'Validation Sprint',
     '+3 m movement speed. You left the lot at the speed of a person who just won an argument about a peach.',
     dict(Boosts='ActionResource(Movement,3,0)')),
    ('HC_OATMILK_LINE_STUCK', OAT_MILK, 'Spell_Enchantment_Bane',
     'Stuck in the Oat-Milk Line',
     'Disadvantage on attack rolls. Eleven people are ahead of you and all of them are ordering for a group.',
     dict(Boosts='Disadvantage(AttackRoll)', StatusPropertyFlags='InitiateCombat')),
]

PASSIVE_SPECS = [
    # name, title, description, icon, extra fields
    (GRIT_PASSIVE, 'Rent-Stabilized Grit',
     'While you are below 50% of your maximum Hit Points you gain +2 Armour Class, immunity to being knocked Prone, '
     'and advantage on Strength saving throws. '
     'The landlord can raise the rent, but this unit is still yours and so is the floor.',
     'PassiveFeature_Resilient',
     dict(Properties='Highlighted', BoostContext='OnDamaged;OnHealed',
          BoostConditions='HasHPPercentageLessThan(50, context.Target)',
          Boosts='AC(2);StatusImmunity(SG_Prone);Advantage(SavingThrow,Strength)')),
    (VEST_PASSIVE, 'Hi-Vis Authority',
     'Advantage on Intimidation checks and disadvantage on Stealth checks. '
     'Nobody argues with the vest, and nobody loses sight of it.',
     'PassiveFeature_Resilient',
     dict(Boosts='Advantage(Skill,Intimidation);Disadvantage(Skill,Stealth)')),
]


def generate_round10(public_dir, add_loca, get_guid):
    public = Path(public_dir)
    stats = public / 'Stats/Generated/Data'
    roots = public / 'RootTemplates'
    stats.mkdir(parents=True, exist_ok=True)
    roots.mkdir(parents=True, exist_ok=True)

    def check(name, fields):
        if not name.startswith('HC_'):
            raise ValueError(f'Stat must start with HC_: {name}')
        for key, value in fields.items():
            if '"' in value or '\n' in value or '\r' in value:
                raise ValueError(f'Unsafe field {name}.{key}')

    # ------------------------------------------------------------------ passives
    passive_blocks = []
    for name, title, description, icon, extra in PASSIVE_SPECS:
        fields = {}
        fields['DisplayName'] = add_loca(name + '_Name', title) + ';1'
        fields['Description'] = add_loca(name + '_Description', description) + ';1'
        fields['Icon'] = icon
        fields.update(extra)
        check(name, fields)
        lines = [f'new entry "{name}"', 'type "PassiveData"']
        lines += [f'data "{k}" "{v}"' for k, v in fields.items()]
        passive_blocks.append('\n'.join(lines))
    (stats / 'HC_Passives_Round10.txt').write_text('\n\n'.join(passive_blocks) + '\n', encoding='utf-8')

    # ---------------------------------------------------------------------- item
    template_id = get_guid(VEST_ARMOR + '_RootTemplate')
    title_handle = add_loca(VEST_ARMOR + '_Name', VEST_TITLE)
    description_handle = add_loca(VEST_ARMOR + '_Description', VEST_DESCRIPTION)
    save = ET.Element('save')
    ET.SubElement(save, 'version', major='4', minor='0', revision='9', build='0')
    region = ET.SubElement(save, 'region', id='Templates')
    templates = ET.SubElement(region, 'node', id='Templates')
    children = ET.SubElement(templates, 'children')
    obj = ET.SubElement(children, 'node', id='GameObjects')
    for attr, attr_type, value in (
        ('MapKey', 'FixedString', template_id),
        ('Name', 'LSString', VEST_ARMOR),
        ('ParentTemplateId', 'FixedString', VEST_PARENT_TEMPLATE),
        ('Stats', 'FixedString', VEST_ARMOR),
        ('Type', 'FixedString', 'item'),
        ('Icon', 'FixedString', VEST_ICON),
    ):
        ET.SubElement(obj, 'attribute', id=attr, type=attr_type, value=value)
    for attr, handle in (('DisplayName', title_handle), ('Description', description_handle)):
        ET.SubElement(obj, 'attribute', id=attr, type='TranslatedString', handle=handle, version='1')
    ET.indent(save, space='    ')
    ET.ElementTree(save).write(roots / 'HC_Round10Items.lsf.lsx', encoding='utf-8', xml_declaration=True)
    (stats / 'HC_Armor_Round10.txt').write_text(
        f'new entry "{VEST_ARMOR}"\n'
        'type "Armor"\n'
        f'using "{VEST_PARENT_STAT}"\n'
        f'data "RootTemplate" "{template_id}"\n'
        'data "Rarity" "Rare"\n'
        'data "ValueOverride" "0"\n'
        'data "Boosts" "Skill(Deception,1)"\n'
        f'data "PassivesOnEquip" "{VEST_PASSIVE}"\n', encoding='utf-8')
    summon = f'SummonInInventory({template_id},-1,1,false,false,false)'

    # ---------------------------------------------------------------- statuses
    status_blocks = []
    for name, icon_spell, fallback_icon, title, description, extra in STATUS_SPECS:
        fields = dict(
            StatusType='BOOST',
            StackId=name,
            StackType='Overwrite',
            TickType='EndTurn',
            Icon=icon_for_spell(icon_spell, fallback_icon),
        )
        fields.update(extra)
        fields['DisplayName'] = add_loca(name + '_Name', title) + ';1'
        fields['Description'] = add_loca(name + '_Description', description) + ';1'
        check(name, fields)
        lines = [f'new entry "{name}"', 'type "StatusData"']
        lines += [f'data "{k}" "{v}"' for k, v in fields.items()]
        status_blocks.append('\n'.join(lines))
    (stats / 'HC_Status_Round10.txt').write_text('\n\n'.join(status_blocks) + '\n', encoding='utf-8')

    # ------------------------------------------------------------------ spells
    base_fields = dict(
        Level='0', Cooldown='OncePerShortRest', DescriptionParams='', ExtraDescription='',
        MemoryCost='0', RechargeValues='', TooltipUpcastDescription='',
        TooltipUpcastDescriptionParams='', TooltipDamageList='', TooltipStatusApply='',
        TooltipAttackSave='', TooltipPermanentWarnings='', TooltipOnSave='',
        SpellProperties='', SpellRoll='', SpellSuccess='', SpellFail='',
        CastTextEvent='Cast',
    )
    dex_save = 'not SavingThrow(Ability.Dexterity, SourceSpellDC())'
    con_save = 'not SavingThrow(Ability.Constitution, SourceSpellDC())'
    wis_save = 'not SavingThrow(Ability.Wisdom, SourceSpellDC())'
    wis_fear = 'not SavingThrow(Ability.Wisdom, SourceSpellDC(), AdvantageOnFrightened(), DisadvantageOnFrightened())'
    hostile = 'Character() and not Ally() and not Dead()'

    spell_specs = [
        # ------------------------------------------------------------- base class
        (IN_N_OUT, 'Shout_SecondWind', 'Spell_Transmutation_Goodberry',
         'In-N-Out Animal-Style Argument',
         'Order off the secret menu, argue about the spread and eat standing up like a champion. '
         'Costs a bonus action and 1 Junk; once per short rest. Regain 1d8 + Constitution modifier Hit Points and gain '
         'Animal-Style Energy (advantage on attack rolls) for 2 turns. '
         'No tomato, extra onions, and a grievance with the cashier.',
         dict(UseCosts='BonusActionPoint:1;HC_Junk:1', TargetConditions='Self()',
              SpellProperties='RegainHitPoints(1d8+ConstitutionModifier);ApplyStatus(SELF,HC_ANIMAL_STYLE_ENERGY,100,2)',
              TooltipDamageList='RegainHitPoints(1d8+ConstitutionModifier)',
              TooltipStatusApply='ApplyStatus(HC_ANIMAL_STYLE_ENERGY,100,2)')),

        (CONE_LABYRINTH, 'Target_ViciousMockery', 'Spell_Conjuration_Grease',
         'Caltrans Cone Labyrinth',
         'Drop a spiral of orange cones around a target and let the detour begin. '
         'Costs an action and 1 Junk; once per short rest. A target within 9 m makes a Dexterity saving throw: on a failure it takes '
         '2d8 Bludgeoning damage and falls Prone for 1 turn, or takes half damage on a success, and whether or not it lands you gain '
         'Detour Dash (+3 m movement) for 1 turn. '
         'The detour ends at the detour, which is more cones.',
         dict(UseCosts='ActionPoint:1;HC_Junk:1', TargetRadius='9', DamageType='Bludgeoning',
              TargetConditions=hostile,
              SpellProperties='ApplyStatus(SELF,HC_DETOUR_DASH,100,1)',
              SpellRoll=dex_save,
              SpellSuccess='DealDamage(2d8,Bludgeoning,Magical);ApplyStatus(PRONE,100,1)',
              SpellFail='DealDamage((2d8)/2,Bludgeoning,Magical)',
              TooltipDamageList='DealDamage(2d8,Bludgeoning)',
              TooltipAttackSave='Dexterity',
              TooltipStatusApply='ApplyStatus(PRONE,100,1);ApplyStatus(HC_DETOUR_DASH,100,1)')),

        (CALTRAIN_HORN, 'Target_ViciousMockery', 'Spell_Evocation_Thunderwave',
         'Caltrain Horn at the Grade Crossing',
         'Lean on a locomotive horn at a crossing where the gate has been down since breakfast. '
         'Costs an action and 1 Junk; once per long rest. A target within 12 m makes a Constitution saving throw: on a failure it takes '
         '3d8 Thunder damage and is Dazed for 1 turn, or takes half damage on a success. '
         'The gate is down. The gate has a schedule and a mood.',
         dict(UseCosts='ActionPoint:1;HC_Junk:1', Cooldown='OncePerRest', TargetRadius='12', DamageType='Thunder',
              TargetConditions=hostile,
              SpellRoll=con_save,
              SpellSuccess='DealDamage(3d8,Thunder,Magical);ApplyStatus(DAZED,100,1)',
              SpellFail='DealDamage((3d8)/2,Thunder,Magical)',
              TooltipDamageList='DealDamage(3d8,Thunder)',
              TooltipAttackSave='Constitution',
              TooltipStatusApply='ApplyStatus(DAZED,100,1)')),

        (RENT_INCREASE, 'Target_ViciousMockery', 'Spell_Enchantment_Bane',
         'Sixty-Day Rent Increase Notice',
         'Tape a sixty-day rent increase over the fridge list and let the number do the work. '
         'Costs an action and 1 Junk; once per long rest. A target within 9 m makes a Wisdom saving throw: on a failure it takes '
         '3d8 Psychic damage and is Frightened for 2 turns, or takes half damage on a success. '
         'Market rate is a place, and you do not live there anymore.',
         dict(UseCosts='ActionPoint:1;HC_Junk:1', Cooldown='OncePerRest', TargetRadius='9', DamageType='Psychic',
              TargetConditions=hostile,
              SpellRoll=wis_fear,
              SpellSuccess='DealDamage(3d8,Psychic,Magical);ApplyStatus(FRIGHTENED,100,2)',
              SpellFail='DealDamage((3d8)/2,Psychic,Magical)',
              TooltipDamageList='DealDamage(3d8,Psychic)',
              TooltipAttackSave='Wisdom',
              TooltipStatusApply='ApplyStatus(FRIGHTENED,100,2)')),

        (VEST_SHOUT, 'Shout_SecondWind', 'Spell_Transmutation_Goodberry',
         'Caltrans Truck-Bed Vest Requisition',
         'Lift a Caltrans Safety Vest from the back of a parked utility truck. '
         'Costs an action; once per long rest. Places a Caltrans Safety Vest (rare light armour) in your inventory; equip it yourself. '
         'Nobody questions a person in orange, and you are about to find out how far that goes.',
         dict(UseCosts='ActionPoint:1', Cooldown='OncePerRest', TargetConditions='Self()',
              SpellFlags='IgnoreSilence;UnavailableInDialogs', TargetRadius='0',
              SpellProperties=summon)),

        # --------------------------------------------------------------- subclasses
        (POOL_HOURS, 'Target_ViciousMockery', 'Spell_Enchantment_Bane',
         'Laminated Pool-Hours Sign',
         'Zip-tie a laminated sign to a locked pool gate and read the hours out loud. '
         'Costs an action and 1 Junk; once per short rest. A target within 9 m makes a Wisdom saving throw: on a failure it takes '
         '2d6 Psychic damage and is Dazed for 1 turn, or takes half damage on a success. '
         'Hours are 10 to 4, it is 4:01, and the laminate does not negotiate.',
         dict(UseCosts='ActionPoint:1;HC_Junk:1', TargetRadius='9', DamageType='Psychic',
              TargetConditions=hostile,
              SpellRoll=wis_save,
              SpellSuccess='DealDamage(2d6,Psychic,Magical);ApplyStatus(DAZED,100,1)',
              SpellFail='DealDamage((2d6)/2,Psychic,Magical)',
              TooltipDamageList='DealDamage(2d6,Psychic)',
              TooltipAttackSave='Wisdom',
              TooltipStatusApply='ApplyStatus(DAZED,100,1)')),

        (STREET_SWEEP, 'Target_ShockingGrasp', 'Spell_Evocation_ShockingGrasp',
         'Street-Sweep Citation at 2:01',
         'Slip a citation under the target\'s wiper one minute after the sweeper left. '
         'Costs an action and 1 Junk; once per short rest. Melee spell attack within 1.5 m: deals 1d6 Slashing plus 2d8 Psychic damage '
         'and files a citation against the target (disadvantage on Dexterity saving throws) for 2 turns. '
         'The sweeper came at 2:00. The city is proud.',
         dict(UseCosts='ActionPoint:1;HC_Junk:1', TargetRadius='1.5', DamageType='Slashing',
              TargetConditions=hostile,
              SpellRoll='Attack(AttackType.MeleeSpellAttack)',
              SpellSuccess='DealDamage(1d6,Slashing,Magical);DealDamage(2d8,Psychic,Magical);ApplyStatus(HC_CITATION_FILED,100,2)',
              TooltipDamageList='DealDamage(1d6,Slashing);DealDamage(2d8,Psychic)',
              TooltipAttackSave='MeleeSpellAttack',
              TooltipStatusApply='ApplyStatus(HC_CITATION_FILED,100,2)')),

        # --------------------------------------------------------------- subraces
        (PEACH_DENIAL, 'Target_ViciousMockery', 'Action_PushingAttack_Melee',
         "Farmers' Market Peach Parking Denial",
         "Deny a parking validation over one peach and watch the attendant's whole world tip over. "
         'Costs a bonus action; once per short rest. A target within 9 m makes a Dexterity saving throw: on a failure it takes '
         '2d6 Bludgeoning damage and falls Prone for 1 turn, or takes half damage on a success, and whether or not it lands you gain '
         'Validation Sprint (+3 m movement) for 1 turn. '
         'Validation is for vendors, and you bought one peach.',
         dict(UseCosts='BonusActionPoint:1', TargetRadius='9', DamageType='Bludgeoning',
              TargetConditions=hostile,
              SpellProperties='ApplyStatus(SELF,HC_VALIDATION_SPRINT,100,1)',
              SpellRoll=dex_save,
              SpellSuccess='DealDamage(2d6,Bludgeoning,Magical);ApplyStatus(PRONE,100,1)',
              SpellFail='DealDamage((2d6)/2,Bludgeoning,Magical)',
              TooltipDamageList='DealDamage(2d6,Bludgeoning)',
              TooltipAttackSave='Dexterity',
              TooltipStatusApply='ApplyStatus(PRONE,100,1);ApplyStatus(HC_VALIDATION_SPRINT,100,1)')),

        (OAT_MILK, 'Target_ViciousMockery', 'Spell_Enchantment_Bane',
         'Seven-Dollar Oat-Milk Line',
         'Stretch a seven-dollar oat-milk line across the sidewalk in front of the old taqueria. '
         'Costs an action; once per short rest. A target within 6 m makes a Wisdom saving throw: on a failure it takes '
         '2d8 Psychic damage and is Stuck in the Oat-Milk Line (disadvantage on attack rolls) for 2 turns, or takes half damage on a success. '
         'The line is for lavender cold brew, and the line is also the sidewalk.',
         dict(UseCosts='ActionPoint:1', TargetRadius='6', DamageType='Psychic',
              TargetConditions=hostile,
              SpellRoll=wis_save,
              SpellSuccess='DealDamage(2d8,Psychic,Magical);ApplyStatus(HC_OATMILK_LINE_STUCK,100,2)',
              SpellFail='DealDamage((2d8)/2,Psychic,Magical)',
              TooltipDamageList='DealDamage(2d8,Psychic)',
              TooltipAttackSave='Wisdom',
              TooltipStatusApply='ApplyStatus(HC_OATMILK_LINE_STUCK,100,2)')),
    ]

    spell_blocks = []
    for name, donor, fallback_icon, title, description, overrides in spell_specs:
        fields = dict(base_fields)
        fields.update(overrides)
        fields['Icon'] = icon_for_spell(name, fallback_icon)
        fields['DisplayName'] = add_loca(name + '_Name', title) + ';1'
        fields['Description'] = add_loca(name + '_Description', description) + ';1'
        check(name, fields)
        lines = [f'new entry "{name}"', 'type "SpellData"', f'using "{donor}"']
        lines += [f'data "{k}" "{v}"' for k, v in fields.items()]
        spell_blocks.append('\n'.join(lines))
    (stats / 'HC_Spells_Round10.txt').write_text('\n\n'.join(spell_blocks) + '\n', encoding='utf-8')

    return {
        'base': {
            5: [IN_N_OUT],
            9: [CONE_LABYRINTH],
            10: [CALTRAIN_HORN],
            11: [VEST_SHOUT],
            12: [RENT_INCREASE],
        },
        'subclasses': {
            'VeniceBoardwalkBrawler': {6: [POOL_HOURS]},
            'BARTPlatformMenace': {10: [STREET_SWEEP]},
        },
        'existing_list_spells': {
            'Beachborn_L3': PEACH_DENIAL,
            'Siliconite_L1': OAT_MILK,
        },
        # Extra key (not in the portapotty shape): passives to append to the base class
        # progression PassivesAdded at the given level, e.g. {9: ['HC_RentStabilizedGrit']}.
        'base_passives': {
            9: [GRIT_PASSIVE],
        },
    }
