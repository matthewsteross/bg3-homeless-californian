"""Round 13 consumable items for Homeless Californian.

Vanilla mechanic evidence (file:line):
- TemporaryHP(20): Shared/Stats/Generated/Data/Status_BOOST.txt:5868
- Resistance(Psychic, Resistant): Shared/Stats/Generated/Data/Status_BOOST.txt:7194
- Disadvantage(SavingThrow,Dexterity): Shared/Stats/Generated/Data/Status_BOOST.txt:391
- RegainHitPoints: Shared/Stats/Generated/Data/Spell_Target.txt:1541
- RemoveStatus(SG_Poisoned): Shared/Stats/Generated/Data/Spell_Target.txt:2601
- Dexterity save, 18 m target and 2 m area projectile pattern:
  Shared/Stats/Generated/Data/Spell_Projectile.txt:1808-1823 (Projectile_AcidSplash)
- Grenade donor: Shared/Stats/Generated/Data/Object.txt:5864-5874 (_Grenade / ItemUseType Grenade)
- SummonInInventory pattern: SharedDev/Stats/Generated/Data/Spell_Target.txt:6362

UNVERIFIED in game: item consumption, status timing, healing/condition removal,
grenade throw range and explosion damage behavior.
"""
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from hc_icon_keys import icon_for_spell

GUMMY = 'HC_OBJ_GreyMarketDelta8Gummy'
BROTH = 'HC_OBJ_ArtisanalBoneBroth'
BATTERY = 'HC_OBJ_LimeScooterBatteryPack'
GUMMY_USE = 'HC_R13_DELTA8_USE'
BROTH_USE = 'HC_R13_BONE_BROTH_USE'
GUMMY_STATUS = 'HC_R13_DELTA8_EFFECT'
BATTERY_PROJECTILE = 'HC_Projectile_LimeScooterBatteryPack'
ITEMS = (
    (GUMMY, 'Object', 'OBJ_Potion_Healing', 'd47006e9-8a51-453d-b200-9e0d42e9bbab', 'Item_CONS_Potion_Healing_A', '1000mg Grey-Market Delta-8 Gummy', 'Uncommon consumable: eat it as a bonus action to gain 20 temporary Hit Points and Psychic resistance for 3 turns. You also have disadvantage on Dexterity saving throws for those 3 turns. The packaging lists a dosage, a phone number, and a drawing of a bear wearing sunglasses. Bought from an unlicensed smoke shop that also sells swords and wholesale phone chargers.', 'Uncommon'),
    (BROTH, 'Object', 'OBJ_Potion_Healing', 'd47006e9-8a51-453d-b200-9e0d42e9bbab', 'Item_CONS_Potion_Healing_A', 'Shoplifted Artisanal Bone Broth', 'Rare consumable: drink it as a bonus action to remove the Poisoned condition and restore 3d8+4 Hit Points. Its label boasts grass-fed marrow, a forty-eight-hour simmer, and an origin story involving a very upscale farm. The jar is warm from being held under a jacket through three security cameras. Simmered 48 hours from grass-fed marrow and smuggled out under an oversized puffer jacket.', 'Rare'),
    (BATTERY, 'Object', '_Grenade', 'c9e45e5a-f089-480b-ab3a-7f5f76dccc3b', 'Item_LOOT_GEN_Throwable_Grenade_Confusion_A', 'Unlocked Lime Scooter Battery Pack', 'Rare grenade: throw it up to 18 m; creatures within 3 m make a Dexterity save, taking 3d10 Lightning and 2d6 Fire damage on a failure, or half damage on a success. The scooter app insists the battery is still assigned to a former roommate. It has a tiny QR code that opens a parking appeal form. Pry open the casing with a butter knife and the lithium cells negotiate for you.', 'Rare'),
)
STATUS_SPECS = (
    (GUMMY_STATUS, 'Unlicensed Calm', 'Gain 20 temporary Hit Points and Psychic resistance, with disadvantage on Dexterity saving throws, for 3 turns. The receipt is legally a napkin.', {'Boosts': 'TemporaryHP(20);Resistance(Psychic, Resistant);Disadvantage(SavingThrow,Dexterity)'}),
    (GUMMY_USE, 'Delta-8 Gummy', 'Gain Unlicensed Calm for 3 turns. The dosage advice was written on the back of a phone charger.', {'OnApplyFunctors': f'ApplyStatus({GUMMY_STATUS},100,3)'}),
    (BROTH_USE, 'Bone Broth', 'Remove Poisoned and restore 3d8+4 Hit Points. The jar has filed for an artisanal designation.', {'OnApplyFunctors': 'RemoveStatus(SG_Poisoned);RegainHitPoints(3d8+4)'}),
)


def _emit(name, kind, fields, donor=None):
    if not name.startswith('HC_'):
        raise ValueError(name)
    lines = [f'new entry "{name}"', f'type "{kind}"']
    if donor:
        lines.append(f'using "{donor}"')
    for key, value in fields.items():
        if any(char in value for char in ('"', '\n', '\r')):
            raise ValueError(f'Unsafe {name}.{key}')
        lines.append(f'data "{key}" "{value}"')
    return '\n'.join(lines)


def patch_round13_glovebox_spell(stats_dir, template_guids):
    """Append missing Round 13 summons while preserving all other spell data."""
    matches = []
    pattern = re.compile(r'(new entry "HC_Shout_GloveBoxCleanout"[^\S\r\n]*\r?\n)(.*?)(?=^new entry |\Z)', re.M | re.S)
    for path in sorted(Path(stats_dir).glob('*.txt')):
        text = path.read_text(encoding='utf-8')
        for match in pattern.finditer(text):
            matches.append((path, text, match))
    if len(matches) != 1:
        raise ValueError(f'Expected exactly one HC_Shout_GloveBoxCleanout spell; found {len(matches)} in {stats_dir}')
    path, text, match = matches[0]
    block = match.group(0)
    prop = re.search(r'(data "SpellProperties" ")([^"]*)(")', block)
    if prop is None:
        raise ValueError('HC_Shout_GloveBoxCleanout has no SpellProperties value')
    value = prop.group(2)
    terms = value.split(';') if value else []
    additions = [f'SummonInInventory({template_guids[name]},-1,1,false,false,false)' for name in (GUMMY, BROTH, BATTERY)]
    for term in additions:
        if term not in terms:
            terms.append(term)
    new_value = ';'.join(terms)
    if new_value == value:
        return
    block = block[:prop.start(2)] + new_value + block[prop.end(2):]
    path.write_text(text[:match.start()] + block + text[match.end():], encoding='utf-8', newline='\n')


def generate_round13_items(public_dir, add_loca, get_guid):
    public = Path(public_dir)
    stats = public / 'Stats/Generated/Data'
    roots = public / 'RootTemplates'
    stats.mkdir(parents=True, exist_ok=True)
    roots.mkdir(parents=True, exist_ok=True)

    def loca(name, title, description):
        return {'DisplayName': add_loca(name + '_Name', title) + ';1', 'Description': add_loca(name + '_Description', description) + ';1'}

    save = ET.Element('save')
    ET.SubElement(save, 'version', major='4', minor='0', revision='9', build='0')
    region = ET.SubElement(save, 'region', id='Templates')
    kids = ET.SubElement(ET.SubElement(region, 'node', id='Templates'), 'children')
    item_blocks = []
    template_guids = {}
    for name, kind, donor, parent, icon, title, description, rarity in ITEMS:
        template_guid = get_guid(name + '_RootTemplate')
        template_guids[name] = template_guid
        obj = ET.SubElement(kids, 'node', id='GameObjects')
        attrs = [('MapKey', 'FixedString', template_guid), ('Name', 'LSString', name), ('ParentTemplateId', 'FixedString', parent), ('Stats', 'FixedString', name), ('Type', 'FixedString', 'item'), ('Icon', 'FixedString', icon_for_spell(name, icon))]
        for key, typ, value in attrs:
            ET.SubElement(obj, 'attribute', id=key, type=typ, value=value)
        for key, value in loca(name, title, description).items():
            ET.SubElement(obj, 'attribute', id=key, type='TranslatedString', handle=value.split(';')[0], version='1')
        if name in (GUMMY, BROTH):
            use = ET.SubElement(ET.SubElement(obj, 'children'), 'node', id='OnUsePeaceActions')
            action = ET.SubElement(ET.SubElement(use, 'children'), 'node', id='Action')
            ET.SubElement(action, 'attribute', id='ActionType', type='int32', value='7')
            attrs_node = ET.SubElement(ET.SubElement(action, 'children'), 'node', id='Attributes')
            stats_id = GUMMY_USE if name == GUMMY else BROTH_USE
            for key, typ, value in [('Animation', 'FixedString', '895ce382-397d-4b9a-9e8f-6ee3b1ff3a13'), ('Conditions', 'LSString', ''), ('Consume', 'bool', 'True'), ('StatsId', 'FixedString', stats_id), ('StatusDuration', 'int32', '0')]:
                ET.SubElement(attrs_node, 'attribute', id=key, type=typ, value=value)
        extra = {'RootTemplate': template_guid, 'Rarity': rarity, 'ValueOverride': '0'}
        if name == GUMMY:
            extra['UseCosts'] = 'BonusActionPoint:1'
        elif name == BROTH:
            extra['UseCosts'] = 'BonusActionPoint:1'
        elif name == BATTERY:
            extra.update(SpellId=BATTERY_PROJECTILE, ItemUseType='Grenade')
        item_blocks.append(_emit(name, kind, {**extra, **loca(name, title, description)}, donor))
    ET.indent(save, space='    ')
    ET.ElementTree(save).write(roots / 'HC_Round13Items.lsf.lsx', encoding='utf-8', xml_declaration=True)
    (stats / 'HC_Object_Round13Items.txt').write_text('\n\n'.join(item_blocks) + '\n', encoding='utf-8')

    status_blocks = []
    for name, title, description, extra in STATUS_SPECS:
        fields = {'StatusType': 'BOOST', 'StackId': name, 'StackType': 'Overwrite', 'TickType': 'EndTurn', 'Icon': icon_for_spell(name, 'Spell_Evocation_Thunderwave'), **extra, **loca(name, title, description)}
        status_blocks.append(_emit(name, 'StatusData', fields))
    (stats / 'HC_Status_Round13Items.txt').write_text('\n\n'.join(status_blocks) + '\n', encoding='utf-8')

    battery_desc = ITEMS[2][5]
    projectile = _emit(BATTERY_PROJECTILE, 'SpellData', {
        'SpellType': 'Projectile', 'Level': '0', 'TargetFloor': '-1', 'TargetRadius': '18', 'AreaRadius': '3', 'ExplodeRadius': '3',
        'SpellRoll': 'not SavingThrow(Ability.Dexterity, SourceSpellDC())',
        'SpellSuccess': 'DealDamage(3d10,Lightning,Magical);DealDamage(2d6,Fire,Magical)',
        'SpellFail': 'DealDamage((3d10)/2,Lightning,Magical);DealDamage((2d6)/2,Fire,Magical)',
        'TooltipDamageList': 'DealDamage(3d10,Lightning);DealDamage(2d6,Fire)', 'TooltipAttackSave': 'Dexterity',
        'DamageType': 'Lightning', 'UseCosts': '', 'ProjectileCount': '1', 'Icon': icon_for_spell(BATTERY_PROJECTILE, 'Spell_Evocation_Thunderwave'),
        'DisplayName': loca(BATTERY_PROJECTILE, 'Unlocked Lime Scooter Battery Pack', battery_desc)['DisplayName'],
        'Description': loca(BATTERY_PROJECTILE, 'Unlocked Lime Scooter Battery Pack', battery_desc)['Description'],
    }, 'Projectile_AcidSplash')
    (stats / 'HC_Spell_Projectile_Round13Items.txt').write_text(projectile + '\n', encoding='utf-8')
    patch_round13_glovebox_spell(stats, template_guids)
    return {'base': {}, 'subclasses': {}, 'existing_list_spells': {}}
