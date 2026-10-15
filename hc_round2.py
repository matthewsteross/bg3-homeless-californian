"""Round 2 additions: four base-class Junk spells and the Inland Emperor level 3 racial spell.

Spec: work/spec-round2.md. Local development candidate; NOT gameplay-tested.
(The Notary Street Trade and Tinfoil Deflector Junk Doctrine options live in hc_choices.py / hc_doctrines.py.)

Vanilla evidence (extracted data under temp_race/Public/Shared/Stats/Generated/Data):
- Target_InflictWounds (Spell_Target.txt:2325): TargetRadius 1.5, SpellRoll Attack(AttackType.MeleeSpellAttack),
  IsMelee flag, SpellSuccess DealDamage(...). The generator blanks SpellRoll, so it is restored explicitly.
- Target_CreateWater (Spell_Target.txt:7237): SpellProperties "ApplyStatus(WET,100, 3); GROUND:CreateSurface(4,0, Water);",
  AreaRadius 4, in container Target_CreateDestroyWater (SpellContainerID is cleared). WET is Status_BOOST.txt:1030.
- Target_MistyStep (Spell_Target.txt:5643): "GROUND:TeleportSource();" with TargetConditions CanStand('') and
  not Character(). The in-mod Target_DisruptivePivot already clones it the same way.
- Target_ViciousMockery (Spell_Target.txt:6164): Wisdom save in SpellRoll, outcome in SpellSuccess / SpellFail.
  BANE is Status_BOOST.txt:1747; Target_Bane applies it as ApplyStatus(BANE, 100, 10) with a failed save.
- Target_FogCloud (Spell_Target.txt:7658): "GROUND:CreateSurface(4.5,10,FogCloud,true)", AreaRadius 4, TargetRadius 18.
  The trailing true makes the cloud concentration-bound and the donor's IsConcentration flag is dropped here.
  Plain CreateSurface(2,2,DarknessCloud) (Spell_Shout.txt:2039) is the no-concentration shape used.
- AC(-2), ActionResourceBlock(ReactionActionPoint): Status_BOOST.txt (several); PANHANDLING_SHAME in generate_mod.py uses the same
  reaction block.

NOT DONE: HOV Lane does not leave mud where the caster stood. GROUND: functors resolve at the target point
(the destination), no vanilla spell places a surface at the teleport source, so the optional surface is omitted.

UNVERIFIED IN GAME: Sawzall inherits Inflict Wounds' necrotic cast and hit visuals/sounds; Sprinkler Violation's WET
reaches only creatures inside the 2 m AreaRadius; Citation deals its damage even when the save succeeds.
"""
from pathlib import Path
from hc_icon_keys import icon_for_spell

DECAT_STATUS = 'HC_DECAT_EXHAUST'
TULE_FOG = 'HC_Target_TuleFog'


def generate_round2(public_dir, add_loca, get_guid):
    public = Path(public_dir)
    data_dir = public / 'Stats/Generated/Data'
    data_dir.mkdir(parents=True, exist_ok=True)

    def check(name, fields):
        for key, value in fields.items():
            if '"' in value or '\n' in value:
                raise ValueError(f'Unsafe field {name}.{key}')

    # ---------------------------------------------------------------- status
    status_fields = dict(
        StatusType='BOOST', StackId=DECAT_STATUS, StackType='Overwrite', TickType='EndTurn',
        Icon='Action_CripplingStrike', Boosts='AC(-2);ActionResourceBlock(ReactionActionPoint)',
        StatusPropertyFlags='InitiateCombat')
    status_fields['DisplayName'] = add_loca(DECAT_STATUS + '_Name', 'Decatted Exhaust') + ';1'
    status_fields['Description'] = add_loca(
        DECAT_STATUS + '_Description',
        '-2 Armour Class and cannot take reactions. Everyone within three blocks has noticed.') + ';1'
    check(DECAT_STATUS, status_fields)
    lines = [f'new entry "{DECAT_STATUS}"', 'type "StatusData"']
    lines += [f'data "{k}" "{v}"' for k, v in status_fields.items()]
    (data_dir / 'HC_Status_Round2.txt').write_text('\n'.join(lines) + '\n', encoding='utf-8')

    # ------------------------------------------------------------------ spells
    # Every inherited tooltip fact is blanked, then the correct ones are set per spell
    # (same approach as the spell() helper in hc_expansion.py).
    base = dict(Level='0', Cooldown='', DescriptionParams='', ExtraDescription='', MemoryCost='0',
                RechargeValues='', TooltipUpcastDescription='', TooltipUpcastDescriptionParams='',
                TooltipDamageList='', TooltipStatusApply='', TooltipAttackSave='',
                TooltipPermanentWarnings='', TooltipOnSave='', SpellProperties='', SpellRoll='',
                SpellSuccess='', SpellFail='', CastTextEvent='Cast')
    wis_roll = 'not SavingThrow(Ability.Wisdom, SourceSpellDC())'
    specs = [
        ('HC_Target_CatalyticConverterSawzall', 'Target_InflictWounds', 'Catalytic Converter Sawzall',
         'Take the exhaust system off something that was not yours to begin with. Costs an action and 1 Junk; once per short rest. '
         'Melee spell attack within 1.5 m: 3d8 Slashing damage. On a hit the target is Decatted for 2 turns: -2 AC and no reactions. '
         'The car will start. It will also be audible from the next county.',
         dict(UseCosts='ActionPoint:1;HC_Junk:1', Cooldown='OncePerShortRest', TargetRadius='1.5',
              Icon='Action_CripplingStrike', DamageType='Slashing',
              TargetConditions='Character() and not Ally() and not Dead()',
              SpellRoll='Attack(AttackType.MeleeSpellAttack)',
              SpellSuccess=f'DealDamage(3d8,Slashing,Magical);ApplyStatus({DECAT_STATUS},100,2)',
              TooltipDamageList='DealDamage(3d8,Slashing)', TooltipAttackSave='MeleeSpellAttack',
              TooltipStatusApply=f'ApplyStatus({DECAT_STATUS},100,2)')),
        ('HC_Target_SprinklerViolation', 'Target_CreateWater', 'Sprinkler Violation',
         'Hold the test valve open until the ceiling does the rest. Costs a bonus action and 1 Junk; once per short rest. '
         'Choose a point within 9 m: a 2 m radius puddle of water lasts 2 turns, and creatures in that area become Wet for 3 turns '
         '(resistant to Fire, vulnerable to Cold and Lightning). '
         'The tag said do not touch. The tag was hopeful.',
         dict(UseCosts='BonusActionPoint:1;HC_Junk:1', Cooldown='OncePerShortRest', TargetRadius='9', AreaRadius='2',
              SpellContainerID='', Icon='Spell_Transmutation_CreateWater',
              SpellProperties='ApplyStatus(WET,100,3);GROUND:CreateSurface(2,2,Water)',
              TooltipStatusApply='ApplyStatus(WET,100,3)')),
        ('HC_Target_HOVLane', 'Target_MistyStep', 'HOV Lane',
         'Slip into the carpool lane with a mannequin in the passenger seat. Costs a bonus action and 1 Junk; once per short rest. '
         'Teleport up to 12 m to an unoccupied place you can see. '
         'Traffic is, for once, moving at the speed of the sign.',
         dict(UseCosts='BonusActionPoint:1;HC_Junk:1', Cooldown='OncePerShortRest', TargetRadius='12',
              Icon='Spell_Conjuration_MistyStep',
              # The generator default blanks SpellProperties, which would delete the donor's teleport.
              SpellProperties='GROUND:TeleportSource()')),
        ('HC_Target_OneStarCitation', 'Target_ViciousMockery', 'One-Star Citation',
         'File a review so specific it reads like a summons. Costs an action and 1 Junk. '
         'A target within 9 m takes 2d8 Psychic damage and makes a Wisdom saving throw; on a failure it is Baned for 2 turns '
         '(subtracts 1d4 from attack rolls and saving throws). '
         'The food was fine. The atmosphere was a lot. The photo is attached.',
         dict(UseCosts='ActionPoint:1;HC_Junk:1', TargetRadius='9', Icon='Spell_Enchantment_Bane',
              TargetConditions='Character() and not Ally() and not Dead()',
              SpellRoll=wis_roll,
              SpellProperties='DealDamage(2d8,Psychic,Magical)',
              SpellSuccess='ApplyStatus(BANE,100,2)',
              SpellFail='ApplyStatus(SAVED_AGAINST_HOSTILE_SPELL,100,0)',
              TooltipDamageList='DealDamage(2d8,Psychic)', TooltipAttackSave='Wisdom',
              TooltipStatusApply='ApplyStatus(BANE,100,2)')),
        (TULE_FOG, 'Target_FogCloud', 'Bakersfield Tule Fog',
         'Let the Central Valley exhale. Costs an action; once per short rest. '
         'Choose a point within 9 m: a 4 m radius cloud of fog heavily obscures the area for 2 turns. '
         'Visibility is one car length, and everyone is still doing seventy-five.',
         dict(UseCosts='ActionPoint:1', Cooldown='OncePerShortRest', TargetRadius='9', AreaRadius='4',
              Icon='Spell_Conjuration_FogCloud',
              # Donor flags minus IsConcentration: a 2-turn racial cloud should not eat the caster's concentration.
              SpellFlags='IsSpell;HasVerbalComponent;HasSomaticComponent;HasHighGroundRangeExtension;RangeIgnoreVerticalThreshold',
              SpellProperties='GROUND:CreateSurface(4,2,FogCloud)')),
    ]
    blocks = []
    for name, donor, title, description, overrides in specs:
        fields = dict(base)
        fields.update(overrides)
        fields['Icon'] = icon_for_spell(name, fields['Icon'])
        fields['DisplayName'] = add_loca(name + '_Name', title) + ';1'
        fields['Description'] = add_loca(name + '_Description', description) + ';1'
        check(name, fields)
        lines = [f'new entry "{name}"', 'type "SpellData"', f'using "{donor}"']
        lines += [f'data "{k}" "{v}"' for k, v in fields.items()]
        blocks.append('\n'.join(lines))
    (data_dir / 'HC_Spells_Round2.txt').write_text('\n\n'.join(blocks) + '\n', encoding='utf-8')

    # Base-class levels chosen because they held the fewest new spells (one each, or two counting
    # a vanilla-donor mod spell); never more than one new spell per level.
    return {'base': {2: ['HC_Target_SprinklerViolation'],
                     4: ['HC_Target_CatalyticConverterSawzall'],
                     8: ['HC_Target_OneStarCitation'],
                     11: ['HC_Target_HOVLane']},
            'subclasses': {}, 'resource_increases': {},
            'racial': {'InlandEmperor': {3: [TULE_FOG]}}}
