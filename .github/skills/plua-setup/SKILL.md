---
name: plua-setup
description: How to install plua, configure HC3 credentials (.env file), scaffold a new QuickApp project (--init-qa), VS Code integration (launch.json, tasks), and key CLI flags reference. USE FOR: setting up a new development workspace, connecting plua to an HC3, understanding --fibaro/--nodebugger/--run-for/--offline flags, initializing a project structure, VS Code F5 debugging setup.
---

# plua Setup and Workspace Guide

---

## Installation

**Requirements:** Python 3.8+, macOS / Linux / Windows

```bash
# Install from PyPI
pip install plua

# Verify
plua --version
```

For development from source:
```bash
git clone https://github.com/jangabrielsson/plua.git
cd plua
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e .
```

---

## HC3 Credentials

plua reads credentials from environment variables. Set them via a `.env` file.

### Option 1 — Project `.env` (recommended)
Create `.env` in your project directory:
```ini
HC3_URL=http://192.168.1.100
HC3_USER=admin
HC3_PASSWORD=your-password
HC3_PIN=1234
```
> `HC3_PIN` is only needed for restricted calls (e.g. alarm panel access).

### Option 2 — Global `~/.env`
Same format, placed in your home directory. Shared across all projects.

### Option 3 — Shell environment variables
```bash
export HC3_URL=http://192.168.1.100
export HC3_USER=admin
export HC3_PASSWORD=your-password
```

### Lookup order
1. System environment variables
2. `.env` in current working directory
3. `~/.env` in home directory

> **Security:** Add `.env` to `.gitignore` — never commit credentials.

### Verify the connection
```bash
plua --diagnostic
```
Prints config summary and HC3 connection status. `✅` = OK, `⚠️` = missing/optional.

---

## Scaffold a New QuickApp Project

```bash
plua --init-qa
```

Interactive wizard — choose from 42 device type templates. Creates:
```
my-quickapp/
├── .vscode/
│   ├── launch.json    # F5 debug configuration
│   └── tasks.json     # HC3 upload/sync tasks
├── .project           # HC3 deployment config (device ID, etc.)
└── main.lua           # QuickApp code
```

---

## VS Code Integration

### Debugging (F5)
The generated `launch.json` runs your QA under the VS Code Lua debugger. Set breakpoints, inspect variables, step through code — press F5 to start.

### Tasks (Ctrl+Shift+P → "Tasks: Run Task")
| Task | Description |
|---|---|
| `Plua, upload current file as QA to HC3` | Package and upload current file as a new QA |
| `Plua, update QA (defined in .project)` | Sync full project to existing HC3 QA |
| `Plua, update single file (part of .project)` | Push one changed file to HC3 QA |
| `Plua, Download and unpack from HC3` | Download a QA from HC3 by ID |

---

## Key CLI Flags

```bash
plua [script.lua] [options]
```

| Flag | Default | Description |
|---|---|---|
| `--fibaro` | off | Enable Fibaro HC3 emulation (required for QA development) |
| `--nodebugger` | off | Disable Lua debugger (use when running from terminal, not VS Code) |
| `--offline` | off | Skip HC3 connection — run fully emulated |
| `--run-for N` | 1 | N>0: run ≥N sec or until no callbacks; N=0: run forever; N<0: run exactly \|N\| sec |
| `--api-port N` | 8080 | FastAPI HTTP server port (WebSocket uses port+2) |
| `--diagnostic` | — | Print config + HC3 connection test, then exit |
| `--init-qa` | — | Interactive project scaffolding wizard |
| `-e "code"` | — | Execute a Lua expression and exit — useful for HC3 queries |
| `-i` | — | Interactive REPL (with prompt_toolkit) |
| `--telnet` | off | Start multi-session telnet server (default port 8023) |
| `--loglevel` | info | Logging verbosity: debug / info / warning / error |

### Common invocations
```bash
# Run a QA from terminal (no VS Code debugger)
plua --fibaro --nodebugger main.lua

# Run for exactly 30 seconds
plua --fibaro --nodebugger --run-for -30 main.lua

# Run without HC3 connection
plua --fibaro --nodebugger --offline main.lua

# One-shot HC3 API query
plua --fibaro -e "json.encodeFormated((api.get('/devices/45')))"

# Run multiple QAs simultaneously
plua --fibaro --nodebugger qa1.lua qa2.lua
```

---

## Typical Project Workflow

1. **Install & configure** — `pip install plua`, create `.env` with HC3 credentials
2. **Verify** — `plua --diagnostic`
3. **Scaffold** — `plua --init-qa` (or create a `.lua` file with `--%%` headers manually)
4. **Develop** — open in VS Code, press F5 to run/debug locally
5. **Inspect HC3** — `plua --fibaro -e "json.encodeFormated((api.get('/devices/45')))"` to check real device structures
6. **Upload** — use VS Code task "upload QA to HC3" or `plua --tool uploadQA main.lua`
