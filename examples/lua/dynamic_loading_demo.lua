-- Dynamic Python Module Loading Demo
-- Shows how EPLua can dynamically load Python modules like an FFI interface

print("=== Dynamic Python Module Loading Demo ===")

-- Show that we can inspect the _PY table before loading
print("\nInspecting _PY table before loading filesystem module:")
for name, _ in pairs(_PY) do
    if name:match("^fs_") then
        print("  " .. name .. " (already available)")
    end
end

-- Show direct loading of filesystem module
print("\nLoading filesystem module dynamically:")
local fs_funcs = _PY.loadPythonModule("filesystem")

if fs_funcs.error then
    print("Error loading module: " .. fs_funcs.error)
    return
end

print("Available filesystem functions:")
for name, func in pairs(fs_funcs) do
    print("  " .. name .. " (" .. type(func) .. ")")
end

-- Test using the loaded functions directly
print("\nTesting direct function calls:")
local current_dir = fs_funcs.fs_currentdir()
print("Current directory: " .. current_dir)

local attrs = fs_funcs.fs_attributes("README.md")
if attrs then
    print("README.md size: " .. attrs.size .. " bytes")
    print("README.md mode: " .. attrs.mode)
end

-- Now demonstrate the lfs module which uses this dynamic loading internally
print("\n" .. string.rep("=", 50))
print("Now testing the lfs module (which uses dynamic loading internally):")

local lfs = require("lfs")

-- This will trigger the dynamic loading inside lfs.lua
local current_dir_lfs = lfs.currentdir()
print("Current directory via lfs: " .. current_dir_lfs)

-- Show that both approaches give the same result
if current_dir == current_dir_lfs then
    print("✓ Both direct and lfs calls return the same result!")
else
    print("✗ Results differ - this shouldn't happen")
end

print("\n=== Demo Complete ===")
print("This demonstrates the FFI-like Python module loading system where:")
print("1. Python modules can be loaded on demand from Lua")
print("2. All exported functions become immediately available")
print("3. Lua modules like lfs.lua can use this for lazy loading")
print("4. This provides a clean separation between Python backend and Lua API")
