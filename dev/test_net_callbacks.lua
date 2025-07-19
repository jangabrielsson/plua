-- test_net_callbacks.lua
-- Test that network callbacks still work with the unified system

print("Testing network callbacks with unified system...")

local client = net.HTTPClient()

print("Making HTTP request...")
client:get("https://httpbin.org/json", function(response)
    print("HTTP response received!")
    print("Status:", response.status_code)
    if response.body then
        local data = json.decode(response.body)
        if data then
            print("JSON data received:", json.encode(data))
        end
    end
    print("Network callback test completed!")
end)

print("HTTP request initiated, waiting for response...")
