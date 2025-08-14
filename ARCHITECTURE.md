# PLua Architecture

EPLua is a Python-based Lua execution engine with native UI support, async timers, Fibaro QuickApp emulation, and multiple communication interfaces. This document describes the system architecture, threading model, and component interactions.

## System Overview

EPLua consists of several key components that work together to provide a rich Lua execution environment:

- **Lua Engine**: Core script execution with async timer support
- **GUI System**: Native tkinter-based UI with thread-safe bridge
- **QuickApp System**: Browser-based Fibaro QuickApp emulation with real-time updates
- **Web Server**: FastAPI-based HTTP API with WebSocket support for remote control
- **Telnet Server**: Async REPL interface for interactive debugging
- **REPL Client**: Enhanced command-line interface with history and completion

## Threading Architecture

EPLua uses a multi-threaded architecture to separate concerns and provide responsive UI:

```mermaid
graph TB
    subgraph "Main Process"
        subgraph "Main Thread"
            CLI[CLI Entry Point]
            GUI[GUI Manager]
            GUI_BRIDGE[GUI Bridge]
        end
        
        subgraph "Engine Thread"
            LUA_ENGINE[Lua Engine]
            TIMER_MGR[Timer Manager]
            ASYNC_LOOP[Async Event Loop]
            FIBARO_SDK[Fibaro SDK]
        end
        
        subgraph "Web Server Process"
            FASTAPI[FastAPI Server]
            WEBSOCKET[WebSocket Handler]
            WEB_ROUTES[HTTP Routes]
            QUICKAPP_API[QuickApp API]
        end
        
        subgraph "Telnet Server"
            TELNET[Async Telnet Server]
            TELNET_CLIENTS[Client Connections]
        end
    end
    
    subgraph "External Clients"
        REPL_CLIENT[REPL Client Process]
        BROWSER[Browser Windows]
        QUICKAPP_UI[QuickApp Desktop UI]
    end
    
    CLI --> GUI
    CLI --> LUA_ENGINE
    GUI <--> GUI_BRIDGE
    GUI_BRIDGE <--> LUA_ENGINE
    LUA_ENGINE --> TIMER_MGR
    LUA_ENGINE --> FIBARO_SDK
    TIMER_MGR --> ASYNC_LOOP
    LUA_ENGINE --> FASTAPI
    LUA_ENGINE --> TELNET
    FASTAPI --> WEBSOCKET
    FASTAPI --> QUICKAPP_API
    TELNET <--> TELNET_CLIENTS
    TELNET_CLIENTS <--> REPL_CLIENT
    WEBSOCKET <--> BROWSER
    QUICKAPP_API <--> QUICKAPP_UI
```

## Component Details

### 1. Lua Engine (`src/plua/engine.py`)

The core execution engine that runs Lua scripts with Python integration:

```mermaid
graph LR
    subgraph "Lua Engine"
        LUA_RUNTIME[Lupa Runtime]
        BINDINGS[Python Bindings]
        SCRIPT_EXEC[Script Execution]
        QUEUE_PROC[Queue Processor]
    end
    
    subgraph "Async Support"
        TIMER_MGR[Timer Manager]
        CALLBACK_Q[Callback Queue]
        EXEC_Q[Execution Queue]
    end
    
    LUA_RUNTIME --> BINDINGS
    BINDINGS --> SCRIPT_EXEC
    SCRIPT_EXEC --> QUEUE_PROC
    QUEUE_PROC --> TIMER_MGR
    TIMER_MGR --> CALLBACK_Q
    CALLBACK_Q --> EXEC_Q
```

**Key Features:**
- Lupa-based Lua runtime with Python integration
- Async timer support with callback system
- Thread-safe script execution
- Queue-based communication between threads

### 2. GUI System (`src/plua/gui_bridge.py`, `src/plua/gui.py`)

Native tkinter-based UI with thread-safe communication:

```mermaid
graph TB
    subgraph "Main Thread"
        GUI_MGR[GUI Manager]
        TKINTER[Tkinter Root]
        WINDOWS[Native Windows]
    end
    
    subgraph "Engine Thread"
        LUA_ENGINE[Lua Engine]
        GUI_BRIDGE[GUI Bridge]
    end
    
    subgraph "Communication"
        CMD_QUEUE[Command Queue]
        RESULT_QUEUE[Result Queue]
    end
    
    GUI_MGR --> TKINTER
    TKINTER --> WINDOWS
    LUA_ENGINE --> GUI_BRIDGE
    GUI_BRIDGE --> CMD_QUEUE
    CMD_QUEUE --> GUI_MGR
    GUI_MGR --> RESULT_QUEUE
    RESULT_QUEUE --> GUI_BRIDGE
```

**Key Features:**
- Thread-safe bridge for GUI commands
- Native window creation and management
- Event-driven UI updates
- Queue-based command processing

### 3. QuickApp System (`src/plua/static/quickapp_ui.html`, `src/plua/fastapi_process.py`)

Browser-based Fibaro QuickApp emulation with real-time WebSocket updates:

```mermaid
graph TB
    subgraph "Browser UI"
        DESKTOP_UI[Desktop Windows]
        QUICKAPP_HTML[QuickApp UI HTML]
        WEBSOCKET_CLIENT[WebSocket Client]
        PING_PONG[Ping/Pong Health Check]
    end
    
    subgraph "FastAPI Server"
        QUICKAPP_ROUTES[QuickApp Routes]
        WEBSOCKET_SERVER[WebSocket Server]
        UI_BROADCAST[UI Update Broadcast]
        IPC_QUEUE[IPC Message Queue]
    end
    
    subgraph "Lua Engine"
        FIBARO_QA[QuickApp Instance]
        UPDATE_VIEW[updateView() calls]
        UI_CALLBACKS[UI Button Callbacks]
    end
    
    DESKTOP_UI --> QUICKAPP_HTML
    QUICKAPP_HTML --> WEBSOCKET_CLIENT
    WEBSOCKET_CLIENT <--> WEBSOCKET_SERVER
    WEBSOCKET_CLIENT --> PING_PONG
    WEBSOCKET_SERVER --> UI_BROADCAST
    UI_BROADCAST --> IPC_QUEUE
    IPC_QUEUE --> FIBARO_QA
    UPDATE_VIEW --> UI_BROADCAST
    UI_CALLBACKS --> FIBARO_QA
```

**Key Features:**
- Real-time UI updates via WebSocket
- Development-friendly connection management
- Automatic window reuse and cleanup
- Browser-based QuickApp UI rendering
- Ping/pong health check (5-second intervals)
- UI state preservation during reconnection
- Manual refresh capability for development workflow

**Connection Management:**
- **Simple Ping/Pong**: Clean 5-second ping with 8-second timeout
- **Auto-reconnection**: Conservative reconnection with 10-second delays
- **Status Preservation**: UI state maintained when server restarts
- **Focus Detection**: Automatic reconnection check on window focus
- **Manual Refresh**: Developer-controlled UI refresh button

### 4. Web Server (`src/plua/fastapi_process.py`, `src/plua/web_server.py`)

FastAPI-based HTTP API with WebSocket support for remote control and QuickApp emulation:

```mermaid
graph LR
    subgraph "FastAPI Process"
        FASTAPI[FastAPI App]
        HTTP_ROUTES[HTTP Routes]
        WEBSOCKET_ROUTES[WebSocket Routes]
        UVICORN[Uvicorn Server]
    end
    
    subgraph "API Endpoints"
        ROOT[/]
        STATUS[/status]
        EXECUTE[/execute]
        QUICKAPP[/plua/quickApp/*]
        WEBSOCKET[/ws WebSocket]
        UI_CALLBACK[/api/plugins/callUIEvent]
    end
    
    subgraph "Engine Integration"
        LUA_ENGINE[Lua Engine]
        IPC_QUEUE[IPC Queue]
        THREAD_EXEC[Thread Execution]
    end
    
    FASTAPI --> HTTP_ROUTES
    FASTAPI --> WEBSOCKET_ROUTES
    HTTP_ROUTES --> ROOT
    HTTP_ROUTES --> STATUS
    HTTP_ROUTES --> EXECUTE
    HTTP_ROUTES --> QUICKAPP
    HTTP_ROUTES --> UI_CALLBACK
    WEBSOCKET_ROUTES --> WEBSOCKET
    FASTAPI --> UVICORN
    EXECUTE --> THREAD_EXEC
    QUICKAPP --> IPC_QUEUE
    UI_CALLBACK --> IPC_QUEUE
    WEBSOCKET --> IPC_QUEUE
    THREAD_EXEC --> LUA_ENGINE
    IPC_QUEUE <--> LUA_ENGINE
```

**Key Features:**
- RESTful API for script execution
- Real-time engine status monitoring
- JSON-based function calling
- Thread-safe execution integration
- WebSocket support for real-time updates
- QuickApp API endpoints for Fibaro emulation
- IPC queue for cross-process communication

### 5. Telnet Server (`src/plua/lua_bindings.py`)

Async telnet server for interactive REPL access:

```mermaid
graph TB
    subgraph "Async Telnet Server"
        ASYNC_SERVER[Async Server]
        CLIENT_HANDLER[Client Handler]
        MESSAGE_Q[Message Queue]
    end
    
    subgraph "Client Connections"
        CLIENT1[Client 1]
        CLIENT2[Client 2]
        CLIENTN[Client N]
    end
    
    subgraph "Lua Integration"
        LUA_ENGINE[Lua Engine]
        CLIENT_EXEC[Client Execute]
        CLIENT_PRINT[Client Print]
    end
    
    ASYNC_SERVER --> CLIENT_HANDLER
    CLIENT_HANDLER --> MESSAGE_Q
    MESSAGE_Q --> CLIENT1
    MESSAGE_Q --> CLIENT2
    MESSAGE_Q --> CLIENTN
    CLIENT_HANDLER --> CLIENT_EXEC
    CLIENT_EXEC --> LUA_ENGINE
    LUA_ENGINE --> CLIENT_PRINT
    CLIENT_PRINT --> MESSAGE_Q
```

**Key Features:**
- Non-blocking async implementation
- Multiple client support
- Integrated with Lua print system
- Automatic stdout fallback

### 6. REPL Client (`src/plua/repl.py`)

Enhanced command-line interface with advanced features:

```mermaid
graph LR
    subgraph "REPL Client Process"
        PROMPT[Prompt Toolkit]
        HISTORY[Command History]
        COMPLETION[Auto-completion]
        SOCKET[Socket Client]
    end
    
    subgraph "Features"
        HISTORY_SEARCH[History Search]
        SYNTAX_HIGHLIGHT[Syntax Highlighting]
        MULTILINE[Multi-line Editing]
    end
    
    PROMPT --> HISTORY
    PROMPT --> COMPLETION
    PROMPT --> SOCKET
    HISTORY --> HISTORY_SEARCH
    COMPLETION --> SYNTAX_HIGHLIGHT
    SOCKET --> TELNET_SERVER
```

**Key Features:**
- Rich command-line interface with prompt_toolkit
- Command history and search
- Auto-completion for Lua functions
- Multi-line editing support

## Data Flow Diagrams

### 1. QuickApp UI Update Flow

```mermaid
sequenceDiagram
    participant QA as QuickApp Lua
    participant Engine as Lua Engine
    participant FastAPI as FastAPI Process
    participant WS as WebSocket
    participant Browser as Browser UI
    
    QA->>Engine: updateView(elementId, property, value)
    Engine->>FastAPI: IPC message (ui_update)
    FastAPI->>WS: Broadcast update to clients
    WS->>Browser: WebSocket message
    Browser->>Browser: Update DOM element
    
    Note over Browser: Real-time UI update without page refresh
```

### 2. QuickApp Button Callback Flow

```mermaid
sequenceDiagram
    participant User as User
    participant Browser as Browser UI
    participant FastAPI as FastAPI Process
    participant Engine as Lua Engine
    participant QA as QuickApp Lua
    
    User->>Browser: Click button
    Browser->>FastAPI: POST /api/plugins/callUIEvent
    FastAPI->>Engine: IPC callback message
    Engine->>QA: Execute callback function
    QA->>Engine: updateView() calls
    Engine->>FastAPI: UI update messages
    FastAPI->>Browser: WebSocket broadcast
    Browser->>Browser: Update UI elements
```

### 3. Connection Health Check Flow

```mermaid
sequenceDiagram
    participant Browser as Browser UI
    participant WS as WebSocket
    participant FastAPI as FastAPI Server
    
    loop Every 5 seconds
        Browser->>WS: Send ping
        WS->>FastAPI: Forward ping
        FastAPI->>WS: Send pong
        WS->>Browser: Receive pong
        
        alt No pong within 8 seconds
            Browser->>Browser: Close WebSocket
            Browser->>Browser: Update status: "Disconnected"
            Browser->>WS: Attempt reconnection
        end
    end
```

### 4. Script Execution Flow

```mermaid
sequenceDiagram
    participant CLI as CLI
    participant Engine as Lua Engine
    participant Timer as Timer Manager
    participant GUI as GUI Bridge
    participant FastAPI as FastAPI Process
    participant Telnet as Telnet Server
    
    CLI->>Engine: Load and execute script
    Engine->>Timer: Register timers/callbacks
    Engine->>GUI: Create windows/UI elements
    Engine->>FastAPI: Start FastAPI process (if requested)
    Engine->>Telnet: Start telnet server
    
    loop Script Execution
        Engine->>Timer: Process timers
        Timer->>Engine: Execute callbacks
        Engine->>GUI: Update UI
        Engine->>FastAPI: Handle IPC messages
        Engine->>Telnet: Handle REPL commands
    end
```

### 5. GUI Command Flow

```mermaid
sequenceDiagram
    participant Lua as Lua Script
    participant Bridge as GUI Bridge
    participant Queue as Command Queue
    participant GUI as GUI Manager
    participant Tkinter as Tkinter
    
    Lua->>Bridge: createNativeWindow()
    Bridge->>Queue: Send command
    Queue->>GUI: Process command
    GUI->>Tkinter: Create window
    Tkinter->>GUI: Window created
    GUI->>Queue: Send result
    Queue->>Bridge: Return result
    Bridge->>Lua: Return window ID
```

### 6. Web API Flow

```mermaid
sequenceDiagram
    participant Client as HTTP Client
    participant FastAPI as FastAPI Server
    participant Engine as Lua Engine
    participant Timer as Timer Manager
    
    Client->>FastAPI: POST /execute
    FastAPI->>Engine: Execute script
    Engine->>Timer: Register callbacks
    Timer->>Engine: Execute callbacks
    Engine->>FastAPI: Return result
    FastAPI->>Client: JSON response
```

### 7. REPL Communication Flow

```mermaid
sequenceDiagram
    participant User as User
    participant REPL as REPL Client
    participant Telnet as Telnet Server
    participant Engine as Lua Engine
    participant Print as Print System
    
    User->>REPL: Type command
    REPL->>Telnet: Send command
    Telnet->>Engine: Execute Lua
    Engine->>Print: Print output
    Print->>Telnet: Send to clients
    Telnet->>REPL: Display output
    REPL->>User: Show result
```

## Threading Model

### Thread Responsibilities

1. **Main Thread**: GUI management and user interaction
2. **Engine Thread**: Lua script execution and async operations
3. **FastAPI Process**: HTTP/WebSocket API handling (separate process)
4. **Telnet Server**: Async REPL server (runs in engine thread)
5. **REPL Client Process**: Separate process for enhanced CLI
6. **Browser Processes**: QuickApp UI windows (external browser windows)

### Thread Communication

```mermaid
graph TB
    subgraph "Thread Communication"
        subgraph "Queue-based"
            CMD_QUEUE[Command Queue]
            RESULT_QUEUE[Result Queue]
            CALLBACK_QUEUE[Callback Queue]
            IPC_QUEUE[IPC Message Queue]
        end
        
        subgraph "Process-based"
            FASTAPI_PROCESS[FastAPI Process]
            IPC_MULTIPROCESSING[Multiprocessing Queue]
            WEBSOCKET_BROADCAST[WebSocket Broadcast]
        end
        
        subgraph "Async-based"
            ASYNC_LOOP[Async Event Loop]
            TELNET_TASK[Telnet Task]
            TIMER_TASKS[Timer Tasks]
        end
        
        subgraph "Socket-based"
            TELNET_SOCKET[Telnet Socket]
            WEBSOCKET[WebSocket Connections]
        end
    end
    
    CMD_QUEUE --> ASYNC_LOOP
    RESULT_QUEUE --> ASYNC_LOOP
    CALLBACK_QUEUE --> ASYNC_LOOP
    IPC_QUEUE --> IPC_MULTIPROCESSING
    IPC_MULTIPROCESSING --> FASTAPI_PROCESS
    FASTAPI_PROCESS --> WEBSOCKET_BROADCAST
    WEBSOCKET_BROADCAST --> WEBSOCKET
    ASYNC_LOOP --> TELNET_TASK
    ASYNC_LOOP --> TIMER_TASKS
    TELNET_TASK --> TELNET_SOCKET
```

## Usage Patterns

### 1. Basic Script Execution

```bash
./run.sh script.lua
```

**Flow:**
1. CLI starts engine thread
2. Engine loads and executes script
3. Script runs with async timer support
4. Process exits when script completes

### 2. GUI Application

```bash
./run.sh gui_app.lua
```

**Flow:**
1. CLI starts GUI in main thread
2. Engine runs in worker thread
3. GUI bridge enables thread-safe communication
4. Lua creates native windows and UI elements

### 3. Web API Server

```lua
_PY.start_web_server("127.0.0.1", 8000)
```

**Flow:**
1. Lua starts web server in separate thread
2. FastAPI provides HTTP endpoints
3. External clients can execute Lua scripts
4. Results returned via JSON responses

### 4. Interactive REPL

```bash
./run.sh --interactive
```

**Flow:**
1. CLI starts telnet server
2. REPL client connects to telnet server
3. User types commands interactively
4. Results displayed in real-time

### 5. Fibaro QuickApp Development

```bash
./run.sh --fibaro quickapp.lua
```

**Flow:**
1. CLI starts with Fibaro SDK enabled
2. FastAPI process starts with QuickApp endpoints
3. Lua script defines QuickApp with UI elements
4. Browser windows automatically open (if `--%%desktop:true`)
5. Real-time UI updates via WebSocket
6. Development cycle: edit script → restart → preserved UI state

**Development Features:**
- **UI State Preservation**: Browser windows keep last UI state during server restart
- **Manual Refresh**: Developer can manually refresh UI via button
- **Connection Health**: Clear status indicators and automatic reconnection
- **Background Updates**: UI updates work even when window is not focused
- **Multiple Windows**: Support for multiple QuickApp instances simultaneously

## Configuration and Extensions

### Configuration System

```mermaid
graph LR
    subgraph "Configuration Sources"
        CLI_ARGS[CLI Arguments]
        CONFIG_TABLE[Config Table]
        ENV_VARS[Environment Variables]
    end
    
    subgraph "Configuration Usage"
        ENGINE[Engine Config]
        GUI[GUI Config]
        WEB[Web Server Config]
        TELNET[Telnet Config]
    end
    
    CLI_ARGS --> CONFIG_TABLE
    CONFIG_TABLE --> ENGINE
    CONFIG_TABLE --> GUI
    CONFIG_TABLE --> WEB
    CONFIG_TABLE --> TELNET
```

### Extension System

```mermaid
graph TB
    subgraph "Core System"
        ENGINE[Lua Engine]
        BINDINGS[Python Bindings]
    end
    
    subgraph "Extensions"
        GUI_EXT[GUI Extension]
        WEB_EXT[Web Server Extension]
        TIMER_EXT[Timer Extension]
        NET_EXT[Network Extension]
    end
    
    subgraph "Lua Libraries"
        NET[net.lua]
        TIMERS[timers.lua]
        LFS[lfs.lua]
        JSON[json.lua]
    end
    
    ENGINE --> BINDINGS
    BINDINGS --> GUI_EXT
    BINDINGS --> WEB_EXT
    BINDINGS --> TIMER_EXT
    BINDINGS --> NET_EXT
    GUI_EXT --> NET
    WEB_EXT --> TIMERS
    TIMER_EXT --> LFS
    NET_EXT --> JSON
```

## Performance Considerations

### Memory Management

- **Lua Engine**: Uses Lupa for efficient Python-Lua integration
- **GUI Bridge**: Queue-based communication minimizes memory overhead
- **Async Operations**: Non-blocking I/O prevents memory leaks
- **Thread Safety**: Proper synchronization prevents race conditions

### Scalability

- **Multiple Clients**: Telnet server supports multiple concurrent connections
- **Web API**: FastAPI provides high-performance HTTP handling
- **Timer System**: Efficient async timer management for many concurrent timers
- **GUI Updates**: Batched updates reduce UI thread overhead

## Security Considerations

### Network Security

- **Telnet Server**: Binds to localhost only by default
- **Web Server**: Configurable host binding for network access
- **Client Validation**: Input validation for all external commands
- **Timeout Protection**: Script execution timeouts prevent hanging

### Script Security

- **Sandboxing**: Lua scripts run in controlled environment
- **Resource Limits**: Timer and callback limits prevent resource exhaustion
- **Error Handling**: Comprehensive error handling prevents crashes
- **Input Validation**: All external inputs are validated

## Recent Enhancements

### Implemented Features

1. **✅ WebSocket Support**: Real-time bidirectional communication for QuickApp UI
2. **✅ Fibaro QuickApp Emulation**: Complete QuickApp SDK with UI rendering
3. **✅ Browser-based UI**: Modern web-based UI with real-time updates
4. **✅ Development-friendly Workflow**: UI state preservation and manual refresh
5. **✅ Connection Health Management**: Robust ping/pong system with automatic reconnection
6. **✅ Multi-process Architecture**: Separate FastAPI process for better isolation

### Connection Management Improvements

- **Simplified Health Checks**: Clean 5-second ping/pong system
- **Conservative Reconnection**: 10-second delays, fewer attempts
- **Status Preservation**: UI state maintained during server restarts
- **Developer Controls**: Manual refresh button and clear status indicators

## Future Enhancements

### Planned Features

1. **Plugin System**: Dynamic loading of Python extensions
2. **Distributed Mode**: Multi-node EPLua clusters  
3. **Performance Profiling**: Built-in performance monitoring
4. **Advanced Debugging**: Integrated debugger with breakpoints
5. **Mobile UI Support**: Touch-friendly QuickApp interfaces

### Architecture Evolution

```mermaid
graph LR
    subgraph "Current"
        SINGLE[Single Process + FastAPI Process]
        THREADS[Multi-threaded Engine]
        WEBSOCKET[WebSocket Support]
        QUICKAPP[QuickApp Emulation]
    end
    
    subgraph "Future"
        CLUSTER[Multi-process Clusters]
        MICROSERVICES[Microservices Architecture]
        DISTRIBUTED[Distributed QuickApps]
        MOBILE[Mobile UI Support]
    end
    
    SINGLE --> CLUSTER
    THREADS --> MICROSERVICES
    WEBSOCKET --> DISTRIBUTED
    QUICKAPP --> MOBILE
```

This architecture provides a solid foundation for building complex Lua applications with rich UI, network capabilities, Fibaro QuickApp emulation, and high performance while maintaining simplicity and extensibility. The recent addition of the QuickApp system makes EPLua particularly well-suited for Fibaro home automation development with a modern, web-based development workflow. 