-- Debug test to see what's happening with package path
print("=== Debug Test ===")
print("Package path:", package.path)
print("Package loaded:", package.loaded)
print("Require function type:", type(require))

-- Try to require fibaro
print("Attempting require('fibaro')...")
local success, result = pcall(require, 'fibaro')
if success then
  print("✓ Success!")
else
  print("✗ Failed:", result)
end

print("=== End Debug Test ===") 