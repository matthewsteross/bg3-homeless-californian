"""4th subclass: Overpass Riverbed Dweller (internal name OverpassRiverbedDweller).

Spec: work/spec-overpass-subclass.md. Local development candidate; NOT gameplay-tested.
The level 12 capstone lives in hc_capstone.py beside the other three Squatter's Rights shouts.

Vanilla evidence (extracted data under temp_race/Public/Shared/Stats/Generated/Data):
- Zone_Thunderwave (Spell_Zone.txt:283): CON-save zone with half damage on save and TooltipOnSave.
  Zone_GustOfWind (Spell_Zone.txt:235) proves a Square zone with Range 12 / Base 3 is a line.
- Target_CureWounds (Spell_Target.txt:1497); Target_HealingWord (Spell_Target.txt:4764) is the vanilla
  ranged heal whose SpellFlags / SpellAnimation are borrowed so a 9 m cast is not a touch spell.
- Shout_SecondWind (Spell_Shout.txt:2458): clean self shout used as the area-shout donor.
- RemoveStatus(BURNING): Zone_GustOfWind SpellProperties. BURNING is Status_BOOST.txt:691.
- GROUND:SurfaceChange(Douse): Spell_Zone.txt / Spell_Projectile.txt (several). CreateSurface(...,Water): Spell_Target.txt:7243.
- Resistance(Fire,Resistant) / Resistance(Cold,Resistant): plain Status_BOOST.txt boosts.
- Zone SpellProperties may carry GROUND: functors (Zone_GustOfWind: GROUND:SurfaceClearLayer(Cloud)).

UNVERIFIED IN GAME: where the Flash Flood GROUND: surface lands along the line, and the shape of a
9 m x 4 m Square zone built from Thunderwave. Both use shipped fields with changed numbers.
"""
from pathlib import Path
from hc_icon_keys import icon_for_spell
from hc_tarp import TEMPLATE_KEY as TARP_TEMPLATE_KEY

SUBCLASS = 'OverpassRiverbedDweller'


def generate_overpass(public_dir, add_loca, get_guid):
    public = Path(public_dir)
    data_dir = public / 'Stats/Generated/Data'
    data_dir.mkdir(parents=True, exist_ok=True)

    def check(name, fields):
        for key, value in fields.items():
            if '"' in value or '\n' in value:
                raise ValueError(f'Unsafe field {name}.{key}')

    # ---------------------------------------------------------------- passives
    passives = [
        ('HC_ConcreteBankTraction', 'Concrete Bank Traction',
         'Mud, webs, vines and other difficult terrain no longer slow you down. Standing on a 40-degree slab of wet concrete is a skill, and you have the certificate.',
         'StatusImmunity(DIFFICULT_TERRAIN);StatusImmunity(DIFFICULT_TERRAIN_MUD);StatusImmunity(DIFFICULT_TERRAIN_WEB);StatusImmunity(DIFFICULT_TERRAIN_VINES)', 'PassiveFeature_UnarmoredMovement'),
        ('HC_UnderpassClimateControl', 'Underpass Climate Control',
         'Resistance to Lightning and Cold damage. The underpass is eleven degrees cooler in summer and eleven degrees warmer in winter. Nobody knows why.',
         'Resistance(Lightning,Resistant);Resistance(Cold,Resistant)', 'Spell_Abjuration_ProtectionFromEnergy'),
        ('HC_RebarAnchor', 'Rebar Anchor',
         '+1 Armour Class and advantage on Strength saving throws. They tried to move you along. The rebar disagreed.',
         'AC(1);Advantage(SavingThrow,Strength)', 'PassiveFeature_Resilient'),
    ]
    passive_blocks = []
    for name, title, description, boosts, icon in passives:
        fields = dict(DisplayName=add_loca(name + '_Name', title) + ';1',
                      Description=add_loca(name + '_Description', description) + ';1',
                      Icon=icon, Properties='Highlighted', Boosts=boosts)
        check(name, fields)
        lines = [f'new entry "{name}"', 'type "PassiveData"']
        lines += [f'data "{k}" "{v}"' for k, v in fields.items()]
        passive_blocks.append('\n'.join(lines))
    (data_dir / 'HC_Passives_Overpass.txt').write_text('\n\n'.join(passive_blocks) + '\n', encoding='utf-8')

    # ---------------------------------------------------------------- statuses
    status_name = 'HC_TARP_COVER'
    status_fields = dict(
        StatusType='BOOST', StackId=status_name, StackType='Overwrite', TickType='EndTurn',
        Icon='Spell_Abjuration_MageArmor', Boosts='AC(1);Advantage(SavingThrow,Dexterity)')
    status_fields['DisplayName'] = add_loca(status_name + '_Name', 'Blue Tarp Cover') + ';1'
    status_fields['Description'] = add_loca(
        status_name + '_Description',
        '+1 Armour Class and advantage on Dexterity saving throws. It is waterproof in the way that matters.') + ';1'
    check(status_name, status_fields)
    lines = [f'new entry "{status_name}"', 'type "StatusData"']
    lines += [f'data "{k}" "{v}"' for k, v in status_fields.items()]
    (data_dir / 'HC_Status_Overpass.txt').write_text('\n'.join(lines) + '\n', encoding='utf-8')

    # ------------------------------------------------------------------ spells
    # Every inherited tooltip fact is blanked, then the correct ones are set per spell
    # (same approach as the spell() helper in hc_expansion.py).
    base = dict(Level='0', Cooldown='', DescriptionParams='', ExtraDescription='', MemoryCost='0',
                RechargeValues='', TooltipUpcastDescription='', TooltipUpcastDescriptionParams='',
                TooltipDamageList='', TooltipStatusApply='', TooltipAttackSave='',
                TooltipPermanentWarnings='', TooltipOnSave='', SpellProperties='', SpellRoll='',
                SpellSuccess='', SpellFail='', CastTextEvent='Cast')
    specs = [
        ('HC_Zone_StormDrainFlashFlood', 'Zone_Thunderwave', 'Storm Drain Flash Flood',
         'Open the storm drain and let the municipality explain itself. Costs an action and 1 Junk; once per short rest. '
         'Creatures in a 9 m line make a Strength saving throw, taking 2d8 + Constitution modifier Bludgeoning damage and '
         'falling Prone on a failure, or half damage on a success. Leaves standing water for 2 turns. '
         'The sign said do not enter during rain. You were already in the channel.',
         dict(UseCosts='ActionPoint:1;HC_Junk:1', Cooldown='OncePerShortRest', Range='9', Base='4',
              DamageType='Bludgeoning', Icon='Spell_Evocation_GustOfWind',
              TargetConditions='Character() and not Ally() and not Dead()',
              SpellRoll='not SavingThrow(Ability.Strength, SourceSpellDC())',
              SpellProperties='', SurfaceType='Water', SurfaceLifetime='2', SurfaceGrowStep='5', SurfaceGrowInterval='10', TooltipOnSave='f762efbb-f8f1-493e-b248-2de1567b4bd2',
              SpellSuccess='DealDamage(2d8+ConstitutionModifier,Bludgeoning,Magical);ApplyStatus(PRONE,100,1)',
              SpellFail='DealDamage((2d8+ConstitutionModifier)/2,Bludgeoning,Magical)',
              TooltipDamageList='DealDamage(2d8+ConstitutionModifier,Bludgeoning)',
              TooltipAttackSave='Strength', TooltipStatusApply='ApplyStatus(PRONE,100,1)')),
        ('HC_Shout_BlueTarpLeanTo', 'Shout_SecondWind', 'Blue Tarp Lean-To',
         'Rig a blue tarp over everyone within 3 m. Costs a bonus action and 1 Junk; once per short rest. '
         'You and your allies gain +1 AC and advantage on Dexterity saving throws for 2 turns, and fire on the ground is doused. '
         'A blue tarp lean-to is left standing where you stood. It has held up through three storms and one very determined raccoon.',
         dict(UseCosts='BonusActionPoint:1;HC_Junk:1', Cooldown='OncePerShortRest', AreaRadius='3',
              Icon='Spell_Abjuration_MageArmor',
              TargetConditions='Character() and (Ally() or Self()) and not Dead()',
              # GROUND:Spawn(<root template>) is the exact functor of HC_Target_AbandonedCart (hc_cart.py), verified
              # in game for a ground-target spell. UNVERIFIED for a self-centred Shout: it should resolve once at the
              # caster's feet (like GROUND:SurfaceChange(Douse) beside it) and not once per target.
              SpellProperties='ApplyStatus(HC_TARP_COVER,100,2);GROUND:SurfaceChange(Douse);GROUND:Spawn(' + get_guid(TARP_TEMPLATE_KEY) + ')',
              TooltipStatusApply='ApplyStatus(HC_TARP_COVER,100,2)')),
        ('HC_Target_CulvertSiphon', 'Target_CureWounds', 'Culvert Siphon',
         'Draw clean runoff from the culvert and pour it over a friend. Costs an action and 1 Junk; once per short rest. '
         'An ally or yourself within 9 m regains 2d6 + Constitution modifier Hit Points, stops Burning, and the ground is doused. '
         'It is mostly water. Mostly.',
         dict(UseCosts='ActionPoint:1;HC_Junk:1', Cooldown='OncePerShortRest', TargetRadius='9',
              Icon='Spell_Transmutation_CreateWater',
              # Ranged heal: borrow the flags and cast animation of vanilla Target_HealingWord
              # instead of keeping Cure Wounds' touch animation (IsMelee) on a 9 m spell.
              SpellFlags='HasVerbalComponent;IsSpell;RangeIgnoreVerticalThreshold',
              SpellAnimation='414bbf02-2918-4f01-83fb-1ddc7a588d88,,;,,;2f893fad-98eb-47cf-a524-dd4efd42bc2a,,;ca3147a8-2cf6-45a8-ac9a-1ce0fc11305f,,;0c5dcc83-fa78-41da-b6a5-440b5ea30936,,;,,;bea988a0-2ec5-40d8-a67e-ffbd7454bc53,,;4156d364-d2c0-4a01-908c-3552f78f434d,,;6f0a29b6-0ae8-4ebf-a1e4-8069c4a6ad16,,',
              TargetConditions="Character() and (Ally() or Self()) and not Dead() and not Tagged('UNDEAD') and not Tagged('CONSTRUCT')",
              SpellProperties='RegainHitPoints(2d6+ConstitutionModifier);RemoveStatus(BURNING);GROUND:SurfaceChange(Douse)',
              TooltipDamageList='RegainHitPoints(2d6+ConstitutionModifier)')),
        # Level 10 spell. Clone of Target_CreateWater (Spell_Target.txt:7237) the same way as
        # HC_Target_SprinklerViolation in hc_round2.py; the Mud surface shape GROUND:CreateSurface(r,turns,Mud)
        # is evidenced at Spell_Target.txt:10506 and Spell_Projectile.txt:4126, DIFFICULT_TERRAIN_MUD at
        # Status_BOOST.txt:781, Spell_Conjuration_Grease at Spell_Target.txt:7719. Granted through the
        # hand-written SpellList_Overpass_L10 in generate_mod.py, so it is not returned in the grants below.
        ('HC_Target_DrainageDitchDigIn', 'Target_CreateWater', 'Drainage Ditch Dig-In',
         'Dig a trench where the pavement used to be and let the rain finish the job. Costs an action and 1 Junk; once per short rest. '
         'Choose a point within 9 m: the ground in a 3 m radius turns to mud (difficult terrain) for 3 turns, '
         'slowing everything that tries to cross it. Concrete Bank Traction means you ignore it. '
         'Technically a flood-control project.',
         dict(UseCosts='ActionPoint:1;HC_Junk:1', Cooldown='OncePerShortRest', TargetRadius='9', AreaRadius='3',
              SpellContainerID='', Icon='Spell_Conjuration_Grease',
              SpellProperties='GROUND:CreateSurface(3,3,Mud)')),
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
    (data_dir / 'HC_Spells_Overpass.txt').write_text('\n\n'.join(blocks) + '\n', encoding='utf-8')

    return {'base': {},
            'subclasses': {SUBCLASS: {3: ['HC_Zone_StormDrainFlashFlood', 'HC_Shout_BlueTarpLeanTo'],
                                      6: ['HC_Target_CulvertSiphon']}},
            'resource_increases': {}}
