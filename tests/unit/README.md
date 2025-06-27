# PLua Test Suite

This directory contains comprehensive tests for the PLua interpreter and its extensions.

## Test Structure

- `conftest.py` - Pytest configuration and common fixtures
- `test_core_extensions.py` - Tests for core extensions (timers, I/O, system functions)
- `test_network_extensions.py` - Tests for network extensions (TCP, UDP, HTTP)
- `test_plua_interpreter.py` - Tests for the main PLua interpreter

## Running Tests

### Prerequisites

Install the development dependencies:

```bash
pip install -e ".[dev]"
```

Or if using uv:

```bash
uv sync --extra dev
```

### Run All Tests

```bash
pytest
```

### Run Specific Test Files

```bash
pytest tests/test_core_extensions.py
pytest tests/test_network_extensions.py
pytest tests/test_plua_interpreter.py
```

### Run Tests with Coverage

```bash
pytest --cov=plua --cov=extensions
```

### Run Tests with Verbose Output

```bash
pytest -v
```

### Run Only Fast Tests (Exclude Slow Tests)

```bash
pytest -m "not slow"
```

### Run Only Unit Tests

```bash
pytest -m "unit"
```

### Run Only Integration Tests

```bash
pytest -m "integration"
```

## Test Categories

### Unit Tests (`@pytest.mark.unit`)
- Fast, isolated tests that don't require external dependencies
- Test individual functions and methods
- Use mocks for external dependencies

### Integration Tests (`@pytest.mark.integration`)
- Tests that verify components work together
- May require network access or external services
- Test real file I/O and network operations

### Slow Tests (`@pytest.mark.slow`)
- Tests that take longer to run (e.g., timer tests, network timeouts)
- May be excluded in CI/CD pipelines for faster feedback

## Test Fixtures

The test suite provides several useful fixtures:

- `lua_interpreter` - Fresh PLua interpreter instance
- `debug_lua_interpreter` - PLua interpreter with debug enabled
- `temp_file` - Temporary file that gets cleaned up
- `temp_dir` - Temporary directory that gets cleaned up
- `sample_lua_file` - Sample Lua file for testing
- `error_lua_file` - Lua file with syntax errors

## Writing Tests

### Basic Test Structure

```python
def test_function_name(lua_interpreter):
    """Test description"""
    lua_code = """
    -- Lua code to test
    local result = _PY.some_function()
    _G.test_result = result
    """
    
    lua_interpreter.lua_runtime.globals()['result'] = []
    lua_interpreter.execute_code(lua_code)
    
    # Assertions
    assert result[1] == expected_value
```

### Testing with Mocks

```python
@patch('builtins.input')
def test_input_function(mock_input, lua_interpreter):
    """Test input function with mock"""
    mock_input.return_value = "test input"
    
    lua_code = """
    local user_input = _PY.input_lua("Enter something: ")
    result[1] = user_input
    """
    
    result = []
    lua_interpreter.lua_runtime.globals()['result'] = result
    lua_interpreter.execute_code(lua_code)
    
    assert result[1] == "test input"
    mock_input.assert_called_once_with("Enter something: ")
```

### Testing Network Functions

```python
def test_tcp_connection(lua_interpreter):
    """Test TCP connection with real server"""
    # Create test server
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('localhost', 0))
    server_socket.listen(1)
    port = server_socket.getsockname()[1]
    
    try:
        lua_code = f"""
        local success, conn_id, message = _PY.tcp_connect_sync("localhost", {port})
        result[1] = success
        """
        
        result = []
        lua_interpreter.lua_runtime.globals()['result'] = result
        lua_interpreter.execute_code(lua_code)
        
        assert result[1] is True
    finally:
        server_socket.close()
```

## Continuous Integration

The test suite is designed to work with CI/CD pipelines:

- Fast unit tests run on every commit
- Integration tests run on pull requests
- Slow tests run on scheduled builds
- Coverage reports are generated automatically

## Debugging Tests

### Enable Debug Output

```bash
pytest -s --log-cli-level=DEBUG
```

### Run Single Test

```bash
pytest tests/test_core_extensions.py::TestTimerExtensions::test_setTimeout_basic -v -s
```

### Use PDB Debugger

```bash
pytest --pdb
```

## Test Coverage

The test suite aims to cover:

- [x] Core extensions (timers, I/O, system functions)
- [x] Network extensions (TCP, UDP, HTTP)
- [x] Main interpreter functionality
- [x] Error handling
- [x] Lua environment setup
- [x] File operations
- [x] Library loading
- [x] Interactive mode

## Contributing

When adding new features to PLua:

1. Write tests first (TDD approach)
2. Ensure all tests pass
3. Add appropriate test markers
4. Update this README if needed
5. Run the full test suite before submitting PRs 