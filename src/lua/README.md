# Lua Modules Directory

This directory contains Lua modules that can be loaded using `require()` in PLua scripts.

## How to Use

### Loading Modules

```lua
-- Load a module
local mymodule = require("mymodule")

-- Use module functions
local result = mymodule.some_function("Hello World")
print(result)
```

### Available Modules

Currently, this directory is empty. You can create your own modules here.

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
local other_module = require("other_module")  -- Load another module

local mymodule = {}

function mymodule.greeting(name)
    return "Hello " .. name .. " from " .. other_module.get_version()
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
├── mymodule.lua
├── math/
│   └── init.lua
└── data/
    └── init.lua
```

## Using _PY Functions

Instead of creating Lua modules, you can also use the built-in `_PY` functions directly:

```lua
-- Use _PY functions directly
local hostname = _PY.get_hostname()
local timestamp = _PY.get_time()
local content = _PY.read_file("myfile.txt")

print("Hostname:", hostname)
print("Timestamp:", timestamp)
print("File content:", content)
``` 