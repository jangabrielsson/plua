#!/bin/bash
# test_fibaro_repl.sh - Test Fibaro support in REPL mode

echo "Testing --fibaro flag with REPL..."
echo "if fibaro then print('Fibaro support loaded!') else print('No Fibaro support') end" | python -m src.plua --fibaro &
PID=$!
sleep 2
kill $PID 2>/dev/null
wait $PID 2>/dev/null
echo "REPL test completed."
