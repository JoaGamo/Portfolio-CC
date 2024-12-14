local basalt = require("basalt")

local function createUI()
    -- Crear el frame principal
    local mainFrame = basalt.createFrame("mainFrame")
        :setSize(term.getSize())
        :setBackground(colors.black)

    -- Crear un Frame para contener la lista con scrollbar
    local contentFrame = mainFrame:addFrame("contentFrame")
        :setSize(mainFrame:getWidth() - 4, mainFrame:getHeight() - 4)
        :setPosition(3, 3)
        :setBackground(colors.gray)
    
    -- Crear el frame que contendrá las operaciones
    local listFrame = contentFrame:addFrame("listFrame")
        :setSize(contentFrame:getWidth() - 1, contentFrame:getHeight())
        :setPosition(1, 1)
        :setBackground(colors.gray)
    
    -- Agregar scrollbar
    local scrollbar = contentFrame:addScrollbar()
        :setPosition(contentFrame:getWidth(), 1)
        :setSize(1, contentFrame:getHeight())
        :setScrollAmount(1)
        :setBarType("vertical")

    -- Conectar scrollbar con el frame de la lista
    scrollbar:onChange(function(self)
        local _, amount = self:getValue()
        listFrame:setPosition(1, 1 - amount)
    end)

    -- Título
    mainFrame:addLabel()
        :setText("Operaciones")
        :setPosition(3, 1)
        :setForeground(colors.white)

    return mainFrame, listFrame, scrollbar
end

local function updateUI(mainFrame, data)
    -- Obtener el listFrame
    local contentFrame = mainFrame:getChild("contentFrame")
    if not contentFrame then return end
    local listFrame = contentFrame:getChild("listFrame")
    if not listFrame then return end
    
    -- Limpiar el contenido anterior
    listFrame:removeChildren()
    
    -- Verificar si hay datos
    if not data then return end
    
    -- Variables para posicionamiento
    local yPos = 1
    local totalHeight = 0

    -- Para cada operación crear una línea
    for i, operation in ipairs(data) do
        -- Crear un frame para la operación
        local opFrame = listFrame:addFrame()
            :setSize(listFrame:getWidth(), 3)
            :setPosition(1, yPos)
            :setBackground(i % 2 == 0 and colors.lightGray or colors.gray)

        -- Añadir detalles de la operación
        opFrame:addLabel()
            :setText(string.format("Ticker: %s", operation.ticker or "N/A"))
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

        -- Agregar un separador
        opFrame:addLabel()
            :setText(string.rep("-", listFrame:getWidth()))
            :setPosition(1, 3)
            :setForeground(colors.lightGray)

        -- Actualizar posición Y para la siguiente operación
        yPos = yPos + 4
        totalHeight = totalHeight + 4
    end

    -- Actualizar el tamaño del frame de la lista
    listFrame:setSize(listFrame:getWidth(), totalHeight)
    
    -- Actualizar el scroll solo si existe el scrollbar
    local scrollbar = contentFrame:getChild("scrollbar")
    if scrollbar then
        scrollbar:setScrollAmount(math.max(0, totalHeight - listFrame:getHeight() + 1))
    end
end

return {
    createUI = createUI,
    updateUI = updateUI
}