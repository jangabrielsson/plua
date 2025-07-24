#!/bin/bash

echo "🧪 Testing plua Fibaro API Hooks"
echo "================================"
echo

echo "📋 Test 1: Loading Fibaro API support and testing main_file_hook"
echo

# First, test loading fibaro.lua which sets up the hooks
echo "Starting plua with fibaro.lua to set up hooks, then test main_file_hook..."
python -m plua -e 'dofile("fibaro.lua")' test_fibaro_main.lua --duration 3 &
PLUA_PID=$!

# Wait a moment for plua to set up
sleep 2

echo
echo "📋 Test 2: Starting API server and testing API hooks"
echo

# Kill the previous instance
kill $PLUA_PID 2>/dev/null
wait $PLUA_PID 2>/dev/null

# Start with API server
echo "Starting plua with API server and Fibaro hooks..."
python -m plua -e 'dofile("fibaro.lua")' --api 8878 --duration 10 &
API_PID=$!

# Wait for server to start
sleep 3

echo
echo "🌐 Testing Fibaro API endpoints:"
echo

echo "1. GET /api/info"
curl -s http://localhost:8878/api/info | python -m json.tool
echo

echo "2. GET /api/devices"
curl -s http://localhost:8878/api/devices | python -m json.tool
echo

echo "3. GET /api/devices/1"
curl -s http://localhost:8878/api/devices/1 | python -m json.tool
echo

echo "4. POST /api/devices/2 (update device)"
curl -s -X POST http://localhost:8878/api/devices/2 \
  -H 'Content-Type: application/json' \
  -d '{"value": true}' | python -m json.tool
echo

echo "5. Testing non-existent endpoint"
curl -s http://localhost:8878/api/unknown | python -m json.tool
echo

echo "6. Testing plua execute endpoint still works"
curl -s -X POST http://localhost:8878/plua/execute \
  -H 'Content-Type: application/json' \
  -d '{"code":"return \"Both plua and Fibaro APIs work!\""}' | python -m json.tool
echo

echo "🧹 Cleaning up..."
kill $API_PID 2>/dev/null
wait $API_PID 2>/dev/null

echo "✅ Tests completed!"
