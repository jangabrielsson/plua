-- fibaro.lua
_PY = _PY or {}
local mobdebug = require('mobdebug')
-- Global table with fibaro functions.
fibaro = {}

local Emulator = require('fibaro.emulator')
local Emu

-- Override the default hook with Fibaro preprocessing
function _PY.main_file_hook(filename)
    require('mobdebug').on()
    xpcall(function()
        Emu = Emulator()
        Emu:loadMainFile(filename)
    end,function(err)
        print(err)
        print(debug.traceback())
    end)
end

_PY.get_quickapps = function()
    if not Emu then
        print("Emulator not initialized. Please call _PY.main_file_hook first.")
        return nil, 503
    end
    return Emu:getQuickApps()
end

_PY.get_quickapp = function(id)
    if not Emu then
        print("Emulator not initialized. Please call _PY.main_file_hook first.")
        return nil, 503
    end
    return Emu:getQuickApp(id)
end

_PY.fibaro_api_hook = function(method, path, data)
    _PY.mobdebug.on()
    --print("fibaro_api_hook called with:", method, path, data)
    if Emu then 
        path = path:gsub("^/api", "")  -- Remove /api prefix for compatibility
        if data and type(data) == 'string' then
            local _,ndata = pcall(json.decode, data)
            data = ndata or {}      
        end
        return Emu:API_CALL(method, path, data)
    else
        print("Emulator not initialized. Please call _PY.main_file_hook first.")
        return {error = "Emulator not initialized"}, 500
    end
end
