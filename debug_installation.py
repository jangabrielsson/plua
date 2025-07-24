#!/usr/bin/env python3
"""
Comprehensive installation and cache debugging script for plua on Windows
This script helps diagnose and fix installation issues, especially cache-related problems.
"""

import os
import sys
import shutil
import subprocess
import importlib
import inspect
from pathlib import Path


def run_command(cmd, capture_output=True):
    """Run a command and return the result"""
    try:
        if isinstance(cmd, str):
            # Use shell=True for string commands
            result = subprocess.run(cmd, shell=True, capture_output=capture_output, text=True, timeout=30)
        else:
            # Use shell=False for list commands
            result = subprocess.run(cmd, capture_output=capture_output, text=True, timeout=30)
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except Exception as e:
        return -1, "", str(e)


def find_python_cache_dirs():
    """Find all Python cache directories"""
    cache_dirs = []
    
    # User cache directory
    import tempfile
    user_cache = os.path.join(tempfile.gettempdir(), f"python-cache-{os.getenv('USERNAME', 'user')}")
    if os.path.exists(user_cache):
        cache_dirs.append(user_cache)
    
    # Python __pycache__ directories
    try:
        import site
        for site_dir in [site.USER_SITE] + site.getsitepackages():
            if site_dir and os.path.exists(site_dir):
                for root, dirs, files in os.walk(site_dir):
                    if '__pycache__' in dirs:
                        cache_dirs.append(os.path.join(root, '__pycache__'))
    except Exception:
        pass
    
    return cache_dirs


def clear_python_caches():
    """Clear all Python caches"""
    print("\n" + "="*60)
    print("CLEARING PYTHON CACHES")
    print("="*60)
    
    # Clear importlib cache
    try:
        importlib.invalidate_caches()
        print("✓ Cleared importlib cache")
    except Exception as e:
        print(f"✗ Failed to clear importlib cache: {e}")
    
    # Clear sys.modules cache for plua
    modules_to_remove = [key for key in sys.modules.keys() if key.startswith('plua')]
    for module in modules_to_remove:
        try:
            del sys.modules[module]
            print(f"✓ Removed {module} from sys.modules")
        except Exception as e:
            print(f"✗ Failed to remove {module}: {e}")
    
    # Find and clear __pycache__ directories
    cache_dirs = find_python_cache_dirs()
    for cache_dir in cache_dirs:
        try:
            if os.path.exists(cache_dir):
                shutil.rmtree(cache_dir)
                print(f"✓ Removed cache directory: {cache_dir}")
        except Exception as e:
            print(f"✗ Failed to remove {cache_dir}: {e}")
    
    # Clear pip cache
    print("\nClearing pip cache...")
    returncode, stdout, stderr = run_command("pip cache purge")
    if returncode == 0:
        print("✓ Cleared pip cache")
    else:
        print(f"✗ Failed to clear pip cache: {stderr}")


def check_plua_installation():
    """Check current plua installation"""
    print("\n" + "="*60)
    print("CHECKING PLUA INSTALLATION")
    print("="*60)
    
    try:
        # Check if plua is installed
        returncode, stdout, stderr = run_command("pip show plua")
        if returncode == 0:
            print("✓ plua is installed:")
            print(stdout)
        else:
            print("✗ plua is not installed")
            return False
        
        # Check plua version
        try:
            import plua
            print(f"✓ plua module loaded, version: {plua.__version__}")
            
            # Check if debug code exists in interpreter
            import plua.interpreter
            code = inspect.getsource(plua.interpreter.LuaInterpreter.initialize)
            has_stderr = 'stderr' in code
            has_debug_banner = 'PLUA DEBUG OUTPUT' in code
            
            print(f"✓ Debug code analysis:")
            print(f"  - Has stderr references: {has_stderr}")
            print(f"  - Has debug banner: {has_debug_banner}")
            print(f"  - Both present: {has_stderr and has_debug_banner}")
            
            if not (has_stderr and has_debug_banner):
                print("✗ DEBUG CODE IS MISSING! This indicates a cache or installation issue.")
                return False
            else:
                print("✓ Debug code is present in the installed version")
                return True
                
        except Exception as e:
            print(f"✗ Failed to import plua: {e}")
            return False
            
    except Exception as e:
        print(f"✗ Error checking installation: {e}")
        return False


def force_reinstall_plua():
    """Force reinstall plua with cache clearing"""
    print("\n" + "="*60)
    print("FORCE REINSTALLING PLUA")
    print("="*60)
    
    # Uninstall first
    print("Uninstalling plua...")
    returncode, stdout, stderr = run_command("pip uninstall plua -y")
    if returncode == 0:
        print("✓ Uninstalled plua")
    else:
        print(f"⚠ Uninstall result: {stderr}")
    
    # Clear caches
    clear_python_caches()
    
    # Reinstall
    print("\nReinstalling plua...")
    returncode, stdout, stderr = run_command("pip install plua --force-reinstall --no-cache-dir")
    if returncode == 0:
        print("✓ Reinstalled plua")
        print(stdout)
    else:
        print(f"✗ Failed to reinstall plua: {stderr}")
        return False
    
    return True


def test_plua_execution():
    """Test plua execution and capture debug output"""
    print("\n" + "="*60)
    print("TESTING PLUA EXECUTION")
    print("="*60)
    
    # Create a simple test script
    test_script = "test_plua_debug.lua"
    with open(test_script, 'w') as f:
        f.write('print("Hello from plua test!")\n')
    
    try:
        # Run plua with the test script
        print(f"Running: plua {test_script}")
        returncode, stdout, stderr = run_command(f"plua {test_script}")
        
        print(f"Return code: {returncode}")
        print("STDOUT:")
        print(stdout if stdout else "(empty)")
        print("STDERR:")
        print(stderr if stderr else "(empty)")
        
        # Check if debug output appeared
        if stderr and "PLUA DEBUG OUTPUT" in stderr:
            print("✓ Debug output is working!")
            return True
        else:
            print("✗ Debug output is missing!")
            return False
            
    except Exception as e:
        print(f"✗ Error running plua: {e}")
        return False
    finally:
        # Clean up test file
        try:
            os.remove(test_script)
        except:
            pass


def main():
    """Main diagnostic and fix routine"""
    print("PLUA INSTALLATION DIAGNOSTIC AND FIX TOOL")
    print("=" * 60)
    print(f"Python: {sys.executable}")
    print(f"Platform: {sys.platform}")
    print(f"Version: {sys.version}")
    
    # Step 1: Check current installation
    install_ok = check_plua_installation()
    
    if not install_ok:
        print("\n⚠ Installation issues detected. Attempting to fix...")
        
        # Step 2: Force reinstall
        reinstall_ok = force_reinstall_plua()
        
        if not reinstall_ok:
            print("\n✗ FAILED TO REINSTALL. Please check pip and internet connection.")
            return False
        
        # Step 3: Check installation again
        install_ok = check_plua_installation()
        
        if not install_ok:
            print("\n✗ INSTALLATION STILL HAS ISSUES AFTER REINSTALL")
            return False
    
    # Step 4: Test execution
    execution_ok = test_plua_execution()
    
    if execution_ok:
        print("\n✅ SUCCESS! plua is working correctly with debug output.")
        return True
    else:
        print("\n❌ EXECUTION FAILED. Debug output is still missing.")
        
        # Additional troubleshooting
        print("\nTROUBLESHOOTING SUGGESTIONS:")
        print("1. Try running with explicit python path:")
        print(f"   {sys.executable} -m plua your_script.lua")
        print("2. Check if you have multiple Python installations")
        print("3. Verify you're using the same Python that has plua installed")
        print("4. Try creating a new virtual environment:")
        print("   python -m venv fresh_env")
        print("   fresh_env\\Scripts\\activate  # Windows")
        print("   pip install plua")
        print("   plua your_script.lua")
        
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
