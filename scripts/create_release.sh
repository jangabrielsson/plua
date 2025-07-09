#!/bin/bash

# Script to create a new PLua release
# Usage: ./scripts/create_release.sh [version]
# Example: ./scripts/create_release.sh 1.0.28

set -e

# Get version from command line or prompt user
if [ $# -eq 1 ]; then
    VERSION=$1
else
    echo "Enter version number (e.g., 1.0.28):"
    read VERSION
fi

# Validate version format
if [[ ! $VERSION =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "Error: Version must be in format X.Y.Z (e.g., 1.0.28)"
    exit 1
fi

echo "Creating release for version: $VERSION"

# Check if we're on the main branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "Warning: You're not on the main branch. Current branch: $CURRENT_BRANCH"
    echo "Do you want to continue? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 1
    fi
fi

# Check if working directory is clean
if [ -n "$(git status --porcelain)" ]; then
    echo "Error: Working directory is not clean. Please commit or stash your changes."
    git status --short
    exit 1
fi

# Check if tag already exists
if git tag -l | grep -q "^v$VERSION$"; then
    echo "Error: Tag v$VERSION already exists."
    exit 1
fi

# Update version in pyproject.toml
echo "Updating version in pyproject.toml..."
sed -i.bak "s/^version = \".*\"/version = \"$VERSION\"/" pyproject.toml
rm pyproject.toml.bak

# Always commit version change (manual releases)
git add pyproject.toml
git commit -m "Bump version to $VERSION"

# Create and push tag
echo "Creating tag v$VERSION..."
git tag -a "v$VERSION" -m "Release v$VERSION"

# Push changes and tag
echo "Pushing changes and tag..."
git push origin main
git push origin "v$VERSION"

echo "✅ Release v$VERSION created successfully!"
echo ""
echo "The GitHub Actions workflow will now:"
echo "1. Build executables for Windows, macOS Intel, and macOS Apple Silicon"
echo "2. Create a GitHub Release with all downloads"
echo "3. Make the release available at: https://github.com/$(git config --get remote.origin.url | sed 's/.*github.com[:/]\([^/]*\/[^/]*\).*/\1/')/releases/tag/v$VERSION"
echo ""
echo "You can monitor the build progress at:"
echo "https://github.com/$(git config --get remote.origin.url | sed 's/.*github.com[:/]\([^/]*\/[^/]*\).*/\1/')/actions" 