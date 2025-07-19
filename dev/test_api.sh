#!/bin/bash

# Test script for plua2 REST API
API_URL="http://localhost:8888"

echo "=== Testing plua2 REST API ==="
echo

echo "1. Testing basic API info..."
curl -s "$API_URL/" | python3 -m json.tool
echo

echo "2. Testing runtime status..."
curl -s "$API_URL/plua/status" | python3 -m json.tool
echo

echo "3. Testing simple calculation..."
curl -s -X POST "$API_URL/plua/execute" \
  -H 'Content-Type: application/json' \
  -d '{"code":"return 2 + 2"}' | python3 -m json.tool
echo

echo "4. Testing string operations..."
curl -s -X POST "$API_URL/plua/execute" \
  -H 'Content-Type: application/json' \
  -d '{"code":"return \"Hello, \" .. \"World!\""}' | python3 -m json.tool
echo

echo "5. Testing print output..."
curl -s -X POST "$API_URL/plua/execute" \
  -H 'Content-Type: application/json' \
  -d '{"code":"print(\"Testing output\"); return 42"}' | python3 -m json.tool
echo

echo "6. Testing multiple print statements..."
curl -s -X POST "$API_URL/plua/execute" \
  -H 'Content-Type: application/json' \
  -d '{"code":"print(\"Line 1\"); print(\"Line 2\"); print(\"Line 3\")"}' | python3 -m json.tool
echo

echo "7. Testing error handling..."
curl -s -X POST "$API_URL/plua/execute" \
  -H 'Content-Type: application/json' \
  -d '{"code":"return 1 / 0"}' | python3 -m json.tool
echo

echo "8. Testing timeout (should be quick)..."
curl -s -X POST "$API_URL/plua/execute" \
  -H 'Content-Type: application/json' \
  -d '{"code":"return \"Quick execution\"", "timeout": 1}' | python3 -m json.tool
echo

echo "9. Testing network capabilities (built-in net module)..."
curl -s -X POST "$API_URL/plua/execute" \
  -H 'Content-Type: application/json' \
  -d '{"code":"return type(net)"}' | python3 -m json.tool
echo

echo "10. Testing JSON capabilities (built-in json module)..."
curl -s -X POST "$API_URL/plua/execute" \
  -H 'Content-Type: application/json' \
  -d '{"code":"return type(json)"}' | python3 -m json.tool
echo

echo "=== API Test Complete ==="
