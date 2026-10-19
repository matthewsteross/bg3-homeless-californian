"""Round 14: three Caltrans spells (base levels 5, 9 and 11) from work/caltrans-grok.md.

Shapes reuse stats whose evidence is cited in earlier rounds: Shout_FeyPresence area save shout (hc_round12.py), Zone_Thunderwave
cone (hc_sub_bart.py), Target_MistyStep teleport (hc_sub_round2.py), SLOW and DAZED and DISENGAGE statuses, DealDamage forms.
The Transfer at the Cone reaction idea was skipped (reactions need engine hooks we have not verified).
UNVERIFIED in game.
"""
from pathlib import Path
from hc_icon_keys import icon_for_spell

PHASE_TWO = 'HC_Shout_CaltransPhaseTwo'
IN_TRANSITION = 'HC_Target_InTransitionLaneConfiguration'
JUST_A_PHASE = 'HC_Zone_ItsJustAPhase'
HOSTILE = 'Enemy() and not Dead()'

SPELLS = [
    # level, name, title, donor, icon fallback, description, fields
    (5, PHASE_TWO, 'Caltrans Phase Two (Phase One Was the Meeting)', 'Shout_FeyPresence', 'Spell_Evocation_Thunderwave',
     'Costs an action and 2 Junk; once per short rest. Enemies within 6 m make a Dexterity save, taking 3d8 Bludgeoning damage and being Slowed for 1 turn on failure, or half damage on success. '
     'The cones arrive before the work does, and the work does not arrive.',
     dict(UseCosts='ActionPoint:1;HC_Junk:2', TargetRadius='0', AreaRadius='6', TargetConditions=HOSTILE,
          SpellRoll='not SavingThrow(Ability.Dexterity, SourceSpellDC())',
          SpellSuccess='DealDamage(3d8,Bludgeoning,Magical);ApplyStatus(SLOW,100,1)',
          SpellFail='DealDamage((3d8)/2,Bludgeoning,Magical)', DamageType='Bludgeoning',
          TooltipDamageList='DealDamage(3d8,Bludgeoning)', TooltipAttackSave='Dexterity',
          TooltipStatusApply='ApplyStatus(SLOW,100,1)', SpellFlags='IsSpell;HasVerbalComponent;HasSomaticComponent;IsHarmful', SpellSchool='Evocation')),
    (9, IN_TRANSITION, 'In Transition (Lane Configuration)', 'Target_MistyStep', 'Spell_Conjuration_MistyStep',
     'Costs a bonus action and 2 Junk; once per short rest. Teleport up to 12 m and gain Disengage for 1 turn. '
     'Lane two is now lane three, lane three is now a suggestion, and nobody has told the cones.',
     dict(UseCosts='BonusActionPoint:1;HC_Junk:2', TargetRadius='12', TargetConditions="CanStand('') and not Character() and not Self()",
          SpellFlags='IsSpell;HasVerbalComponent;RangeIgnoreVerticalThreshold',
          SpellProperties='GROUND:TeleportSource();ApplyStatus(SELF,DISENGAGE,100,1)',
          TooltipStatusApply='ApplyStatus(SELF,DISENGAGE,100,1)')),
    (11, JUST_A_PHASE, "It's Just a Phase (the Phase Is Asphalt)", 'Zone_Thunderwave', 'Spell_Evocation_Thunderwave',
     'Costs an action and 3 Junk; once per long rest. Enemies in a 5 m cone make a Constitution save, taking 6d8 Thunder damage and becoming Dazed for 1 turn on failure, or half damage on success. '
     'It is a phase. The phase is asphalt, and it lasts until at least 2041.',
     dict(UseCosts='ActionPoint:1;HC_Junk:3', Cooldown='OncePerRest', Shape='Cone', Range='5', Base='5', Angle='60',
          TargetConditions=HOSTILE, SpellRoll='not SavingThrow(Ability.Constitution, SourceSpellDC())',
          SpellSuccess='DealDamage(6d8,Thunder,Magical);ApplyStatus(DAZED,100,1)',
          SpellFail='DealDamage((6d8)/2,Thunder,Magical)', DamageType='Thunder',
          TooltipDamageList='DealDamage(6d8,Thunder)', TooltipAttackSave='Constitution',
          TooltipStatusApply='ApplyStatus(DAZED,100,1)')),
]


def generate_round14(public_dir, add_loca, get_guid):
    stats = Path(public_dir) / 'Stats/Generated/Data'
    stats.mkdir(parents=True, exist_ok=True)
    base = dict(Level='0', Cooldown='OncePerShortRest', MemoryCost='0', RechargeValues='', RootSpellID='', SpellContainerID='',
                DescriptionParams='', ExtraDescription='', TooltipUpcastDescription='', TooltipUpcastDescriptionParams='',
                TooltipDamageList='', TooltipStatusApply='', TooltipAttackSave='', TooltipPermanentWarnings='', TooltipOnSave='f762efbb-f8f1-493e-b248-2de1567b4bd2',
                SpellProperties='', SpellRoll='', SpellSuccess='', SpellFail='', CastTextEvent='Cast')
    blocks, grants = [], {'base': {}, 'subclasses': {}, 'existing_list_spells': {}}
    for level, name, title, donor, icon, description, overrides in SPELLS:
        fields = dict(base)
        fields.update(overrides)
        fields['Icon'] = icon_for_spell(name, icon)
        fields['DisplayName'] = add_loca(name + '_Name', title) + ';1'
        fields['Description'] = add_loca(name + '_Description', description) + ';1'
        for key, value in fields.items():
            if any(ch in value for ch in ('"', '\n', '\r')):
                raise ValueError(f'Unsafe field {name}.{key}')
        blocks.append('\n'.join([f'new entry "{name}"', 'type "SpellData"', f'using "{donor}"'] + [f'data "{k}" "{v}"' for k, v in fields.items()]))
        grants['base'].setdefault(level, []).append(name)
    (stats / 'HC_Spells_Round14.txt').write_text('\n\n'.join(blocks) + '\n', encoding='utf-8')
    return grants
