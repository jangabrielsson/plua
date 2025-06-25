-- Test script that uses a library loaded with -l flag
print("=== Testing Library Loading ===")

-- This script expects the utils library to be loaded with -l utils
if utils then
  print("Utils library is available!")
  print("Capitalized:", utils.capitalize("hello world"))
  print("Formatted:", utils.format_with_prefix("Info", "Library loaded successfully"))
  
  local test_table = utils.create_table("name", "Test", "value", 42)
  print("Created table:")
  for key, value in pairs(test_table) do
  print("  " .. key .. ":", value)
  end
else
  print("Error: utils library not loaded. Run with: plua -l utils test/test_with_lib.lua")
end

print("=== Test completed ===") 