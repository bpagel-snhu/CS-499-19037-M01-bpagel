#!/usr/bin/env python3
"""
Test script for the build info functionality.
"""

import sys
import os

# Add the current directory to the path so we can import batch_renamer
sys.path.insert(0, os.path.dirname(__file__))

try:
    from batch_renamer.build_info import format_build_string, get_build_info
    
    print("Testing build info functionality...")
    print(f"Build string: {format_build_string()}")
    
    info = get_build_info()
    print(f"Build info: {info}")
    
    print("\nBranch detection test:")
    if info['branch_name']:
        if info['branch_name'] in ['main', 'master']:
            print(f"✓ On main branch: {info['branch_name']}")
        else:
            print(f"✓ On development branch: {info['branch_name']}")
    else:
        print("✗ No branch information available")
    
except ImportError as e:
    print(f"Import error: {e}")
    print("This is expected if dependencies are not installed.")
except Exception as e:
    print(f"Error: {e}") 