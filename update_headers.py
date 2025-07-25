#!/usr/bin/env python3
"""
Script to update header formats in all Fibaro stdQA files
1. Remove --%%webui=true lines
2. Change --%%<header>=<value> to --%%<header>:<value>
"""

import os
import re
import glob

def update_file_headers(file_path):
    """Update headers in a single file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Remove --%%webui=true lines
    content = re.sub(r'^--%%webui=true\s*\n', '', content, flags=re.MULTILINE)
    
    # Change --%%<header>=<value> to --%%<header>:<value>
    # This pattern matches header lines but preserves quoted values
    content = re.sub(r'^--%%([^=\s]+)=(.*)$', r'--%%\1:\2', content, flags=re.MULTILINE)
    
    # Only write if content changed
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    """Process all files in the stdQAs directory"""
    pattern = "examples/fibaro/stdQAs/*.lua"
    files = glob.glob(pattern)
    
    updated_count = 0
    total_count = len(files)
    
    print(f"Found {total_count} files to process...")
    
    for file_path in files:
        if update_file_headers(file_path):
            updated_count += 1
            print(f"Updated: {os.path.basename(file_path)}")
        else:
            print(f"No changes: {os.path.basename(file_path)}")
    
    print(f"\nProcessed {total_count} files, updated {updated_count} files")

if __name__ == "__main__":
    main()
