-- Simple test script for API testing
print("API test script started")

-- Set up a simple timer to keep the script running
setTimeout(function()
    print("Timer fired - API should be responsive")
end, 2000)

-- Keep running for a while
setTimeout(function()
    print("Shutting down test script")
    os.exit()
end, 10000)
