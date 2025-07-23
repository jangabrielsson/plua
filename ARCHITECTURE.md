# plua2 Architecture

plua2 is a Python-Lua async runtime that bridges Python's asyncio with Lua's coroutines, providing JavaScript-like timers and async operations. This document outlines the core architecture, components, and subsystems.

## 📋 Table of Contents

- [Overview](#overview)
- [Core Architecture](#core-architecture)
- [Component Details](#component-details)
- [Data Flow](#data-flow)
- [Fibaro Integration](#fibaro-integration)
- [Development Patterns](#development-patterns)

## 🏗️ Overview

plua2 can be thought of as "Node.js for Lua" with Python as the runtime. It provides:

- **Async Lua Runtime**: Coroutine-based async operations
- **JavaScript-style Timers**: `setTimeout`, `clearTimeout`, `setInterval`
- **Network Layer**: HTTP, TCP, UDP, WebSocket support
- **Web Interface**: Browser-based REPL and development tools
- **REST API**: HTTP endpoints for external integration
- **Fibaro HC3 Emulation**: Complete HC3 API compatibility

## 🔧 Core Architecture

```mermaid
graph TB
    subgraph "Python Runtime Layer"
        A[LuaAsyncRuntime] --> B[LuaInterpreter]
        B --> C[lupa - Python-Lua Bridge]
        A --> D[asyncio Event Loop]
        A --> E[Timer Management]
        A --> F[Callback Queue]
    end
    
    subgraph "Lua Environment"
        G[init.lua - Core Runtime]
        H[_PY Bridge Table]
        I[PLUA Utility Functions]
        J[Timer Functions]
        K[Network Modules]
        L[User Scripts]
    end
    
    subgraph "Network Layer"
        M[HTTPClient/Server]
        N[TCP/UDP Sockets]
        O[WebSocket Support]
        P[Async Network Handler]
    end
    
    subgraph "Interface Layer"
        Q[CLI REPL]
        R[Web UI/REPL]
        S[FastAPI REST Server]
        T[Static File Server]
    end
    
    subgraph "Fibaro Integration"
        U[fibaro_api_endpoints.py]
        V[Auto-generated HC3 APIs]
        W[fibaro.lua Runtime]
        X[QuickApp Support]
    end
    
    C --> H
    H --> G
    A --> M
    A --> Q
    A --> S
    S --> R
    U --> S
    W --> U
    
    style A fill:#ff9999
    style B fill:#99ccff
    style G fill:#99ff99
    style S fill:#ffcc99
    style U fill:#cc99ff
```

## 🧩 Component Details

### 1. Python Runtime Core

#### LuaAsyncRuntime (`src/plua2/runtime.py`)
- **Role**: Main async event loop coordinator
- **Responsibilities**:
  - Manages asyncio event loop
  - Coordinates timer execution
  - Handles async callback processing
  - Provides runtime state management

#### LuaInterpreter (`src/plua2/interpreter.py`)
- **Role**: Lua runtime wrapper with Python bridge
- **Responsibilities**:
  - Wraps lupa Lua state
  - Manages `_PY` bridge table
  - Handles Lua code execution
  - Provides error handling and debugging

```mermaid
sequenceDiagram
    participant User
    participant Runtime as LuaAsyncRuntime
    participant Interpreter as LuaInterpreter
    participant Lua as Lua State
    participant Python as Python Functions
    
    User->>Runtime: Execute Lua Script
    Runtime->>Interpreter: load_and_execute()
    Interpreter->>Lua: Load init.lua
    Lua->>Python: Call _PY.setTimeout()
    Python->>Runtime: Schedule async timer
    Runtime->>Runtime: Timer expires
    Runtime->>Interpreter: Execute callback
    Interpreter->>Lua: Run Lua function
    Lua-->>User: Output/Results
```

### 2. The _PY Bridge System

The `_PY` table is the central communication mechanism between Python and Lua:

```lua
-- Core bridge functions
_PY.setTimeout(callback, delay_ms)    -- Timer creation
_PY.clearTimeout(timer_id)           -- Timer cancellation
_PY.json_encode(data)                -- JSON serialization
_PY.json_decode(string)              -- JSON parsing
_PY.getRuntimeState()                -- Runtime introspection

-- Hook system for customization
_PY.main_file_hook = function(filename) end      -- File preprocessing
_PY.fibaro_api_hook = function(method, path, data) end  -- API delegation
_PY.isRunning = function() return true end       -- Auto-termination
```

#### Function Export Pattern
Python functions are exported using the `@lua_exporter` decorator:

```python
@lua_exporter
def my_function(arg1, arg2):
    """Function exposed to Lua as _PY.my_function"""
    return result
```

### 3. Async Timer Architecture

plua2 implements a producer-consumer pattern for timer management:

```mermaid
graph LR
    subgraph "Timer Creation (Lua)"
        A[setTimeout call] --> B[_PY.setTimeout]
        B --> C[Python Timer Task]
    end
    
    subgraph "Timer Execution (Python)"
        C --> D[asyncio.sleep]
        D --> E[Callback Queue]
    end
    
    subgraph "Callback Processing (Lua)"
        E --> F[run_timer_callbacks_loop]
        F --> G[Execute Lua Function]
        G --> H[Main Thread Safety]
    end
    
    style C fill:#ff9999
    style E fill:#99ccff
    style G fill:#99ff99
```

**Key Design Principles:**
1. **Thread Safety**: All Lua execution happens in the main thread
2. **Async Coordination**: Python asyncio manages timer scheduling
3. **Callback Queue**: Decouples timer expiration from Lua execution
4. **Resource Management**: Automatic cleanup of expired timers

### 4. Network Layer

The network subsystem provides async networking with Fibaro HC3 compatibility:

```mermaid
graph TB
    subgraph "Lua Network API"
        A[net.HTTPClient] --> B[HTTP Requests]
        C[net.TCPSocket] --> D[TCP Connections]
        E[net.UDPSocket] --> F[UDP Communication]
        G[net.WebSocket] --> H[WebSocket Connections]
    end
    
    subgraph "Python Network Backend"
        I[syncsocket.py] --> J[Synchronous Socket Ops]
        K[Async HTTP Client] --> L[aiohttp Integration]
        M[Network Utils] --> N[Protocol Handling]
    end
    
    subgraph "Callback System"
        O[Success Callbacks]
        P[Error Callbacks]
        Q[Data Callbacks]
    end
    
    B --> K
    D --> I
    F --> I
    H --> I
    
    K --> O
    I --> P
    L --> Q
    
    style I fill:#ff9999
    style O fill:#99ff99
```

### 5. Web Interface and REST API

plua2 provides multiple interfaces for interaction:

```mermaid
graph TB
    subgraph "User Interfaces"
        A[CLI REPL] --> B[Terminal Input/Output]
        C[Web REPL] --> D[Browser Interface]
        E[VS Code Integration] --> F[Editor Integration]
    end
    
    subgraph "FastAPI Server"
        G[REST API Endpoints]
        H[Static File Server]
        I[WebSocket REPL]
        J[Fibaro API Emulation]
    end
    
    subgraph "Shared State"
        K[LuaInterpreter Instance]
        L[Runtime State]
        M[Timer Management]
    end
    
    A --> K
    C --> I
    I --> K
    G --> K
    
    H --> C
    J --> G
    
    K --> L
    K --> M
    
    style G fill:#ffcc99
    style K fill:#99ccff
    style I fill:#99ff99
```

#### API Server Structure (`api_server.py`)
- **FastAPI Application**: Modern async web framework
- **Static File Serving**: Web UI assets from `/static/` directory
- **WebSocket REPL**: Real-time Lua interaction
- **Shared Interpreter**: Same Lua state across CLI and web interfaces

### 6. Fibaro HC3 Integration

The `--fibaro` flag enables comprehensive Fibaro Home Center 3 emulation:

```mermaid
graph TB
    subgraph "Fibaro API Layer"
        A[194 Auto-generated Endpoints] --> B[fibaro_api_endpoints.py]
        C[Swagger/OpenAPI Specs] --> A
        D[generate_fibaro_api.py] --> A
    end
    
    subgraph "Lua Fibaro Runtime"
        E[fibaro.lua] --> F[HC3 API Functions]
        G[QuickApp Classes] --> F
        H[Scene Support] --> F
    end
    
    subgraph "API Delegation"
        I[_PY.fibaro_api_hook] --> J[Method Routing]
        J --> K[Default 503 Response]
        J --> L[fibaro.lua Handler]
    end
    
    subgraph "VS Code Integration"
        M[HC3 Upload Tasks] --> N[QuickApp Development]
        O[Project Management] --> N
    end
    
    B --> I
    F --> L
    L --> B
    
    style B fill:#cc99ff
    style F fill:#99ff99
    style I fill:#ffcc99
```

#### Fibaro Integration Flow

1. **Endpoint Generation**: `generate_fibaro_api.py` processes Swagger specs
2. **API Registration**: 194 endpoints automatically registered with FastAPI
3. **Hook System**: `_PY.fibaro_api_hook` handles all API calls
4. **Default Behavior**: Returns 503 "Service Unavailable" unless overridden
5. **fibaro.lua Override**: Provides actual HC3 functionality when loaded

## 🔄 Data Flow

### Script Execution Flow

```mermaid
sequenceDiagram
    participant CLI as CLI/Web UI
    participant Runtime as LuaAsyncRuntime
    participant Interpreter as LuaInterpreter
    participant Init as init.lua
    participant Script as User Script
    participant Timers as Timer System
    
    CLI->>Runtime: Execute script.lua
    Runtime->>Interpreter: Initialize Lua state
    Interpreter->>Init: Load runtime environment
    Init->>Init: Setup _PY bridge, timers, modules
    Interpreter->>Script: Execute user script
    Script->>Timers: setTimeout(callback, 1000)
    Timers->>Runtime: Schedule async timer
    Runtime->>Runtime: Timer expires after 1000ms
    Runtime->>Interpreter: Execute callback
    Interpreter->>Script: Run callback function
    Script-->>CLI: Output results
```

### Network Request Flow

```mermaid
sequenceDiagram
    participant Lua as Lua Script
    participant Net as net.HTTPClient
    participant Python as Python Backend
    participant External as External API
    
    Lua->>Net: http:request(url, callbacks)
    Net->>Python: _PY.http_request_async()
    Python->>Python: Create asyncio task
    Python->>External: HTTP request
    External-->>Python: HTTP response
    Python->>Python: Queue callback
    Python->>Lua: Execute success callback
    Lua->>Lua: Process response data
```

## 🏠 Fibaro Integration Architecture

### HC3 API Emulation

```mermaid
graph TB
    subgraph "HC3 Compatibility Layer"
        A[fibaro Global Object] --> B[API Methods]
        C[QuickApp Base Class] --> D[Device Simulation]
        E[Scene Functions] --> F[Home Automation Logic]
    end
    
    subgraph "API Endpoint Mapping"
        G["/api/devices/{id}"] --> H[Device Management]
        I["/api/quickApps/{id}"] --> J[QuickApp Management]
        K["/api/scenes/{id}"] --> L[Scene Control]
        M["/api/globalVariables"] --> N[Variable Storage]
    end
    
    subgraph "VS Code Development"
        O[.project Files] --> P[Multi-file QuickApps]
        Q[Upload Tasks] --> R[HC3 Deployment]
        S[Live Development] --> T[Hot Reload]
    end
    
    B --> H
    D --> J
    F --> L
    
    P --> Q
    R --> H
    
    style A fill:#cc99ff
    style O fill:#99ff99
    style G fill:#ffcc99
```

### QuickApp Development Workflow

1. **Development**: Write QuickApp in VS Code with plua2
2. **Testing**: Use `--fibaro` flag for HC3 API emulation
3. **Upload**: VS Code tasks upload to real HC3 system
4. **Debugging**: plua2 provides debugging capabilities

## 🛠️ Development Patterns

### Module Registration Pattern
```python
from plua2.luafuns_lib import lua_exporter

@lua_exporter
def my_utility_function(param1, param2):
    """Exposed to Lua as _PY.my_utility_function"""
    # Implementation
    return result
```

### Hook Override Pattern
```lua
-- Custom file preprocessing
function _PY.main_file_hook(filename)
    print("Loading:", filename)
    -- Custom logic here
    -- Call original implementation or custom loading
end

-- Custom API handling
function _PY.fibaro_api_hook(method, path, data)
    if path:match("^/api/devices") then
        -- Handle device API calls
        return custom_device_handler(method, path, data)
    end
    -- Return nil, 503 for unhandled paths
    return nil, 503
end
```

### Error Handling Pattern
```lua
-- Async operations with error handling
local client = net.HTTPClient()
client:request("https://api.example.com/data", {
    success = function(response)
        print("Success:", response.data)
    end,
    error = function(err)
        print("Error:", err)
        -- Fallback logic
    end
})
```

## 🚀 Startup Sequence

```mermaid
sequenceDiagram
    participant CLI as plua2 CLI
    participant Runtime as LuaAsyncRuntime
    participant API as FastAPI Server
    participant Lua as Lua Environment
    participant Script as User Script
    
    CLI->>Runtime: Initialize with config
    Runtime->>API: Start FastAPI server (port 8888)
    Runtime->>Lua: Create LuaInterpreter
    Lua->>Lua: Load init.lua (timers, _PY bridge)
    
    alt Fibaro flag enabled
        Runtime->>API: Register 194 Fibaro endpoints
        Lua->>Lua: Set up fibaro API hooks
    end
    
    alt Script provided
        Runtime->>Lua: Execute user script
        Script->>Script: Run application logic
    else Interactive mode
        Runtime->>CLI: Start REPL loop
    end
    
    API-->>CLI: Web interface available
    Runtime->>Runtime: Run event loop until termination
```

## 📊 Performance Considerations

### Timer Performance
- **Callback Queue**: Prevents blocking the main thread
- **Batch Processing**: Multiple callbacks processed per loop iteration
- **Resource Cleanup**: Automatic cleanup of expired timers

### Memory Management
- **Lua GC**: Standard Lua garbage collection
- **Python References**: Careful management of Python-Lua object references
- **Callback Cleanup**: Non-persistent callbacks automatically removed

### Network Performance
- **Async I/O**: Non-blocking network operations
- **Connection Pooling**: Reuse of HTTP connections where possible
- **Error Recovery**: Graceful handling of network failures

## 🔧 Configuration and Extensibility

### Runtime Configuration
```python
# Example configuration options
config = {
    "api_port": 8888,
    "debug": False,
    "fibaro_enabled": True,
    "auto_termination": False,
    "duration": None  # Auto-termination time
}
```

### Extension Points
1. **Custom _PY Functions**: Add new Python functions via `@lua_exporter`
2. **Hook Overrides**: Customize file loading and API handling
3. **Module System**: Add new Lua modules via `require()`
4. **API Endpoints**: Extend FastAPI server with custom endpoints

This architecture provides a robust, extensible foundation for async Lua development with comprehensive HC3 compatibility and modern web-based development tools.
