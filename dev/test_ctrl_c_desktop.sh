#!/bin/bash

# Test script to verify Ctrl+C handling with actual desktop UI window
cd /Users/jangabrielsson/Documents/dev/plua

echo "Starting plua with desktop UI window in background..."
python -m plua --fibaro --desktop true main.lua &
PLUA_PID=$!

echo "Started plua with PID: $PLUA_PID"
sleep 5  # Give time for UI window to open

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
