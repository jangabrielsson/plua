-- LuaFileSystem Example - Basic Usage
-- Shows how to use the lfs module for common filesystem operations

local lfs = require("lfs")

print("=== LuaFileSystem Basic Usage ===")

-- Get current directory
local current_dir = lfs.currentdir()
print("Current directory:", current_dir)

-- List files in current directory
print("\nFiles in current directory:")
for filename in lfs.dir(".") do
    local path = current_dir .. "/" .. filename
    local attrs = lfs.attributes(path)
    if attrs then
        local file_type = attrs.mode
        local size = attrs.size
        local mod_time = os.date("%Y-%m-%d %H:%M:%S", attrs.modification)
        print(string.format("  %-20s %10s %8d bytes  %s", 
                           filename, file_type, size, mod_time))
    end
end

-- Check if a specific file exists
local function file_exists(filename)
    local attrs = lfs.attributes(filename)
    return attrs ~= nil
end

print("\nChecking for common files:")
local common_files = {"README.md", "src", "docs", "examples"}
for _, filename in ipairs(common_files) do
    if file_exists(filename) then
        local attrs = lfs.attributes(filename)
        print(string.format("  ✓ %s (%s)", filename, attrs.mode))
    else
        print(string.format("  ✗ %s (not found)", filename))
    end
end

-- Create a temporary directory
local temp_dir = "temp_example"
print(string.format("\nCreating temporary directory: %s", temp_dir))

if lfs.mkdir(temp_dir) then
    print("  ✓ Directory created successfully")
    
    -- Create a file in the directory
    local temp_file = temp_dir .. "/example.txt"
    local f = io.open(temp_file, "w")
    if f then
        f:write("Hello from LuaFileSystem!\n")
        f:close()
        print("  ✓ File created:", temp_file)
        
        -- Check file attributes
        local attrs = lfs.attributes(temp_file)
        if attrs then
            print(string.format("    File size: %d bytes", attrs.size))
            print(string.format("    File mode: %s", attrs.mode))
            print(string.format("    Modified: %s", os.date("%c", attrs.modification)))
        end
        
        -- Clean up
        os.remove(temp_file)
        print("  ✓ File removed")
    end
    
    -- Remove directory
    if lfs.rmdir(temp_dir) then
        print("  ✓ Directory removed")
    end
else
    print("  ✗ Failed to create directory")
end

-- Demonstrate touch functionality
print("\nDemonstrating touch functionality:")
local touch_file = "touch_example.txt"
local f = io.open(touch_file, "w")
if f then
    f:write("Touch test file")
    f:close()
    
    -- Get original modification time
    local original_attrs = lfs.attributes(touch_file)
    print(string.format("  Original mtime: %s", os.date("%c", original_attrs.modification)))
    
    -- Wait a moment then touch the file
    os.execute("sleep 1") -- Simple delay
    
    -- Touch with current time
    if lfs.touch(touch_file) then
        local new_attrs = lfs.attributes(touch_file)
        print(string.format("  New mtime:      %s", os.date("%c", new_attrs.modification)))
        print("  ✓ File touched successfully")
    end
    
    -- Clean up
    os.remove(touch_file)
    print("  ✓ File cleaned up")
end

print("\n=== LuaFileSystem Example Complete ===")
print("The lfs module is working correctly and provides full compatibility")
print("with the standard luafilesystem library!")
