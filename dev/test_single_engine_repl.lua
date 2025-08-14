-- Test script to verify single engine architecture
print("Script started - setting up timer and variables")

-- Set a global variable from the script
test_var = "Hello from script"

-- Set up a timer
setTimeout(function()
    print("Timer fired! test_var =", test_var)
end, 3000)

print("Script setup complete - REPL should be able to access test_var")
print("Try: print(test_var) in the REPL")
