"""Round 16: two camp features from work/r13-agy.md (ideas 11 and 12), built on a rest listener in hc_proplua.py.

Sunset Strip Sound Bath (base level 3): when a character who has it finishes a Short Rest, the whole party gets Temporary Hit Points.
Curbside Mattress Appraisal (base level 5): after a Long Rest the character finds 2 Junk and gets +1 to saving throws until the next
Long Rest (the status has no end and is replaced by the next rest). The exhaustion cleanse of the original idea was dropped (no
verified functor). Stats side uses only forms seen in vanilla: GainTemporaryHitPoints(1d6), RollBonus(SavingThrow, 1),
RestoreResource(HC_Junk,n,0). The Lua listeners only apply the statuses; without the Script Extender the passives do nothing visible.
UNVERIFIED in game (Osiris events ShortRested and LongRestFinished, Osi.HasPassive, Osi.ApplyStatus with duration -1).
"""
from pathlib import Path

SOUND_BATH = 'HC_SunsetStripSoundBath'
MATTRESS = 'HC_CurbsideMattressAppraisal'
SOUND_BATH_STATUS = 'HC_SOUND_BATH'
MATTRESS_STATUS = 'HC_CURBSIDE_APPRAISAL'

PASSIVES = [
    (SOUND_BATH, 'Sunset Strip Sound Bath', 3,
     'Whenever you finish a Short Rest, you and your companions gain 1d6 temporary hit points. Forty-five minutes of Tibetan singing '
     'bowls in a parking lot, for the low price of a donation you cannot afford.'),
    (MATTRESS, 'Curbside Mattress Appraisal', 5,
     'After each Long Rest you find 2 Junk and gain +1 to all saving throws until your next Long Rest. A gently used memory foam topper '
     'on the curb, with no visible stains, if you do not look under the tag.'),
]

STATUSES = [
    (SOUND_BATH_STATUS, 'Sound Bathed', 'You have 1d6 more temporary hit points than you did before the singing bowls. Your chakras remain unaligned.',
     '', 'GainTemporaryHitPoints(1d6)'),
    (MATTRESS_STATUS, 'Appraised the Mattress', 'You found 2 Junk and gain +1 to all saving throws until your next Long Rest. '
     'The mattress was fine. Probably.', 'RollBonus(SavingThrow,1)', 'RestoreResource(HC_Junk,2,0)'),
]

GRANTS = {'base': {}, 'subclasses': {}, 'existing_list_spells': {},
          'base_passives': {level: [name] for name, _t, level, _d in PASSIVES}}


def _block(kind, name, fields):
    for key, value in fields.items():
        if any(ch in value for ch in ('"', '\n', '\r')):
            raise ValueError(f'Unsafe {name}.{key}')
    return '\n'.join([f'new entry "{name}"', f'type "{kind}"'] + [f'data "{k}" "{v}"' for k, v in fields.items()])


def generate_round16(public_dir, add_loca, get_guid):
    stats = Path(public_dir) / 'Stats/Generated/Data'
    stats.mkdir(parents=True, exist_ok=True)
    passives = [_block('PassiveData', name, {'DisplayName': add_loca(name + '_Name', title) + ';1',
                                             'Description': add_loca(name + '_Description', desc) + ';1',
                                             'Icon': 'PassiveFeature_Alert', 'Properties': 'Highlighted'})
                for name, title, _lvl, desc in PASSIVES]
    statuses = []
    for name, title, desc, boosts, functors in STATUSES:
        fields = {'StatusType': 'BOOST', 'StackId': name, 'StackType': 'Overwrite', 'Icon': 'PassiveFeature_Alert',
                  'DisplayName': add_loca(name + '_Name', title) + ';1', 'Description': add_loca(name + '_Description', desc) + ';1',
                  'OnApplyFunctors': functors}
        if boosts:
            fields['Boosts'] = boosts
        statuses.append(_block('StatusData', name, fields))
    (stats / 'HC_Passives_Round16.txt').write_text('\n\n'.join(passives) + '\n', encoding='utf-8')
    (stats / 'HC_Status_Round16.txt').write_text('\n\n'.join(statuses) + '\n', encoding='utf-8')
    return {k: ({lv: list(v) for lv, v in val.items()} if isinstance(val, dict) else val) for k, val in GRANTS.items()}
