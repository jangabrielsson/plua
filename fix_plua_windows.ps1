# PLUA Windows Installation Fix Script (PowerShell)
# Run this as: powershell -ExecutionPolicy Bypass -File fix_plua_windows.ps1

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "PLUA WINDOWS INSTALLATION FIX SCRIPT (PowerShell)" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check Python and pip
Write-Host "Step 1: Checking current Python and pip..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    $pipVersion = pip --version 2>&1
    Write-Host "✓ Python: $pythonVersion" -ForegroundColor Green
    Write-Host "✓ Pip: $pipVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Error checking Python/pip: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 2: Uninstall plua
Write-Host "Step 2: Uninstalling plua..." -ForegroundColor Yellow
try {
    $result = pip uninstall plua -y 2>&1
    Write-Host "✓ Uninstalled plua" -ForegroundColor Green
} catch {
    Write-Host "⚠ Uninstall result: $($_.Exception.Message)" -ForegroundColor Orange
}
Write-Host ""

# Step 3: Clear pip cache
Write-Host "Step 3: Clearing pip cache..." -ForegroundColor Yellow
try {
    $result = pip cache purge 2>&1
    Write-Host "✓ Cleared pip cache" -ForegroundColor Green
} catch {
    Write-Host "⚠ Cache clear result: $($_.Exception.Message)" -ForegroundColor Orange
}
Write-Host ""

# Step 4: Clear Python bytecode cache
Write-Host "Step 4: Clearing Python bytecode cache..." -ForegroundColor Yellow
try {
    # Clear __pycache__ directories
    Get-ChildItem -Path . -Recurse -Directory -Name "__pycache__" | ForEach-Object {
        $path = $_.FullName
        Remove-Item -Path $path -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "  Removed: $path" -ForegroundColor Gray
    }
    
    # Also check site-packages
    $sitePackages = python -c "import site; print(';'.join([site.USER_SITE] + site.getsitepackages()))" 2>$null
    if ($sitePackages) {
        $sitePackages.Split(';') | ForEach-Object {
            $sitePath = $_
            if (Test-Path $sitePath) {
                Get-ChildItem -Path $sitePath -Recurse -Directory -Name "__pycache__" -ErrorAction SilentlyContinue | ForEach-Object {
                    $path = $_.FullName
                    Remove-Item -Path $path -Recurse -Force -ErrorAction SilentlyContinue
                    Write-Host "  Removed: $path" -ForegroundColor Gray
                }
            }
        }
    }
    Write-Host "✓ Cleared Python bytecode cache" -ForegroundColor Green
} catch {
    Write-Host "⚠ Cache clear result: $($_.Exception.Message)" -ForegroundColor Orange
}
Write-Host ""

# Step 5: Clear Python module cache
Write-Host "Step 5: Clearing Python module cache..." -ForegroundColor Yellow
try {
    $result = python -c "import sys; import importlib; importlib.invalidate_caches(); [sys.modules.pop(k) for k in list(sys.modules.keys()) if k.startswith('plua')]; print('Module cache cleared')" 2>&1
    Write-Host "✓ $result" -ForegroundColor Green
} catch {
    Write-Host "⚠ Module cache clear result: $($_.Exception.Message)" -ForegroundColor Orange
}
Write-Host ""

# Step 6: Reinstall plua
Write-Host "Step 6: Reinstalling plua with forced refresh..." -ForegroundColor Yellow
try {
    Write-Host "  Installing without dependencies first..." -ForegroundColor Gray
    $result1 = pip install plua --force-reinstall --no-cache-dir --no-deps 2>&1
    Write-Host "  Installing with dependencies..." -ForegroundColor Gray
    $result2 = pip install plua --force-reinstall --no-cache-dir 2>&1
    Write-Host "✓ Reinstalled plua" -ForegroundColor Green
} catch {
    Write-Host "✗ Reinstall failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Please check your internet connection and try again." -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 7: Verify installation
Write-Host "Step 7: Verifying installation..." -ForegroundColor Yellow
try {
    $showResult = pip show plua 2>&1
    Write-Host "✓ Installation verified:" -ForegroundColor Green
    Write-Host $showResult -ForegroundColor Gray
} catch {
    Write-Host "✗ Verification failed: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Step 8: Test debug code presence
Write-Host "Step 8: Testing debug code presence..." -ForegroundColor Yellow
try {
    $debugTest = python -c "import plua.interpreter; import inspect; code = inspect.getsource(plua.interpreter.LuaInterpreter.initialize); print('stderr' in code and 'PLUA DEBUG OUTPUT' in code)" 2>&1
    if ($debugTest -eq "True") {
        Write-Host "✓ Debug code is present in installed version" -ForegroundColor Green
    } else {
        Write-Host "✗ Debug code is MISSING: $debugTest" -ForegroundColor Red
        Write-Host "  This indicates a persistent cache issue or package problem." -ForegroundColor Red
    }
} catch {
    Write-Host "✗ Debug test failed: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Step 9: Create and run test script
Write-Host "Step 9: Testing plua execution..." -ForegroundColor Yellow
try {
    # Create test script
    'print("Hello from plua!")' | Out-File -FilePath "test_debug.lua" -Encoding ASCII
    Write-Host "  Created test script: test_debug.lua" -ForegroundColor Gray
    
    # Run plua and capture both stdout and stderr
    Write-Host "  Running plua test_debug.lua..." -ForegroundColor Gray
    $pluaProcess = Start-Process -FilePath "plua" -ArgumentList "test_debug.lua" -NoNewWindow -Wait -PassThru -RedirectStandardOutput "plua_stdout.tmp" -RedirectStandardError "plua_stderr.tmp"
    
    # Read output files
    $stdout = Get-Content "plua_stdout.tmp" -ErrorAction SilentlyContinue | Out-String
    $stderr = Get-Content "plua_stderr.tmp" -ErrorAction SilentlyContinue | Out-String
    
    Write-Host "  Exit code: $($pluaProcess.ExitCode)" -ForegroundColor Gray
    
    if ($stdout) {
        Write-Host "  STDOUT:" -ForegroundColor Gray
        Write-Host $stdout -ForegroundColor White
    }
    
    if ($stderr) {
        Write-Host "  STDERR:" -ForegroundColor Gray
        Write-Host $stderr -ForegroundColor White
        
        if ($stderr -like "*PLUA DEBUG OUTPUT*") {
            Write-Host "✓ Debug output is working!" -ForegroundColor Green
        } else {
            Write-Host "✗ Debug output is missing from stderr" -ForegroundColor Red
        }
    } else {
        Write-Host "✗ No stderr output - debug messages are missing" -ForegroundColor Red
    }
    
    # Clean up temporary files
    Remove-Item "test_debug.lua", "plua_stdout.tmp", "plua_stderr.tmp" -ErrorAction SilentlyContinue
    
} catch {
    Write-Host "✗ Test execution failed: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "INSTALLATION FIX COMPLETE" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "If you still see issues:" -ForegroundColor Yellow
Write-Host "1. Try running the Python diagnostic: python debug_installation.py" -ForegroundColor White
Write-Host "2. Create a fresh virtual environment:" -ForegroundColor White
Write-Host "   python -m venv fresh_plua_env" -ForegroundColor Gray
Write-Host "   fresh_plua_env\Scripts\activate" -ForegroundColor Gray
Write-Host "   pip install plua" -ForegroundColor Gray
Write-Host "   plua your_script.lua" -ForegroundColor Gray
Write-Host ""
Write-Host "Press any key to continue..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
