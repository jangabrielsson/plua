-- Network Extensions Demo (Fixed Version)
-- Demonstrates TCP and UDP networking with proper timeout handling
local tcp_connect = _PY.tcp_connect
local tcp_write = _PY.tcp_write
local tcp_read = _PY.tcp_read
local tcp_close = _PY.tcp_close
local udp_connect = _PY.udp_connect
local udp_write = _PY.udp_write
local udp_read = _PY.udp_read
local get_local_ip = _PY.get_local_ip
local is_port_available = _PY.is_port_available
local udp_close = _PY.udp_close

print("=== PLua Network Extensions Demo (Fixed) ===")

-- TCP Connection Example
print("\n--- TCP Connection Example ---")
print("Attempting to connect to httpbin.org:80...")

tcp_connect("httpbin.org", 80, function(success, conn_id, message)
  if success then
    print("TCP Connect Success:", message)
    print("Connection ID:", conn_id)
    
    -- Send HTTP GET request
    local http_request = "GET /get HTTP/1.1\r\nHost: httpbin.org\r\nConnection: close\r\n\r\n"
    tcp_write(conn_id, http_request, function(write_success, bytes_sent, write_message)
      if write_success then
        print("TCP Write Success:", write_message)
        
        -- Read response with timeout handling
        tcp_read(conn_id, 2048, function(read_success, data, read_message)
          if read_success then
            print("TCP Read Success:", read_message)
            print("Response preview (first 200 chars):", string.sub(data, 1, 200))
          else
            print("TCP Read Error:", read_message)
          end
          
          -- Always close connection
          tcp_close(conn_id, function(close_success, close_message)
            print("TCP Close:", close_success, close_message)
          end)
        end)
      else
        print("TCP Write Error:", write_message)
        -- Close connection on write error
        tcp_close(conn_id, function(close_success, close_message)
          print("TCP Close after write error:", close_success, close_message)
        end)
      end
    end)
  else
    print("TCP Connect Error:", message)
  end
end)

-- UDP Connection Example (Simplified)
print("\n--- UDP Connection Example ---")
print("Attempting UDP connection to 8.8.8.8:53 (DNS)...")

udp_connect("8.8.8.8", 53, function(success, conn_id, message)
  if success then
    print("UDP Connect Success:", message)
    print("Connection ID:", conn_id)
    
    -- Send a simple DNS query
    local dns_query = string.char(0x00, 0x01, 0x01, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x03, 0x77, 0x77, 0x77, 0x06, 0x67, 0x6f, 0x6f, 0x67, 0x6c, 0x65, 0x03, 0x63, 0x6f, 0x6d, 0x00, 0x00, 0x01, 0x00, 0x01)
    udp_write(conn_id, dns_query, "8.8.8.8", 53, function(write_success, bytes_sent, write_message)
      if write_success then
        print("UDP Write Success:", write_message)
        
        -- Read response with timeout
        udp_read(conn_id, 512, function(read_success, data, read_message)
          if read_success then
            print("UDP Read Success:", read_message)
            print("Response length:", #data)
          else
            print("UDP Read Error:", read_message)
          end
          
          -- Always close connection
          udp_close(conn_id, function(close_success, close_message)
            print("UDP Close:", close_success, close_message)
          end)
        end)
      else
        print("UDP Write Error:", write_message)
        -- Close connection on write error
        udp_close(conn_id, function(close_success, close_message)
          print("UDP Close after write error:", close_success, close_message)
        end)
      end
    end)
  else
    print("UDP Connect Error:", message)
  end
end)

-- Network Utility Functions
print("\n--- Network Utility Functions ---")
print("Local IP address:", get_local_ip())
print("Port 80 available:", is_port_available(80))
print("Port 8080 available:", is_port_available(8080))

-- Error Handling Example (with timeout)
print("\n--- Error Handling Example ---")
print("Attempting to connect to non-existent server...")

tcp_connect("nonexistent.example.com", 9999, function(success, conn_id, message)
  if success then
    print("Unexpected success:", message)
    tcp_close(conn_id, function(close_success, close_message)
      print("Close after unexpected success:", close_success, close_message)
    end)
  else
    print("Expected error:", message)
  end
end)

-- Simple Test Operations
print("\n--- Simple Test Operations ---")

-- Test 1: Simple TCP connect and close
tcp_connect("google.com", 80, function(success, conn_id, message)
  if success then
    print("Test 1 - Connect Success:", message)
    tcp_close(conn_id, function(close_success, close_message)
      print("Test 1 - Close:", close_success, close_message)
    end)
  else
    print("Test 1 - Connect Error:", message)
  end
end)

-- Test 2: Simple UDP connect and close
udp_connect("8.8.8.8", 53, function(success, conn_id, message)
  if success then
    print("Test 2 - UDP Connect Success:", message)
    udp_close(conn_id, function(close_success, close_message)
      print("Test 2 - UDP Close:", close_success, close_message)
    end)
  else
    print("Test 2 - UDP Connect Error:", message)
  end
end)

print("\n=== Network Demo (Fixed) completed ===")
print("(All operations should complete and exit cleanly)") 