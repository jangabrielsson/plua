#!/bin/bash
# PLua runner script

# Get the absolute path to the current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Set PYTHONPATH to include src directory - force development code to take precedence
export PYTHONPATH="$SCRIPT_DIR/src:$PYTHONPATH"

# Activate virtual environment if available
if [ -f "$SCRIPT_DIR/.venv/bin/activate" ]; then
    source "$SCRIPT_DIR/.venv/bin/activate"
    # echo "ℹ️ Activated .venv virtual environment"
else
    echo "ℹ️ .venv not found, using system Python"
fi

# Create a new session and process group to ensure proper cleanup
# This ensures that when VSCode kills the process, all child processes are also killed
exec python -u -m plua.cli "$@"
