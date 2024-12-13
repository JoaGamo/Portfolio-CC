local basalt = require("basalt")
local ui = require("ui")
local api = require("api_client")

local mainUI = ui.createUI()


while true do
    local data = api.obtenerBalance("NVDA")
    ui.updateUI(mainUI, { value = data })
    basalt.autoUpdate()
end