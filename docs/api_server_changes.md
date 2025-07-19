# API Server Changes in plua2

## Overview

The plua2 CLI has been updated to make the REST API server the default behavior, providing a more consistent and user-friendly experience.

## Changes Made

### 1. API Server is Now Default
- **Before**: API server was opt-in with `--api [port]`
- **After**: API server runs by default on port 8888

### 2. New CLI Arguments

#### `--noapi`
Disables the REST API server entirely.
```bash
plua2 --noapi script.lua          # Run without API server
plua2 --noapi                     # REPL without API server
```

#### `--api-port <port>`
Specifies a custom port for the API server (default: 8888).
```bash
plua2 --api-port 9000 script.lua  # API server on port 9000
plua2 --api-port 7777             # REPL with API on port 7777
```

#### `--cleanup-port`
Cleans up the API port and exits. Now automatically uses the configured API port.
```bash
plua2 --cleanup-port              # Clean up default port 8888
plua2 --api-port 9000 --cleanup-port  # Clean up port 9000
```

### 3. Updated Help and Examples

The help text now reflects the new default behavior:
```
Examples:
  plua2 script.lua                    # Run script.lua with API server
  plua2 --noapi script.lua            # Run script.lua without API server
  plua2 --api-port 9000 script.lua    # Run with API on port 9000
  plua2 --cleanup-port                # Clean up stuck API port
```

## Behavior Matrix

| Command | API Server | Port | REPL |
|---------|------------|------|------|
| `plua2` | ✅ Yes | 8888 | ✅ Yes |
| `plua2 --noapi` | ❌ No | - | ✅ Yes |
| `plua2 --api-port 9000` | ✅ Yes | 9000 | ✅ Yes |
| `plua2 script.lua` | ✅ Yes | 8888 | ❌ No |
| `plua2 --noapi script.lua` | ❌ No | - | ❌ No |
| `plua2 --api-port 9000 script.lua` | ✅ Yes | 9000 | ❌ No |

## Migration Guide

### For Users Who Want API Server (Most Users)
- **No changes needed** - API server now runs by default
- Use `--api-port <port>` instead of `--api <port>` for custom ports

### For Users Who Don't Want API Server
- Add `--noapi` flag to disable the API server
- Replace: `plua2 script.lua` → `plua2 --noapi script.lua`

### For Users Using `--cleanup-port`
- **No changes needed** - `--cleanup-port` now automatically uses the API port
- Use `--api-port <port> --cleanup-port` to clean up custom ports

## Examples

### Basic Usage
```bash
# Default: script with API server on port 8888
plua2 script.lua

# REPL with API server on port 8888
plua2

# Script without API server
plua2 --noapi script.lua

# REPL without API server
plua2 --noapi
```

### Custom Ports
```bash
# API server on port 9000
plua2 --api-port 9000 script.lua

# REPL with API on port 7777
plua2 --api-port 7777
```

### Combined with Other Flags
```bash
# Fibaro support with custom port
plua2 --fibaro --api-port 8890 script.lua

# Debug mode without API
plua2 --debug --noapi script.lua

# Fibaro + debugger + custom port
plua2 --fibaro --debugger --api-port 8889 script.lua
```

### Port Management
```bash
# Clean up default API port (8888)
plua2 --cleanup-port

# Clean up custom port
plua2 --api-port 9000 --cleanup-port
```

## Benefits

1. **Consistency**: API server is always available unless explicitly disabled
2. **Convenience**: No need to remember to add `--api` for most use cases
3. **Web REPL**: Interactive web interface available by default
4. **Fibaro Integration**: API endpoints work seamlessly with Fibaro support
5. **Port Management**: Simplified port cleanup process

The new default behavior makes plua2 more accessible while maintaining full flexibility for users who need different configurations.
