#!/bin/bash
# Project-specific shell initialization for plua development

# Auto-activate virtual environment if it exists
if [ -f ".venv/bin/activate" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
    echo "Virtual environment activated: $(which python)"
fi

# Add any other project-specific environment setup here
export PLUA_DEV_MODE=1
