#!/bin/bash

echo "=== Testing Simplified Signal Handler ==="
cd /Users/jangabrielsson/Documents/dev/plua

# Test 1: Non-interactive mode
echo "Test 1: Running QA_basic.lua in non-interactive mode"
python -m plua --fibaro --desktop true examples/fibaro/QA_basic.lua &
PID1=$!
echo "Started process with PID: $PID1"

sleep 3
echo "Sending SIGINT..."
kill -INT $PID1

sleep 2
if kill -0 $PID1 2>/dev/null; then
    echo "❌ Process still running"
    kill -9 $PID1
else
    echo "✅ Process exited cleanly"
fi

echo ""
echo "Test 2: Interactive mode (REPL)"
echo "" | python -m plua --fibaro --desktop true -i examples/fibaro/QA_basic.lua &
PID2=$!
echo "Started REPL process with PID: $PID2"

sleep 3
echo "Sending SIGINT to REPL..."
kill -INT $PID2

sleep 2
if kill -0 $PID2 2>/dev/null; then
    echo "❌ REPL process still running"
    kill -9 $PID2
else
    echo "✅ REPL process exited cleanly"
fi

echo ""
echo "=== Test Complete ==="
