-- PLua initialization script
-- This script is automatically loaded at startup to set up the Lua environment

-- List of functions that need special handling (socket functions)
local socket_functions = {
    "tcp_connect_sync",
    "tcp_write_sync", 
    "tcp_read_sync",
    "tcp_close_sync",
    "tcp_set_timeout_sync",
    "tcp_get_timeout_sync",
    "tcp_read_until_sync",
    -- Network functions that might interfere with MobDebug
    "get_local_ip",
    "is_port_available",
    "get_hostname"
}

-- Create a lookup table for socket functions
local socket_lookup = {}
for _, func_name in ipairs(socket_functions) do
    socket_lookup[func_name] = true
end

-- Wrap all Python functions in _PY to convert exceptions to Lua string errors
for k, v in pairs(_PY) do
    if type(v) == "userdata" and not socket_lookup[k] then
        -- Standard wrapping for non-socket functions
        _PY[k] = function(...)
            local success, result = pcall(v, ...)
            if success then
                return result
            else
                -- Convert the error to a string if it isn't already
                if type(result) == "string" then
                    error(result)
                else
                    error(tostring(result))
                end
            end
        end
    end
    -- else: leave socket functions untouched!
end

-- Add any other global Lua setup here in the future
-- For example:
-- - Global helper functions
-- - Metatable configurations
-- - Global variables
-- - Utility functions 