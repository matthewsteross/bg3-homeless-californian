"""Round 5 additions: stereotype & street comedy expansion (4 base spells, 4 subclass L6 spells, 2 racial spells, 7 statuses).

Local development candidate; NOT gameplay-tested.

Vanilla evidence (extracted data under temp_race/Public):
- Shout_SecondWind (Shared/Stats/Generated/Data/Spell_Shout.txt:2458): self-shout donor.
- Target_ShockingGrasp (Shared/Stats/Generated/Data/Spell_Target.txt): melee spell attack donor.
- Target_ViciousMockery (Shared/Stats/Generated/Data/Spell_Target.txt:6164): 9 m ranged save spell donor.
- Zone_Thunderwave (Shared/Stats/Generated/Data/Spell_Zone.txt:283): Square line/zone donor.
- Projectile_AcidSplash (Shared/Stats/Generated/Data/Spell_Projectile.txt): AoE projectile donor.
- Surfaces: WaterElectrified, FogCloud, Fire (verified in vanilla CreateSurface calls).
- Statuses: DAZED, PRONE, SAVED_AGAINST_HOSTILE_SPELL (Shared), plus mod statuses FENT_STUPOR, PANHANDLING_SHAME, FECAL_STENCH.
- Gold template: 1c3c9c74-34a1-4685-989e-410dc080be6f (OBJ_GoldCoin RootTemplate).
"""
from pathlib import Path
from hc_icon_keys import icon_for_spell

GOLD_TEMPLATE = '1c3c9c74-34a1-4685-989e-410dc080be6f'

LAWNMOWER = 'HC_Shout_3AMLawnmowerDisassembly'
COPPER_STRIP = 'HC_Target_CopperWireStrip'
PROP47_CALC = 'HC_Target_Prop47Calculator'
SCOOTER_HIT = 'HC_Zone_LimeScooterHitAndRun'

FOIL_HOTBOX = 'HC_Projectile_FoilFentHotbox'
VENICE_BONGOS = 'HC_Target_VeniceDrumCircle'
BART_SEAT = 'HC_Target_BARTFabricSeatBiohazard'
PROPANE_BBQ = 'HC_Shout_PropaneTankSidewalkBBQ'

UNHOUSED_LECTURE = 'HC_Target_UnhousedLecture'
EREWHON_SMOOTHIE = 'HC_Shout_ErewhonSmoothie'

STATUS_SPECS = [
    ('HC_TWEAKER_HYPERFOCUS', LAWNMOWER, 'Spell_Transmutation_Haste',
     '3 AM Tweaker Hyperfocus',
     '+4.5 m movement speed, +2 AC, advantage on Dexterity saving throws and Sleight of Hand checks, and immunity to Sleep. Everything makes sense if you take enough screws out.',
     dict(Boosts='ActionResource(Movement,4.5,0);AC(2);Advantage(SavingThrow,Dexterity);Advantage(Skill,SleightOfHand);StatusImmunity(SG_Sleeping)', StackId='HC_CHAIR_BRACED')),
    ('HC_STRIPPED_WIRING', COPPER_STRIP, 'Spell_Evocation_ShockingGrasp',
     'Stripped Copper & Live Sparks',
     '-2 Armour Class and cannot take reactions. Somebody yanked your ground wire right out of the drywall.',
     dict(Boosts='AC(-2);ActionResourceBlock(ReactionActionPoint)',
          StatusPropertyFlags='InitiateCombat')),
    ('HC_UNDER_FELONY_LIMIT', PROP47_CALC, 'PassiveFeature_ReliableTalent',
     'Under the $950 Felony Threshold',
     '+3 m movement speed and immunity to being knocked Prone. Loss prevention is legally required to just stand there filming you vertically.',
     dict(Boosts='ActionResource(Movement,3,0);StatusImmunity(SG_Prone)')),
    ('HC_SCOOTER_GETAWAY', SCOOTER_HIT, 'Spell_Transmutation_Longstrider',
     'Unregistered E-Scooter Getaway',
     '+3 m movement speed. The rental app thinks this scooter is at the bottom of a canal.',
     dict(Boosts='ActionResource(Movement,3,0)')),
    ('HC_PROPANE_WARMTH', PROPANE_BBQ, 'Spell_Abjuration_ProtectionFromEnergy_Cold',
     'Propane Overpass Warmth',
     'Resistance to Cold damage and weapon attacks deal an extra 1d6 Fire damage. Do not ask why the regulator is hissing.',
     dict(Boosts='Resistance(Cold,Resistant);CharacterWeaponDamage(1d6,Fire)')),
    ('HC_CANCELLED_PROBLEMATIC', UNHOUSED_LECTURE, 'Spell_Enchantment_Bane',
     'Cancelled & Tone-Policed',
     'Disadvantage on attack rolls and cannot take reactions. Buried under a forty-minute HR lecture on problematic combat phrasing.',
     dict(Boosts='Disadvantage(AttackRoll);ActionResourceBlock(ReactionActionPoint)',
          StatusPropertyFlags='InitiateCombat')),
    ('HC_EREWHON_GLOW', EREWHON_SMOOTHIE, 'Item_CONS_Potion_Speed',
     '$24 Erewhon & Ozempic Glow',
     '+2 Armour Class, +3 m movement speed, and advantage on Constitution saving throws. Your cheekbones are concave and your moral superiority is blinding.',
     dict(Boosts='AC(2);ActionResource(Movement,3,0);Advantage(SavingThrow,Constitution)')),
]


def generate_round5(public_dir, add_loca, get_guid):
    public = Path(public_dir)
    data_dir = public / 'Stats/Generated/Data'
    data_dir.mkdir(parents=True, exist_ok=True)

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
    (data_dir / 'HC_Status_Round5.txt').write_text('\n\n'.join(status_blocks) + '\n', encoding='utf-8')

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
    con_save = 'not SavingThrow(Ability.Constitution, SourceSpellDC())'
    dex_save = 'not SavingThrow(Ability.Dexterity, SourceSpellDC())'

    spell_specs = [
        (LAWNMOWER, 'Shout_SecondWind', 'Spell_Transmutation_Haste',
         '3 AM Sidewalk Lawnmower Disassembly',
         'Drop to your knees on a bath towel and take apart a lawnmower with a butter knife. '
         'Costs a bonus action and 1 Junk; once per short rest. For 2 turns, gain +4.5 m movement speed, '
         '+2 AC, advantage on Dexterity saving throws and Sleight of Hand checks, and immunity to Sleep. '
         'You do not own a lawn, and by sunrise you will have fourteen extra screws.',
         dict(UseCosts='BonusActionPoint:1;HC_Junk:1', TargetConditions='Self()',
              SpellProperties='ApplyStatus(HC_TWEAKER_HYPERFOCUS,100,2)',
              TooltipStatusApply='ApplyStatus(HC_TWEAKER_HYPERFOCUS,100,2)')),

        (COPPER_STRIP, 'Target_ShockingGrasp', 'Spell_Evocation_ShockingGrasp',
         'Live Copper Wire Harvest',
         'Rip the live copper wiring straight out of a municipal streetlamp or enemy armour while the breaker is still on. '
         'Costs an action and 1 Junk; once per short rest. Melee spell attack within 1.5 m: deals 3d8 Lightning plus '
         '1d8 Slashing damage, leaves the target with Stripped Copper (-2 AC and no reactions) for 2 turns, and creates '
         'a 1.5 m electrified water puddle for 2 turns. That copper belongs to the scrap yard now.',
         dict(UseCosts='ActionPoint:1;HC_Junk:1', TargetRadius='1.5', DamageType='Lightning',
              TargetConditions='Character() and not Ally() and not Dead()',
              SpellRoll='Attack(AttackType.MeleeSpellAttack)',
              SpellProperties='GROUND:CreateSurface(1.5,2,WaterElectrified)',
              SpellSuccess='DealDamage(3d8,Lightning,Magical);DealDamage(1d8,Slashing,Magical);ApplyStatus(HC_STRIPPED_WIRING,100,2)',
              TooltipDamageList='DealDamage(3d8,Lightning);DealDamage(1d8,Slashing)',
              TooltipAttackSave='MeleeSpellAttack',
              TooltipStatusApply='ApplyStatus(HC_STRIPPED_WIRING,100,2)')),

        (PROP47_CALC, 'Target_ViciousMockery', 'PassiveFeature_ReliableTalent',
         "Prop 47 '$949' Calculator",
         'Mentally tally your trash bag of liberated merchandise at the exact misdemeanor threshold. '
         'Costs an action and 1 Junk; once per short rest. Pocket 5 gold and gain +3 m movement and Prone immunity for 1 turn, '
         'while a target within 9 m makes a Wisdom saving throw: on a failure it takes 3d8 Psychic damage and is Dazed for 2 turns, '
         'or half damage on a success. Loss prevention is legally required to just stand there filming you vertically.',
         dict(UseCosts='ActionPoint:1;HC_Junk:1', TargetRadius='9',
              TargetConditions='Character() and not Ally() and not Dead()',
              SpellProperties=f'SELF:SummonInInventory({GOLD_TEMPLATE},-1,5,false,false,false);ApplyStatus(SELF,HC_UNDER_FELONY_LIMIT,100,1)',
              SpellRoll=wis_save,
              SpellSuccess='DealDamage(3d8,Psychic,Magical);ApplyStatus(DAZED,100,2)',
              SpellFail='DealDamage((3d8)/2,Psychic,Magical)',
              TooltipDamageList='DealDamage(3d8,Psychic)',
              TooltipAttackSave='Wisdom',
              TooltipStatusApply='ApplyStatus(DAZED,100,2)')),

        (SCOOTER_HIT, 'Zone_Thunderwave', 'Spell_Evocation_Thunderwave',
         'Jailbroken E-Scooter Hit-and-Run',
         'Blast down the pavement on a hotwired rental e-scooter while its GPS speaker shrieks at maximum volume. '
         'Costs an action and 1 Junk; once per short rest. Gain +3 m movement for 1 turn while creatures in a 9 m by 3 m rectangle ahead of you '
         'make a Dexterity saving throw, taking 3d8 + Constitution modifier Bludgeoning plus 1d8 Thunder damage and falling '
         'Prone for 1 turn on a failure, or half damage on a success. The app thinks this scooter is at the bottom of a canal.',
         dict(UseCosts='ActionPoint:1;HC_Junk:1', Range='9', Base='3', DamageType='Bludgeoning',
              TargetConditions='Character() and not Ally() and not Dead()',
              SpellProperties='ApplyStatus(SELF,HC_SCOOTER_GETAWAY,100,1)',
              SpellRoll=dex_save,
              SpellSuccess='DealDamage(3d8+ConstitutionModifier,Bludgeoning,Magical);DealDamage(1d8,Thunder,Magical);ApplyStatus(PRONE,100,1)',
              SpellFail='DealDamage((3d8+ConstitutionModifier)/2,Bludgeoning,Magical);DealDamage((1d8)/2,Thunder,Magical)',
              TooltipDamageList='DealDamage(3d8+ConstitutionModifier,Bludgeoning);DealDamage(1d8,Thunder)',
              TooltipAttackSave='Dexterity',
              TooltipStatusApply='ApplyStatus(PRONE,100,1)')),

        (FOIL_HOTBOX, 'Projectile_AcidSplash', 'Spell_Conjuration_AcidSplash',
         'Tin-Foil Bus Shelter Hotbox',
         'Cook mystery blue tablets on a square of foil until the entire block fails a contact toxicology screen. '
         'Costs an action and 2 Junk; once per short rest. Fills a 3 m radius with fog for 2 turns while creatures inside '
         'make a Constitution saving throw, taking 3d8 Poison plus 2d6 Psychic damage and falling into Fent Stupor for 1 turn '
         'on a failure, or half damage on a success. Three commuters upwind just failed their CDL physical.',
         dict(UseCosts='ActionPoint:1;HC_Junk:2', AreaRadius='3', ExplodeRadius='3', DamageType='Poison',
              SpellProperties='GROUND:CreateSurface(3,2,FogCloud)',
              SpellRoll=con_save,
              SpellSuccess='DealDamage(3d8,Poison,Magical);DealDamage(2d6,Psychic,Magical);ApplyStatus(FENT_STUPOR,100,1)',
              SpellFail='DealDamage((3d8)/2,Poison,Magical);DealDamage((2d6)/2,Psychic,Magical)',
              TooltipDamageList='DealDamage(3d8,Poison);DealDamage(2d6,Psychic)',
              TooltipAttackSave='Constitution',
              TooltipStatusApply='ApplyStatus(FENT_STUPOR,100,1)')),

        (VENICE_BONGOS, 'Target_ViciousMockery', 'Spell_Enchantment_ViciousMockery',
         'Aggressive Mixtape & Sunset Bongos',
         'Corner a stranger on the boardwalk with a relentless bongo solo and a signed blank CD-R that suddenly costs twenty dollars. '
         'Costs an action and 1 Junk; once per short rest. A target within 9 m makes a Wisdom saving throw: on a failure it takes '
         '2d8 Thunder plus 2d8 Psychic damage, becomes Socially Shamed for 2 turns, and hands over 5 gold, or takes half damage on a success. '
         'You already took the CD, bro, it is personalised.',
         dict(UseCosts='ActionPoint:1;HC_Junk:1', TargetRadius='9',
              TargetConditions='Character() and not Ally() and not Dead()',
              SpellRoll=wis_save,
              SpellSuccess=f'DealDamage(2d8,Thunder,Magical);DealDamage(2d8,Psychic,Magical);ApplyStatus(PANHANDLING_SHAME,100,2);SELF:SummonInInventory({GOLD_TEMPLATE},-1,5,false,false,false)',
              SpellFail='DealDamage((2d8)/2,Thunder,Magical);DealDamage((2d8)/2,Psychic,Magical)',
              TooltipDamageList='DealDamage(2d8,Thunder);DealDamage(2d8,Psychic)',
              TooltipAttackSave='Wisdom',
              TooltipStatusApply='ApplyStatus(PANHANDLING_SHAME,100,2)')),

        (BART_SEAT, 'Target_ViciousMockery', 'Spell_Conjuration_AcidSplash',
         'Damp Cloth BART Seat Mystery Stain',
         'Slap a vintage 1990s fabric transit cushion and unleash thirty years of fermented mystery dampness. '
         'Costs an action and 1 Junk; once per short rest. A target within 9 m makes a Constitution saving throw, taking '
         '3d8 Poison plus 1d8 Acid damage and suffering Fecal Stench for 2 turns on a failure, or half damage on a success. '
         'Nobody knows why the seat was warm.',
         dict(UseCosts='ActionPoint:1;HC_Junk:1', TargetRadius='9',
              TargetConditions='Character() and not Ally() and not Dead()',
              SpellRoll=con_save,
              SpellSuccess='DealDamage(3d8,Poison,Magical);DealDamage(1d8,Acid,Magical);ApplyStatus(FECAL_STENCH,100,2)',
              SpellFail='DealDamage((3d8)/2,Poison,Magical);DealDamage((1d8)/2,Acid,Magical)',
              TooltipDamageList='DealDamage(3d8,Poison);DealDamage(1d8,Acid)',
              TooltipAttackSave='Constitution',
              TooltipStatusApply='ApplyStatus(FECAL_STENCH,100,2)')),

        (PROPANE_BBQ, 'Shout_SecondWind', 'Spell_Abjuration_ProtectionFromEnergy_Cold',
         'Stolen Propane Tank Overpass Cookout',
         'Fire up a dented twenty-pound propane cylinder with a taped regulator under the freeway. '
         'Costs a bonus action and 1 Junk; once per short rest. Regain 1d8 + Constitution modifier Hit Points, gain Cold resistance '
         'and +1d6 Fire weapon damage for 2 turns, and ignite a 2 m patch of fire around you for 2 turns (careful, you are standing in it). '
         'Dinner is hot and so is the retaining wall.',
         dict(UseCosts='BonusActionPoint:1;HC_Junk:1', TargetConditions='Self()',
              SpellProperties='RegainHitPoints(1d8+ConstitutionModifier);ApplyStatus(SELF,HC_PROPANE_WARMTH,100,2);GROUND:CreateSurface(2,2,Fire)',
              TooltipDamageList='RegainHitPoints(1d8+ConstitutionModifier)',
              TooltipStatusApply='ApplyStatus(HC_PROPANE_WARMTH,100,2)')),

        (UNHOUSED_LECTURE, 'Target_ViciousMockery', 'Spell_Enchantment_Bane',
         "'Actually, The Term Is Unhoused Neighbor'",
         'Deliver a forty-minute Silver Lake lecture on why your opponent is using problematic combat terminology. '
         'Costs an action; once per short rest. A target within 9 m makes a Wisdom saving throw: on a failure it takes '
         '2d6 Psychic damage and is Cancelled for 2 turns (disadvantage on attack rolls and no reactions), or takes 1d6 Psychic damage on a success. '
         'Let us unpack why you swung that scimitar.',
         dict(UseCosts='ActionPoint:1', TargetRadius='9',
              TargetConditions='Character() and not Ally() and not Dead()',
              SpellRoll=wis_save,
              SpellSuccess='DealDamage(2d6,Psychic,Magical);ApplyStatus(HC_CANCELLED_PROBLEMATIC,100,2)',
              SpellFail='DealDamage(1d6,Psychic,Magical)',
              TooltipDamageList='DealDamage(2d6,Psychic)',
              TooltipAttackSave='Wisdom',
              TooltipStatusApply='ApplyStatus(HC_CANCELLED_PROBLEMATIC,100,2)')),

        (EREWHON_SMOOTHIE, 'Shout_SecondWind', 'Item_CONS_Potion_Speed',
         '$24 Erewhon Sea-Moss & Ozempic Glaze',
         'Sip a twenty-four-dollar jar of wild sea-moss gel and colostrum while microdosing semaglutide. '
         'Costs a bonus action; once per long rest. Regain 1d8 + Spellcasting Ability modifier Hit Points and gain +2 AC, '
         '+3 m movement speed, and advantage on Constitution saving throws for 2 turns. '
         'You have not eaten a solid carbohydrate since 2021.',
         dict(UseCosts='BonusActionPoint:1', Cooldown='OncePerRest', TargetConditions='Self()',
              SpellProperties='RegainHitPoints(1d8+SpellCastingAbilityModifier);ApplyStatus(SELF,HC_EREWHON_GLOW,100,2)',
              TooltipDamageList='RegainHitPoints(1d8+SpellCastingAbilityModifier)',
              TooltipStatusApply='ApplyStatus(HC_EREWHON_GLOW,100,2)')),
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
    (data_dir / 'HC_Spells_Round5.txt').write_text('\n\n'.join(spell_blocks) + '\n', encoding='utf-8')

    return {
        'base': {
            6: [LAWNMOWER],
            7: [COPPER_STRIP],
            9: [PROP47_CALC],
            10: [SCOOTER_HIT],
        },
        'subclasses': {
            'TenderloinBiohazard': {6: [FOIL_HOTBOX]},
            'VeniceBoardwalkBrawler': {6: [VENICE_BONGOS]},
            'BARTPlatformMenace': {6: [BART_SEAT]},
            'OverpassRiverbedDweller': {6: [PROPANE_BBQ]},
        },
        'racial_spells': [UNHOUSED_LECTURE, EREWHON_SMOOTHIE],
    }
