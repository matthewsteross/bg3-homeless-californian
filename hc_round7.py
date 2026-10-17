"""Round 7 additions: 4 subclass stereotype signatures (Tenderloin L3, Venice L10, BART L10, Overpass L3),
3 subrace stereotype spells (Beachborn L5, Siliconite L5, Inland Emperor L1),
and 4 base-class street comedy spells (Base L1, L2, L7, L12), plus 8 statuses.

Local development candidate; NOT gameplay-tested.

Vanilla evidence (extracted data under temp_race/Public):
- Spell donors: Target_ViciousMockery, Shout_SecondWind, Shout_FeyPresence, Target_ShockingGrasp, Projectile_AcidSplash.
- Surfaces: WaterElectrified, Acid (verified in vanilla CreateSurface calls).
- Statuses: DAZED, BLINDED, SAVED_AGAINST_HOSTILE_SPELL (Shared), plus mod statuses FECAL_STENCH, PANHANDLING_SHAME, HC_SCOOTER_GETAWAY.
"""
from pathlib import Path
from hc_icon_keys import icon_for_spell

FOIL_BLOWBACK = 'HC_Target_UsedFoilBlowback'
ROID_RAGE = 'HC_Shout_MuscleBeachRoidRage'
EMERGENCY_GATE = 'HC_Shout_TurnstileEmergencyGate'
EXTENSION_TAP = 'HC_Target_ExtensionCordTap'

BOTOX_FREEZE = 'HC_Target_BotoxFillerParalyze'
POLYCULE_CALENDAR = 'HC_Shout_PolyculeGoogleCalendar'
ALTIMA_REV = 'HC_Target_CatalyticStraightPipeRev'

SQUEEGEE_SMEAR = 'HC_Target_GasStationSqueegee'
SERVICE_VEST = 'HC_Shout_FakeServiceVest'
PISS_JUG = 'HC_Projectile_PissJugCatapult'
GOVERNOR_PHOTO_OP = 'HC_Shout_GovernorGavinPhotoOp'

STATUS_SPECS = [
    ('HC_CONTACT_HIGH_NOD', FOIL_BLOWBACK, 'Spell_Enchantment_Bane',
     'Involuntary Sidewalk Nod',
     'Movement speed halved and disadvantage on attack rolls. Somebody exhaled burnt-marshmallow foil fumes straight into your face at the crosswalk.',
     dict(Boosts='ActionResourceMultiplier(Movement,50,0);Disadvantage(AttackRoll)',
          StatusPropertyFlags='InitiateCombat')),
    ('HC_TRENBOLONE_MELTDOWN', ROID_RAGE, 'Spell_Transmutation_Haste',
     'Counterfeit Trenbolone & Raw Liver Meltdown',
     'Weapon attacks deal an extra 1d8 Force damage, +3 m movement speed, and advantage on attack rolls. Your neck veins look like garden hoses and you are screaming at a tripod.',
     dict(Boosts='CharacterWeaponDamage(1d8,Force);ActionResource(Movement,3,0);Advantage(AttackRoll)')),
    ('HC_DAISY_CHAIN_SHOCK', EXTENSION_TAP, 'Spell_Evocation_ShockingGrasp',
     'Seventeen-Cord Harbor Freight Short Circuit',
     'Cannot take reactions and disadvantage on Dexterity saving throws. Electrocuted by an ungrounded orange extension cord plugged into a pried-open streetlight.',
     dict(Boosts='ActionResourceBlock(ReactionActionPoint);Disadvantage(SavingThrow,Dexterity)',
          StatusPropertyFlags='InitiateCombat')),
    ('HC_BOTOX_FACE_FREEZE', BOTOX_FREEZE, 'Spell_Enchantment_Bane',
     'Beverly Hills 40cc Neurotoxin Freeze',
     'Cannot take bonus actions or reactions, and disadvantage on Constitution saving throws. Your forehead and upper lip are medically incapable of human expression.',
     dict(Boosts='ActionResourceBlock(BonusActionPoint);ActionResourceBlock(ReactionActionPoint);Disadvantage(SavingThrow,Constitution)',
          StatusPropertyFlags='InitiateCombat')),
    ('HC_POLYCULE_EXHAUSTION', POLYCULE_CALENDAR, 'Spell_Enchantment_Bane',
     'Trapped in a 9-Person Polycule Calendar Sync',
     'Movement speed halved and disadvantage on attack rolls. Buried under forty-seven colour-coded Google Calendar boundary check-ins.',
     dict(Boosts='ActionResourceMultiplier(Movement,50,0);Disadvantage(AttackRoll)',
          StatusPropertyFlags='InitiateCombat')),
    ('HC_ALTIMA_TINNITUS', ALTIMA_REV, 'Spell_Enchantment_Bane',
     '2 AM Straight-Piped Altima Tinnitus',
     '-2 Armour Class and disadvantage on Wisdom saving throws. Your eardrums were shattered by a bungee-corded 2007 sedan redlining on three spare tires.',
     dict(Boosts='AC(-2);Disadvantage(SavingThrow,Wisdom)',
          StatusPropertyFlags='InitiateCombat')),
    ('HC_ADA_LAWSUIT_SHIELD', SERVICE_VEST, 'Spell_Abjuration_MageArmor',
     'Prime-Shipped Service Vest Immunity',
     '+2 Armour Class and advantage on Deception and Intimidation checks. Store management is far too terrified of a federal lawsuit to ask any follow-up questions.',
     dict(Boosts='AC(2);Advantage(Skill,Deception);Advantage(Skill,Intimidation)', StackId='HC_CHAIR_BRACED')),
    ('HC_NAPA_FUNDRAISER_BUFF', GOVERNOR_PHOTO_OP, 'Skill_Fighter_SecondWind',
     'Gubernatorial Campaign B-Roll Glow',
     '+2 Armour Class and +3 m movement speed. The news vans have already packed up and left for a fifteen-thousand-dollar-a-plate vineyard dinner in Napa.',
     dict(Boosts='AC(2);ActionResource(Movement,3,0)')),
]


def generate_round7(public_dir, add_loca, get_guid):
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
    (stats / 'HC_Status_Round7.txt').write_text('\n\n'.join(status_blocks) + '\n', encoding='utf-8')

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
        (FOIL_BLOWBACK, 'Target_ViciousMockery', 'Spell_Enchantment_Bane',
         'Secondhand Foil-Trail Exhale',
         'Exhale a thick plume of burnt-marshmallow chemical smoke off a creased square of Reynolds Wrap straight into someone at the crosswalk. '
         'Costs an action and 1 Junk; once per short rest. A target within 3 m makes a Constitution saving throw: on a failure it takes '
         '2d8 Poison plus 2d8 Psychic damage and suffers Involuntary Sidewalk Nod (halved movement and disadvantage on attack rolls) for 2 turns, '
         'or takes half damage on a success. Do not stand downwind at the bus stop.',
         dict(UseCosts='ActionPoint:1;HC_Junk:1', TargetRadius='3', DamageType='Poison',
              TargetConditions='Character() and not Ally() and not Dead()',
              SpellRoll=con_save,
              SpellSuccess='DealDamage(2d8,Poison,Magical);DealDamage(2d8,Psychic,Magical);ApplyStatus(HC_CONTACT_HIGH_NOD,100,2)',
              SpellFail='DealDamage((2d8)/2,Poison,Magical);DealDamage((2d8)/2,Psychic,Magical)',
              TooltipDamageList='DealDamage(2d8,Poison);DealDamage(2d8,Psychic)',
              TooltipAttackSave='Constitution',
              TooltipStatusApply='ApplyStatus(HC_CONTACT_HIGH_NOD,100,2)')),

        (ROID_RAGE, 'Shout_SecondWind', 'Spell_Transmutation_Haste',
         'Expired Trenbolone & Raw Liver Tantrum',
         'Dry-scoop expired Tijuana pre-workout and a handful of warm organ meat before snapping at a stranger filming your form. '
         'Costs a bonus action and 1 Junk; once per short rest. For 2 turns, weapon attacks deal an extra 1d8 Force damage, '
         'movement speed increases by 3 m, and you have advantage on attack rolls. '
         'You are 100 percent natural, bro, it is just ancestral eating and cold plunges.',
         dict(UseCosts='BonusActionPoint:1;HC_Junk:1', TargetConditions='Self()',
              SpellProperties='ApplyStatus(HC_TRENBOLONE_MELTDOWN,100,2)',
              TooltipStatusApply='ApplyStatus(HC_TRENBOLONE_MELTDOWN,100,2)')),

        (EMERGENCY_GATE, 'Shout_FeyPresence', 'Spell_Evocation_Thunderwave',
         'Emergency Exit Gate Alarm & JBL Speaker',
         'Kick open the red emergency transit gate while blasting distorted SoundCloud bass out of a blown-out Bluetooth speaker clipped to your belt. '
         'Costs an action and 1 Junk; once per short rest. Gain +3 m movement for 1 turn while enemies within 6 m make a Constitution saving throw: '
         'on a failure they take 3d8 Thunder plus 1d8 Psychic damage and are Dazed for 2 turns, or take half damage on a success. '
         'The alarm will sound for the next forty-five minutes.',
         dict(UseCosts='ActionPoint:1;HC_Junk:1', AreaRadius='6', SpellContainerID='',
              TargetConditions='Enemy()',
              SpellProperties='ApplyStatus(SELF,HC_SCOOTER_GETAWAY,100,1)',
              SpellRoll=con_save,
              SpellSuccess='DealDamage(3d8,Thunder,Magical);DealDamage(1d8,Psychic,Magical);ApplyStatus(DAZED,100,2)',
              SpellFail='DealDamage((3d8)/2,Thunder,Magical);DealDamage((1d8)/2,Psychic,Magical)',
              TooltipDamageList='DealDamage(3d8,Thunder);DealDamage(1d8,Psychic)',
              TooltipAttackSave='Constitution',
              TooltipStatusApply='ApplyStatus(DAZED,100,2)')),

        (EXTENSION_TAP, 'Target_ViciousMockery', 'Spell_Evocation_ShockingGrasp',
         'Bootleg Streetlight 220V Power Tap',
         'Run seventeen daisy-chained orange extension cords out of a pried-open municipal lamppost box down into the flood channel. '
         'Costs an action and 1 Junk; once per short rest. Creates a 2 m electrified water puddle for 2 turns while a target within 9 m '
         'makes a Dexterity saving throw: on a failure it takes 3d8 Lightning plus 1d8 Fire damage and loses reactions and Dexterity save '
         'composure for 2 turns, or takes half damage on a success. It powers a microwave, a box fan, and three neon signs.',
         dict(UseCosts='ActionPoint:1;HC_Junk:1', TargetRadius='9', DamageType='Lightning',
              TargetConditions='Character() and not Ally() and not Dead()',
              SpellProperties='GROUND:CreateSurface(2,2,WaterElectrified)',
              SpellRoll=dex_save,
              SpellSuccess='DealDamage(3d8,Lightning,Magical);DealDamage(1d8,Fire,Magical);ApplyStatus(HC_DAISY_CHAIN_SHOCK,100,2)',
              SpellFail='DealDamage((3d8)/2,Lightning,Magical);DealDamage((1d8)/2,Fire,Magical)',
              TooltipDamageList='DealDamage(3d8,Lightning);DealDamage(1d8,Fire)',
              TooltipAttackSave='Dexterity',
              TooltipStatusApply='ApplyStatus(HC_DAISY_CHAIN_SHOCK,100,2)')),

        (BOTOX_FREEZE, 'Target_ViciousMockery', 'Spell_Enchantment_Bane',
         'Beverly Hills Emergency Botox & Lip-Filler Freeze',
         'Subject your target to forty cubic centimetres of bargain-basement Rodeo Drive neurotoxin and migrating lip filler. '
         'Costs an action; once per long rest. A target within 9 m makes a Constitution saving throw: on a failure it takes '
         '3d8 Poison damage and loses bonus actions, reactions, and Constitution save composure for 2 turns, or takes half damage on a success. '
         'She is furious on the inside, probably.',
         dict(UseCosts='ActionPoint:1', Cooldown='OncePerRest', TargetRadius='9', DamageType='Poison',
              TargetConditions='Character() and not Ally() and not Dead()',
              SpellRoll=con_save,
              SpellSuccess='DealDamage(3d8,Poison,Magical);ApplyStatus(HC_BOTOX_FACE_FREEZE,100,2)',
              SpellFail='DealDamage((3d8)/2,Poison,Magical)',
              TooltipDamageList='DealDamage(3d8,Poison)',
              TooltipAttackSave='Constitution',
              TooltipStatusApply='ApplyStatus(HC_BOTOX_FACE_FREEZE,100,2)')),

        (POLYCULE_CALENDAR, 'Shout_FeyPresence', 'Spell_Enchantment_Bane',
         'Bay Area 9-Person Polycule Google Calendar Invite',
         'Corner everyone within earshot and force them to review the colour-coded scheduling spreadsheet for your nine-person Berkeley board-game polycule. '
         'Costs an action; once per long rest. Enemies within 6 m make a Wisdom saving throw: on a failure they take 3d8 Psychic damage and have '
         'their movement halved and attack rolls given disadvantage for 2 turns, or take half damage on a success. '
         'Your metamour has requested a forty-minute emotional check-in before initiative continues.',
         dict(UseCosts='ActionPoint:1', Cooldown='OncePerRest', AreaRadius='6', SpellContainerID='',
              TargetConditions='Enemy()',
              SpellRoll=wis_save,
              SpellSuccess='DealDamage(3d8,Psychic,Magical);ApplyStatus(HC_POLYCULE_EXHAUSTION,100,2)',
              SpellFail='DealDamage((3d8)/2,Psychic,Magical)',
              TooltipDamageList='DealDamage(3d8,Psychic)',
              TooltipAttackSave='Wisdom',
              TooltipStatusApply='ApplyStatus(HC_POLYCULE_EXHAUSTION,100,2)')),

        (ALTIMA_REV, 'Target_ViciousMockery', 'Spell_Evocation_Thunderwave',
         '2 AM Straight-Piped Nissan Altima Rev',
         'Redline an unregistered 2007 sedan with a bungee-corded trunk, expired paper plates, and three spare donut tires at seven thousand RPM. '
         'Costs an action; once per short rest. A target within 9 m makes a Constitution saving throw: on a failure it takes 2d8 Thunder damage '
         'and suffers -2 AC and disadvantage on Wisdom saving throws for 2 turns, or takes half damage on a success. '
         'Insurance is a social construct.',
         dict(UseCosts='ActionPoint:1', TargetRadius='9', DamageType='Thunder',
              TargetConditions='Character() and not Ally() and not Dead()',
              SpellRoll=con_save,
              SpellSuccess='DealDamage(2d8,Thunder,Magical);ApplyStatus(HC_ALTIMA_TINNITUS,100,2)',
              SpellFail='DealDamage((2d8)/2,Thunder,Magical)',
              TooltipDamageList='DealDamage(2d8,Thunder)',
              TooltipAttackSave='Constitution',
              TooltipStatusApply='ApplyStatus(HC_ALTIMA_TINNITUS,100,2)')),

        (SQUEEGEE_SMEAR, 'Target_ShockingGrasp', 'Spell_Conjuration_AcidSplash',
         'Unsolicited Red-Light Dirty Squeegee',
         'Sprint up to a target before the light turns green and smear grey gutter sludge across their eyes with a torn gas-station squeegee. '
         'Costs an action and 1 Junk; once per short rest. Melee spell attack within 1.5 m: deals 2d6 Acid plus 1d6 Bludgeoning damage and '
         'leaves the target Blinded for 1 turn. That will be five dollars, cash or Venmo.',
         dict(UseCosts='ActionPoint:1;HC_Junk:1', TargetRadius='1.5', DamageType='Acid',
              TargetConditions='Character() and not Ally() and not Dead()',
              SpellRoll='Attack(AttackType.MeleeSpellAttack)',
              SpellSuccess='DealDamage(2d6,Acid,Magical);DealDamage(1d6,Bludgeoning,Magical);ApplyStatus(BLINDED,100,1)',
              TooltipDamageList='DealDamage(2d6,Acid);DealDamage(1d6,Bludgeoning)',
              TooltipAttackSave='MeleeSpellAttack',
              TooltipStatusApply='ApplyStatus(BLINDED,100,1)')),

        (SERVICE_VEST, 'Shout_SecondWind', 'Spell_Abjuration_MageArmor',
         'Amazon Fake Service-Animal Vest',
         'Velcro a twelve-dollar red nylon WORKING SERVICE ANIMAL vest onto your chest and dare anyone in Trader Joe\'s to ask for paperwork. '
         'Costs a bonus action and 1 Junk; once per short rest. Gain +2 Armour Class and advantage on Deception and Intimidation checks for 2 turns. '
         'Asking what task you are trained to perform is a federal crime, probably.',
         dict(UseCosts='BonusActionPoint:1;HC_Junk:1', TargetConditions='Self()',
              SpellProperties='ApplyStatus(HC_ADA_LAWSUIT_SHIELD,100,2)',
              TooltipStatusApply='ApplyStatus(HC_ADA_LAWSUIT_SHIELD,100,2)')),

        (PISS_JUG, 'Projectile_AcidSplash', 'Spell_Conjuration_AcidSplash',
         "Fermented Trucker 'Way of the Road' Gallon Jug",
         'Lob a sun-baked one-gallon iced tea jug that has been fermenting on a freeway shoulder in ninety-eight-degree heat since July. '
         'Costs an action and 1 Junk; once per short rest. Splashes a 3 m Acid surface for 2 turns while creatures in a 3 m radius make a '
         'Constitution saving throw, taking 3d8 Acid plus 2d6 Poison damage and suffering Fecal Stench for 2 turns on a failure, '
         'or half damage on a success. Way of the road, Bubs.',
         dict(UseCosts='ActionPoint:1;HC_Junk:1', AreaRadius='3', ExplodeRadius='3', DamageType='Acid',
              SpellProperties='GROUND:CreateSurface(3,2,Acid)',
              SpellRoll=con_save,
              SpellSuccess='DealDamage(3d8,Acid,Magical);DealDamage(2d6,Poison,Magical);ApplyStatus(FECAL_STENCH,100,2)',
              SpellFail='DealDamage((3d8)/2,Acid,Magical);DealDamage((2d6)/2,Poison,Magical)',
              TooltipDamageList='DealDamage(3d8,Acid);DealDamage(2d6,Poison)',
              TooltipAttackSave='Constitution',
              TooltipStatusApply='ApplyStatus(FECAL_STENCH,100,2)')),

        (GOVERNOR_PHOTO_OP, 'Shout_FeyPresence', 'Skill_Fighter_SecondWind',
         'Election-Year VIP Street-Sweep Photo Op',
         'Summon a fourteen-camera press pool and a politician in rolled-up dress-shirt sleeves for twelve minutes before a foreign head of state visits. '
         'Costs a bonus action; once per long rest. Gain +2 AC and +3 m movement for 2 turns, while enemies within 6 m make a '
         'Wisdom saving throw: on a failure they take 4d8 Psychic damage and become Socially Shamed for 2 turns, or take half damage on a success. '
         'Mission accomplished; the barriers come down as soon as the motorcade leaves.',
         dict(UseCosts='BonusActionPoint:1', Cooldown='OncePerRest', AreaRadius='6', SpellContainerID='',
              TargetConditions='Enemy()',
              SpellProperties='ApplyStatus(SELF,HC_NAPA_FUNDRAISER_BUFF,100,2)',
              SpellRoll=wis_save,
              SpellSuccess='DealDamage(4d8,Psychic,Magical);ApplyStatus(PANHANDLING_SHAME,100,2)',
              SpellFail='DealDamage((4d8)/2,Psychic,Magical)',
              TooltipDamageList='DealDamage(4d8,Psychic)',
              TooltipAttackSave='Wisdom',
              TooltipStatusApply='ApplyStatus(PANHANDLING_SHAME,100,2)')),
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
    (stats / 'HC_Spells_Round7.txt').write_text('\n\n'.join(spell_blocks) + '\n', encoding='utf-8')

    return {
        'base': {
            1: [SQUEEGEE_SMEAR],
            2: [SERVICE_VEST],
            7: [PISS_JUG],
            12: [GOVERNOR_PHOTO_OP],
        },
        'subclasses': {
            'TenderloinBiohazard': {3: [FOIL_BLOWBACK]},
            'VeniceBoardwalkBrawler': {10: [ROID_RAGE]},
            'OverpassRiverbedDweller': {3: [EXTENSION_TAP]},
        },
        'existing_list_spells': {
            'BART_L10': EMERGENCY_GATE,
            'Beachborn_L5': BOTOX_FREEZE,
            'Siliconite_L5': POLYCULE_CALENDAR,
            'InlandEmperor_L1': ALTIMA_REV,
        },
    }
