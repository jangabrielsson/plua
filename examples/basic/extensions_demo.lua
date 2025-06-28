-- Extensions Demo
-- Demonstrates the new extension system with various Python functions

setTimeout = _PY.setTimeout
clearTimeout = _PY.clearTimeout

print("=== PLua Extensions Demo ===")

-- Timer functions (original functionality)
print("\n--- Timer Functions ---")
print("Setting up a timer...")
local timer_id = setTimeout(function()
  print("Timer fired after 2 seconds!")
end, 2000)

-- I/O functions
print("\n--- I/O Functions ---")
print("Current time:", _PY.get_time())
print("Python version:", _PY.get_python_version())

-- Write a test file
local success = _PY.write_file("test_output.txt", "Hello from PLua extensions!")
if success then
  print("File written successfully")
  local content = _PY.read_file("test_output.txt")
  print("File content:", content)
else
  print("Failed to write file")
end

-- File system functions
print("\n--- File System Functions ---")
print("Current directory files:")
local files = _PY.list_files(".")
if files then
  for i = 1, #files do
  if i <= 5 then  -- Show first 5 files
  print("  " .. files[i])
  end
  end
end

print("File exists 'examples/basic.lua':", _PY.file_exists("examples/basic.lua"))
print("File exists 'nonexistent.txt':", _PY.file_exists("nonexistent.txt"))

-- JSON functions
print("\n--- JSON Functions ---")
local json_data = '{"name": "John", "age": 30, "city": "New York"}'
local parsed = _PY.parse_json(json_data)
if parsed then
  print("Parsed JSON name:", parsed.name)
  print("Parsed JSON age:", parsed.age)
  
  local back_to_json = _PY.to_json(parsed)
  print("Back to JSON:", back_to_json)
end

-- Network functions
print("\n--- Network Functions ---")
print("Hostname:", _PY.get_hostname())
print("Port 80 open on localhost:", _PY.check_port("localhost", 80))

-- Configuration functions
print("\n--- Configuration Functions ---")
local home_dir = _PY.get_env_var("HOME", "Not set")
print("HOME environment variable:", home_dir)

-- List all available extensions
print("\n--- Available Extensions ---")
_PY.list_extensions()

print("\n=== Demo completed ===")
print("(Timer will fire in 2 seconds if still running)") 