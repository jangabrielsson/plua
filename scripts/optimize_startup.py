#!/usr/bin/env python3
"""
Startup optimization script for PLua
Measures startup time and identifies bottlenecks
"""

import time
import sys
import importlib
import cProfile
import pstats
from pathlib import Path


def measure_import_time(module_name):
    """Measure the time it takes to import a module"""
    start_time = time.time()
    try:
        importlib.import_module(module_name)
        import_time = time.time() - start_time
        return import_time, True
    except Exception as e:
        import_time = time.time() - start_time
        return import_time, False, str(e)


def profile_startup():
    """Profile the startup process to identify bottlenecks"""
    print("🔍 Profiling PLua startup...")
    print("=" * 50)

    # Add the project root to the path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))

    # Modules to profile
    modules_to_profile = [
        'lupa',
        'extensions.core',
        'extensions.network_extensions',
        'extensions.websocket_extensions',
        'extensions.html_extensions',
        'extensions.web_server',
        'extensions.registry',
        'requests',
        'fastapi',
        'uvicorn',
        'pydantic',
        'plua.interpreter',
        'plua.embedded_api_server',
    ]

    print("📊 Module import times:")
    print("-" * 30)

    total_time = 0
    slow_modules = []

    for module in modules_to_profile:
        import_time, success = measure_import_time(module)
        total_time += import_time

        status = "✅" if success else "❌"
        print(f"{status} {module:<30} {import_time:.3f}s")

        if import_time > 0.1:  # Modules taking more than 100ms
            slow_modules.append((module, import_time))

    print("-" * 30)
    print(f"📈 Total import time: {total_time:.3f}s")

    if slow_modules:
        print("\n🐌 Slow modules (>100ms):")
        for module, import_time in sorted(slow_modules, key=lambda x: x[1], reverse=True):
            print(f"   {module}: {import_time:.3f}s")

    return total_time, slow_modules


def profile_main_execution():
    """Profile the main execution path"""
    print("\n🚀 Profiling main execution...")
    print("=" * 50)

    # Create a profiler
    profiler = cProfile.Profile()
    profiler.enable()

    try:
        # Import the main module to profile import time
        import plua.__main__  # noqa: F401
        # Don't actually run main(), just profile the import
    except Exception as e:
        print(f"❌ Error profiling main execution: {e}")
        return

    profiler.disable()

    # Print stats
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    print("Top 10 functions by cumulative time:")
    stats.print_stats(10)


def suggest_optimizations(slow_modules):
    """Suggest optimizations based on profiling results"""
    print("\n💡 Optimization suggestions:")
    print("=" * 50)

    suggestions = []

    for module, import_time in slow_modules:
        if 'network_extensions' in module:
            suggestions.append("🔧 Use lazy loading for network_extensions (already implemented)")
        elif 'websocket_extensions' in module:
            suggestions.append("🔧 Use lazy loading for websocket_extensions (already implemented)")
        elif 'html_extensions' in module:
            suggestions.append("🔧 Use lazy loading for html_extensions (already implemented)")
        elif 'requests' in module:
            suggestions.append("🔧 Consider using urllib3 directly instead of requests for basic HTTP")
        elif 'fastapi' in module or 'uvicorn' in module:
            suggestions.append("🔧 Only import FastAPI/uvicorn when API server is actually needed")
        elif 'pydantic' in module:
            suggestions.append("🔧 Consider lazy loading Pydantic models")

    if not suggestions:
        suggestions.append("✅ No major optimizations needed - startup time looks good!")

    for suggestion in suggestions:
        print(f"   {suggestion}")


def main():
    """Main optimization function"""
    print("⚡ PLua Startup Optimization Tool")
    print("=" * 50)

    # Profile module imports
    total_time, slow_modules = profile_startup()

    # Profile main execution
    profile_main_execution()

    # Suggest optimizations
    suggest_optimizations(slow_modules)

    print("\n🎯 Summary:")
    print(f"   Total startup time: {total_time:.3f}s")
    if total_time < 0.5:
        print("   ✅ Startup time is good (< 0.5s)")
    elif total_time < 1.0:
        print("   ⚠️  Startup time is acceptable (< 1.0s)")
    else:
        print("   ❌ Startup time needs improvement (> 1.0s)")


if __name__ == '__main__':
    main()
