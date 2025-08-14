"""
Filesystem operations for PLua.

This module provides luafilesystem-compatible functionality using Python's standard library.
All functions are designed to be called from Lua scripts via the _PY interface.
"""

import os
import stat
import time
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union, Tuple
from plua.lua_bindings import export_to_lua, python_to_lua_table

@export_to_lua()
def fs_attributes(filepath: str, request_name: Optional[str] = None) -> Union[Dict[str, Any], Any, None]:
    """
    Get file attributes (implements lfs.attributes)
    Returns a table with file attributes or specific attribute if request_name provided
    """
    try:
        path = Path(filepath)
        if not path.exists():
            return None, f"No such file or directory: {filepath}", 2
        
        stat_result = path.stat()
        
        # Determine file mode string
        mode_map = {
            stat.S_IFREG: "file",
            stat.S_IFDIR: "directory", 
            stat.S_IFLNK: "link",
            stat.S_IFSOCK: "socket",
            stat.S_IFIFO: "named pipe",
            stat.S_IFCHR: "char device",
            stat.S_IFBLK: "block device"
        }
        
        file_mode = stat_result.st_mode
        mode_type = stat.S_IFMT(file_mode)
        mode_str = mode_map.get(mode_type, "other")
        
        # Build attributes table
        attributes = {
            "dev": stat_result.st_dev,
            "ino": stat_result.st_ino,
            "mode": mode_str,
            "nlink": stat_result.st_nlink,
            "uid": stat_result.st_uid,
            "gid": stat_result.st_gid,
            "rdev": stat_result.st_rdev if hasattr(stat_result, 'st_rdev') else stat_result.st_dev,
            "access": int(stat_result.st_atime),
            "modification": int(stat_result.st_mtime),
            "change": int(stat_result.st_ctime),
            "size": stat_result.st_size,
            "permissions": oct(stat.S_IMODE(file_mode)),
            "blocks": getattr(stat_result, 'st_blocks', 0),
            "blksize": getattr(stat_result, 'st_blksize', 4096)
        }
        
        if request_name:
            return attributes.get(request_name)
        
        return attributes
        
    except OSError as e:
        return None, str(e), e.errno

@export_to_lua()  
def fs_symlinkattributes(filepath: str, request_name: Optional[str] = None) -> Union[Dict[str, Any], Any, None]:
    """
    Get symlink attributes (implements lfs.symlinkattributes)
    Like fs_attributes but for symlinks themselves, adds 'target' field
    """
    try:
        path = Path(filepath)
        if not path.exists() and not path.is_symlink():
            return None, f"No such file or directory: {filepath}", 2
            
        # Use lstat to get symlink info instead of following it
        stat_result = path.lstat()
        
        # Determine file mode string
        mode_map = {
            stat.S_IFREG: "file",
            stat.S_IFDIR: "directory", 
            stat.S_IFLNK: "link",
            stat.S_IFSOCK: "socket",
            stat.S_IFIFO: "named pipe",
            stat.S_IFCHR: "char device",
            stat.S_IFBLK: "block device"
        }
        
        file_mode = stat_result.st_mode
        mode_type = stat.S_IFMT(file_mode)
        mode_str = mode_map.get(mode_type, "other")
        
        # Build attributes table
        attributes = {
            "dev": stat_result.st_dev,
            "ino": stat_result.st_ino,
            "mode": mode_str,
            "nlink": stat_result.st_nlink,
            "uid": stat_result.st_uid,
            "gid": stat_result.st_gid,
            "rdev": stat_result.st_rdev if hasattr(stat_result, 'st_rdev') else stat_result.st_dev,
            "access": int(stat_result.st_atime),
            "modification": int(stat_result.st_mtime),
            "change": int(stat_result.st_ctime),
            "size": stat_result.st_size,
            "permissions": oct(stat.S_IMODE(file_mode)),
            "blocks": getattr(stat_result, 'st_blocks', 0),
            "blksize": getattr(stat_result, 'st_blksize', 4096)
        }
        
        # Add target field for symlinks
        if path.is_symlink():
            try:
                attributes["target"] = str(path.readlink())
            except OSError:
                attributes["target"] = ""
        
        if request_name:
            return attributes.get(request_name)
        
        return attributes
        
    except OSError as e:
        return None, str(e), e.errno

@export_to_lua()
def fs_chdir(path: str) -> Union[bool, Tuple[None, str]]:
    """
    Change current working directory (implements lfs.chdir)
    """
    try:
        os.chdir(path)
        return True
    except OSError as e:
        return None, str(e)

@export_to_lua()
def fs_currentdir() -> Union[str, Tuple[None, str]]:
    """
    Get current working directory (implements lfs.currentdir)
    """
    try:
        return os.getcwd()
    except OSError as e:
        return None, str(e)

@export_to_lua()
def fs_mkdir(dirname: str) -> Union[bool, Tuple[None, str, int]]:
    """
    Create directory (implements lfs.mkdir)
    """
    try:
        os.mkdir(dirname)
        return True
    except OSError as e:
        return None, str(e), e.errno

@export_to_lua()
def fs_rmdir(dirname: str) -> Union[bool, Tuple[None, str, int]]:
    """
    Remove directory (implements lfs.rmdir)
    """
    try:
        os.rmdir(dirname)
        return True
    except OSError as e:
        return None, str(e), e.errno

@export_to_lua()
def fs_dir_open(path: str) -> Union[int, Tuple[None, str]]:
    """
    Open directory for iteration (implements lfs.dir)
    Returns directory handle ID or nil + error
    """
    try:
        if not os.path.isdir(path):
            return None, f"Not a directory: {path}"
        
        entries = os.listdir(path)
        # Store directory state in a global registry
        if not hasattr(fs_dir_open, '_dir_registry'):
            fs_dir_open._dir_registry = {}
            fs_dir_open._next_id = 1
        
        dir_id = fs_dir_open._next_id
        fs_dir_open._next_id += 1
        fs_dir_open._dir_registry[dir_id] = {
            'entries': entries,
            'index': 0,
            'closed': False
        }
        
        return dir_id
    except OSError as e:
        return None, str(e)

@export_to_lua()
def fs_dir_next(dir_id: int) -> Optional[str]:
    """
    Get next directory entry (for lfs.dir iterator)
    """
    if not hasattr(fs_dir_open, '_dir_registry'):
        return None
    
    dir_state = fs_dir_open._dir_registry.get(dir_id)
    if not dir_state or dir_state['closed']:
        return None
    
    if dir_state['index'] >= len(dir_state['entries']):
        return None
    
    entry = dir_state['entries'][dir_state['index']]
    dir_state['index'] += 1
    return entry

@export_to_lua()
def fs_dir_close(dir_id: int) -> bool:
    """
    Close directory iterator (for lfs.dir)
    """
    if not hasattr(fs_dir_open, '_dir_registry'):
        return False
    
    dir_state = fs_dir_open._dir_registry.get(dir_id)
    if dir_state:
        dir_state['closed'] = True
        del fs_dir_open._dir_registry[dir_id]
        return True
    return False

@export_to_lua()
def fs_touch(filepath: str, atime: Optional[float] = None, mtime: Optional[float] = None) -> Union[bool, Tuple[None, str, int]]:
    """
    Set file access and modification times (implements lfs.touch)
    """
    try:
        path = Path(filepath)
        
        # Create file if it doesn't exist
        if not path.exists():
            path.touch()
        
        current_time = time.time()
        
        # Handle time arguments
        if atime is None and mtime is None:
            # Both omitted - use current time
            atime = mtime = current_time
        elif mtime is None:
            # mtime omitted - use atime for both
            mtime = atime
        elif atime is None:
            # atime omitted - use current time
            atime = current_time
        
        os.utime(filepath, (atime, mtime))
        return True
        
    except OSError as e:
        return None, str(e), e.errno

@export_to_lua()
def fs_link(old: str, new: str, symlink: bool = False) -> Union[bool, Tuple[None, str, int]]:
    """
    Create hard or symbolic link (implements lfs.link)
    """
    try:
        if symlink:
            os.symlink(old, new)
        else:
            os.link(old, new)
        return True
    except OSError as e:
        return None, str(e), e.errno

@export_to_lua()
def fs_setmode(file_handle, mode: str) -> Union[Tuple[bool, str], Tuple[None, str]]:
    """
    Set file mode (implements lfs.setmode)
    On Unix/macOS, this is a no-op since binary/text modes are identical
    """
    try:
        # On Unix systems, binary and text modes are the same
        # Return success with previous mode as "binary"
        if mode in ["binary", "text"]:
            return True, "binary"
        else:
            return None, f"Invalid mode: {mode}"
    except Exception as e:
        return None, str(e)
