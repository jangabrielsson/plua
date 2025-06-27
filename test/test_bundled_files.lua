-- Test script to access bundled files in PyInstaller executable
print("Testing bundled file access...")

-- Method 1: Try relative paths (most common)
print("\n--- Method 1: Relative paths ---")
local files_to_test = {
    "demos/QA_basic.lua",
    "examples/basic.lua", 
    "lua/fibaro.lua",
    "lua/plua/net.lua"
}

for _, file in ipairs(files_to_test) do
    local f = io.open(file, "r")
    if f then
        print("✅ Found: " .. file)
        f:close()
    else
        print("❌ Not found: " .. file)
    end
end

-- Method 2: Try with _MEIPASS path (if available)
print("\n--- Method 2: _MEIPASS path ---")
local meipass = _G._MEIPASS
if meipass then
    print("_MEIPASS available: " .. meipass)
    local f = io.open(meipass .. "/demos/QA_basic.lua", "r")
    if f then
        print("✅ Found via _MEIPASS: demos/QA_basic.lua")
        f:close()
    else
        print("❌ Not found via _MEIPASS: demos/QA_basic.lua")
    end
else
    print("_MEIPASS not available (running in development mode)")
end

-- Method 3: List directory contents
print("\n--- Method 3: Directory listing ---")
local function list_dir(dir)
    local files = {}
    local handle = io.popen('dir "' .. dir .. '" 2>nul')
    if handle then
        local result = handle:read("*a")
        handle:close()
        if result and result ~= "" then
            print("Directory " .. dir .. " contents:")
            print(result)
        else
            print("Directory " .. dir .. " not found or empty")
        end
    end
end

list_dir("demos")
list_dir("examples")
list_dir("lua")

print("\n--- Test complete ---") 