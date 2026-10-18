"""Script Extender server script that actually deletes expired prop items.

In game (2026-10-18) the prop lifetime status HC_PROP_LIFETIME_10T was applied and removed after 10 turns as designed,
but its OnRemoveFunctors Kill() did NOT remove the spawned item (the wardrobe stayed). This adds a tiny Osiris listener
through the Script Extender (which Matthew has installed; without it the props simply stay as before):
  Mods/HomelessCalifornian/ScriptExtender/Config.json
  Mods/HomelessCalifornian/ScriptExtender/Lua/BootstrapServer.lua
UNVERIFIED in game: that Osi.RequestDelete removes these items on StatusRemoved.
"""
from pathlib import Path

CONFIG = '''{
    "RequiredVersion": 1,
    "ModTable": "HomelessCalifornian",
    "FeatureFlags": ["Lua", "Osiris"]
}
'''

LUA = '''-- Homeless Californian: remove spawned prop items when their lifetime status ends.
-- The stat functor Kill() does not delete item props, so do it from Osiris.
local LIFETIME_STATUS = "HC_PROP_LIFETIME_10T"

Ext.Osiris.RegisterListener("StatusRemoved", 4, "after", function(object, status, causee, storyActionID)
    if status ~= LIFETIME_STATUS then
        return
    end
    local ok, err = pcall(function()
        Osi.RequestDelete(object)
    end)
    if not ok then
        Ext.Utils.PrintWarning("[HomelessCalifornian] could not delete expired prop " .. tostring(object) .. ": " .. tostring(err))
    end
end)

Ext.Utils.Print("[HomelessCalifornian] prop cleanup script loaded")
'''


def generate_proplua(mod_dir):
    """Write the Script Extender files under src/<Mod>/Mods/<Folder>/ScriptExtender."""
    base = Path(mod_dir) / 'ScriptExtender'
    (base / 'Lua').mkdir(parents=True, exist_ok=True)
    (base / 'Config.json').write_text(CONFIG, encoding='utf-8', newline='\n')
    (base / 'Lua' / 'BootstrapServer.lua').write_text(LUA, encoding='utf-8', newline='\n')
    return base
