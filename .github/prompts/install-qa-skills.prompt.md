---
mode: agent
description: Downloads and installs plua QuickApp development skills and auto-apply instructions from github.com/jangabrielsson/plua into this workspace. Safe to re-run for updates.
skill_version: "1.1.0"
---

<!-- SKILL VERSION: 1.1.0 -->

Install / update the plua QuickApp development skills in this workspace.

## Bootstrap — get this file first

Before you can run `/install-qa-skills`, you need this prompt file in your workspace. Run one of these commands from your workspace root, then type `/install-qa-skills` in Copilot chat.

**Universal (Python — macOS, Linux, Windows):**
```
python3 -c "import urllib.request,pathlib; pathlib.Path('.github/prompts').mkdir(parents=True,exist_ok=True); urllib.request.urlretrieve('https://raw.githubusercontent.com/jangabrielsson/plua/main/.github/prompts/install-qa-skills.prompt.md','.github/prompts/install-qa-skills.prompt.md'); print('Done')"
```
> On Windows, replace `python3` with `python` if needed.

**macOS / Linux (curl):**
```bash
mkdir -p .github/prompts && curl -sL https://raw.githubusercontent.com/jangabrielsson/plua/main/.github/prompts/install-qa-skills.prompt.md -o .github/prompts/install-qa-skills.prompt.md
```

**Windows (PowerShell):**
```powershell
New-Item -ItemType Directory -Force .github/prompts | Out-Null; Invoke-WebRequest https://raw.githubusercontent.com/jangabrielsson/plua/main/.github/prompts/install-qa-skills.prompt.md -OutFile .github/prompts/install-qa-skills.prompt.md
```

Then in VS Code Copilot Chat: type `/install-qa-skills` and the agent will download all skills automatically.

---

## What this does
- Downloads `.github/skills/` (7 skills with Lua templates) and `.github/instructions/quickapp-dev.instructions.md` from the public `jangabrielsson/plua` GitHub repo
- Adds or updates the `## QuickApp Development Skills` section in `.github/copilot-instructions.md`

## Step 1 — Download files

**Do NOT use `python3 -c "..."` — multi-line shell strings get mangled.**

Instead, use the `create_file` tool to write the script to a temp file, run it, then delete it:

1. Use `create_file` to create `_install_skills.py` in the workspace root with this content:

```python
import urllib.request, json, pathlib, sys

REPO = 'jangabrielsson/plua'
BRANCH = 'main'

def raw(path):
    return f'https://raw.githubusercontent.com/{REPO}/{BRANCH}/{path}'

print('Fetching file list from GitHub...')
req = urllib.request.Request(
    f'https://api.github.com/repos/{REPO}/git/trees/{BRANCH}?recursive=1',
    headers={'Accept': 'application/vnd.github+json', 'User-Agent': 'plua-skill-installer'}
)
try:
    with urllib.request.urlopen(req) as r:
        tree = json.loads(r.read())
except Exception as e:
    print('ERROR fetching file list:', e)
    sys.exit(1)

files = [
    item['path'] for item in tree['tree']
    if item['type'] == 'blob' and (
        item['path'].startswith('.github/skills/') or
        item['path'] == '.github/instructions/quickapp-dev.instructions.md' or
        item['path'] == '.github/prompts/install-qa-skills.prompt.md'
    )
]

errors = []
for path in files:
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    try:
        urllib.request.urlretrieve(raw(path), p)
        print('OK ', path)
    except Exception as e:
        print('ERR', path, e)
        errors.append(path)

print()
print(f'{len(files) - len(errors)}/{len(files)} files installed.')
if errors:
    print('Failed:', errors)
    sys.exit(1)
```

2. Run in terminal: `python3 _install_skills.py`
   > **Windows:** If `python3` is not found, try `python` instead.

3. Delete the temp file: `rm _install_skills.py` (Windows: `del _install_skills.py`)

If the GitHub API rate-limits you, use the git fallback:
```
git clone --no-checkout --depth=1 https://github.com/jangabrielsson/plua.git _plua_tmp && cd _plua_tmp && git sparse-checkout set .github/skills .github/instructions && git checkout && cd .. && cp -r _plua_tmp/.github/skills .github/ && mkdir -p .github/instructions && cp _plua_tmp/.github/instructions/quickapp-dev.instructions.md .github/instructions/ && rm -rf _plua_tmp
```

## Step 2 — Update .github/copilot-instructions.md

Check whether `.github/copilot-instructions.md` exists in the workspace root:

- **Does not exist** → create `.github/copilot-instructions.md` containing only the section below.
- **Exists and already contains `## QuickApp Development Skills`** → replace that entire section (from the `## QuickApp Development Skills` heading to the end of its bullet list) with the section below.
- **Exists but does not contain that section** → append the section below to the end of the file (preceded by a blank line).

The section to write:

```markdown
## QuickApp Development Skills

Skill version: **1.1.0**

Skills for Fibaro HC3 QuickApp development with plua, auto-discovered from `.github/skills/`.
The instruction file `.github/instructions/quickapp-dev.instructions.md` is auto-applied to all `*.lua` files.

Type a slash command in Copilot chat for detailed reference:

- `/quickapp-api` — full fibaro.*, QuickApp methods, net.HTTPClient, timers
- `/quickapp-types` — all 40+ device types, UI headers, starter templates
- `/quickapp-patterns` — timer loops, refreshStates, HTTP, children, state persistence
- `/hc3-rest-api` — HC3 REST endpoints with examples
- `/lua-basics` — Lua language reference for non-Lua developers
- `/plua-troubleshooting` — port conflicts, debugger warnings, common runtime errors
- `/plua-setup` — install, HC3 credentials, --init-qa, VS Code integration, CLI flags
- `/quickapp-troubleshooting` — HTML in labels, UI callbacks, property persistence, HC3 vs plua differences
- `/hc3vfs` — editing QA files in the VS Code hc3:// virtual filesystem (requires hc3-vfs extension)
```

## Done

Report the following message to the user:

> **QuickApp skills v1.1.0 installed successfully.**
> Ask me anything about QuickApp development, or type a `/` command for detailed reference.
> To check the installed version at any time, ask: *"what QuickApp skill version is installed?"*

When a user asks **"what QuickApp skill version is installed?"** (or similar), look for the `Skill version:` line in the `## QuickApp Development Skills` section of `.github/copilot-instructions.md` and report that version number.

Report:
- How many files were downloaded (and any that failed)
- Whether `.github/copilot-instructions.md` was created, updated, or had the section appended
