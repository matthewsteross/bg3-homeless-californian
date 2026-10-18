"""Temporary static-prop spawn recipe, verified against extracted vanilla stat syntax.
GustavDev/Spell_ProjectileStrike.txt:71: Spawn(template, ,STATUS).
SharedDev/Status_BOOST.txt:7869: OnApplyFunctors SetStatusDuration(status,3,ForceSet).
Gustav/Status_BOOST.txt:2431: SetStatusDuration(status,10,ForceSet).
GustavDev/Status_BOOST.txt:420,423,425: OnRemove, hidden flags, Kill().
Paths relative to temp_race/Public/*/Stats/Generated/Data.
UNVERIFIED in game: Spawn-applied status timing and Kill removing a static invulnerable item.
"""
from uuid import UUID
STATUS = 'HC_PROP_LIFETIME_10T'
TURNS = 10


def prop_lifetime(template_id):
    """Return (one shared StatusData definition, lifetime-aware ground Spawn functor).

    No assumed status Duration field and no invented counter syntax: its OnApply
    explicitly forces ten turns. Ten turns is approximately sixty realtime seconds.
    """
    template_id = str(UUID(str(template_id)))
    status = f'''new entry "{STATUS}"
type "StatusData"
data "StatusType" "BOOST"
data "StatusPropertyFlags" "DisableOverhead;DisableCombatlog;DisablePortraitIndicator"
data "TickType" "StartTurn"
data "OnApplyFunctors" "SetStatusDuration({STATUS},{TURNS},ForceSet)"
data "RemoveEvents" "OnRemove"
data "OnRemoveFunctors" "Kill()"
'''
    return status, f'GROUND:Spawn({template_id}, ,{STATUS})'
