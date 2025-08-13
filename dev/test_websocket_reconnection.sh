#!/bin/bash

# Test script for WebSocket reconnection after window reuse
# This script demonstrates the WebSocket reconnection fix

echo "🧪 Testing WebSocket Reconnection Fix"
echo "====================================="
echo

# Step 1: Start EPLua
echo "1. Starting EPLua with basic QuickApp..."
cd /Users/jangabrielsson/Documents/dev/eplua
./run.sh examples/fibaro/QA_basic.lua --fibaro --api-port 8081 --telnet-port 8024 --run-for 15 &
EPLUA_PID=$!
sleep 5

echo "2. EPLua started (PID: $EPLUA_PID)"
echo "   QuickApp UI should be available at: http://localhost:8081/plua/quickApp/5555/ui"
echo

# Step 2: Test initial WebSocket
echo "3. Testing initial WebSocket connection..."
curl -s -X POST "http://localhost:8081/plua/broadcast" \
     -H "Content-Type: application/json" \
     -d '{"qa_id": 5555, "element_id": "lbl1", "property_name": "text", "value": "Initial WebSocket Test"}' \
     && echo "   ✅ Initial WebSocket broadcast successful" \
     || echo "   ❌ Initial WebSocket broadcast failed"
echo

# Wait for EPLua to exit (simulating server restart)
echo "4. Waiting for EPLua to exit (simulating server restart)..."
wait $EPLUA_PID
echo "   EPLua process ended"
echo

# Step 3: Restart EPLua
echo "5. Restarting EPLua (simulating server restart)..."
./run.sh examples/fibaro/QA_basic.lua --fibaro --api-port 8081 --telnet-port 8024 --run-for 10 &
EPLUA_PID2=$!
sleep 5

echo "6. EPLua restarted (PID: $EPLUA_PID2)"
echo "   The browser window (if open) should automatically reconnect WebSocket"
echo

# Step 4: Test reconnected WebSocket
echo "7. Testing WebSocket after restart (this should work with the fix)..."
curl -s -X POST "http://localhost:8081/plua/broadcast" \
     -H "Content-Type: application/json" \
     -d '{"qa_id": 5555, "element_id": "lbl1", "property_name": "text", "value": "Reconnected WebSocket Test!"}' \
     && echo "   ✅ Reconnected WebSocket broadcast successful" \
     || echo "   ❌ Reconnected WebSocket broadcast failed"
echo

echo "8. Test completed. Check the browser window to verify UI updates work."
echo "   The WebSocket reconnection fix should ensure update_view works after restart."

# Clean up
wait $EPLUA_PID2
