-- Test UDP Read Functionality
print_lua("=== UDP Read Test ===")

-- Test UDP connection and read
print_lua("Connecting to 8.8.8.8:53 (Google DNS)...")
udp_connect("8.8.8.8", 53, function(success, conn_id, message)
  if success then
  print_lua("UDP Connect Success:", message)
  print_lua("Connection ID:", conn_id)
  
  -- Send a simple DNS query (this will likely fail, but we can test the read)
  local dns_query = string.char(0x00, 0x01, 0x01, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x03, 0x77, 0x77, 0x77, 0x06, 0x67, 0x6f, 0x6f, 0x67, 0x6c, 0x65, 0x03, 0x63, 0x6f, 0x6d, 0x00, 0x00, 0x01, 0x00, 0x01)
  
  udp_write(conn_id, dns_query, "8.8.8.8", 53, function(write_success, bytes_sent, write_message)
  if write_success then
  print_lua("UDP Write Success:", write_message)
  
  -- Try to read response
  print_lua("Attempting to read UDP response...")
  udp_read(conn_id, 512, function(read_success, data, read_message)
  if read_success then
  print_lua("UDP Read Success:", read_message)
  print_lua("Data length:", #data)
  print_lua("Data preview (first 50 chars):", string.sub(data, 1, 50))
  else
  print_lua("UDP Read Error:", read_message)
  end
  
  -- Close connection
  udp_close(conn_id, function(close_success, close_message)
  print_lua("UDP Close:", close_message)
  end)
  end)
  else
  print_lua("UDP Write Error:", write_message)
  udp_close(conn_id, function(close_success, close_message)
  print_lua("UDP Close:", close_message)
  end)
  end
  end)
  else
  print_lua("UDP Connect Error:", message)
  end
end)

print_lua("UDP test initiated, waiting for results...")
sleep(5)
print_lua("=== UDP Read Test completed ===") 