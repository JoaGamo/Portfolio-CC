local function loadConfig()
    local config = {}
    local file = io.open(".env", "r")
    
    if file then
        for line in file:lines() do
            local key, value = line:match("([^=]+)=(.+)")
            if key and value then
                key = key:gsub("^%s*(.-)%s*$", "%1")
                value = value:gsub("^%s*(.-)%s*$", "%1")
                value = value:gsub('"', ''):gsub("'", '')
                config[key] = value
            end
        end
        file:close()
    end
    
    config.API_URL = config.API_URL or "http://localhost:8000"
    return config
end

return {
    loadConfig = loadConfig
}