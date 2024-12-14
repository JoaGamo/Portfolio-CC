local json = require("json")

local function obtenerOperaciones(ticker)
    local url = "http://localhost:8000/operaciones/" .. ticker
    local response = http.get(url)

    if response then
        local body = response.readAll()

        local responseCode = response.getResponseCode()
        response.close() -- Cierra la respuesta para liberar recursos.

        local data, err = json.decode(body)
        if not data then
            print("Error al decodificar JSON:", err)
            return nil, "Error al decodificar JSON"
        end
        if responseCode == 200 then
            return data, nil

        elseif responseCode == 500 then
            print("Error del servidor:", data.error)
            return nil, data.error or "Error interno del servidor"
        else
            print("Error en la solicitud:", responseCode)
            return nil, "Error en la solicitud: " .. responseCode
        end
    else
        print("Error de conexion a la API")
        return nil, "Error de conexion"
    end
end

-- Otras funciones...

return {obtenerOperaciones = obtenerOperaciones, enviarOrden = enviarOrden } -- Exporta las funciones