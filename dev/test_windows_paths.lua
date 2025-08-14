-- Test Windows path handling
print("=== Windows Path Test ===")
print("Config paths:")
print("  enginePath:", _PY.config.enginePath)
print("  luaLibPath:", _PY.config.luaLibPath)
print("  fileSeparator:", _PY.config.fileSeparator)
print("  pathSeparator:", _PY.config.pathSeparator)
print("  isWindows:", _PY.config.isWindows)

-- Test if we can access these paths without errors
print("=== End Windows Path Test ===")
