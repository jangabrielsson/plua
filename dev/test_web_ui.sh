#!/bin/bash
# Test script for plua2 Web UI functionality

echo "=== Testing plua2 Web UI ==="

# Start the server in background  
echo "Starting plua2 API server..."
cd /Users/jangabrielsson/Documents/dev/plua2
python -m plua2 --api 8888 &
SERVER_PID=$!

# Wait for server to start
sleep 3

echo "Server started with PID: $SERVER_PID"

# Test API endpoints
echo -e "\n1. Testing API root endpoint..."
curl -s http://localhost:8888/ | python -m json.tool

echo -e "\n2. Testing Web UI availability..."
WEB_UI_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8888/web)
if [ "$WEB_UI_STATUS" = "200" ]; then
    echo "✅ Web UI is accessible at http://localhost:8888/web"
else
    echo "❌ Web UI failed with status: $WEB_UI_STATUS"
fi

echo -e "\n3. Testing API info endpoint..."
curl -s http://localhost:8888/plua/info | python -m json.tool

echo -e "\n4. Testing Lua execution via API..."
echo '{"code":"return 2 + 2"}' | curl -s -X POST http://localhost:8888/plua/execute -H "Content-Type: application/json" -d @- | python -m json.tool

echo -e "\n5. Testing state persistence..."
echo '{"code":"webTestVar = 42; return \"Variable set\""}' | curl -s -X POST http://localhost:8888/plua/execute -H "Content-Type: application/json" -d @- | python -m json.tool

echo '{"code":"return webTestVar"}' | curl -s -X POST http://localhost:8888/plua/execute -H "Content-Type: application/json" -d @- | python -m json.tool

echo -e "\n6. Testing built-in modules..."
echo '{"code":"return \"net available: \" .. tostring(net ~= nil) .. \", json available: \" .. tostring(json ~= nil)"}' | curl -s -X POST http://localhost:8888/plua/execute -H "Content-Type: application/json" -d @- | python -m json.tool

echo -e "\n=== Web UI Test Complete ==="
echo "✅ You can now open http://localhost:8888/web in your browser"
echo "✅ The Web REPL should be fully functional"

# Keep server running for manual testing
echo -e "\nPress Ctrl+C to stop the server and exit..."
wait $SERVER_PID
