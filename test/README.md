# Test Files

This directory contains various test files for the PLua interpreter.

## Test Files

### `test_modules.lua`
Tests the Lua module system and demonstrates loading modules from the `lua/` directory.
- Tests loading `utils` and `network_utils` modules
- Demonstrates module dependencies
- Tests utility functions and network operations

### `simple_test.lua`
Basic functionality test for the PLua interpreter.
- Tests basic Lua syntax and operations
- Tests Python extension functions
- Tests timer functionality

### `test_shutdown.lua`
Tests the shutdown mechanism of the PLua interpreter.
- Tests that the interpreter exits cleanly when no operations are running
- Tests timer cleanup
- Tests network operation cleanup

### `test_udp_read.lua`
Tests UDP network functionality.
- Tests UDP socket creation
- Tests UDP read operations with timeouts
- Tests UDP callback handling

### `debug_network.lua`
Network debugging and testing script.
- Tests various network operations
- Tests TCP and UDP functionality
- Tests network error handling

### `test_output.txt`
Output file from test runs (may contain test results).

## Running Tests

You can run any test file using the PLua interpreter:

```bash
# Run a specific test
uv run python plua.py test/test_modules.lua

# Run the simple test
uv run python plua.py test/simple_test.lua

# Run the shutdown test
uv run python plua.py test/test_shutdown.lua
```

## Test Categories

- **Module Tests**: `test_modules.lua`
- **Basic Functionality**: `simple_test.lua`
- **Network Tests**: `test_udp_read.lua`, `debug_network.lua`
- **System Tests**: `test_shutdown.lua`

## Adding New Tests

When adding new test files:
1. Place them in this `test/` directory
2. Use descriptive names starting with `test_` or `debug_`
3. Add documentation to this README
4. Test that they run successfully with the PLua interpreter 