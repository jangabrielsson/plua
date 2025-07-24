-- REPL Demo Example
-- This file demonstrates features you can try in the REPL
-- Run: plua
-- Then type these commands one by one

-- Basic Lua operations
print("=== Basic Lua ===")
x = 42
y = x + 8
print("x + 8 =", y)

-- JSON operations
print("\n=== JSON Example ===")
person = {name = "Alice", age = 30, city = "New York"}
json_str = json.encode(person)
print("JSON:", json_str)

parsed = json.decode(json_str)
print("Parsed name:", parsed.name)

-- Timer operations
print("\n=== Timer Example ===")
function delayed_message(msg, delay)
    setTimeout(function()
        print("⏰ Delayed message:", msg)
    end, delay)
    print("Timer scheduled for", delay, "ms")
end

delayed_message("Hello from the future!", 2000)

-- HTTP client example
print("\n=== HTTP Client Example ===")
function test_http()
    local client = net.HTTPClient()
    client:request("https://httpbin.org/json", {
        success = function(response)
            print("✅ HTTP request successful!")
            print("Status:", response.status)
            local data = json.decode(response.data)
            print("Response data:", data.slideshow.title)
        end,
        error = function(err)
            print("❌ HTTP request failed:", err)
        end
    })
    print("HTTP request sent...")
end

-- Uncomment the next line to test HTTP (requires internet)
-- test_http()

print("\n=== REPL Commands to Try ===")
print("help()     - Show REPL help")
print("state()    - Show runtime state")
print("clear()    - Clear screen")
print("exit()     - Exit REPL")

print("\nThis file demonstrates REPL features.")
print("Start the REPL with 'plua' and try these commands!")
