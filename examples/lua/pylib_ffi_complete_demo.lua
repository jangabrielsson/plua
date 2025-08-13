-- PyLib FFI System Complete Demo
-- Demonstrates the full FFI-like Python module loading system

print("=== EPLua PyLib FFI System - Complete Demo ===")

print("\n🔧 SYSTEM ARCHITECTURE:")
print("  ┌─ EPLua Core")
print("  │  ├─ engine.py (Lua runtime)")
print("  │  ├─ lua_bindings.py (Python-Lua bridge)")
print("  │  └─ extensions.py (loadPythonModule function)")
print("  │")
print("  └─ PyLib FFI Libraries")
print("     ├─ filesystem.py (luafilesystem compatible)")
print("     ├─ http_client.py (HTTP requests)")
print("     ├─ tcp_client.py (TCP networking)")
print("     ├─ udp_client.py (UDP networking)")
print("     ├─ websocket_client.py (WebSocket)")
print("     └─ mqtt_client.py (MQTT messaging)")

print("\n📦 DYNAMIC LOADING DEMONSTRATION:")

-- Demonstrate loading different types of modules
local modules = {
    {name = "filesystem", description = "File system operations", test_func = "fs_currentdir"},
    {name = "http_client", description = "HTTP client", test_func = "http_request_sync"},
    {name = "tcp_client", description = "TCP networking", test_func = "tcp_connect"},
    {name = "udp_client", description = "UDP networking", test_func = "udp_create_socket"},
    {name = "websocket_client", description = "WebSocket communication", test_func = "websocket_connect"},
    {name = "mqtt_client", description = "MQTT messaging", test_func = "mqtt_client_connect"}
}

for _, module_info in ipairs(modules) do
    print(string.format("\n  Loading %s (%s):", module_info.name, module_info.description))
    
    local module_funcs = _PY.loadPythonModule(module_info.name)
    if module_funcs.error then
        print("    ✗ Error:", module_funcs.error)
    else
        print("    ✓ Loaded successfully")
        
        -- Test if expected function exists
        if module_funcs[module_info.test_func] then
            print("    ✓ Key function available:", module_info.test_func)
        else
            print("    ⚠ Key function not found:", module_info.test_func)
        end
        
        -- Count total functions
        local count = 0
        for _ in pairs(module_funcs) do count = count + 1 end
        print("    📊 Functions available:", count)
    end
end

print("\n🚀 HIGH-LEVEL LUA MODULES:")
print("  These Lua modules use PyLib FFI libraries internally:")

-- Test lfs (uses filesystem.py)
print("\n  📁 LuaFileSystem (lfs.lua):")
local lfs = require("lfs")
print("    ✓ lfs.currentdir():", lfs.currentdir())
print("    ✓ Uses filesystem.py via dynamic loading")

-- Test custom HTTP module (uses http_client.py)
print("\n  🌐 HTTP Module (http.lua):")
local http = require("examples.lua.http")
local response = http.request({url = "https://httpbin.org/json", method = "GET"})
if response and response.status == 200 then
    print("    ✓ http.request() successful, status:", response.status)
else
    print("    ⚠ http.request() failed (maybe no internet)")
end
print("    ✓ Uses http_client.py via dynamic loading")

print("\n🎯 FFI-LIKE INTERFACE COMPARISON:")
print("  LuaJIT FFI:    ffi.load('mylib') -> C functions")
print("  EPLua PyLib:   _PY.loadPythonModule('mymodule') -> Python functions")
print()
print("  LuaJIT:        local lib = ffi.load('sqlite3'); lib.sqlite3_open()")
print("  EPLua:         local db = _PY.loadPythonModule('sqlite'); db.open()")

print("\n📈 BENEFITS:")
print("  ✓ Lazy loading - only load what you need")
print("  ✓ Memory efficient - unused modules not loaded")
print("  ✓ Hot reloading - modules can be reloaded during development")
print("  ✓ Clean separation - Python backend, Lua frontend")
print("  ✓ PyPI packaging - all libraries bundled with EPLua")
print("  ✓ Extensible - users can add custom pylib modules")

print("\n🔮 FUTURE PYPI USAGE:")
print("  $ pip install eplua")
print("  $ eplua my_script.lua")
print()
print("  -- In my_script.lua:")
print("  local fs = _PY.loadPythonModule('filesystem')  -- Built-in")
print("  local http = _PY.loadPythonModule('http_client')  -- Built-in")
print("  local custom = _PY.loadPythonModule('my_custom')  -- User-added")

print("\n✨ EXTENSIBILITY:")
print("  Users can add custom libraries to:")
print("  • ~/.eplua/pylib/my_custom.py")
print("  • ./pylib/project_specific.py")
print("  • site-packages/eplua_extensions/")

print("\n" .. string.rep("=", 60))
print("🎉 EPLua PyLib FFI System: Making Python as Easy as C!")
print("   FFI-like convenience + Python ecosystem = ❤️")
