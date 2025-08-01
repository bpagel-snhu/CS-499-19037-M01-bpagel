"""
Build information module for the batch_renamer application.
This module provides version, build date, and commit information.
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
        # Get the project root directory
        current_dir = os.path.dirname(os.path.dirname(__file__))
        
        # Get commit hash
        hash_result = subprocess.run(
            ['git', 'rev-parse', '--short', 'HEAD'],
            cwd=current_dir,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        # Get commit date
        date_result = subprocess.run(
            ['git', 'log', '-1', '--format=%cd', '--date=short'],
            cwd=current_dir,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        # Get current branch name
        branch_result = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            cwd=current_dir,
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


def get_version() -> str:
    """
    Get the application version.
    
    Returns:
        Version string
    """
    # For now, return a simple version
    # In a real application, you might read this from a version file or __init__.py
    return "1.0.0"


def get_build_date() -> str:
    """
    Get the build date using multiple fallback methods.
    
    Returns:
        Build date in YYYY-MM-DD format
    """
    # Try to get from build-time constant (for compiled versions)
    try:
        return __BUILD_DATE__
    except NameError:
        pass
    
    # Try to get from generated build info file
    try:
        from .build_info_generated import __BUILD_DATE__ as generated_build_date
        return generated_build_date
    except ImportError:
        pass
    
    # Try to get from Git commit date
    _, commit_date, _ = get_git_info()
    if commit_date:
        return commit_date
    
    # Fallback: Get the modification time of the main application file
    try:
        main_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'main.py')
        
        if os.path.exists(main_file):
            mtime = os.path.getmtime(main_file)
            return datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
    except Exception:
        pass
    
    # Final fallback: current date
    return datetime.datetime.now().strftime('%Y-%m-%d')


def get_build_info() -> dict:
    """
    Get comprehensive build information.
    
    Returns:
        Dictionary containing build information
    """
    commit_hash, commit_date, branch_name = get_git_info()
    
    # Try to get branch info from generated file if Git info is not available
    if not branch_name:
        try:
            from .build_info_generated import __BRANCH_NAME__ as generated_branch_name
            if generated_branch_name != 'unknown':
                branch_name = generated_branch_name
        except ImportError:
            pass
    
    return {
        'version': get_version(),
        'build_date': get_build_date(),
        'commit_hash': commit_hash,
        'commit_date': commit_date,
        'branch_name': branch_name,
        'is_git_repo': commit_hash is not None
    }


def format_build_string() -> str:
    """
    Format build information as a display string.
    
    Returns:
        Formatted build string for display
    """
    info = get_build_info()
    
    # Start with the basic build date
    build_string = f"Build: {info['build_date']}"
    
    # Add commit hash if available
    if info['commit_hash']:
        build_string += f" ({info['commit_hash']})"
    
    # Add branch information if not on main/master
    if info['branch_name'] and info['branch_name'] not in ['main', 'master']:
        build_string += f" [{info['branch_name']}]"
    
    return build_string 