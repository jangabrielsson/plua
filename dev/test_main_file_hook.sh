#!/bin/bash
# Test script for simplified main_file_hook system

echo "=== Testing Simplified main_file_hook System ==="
echo

# Test 1: Default hook behavior
echo "🔧 Test 1: Default main_file_hook (no preprocessing)"
echo "Running: python -m src.plua.main test_hook.lua --duration 2"
python -m src.plua.main test_hook.lua --duration 2
echo

# Test 2: Fibaro hook override
echo "🔧 Test 2: Fibaro main_file_hook override (with preprocessing)"
echo "Running: python -m src.plua.main -e 'dofile(\"fibaro.lua\")' test_hook.lua --duration 2"
python -m src.plua.main -e 'dofile("fibaro.lua")' test_hook.lua --duration 2
echo

# Test 3: Direct fibaro.lua loading
echo "🔧 Test 3: Direct Fibaro loading"
echo "Running: python -m src.plua.main fibaro.lua --duration 2"
python -m src.plua.main fibaro.lua --duration 2
echo

echo "✅ All hook tests completed!"
echo
echo "📋 Summary of simplified main_file_hook system:"
echo "  • init.lua provides default implementation (simple file loading)"
echo "  • Libraries can override _PY.main_file_hook for custom behavior"
echo "  • interpreter.execute_file() is now much simpler (always uses hook)"
echo "  • Fibaro preprocessing works via hook override"
