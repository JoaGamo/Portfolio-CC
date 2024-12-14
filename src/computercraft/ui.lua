local basalt = require("basalt")

local function createUI()
    -- Crear el frame principal
    local mainFrame = basalt.createFrame("mainFrame")
        :setSize(term.getSize())
        :setBackground(colors.black)

    -- En lugar de usar setVariable en mainFrame, usaremos basalt.setVariable
    basalt.setVariable("activeMenu", "Operaciones")

    -- Crear la barra de menú
    local menuBar = mainFrame:addMenubar()
        :setPosition(1, 1)
        :setSize(mainFrame:getWidth(), 3)
        :setBackground(colors.blue)
        :setSelectionColor(colors.lightBlue, colors.white)
        :addItem("Operaciones", colors.white, colors.blue)
        :addItem("Profit", colors.white, colors.blue)
        :addItem("Portfolio", colors.white, colors.blue)

    -- Crear un diccionario para los frames de contenido
    local contentFrames = {}

    -- Crear el frame para las operaciones
    contentFrames["Operaciones"] = mainFrame:addFrame("operacionesFrame")
        :setPosition(1, 4)
        :setSize(mainFrame:getWidth(), mainFrame:getHeight() - 3)
        :setBackground(colors.black)
    
    -- Añadir contenido al frame de operaciones
    local tickerLabel = contentFrames["Operaciones"]:addLabel("tickerLabel")
        :setPosition(2, 1)
        :setForeground(colors.white)
        :setText("Ticker: NVDA")  -- Valor por defecto

    local listFrame = contentFrames["Operaciones"]:addFrame("listFrame")
        :setPosition(1, 2)
        :setSize(contentFrames["Operaciones"]:getWidth(), contentFrames["Operaciones"]:getHeight() - 1)
        :setBackground(colors.black)

    -- Crear el frame para el profit
    contentFrames["Profit"] = mainFrame:addFrame("profitFrame")
        :setPosition(1, 4)
        :setSize(mainFrame:getWidth(), mainFrame:getHeight() - 3)
        :setBackground(colors.black)
        :hide()
    
    -- Añadir contenido al frame de profit
    -- Añadir tickerLabel también al frame de profit
    local profitTickerLabel = contentFrames["Profit"]:addLabel("tickerLabel")
        :setPosition(2, 1)
        :setForeground(colors.white)
        :setText("Ticker: NVDA")

    local profitLabel = contentFrames["Profit"]:addLabel("profitLabel")
        :setPosition(2, 3) -- Moverlo más abajo del ticker
        :setForeground(colors.white)
        :setText("Cargando profit...") -- Texto por defecto

    -- Crear el frame para el portfolio
    contentFrames["Portfolio"] = mainFrame:addFrame("portfolioFrame")
        :setPosition(1, 4)
        :setSize(mainFrame:getWidth(), mainFrame:getHeight() - 3)
        :setBackground(colors.black)
        :hide()
    
    -- Añadir una lista para mostrar el portfolio
    local portfolioList = contentFrames["Portfolio"]:addList("portfolioList")
        :setPosition(2, 2)
        :setSize(mainFrame:getWidth() - 4, mainFrame:getHeight() - 6)
        :setBackground(colors.black)
        :setForeground(colors.white)

    -- Estado inicial - mostrar Operaciones
    local currentMenu = "Operaciones"

    -- Modificar el onChange del menuBar
    menuBar:onChange(function(self, event, value)
        basalt.debug("=== Debug onChange ===")
        basalt.debug(event, value)
        basalt.debug("Cambiando a menú:", value)
        --basalt.debug("Cambiando a menú:", item and item.text)
        
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
        basalt.debug("=== Fin Debug ===\n")
    end)

    return mainFrame, contentFrames, tickerLabel, profitLabel, listFrame
end

local function updateProfitDisplay(profitLabel, ticker, profit)
    if profit then
        local color = profit >= 0 and colors.green or colors.red
        profitLabel:setForeground(color)
        profitLabel:setText(string.format("Profit actual: $%.2f", profit))
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

local function updatePortfolioList(portfolioList, data)
    if not data then return end
    portfolioList:clear()
    
    for _, holding in ipairs(data) do
        portfolioList:addItem(string.format(
            "%s - Cantidad: %d",
            holding.ticker,
            holding.cantidad
        ))
    end
end

local function updateUI(mainFrame, contentFrames, ticker, data, profit, portfolio)

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
        local profitLabel = contentFrames["Profit"]:getChild("profitLabel")
        if profitLabel then
            updateProfitDisplay(profitLabel, ticker, profit)
        end
    elseif activeMenu == "Portfolio" then
        contentFrames["Operaciones"]:hide()
        contentFrames["Profit"]:hide()
        contentFrames["Portfolio"]:show()
        local portfolioList = contentFrames["Portfolio"]:getChild("portfolioList")
        if portfolioList then
            updatePortfolioList(portfolioList, portfolio)
        end
    end

    mainFrame:updateDraw()
end

return {
    createUI = createUI,
    updateUI = updateUI
}