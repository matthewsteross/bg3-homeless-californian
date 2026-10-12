"""Custom icon keys shared by generators and the icon builder."""
from pathlib import Path

ASSETS = Path(__file__).resolve().parent / 'assets/icons'
SPELL_ICON_KEYS = {
    'HC_Projectile_EmotionalSupportBrick': 'Spell_EmotionalSupportBrick',
    'HC_Target_BagOfOtherBags': 'Spell_BagOfOtherBags',
    'HC_Shout_LoadBearingChair': 'Spell_LoadBearingChair',
    'HC_Shout_DumpsterDive': 'Spell_DumpsterDive',
    'HC_Shout_MovingDay': 'Spell_MovingDay',
    'HC_Target_PigeonWitnessProtection': 'Spell_PigeonWitnessProtection',
    'HC_Target_HeirloomFurniture': 'Spell_HeirloomFurniture',
    'HC_Target_ChairLegShiv': 'Spell_ChairLegShiv',
    'HC_Target_WrongPlatform': 'Spell_WrongPlatform',
    'HC_Shout_ClaimUnclaimedWardrobe': 'Spell_UnclaimedWardrobe',
    'HC_Target_CoatHangerSlimJim': 'Spell_CoatHangerSlimJim',
    'HC_Shout_CardboardInsulation': 'Spell_CardboardInsulation',
    'HC_Target_CurbsideClinic': 'Spell_CurbsideClinic',
    'HC_Target_BoardwalkDisarm': 'Spell_BoardwalkDisarm',
}

def icon_for_spell(spell, fallback):
    """Use custom art only when its source exists; never grant a missing icon."""
    key = SPELL_ICON_KEYS.get(spell)
    return key if key and (ASSETS / (key + '.png')).is_file() else fallback
