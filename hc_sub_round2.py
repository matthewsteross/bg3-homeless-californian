"""Subclass round 2: twelve signature spells at class levels 5, 8 and 11 plus a level 7 needle spell, SHARED by all four subclasses.

Brainstormed by Gemini Flash (Venice, Tenderloin) and Gemini Argon (Overpass, BART), shaped into stats by the lead.
Every shape copies a stat already used by hc_sub_others.py / hc_sub_bart.py, which cite their vanilla evidence:
Zone_Thunderwave / Zone_GustOfWind (cone and line zones), Target_Shatter and Target_StinkingCloud (radius save spells
with GROUND:CreateSurface), Target_MistyStep (teleport), Shout_SecondWind (self shout applying a status), and BOOST statuses
with Boosts such as AC(), Resistance(,Resistant), ActionResource(Movement,,), Advantage(SavingThrow,) and DamageBonus().
Temporary hit points from the brainstorm were dropped (the functor is unverified); the buffs use AC, resistance and speed.
UNVERIFIED in game: everything. The sound and prop ideas from the brainstorm are in work/sc2-*.md.
"""
from pathlib import Path
from hc_icon_keys import icon_for_spell

VENICE = 'VeniceBoardwalkBrawler'
TENDERLOIN = 'TenderloinBiohazard'
OVERPASS = 'OverpassRiverbedDweller'
BART = 'BARTPlatformMenace'
HOSTILE = 'Character() and not Ally() and not Dead()'

ROLLER, SPOTTER, SLUDGED, HAZMAT, MANHOLE, PALLET, RAIL = (
    'HC_ROLLERBLADE_SLALOM', 'HC_MUSCLE_SPOTTER', 'HC_BIOHAZARD_SLUDGED', 'HC_FEDERAL_HAZMAT',
    'HC_MANHOLE_BUNKER', 'HC_PALLET_TIN_ARMOR', 'HC_THIRD_RAIL')

STATUS_SPECS = [
    (ROLLER, 'Rollerblade Slalom', 'Gain +6 m movement and moving away from enemies does not provoke opportunity attacks. Cruising at 25 mph on neon wheels through European tourists who never stood a chance.',
     'ActionResource(Movement,6,0);IgnoreLeaveAttackRange', 'Spell_Transmutation_Longstrider'),
    (SPOTTER, 'Muscle Beach Bro Spotter', 'Gain +2 Armour Class, advantage on Strength saving throws, and +1d6 weapon damage. He does not know your name, but he will scream LIGHT WEIGHT until the Absolute surrenders.',
     'AC(2);Advantage(SavingThrow,Strength);CharacterWeaponDamage(1d6)', 'Spell_Enchantment_Heroism'),
    (SLUDGED, 'Sludged', 'Attack rolls have disadvantage. You are wearing six months of pressurised sidewalk fermentation.',
     'Disadvantage(AttackRoll)', 'Spell_Necromancy_Contagion_FilthFever'),
    (HAZMAT, 'Federal Hazmat Disaster Declaration', 'Gain +2 Armour Class and resistance to Acid and Poison damage. You are officially an uninhabitable Superfund perimeter, eligible for expedited FEMA grants.',
     'AC(2);Resistance(Acid,Resistant);Resistance(Poison,Resistant)', 'Spell_Abjuration_ProtectionFromPoison'),
    (MANHOLE, 'Pop-Up Bunker', 'Gain +2 Armour Class. The Department of Water and Power welded this grate shut in 2021, which only made the foyer more exclusive.',
     'AC(2)', 'Spell_Abjuration_Stoneskin'),
    (PALLET, 'Pallet & Tin Armour', 'Gain resistance to Bludgeoning, Piercing and Slashing damage. Meets zero California Title 24 building codes, yet somehow survives wildfires, earthquakes, and three consecutive Caltrans abatement crews.',
     'Resistance(Bludgeoning,Resistant);Resistance(Piercing,Resistant);Resistance(Slashing,Resistant)', 'Spell_Abjuration_Stoneskin'),
    (RAIL, 'Third-Rail Overcharge', 'Gain +3 m movement, advantage on Dexterity saving throws and +1 Armour Class. PG&E charges forty-eight cents a kilowatt-hour at peak, whereas the track bed is free if your rubber soles are thick enough.',
     'ActionResource(Movement,3,0);Advantage(SavingThrow,Dexterity);AC(1)', 'Spell_Evocation_ShockingGrasp'),
]

SPELL_SPECS = []
# Matthew: the subclasses should share a common core and differ mildly, so every round-2 spell goes to all four subclasses.
ALL_SUBCLASSES = (VENICE, TENDERLOIN, OVERPASS, BART)


def _spell(subclass, level, name, title, donor, icon, mechanics, joke, fields):
    SPELL_SPECS.append((subclass, level, name, title, donor, icon, mechanics + ' ' + joke, fields))


def _save(ability, dice, damage, status=''):
    return dict(SpellRoll=f'not SavingThrow(Ability.{ability}, SourceSpellDC())',
                SpellSuccess=f'DealDamage({dice},{damage},Magical)' + (';' + status if status else ''),
                SpellFail=f'DealDamage(({dice})/2,{damage},Magical)',
                DamageType=damage, TooltipDamageList=f'DealDamage({dice},{damage})',
                TooltipAttackSave=ability, TooltipStatusApply=status)


def _self(status, turns):
    return dict(TargetConditions='', SpellProperties=f'ApplyStatus({status},100,{turns})',
                TooltipStatusApply=f'ApplyStatus({status},100,{turns})', SpellFlags='IsSpell;HasVerbalComponent;HasSomaticComponent')


_spell(VENICE, 5, 'HC_Shout_BoardwalkRollerbladeSlalom', 'Boardwalk Rollerblade Slalom', 'Shout_SecondWind', 'Spell_Transmutation_Longstrider',
       'Costs a bonus action and 1 Junk; once per short rest. For 2 turns gain +6 m movement and moving away from enemies does not provoke opportunity attacks.',
       'Cruising at 25 mph on neon polyurethane through European tourists who never stood a chance.',
       dict(UseCosts='BonusActionPoint:1;HC_Junk:1', **_self(ROLLER, 2)))
_spell(VENICE, 8, 'HC_Target_BreakdancerCardboardDrop', 'Breakdancer Cardboard Drop', 'Target_Shatter', 'Spell_Evocation_Shatter',
       'Costs an action and 2 Junk; once per short rest. Enemies in a 6 m radius within 18 m make a Dexterity save, taking 3d8 Bludgeoning damage and falling Prone for 1 turn on failure, or half damage on success. The slick cardboard leaves mud for 3 turns.',
       'Dropping a refrigerator box on the sidewalk subjects every bystander to a non-negotiable street-dance cypher.',
       dict(UseCosts='ActionPoint:1;HC_Junk:2', TargetRadius='18', AreaRadius='6',
            SpellProperties='GROUND:CreateSurface(6,3,Mud)', **_save('Dexterity', '3d8', 'Bludgeoning', 'ApplyStatus(PRONE,100,1)')))
_spell(VENICE, 11, 'HC_Shout_MuscleBeachBroSpotter', 'Muscle Beach Bro Spotter', 'Shout_SecondWind', 'Spell_Enchantment_Heroism',
       'Costs an action and 3 Junk; once per long rest. For 5 turns gain +2 Armour Class, advantage on Strength saving throws, and +1d6 weapon damage.',
       'He does not know your name and refuses to put on a tank top, but he will scream LIGHT WEIGHT until the Absolute surrenders.',
       dict(UseCosts='ActionPoint:1;HC_Junk:3', Cooldown='OncePerRest', **_self(SPOTTER, 5)))

_spell(TENDERLOIN, 5, 'HC_Zone_HazmatBackblast', 'Hazardous Materials Backblast', 'Zone_Thunderwave', 'Spell_Conjuration_StinkingCloud',
       'Costs a bonus action and 1 Junk; once per short rest. Enemies in a 4 m cone make a Dexterity save, taking 2d8 Acid damage and attacking with disadvantage for 1 turn on failure, or half damage on success.',
       'The mugger\'s dagger punctures your fourth surplus windbreaker, releasing six months of pressurised sidewalk fermentation.',
       dict(UseCosts='BonusActionPoint:1;HC_Junk:1', Shape='Cone', Range='4', Base='5',
            **_save('Dexterity', '2d8', 'Acid', f'ApplyStatus({SLUDGED},100,1)')))
_spell(TENDERLOIN, 7, 'HC_Shout_OversizedSharpsDisposal', 'Oversized Sharps Disposal', 'Shout_FeyPresence', 'Spell_Necromancy_Contagion_FilthFever',
       'Costs an action and 2 Junk; once per short rest. Enemies within 6 m make a Wisdom save, taking 3d6 Psychic damage and becoming Frightened for 2 turns on failure, or half damage on success. A questionable puddle spreads where it lands.',
       'The county sharps container is full, so you went with the bigger one. It is the size of a streetlight, it also lives at Powell Street Station, and nobody will make eye contact with it.',
       dict(UseCosts='ActionPoint:1;HC_Junk:2', TargetRadius='0', AreaRadius='6', TargetConditions='Enemy() and not Dead()', SpellProperties='GROUND:CreateSurface(4,3,Poison)',
            SpellFlags='IsSpell;HasVerbalComponent;HasSomaticComponent', **_save('Wisdom', '3d6', 'Psychic', 'ApplyStatus(FRIGHTENED,100,2)')))
_spell(TENDERLOIN, 8, 'HC_Target_UnpermittedBleachFogger', 'Unpermitted Bleach Fogger', 'Target_StinkingCloud', 'Spell_Conjuration_StinkingCloud',
       'Costs an action and 2 Junk; once per short rest. Enemies in a 6 m radius within 18 m make a Constitution save, taking 3d8 Acid damage and becoming Blinded for 2 turns on failure, or half damage on success. A vanilla Stinking Cloud lingers for 3 turns.',
       'Public Works promised a downtown sanitising sweep; what arrived was a chlorine cloud that etches glass and blinds archdevils.',
       dict(UseCosts='ActionPoint:1;HC_Junk:2', TargetRadius='18', AreaRadius='6',
            SpellProperties='GROUND:CreateSurface(6,3,StinkingCloud,true)', **_save('Constitution', '3d8', 'Acid', 'ApplyStatus(BLINDED,100,2)')))
_spell(TENDERLOIN, 11, 'HC_Shout_FederalHazmatDeclaration', 'Federal Hazmat Disaster Declaration', 'Shout_SecondWind', 'Spell_Abjuration_ProtectionFromPoison',
       'Costs a bonus action and 3 Junk; once per long rest. For 3 turns gain +2 Armour Class and resistance to Acid and Poison damage.',
       'Officially designated a Superfund perimeter, your mere biological existence qualifies you for expedited FEMA grants.',
       dict(UseCosts='BonusActionPoint:1;HC_Junk:3', Cooldown='OncePerRest', **_self(HAZMAT, 3)))

_spell(OVERPASS, 5, 'HC_Target_ManholeCoverPopUpBunker', 'Manhole Cover Pop-Up Bunker', 'Target_MistyStep', 'Spell_Conjuration_MistyStep',
       'Costs a bonus action and 1 Junk; once per short rest. Teleport up to 9 m and gain +2 Armour Class for 1 turn.',
       'The Department of Water and Power welded this grate shut in 2021, which only made the foyer more exclusive.',
       dict(UseCosts='BonusActionPoint:1;HC_Junk:1', TargetRadius='9', TargetConditions="CanStand('') and not Character() and not Self()",
            SpellFlags='IsSpell;HasVerbalComponent;RangeIgnoreVerticalThreshold',
            SpellProperties=f'GROUND:TeleportSource();ApplyStatus(SELF,{MANHOLE},100,1)'))
_spell(OVERPASS, 8, 'HC_Shout_PalletAndTinArmor', 'Corrugated Sheet-Metal & Pallet Armor', 'Shout_SecondWind', 'Spell_Abjuration_Stoneskin',
       'Costs a bonus action and 2 Junk; once per short rest. For 3 turns gain resistance to Bludgeoning, Piercing and Slashing damage.',
       'Meets zero California Title 24 building codes, yet survives wildfires, earthquakes and three consecutive Caltrans abatement crews.',
       dict(UseCosts='BonusActionPoint:1;HC_Junk:2', **_self(PALLET, 3)))
_spell(OVERPASS, 11, 'HC_Target_OrovilleSpillwayRupture', 'Oroville Dam Emergency Spillway Rupture', 'Target_Shatter', 'Spell_Transmutation_CreateWater',
       'Costs an action and 3 Junk; once per long rest. Enemies in a 6 m radius within 18 m make a Strength save, taking 5d8 Bludgeoning damage, falling Prone for 1 turn and being Slowed for 2 turns on failure, or half damage on success. Water covers the ground for 3 turns.',
       'State engineers called it minor seasonal flaking right before half of Butte County floated past Sacramento.',
       dict(UseCosts='ActionPoint:1;HC_Junk:3', Cooldown='OncePerRest', TargetRadius='18', AreaRadius='6',
            SpellProperties='GROUND:CreateSurface(6,3,Water)',
            **_save('Strength', '5d8', 'Bludgeoning', 'ApplyStatus(PRONE,100,1);ApplyStatus(SLOW,100,2)')))

_spell(BART, 5, 'HC_Zone_EmergencyBrakeHandlePull', 'Emergency Brake Handle Pull', 'Zone_Thunderwave', 'Spell_Evocation_Thunderwave',
       'Costs a bonus action and 1 Junk; once per short rest. Enemies in a 4 m cone make a Dexterity save, taking 2d8 Force damage and falling Prone for 1 turn on failure, or half damage on success.',
       'PENALTY FOR IMPROPER USE: $250 or six months in jail, assuming the operator ever walks back eight cars to check.',
       dict(UseCosts='BonusActionPoint:1;HC_Junk:1', Shape='Cone', Range='4', Base='5',
            **_save('Dexterity', '2d8', 'Force', 'ApplyStatus(PRONE,100,1)')))
_spell(BART, 8, 'HC_Shout_ThirdRailOvercharge', '700-Volt Third-Rail Overcharge', 'Shout_SecondWind', 'Spell_Evocation_ShockingGrasp',
       'Costs a bonus action and 2 Junk; once per short rest. For 3 turns gain +3 m movement, +1 Armour Class and advantage on Dexterity saving throws.',
       'PG&E charges forty-eight cents a kilowatt-hour at peak; the Oakland Wye track bed is free if your soles are thick enough.',
       dict(UseCosts='BonusActionPoint:1;HC_Junk:2', **_self(RAIL, 3)))
_spell(BART, 11, 'HC_Zone_DalyCityTurnbackRunaway', 'Daly City Turnback: Runaway 10-Car Train', 'Zone_GustOfWind', 'Spell_Evocation_GustOfWind',
       'Costs an action and 3 Junk; once per long rest. Enemies in a 12 m by 3 m line make a Dexterity save, taking 5d8 Thunder damage, being pushed 6 m and becoming Frightened and Dazed for 1 turn on failure, or half damage on success.',
       'This is a 10-car Antioch train; please stand back from the yellow line, because the train-control computer blue-screened in 1972.',
       dict(UseCosts='ActionPoint:1;HC_Junk:3', Cooldown='OncePerRest', Range='12', Base='3',
            **_save('Dexterity', '5d8', 'Thunder', 'Force(6);ApplyStatus(FRIGHTENED,100,1);ApplyStatus(DAZED,100,1)')))


def generate_sub_round2(public_dir, add_loca, get_guid):
    stats = Path(public_dir) / 'Stats/Generated/Data'
    stats.mkdir(parents=True, exist_ok=True)

    def block(name, kind, title, description, fields, donor=None):
        values = dict(fields, DisplayName=add_loca(name + '_Name', title) + ';1',
                      Description=add_loca(name + '_Description', description) + ';1')
        for key, value in values.items():
            if any(char in value for char in ('"', '\n', '\r')):
                raise ValueError(f'Unsafe field {name}.{key}')
        lines = [f'new entry "{name}"', f'type "{kind}"']
        if donor:
            lines.append(f'using "{donor}"')
        return '\n'.join(lines + [f'data "{k}" "{v}"' for k, v in values.items()])

    statuses = [block(name, 'StatusData', title, description,
                      dict(StatusType='BOOST', StackId=name, StackType='Overwrite', TickType='EndTurn',
                           Icon=icon_for_spell(name, icon), Boosts=boosts))
                for name, title, description, boosts, icon in STATUS_SPECS]
    (stats / 'HC_Status_SubRound2.txt').write_text('\n\n'.join(statuses) + '\n', encoding='utf-8')

    base = dict(Level='0', Cooldown='OncePerShortRest', MemoryCost='0', RechargeValues='',
                RootSpellID='', SpellContainerID='', DescriptionParams='', ExtraDescription='',
                TooltipUpcastDescription='', TooltipUpcastDescriptionParams='', TooltipDamageList='',
                TooltipStatusApply='', TooltipAttackSave='', TooltipPermanentWarnings='', TooltipOnSave='',
                SpellProperties='', SpellRoll='', SpellSuccess='', SpellFail='', CastTextEvent='Cast',
                TargetConditions=HOSTILE)
    spells = []
    grants = dict(base={}, subclasses={}, existing_list_spells={})
    for sub, level, name, title, donor, icon, description, overrides in SPELL_SPECS:
        fields = dict(base)
        fields.update(overrides)
        fields['Icon'] = icon_for_spell(name, icon)
        spells.append(block(name, 'SpellData', title, description, fields, donor))
        grants['subclasses'].setdefault(sub, {}).setdefault(level, []).append(name)
        for other in ALL_SUBCLASSES:
            if other == sub:
                continue
            grants['subclasses'].setdefault(other, {}).setdefault(level, []).append(name)
    (stats / 'HC_Spells_SubRound2.txt').write_text('\n\n'.join(spells) + '\n', encoding='utf-8')
    return grants
