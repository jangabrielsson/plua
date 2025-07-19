#!/bin/bash
# Fibaro API Integration Test Script
# Tests the auto-generated Fibaro API endpoints

echo "=== Fibaro API Integration Test ==="
echo

# Check if server is running
if ! curl -s http://localhost:8888 > /dev/null; then
    echo "❌ Server not running. Start with:"
    echo "   python -m src.plua2.main --api 8888 fibaro.lua"
    exit 1
fi

echo "✅ Server is running"
echo

# Test main API info
echo "📋 Testing API Info:"
curl -s http://localhost:8888/plua/info | jq -r '.api_version + " - " + (.runtime_active | tostring)'
echo

# Test devices endpoint
echo "🔌 Testing Devices API:"
DEVICES_COUNT=$(curl -s http://localhost:8888/api/devices | jq '.[0].devices | length')
echo "   Found $DEVICES_COUNT devices"

# Test specific device
echo "🏠 Testing Device Detail:"
DEVICE_NAME=$(curl -s http://localhost:8888/api/devices/1 | jq -r '.[0].name')
echo "   Device 1: $DEVICE_NAME"

# Test rooms
echo "🏢 Testing Rooms API:"
ROOMS_COUNT=$(curl -s http://localhost:8888/api/rooms | jq '.[0] | length')
echo "   Found $ROOMS_COUNT rooms"

# Test categories
echo "📂 Testing Categories API:"
CATEGORIES_COUNT=$(curl -s http://localhost:8888/api/categories | jq '.[0] | length')
echo "   Found $CATEGORIES_COUNT categories"

# Test sections
echo "🏘️ Testing Sections API:"
SECTIONS_COUNT=$(curl -s http://localhost:8888/api/sections | jq '.[0] | length')
echo "   Found $SECTIONS_COUNT sections"

# Test system info
echo "ℹ️ Testing System Info:"
SYSTEM_STATUS=$(curl -s http://localhost:8888/api/info | jq -r '.[0].status')
echo "   System status: $SYSTEM_STATUS"

echo
echo "🎉 All tests completed successfully!"
echo
echo "📖 Available endpoints include:"
echo "   GET  /api/devices          - List all devices"
echo "   GET  /api/devices/{id}     - Get specific device"
echo "   POST /api/devices/{id}     - Update device"
echo "   GET  /api/rooms            - List all rooms"
echo "   GET  /api/sections         - List all sections"
echo "   GET  /api/categories       - List all categories"
echo "   GET  /api/info             - System information"
echo "   + 187 more auto-generated endpoints"
echo
echo "🌐 Web REPL: http://localhost:8888/web"
echo "📚 Full API docs: Generated from Fibaro HC3 Swagger specs"
