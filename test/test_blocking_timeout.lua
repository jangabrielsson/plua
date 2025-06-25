-- Test script to verify that blocking reads with timeout actually block for the specified duration
-- This test connects to a server that doesn't send data and measures the time taken for a read operation

print("=== Blocking Read Timeout Test ===")
print("This test verifies that tcp_read_sync with timeout actually blocks for the specified duration")

local tcp_connect_sync = _PY.tcp_connect_sync
local tcp_read_sync = _PY.tcp_read_sync
local tcp_set_timeout_sync = _PY.tcp_set_timeout_sync
local tcp_get_timeout_sync = _PY.tcp_get_timeout_sync
local tcp_close_sync = _PY.tcp_close_sync
local os = _PY.os

-- Function to measure time taken for an operation
local function measure_time(func)
  local start_time = os.time()
  local start_clock = os.clock()
  
  local result = func()
  
  local end_time = os.time()
  local end_clock = os.clock()
  
  local wall_time = end_time - start_time
  local cpu_time = end_clock - start_clock
  
  return result, wall_time, cpu_time
end

-- Test 1: Connect to a server that doesn't send data (localhost:80 should work)
print("\n--- Test 1: Blocking read with 5-second timeout ---")
print("Connecting to localhost:80 (should connect but no data will be sent)")

local success, conn_id, message = tcp_connect_sync("localhost", 80)
if not success then
  print("Failed to connect to localhost:80, trying 127.0.0.1:80")
  success, conn_id, message = tcp_connect_sync("127.0.0.1", 80)
end

if not success then
  print("Failed to connect to any local server. Creating a simple test server...")
  
  -- Create a simple test server that accepts connections but doesn't send data
  print("Starting test server on port 8888...")
  os.execute("python3 test/test_server.py 8888 &")
  
  -- Wait a moment for server to start
  os.execute("sleep 2")
  
  -- Now try to connect to our test server
  success, conn_id, message = tcp_connect_sync("localhost", 8888)
end

if success then
  print("✓ Connected successfully:", message)
  print("Connection ID:", conn_id)
  
  -- Set 5-second timeout
  print("\nSetting 5-second timeout...")
  local timeout_success, timeout_msg = tcp_set_timeout_sync(conn_id, 5.0)
  print("Timeout set:", timeout_msg)
  
  -- Verify timeout was set correctly
  local get_success, current_timeout, timeout_info = tcp_get_timeout_sync(conn_id)
  if get_success then
  print("Current timeout:", current_timeout, "seconds")
  end
  
  -- Measure time for blocking read
  print("\nStarting blocking read (should block for 5 seconds)...")
  local start_time = os.time()
  local start_clock = os.clock()
  
  local read_success, data, read_msg = tcp_read_sync(conn_id, 1024)
  
  local end_time = os.time()
  local end_clock = os.clock()
  local wall_time = end_time - start_time
  local cpu_time = end_clock - start_clock
  
  print("Read completed!")
  print("Read result:", read_success, "Data:", data, "Message:", read_msg)
  print("Wall clock time taken:", wall_time, "seconds")
  print("CPU time taken:", string.format("%.3f", cpu_time), "seconds")
  
  -- Check if it actually blocked for approximately 5 seconds
  if wall_time >= 4.5 and wall_time <= 5.5 then
  print("✓ SUCCESS: Read blocked for approximately 5 seconds as expected")
  else
  print("✗ FAILURE: Read did not block for expected duration")
  print("   Expected: ~5 seconds, Actual:", wall_time, "seconds")
  end
  
  -- Close connection
  local close_success, close_msg = tcp_close_sync(conn_id)
  print("Connection closed:", close_msg)
  
else
  print("✗ Failed to connect:", message)
end

-- Test 2: Try with a different timeout value (2 seconds)
print("\n--- Test 2: Blocking read with 2-second timeout ---")

if success then
  -- Reconnect
  success, conn_id, message = tcp_connect_sync("localhost", 80)
  if not success then
  success, conn_id, message = tcp_connect_sync("127.0.0.1", 80)
  end
  if not success and os.execute("lsof -i :8888 > /dev/null 2>&1") == 0 then
  success, conn_id, message = tcp_connect_sync("localhost", 8888)
  end
end

if success then
  print("✓ Connected successfully:", message)
  
  -- Set 2-second timeout
  print("Setting 2-second timeout...")
  local timeout_success, timeout_msg = tcp_set_timeout_sync(conn_id, 2.0)
  print("Timeout set:", timeout_msg)
  
  -- Measure time for blocking read
  print("Starting blocking read (should block for 2 seconds)...")
  local start_time = os.time()
  
  local read_success, data, read_msg = tcp_read_sync(conn_id, 1024)
  
  local end_time = os.time()
  local wall_time = end_time - start_time
  
  print("Read completed!")
  print("Read result:", read_success, "Data:", data, "Message:", read_msg)
  print("Wall clock time taken:", wall_time, "seconds")
  
  -- Check if it actually blocked for approximately 2 seconds
  if wall_time >= 1.5 and wall_time <= 2.5 then
  print("✓ SUCCESS: Read blocked for approximately 2 seconds as expected")
  else
  print("✗ FAILURE: Read did not block for expected duration")
  print("   Expected: ~2 seconds, Actual:", wall_time, "seconds")
  end
  
  -- Close connection
  local close_success, close_msg = tcp_close_sync(conn_id)
  print("Connection closed:", close_msg)
  
else
  print("✗ Failed to connect for second test")
end

-- Test 3: Non-blocking read (timeout = 0)
print("\n--- Test 3: Non-blocking read (timeout = 0) ---")

if success then
  -- Reconnect
  success, conn_id, message = tcp_connect_sync("localhost", 80)
  if not success then
  success, conn_id, message = tcp_connect_sync("127.0.0.1", 80)
  end
  if not success and os.execute("lsof -i :8888 > /dev/null 2>&1") == 0 then
  success, conn_id, message = tcp_connect_sync("localhost", 8888)
  end
end

if success then
  print("✓ Connected successfully:", message)
  
  -- Set non-blocking mode (timeout = 0)
  print("Setting non-blocking mode (timeout = 0)...")
  local timeout_success, timeout_msg = tcp_set_timeout_sync(conn_id, 0)
  print("Timeout set:", timeout_msg)
  
  -- Measure time for non-blocking read
  print("Starting non-blocking read (should return immediately)...")
  local start_time = os.time()
  
  local read_success, data, read_msg = tcp_read_sync(conn_id, 1024)
  
  local end_time = os.time()
  local wall_time = end_time - start_time
  
  print("Read completed!")
  print("Read result:", read_success, "Data:", data, "Message:", read_msg)
  print("Wall clock time taken:", wall_time, "seconds")
  
  -- Check if it returned immediately (should be very fast)
  if wall_time < 1 then
  print("✓ SUCCESS: Non-blocking read returned immediately as expected")
  else
  print("✗ FAILURE: Non-blocking read took too long")
  print("   Expected: < 1 second, Actual:", wall_time, "seconds")
  end
  
  -- Close connection
  local close_success, close_msg = tcp_close_sync(conn_id)
  print("Connection closed:", close_msg)
  
else
  print("✗ Failed to connect for third test")
end

print("\n=== Test Summary ===")
print("This test verifies that:")
print("1. Blocking reads with timeout actually block for the specified duration")
print("2. Non-blocking reads return immediately")
print("3. The timeout mechanism works correctly")

-- Clean up test server if it was started
os.execute("pkill -f 'test_server.py' > /dev/null 2>&1")
print("\nTest completed!") 