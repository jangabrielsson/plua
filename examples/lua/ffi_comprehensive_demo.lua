-- FFI-like Dynamic Loading Comprehensive Demo
-- Shows the complete FFI-like Python module loading system

print("=== EPLua Dynamic Python Module Loading (FFI-like Interface) ===")
print()

-- Demonstrate the core concept
print("1. CORE CONCEPT:")
print("   Just like LuaJIT's FFI allows loading C libraries on demand,")
print("   EPLua allows loading Python modules on demand from Lua.")
print()

-- Show the basic mechanism
print("2. BASIC MECHANISM:")
print("   _PY.loadPythonModule(module_name) -> table of functions")
print()

-- Load and demonstrate filesystem (like luafilesystem)
print("3. FILESYSTEM MODULE (like luafilesystem):")
local fs_funcs = _PY.loadPythonModule("filesystem")
print("   ✓ Loaded filesystem module")
print("   ✓ Current directory:", fs_funcs.fs_currentdir())

local attrs = fs_funcs.fs_attributes("README.md")
if attrs then
    print("   ✓ README.md size:", attrs.size, "bytes")
end
print()

-- Load and demonstrate HTTP client
print("4. HTTP CLIENT MODULE:")
local http_funcs = _PY.loadPythonModule("http_client")
print("   ✓ Loaded HTTP client module")
print("   ✓ Available functions:", "call_http, http_request_sync")

-- Test a simple HTTP request
local http_result = http_funcs.http_request_sync({
    url = "https://httpbin.org/json",
    method = "GET"
})

if http_result and http_result.status == 200 then
    print("   ✓ HTTP GET successful, status:", http_result.status)
else
    print("   ✗ HTTP request failed (maybe no internet)")
end
print()

-- Load and demonstrate TCP module
print("5. TCP MODULE:")
local tcp_funcs = _PY.loadPythonModule("tcp")
print("   ✓ Loaded TCP module")
print("   ✓ Available functions include:", "tcp_connect, tcp_server_create")
print()

-- Show high-level Lua modules that use this
print("6. HIGH-LEVEL LUA MODULES:")
print("   These Lua modules use dynamic loading internally:")
print()

-- Test lfs module (filesystem wrapper)
local lfs = require("lfs")
print("   lfs (filesystem):")
print("   ✓ lfs.currentdir():", lfs.currentdir())
print("   ✓ All lfs functions work transparently")
print()

-- Test http module (our custom wrapper)
local http = require("examples.lua.http")
print("   http (our custom wrapper):")
local http_test = http.get("https://httpbin.org/json")
if http_test and http_test.ok then
    print("   ✓ http.get() successful")
else
    print("   ✗ http.get() failed (maybe no internet)")
end
print()

-- Show the benefits
print("7. BENEFITS OF THIS APPROACH:")
print("   ✓ Lazy loading - modules only loaded when needed")
print("   ✓ Memory efficient - unused Python code isn't loaded")
print("   ✓ Hot reloading - modules can be reloaded during development")
print("   ✓ Clean separation - Python backend, Lua frontend")
print("   ✓ Modular development - each module is independent")
print("   ✓ FFI-like convenience - 'C library' feeling but Python powered")
print()

-- Show the comparison
print("8. COMPARISON TO LUAJIT FFI:")
print("   LuaJIT FFI:    ffi.load('libname') -> C library functions")
print("   EPLua:         _PY.loadPythonModule('module') -> Python functions")
print()
print("   LuaJIT FFI:    Direct C function calls")
print("   EPLua:         Direct Python function calls (via Lupa)")
print()
print("   LuaJIT FFI:    C types and structures")
print("   EPLua:         Python objects and data structures")
print()

-- Show available modules
print("9. AVAILABLE MODULES:")
local available_modules = {
    "filesystem", "http_client", "tcp", "udp", "websocket", 
    "mqtt", "gui", "extensions"
}

for _, module_name in ipairs(available_modules) do
    local success, module_funcs = pcall(function()
        return _PY.loadPythonModule(module_name)
    end)
    
    if success and not module_funcs.error then
        local func_count = 0
        for _ in pairs(module_funcs) do
            func_count = func_count + 1
        end
        print(string.format("   ✓ %-15s (%d functions available)", module_name, func_count))
    else
        print(string.format("   ✗ %-15s (not available)", module_name))
    end
end

print()
print("=== CONCLUSION ===")
print("EPLua provides a powerful FFI-like interface where:")
print("• Lua scripts can dynamically load Python modules")
print("• All Python functionality becomes immediately available")
print("• Clean APIs can be built on top of Python backends")
print("• Development is modular and memory-efficient")
print("• The same convenience as LuaJIT FFI, but Python-powered!")
