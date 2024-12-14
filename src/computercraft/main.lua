local basalt = require("basalt")
local ui = require("ui")
local api = require("api_client")

-- Ticker actual
local currentTicker = "PAMP" -- Podríamos hacer esto configurable por argumentos o UI

-- Crear la UI
local mainFrame, contentFrames, tickerLabel, profitLabel, listFrame = ui.createUI()

-- Función para actualizar los datos de un ticker
local function updateTickerData()
    local data, err = api.obtenerOperaciones(currentTicker)
    local profit, profitErr = api.obtenerProfit(currentTicker)
    local portfolio, portfolioErr = api.obtenerPortfolio()
    
    if data or profit or portfolio then
        ui.updateUI(mainFrame, contentFrames, currentTicker, data, profit, portfolio)
        return true
    else
        print("Error:", err or profitErr or portfolioErr)
        return false
    end
end

-- Función para actualizar los datos periódicamente
local function updateData()
    local contadorErrores = 0
    while true do
        if not updateTickerData() then
            contadorErrores = contadorErrores + 1
            if contadorErrores >= 3 then
                print("Demasiados errores, deteniendo actualización.")
                return
            end
        else
            contadorErrores = 0
        end
        sleep(3)
    end
end

-- Función para manejar eventos y permitir la terminación del programa
local function handleEvents()
    while true do
        local event = os.pullEvent()
        if event == "terminate" then
            basalt.stopUpdate()
            print("Programa terminado.")
            return
        end
    end
end

-- Ejecuta las funciones en paralelo
parallel.waitForAny(
    function() basalt.autoUpdate() end,
    updateData,
    handleEvents
)