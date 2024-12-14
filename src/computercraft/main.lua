local basalt = require("basalt")
local ui = require("ui")
local api = require("api_client")

-- Crear la UI - ahora recibimos los 3 componentes que retorna createUI()
local mainFrame, listFrame, scrollbar = ui.createUI()

-- Función para actualizar los datos periódicamente
local function updateData()
    local contadorErrores = 0
    while true do
        local data, err = api.obtenerOperaciones("NVDA")
        if data then
            -- Actualizamos pasando el mainFrame, que internamente tiene acceso al listFrame y scrollbar
            ui.updateUI(mainFrame, data)
        else
            print("Error:", err)
            contadorErrores = contadorErrores + 1
            if contadorErrores >= 3 then
                print("Demasiados errores, deteniendo actualización.")
                return
            end
        end
        sleep(5) -- Pausa para reducir el uso de CPU
    end
end

-- Función para manejar eventos y permitir la terminación del programa
local function handleEvents()
    while true do
        local event = os.pullEvent()
        if event == "terminate" then -- Detecta Ctrl + T
            basalt.stopUpdate()      -- Detiene la actualización de Basalt
            print("Programa terminado.")
            return                   -- Sale de la función y termina el programa
        end
    end
end

-- Ejecuta las funciones en paralelo
parallel.waitForAny(
    function() basalt.autoUpdate() end,
    updateData,
    handleEvents
)