"""Round 9 additions: 10 grocery/DMV/HOA/tech-bro comedy spells and 3 custom statuses.

Base class L8 (x3) and L12, subclass BART L3 / Tenderloin L12 / Overpass L12,
Siliconite L3, Inland Emperor L3 and Beachborn L1 racial lists.

Local development candidate; NOT gameplay-tested.

Vanilla evidence (extracted data under temp_race/Public, Shared/SharedDev/Gustav/GustavDev layers; none are overridden in Honour):
- Spell donors: Target_ViciousMockery (Costco, DMV, Self-Checkout, Raccoon, PurpleAir, HOA), Zone_Thunderwave (Tech Shuttle,
  Square 9 m x 3 m rectangle exactly like HC_Zone_LimeScooterHitAndRun), Target_ShockingGrasp (Trust Fall, melee spell attack
  exactly like HC_Target_CopperWireStrip), Shout_SecondWind (Prop 13 self shout), Shout_FeyPresence (Nextdoor Enemy() shout).
- Statuses: DAZED, FRIGHTENED, BLINDED and PRONE (vanilla StatusData). Round 9 applies them as ApplyStatus(X,100,1|2) forms that
  all occur verbatim in vanilla (FRIGHTENED 1 and 2 turns, DAZED 1 and 2 turns, BLINDED 1 turn, PRONE 1 turn).
- Functors: DealDamage(2d6,Bludgeoning,Magical), DealDamage(2d8,Psychic,Magical), DealDamage(3d8,Bludgeoning,Magical),
  DealDamage(2d8,Bludgeoning,Magical), DealDamage(2d6,Piercing,Magical), DealDamage(1d8,Poison,Magical),
  DealDamage(2d6,Poison,Magical), RegainHitPoints(1d8+ConstitutionModifier). (DealDamage(2d8,Piercing,Magical) and
  RegainHitPoints(1d6+ConstitutionModifier) do NOT exist in vanilla, so the raccoon tribunal uses 2d6 Piercing + 1d8 Poison
  and Prop 13 heals 1d8 + Constitution modifier.)
- Boosts: ActionResource(Movement,-3,0), AC(2), Advantage(AttackRoll).
- Saves: Strength / Wisdom / Dexterity / Constitution via SavingThrow(Ability.X, SourceSpellDC()); melee spell attack via
  Attack(AttackType.MeleeSpellAttack).
- Prop 13 shares StackId HC_CHAIR_BRACED with the other +2 AC posture statuses (Chair-Braced, Tweaker Hyperfocus, ...).
"""
from pathlib import Path
from hc_icon_keys import icon_for_spell

# Base class
COSTCO_CART = 'HC_Target_CostcoSampleCartSideways'               # L8
DMV_TICKET = 'HC_Target_DMVTicketB047FarWindow'                  # L8
SELF_CHECKOUT = 'HC_Target_SelfCheckoutUnexpectedItem'           # L8
PROP13 = 'HC_Shout_Prop13GrandfatheredSmirk'                     # L12

# Subclasses
TECH_SHUTTLE = 'HC_Zone_DoubleDeckerTechShuttleBikeLane'         # BART L3
RACCOON_TRIBUNAL = 'HC_Target_RaccoonTribunalCompostBins'        # Tenderloin L12
PURPLEAIR = 'HC_Target_PurpleAirWildfireRefresh'                 # Overpass L12

# Race / subrace
TRUST_FALL = 'HC_Target_SeriesBOffsiteTrustFall'                 # Siliconite L3
HOA_BEIGE = 'HC_Target_HOABeigePaintDenial'                      # Inland Emperor L3
NEXTDOOR_COYOTE = 'HC_Shout_NextdoorLostCoyoteThread'            # Beachborn L1

STATUS_SPECS = [
    ('HC_CUBE_DENIED', COSTCO_CART, 'Spell_Enchantment_Bane',
     'Cube-Denied',
     '-3 m movement speed. The sign says one sample per customer and you are still processing what that means.',
     dict(Boosts='ActionResource(Movement,-3,0)', StatusPropertyFlags='InitiateCombat')),
    ('HC_UNEXPECTED_ITEM_LOCKOUT', SELF_CHECKOUT, 'Spell_Enchantment_Bane',
     'Unexpected Item Lockout',
     'Cannot take bonus actions and has disadvantage on attack rolls. Please remove the item and wait for assistance. Assistance is not coming.',
     dict(Boosts='ActionResourceBlock(BonusActionPoint);Disadvantage(AttackRoll)', StatusPropertyFlags='InitiateCombat')),
    ('HC_GRANDFATHERED_IN', PROP13, 'Spell_Abjuration_MageArmor',
     'Grandfathered In',
     '+2 Armour Class. Does not stack with other braced-posture bonuses. Your assessed value froze in 1978 and so did your fear of the county.',
     dict(Boosts='AC(2)', StackId='HC_CHAIR_BRACED')),
    ('HC_OFFSITE_BOUNCE_BACK', TRUST_FALL, 'Spell_Abjuration_MageArmor',
     'Offsite Bounce-Back',
     'Advantage on attack rolls. You have completed a ropes course and are no longer afraid of consequences.',
     dict(Boosts='Advantage(AttackRoll)')),
]


def generate_round9(public_dir, add_loca, get_guid):
    public = Path(public_dir)
    stats = public / 'Stats/Generated/Data'
    stats.mkdir(parents=True, exist_ok=True)

    def check(name, fields):
        if not name.startswith('HC_'):
            raise ValueError(f'Stat must start with HC_: {name}')
        for key, value in fields.items():
            if '"' in value or '\n' in value or '\r' in value:
                raise ValueError(f'Unsafe field {name}.{key}')

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
    (stats / 'HC_Status_Round9.txt').write_text('\n\n'.join(status_blocks) + '\n', encoding='utf-8')

    # ------------------------------------------------------------------ spells
    base_fields = dict(
        Level='0', Cooldown='OncePerShortRest', DescriptionParams='', ExtraDescription='',
        MemoryCost='0', RechargeValues='', TooltipUpcastDescription='',
        TooltipUpcastDescriptionParams='', TooltipDamageList='', TooltipStatusApply='',
        TooltipAttackSave='', TooltipPermanentWarnings='', TooltipOnSave='',
        SpellProperties='', SpellRoll='', SpellSuccess='', SpellFail='',
        CastTextEvent='Cast',
    )
    str_save = 'not SavingThrow(Ability.Strength, SourceSpellDC())'
    dex_save = 'not SavingThrow(Ability.Dexterity, SourceSpellDC())'
    con_save = 'not SavingThrow(Ability.Constitution, SourceSpellDC())'
    wis_save = 'not SavingThrow(Ability.Wisdom, SourceSpellDC())'
    wis_fear = 'not SavingThrow(Ability.Wisdom, SourceSpellDC(), AdvantageOnFrightened(), DisadvantageOnFrightened())'
    con_fear = 'not SavingThrow(Ability.Constitution, SourceSpellDC(), AdvantageOnFrightened(), DisadvantageOnFrightened())'
    hostile = 'Character() and not Ally() and not Dead()'

    spell_specs = [
        # ------------------------------------------------------------- base class
        (COSTCO_CART, 'Target_ViciousMockery', 'Spell_Enchantment_Bane',
         'Costco Sample Cart Parked Sideways in the Aisle',
         'Park a heated sample cart across the aisle and guard one cube of pepper jack with your life. '
         'Costs an action and 1 Junk; once per short rest. A target within 6 m makes a Strength saving throw: on a failure it takes '
         '2d6 Bludgeoning damage and is Cube-Denied (-3 m movement speed) for 2 turns, or takes half damage on a success. '
         "'You may have one cube. You may not pass.'",
         dict(UseCosts='ActionPoint:1;HC_Junk:1', TargetRadius='6', DamageType='Bludgeoning',
              TargetConditions=hostile,
              SpellRoll=str_save,
              SpellSuccess='DealDamage(2d6,Bludgeoning,Magical);ApplyStatus(HC_CUBE_DENIED,100,2)',
              SpellFail='DealDamage((2d6)/2,Bludgeoning,Magical)',
              TooltipDamageList='DealDamage(2d6,Bludgeoning)',
              TooltipAttackSave='Strength',
              TooltipStatusApply='ApplyStatus(HC_CUBE_DENIED,100,2)')),

        (DMV_TICKET, 'Target_ViciousMockery', 'Spell_Enchantment_Bane',
         'DMV Ticket B047 Called at the Far Window',
         'Call a ticket number over a crackling PA while the target is three hours into a two-hour wait. '
         'Costs an action and 1 Junk; once per short rest. A target within 12 m makes a Wisdom saving throw: on a failure it takes '
         '2d8 Psychic damage and is Dazed for 1 turn, or takes half damage on a success. '
         'They are on B048. They were always on B048.',
         dict(UseCosts='ActionPoint:1;HC_Junk:1', TargetRadius='12', DamageType='Psychic',
              TargetConditions=hostile,
              SpellRoll=wis_save,
              SpellSuccess='DealDamage(2d8,Psychic,Magical);ApplyStatus(DAZED,100,1)',
              SpellFail='DealDamage((2d8)/2,Psychic,Magical)',
              TooltipDamageList='DealDamage(2d8,Psychic)',
              TooltipAttackSave='Wisdom',
              TooltipStatusApply='ApplyStatus(DAZED,100,1)')),

        (SELF_CHECKOUT, 'Target_ViciousMockery', 'Spell_Enchantment_Bane',
         'Self-Checkout: Unexpected Item in the Bagging Area',
         'Scan an item that does not exist and let the machine announce it to the entire store. '
         'Costs an action and 1 Junk; once per short rest. A target within 9 m makes a Wisdom saving throw: on a failure it takes '
         '2d8 Psychic damage and is locked out of bonus actions with disadvantage on attack rolls for 2 turns, or takes half damage on a success. '
         'The attendant is on break until the heat death of the store.',
         dict(UseCosts='ActionPoint:1;HC_Junk:1', TargetRadius='9', DamageType='Psychic',
              TargetConditions=hostile,
              SpellRoll=wis_save,
              SpellSuccess='DealDamage(2d8,Psychic,Magical);ApplyStatus(HC_UNEXPECTED_ITEM_LOCKOUT,100,2)',
              SpellFail='DealDamage((2d8)/2,Psychic,Magical)',
              TooltipDamageList='DealDamage(2d8,Psychic)',
              TooltipAttackSave='Wisdom',
              TooltipStatusApply='ApplyStatus(HC_UNEXPECTED_ITEM_LOCKOUT,100,2)')),

        (PROP13, 'Shout_SecondWind', 'Spell_Abjuration_MageArmor',
         'Prop 13 Grandfathered Assessment Smirk',
         'Wave a 1978 property tax bill at the county assessor and smirk until the numbers stop meaning anything. '
         'Costs a bonus action and 1 Junk; once per long rest. Regain 1d8 + Constitution modifier Hit Points and gain +2 Armour Class '
         'for 2 turns, which does not stack with other braced-posture bonuses. '
         'You bought in 1978, your neighbour bought in 2019, and the county calls this fair.',
         dict(UseCosts='BonusActionPoint:1;HC_Junk:1', Cooldown='OncePerRest', TargetConditions='Self()',
              SpellProperties='RegainHitPoints(1d8+ConstitutionModifier);ApplyStatus(SELF,HC_GRANDFATHERED_IN,100,2)',
              TooltipDamageList='RegainHitPoints(1d8+ConstitutionModifier)',
              TooltipStatusApply='ApplyStatus(HC_GRANDFATHERED_IN,100,2)')),

        # --------------------------------------------------------------- subclasses
        (TECH_SHUTTLE, 'Zone_Thunderwave', 'Spell_Evocation_Thunderwave',
         'Double-Decker Tech Shuttle Idling in the Bike Lane',
         'Pull a double-decker tech shuttle into the bike lane and let it idle with its hazards on. '
         'Costs an action and 1 Junk; once per short rest. Enemy creatures in a 9 m by 3 m rectangle ahead of you make a Dexterity saving throw: '
         'on a failure they take 3d8 Bludgeoning damage and fall Prone for 1 turn, or take half damage on a success. '
         'The shuttle does not see bikes. The shuttle sees headcount.',
         dict(UseCosts='ActionPoint:1;HC_Junk:1', Range='9', Base='3', DamageType='Bludgeoning',
              TargetConditions='Enemy()',
              SpellRoll=dex_save,
              SpellSuccess='DealDamage(3d8,Bludgeoning,Magical);ApplyStatus(PRONE,100,1)',
              SpellFail='DealDamage((3d8)/2,Bludgeoning,Magical)',
              TooltipDamageList='DealDamage(3d8,Bludgeoning)',
              TooltipAttackSave='Dexterity',
              TooltipStatusApply='ApplyStatus(PRONE,100,1)')),

        (RACCOON_TRIBUNAL, 'Target_ViciousMockery', 'Spell_Conjuration_AcidSplash',
         'Raccoon Tribunal Behind the Green Compost Bins',
         'Convene a raccoon tribunal behind the green compost bins and read the charges aloud. '
         'Costs an action and 1 Junk; once per long rest. A target within 3 m makes a Constitution saving throw: on a failure it takes '
         '2d6 Piercing plus 1d8 Poison damage and is Frightened for 1 turn, or takes half damage on a success. '
         'They have a quorum, your leftovers, and minutes from last week.',
         dict(UseCosts='ActionPoint:1;HC_Junk:1', Cooldown='OncePerRest', TargetRadius='3', DamageType='Piercing',
              TargetConditions=hostile,
              SpellRoll=con_fear,
              SpellSuccess='DealDamage(2d6,Piercing,Magical);DealDamage(1d8,Poison,Magical);ApplyStatus(FRIGHTENED,100,1)',
              SpellFail='DealDamage((2d6)/2,Piercing,Magical);DealDamage((1d8)/2,Poison,Magical)',
              TooltipDamageList='DealDamage(2d6,Piercing);DealDamage(1d8,Poison)',
              TooltipAttackSave='Constitution',
              TooltipStatusApply='ApplyStatus(FRIGHTENED,100,1)')),

        (PURPLEAIR, 'Target_ViciousMockery', 'Spell_Conjuration_AcidSplash',
         'PurpleAir Wildfire Refresh at 2:14 PM',
         'Refresh the PurpleAir map at 2:14 PM and watch your whole neighbourhood turn the colour of a plum. '
         'Costs an action and 1 Junk; once per long rest. A target within 6 m makes a Constitution saving throw: on a failure it takes '
         '2d6 Poison damage and is Blinded for 1 turn, or takes half damage on a success. '
         'AQI 187. The app would like you to stay indoors, which you cannot.',
         dict(UseCosts='ActionPoint:1;HC_Junk:1', Cooldown='OncePerRest', TargetRadius='6', DamageType='Poison',
              TargetConditions=hostile,
              SpellRoll=con_save,
              SpellSuccess='DealDamage(2d6,Poison,Magical);ApplyStatus(BLINDED,100,1)',
              SpellFail='DealDamage((2d6)/2,Poison,Magical)',
              TooltipDamageList='DealDamage(2d6,Poison)',
              TooltipAttackSave='Constitution',
              TooltipStatusApply='ApplyStatus(BLINDED,100,1)')),

        # --------------------------------------------------------------- race / subrace
        (TRUST_FALL, 'Target_ShockingGrasp', 'Spell_Evocation_ShockingGrasp',
         'Series-B Offsite Trust Fall Onto Asphalt',
         'Wave a colleague backwards off a loading dock in the name of team building. '
         'Costs an action; once per short rest. Melee spell attack within 1.5 m: deals 2d8 Bludgeoning damage and knocks the target Prone, '
         'and whether or not it lands you gain Offsite Bounce-Back (advantage on attack rolls) for 2 turns. '
         "The facilitator said 'I've got you.' The facilitator has stock options.",
         dict(UseCosts='ActionPoint:1', TargetRadius='1.5', DamageType='Bludgeoning',
              TargetConditions=hostile,
              SpellRoll='Attack(AttackType.MeleeSpellAttack)',
              SpellProperties='ApplyStatus(SELF,HC_OFFSITE_BOUNCE_BACK,100,2)',
              SpellSuccess='DealDamage(2d8,Bludgeoning,Magical);ApplyStatus(PRONE,100,1)',
              TooltipDamageList='DealDamage(2d8,Bludgeoning)',
              TooltipAttackSave='MeleeSpellAttack',
              TooltipStatusApply='ApplyStatus(PRONE,100,1);ApplyStatus(HC_OFFSITE_BOUNCE_BACK,100,2)')),

        (HOA_BEIGE, 'Target_ViciousMockery', 'Spell_Enchantment_Bane',
         'HOA Architectural Committee Beige-Paint Denial',
         'Mail a rejection letter citing Section 14(c) of the CC&Rs over a paint chip that is two shades off. '
         'Costs an action; once per short rest. A target within 9 m makes a Wisdom saving throw: on a failure it takes '
         '2d8 Psychic damage and is Frightened for 2 turns, or takes half damage on a success. '
         'The beige you submitted is not the approved beige.',
         dict(UseCosts='ActionPoint:1', TargetRadius='9', DamageType='Psychic',
              TargetConditions=hostile,
              SpellRoll=wis_fear,
              SpellSuccess='DealDamage(2d8,Psychic,Magical);ApplyStatus(FRIGHTENED,100,2)',
              SpellFail='DealDamage((2d8)/2,Psychic,Magical)',
              TooltipDamageList='DealDamage(2d8,Psychic)',
              TooltipAttackSave='Wisdom',
              TooltipStatusApply='ApplyStatus(FRIGHTENED,100,2)')),

        (NEXTDOOR_COYOTE, 'Shout_FeyPresence', 'Spell_Enchantment_Bane',
         'Nextdoor Lost-Coyote Thread, 214 Comments Deep',
         'Post a grainy photo of a perfectly ordinary dog to Nextdoor and caption it LOST COYOTE. '
         'Costs an action; once per short rest. Enemies within 6 m of you make a Wisdom saving throw: on a failure they take '
         '2d8 Psychic damage and are Frightened for 1 turn, or take half damage on a success. '
         "It is not a coyote. It has been everyone's coyote since March.",
         dict(UseCosts='ActionPoint:1', AreaRadius='6', SpellContainerID='',
              TargetConditions='Enemy()',
              SpellRoll=wis_fear,
              SpellSuccess='DealDamage(2d8,Psychic,Magical);ApplyStatus(FRIGHTENED,100,1)',
              SpellFail='DealDamage((2d8)/2,Psychic,Magical)',
              TooltipDamageList='DealDamage(2d8,Psychic)',
              TooltipAttackSave='Wisdom',
              TooltipStatusApply='ApplyStatus(FRIGHTENED,100,1)')),
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
    (stats / 'HC_Spells_Round9.txt').write_text('\n\n'.join(spell_blocks) + '\n', encoding='utf-8')

    return {
        'base': {
            8: [COSTCO_CART, DMV_TICKET, SELF_CHECKOUT],
            12: [PROP13],
        },
        'subclasses': {
            'BARTPlatformMenace': {3: [TECH_SHUTTLE]},
            'TenderloinBiohazard': {12: [RACCOON_TRIBUNAL]},
            'OverpassRiverbedDweller': {12: [PURPLEAIR]},
        },
        'existing_list_spells': {
            'Siliconite_L3': TRUST_FALL,
            'InlandEmperor_L3': HOA_BEIGE,
            'Beachborn_L1': NEXTDOOR_COYOTE,
        },
    }
