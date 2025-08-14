#!/bin/bash

# Test REPL functionality by sending commands via stdin
echo "Testing REPL state sharing..."
echo ""

# Create a temporary file with commands
cat > /tmp/repl_test_commands.txt << 'EOF'
print("=== Testing variable access ===")
print("test_var =", test_var)
print("fragment_var =", fragment_var)
print("=== Setting new variable ===")
repl_var = "Hello from REPL"
print("repl_var =", repl_var)
print("=== Test complete ===")
exit
EOF

# Run PLua with REPL and pipe the commands
cd /Users/jangabrielsson/Documents/dev/plua_new/plua
./run.sh -e "fragment_var = 42" dev/test_single_engine_repl.lua -i --nodebugger < /tmp/repl_test_commands.txt

# Clean up
rm -f /tmp/repl_test_commands.txt
