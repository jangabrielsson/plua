---
name: plua-troubleshooting
description: Common plua runtime errors and how to fix them: port conflicts (WebSocket/API server already in use), HC3 connection failures, Lua runtime errors, debugger warnings, timer/async issues. USE FOR: diagnosing plua startup errors, port-in-use messages, fixing "address already in use", understanding --api-port and --nodebugger flags, cross-platform remedies for macOS and Windows.
---

# plua Troubleshooting

---

## Port already in use (WebSocket / API server)

**Error message:**
```
WebSocket server start error: [Errno 48] error while attempting to bind on address ('x.x.x.x', 8082): address already in use
```
or
```
ERROR: [Errno 98] Address already in use
```

**Cause:** A previous plua process crashed or was killed without releasing its ports. plua uses two ports:
- `--api-port N` (default **8080**) — FastAPI HTTP server
- `--api-port N` + 2 (default **8082**) — WebSocket broadcast server

**Fix 1 — Kill the process holding the port**

macOS / Linux:
```bash
kill -9 $(lsof -ti:8082)
# or for the API port:
kill -9 $(lsof -ti:8080)
```

Windows (Command Prompt):
```cmd
for /f "tokens=5" %a in ('netstat -aon ^| findstr :8082') do taskkill /F /PID %a
```

Windows (PowerShell):
```powershell
Stop-Process -Id (Get-NetTCPConnection -LocalPort 8082 -ErrorAction SilentlyContinue).OwningProcess -Force
```

**Fix 2 — Use a different port**

Run plua with a different base port to avoid the conflict entirely:
```bash
plua --fibaro --api-port 8090 dev/myQA.lua
# WebSocket will then use 8092
```

---

## Debugger warning on startup

**Message:**
```
Lua debugger not connected / waiting for debugger...
```

**Cause:** plua starts the Lua debugger listener by default when run outside VS Code.

**Fix:** Pass `--nodebugger` when running from the terminal:
```bash
plua --fibaro --nodebugger dev/myQA.lua
```

---

## HC3 connection failure

**First step — run the built-in diagnostic:**
```bash
plua --diagnostic
```
This tests the HC3 connection and prints a full config summary including URL, credentials, platform, API port, and HC3 firmware version. Example output:
```
✅ hc3_url             : http://192.168.50.57
✅ hc3_user            : admin
✅ hc3_password        : Admin1477!
⚠️  hc3_pin             : nil
✅ HC3 Serialnumber    : HC3-00000422
✅ HC3 Software version: 5.201.18
```
`✅` = configured/reachable, `⚠️` = missing/optional.

**Other checks:**
1. HC3 IP/credentials configured? See `plua --help` or `~/.plua/config.json`
2. HC3 reachable on the network? `ping <hc3-ip>`
3. Run with `--offline` to skip HC3 connection entirely (emulated environment only):
```bash
plua --fibaro --nodebugger --offline dev/myQA.lua
```

---

## Script exits immediately

**Cause:** Default `--run-for 1` — plua exits after 1 second if no active timers/callbacks remain.

**Fix:**
```bash
# Run for at least N seconds (or until no pending callbacks)
plua --fibaro --nodebugger --run-for 30 dev/myQA.lua

# Run until manually killed
plua --fibaro --nodebugger --run-for 0 dev/myQA.lua

# Run for exactly N seconds regardless of callbacks
plua --fibaro --nodebugger --run-for -30 dev/myQA.lua
```

---

## `attempt to concatenate a nil value` on `self:getVariable()`

**Cause:** `self:getVariable()` can return `nil` (not `""`) if the variable is not yet defined on the emulated device.

**Fix:** Always guard with a fallback:
```lua
local val = self:getVariable("myVar")
if val == nil or val == "" then val = "default" end
```

---

## `bad argument #2 to 'format' (number expected, got table)`

**Cause:** Values decoded from JSON via Lupa are proxy objects, not native Lua numbers. `tonumber()` on a proxy object returns a table in some cases.

**Fix:** Always wrap with `tostring()` before `tonumber()`:
```lua
local temp = tonumber(tostring(data.temp_C))
```

---

## Inspect running port usage

```bash
# macOS — show what is using plua's default ports
lsof -i :8080 -i :8082

# Windows PowerShell
Get-NetTCPConnection -LocalPort 8080,8082 | Select-Object LocalPort, State, OwningProcess
```
