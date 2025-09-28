# Changelog

All notable changes to this project will be documented in this file.

## [v1.2.46] - 2025-09-28



#### Commits since v1.2.45:

- ✨ **Feature**: update quickApp import endpoint to use a more general path
- ✨ **Feature**: update QwikAppChild library version to 2.5 and add child removal hook functionality



## [v1.2.45] - 2025-09-23



#### Commits since v1.2.44:

- ✨ **Feature**: implement Multi PositionSwitch functionality and enhance proxy error handling



## [v1.2.44] - 2025-09-21



#### Commits since v1.2.43:

- 📝 Fix proxy connection IP address and enhance local IP detection method



## [v1.2.43] - 2025-09-17



#### Commits since v1.2.42:

- ✨ **Feature**: add JSON encoding optimization and initialize array utility



## [v1.2.42] - 2025-09-17



#### Commits since v1.2.41:

- ✨ **Feature**: add file merging header



## [v1.2.41] - 2025-09-16



#### Commits since v1.2.40:

- ✨ **Feature**: enhance proxy handling to log UI updates for existing proxies



## [v1.2.40] - 2025-09-15



#### Commits since v1.2.39:

- ✨ **Feature**: add support for multiple values in UI event handling



## [v1.2.39] - 2025-09-14



#### Commits since v1.2.38:

- ✨ **Feature**: update FastAPI host configuration to allow external access



## [v1.2.38] - 2025-09-11



#### Commits since v1.2.37:

- 🧪 **Test**: add script to verify Windows subprocess encoding fix



## [v1.2.37] - 2025-09-10



#### Commits since v1.2.36:

- 🐛 **Fix**: rename 'executable' to 'interpreter' in VSCode launch configuration



## [v1.2.36] - 2025-09-10



#### Commits since v1.2.35:

- 📝 Add QuickApps tutorials and examples; enhance emulator and API functionality



## [v1.2.35] - 2025-09-03



#### Commits since v1.2.34:

- ✨ **Feature**: add better QA functionality and improve HTTP client options (checkCertificate)



## [v1.2.34] - 2025-09-01



#### Commits since v1.2.33:

- ✨ **Feature**: add functions to list sprinklers and location, sort global variables
- ✨ **Feature**: add functions to list alarms, climate, and profiles



## [v1.2.33] - 2025-08-31



#### Commits since v1.2.32:

- 🐛 **Fix**: handle nil path in file existence check
- ✨ **Feature**: add launch configuration for Lua debugging
- 📝 Stop tracking .vscode/launch.json (added to .gitignore)
- ✨ **Feature**: enhance findIdAndName function to include filename in search
- ✨ **Feature**: update launch configuration arguments and add new ProjTest file
- ✨ **Feature**: enhance error handling and add exit function to OS environment feat(offline): update event handling logic in setup function



## [v1.2.32] - 2025-08-29



#### Commits since v1.2.31:

- ✨ **Feature**: implement event publishing in QuickApp initialization fix(emulator): correct response handling and logging in HC3_CALL refactor(helper): improve logging and remove commented-out code feat(offline): enhance setup function to handle scene activation events fix(json): optimize prettyJsonFlat function by removing unnecessary code feat(cli): add host IP retrieval to configuration in CLI



## [v1.2.31] - 2025-08-29



#### Commits since v1.2.30:

- ✨ **Feature**: add event publishing functionality to setup



## [v1.2.30] - 2025-08-29



#### Commits since v1.2.29:

- 🐛 **Fix**: os.time reported wrong when setting --%%time



## [v1.2.29] - 2025-08-28



#### Commits since v1.2.28:

- ✨ **Feature**: add restart functionality and update variable handling
- ✨ **Feature**: add MIT License file and update README with license badge
- ✨ **Feature**: add backup and test directories to .gitignore



## [v1.2.28] - 2025-08-27



#### Commits since v1.2.27:

- ✨ **Feature**: add new launch configuration for testing FQA and update README options refactor(emulator): improve directory handling and event processing fix(fibaro_api): update event structure for device property updates fix(quickapp): handle missing args in action calls fix(tools): ensure temp directory is created before file operations



## [v1.2.27] - 2025-08-25



#### Commits since v1.2.26:

- ✨ **Feature**: add support for setting QuickApp window background color with new function and CSS injection bug(emulator): fixed project file generation bug
- ♻️ **Refactor**: remove debug print statement and improve error handling refactor(json): move quote function and optimize key handling in prettyJsonFlat



## [v1.2.26] - 2025-08-21



#### Commits since v1.2.25:

- ✨ **Feature**: enhance loadLuaFile function to handle directory checks and improve error handling feat(lua_bindings): add is_directory function to check if a path is a directory



## [v1.2.25] - 2025-08-21



#### Commits since v1.2.24:

- ✨ **Feature**: add debug print statement when loading Lua files



## [v1.2.24] - 2025-08-21



#### Commits since v1.2.23:

- ✨ **Feature**: add authentication details and example API calls to FIBARO_REST documentation



## [v1.2.23] - 2025-08-21



#### Commits since v1.2.22:

- ✨ **Feature**: enhance FIBARO_REST documentation with MCP usage patterns and examples
- ✨ **Feature**: enhance system info detection and add user validation in test script



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
