-- fibaro.lua
_PY = _PY or {}
_PY.mobdebug.on()
_PY.mobdebug.coro()
-- Global table with fibaro functions.
print("Fibaro API support")

local Emulator = require('fibaro.emulator')
local Emu = Emulator()
fibaro = require("fibaro.fibaro_funs")
fibaro.plua = Emu
api = Emu.api

-- Override the default hook with Fibaro preprocessing
function _PY.mainLuaFile(filename)
    require('mobdebug').on()
    xpcall(function()
        Emu:loadMainFile(filename)
    end,function(err)
        print(err)
        print(debug.traceback())
    end)
end


_PY.fibaroApiHook = function(method, path, data)
    _PY.mobdebug.on()
    --print("✅ fibaro.lua fibaroApiHook called with:", method, path, data)
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

_PY.getQuickapps = function()
    if not Emu then
        print("Emulator not initialized. Please call _PY.main_file_hook first.")
        return nil, 503
    end
    return Emu:getQuickApps()
end

_PY.getQuickapp = function(id)
    if not Emu then
        print("Emulator not initialized. Please call _PY.main_file_hook first.")
        return nil, 503
    end
    return Emu:getQuickApp(id)
end