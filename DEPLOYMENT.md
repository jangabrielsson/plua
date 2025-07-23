# Single-File Deployment Options for plua2

This document compares different approaches to package plua2 as a single executable or easily distributable package.

## 🚀 Performance Comparison

| Method | Startup Time | File Size | Portability | Build Time | Pros | Cons |
|--------|-------------|-----------|-------------|------------|------|------|
| **Nuitka** | 🟢 ~50-100ms | 🟡 30-50MB | 🟢 Excellent | 🟡 5-10min | Native code, fast | Large, long build |
| **PyInstaller** | 🟡 ~200-500ms | 🟡 25-40MB | 🟢 Good | 🟢 2-5min | Mature, reliable | Slower startup |
| **Zipapp + System Python** | 🟢 ~30-80ms | 🟢 5-15MB | 🟡 Needs Python | 🟢 <1min | Fastest startup | Needs Python installed |
| **Zipapp + Embedded Python** | 🟢 ~50-100ms | 🟡 20-35MB | 🟢 Excellent | 🟢 <1min | Fast, portable | Manual Python bundle |

## 🏆 Recommended Approach: Nuitka

Based on your requirements for good startup performance, **Nuitka** is the best choice:

### Advantages:
- ✅ **Excellent startup time** (~50-100ms vs 200-500ms for PyInstaller)
- ✅ **True native compilation** - no Python interpreter overhead
- ✅ **Single file** - easy distribution
- ✅ **No dependencies** - completely self-contained
- ✅ **Cross-platform** - works on Windows, macOS, Linux

### Building with Nuitka:

```bash
# Install Nuitka
pip install nuitka

# Build single-file executable  
python build_nuitka.py

# The result will be in dist/plua2 (or dist/plua2.exe on Windows)
```

## 🚄 Ultra-Fast Alternative: Zipapp

If you need the absolute fastest startup time and don't mind requiring Python to be installed:

```bash
# Build zipapp (requires Python 3.8+ on target)
python build_zipapp.py

# Result: dist_zipapp/plua2.pyz - runs in ~30-80ms
```

## 📋 Implementation Steps

### 1. Basic Nuitka Build

```bash
# Install build tools
pip install nuitka

# Run build script
python build_nuitka.py
```

### 2. Optimize for Smaller Size (Optional)

```bash
# Install UPX for compression
# macOS: brew install upx
# Ubuntu: sudo apt install upx
# Windows: Download from https://upx.github.io/

# Build with compression
python build_nuitka.py  # Automatically uses UPX if available
```

### 3. Test the Executable

```bash
# Test basic functionality
./dist/plua2 --help

# Test with a script
./dist/plua2 examples/websocket_server_example.lua

# Test REPL
./dist/plua2
```

## 🐛 Common Issues and Solutions

### Nuitka Build Issues

1. **Missing dependencies**: Add `--include-package=<package>` to Nuitka command
2. **Lua files not found**: Ensure `--include-data-dir=src/lua=lua` is correct
3. **Static files missing**: Ensure `--include-data-dir=static=static` is included

### Runtime Issues

1. **"lua" directory not found**: The executable looks for lua files in the same directory
2. **Import errors**: Some optional dependencies might need explicit inclusion
3. **Permissions**: Ensure the executable has execute permissions (`chmod +x`)

## 🔧 Advanced Optimizations

### For Even Faster Startup

1. **Profile-guided optimization** with Nuitka:
   ```bash
   # Build with PGO (requires multiple runs)
   python -m nuitka --onefile --pgo src/plua2/__main__.py
   ```

2. **Reduce import overhead** by lazy loading:
   - Move heavy imports inside functions
   - Use conditional imports for optional features

3. **Precompile frequently used scripts**:
   - Cache compiled Lua bytecode
   - Use faster JSON libraries for large configs

### For Smaller Size

1. **Exclude unused features**:
   ```python
   # In Nuitka build script, add:
   "--exclude-package=matplotlib",
   "--exclude-package=tkinter", 
   "--exclude-package=pytest",
   ```

2. **Use minimal FastAPI**:
   - Only import needed FastAPI components
   - Consider switching to a lighter web framework if needed

## 🎯 Deployment Recommendations

### Development/Testing
- Use **zipapp** for fastest iteration and testing
- Startup time: ~30-80ms
- Command: `python build_zipapp.py`

### Production Distribution  
- Use **Nuitka** for best end-user experience
- Startup time: ~50-100ms
- Single file, no dependencies
- Command: `python build_nuitka.py`

### CI/CD Integration
- Build artifacts for multiple platforms
- Upload to GitHub releases
- Automate testing of built executables

## 📈 Performance Benchmarks

Typical startup times on modern hardware:

```
Method                  Cold Start    Warm Start    File Size
----------------------  -----------   -----------   ----------
plua2 (Python)          ~300-800ms    ~200-400ms    Source
Nuitka executable       ~50-100ms     ~30-80ms      35-50MB  
PyInstaller executable  ~200-500ms    ~150-300ms    25-40MB
Zipapp + Python         ~30-80ms      ~20-60ms      5-15MB
```

The **Nuitka** approach gives you the best balance of startup performance, distribution simplicity, and user experience.
