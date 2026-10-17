"""Round 6 additions: Oakland Flea Market contraband item table (4 items + shout),
3 subrace stereotype spells (Beachborn L3, Siliconite L3, Inland Emperor L5),
and 3 street-tactics spells (Base L5, Base L11, BART L6).

Local development candidate; NOT gameplay-tested.

Vanilla evidence (extracted data under temp_race/Public):
- WPN_Mace (Weapon.txt) -> RootTemplate 3186796d-3ab3-4d49-bfc2-cba1aff0cf5a, Icon Item_WPN_HUM_Mace_A_0
- ARM_Robe_Destroyed (Armor.txt) -> RootTemplate 14c13bc9-ab35-4cab-a220-23a61cd43845, Icon Item_ARM_Robe_Destroyed_Crash
- ARM_Shoes (Armor.txt) -> RootTemplate 97f37571-35e8-4cc8-8b0d-ff92d20ae0bb, Icon Item_ARM_Shoes
- OBJ_Potion_Healing (Object.txt) -> RootTemplate d47006e9-8a51-453d-b200-9e0d42e9bbab, Icon Item_CONS_Potion_Healing_A
- Spell donors: Shout_SecondWind, Target_ShockingGrasp, Shout_FeyPresence, Projectile_AcidSplash, Target_ViciousMockery.
"""
from pathlib import Path
import xml.etree.ElementTree as ET
from hc_icon_keys import icon_for_spell

FLEA_MARKET_SHOUT = 'HC_Shout_OaklandFleaMarket'
SURFBOARD_CHECK = 'HC_Target_LocalismSurfboardCheck'
ZOOM_LAYOFF = 'HC_Shout_ZoomMassLayoff'
SHAKE_AND_BAKE = 'HC_Projectile_GarageShakeAndBake'
SQUATTER_LIEN = 'HC_Target_SquatterAdversePossession'
CVS_RECEIPT = 'HC_Shout_CVSReceiptScroll'
SIDESHOW_DONUT = 'HC_Target_SideshowMustangDonut'

REBAR_WPN = 'HC_WPN_SharpenedRebarPrybar'
PATAGONIA_ARM = 'HC_ARM_StolenPatagoniaPuffer'
ANKLE_BOOTS = 'HC_ARM_AnkleMonitorSandals'
RHINO_DRINK = 'HC_OBJ_GasStationKratomShot'

RHINO_CONSUME_STATUS = 'HC_POTION_RHINO_SHOT'
RHINO_BUFF_STATUS = 'HC_GAS_STATION_RHINO_RUSH'

ITEMS = (
    (REBAR_WPN, 'Weapon', 'WPN_Mace', '3186796d-3ab3-4d49-bfc2-cba1aff0cf5a',
     'Item_WPN_HUM_Mace_A_0', 'Uncommon', 'Sharpened Interstate-880 Rebar',
     'Yanked out of a crumbling highway median column with a tow strap. Weapon attacks deal an extra 1d4 Piercing damage. Technically still structural.',
     (('Boosts', 'CharacterWeaponDamage(1d4,Piercing)'),)),
    (PATAGONIA_ARM, 'Armor', 'ARM_Robe_Destroyed', '14c13bc9-ab35-4cab-a220-23a61cd43845',
     'Item_ARM_Robe_Destroyed_Crash', 'Uncommon', 'Shoplifted Finance-Bro Patagonia Vest',
     'Still has the plastic anti-theft ink tag clipped to the zipper. Grants +1 Armour Class and advantage on Persuasion checks. Venture capitalists instinctively offer you seed funding.',
     (('Boosts', 'AC(1);Advantage(Skill,Persuasion)'),)),
    (ANKLE_BOOTS, 'Armor', 'ARM_Shoes', '97f37571-35e8-4cc8-8b0d-ff92d20ae0bb',
     'Item_ARM_Shoes', 'Uncommon', 'Foil-Wrapped GPS Ankle Monitor & Jail Slides',
     'Beeps furiously every forty seconds, but three layers of Reynolds Wrap tell your parole officer you are currently inside a library. Grants +1 to Saving Throws and immunity to being knocked Prone.',
     (('Boosts', 'StatusImmunity(SG_Prone);RollBonus(SavingThrow,1)'),)),
    (RHINO_DRINK, 'Object', 'OBJ_Potion_Healing', 'd47006e9-8a51-453d-b200-9e0d42e9bbab',
     'Item_CONS_Potion_Healing_A', 'Uncommon', "Bodega Counter 'Rhino 69K & Kratom' Shot",
     'Sold from a locked acrylic box behind the register next to the glass roses and scratch-off tickets. Restores 2d4+2 Hit Points and grants Gas Station Rhino Rush (+1d6 weapon damage and advantage on Strength checks and saving throws) for 2 turns. The FDA has issued six separate recalls on the holographic rhino.',
     ()),
)

STATUS_SPECS = [
    (RHINO_BUFF_STATUS, FLEA_MARKET_SHOUT, 'Item_CONS_Potion_Speed',
     'Gas Station Rhino Rush',
     'Weapon attacks deal an extra 1d6 damage, and you have advantage on Strength checks and Strength saving throws. Your heart rate is currently audible to dogs.',
     dict(Boosts='CharacterWeaponDamage(1d6);Advantage(Ability,Strength);Advantage(SavingThrow,Strength)')),
    ('HC_VALLEY_KOOK_SHAME', SURFBOARD_CHECK, 'Spell_Enchantment_Bane',
     'banished to the Valley (Kook)',
     'Disadvantage on attack rolls. A forty-year-old trust-fund surfer just screamed LOCALS ONLY in your face.',
     dict(Boosts='Disadvantage(AttackRoll)', StatusPropertyFlags='InitiateCombat')),
    ('HC_STOCK_BUYBACK_SHIELD', ZOOM_LAYOFF, 'Spell_Abjuration_MageArmor',
     'Q4 Stock Buyback Golden Parachute',
     '+2 Armour Class and advantage on Wisdom saving throws. Letting go of fifteen percent of the encounter was the hardest decision you ever made from your Tahoe cabin.',
     dict(Boosts='AC(2);Advantage(SavingThrow,Wisdom)')),
    ('HC_RESTRUCTURED_OUT', ZOOM_LAYOFF, 'Spell_Enchantment_Bane',
     'Impacted by Macroeconomic Headwinds',
     'Movement speed reduced by 3 m and cannot take reactions. Your badge and Slack access have been deactivated effective immediately.',
     dict(Boosts='ActionResource(Movement,-3,0);ActionResourceBlock(ReactionActionPoint)',
          StatusPropertyFlags='InitiateCombat')),
    ('HC_EVICTION_MORATORIUM', SQUATTER_LIEN, 'Spell_Enchantment_Bane',
     'Tied Up in Unlawful Detainer Court',
     'Cannot move and has disadvantage on attack rolls. The sheriff cannot enforce the writ until the maritime-law crayon lien is adjudicated.',
     dict(Boosts='ActionResourceBlock(Movement);Disadvantage(AttackRoll)',
          StatusPropertyFlags='InitiateCombat')),
    ('HC_CVS_COUPON_ARMOR', CVS_RECEIPT, 'Spell_Abjuration_MageArmor',
     'Six-Foot CVS Thermal-Paper Ward',
     '+2 Armour Class and resistance to Slashing and Piercing damage. Wrapped head-to-toe in four expired ExtraBucks offers for toothpaste.',
     dict(Boosts='AC(2);Resistance(Slashing,Resistant);Resistance(Piercing,Resistant)')),
]


def generate_round6(public_dir, add_loca, get_guid):
    public = Path(public_dir)
    stats = public / 'Stats/Generated/Data'
    roots = public / 'RootTemplates'
    stats.mkdir(parents=True, exist_ok=True)
    roots.mkdir(parents=True, exist_ok=True)

    def check(name, fields):
        if not name.startswith('HC_'):
            raise ValueError(f'Stat must start with HC_: {name}')
        for key, value in fields.items():
            if '"' in value or '\n' in value or '\r' in value:
                raise ValueError(f'Unsafe field {name}.{key}')

    # ------------------------------------------------------------------ items
    save = ET.Element('save')
    ET.SubElement(save, 'version', major='4', minor='0', revision='9', build='0')
    region = ET.SubElement(save, 'region', id='Templates')
    templates = ET.SubElement(region, 'node', id='Templates')
    children = ET.SubElement(templates, 'children')
    item_blocks = {'Weapon': [], 'Armor': [], 'Object': []}
    summoned = []

    for name, kind, base_stat, parent, icon, rarity, title, description, extra in ITEMS:
        template_id = get_guid(name + '_RootTemplate')
        title_handle = add_loca(name + '_Name', title)
        description_handle = add_loca(name + '_Description', description)
        obj = ET.SubElement(children, 'node', id='GameObjects')
        for attr, attr_type, value in (
            ('MapKey', 'FixedString', template_id),
            ('Name', 'LSString', name),
            ('ParentTemplateId', 'FixedString', parent),
            ('Stats', 'FixedString', name),
            ('Type', 'FixedString', 'item'),
            ('Icon', 'FixedString', icon),
        ):
            ET.SubElement(obj, 'attribute', id=attr, type=attr_type, value=value)
        for attr, handle in (('DisplayName', title_handle), ('Description', description_handle)):
            ET.SubElement(obj, 'attribute', id=attr, type='TranslatedString', handle=handle, version='1')
        if name == RHINO_DRINK:
            technical = add_loca(name + '_TechnicalDescription',
                                 'Restores 2d4+2 hit points and grants +1d6 weapon damage and advantage on Strength checks and saves for 2 turns.')
            ET.SubElement(obj, 'attribute', id='TechnicalDescription', type='TranslatedString',
                          handle=technical, version='1')
            node_children = ET.SubElement(obj, 'children')
            use = ET.SubElement(node_children, 'node', id='OnUsePeaceActions')
            use_children = ET.SubElement(use, 'children')
            action = ET.SubElement(use_children, 'node', id='Action')
            ET.SubElement(action, 'attribute', id='ActionType', type='int32', value='7')
            action_children = ET.SubElement(action, 'children')
            attrs = ET.SubElement(action_children, 'node', id='Attributes')
            for attr, attr_type, value in (
                ('Animation', 'FixedString', '895ce382-397d-4b9a-9e8f-6ee3b1ff3a13'),
                ('Conditions', 'LSString', ''),
                ('Consume', 'bool', 'True'),
                ('StatsId', 'FixedString', RHINO_CONSUME_STATUS),
                ('StatusDuration', 'int32', '0'),
            ):
                ET.SubElement(attrs, 'attribute', id=attr, type=attr_type, value=value)

        lines = [f'new entry "{name}"', f'type "{kind}"', f'using "{base_stat}"',
                 f'data "RootTemplate" "{template_id}"', f'data "Rarity" "{rarity}"',
                 'data "ValueOverride" "0"']
        lines += [f'data "{key}" "{value}"' for key, value in extra]
        item_blocks[kind].append('\n'.join(lines) + '\n')
        summoned.append(f'SummonInInventory({template_id},-1,1,false,false,false)')

    ET.indent(save, space='    ')
    ET.ElementTree(save).write(roots / 'HC_Round6Items.lsf.lsx', encoding='utf-8', xml_declaration=True)
    (stats / 'HC_Weapon_Round6.txt').write_text('\n'.join(item_blocks['Weapon']), encoding='utf-8')
    (stats / 'HC_Armor_Round6.txt').write_text('\n'.join(item_blocks['Armor']), encoding='utf-8')
    (stats / 'HC_Object_Round6.txt').write_text('\n'.join(item_blocks['Object']), encoding='utf-8')

    # ---------------------------------------------------------------- statuses
    rhino_title = add_loca(RHINO_CONSUME_STATUS + '_Name', "Bodega Counter 'Rhino 69K & Kratom' Shot")
    status_blocks = [f'''new entry "{RHINO_CONSUME_STATUS}"
type "StatusData"
data "StatusType" "BOOST"
data "DisplayName" "{rhino_title};1"
data "Icon" "Item_CONS_Potion_Healing_A"
data "HitAnimationType" "MagicalNonDamage"
data "StackId" "{RHINO_CONSUME_STATUS}"
data "StatusPropertyFlags" "DisableOverhead;DisableCombatlog;DisablePortraitIndicator"
data "OnApplyFunctors" "RegainHitPoints(2d4+2);ApplyStatus({RHINO_BUFF_STATUS},100,2)"
data "ApplyEffect" "89f2d0ac-9295-4657-bfa6-fb6d61adf59c"''']

    for name, icon_spell, fallback_icon, title, description, extra in STATUS_SPECS:
        fields = dict(
            StatusType='BOOST',
            StackId=name,
            StackType='Overwrite',
            TickType='EndTurn',
            Icon=icon_for_spell(icon_spell, fallback_icon),
        )
        fields.update(extra)
        fields['DisplayName'] = add_loca(name + '_Name', title) + ';1'
        fields['Description'] = add_loca(name + '_Description', description) + ';1'
        check(name, fields)
        lines = [f'new entry "{name}"', 'type "StatusData"']
        lines += [f'data "{k}" "{v}"' for k, v in fields.items()]
        status_blocks.append('\n'.join(lines))
    (stats / 'HC_Status_Round6.txt').write_text('\n\n'.join(status_blocks) + '\n', encoding='utf-8')

    # ------------------------------------------------------------------ spells
    base_fields = dict(
        Level='0', Cooldown='OncePerShortRest', DescriptionParams='', ExtraDescription='',
        MemoryCost='0', RechargeValues='', TooltipUpcastDescription='',
        TooltipUpcastDescriptionParams='', TooltipDamageList='', TooltipStatusApply='',
        TooltipAttackSave='', TooltipPermanentWarnings='', TooltipOnSave='',
        SpellProperties='', SpellRoll='', SpellSuccess='', SpellFail='',
        CastTextEvent='Cast',
    )
    wis_save = 'not SavingThrow(Ability.Wisdom, SourceSpellDC())'
    dex_save = 'not SavingThrow(Ability.Dexterity, SourceSpellDC())'

    spell_specs = [
        (FLEA_MARKET_SHOUT, 'Shout_SecondWind', 'Spell_Transmutation_Goodberry',
         'Oakland Flea Market Stolen Tool Table',
         'Unroll a velvet blanket on the asphalt and display goods of deeply questionable provenance. '
         'Costs an action; once per long rest. Places a Sharpened Interstate-880 Rebar, a Shoplifted Finance-Bro Patagonia Vest, '
         'Foil-Wrapped GPS Ankle Monitor & Jail Slides, and a Bodega Counter Rhino 69K & Kratom Shot into your inventory. '
         'No receipts, no refunds, and do not ask why the serial numbers are filed off.',
         dict(UseCosts='ActionPoint:1', Cooldown='OncePerRest', TargetConditions='Self()',
              SpellFlags='IgnoreSilence;UnavailableInDialogs', TargetRadius='0',
              SpellProperties=';'.join(summoned))),

        (SURFBOARD_CHECK, 'Target_ShockingGrasp', 'Action_PushingAttack_Melee',
         'Malibu Trust-Fund Surfboard Localism',
         'Channel a thirty-eight-year-old unemployed Malibu local whose parents bought his beach bungalow in 1978. '
         'Costs an action; once per short rest. Melee spell attack within 1.5 m: deals 2d8 Bludgeoning plus 1d6 Cold damage, '
         'shoves the target back 4 m, and leaves it Banished to the Valley (disadvantage on attack rolls) for 2 turns. '
         'Locals only, kook, go back to Encino.',
         dict(UseCosts='ActionPoint:1', TargetRadius='1.5', DamageType='Bludgeoning',
              TargetConditions='Character() and not Ally() and not Dead()',
              SpellRoll='Attack(AttackType.MeleeSpellAttack)',
              SpellSuccess='DealDamage(2d8,Bludgeoning,Magical);DealDamage(1d6,Cold,Magical);Force(4, OriginToTarget);ApplyStatus(HC_VALLEY_KOOK_SHAME,100,2)',
              TooltipDamageList='DealDamage(2d8,Bludgeoning);DealDamage(1d6,Cold)',
              TooltipAttackSave='MeleeSpellAttack',
              TooltipStatusApply='ApplyStatus(HC_VALLEY_KOOK_SHAME,100,2)')),

        (ZOOM_LAYOFF, 'Shout_FeyPresence', 'Spell_Enchantment_Bane',
         '9 AM Zoom All-Hands 15% Layoff',
         'Put on a five-hundred-dollar cashmere hoodie, shed one rehearsed tear into the webcam, and take full responsibility for '
         'firing everyone around you. Costs an action; once per short rest. Gain +2 AC and advantage on Wisdom saving throws for 2 turns, '
         'while enemies within 6 m make a Wisdom saving throw: on a failure they take 2d8 Psychic damage and lose 3 m movement and '
         'reactions for 2 turns, or take half damage on a success. Your Slack access has been revoked.',
         dict(UseCosts='ActionPoint:1', AreaRadius='6', SpellContainerID='',
              TargetConditions='Enemy()',
              SpellProperties='ApplyStatus(SELF,HC_STOCK_BUYBACK_SHIELD,100,2)',
              SpellRoll=wis_save,
              SpellSuccess='DealDamage(2d8,Psychic,Magical);ApplyStatus(HC_RESTRUCTURED_OUT,100,2)',
              SpellFail='DealDamage((2d8)/2,Psychic,Magical)',
              TooltipDamageList='DealDamage(2d8,Psychic)',
              TooltipAttackSave='Wisdom',
              TooltipStatusApply='ApplyStatus(HC_RESTRUCTURED_OUT,100,2)')),

        (SHAKE_AND_BAKE, 'Projectile_AcidSplash', 'Spell_Evocation_FireBolt',
         'Hemet Garage 2-Liter Shake-and-Bake Rupture',
         'Hurl a warm two-liter soda bottle packed with camp fuel, lithium strips, and crushed cold medicine just as it goes supercritical. '
         'Costs an action; once per long rest. Ignites a 3 m fire surface for 2 turns while creatures in a 3 m radius make a Dexterity saving throw, '
         'taking 3d8 Fire plus 2d8 Poison damage and Burning for 2 turns on a failure, or half damage on a success. '
         'The eyebrows will grow back by November.',
         dict(UseCosts='ActionPoint:1', Cooldown='OncePerRest', AreaRadius='3', ExplodeRadius='3', DamageType='Fire',
              SpellProperties='GROUND:CreateSurface(3,2,Fire)',
              SpellRoll=dex_save,
              SpellSuccess='DealDamage(3d8,Fire,Magical);DealDamage(2d8,Poison,Magical);ApplyStatus(BURNING,100,2)',
              SpellFail='DealDamage((3d8)/2,Fire,Magical);DealDamage((2d8)/2,Poison,Magical)',
              TooltipDamageList='DealDamage(3d8,Fire);DealDamage(2d8,Poison)',
              TooltipAttackSave='Dexterity',
              TooltipStatusApply='ApplyStatus(BURNING,100,2)')),

        (SQUATTER_LIEN, 'Target_ViciousMockery', 'Spell_Enchantment_Bane',
         'Fake Lease & Sovereign Citizen Lien',
         'Serve your opponent with a crayon-notarized maritime-law lease claiming you have lived in their armour since 2019. '
         'Costs an action and 1 Junk; once per short rest. A target within 9 m makes a Wisdom saving throw: on a failure it takes '
         '2d8 Psychic damage and is Tied Up in Unlawful Detainer Court (cannot move and disadvantage on attack rolls) for 2 turns, '
         'or takes half damage on a success. The sheriff cannot evict you until the court date in 2028.',
         dict(UseCosts='ActionPoint:1;HC_Junk:1', TargetRadius='9',
              TargetConditions='Character() and not Ally() and not Dead()',
              SpellRoll=wis_save,
              SpellSuccess='DealDamage(2d8,Psychic,Magical);ApplyStatus(HC_EVICTION_MORATORIUM,100,2)',
              SpellFail='DealDamage((2d8)/2,Psychic,Magical)',
              TooltipDamageList='DealDamage(2d8,Psychic)',
              TooltipAttackSave='Wisdom',
              TooltipStatusApply='ApplyStatus(HC_EVICTION_MORATORIUM,100,2)')),

        (CVS_RECEIPT, 'Shout_SecondWind', 'Spell_Abjuration_MageArmor',
         'Six-Foot CVS Receipt Ward',
         'Wrap yourself like a pharaoh in the indestructible six-foot thermal-paper coupon scroll from buying a single pack of gum. '
         'Costs a bonus action and 1 Junk; once per short rest. Gain +2 Armour Class and resistance to Slashing and Piercing damage for 2 turns. '
         'Expires tomorrow, excluding dairy and gift cards.',
         dict(UseCosts='BonusActionPoint:1;HC_Junk:1', TargetConditions='Self()',
              SpellProperties='ApplyStatus(HC_CVS_COUPON_ARMOR,100,2)',
              TooltipStatusApply='ApplyStatus(HC_CVS_COUPON_ARMOR,100,2)')),

        (SIDESHOW_DONUT, 'Target_ViciousMockery', 'Spell_Evocation_Thunderwave',
         '3 AM Oakland Intersection Sideshow',
         'Shut down the intersection while a stolen V6 muscle car with a missing bumper swings wild donuts through a cloud of burning rubber. '
         'Costs an action and 1 Junk; once per short rest. Creates a 2.5 m cloud of tire smoke for 2 turns while a target within 9 m '
         'makes a Dexterity saving throw, taking 3d8 Bludgeoning plus 1d8 Fire damage and falling Prone for 1 turn on a failure, '
         'or half damage on a success. Fifteen bystanders are filming with their flash on.',
         dict(UseCosts='ActionPoint:1;HC_Junk:1', TargetRadius='9', DamageType='Bludgeoning',
              TargetConditions='Character() and not Ally() and not Dead()',
              SpellProperties='GROUND:CreateSurface(2.5,2,FogCloud)',
              SpellRoll=dex_save,
              SpellSuccess='DealDamage(3d8,Bludgeoning,Magical);DealDamage(1d8,Fire,Magical);ApplyStatus(PRONE,100,1)',
              SpellFail='DealDamage((3d8)/2,Bludgeoning,Magical);DealDamage((1d8)/2,Fire,Magical)',
              TooltipDamageList='DealDamage(3d8,Bludgeoning);DealDamage(1d8,Fire)',
              TooltipAttackSave='Dexterity',
              TooltipStatusApply='ApplyStatus(PRONE,100,1)')),
    ]

    spell_blocks = []
    for name, donor, fallback_icon, title, description, overrides in spell_specs:
        fields = dict(base_fields)
        fields.update(overrides)
        fields['Icon'] = icon_for_spell(name, fallback_icon)
        fields['DisplayName'] = add_loca(name + '_Name', title) + ';1'
        fields['Description'] = add_loca(name + '_Description', description) + ';1'
        check(name, fields)
        lines = [f'new entry "{name}"', 'type "SpellData"', f'using "{donor}"']
        lines += [f'data "{k}" "{v}"' for k, v in fields.items()]
        spell_blocks.append('\n'.join(lines))
    (stats / 'HC_Spells_Round6.txt').write_text('\n\n'.join(spell_blocks) + '\n', encoding='utf-8')

    return {
        'base': {
            5: [SQUATTER_LIEN],
            8: [FLEA_MARKET_SHOUT],
            11: [CVS_RECEIPT],
        },
        'subclasses': {
            'BARTPlatformMenace': {6: [SIDESHOW_DONUT]},
        },
        'subrace_spells': {
            'Beachborn_L3': SURFBOARD_CHECK,
            'Siliconite_L3': ZOOM_LAYOFF,
            'InlandEmperor_L5': SHAKE_AND_BAKE,
        },
    }
