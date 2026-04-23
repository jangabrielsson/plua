# How PLua Works — a friendly overview

This is the "big picture" version of [ARCHITECTURE.md](../ARCHITECTURE.md).
It is meant for **QuickApp developers** who use plua every day but don't
particularly care about the Python internals — you just want a mental
model of what's happening when you press *Run*.

If you ever need the deep-dive (every module, every queue, every class),
the full ARCHITECTURE.md is one click away.

---

## What plua actually is

Plua is two things bolted together:

1. **A Lua interpreter that runs on your laptop.** Fibaro's Home Center 3
   (HC3) is itself a Lua machine, and plua runs the same Lua 5.4 dialect.
2. **A fake HC3 written in Lua.** A few thousand lines of Lua code
   pretend to be a Home Center 3 — there is a device list, a `fibaro.*`
   API, a UI engine, scenes, global variables, the works. Your QuickApp
   talks to this fake HC3 exactly the way it would talk to a real one.

The Lua interpreter is hosted by Python (using a library called
[Lupa](https://github.com/scoder/lupa)), because Python gives us easy
access to networking, an HTTP server, and a window manager — all things
that a plain Lua interpreter doesn't have built-in.

So, very roughly:

```
┌─────────────────────────────────────────────────┐
│  plua process (one program)                     │
│                                                 │
│   ┌────────────────────┐    ┌────────────────┐  │
│   │  Your QuickApp     │    │  Browser       │  │
│   │  (Lua)             │    │  (UI windows)  │  │
│   └─────────┬──────────┘    └────────┬───────┘  │
│             │  fibaro.*              │ HTTP/WS  │
│   ┌─────────▼──────────┐    ┌────────▼───────┐  │
│   │  Fake HC3 (Lua)    │◄──►│  Web server    │  │
│   │  emulator + API    │    │  (FastAPI)     │  │
│   └─────────┬──────────┘    └────────┬───────┘  │
│             │  _PY.*                  │         │
│   ┌─────────▼─────────────────────────▼───────┐ │
│   │  Python core: timers, HTTP/TCP/UDP/WS/MQTT│ │
│   │  network clients, file I/O                │ │
│   └───────────────────────────┬───────────────┘ │
└───────────────────────────────┼─────────────────┘
                                │
                       ┌────────▼────────┐
                       │  Real HC3 or    │
                       │  the wider net  │
                       └─────────────────┘
```

---

## The four layers, top to bottom

### 1. Your QuickApp

Plain Lua. The same code you would upload to a real HC3. It calls
`fibaro.call(...)`, `self:updateProperty(...)`, `setTimeout(...)` and so
on, blissfully unaware that it's running on your laptop.

### 2. The fake HC3 (`src/lua/fibaro/`)

Also pure Lua. A singleton object called `Emu` is the heart of it:

- It keeps a table of every "device" that exists in this fake HC3 (your
  QA, plus any child devices, plus a couple of housekeeping entries).
- It implements the `fibaro.*` functions and the `/api/...` REST routes.
- It compiles your `--%%u:` UI headers into something the browser can
  draw.
- When you call `fibaro.call(123, "turnOn")`, `Emu` decides whether to
  handle it locally, forward it to a real HC3, or look it up in an
  in-memory store — that decision is what we call **modes** (see below).

The user-facing class `QuickApp` lives here too. When plua starts your
script, it parses the `--%%` headers, builds a synthetic device record,
registers it with `Emu`, and calls your `onInit()`.

### 3. The Python core (`src/plua/`)

A small number of Python modules that exist mainly to give the Lua side
super-powers it doesn't have on its own:

- **`engine.py`** — owns the Lua VM and the asyncio event loop. Think of
  this as "the heartbeat".
- **`timers.py`** — when you call `setTimeout(fn, 1000)` in Lua, this is
  what schedules it.
- **`lua_bindings.py`** — the bridge. Anything Python wants to expose to
  Lua is decorated with `@export_to_lua` and shows up in Lua as
  `_PY.somefunction()`. (You almost never call `_PY` directly — Lua
  wrappers like `net.HTTPClient` do that for you.)
- **`fastapi_process.py`** — runs the small web server that powers the UI
  windows and the REST API.
- **`window_manager.py`** — opens browser windows for QA UIs and
  remembers their position.

### 4. The network library (`src/pylib/`)

Roughly one Python file per protocol: HTTP, TCP, UDP, WebSocket, MQTT,
plus filesystem access. These are the things `net.HTTPClient`,
`net.TCPSocket`, etc. quietly call into. They don't know anything about
Fibaro — they just do networking and report results back to Lua via a
callback.

---

## What happens when you press F5

A simplified play-by-play of `./run.sh --fibaro myqa.lua`:

1. **Python starts up.** It reads your command-line flags, makes sure
   the API port is free, and starts the small FastAPI web server in the
   background.
2. **The Lua VM is created** and a few hundred Python helpers are
   exposed to it under the global `_PY` table.
3. **`init.lua` runs.** It patches some things (UTF-8, timers,
   `print`) and waits to be told what file to load.
4. **`fibaro.lua` runs** (because of `--fibaro`). This brings the fake
   HC3 to life: it creates `Emu`, sets up the API router, and tells
   `init.lua` "actually, let *me* load the user's file."
5. **Your file is loaded.** plua reads the `--%%` headers, builds a
   device record, and creates an instance of your `QuickApp` class.
   `QuickApp:onInit()` is called.
6. **The event loop runs.** Timers fire, HTTP responses arrive, UI
   clicks come in from the browser, the QA reacts. This continues until
   `--run-for` says it's time to quit (default: at least 1 second, then
   exit when nothing is pending).

---

## Talking to the outside world

When your QA does `net.HTTPClient():request(url, ...)`:

```
QA (Lua)
  │  net.HTTPClient:request(url, callback)
  ▼
net.lua wrapper
  │  _PY.call_http(url, callback_id)        ← callback registered
  ▼
pylib/http_client.py
  │  asyncio task: aiohttp does the request
  ▼  (network)
The actual HTTP server
  │
  ▼  response comes back, possibly on another thread
engine.post_callback_from_thread(id, result)
  │  result lands on a queue
  ▼  next event-loop tick
Lua callback runs with the response
```

The same pattern works for TCP, UDP, WebSocket, MQTT, timers, and even
"a HTTP request hit our FastAPI server, please handle it in Lua". It is
**always**: register a callback ID in Lua → do work in Python → drop the
result on a queue → Lua gets called back. This is what lets a single Lua
thread coexist with everything async without ever blocking.

---

## The three modes

A QA always runs in one of three modes (set by `--%%offline:true`,
`--%%proxy:true`, or neither):

| Mode | What `fibaro.call(...)` actually hits |
|---|---|
| **Online** *(default)* | The fake HC3 first, and anything it can't handle is forwarded to your real HC3 over HTTP. You need credentials in `.env`. |
| **Offline** | Only the fake HC3, plus an in-memory store seeded with some realistic dummy devices. No network at all. Great for CI and trains. |
| **Proxy** | Your QA runs locally **and** a tiny stub QA is installed on the real HC3. UI clicks and HC3 events tunnel back to plua over a WebSocket, so you can iterate locally while still reacting to the real device. |

---

## The UI windows

When a QA has `--%%desktop:true`, plua opens a browser window pointed at
its built-in web server. The page (`quickapp_ui.html`) draws your
buttons, sliders, and labels by fetching `/plua/quickApp/<id>/info`.

When you click a button:

1. The browser POSTs to `/api/plugins/callUIEvent`.
2. FastAPI hands the request to the engine.
3. The engine looks up the QA, calls the right handler method.
4. If the handler calls `self:updateView(...)`, the engine pushes the
   change back to the browser over a WebSocket so the UI updates live.

You don't have to think about any of this — just write `onReleased`
handlers and call `updateView`.

---

## Where things live (cheat sheet)

```
src/
├── plua/        ← Python: engine, web server, bridge, window manager
├── pylib/       ← Python: HTTP/TCP/UDP/WS/MQTT/filesystem primitives
└── lua/
    ├── init.lua, json.lua, net.lua, ...   ← runtime + std libs
    └── fibaro/  ← the fake HC3 (Emu, QuickApp, UI compiler, modes, ...)
```

**Things you'll touch as a QA developer:** your own `.lua` file, the
HC3 credentials in `.env`, and sometimes a header in `.project`.

**Things you'll never need to touch (but now know exist):** Python core,
the FastAPI server, the queue plumbing.

---

## Where to go next

- **Want a concrete starter QA?** `plua --init-qa` scaffolds a project.
- **Want to see every API your QA can call?** Ask Copilot for
  `/quickapp-api`.
- **Want common patterns** (timers, polling, child devices)? Ask for
  `/quickapp-patterns`.
- **Want the deep architecture?** Read [ARCHITECTURE.md](../ARCHITECTURE.md).
- **Stuck?** [`/plua-troubleshooting`](../.github/skills/plua-troubleshooting/SKILL.md)
  and [`/quickapp-troubleshooting`](../.github/skills/quickapp-troubleshooting/SKILL.md)
  cover the common pitfalls.
