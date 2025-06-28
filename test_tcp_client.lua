-- Simple TCP Client Test
print("Starting TCP Client Test...")

-- Connect to the debug server
_PY.tcp_connect("127.0.0.1", 8767, function(success, conn_id, message)
    print("Connect result:", success, conn_id, message)
    
    if success then
        -- Send a test message
        _PY.tcp_write(conn_id, "Hello from client!\n", function(success, result, message)
            print("Write result:", success, result, message)
            
            if success then
                -- Read response
                _PY.tcp_read(conn_id, 1024, function(success, data, message)
                    print("Read result:", success, data, message)
                    
                    if success and data then
                        print("Received:", data)
                    end
                    
                    -- Close connection
                    _PY.tcp_close(conn_id, function(success, message)
                        print("Close result:", success, message)
                    end)
                end)
            end
        end)
    end
end)

-- Keep running for a few seconds
for i = 1, 5 do
    _PY.sleep(1)
    print("Client running...", i, "seconds")
end

print("Client test completed.") 