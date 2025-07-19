# plua2 Development Tests

This directory contains internal development tests and examples that may use `_PY` functions or other internal APIs. These are not intended for end users but are useful for:

- Testing new features during development
- Integration testing of Python-Lua bridge
- Performance testing and benchmarking
- Debugging internal functionality

📝 **Note**: For development documentation, see [`docs/dev/`](../docs/dev/README.md)

## File Organization

All development and test files should be placed in this `dev/` directory to keep the project root clean. This includes:

- **Test scripts**: `test_*.lua`, `test_*.sh`
- **Debug utilities**: `debug_*.lua`
- **Development examples**: `*_example.lua`
- **Internal tools**: `generate_*.py`, utility scripts
- **Temporary test files**: Any experimental or one-off test files

**Do not** place test files in the project root - they should always go in `dev/` or `tests/` (for formal unit tests).

## Test Files

The test files in this directory may:
- Use `_PY` functions directly
- Test error conditions and edge cases
- Include debugging output and internal state inspection
- Require specific network services or test data

## Usage

These tests are primarily for plua2 developers and contributors. If you're looking for examples of how to use plua2 in your own projects, see the `examples/` directory instead.

For development documentation and implementation guides, see the [`docs/dev/`](../docs/dev/README.md) directory.

To run development tests:

```bash
plua2 dev/test_filename.lua
```

## Contributing

When adding new features to plua2:
1. Add comprehensive tests in this directory
2. Create clean, end-user examples in the `examples/` directory
3. Ensure tests cover both success and error cases
4. Document any special requirements or setup needed
