print("Hello from test file!")
print("Current time:", os.time())
print("Testing restart functionality...")

-- Set a variable to test if state is preserved
test_var = "test_value_" .. os.time()
print("Set test_var to:", test_var) 