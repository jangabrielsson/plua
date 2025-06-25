# PLua - Lua Interpreter in Python

A Lua interpreter implemented in Python using the Lupa library. It provides a Lua 5.4 environment with a modular extension system for adding Python functions to the Lua environment.

## Features

- **Lua 5.4 Environment**: Full Lua 5.4 compatibility through the Lupa library
- **Command Line Interface**: Run Lua files or execute code fragments
- **Interactive Shell**: REPL mode for interactive Lua development
- **Modular Extension System**: Easy-to-use decorator system for adding Python functions
- **Rich Function Library**: 50+ built-in Python functions across multiple categories
- **Network Support**: Asynchronous TCP and UDP networking with callback support

## Requirements

- Python 3.12+
- uv package manager

## Installation

### Using uv (Recommended)

1. Clone or download this repository
2. Install uv if you haven't already:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
3. Set up the environment and install dependencies:
   ```bash
   uv sync
   ```

### Alternative: Using pip

1. Clone or download this repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running Lua Files

```bash
# Using uv (recommended)
uv run python plua.py script.lua

# Using pip
python plua.py script.lua
```

### Executing Code Fragments

```bash
# Using uv (recommended)
uv run python plua.py -e "print_lua('Hello, World!')"

# Using pip
python plua.py -e "print_lua('Hello, World!')"
```

### Interactive Mode

```bash
# Using uv (recommended)
uv run python plua.py -i
# or simply
uv run python plua.py

# Using pip
python plua.py -i
# or simply
python plua.py
```

### Command Line Options

- `file` - Lua file to execute
- `-e, --execute` - Execute Lua code string
- `-i, --interactive` - Start interactive shell
- `-v, --version` - Show version information

## Extension System

PLua uses a decorator-based extension system that automatically registers Python functions to the Lua environment. This makes it easy to add new functionality.

### Adding Custom Extensions

Create a new Python file and use the `@registry.register` decorator:

```python
from lua_extensions import registry

@registry.register(description="My custom function", category="custom")
def my_function(arg1, arg2):
    """My custom function that will be available in Lua"""
    return arg1 + arg2
```

### Available Function Categories

#### Timer Functions
- `setTimeout(function, ms)` - Schedule a function to run after ms milliseconds
- `clearTimeout(reference)` - Cancel a timer using its reference ID

#### I/O Functions
- `print_lua(...)` - Print values to stdout
- `input_lua(prompt)` - Get user input with optional prompt
- `read_file(filename)` - Read and return file contents
- `write_file(filename, content)` - Write content to a file

#### Math Functions
- `sqrt(x)` - Calculate square root
- `pow(x, y)` - Calculate x raised to the power of y
- `random()` - Get random number between 0 and 1
- `randint(min, max)` - Get random integer between min and max

#### String Functions
- `to_upper(text)` - Convert string to uppercase
- `to_lower(text)` - Convert string to lowercase
- `split_string(text, delimiter)` - Split string by delimiter
- `join_strings(strings, delimiter)` - Join list of strings with delimiter

#### File System Functions
- `file_exists(filename)` - Check if file exists
- `get_file_size(filename)` - Get file size in bytes
- `list_files(directory)` - List files in directory
- `create_directory(path)` - Create directory

#### JSON Functions
- `parse_json(json_string)` - Parse JSON string to table
- `to_json(data)` - Convert data to JSON string

#### Data Processing Functions
- `average(numbers)` - Calculate average of numbers
- `max_value(values)` - Find maximum value in list
- `min_value(values)` - Find minimum value in list
- `count_occurrences(values, target)` - Count occurrences of value in list

#### Date/Time Functions
- `get_datetime()` - Get current date and time as string
- `format_timestamp(timestamp, format)` - Format timestamp as date string

#### System Functions
- `get_time()` - Get current timestamp in seconds
- `sleep(seconds)` - Sleep for specified seconds
- `get_python_version()` - Get Python version information

#### Network Functions
- `get_hostname()` - Get current hostname
- `check_port(host, port)` - Check if port is open on host
- `get_local_ip()` - Get local IP address
- `is_port_available(port, host)` - Check if port is available for binding

#### TCP Functions (Asynchronous with Callbacks)
- `tcp_connect(host, port, callback)` - Connect to TCP server asynchronously
- `tcp_write(conn_id, data, callback)` - Write data to TCP connection asynchronously
- `tcp_read(conn_id, max_bytes, callback)` - Read data from TCP connection asynchronously
- `tcp_close(conn_id, callback)` - Close TCP connection
- `tcp_set_timeout(conn_id, timeout_seconds, callback)` - Set TCP timeout asynchronously
- `tcp_get_timeout(conn_id, callback)` - Get TCP timeout asynchronously

#### TCP Functions (Synchronous - No Callbacks)
- `tcp_connect_sync(host, port)` - Connect to TCP server, returns `(success, conn_id, message)`
- `tcp_write_sync(conn_id, data)` - Write data to TCP connection, returns `(success, bytes_written, message)`
- `tcp_read_sync(conn_id, pattern)` - Read data from TCP connection using pattern, returns `(success, data, message)`
  - Patterns: `'*a'` (all data), `'*l'` (line), or number (bytes)
  - **Non-blocking behavior**: When socket has no data available (Errno 35), returns `(true, "", "No data available")` instead of error
- `tcp_close_sync(conn_id)` - Close TCP connection, returns `(success, message)`
- `tcp_set_timeout_sync(conn_id, timeout_seconds)` - Set TCP timeout, returns `(success, message)`
  - Use `0` for non-blocking mode
  - Use `nil` for blocking mode
  - Use positive number for timeout in seconds
- `tcp_get_timeout_sync(conn_id)` - Get TCP timeout, returns `(success, timeout_seconds, message)`

#### UDP Functions (Asynchronous with Callbacks)
- `udp_connect(host, port, callback)` - Connect to UDP server asynchronously
- `udp_write(conn_id, data, host, port, callback)` - Write data to UDP connection asynchronously
- `udp_read(conn_id, max_bytes, callback)` - Read data from UDP connection asynchronously
- `udp_close(conn_id, callback)` - Close UDP connection

#### Configuration Functions
- `get_env_var(name, default)` - Get environment variable value
- `set_env_var(name, value)` - Set environment variable

#### Utility Functions
- `get_type(value)` - Get type of a value as string
- `is_number(value)` - Check if value is a number
- `is_string(value)` - Check if value is a string
- `to_string(value)` - Convert value to string
- `to_number(value)` - Convert value to number
- `list_extensions()` - List all available Python extensions

#### Debug Functions
- `debug_value(value)` - Print debug information about value
- `measure_time(func, ...)` - Measure execution time of function

## Examples

### Basic Lua Code

```lua
-- Variables and control structures
local name = "World"
if name == "World" then
    print_lua("Hello, " .. name .. "!")
end

-- Functions
local function greet(person)
    return "Hello, " .. person .. "!"
end

print_lua(greet("Alice"))
```

### Using Extensions

```lua
-- Timer example
print_lua("Starting timer...")
setTimeout(function()
    print_lua("Timer fired after 3 seconds!")
end, 3000)

-- File operations
local content = read_file("input.txt")
if content then
    local upper_content = to_upper(content)
    write_file("output.txt", upper_content)
end

-- Math and data processing
local numbers = {1, 2, 3, 4, 5}
print_lua("Average:", average(numbers))
print_lua("Square root of 16:", sqrt(16))

-- String processing
local text = "hello world"
print_lua("Uppercase:", to_upper(text))
local words = split_string(text, " ")
print_lua("Words:", table.unpack(words))

-- JSON processing
local json_data = '{"name": "John", "age": 30}'
local parsed = parse_json(json_data)
if parsed then
    print_lua("Name:", parsed.name)
    print_lua("Age:", parsed.age)
end

-- Network operations
print_lua("Local IP:", get_local_ip())

-- TCP connection with callbacks
tcp_connect("example.com", 80, function(success, conn_id, message)
    if success then
        print_lua("Connected:", message)
        tcp_write(conn_id, "GET / HTTP/1.0\r\n\r\n", function(write_success, bytes_sent, write_message)
            if write_success then
                print_lua("Sent:", write_message)
                tcp_read(conn_id, 1024, function(read_success, data, read_message)
                    if read_success then
                        print_lua("Received:", read_message)
                        print_lua("Data preview:", string.sub(data, 1, 100))
                    end
                    tcp_close(conn_id, function(close_success, close_message)
                        print_lua("Closed:", close_message)
                    end)
                end)
            end
        end)
    else
        print_lua("Connection failed:", message)
    end
end)

-- TCP connection with synchronous functions (no callbacks)
local success, conn_id, message = tcp_connect_sync("example.com", 80)
if success then
    print_lua("Connected:", message)
    
    -- Set a custom timeout for this connection
    local timeout_success, timeout_message = tcp_set_timeout_sync(conn_id, 5.0)
    print_lua("Timeout set:", timeout_message)
    
    -- Set to blocking mode (no timeout)
    local blocking_success, blocking_message = tcp_set_timeout_sync(conn_id, nil)
    print_lua("Blocking mode:", blocking_message)
    
    -- Set back to timeout mode
    local set_success2, set_message2 = tcp_set_timeout_sync(conn_id, 5.0)
    print_lua("Set back to timeout mode:", set_message2)
    
    -- Read data using patterns
    local read_success, data, read_message = tcp_read_sync(conn_id, "*l")  -- Read a line
    if read_success then
        print_lua("First line:", data)
    end
    
    local read_success2, data2, read_message2 = tcp_read_sync(conn_id, 100)  -- Read 100 bytes
    if read_success2 then
        print_lua("Next 100 bytes:", string.sub(data2, 1, 50) .. "...")
    end
    
    local write_success, bytes_written, write_message = tcp_write_sync(conn_id, "GET / HTTP/1.0\r\n\r\n")
    if write_success then
        print_lua("Sent:", write_message)
        local read_success, data, read_message = tcp_read_sync(conn_id, 1024)
        if read_success then
            print_lua("Received:", read_message)
            print_lua("Data preview:", string.sub(data, 1, 100))
        end
    end
    local close_success, close_message = tcp_close_sync(conn_id)
    if close_success then
        print_lua("Closed:", close_message)
    else
        print_lua("Connection failed:", message)
    end
else
    print_lua("Connection failed:", message)
end

-- Non-blocking socket example (improved behavior)
local success, conn_id, message = tcp_connect_sync("example.com", 80)
if success then
    print_lua("Connected:", message)
    
    -- Set to non-blocking mode
    tcp_set_timeout_sync(conn_id, 0)
    print_lua("Set to non-blocking mode")
    
    -- Try to read - now returns empty string instead of error
    local read_success, data, read_message = tcp_read_sync(conn_id, 1024)
    if read_success then
        if #data > 0 then
            print_lua("Data received:", #data, "bytes")
        else
            print_lua("No data available (normal for non-blocking)")
        end
    else
        print_lua("Read error:", read_message)
    end
    
    -- Simple retry loop (much easier now!)
    local max_retries = 10
    for i = 1, max_retries do
        local success, data, message = tcp_read_sync(conn_id, 1024)
        if success and #data > 0 then
            print_lua("Data received on attempt", i, ":", #data, "bytes")
            break
        elseif success then
            print_lua("Attempt", i, ": No data available")
            os.execute("sleep 0.1")  -- Small delay
        else
            print_lua("Read error on attempt", i, ":", message)
            break
        end
    end
    
    tcp_close_sync(conn_id)
else
    print_lua("Connection failed:", message)
end
```