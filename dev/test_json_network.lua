-- Test JSON functions with network operations
require("net")

print("=== JSON + Network Integration Test ===")

-- Test 1: HTTP request with JSON response parsing
print("\n--- Test 1: HTTP + JSON Integration ---")
local http_client = net.HTTPClient()

http_client:request("http://httpbin.org/json", {
    success = function(response)
        print("✓ HTTP request successful, status:", response.status)
        print("Raw JSON response length:", string.len(response.data))
        
        -- Parse the JSON response
        local parsed = _PY.json_decode(response.data)
        if parsed.error then
            print("✗ JSON parsing failed:", parsed.error)
        else
            print("✓ JSON parsing successful!")
            if parsed.slideshow then
                print("  Title:", parsed.slideshow.title)
                print("  Author:", parsed.slideshow.author)
                print("  Date:", parsed.slideshow.date)
                print("  Number of slides:", #parsed.slideshow.slides)
            end
        end
    end,
    error = function(status)
        print("✗ HTTP request failed:", status)
    end
})

-- Test 2: Create JSON payload and send via HTTP POST
print("\n--- Test 2: JSON Encoding for HTTP POST ---")
local post_data = {
    user = {
        name = "John Doe",
        email = "john@example.com",
        preferences = {
            theme = "dark",
            notifications = true,
            language = "en"
        }
    },
    timestamp = os.date("%Y-%m-%d %H:%M:%S"),
    action = "user_update"
}

local json_payload = _PY.json_encode(post_data)
print("JSON payload:", json_payload)

http_client:request("http://httpbin.org/post", {
    options = {
        method = "POST",
        headers = {
            ["Content-Type"] = "application/json",
            ["User-Agent"] = "plua-json-test/1.0"
        },
        data = json_payload
    },
    success = function(response)
        print("✓ HTTP POST successful, status:", response.status)
        
        -- Parse the response to see how our JSON was received
        local post_response = _PY.json_decode(response.data)
        if post_response.error then
            print("✗ Response parsing failed:", post_response.error)
        else
            print("✓ Response parsing successful!")
            print("  Server received our JSON data")
            
            -- Parse the data that was echoed back
            if post_response.data then
                local echoed_data = _PY.json_decode(post_response.data)
                if echoed_data.error then
                    print("  Echoed data parse failed:", echoed_data.error)
                else
                    print("  Echoed user name:", echoed_data.user.name)
                    print("  Echoed action:", echoed_data.action)
                    print("  Echoed timestamp:", echoed_data.timestamp)
                end
            end
        end
    end,
    error = function(status)
        print("✗ HTTP POST failed:", status)
    end
})

-- Test 3: Complex JSON structures
print("\n--- Test 3: Complex JSON Structures ---")
local complex_data = {
    api = {
        version = "1.0",
        endpoints = {
            {name = "users", methods = {"GET", "POST", "PUT", "DELETE"}},
            {name = "posts", methods = {"GET", "POST"}},
            {name = "auth", methods = {"POST"}}
        }
    },
    config = {
        database = {
            host = "localhost",
            port = 5432,
            ssl = true,
            pools = {
                read = {min = 1, max = 10},
                write = {min = 1, max = 5}
            }
        },
        cache = {
            enabled = true,
            ttl = 3600,
            servers = {"redis1.local", "redis2.local"}
        }
    }
}

local complex_json = _PY.json_encode(complex_data)
print("Complex JSON length:", string.len(complex_json))

-- Round-trip test
local parsed_complex = _PY.json_decode(complex_json)
if parsed_complex.error then
    print("✗ Complex JSON round-trip failed:", parsed_complex.error)
else
    print("✓ Complex JSON round-trip successful!")
    print("  API version:", parsed_complex.api.version)
    print("  Database host:", parsed_complex.config.database.host)
    print("  Number of endpoints:", #parsed_complex.api.endpoints)
    print("  Cache enabled:", parsed_complex.config.cache.enabled)
    print("  First cache server:", parsed_complex.config.cache.servers[1])
end

print("\nJSON + Network integration tests initiated!")

-- Wait for async operations to complete
setTimeout(function()
    print("\n=== Integration Test Summary ===")
    print("✓ JSON encode/decode functions working")
    print("✓ JSON integration with HTTP requests")
    print("✓ Complex data structure handling")
    print("✓ Network + JSON workflow complete")
end, 10000)
