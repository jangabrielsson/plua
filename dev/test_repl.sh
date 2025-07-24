#!/bin/bash
# Test script to verify REPL functionality with input

echo "Testing plua REPL with sample commands..."

# Change to parent directory to run from project root
cd "$(dirname "$0")/.."

# Use here-doc to send commands to the REPL
python -m src.plua << 'EOF'
print("Hello from REPL!")
x = 42
x + 10
help()
state()
exit()
EOF

echo "REPL test completed."
