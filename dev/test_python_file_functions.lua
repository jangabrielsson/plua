-- Test Python-based file functions (readFile, writeFile, fileExist)

print("=== Testing Python file functions ===")

-- Test writeFile
local test_content = "Hello from Python file functions!\nLine 2 with UTF-8: 🎉\nLine 3"
local test_file = "python_test.txt"

print("1. Testing writeFile...")
_PY.writeFile(test_file, test_content)
print("✓ File written successfully")

-- Test fileExist
print("2. Testing fileExist...")
local exists = _PY.fileExist(test_file)
print("✓ File exists: " .. tostring(exists))

local not_exists = _PY.fileExist("nonexistent_file.txt")
print("✓ Nonexistent file: " .. tostring(not_exists))

local nil_path = _PY.fileExist(nil)
print("✓ Nil path: " .. tostring(nil_path))

-- Test readFile
print("3. Testing readFile...")
local read_content = _PY.readFile(test_file)
print("✓ File read successfully, length: " .. string.len(read_content))
print("✓ Content matches: " .. tostring(read_content == test_content))

-- Test error handling
print("4. Testing error handling...")
local success, error_msg = pcall(function()
    _PY.readFile("nonexistent_file.txt")
end)
print("✓ Read nonexistent file error handled: " .. tostring(not success))
if not success then
    print("  Error message: " .. tostring(error_msg))
end

success, error_msg = pcall(function()
    _PY.writeFile("/root/impossible_path.txt", "test")
end)
print("✓ Write to impossible path error handled: " .. tostring(not success))
if not success then
    print("  Error message: " .. tostring(error_msg))
end

-- Cleanup
os.remove(test_file)
print("✓ Test file cleaned up")

print("\n=== File functions are now Python-based and user-facing! ===")
