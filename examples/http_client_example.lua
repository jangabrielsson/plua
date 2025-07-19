-- HTTP Client Example
-- This example shows how to make HTTP requests using the built-in net module

print("=== HTTP Client Example ===")

-- Load configuration from .env file if available
local config = {
    timeout = tonumber(_PY.getenv_dotenv("HTTP_TIMEOUT", "30")) or 30,
    user_agent = _PY.getenv_dotenv("USER_AGENT", "plua2-http-client/1.0"),
    debug = _PY.config.debug  -- Use system config for debug flag
}

print("Configuration:")
print("  Timeout:", config.timeout, "seconds")
print("  User Agent:", config.user_agent)
print("  Debug:", config.debug)
print("  Platform:", _PY.config.platform)
print("  Home Directory:", _PY.config.homedir)

-- Create an HTTP client
local client = net.HTTPClient()

-- Example 1: Simple GET request
print("\n1. Making a GET request to httpbin.org...")

client:request("https://httpbin.org/get", {        success = function(response)
            print("✅ Request successful!")
            print("Status:", response.status)
            if config.debug then
                print("Response:")
                print(response.data)
            else
                print("Response length:", string.len(response.data), "characters")
            end
        end,
    error = function(status)
        print("❌ Request failed with status:", status)
    end
})

-- Example 2: POST request with JSON data
setTimeout(function()
    print("\n2. Making a POST request with JSON data...")
    
    local post_data = {
        name = "John Doe",
        email = "john@example.com",
        message = "Hello from plua2!"
    }
    
    client:request("https://httpbin.org/post", {
        options = {
            method = "POST",
            headers = {
                ["Content-Type"] = "application/json",
                ["User-Agent"] = config.user_agent
            },
            data = json.encode(post_data)
        },
        success = function(response)
            print("✅ POST request successful!")
            print("Status:", response.status)
            
            -- Parse the response to show what was echoed back
            local response_data = json.decode(response.data)
            if response_data and response_data.json then
                print("Echoed back:")
                print("  Name:", response_data.json.name)
                print("  Email:", response_data.json.email)
                print("  Message:", response_data.json.message)
            end
            
            if config.debug then
                print("Full response:", response.data)
            end
        end,
        error = function(status)
            print("❌ POST request failed with status:", status)
        end
    })
end, 2000)

-- Example 3: Request with custom headers
setTimeout(function()
    print("\n3. Making a request with custom headers...")
    
    client:request("https://httpbin.org/headers", {
        options = {
            headers = {
                ["X-Custom-Header"] = "MyValue",
                ["Authorization"] = "Bearer fake-token-123"
            }
        },
        success = function(response)
            print("✅ Headers request successful!")
            local response_data = json.decode(response.data)
            if response_data and response_data.headers then
                print("Server received headers:")
                for key, value in pairs(response_data.headers) do
                    if key:match("^X%-") or key == "Authorization" then
                        print("  " .. key .. ":", value)
                    end
                end
            end
        end,
        error = function(status)
            print("❌ Headers request failed with status:", status)
        end
    })
end, 4000)

-- Example 4: Timeout handling
setTimeout(function()
    print("\n4. Testing timeout handling...")
    
    client:request("http://10.255.255.1:12345/timeout", {
        options = {
            method = "GET",
            timeout = config.timeout  -- Use configured timeout
        },
        success = function(response)
            print("✅ Timeout request successful (should not happen)!")
        end,
        error = function(status)
            if status == "timeout" then
                print("⏰ Request timed out as expected (status: '" .. status .. "')")
            else
                print("❌ Request failed with status:", status)
            end
        end
    })
end, 6000)

print("\nHTTP client examples started. Responses will appear as they complete...")
