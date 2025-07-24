# Simplified main_file_hook System

## Overview

The `main_file_hook` system has been simplified to provide a cleaner, more flexible architecture for file loading and preprocessing in plua.

## Architecture

### Default Implementation (init.lua)
- `init.lua` now provides a default `_PY.main_file_hook` implementation
- The default behavior simply loads and executes Lua files in coroutines
- No preprocessing is applied by default

### Override Capability
- Libraries can override `_PY.main_file_hook` to provide custom behavior
- Examples: preprocessing, syntax transformation, custom module loading
- The hook function signature: `function(filename) -> void`

### Simplified Interpreter Logic
- `interpreter.execute_file()` always calls the hook (no fallback logic needed)
- Much cleaner and more predictable code path
- Consistent behavior across all file loading scenarios

## Implementation Details

### init.lua Default Hook
```lua
function _PY.main_file_hook(filename)
    print("Loading file: " .. filename)
    
    local file = io.open(filename, "r")
    if not file then
        error("Cannot open file: " .. filename)
    end
    
    local content = file:read("*all")
    file:close()
    
    local func, err = load(content, "@" .. filename)
    if func then
        coroutine.wrap(func)()
    else
        error("Failed to load script: " .. tostring(err))
    end
end
```

### Fibaro Override Example
```lua
function _PY.main_file_hook(filename)
    print("Fibaro main_file_hook called with: " .. filename)
    
    local file = io.open(filename, "r")
    if not file then
        error("Cannot open file: " .. filename)
    end
    
    local content = file:read("*all")
    file:close()
    
    -- Add Fibaro-specific preprocessing
    local preprocessed = [[
-- Fibaro API preprocessing applied
print("File preprocessed by Fibaro hook: ]] .. filename .. [[")
]] .. content
    
    local func, err = load(preprocessed, "@" .. filename)
    if func then
        coroutine.wrap(func)()
    else
        error("Failed to load preprocessed script: " .. tostring(err))
    end
end
```

### Simplified Python Code
```python
def execute_file(self, filepath: str, debugging: bool = False, debug: bool = False) -> None:
    """Execute a Lua file using the main_file_hook"""
    if not self.lua:
        raise RuntimeError("Lua runtime not initialized. Call initialize() first.")
    
    self.debug_print(f"Executing file: {filepath}")
    
    # Always use the main_file_hook (which has a default implementation in init.lua)
    try:
        self.PY.main_file_hook(filepath)
    except Exception as e:
        raise RuntimeError(f"main_file_hook failed for {filepath}: {e}")
```

## Benefits

### Consistency
- All file loading goes through the same code path
- Predictable behavior regardless of use case
- No branching logic in the interpreter

### Flexibility
- Libraries can easily override the hook for custom behavior
- Multiple libraries can chain hooks if needed
- Hook can be changed at runtime

### Simplicity
- Much cleaner interpreter code
- Easier to understand and maintain
- Fewer edge cases to handle

### Extensibility
- Easy to add new preprocessing features
- Libraries can provide their own file loading logic
- Custom syntax transformations possible

## Usage Examples

### Basic File Loading
```bash
# Uses default hook (simple loading)
python -m src.plua.main script.lua
```

### With Fibaro Preprocessing
```bash
# Load fibaro.lua first to override the hook, then load main script
python -m src.plua.main -e 'dofile("fibaro.lua")' main_script.lua
```

### Direct Library Loading
```bash
# fibaro.lua overrides the hook when it's loaded
python -m src.plua.main fibaro.lua
```

## Testing

### Test Results
- ✅ Default hook works correctly (simple file loading)
- ✅ Fibaro override works correctly (preprocessing applied)
- ✅ No performance or functionality regressions
- ✅ Cleaner, more maintainable code

### Test Commands
```bash
# Run comprehensive hook tests
./test_main_file_hook.sh

# Individual tests
python -m src.plua.main test_hook.lua --duration 2
python -m src.plua.main -e 'dofile("fibaro.lua")' test_hook.lua --duration 2
```

## Future Enhancements

### Possible Extensions
- **Hook chaining**: Allow multiple hooks to process files in sequence
- **Conditional preprocessing**: Apply different preprocessing based on file patterns
- **Module system**: Advanced module loading with dependency resolution
- **Source maps**: Better debugging support for preprocessed files

### Integration Opportunities
- **TypeScript support**: Transpile TypeScript-like syntax to Lua
- **Template systems**: Support for Lua template engines
- **Package managers**: Integration with external package systems
- **IDE support**: Better development tooling integration

## Conclusion

The simplified `main_file_hook` system provides a much cleaner and more flexible foundation for file loading in plua. The default implementation handles standard use cases, while libraries like Fibaro can easily override the hook to provide custom preprocessing without complicating the core interpreter logic.
