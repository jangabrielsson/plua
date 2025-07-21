-- fibaro.lua

local mobdebug = require('mobdebug')
-- Global table with fibaro functions.
fibaro = {}

local Emulator = require('fibaro.emulator')
local Emu

-- Override the default hook with Fibaro preprocessing
function _PY.main_file_hook(filename)
    require('mobdebug').on()
    
    Emu = Emulator()
    Emu:loadMainFile(filename)
end

_PY.fibaro_api_hook = function(method, path, data)
    mobdebug.on()
    print("fibaro_api_hook called with:", method, path, data)
    if Emu then 
        path = path:gsub("^/api", "")  -- Remove /api prefix for compatibility
        return Emu:API_CALL(method, path, data)
    else
        print("Emulator not initialized. Please call _PY.main_file_hook first.")
        return {error = "Emulator not initialized"}, 500
    end
end
    