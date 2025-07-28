#!/bin/bash

# Test script to verify Ctrl+C handling with desktop UI
cd /Users/jangabrielsson/Documents/dev/plua

echo "Starting plua with desktop UI in background..."
python -m plua --init-quickapp test_app &
PLUA_PID=$!

echo "Started plua with PID: $PLUA_PID"
sleep 5  # Give more time for UI to start

echo "Sending SIGINT to plua..."
kill -INT $PLUA_PID

# Wait a bit to see the response
sleep 3

# Check if process is still running
if kill -0 $PLUA_PID 2>/dev/null; then
    echo "Process still running, sending SIGKILL..."
    kill -9 $PLUA_PID
    echo "FAIL: Process didn't exit on SIGINT"
    exit 1
else
    echo "SUCCESS: Process exited cleanly"
    exit 0
fi
