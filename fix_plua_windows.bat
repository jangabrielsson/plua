@echo off
echo ====================================================
echo PLUA WINDOWS INSTALLATION FIX SCRIPT
echo ====================================================
echo.

echo Step 1: Checking current Python and pip...
python --version
pip --version
echo.

echo Step 2: Uninstalling plua...
pip uninstall plua -y
echo.

echo Step 3: Clearing pip cache...
pip cache purge
echo.

echo Step 4: Clearing Python bytecode cache...
echo Clearing __pycache__ directories...
for /d /r %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
echo.

echo Step 5: Clearing Python module cache...
python -c "import sys; import importlib; importlib.invalidate_caches(); [sys.modules.pop(k) for k in list(sys.modules.keys()) if k.startswith('plua')]; print('Module cache cleared')"
echo.

echo Step 6: Reinstalling plua with forced refresh...
pip install plua --force-reinstall --no-cache-dir --no-deps
pip install plua --force-reinstall --no-cache-dir
echo.

echo Step 7: Verifying installation...
pip show plua
echo.

echo Step 8: Testing debug code presence...
python -c "import plua.interpreter; import inspect; code = inspect.getsource(plua.interpreter.LuaInterpreter.initialize); print('Debug code present:', 'stderr' in code and 'PLUA DEBUG OUTPUT' in code)"
echo.

echo Step 9: Creating test script...
echo print("Hello from plua!") > test_debug.lua
echo.

echo Step 10: Testing plua execution...
echo Running plua test_debug.lua...
plua test_debug.lua
echo.

echo Step 11: Cleanup...
del test_debug.lua
echo.

echo ====================================================
echo INSTALLATION FIX COMPLETE
echo ====================================================
echo.
echo If you still see "False" in step 8 or no debug output in step 10,
echo please run the Python diagnostic script:
echo   python debug_installation.py
echo.
pause
