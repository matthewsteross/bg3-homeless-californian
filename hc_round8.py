"""Round 8 additions: 10 bureaucracy/infrastructure/wellness comedy spells and 9 statuses.

Base class L4 / L6 / L10 / L11, subclass L10 / L10 / L12 / L12 (Tenderloin / Overpass / Venice / BART),
Californian race L1 and Siliconite subrace L1.

Local development candidate; NOT gameplay-tested.

Vanilla evidence (extracted data under temp_race/Public, Shared/SharedDev/Gustav/GustavDev layers; none are overridden in Honour):
- Spell donors: Target_ViciousMockery, Target_CureWounds, Target_Longstrider, Shout_SecondWind, Shout_FeyPresence,
  Projectile_AcidSplash (all already used as donors by Rounds 5-7 or the Hustle kit).
- Statuses: PRONE and BLINDED (vanilla StatusData, used by earlier rounds).
- Surface: DarknessCloud (vanilla CreateSurface evidence, e.g. the Darkness spell).
- Functors: DealDamage(..., Magical), RegainHitPoints(1d8+ConstitutionModifier) / RegainHitPoints(2d8), ApplyStatus, GROUND:CreateSurface.
- Boosts: RollBonus(Attack,1d4), RollBonus(SavingThrow,1d4), RollBonus(SkillCheck,1d4), AC(1), AC(2),
  ActionResource(Movement,-3,0), ActionResourceMultiplier(Movement,50,0), ActionResourceMultiplier(Movement,0,0),
  ActionResourceBlock(ActionPoint / BonusActionPoint / ReactionActionPoint), StatusImmunity(SG_Blinded), StatusImmunity(SG_Prone),
  Advantage(AttackTarget), Advantage(SavingThrow,Constitution/Strength/Dexterity), Disadvantage(SavingThrow,Dexterity/Wisdom),
  Advantage(Skill,Intimidation).
"""
from pathlib import Path
from hc_icon_keys import icon_for_spell

# Base class
POTHOLE = 'HC_Target_PotholeAnkleBreaker'                 # L4
NIMBY_COMMENT = 'HC_Shout_NIMBYPublicCommentPeriod'        # L6
UNFINISHED_BUSINESS = 'HC_Target_DepartmentUnfinishedBusiness'  # L10
BUDGET_HEARING = 'HC_Shout_MunicipalBudgetHearing'         # L11

# Subclasses
CHIROPRACTIC = 'HC_Target_SidewalkChiropracticAdjustment'  # Tenderloin L10
BLACKOUT = 'HC_Projectile_PGEPublicSafetyBlackout'         # Overpass L10
SUNGLASSES = 'HC_Shout_EmergencyBoardwalkSunglasses'       # Venice L12
SEISMIC_RETROFIT = 'HC_Shout_HaywardFaultSeismicRetrofit'  # BART L12

# Race / subrace
HOT_BAR = 'HC_Shout_WholeFoodsHotBarHeist'                 # Californian L1
SCROLL_MEETING = 'HC_Target_MeetingCouldHaveBeenAScroll'   # Siliconite L1

STATUS_SPECS = [
    ('HC_BROKEN_ANKLE', POTHOLE, 'Spell_Enchantment_Bane',
     'Class-Action Metatarsal Fracture (Pending)',
     'Movement speed halved and disadvantage on Dexterity saving throws. You stepped in a pothole the city has been aware of since 2014.',
     dict(Boosts='ActionResourceMultiplier(Movement,50,0);Disadvantage(SavingThrow,Dexterity)',
          StatusPropertyFlags='InitiateCombat')),
    ('HC_PUBLIC_COMMENT_TRANCE', NIMBY_COMMENT, 'Spell_Enchantment_Bane',
     'Speaker Forty-One of Forty-Four',
     'Cannot move or take actions, bonus actions, or reactions. Gary is reading his parking-impact study aloud and nobody is allowed to leave.',
     dict(Boosts='ActionResourceBlock(ActionPoint);ActionResourceBlock(BonusActionPoint);ActionResourceBlock(ReactionActionPoint);ActionResourceMultiplier(Movement,0,0)',
          StatusPropertyFlags='InitiateCombat')),
    ('HC_RED_TAGGED', UNFINISHED_BUSINESS, 'Spell_Enchantment_Bane',
     'Red-Tagged: Unpermitted Everything',
     'Attack rolls against you have advantage and you have disadvantage on Wisdom saving throws. Notice of Violation 4471-B has been stapled to your forehead.',
     dict(Boosts='Advantage(AttackTarget);Disadvantage(SavingThrow,Wisdom)',
          StatusPropertyFlags='InitiateCombat')),
    ('HC_LINE_ITEM_APPROVED', BUDGET_HEARING, 'Spell_Abjuration_MageArmor',
     'Consent Calendar: Approved 5 to 4',
     '+1d4 to attack rolls, +1d4 to saving throws, and +1 Armour Class. The line item for consultants passed without anyone reading it.',
     dict(Boosts='RollBonus(Attack,1d4);RollBonus(SavingThrow,1d4);AC(1)')),
    ('HC_CERVICAL_REALIGNMENT', CHIROPRACTIC, 'Skill_Fighter_SecondWind',
     'Freshly Cracked Cervical Spine',
     'Advantage on Strength and Dexterity saving throws. Your chakras are aligned, your neck is not, and you can taste colours.',
     dict(Boosts='Advantage(SavingThrow,Strength);Advantage(SavingThrow,Dexterity)')),
    ('HC_TEN_DOLLAR_SHADES', SUNGLASSES, 'Spell_Abjuration_MageArmor',
     'Ten-Dollar Wraparound Cool',
     'Immune to being Blinded, +1d4 to attack rolls, and advantage on Intimidation checks. Nobody can see your eyes, which makes this entirely about vibes.',
     dict(Boosts='StatusImmunity(SG_Blinded);RollBonus(Attack,1d4);Advantage(Skill,Intimidation)')),
    ('HC_RETROFIT_PENDING', SEISMIC_RETROFIT, 'Spell_Abjuration_Stoneskin',
     'Seismic Retrofit (Pending Since 1989)',
     '+2 Armour Class and immunity to being knocked Prone. The retrofit was approved, funded, re-funded, and never actually started, but somehow you are fine.',
     dict(Boosts='AC(2);StatusImmunity(SG_Prone)')),
    ('HC_HOT_BAR_FOOD_COMA', HOT_BAR, 'Skill_Fighter_SecondWind',
     'Four Pounds of Mac and Cheese, By Weight',
     'Advantage on Constitution saving throws, but -3 m movement speed. You have paid for one olive.',
     dict(Boosts='Advantage(SavingThrow,Constitution);ActionResource(Movement,-3,0)')),
    ('HC_SYNERGY_ALIGNED', SCROLL_MEETING, 'Spell_Abjuration_MageArmor',
     'Aligned On Next Steps',
     '+1d4 to attack rolls and +1d4 to ability checks. Everyone left the room with the same understanding, which has never happened before.',
     dict(Boosts='RollBonus(Attack,1d4);RollBonus(SkillCheck,1d4)')),
]


def generate_round8(public_dir, add_loca, get_guid):
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
    (stats / 'HC_Status_Round8.txt').write_text('\n\n'.join(status_blocks) + '\n', encoding='utf-8')

    # ------------------------------------------------------------------ spells
    base_fields = dict(
        Level='0', Cooldown='OncePerShortRest', DescriptionParams='', ExtraDescription='',
        MemoryCost='0', RechargeValues='', TooltipUpcastDescription='',
        TooltipUpcastDescriptionParams='', TooltipDamageList='', TooltipStatusApply='',
        TooltipAttackSave='', TooltipPermanentWarnings='', TooltipOnSave='',
        SpellProperties='', SpellRoll='', SpellSuccess='', SpellFail='',
        CastTextEvent='Cast',
    )
    wis_save = 'not SavingThrow(Ability.Wisdom, SourceSpellDC())'
    dex_save = 'not SavingThrow(Ability.Dexterity, SourceSpellDC())'
    healable = "Character() and Ally() and not Self() and not Dead() and not Tagged('UNDEAD') and not Tagged('CONSTRUCT')"

    spell_specs = [
        # ------------------------------------------------------------- base class
        (POTHOLE, 'Target_ViciousMockery', 'Spell_Conjuration_Grease',
         'Unrepaired Pothole Since 2014 Ankle-Breaker',
         'Open a crater the city has had on its to-do list for a decade directly under your target\'s front foot. '
         'Costs an action and 1 Junk; once per short rest. A target within 9 m makes a Dexterity saving throw: on a failure it takes '
         '2d8 Bludgeoning damage, falls Prone, and suffers a Class-Action Metatarsal Fracture (halved movement and disadvantage on '
         'Dexterity saving throws) for 2 turns, or takes half damage on a success. '
         'A cone has been placed beside the hole, and the cone has also been there since 2014.',
         dict(UseCosts='ActionPoint:1;HC_Junk:1', TargetRadius='9', DamageType='Bludgeoning',
              TargetConditions='Character() and not Ally() and not Dead()',
              SpellRoll=dex_save,
              SpellSuccess='DealDamage(2d8,Bludgeoning,Magical);ApplyStatus(PRONE,100,1);ApplyStatus(HC_BROKEN_ANKLE,100,2)',
              SpellFail='DealDamage((2d8)/2,Bludgeoning,Magical)',
              TooltipDamageList='DealDamage(2d8,Bludgeoning)',
              TooltipAttackSave='Dexterity',
              TooltipStatusApply='ApplyStatus(HC_BROKEN_ANKLE,100,2)')),

        (NIMBY_COMMENT, 'Shout_FeyPresence', 'Spell_Enchantment_Bane',
         'NIMBY Three-Minute Public Comment Period',
         'Stand at the lectern and begin reading a forty-one-page objection to a bicycle rack. '
         'Costs an action and 1 Junk; once per long rest. Enemies within 6 m make a Wisdom saving throw: on a failure they take '
         '2d6 Psychic damage and cannot move or take actions, bonus actions, or reactions for 1 turn, or take half damage on a success. '
         'The planning commission would like to table this item until the next meeting, which is in March.',
         dict(UseCosts='ActionPoint:1;HC_Junk:1', Cooldown='OncePerRest', AreaRadius='6', SpellContainerID='',
              TargetConditions='Character() and not Self() and not Ally() and not Dead()',
              SpellRoll=wis_save,
              SpellSuccess='DealDamage(2d6,Psychic,Magical);ApplyStatus(HC_PUBLIC_COMMENT_TRANCE,100,1)',
              SpellFail='DealDamage((2d6)/2,Psychic,Magical)',
              TooltipDamageList='DealDamage(2d6,Psychic)',
              TooltipAttackSave='Wisdom',
              TooltipStatusApply='ApplyStatus(HC_PUBLIC_COMMENT_TRANCE,100,1)')),

        (UNFINISHED_BUSINESS, 'Target_ViciousMockery', 'Spell_Enchantment_Bane',
         'Department of Unfinished Business Red-Tag Notice',
         'Staple a neon orange Notice of Violation onto something the target has never been permitted to own, including its own sword. '
         'Costs an action and 1 Junk; once per short rest. A target within 12 m makes a Wisdom saving throw: on a failure it takes '
         '2d8 Force damage and is Red-Tagged for 2 turns (attack rolls against it have advantage and it has disadvantage on Wisdom saving throws), '
         'or takes half damage on a success. The fine is waived if it can produce a 1987 grading permit, which nobody can.',
         dict(UseCosts='ActionPoint:1;HC_Junk:1', TargetRadius='12', DamageType='Force',
              TargetConditions='Character() and not Ally() and not Dead()',
              SpellRoll=wis_save,
              SpellSuccess='DealDamage(2d8,Force,Magical);ApplyStatus(HC_RED_TAGGED,100,2)',
              SpellFail='DealDamage((2d8)/2,Force,Magical)',
              TooltipDamageList='DealDamage(2d8,Force)',
              TooltipAttackSave='Wisdom',
              TooltipStatusApply='ApplyStatus(HC_RED_TAGGED,100,2)')),

        (BUDGET_HEARING, 'Shout_SecondWind', 'Spell_Abjuration_MageArmor',
         'Municipal Budget Hearing & Consent Calendar',
         'Burn 1 Junk as a fourteen-hundred-page budget packet and slip every self-serving line item through on the consent calendar. '
         'Costs a bonus action and 1 Junk; once per long rest. For 3 turns, gain +1d4 to attack rolls, +1d4 to saving throws, and +1 Armour Class. '
         'It passes five to four, nobody read it, and a consultant just bought a boat.',
         dict(UseCosts='BonusActionPoint:1;HC_Junk:1', Cooldown='OncePerRest', TargetConditions='Self()',
              SpellProperties='ApplyStatus(SELF,HC_LINE_ITEM_APPROVED,100,3)',
              TooltipStatusApply='ApplyStatus(HC_LINE_ITEM_APPROVED,100,3)')),

        # --------------------------------------------------------------- subclasses
        (CHIROPRACTIC, 'Target_CureWounds', 'Skill_Fighter_SecondWind',
         'Unlicensed Sidewalk Chiropractic Cervical Adjustment',
         'Grab an ally by the skull and give it a firm, cash-only twist behind a bus shelter. '
         'Costs an action and 1 Junk; once per short rest. An ally within 1.5 m regains 2d8 Hit Points and gains advantage on Strength and '
         'Dexterity saving throws for 3 turns, but is knocked Prone by the pop. '
         'Your clinic accepts Venmo, hugs, and no questions about the diploma.',
         dict(UseCosts='ActionPoint:1;HC_Junk:1', TargetRadius='1.5',
              TargetConditions=healable,
              SpellProperties='RegainHitPoints(2d8);ApplyStatus(PRONE,100,1);ApplyStatus(HC_CERVICAL_REALIGNMENT,100,3)',
              TooltipDamageList='RegainHitPoints(2d8)',
              TooltipStatusApply='ApplyStatus(HC_CERVICAL_REALIGNMENT,100,3)')),

        (BLACKOUT, 'Projectile_AcidSplash', 'Spell_Evocation_ShockingGrasp',
         'PG&E Public Safety Power Shutoff Rolling Blackout',
         'Lob a smoking pole-mounted transformer into the middle of the fight and announce a precautionary utility shutoff. '
         'Costs an action and 1 Junk; once per long rest. Creates a 4 m cloud of darkness for 3 turns while creatures in a 4 m radius make '
         'a Dexterity saving throw, taking 3d8 Lightning damage and being Blinded for 1 turn on a failure, or half damage on a success. '
         'Power should be restored between four hours and six business weeks from now.',
         dict(UseCosts='ActionPoint:1;HC_Junk:1', Cooldown='OncePerRest', AreaRadius='4', ExplodeRadius='4', DamageType='Lightning',
              SpellProperties='GROUND:CreateSurface(4,3,DarknessCloud)',
              SpellRoll=dex_save,
              SpellSuccess='DealDamage(3d8,Lightning,Magical);ApplyStatus(BLINDED,100,1)',
              SpellFail='DealDamage((3d8)/2,Lightning,Magical)',
              TooltipDamageList='DealDamage(3d8,Lightning)',
              TooltipAttackSave='Dexterity',
              TooltipStatusApply='ApplyStatus(BLINDED,100,1)')),

        (SUNGLASSES, 'Shout_SecondWind', 'Spell_Abjuration_MageArmor',
         'Emergency Ten-Dollar Boardwalk Sunglasses',
         'Slap on a pair of wraparound shades bought from a folding table between a henna tent and a man selling crystals. '
         'Costs a bonus action and 1 Junk; once per long rest. For 3 turns, you cannot be Blinded and gain +1d4 to attack rolls and advantage on Intimidation checks. '
         'The lenses are certified for neither sunlight nor eclipses, and you look incredible.',
         dict(UseCosts='BonusActionPoint:1;HC_Junk:1', Cooldown='OncePerRest', TargetConditions='Self()',
              SpellProperties='ApplyStatus(SELF,HC_TEN_DOLLAR_SHADES,100,3)',
              TooltipStatusApply='ApplyStatus(HC_TEN_DOLLAR_SHADES,100,3)')),

        (SEISMIC_RETROFIT, 'Shout_FeyPresence', 'Spell_Abjuration_Stoneskin',
         'Hayward Fault Transbay Seismic Retrofit (Delayed Until 2041)',
         'Stomp the platform and invoke a retrofit contract that has been under review longer than most marriages. '
         'Costs an action and 1 Junk; once per long rest. Enemies within 6 m make a Dexterity saving throw: on a failure they take '
         '3d6 Bludgeoning damage and fall Prone, or take half damage on a success. '
         'You gain +2 Armour Class and immunity to being knocked Prone for 2 turns, because only you read the engineering report.',
         dict(UseCosts='ActionPoint:1;HC_Junk:1', Cooldown='OncePerRest', AreaRadius='6', SpellContainerID='',
              TargetConditions='Character() and not Self() and not Ally() and not Dead()',
              SpellProperties='ApplyStatus(SELF,HC_RETROFIT_PENDING,100,2)',
              SpellRoll=dex_save,
              SpellSuccess='DealDamage(3d6,Bludgeoning,Magical);ApplyStatus(PRONE,100,1)',
              SpellFail='DealDamage((3d6)/2,Bludgeoning,Magical)',
              TooltipDamageList='DealDamage(3d6,Bludgeoning)',
              TooltipAttackSave='Dexterity',
              TooltipStatusApply='ApplyStatus(HC_RETROFIT_PENDING,100,2)')),

        # --------------------------------------------------------------- race / subrace
        (HOT_BAR, 'Shout_SecondWind', 'Skill_Fighter_SecondWind',
         'Whole Foods Pay-By-Weight Hot Bar Heist',
         'Pack a clamshell container the size of a hatbox with mac and cheese, then walk to the register and declare it all \'mostly lettuce\'. '
         'Costs a bonus action; once per short rest. Regain 1d8 + Constitution modifier Hit Points and gain advantage on Constitution saving throws for 2 turns, '
         'but you are slowed by 3 m of movement as the cheese settles. '
         'The cashier weighs it at four pounds, you pay for one olive, and everyone agrees to never mention this.',
         dict(UseCosts='BonusActionPoint:1', TargetConditions='Self()',
              SpellProperties='RegainHitPoints(1d8+ConstitutionModifier);ApplyStatus(SELF,HC_HOT_BAR_FOOD_COMA,100,2)',
              TooltipDamageList='RegainHitPoints(1d8+ConstitutionModifier)',
              TooltipStatusApply='ApplyStatus(HC_HOT_BAR_FOOD_COMA,100,2)')),

        (SCROLL_MEETING, 'Target_Longstrider', 'Spell_Abjuration_MageArmor',
         'This Meeting Could Have Been a Scroll',
         'Wave an ally into a conference room and drag a forty-slide deck onto the screen, then summarize it in one sentence to everyone\'s relief. '
         'Costs a bonus action; once per short rest. An ally or yourself within 9 m gains +1d4 to attack rolls and +1d4 to ability checks for 2 turns. '
         'Let us take the rest offline and circle back to confirm we are aligned on being aligned.',
         dict(UseCosts='BonusActionPoint:1', TargetRadius='9', RitualCosts='',
              SpellFlags='IsSpell;HasVerbalComponent;HasSomaticComponent;IgnorePreviouslyPickedEntities',
              TargetConditions='Character() and (Ally() or Self()) and not Dead()',
              SpellProperties='ApplyStatus(HC_SYNERGY_ALIGNED,100,2)',
              TooltipStatusApply='ApplyStatus(HC_SYNERGY_ALIGNED,100,2)')),
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
    (stats / 'HC_Spells_Round8.txt').write_text('\n\n'.join(spell_blocks) + '\n', encoding='utf-8')

    return {
        'base': {
            4: [POTHOLE],
            6: [NIMBY_COMMENT],
            10: [UNFINISHED_BUSINESS],
            11: [BUDGET_HEARING],
        },
        'subclasses': {
            'TenderloinBiohazard': {10: [CHIROPRACTIC]},
            'VeniceBoardwalkBrawler': {12: [SUNGLASSES]},
            'BARTPlatformMenace': {12: [SEISMIC_RETROFIT]},
            'OverpassRiverbedDweller': {10: [BLACKOUT]},
        },
        'existing_list_spells': {
            'Californian_L1': HOT_BAR,
            'Siliconite_L1': SCROLL_MEETING,
        },
    }
