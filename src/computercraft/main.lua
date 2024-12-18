local basalt = require("basalt")
local ui = require("ui")
local base64 = require("base64")
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

-- ...existing code...

local cacheChart
local cachePortfolio
local cacheTime = 0

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
    
    -- Lanzar los requests
    responses.operations = makeRequest(api.obtenerOperaciones, currentTicker)
    responses.profit = makeRequest(api.obtenerProfit, currentTicker)
    responses.profitUSD = makeRequest(api.obtenerProfitUSD, currentTicker)
    
    if cacheTime == 0 then
        responses.portfolio = makeRequest(api.obtenerPortfolio)
        responses.chart = makeRequest(api.obtenerPortfolioChart)
    else
        responses.portfolio = cachePortfolio
        responses.chart = cacheChart
    end

    -- Actualizar la UI con los resultados
    ui.updateUI(mainFrame, contentFrames, currentTicker,
        responses.operations,
        responses.profit,
        responses.profitUSD, 
        responses.portfolio,
        responses.chart  -- Pasar los datos del chart
    )

    return responses.operations ~= nil 
       or responses.profit ~= nil
       or responses.portfolio ~= nil
       or responses.chart ~= nil
end

-- Función para actualizar los datos periódicamente
local function updateData()
    while true do
        updateTickerData()
        sleep(1)
        cacheTime = cacheTime + 1
        if cacheTime >= 180 then
            cacheTime = 0
        end
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

-- Dentro de updatePortfolioList en ui.lua o donde corresponda

local function updatePortfolioList(portfolioList, data, chartData)
    if not data then return end
    portfolioList:clear()
    
    for _, holding in ipairs(data) do
        portfolioList:addItem(string.format(
            "%s - %.2f%%", 
                holding.ticker,
                holding.porcentaje or 0
            ),
        nil, 
        colors[holding.color])
    end

    -- Actualizar chart si hay datos nuevos
    if chartData then
        -- Guardar temporalmente el chart
        local tempFile = "temp_chart.bimg"
        local file = fs.open(tempFile, "wb") -- Modo binario
        file.write(chartData) -- chartData es binario
        file.close()
        
        -- Cargar y mostrar el chart
        local imageFrame = portfolioList:getParent():getChild("imageFrame")
        local chartImage = imageFrame:getChild("chartImage")
        chartImage:loadImage(tempFile)
            :resizeImage(imageFrame:getWidth(), imageFrame:getHeight())
        
        -- Eliminar archivo temporal si es necesario
        -- fs.delete(tempFile)
    end
end