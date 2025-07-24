-- Test built-in modules
-- Verifies that json and net are automatically available

print("=== Built-in Modules Test ===")

-- Test JSON module
print("\n1. Testing JSON module:")
local data = {
    name = "plua",
    version = "0.1.0",
    features = {"timers", "networking", "json"},
    built_in = true
}

local json_string = json.encode(data)
print("Encoded:", json_string)

local parsed = json.decode(json_string)
print("Parsed name:", parsed.name)
print("Built-in:", parsed.built_in)

-- Test Net module
print("\n2. Testing Net module:")
local client = net.HTTPClient()
print("HTTPClient created:", client ~= nil)

local server = net.HTTPServer()
print("HTTPServer created:", server ~= nil)

print("\n✅ Both json and net modules are built-in and working!")
print("No need to call require() for these modules in your scripts.")
