-- PLua initialization script
-- This script is automatically loaded at startup to set up the Lua environment

-- Wrap all Python functions in _PY to convert exceptions to Lua string errors
for k, v in pairs(_PY) do
    if type(v) == "userdata" then
        -- This is a Python function, wrap it with error handling
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
end

-- Add any other global Lua setup here in the future
-- For example:
-- - Global helper functions
-- - Metatable configurations
-- - Global variables
-- - Utility functions 