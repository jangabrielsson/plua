-- Test the config table with CLI flags
print('=== EPLua Config Test ===')
for k,v in pairs(_PY.config) do
    if type(v) == 'table' then
        v = json.encode(v)  -- Convert table to JSON string for better readability
    end
    print(k .. ': ' .. tostring(v))
end
print('========================')

-- Test specific values
print('File separator: ' .. _PY.config.fileSeparator)
print('Platform: ' .. _PY.config.platform) 
print('Lua lib path: ' .. _PY.config.luaLibPath)
print('Offline mode: ' .. tostring(_PY.config.offline))
print('Debugger enabled: ' .. tostring(_PY.config.debugger))
print('Debugger host: ' .. tostring(_PY.config.debugger_host))
print('Debugger port: ' .. tostring(_PY.config.debugger_port))
