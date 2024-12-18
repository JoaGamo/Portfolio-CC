local basalt = require("basalt")

local function createUI(onTickerChanged)
    local mainFrame = basalt.createFrame("mainFrame")
        :setSize(term.getSize())
        :setBackground(colors.black)

    basalt.setVariable("activeMenu", "Operaciones")

    -- Crear la barra de menú
    local menuBar = mainFrame:addMenubar()
        :setPosition(1, 1)
        :setSize(mainFrame:getWidth(), 1)  -- Cambiar de 3 a 1 para reducir altura
        :setBackground(colors.blue)
        :setSelectionColor(colors.lightBlue, colors.white)
        :addItem("Operaciones", colors.white, colors.blue)
        :addItem("Profit", colors.white, colors.blue)
        :addItem("Portfolio", colors.white, colors.blue)

    -- Crear un diccionario para los frames de contenido
    local contentFrames = {}

    -- Crear el frame para las operaciones
    contentFrames["Operaciones"] = mainFrame:addFrame("operacionesFrame")
        :setPosition(1, 2)  -- Cambiar de 4 a 2
        :setSize(mainFrame:getWidth(), mainFrame:getHeight() - 1)  -- Cambiar -3 a -1
        :setBackground(colors.black)
    
    -- Añadir contenido al frame de operaciones
    local tickerLabel = contentFrames["Operaciones"]:addLabel("tickerLabel")
        :setPosition(2, 1)
        :setForeground(colors.white)
        :setText("Ticker: ???")  -- Valor por defecto

    local listFrame = contentFrames["Operaciones"]:addFrame("listFrame")
        :setPosition(1, 2)
        :setSize(contentFrames["Operaciones"]:getWidth(), contentFrames["Operaciones"]:getHeight() - 1)
        :setBackground(colors.black)

    -- Crear el frame para el profit
    contentFrames["Profit"] = mainFrame:addFrame("profitFrame")
        :setPosition(1, 2)  -- Cambiar de 4 a 2
        :setSize(mainFrame:getWidth(), mainFrame:getHeight() - 1)  -- Cambiar -3 a -1
        :setBackground(colors.black)
        :hide()
    
    -- Añadir contenido al frame de profit
    -- Añadir tickerLabel también al frame de profit
    local profitTickerLabel = contentFrames["Profit"]:addLabel("tickerLabel")
        :setPosition(2, 1)
        :setForeground(colors.white)
        :setText("Ticker: ???")

    -- Añadir dropdown para selección de ticker
    local tickerDropdown = contentFrames["Profit"]:addDropdown("tickerSelect")
        :setPosition(2, 2)
        :setSize(16, 1)
        :setBackground(colors.blue)
        :setForeground(colors.white)
        :setScrollable(true)

    -- Configurar el callback para manejar la selección del ticker
    tickerDropdown:onChange(function(self, event, item)
        if item and onTickerChanged and type(onTickerChanged) == "function" then
            onTickerChanged(item.text)
        end
    end)

    local profitLabel = contentFrames["Profit"]:addLabel("profitLabel")
        :setPosition(2, 4)
        :setForeground(colors.white)
        :setText("Cargando profit...")

    contentFrames["Portfolio"] = mainFrame:addFrame("portfolioFrame")
        :setPosition(1, 2)  -- Cambiar de 4 a 2
        :setSize(mainFrame:getWidth(), mainFrame:getHeight() - 1)  -- Cambiar -3 a -1
        :setBackground(colors.black)
        :hide()
    
    -- Modificar el portfolioList para que ocupe solo un tercio izquierdo
    local portfolioList = contentFrames["Portfolio"]:addList("portfolioList")
        :setPosition(2, 2)
        :setSize(math.floor(mainFrame:getWidth()/3) - 2, mainFrame:getHeight() - 6) -- Usar 1/3 del ancho
        :setBackground(colors.black)
        :setForeground(colors.white)
        :addItem("Cargando...")


    -- Crear un frame contenedor para la imagen
    local imageFrame = contentFrames["Portfolio"]:addFrame("imageFrame")  -- añadir ID al frame
        :setPosition(math.floor(mainFrame:getWidth()/3) + 2, 1)
        :setSize(math.floor(mainFrame:getWidth() * 2/3), mainFrame:getHeight() - 1)
        :setBackground(colors.black)

    local chartImage = imageFrame:addImage("chartImage")  -- añadir ID a la imagen
        :setBackground(colors.black)
        :setSize(imageFrame:getWidth(), imageFrame:getHeight())
        

    -- Estado inicial - mostrar Operaciones
    local currentMenu = "Operaciones"

    menuBar:onChange(function(self, event, value)
        
        -- Obtener frames usando getChild
        local operacionesFrame = mainFrame:getChild("operacionesFrame")
        local profitFrame = mainFrame:getChild("profitFrame")
        local portfolioFrame = mainFrame:getChild("portfolioFrame")
        
        -- Ocultar el frame actual
        operacionesFrame:hide()
        profitFrame:hide()
        portfolioFrame:hide()
        
        -- Mostrar el nuevo frame
        if value.text == "Operaciones" then
            operacionesFrame:show()
        elseif value.text == "Profit" then
            profitFrame:show()
        elseif value.text == "Portfolio" then
            portfolioFrame:show()
        end
        
        mainFrame:updateDraw()
        basalt.setVariable("activeMenu", value.text)
    end)

    return mainFrame, contentFrames, tickerLabel, profitLabel, listFrame
end

local function updateProfitDisplay(profitLabel, ticker, profit)
    if profit then
        local color = profit >= 0 and colors.green or colors.red
        profitLabel:setForeground(color)
        profitLabel:setText(string.format("Profit actual (en pesos): $%.2f", profit))
    end
end

local function updateOperationsList(listFrame, data)
    if not data then return end
    listFrame:removeChildren()
    local yPos = 1

    for i, operation in ipairs(data) do
        -- Crear un frame para la operación
        local opFrame = listFrame:addFrame()
            :setSize(listFrame:getWidth(), 3)
            :setPosition(1, yPos)
            :setBackground(i % 2 == 0 and colors.gray or colors.black)

        -- Añadir detalles de la operación
        opFrame:addLabel()
            :setText(string.format("Fecha: %s", operation.fecha and operation.fecha:sub(1,10) or "N/A"))
            :setPosition(2, 1)
            :setForeground(colors.white)

        opFrame:addLabel()
            :setText(string.format("Precio: $%.2f", operation.precio or 0))
            :setPosition(2, 2)
            :setForeground(colors.white)

        opFrame:addLabel()
            :setText(string.format("Cantidad: %d", operation.cantidad or 0))
            :setPosition(listFrame:getWidth() - 15, 2)
            :setForeground(colors.white)

        -- Actualizar posición Y para la siguiente operación
        yPos = yPos + 4
    end
end

local function updatePortfolioList(portfolioList, data, chartData)
    if not data then return end
    portfolioList:clear()
    portfolioList:addItem("", colors.black, colors.black) -- No podemos desmarcar casillas en Basalt, esto es un workaround
    for _, holding in ipairs(data) do
        portfolioList:addItem(string.format(
            "%s - %.2f%%", 
                holding.ticker,
                holding.porcentaje or 0
            ),
        nil, 
        colors[holding.color])
    end

    if chartData then
        local imageFrame = portfolioList:getParent():getChild("imageFrame")
        local chartImage = imageFrame:getChild("chartImage")
        
        -- Guardar temporalmente el chart
        local tempFile = "temp_chart.bimg"
        local file = fs.open(tempFile, "wb")
        file.write(chartData)
        file.close()
        chartImage:loadImage(tempFile):resizeImage(imageFrame:getWidth(), imageFrame:getHeight())
        
        -- Eliminar archivo temporal
        --fs.delete(tempFile)
    end
end

-- Modificar updateUI para aceptar el parámetro chart
local function updateUI(mainFrame, contentFrames, ticker, data, profit, portfolio, chart)

    -- Actualizar labels de ticker en ambos frames
    for _, frame in pairs(contentFrames) do
        local tickerLabel = frame:getChild("tickerLabel")
        if tickerLabel then
            tickerLabel:setText("Ticker: " .. ticker)
        end
    end

    -- Actualizar contenido según el menú activo
    local activeMenu = basalt.getVariable("activeMenu")
    if activeMenu == "Operaciones" then
        contentFrames["Profit"]:hide()
        contentFrames["Portfolio"]:hide()
        contentFrames["Operaciones"]:show()
        local listFrame = contentFrames["Operaciones"]:getChild("listFrame")
        if listFrame then
            updateOperationsList(listFrame, data)
        end
    elseif activeMenu == "Profit" then
        contentFrames["Operaciones"]:hide()
        contentFrames["Portfolio"]:hide()
        contentFrames["Profit"]:show()
        
        -- Actualizar el dropdown con el ticker actual
        local tickerDropdown = contentFrames["Profit"]:getChild("tickerSelect")
        if tickerDropdown then
            tickerDropdown:setValue(ticker)
        end
        
        local profitLabel = contentFrames["Profit"]:getChild("profitLabel")
        if profitLabel then
            updateProfitDisplay(profitLabel, ticker, profit)
        end

        -- Encontrar y seleccionar el ticker correcto en el dropdown
        local tickerDropdown = contentFrames["Profit"]:getChild("tickerSelect")
        if tickerDropdown then
            -- Buscar el índice del ticker actual
            local items = tickerDropdown:getAll()
            for i, item in ipairs(items) do
                if item.text == ticker then
                    -- Eliminar la llamada a setSelectedItem ya que no existe
                    -- tickerDropdown:setSelectedItem(i, false)
                    break
                end
            end
        end
    elseif activeMenu == "Portfolio" then
        contentFrames["Operaciones"]:hide()
        contentFrames["Profit"]:hide()
        contentFrames["Portfolio"]:show()
        local portfolioList = contentFrames["Portfolio"]:getChild("portfolioList")
        if portfolioList then
            updatePortfolioList(portfolioList, portfolio, chart)  -- Pasar el chart a updatePortfolioList
        end
    end

    mainFrame:updateDraw()
end

return {
    createUI = createUI,
    updateUI = updateUI,
    updateTickersList = function(dropdown, tickers)
        if tickers then
            dropdown:clear()
            for _, ticker in ipairs(tickers) do
                -- Asegurarnos que solo agregamos el ticker limpio
                local tickerValue
                if type(ticker) == "table" then
                    -- Si viene como {ticker: "AAPL"}
                    tickerValue = ticker.ticker
                elseif type(ticker) == "string" then
                    -- Si viene como string, limpiar URLs
                    tickerValue = string.match(ticker, "[^/]+$") or ticker
                    tickerValue = string.match(tickerValue, "^[^?]+") or tickerValue
                end
                dropdown:addItem(tickerValue)
            end
        end
    end
}