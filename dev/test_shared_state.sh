#!/bin/bash

# Test script to demonstrate shared interpreter state between REPL and API
API_URL="http://localhost:8888"

echo "=== Testing Shared Interpreter State ==="
echo

echo "1. Setting variable 'a' via API..."
result=$(curl -s -X POST "$API_URL/plua/execute" \
  -H 'Content-Type: application/json' \
  -d '{"code":"a = 42; return a"}')
echo "API Response: $result"
echo

echo "2. Reading variable 'a' via API..."
result=$(curl -s -X POST "$API_URL/plua/execute" \
  -H 'Content-Type: application/json' \
  -d '{"code":"return a"}')
echo "API Response: $result"
echo

echo "3. Setting variable 'name' via API..."
result=$(curl -s -X POST "$API_URL/plua/execute" \
  -H 'Content-Type: application/json' \
  -d '{"code":"name = \"plua2\"; return name"}')
echo "API Response: $result"
echo

echo "4. Creating a function via API..."
result=$(curl -s -X POST "$API_URL/plua/execute" \
  -H 'Content-Type: application/json' \
  -d '{"code":"function greet(n) return \"Hello, \" .. n .. \"!\" end; return \"Function created\""}')
echo "API Response: $result"
echo

echo "5. Calling the function via API..."
result=$(curl -s -X POST "$API_URL/plua/execute" \
  -H 'Content-Type: application/json' \
  -d '{"code":"return greet(name)"}')
echo "API Response: $result"
echo

echo "6. Creating a table via API..."
result=$(curl -s -X POST "$API_URL/plua/execute" \
  -H 'Content-Type: application/json' \
  -d '{"code":"config = {host=\"localhost\", port=8080, debug=true}; return config.host"}')
echo "API Response: $result"
echo

echo "7. Reading table data via API..."
result=$(curl -s -X POST "$API_URL/plua/execute" \
  -H 'Content-Type: application/json' \
  -d '{"code":"return config.port"}')
echo "API Response: $result"
echo

echo "=== All variables and functions are now available in both REPL and API ==="
echo "Try these commands in the REPL:"
echo "  return a"
echo "  return name"
echo "  return greet(\"World\")"
echo "  return config.debug"
echo
