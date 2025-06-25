-- Test to see what's happening with MobDebug
print("=== MobDebug Test ===")
print("This is a test file to debug MobDebug integration")

-- Check if we're running in PLua or system Lua
print("Checking environment...")

-- Try to access PLua-specific features
if package and package.path then
  print("Package system is available")
  print("Package path:", package.path)
else
  print("Package system is NOT available")
end

-- Check require function
if require then
  print("Require function is available")
  print("Require function type:", type(require))
else
  print("Require function is NOT available")
end

-- Try to require fibaro
print("Attempting to require('fibaro')...")
local success, result = pcall(require, 'fibaro')
if success then
  print("✓ Successfully required fibaro")
else
  print("✗ Failed to require fibaro:", result)
end

print("=== End MobDebug Test ===") 