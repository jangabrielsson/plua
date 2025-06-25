-- Test script to demonstrate Lua modules
print("=== Lua Module Test ===")

-- Load the utility module
print("\n--- Loading utils module ---")
local utils = require("utils")
print("Utils module loaded successfully")

-- Test utility functions
print("\n--- Testing utility functions ---")
print("Format with prefix:", utils.format_with_prefix("Test", "Hello World"))
print("Is empty check:", utils.is_empty(""), utils.is_empty("not empty"))
print("Capitalize:", utils.capitalize("hello"), utils.capitalize("world"))

local test_table = utils.create_table("name", "John", "age", 30, "city", "New York")
print("Created table:")
for key, value in pairs(test_table) do
  print("  " .. key .. ":", value)
end

-- Load the network utils module
print("\n--- Loading network_utils module ---")
local network_utils = require("network_utils")
print("Network utils module loaded successfully")

-- Test network utilities
print("\n--- Testing network utilities ---")
network_utils.get_network_info()

-- Test a simple network connection
print("\n--- Testing network connection ---")
network_utils.test_tcp_connection("google.com", 80, function(success, conn_id, message)
  print("Connection test completed")
end)

print("\n=== Module test completed ===") 