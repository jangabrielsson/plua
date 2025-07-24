-- Example Lua script that demonstrates API integration
-- This script runs in the background while the API server is available

print("API Example Script started")
print("The REST API is available at http://localhost:8888")

local counter = 0

-- Create a timer that runs every 5 seconds using the proper plua timer function
setTimeout(function()
    counter = counter + 1
    print("Background timer tick #" .. counter)
    
    -- Create another timer for the next tick
    if counter < 10 then  -- Limit to 10 ticks for demonstration
        setTimeout(function()
            counter = counter + 1
            print("Background timer tick #" .. counter)
        end, 5000)
    end
end, 5000)

-- Create some global variables that can be accessed via API
message = "Hello from API script!"
data = {
    name = "plua API Example",
    version = "1.0",
    features = {"timers", "networking", "json", "rest_api"}
}

-- Example function that can be called via API
function getInfo()
    return {
        uptime_ticks = counter,
        message = message,
        current_time = os.date("%Y-%m-%d %H:%M:%S"),
        available_modules = {
            net = type(net),
            json = type(json)
        }
    }
end

print("Try these API calls:")
print("curl -X POST http://localhost:8888/plua/execute -H 'Content-Type: application/json' -d '{\"code\":\"return message\"}'")
print("curl -X POST http://localhost:8888/plua/execute -H 'Content-Type: application/json' -d '{\"code\":\"return json.encode(data)\"}'")
print("curl -X POST http://localhost:8888/plua/execute -H 'Content-Type: application/json' -d '{\"code\":\"return json.encode(getInfo())\"}'")
print("curl -X POST http://localhost:8888/plua/execute -H 'Content-Type: application/json' -d '{\"code\":\"return counter\"}'")

print("Script initialization complete. API server is running...")
