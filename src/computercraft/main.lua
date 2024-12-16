local basalt = require("basalt")
local ui = require("ui")
local api = require("api_client")

local currentTicker = "CRES" -- Ticker inicial

-- Declaración inicial de la función
local updateTickerData

-- Crear la UI y pasar el callback 'onTickerChanged'
local mainFrame, contentFrames, tickerLabel, profitLabel, listFrame = ui.createUI(function(newTicker)
    if newTicker then
        currentTicker = newTicker
        updateTickerData()
    end
end)

-- Al inicio después de crear la UI
local profitFrame = mainFrame:getChild("profitFrame")
local tickerDropdown = profitFrame:getChild("tickerSelect") -- Cambiado a "tickerSelect"

-- Obtener lista inicial de tickers
local tickers = api.obtenerTickersUnicos()
if tickers then
    ui.updateTickersList(tickerDropdown, tickers)
end

-- Eliminar el manejador de evento 'ticker_changed'
--[[
mainFrame:onEvent("ticker_changed", function(self, event, newTicker)
    -- Código eliminado
end)
]]

-- Configuración de reintentos
local MAX_RETRIES = 5
local BASE_WAIT = 0.5 -- segundos
local MAX_WAIT = 5 -- máximo tiempo de espera

local function exponentialBackoff(attempt)
    local wait = math.min(MAX_WAIT, BASE_WAIT * (2 ^ (attempt - 1)))
    return wait + math.random() -- añadir jitter
end

-- Función para hacer requests con reintentos inmediatos (no bloqueantes)
local function makeRequest(requestFn, ...)
    local args = {...}
    local attempt = 1
    
    local function tryRequest() 
        local data, err = requestFn(table.unpack(args))
        while not data and attempt < MAX_RETRIES do
            attempt = attempt + 1
            basalt.debug(string.format("Error en intento %d/%d: %s", attempt, MAX_RETRIES, err))
            data, err = requestFn(table.unpack(args))
        end
        return data, err
    end

    return tryRequest()
end

-- Hacer los requests en paralelo
updateTickerData = function()
    -- Crear una tabla para almacenar las respuestas
    local responses = {}
    
    -- Lanzar los 3 requests  
    responses.operations = makeRequest(api.obtenerOperaciones, currentTicker)
    responses.profit = makeRequest(api.obtenerProfit, currentTicker)
    responses.portfolio = makeRequest(api.obtenerPortfolio)

    -- Actualizar la UI con los resultados
    ui.updateUI(mainFrame, contentFrames, currentTicker,
        responses.operations,
        responses.profit, 
        responses.portfolio
    )

    return responses.operations ~= nil 
       or responses.profit ~= nil
       or responses.portfolio ~= nil
end

-- Función para actualizar los datos periódicamente
local function updateData()
    while true do
        updateTickerData()
        sleep(3) -- Reducido de 60s a 3s ya que es una API local
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