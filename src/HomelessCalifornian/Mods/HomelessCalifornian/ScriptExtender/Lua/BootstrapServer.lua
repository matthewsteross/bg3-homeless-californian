-- Homeless Californian: remove spawned prop items when their lifetime status ends.
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
