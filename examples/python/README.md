# Python Integration Examples

These examples show how to **embed and use EPLua from Python applications**.

## Python APIs

### Engine Management
```python
from src.eplua.engine import LuaEngine

# Create and configure engine
engine = LuaEngine()
engine.start()

# Execute Lua code
result = engine.execute_lua("return 1 + 2")
print(result)  # 3

# Call Lua functions
engine.execute_lua("function greet(name) return 'Hello ' .. name end")
result = engine.call_lua_function("greet", "World")
print(result)  # "Hello World"

# Cleanup
engine.stop()
```

### Extension Development
```python
# Add custom Python functions to Lua
from src.eplua.lua_bindings import export_to_lua

@export_to_lua("my_custom_function")
def my_function(arg1, arg2):
    return f"Python received: {arg1}, {arg2}"

# Now available in Lua as _PY.my_custom_function()
```

## Examples

### `basic_usage.py`
**Start here!** Shows how to:
- Create and manage EPLua engine
- Execute Lua scripts from Python
- Handle Lua return values
- Proper cleanup and error handling

### `custom_extensions.py`
Advanced integration:
- Adding custom Python functions to Lua
- Handling Lua callbacks from Python
- Type conversion between Python and Lua
- Creating custom Lua modules

## Use Cases

### 1. **Lua Scripting in Python Apps**
Add Lua scripting capabilities to your Python application:
```python
# Let users write custom scripts
user_script = """
  setTimeout(function()
    print("User script executed!")
  end, 1000)
"""
engine.execute_lua(user_script)
```

### 2. **Configuration Scripts**
Use Lua for complex configuration:
```python
# Load configuration from Lua
config_script = """
  return {
    server = { host = "localhost", port = 8080 },
    database = { url = "postgresql://..." },
    features = { enable_mqtt = true, enable_gui = false }
  }
"""
config = engine.execute_lua(config_script)
```

### 3. **Plugin Systems** 
Create pluggable architectures:
```python
# Load user plugins written in Lua
plugin_code = load_plugin_file("user_plugin.lua")
engine.execute_lua(plugin_code)

# Plugins can use full EPLua networking APIs
```

### 4. **Automation Scripts**
IoT and automation logic:
```python
# Run automation scripts with network access
automation_script = """
  local mqtt = net.MQTTClient()
  mqtt:connect("mqtt://broker.example.com")
  mqtt:publish("sensors/temperature", "23.5")
"""
engine.execute_lua(automation_script)
```

## Running Examples

```bash
# Basic usage
python examples/python/basic_usage.py

# Custom extensions
python examples/python/custom_extensions.py
```

## Engine Configuration

```python
# Configure engine features
engine = LuaEngine(
    enable_gui=True,      # Enable GUI functions
    enable_networking=True, # Enable network modules
    debug_mode=False,     # Disable debug output
    timeout=30.0          # Script timeout in seconds
)
```

## Thread Safety

The EPLua engine is **not thread-safe**. Use these patterns:

```python
# Option 1: One engine per thread
import threading

def worker():
    engine = LuaEngine()
    engine.start()
    # ... use engine ...
    engine.stop()

# Option 2: Queue-based communication
import queue
lua_queue = queue.Queue()
```

## Error Handling

```python
try:
    result = engine.execute_lua("invalid lua syntax")
except LuaError as e:
    print(f"Lua error: {e}")
except Exception as e:
    print(f"Engine error: {e}")
```

## Best Practices

1. **Always call `engine.stop()`** for proper cleanup
2. **Handle Lua errors gracefully** with try/catch
3. **Use one engine per thread** for thread safety
4. **Validate Lua code** before execution in production
5. **Set reasonable timeouts** for long-running scripts
