-- Test script 1
print("Script 1: Hello from first script!")
---@diagnostic disable-next-line: lowercase-global
script1_var = "I am script 1"
local a = api.get("/quickApp/export/4205")
print(json.encode(a))