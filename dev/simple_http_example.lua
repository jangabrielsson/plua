-- Simple HTTP sync call example
print("Simple HTTP sync example")

-- Basic GET request
print("Making GET request...")
local success, status, body, error = _PY.http_call_sync("GET", "https://httpbin.org/json", {}, nil)

if success then
    print("✅ Success! Status:", status)
    print("Response:", body:sub(1, 100) .. "...")  -- First 100 chars
    
    -- Parse JSON response
    local data = json.decode(body)
    if data and data.slideshow then
        print("Title:", data.slideshow.title)
    end
else
    print("❌ Failed:", error)
end

-- Test Base64 encoding
print("\nTesting Base64 encoding:")
local original = "Hello, World!"
local encoded = _PY.base64_encode(original)
local decoded = _PY.base64_decode(encoded)
print("Original:", original)
print("Encoded:", encoded)
print("Decoded:", decoded)
print("Match:", original == decoded and "✅" or "❌")
