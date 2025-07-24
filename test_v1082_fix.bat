@echo off
echo ============================================================
echo TESTING PLUA v1.0.82 WITH FIXED LUA FILES  
echo ============================================================
echo.

echo Step 1: Upgrading to plua v1.0.82 (contains lua files)...
pip install plua==1.0.82 --force-reinstall --no-cache-dir
echo.

echo Step 2: Verifying lua files are included...
python -c "import os, site; sites = [site.USER_SITE] + site.getsitepackages(); lua_dirs = [os.path.join(s, 'lua') for s in sites if s and os.path.exists(os.path.join(s, 'lua'))]; print('Lua directories found:', lua_dirs); [print(f'  {d}: {os.listdir(d)[:5]}') for d in lua_dirs]"
echo.

echo Step 3: Testing plua execution...
echo print("Hello from plua v1.0.82 with lua files!") > test_v1082.lua
echo Running plua test_v1082.lua...
echo.
plua test_v1082.lua
echo.

echo Step 4: Cleanup...
del test_v1082.lua
echo.

echo ============================================================
echo If plua runs successfully without "init.lua not found" errors,
echo the fix is working! The lua directory is now properly included.
echo ============================================================
pause
