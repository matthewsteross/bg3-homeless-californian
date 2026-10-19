"""Script Extender server script: deletes expired prop items, plus a dormant in-game self-test.

1) Prop cleanup. In game (2026-10-18) the prop lifetime status HC_PROP_LIFETIME_10T was applied and removed after 10 turns
   as designed, but its OnRemoveFunctors Kill() did NOT remove the spawned item (the wardrobe stayed). A tiny Osiris listener
   calls Osi.RequestDelete when the status ends. Needs the Script Extender; without it the props simply stay.
   UNVERIFIED in game: that RequestDelete removes these items.
2) Self-test. Matthew cannot hand-test everything, so the mod can test itself: if the file HC_SELFTEST.txt exists in the
   Script Extender folder (%LOCALAPPDATA%/Larian Studios/Baldur's Gate 3/Script Extender/), then on LevelGameplayStarted it checks
   that every stat entry this mod defines exists (Ext.Stats.Get), that every item root template exists, spawns and deletes each
   item, and writes HC_SELFTEST_RESULT.txt in the same folder. Without the flag file it does nothing.
   UNVERIFIED in game: the Script Extender API calls used (Ext.IO.LoadFile/SaveFile, Ext.Template.GetRootTemplate, Osi.CreateAt).
Files written:
  Mods/HomelessCalifornian/ScriptExtender/Config.json
  Mods/HomelessCalifornian/ScriptExtender/Lua/BootstrapServer.lua
"""
import re
import xml.etree.ElementTree as ET
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

SELFTEST_LUA = '''
-- ===== Self-test (dormant unless the flag file exists) =====
-- Create HC_SELFTEST.txt (any content) in the Script Extender folder, start the game and load a save.
-- Writes HC_SELFTEST_RESULT.txt next to it. Without the flag file nothing here runs.
local HC_STATS = {
@@STATS@@
}
local HC_TEMPLATES = {
@@TEMPLATES@@
}

local function hc_flagged()
    local ok, content = pcall(function() return Ext.IO.LoadFile("HC_SELFTEST.txt") end)
    return ok and content ~= nil
end

local function hc_selftest()
    local out = {}
    local function add(line) out[#out + 1] = line end
    add("Homeless Californian self-test")
    local bad = 0
    for _, e in ipairs(HC_STATS) do
        local ok, stat = pcall(Ext.Stats.Get, e[1])
        if (not ok) or stat == nil then bad = bad + 1; add("MISSING STAT " .. e[2] .. " " .. e[1]) end
    end
    add(string.format("stats: %d checked, %d missing", #HC_STATS, bad))
    local tbad = 0
    for _, t in ipairs(HC_TEMPLATES) do
        local ok, tpl = pcall(function() return Ext.Template.GetRootTemplate(t[1]) end)
        if (not ok) or tpl == nil then tbad = tbad + 1; add("MISSING TEMPLATE " .. t[2] .. " " .. t[1]) end
    end
    add(string.format("item templates: %d checked, %d missing", #HC_TEMPLATES, tbad))
    local sbad = 0
    local okh, host = pcall(Osi.GetHostCharacter)
    if okh and host then
        local okp, x, y, z = pcall(Osi.GetPosition, host)
        if okp and x then
            for _, t in ipairs(HC_TEMPLATES) do
                local oks, guid = pcall(Osi.CreateAt, t[1], x + 3, y, z, 0, 0, "")
                if (not oks) or guid == nil or guid == "" then
                    sbad = sbad + 1; add("SPAWN FAILED " .. t[2])
                else
                    pcall(Osi.RequestDelete, guid)
                end
            end
            add(string.format("spawn tests: %d run, %d failed", #HC_TEMPLATES, sbad))
        else
            add("spawn tests skipped: no host position")
        end
    else
        add("spawn tests skipped: no host character")
    end
    add((bad + tbad + sbad == 0) and "RESULT: ALL PASSED" or "RESULT: PROBLEMS FOUND")
    local text = table.concat(out, "\\n")
    pcall(function() Ext.IO.SaveFile("HC_SELFTEST_RESULT.txt", text) end)
    Ext.Utils.Print("[HomelessCalifornian] " .. text)
end

Ext.Osiris.RegisterListener("LevelGameplayStarted", 2, "after", function()
    if hc_flagged() then
        local ok, err = pcall(hc_selftest)
        if not ok then Ext.Utils.PrintWarning("[HomelessCalifornian] self-test crashed: " .. tostring(err)) end
    end
end)
'''

ENTRY = re.compile(r'new entry "([^"]+)"\s*\r?\ntype "(\w+)"')


def collect_names(public_dir):
    """All stat entries (name, type) and item root templates (guid, name, type) this mod defines, from the generated source."""
    public = Path(public_dir)
    stats = []
    for path in sorted((public / 'Stats' / 'Generated' / 'Data').glob('*.txt')):
        for m in ENTRY.finditer(path.read_text(encoding='utf-8')):
            stats.append((m.group(1), m.group(2)))
    templates = []
    for path in sorted((public / 'RootTemplates').glob('*.lsf.lsx')):
        for node in ET.parse(path).iter('node'):
            if node.get('id') != 'GameObjects':
                continue
            a = {x.get('id'): x.get('value') for x in node.findall('attribute')}
            if a.get('MapKey') and a.get('Type') == 'item':
                templates.append((a['MapKey'], a.get('Name', ''), a.get('Type', '')))
    return stats, templates


def _q(text):
    return '"' + text.replace('\\', '\\\\').replace('"', '\\"') + '"'


def selftest_lua(stats, templates):
    stat_rows = ',\n'.join(f'    {{{_q(n)}, {_q(k)}}}' for n, k in stats)
    tpl_rows = ',\n'.join(f'    {{{_q(g)}, {_q(n)}}}' for g, n, _ in templates)
    return SELFTEST_LUA.replace('@@STATS@@', stat_rows).replace('@@TEMPLATES@@', tpl_rows)


def generate_proplua(mod_dir, public_dir=None):
    """Write the Script Extender files under src/<Mod>/Mods/<Folder>/ScriptExtender (self-test included when public_dir is given)."""
    base = Path(mod_dir) / 'ScriptExtender'
    (base / 'Lua').mkdir(parents=True, exist_ok=True)
    (base / 'Config.json').write_text(CONFIG, encoding='utf-8', newline='\n')
    text = LUA
    if public_dir is not None:
        stats, templates = collect_names(public_dir)
        text = LUA + selftest_lua(stats, templates)
    (base / 'Lua' / 'BootstrapServer.lua').write_text(text, encoding='utf-8', newline='\n')
    return base
