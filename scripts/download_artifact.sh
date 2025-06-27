#!/bin/bash

# Create dist directory if it doesn't exist
mkdir -p dist

# Get the latest successful run of the windows-build workflow
echo "Finding latest successful workflow run..."
LATEST_RUN=$(gh run list --workflow=windows-build.yml --json databaseId,conclusion --jq '.[] | select(.conclusion == "success") | .databaseId' | head -1)

if [ -z "$LATEST_RUN" ]; then
    echo "No successful workflow runs found. Make sure the workflow has completed successfully."
    exit 1
fi

echo "Latest successful run: $LATEST_RUN"

# Download the artifact
echo "Downloading plua-windows-exe artifact..."
gh run download $LATEST_RUN --name plua-windows-exe --dir dist

if [ $? -eq 0 ]; then
    echo "✅ Windows executable downloaded to ./dist/"
    echo "Files in dist/:"
    ls -la dist/
else
    echo "❌ Failed to download artifact"
    exit 1
fi 