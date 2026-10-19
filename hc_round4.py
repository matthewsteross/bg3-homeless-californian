"""Round 4 source-only candidate. No pak/release work and no new animations.

Vanilla evidence, all under temp_race/Public (all five stat layers searched):
Shared/Stats/Generated/Data/Spell_Target.txt: Target_HideousLaughter, Target_Bane;
Status_KNOCKED_DOWN.txt: HIDEOUS_LAUGHTER (not TASHAS_HIDEOUS_LAUGHTER);
Status_INCAPACITATED.txt: HOLD_PERSON (copied incapacitation/save fields);
Status_BOOST.txt: BANE, SLOW (not SLOWED), WET, CHILLED;
Passive.txt: ExtraAttack (OnStatusApplied/StatusId), ShortResting (OnShortRest).
Gustav/Stats/Generated/Data/Status_BOOST.txt: KNOCKED_OUT_ANIMTEST
(display-only BOOST, no effects); SharedDev/.../Passive.txt:
AspectOfTheBeast_Crocodile (SurfaceWaterFrozen/SurfaceBloodFrozen);
GustavDev/.../Passive.txt: LOW_Cazador_SpawnBuff_Astarion_Passive
(OnSurfaceEnter); SharedDev/.../Spell_Target.txt: HasHPMoreThan;
Gustav/.../Spell_Target.txt: Target_HAG_MaskOfTerror (save advantage args).

UNVERIFIED: HasHPMoreThan(100) checks CURRENT HP, not maximum HP or a boss tag.
Its use as a save-advantage argument needs game testing, including HP changes.
UNVERIFIED: BANE has no decrementing stacks. Three exclusive numbered stages
model the requested 3/2/1 stacks using HOLD_PERSON's end-turn removal save
and vanilla condition-removal follow-up functors. Original caster/DC preservation
across OnRemoveFunctors, transition timing and final SLOW duration need game QA.
UNVERIFIED: cosmetic overhead display, self-only status event routing, nested
event reentrancy and per-short-rest lock reset need game QA. Vanilla hooks exist;
no OnTurnStart fallback is needed. Ice uses surface entry, not a frozen status;
already standing on ice when gaining the passive does not trigger a complaint.
UNVERIFIED: Laughing_Hideous on a non-prone INCAPACITATED status needs game QA.
Freeway's SourceSpellDC() for a non-caster class also needs game QA.
The Freeway and approval statuses copy Shared fields, with no status inheritance.
Permit tiers deliberately inherit BANE's combat flags, VFX and Weakened idle,
but replace its roll penalties. Approval deliberately retains both Slow passives.
"""
from pathlib import Path
from hc_icon_keys import icon_for_spell

FREEWAY = 'HC_Target_FreewayDirections'
PERMIT = 'HC_Target_PermitPending'
WEATHER = 'HC_WeatherComplaint'
PERMIT_LEVEL = 5  # hc_round2 BASE occupies 2, 4, 8, 11.
WEATHER_LINES = {'WET': 'Is this a storm??', 'CHILLED': "It's literally 60 degrees.",
                 'ICE': "I didn't bring a jacket."}
BOSS_CHECK = 'HasHPMoreThan(100)'
PERMIT_SAVE = f'SavingThrow(Ability.Wisdom, SourceSpellDC(), {BOSS_CHECK}, false)'


def generate_round4(public_dir, add_loca, get_guid):
    data = Path(public_dir) / 'Stats/Generated/Data'
    data.mkdir(parents=True, exist_ok=True)
    blocks = {'Status': [], 'Spells': [], 'Passives': []}

    def emit(group, name, kind, donor, title, description, **fields):
        if not name.startswith('HC_'):
            raise ValueError(name)
        fields['DisplayName'] = add_loca(name + '_Name', title) + ';1'
        fields['Description'] = add_loca(name + '_Description', description) + ';1'
        lines = [f'new entry "{name}"', f'type "{kind}"']
        if donor:
            lines.append(f'using "{donor}"')
        for key, value in fields.items():
            if '"' in value or '\n' in value or '\r' in value:
                raise ValueError(f'Unsafe field {name}.{key}')
            lines.append(f'data "{key}" "{value}"')
        blocks[group].append('\n'.join(lines))

    emit('Status', 'HC_FREEWAY_DIRECTIONS', 'StatusData', None,
         'Freeway Directions', 'Incapacitated for 1 turn. No Prone.',
         StatusType='INCAPACITATED', StackId='HC_FREEWAY_DIRECTIONS',
         StackType='Overwrite', TickType='EndTurn',
         Boosts='DetectDisturbancesBlock(true);', StatusGroups='SG_Incapacitated;SG_Condition',
         RemoveConditions='SavingThrow(Ability.Wisdom, SourceSpellDC())',
         RemoveEvents='OnTurn', OnApplyFunctors='BreakConcentration()', OnRemoveFunctors='',
         Icon="Spell_Enchantment_Tasha'sHideousLaughter", TooltipSave='Wisdom',
         StatusPropertyFlags='OverheadOnTurn;InitiateCombat',
         StillAnimationType='Laughing_Hideous', StillAnimationPriority='Shouting',
         SoundVocalStart='NONE', SoundVocalLoop='LAUGHTERMANIACAL',
         SoundStart='Misc_Status_HideousLaughter,HEAD;',
         SoundStop='Misc_Status_HideousLaughter_Stop,HEAD;', SoundVocalEnd='RECOVER')

    for key, line in WEATHER_LINES.items():
        status = 'HC_WEATHER_' + key
        lock = status + '_USED'
        emit('Status', status, 'StatusData', 'KNOCKED_OUT_ANIMTEST', line,
             'A purely cosmetic weather complaint.', StatusType='BOOST',
             StackId=status, StackType='Overwrite', TickType='EndTurn', Boosts='',
             StatusPropertyFlags='DisableCombatlog;DisablePortraitIndicator')
        emit('Status', lock, 'StatusData', 'KNOCKED_OUT_ANIMTEST',
             'Weather complaint cooldown', 'Resets on a Short Rest or Long Rest.',
             StatusType='BOOST', StackId=lock, Boosts='',
             StatusPropertyFlags='DisableOverhead;DisableCombatlog;DisablePortraitIndicator')

    for key in WEATHER_LINES:
        trigger = (f'context.HasContextFlag(StatsFunctorContext.OnStatusApplied) and StatusId(\'{key}\')'
                   if key != 'ICE' else
                   "context.HasContextFlag(StatsFunctorContext.OnSurfaceEnter) and "
                   "(InSurface('SurfaceWaterFrozen',context.Source) or InSurface('SurfaceBloodFrozen',context.Source))")
        status = 'HC_WEATHER_' + key
        condition = f"({trigger}) and not HasStatus('{status}_USED',context.Source)"
        # Set lock FIRST: applying the cosmetic status recursively emits OnStatusApplied.
        # Evaluate eligibility once for the whole functor list.
        emit('Passives', WEATHER + '_' + key, 'PassiveData', None, 'Weather Complaint',
             'One cosmetic complaint per weather type per Short Rest.',
             Properties='IsHidden', StatsFunctorContext='OnStatusApplied' if key != 'ICE' else 'OnSurfaceEnter',
             Conditions=condition,
             StatsFunctors=f'ApplyStatus(SELF,{status}_USED,100,-1);ApplyStatus(SELF,{status},100,1)')
    emit('Passives', WEATHER, 'PassiveData', None, 'Weather Complaint',
         'Wet, Chilled or ice prompts a cosmetic complaint, each once per Short Rest.',
         Properties='Highlighted', StatsFunctorContext='OnShortRest;OnLongRest',
         StatsFunctors=';'.join(f'RemoveStatus(SELF,HC_WEATHER_{key}_USED)' for key in WEATHER_LINES))

    for stage in (3, 2, 1):
        name = f'HC_PERMIT_PENDING_{stage}'
        following = f'HC_PERMIT_PENDING_{stage - 1}' if stage > 1 else 'HC_PERMIT_APPROVED'
        duration = '-1' if stage > 1 else '1'
        emit('Status', name, 'StatusData', 'BANE', f'Permit Pending ({stage} stack{"" if stage == 1 else "s"})',
             f'{stage} stack{"" if stage == 1 else "s"}. No Bonus Action; movement reduced by 3 m. Each successful end-of-turn Wisdom save removes 1 stack.',
             StatusType='BOOST', StackId='HC_PERMIT_PENDING', StackType='Overwrite',
             TickType='EndTurn', Boosts='ActionResourceBlock(BonusActionPoint);ActionResource(Movement,-3,0)',
             RemoveConditions=PERMIT_SAVE, RemoveEvents='OnTurn', TooltipSave='Wisdom',
             OnRemoveFunctors=f'IF(RemoveCause(StatusRemoveCause.Condition)):ApplyStatus(SELF,{following},100,{duration})')
    # Keep both Slow passives so the final one-turn approval has full vanilla Slow mechanics.
    emit('Status', 'HC_PERMIT_APPROVED', 'StatusData', None, 'Approved, pending review.',
         'Slowed for 1 turn.', StatusType='BOOST', StackId='HC_PERMIT_APPROVED', TickType='EndTurn',
         Icon='Spell_Transmutation_Slow', SoundVocalStart='WEAK',
         SoundLoop='Spell_Status_Slow_MO', SoundStop='Spell_Status_Slow_MO_Stop',
         Boosts='AC(-2);RollBonus(SavingThrow,0-2,Dexterity);ActionResourceBlock(ReactionActionPoint);ActionResourceMultiplier(Movement,50,0);MovementSpeedLimit(Walk);AI_IGNORE:Tag(EXTRA_ATTACK_BLOCKED);',
         Passives='Slow_ActionPoint;Slow_Casting',
         OnApplyFunctors='RemoveStatus(EXTRA_ATTACK);RemoveStatus(EXTRA_ATTACK_2);RemoveStatus(EXTRA_ATTACK_WAR_MAGIC);RemoveStatus(EXTRA_ATTACK_WAR_PRIEST);RemoveStatus(MAG_MARTIAL_EXERTION);RemoveStatus(WILDSTRIKE_EXTRA_ATTACK);RemoveStatus(WILDSTRIKE_2_EXTRA_ATTACK);RemoveStatus(STALKERS_FLURRY);RemoveStatus(EXTRA_ATTACK_THIRSTING_BLADE);RemoveStatus(COMMANDERS_STRIKE_D8);RemoveStatus(COMMANDERS_STRIKE_D10)',
         StatusEffect='1e34754f-17e3-4aeb-9db9-a34f682c1c45',
         ManagedStatusEffectType='Negative', ManagedStatusEffectGroup='d787f666-8ee6-4185-9365-6aac9ebe76ae',
         RemoveConditions='', RemoveEvents='', TooltipSave='', OnRemoveFunctors='')

    for name, donor, title, description, radius, cost, status, duration, save, fallback in [
        (FREEWAY, 'Target_HideousLaughter', 'Freeway Directions',
         'Action; once per Short Rest; 9 m. Wisdom save or Incapacitated for 1 turn, without Prone. '
         'You will want to take the 101. Trust the 101. There is no 101 at this hour.',
         '9', 'ActionPoint:1', 'HC_FREEWAY_DIRECTIONS', '1',
         'SavingThrow(Ability.Wisdom, SourceSpellDC())', "Spell_Enchantment_Tasha'sHideousLaughter"),
        (PERMIT, 'Target_Bane', 'Permit Pending',
         'Action and 1 Junk; once per Short Rest; 18 m. Wisdom save or 3 stacks: no Bonus Action and -3 m movement. '
         'Successful end-of-turn saves remove 1 stack; the last grants 1 turn of Slow. Targets above 100 current HP '
         'have advantage on these saves. Your form was received. Please allow 6-8 business turns.',
         '18', 'ActionPoint:1;HC_Junk:1', 'HC_PERMIT_PENDING_3', '-1', PERMIT_SAVE, 'Spell_Enchantment_Bane'),
    ]:
        target_conditions = 'Character() and not Self() and not Dead()'
        if name == FREEWAY:
            target_conditions += ' and IntelligenceGreaterThan(4)'
        emit('Spells', name, 'SpellData', donor, title, description,
             Level='0', MemoryCost='0', UseCosts=cost, Cooldown='OncePerShortRest',
             CombatAIOverrideSpell='',
             TargetRadius=radius, AmountOfTargets='1', TargetConditions=target_conditions,
             SpellFlags='IsSpell;HasVerbalComponent;HasSomaticComponent;HasHighGroundRangeExtension;IsHarmful',
             SpellProperties='', SpellRoll='not ' + save,
             SpellSuccess=f'ApplyStatus({status},100,{duration})',
             SpellFail='ApplyStatus(SAVED_AGAINST_HOSTILE_SPELL_DOMINATED,100,0)',
             Icon=icon_for_spell(name, fallback), TooltipAttackSave='Wisdom',
             TooltipStatusApply=f'ApplyStatus({status},100,{duration})',
             DescriptionParams='', TooltipUpcastDescription='', TooltipUpcastDescriptionParams='',
             TooltipPermanentWarnings='', TooltipDamageList='', TooltipOnSave='',
             ExtraDescription='', RechargeValues='')

    for group, entries in blocks.items():
        (data / f'HC_{group}_Round4.txt').write_text('\n\n'.join(entries) + '\n', encoding='utf-8')
    return {'base': {PERMIT_LEVEL: [PERMIT]}, 'racial_spell': FREEWAY,
            'racial_passives': [WEATHER, *(WEATHER + '_' + key for key in WEATHER_LINES)]}
