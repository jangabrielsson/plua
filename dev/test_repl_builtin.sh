#!/bin/bash
# Test REPL with network functionality

echo "Testing REPL with built-in net module..."

python -m src.plua2 << 'EOF'
print("Testing built-in modules:")
print("JSON available:", json ~= nil)
print("Net available:", net ~= nil)
client = net.HTTPClient()
print("HTTPClient created:", client ~= nil)
exit()
EOF

echo "REPL test completed."
