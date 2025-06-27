# PLua Architecture Documentation

## Overview

PLua is a Python-based Lua interpreter that uses the Lupa library to provide a Lua 5.4 environment with custom Python-extended functions. The system is built around an asyncio event loop architecture that enables true asynchronous operations while maintaining compatibility with Lua's synchronous programming model.

## Core Architecture

### High-Level System Architecture

```mermaid
graph TB
    subgraph "PLua Interpreter"
        A[PLuaInterpreter] --> B[LuaRuntime]
        A --> C[ExecutionTracker]
        A --> D[Extension Registry]
    end
    
    subgraph "Asyncio Event Loop"
        E[AsyncioLoopManager] --> F[Event Loop]
        F --> G[Network Manager]
        F --> H[Timer Manager]
        F --> I[Web Server]
    end
    
    subgraph "Lua Environment"
        B --> J[_PY Table]
        J --> K[Network Extensions]
        J --> L[Core Extensions]
        J --> M[Web Server Extensions]
    end
    
    subgraph "Threading Layer"
        N[Main Thread] --> O[Lua Execution Thread]
        N --> P[Background Threads]
    end
    
    A --> E
    G --> N
    H --> N
    I --> N
```

### Event Loop Management Architecture

```mermaid
sequenceDiagram
    participant Main as Main Thread
    participant LoopMgr as LoopManager
    participant EventLoop as Event Loop
    participant NetworkMgr as NetworkManager
    participant Lua as Lua Runtime
    
    Main->>LoopMgr: get_loop()
    LoopMgr->>EventLoop: new_event_loop()
    EventLoop-->>LoopMgr: loop instance
    LoopMgr-->>Main: loop instance
    
    Main->>NetworkMgr: tcp_connect(host, port, callback)
    NetworkMgr->>LoopMgr: create_task(coro)
    LoopMgr->>EventLoop: create_task()
    EventLoop-->>LoopMgr: task
    LoopMgr-->>NetworkMgr: task
    
    NetworkMgr->>EventLoop: await connection
    EventLoop-->>NetworkMgr: connection result
    NetworkMgr->>Lua: callback(result)
    Lua-->>Main: callback executed
```

## Asyncio Integration Strategy

### Threading Model

PLua uses a hybrid threading model to bridge Lua's synchronous execution with Python's asyncio:

```mermaid
graph LR
    subgraph "Main Thread"
        A[PLuaInterpreter] --> B[LuaRuntime]
        B --> C[Lua Code Execution]
    end
    
    subgraph "Event Loop Thread"
        D[AsyncioLoopManager] --> E[Event Loop]
        E --> F[Network Operations]
        E --> G[Timer Operations]
        E --> H[Web Server]
    end
    
    subgraph "Background Threads"
        I[HTTP Request Threads]
        J[Long-running Operations]
    end
    
    C -.->|Callback Registration| E
    E -.->|Callback Execution| C
    C -.->|Thread Pool| I
    I -.->|Result Queue| C
```

### Execution Phases

The system tracks execution phases to determine when to terminate:

```mermaid
stateDiagram-v2
    [*] --> Init: Start
    Init --> Fragments: -e commands
    Init --> Main: Direct file execution
    Init --> Interactive: -i flag
    
    Fragments --> Main: Complete fragments
    Main --> Tracking: Complete main
    Tracking --> [*]: No active operations
    
    Interactive --> [*]: User exit
    
    state Tracking {
        [*] --> CheckOperations
        CheckOperations --> WaitForStable: Operations active
        CheckOperations --> Terminate: No operations
        WaitForStable --> CheckOperations: Check again
        WaitForStable --> Terminate: Stable for 3 checks
    }
```

## Network Architecture

### TCP/UDP Connection Management

```mermaid
graph TB
    subgraph "Connection Pool"
        A[TCP Connections] --> B[Connection ID 1]
        A --> C[Connection ID 2]
        A --> D[Connection ID N]
        
        E[UDP Transports] --> F[Transport ID 1]
        E --> G[Transport ID 2]
        E --> H[Transport ID N]
    end
    
    subgraph "Network Manager"
        I[AsyncioNetworkManager] --> J[Connection Tracking]
        I --> K[Operation Counting]
        I --> L[Callback Management]
    end
    
    subgraph "Lua Interface"
        M[_PY.tcp_connect] --> N[Async Wrapper]
        O[_PY.tcp_connect_sync] --> P[Sync Wrapper]
        Q[_PY.udp_connect] --> R[Async Wrapper]
    end
    
    N --> I
    P --> I
    R --> I
    I --> A
    I --> E
```

### Network Operation Flow

```mermaid
sequenceDiagram
    participant Lua as Lua Code
    participant PY as _PY Table
    participant NetworkMgr as NetworkManager
    participant EventLoop as Event Loop
    participant Socket as Socket
    
    Lua->>PY: tcp_connect_sync(host, port)
    PY->>NetworkMgr: tcp_connect_sync()
    NetworkMgr->>Socket: socket.socket()
    NetworkMgr->>Socket: connect()
    Socket-->>NetworkMgr: connection
    NetworkMgr->>NetworkMgr: store_connection()
    NetworkMgr-->>PY: (success, conn_id, message)
    PY-->>Lua: (success, conn_id, message)
    
    Lua->>PY: tcp_write_sync(conn_id, data)
    PY->>NetworkMgr: tcp_write_sync()
    NetworkMgr->>Socket: send()
    Socket-->>NetworkMgr: bytes_sent
    NetworkMgr-->>PY: (success, bytes_sent, message)
    PY-->>Lua: (success, bytes_sent, message)
```

## Timer Architecture

### Timer Management System

```mermaid
graph TB
    subgraph "Timer Registry"
        A[Timer Manager] --> B[Active Timers]
        A --> C[Active Intervals]
        A --> D[Timer ID Counter]
    end
    
    subgraph "Event Loop Integration"
        E[Event Loop] --> F[Timer Tasks]
        F --> G[setTimeout Tasks]
        F --> H[setInterval Tasks]
    end
    
    subgraph "Lua Interface"
        I[_PY.setTimeout] --> J[Timer Creation]
        K[_PY.setInterval] --> L[Interval Creation]
        M[_PY.clearTimeout] --> N[Timer Cancellation]
        O[_PY.clearInterval] --> P[Interval Cancellation]
    end
    
    J --> A
    L --> A
    N --> A
    P --> A
    A --> E
```

## Extension System Architecture

### Extension Registration and Discovery

```mermaid
graph TB
    subgraph "Extension Registry"
        A[Registry] --> B[Core Extensions]
        A --> C[Network Extensions]
        A --> D[Web Server Extensions]
        A --> E[HTML Extensions]
    end
    
    subgraph "Registration Process"
        F[Registry.register] --> G[Function Registration]
        G --> H[Category Assignment]
        H --> I[Description Storage]
    end
    
    subgraph "Lua Integration"
        J[get_lua_extensions] --> K[Extension Collection]
        K --> L[_PY Table Creation]
        L --> M[Lua Environment]
    end
    
    F --> A
    A --> J
    J --> M
```

### Extension Function Flow

```mermaid
sequenceDiagram
    participant Lua as Lua Code
    participant PY as _PY Table
    participant Registry as Extension Registry
    participant Python as Python Function
    participant EventLoop as Event Loop
    
    Lua->>PY: _PY.tcp_connect(host, port, callback)
    PY->>Registry: Lookup function
    Registry-->>PY: Function reference
    PY->>Python: tcp_connect(host, port, callback)
    Python->>EventLoop: Schedule async operation
    EventLoop->>Python: Execute operation
    Python->>Lua: Execute callback
    Lua-->>Lua: Handle result
```

## Termination Detection

### Smart Shutdown Architecture

```mermaid
graph TB
    subgraph "Execution Tracker"
        A[ExecutionTracker] --> B[Phase Tracking]
        A --> C[Operation Counting]
        A --> D[Stability Detection]
    end
    
    subgraph "Active Operations"
        E[Network Operations] --> F[TCP Connections]
        E --> G[UDP Transports]
        E --> H[HTTP Requests]
        
        I[Timer Operations] --> J[Active Timers]
        I --> K[Active Intervals]
        
        L[Web Server] --> M[Server Status]
    end
    
    subgraph "Termination Logic"
        N[should_terminate] --> O[Check Phase]
        N --> P[Check Operations]
        N --> Q[Check Stability]
        N --> R[Check Web Server]
    end
    
    B --> N
    C --> N
    D --> N
    E --> C
    I --> C
    L --> C
```

### Termination Flow

```mermaid
sequenceDiagram
    participant Main as Main Thread
    participant Tracker as ExecutionTracker
    participant NetworkMgr as NetworkManager
    participant EventLoop as Event Loop
    participant Lua as Lua Runtime
    
    Main->>Tracker: complete_main()
    Tracker->>Tracker: start_tracking()
    
    loop Termination Check
        Main->>Tracker: should_terminate()
        Tracker->>NetworkMgr: has_active_operations()
        NetworkMgr-->>Tracker: operation_count
        Tracker->>EventLoop: get_pending_tasks()
        EventLoop-->>Tracker: task_count
        Tracker->>Tracker: check_stability()
        
        alt No operations and stable
            Tracker-->>Main: true (terminate)
            Main->>EventLoop: shutdown()
            EventLoop->>NetworkMgr: force_cleanup()
            Main->>Lua: exit
        else Operations active or unstable
            Tracker-->>Main: false (continue)
            Main->>Main: wait(100ms)
        end
    end
```

## Web Server Architecture

### Web Server Integration

```mermaid
graph TB
    subgraph "Web Server"
        A[WebServer Extension] --> B[HTTP Server]
        B --> C[Request Handlers]
        B --> D[Static File Serving]
        B --> E[Lua Route Handlers]
    end
    
    subgraph "Event Loop Integration"
        F[Event Loop] --> G[Server Task]
        G --> H[Request Processing]
        H --> I[Response Generation]
    end
    
    subgraph "Lua Interface"
        J[_PY.start_web_server] --> K[Server Startup]
        L[_PY.stop_web_server] --> M[Server Shutdown]
        N[_PY.add_route] --> O[Route Registration]
    end
    
    K --> A
    M --> A
    O --> A
    A --> F
```

## Debugging Architecture

### MobDebug Integration

```mermaid
graph TB
    subgraph "Debugger System"
        A[MobDebug] --> B[Debug Server]
        B --> C[Breakpoint Management]
        B --> D[Variable Inspection]
        B --> E[Step Execution]
    end
    
    subgraph "Lua Integration"
        F[require.mobdebug] --> G[MobDebug Module]
        G --> H[mobdebug.start]
        H --> I[Server Startup]
    end
    
    subgraph "VS Code Integration"
        J[VS Code Debugger] --> K[Debug Adapter]
        K --> L[Debug Protocol]
        L --> B
    end
    
    I --> B
    B --> L
```

## Key Design Principles

### 1. Thread Safety
- Lua execution happens in the main thread
- Asyncio operations run in the event loop thread
- Callbacks are executed in the main thread via `call_soon()`
- Background operations use thread pools for CPU-intensive tasks

### 2. Graceful Termination
- Smart detection of active operations
- Stability checking to avoid premature termination
- Force cleanup when timeout is reached
- Proper event loop shutdown

### 3. Extension System
- Registry-based function discovery
- Category-based organization
- Automatic Lua table creation
- Support for both sync and async operations

### 4. Error Handling
- Comprehensive exception handling in all layers
- Graceful degradation for network failures
- Proper cleanup on errors
- Debug output for troubleshooting

## Performance Considerations

### Event Loop Efficiency
- Single event loop per process
- Efficient task scheduling
- Minimal overhead for callback execution
- Proper resource cleanup

### Memory Management
- Connection pooling for network operations
- Automatic cleanup of completed operations
- Proper Lua object lifecycle management
- Memory leak prevention through proper shutdown

### Scalability
- Support for multiple concurrent connections
- Efficient timer management
- Background thread pools for heavy operations
- Web server with async request handling

## Future Enhancements

### Planned Improvements
1. **Connection Pooling**: Implement connection reuse for HTTP requests
2. **Streaming Support**: Add support for streaming network operations
3. **WebSocket Support**: Native WebSocket client and server
4. **Database Extensions**: Add database connectivity extensions
5. **Plugin System**: Allow third-party extension development
6. **Performance Profiling**: Built-in performance monitoring
7. **Distributed Tracing**: Support for distributed operation tracing

### Architecture Evolution
- Maintain backward compatibility
- Incremental feature additions
- Performance optimization
- Enhanced debugging capabilities
- Better error reporting and recovery

## Single-Process, Embedded API Server

- The FastAPI server is now always started and managed by the PLua interpreter itself (embedded).
- There is no registration, coordination, or separate process for the API server.
- All communication between the web interface and the interpreter is in-process.
- To use the system, always start with `python plua.py` or your main entrypoint. 