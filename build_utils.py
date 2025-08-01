#!/usr/bin/env python3
"""
Build utilities for the batch_renamer application.
This script can be used to generate build information for compiled versions.
"""

import os
import subprocess
import datetime
from typing import Optional, Tuple


def get_git_info() -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Get Git commit hash, date, and branch name.
    
    Returns:
        Tuple of (commit_hash, commit_date, branch_name) or (None, None, None) if not available
    """
    try:
        # Get commit hash
        hash_result = subprocess.run(
            ['git', 'rev-parse', '--short', 'HEAD'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        # Get commit date
        date_result = subprocess.run(
            ['git', 'log', '-1', '--format=%cd', '--date=short'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        # Get current branch name
        branch_result = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        commit_hash = hash_result.stdout.strip() if hash_result.returncode == 0 else None
        commit_date = date_result.stdout.strip() if date_result.returncode == 0 else None
        branch_name = branch_result.stdout.strip() if branch_result.returncode == 0 else None
        
        return commit_hash, commit_date, branch_name
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
        return None, None, None


def generate_build_info_py():
    """
    Generate a build_info.py file with build-time constants.
    This is useful for compiled versions where Git info is not available.
    """
    commit_hash, commit_date, branch_name = get_git_info()
    current_date = datetime.datetime.now().strftime('%Y-%m-%d')
    
    # Use Git commit date if available, otherwise use current date
    build_date = commit_date if commit_date else current_date
    
    content = f'''"""
Auto-generated build information.
This file is generated during the build process.
"""

# Build date (from Git commit or current date)
__BUILD_DATE__ = "{build_date}"

# Git commit hash (if available)
__COMMIT_HASH__ = "{commit_hash if commit_hash else 'unknown'}"

# Branch name (if available)
__BRANCH_NAME__ = "{branch_name if branch_name else 'unknown'}"

# Build timestamp
__BUILD_TIMESTAMP__ = "{datetime.datetime.now().isoformat()}"

# Version
__VERSION__ = "1.0.0"
'''
    
    with open('batch_renamer/build_info_generated.py', 'w') as f:
        f.write(content)
    
    print(f"Generated build_info_generated.py with build date: {build_date}")
    if commit_hash:
        print(f"Git commit: {commit_hash}")
    if branch_name and branch_name not in ['main', 'master']:
        print(f"Branch: {branch_name}")


def generate_version_file():
    """
    Generate a version file that can be used by PyInstaller or other build tools.
    """
    commit_hash, commit_date, branch_name = get_git_info()
    current_date = datetime.datetime.now().strftime('%Y-%m-%d')
    
    build_date = commit_date if commit_date else current_date
    
    version_info = {
        'version': '1.0.0',
        'build_date': build_date,
        'commit_hash': commit_hash if commit_hash else 'unknown',
        'branch_name': branch_name if branch_name else 'unknown',
        'build_timestamp': datetime.datetime.now().isoformat()
    }
    
    content = f'''# Auto-generated version information
VERSION = "{version_info['version']}"
BUILD_DATE = "{version_info['build_date']}"
COMMIT_HASH = "{version_info['commit_hash']}"
BRANCH_NAME = "{version_info['branch_name']}"
BUILD_TIMESTAMP = "{version_info['build_timestamp']}"
'''
    
    with open('version.py', 'w') as f:
        f.write(content)
    
    print(f"Generated version.py with build date: {build_date}")
    if branch_name and branch_name not in ['main', 'master']:
        print(f"Branch: {branch_name}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "build-info":
            generate_build_info_py()
        elif command == "version":
            generate_version_file()
        else:
            print("Usage: python build_utils.py [build-info|version]")
    else:
        print("Available commands:")
        print("  build-info - Generate build_info_generated.py")
        print("  version    - Generate version.py")
        print("\nExample: python build_utils.py build-info") 