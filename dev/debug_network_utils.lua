-- Network Module Debug Helper
-- Utility functions for debugging network operations

local debug = {}

-- Color codes for terminal output
debug.colors = {
    reset = "\27[0m",
    red = "\27[31m",
    green = "\27[32m", 
    yellow = "\27[33m",
    blue = "\27[34m",
    magenta = "\27[35m",
    cyan = "\27[36m",
    white = "\27[37m"
}

function debug.colored_print(color, message)
    if debug.colors[color] then
        print(debug.colors[color] .. message .. debug.colors.reset)
    else
        print(message)
    end
end

function debug.print_request(method, path, payload, request_id)
    debug.colored_print("cyan", "=== HTTP REQUEST DEBUG ===")
    print("Request ID: " .. (request_id or "unknown"))
    print("Timestamp: " .. os.date("%Y-%m-%d %H:%M:%S"))
    debug.colored_print("green", "Method: " .. method)
    debug.colored_print("blue", "Path: " .. path)
    
    if payload and payload ~= "" then
        debug.colored_print("yellow", "Payload (" .. #payload .. " bytes):")
        print("  " .. string.sub(payload, 1, 200) .. (string.len(payload) > 200 and "..." or ""))
    else
        debug.colored_print("magenta", "Payload: (empty)")
    end
    print()
end

function debug.print_response(data, status_code, request_id)
    debug.colored_print("cyan", "=== HTTP RESPONSE DEBUG ===")
    print("Request ID: " .. (request_id or "unknown"))
    print("Timestamp: " .. os.date("%Y-%m-%d %H:%M:%S"))
    debug.colored_print("green", "Status: " .. status_code)
    
    if data and data ~= "" then
        debug.colored_print("yellow", "Response (" .. #data .. " bytes):")
        print("  " .. string.sub(data, 1, 200) .. (string.len(data) > 200 and "..." or ""))
    else
        debug.colored_print("magenta", "Response: (empty)")
    end
    print()
end

function debug.hex_dump(data, max_bytes)
    max_bytes = max_bytes or 64
    local bytes = string.sub(data, 1, max_bytes)
    local hex = ""
    local ascii = ""
    
    for i = 1, #bytes do
        local byte = string.byte(bytes, i)
        hex = hex .. string.format("%02x ", byte)
        if byte >= 32 and byte <= 126 then
            ascii = ascii .. string.char(byte)
        else
            ascii = ascii .. "."
        end
        
        if i % 16 == 0 then
            print(hex .. " | " .. ascii)
            hex = ""
            ascii = ""
        end
    end
    
    if hex ~= "" then
        -- Pad the last line
        while #hex < 48 do
            hex = hex .. "   "
        end
        print(hex .. " | " .. ascii)
    end
end

function debug.test_json_parsing(json_string)
    debug.colored_print("cyan", "=== JSON PARSING TEST ===")
    print("Input: " .. json_string)
    
    local success, result = pcall(json.decode, json_string)
    if success then
        debug.colored_print("green", "✅ JSON parsing successful!")
        if type(result) == "table" then
            for k, v in pairs(result) do
                print("  " .. k .. ": " .. tostring(v))
            end
        else
            print("  Result: " .. tostring(result))
        end
    else
        debug.colored_print("red", "❌ JSON parsing failed: " .. tostring(result))
    end
    print()
end

function debug.benchmark_request(url, iterations)
    iterations = iterations or 10
    debug.colored_print("cyan", "=== BENCHMARK TEST ===")
    print("URL: " .. url)
    print("Iterations: " .. iterations)
    
    local client = net.HTTPClient()
    local start_time = os.time()
    local completed = 0
    
    for i = 1, iterations do
        client:request(url, {
            success = function(response)
                completed = completed + 1
                if completed == iterations then
                    local elapsed = os.time() - start_time
                    debug.colored_print("green", "✅ Benchmark completed!")
                    print("Total time: " .. elapsed .. " seconds")
                    print("Average: " .. string.format("%.2f", elapsed / iterations) .. " seconds per request")
                end
            end,
            error = function(status)
                debug.colored_print("red", "❌ Request " .. i .. " failed: " .. status)
            end
        })
    end
end

return debug
