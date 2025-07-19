-- Test script with Fibaro API hook
print("Setting up Fibaro API hook...")

-- Set up a simple Fibaro API hook
_PY.fibaro_api_hook = function(method, path, data)
    print("Fibaro API called:", method, path)
    return {message = "Hello from Fibaro API"}, 200
end

print("Fibaro API hook installed, waiting...")

-- Keep the script running for a moment
setTimeout(function()
    print("Test complete")
end, 1000)
