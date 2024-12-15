local json = require("json")
local basalt = require("basalt")

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

local function makeRequest(url)
    local success, response = pcall(http.get, url)
    if not success then
        return nil, "Error de conexión: " .. tostring(response) 
    end
    return handleResponse(response)
end

local function obtenerOperaciones(ticker)
    return makeRequest("http://localhost:8000/operaciones/" .. ticker)
end

local function obtenerProfit(ticker)
    return makeRequest("http://localhost:8000/profit_actual/" .. ticker)
end

local function obtenerPortfolio()
    return makeRequest("http://localhost:8000/portfolio")
end

local function obtenerTickersUnicos()
    return makeRequest("http://localhost:8000/tickers_unicos")
end

return {
    obtenerOperaciones = obtenerOperaciones,
    obtenerProfit = obtenerProfit,
    obtenerPortfolio = obtenerPortfolio,
    obtenerTickersUnicos = obtenerTickersUnicos
}