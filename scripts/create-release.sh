#!/bin/bash

# GitHub Release Helper Script for plua
# Usage: ./scripts/create-release.sh [version] [release-notes]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Get current version from __init__.py
get_current_version() {
    grep "__version__" src/plua/__init__.py | sed 's/.*"\(.*\)".*/\1/'
}

# Bump version based on type
bump_version() {
    local current_version=$1
    local bump_type=$2
    
    IFS='.' read -ra VERSION_PARTS <<< "$current_version"
    local major=${VERSION_PARTS[0]}
    local minor=${VERSION_PARTS[1]}
    local patch=${VERSION_PARTS[2]}
    
    case $bump_type in
        "major")
            echo "$((major + 1)).0.0"
            ;;
        "minor")
            echo "$major.$((minor + 1)).0"
            ;;
        "patch")
            echo "$major.$minor.$((patch + 1))"
            ;;
        *)
            echo "$bump_type"  # Custom version
            ;;
    esac
}

# Main script
main() {
    print_status "🚀 GitHub Release Helper for plua"
    echo
    
    # Check if we're in the right directory
    if [[ ! -f "src/plua/__init__.py" ]]; then
        print_error "Must be run from the plua project root directory"
        exit 1
    fi
    
    # Check if gh CLI is installed
    if ! command -v gh &> /dev/null; then
        print_error "GitHub CLI (gh) is required but not installed"
        print_status "Install with: brew install gh"
        exit 1
    fi
    
    # Check if user is authenticated
    if ! gh auth status &> /dev/null; then
        print_error "Not authenticated with GitHub CLI"
        print_status "Run: gh auth login"
        exit 1
    fi
    
    current_version=$(get_current_version)
    print_status "Current version: $current_version"
    
    # Get version argument
    if [[ -n "$1" ]]; then
        if [[ "$1" =~ ^(major|minor|patch)$ ]]; then
            new_version=$(bump_version "$current_version" "$1")
            print_status "Bumping $1 version: $current_version → $new_version"
        else
            new_version="$1"
            print_status "Setting custom version: $current_version → $new_version"
        fi
    else
        echo "Select version bump type:"
        echo "1) Patch (${current_version} → $(bump_version "$current_version" "patch"))"
        echo "2) Minor (${current_version} → $(bump_version "$current_version" "minor"))"
        echo "3) Major (${current_version} → $(bump_version "$current_version" "major"))"
        echo "4) Custom version"
        echo
        read -p "Choice (1-4): " choice
        
        case $choice in
            1) new_version=$(bump_version "$current_version" "patch") ;;
            2) new_version=$(bump_version "$current_version" "minor") ;;
            3) new_version=$(bump_version "$current_version" "major") ;;
            4) 
                read -p "Enter custom version: " new_version
                ;;
            *) 
                print_error "Invalid choice"
                exit 1
                ;;
        esac
    fi
    
    # Get release notes
    if [[ -n "$2" ]]; then
        release_notes="$2"
    else
        print_status "Enter release notes (press Ctrl+D when done):"
        release_notes=$(cat)
    fi
    
    if [[ -z "$release_notes" ]]; then
        release_notes="Release version $new_version"
    fi
    
    echo
    print_status "📋 Release Summary:"
    echo "  Version: $new_version"
    echo "  Notes: $release_notes"
    echo
    
    read -p "Create this release? (y/N): " confirm
    if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
        print_warning "Release cancelled"
        exit 0
    fi
    
    # Update version in __init__.py
    print_status "Updating version in src/plua/__init__.py..."
    sed -i.bak "s/__version__ = \".*\"/__version__ = \"$new_version\"/" src/plua/__init__.py
    rm src/plua/__init__.py.bak
    
    # Update version in pyproject.toml
    print_status "Updating version in pyproject.toml..."
    sed -i.bak "s/version = \".*\"/version = \"$new_version\"/" pyproject.toml
    rm pyproject.toml.bak
    
    # Commit the version change
    print_status "Committing version update..."
    git add src/plua/__init__.py pyproject.toml
    git commit -m "Bump version to $new_version"
    
    # Create and push tag
    print_status "Creating and pushing tag v$new_version..."
    git tag "v$new_version"
    git push origin main
    git push origin "v$new_version"
    
    # Create GitHub release
    print_status "Creating GitHub release..."
    gh release create "v$new_version" \
        --title "Release v$new_version" \
        --notes "$release_notes" \
        --verify-tag
    
    print_success "✅ Release v$new_version created successfully!"
    print_status "� Release URL: https://github.com/jangabrielsson/plua/releases/tag/v$new_version"
    print_status "�🔄 GitHub Actions will automatically:"
    print_status "   📦 Publish to PyPI using stored API token"
    print_status "🎉 PyPI package will be available at: https://pypi.org/project/plua/$new_version/"
    echo
    print_status "💡 Note: Executable building is currently disabled"
    print_status "   To enable: manually trigger 'Build Executables' workflow with force_build=yes"
}

# Run main function with all arguments
main "$@"
