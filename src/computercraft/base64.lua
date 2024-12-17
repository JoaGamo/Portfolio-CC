local b='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'

local function decode(data)
    data = string.gsub(data, '[^'..b..'=]', '')
    local result = ''
    local count = 0
    
    -- Process binary conversion
    local binary = data:gsub('.', function(x)
        count = count + 1
        if count % 100 == 0 then  -- Yield every 100 characters
            os.queueEvent("yield")
            os.pullEvent("yield")
        end
        
        if x == '=' then return '' end
        local r,f='', (b:find(x)-1)
        for i=6,1,-1 do
            r = r .. (f%2^i - f%2^(i-1) > 0 and '1' or '0')
        end
        return r
    end)
    
    -- Process character conversion
    count = 0
    result = binary:gsub('%d%d%d%d%d%d%d%d', function(x)
        count = count + 1
        if count % 100 == 0 then  -- Yield every 100 characters
            os.queueEvent("yield")
            os.pullEvent("yield")
        end
        
        local c = 0
        for i = 1,8 do
            c = c + (x:sub(i,i) == '1' and 2^(8-i) or 0)
        end
        return string.char(c)
    end)
    
    return result
end

return {
    decode = decode
}