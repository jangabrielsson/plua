@echo off
echo ============================================================
echo TESTING PLUA v1.0.81 WITH DEBUG OUTPUT
echo ============================================================
echo.

echo Step 1: Upgrading to plua v1.0.81...
pip install plua==1.0.81 --force-reinstall --no-cache-dir
echo.

echo Step 2: Verifying debug code is present...
python -c "import plua.interpreter; import inspect; code = inspect.getsource(plua.interpreter.LuaInterpreter.initialize); result = 'stderr' in code and 'PLUA DEBUG OUTPUT' in code; print('Debug code present:', result); print('SUCCESS!' if result else 'FAILED - debug code still missing')"
echo.

echo Step 3: Testing plua execution with debug output...
echo print("Hello from plua v1.0.81!") > test_debug_v1081.lua
echo Running plua test_debug_v1081.lua...
echo Expected: You should see debug output starting with "PLUA DEBUG OUTPUT"
echo.
plua test_debug_v1081.lua
echo.

echo Step 4: Cleanup...
del test_debug_v1081.lua
echo.

echo ============================================================
echo TEST COMPLETE
echo ============================================================
echo.
echo If you see "Debug code present: True" in step 2 and debug output 
echo starting with "PLUA DEBUG OUTPUT" in step 3, the fix is working!
echo.
pause
