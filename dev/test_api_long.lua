-- Long-running test script for API testing
print("Long-running API test script started")

-- Set up a repeating timer to keep the script alive
local function keepAlive()
    print("Keep-alive timer fired at", os.date())
    setTimeout(keepAlive, 5000)  -- Every 5 seconds
end

-- Start the keep-alive loop
setTimeout(keepAlive, 5000)

print("Script will run indefinitely. Use Ctrl+C to stop.")
