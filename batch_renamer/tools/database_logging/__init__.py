"""
Database Logging Tool

This tool provides functionality for database logging operations.
Currently includes client management with SQLite database.
"""

from .database_frame import DatabaseFrame
from .database_manager import DatabaseManager

__version__ = "1.0.0"
__all__ = ['DatabaseFrame', 'DatabaseManager'] 