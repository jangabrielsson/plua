-- fibaro.lua
_PY = _PY or {}
_PY.mobdebug.on()
_PY.mobdebug.coro()
-- Global table with fibaro functions.

local Emulator = require('fibaro.emulator')
local Emu = Emulator()
fibaro = require("fibaro.fibaro_funs")
fibaro.plua = Emu
api = Emu.api

-- Override the default hook with Fibaro preprocessing

function _PY.mainLuaFile(filenames)
    if _PY.config.tool then return Emu:runTool(table.unpack(_PY.config.scripts)) end
    filenames[1] =  _PY.mainfileResolver(filenames[1])
    _PY.mobdebug.on()
    --_print("mainLuaFile",_PY.milli_time()-_PY.config.startTime)
    xpcall(function()
        Emu:loadMainFile(filenames,"greet")
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

return Emu