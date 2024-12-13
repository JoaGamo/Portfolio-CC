-- Import necesarios
local http = require("http")
local fs = require("fs")
local shell = require("shell")

-- URLs base de los archivos raw en GitHub 
local baseURL = "https://raw.githubusercontent.com/JoaGamo/Portfolio-CC/main/src/computercraft/"

-- Lista de archivos a descargar
local files = {
    "main.lua",
    "ui.lua", 
    "api_client.lua",
    "basalt.lua"
}

-- Función para descargar un archivo
local function downloadFile(filename)
    print("Descargando " .. filename .. "...")
    
    local url = baseURL .. filename
    local response = http.get(url)
    
    if response then
        print("Guardando " .. filename)
        local file = fs.open(filename, "w")
        file.write(response.readAll())
        file.close()
        response.close()
        return true
    else
        print("Error descargando " .. filename)
        return false
    end
end

-- Crear directorio si no existe
if not fs.exists("Portfolio-CC") then
    fs.makeDir("Portfolio-CC") 
end

-- Cambiar al directorio
shell.setDir("Portfolio-CC")

-- Descargar cada archivo
print("Iniciando instalación...")
local success = true

for _, filename in ipairs(files) do
    if not downloadFile(filename) then
        success = false
        break
    end
end

if success then
    print("Instalación completada!")
    print("Ejecuta 'Portfolio-CC/main.lua' para iniciar")
else
    print("La instalación falló")
    -- Limpiar archivos parcialmente descargados
    for _, filename in ipairs(files) do
        if fs.exists(filename) then
            fs.delete(filename)
        end
    end
end
