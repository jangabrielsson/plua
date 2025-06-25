-- Debug Network Test
print("=== Debug Network Test ===")

-- Test 1: Simple TCP connection with immediate callback
print("Test 1: TCP connection to example.com:80")
tcp_connect("example.com", 80, function(success, conn_id, message)
  print("CALLBACK EXECUTED!")
  print("Success:", success)
  print("Connection ID:", conn_id)
  print("Message:", message)
  
  if success then
  print("Connection successful, closing...")
  tcp_close(conn_id, function(close_success, close_message)
  print("Close result:", close_success, close_message)
  end)
  end
end)

print("TCP connect initiated, waiting 10 seconds...")
sleep(10)
print("Test 1 completed")

-- Test 2: UDP connection
print("\nTest 2: UDP connection to 8.8.8.8:53")
udp_connect("8.8.8.8", 53, function(success, conn_id, message)
  print("UDP CALLBACK EXECUTED!")
  print("Success:", success)
  print("Connection ID:", conn_id)
  print("Message:", message)
  
  if success then
  print("UDP connection successful, closing...")
  udp_close(conn_id, function(close_success, close_message)
  print("UDP Close result:", close_success, close_message)
  end)
  end
end)

print("UDP connect initiated, waiting 5 seconds...")
sleep(5)
print("Test 2 completed")

print("=== Debug test completed ===") 