-- Basic Lua example demonstrating standard Lua features

print("=== Basic Lua Example ===")

-- Variables and data types
local name = "World"
local number = 42
local boolean = true
local table = {1, 2, 3, name = "test"}

print("Name:", name)
print("Number:", number)
print("Boolean:", boolean)
print("Table:", table[1], table[2], table[3], table.name)

-- Control structures
if number > 40 then
  print("Number is greater than 40")
else
  print("Number is 40 or less")
end

-- Loops
print("Counting from 1 to 5:")
for i = 1, 5 do
  print("  " .. i)
end

-- Functions
local function greet(person)
  return "Hello, " .. person .. "!"
end

local function factorial(n)
  if n <= 1 then
  return 1
  else
  return n * factorial(n - 1)
  end
end

print(greet("Alice"))
print("Factorial of 5:", factorial(5))

-- String operations
local str1 = "Hello"
local str2 = "World"
local combined = str1 .. " " .. str2
print("Combined string:", combined)

print("=== Example completed ===") 