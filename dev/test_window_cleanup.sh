#!/bin/bash

# Test script to verify QuickApp window cleanup during timeout
cd /Users/jangabrielsson/Documents/dev/plua

echo "Starting plua with QuickApp that opens a window..."
python -m plua --fibaro --desktop true -i main.lua &
PLUA_PID=$!

echo "Started plua with PID: $PLUA_PID"
echo "Waiting for QuickApp window to open..."
sleep 8  # Give time for window to open

echo "Sending SIGINT to plua..."
kill -INT $PLUA_PID

# Wait to see the timeout cleanup
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
