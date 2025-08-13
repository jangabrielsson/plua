# Building plua Standalone Executables

This document explains how to build standalone executables of plua using Nuitka.

## Prerequisites

### Development Environment Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/jangabrielsson/plua.git
   cd plua
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv .venv
   
   # On macOS/Linux:
   source .venv/bin/activate
   
   # On Windows:
   .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   # Install runtime dependencies
   pip install -e .
   
   # Install build dependencies (including Nuitka)
   pip install -e ".[build]"
   
   # Or install all development dependencies
   pip install -e ".[dev]"
   ```

### Platform-Specific Requirements

#### Windows
- **Visual Studio Build Tools** or **Visual Studio Community** (for C++ compiler)
- **Windows SDK** (usually included with Visual Studio)

#### macOS
- **Xcode Command Line Tools**: `xcode-select --install`
- **Homebrew** (recommended): For additional tools like UPX (optional)

#### Linux
- **GCC compiler**: `sudo apt-get install gcc` (Ubuntu/Debian)
- **Development headers**: `sudo apt-get install python3-dev`

## Building

### Quick Build
```bash
cd scripts
python build_nuitka.py
```

### Platform-Specific Outputs

- **macOS**: Creates `dist/build_main_standalone.app` (app bundle)
- **Windows**: Creates `dist/plua.exe` (single executable)
- **Linux**: Creates `dist/plua` (single executable)

### Build Options

The build script automatically:
- Uses `--mode=app` on macOS for Foundation framework compatibility
- Uses `--onefile` on Windows/Linux for single executable
- Skips UPX compression on macOS (causes issues with native frameworks)
- Includes all static web UI files and Lua runtime files
- Optimizes with LTO (Link Time Optimization)

## Troubleshooting

### "Nuitka installation appears corrupted"
This usually means Nuitka isn't properly installed. Solutions:

1. **Reinstall Nuitka:**
   ```bash
   pip uninstall nuitka
   pip install nuitka>=2.7.0
   ```

2. **Check Python version compatibility:**
   - Nuitka requires Python 3.6+ 
   - Works best with Python 3.8-3.12

3. **Verify C++ compiler:**
   - Windows: Install Visual Studio Build Tools
   - macOS: Run `xcode-select --install`
   - Linux: Install GCC

### Build Fails on Windows
- Ensure Visual Studio Build Tools are installed
- Try running from "Developer Command Prompt"
- Check Windows Defender isn't blocking the compilation

### Build Fails on macOS
- Install Xcode Command Line Tools
- If using Homebrew Python, ensure it's properly linked
- Check that you're using the correct Python interpreter

### Missing Files in Built Executable
The build script should automatically include:
- All Lua runtime files from `src/lua/`
- All web UI files from `src/plua/static/`
- All required Python packages

If files are missing, check the build output for inclusion warnings.

## Testing the Build

### macOS
```bash
# Test the app bundle
open scripts/dist/build_main_standalone.app

# Or run directly
scripts/dist/build_main_standalone.app/Contents/MacOS/plua --help
```

### Windows/Linux
```bash
# Test the executable
scripts/dist/plua --help   # Linux
scripts/dist/plua.exe --help   # Windows
```

### Verify Web UI
1. Run the executable without arguments to start interactive mode
2. The web UI should be available at `http://localhost:8888`
3. Test that Fibaro API endpoints respond (even if with 503 errors)

## File Size Expectations

Typical sizes for standalone builds:
- **macOS**: ~160-200 MB (app bundle)
- **Windows**: ~80-120 MB (executable)  
- **Linux**: ~80-120 MB (executable)

Large size is normal due to including the full Python runtime and all dependencies.
