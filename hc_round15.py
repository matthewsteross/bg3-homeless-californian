"""Round 15: one level-1 racial passive per Californian subrace (Beachborn, Siliconite), from work/r13-agy.md ideas 9 and 10.

The original ideas were a reaction (SigAlert) and an aura action (Pre-Seed). Both need engine hooks that are not verified, so they
become passives built only from boost forms already proven in earlier rounds: Initiative(n), ActionResource(Movement,n,0),
RollBonus(Attack,n), Advantage(Skill,Persuasion). Granted by appending to the subrace level-1 progression PassivesAdded.
UNVERIFIED in game; a character needs a respec or a new game to receive them.
"""
from pathlib import Path

SIGALERT = 'HC_SoCalSigAlertSixthSense'
PRESEED = 'HC_NorCalPreSeedPitchDeck'

PASSIVES = [
    (SIGALERT, 'SoCal SigAlert Sixth Sense', 'Beachborn',
     'Gain +2 to initiative and your movement speed increases by 1.5 m. Decades of anticipating sudden brake-checks on the '
     'freeway taught you to veer into the shoulder before anyone else has even seen the brake lights.',
     'Initiative(2);ActionResource(Movement,1.5,0)'),
    (PRESEED, 'NorCal Pre-Seed Pitch Deck', 'Siliconite',
     'Gain +1 to attack rolls and advantage on Persuasion checks. Radiating completely unearned investor confidence convinces '
     'reality itself to fund your runway.',
     'RollBonus(Attack,1);Advantage(Skill,Persuasion)'),
]

SUBRACE_PASSIVES = {'Beachborn': [SIGALERT], 'Siliconite': [PRESEED]}


def generate_round15(public_dir, add_loca, get_guid):
    stats = Path(public_dir) / 'Stats/Generated/Data'
    stats.mkdir(parents=True, exist_ok=True)
    blocks = []
    for name, title, _subrace, description, boosts in PASSIVES:
        fields = {'DisplayName': add_loca(name + '_Name', title) + ';1',
                  'Description': add_loca(name + '_Description', description) + ';1',
                  'Icon': 'PassiveFeature_Alert', 'Properties': 'Highlighted', 'Boosts': boosts}
        for key, value in fields.items():
            if any(ch in value for ch in ('"', '\n', '\r')):
                raise ValueError(f'Unsafe {name}.{key}')
        blocks.append('\n'.join([f'new entry "{name}"', 'type "PassiveData"'] + [f'data "{k}" "{v}"' for k, v in fields.items()]))
    (stats / 'HC_Passives_Round15.txt').write_text('\n\n'.join(blocks) + '\n', encoding='utf-8')
    return {k: list(v) for k, v in SUBRACE_PASSIVES.items()}
