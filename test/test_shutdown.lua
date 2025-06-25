-- Test Shutdown Mechanism
print("=== Shutdown Test ===")

-- Test 1: Simple timer
print("Setting up a 2-second timer...")
_PY.setTimeout(function()
  print("Timer completed!")
end, 2000)

-- Test 2: Simple network operation
print("Setting up a TCP connection...")
tcp_connect("google.com", 80, function(success, conn_id, message)
  print("TCP result:", success, conn_id, message)
  if success then
  tcp_close(conn_id, function(close_success, close_message)
  print("TCP close:", close_success, close_message)
  end)
  end
end)

print("All operations initiated. Interpreter should exit when complete.")
print("Active timers:", _PY.has_active_timers())
print("Active network ops:", has_active_network_operations()) 