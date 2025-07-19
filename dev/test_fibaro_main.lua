-- test_fibaro_main.lua - Test script to verify main_file_hook functionality

print("Original script starting...")

-- This should show that the preprocessing worked
print("Testing Fibaro functionality...")

-- Set up a timer to test API
setTimeout(function()
    print("Timer test - Fibaro hooks are working!")
end, 1000)

print("Original script completed.")
