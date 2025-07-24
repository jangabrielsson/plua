-- UDP Socket Example
-- This example shows how to use UDP sockets with the built-in net module

print("=== UDP Socket Example ===")

-- Example 1: Send UDP packet to a public service
print("\n1. Sending UDP packet to time server...")

local udp_socket = net.UDPSocket()

-- Send a time request to a public NTP-like service
-- Note: This is a simple example, real NTP protocol is more complex
udp_socket:sendTo("time request", "time.cloudflare.com", 123, {
    success = function()
        print("✅ UDP packet sent to time server!")
        print("(Note: This is just an example send - real NTP requires specific protocol)")
    end,
    error = function(err)
        print("❌ Failed to send UDP packet:", err)
    end
})

-- Example 2: Simple UDP echo using local loopback
setTimeout(function()
    print("\n2. UDP loopback test...")
    
    local echo_socket = net.UDPSocket()
    
    -- Send to a local echo service (if available) or loopback
    local message = "Hello UDP World!"
    print("Sending message:", message)
    
    echo_socket:sendTo(message, "127.0.0.1", 12345, {
        success = function()
            print("✅ UDP message sent to localhost:12345")
            print("(Note: This will only work if you have an echo service running)")
        end,
        error = function(err)
            print("❌ UDP send failed:", err)
        end
    })
    
    -- Try to receive (this is mainly for demonstration)
    echo_socket:receive({
        success = function(data, ip, port)
            print("✅ Received UDP data:", data, "from", ip .. ":" .. port)
        end,
        error = function(err)
            print("ℹ️  UDP receive note:", err)
        end
    })
    
    -- Close the socket after a short time
    setTimeout(function()
        echo_socket:close()
        print("UDP socket closed.")
    end, 2000)
end, 2000)

-- Example 3: Broadcasting (conceptual example)
setTimeout(function()
    print("\n3. UDP broadcast example...")
    
    local broadcast_socket = net.UDPSocket()
    
    local broadcast_message = json.encode({
        type = "discovery",
        sender = "plua-example",
        timestamp = os.time(),
        message = "Hello from plua!"
    })
    
    print("Broadcasting discovery message...")
    
    -- Send to broadcast address (conceptual)
    broadcast_socket:sendTo(broadcast_message, "255.255.255.255", 9999, {
        success = function()
            print("✅ Broadcast message sent!")
            print("Message:", broadcast_message)
        end,
        error = function(err)
            print("❌ Broadcast failed:", err)
            print("(Note: Broadcasting may require special network permissions)")
        end
    })
    
    setTimeout(function()
        broadcast_socket:close()
    end, 1000)
end, 5000)

print("\nUDP socket examples started. Results will appear as they complete...")
print("\nNote: UDP is connectionless, so some examples may not show responses")
print("unless you have corresponding services running on the target ports.")
