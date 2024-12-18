local json = require("json")
local basalt = require("basalt")
local config = require("config").loadConfig()
local base64 = require("base64")

local function handleResponse(response)
    if not response then
        return nil, "Error de conexion"
    end

    -- Leer body de forma segura
    local success, body = pcall(function()
        return response.readAll()
    end)

    if not success then
        response.close()
        return nil, "Error leyendo respuesta: " .. tostring(body)
    end

    -- Obtener código de respuesta de forma segura  
    local success2, responseCode = pcall(function()
        return response.getResponseCode()
    end)

    response.close()

    if not success2 then
        return nil, "Error obteniendo código: " .. tostring(responseCode)
    end

    if responseCode == 200 and body then
        if body == "" then
            return nil, "Respuesta vacía"
        end

        -- Decodificar JSON de forma segura
        local success3, data = pcall(json.decode, body)
        
        if not success3 then
            return nil, "Error decodificando JSON: " .. tostring(data)
        end
        
        if data == nil then
            return nil, "JSON decodificado es nil"
        end

        return data
    end

    return nil, "Error en la solicitud: " .. responseCode .. " Body: " .. tostring(body)
end

local function handleBinaryResponse(response)
    if not response then
        return nil, "Error de conexión"
    end

    -- Leer el cuerpo de la respuesta como datos binarios
    local body = response.readAll()
    response.close()

    if body then
        return body  -- Devolver los datos binarios directamente
    end

    return nil, "Respuesta vacía"
end

local function makeRequest(url, isBinary)
    local success, response = pcall(http.get, url)
    if not success then
        return nil, "Error de conexión: " .. tostring(response) 
    end
    if isBinary then
        return handleBinaryResponse(response)
    end
    return handleResponse(response)
end

local function obtenerOperaciones(ticker)
    return makeRequest(config.API_URL .. "/operaciones/" .. ticker)
end

local function obtenerProfit(ticker)
    return makeRequest(config.API_URL .. "/profit_actual/" .. ticker)
end

local function obtenerProfitUSD(ticker)
    return makeRequest(config.API_URL .. "/profit_actual_usd/" .. ticker)
end

local function obtenerPortfolio()
    return makeRequest(config.API_URL .. "/portfolio")
end

local function obtenerTickersUnicos()
    return makeRequest(config.API_URL .. "/tickers_unicos")
end

local function obtenerPortfolioChart()
    return makeRequest(config.API_URL .. "/portfolio/chart", true)
end

return {
    obtenerOperaciones = obtenerOperaciones,
    obtenerProfit = obtenerProfit,
    obtenerProfitUSD = obtenerProfitUSD,
    obtenerPortfolio = obtenerPortfolio,
    obtenerTickersUnicos = obtenerTickersUnicos,
    obtenerPortfolioChart = obtenerPortfolioChart
}