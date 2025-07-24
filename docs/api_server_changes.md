# API Server Changes in plua

## Overview

The plua CLI has been updated to make the REST API server the default behavior, providing a more consistent and user-friendly experience.

## Changes Made

### 1. API Server is Now Default
- **Before**: API server was opt-in with `--api [port]`
- **After**: API server runs by default on port 8888

### 2. New CLI Arguments

#### `--noapi`
Disables the REST API server entirely.
```bash
plua --noapi script.lua          # Run without API server
plua --noapi                     # REPL without API server
```

#### `--api-port <port>`
Specifies a custom port for the API server (default: 8888).
```bash
plua --api-port 9000 script.lua  # API server on port 9000
plua --api-port 7777             # REPL with API on port 7777
```

#### `--cleanup-port`
Cleans up the API port and exits. Now automatically uses the configured API port.
```bash
plua --cleanup-port              # Clean up default port 8888
plua --api-port 9000 --cleanup-port  # Clean up port 9000
```

### 3. Updated Help and Examples

The help text now reflects the new default behavior:
```
Examples:
  plua script.lua                    # Run script.lua with API server
  plua --noapi script.lua            # Run script.lua without API server
  plua --api-port 9000 script.lua    # Run with API on port 9000
  plua --cleanup-port                # Clean up stuck API port
```

## Behavior Matrix

| Command | API Server | Port | REPL |
|---------|------------|------|------|
| `plua` | ✅ Yes | 8888 | ✅ Yes |
| `plua --noapi` | ❌ No | - | ✅ Yes |
| `plua --api-port 9000` | ✅ Yes | 9000 | ✅ Yes |
| `plua script.lua` | ✅ Yes | 8888 | ❌ No |
| `plua --noapi script.lua` | ❌ No | - | ❌ No |
| `plua --api-port 9000 script.lua` | ✅ Yes | 9000 | ❌ No |

## Migration Guide

### For Users Who Want API Server (Most Users)
- **No changes needed** - API server now runs by default
- Use `--api-port <port>` instead of `--api <port>` for custom ports

### For Users Who Don't Want API Server
- Add `--noapi` flag to disable the API server
- Replace: `plua script.lua` → `plua --noapi script.lua`

### For Users Using `--cleanup-port`
- **No changes needed** - `--cleanup-port` now automatically uses the API port
- Use `--api-port <port> --cleanup-port` to clean up custom ports

## Examples

### Basic Usage
```bash
# Default: script with API server on port 8888
plua script.lua

# REPL with API server on port 8888
plua

# Script without API server
plua --noapi script.lua

# REPL without API server
plua --noapi
```

### Custom Ports
```bash
# API server on port 9000
plua --api-port 9000 script.lua

# REPL with API on port 7777
plua --api-port 7777
```

### Combined with Other Flags
```bash
# Fibaro support with custom port
plua --fibaro --api-port 8890 script.lua

# Debug mode without API
plua --debug --noapi script.lua

# Fibaro + debugger + custom port
plua --fibaro --debugger --api-port 8889 script.lua
```

### Port Management
```bash
# Clean up default API port (8888)
plua --cleanup-port

# Clean up custom port
plua --api-port 9000 --cleanup-port
```

## Benefits

1. **Consistency**: API server is always available unless explicitly disabled
2. **Convenience**: No need to remember to add `--api` for most use cases
3. **Web REPL**: Interactive web interface available by default
4. **Fibaro Integration**: API endpoints work seamlessly with Fibaro support
5. **Port Management**: Simplified port cleanup process

The new default behavior makes plua more accessible while maintaining full flexibility for users who need different configurations.
