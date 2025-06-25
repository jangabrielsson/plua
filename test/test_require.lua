-- Test require functionality
print("=== Testing require ===")

-- Check package path
print("Package path:", package.path)

-- Try to require fibaro
print("Attempting to require('fibaro')...")
local success, result = pcall(require, 'fibaro')
if success then
  print("✓ Successfully required fibaro")
  print("Result:", result)
else
  print("✗ Failed to require fibaro:", result)
end

-- Try to require with explicit path
print("Attempting to require('lua.fibaro')...")
local success2, result2 = pcall(require, 'lua.fibaro')
if success2 then
  print("✓ Successfully required lua.fibaro")
  print("Result:", result2)
else
  print("✗ Failed to require lua.fibaro:", result2)
end

print("=== Test completed ===") 