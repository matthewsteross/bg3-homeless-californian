"""Homeless Californian Level 12 Signature Capstone: Squatter's Rights.

Local development candidate, adapted from the Solo Gemini draft; not gameplay-tested.
Requires 12 Homeless Californian class levels via subclass progression tables (ptype=1).
Preserves existing base-class Level 12 feat/ASI (AllowImprovement=true) and Call 311 (Shout_Call311).
All mechanics use evidenced vanilla BG3 syntax; unproven/unsafe ideas are excluded.

UNVERIFIED STATUS NOTE:
Citing field existence and syntax in shipped game data is not proof of in-game engine
behavior, AI combat interaction, or boss encounter stability. Position swaps (SwapPlaces()),
aura propagation (AuraStatuses), and turn-boundary resource timing remain unverified in
live gameplay until tested in an active game session. This module remains an unintegrated draft.
"""
from pathlib import Path
import sys

# Safe import of icon resolver with graceful fallback
try:
    from hc_icon_keys import icon_for_spell
except ImportError:
    repo_root = Path(__file__).resolve().parents[2]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    try:
        from hc_icon_keys import icon_for_spell
    except ImportError:
        def icon_for_spell(spell, fallback):
            return fallback


def generate_capstone(public_dir, add_loca, get_guid):
    """Generate Squatter's Rights capstone statuses, spells, and progression grants.
    
    Returns standard grant dictionary matching hc_expansion / generate_local_expansion:
    {
        'base': {},  # Base class level 12 is untouched, preserving Feat & Call 311
        'subclasses': {
            'TenderloinBiohazard': {12: ['HC_Shout_SquattersRights_Tenderloin']},
            'VeniceBoardwalkBrawler': {12: ['HC_Shout_SquattersRights_Venice']},
            'BARTPlatformMenace': {12: ['HC_Shout_SquattersRights_BART']},
        },
        'resource_increases': {}
    }
    """
    public = Path(public_dir)
    stats_dir = public / 'Stats/Generated/Data'
    stats_dir.mkdir(parents=True, exist_ok=True)

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
        return {
            'DisplayName': add_loca(name + '_Name', title) + ';1',
            'Description': add_loca(name + '_Description', description) + ';1'
        }

    # -------------------------------------------------------------------------
    # 1. Capstone Statuses
    # -------------------------------------------------------------------------
    # Vanilla citations:
    # - ACTION_SURGE: Shared/Status_BOOST.txt:1646-1655
    #   data "Boosts" "ActionResource(ActionPoint,1,0)", TickType "EndTurn"
    # - TENDERLOIN_MIASMA: src/HomelessCalifornian/Public/HomelessCalifornian/Stats/Generated/Data/Status_BOOST.txt:20-30
    #   data "AuraRadius" "3", data "AuraStatuses" "TARGET:IF(Character() and Enemy() and not Dead()):ApplyStatus(FECAL_STENCH_AURA)"
    #
    # Evidentiary & Engine safety notes:
    # - StatusImmunity(FORCE) rejected (per ROOT-REVIEW.md line 23; does not grant displacement immunity).
    # - Multi-turn extra AP rejected (only 1-turn ACTION_SURGE is evidenced by vanilla data).
    # - AllCloseAttacks removed (not in any vanilla layer); using evidenced Advantage(AttackRoll).
    # - In-game engine behavior for auras and swaps remains unverified until live playtesting.
    # -------------------------------------------------------------------------
    status_blocks = []

    # Tenderloin Status: Condemned Block (3 turns)
    # Radiates FECAL_STENCH_AURA within 6 m, protects concentration, unlocks active condemnation projectile.
    fields_tl = dict(
        StatusType='BOOST',
        StackId='HC_SQUATTERS_TENDERLOIN',
        StackType='Overwrite',
        TickType='EndTurn',
        Icon='Spell_SlingPoop',
        AuraRadius='6',
        AuraStatuses='TARGET:IF(Character() and Enemy() and not Dead()):ApplyStatus(FECAL_STENCH_AURA)',
        Boosts='Advantage(Concentration);UnlockSpell(HC_Projectile_BiohazardCondemn)'
    )
    fields_tl.update(loca(
        'HC_SQUATTERS_TENDERLOIN',
        "Squatter's Rights: Condemned Block",
        'Declared a municipal biohazard condemnation zone for 3 turns. Enemies within 6 m suffer Fecal Stench (disadvantage on attack rolls and turn-based poison damage). You gain advantage on Concentration checks and can cast Condemn.'
    ))
    status_blocks.append(emit('HC_SQUATTERS_TENDERLOIN', 'StatusData', fields_tl))

    # Venice Status: Eviction Defense (3 turns)
    # Pairs with 1-turn vanilla ACTION_SURGE applied on shout activation.
    # Unlocks Chair-Leg Shiv without needing Heirloom Furniture first; grants Advantage(AttackRoll).
    fields_vn = dict(
        StatusType='BOOST',
        StackId='HC_SQUATTERS_VENICE',
        StackType='Overwrite',
        TickType='EndTurn',
        Icon='Skill_Fighter_ActionSurge',
        Boosts='UnlockSpell(HC_Target_ChairLegShiv_Eviction);Advantage(AttackRoll)'
    )
    fields_vn.update(loca(
        'HC_SQUATTERS_VENICE',
        "Squatter's Rights: Eviction Defense",
        'Holding the property by force for 3 turns. You gain advantage on attack rolls, and can strike with an Emergency Chair-Leg Shiv using a Bonus Action once per turn without preparing furniture first.'
    ))
    status_blocks.append(emit('HC_SQUATTERS_VENICE', 'StatusData', fields_vn))

    # BART Status: Last Train Out (3 turns)
    # Unlocks allied Platform Rescue (willing ally swap) and bonus-action Wrong Platform Express (enemy swap with Wisdom save).
    # Grants +1 Reaction and +4.5 m Movement.
    fields_bt = dict(
        StatusType='BOOST',
        StackId='HC_SQUATTERS_BART',
        StackType='Overwrite',
        TickType='EndTurn',
        Icon='Action_BenignTransposition',
        Boosts='UnlockSpell(HC_Target_PlatformRescue);UnlockSpell(HC_Target_WrongPlatform_Express);ActionResource(ReactionActionPoint,1,0);ActionResource(Movement,4.5,0)'
    )
    fields_bt.update(loca(
        'HC_SQUATTERS_BART',
        "Squatter's Rights: Last Train Out",
        'You command the transit interchange for 3 turns. Gain +1 Reaction and +4.5 m movement speed. Unlocks Platform Rescue to swap positions with willing allies, and Wrong Platform Express to swap enemies using a Bonus Action.'
    ))
    status_blocks.append(emit('HC_SQUATTERS_BART', 'StatusData', fields_bt))

    (stats_dir / 'HC_Status_Capstone.txt').write_text('\n'.join(status_blocks), encoding='utf-8')

    # -------------------------------------------------------------------------
    # 2. Capstone Spells
    # -------------------------------------------------------------------------
    spells = []

    def spell(name, donor, title, description, **fields):
        data = dict(
            Level='0', Cooldown='', DescriptionParams='', ExtraDescription='',
            MemoryCost='0', RechargeValues='', TooltipUpcastDescription='',
            TooltipUpcastDescriptionParams='', TooltipDamageList='',
            TooltipStatusApply='', TooltipAttackSave='', TooltipPermanentWarnings='',
            SpellProperties='', SpellSuccess='', SpellFail='', CastTextEvent='Cast'
        )
        data.update(fields)
        data['Icon'] = icon_for_spell(name, data.get('Icon', ''))
        data.update(loca(name, title, description))
        spells.append(emit(name, 'SpellData', data, donor))

    # Shared properties across all 3 activation shouts:
    # - Bonus Action activation
    # - Cooldown: OncePerRest (vanilla engine enum for Long Rest cooldown)
    # - Restores Junk to full (7) to feed toolkit and capstone sub-actions
    # - Donor: Shout_SecondWind (clean self-buff shout)

    # Tenderloin Activation Shout
    spell(
        'HC_Shout_SquattersRights_Tenderloin',
        'Shout_SecondWind',
        "Squatter's Rights: Condemned Block",
        "Bonus Action: Claim this territory as a declared biohazard zone for 3 turns, and restore all Junk. Radiates Fecal Stench to all enemies within 6 m, protects concentration, and unlocks Condemn. Once per Long Rest. Possession is nine-tenths of the law. You have been possessing since Tuesday.",
        UseCosts='BonusActionPoint:1',
        Cooldown='OncePerRest',
        Icon='Spell_SlingPoop',
        SpellProperties='ApplyStatus(HC_SQUATTERS_TENDERLOIN,100,3);RestoreResource(HC_Junk,100%,0)',
        TooltipStatusApply='ApplyStatus(HC_SQUATTERS_TENDERLOIN,100,3)'
    )

    # Tenderloin Active Payload: Condemn Block (unlocked during capstone)
    # Donor: Projectile_AcidSplash (SpellType Projectile, cleared area radius, explicit enemy targeting)
    # Valid save / half damage syntax evidenced by donor pattern in generate_mod.py
    spell(
        'HC_Projectile_BiohazardCondemn',
        'Projectile_AcidSplash',
        'Condemn Block',
        'Hurl concentrated biohazard waste at an enemy: 3d8 Poison damage on a failed Constitution save (half damage on save), and inflicts Fecal Stench for 3 turns. Costs 1 Action and 2 Junk. Once per turn while Condemned Block is active.',
        SpellType='Projectile',
        UseCosts='ActionPoint:1;HC_Junk:2',
        Cooldown='OncePerTurn',
        TargetRadius='9',
        AreaRadius='0',
        ExplodeRadius='0',
        SpellFlags='IsSpell;IsHarmful;HasVerbalComponent;HasSomaticComponent',
        TargetConditions='Character() and Enemy() and not Dead()',
        RequirementConditions="HasStatus('HC_SQUATTERS_TENDERLOIN')",
        SpellRoll='not SavingThrow(Ability.Constitution,SourceSpellDC())',
        SpellSuccess='DealDamage(3d8,Poison,Magical);ApplyStatus(FECAL_STENCH,100,3)',
        SpellFail='DealDamage(3d8/2,Poison,Magical)',
        TooltipDamageList='DealDamage(3d8,Poison)',
        TooltipAttackSave='Constitution',
        TooltipStatusApply='ApplyStatus(FECAL_STENCH,100,3)',
        DamageType='Poison',
        Icon='Spell_SlingPoop'
    )

    # Venice Activation Shout
    # Applies 1-turn vanilla ACTION_SURGE directly (Shared/Spell_Shout.txt:1 & Shared/Status_BOOST.txt:1646).
    # Grants +1 Action Point immediately for turn 1, plus 3 turns of Eviction Defense status.
    spell(
        'HC_Shout_SquattersRights_Venice',
        'Shout_SecondWind',
        "Squatter's Rights: Eviction Defense",
        "Bonus Action: Surge into total territorial defense. Gain an immediate additional Action this turn (Action Surge), 3 turns of Eviction Defense (advantage on attack rolls, bonus-action Chair-Leg Shiv once per turn), and restore all Junk. Once per Long Rest. Some assembly was required. None will be accepted from the landlord.",
        UseCosts='BonusActionPoint:1',
        Cooldown='OncePerRest',
        Icon='Skill_Fighter_ActionSurge',
        SpellProperties='ApplyStatus(ACTION_SURGE,100,1);ApplyStatus(HC_SQUATTERS_VENICE,100,3);RestoreResource(HC_Junk,100%,0)',
        TooltipStatusApply='ApplyStatus(ACTION_SURGE,100,1);ApplyStatus(HC_SQUATTERS_VENICE,100,3)'
    )

    # Venice Capstone Shiv Attack (unlocked during capstone)
    # Bonus Action melee weapon attack with explicit OncePerTurn cooldown.
    # Donor: Target_BrokenBottleShank
    spell(
        'HC_Target_ChairLegShiv_Eviction',
        'Target_BrokenBottleShank',
        'Emergency Chair-Leg Shiv',
        'Bonus Action melee weapon attack: 2d6 + Constitution modifier Piercing damage. Ready-to-use splinter weapon usable once per turn while Eviction Defense is active without needing to smash furniture first.',
        UseCosts='BonusActionPoint:1',
        Cooldown='OncePerTurn',
        Icon='Spell_BottleShank',
        DamageType='Piercing',
        TargetRadius='MeleeMainWeaponRange',
        RequirementConditions="HasStatus('HC_SQUATTERS_VENICE')",
        SpellRoll='Attack(AttackType.MeleeWeaponAttack)',
        SpellSuccess='DealDamage(2d6+ConstitutionModifier,Piercing)',
        TooltipDamageList='DealDamage(2d6+ConstitutionModifier,Piercing)',
        TooltipAttackSave='MeleeWeaponAttack'
    )

    # BART Activation Shout
    # Grants 3 turns of Last Train Out, +1 Reaction, +4.5 m Movement, and restores 7 Junk.
    spell(
        'HC_Shout_SquattersRights_BART',
        'Shout_SecondWind',
        "Squatter's Rights: Last Train Out",
        "Bonus Action: Establish undisputed control of the transit hub for 3 turns, and restore all Junk. Gain +1 Reaction, +4.5 m movement speed, and unlock Platform Rescue (allied position swap) and Wrong Platform Express (bonus-action enemy position swap). Once per Long Rest. Stand clear of the closing doors.",
        UseCosts='BonusActionPoint:1',
        Cooldown='OncePerRest',
        Icon='Action_BenignTransposition',
        SpellProperties='ApplyStatus(HC_SQUATTERS_BART,100,3);RestoreResource(HC_Junk,100%,0)',
        TooltipStatusApply='ApplyStatus(HC_SQUATTERS_BART,100,3)'
    )

    # BART Rescue Tool: Platform Rescue
    # Consensual swap with a willing ally within 12 m.
    # HasHighGroundRangeExtension removed to enforce exact 12 m boundary.
    # Donor: Target_BenignTransposition_Teleport
    spell(
        'HC_Target_PlatformRescue',
        'Target_BenignTransposition_Teleport',
        'Platform Rescue',
        'Bonus Action: Swap positions with a willing ally within 12 m. Costs 1 Bonus Action and 1 Junk. Pull an overextended partner back to safety or slingshot them into position.',
        UseCosts='BonusActionPoint:1;HC_Junk:1',
        Icon='Action_BenignTransposition',
        TargetRadius='12',
        TargetConditions='Character() and Ally() and not Self() and not Dead()',
        RequirementConditions="HasStatus('HC_SQUATTERS_BART')",
        SpellRoll='',
        SpellProperties='SwapPlaces()',
        SpellFlags='HasVerbalComponent;RangeIgnoreVerticalThreshold'
    )

    # BART Reposition Tool: Wrong Platform Express
    # Bonus-action swap targeting an enemy within 9 m with mandatory Wisdom saving throw.
    # HasHighGroundRangeExtension removed to enforce exact 9 m boundary.
    # Donor: Target_BenignTransposition_Teleport
    spell(
        'HC_Target_WrongPlatform_Express',
        'Target_BenignTransposition_Teleport',
        'Wrong Platform Express',
        'Bonus Action: Target an enemy within 9 m. On a failed Wisdom saving throw, instantly swap positions with it. Costs 1 Bonus Action and 1 Junk; once per turn while Last Train Out is active.',
        UseCosts='BonusActionPoint:1;HC_Junk:1',
        Cooldown='OncePerTurn',
        Icon='Action_BenignTransposition',
        TargetRadius='9',
        TargetConditions='Character() and Enemy() and not Self() and not Dead()',
        RequirementConditions="HasStatus('HC_SQUATTERS_BART')",
        SpellRoll='not SavingThrow(Ability.Wisdom,SourceSpellDC())',
        SpellSuccess='SwapPlaces()',
        SpellFail='ApplyStatus(SAVED_AGAINST_HOSTILE_SPELL,100,0)',
        TooltipAttackSave='Wisdom',
        SpellFlags='HasVerbalComponent;RangeIgnoreVerticalThreshold;IsHarmful'
    )

    (stats_dir / 'HC_Spells_Capstone.txt').write_text('\n'.join(spells), encoding='utf-8')

    # Grant mapping for root integration:
    # - Base class level 12 remains untouched, preserving existing AllowImprovement=true (Feat) and Shout_Call311.
    # - Each subclass receives its respective Squatter's Rights variant at subclass level 12.
    return {
        'base': {},
        'subclasses': {
            'TenderloinBiohazard': {12: ['HC_Shout_SquattersRights_Tenderloin']},
            'VeniceBoardwalkBrawler': {12: ['HC_Shout_SquattersRights_Venice']},
            'BARTPlatformMenace': {12: ['HC_Shout_SquattersRights_BART']},
        },
        'resource_increases': {}
    }


# -----------------------------------------------------------------------------
# Root Integration Mapping & Instructions
# -----------------------------------------------------------------------------
# When root integrates this draft into production:
# 1. In generate_mod.py:
#    In generate_progressions_lsx(), add the 3 subclass level 12 progression nodes:
#
#    prog("Prog_Tenderloin_L12", "TenderloinBiohazard", 12, SUBCLASS_TENDERLOIN_TABLE_UUID, ptype=1)
#    prog("Prog_Venice_L12", "VeniceBoardwalkBrawler", 12, SUBCLASS_VENICE_TABLE_UUID, ptype=1)
#    prog("Prog_BART_L12", "BARTPlatformMenace", 12, SUBCLASS_BART_TABLE_UUID, ptype=1)
#
# 2. In generate_local_expansion() (or equivalent root aggregator):
#    Import generate_capstone and merge its grants:
#
#    from hc_capstone_draft import generate_capstone
#    capstone_grants = generate_capstone(PUBLIC_DIR, add_loca, get_guid)
#    for category, levels in capstone_grants['subclasses'].items():
#        for level, spells in levels.items():
#            grants['subclasses'].setdefault(category, {}).setdefault(level, []).extend(spells)
#
# 3. The existing attach() logic in generate_local_expansion() will automatically
#    create SpellList nodes (e.g. HC_ExpansionList_TenderloinBiohazard_12) and
#    attach AddSpells(...) to each subclass's Level 12 Progression node.
# -----------------------------------------------------------------------------
