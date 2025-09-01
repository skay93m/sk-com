#!/usr/bin/env python3
"""
Script to replace hardcoded color values with centralized CSS variables
"""

import os
import re
from pathlib import Path

# Color mapping from hardcoded values to CSS variables
COLOR_MAPPINGS = {
    # Common hardcoded colors to centralized variables
    '#f8f9fa': 'var(--gray-100)',
    '#e9ecef': 'var(--gray-200)',
    '#dee2e6': 'var(--gray-300)',
    '#ced4da': 'var(--gray-400)',
    '#6c757d': 'var(--gray-500)',
    '#495057': 'var(--gray-600)',
    '#444': 'var(--gray-700)',
    '#666': 'var(--gray-700)',
    '#888': 'var(--gray-500)',
    '#343a40': 'var(--gray-800)',
    '#212529': 'var(--gray-900)',
    '#ffffff': 'var(--white)',
    '#fff': 'var(--white)',
    'white': 'var(--white)',
    '#000000': 'var(--black)',
    '#000': 'var(--black)',
    'black': 'var(--black)',
    
    # Bootstrap defaults to our variables
    '#007bff': 'var(--bootstrap-blue)',
    '#28a745': 'var(--bootstrap-green)',
    '#ffc107': 'var(--bootstrap-yellow)',
    '#dc3545': 'var(--bootstrap-red)',
    
    # Transparency mappings
    'rgba(255, 255, 255, 0.1)': 'var(--white-alpha-10)',
    'rgba(255, 255, 255, 0.15)': 'var(--white-alpha-15)',
    'rgba(255, 255, 255, 0.2)': 'var(--white-alpha-20)',
    'rgba(255, 255, 255, 0.25)': 'var(--white-alpha-25)',
    'rgba(255, 255, 255, 0.3)': 'var(--white-alpha-30)',
    'rgba(255, 255, 255, 0.5)': 'var(--white-alpha-50)',
    'rgba(255, 255, 255, 0.75)': 'var(--white-alpha-75)',
    'rgba(255, 255, 255, 0.95)': 'var(--white-alpha-95)',
    
    'rgba(0, 0, 0, 0.1)': 'var(--black-alpha-10)',
    'rgba(0, 0, 0, 0.15)': 'var(--black-alpha-15)',
    'rgba(0, 0, 0, 0.2)': 'var(--black-alpha-20)',
    
    'rgba(61, 64, 91, 0.05)': 'var(--delft-blue-alpha-5)',
    'rgba(61, 64, 91, 0.1)': 'var(--delft-blue-alpha-10)',
    'rgba(61, 64, 91, 0.15)': 'var(--delft-blue-alpha-15)',
    'rgba(61, 64, 91, 0.2)': 'var(--delft-blue-alpha-20)',
    'rgba(61, 64, 91, 0.3)': 'var(--delft-blue-alpha-30)',
    'rgba(61, 64, 91, 0.4)': 'var(--delft-blue-alpha-40)',
    'rgba(61, 64, 91, 0.95)': 'var(--delft-blue-alpha-95)',
    
    'rgba(129, 178, 154, 0.15)': 'var(--cambridge-blue-alpha-15)',
    'rgba(129, 178, 154, 0.3)': 'var(--cambridge-blue-alpha-30)',
    'rgba(129, 178, 154, 0.9)': 'var(--cambridge-blue-alpha-90)',
    
    'rgba(224, 122, 95, 0.15)': 'var(--burnt-sienna-alpha-15)',
    'rgba(224, 122, 95, 0.3)': 'var(--burnt-sienna-alpha-30)',
    'rgba(224, 122, 95, 0.9)': 'var(--burnt-sienna-alpha-90)',
    
    'rgba(242, 204, 143, 0.15)': 'var(--sunset-alpha-15)',
    'rgba(242, 204, 143, 0.3)': 'var(--sunset-alpha-30)',
    
    'rgba(0, 123, 255, 0.1)': 'var(--bootstrap-blue-alpha-10)',
    'rgba(0, 123, 255, 0.2)': 'var(--bootstrap-blue-alpha-20)',
    'rgba(0, 123, 255, 0.3)': 'var(--bootstrap-blue-alpha-30)',
    
    'rgba(40, 167, 69, 0.1)': 'var(--bootstrap-green-alpha-10)',
    'rgba(40, 167, 69, 0.3)': 'var(--bootstrap-green-alpha-30)',
    'rgba(40, 167, 69, 0.4)': 'var(--bootstrap-green-alpha-40)',
    
    'rgba(255, 193, 7, 0.4)': 'var(--bootstrap-yellow-alpha-40)',
    'rgba(220, 53, 69, 0.4)': 'var(--bootstrap-red-alpha-40)',
}

def replace_colors_in_file(file_path):
    """Replace hardcoded colors in a single CSS file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Replace each mapping
        for old_color, new_var in COLOR_MAPPINGS.items():
            content = content.replace(old_color, new_var)
        
        # Only write if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated: {file_path}")
            return True
        else:
            print(f"No changes needed: {file_path}")
            return False
            
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Main function to process all CSS files"""
    project_root = Path(__file__).parent.parent
    
    # Find all CSS files in static directories
    css_files = []
    for app_dir in project_root.glob('*/static/css/*.css'):
        css_files.append(app_dir)
    
    print(f"Found {len(css_files)} CSS files to process")
    
    updated_count = 0
    for css_file in css_files:
        if replace_colors_in_file(css_file):
            updated_count += 1
    
    print(f"\nCompleted! Updated {updated_count} files.")

if __name__ == "__main__":
    main()
