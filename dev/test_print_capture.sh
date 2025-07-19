#!/bin/bash
# Test script for plua2 Web UI with print capture

echo "=== Testing plua2 Web UI with Print Capture ==="

# Start the server if not already running
if ! lsof -i :8888 >/dev/null 2>&1; then
    echo "Starting plua2 API server..."
    cd /Users/jangabrielsson/Documents/dev/plua2
    python -m plua2 --api 8888 &
    SERVER_PID=$!
    sleep 3
    echo "Server started with PID: $SERVER_PID"
else
    echo "Server already running on port 8888"
fi

echo -e "\n1. Testing simple print capture..."
echo '{"code":"print(\"Hello, World!\"); return \"Done\""}' | curl -s -X POST http://localhost:8888/plua/execute -H "Content-Type: application/json" -d @- | python -m json.tool

echo -e "\n2. Testing multiple prints..."
echo '{"code":"print(\"Line 1\"); print(\"Line 2\"); print(\"Line 3\")"}' | curl -s -X POST http://localhost:8888/plua/execute -H "Content-Type: application/json" -d @- | python -m json.tool

echo -e "\n3. Testing JSON with prints..."
echo '{"code":"print(\"Creating JSON...\"); local data = {name=\"test\", value=42}; print(\"Data created:\", json.encode(data)); return data"}' | curl -s -X POST http://localhost:8888/plua/execute -H "Content-Type: application/json" -d @- | python -m json.tool

echo -e "\n4. Testing timer with print (should capture immediately)..."
echo '{"code":"print(\"Setting timer...\"); setTimeout(function() print(\"Timer fired!\") end, 1000); return \"Timer set\""}' | curl -s -X POST http://localhost:8888/plua/execute -H "Content-Type: application/json" -d @- | python -m json.tool

echo -e "\n5. Testing error with prior print..."
echo '{"code":"print(\"Before error\"); error(\"Test error\")"}' | curl -s -X POST http://localhost:8888/plua/execute -H "Content-Type: application/json" -d @- | python -m json.tool

echo -e "\n=== Print Capture Tests Complete ==="
echo "✅ Open http://localhost:8888/web to test the Web REPL"
echo "✅ Try entering: print('Hello from browser!'); return 'Success'"
echo "✅ The print output should now appear in the web interface!"

if [ ! -z "$SERVER_PID" ]; then
    echo -e "\nPress Ctrl+C to stop the server..."
    wait $SERVER_PID
fi
