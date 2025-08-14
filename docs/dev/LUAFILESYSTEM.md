# LuaFileSystem Implementation for EPLua

EPLua now provides a complete, compatible implementation of the LuaFileSystem (lfs) API that can be used in environments where installing binary Lua modules is not possible.

## Overview

This implementation provides a pure Python backend with a Lua frontend that matches the [luafilesystem API specification](https://lunarmodules.github.io/luafilesystem/manual.html#reference) exactly.

## Installation

No installation required! Simply use:

```lua
local lfs = require("lfs")
```

## Minimal _PY Functions Implemented

The following minimal set of Python functions in `src/plua/filesystem.py` provides complete lfs compatibility:

### Core File Operations
- **`fs_attributes(filepath, request_name)`** - Get file attributes (stat information)
- **`fs_symlinkattributes(filepath, request_name)`** - Get symlink attributes (lstat information)

### Directory Operations
- **`fs_currentdir()`** - Get current working directory
- **`fs_chdir(path)`** - Change current working directory
- **`fs_mkdir(dirname)`** - Create directory
- **`fs_rmdir(dirname)`** - Remove directory

### Directory Iteration
- **`fs_dir_open(path)`** - Open directory for iteration
- **`fs_dir_next(dir_id)`** - Get next directory entry
- **`fs_dir_close(dir_id)`** - Close directory iterator

### File Manipulation
- **`fs_touch(filepath, atime, mtime)`** - Set file access/modification times
- **`fs_link(old, new, symlink)`** - Create hard or symbolic links
- **`fs_setmode(file_handle, mode)`** - Set file mode (no-op on Unix)

## Compatible lfs Functions

All standard luafilesystem functions are implemented:

```lua
-- File attributes
local attrs = lfs.attributes("myfile.txt")
local mode = lfs.attributes("myfile.txt", "mode")
local result_table = {}
lfs.attributes("myfile.txt", result_table)

-- Directory operations
local current = lfs.currentdir()
lfs.chdir("/path/to/directory")
lfs.mkdir("new_directory")
lfs.rmdir("old_directory")

-- Directory iteration
for filename in lfs.dir(".") do
    print(filename)
end

-- File operations
lfs.touch("myfile.txt", os.time(), os.time())
lfs.link("source", "target", true) -- true = symbolic link

-- Symlink attributes
local link_attrs = lfs.symlinkattributes("mylink")
print(link_attrs.target) -- Shows link target

-- Directory locking (simplified)
local lock = lfs.lock_dir(".")
if lock then
    lock:free()
end
```

## File Attributes

The attributes table includes all standard lfs fields:

- **`mode`** - File type ("file", "directory", "link", etc.)
- **`size`** - File size in bytes
- **`access`** - Last access time (Unix timestamp)
- **`modification`** - Last modification time (Unix timestamp)
- **`change`** - Last status change time (Unix timestamp)
- **`dev`** - Device ID
- **`ino`** - Inode number
- **`nlink`** - Number of hard links
- **`uid`** - User ID
- **`gid`** - Group ID
- **`rdev`** - Device type (for special files)
- **`permissions`** - File permissions (octal string)
- **`blocks`** - Number of blocks allocated
- **`blksize`** - Optimal block size

For symlinks, `symlinkattributes()` also includes:
- **`target`** - Target of the symbolic link

## Cross-Platform Compatibility

- **Unix/Linux/macOS**: Full functionality including symlinks
- **Windows**: Basic functionality (symlinks may be limited)
- **File locking**: Simplified implementation (platform-independent)

## Usage Examples

See `dev/test_lfs.lua` for comprehensive examples, or `examples/lua/` for user-facing documentation.

## Benefits

1. **No Binary Dependencies**: Pure Python implementation
2. **Full API Compatibility**: Drop-in replacement for luafilesystem
3. **Cross-Platform**: Works everywhere EPLua runs
4. **Lightweight**: Minimal implementation focused on core functionality
5. **Extensible**: Easy to add platform-specific optimizations

## Limitations

- File locking functions (`lfs.lock`, `lfs.unlock`) are simplified stubs
- Platform-specific attributes may vary slightly
- Performance is good but not optimized for massive file operations

This implementation provides everything needed for typical filesystem operations in Lua scripts while maintaining full compatibility with existing luafilesystem-dependent code.
