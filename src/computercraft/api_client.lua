-- modulos/api_client.lua
local http = require("http")
local json = require("json")


local function obtenerOperaciones(ticker)
    local url = "http://localhost:5000/operaciones/" .. ticker
    local response = http.get(url)

    if response then
        local body = response.readAll()
        response.close() -- Cierra la respuesta para liberar recursos.

        local data, err = json(body)
if not data then
          print("Error al decodificar JSON:", err)
  print(body) --para debug
            return nil, "Error al decodificar JSON"
        end
        if response.getResponseCode() == 200 then
  if data and data.balance then
    return data.balance, nil
  else
    return nil, data.error
  end
        elseif response.getResponseCode() == 500 then
            print("Error del servidor:", data.error)
            return nil, data.error or "Error interno del servidor"
        else
            print("Error en la solicitud:", response.getResponseCode())
            return nil, "Error en la solicitud: " .. response.getResponseCode()
        end

    else
        print("Error de conexion a la API")
        return nil, "Error de conexion"
    end
end

-- Otras funciones...

return { obtenerBalance = obtenerBalance, obtenerOperaciones = obtenerOperaciones, enviarOrden = enviarOrden } -- Exporta las funciones