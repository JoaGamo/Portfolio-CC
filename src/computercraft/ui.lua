local basalt = require("basalt")

local function createUI()
    local frame = basalt.createFrame():setSize("parent.w", "parent.h")
    frame:addLabel():setText("Data:"):setPosition(2, 2)
    return frame
end

local function updateUI(frame, data)
    frame:getObject("Label"):setText("Data: " .. (data.value or "N/A"))
end

return {
    createUI = createUI,
    updateUI = updateUI
}
