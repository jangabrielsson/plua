#!/bin/bash

# Create dist directory if it doesn't exist
mkdir -p dist

# Get the latest successful run of the macos-intel-build workflow
echo "Finding latest successful workflow run..."
LATEST_RUN=$(gh run list --workflow=macos-intel-build.yml --json databaseId,conclusion --jq '.[] | select(.conclusion == "success") | .databaseId' | head -1)

if [ -z "$LATEST_RUN" ]; then
    echo "No successful workflow runs found. Make sure the workflow has completed successfully."
    exit 1
fi

echo "Latest successful run: $LATEST_RUN"

# Download the artifact
echo "Downloading plua-macos-intel-exe artifact..."
gh run download $LATEST_RUN --name plua-macos-intel-exe --dir dist

if [ $? -eq 0 ]; then
    echo "✅ macOS Intel executable downloaded to ./dist/"
    echo "Files in dist/:"
    ls -la dist/
    
    # Make executable
    chmod +x dist/plua
    echo "✅ Made executable: dist/plua"
    
    # Verify architecture
    echo "Architecture verification:"
    file dist/plua
else
    echo "❌ Failed to download artifact"
    exit 1
fi 