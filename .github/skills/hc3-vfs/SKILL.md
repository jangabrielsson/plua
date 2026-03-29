---
name: hc3vfs
description: >
  Use this skill when the user asks you to work with Fibaro HC3 QuickApp files in
  the VS Code Explorer. This covers reading, editing, creating, deleting, and searching
  Lua files inside hc3:// workspace folders, as well as reading and updating QuickApp
  properties via the (QuickApp).hc3qa file.
applyTo: "hc3://**"
---

# HC3 Virtual Filesystem (hc3-vfs) — Agent Instructions

## Overview

The **hc3-vfs** extension mounts Fibaro HC3 QuickApp files directly in the VS Code Explorer
under a virtual filesystem using the `hc3://` URI scheme.

Each QuickApp appears as a folder:
```
hc3://192.168.1.100/
  42-my-quickapp/
    main.lua          ← always present; the main Lua module
    helper.lua        ← additional Lua modules
    (QuickApp).hc3qa  ← virtual properties file (see below)
  99-another-qa/
    main.lua
```

**Folder naming:** `{id}-{slug}` — the numeric prefix is the HC3 device ID.  
**File naming:** `.lua` extension is added/stripped automatically; the HC3 API stores files without it.

---

## Reading Files

Use standard file read tools with `hc3://` URIs:

```
hc3://192.168.1.100/42-my-quickapp/main.lua
```

The `(QuickApp).hc3qa` file is JSON containing all device properties (name, type, enabled,
visible, interfaces, quickAppVariables, created, modified timestamps, etc.).

---

## Writing / Editing Files

Standard file edit tools work on `hc3://` URIs. Changes are saved directly to the HC3
via `PUT /api/quickApp/{id}/files/{name}`. No local copy — the HC3 is the source of truth.

---

## Creating a New Lua File

Use `create_file` targeting a `hc3://` URI:

```
hc3://{host}/{id}-{slug}/newmodule.lua
```

Rules enforced by the extension:
- Filename must be at least 3 characters (without `.lua`)
- Only alphanumeric characters and underscores are allowed in the name
- Cannot create `(QuickApp).hc3qa` (it is virtual and managed automatically)

After creation the file appears in the Explorer and on the HC3 immediately.

---

## Deleting a Lua File

The extension registers the command `hc3vfs.deleteFile` specifically for programmatic and
agent use. Call it with the full `hc3://` URI as a string argument:

```javascript
// Via VS Code command palette or programmatic invocation:
vscode.commands.executeCommand(
  'hc3vfs.deleteFile',
  'hc3://192.168.1.100/42-my-quickapp/helper.lua'
)
```

**Important constraints:**
- The `main.lua` (the QuickApp's main file, marked `isMain: true`) **cannot be deleted** —
  the HC3 API does not permit it.
- `(QuickApp).hc3qa` cannot be deleted — it is a virtual file.
- All other `.lua` files in a QuickApp folder can be deleted freely.

---

## Searching Code

Use `grep_search` or `semantic_search` targeting `hc3://{host}/**` to search across all
QuickApp files on the connected HC3.

Example — find all usages of `fibaro.call` across all QAs:
```
grep_search: "fibaro.call"  includePattern: "hc3://**"
```

Note: `.hc3qa` files are excluded from text search automatically by the extension.

---

## QuickApp Properties — (QuickApp).hc3qa

Each QA folder contains a `(QuickApp).hc3qa` file. Clicking it opens a webview editor.
Reading the raw file gives JSON with all device properties:

```json
{
  "id": 42,
  "name": "My QuickApp",
  "type": "com.fibaro.binarySwitch",
  "enabled": true,
  "visible": true,
  "interfaces": ["zwave", "energy"],
  "created": 1700000000,
  "modified": 1710000000,
  "properties": {
    "quickAppVariables": [
      { "name": "apiKey", "value": "abc123" }
    ],
    "userDescription": "Controls the living room switch"
  }
}
```

The webview editor supports saving changes to: name, enabled, visible, description,
interfaces (add/remove), and quickAppVariables (add/edit/delete rows).

---

## Available Commands

| Command | Description |
|---------|-------------|
| `HC3: Connect` | Connect to the configured HC3 and mount the filesystem |
| `HC3: Disconnect` | Unmount the filesystem |
| `HC3: Refresh` | Clear all caches and reload device/file lists |
| `HC3: Configure Credentials` | Set HC3 host, user, and password |
| `HC3: Export .fqa` | Export a QuickApp as a `.fqa` archive to disk |
| `HC3: Rename QuickApp` | Rename a QuickApp on the HC3 |
| `HC3: Open in HC3 Web UI` | Open the device in the HC3 browser UI |
| `HC3: Delete File` | Delete a `.lua` file from a QuickApp (for agent use) |
| `HC3: Statistics` | Show API call statistics for the session |

---

## Credentials & Configuration

Credentials are resolved in this priority order:
1. `.env` file in the workspace folder (`HC3_URL` or `HC3_HOST`, `HC3_USER`, `HC3_PASSWORD`)
2. `~/.env` in the home directory
3. VS Code settings (`hc3vfs.host`, `hc3vfs.user`) + VS Code Secret Storage (password)

**Example `.env`:**
```
HC3_URL=http://192.168.1.100
HC3_USER=admin
HC3_PASSWORD=your_password
```
`HC3_HOST` is accepted as an alias for `HC3_URL`.

---

## Common Agent Workflows

### Add a new module to a QuickApp
```
1. create_file: hc3://192.168.1.100/42-my-quickapp/utils.lua  (with content)
2. Done — visible in Explorer and live on HC3 immediately.
```

### Delete a module from a QuickApp
```
1. run_vscode_command: hc3vfs.deleteFile
   arg: "hc3://192.168.1.100/42-my-quickapp/utils.lua"
2. Confirm the modal prompt (Delete button).
```

### Edit a QuickApp variable value
```
1. read_file: hc3://192.168.1.100/42-my-quickapp/(QuickApp).hc3qa
2. Find the variable in properties.quickAppVariables
3. The webview editor is the user-facing way; for agent use, note that the .hc3qa
   file is read-only via file tools — use the HC3 API directly if needed.
```

### Search for a function across all QuickApps
```
1. grep_search: "function myHelper" isRegexp: false includePattern: "hc3://**"
```

### Refresh after external changes
```
1. HC3: Refresh command — clears the 5-second TTL caches so the Explorer shows current state.
```
