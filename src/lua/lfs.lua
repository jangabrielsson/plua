-- LuaFileSystem compatible implementation for EPLua
-- Implements the luafilesystem API using dynamic Python module loading
-- Compatible with: https://lunarmodules.github.io/luafilesystem/manual.html

local lfs = {}

-- Dynamically load the filesystem Python module
local fs_module = nil

local function ensure_filesystem_loaded()
  if not fs_module then
    --print("Loading filesystem module dynamically...")
    fs_module = _PY.loadPythonModule("filesystem")
    if fs_module.error then
      error("Failed to load filesystem module: " .. fs_module.error)
    end
    --print("Filesystem module loaded successfully!")
  end
  return fs_module
end

-- File attributes function
-- lfs.attributes(filepath [, request_name | result_table])
function lfs.attributes(filepath, request_name_or_table)
  local fs = ensure_filesystem_loaded()
  
  if type(request_name_or_table) == "string" then
    -- Single attribute request
    return fs.fs_attributes(filepath, request_name_or_table)
  elseif type(request_name_or_table) == "table" then
    -- Fill provided table with attributes
    local attrs = fs.fs_attributes(filepath)
    if attrs then
      -- Convert Lupa table to Lua table if needed
      if type(attrs) == "userdata" then
        -- This is a Lupa table, need to copy values manually
        for _, key in ipairs({"dev", "ino", "mode", "nlink", "uid", "gid", "rdev", 
                             "access", "modification", "change", "size", "permissions", 
                             "blocks", "blksize"}) do
          if attrs[key] ~= nil then
            request_name_or_table[key] = attrs[key]
          end
        end
      else
        -- Regular table, can use pairs
        for k, v in pairs(attrs) do
          request_name_or_table[k] = v
        end
      end
      return request_name_or_table
    else
      return nil
    end
  else
    -- Return full attributes table
    return fs.fs_attributes(filepath)
  end
end

-- Symlink attributes function  
-- lfs.symlinkattributes(filepath [, request_name])
function lfs.symlinkattributes(filepath, request_name)
  local fs = ensure_filesystem_loaded()
  return fs.fs_symlinkattributes(filepath, request_name)
end

-- Change directory
-- lfs.chdir(path)
function lfs.chdir(path)
  local fs = ensure_filesystem_loaded()
  return fs.fs_chdir(path)
end

-- Get current directory
-- lfs.currentdir()
function lfs.currentdir()
  local fs = ensure_filesystem_loaded()
  return fs.fs_currentdir()
end

-- Make directory
-- lfs.mkdir(dirname)
function lfs.mkdir(dirname)
  local fs = ensure_filesystem_loaded()
  return fs.fs_mkdir(dirname)
end

-- Remove directory
-- lfs.rmdir(dirname)
function lfs.rmdir(dirname)
  local fs = ensure_filesystem_loaded()
  return fs.fs_rmdir(dirname)
end

-- Directory iterator
-- iter, dir_obj = lfs.dir(path)
function lfs.dir(path)
  local fs = ensure_filesystem_loaded()
  local dir_id, err = fs.fs_dir_open(path)
  if not dir_id then
    error(err or "Failed to open directory")
  end
  
  -- Create directory object
  local dir_obj = {
    _id = dir_id,
    _closed = false
  }
  
  -- Iterator function
  local function dir_iter(dir_state)
    if dir_state._closed then
      return nil
    end
    return fs.fs_dir_next(dir_state._id)
  end
  
  -- Directory object methods
  function dir_obj:next()
    if self._closed then
      return nil
    end
    return fs.fs_dir_next(self._id)
  end
  
  function dir_obj:close()
    if not self._closed then
      fs.fs_dir_close(self._id)
      self._closed = true
    end
  end
  
  -- Set up metatable for cleanup
  setmetatable(dir_obj, {
    __gc = function(self)
      self:close()
    end
  })
  
  return dir_iter, dir_obj
end

-- Touch file (set access/modification times)
-- lfs.touch(filepath [, atime [, mtime]])
function lfs.touch(filepath, atime, mtime)
  local fs = ensure_filesystem_loaded()
  return fs.fs_touch(filepath, atime, mtime)
end

-- Create link
-- lfs.link(old, new [, symlink])
function lfs.link(old, new, symlink)
  local fs = ensure_filesystem_loaded()
  return fs.fs_link(old, new, symlink or false)
end

-- Set file mode (binary/text)
-- lfs.setmode(file, mode)
function lfs.setmode(file, mode)
  local fs = ensure_filesystem_loaded()
  return fs.fs_setmode(file, mode)
end

-- Lock directory (simplified implementation)
-- lfs.lock_dir(path [, seconds_stale])
function lfs.lock_dir(path, seconds_stale)
  -- Simplified implementation - creates a lockfile
  local lockfile = path .. "/lockfile.lfs"
  
  -- Check if lock exists
  local attrs = lfs.attributes(lockfile)
  if attrs then
    -- Check if stale
    if seconds_stale and seconds_stale < math.huge then
      local current_time = os.time()
      if current_time - attrs.modification > seconds_stale then
        -- Lock is stale, remove it
        os.remove(lockfile)
      else
        return nil, "File exists"
      end
    else
      return nil, "File exists"
    end
  end
  
  -- Create lock file
  local f = io.open(lockfile, "w")
  if not f then
    return nil, "Cannot create lock file"
  end
  f:write(tostring(os.time()))
  f:close()
  
  -- Return lock object
  local lock = {
    _lockfile = lockfile
  }
  
  function lock:free()
    if self._lockfile then
      os.remove(self._lockfile)
      self._lockfile = nil
    end
  end
  
  setmetatable(lock, {
    __gc = function(self)
      self:free()
    end
  })
  
  return lock
end

-- File locking functions (simplified - platform dependent)
-- lfs.lock(filehandle, mode [, start [, length]])
function lfs.lock(filehandle, mode, start, length)
  -- Note: File locking is platform-specific and complex
  -- This is a placeholder that always returns true
  -- Real implementation would need platform-specific code
  return true
end

-- lfs.unlock(filehandle [, start [, length]])
function lfs.unlock(filehandle, start, length)
  -- Note: File locking is platform-specific and complex
  -- This is a placeholder that always returns true
  -- Real implementation would need platform-specific code
  return true
end

-- Version information (for compatibility)
lfs._VERSION = "EPLua LFS 1.0"

return lfs
