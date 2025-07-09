#!/bin/bash

# Script to test all build types locally
# This helps verify that all architectures build correctly before creating a release

set -e

echo "🧪 Testing PLua builds for all architectures..."
echo "================================================"

# Function to test a build
test_build() {
    local platform=$1
    local script=$2
    local description=$3
    
    echo ""
    echo "🔨 Testing $description..."
    echo "----------------------------------------"
    
    if [ -f "$script" ]; then
        if python "$script"; then
            echo "✅ $description - SUCCESS"
            
            # Check if executable was created
            if [ "$platform" = "windows" ]; then
                exe_path="dist/plua.exe"
            else
                exe_path="dist/plua"
            fi
            
            if [ -f "$exe_path" ]; then
                echo "   📦 Executable created: $exe_path"
                echo "   📏 Size: $(du -h "$exe_path" | cut -f1)"
                
                # Test the executable
                if [ "$platform" != "windows" ]; then
                    chmod +x "$exe_path"
                fi
                
                if timeout 10s "$exe_path" --version > /dev/null 2>&1; then
                    echo "   ✅ Executable test passed"
                else
                    echo "   ⚠️  Executable test failed"
                fi
            else
                echo "   ❌ Executable not found: $exe_path"
            fi
        else
            echo "❌ $description - FAILED"
            return 1
        fi
    else
        echo "❌ Build script not found: $script"
        return 1
    fi
}

# Test all builds
echo "Testing builds..."

# Test macOS Universal build (works on both Intel and Apple Silicon)
test_build "macos-universal" "scripts/build.py" "macOS Universal Build"

# Test macOS Apple Silicon build (if on Apple Silicon)
if [ "$(uname -m)" = "arm64" ]; then
    test_build "macos-apple-silicon" "scripts/build.py" "macOS Apple Silicon Build"
else
    echo ""
    echo "⚠️  Skipping Apple Silicon build test (not on Apple Silicon)"
fi

# Note: Windows builds are handled by GitHub Actions workflow
# Cross-compilation from Apple Silicon macOS has issues, so we rely on the CI/CD pipeline
echo ""
echo "ℹ️  Windows builds are handled by GitHub Actions workflow"
echo "   - Cross-compilation from Apple Silicon has compatibility issues"
echo "   - Windows builds run automatically on every push/PR"
echo "   - Artifacts are available in GitHub Actions"

echo ""
echo "🎉 Build testing completed!"
echo ""
echo "Next steps:"
echo "1. Review the build outputs above"
echo "2. If all builds succeed, create a release:"
echo "   ./scripts/create_release.sh [version]"
echo ""
echo "3. The GitHub Actions workflow will automatically:"
echo "   - Build all architectures"
echo "   - Create a GitHub Release"
echo "   - Upload all executables" 