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

# Get the last release tag
get_last_release_tag() {
    git tag --sort=-version:refname | grep -E '^v[0-9]+\.[0-9]+\.[0-9]+$' | head -1
}

# Generate release notes from git commits since last release
generate_release_notes() {
    local last_tag=$(get_last_release_tag)
    local version=$1
    
    echo "## Changes in v$version"
    echo
    
    if [[ -n "$last_tag" ]]; then
        print_status "Generating release notes from commits since $last_tag..."
        echo "### Commits since $last_tag:"
        echo
        # Get commits since last tag, format them nicely
        git log --oneline --no-merges "${last_tag}..HEAD" | while read -r commit; do
            # Extract commit hash and message
            hash=$(echo "$commit" | cut -d' ' -f1)
            message=$(echo "$commit" | cut -d' ' -f2-)
            
            # Categorize commits based on conventional commit patterns
            if [[ "$message" =~ ^feat(\(.*\))?:\ (.+) ]]; then
                echo "- ✨ **Feature**: ${message#feat*: }"
            elif [[ "$message" =~ ^fix(\(.*\))?:\ (.+) ]]; then
                echo "- 🐛 **Fix**: ${message#fix*: }"
            elif [[ "$message" =~ ^docs(\(.*\))?:\ (.+) ]]; then
                echo "- 📚 **Docs**: ${message#docs*: }"
            elif [[ "$message" =~ ^style(\(.*\))?:\ (.+) ]]; then
                echo "- 💄 **Style**: ${message#style*: }"
            elif [[ "$message" =~ ^refactor(\(.*\))?:\ (.+) ]]; then
                echo "- ♻️ **Refactor**: ${message#refactor*: }"
            elif [[ "$message" =~ ^test(\(.*\))?:\ (.+) ]]; then
                echo "- 🧪 **Test**: ${message#test*: }"
            elif [[ "$message" =~ ^chore(\(.*\))?:\ (.+) ]]; then
                echo "- 🔧 **Chore**: ${message#chore*: }"
            elif [[ "$message" =~ ^perf(\(.*\))?:\ (.+) ]]; then
                echo "- ⚡ **Performance**: ${message#perf*: }"
            elif [[ "$message" =~ ^ci(\(.*\))?:\ (.+) ]]; then
                echo "- 👷 **CI**: ${message#ci*: }"
            elif [[ "$message" =~ ^build(\(.*\))?:\ (.+) ]]; then
                echo "- 🏗️ **Build**: ${message#build*: }"
            else
                echo "- 📝 $message"
            fi
        done
    else
        echo "### All commits (no previous release found):"
        echo
        git log --oneline --no-merges | while read -r commit; do
            message=$(echo "$commit" | cut -d' ' -f2-)
            echo "- 📝 $message"
        done
    fi
    
    echo
    echo "---"
    echo "*Generated automatically from git commits*"
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
        echo
        echo "Release notes options:"
        echo "1) Auto-generate from git commits since last release"
        echo "2) Enter custom release notes"
        echo "3) Use simple default message"
        echo
        read -p "Choice (1-3): " notes_choice
        
        case $notes_choice in
            1)
                print_status "Generating release notes from git commits..."
                release_notes=$(generate_release_notes "$new_version")
                echo
                print_status "Generated release notes:"
                echo "$release_notes"
                echo
                read -p "Use these release notes? (Y/n): " use_generated
                if [[ "$use_generated" == "n" || "$use_generated" == "N" ]]; then
                    print_status "Enter custom release notes (press Ctrl+D when done):"
                    release_notes=$(cat)
                fi
                ;;
            2)
                print_status "Enter custom release notes (press Ctrl+D when done):"
                release_notes=$(cat)
                ;;
            3)
                release_notes="Release version $new_version"
                ;;
            *)
                print_warning "Invalid choice, using auto-generated notes"
                release_notes=$(generate_release_notes "$new_version")
                ;;
        esac
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
    
    # Update or create CHANGELOG.md
    print_status "Updating CHANGELOG.md..."
    if [[ ! -f "CHANGELOG.md" ]]; then
        echo "# Changelog" > CHANGELOG.md
        echo "" >> CHANGELOG.md
        echo "All notable changes to this project will be documented in this file." >> CHANGELOG.md
        echo "" >> CHANGELOG.md
    fi
    
    # Prepare changelog entry
    changelog_entry="## [v$new_version] - $(date +%Y-%m-%d)"
    
    # Create temporary file with new changelog entry
    temp_changelog=$(mktemp)
    echo "# Changelog" > "$temp_changelog"
    echo "" >> "$temp_changelog"
    echo "All notable changes to this project will be documented in this file." >> "$temp_changelog"
    echo "" >> "$temp_changelog"
    echo "$changelog_entry" >> "$temp_changelog"
    echo "" >> "$temp_changelog"
    
    # Add the release notes to changelog (convert from markdown to simpler format)
    echo "$release_notes" | sed 's/^## Changes in v[0-9.]*$//' | sed 's/^### /#### /' | sed '/^---$/,$d' >> "$temp_changelog"
    echo "" >> "$temp_changelog"
    
    # Append existing changelog content (skip the header)
    if [[ -f "CHANGELOG.md" ]]; then
        tail -n +4 CHANGELOG.md | grep -v "^## \[v$new_version\]" >> "$temp_changelog" 2>/dev/null || true
    fi
    
    mv "$temp_changelog" CHANGELOG.md
    
    # Commit the version change and changelog
    print_status "Committing version update and changelog..."
    git add src/plua/__init__.py pyproject.toml CHANGELOG.md
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
    print_status "🔗 Release URL: https://github.com/jangabrielsson/plua/releases/tag/v$new_version"
    print_status "🔄 GitHub Actions will automatically:"
    print_status "   📦 Publish to PyPI using stored API token"
    print_status "   🔨 Build executables for Linux, Windows, and macOS"
    print_status "🎉 PyPI package will be available at: https://pypi.org/project/plua/$new_version/"
    print_status "📝 Updated CHANGELOG.md with release notes"
    print_status "💡 Note: PyPI description comes from README.md, not release notes"
    echo
}

# Run main function with all arguments
main "$@"
