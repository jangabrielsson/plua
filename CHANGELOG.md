# Changelog

All notable changes to this project will be documented in this file.

## [v1.3.3] - 2026-04-26



#### Commits since v1.3.2:

- ✨ **Feature**: Enhance HTTP client with streaming support and improve request handling



## [v1.3.2] - 2026-04-24



#### Commits since v1.3.1:

- ✨ **Feature**: Update type hints to support optional values in various modules



## [v1.3.1] - 2026-04-24



#### Commits since v1.3.0:

- ✨ **Feature**: Implement speed library for time management and debugging enhancements
- 📚 **Docs**: Add friendly overview of PLua architecture for QuickApp developers



## [v1.3.0] - 2026-04-23



#### Commits since v1.2.79:

- 📝 Refactor PLua engine for improved cross-thread communication and port management
- 📚 **Docs**: Revise PLua architecture documentation for clarity and detail on system components and data flow
- 📚 **Docs**: Enhance HC3 write safety documentation in SKILL.md for better clarity on silent failures and defensive patterns
- ✨ **Feature**: add hc3-write-safety skill



## [v1.2.79] - 2026-04-22



#### Commits since v1.2.78:

- ✨ **Feature**: Update version handling in create-release script and enforce C locale for Lua pattern consistency
- 🐛 **Fix**: Restrict workflow triggers to manual only for build executables and release pipeline



## [v1.2.78] - 2026-04-22



#### Commits since v1.2.77:

- ✨ **Feature**: Add quality checks for ruff, pyright, and pytest before release
- 📝 Refactor type hints and imports across multiple modules



## [v1.2.77] - 2026-04-22



#### Commits since v1.2.76:

- 🐛 **Fix**: Improve UTF-8 handling in error messages and diagnostics



## [v1.2.76] - 2026-04-22



#### Commits since v1.2.75:

- ✨ **Feature**: Add UTF test script and enhance JSON array handling in emulator



## [v1.2.75] - 2026-04-22



#### Commits since v1.2.74:

- ✨ **Feature**: Improve HTTP request handling for UTF-8 encoding and enhance JSON escaping



## [v1.2.74] - 2026-04-13



#### Commits since v1.2.73:

- ✨ **Feature**: Update error handling in validate function and include timestamp in refreshEvent



## [v1.2.73] - 2026-04-06



#### Commits since v1.2.72:

- ✨ **Feature**: Enhance JSON encoding to handle additional control characters and update test error handling



## [v1.2.72] - 2026-04-06



#### Commits since v1.2.71:

- ✨ **Feature**: Enhance luaToFQA function to return additional info and update quick app variable handling



## [v1.2.71] - 2026-04-06



#### Commits since v1.2.70:

- ✨ **Feature**: Update variable handling in emulator and add initialization function in QuickApp



## [v1.2.70] - 2026-04-06



#### Commits since v1.2.69:

- ✨ **Feature**: Enhance UI components and update variable handling in emulator
- ✨ **Feature**: Add skill description improvement and evaluation scripts
- ✨ **Feature**: Update Copilot instructions and add QwikAppChild library documentation



## [v1.2.69] - 2026-04-01



#### Commits since v1.2.68:

- ✨ **Feature**: Enhance HTTP client timeout settings and improve WebSocket message handling



## [v1.2.68] - 2026-03-31



#### Commits since v1.2.67:

- ✨ **Feature**: Enhance WebSocket handling to respond to ping messages



## [v1.2.67] - 2026-03-31



#### Commits since v1.2.66:

- ✨ **Feature**: Add corErr.lua for API error handling and enhance QA_children.lua with child creation logging



## [v1.2.66] - 2026-03-30



#### Commits since v1.2.65:

- ✨ **Feature**: Enhance updateQAparts function to log skipped quickAppVariables when 'nq' flag is present



## [v1.2.65] - 2026-03-30



#### Commits since v1.2.64:

- ✨ **Feature**: Update HTTPTestQA to use dynamic location for weather API and modify updateQA function to accept flags
- ✨ **Feature**: Add hc3vfs skill for managing Fibaro HC3 QuickApp files in VS Code
- ✨ **Feature**: Add HTTPTestQA script for testing HTTP requests in QuickApps
- ✨ **Feature**: Update SKILL.md with VS Code integration details and debugging configuration
- ✨ **Feature**: Enhance WebSocket management for QuickApps with per-QA tracking and UI reload support
- ✨ **Feature**: Enhance colorController value formatting for improved RGB display
- ♻️ **Refactor**: Simplify string formatting logic in updateProperty API endpoint
- ✨ **Feature**: Update QuickApp skill version to 1.1.0 in instructions and prompts
- ✨ **Feature**: Add Hue Bridge QuickApp integration with variable management for secure API access
- ✨ **Feature**: Implement Binary Switch Status QuickApp with real-time updates and HTML rendering
- ✨ **Feature**: Add Device Sync Sensor implementation with RefreshStateSubscriber for real-time updates
- 📚 **Docs**: Update HC3 REST API documentation with detailed endpoint parameters and examples for energy consumption
- 📚 **Docs**: Update QuickApp variable declaration examples for clarity and correctness
- 📝 fix
- ✨ **Feature**: Add quickapp-troubleshooting skill and update documentation for QuickApp development
- 📝 Update HC3 REST API documentation with detailed endpoint references for devices, energy & climate, scenes & automation, system configuration, and miscellaneous features. Added new markdown files for assets and improved descriptions for better clarity and usability.
- 📚 **Docs**: Clarify installation instructions for plua QuickApp development skills
- ♻️ **Refactor**: Update QuickApp development skills instructions for clarity and auto-discovery
- ✨ **Feature**: Add installation prompt for plua QuickApp development skills
- 📝 Add QuickApp device type templates and documentation



## [v1.2.64] - 2026-03-25



#### Commits since v1.2.63:

- 📝 Fix updateQA



## [v1.2.63] - 2026-03-23



#### Commits since v1.2.62:

- ✨ **Feature**: Enhance Lua integration and fix potential crash issues
- ✨ **Feature**: add .luarc.json configuration and refactor variable scopes in multiple files
- 📚 **Docs**: add HC3 credentials setup instructions to README
- 🐛 **Fix**: update error handling in QuickApp and improve initialization process



## [v1.2.62] - 2026-03-11



#### Commits since v1.2.61:

- 🐛 **Fix**: improve loadQA function to handle options more effectively



## [v1.2.61] - 2026-03-11



#### Commits since v1.2.60:

- 🐛 **Fix**: correct internal storage key and adjust debug logging in TestHelper



## [v1.2.60] - 2026-03-11



#### Commits since v1.2.59:

- ✨ **Feature**: enhance TestHelper with internal storage management and debug logging fix: improve startServer function to handle pending messages correctly in WebSocket refactor: update setTimeout and setInterval to use coroutine for better error handling



## [v1.2.59] - 2026-03-10



#### Commits since v1.2.58:

- ✨ **Feature**: add iOS location tracking QuickApp and geofence event publishing



## [v1.2.58] - 2026-03-09



#### Commits since v1.2.57:

- 🐛 **Fix**: switch to SelectorEventLoop on Windows for compatibility with aiomqtt



## [v1.2.57] - 2026-03-08



#### Commits since v1.2.56:

- ✨ **Feature**: add TLS certificate verification options for MQTT client
- 📚 **Docs**: remove outdated debug handler examples from EventLib documentation
- 📚 **Docs**: enhance EventLib documentation with detailed examples and key points for initialization
- 📚 **Docs**: update EventLib documentation with new examples and clarify device ID usage
- 📝 Add EventLib documentation and examples; update eventlib.lua with new features



## [v1.2.56] - 2026-02-25



#### Commits since v1.2.55:

- ✨ **Feature**: update MQTT example and integrate MQTT into Emulator environment



## [v1.2.55] - 2026-02-25



#### Commits since v1.2.54:

- ✨ **Feature**: add MQTT event handling tests and improve net.Client connection options



## [v1.2.54] - 2026-01-14



#### Commits since v1.2.53:

- ✨ **Feature**: implement UTF-8 handling improvements across Lua and Python integration
- ✨ **Feature**: enhance JSON handling with UTF-8 support and error logging in to_json functions



## [v1.2.53] - 2026-01-09



#### Commits since v1.2.52:

- ✨ **Feature**: add loadFQA function and installQuickAppFromInfo method for enhanced quick app handling



## [v1.2.52] - 2026-01-03



#### Commits since v1.2.51:

- 📝 Add donation button to README
- ✨ **Feature**: populate QAs.json with detailed entries for EventRunner6, Yahue, NTFY, and Dirigera
- ✨ **Feature**: add initial QAs.json file for QA updater



## [v1.2.51] - 2025-10-11



#### Commits since v1.2.50:

- 🐛 **Fix**: enhance error reporting for included files in Emulator:startQA for better debugging
- 📝 Add NTFY QuickApp documentation for Fibaro HC3 integration
- 🐛 **Fix**: update WebSocketClient to WebSocketClientTls for secure connection



## [v1.2.50] - 2025-10-10



#### Commits since v1.2.49:

- ✨ **Feature**: add NTFY Notification Service and publishing options schema documentation
- 🐛 **Fix**: correct escape character handling in json.lua



## [v1.2.49] - 2025-10-09



#### Commits since v1.2.48:

- ✨ **Feature**: add timer function and child definition verification in QwikAppChild



## [v1.2.48] - 2025-10-09



#### Commits since v1.2.47:

- ✨ **Feature**: add toggle functionality for auto mode in QuickApp and update UI text dynamically
- 🐛 **Fix**: remove unnecessary print statement in createChild function
- ✨ **Feature**: add POST endpoint for quickApp to load data
- ✨ **Feature**: update QwikAppChild library version to 2.5.1 and improve error handling in createChild function



## [v1.2.47] - 2025-09-28



#### Commits since v1.2.46:

- ✨ **Feature**: comment out quickApp POST endpoint in router



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
