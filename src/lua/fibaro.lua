-- fibaro.lua

-- Global table with fibaro functions.
fibaro = {}

-- Global table with fibaro api functions. Dummy implmenetations for now.
api = {}
function api.get(path) return nil,200 end
function api.post(path, data) return nil,200 end
function api.put(path, data) return nil,200 end
function api.delete(path) return nil,200 end

-- Override the default hook with Fibaro preprocessing
function _PY.main_file_hook(filename)
    
    -- Read the file content
    local file = io.open(filename, "r")
    if not file then
        error("Cannot open file: " .. filename)
    end
    
    local content = file:read("*all")
    file:close()
    
    -- Dummy pre-process message
    print("Pre-processing file: " .. filename)
    local preprocessed = content
    
    -- Execute the preprocessed content
    local func, err = load(preprocessed, "@" .. filename)
    if func then
        coroutine.wrap(func)()
    else
        error("Failed to load preprocessed script: " .. tostring(err))
    end
end

-- Set up the single Fibaro API handler function
-- Dummy version for now.
_PY.fibaro_api_hook = function(method, path, path_params, query_params, body_data)
    print("Fibaro API hook called:")
    print("  Method: " .. method)
    print("  Path: " .. path)
    return {},200
end
    