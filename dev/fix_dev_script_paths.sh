#!/bin/bash
# fix_dev_script_paths.sh - Fix paths in dev scripts

echo "Fixing paths in dev scripts..."

cd /Users/jangabrielsson/Documents/dev/plua/dev

for script in *.sh; do
    if [ -f "$script" ]; then
        echo "Processing $script..."
        
        # Add cd to parent directory before python commands
        if ! grep -q "cd.*\.\." "$script"; then
            # Insert cd command after the first few lines but before python commands
            sed -i.bak '/python -m src\.plua/i\
# Change to parent directory to run from project root\
cd "$(dirname "$0")/.."' "$script"
            
            # Clean up backup file
            rm -f "${script}.bak"
        fi
    fi
done

echo "Script path fixing completed."
