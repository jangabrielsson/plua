# File Organization Guidelines

## Keep It Clean

All development-related files should be organized in the `dev/` directory to keep the project root clean and focused.

## Top-Level Files (Keep Minimal)

The project root should only contain:
- **Core project files**: `pyproject.toml`, `README.md`, `LICENSE`, etc.
- **Frequently used utilities**: `run.sh` (used often for development)
- **Essential directories**: `src/`, `docs/`, `dev/`

## Development Files → dev/ Directory

All development and testing related files should go in `dev/`:

### Test Files
- `test_*.lua` - Lua test scripts
- `test_*.py` - Python test scripts  
- `test_*.sh` - Shell test scripts

### Debug and Development Scripts
- `debug_*.lua` - Debug and diagnostic scripts
- Development utilities and helpers
- Experimental code

### Generated or Temporary Files
- API generation scripts
- Documentation generation tools
- Build helpers

### Examples and Samples
- Example Lua scripts
- Sample configurations
- Demo applications

## Exception: run.sh

The `run.sh` script remains at the top level because:
- It's used frequently during development
- It's a primary entry point for VS Code integration
- It needs to be easily accessible from the project root

## Benefits

- **Clean project root**: Easy to understand what the project is about
- **Organized development**: All test/debug files in one place
- **Version control**: Easier to manage what gets committed
- **Documentation**: Clear separation between user docs and dev notes