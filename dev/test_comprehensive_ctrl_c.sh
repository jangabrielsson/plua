#!/bin/bash

# Comprehensive test for both REPL and global signal handlers
cd /Users/jangabrielsson/Documents/dev/plua

echo "=== Testing CTRL+C Signal Handling ==="
echo ""

echo "Test 1: REPL mode (interactive) signal handling"
echo "Starting plua in REPL mode..."
python -m plua -i dev/test_simple_isrunning.lua &
REPL_PID=$!

sleep 3
echo "Sending SIGINT to REPL process (PID: $REPL_PID)..."
kill -INT $REPL_PID

sleep 2
if kill -0 $REPL_PID 2>/dev/null; then
    echo "❌ REPL: Process still running, killing forcefully"
    kill -9 $REPL_PID
    REPL_RESULT="FAIL"
else
    echo "✅ REPL: Process exited cleanly"
    REPL_RESULT="PASS"
fi

echo ""
echo "Test 2: Global signal handler (non-interactive mode)"
echo "Starting plua without REPL..."
python -m plua --fibaro main.lua &
GLOBAL_PID=$!

sleep 3
echo "Sending SIGINT to global process (PID: $GLOBAL_PID)..."
kill -INT $GLOBAL_PID

sleep 2
if kill -0 $GLOBAL_PID 2>/dev/null; then
    echo "❌ Global: Process still running, killing forcefully"
    kill -9 $GLOBAL_PID
    GLOBAL_RESULT="FAIL"
else
    echo "✅ Global: Process exited cleanly"
    GLOBAL_RESULT="PASS"
fi

echo ""
echo "=== Test Results ==="
echo "REPL signal handler: $REPL_RESULT"
echo "Global signal handler: $GLOBAL_RESULT"

if [[ "$REPL_RESULT" == "PASS" && "$GLOBAL_RESULT" == "PASS" ]]; then
    echo "🎉 All tests passed! Ctrl+C handling is working correctly."
    exit 0
else
    echo "💥 Some tests failed. Signal handling needs improvement."
    exit 1
fi
