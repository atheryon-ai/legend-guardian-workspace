#!/usr/bin/env python3
"""Update imports from old structure to new structure."""

import os
import re
from pathlib import Path

def update_imports_in_file(filepath):
    """Update imports in a single Python file."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Track if changes were made
    original_content = content
    
    # Update various import patterns
    replacements = [
        # From old src.* imports to legend_guardian.*
        (r'from src\.agent\.', 'from legend_guardian.agent.'),
        (r'from src\.api\.', 'from legend_guardian.api.'),
        (r'from src\.clients\.', 'from legend_guardian.clients.'),
        (r'from src\.rag\.', 'from legend_guardian.rag.'),
        (r'from src\.settings import', 'from legend_guardian.config import'),
        (r'import src\.', 'import legend_guardian.'),
        
        # Update Settings class imports
        (r'from src\.settings import Settings', 'from legend_guardian.config import Settings'),
        (r'from legend_guardian\.config import settings', 'from legend_guardian.config import settings'),
        
        # Fix any absolute imports that might exist
        (r'from agent\.', 'from legend_guardian.agent.'),
        (r'from api\.', 'from legend_guardian.api.'),
        (r'from clients\.', 'from legend_guardian.clients.'),
        (r'from rag\.', 'from legend_guardian.rag.'),
    ]
    
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)
    
    # Write back if changes were made
    if content != original_content:
        with open(filepath, 'w') as f:
            f.write(content)
        return True
    return False

def main():
    """Update all Python files in the new structure."""
    base_path = Path('src/legend_guardian')
    
    updated_files = []
    for py_file in base_path.rglob('*.py'):
        if update_imports_in_file(py_file):
            updated_files.append(py_file)
            print(f"Updated: {py_file}")
    
    print(f"\nTotal files updated: {len(updated_files)}")
    
    # Also update test files if they exist
    test_path = Path('tests')
    if test_path.exists():
        for py_file in test_path.rglob('*.py'):
            if update_imports_in_file(py_file):
                updated_files.append(py_file)
                print(f"Updated test: {py_file}")

if __name__ == '__main__':
    main()