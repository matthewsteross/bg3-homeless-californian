"""BART L4/5/7/8/9/11: mobility and transit control; NOT gameplay-tested.

Vanilla evidence below is relative to temp_race/Public, Stats/Generated/Data:
Shared/Spell_Target.txt:5643 Target_MistyStep, 5648 GROUND:TeleportSource();
Shared/Spell_Target.txt:6164 Target_ViciousMockery save/target spell shape;
Shared/Spell_Zone.txt:283 Zone_Thunderwave, 292-294 save/half-damage branches;
Gustav/Spell_Zone.txt:78 Shape Cone; SharedDev/Spell_Teleportation.txt:99-114
Teleportation_Displacement_DisplacerBeast: TargetRadius 3, AreaRadius 18,
OriginSpellRoll/Success/Fail, OriginTargetConditions and TeleportSelf Yes.
GustavDev/Spell_Target.txt:2488-2495 HellCrawler proves the exact sequence
GROUND:CreateExplosion(projectile);GROUND:TeleportSource(). Its explosion donor
is GustavDev/Spell_Projectile.txt:1647-1663 Projectile_MAG_Infernal_MistyStep_Fireball.
Shared/Spell_Projectile.txt:871 3d8 Thunder; :977 4d8 Lightning. Damage dice/type
arguments are adapted, not claimed as verbatim copies of every full expression.
GustavDev/Spell_Shout.txt:1074 DAZED 1; Gustav/Passive.txt:178 FRIGHTENED 2;
GustavDev/Spell_Target.txt:2737 STUNNED 1; Gustav/Passive.txt:258 PRONE 1.
No vanilla DEAFENED found: omitted.
GustavDev/Spell_Shout.txt:1124 INVISIBILITY 1, :1821 DISENGAGE 1; SELF routing
also appears at :1821 (ApplyStatus(SELF,...)). Invisibility breaks per vanilla.
Gustav/Passive.txt:734-741 HP-gated BoostContext/BoostConditions passive shape;
Shared/Passive.txt:836 AC(1), :2248 ActionResource(Movement,3,0);
SharedDev/Status_BOOST.txt:39 ActionResource(Movement,1.5,0);
GustavDev/Passive.txt:515 Advantage(SavingThrow,Dexterity), :1809 terrain immunity,
:2200 StatusImmunity(SG_Prone); Gustav/Passive.txt:756 IgnoreLeaveAttackRange;
Honour/Passive.txt:579 DamageBonus(1d4,Force) (token reference only, no donor);
GustavDev/Status_BOOST.txt:3439 ActionResourceBlock(Movement);
Shared/Spell_Target.txt:5330 Target_HoldPerson; SharedDev/Spell_Target.txt:4065-4070
Target_HoldPerson_4 proves AmountOfTargets 3 (no concentration used here).
Gustav/Armor.txt:20 UnlockSpell(Target_SpeakWithDead_Amulet_CHA) generic unlock.
All five vanilla layers are checked for donor collisions/overrides in tests.
"""
from pathlib import Path

SUBCLASS = 'BARTPlatformMenace'
LEVELS = (4, 5, 7, 8, 9, 11)
EAR_POP = 'HC_Target_TransbayTubeEarPop'
BETWEEN = 'HC_Target_BetweenTheCars'
SCREECH = 'HC_Zone_WheelFlangeScreech'
BACKPACK = 'HC_Target_BackpackInTheDoors'
TRACK_JUMP = 'HC_Teleportation_RedLineEmergencyTrackJump'
LOCKDOWN = 'HC_Target_StationAgentIntercomLockdown'
IMPACT = 'HC_Projectile_BARTGangwayImpact'
ESCAPE = 'HC_Target_BARTQualifiedEscape'
DOORS = 'HC_BART_DOORS_HELD'

# name, title, description, fields; every description ends with its source joke.
PASSIVE_SPECS = [
    ('HC_PrioritySeatingSelfAppointed', 'Priority Seating, Self-Appointed',
     'Gain +1 Armour Class. This benefit is always active. The sign says yield. You sat down in the sign.',
     dict(Boosts='AC(1)')),
    ('HC_GapStepCommuterReflexes', 'Gap-Step Commuter Reflexes',
     'You are immune to being knocked Prone. You also have advantage on Dexterity saving throws. '
     'A decade of minding the jagged two-foot gap between train and concrete gives your lower joints the reactive suspension of a trophy truck.',
     dict(Boosts='StatusImmunity(SG_Prone);Advantage(SavingThrow,Dexterity)')),
    ('HC_CrowdedCarElbowRoom', 'Crowded Car Elbow Room',
     'Ignore difficult terrain, including mud, webs and vines. Gain +1.5 m movement speed and +1 Armour Class. '
     'Surviving the 5:15 PM commute out of Montgomery Street means your elbows naturally rest at eye level and your personal space bubble is weaponized.',
     dict(Boosts='StatusImmunity(DIFFICULT_TERRAIN);StatusImmunity(DIFFICULT_TERRAIN_MUD);StatusImmunity(DIFFICULT_TERRAIN_WEB);StatusImmunity(DIFFICULT_TERRAIN_VINES);ActionResource(Movement,1.5,0);AC(1)')),
    ('HC_DelayUnspecified', 'Delay, Unspecified',
     'Gain +3 m movement speed. While below 50% of your maximum Hit Points, moving out of melee range does not provoke opportunity attacks. '
     'Arrival time updated to: conceptually.',
     dict(Boosts='ActionResource(Movement,3,0)')),
    ('HC_TransbaySlipstreamMomentum', 'Transbay Slipstream Momentum',
     'While below 50% of your maximum Hit Points, your damaging attacks and spells deal an additional 1d4 Force damage. '
     'This benefit lasts while you remain below that threshold. '
     'Catching the vacuum draft behind an outbound Antioch express train adds four tons of kinetic municipal authority to your sucker punch.',
     dict(BoostContext='OnDamaged;OnHealed', BoostConditions='HasHPPercentageLessThan(50, context.Target)', Boosts='DamageBonus(1d4,Force)')),
    ('HC_BARTPoliceQualifiedEvasion', 'BART Police Qualified Evasion',
     'Gain Qualified Evasion: a bonus-action teleport of up to 9 m costing 2 Junk, once per short rest. '
     'It grants Disengage and Invisibility for 1 turn; attacking or casting a spell ends the invisibility. '
     'The exact instant high-visibility transit enforcement vests crest the escalator stairs, you seamlessly evaporate into an alternate jurisdictional dimension.',
     dict(Boosts=f'UnlockSpell({ESCAPE})')),
]
# Delay's conditional component is separate so its constant speed remains active.
DELAY_HELPER = 'HC_DelayUnspecifiedLowHP'

SPELL_SPECS = [
    (EAR_POP, 'Target_ViciousMockery', 'Transbay Tube Ear-Pop',
     'An enemy within 15 m makes a Constitution saving throw, taking 2d8 Thunder damage and becoming Dazed for 1 turn on failure, or half damage on success. '
     'Costs an action and 1 Junk; once per short rest. '
     "That deafening subterranean pop in your Eustachian tubes reminds you you're sealed inside a sixty-year-old tin tube beneath forty fathoms of saltwater.",
     dict(TargetRadius='15', SpellRoll='not SavingThrow(Ability.Constitution, SourceSpellDC())',
          SpellSuccess='DealDamage(2d8,Thunder,Magical);ApplyStatus(DAZED,100,1)', SpellFail='DealDamage((2d8)/2,Thunder,Magical)',
          TooltipDamageList='DealDamage(2d8,Thunder)', TooltipAttackSave='Constitution', TooltipStatusApply='ApplyStatus(DAZED,100,1)',
          UseCosts='ActionPoint:1;HC_Junk:1', Icon='Spell_Evocation_Thunderwave', DamageType='Thunder')),
    (BETWEEN, 'Target_MistyStep', 'Between the Cars',
     'Teleport to an unoccupied space within 9 m; enemies within 3 m of the destination make a Constitution saving throw, taking 2d8 Bludgeoning damage and falling Prone for 1 turn on failure, or half damage on success. '
     'Costs a bonus action and 1 Junk; once per short rest. The gangway invited you. The gangway lies.',
     dict(TargetRadius='9', TargetConditions="CanStand('') and not Character() and not Self()",
          SpellProperties=f'GROUND:CreateExplosion({IMPACT});GROUND:TeleportSource()', UseCosts='BonusActionPoint:1;HC_Junk:1',
          TooltipDamageList='DealDamage(2d8,Bludgeoning)', TooltipAttackSave='Constitution', TooltipStatusApply='ApplyStatus(PRONE,100,1)', Icon='Spell_Conjuration_MistyStep')),
    (SCREECH, 'Zone_Thunderwave', 'Wheel Flange Screech on the S-Curve',
     'Enemies in a 9 m cone make a Constitution saving throw, taking 3d8 Thunder damage and becoming Frightened for 2 turns on failure, or half damage on success. '
     'Costs an action and 2 Junk; once per short rest. '
     'Metal grinding against ungreased steel curves between Embarcadero and West Oakland hits 110 decibels of pure, unadulterated civic suffering.',
     dict(Shape='Cone', Range='9', Base='5', SpellRoll='not SavingThrow(Ability.Constitution, SourceSpellDC())',
          SpellSuccess='DealDamage(3d8,Thunder,Magical);ApplyStatus(FRIGHTENED,100,2)', SpellFail='DealDamage((3d8)/2,Thunder,Magical)',
          UseCosts='ActionPoint:1;HC_Junk:2', TooltipDamageList='DealDamage(3d8,Thunder)', TooltipAttackSave='Constitution',
          TooltipStatusApply='ApplyStatus(FRIGHTENED,100,2)', Icon='Spell_Evocation_Thunderwave', DamageType='Thunder')),
    (BACKPACK, 'Target_ViciousMockery', 'Backpack in the Doors',
     'An enemy within 3 m makes a Strength saving throw, taking 3d8 Bludgeoning damage and losing all movement for 1 turn on failure, or half damage on success. '
     'Costs an action and 1 Junk; once per short rest. The doors asked once. The doors do not ask twice.',
     dict(TargetRadius='3', SpellRoll='not SavingThrow(Ability.Strength, SourceSpellDC())',
          SpellSuccess=f'DealDamage(3d8,Bludgeoning,Magical);ApplyStatus({DOORS},100,1)', SpellFail='DealDamage((3d8)/2,Bludgeoning,Magical)',
          UseCosts='ActionPoint:1;HC_Junk:1', TooltipDamageList='DealDamage(3d8,Bludgeoning)', TooltipAttackSave='Strength',
          TooltipStatusApply=f'ApplyStatus({DOORS},100,1)', Icon='Spell_Enchantment_HoldPerson', DamageType='Bludgeoning')),
    (TRACK_JUMP, 'Teleportation_Displacement_DisplacerBeast', 'Red-Line Emergency Track Jump',
     'Teleport up to 18 m; enemies within 3 m of your departure point make a Dexterity saving throw, taking 4d8 Lightning damage on failure or half damage on success. '
     'Costs a bonus action and 2 Junk; once per short rest. '
     'Dropping off the platform edge onto live rail ballast is strictly illegal, universally fatal, and gets you to the opposite track three minutes faster.',
     dict(TargetRadius='3', AreaRadius='18', TargetConditions="CanStand('') and not Character() and not Self()",
          SpellProperties='GROUND:TeleportSource()', OriginSpellProperties='', OriginSpellRoll='not SavingThrow(Ability.Dexterity, SourceSpellDC())',
          OriginSpellSuccess='DealDamage(4d8,Lightning,Magical)', OriginSpellFail='DealDamage((4d8)/2,Lightning,Magical)',
          OriginTargetConditions='Character() and not Ally() and not Self() and not Dead()', TeleportSelf='Yes', TeleportSurface='No',
          UseCosts='BonusActionPoint:1;HC_Junk:2', TooltipDamageList='DealDamage(4d8,Lightning)', TooltipAttackSave='Dexterity',
          Icon='Spell_Conjuration_MistyStep', DamageType='Lightning')),
    (LOCKDOWN, 'Target_HoldPerson', 'Station Agent Intercom Lockdown',
     'Choose up to three enemies within 18 m; each makes a Wisdom saving throw or becomes Stunned for 1 turn. '
     'Costs an action and 3 Junk; once per long rest. '
     'Locked safely behind three inches of scratched bulletproof plexiglass, the station agent hits the master gate toggle and immediately walks away for a 45-minute lunch break.',
     dict(TargetRadius='18', AmountOfTargets='3', SpellFlags='IsSpell;HasVerbalComponent;IsHarmful;RangeIgnoreVerticalThreshold;IgnorePreviouslyPickedEntities', SpellRoll='not SavingThrow(Ability.Wisdom, SourceSpellDC())', SpellSuccess='ApplyStatus(STUNNED,100,1)',
          SpellFail='', UseCosts='ActionPoint:1;HC_Junk:3', Cooldown='OncePerRest', TooltipAttackSave='Wisdom',
          TooltipStatusApply='ApplyStatus(STUNNED,100,1)', TooltipOnSave='', Icon='Spell_Enchantment_HoldPerson')),
]


def generate_sub_bart(public_dir, add_loca, get_guid):
    """Write only own stats under the supplied Public mod directory."""
    stats = Path(public_dir) / 'Stats/Generated/Data'
    stats.mkdir(parents=True, exist_ok=True)

    def block(name, typ, title, description, fields, donor=None):
        values = dict(DisplayName=add_loca(name + '_Name', title) + ';1',
                      Description=add_loca(name + '_Description', description) + ';1', **fields)
        for key, value in values.items():
            if any(c in value for c in ('"', '\n', '\r')):
                raise ValueError(f'Unsafe field {name}.{key}')
        lines = [f'new entry "{name}"', f'type "{typ}"']
        if donor:
            lines.append(f'using "{donor}"')
        return '\n'.join(lines + [f'data "{k}" "{v}"' for k, v in values.items()])

    passives = [block(n, 'PassiveData', t, d, dict(Icon='Spell_Conjuration_MistyStep', Properties='Highlighted', **f))
                for n, t, d, f in PASSIVE_SPECS]
    passives.append(block(DELAY_HELPER, 'PassiveData', 'Delay, Unspecified: Evasion',
                          'Below 50% of your maximum Hit Points, moving out of melee range does not provoke opportunity attacks. '
                          'The movement benefit comes from Delay, Unspecified. Arrival time updated to: conceptually.',
                          dict(Properties='IsHidden', Icon='Spell_Conjuration_MistyStep', BoostContext='OnDamaged;OnHealed',
                               BoostConditions='HasHPPercentageLessThan(50, context.Target)', Boosts='IgnoreLeaveAttackRange')))
    (stats / 'HC_Passives_SubBART.txt').write_text('\n\n'.join(passives) + '\n', encoding='utf-8')
    status = block(DOORS, 'StatusData', 'Backpack in the Doors',
                   'Movement is blocked for 1 turn. Actions and bonus actions remain available. The doors asked once. The doors do not ask twice.',
                   dict(StatusType='BOOST', StackId=DOORS, StackType='Overwrite', TickType='EndTurn',
                        StatusPropertyFlags='InitiateCombat', Icon='Spell_Enchantment_HoldPerson', Boosts='ActionResourceBlock(Movement)'))
    (stats / 'HC_Status_SubBART.txt').write_text(status + '\n', encoding='utf-8')
    # Explicitly clear inherited damage, status and scaling tooltips and mechanics.
    common = dict(Level='0', MemoryCost='0', Cooldown='OncePerShortRest', RechargeValues='',
                  DescriptionParams='', ExtraDescription='', TooltipUpcastDescription='', TooltipUpcastDescriptionParams='',
                  TooltipDamageList='', TooltipStatusApply='', TooltipAttackSave='', TooltipPermanentWarnings='',
                  TooltipOnSave='f762efbb-f8f1-493e-b248-2de1567b4bd2', SpellProperties='', SpellRoll='', SpellSuccess='', SpellFail='',
                  TargetConditions='Character() and not Ally() and not Dead()', SpellFlags='IsSpell;HasVerbalComponent;IsHarmful;RangeIgnoreVerticalThreshold',
                  DamageType='', CastTextEvent='Cast')
    spells = []
    for name, donor, title, description, extra in SPELL_SPECS:
        fields = dict(common)
        fields.update(extra)
        if name in (BETWEEN, TRACK_JUMP):
            fields['SpellFlags'] = 'IsSpell;HasVerbalComponent;RangeIgnoreVerticalThreshold'
        if name == TRACK_JUMP:
            # Humanoid animation and VFX from Misty Step, not Displacer Beast assets.
            fields.update(SpellAnimation='dd86aa43-8189-4d9f-9a5c-454b5fe4a197,,;,,;39daf365-ec06-49a8-81f3-9032640699d7,,;5c400e93-0266-499c-a2e1-75d53358460f,,;cc5b0caf-3ed1-4711-a50d-11dc3f1fdc6a,,;,,;1715b877-4512-472e-9bd0-fd568a112e90,,;,,;,,',
                          PrepareSound='', PrepareLoopSound='', CastSound='Spell_Cast_Utility_MistyStep_L1to3', TargetSound='Spell_Impact_Utility_MistyStep_L1to3',
                          PrepareEffect='7121a488-7c9a-4ba1-a585-f79aaa77e97c', CastEffect='71859b27-bdda-44c3-8c65-7f142a1a2f60', TargetEffect='', SpellAnimationIntentType='')
        spells.append(block(name, 'SpellData', title, description, fields, donor))
    impact = dict(common)
    impact.update(AreaRadius='3', ExplodeRadius='3', TargetRadius='3', UseCosts='', Cooldown='',
                  Icon='Spell_Evocation_Thunderwave', SurfaceType='Sentinel', SurfaceLifetime='0',
                  SpellRoll='not SavingThrow(Ability.Constitution, SourceSpellDC())',
                  SpellSuccess='DealDamage(2d8,Bludgeoning,Magical);ApplyStatus(PRONE,100,1)',
                  SpellFail='DealDamage((2d8)/2,Bludgeoning,Magical)', DamageType='Bludgeoning',
                  TooltipDamageList='DealDamage(2d8,Bludgeoning)', TooltipAttackSave='Constitution', TooltipStatusApply='ApplyStatus(PRONE,100,1)')
    spells.append(block(IMPACT, 'SpellData', 'Between the Cars: Impact',
                        'Enemies within 3 m of the landing point make a Constitution saving throw against 2d8 Bludgeoning damage and Prone for 1 turn. '
                        'A successful save halves the damage and prevents Prone. The gangway invited you. The gangway lies.',
                        impact, 'Projectile_MAG_Infernal_MistyStep_Fireball'))
    escape = dict(common)
    escape.update(TargetRadius='9', TargetConditions="CanStand('') and not Character() and not Self()",
                  SpellProperties='GROUND:TeleportSource();ApplyStatus(SELF,DISENGAGE,100,1);ApplyStatus(SELF,INVISIBILITY,100,1)',
                  SpellFlags='IsSpell;HasVerbalComponent;RangeIgnoreVerticalThreshold', TooltipOnSave='',
                  UseCosts='BonusActionPoint:1;HC_Junk:2', Icon='Spell_Illusion_Invisibility')
    spells.append(block(ESCAPE, 'SpellData', 'Qualified Evasion', PASSIVE_SPECS[-1][2], escape, 'Target_MistyStep'))
    (stats / 'HC_Spells_SubBART.txt').write_text('\n\n'.join(spells) + '\n', encoding='utf-8')
    passive_grants = {level: [spec[0]] for level, spec in zip(LEVELS, PASSIVE_SPECS)}
    passive_grants[8].append(DELAY_HELPER)
    return dict(base={}, subclasses={SUBCLASS: {level: [spec[0]] for level, spec in zip(LEVELS, SPELL_SPECS)}},
                existing_list_spells={}, subclass_passives={SUBCLASS: passive_grants})
