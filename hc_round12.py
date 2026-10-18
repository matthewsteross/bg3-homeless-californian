"""Round 12: ten self-cast base-class Shouts that each drop a funny object (the prop is attached by hc_<prop>.py modules).

Brainstormed by Gemini Flash and Gemini Argon (work/r12-flash.md, work/r12-argon.md), shaped by the lead.
Shapes copy stats that earlier rounds cite vanilla evidence for: Shout_SecondWind (self shout applying a status,
RegainHitPoints as in HC_Target_CurbsideClinic) and Shout_FeyPresence (area save shout as in HC_Shout_ReplyAllWholeCompany),
GROUND:CreateSurface(...,Water) as in hc_sub_round2.py. The ground prop is appended later to SpellProperties by the
prop modules (hc_mailbox.py ... hc_walkoffame.py) using hc_prop_lifetime.py.
UNVERIFIED in game: everything, including area targeting around the dropped prop.
"""
from pathlib import Path
from hc_icon_keys import icon_for_spell

HOSTILE = 'Enemy() and not Dead()'
STATUS_SPECS = [
    ('HC_MAILBOX_SANCTUARY', 'Federal Mailbox Sanctuary', 'Gain +2 Armour Class. Tampering with it carries a twenty-year federal prison sentence, making it the most legally bulletproof fort in the city.',
     'AC(2)', 'Spell_Abjuration_ShieldOfFaith'),
    ('HC_COINSTAR_CASHOUT', 'Coinstar Cash-Out', 'Gain +3 m movement and +1 Armour Class. It takes an 11.9 percent fee, two Canadian dimes and a Chuck E. Cheese token, and still beats your 401(k).',
     'ActionResource(Movement,3,0);AC(1)', 'Spell_Transmutation_Longstrider'),
    ('HC_PRIVACY_POD', 'Open-Office Privacy Pod', 'Gain +2 Armour Class and resistance to Psychic and Thunder damage. Ninety-eight percent acoustic reduction, so your venture debt sync is private.',
     'AC(2);Resistance(Psychic,Resistant);Resistance(Thunder,Resistant)', 'Spell_Abjuration_ProtectionFromEnergy'),
    ('HC_DANGER_DOG_BUFF', 'Danger Dog Afterglow', 'Gain +3 m movement and resistance to Poison damage. Operating outside the Palladium with zero health permits and an aroma that resurrects the dead.',
     'ActionResource(Movement,3,0);Resistance(Poison,Resistant)', 'Spell_Transmutation_Longstrider'),
    ('HC_TACO_TRUCK_BUFF', 'Lonchera Fortitude', 'Gain +2 Armour Class and +3 m movement. The transmission fell out in 2011 and the carnitas reached critical mass.',
     'AC(2);ActionResource(Movement,3,0)', 'Spell_Enchantment_Heroism'),
]
SPELL_SPECS = []


def _spell(level, name, title, icon, donor, mechanics, joke, fields):
    SPELL_SPECS.append((level, name, title, donor, icon, mechanics + ' ' + joke, fields))


def _self(status, turns, extra=''):
    props = f'ApplyStatus({status},100,{turns})' + (';' + extra if extra else '')
    return dict(TargetConditions='', SpellProperties=props, TooltipStatusApply=f'ApplyStatus({status},100,{turns})',
                SpellFlags='IsSpell;HasVerbalComponent;HasSomaticComponent')


def _area(ability, dice, damage, radius, status='', props=''):
    return dict(TargetRadius='0', AreaRadius=str(radius), TargetConditions=HOSTILE, SpellProperties=props,
                SpellRoll=f'not SavingThrow(Ability.{ability}, SourceSpellDC())',
                SpellSuccess=f'DealDamage({dice},{damage},Magical)' + (';' + status if status else ''),
                SpellFail=f'DealDamage(({dice})/2,{damage},Magical)', DamageType=damage,
                TooltipDamageList=f'DealDamage({dice},{damage})', TooltipAttackSave=ability, TooltipStatusApply=status,
                SpellFlags='IsSpell;HasVerbalComponent;HasSomaticComponent')


SECOND, FEY = 'Shout_SecondWind', 'Shout_FeyPresence'
_spell(2, 'HC_Shout_FederalMailboxSanctuary', 'Federal Mailbox Sanctuary', 'Spell_Abjuration_ShieldOfFaith', SECOND,
       'Costs a bonus action and 1 Junk; once per short rest. A blue USPS box drops at your feet and you gain +2 Armour Class for 2 turns.',
       'Tampering with it carries a twenty-year federal prison sentence.', dict(UseCosts='BonusActionPoint:1;HC_Junk:1', **_self('HC_MAILBOX_SANCTUARY', 2)))
_spell(4, 'HC_Shout_StolenCoinstarJackpot', 'Stolen Coinstar Reject-Tray Jackpot', 'Spell_Transmutation_Longstrider', SECOND,
       'Costs a bonus action and 1 Junk; once per short rest. A coin-counting kiosk drops at your feet; you regain 2d6+4 Hit Points and gain +3 m movement and +1 Armour Class for 2 turns.',
       'It takes an 11.9 percent processing fee and two Canadian dimes, and still beats your 401(k).',
       dict(UseCosts='BonusActionPoint:1;HC_Junk:1', **_self('HC_COINSTAR_CASHOUT', 2, 'RegainHitPoints(2d6+4)')))
_spell(5, 'HC_Shout_RedCurbHydrantBlowout', 'Red-Curb Fire Hydrant Blowout', 'Spell_Transmutation_CreateWater', FEY,
       'Costs an action and 1 Junk; once per short rest. A sheared hydrant geysers at your feet; enemies within 4 m make a Strength save, taking 3d8 Bludgeoning damage and falling Prone for 1 turn on failure, or half damage on success. Water covers the ground for 3 turns.',
       'Public Works scheduled the repair for 2029, so enjoy your complimentary car wash.',
       dict(UseCosts='ActionPoint:1;HC_Junk:1', **_area('Strength', '3d8', 'Bludgeoning', 4, 'ApplyStatus(PRONE,100,1)', 'GROUND:CreateSurface(4,3,Water)')))
_spell(6, 'HC_Shout_AcousticPrivacyPod', 'Acoustic Open-Office Privacy Pod', 'Spell_Abjuration_ProtectionFromEnergy', SECOND,
       'Costs an action and 2 Junk; once per short rest. A phone booth pod drops at your feet; for 3 turns you gain +2 Armour Class and resistance to Psychic and Thunder damage.',
       'Ninety-eight percent acoustic reduction, so nobody hears you cry during the venture debt sync.',
       dict(UseCosts='ActionPoint:1;HC_Junk:2', **_self('HC_PRIVACY_POD', 3)))
_spell(7, 'HC_Shout_MufflerShopTotem', 'Muffler Shop Scrap Metal Totem', 'Spell_Conjuration_StinkingCloud', FEY,
       'Costs an action and 2 Junk; once per short rest. A welded exhaust totem drops at your feet; enemies within 5 m make a Constitution save, taking 3d8 Poison damage and becoming Poisoned for 2 turns on failure, or half damage on success.',
       'Welded together in eighteen minutes of midnight Sawzall labour behind a Pep Boys.',
       dict(UseCosts='ActionPoint:1;HC_Junk:2', **_area('Constitution', '3d8', 'Poison', 5, 'ApplyStatus(POISONED,100,2)')))
_spell(8, 'HC_Shout_BaconWrappedDangerDogCart', 'Bootleg Bacon-Wrapped Danger-Dog Cart', 'Spell_Transmutation_Longstrider', SECOND,
       'Costs an action and 2 Junk; once per short rest. A sizzling hot-dog cart drops at your feet; you regain 3d8+6 Hit Points and gain +3 m movement and resistance to Poison damage for 3 turns.',
       'Operating outside the Palladium with zero health permits and an aroma powerful enough to resurrect the dead.',
       dict(UseCosts='ActionPoint:1;HC_Junk:2', **_self('HC_DANGER_DOG_BUFF', 3, 'RegainHitPoints(3d8+6)')))
_spell(9, 'HC_Shout_CybertruckHuskOnBlocks', 'Cinderblock-Mounted Cybertruck Husk', 'Spell_Evocation_ShockingGrasp', FEY,
       'Costs an action and 2 Junk; once per long rest. A stripped steel pickup husk drops at your feet; enemies within 5 m make a Dexterity save, taking 4d8 Lightning damage and becoming Stunned for 1 turn on failure, or half damage on success.',
       'Brick-moded by a car wash and stripped in Oakland in eleven minutes, yet the owner still tweeted that he loves the truck.',
       dict(UseCosts='ActionPoint:1;HC_Junk:2', Cooldown='OncePerRest', **_area('Dexterity', '4d8', 'Lightning', 5, 'ApplyStatus(STUNNED,100,1)')))
_spell(10, 'HC_Shout_AmberAlertMatrixTrailer', 'Caltrans Solar Amber-Alert Matrix Trailer', 'Spell_Evocation_Thunderwave', FEY,
       'Costs an action and 2 Junk; once per long rest. A flashing highway sign trailer drops at your feet; enemies within 6 m make a Constitution save, taking 4d8 Radiant damage and becoming Blinded and Slowed for 2 turns on failure, or half damage on success.',
       'SEVERE TRAFFIC ALERT: YOUR POOR LIFE CHOICES AHEAD. EXPECT DELAYS THROUGH NEXT TUESDAY.',
       dict(UseCosts='ActionPoint:1;HC_Junk:2', Cooldown='OncePerRest', **_area('Constitution', '4d8', 'Radiant', 6, 'ApplyStatus(BLINDED,100,2);ApplyStatus(SLOW,100,2)')))
_spell(11, 'HC_Shout_LoncheraTacoTruck', 'Up-On-Blocks Lonchera Taco Truck', 'Spell_Enchantment_Heroism', SECOND,
       'Costs an action and 3 Junk; once per long rest. A taco truck drops at your feet; you regain 4d8+8 Hit Points and gain +2 Armour Class and +3 m movement for 3 turns.',
       'Parked by a fire hydrant since 2011 because the transmission fell out and the carnitas reached critical mass.',
       dict(UseCosts='ActionPoint:1;HC_Junk:3', Cooldown='OncePerRest', **_self('HC_TACO_TRUCK_BUFF', 3, 'RegainHitPoints(4d8+8)')))
_spell(12, 'HC_Shout_WalkOfFameStarSlam', 'Walk-of-Fame Terrazzo Star Slam', 'Spell_Evocation_Shatter', FEY,
       'Costs an action and 3 Junk; once per long rest. A chunk of sidewalk with a brass star slams down at your feet; enemies within 6 m make a Strength save, taking 5d8 Thunder damage and becoming Stunned and Prone for 1 turn on failure, or half damage on success.',
       'You paid the Chamber of Commerce fifty thousand dollars for a brass star that three tourists and a pigeon just peed on.',
       dict(UseCosts='ActionPoint:1;HC_Junk:3', Cooldown='OncePerRest', **_area('Strength', '5d8', 'Thunder', 6, 'ApplyStatus(STUNNED,100,1);ApplyStatus(PRONE,100,1)')))


def generate_round12(public_dir, add_loca, get_guid):
    stats = Path(public_dir) / 'Stats/Generated/Data'
    stats.mkdir(parents=True, exist_ok=True)

    def block(name, kind, title, description, fields, donor=None):
        values = dict(fields, DisplayName=add_loca(name + '_Name', title) + ';1',
                      Description=add_loca(name + '_Description', description) + ';1')
        for key, value in values.items():
            if any(char in value for char in ('"', '\n', '\r')):
                raise ValueError(f'Unsafe field {name}.{key}')
        lines = [f'new entry "{name}"', f'type "{kind}"']
        if donor:
            lines.append(f'using "{donor}"')
        return '\n'.join(lines + [f'data "{k}" "{v}"' for k, v in values.items()])

    statuses = [block(n, 'StatusData', t, d, dict(StatusType='BOOST', StackId=n, StackType='Overwrite', TickType='EndTurn',
                                                  Icon=icon_for_spell(n, i), Boosts=b)) for n, t, d, b, i in STATUS_SPECS]
    (stats / 'HC_Status_Round12.txt').write_text('\n\n'.join(statuses) + '\n', encoding='utf-8')
    base = dict(Level='0', Cooldown='OncePerShortRest', MemoryCost='0', RechargeValues='', RootSpellID='', SpellContainerID='',
                DescriptionParams='', ExtraDescription='', TooltipUpcastDescription='', TooltipUpcastDescriptionParams='',
                TooltipDamageList='', TooltipStatusApply='', TooltipAttackSave='', TooltipPermanentWarnings='', TooltipOnSave='',
                SpellProperties='', SpellRoll='', SpellSuccess='', SpellFail='', CastTextEvent='Cast')
    spells, grants = [], dict(base={}, subclasses={}, existing_list_spells={})
    for level, name, title, donor, icon, description, overrides in SPELL_SPECS:
        fields = dict(base)
        fields.update(overrides)
        fields['Icon'] = icon_for_spell(name, icon)
        spells.append(block(name, 'SpellData', title, description, fields, donor))
        grants['base'].setdefault(level, []).append(name)
    (stats / 'HC_Spells_Round12.txt').write_text('\n\n'.join(spells) + '\n', encoding='utf-8')
    return grants
