-- Test TCP and UDP socket functionality
require("net")

print("Testing TCP and UDP socket functionality...")

-- Test that the functions are available
local tcp_socket = net.TCPSocket()
print("✓ net.TCPSocket() is available")

local udp_socket = net.UDPSocket()
print("✓ net.UDPSocket() is available")

-- Check if the Python functions are exported
if _PY.tcp_connect then
    print("✓ _PY.tcp_connect is available")
else
    print("✗ _PY.tcp_connect not found")
end

if _PY.tcp_read then
    print("✓ _PY.tcp_read is available")
else
    print("✗ _PY.tcp_read not found")
end

if _PY.tcp_write then
    print("✓ _PY.tcp_write is available")
else
    print("✗ _PY.tcp_write not found")
end

if _PY.tcp_close then
    print("✓ _PY.tcp_close is available")
else
    print("✗ _PY.tcp_close not found")
end

if _PY.udp_create_socket then
    print("✓ _PY.udp_create_socket is available")
else
    print("✗ _PY.udp_create_socket not found")
end

if _PY.udp_send_to then
    print("✓ _PY.udp_send_to is available")
else
    print("✗ _PY.udp_send_to not found")
end

if _PY.udp_receive then
    print("✓ _PY.udp_receive is available")
else
    print("✗ _PY.udp_receive not found")
end

print("\nTCP and UDP socket modules are ready!")

-- Quick test of TCP connection to a well-known server
print("\n=== Testing TCP connection ===")
tcp_socket:connect("httpbin.org", 80, {
    success = function()
        print("✓ TCP connection to httpbin.org:80 successful!")
        
        -- Test writing HTTP request
        tcp_socket:write("GET / HTTP/1.1\r\nHost: httpbin.org\r\nConnection: close\r\n\r\n", {
            success = function()
                print("✓ HTTP request sent successfully!")
                
                -- Test reading response
                tcp_socket:read({
                    success = function(data)
                        print("✓ HTTP response received!")
                        print("Response preview:", string.sub(data, 1, 100) .. "...")
                        
                        tcp_socket:close()
                    end,
                    error = function(err)
                        print("✗ TCP read failed:", err)
                    end
                })
            end,
            error = function(err)
                print("✗ TCP write failed:", err)
            end
        })
    end,
    error = function(err)
        print("✗ TCP connection failed:", err)
    end
})

print("TCP test initiated, waiting for results...")

-- Keep runtime alive to see results
setTimeout(function()
    print("\n=== Network tests completed ===")
end, 10000)
