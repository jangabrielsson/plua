# Lua Modules Directory

This directory contains Lua modules that can be loaded using `require()` in PLua scripts.

## How to Use

### Loading Modules

```lua
-- Load a module
local utils = require("utils")

-- Use module functions
local formatted = utils.format_with_prefix("Test", "Hello World")
print(formatted)  -- Output: Test: Hello World
```

### Available Modules

#### `utils.lua`
A general utility module with common helper functions:

- `utils.format_with_prefix(prefix, text)` - Format text with a prefix
- `utils.is_empty(str)` - Check if a string is empty
- `utils.capitalize(str)` - Capitalize the first letter of a string
- `utils.create_table(...)` - Create a table from key-value pairs

#### `network_utils.lua`
Network utility functions that use the PLua network extensions:

- `network_utils.test_tcp_connection(host, port, callback)` - Test a TCP connection
- `network_utils.get_network_info()` - Get network information
- `network_utils.quick_test()` - Run a quick network test

### Creating Your Own Modules

1. Create a new `.lua` file in this directory
2. Define your module as a table with functions
3. Return the module at the end of the file

Example:
```lua
-- mymodule.lua
local mymodule = {}

function mymodule.hello(name)
    return "Hello, " .. name .. "!"
end

return mymodule
```

### Module Dependencies

Modules can depend on other modules using `require()`:

```lua
-- mymodule.lua
local utils = require("utils")  -- Load another module

local mymodule = {}

function mymodule.greeting(name)
    return utils.format_with_prefix("Greeting", "Hello " .. name)
end

return mymodule
```

## Package Path

The PLua interpreter automatically sets up the package path to include:
- `./lua/?.lua` - Direct module files
- `./lua/?/init.lua` - Module directories with init files
- `./examples/?.lua` - Example files
- `./examples/?/init.lua` - Example directories with init files

This means you can organize modules in subdirectories if needed:

```
lua/
├── utils.lua
├── network_utils.lua
├── math/
│   └── init.lua
└── data/
    └── init.lua
``` 