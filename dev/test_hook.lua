-- test_hook.lua - Simple test file to verify main_file_hook functionality

print("This is a test file loaded via main_file_hook")
print("Testing timer functionality...")

setTimeout(function()
    print("Timer executed successfully!")
end, 1000)

print("Test file loaded successfully")
