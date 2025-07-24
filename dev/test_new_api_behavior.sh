#!/bin/bash
# test_new_api_behavior.sh - Comprehensive test of new API behavior

echo "=== Testing New API Behavior ==="

echo ""
echo "1. Testing default cleanup-port behavior (should use default port 8888)..."
python -m src.plua --cleanup-port

echo ""
echo "2. Testing cleanup-port with custom API port..."
python -m src.plua --api-port 9001 --cleanup-port

echo ""
echo "3. Testing --noapi with inline script (should not start API)..."
python -m src.plua --noapi -e 'print("No API server running")' -e 'print("Test completed")'

echo ""
echo "4. Testing custom API port with script..."
echo 'print("Testing custom port")' > /tmp/test_custom_port.lua
python -m src.plua --api-port 8891 /tmp/test_custom_port.lua &
TEST_PID=$!
sleep 3

echo "   Checking if API is available on port 8891..."
if curl -s http://localhost:8891/plua/status > /dev/null; then
    echo "   ✓ API server running on port 8891"
else
    echo "   ✗ API server not responding on port 8891"
fi

kill $TEST_PID 2>/dev/null
wait $TEST_PID 2>/dev/null
rm -f /tmp/test_custom_port.lua

echo ""
echo "5. Testing Fibaro + custom port combination..."
python -m src.plua --fibaro --api-port 8892 -e 'print("Fibaro:", fibaro ~= nil)' &
FIBARO_PID=$!
sleep 3

echo "   Checking Fibaro API endpoint on port 8892..."
if curl -s http://localhost:8892/api/devices > /dev/null; then
    echo "   ✓ Fibaro API endpoint responding on port 8892"
else
    echo "   ✗ Fibaro API endpoint not responding on port 8892"
fi

kill $FIBARO_PID 2>/dev/null
wait $FIBARO_PID 2>/dev/null

echo ""
echo "=== All tests completed ==="
