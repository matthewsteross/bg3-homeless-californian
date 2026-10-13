"""Phase 4 'Hustle' kit: spells that cash in the Socially Shamed / Homeless Fatigue statuses.

Local development candidate (2026-10-13); NOT gameplay-tested.

Vanilla evidence (extracted data under temp_race/Public):
- Target donor Target_ViciousMockery: Shared/Stats/Generated/Data/Spell_Target.txt:6164 (WIS save, SpellSuccess/SpellFail)
- Zone donor Zone_Thunderwave: Shared/Stats/Generated/Data/Spell_Zone.txt:283 (CON save, Force push)
- Frightened applied as ApplyStatus(FRIGHTENED,100,2): Shared/.../Spell_Shout.txt:3176
- Boost Advantage(AttackTarget) (attackers have advantage): GustavDev/.../Status_BOOST.txt (4 plain uses)
- Boost ActionResourceBlock(Movement) (cannot move): 70 uses across Status_*.txt
- Gold: OBJ_GoldCoin RootTemplate 1c3c9c74-34a1-4685-989e-410dc080be6f: Shared/.../Object.txt:3132
- SummonInInventory(<uuid>,-1,<amount>,false,false,false): Shared/.../Spell_Target.txt:2106
- HasStatus('X') in TargetConditions: used widely (e.g. HasStatus('SG_Prone'))
- Non-hostile NPC condition shape: "Character() and not Enemy()" / "Character() and Party()"

UNVERIFIED IN GAME (see work/phase4/NOTES.md):
- whether SummonInInventory on an NPC-targeted spell puts the gold in the caster's or the target's inventory
- whether casting Beg on a neutral NPC counts as a hostile act
- permanent (-1) Homeless Fatigue duration out of combat
"""
from pathlib import Path
from hc_icon_keys import icon_for_spell

GOLD_TEMPLATE = '1c3c9c74-34a1-4685-989e-410dc080be6f'  # OBJ_GoldCoin RootTemplate
BEG_GOLD = 5


def generate_hustle(public_dir, add_loca, get_guid):
    public = Path(public_dir)
    data_dir = public / 'Stats/Generated/Data'
    data_dir.mkdir(parents=True, exist_ok=True)

    def check(name, fields):
        for key, value in fields.items():
            if '"' in value or '\n' in value:
                raise ValueError(f'Unsafe field {name}.{key}')

    # ---------------------------------------------------------------- statuses
    statuses = [
        ('HC_HOMELESS_FATIGUE', 'Homeless Fatigue',
         'They have stopped seeing you, and honestly everything else too. Attack rolls against them have advantage.',
         dict(StatusType='BOOST', StackId='HC_HOMELESS_FATIGUE', StackType='Overwrite', TickType='EndTurn',
              Icon='Spell_Panhandling', Boosts='Advantage(AttackTarget)')),
        ('HC_INVISIBLE_BOX', 'Trapped in the Invisible Box',
         'Pressing hands against a wall that is not there. Cannot move.',
         dict(StatusType='BOOST', StackId='HC_INVISIBLE_BOX', StackType='Overwrite', TickType='EndTurn',
              Icon='Spell_Panhandling', Boosts='ActionResourceBlock(Movement)')),
        ('HC_BREADCRUMBED', 'Breadcrumbed',
         'A flock has taken an interest. Attack rolls against the target have advantage, and its own attack rolls have disadvantage.',
         dict(StatusType='BOOST', StackId='HC_BREADCRUMBED', StackType='Overwrite', TickType='EndTurn',
              Icon='Spell_Panhandling', Boosts='Advantage(AttackTarget);Disadvantage(AttackRoll)')),
    ]
    status_blocks = []
    for name, title, description, fields in statuses:
        fields = dict(fields)
        fields['DisplayName'] = add_loca(name + '_Name', title) + ';1'
        fields['Description'] = add_loca(name + '_Description', description) + ';1'
        check(name, fields)
        lines = [f'new entry "{name}"', 'type "StatusData"']
        lines += [f'data "{k}" "{v}"' for k, v in fields.items()]
        status_blocks.append('\n'.join(lines))
    (data_dir / 'HC_Status_Hustle.txt').write_text('\n\n'.join(status_blocks) + '\n', encoding='utf-8')

    # ------------------------------------------------------------------ spells
    wis_roll = 'not SavingThrow(Ability.Wisdom, SourceSpellDC())'
    shamed = "HasStatus('PANHANDLING_SHAME')"
    fatigued = "HasStatus('HC_HOMELESS_FATIGUE')"
    specs = [
        # name, donor, title, description, overrides
        ('HC_Target_GuiltTrip', 'Target_ViciousMockery', 'Guilt Trip',
         'Make it land. Costs a bonus action and 1 Junk. A Socially Shamed target takes 2d6 + Constitution modifier Psychic damage and the shame is spent. Do you have any idea what groceries cost?',
         dict(TargetRadius='9', UseCosts='BonusActionPoint:1;HC_Junk:1',
              TargetConditions=f'Character() and not Ally() and not Dead() and {shamed}',
              SpellProperties='DealDamage(2d6+ConstitutionModifier,Psychic,Magical);RemoveStatus(PANHANDLING_SHAME)',
              TooltipDamageList='DealDamage(2d6+ConstitutionModifier,Psychic)')),
        ('HC_Target_PublicScene', 'Target_ViciousMockery', 'Public Scene',
         'Escalate. Costs an action and 1 Junk. A Socially Shamed target makes a Wisdom saving throw or becomes Frightened for 2 turns. Everyone is looking. Everyone.',
         dict(TargetRadius='9', UseCosts='ActionPoint:1;HC_Junk:1', SpellRoll=wis_roll,
              SpellSuccess='ApplyStatus(FRIGHTENED,100,2)',
              SpellFail='ApplyStatus(SAVED_AGAINST_HOSTILE_SPELL,100,0)',
              TargetConditions=f'Character() and not Ally() and not Dead() and {shamed}',
              TooltipAttackSave='Wisdom', TooltipStatusApply='ApplyStatus(FRIGHTENED,100,2)')),
        ('HC_Target_TrappedInTheInvisibleBox', 'Target_ViciousMockery', 'Trapped in the Invisible Box',
         'An invisible box appears. It is extremely real to the target. Costs an action and 1 Junk; once per short rest. The target makes a Wisdom saving throw or cannot move for 1 turn.',
         dict(TargetRadius='9', UseCosts='ActionPoint:1;HC_Junk:1', Cooldown='OncePerShortRest', SpellRoll=wis_roll,
              SpellSuccess='ApplyStatus(HC_INVISIBLE_BOX,100,1)',
              SpellFail='ApplyStatus(SAVED_AGAINST_HOSTILE_SPELL,100,0)',
              TargetConditions='Character() and not Ally() and not Dead()',
              TooltipAttackSave='Wisdom', TooltipStatusApply='ApplyStatus(HC_INVISIBLE_BOX,100,1)')),
        ('HC_Target_CompassionBurnout', 'Target_ViciousMockery', 'Compassion Burnout',
         'Their patience snaps. Costs a bonus action and 1 Junk. A target with Homeless Fatigue takes 3d6 Psychic damage and the fatigue ends.',
         dict(TargetRadius='9', UseCosts='BonusActionPoint:1;HC_Junk:1',
              TargetConditions=f'Character() and not Ally() and not Dead() and {fatigued}',
              SpellProperties='DealDamage(3d6,Psychic,Magical);RemoveStatus(HC_HOMELESS_FATIGUE)',
              TooltipDamageList='DealDamage(3d6,Psychic)')),
        ('HC_Target_Beg', 'Target_ViciousMockery', 'Beg',
         f'Ask a non-hostile stranger for spare change. Costs an action; once per short rest. The target makes a Wisdom saving throw. On a failure they hand over {BEG_GOLD} gold. Either way they gain Homeless Fatigue and will not be swayed again.',
         dict(TargetRadius='3', UseCosts='ActionPoint:1', Cooldown='OncePerShortRest', SpellRoll=wis_roll,
              SpellSuccess=f'SummonInInventory({GOLD_TEMPLATE},-1,{BEG_GOLD},false,false,false);ApplyStatus(HC_HOMELESS_FATIGUE,100,-1)',
              SpellFail='ApplyStatus(HC_HOMELESS_FATIGUE,100,-1)',
              TargetConditions=f"Character() and not Enemy() and not Party() and not Dead() and not {fatigued}",
              TooltipAttackSave='Wisdom', TooltipStatusApply='ApplyStatus(HC_HOMELESS_FATIGUE,100,-1)')),
        ('HC_Zone_BucketDrumSolo', 'Zone_Thunderwave', 'Bucket Drum Solo',
         'Play the five-gallon bucket like it owes you money. Costs an action and 1 Junk. Creatures in the cone make a Constitution saving throw, taking 2d6 Thunder damage and being pushed back on a failure, or half damage on a success. Failures gain Homeless Fatigue for 3 turns.',
         dict(UseCosts='ActionPoint:1;HC_Junk:1',
              SpellSuccess='DealDamage(2d6,Thunder,Magical);Force(4, OriginToTarget);ApplyStatus(HC_HOMELESS_FATIGUE,100,3)',
              SpellFail='DealDamage((2d6)/2,Thunder,Magical)',
              TargetConditions='Character() and not Ally() and not Dead()',
              TooltipDamageList='DealDamage(2d6,Thunder)', TooltipAttackSave='Constitution',
              TooltipStatusApply='ApplyStatus(HC_HOMELESS_FATIGUE,100,3)')),
        ('HC_Target_Sublet', 'Target_Longstrider', 'Sublet',
         'Rent out your doorway. Costs an action and 1 Junk. An ally within 9 m gets the Lawn Chair treatment for 2 turns: +2 AC, advantage on Strength saving throws and immunity to being knocked Prone. You do not get it. Rent is due.',
         dict(TargetRadius='9', UseCosts='ActionPoint:1;HC_Junk:1',
              TargetConditions='Character() and Ally() and not Self() and not Dead()',
              SpellProperties='ApplyStatus(HC_CHAIR_BRACED,100,2)',
              TooltipStatusApply='ApplyStatus(HC_CHAIR_BRACED,100,2)')),
        ('HC_Target_EverybodyKnowsThisGuy', 'Target_ViciousMockery', 'Everybody Knows This Guy',
         'The flock knows who owes them lunch. Costs an action and 1 Junk. The target makes a Wisdom saving throw or becomes Breadcrumbed for 2 turns: attack rolls against it have advantage, and its own attack rolls have disadvantage.',
         dict(TargetRadius='9', UseCosts='ActionPoint:1;HC_Junk:1', SpellRoll=wis_roll,
              SpellSuccess='ApplyStatus(HC_BREADCRUMBED,100,2)',
              SpellFail='ApplyStatus(SAVED_AGAINST_HOSTILE_SPELL,100,0)',
              TargetConditions='Character() and not Ally() and not Dead()',
              TooltipAttackSave='Wisdom', TooltipStatusApply='ApplyStatus(HC_BREADCRUMBED,100,2)')),
        ('HC_Projectile_PuncturedLithiumCell', 'Projectile_FireBolt', 'Punctured Lithium Cell',
         'Hurl a swollen scooter battery. Costs an action and 1 Junk. Ranged spell attack for 2d6 Lightning plus 2d6 Fire damage, and it sets the ground alight. Indoors, mind your friends.',
         dict(TargetRadius='12', UseCosts='ActionPoint:1;HC_Junk:1',
              SpellSuccess='DealDamage(2d6,Lightning,Magical);DealDamage(2d6,Fire,Magical)',
              TooltipDamageList='DealDamage(2d6,Lightning);DealDamage(2d6,Fire)')),
    ]
    icons = {
        'HC_Target_Sublet': 'Spell_LoadBearingChair',
        'HC_Target_EverybodyKnowsThisGuy': 'Spell_Panhandling',
        'HC_Projectile_PuncturedLithiumCell': 'Spell_Evocation_FireBolt',
        'HC_Target_GuiltTrip': 'Spell_Enchantment_ViciousMockery',
        'HC_Target_PublicScene': 'Spell_Enchantment_ViciousMockery',
        'HC_Target_TrappedInTheInvisibleBox': 'Spell_Panhandling',
        'HC_Target_CompassionBurnout': 'Spell_Enchantment_ViciousMockery',
        'HC_Target_Beg': 'Spell_Panhandling',
        'HC_Zone_BucketDrumSolo': 'Spell_Evocation_Thunderwave',
    }
    blocks = []
    for name, donor, title, description, overrides in specs:
        fields = dict(Level='0', UseCosts='ActionPoint:1;HC_Junk:1', MemoryCost='0', Cooldown='', RechargeValues='',
                      DescriptionParams='', ExtraDescription='', TooltipUpcastDescription='',
                      TooltipUpcastDescriptionParams='', TooltipDamageList='', TooltipStatusApply='',
                      TooltipAttackSave='', TooltipPermanentWarnings='', TooltipOnSave='', SpellProperties='',
                      SpellRoll='', SpellSuccess='', SpellFail='', CastTextEvent='Cast')
        fields.update(overrides)
        fields['Icon'] = icon_for_spell(name, icons[name])
        fields['DisplayName'] = add_loca(name + '_Name', title) + ';1'
        fields['Description'] = add_loca(name + '_Description', description) + ';1'
        check(name, fields)
        lines = [f'new entry "{name}"', 'type "SpellData"', f'using "{donor}"']
        lines += [f'data "{k}" "{v}"' for k, v in fields.items()]
        blocks.append('\n'.join(lines))
    (data_dir / 'HC_Spells_Hustle.txt').write_text('\n\n'.join(blocks) + '\n', encoding='utf-8')

    return {'base': {5: ['HC_Target_GuiltTrip', 'HC_Target_Beg'],
                     6: ['HC_Target_PublicScene'],
                     8: ['HC_Target_TrappedInTheInvisibleBox'],
                     9: ['HC_Zone_BucketDrumSolo'],
                     10: ['HC_Target_CompassionBurnout'],
                     11: ['HC_Projectile_PuncturedLithiumCell']},
            'subclasses': {'VeniceBoardwalkBrawler': {6: ['HC_Target_Sublet']},
                           'TenderloinBiohazard': {10: ['HC_Target_EverybodyKnowsThisGuy']}},
            'resource_increases': {}}
