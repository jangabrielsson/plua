---
name: lua-basics
description: Lua language fundamentals for developers new to Lua: types, local vs global variables, conditionals (falsy values: only nil and false), functions (named, anonymous, multiple returns, variadic), tables as arrays and dictionaries (1-indexed!), iterating with ipairs/pairs, strings (pattern matching, format, split), closures, error handling (pcall/xpcall), OOP with the colon syntax, the Fibaro class system, and common gotchas (table reference semantics, # operator limitations, tostring/tonumber). USE FOR: help with Lua syntax, understanding why code behaves unexpectedly, table/string/function patterns, OOP in Lua.
---

# Lua Basics for QuickApp Developers

A practical Lua reference for developers who are new to Lua but have experience in other programming languages. Focused on patterns you'll actually use in Fibaro QuickApps.

---

## Types

Lua has 8 types: `nil`, `boolean`, `number`, `string`, `table`, `function`, `userdata`, `thread`.

```lua
print(type(nil))         -- "nil"
print(type(true))        -- "boolean"
print(type(42))          -- "number"
print(type(3.14))        -- "number"  (no int/float split in Lua 5.3+)
print(type("hello"))     -- "string"
print(type({}))          -- "table"
print(type(print))       -- "function"
```

---

## Variables: local vs global

**Always prefer `local`**. Global variables pollute `_G` and can collide across files.

```lua
x = 10          -- GLOBAL (avoid)
local y = 20    -- local to this scope (prefer)
```

In a QuickApp, instance state goes on `self`:
```lua
function QuickApp:onInit()
    self.myTimer = nil   -- instance variable — safe
    self.count = 0
end
```

---

## Conditionals

```lua
if x > 10 then
    print("big")
elseif x > 5 then
    print("medium")
else
    print("small")
end
```

Falsy values: **only `nil` and `false`**. Zero and empty string are truthy!
```lua
if 0  then print("truthy") end  -- prints!
if "" then print("truthy") end  -- prints!
if nil   then print("truthy") end  -- does NOT print
if false then print("truthy") end  -- does NOT print
```

Ternary idiom:
```lua
local label = active and "ON" or "OFF"
-- caution: if first branch could be false/nil, use an if/else instead
```

---

## Functions

```lua
-- Named function
function add(a, b)
    return a + b
end

-- Equivalent (functions are values)
local add = function(a, b)
    return a + b
end

-- Multiple return values
local function minmax(a, b)
    return math.min(a,b), math.max(a,b)
end
local lo, hi = minmax(10, 3)   -- lo=3, hi=10

-- Variadic arguments
local function sum(...)
    local total = 0
    for _, v in ipairs({...}) do total = total + v end
    return total
end
print(sum(1,2,3,4))  -- 10
```

Functions must be defined before they are called — Lua runs top to bottom:
```lua
-- Forward declaration for mutual recursion
local isEven, isOdd
isEven = function(n) return n == 0 or isOdd(n - 1)  end
isOdd  = function(n) return n ~= 0 and isEven(n - 1) end
```

---

## Tables

Tables are Lua's only data structure — they act as both arrays and dictionaries.

### As array (1-indexed!)
```lua
local fruits = {"apple", "banana", "cherry"}
print(fruits[1])        -- "apple"  (NOT fruits[0])
print(#fruits)          -- 3

table.insert(fruits, "date")           -- append
table.insert(fruits, 2, "avocado")    -- insert at position 2
table.remove(fruits, 1)               -- remove first element
table.sort(fruits)                    -- sort in place
```

### As dictionary
```lua
local person = { name = "Alice", age = 30 }
person.city = "London"
person["country"] = "UK"
print(person.name)             -- "Alice"
person.age = nil               -- remove field
```

### Iterating

Ordered integer keys:
```lua
for i, v in ipairs(fruits) do print(i, v) end
```

All keys (unordered):
```lua
for key, value in pairs(person) do print(key, "=", value) end
```

Numeric for:
```lua
for i = 1, 10       do print(i) end   -- 1 to 10
for i = 10, 1, -1   do print(i) end   -- 10 down to 1
```

---

## Strings

```lua
local s = "Hello, World!"
print(#s)                           -- 13
print(s:upper())                    -- "HELLO, WORLD!"
print(s:sub(1, 5))                  -- "Hello" (1-indexed, inclusive)
print(s:find("World"))              -- 8  14

-- Concatenation
local msg = "Temperature: " .. tostring(temp) .. "°C"

-- Formatting
local msg = string.format("Device %d: %.1f°C", id, temp)

-- Pattern matching
local year, month, day = ("2024-03-15"):match("(%d+)-(%d+)-(%d+)")

-- Split (Fibaro extension)
local parts = ("a,b,c"):split(",")   -- {"a","b","c"}
```

---

## Closures

A function that captures variables from its enclosing scope:

```lua
function QuickApp:onInit()
    local count = 0    -- captured by the closure below

    setInterval(function()
        count = count + 1
        self:debug("Tick", count)    -- self is also captured
    end, 1000)
end
```

---

## Error Handling

```lua
-- pcall: protected call — catches errors
local ok, result = pcall(function()
    return json.decode(rawString)
end)

if ok then
    print(result.key)
else
    self:error("Decode failed:", result)   -- result is the error message
end

-- assert: error if condition false
assert(value ~= nil, "value is required")

-- raise error
error("something went wrong")
error({code = 404, msg = "not found"})   -- can be any value
```

---

## Object-Oriented Programming

### The colon syntax
`obj:method(arg)` is syntax sugar for `obj.method(obj, arg)` — passes the object as `self`.

```lua
-- These are identical:
self:debug("hello")
QuickApp.debug(self, "hello")
```

### Defining methods on QuickApp
```lua
function QuickApp:doSomething(x)
    self:debug("doing", x)
    return x * 2
end
```

### Creating your own classes (Fibaro class system)
```lua
class 'MyHelper'

function MyHelper:__init(name)
    self.name = name
    self.data = {}
end

function MyHelper:add(item)
    table.insert(self.data, item)
end

function MyHelper:count()
    return #self.data
end

local h = MyHelper("test")
h:add("item1")
print(h:count())   -- 1
```

### Inheritance
```lua
class 'MySensor'(QuickAppChild)

function MySensor:__init(device)
    QuickAppChild.__init(self, device)  -- MUST call parent __init
end

function MySensor:onInit()
    self:debug("MySensor", self.id, "started")
end
```

---

## Common Gotchas

### `#` is unreliable with holes or non-integer keys
```lua
local t = {1, 2, nil, 4}   -- hole: #t is undefined
local t = {a=1, b=2}       -- #t == 0 (no integer keys)
```

### Tables are references, not copies
```lua
local a = {1, 2, 3}
local b = a       -- b IS a (same table)
b[1] = 99
print(a[1])       -- 99!

-- Shallow copy:
local function copy(t)
    local c = {}
    for k, v in pairs(t) do c[k] = v end
    return c
end
```

### Always use `tostring` / `tonumber` for conversions
```lua
local s = tostring(42)       -- "42"
local n = tonumber("3.14")   -- 3.14
local n = tonumber("abc")    -- nil (always check)
if n then ... end
```

### Build strings efficiently with `table.concat`
```lua
-- Slow (creates many intermediate strings):
local s = ""
for i = 1, 100 do s = s .. tostring(i) .. "," end

-- Fast:
local parts = {}
for i = 1, 100 do parts[i] = tostring(i) end
local s = table.concat(parts, ",")
```

---

## Useful Standard Library

```lua
math.floor(3.7)     -- 3
math.ceil(3.2)      -- 4
math.abs(-5)        -- 5
math.max(1,5,3)     -- 5
math.random(1,10)   -- random int 1–10

string.format("%.2f", 3.14159)   -- "3.14"
string.format("%05d", 42)        -- "00042"
string.rep("ab", 3)              -- "ababab"

table.concat({"a","b","c"}, "-") -- "a-b-c"

os.time()                        -- Unix timestamp
os.date("%Y-%m-%d %H:%M:%S")    -- "2024-03-15 14:30:00"
os.date("*t")                    -- {year,month,day,hour,min,sec,...}
```
