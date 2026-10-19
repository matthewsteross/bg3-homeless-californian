"""Round 13: four base-class passives (levels 4, 6, 8, 10), from the Gemini brainstorm in work/r13-agy.md.

Only boosts whose exact form already appears in earlier rounds (and so in vanilla stats) are used:
Initiative(n), Advantage(SavingThrow,Dexterity), AC(n), StatusImmunity(DIFFICULT_TERRAIN), ActionResource(Movement,n,0),
Advantage(Skill,Persuasion), Advantage(Skill,Deception). Conditional parts of the original ideas were dropped on purpose (no new
engine behaviour). Granted through base_passives like Round 10/11; a character needs a level-up or respec to receive them.
UNVERIFIED in game.
"""
from pathlib import Path

CEQA = 'HC_FastTrackCEQAExemption'
COUNTY = 'HC_UnincorporatedCountyImmunity'
TRANSPONDER = 'HC_ExpressLaneTransponderCheat'
SECRET_MENU = 'HC_InNOutSecretMenuSavant'

PASSIVES = [
    (CEQA, 'Fast-Track CEQA Exemption', 4, 'PassiveFeature_Alert',
     'Gain +2 to initiative and advantage on Dexterity saving throws. A confidential settlement with the historical society '
     'means your plans skip every public hearing, and so does your sense of danger.',
     'Initiative(2);Advantage(SavingThrow,Dexterity)'),
    (COUNTY, 'Unincorporated County Immunity', 6, 'PassiveFeature_Resilient',
     'Gain +1 Armour Class and immunity to difficult terrain. Neither city code enforcement nor municipal jurisdiction can '
     'legally cross this particular drainage swale.',
     'AC(1);StatusImmunity(DIFFICULT_TERRAIN);StatusImmunity(DIFFICULT_TERRAIN_MUD);StatusImmunity(DIFFICULT_TERRAIN_WEB);StatusImmunity(DIFFICULT_TERRAIN_VINES)'),
    (TRANSPONDER, 'Express Lane Transponder Cheat', 8, 'PassiveFeature_FastMovement',
     'Your movement speed increases by 3 m. Three layers of duct tape over the licence plate scanner let you cruise at full '
     'speed without paying the toll.',
     'ActionResource(Movement,3,0)'),
    (SECRET_MENU, 'In-N-Out Secret Menu Savant', 10, 'PassiveFeature_Resilient',
     'Gain advantage on Persuasion and Deception checks. Ordering flying dutchman, well-done, with grilled onions projects an '
     'aura of terrifying local authority.',
     'Advantage(Skill,Persuasion);Advantage(Skill,Deception)'),
]

GRANTS = {
    'base': {},
    'subclasses': {},
    'existing_list_spells': {},
    'base_passives': {level: [name] for name, _t, level, _i, _d, _b in PASSIVES},
}


def generate_round13(public_dir, add_loca, get_guid):
    stats = Path(public_dir) / 'Stats/Generated/Data'
    stats.mkdir(parents=True, exist_ok=True)
    blocks = []
    for name, title, _level, icon, description, boosts in PASSIVES:
        fields = {'DisplayName': add_loca(name + '_Name', title) + ';1',
                  'Description': add_loca(name + '_Description', description) + ';1',
                  'Icon': icon, 'Properties': 'Highlighted', 'Boosts': boosts}
        for key, value in fields.items():
            if any(ch in value for ch in ('"', '\n', '\r')):
                raise ValueError(f'Unsafe {name}.{key}')
        blocks.append('\n'.join([f'new entry "{name}"', 'type "PassiveData"'] + [f'data "{k}" "{v}"' for k, v in fields.items()]))
    (stats / 'HC_Passives_Round13.txt').write_text('\n\n'.join(blocks) + '\n', encoding='utf-8')
    return {k: ({lv: list(v) for lv, v in val.items()} if isinstance(val, dict) else val) for k, val in GRANTS.items()}
