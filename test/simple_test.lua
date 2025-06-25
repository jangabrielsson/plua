-- Simple Test to isolate hanging issue
print("=== Simple Test ===")

-- Test 1: Simple TCP connect
print("Test 1: TCP connect to google.com")
tcp_connect("google.com", 80, function(success, conn_id, message)
  print("Test 1 result:", success, conn_id, message)
  if success then
  tcp_close(conn_id, function(close_success, close_message)
  print("Test 1 close:", close_success, close_message)
  end)
  end
end)

-- Test 2: Simple UDP connect
print("Test 2: UDP connect to 8.8.8.8")
udp_connect("8.8.8.8", 53, function(success, conn_id, message)
  print("Test 2 result:", success, conn_id, message)
  if success then
  udp_close(conn_id, function(close_success, close_message)
  print("Test 2 close:", close_success, close_message)
  end)
  end
end)

-- Test 3: Simple timer
print("Test 3: Timer")
_PY.setTimeout(function()
  print("Test 3 timer fired")
end, 1000)

print("All tests initiated. Should exit when complete.")
print("Active timers:", _PY.has_active_timers())
print("Active network ops:", has_active_network_operations()) 