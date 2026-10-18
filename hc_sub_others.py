"""Venice, Tenderloin and Overpass level 4/5/7/8/9/11 content.

Vanilla evidence, relative to temp_race/Public (all five layers searched;
donors checked for Honour overrides by validation/test_sub_others.py).
Numeric radii, durations, dice and costs are deliberate adaptations.
SpellSuccess / SpellFail use the Thunderwave half-on-save pattern at
Shared/Stats/Generated/Data/Spell_Zone.txt:294-295. HC_Junk is the existing
mod resource, not a vanilla token. Constant passives copy the plain
DisplayName/Description/Boosts PassiveData shape of ARM_Ambusher_1_Passive.
- new entry "Zone_GustOfWind": Shared/Stats/Generated/Data/Spell_Zone.txt:235
- Spell_Evocation_GustOfWind: Shared/Stats/Generated/Data/Spell_Zone.txt:249
- Character() and not Ally() and not Dead(): Shared/Stats/Generated/Data/Spell_Rush.txt:262
- DealDamage(2d8,Bludgeoning,Magical): SharedDev/Stats/Generated/Data/Spell_Target.txt:6942
- ApplyStatus(PRONE,100,1): Shared/Stats/Generated/Data/Spell_Projectile.txt:386
- SavingThrow(Ability.Dexterity, SourceSpellDC()): Shared/Stats/Generated/Data/Spell_Projectile.txt:1154
- "Cooldown" "OncePerShortRest": Shared/Stats/Generated/Data/Spell_Projectile.txt:483
- new entry "Target_ShockingGrasp": Shared/Stats/Generated/Data/Spell_Target.txt:3134
- Spell_Enchantment_DissonantWhispers: Shared/Stats/Generated/Data/Spell_Target.txt:4529
- DealDamage(3d8,Psychic,Magical): SharedDev/Stats/Generated/Data/Spell_Target.txt:4630
- ApplyStatus(FRIGHTENED,100,2): Shared/Stats/Generated/Data/Spell_Projectile.txt:315
- Attack(AttackType.MeleeSpellAttack): Shared/Stats/Generated/Data/Spell_Rush.txt:148
- new entry "Target_Shatter": Shared/Stats/Generated/Data/Spell_Target.txt:7850
- Spell_Evocation_Shatter: Shared/Stats/Generated/Data/Spell_Target.txt:7861
- DealDamage(4d8,Thunder,Magical): Shared/Stats/Generated/Data/Spell_Projectile.txt:937
- ApplyStatus(STUNNED,100,1): Shared/Stats/Generated/Data/Spell_Target.txt:9218
- SavingThrow(Ability.Wisdom, SourceSpellDC()): Shared/Stats/Generated/Data/Spell_Projectile.txt:1854
- "Cooldown" "OncePerRest": Shared/Stats/Generated/Data/Spell_Projectile.txt:230
- Spell_Conjuration_StinkingCloud: Shared/Stats/Generated/Data/Spell_Target.txt:8139
- DealDamage(2d8,Poison,Magical): Shared/Stats/Generated/Data/Spell_Projectile.txt:854
- ApplyStatus(POISONED,100,2): Shared/Stats/Generated/Data/Spell_Projectile.txt:1695
- SavingThrow(Ability.Constitution, SourceSpellDC()): Shared/Stats/Generated/Data/Spell_Shout.txt:3416
- new entry "Target_ViciousMockery": Shared/Stats/Generated/Data/Spell_Target.txt:6164
- Spell_Necromancy_Blindness: Shared/Stats/Generated/Data/Spell_Target.txt:3794
- DealDamage(3d8,Necrotic,Magical): Shared/Stats/Generated/Data/Status_BOOST.txt:4876
- ApplyStatus(BLINDED,100,2): Shared/Stats/Generated/Data/Spell_Target.txt:10352
- new entry "Target_StinkingCloud": Shared/Stats/Generated/Data/Spell_Target.txt:8131
- DealDamage(4d8,Poison,Magical): Shared/Stats/Generated/Data/Spell_Projectile.txt:987
- GROUND:CreateSurface(6,10,StinkingCloud,true): Shared/Stats/Generated/Data/Spell_Target.txt:8136
- "SpellFlags" "HasVerbalComponent;HasSomaticComponent;IsConcentration;IsSpell": Shared/Stats/Generated/Data/Spell_Shout.txt:1594
- new entry "Zone_BurningHands": Shared/Stats/Generated/Data/Spell_Zone.txt:55
- Spell_Evocation_BurningHands: Shared/Stats/Generated/Data/Spell_Zone.txt:69
- DealDamage(2d8,Fire,Magical): Shared/Stats/Generated/Data/Spell_Projectile.txt:820
- ApplyStatus(DAZED,100,1): SharedDev/Stats/Generated/Data/Passive.txt:964
- Spell_Transmutation_CreateWater: Shared/Stats/Generated/Data/Spell_Target.txt:7246
- DealDamage(3d8,Bludgeoning,Magical): SharedDev/Stats/Generated/Data/Spell_Target.txt:6974
- Force(6): Shared/Stats/Generated/Data/Spell_Shout.txt:3448
- SavingThrow(Ability.Strength, SourceSpellDC()): Shared/Stats/Generated/Data/Spell_Projectile.txt:3980
- "SurfaceType" "Water": Gustav/Stats/Generated/Data/Spell_Zone.txt:49
- "SurfaceGrowStep" "5": Shared/Stats/Generated/Data/Spell_Zone.txt:63
- "SurfaceGrowInterval" "10": Shared/Stats/Generated/Data/Spell_Zone.txt:64
- DealDamage(4d8,Bludgeoning,Magical): SharedDev/Stats/Generated/Data/Spell_Target.txt:6985
- GROUND:CreateSurface(2,2,Mud): Shared/Stats/Generated/Data/Spell_Target.txt:10506
- Spell_Illusion_Blur: Shared/Stats/Generated/Data/Spell_Shout.txt:321
- new entry "ARM_Ambusher_1_Passive": SharedDev/Stats/Generated/Data/Passive.txt:3789
- AC(1): Shared/Stats/Generated/Data/Armor.txt:230
- Spell_Abjuration_MageArmor: Shared/Stats/Generated/Data/Passive.txt:394
- Advantage(SavingThrow,Strength): Shared/Stats/Generated/Data/Passive.txt:1286
- Spell_Enchantment_Heroism: Shared/Stats/Generated/Data/Spell_Target.txt:2236
- CharacterWeaponDamage(1d6): Shared/Stats/Generated/Data/Passive.txt:1852
- Advantage(Skill,Intimidation): Shared/Stats/Generated/Data/Status_BOOST.txt:4961
- Spell_Abjuration_ProtectionFromEnergy: Shared/Stats/Generated/Data/Spell_Target.txt:2896
- Resistance(Acid,Resistant): Shared/Stats/Generated/Data/Status_BOOST.txt:3980
- Spell_Abjuration_ProtectionFromPoison: Shared/Stats/Generated/Data/Spell_Target.txt:3049
- Resistance(Poison,Resistant): Shared/Stats/Generated/Data/Armor.txt:1241
- ActionResource(Movement,3,0): Shared/Stats/Generated/Data/Passive.txt:2065
- Spell_Necromancy_Contagion: SharedDev/Stats/Generated/Data/Passive.txt:1918
- StatusImmunity(SG_Poisoned): Shared/Stats/Generated/Data/Status_BOOST.txt:7184
- DamageBonus(2): Shared/Stats/Generated/Data/Status_BOOST.txt:5903
- Spell_Abjuration_Stoneskin: SharedDev/Stats/Generated/Data/Spell_Target.txt:2469
- StatusImmunity(SG_Prone): Shared/Stats/Generated/Data/Status_DOWNED.txt:18
- Spell_Abjuration_ShieldOfFaith: Shared/Stats/Generated/Data/Spell_Target.txt:5951
- Advantage(SavingThrow,Dexterity): Shared/Stats/Generated/Data/Passive.txt:573
- ActionResource(BonusActionPoint,1,0): Shared/Stats/Generated/Data/Passive.txt:768
- Advantage(Skill,Athletics): Shared/Stats/Generated/Data/Passive.txt:2691
- "Shape" "Square": Shared/Stats/Generated/Data/Spell_Zone.txt:261
- "Shape" "Cone": Shared/Stats/Generated/Data/Spell_Zone.txt:23
- "SurfaceLifetime": Shared/Stats/Generated/Data/Spell_Zone.txt:7
- ActionPoint:1: Shared/Stats/Generated/Data/Armor.txt:5
- BonusActionPoint:1: Shared/Stats/Generated/Data/Character.txt:24
- "TooltipOnSave": Shared/Stats/Generated/Data/Spell_Projectile.txt:1167
- "MemoryCost" "0": Shared/Stats/Generated/Data/Spell_Projectile.txt:572

UNVERIFIED: all gameplay, donor VFX, targeting, cloud and surface placement.
"""
from pathlib import Path
from hc_icon_keys import icon_for_spell

VENICE = 'VeniceBoardwalkBrawler'
TENDERLOIN = 'TenderloinBiohazard'
OVERPASS = 'OverpassRiverbedDweller'
SPELL_SPECS = []
PASSIVE_SPECS = []
HOSTILE = 'Character() and not Ally() and not Dead()'


def _spell(subclass, level, name, title, donor, icon, mechanics, joke, fields):
    SPELL_SPECS.append((subclass, level, name, title, donor, icon,
                        mechanics + ' ' + joke, fields))


def _passive(subclass, level, name, title, icon, mechanics, joke, boosts):
    PASSIVE_SPECS.append((subclass, level, name, title, icon,
                          mechanics + ' ' + joke, dict(Properties='Highlighted', Boosts=boosts)))


def _save(ability, dice, damage, status=''):
    return dict(SpellRoll=f'not SavingThrow(Ability.{ability}, SourceSpellDC())',
                SpellSuccess=f'DealDamage({dice},{damage},Magical)' + (';' + status if status else ''),
                SpellFail=f'DealDamage(({dice})/2,{damage},Magical)',
                DamageType=damage, TooltipDamageList=f'DealDamage({dice},{damage})',
                TooltipAttackSave=ability, TooltipStatusApply=status)


_spell(VENICE, 4, 'HC_Zone_RentedCruiserNoBrakes', 'Rented Cruiser, No Brakes',
       'Zone_GustOfWind', 'Spell_Evocation_GustOfWind',
       'Costs a bonus action and 1 Junk; once per short rest. Enemies in a 6 m by 2 m line make a Dexterity save, taking 2d8 Bludgeoning damage and falling Prone for 1 turn on failure, or half damage on success.',
       'The lock was a suggestion. So was stopping.',
       dict(UseCosts='BonusActionPoint:1;HC_Junk:1', Range='6', Base='2',
            **_save('Dexterity', '2d8', 'Bludgeoning', 'ApplyStatus(PRONE,100,1)')))
_passive(VENICE, 5, 'HC_HennaStillWet', 'Henna Still Wet', 'Spell_Illusion_Blur',
         'Gain +1 Armour Class. The unfinished ink makes you harder to pin down.',
         'The design is a snake. The snake is not finished. You are.', 'AC(1)')
_spell(VENICE, 7, 'HC_Target_PalmReadingAggressively', 'Palm Reading, Aggressively',
       'Target_ShockingGrasp', 'Spell_Enchantment_DissonantWhispers',
       'Costs an action and 2 Junk; once per short rest. Make a melee spell attack that deals 3d8 Psychic damage and Frightens the target for 2 turns on a hit.',
       'You will meet a tall man. He is the bouncer, and he has already decided.',
       dict(UseCosts='ActionPoint:1;HC_Junk:2', TargetRadius='1.5',
            SpellRoll='Attack(AttackType.MeleeSpellAttack)',
            SpellSuccess='DealDamage(3d8,Psychic,Magical);ApplyStatus(FRIGHTENED,100,2)',
            DamageType='Psychic', TooltipDamageList='DealDamage(3d8,Psychic)',
            TooltipStatusApply='ApplyStatus(FRIGHTENED,100,2)'))
_passive(VENICE, 8, 'HC_ThisSpotIsTakenSince1998', 'This Spot Is Taken (Since 1998)',
         'Spell_Abjuration_MageArmor',
         'Gain +1 Armour Class and advantage on Strength saving throws. These benefits are constant.',
         'The city grew up around the towel. The towel did not consult the city.',
         'AC(1);Advantage(SavingThrow,Strength)')
_spell(VENICE, 9, 'HC_Target_PierPressure', 'Pier Pressure',
       'Target_Shatter', 'Spell_Evocation_Shatter',
       'Costs an action and 2 Junk; once per long rest. Enemies in a 5 m radius within 12 m make a Wisdom save, taking 4d8 Thunder damage and becoming Stunned for 1 turn on failure, or half damage on success.',
       'The bucket has a jurisdiction and you are in it.',
       dict(UseCosts='ActionPoint:1;HC_Junk:2', Cooldown='OncePerRest', TargetRadius='12', AreaRadius='5',
            **_save('Wisdom', '4d8', 'Thunder', 'ApplyStatus(STUNNED,100,1)')))
_passive(VENICE, 11, 'HC_BoardwalkMainCharacter', 'Boardwalk Main Character',
         'Spell_Enchantment_Heroism',
         'Your weapon attacks deal an additional 1d6 damage. Gain advantage on Intimidation checks.',
         'The sunset is behind you. Unfortunately, so is the bench.',
         'CharacterWeaponDamage(1d6);Advantage(Skill,Intimidation)')
_passive(TENDERLOIN, 4, 'HC_Prop65CarcinogenWarningLabel', 'Prop 65 Carcinogen Warning Label',
         'Spell_Abjuration_ProtectionFromEnergy',
         'Gain resistance to Acid damage. This protection is constant.',
         'Known to the State of California to cause birth defects, reproductive harm, and immediate regret in anyone who tries to mug you outside the Civic Center Walgreens.',
         'Resistance(Acid,Resistant)')
_spell(TENDERLOIN, 5, 'HC_Target_CivicCenterBioSludgeGeyser', 'Civic Center Escalator Bio-Sludge Geyser',
       'Target_Shatter', 'Spell_Conjuration_StinkingCloud',
       'Costs an action and 1 Junk; once per short rest. Enemies in a 3 m radius within 9 m make a Constitution save, taking 2d8 Poison damage and becoming Poisoned for 2 turns on failure, or half damage on success.',
       'BART maintenance technicians put a yellow plastic cone in front of this escalator in 2017 and spiritually moved on.',
       dict(UseCosts='ActionPoint:1;HC_Junk:1', TargetRadius='9', AreaRadius='3',
            **_save('Constitution', '2d8', 'Poison', 'ApplyStatus(POISONED,100,2)')))
_passive(TENDERLOIN, 7, 'HC_HerdImmunityTotalExposure', 'Herd Immunity Through Total Exposure',
         'Spell_Abjuration_ProtectionFromPoison',
         'Gain resistance to Poison damage. Your movement speed increases by 3 m.',
         'Your immune system is no longer a biological defense mechanism; it is a gated community run by five competing hepatology textbook chapters.',
         'Resistance(Poison,Resistant);ActionResource(Movement,3,0)')
_spell(TENDERLOIN, 8, 'HC_Target_RedBagQuarantine', 'Department of Public Health Red-Bag Quarantine',
       'Target_ViciousMockery', 'Spell_Necromancy_Blindness',
       'Costs a bonus action and 2 Junk; once per short rest. An enemy within 12 m makes a Constitution save, taking 3d8 Necrotic damage and becoming Blinded for 2 turns on failure, or half damage on success.',
       'The city spent $4.2 million on a blue ribbon task force and concluded the best solution was wrapping the problem in heavy-duty contractor plastic.',
       dict(UseCosts='BonusActionPoint:1;HC_Junk:2', TargetRadius='12',
            **_save('Constitution', '3d8', 'Necrotic', 'ApplyStatus(BLINDED,100,2)')))
_spell(TENDERLOIN, 9, 'HC_Target_SteamGrateMiasma', 'Golden Gate Alley Steam-Grate Miasma',
       'Target_StinkingCloud', 'Spell_Conjuration_StinkingCloud',
       'Costs an action and 2 Junk; once per long rest. Enemies in a 6 m radius within 18 m make a Constitution save for 4d8 Poison damage, halved on success. The area holds a vanilla Stinking Cloud for 3 turns, affecting everyone inside with its normal choking effects and requiring concentration.',
       'Is it geothermal municipal heating, a ruptured Victorian sewer main, or somebody boiling denim in a puddle? Do not breathe in to find out.',
       dict(UseCosts='ActionPoint:1;HC_Junk:2', Cooldown='OncePerRest', TargetRadius='18', AreaRadius='6',
            SpellProperties='GROUND:CreateSurface(6,3,StinkingCloud,true)',
            **_save('Constitution', '4d8', 'Poison')))
_passive(TENDERLOIN, 11, 'HC_WalkingSuperfundSite', 'Walking Superfund Site',
         'Spell_Necromancy_Contagion_FilthFever',
         'Gain immunity to the Poisoned condition. Deal 2 additional damage with damaging attacks and spells.',
         "The EPA tried to designate your jacket as a federal cleanup zone, but the inspector's Geiger counter melted in the parking lot.",
         'StatusImmunity(SG_Poisoned);DamageBonus(2)')
_passive(OVERPASS, 4, 'HC_CaltransRiprapConcreteFooting', 'Caltrans Riprap & Concrete Footing',
         'Spell_Abjuration_Stoneskin',
         'Gain immunity to being knocked Prone. This footing is constant.',
         'Wait-listed for a duplex since 2016, you have achieved permanent structural harmony with a 45-degree sloped concrete flood channel.',
         'StatusImmunity(SG_Prone)')
_spell(OVERPASS, 5, 'HC_Zone_TailpipeDowndraft', '110 Freeway Tailpipe Carbon Monoxide Downdraft',
       'Zone_BurningHands', 'Spell_Evocation_BurningHands',
       'Costs an action and 1 Junk; once per short rest. Enemies in a 9 m cone make a Constitution save, taking 2d8 Fire damage and becoming Dazed for 1 turn on failure, or half damage on success.',
       'Living directly underneath eight lanes of bumper-to-bumper commuter traffic gives you complete authority over who gets to breathe oxygen today.',
       dict(UseCosts='ActionPoint:1;HC_Junk:1', Range='9',
            **_save('Constitution', '2d8', 'Fire', 'ApplyStatus(DAZED,100,1)')))
_passive(OVERPASS, 7, 'HC_LoadBearingCartRetainingWall', 'Load-Bearing Shopping Cart Retaining Wall',
         'Spell_Abjuration_ShieldOfFaith',
         'Gain advantage on Dexterity saving throws. Your personal retaining wall is always on duty.',
         'Three zip-ties, an IKEA bed slat, and a stolen Target cart have held up this embankment longer than the state bridge retrofit budget.',
         'Advantage(SavingThrow,Dexterity)')
_spell(OVERPASS, 8, 'HC_Zone_SandbagBreach', 'Atmospheric River Sandbag Breach',
       'Zone_GustOfWind', 'Spell_Transmutation_CreateWater',
       'Costs an action and 2 Junk; once per short rest. Enemies in a 12 m by 2 m line make a Strength save, taking 3d8 Bludgeoning damage, being pushed 6 m and falling Prone for 1 turn on failure, or half damage on success. Leaves water along the line for 3 turns.',
       "Meteorologists called it a 'once-in-a-thousand-year pineapple express' for the fourth Tuesday in a row.",
       dict(UseCosts='ActionPoint:1;HC_Junk:2', Range='12', Base='2',
            SurfaceType='Water', SurfaceLifetime='3', SurfaceGrowStep='5', SurfaceGrowInterval='10',
            **_save('Strength', '3d8', 'Bludgeoning', 'Force(6);ApplyStatus(PRONE,100,1)')))
_spell(OVERPASS, 9, 'HC_Target_FreewayOverpassCollapse', 'Forever-Under-Construction Freeway Overpass Collapse',
       'Target_Shatter', 'Spell_Evocation_Shatter',
       'Costs an action and 2 Junk; once per long rest. Enemies in a 5 m radius within 18 m make a Dexterity save, taking 4d8 Bludgeoning damage and becoming Stunned for 1 turn on failure, or half damage on success. Mud makes the area difficult terrain for 3 turns.',
       'Started under a 1998 bond measure, $900 million over budget, and finally completed directly on top of an enemy paladin.',
       dict(UseCosts='ActionPoint:1;HC_Junk:2', Cooldown='OncePerRest', TargetRadius='18', AreaRadius='5',
            SpellProperties='GROUND:CreateSurface(5,3,Mud)',
            **_save('Dexterity', '4d8', 'Bludgeoning', 'ApplyStatus(STUNNED,100,1)')))
_passive(OVERPASS, 11, 'HC_SovereignConcreteSpillway', 'Sovereign Citizen of the Concrete Spillway',
         'Spell_Evocation_GustOfWind',
         'Gain one additional bonus action each turn, usable for Shove or any other bonus action. Gain advantage on Athletics checks.',
         'According to Admiralty Maritime Law and a Sharpie sign taped to this storm drain, the Army Corps of Engineers has no jurisdiction over your living room.',
         'ActionResource(BonusActionPoint,1,0);Advantage(Skill,Athletics)')


def generate_sub_others(public_dir, add_loca, get_guid):
    """Write only this batch's stats; return grants for the lead's list plumbing."""
    stats = Path(public_dir) / 'Stats/Generated/Data'
    stats.mkdir(parents=True, exist_ok=True)
    grants = dict(base={}, subclasses={}, existing_list_spells={}, subclass_passives={})

    def block(name, kind, title, description, icon, fields, donor=None):
        values = dict(fields, Icon=icon_for_spell(name, icon),
                      DisplayName=add_loca(name + '_Name', title) + ';1',
                      Description=add_loca(name + '_Description', description) + ';1')
        if not name.startswith('HC_'):
            raise ValueError(name)
        for key, value in values.items():
            if any(char in value for char in ('"', '\n', '\r')):
                raise ValueError(f'Unsafe field {name}.{key}')
        lines = [f'new entry "{name}"', f'type "{kind}"']
        if donor:
            lines.append(f'using "{donor}"')
        return '\n'.join(lines + [f'data "{k}" "{v}"' for k,v in values.items()])

    base = dict(Level='0', Cooldown='OncePerShortRest', MemoryCost='0', RechargeValues='',
                RootSpellID='', SpellContainerID='', DescriptionParams='', ExtraDescription='',
                TooltipUpcastDescription='', TooltipUpcastDescriptionParams='', TooltipDamageList='',
                TooltipStatusApply='', TooltipAttackSave='', TooltipPermanentWarnings='', TooltipOnSave='',
                SpellProperties='', SpellRoll='', SpellSuccess='', SpellFail='', CastTextEvent='Cast',
                TargetConditions=HOSTILE)
    spells = []
    for sub, level, name, title, donor, icon, description, overrides in SPELL_SPECS:
        fields = dict(base)
        fields.update(overrides)
        spells.append(block(name, 'SpellData', title, description, icon, fields, donor))
        grants['subclasses'].setdefault(sub, {}).setdefault(level, []).append(name)
    passives = []
    for sub, level, name, title, icon, description, fields in PASSIVE_SPECS:
        passives.append(block(name, 'PassiveData', title, description, icon, fields))
        grants['subclass_passives'].setdefault(sub, {}).setdefault(level, []).append(name)
    (stats/'HC_Spells_SubOthers.txt').write_text('\n\n'.join(spells)+'\n', encoding='utf-8')
    (stats/'HC_Passives_SubOthers.txt').write_text('\n\n'.join(passives)+'\n', encoding='utf-8')
    return grants
