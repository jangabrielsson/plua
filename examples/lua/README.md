# EPLua Examples - Native UI & Network Demos

These examples demonstrate EPLua's **user-friendly APIs** for end users writing Lua scripts, with a focus on **native UI** using tkinter widgets.

## 🎯 **Recommended Starting Examples**

### **Native UI Demos** (✅ Working)
- **[`button_row_demo.lua`](button_row_demo.lua)** - **NEW!** Complete button row demo with callbacks
- **[`native_ui_demo.lua`](native_ui_demo.lua)** - Comprehensive native UI showcase  
- **[`getting_started.lua`](getting_started.lua)** - Basic EPLua introduction

### **Network Examples** (✅ Working)
- **[`http_demo.lua`](http_demo.lua)** - HTTP client examples
- **[`network_demo.lua`](network_demo.lua)** - Network module demonstrations
- **[`mqtt_example.lua`](mqtt_example.lua)** - MQTT client examples

## Available APIs

### Native UI Module
- `nativeUI.createWindow()` - Create native tkinter windows
- `nativeUI.isAvailable()` - Check native UI availability
- `nativeUI.quickUI()` - Fluent UI builder with button rows
- **Button Rows**: Horizontal button layouts with individual callbacks

### Timer Functions
- `setTimeout(callback, milliseconds)` - Run function after delay
- `setInterval(callback, milliseconds)` - Run function repeatedly  
- `clearTimeout(id)` - Cancel a timeout
- `clearInterval(id)` - Cancel an interval

### Network Modules  
- `net.HTTPClient()` - HTTP/HTTPS requests
- `net.WebSocketClient()` - WebSocket connections
- `net.MQTTClient()` - MQTT messaging
- `net.TCPSocket()` - TCP connections
- `net.UDPSocket()` - UDP datagrams

### Legacy Windows Module (⚠️ HTML-dependent)
- `windows.createWindow()` - Create HTML-capable windows (requires CEF)
- `windows.isAvailable()` - Check GUI availability
- `windows.htmlSupported()` - Check HTML rendering support

### Utility Modules
- `json.encode()` / `json.decode()` - JSON processing
- `lfs.*` - File system operations (LuaFileSystem compatible)

## Examples

### `button_row_demo.lua` **⭐ NEW!**
**Complete button row demonstration!** Shows:
- Button rows with individual callbacks
- Proper callback data handling (`data.data.value` for sliders)
- Multiple button row configurations (2, 3, 4, 5 buttons)
- Real-time UI updates and status display
- QuickApp-style interface design

### `native_ui_demo.lua` **⭐ RECOMMENDED**
**Comprehensive native UI showcase** featuring:
- All native widgets: labels, buttons, sliders, dropdowns
- Proper callback handling with event data
- Dynamic UI updates
- Multi-window management

### `getting_started.lua`
**Perfect for beginners!** Step-by-step introduction to EPLua's main features:
- Basic timers and intervals
- HTTP requests
- WebSocket communication
- MQTT messaging
- Low-level networking

### `basic_example.lua`
Comprehensive overview showing:
- Timer usage patterns
- HTTP client with success/error callbacks
- WebSocket event handling
- Network client lifecycle

### `network_demo.lua`
In-depth networking examples:
- HTTP GET/POST requests with custom headers
- TCP socket connections
- UDP socket messaging
- MQTT publish/subscribe
- Error handling patterns

### `timer_examples.lua`
Complete timer functionality:
- Basic setTimeout/setInterval usage
- Clearing timers
- Timer chains
- Self-clearing intervals
- Performance testing

### `test_json.lua`
JSON processing examples:
- Encoding Lua tables to JSON
- Decoding JSON to Lua tables
- Pretty-printing with formatting
- Error handling and edge cases

### `windows_example.lua`
GUI window creation:
- Creating HTML-capable windows
- Method chaining interface
- Beautiful CSS styling
- Window management

### `test_windows.lua`
Comprehensive windows testing:
- Object-oriented and functional interfaces
- HTML rendering and URL loading
- Error handling and capabilities checking
- Multiple window management

## Usage

```bash
# Run any example
python -m src.eplua.cli examples/lua/getting_started.lua
python -m src.eplua.cli examples/lua/network_demo.lua
```

## API Documentation

All user APIs are designed to be:
- **Simple** - Easy to learn and use
- **Consistent** - Similar patterns across all modules
- **Safe** - Automatic error handling
- **Async** - Non-blocking operations with callbacks

These APIs abstract away the internal `_PY.*` functions and provide a clean, Fibaro HC3-compatible interface.

## 🚀 **Quick Start**

```bash
# Run the comprehensive button row demo
./run.sh examples/lua/button_row_demo.lua

# Run the native UI showcase
./run.sh examples/lua/native_ui_demo.lua

# Basic getting started
./run.sh examples/lua/getting_started.lua
```
