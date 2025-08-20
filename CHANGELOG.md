# Changelog

All notable changes to this project will be documented in this file.

## [v1.2.22] - 2025-08-20



#### Commits since v1.2.21:

- 📝 `fastapi_process.py` to convert LuaTable objects before IPC. - Improved error handling in `quickapp_ui.html` for select and multi-select elements to provide better user feedback. - Created a new test script `test_rich_colors.py` to validate console color detection and configuration.
- ✨ **Feature**: integrate Rich for enhanced terminal output and add styled print functions
- 📚 **Docs**: enhance device management section with examples and clarifications
- 📝 Added FIbaro REST documentation



## [v1.2.21] - 2025-08-20



#### Commits since v1.2.20:

- ✨ **Feature**: update upload functionality and add noproxy support



## [v1.2.20] - 2025-08-19



#### Commits since v1.2.19:

- ✨ **Feature**: add wake_network_device functionality to handle device wake-up on connection errors feat(backup): refactor backup functions to accept path and now parameters for improved flexibility feat(lua_bindings): implement wake_network_device and py_sleep functions for enhanced Lua-Python integration



## [v1.2.19] - 2025-08-18



#### Commits since v1.2.18:

- ✨ **Feature**: update backup tool to include encrypted quickApp filenames
- ✨ **Feature**: enhance backup functionality to include older versions of files



## [v1.2.18] - 2025-08-18



#### Commits since v1.2.17:

- ✨ **Feature**: implement backup tool for HC3 with support for QuickApps, Scenes, and more



## [v1.2.17] - 2025-08-18



#### Commits since v1.2.16:

- ✨ **Feature**: add sorting to tools and enhance pack/unpack functionality feat(tools): refactor getFQA and add info2FQA for improved structure handling refactor: remove obsolete test_nuitka.lua script
- 📝 Loads ~/.plua/user_funs.lua if available



## [v1.2.16] - 2025-08-18

Fixed launch.json with correct options

- ✨ **Feature**: Add automatic changelog generation and update release notes options
All notable changes to this project will be documented in this file.

## [v1.2.15] - 2025-08-18

#### Commits since v1.2.14:

- ✨ **Feature**: Add automatic changelog generation and update release notes options



## [v1.2.14] - 2025-08-18

### Features
- ✨ **Feature**: Implement pretty JSON encoding and enhance Lua table serialization

### Improvements
- ♻️ **Refactor**: Clean up debug message handling and improve output formatting
- 🔧 **Chore**: Remove unused json.lua file

## [v1.2.13] - 2025-08-17

### Bug Fixes
- 🐛 **Fix**: Enhance Windows support in build_nuitka script with UPX and threading adjustments
- 🐛 **Fix**: Update release success messages and improve output clarity

## [v1.2.12] - 2025-08-17

### Features
- ✨ **Feature**: Add prompt_toolkit for enhanced REPL functionality

### Improvements
- ♻️ **Refactor**: Remove unused input prompts from tasks configuration

## [v1.2.11] - 2025-08-17

### Features
- ✨ **Feature**: Add new test cases and diagnostic mode for improved functionality

### Bug Fixes
- 🐛 **Fix**: Add file existence checks and convert file paths to strings in tool functions
- 🐛 **Fix**: Update command arguments to use '--tool' instead of '--fibaro' for consistency

## [v1.2.10] - 2025-08-16

### Features
- ✨ **Feature**: Implement CI-optimized Nuitka build script with minimal dependencies

### Bug Fixes
- 🐛 **Fix**: GitHub workflow build failures

### Improvements
- 🔧 **Chore**: Add CI-optimized Nuitka build script

---

*This changelog is automatically maintained by the release script starting from v1.2.15+*
