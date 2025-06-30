-- Bundled Files Helper for PyInstaller
-- Provides utilities to access files bundled with the executable

local bundled_files = {}

-- Get the base path for bundled files
function bundled_files.get_base_path()
    -- In PyInstaller, files are extracted to sys._MEIPASS
    -- We can access this through the Python environment
    local py = _G._PY
    if py then
        local sys = py.import_module("sys")
        if sys then
            -- Check if _MEIPASS exists without throwing an error
            local success, meipass = pcall(function() return sys._MEIPASS end)
            if success and meipass then
                return meipass
            end
        end
    end
    
    -- Fallback: current directory (development mode)
    return "."
end

-- Get the correct base path that accounts for the src/lua structure
function bundled_files.get_corrected_base_path()
    local base = bundled_files.get_base_path()
    
    -- Check if we're in development mode (src/lua exists)
    local src_lua_path = base .. "/src/lua"
    local file = io.open(src_lua_path .. "/plua/plua_init.lua", "r")
    if file then
        file:close()
        return base .. "/src"  -- Return src/ as the base
    end
    
    -- Check if we're in installed mode (lua exists directly)
    local lua_path = base .. "/lua"
    local file = io.open(lua_path .. "/plua/plua_init.lua", "r")
    if file then
        file:close()
        return base  -- Return current directory as base
    end
    
    -- Fallback: assume src/lua structure
    return base .. "/src"
end

-- Check if a bundled file exists
function bundled_files.exists(path)
    local full_path = bundled_files.get_corrected_base_path() .. "/lua/" .. path
    local file = io.open(full_path, "r")
    if file then
        file:close()
        return true
    end
    return false
end

-- Read a bundled file
function bundled_files.read(path)
    local full_path = bundled_files.get_corrected_base_path() .. "/lua/" .. path
    local file = io.open(full_path, "r")
    if file then
        local content = file:read("*a")
        file:close()
        return content
    end
    return nil
end

-- List files in a bundled directory
function bundled_files.list_dir(dir_path)
    local py = _G._PY
    if py then
        local os = py.import_module("os")
        local base = bundled_files.get_corrected_base_path()
        local full_path = base .. "/lua/" .. dir_path
        local files = {}
        local pylist = os.listdir(full_path)
        if pylist then
            -- Access Python list elements directly
            local i = 0
            while true do
                local success, fname = pcall(function() return pylist[i] end)
                if not success or fname == nil then
                    break
                end
                table.insert(files, fname)
                i = i + 1
            end
        end
        return files
    end
    return {}
end

-- Get common bundled directories
function bundled_files.get_demos_path()
    local base = bundled_files.get_base_path()
    -- Demos are at the root level, not in src/
    return base .. "/demos"
end

function bundled_files.get_examples_path()
    local base = bundled_files.get_base_path()
    -- Examples are at the root level, not in src/
    return base .. "/examples"
end

function bundled_files.get_lua_path()
    return bundled_files.get_corrected_base_path() .. "/lua"
end

-- Example usage functions
function bundled_files.load_demo(name)
    local content = bundled_files.read("demos/" .. name .. ".lua")
    if content then
        return load(content, "demos/" .. name .. ".lua")
    end
    return nil
end

function bundled_files.load_example(name)
    local content = bundled_files.read("examples/" .. name .. ".lua")
    if content then
        return load(content, "examples/" .. name .. ".lua")
    end
    return nil
end

return bundled_files 