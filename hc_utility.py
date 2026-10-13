"""Junk exploration and Tenderloin support; vanilla spell donors supply visuals."""
from pathlib import Path
from hc_icon_keys import icon_for_spell


def generate_utility(public_dir, add_loca, get_guid):
    specs = [
        ('HC_Target_CoatHangerSlimJim', 'Target_Knock', 'Coat-Hanger Slim Jim',
         'Unlock a door or container within 1.5 m. Costs an action and 1 Junk. Cannot open magical locks. Every lock is a suggestion with paperwork.',
         dict(TargetRadius='1.5', SpellFlags='IsSpell;HasVerbalComponent',
              TargetConditions="Item() and (Locked() or Tagged('KNOCK_TARGET')) and not Tagged('KNOCKBLOCK') and not HasStatus('ARCANE_LOCK')",
              SpellProperties='Unlock()', Icon='Spell_Transmutation_Knock')),
        ('HC_Target_CurbsideClinic', 'Target_LesserRestoration', 'Curbside Needle Exchange',
         'Cure Poisoned, Diseased, Blinded and Paralysed on a living ally within 1.5 m, and restore 2d6 + Constitution modifier Hit Points. Costs an action and 1 Junk; once per short rest. The clinic has no address. It has standards.',
         dict(TargetRadius='1.5', TargetConditions='Character() and Ally() and not Dead()',
              Cooldown='OncePerShortRest', Icon='Spell_Abjuration_LesserRestoration',
              SpellProperties='RemoveStatus(SG_Poisoned);RemoveStatus(SG_Disease);RemoveStatus(SG_Blinded);RemoveStatus(SG_Paralyzed);RegainHitPoints(2d6+ConstitutionModifier)',
              TooltipDamageList='RegainHitPoints(2d6+ConstitutionModifier)',
              TooltipStatusApply='RemoveStatus(SG_Poisoned);RemoveStatus(SG_Disease);RemoveStatus(SG_Blinded);RemoveStatus(SG_Paralyzed)')),
    ]
    blocks = []
    for name, donor, title, description, overrides in specs:
        fields = dict(Level='0', UseCosts='ActionPoint:1;HC_Junk:1', MemoryCost='0', Cooldown='', RechargeValues='',
                      DescriptionParams='', ExtraDescription='', TooltipUpcastDescription='',
                      TooltipUpcastDescriptionParams='', TooltipDamageList='', TooltipStatusApply='',
                      TooltipAttackSave='', TooltipPermanentWarnings='', SpellProperties='',
                      SpellSuccess='', SpellFail='', CastTextEvent='Cast')
        fields.update(overrides)
        fields['Icon'] = icon_for_spell(name, fields['Icon'])
        fields['DisplayName'] = add_loca(name + '_Name', title) + ';1'
        fields['Description'] = add_loca(name + '_Description', description) + ';1'
        lines = [f'new entry "{name}"', 'type "SpellData"', f'using "{donor}"']
        for key, value in fields.items():
            if '"' in value or '\n' in value:
                raise ValueError(f'Unsafe field {name}.{key}')
            lines.append(f'data "{key}" "{value}"')
        blocks.append('\n'.join(lines))
    target = Path(public_dir) / 'Stats/Generated/Data/HC_Spells_Utility.txt'
    target.write_text('\n\n'.join(blocks) + '\n', encoding='utf-8')
    return {'base': {4: ['HC_Target_CoatHangerSlimJim']},
            'subclasses': {'TenderloinBiohazard': {6: ['HC_Target_CurbsideClinic']}}}
