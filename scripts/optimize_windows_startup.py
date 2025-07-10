#!/usr/bin/env python3
"""
Windows Startup Optimization Tool for PLua
Measures startup time and provides Windows-specific optimizations
"""

import time
import sys
import platform
import subprocess


def measure_startup_time(command, iterations=3):
    """Measure startup time of a command"""
    times = []
    
    print(f"🔄 Measuring startup time for: {command}")
    print(f"   Running {iterations} iterations...")
    
    for i in range(iterations):
        start_time = time.time()
        try:
            # Run the command and capture output
            subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            end_time = time.time()
            startup_time = end_time - start_time
            times.append(startup_time)
            print(f"   Run {i+1}: {startup_time:.3f}s")
        except subprocess.TimeoutExpired:
            print(f"   Run {i+1}: TIMEOUT (>30s)")
            times.append(30.0)
        except Exception as e:
            print(f"   Run {i+1}: ERROR - {e}")
            times.append(30.0)
    
    if times:
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        print(f"   Average: {avg_time:.3f}s")
        print(f"   Min: {min_time:.3f}s, Max: {max_time:.3f}s")
        return avg_time
    return None


def check_windows_optimizations():
    """Check for Windows-specific optimizations"""
    print("\n🔧 Windows Optimization Recommendations:")
    print("=" * 50)
    
    # Check Python version
    python_version = sys.version_info
    print(f"✅ Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Check if running on Windows
    if platform.system() != "Windows":
        print("❌ This script is designed for Windows optimization")
        return
    
    # Check for antivirus interference
    print("\n🛡️  Antivirus Check:")
    print("   - Consider adding PLua to antivirus exclusions")
    print("   - Real-time scanning can slow down startup")
    
    # Check for Windows Defender
    try:
        result = subprocess.run(
            ["powershell", "Get-MpComputerStatus"], 
            capture_output=True, 
            text=True
        )
        if "RealTimeProtectionEnabled : True" in result.stdout:
            print("   ⚠️  Windows Defender real-time protection is enabled")
            print("   💡 Consider temporarily disabling for testing")
    except Exception:
        pass
    
    # Check disk type
    try:
        result = subprocess.run(
            ["wmic", "logicaldisk", "where", "DeviceID='C:'", "get", "MediaType"], 
            capture_output=True, 
            text=True
        )
        if "SSD" in result.stdout:
            print("✅ SSD detected - good for startup performance")
        elif "HDD" in result.stdout:
            print("⚠️  HDD detected - consider SSD for better performance")
    except Exception:
        pass


def main():
    """Main optimization function"""
    print("⚡ PLua Windows Startup Optimization Tool")
    print("=" * 50)
    
    # Check if we're on Windows
    if platform.system() != "Windows":
        print("❌ This tool is designed for Windows optimization")
        print("   Use scripts/optimize_startup.py for other platforms")
        return
    
    # Check if plua is installed
    try:
        result = subprocess.run(
            ["plua", "--version"], 
            capture_output=True, 
            text=True
        )
        if result.returncode != 0:
            print("❌ PLua not found in PATH")
            print("   Please install PLua first: pip install plua")
            return
    except FileNotFoundError:
        print("❌ PLua not found in PATH")
        print("   Please install PLua first: pip install plua")
        return
    
    print("✅ PLua found in PATH")
    
    # Measure startup times
    print("\n📊 Startup Time Measurements:")
    print("=" * 50)
    
    # Test with API server (default)
    print("\n1️⃣ Testing with API server (default):")
    avg_with_api = measure_startup_time("plua --version")
    
    # Test without API server
    print("\n2️⃣ Testing without API server:")
    avg_without_api = measure_startup_time("plua --no-api-server --version")
    
    # Compare results
    if avg_with_api and avg_without_api:
        improvement = ((avg_with_api - avg_without_api) / avg_with_api) * 100
        print("\n📈 Performance Comparison:")
        print(f"   With API server:    {avg_with_api:.3f}s")
        print(f"   Without API server: {avg_without_api:.3f}s")
        print(f"   Improvement:        {improvement:.1f}% faster")
        
        if improvement > 20:
            print("   🎉 Significant improvement! Use --no-api-server when web interface not needed")
        elif improvement > 10:
            print("   👍 Good improvement! Consider --no-api-server for faster startup")
        else:
            print("   📊 Minimal improvement - API server overhead is low")
    
    # Windows-specific recommendations
    check_windows_optimizations()
    
    # Final recommendations
    print("\n💡 Recommendations for Windows:")
    print("=" * 50)
    print("1. Background API server loading (NEW):")
    print("   - FastAPI now loads in background thread")
    print("   - Main startup completes quickly")
    print("   - API server becomes available shortly after")
    print()
    print("2. Use --no-api-server when web interface not needed")
    print("3. Consider adding PLua to antivirus exclusions")
    print("4. Use SSD storage for better performance")
    print("5. Close unnecessary background applications")
    print("6. Consider using a virtual environment for isolation")


if __name__ == "__main__":
    main() 